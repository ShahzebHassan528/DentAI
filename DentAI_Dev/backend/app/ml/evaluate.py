"""
Day 7 — Model Evaluation & Metrics Script
==========================================
Evaluates both models and saves metrics.json for the API to serve.

  EfficientNetV2-M  → evaluated on DentAI_dataset/test/
  BERT              → evaluated on 15% held-out split of symptom_dataset.json
  Confidence Threshold → accuracy vs. coverage sweep

Run from DentAI_Dev/backend/:
    python -m app.ml.evaluate

Output:
    backend/app/ml/weights/metrics.json
"""

import json
import sys
import copy
from pathlib import Path
from datetime import datetime

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import datasets, models, transforms
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
)
from transformers import BertTokenizerFast, BertForSequenceClassification

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parents[4]
DATA_DIR     = BASE_DIR / "DentAI_dataset"
WEIGHTS_DIR  = Path(__file__).parent / "weights"
METRICS_PATH = WEIGHTS_DIR / "metrics.json"

EFFNET_PATH    = WEIGHTS_DIR / "efficientnet_dental.pth"
EFFNET_CLASSES = WEIGHTS_DIR / "efficientnet_classes.json"
BERT_DIR       = WEIGHTS_DIR / "bert_dental"
DATASET_PATH   = WEIGHTS_DIR / "symptom_dataset.json"

DEVICE     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_SIZE   = 480
BATCH_SIZE = 16
CLASSES    = ["cavity", "healthy", "impacted", "infection", "other"]

print(f"Device: {DEVICE}")
print(f"Weights dir: {WEIGHTS_DIR}")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _build_per_class(labels, preds, classes):
    """Build per-class precision / recall / f1 / support dict."""
    report = classification_report(labels, preds, target_names=classes,
                                   output_dict=True, zero_division=0)
    per_class = {}
    for cls in classes:
        row = report.get(cls, {})
        per_class[cls] = {
            "precision": round(float(row.get("precision", 0)), 4),
            "recall":    round(float(row.get("recall", 0)), 4),
            "f1":        round(float(row.get("f1-score", 0)), 4),
            "support":   int(row.get("support", 0)),
        }
    return per_class


def _threshold_analysis(all_probs, all_labels):
    """
    Sweep confidence thresholds (0.40 → 0.95).
    For each threshold, compute:
      coverage  = fraction of samples where max_prob >= threshold
      accuracy  = accuracy on those 'confident' samples
    Returns list of dicts, plus recommended threshold.
    """
    all_probs  = np.array(all_probs)   # (N, C)
    all_labels = np.array(all_labels)  # (N,)
    max_probs  = all_probs.max(axis=1)
    pred_labels = all_probs.argmax(axis=1)

    rows = []
    best_thresh = 0.5
    for t in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        mask = max_probs >= t
        coverage = float(mask.sum()) / len(mask) if len(mask) > 0 else 0.0
        if mask.sum() > 0:
            acc = accuracy_score(all_labels[mask], pred_labels[mask])
        else:
            acc = 0.0
        rows.append({
            "threshold": t,
            "coverage":  round(coverage, 4),
            "accuracy_when_confident": round(float(acc), 4),
        })
        # Recommend the lowest threshold where accuracy >= 0.85
        if float(acc) >= 0.85 and coverage >= 0.50:
            best_thresh = t

    return rows, best_thresh


