"""
BERT fine-tuning script for dental symptom text classification.
Classes: cavity, healthy, impacted, infection, other

Run:
    python -m app.ml.train_bert
"""

import json
import copy
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from torch.optim import AdamW
from torch.optim.lr_scheduler import LinearLR, CosineAnnealingLR, SequentialLR
from transformers import BertTokenizerFast, BertForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parents[4]
WEIGHTS_DIR = BASE_DIR / "DentAI_Dev" / "backend" / "app" / "ml" / "weights"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

DATASET_PATH = WEIGHTS_DIR / "symptom_dataset.json"
MODEL_DIR    = WEIGHTS_DIR / "bert_dental"
MODEL_PATH   = WEIGHTS_DIR / "bert_dental.pth"

CLASSES = ["cavity", "healthy", "impacted", "infection", "other"]

# ── Config ─────────────────────────────────────────────────────────────────────
DEVICE       = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_NAME   = "bert-base-uncased"
MAX_LENGTH   = 128
BATCH_SIZE   = 16
EPOCHS       = 15
LR           = 2e-5
WEIGHT_DECAY = 1e-2
WARMUP_RATIO = 0.1
VAL_SPLIT    = 0.15

print(f"Using device: {DEVICE}")


# ── Dataset ────────────────────────────────────────────────────────────────────
class SymptomDataset(Dataset):
    def __init__(self, records: list[dict], tokenizer, max_length: int = MAX_LENGTH):
        self.records   = records
        self.tokenizer = tokenizer
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


def load_data(tokenizer):
    if not DATASET_PATH.exists():
        print("Generating symptom dataset...")
        from app.ml.symptom_dataset import save_dataset
        save_dataset(DATASET_PATH, target_per_class=200)

    with open(DATASET_PATH) as f:
        raw = json.load(f)

    records = raw["data"]
    full_ds = SymptomDataset(records, tokenizer)

    val_size   = int(len(full_ds) * VAL_SPLIT)
    train_size = len(full_ds) - val_size
    train_ds, val_ds = random_split(
        full_ds, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)

    print(f"Train: {len(train_ds)} | Val: {len(val_ds)}")
    return train_loader, val_loader


# ── Training ───────────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, optimizer):
    model.train()
    total_loss, correct, total = 0.0, 0, 0

    for batch in loader:
        input_ids      = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        labels         = batch["labels"].to(DEVICE)

        optimizer.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss    = outputs.loss
        logits  = outputs.logits

        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item() * labels.size(0)
        preds = logits.argmax(dim=-1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)

    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    all_preds, all_labels = [], []

    for batch in loader:
        input_ids      = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        labels         = batch["labels"].to(DEVICE)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss    = outputs.loss
        logits  = outputs.logits

        total_loss += loss.item() * labels.size(0)
        preds = logits.argmax(dim=-1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    return total_loss / total, correct / total, all_preds, all_labels


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("Loading tokenizer and model...")
    tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)
    model     = BertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(CLASSES),
        id2label={i: c for i, c in enumerate(CLASSES)},
        label2id={c: i for i, c in enumerate(CLASSES)},
    ).to(DEVICE)

    train_loader, val_loader = load_data(tokenizer)

    total_steps  = len(train_loader) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    warmup_scheduler = LinearLR(optimizer, start_factor=0.1, end_factor=1.0, total_iters=warmup_steps)
    cosine_scheduler = CosineAnnealingLR(optimizer, T_max=total_steps - warmup_steps, eta_min=1e-7)
    scheduler = SequentialLR(optimizer, schedulers=[warmup_scheduler, cosine_scheduler],
                             milestones=[warmup_steps])

    best_val_acc = 0.0
    best_model_wts = copy.deepcopy(model.state_dict())

    print("\n" + "="*60)
    print("Training BERT for dental symptom classification")
    print("="*60)

    for epoch in range(1, EPOCHS + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer)
        val_loss, val_acc, _, _ = evaluate(model, val_loader)
        scheduler.step()

        elapsed = time.time() - t0
        print(f"Epoch {epoch:02d}/{EPOCHS} | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
              f"Time: {elapsed:.1f}s")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            print(f"  ✓ New best val accuracy: {best_val_acc:.4f}")

    # ── Save model ─────────────────────────────────────────────────────────────
    model.load_state_dict(best_model_wts)
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    torch.save(best_model_wts, MODEL_PATH)

    print(f"\nModel saved to {MODEL_DIR}")
    print(f"Best Val Accuracy: {best_val_acc:.4f}")

    # Final report on full val set
    _, _, preds, labels = evaluate(model, val_loader)
    print("\nClassification Report:")
    print(classification_report(labels, preds, target_names=CLASSES))
    print("Confusion Matrix:")
    print(confusion_matrix(labels, preds))


if __name__ == "__main__":
    main()
