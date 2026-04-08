"""
EfficientNetV2-M training script for dental X-ray classification.
Classes: cavity, healthy, impacted, infection, other

Training strategy:
  Phase 1 (5 epochs)  — freeze backbone, train classifier head only
  Phase 2 (30 epochs) — unfreeze all layers, full fine-tune with low LR

Run:
    python -m app.ml.train_efficientnet
    python -m app.ml.train_efficientnet --skip-phase1              # resume from Phase 1 checkpoint
    python -m app.ml.train_efficientnet --resume-phase2 4          # resume Phase 2 from epoch 4
    python -m app.ml.train_efficientnet --resume-phase2 4 --checkpoint efficientnet_dental.pth
"""

import os
import sys
import copy
import json
import time
import argparse
from pathlib import Path

# Force UTF-8 output to avoid Windows cp1252 encoding errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, models, transforms
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[4]          # repo root
DATA_DIR = BASE_DIR / "DentAI_dataset"
MODEL_DIR = BASE_DIR / "DentAI_Dev" / "backend" / "app" / "ml" / "weights"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "efficientnet_dental.pth"
PHASE1_CKPT = MODEL_DIR / "efficientnet_phase1_best.pth"
CLASSES_PATH = MODEL_DIR / "efficientnet_classes.json"

# ── Config ─────────────────────────────────────────────────────────────────────
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_SIZE = 480          # EfficientNetV2-M native resolution
BATCH_SIZE = 16         # Phase 1 batch size (backbone frozen, small memory)
PHASE2_BATCH_SIZE = 4   # Phase 2 batch size (full backprop, large memory)
ACCUM_STEPS = 4         # Gradient accumulation: effective batch = PHASE2_BATCH_SIZE * ACCUM_STEPS = 16
NUM_WORKERS = 0         # 0 is safest on Windows
NUM_CLASSES = 5

PHASE1_EPOCHS = 5       # head-only warmup
PHASE2_EPOCHS = 30      # full fine-tune

LR_HEAD = 1e-3          # phase 1 lr
LR_FULL = 3e-5          # phase 2 lr (low to preserve pretrained weights)
WEIGHT_DECAY = 1e-4
LABEL_SMOOTHING = 0.1

print(f"Using device: {DEVICE}")


# ── Transforms ─────────────────────────────────────────────────────────────────
train_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
    transforms.RandomCrop(IMG_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
    transforms.RandomGrayscale(p=0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    transforms.RandomErasing(p=0.2, scale=(0.02, 0.15)),
])

val_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


# ── Dataset ────────────────────────────────────────────────────────────────────
def build_dataloaders(train_batch_size=BATCH_SIZE):
    train_ds = datasets.ImageFolder(DATA_DIR / "train", transform=train_transforms)
    val_ds   = datasets.ImageFolder(DATA_DIR / "val",   transform=val_transforms)
    test_ds  = datasets.ImageFolder(DATA_DIR / "test",  transform=val_transforms)

    # Weighted sampler to handle class imbalance
    class_counts = np.array([len(os.listdir(DATA_DIR / "train" / c)) for c in train_ds.classes])
    class_weights = 1.0 / class_counts
    sample_weights = [class_weights[label] for _, label in train_ds.samples]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    train_loader = DataLoader(train_ds, batch_size=train_batch_size, sampler=sampler,
                              num_workers=NUM_WORKERS, pin_memory=False)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=NUM_WORKERS)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=NUM_WORKERS)

    print(f"Classes: {train_ds.classes}")
    print(f"Train: {len(train_ds)} | Val: {len(val_ds)} | Test: {len(test_ds)}")

    return train_loader, val_loader, test_loader, train_ds.classes


# ── Model ──────────────────────────────────────────────────────────────────────
def build_model():
    model = models.efficientnet_v2_m(weights=models.EfficientNet_V2_M_Weights.IMAGENET1K_V1)

    # Replace classifier head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, NUM_CLASSES),
    )
    return model.to(DEVICE)


def freeze_backbone(model):
    for param in model.features.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True


def unfreeze_all(model):
    for param in model.parameters():
        param.requires_grad = True