# ──────────────────────────────────────────────────────────────────────────────
# EfficientNetV2-M
# ──────────────────────────────────────────────────────────────────────────────
def evaluate_efficientnet():
    print("\n" + "=" * 60)
    print("EVALUATING  EfficientNetV2-M  on test split")
    print("=" * 60)

    if not EFFNET_PATH.exists():
        print(f"  [SKIP] Weights not found at {EFFNET_PATH}")
        return None

    test_dir = DATA_DIR / "test"
    if not test_dir.exists():
        print(f"  [SKIP] Test directory not found at {test_dir}")
        return None

    # Load class order used at training time
    with open(EFFNET_CLASSES) as f:
        meta = json.load(f)
    classes = meta["classes"]

    # Rebuild model
    model = models.efficientnet_v2_m(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, len(classes)),
    )
    model.load_state_dict(torch.load(EFFNET_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()

    val_transforms = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    test_ds     = datasets.ImageFolder(test_dir, transform=val_transforms)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=0)

    all_preds, all_labels, all_probs_list = [], [], []
    with torch.no_grad():
        for imgs, lbls in test_loader:
            imgs = imgs.to(DEVICE)
            logits = model(imgs)
            probs  = F.softmax(logits, dim=1).cpu()
            preds  = probs.argmax(dim=1)
            all_probs_list.extend(probs.tolist())
            all_preds.extend(preds.tolist())
            all_labels.extend(lbls.tolist())

    acc     = accuracy_score(all_labels, all_preds)
    f1_mac  = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    f1_wt   = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
    cm      = confusion_matrix(all_labels, all_preds).tolist()
    per_cls = _build_per_class(all_labels, all_preds, classes)
    thresh_rows, best_thresh = _threshold_analysis(all_probs_list, all_labels)

    print(f"  Test Accuracy : {acc:.4f}  ({acc*100:.1f}%)")
    print(f"  F1 Macro      : {f1_mac:.4f}")
    print(f"  F1 Weighted   : {f1_wt:.4f}")
    print(f"  Samples       : {len(all_labels)}")
    print(f"  Recommended threshold: {best_thresh}")
    print()
    print(classification_report(all_labels, all_preds, target_names=classes,
                                zero_division=0))
    print("Confusion Matrix:")
    print(np.array(cm))

    return {
        "test_accuracy":    round(float(acc), 4),
        "test_f1_macro":    round(float(f1_mac), 4),
        "test_f1_weighted": round(float(f1_wt), 4),
        "num_test_samples": len(all_labels),
        "classes":          classes,
        "per_class":        per_cls,
        "confusion_matrix": cm,
        "threshold_analysis": thresh_rows,
        "recommended_threshold": best_thresh,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BERT
# ──────────────────────────────────────────────────────────────────────────────
class _SymptomDataset(Dataset):
    def __init__(self, records, tokenizer, max_length=128):
        self.records    = records
        self.tokenizer  = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]
        enc = self.tokenizer(
            rec["text"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels":         torch.tensor(rec["label"], dtype=torch.long),
        }


def evaluate_bert():
    print("\n" + "=" * 60)
    print("EVALUATING  BERT  on held-out validation split")
    print("=" * 60)

    if not BERT_DIR.exists():
        print(f"  [SKIP] BERT model not found at {BERT_DIR}")
        return None

    if not DATASET_PATH.exists():
        print(f"  [SKIP] Dataset not found at {DATASET_PATH}")
        return None

    tokenizer = BertTokenizerFast.from_pretrained(str(BERT_DIR))
    model     = BertForSequenceClassification.from_pretrained(str(BERT_DIR))
    model.to(DEVICE)
    model.eval()

    with open(DATASET_PATH) as f:
        raw = json.load(f)

    records    = raw["data"]
    full_ds    = _SymptomDataset(records, tokenizer)
    val_size   = int(len(full_ds) * 0.15)
    train_size = len(full_ds) - val_size
    _, val_ds  = random_split(full_ds, [train_size, val_size],
                              generator=torch.Generator().manual_seed(42))

    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)
    classes    = list(model.config.id2label.values())

    all_preds, all_labels, all_probs_list = [], [], []
    with torch.no_grad():
        for batch in val_loader:
            input_ids      = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels         = batch["labels"].to(DEVICE)
            outputs        = model(input_ids=input_ids,
                                   attention_mask=attention_mask)
            probs = F.softmax(outputs.logits, dim=1).cpu()
            preds = probs.argmax(dim=1)
            all_probs_list.extend(probs.tolist())
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.cpu().tolist())

    acc    = accuracy_score(all_labels, all_preds)
    f1_mac = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    f1_wt  = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
    cm     = confusion_matrix(all_labels, all_preds).tolist()
    per_cls = _build_per_class(all_labels, all_preds, classes)
    thresh_rows, best_thresh = _threshold_analysis(all_probs_list, all_labels)

    print(f"  Val Accuracy  : {acc:.4f}  ({acc*100:.1f}%)")
    print(f"  F1 Macro      : {f1_mac:.4f}")
    print(f"  F1 Weighted   : {f1_wt:.4f}")
    print(f"  Samples       : {len(all_labels)}")
    print(f"  Recommended threshold: {best_thresh}")
    print()
    print(classification_report(all_labels, all_preds, target_names=classes,
                                zero_division=0))
    print("Confusion Matrix:")
    print(np.array(cm))

    return {
        "val_accuracy":    round(float(acc), 4),
        "val_f1_macro":    round(float(f1_mac), 4),
        "val_f1_weighted": round(float(f1_wt), 4),
        "num_val_samples": len(all_labels),
        "classes":         classes,
        "per_class":       per_cls,
        "confusion_matrix": cm,
        "threshold_analysis": thresh_rows,
        "recommended_threshold": best_thresh,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    effnet_metrics = evaluate_efficientnet()
    bert_metrics   = evaluate_bert()

    # Compute fused recommended threshold (average of both, or just effnet)
    thresh_effnet = (effnet_metrics or {}).get("recommended_threshold", 0.6)
    thresh_bert   = (bert_metrics   or {}).get("recommended_threshold", 0.6)
    fused_thresh  = round((thresh_effnet + thresh_bert) / 2, 2)

    metrics = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "efficientnet": effnet_metrics or {"status": "weights not found — run train_efficientnet.py"},
        "bert":         bert_metrics   or {"status": "weights not found — run train_bert.py"},
        "fusion": {
            "strategy":        "Late fusion (weighted average of softmax probabilities)",
            "efficientnet_weight": 0.6,
            "bert_weight":         0.4,
            "formula":         "final = 0.6 × efficientnet_prob + 0.4 × bert_prob",
            "fallback":        "Single-model if only one input is provided",
            "recommended_combined_threshold": fused_thresh,
        },
    }

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Metrics saved to {METRICS_PATH}")
    print("=" * 60)

    # Summary table
    print("\n SUMMARY")
    print("-" * 40)
    if effnet_metrics:
        print(f"  EfficientNetV2  test accuracy : {effnet_metrics['test_accuracy']*100:.1f}%")
        print(f"  EfficientNetV2  F1 macro      : {effnet_metrics['test_f1_macro']*100:.1f}%")
    if bert_metrics:
        print(f"  BERT            val  accuracy : {bert_metrics['val_accuracy']*100:.1f}%")
        print(f"  BERT            F1 macro      : {bert_metrics['val_f1_macro']*100:.1f}%")
    print(f"  Fusion weights  : 0.6 / 0.4")
    print(f"  Recommended threshold : {fused_thresh}")
    print("-" * 40)


if __name__ == "__main__":
    main()
