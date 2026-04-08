"""
Prediction pipelines for DentAI.

Usage:
    from app.ml.predict import predict_image, predict_text, predict_combined
"""

import json
from pathlib import Path
from io import BytesIO

import torch
import torch.nn.functional as F
from torchvision import models, transforms
import torch.nn as nn
from PIL import Image
from transformers import BertTokenizerFast, BertForSequenceClassification

# ── Paths ──────────────────────────────────────────────────────────────────────
WEIGHTS_DIR   = Path(__file__).parent / "weights"
EFFNET_PATH   = WEIGHTS_DIR / "efficientnet_dental.pth"
EFFNET_CLASSES = WEIGHTS_DIR / "efficientnet_classes.json"
BERT_DIR      = WEIGHTS_DIR / "bert_dental"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_SIZE = 480

# Fusion weights (image model is more reliable for visual conditions)
EFFNET_WEIGHT = 0.6
BERT_WEIGHT   = 0.4

# ── Singletons — loaded once on first call ────────────────────────────────────
_effnet_model  = None
_effnet_classes = None
_bert_model    = None
_bert_tokenizer = None


# ── EfficientNetV2-M ───────────────────────────────────────────────────────────
def _load_effnet():
    global _effnet_model, _effnet_classes

    if _effnet_model is not None:
        return _effnet_model, _effnet_classes

    if not EFFNET_PATH.exists():
        raise FileNotFoundError(
            f"EfficientNet weights not found at {EFFNET_PATH}. "
            "Run app/ml/train_efficientnet.py first."
        )

    with open(EFFNET_CLASSES) as f:
        meta = json.load(f)
    _effnet_classes = meta["classes"]

    model = models.efficientnet_v2_m(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, len(_effnet_classes)),
    )
    model.load_state_dict(torch.load(EFFNET_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    _effnet_model = model
    return _effnet_model, _effnet_classes


_val_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def predict_image(image_bytes: bytes) -> dict:
    """
    Predict dental condition from X-ray image bytes.

    Returns:
        {
          "diagnosis": "cavity",
          "confidence": 0.87,
          "probabilities": {"cavity": 0.87, "healthy": 0.05, ...}
        }
    """
    model, classes = _load_effnet()

    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    tensor = _val_transforms(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(tensor)
        probs  = F.softmax(logits, dim=1).squeeze(0).cpu().tolist()

    idx = int(torch.tensor(probs).argmax())
    return {
        "diagnosis":     classes[idx],
        "confidence":    round(probs[idx], 4),
        "probabilities": {c: round(p, 4) for c, p in zip(classes, probs)},
    }


# ── BERT ───────────────────────────────────────────────────────────────────────
def _load_bert():
    global _bert_model, _bert_tokenizer

    if _bert_model is not None:
        return _bert_model, _bert_tokenizer

    if not BERT_DIR.exists():
        raise FileNotFoundError(
            f"BERT model not found at {BERT_DIR}. "
            "Run app/ml/train_bert.py first."
        )

    _bert_tokenizer = BertTokenizerFast.from_pretrained(str(BERT_DIR))
    _bert_model     = BertForSequenceClassification.from_pretrained(str(BERT_DIR))
    _bert_model.to(DEVICE)
    _bert_model.eval()
    return _bert_model, _bert_tokenizer


BERT_CLASSES = ["cavity", "healthy", "impacted", "infection", "other"]


def predict_text(symptoms: str) -> dict:
    """
    Predict dental condition from symptom text.

    Returns:
        {
          "diagnosis": "infection",
          "confidence": 0.91,
          "probabilities": {"cavity": 0.02, "infection": 0.91, ...}
        }
    """
    model, tokenizer = _load_bert()

    enc = tokenizer(
        symptoms,
        max_length=128,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    input_ids      = enc["input_ids"].to(DEVICE)
    attention_mask = enc["attention_mask"].to(DEVICE)

    with torch.no_grad():
        logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
        probs  = F.softmax(logits, dim=1).squeeze(0).cpu().tolist()

    idx = int(torch.tensor(probs).argmax())
    classes = list(model.config.id2label.values())
    return {
        "diagnosis":     classes[idx],
        "confidence":    round(probs[idx], 4),
        "probabilities": {c: round(p, 4) for c, p in zip(classes, probs)},
    }


# ── Late Fusion ────────────────────────────────────────────────────────────────
def predict_combined(image_bytes: bytes | None, symptoms: str | None) -> dict:
    """
    Late fusion: final = 0.6 × efficientnet_prob + 0.4 × bert_prob
    Falls back to single model if only one input is provided.

    Returns:
        {
          "final_diagnosis": "cavity",
          "confidence": 0.84,
          "image_diagnosis": "cavity",       # or None
          "text_diagnosis": "cavity",        # or None
          "probabilities": {...},
          "mode": "combined" | "image_only" | "text_only"
        }
    """
    if image_bytes is None and symptoms is None:
        raise ValueError("At least one of image_bytes or symptoms must be provided.")

    img_result  = None
    text_result = None

    if image_bytes is not None:
        img_result = predict_image(image_bytes)

    if symptoms is not None and symptoms.strip():
        text_result = predict_text(symptoms)

    # Both inputs — late fusion
    if img_result is not None and text_result is not None:
        classes = list(img_result["probabilities"].keys())
        fused = {
            c: round(
                EFFNET_WEIGHT * img_result["probabilities"][c]
                + BERT_WEIGHT * text_result["probabilities"][c],
                4
            )
            for c in classes
        }
        best = max(fused, key=fused.get)
        return {
            "final_diagnosis": best,
            "confidence":      round(fused[best], 4),
            "image_diagnosis": img_result["diagnosis"],
            "text_diagnosis":  text_result["diagnosis"],
            "probabilities":   fused,
            "mode":            "combined",
        }

    # Image only
    if img_result is not None:
        return {
            "final_diagnosis": img_result["diagnosis"],
            "confidence":      img_result["confidence"],
            "image_diagnosis": img_result["diagnosis"],
            "text_diagnosis":  None,
            "probabilities":   img_result["probabilities"],
            "mode":            "image_only",
        }

    # Text only
    return {
        "final_diagnosis": text_result["diagnosis"],
        "confidence":      text_result["confidence"],
        "image_diagnosis": None,
        "text_diagnosis":  text_result["diagnosis"],
        "probabilities":   text_result["probabilities"],
        "mode":            "text_only",
    }