# ── Training loop ──────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, criterion, optimizer, epoch, total_epochs, phase, accum_steps=1):
    model.train()
    running_loss, correct, total = 0.0, 0, 0

    pbar = tqdm(loader, desc=f"[{phase}] Epoch {epoch}/{total_epochs} Train", unit="batch", leave=False)
    optimizer.zero_grad()
    for step, (inputs, labels) in enumerate(pbar):
        inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
        outputs = model(inputs)
        loss = criterion(outputs, labels) / accum_steps
        loss.backward()

        if (step + 1) % accum_steps == 0 or (step + 1) == len(loader):
            optimizer.step()
            optimizer.zero_grad()

        running_loss += loss.item() * accum_steps * inputs.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)
        pbar.set_postfix(loss=f"{running_loss/total:.4f}", acc=f"{correct/total:.4f}")

    return running_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, desc="Val"):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    all_preds, all_labels = [], []

    pbar = tqdm(loader, desc=f"  {desc}", unit="batch", leave=False)
    for inputs, labels in pbar:
        inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        running_loss += loss.item() * inputs.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        pbar.set_postfix(loss=f"{running_loss/total:.4f}", acc=f"{correct/total:.4f}")

    return running_loss / total, correct / total, all_preds, all_labels


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-phase1", action="store_true",
                        help="Skip Phase 1 and resume from saved Phase 1 checkpoint")
    parser.add_argument("--resume-phase2", type=int, default=None, metavar="EPOCH",
                        help="Skip Phase 1 and start Phase 2 from this epoch number (1-based). "
                             "Loads --checkpoint (default: efficientnet_dental.pth).")
    parser.add_argument("--checkpoint", type=str, default="efficientnet_dental.pth",
                        help="Checkpoint filename inside weights/ to load when using --resume-phase2 "
                             "(default: efficientnet_dental.pth)")
    args = parser.parse_args()

    if args.resume_phase2 is not None and args.resume_phase2 < 1:
        parser.error("--resume-phase2 must be >= 1")

    train_loader, val_loader, test_loader, classes = build_dataloaders(train_batch_size=BATCH_SIZE)

    # Save class mapping
    class_to_idx = {c: i for i, c in enumerate(classes)}
    with open(CLASSES_PATH, "w") as f:
        json.dump({"classes": classes, "class_to_idx": class_to_idx}, f, indent=2)
    print(f"Class mapping saved to {CLASSES_PATH}")

    model = build_model()
    criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)

    best_val_acc = 0.0
    best_model_wts = copy.deepcopy(model.state_dict())

    if args.resume_phase2 is not None:
        # ── Resume Phase 2 from a specific epoch ──────────────────────────────
        ckpt_path = MODEL_DIR / args.checkpoint
        if not ckpt_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
        print("\n" + "="*60)
        print(f"RESUMING PHASE 2 from epoch {args.resume_phase2}")
        print(f"  Checkpoint: {ckpt_path}")
        print("="*60)
        model.load_state_dict(torch.load(ckpt_path, map_location=DEVICE))
        best_model_wts = copy.deepcopy(model.state_dict())
        print("Evaluating checkpoint on val set...")
        _, best_val_acc, _, _ = evaluate(model, val_loader, criterion, desc="Val")
        print(f"Checkpoint val accuracy: {best_val_acc:.4f}")

        # Go straight to Phase 2 with remaining epochs
        print("\n" + "="*60)
        print("PHASE 2: Full fine-tune (all layers unfrozen) — RESUMED")
        print(f"  Starting from epoch {args.resume_phase2}/{PHASE2_EPOCHS}")
        print(f"  Batch size: {PHASE2_BATCH_SIZE} | Gradient accumulation: {ACCUM_STEPS} steps | Effective batch: {PHASE2_BATCH_SIZE * ACCUM_STEPS}")
        print("="*60)
        unfreeze_all(model)
        p2_train_loader, _, _, _ = build_dataloaders(train_batch_size=PHASE2_BATCH_SIZE)
        optimizer = optim.AdamW(model.parameters(), lr=LR_FULL, weight_decay=WEIGHT_DECAY)
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=10, T_mult=2, eta_min=1e-7
        )
        # Advance scheduler state to match the epoch we're resuming from
        for _ in range(args.resume_phase2 - 1):
            scheduler.step()

        for epoch in range(args.resume_phase2, PHASE2_EPOCHS + 1):
            t0 = time.time()
            train_loss, train_acc = train_one_epoch(model, p2_train_loader, criterion, optimizer, epoch, PHASE2_EPOCHS, "P2", accum_steps=ACCUM_STEPS)
            val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, desc="Val")
            scheduler.step()

            elapsed = time.time() - t0
            print(f"Epoch {epoch:02d}/{PHASE2_EPOCHS} | "
                  f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
                  f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
                  f"Time: {elapsed:.1f}s")

            torch.save(model.state_dict(), MODEL_DIR / "efficientnet_latest.pth")

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_model_wts = copy.deepcopy(model.state_dict())
                torch.save(best_model_wts, MODEL_PATH)
                print(f"  >> New best val accuracy: {best_val_acc:.4f} - saved to {MODEL_PATH}")

        # Final evaluation
        print("\n" + "="*60)
        print("FINAL EVALUATION ON TEST SET")
        print("="*60)
        model.load_state_dict(best_model_wts)
        _, test_acc, test_preds, test_labels = evaluate(model, test_loader, criterion, desc="Test")
        print(f"Test Accuracy: {test_acc:.4f}")
        print("\nClassification Report:")
        print(classification_report(test_labels, test_preds, target_names=classes))
        print("Confusion Matrix:")
        print(confusion_matrix(test_labels, test_preds))
        torch.save(best_model_wts, MODEL_PATH)
        print(f"\nModel saved to {MODEL_PATH}")
        print(f"Best Val Accuracy: {best_val_acc:.4f}")
        return

    elif args.skip_phase1:
        # ── Load Phase 1 checkpoint ────────────────────────────────────────────
        if not PHASE1_CKPT.exists():
            raise FileNotFoundError(f"Phase 1 checkpoint not found: {PHASE1_CKPT}\nRun without --skip-phase1 first.")
        print("\n" + "="*60)
        print("SKIPPING PHASE 1 — loading checkpoint")
        print(f"  {PHASE1_CKPT}")
        print("="*60)
        model.load_state_dict(torch.load(PHASE1_CKPT, map_location=DEVICE))
        best_model_wts = copy.deepcopy(model.state_dict())
        # Evaluate on val set so best_val_acc is meaningful for Phase 2 saving
        print("Evaluating Phase 1 checkpoint on val set...")
        _, best_val_acc, _, _ = evaluate(model, val_loader, criterion, desc="Val")
        print(f"Phase 1 checkpoint val accuracy: {best_val_acc:.4f}")
    else:
        # ── Phase 1: Train head only ───────────────────────────────────────────
        print("\n" + "="*60)
        print("PHASE 1: Training classifier head (backbone frozen)")
        print("="*60)
        freeze_backbone(model)
        optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()),
                                lr=LR_HEAD, weight_decay=WEIGHT_DECAY)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=PHASE1_EPOCHS)

        for epoch in range(1, PHASE1_EPOCHS + 1):
            t0 = time.time()
            train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, epoch, PHASE1_EPOCHS, "P1")
            val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, desc="Val")
            scheduler.step()

            elapsed = time.time() - t0
            print(f"Epoch {epoch:02d}/{PHASE1_EPOCHS} | "
                  f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
                  f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
                  f"Time: {elapsed:.1f}s")

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_model_wts = copy.deepcopy(model.state_dict())
                print(f"  >> New best val accuracy: {best_val_acc:.4f}")

        # Save Phase 1 best weights as checkpoint before Phase 2
        torch.save(best_model_wts, PHASE1_CKPT)
        print(f"Phase 1 complete. Best val acc: {best_val_acc:.4f} | Checkpoint: {PHASE1_CKPT}")

    # ── Phase 2: Full fine-tune ────────────────────────────────────────────────
    print("\n" + "="*60)
    print("PHASE 2: Full fine-tune (all layers unfrozen)")
    print(f"  Batch size: {PHASE2_BATCH_SIZE} | Gradient accumulation: {ACCUM_STEPS} steps | Effective batch: {PHASE2_BATCH_SIZE * ACCUM_STEPS}")
    print("="*60)
    model.load_state_dict(best_model_wts)   # start from best phase-1 weights
    unfreeze_all(model)

    # Rebuild train loader with smaller batch to avoid OOM during full backprop
    p2_train_loader, _, _, _ = build_dataloaders(train_batch_size=PHASE2_BATCH_SIZE)

    optimizer = optim.AdamW(model.parameters(), lr=LR_FULL, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2, eta_min=1e-7
    )

    for epoch in range(1, PHASE2_EPOCHS + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, p2_train_loader, criterion, optimizer, epoch, PHASE2_EPOCHS, "P2", accum_steps=ACCUM_STEPS)
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, desc="Val")
        scheduler.step()

        elapsed = time.time() - t0
        print(f"Epoch {epoch:02d}/{PHASE2_EPOCHS} | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
              f"Time: {elapsed:.1f}s")

        # Save latest checkpoint every epoch (safe resume point)
        torch.save(model.state_dict(), MODEL_DIR / "efficientnet_latest.pth")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            torch.save(best_model_wts, MODEL_PATH)
            print(f"  >> New best val accuracy: {best_val_acc:.4f} - saved to {MODEL_PATH}")

    # ── Final evaluation on test set ──────────────────────────────────────────
    print("\n" + "="*60)
    print("FINAL EVALUATION ON TEST SET")
    print("="*60)
    model.load_state_dict(best_model_wts)
    _, test_acc, test_preds, test_labels = evaluate(model, test_loader, criterion, desc="Test")
    print(f"Test Accuracy: {test_acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(test_labels, test_preds, target_names=classes))
    print("Confusion Matrix:")
    print(confusion_matrix(test_labels, test_preds))

    # Save final model
    torch.save(best_model_wts, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Best Val Accuracy: {best_val_acc:.4f}")


if __name__ == "__main__":
    main()
