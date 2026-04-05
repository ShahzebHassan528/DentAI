import os
import shutil
from collections import defaultdict

# ── CONFIG ──────────────────────────────────────────────────────────────────
KAGGLE4_ROOT = r"C:\Users\DELL\Desktop\Shahzeb\DATASETS\Kaggle\Dental Radiography Segmentation Abbas\Dental_Radiography"
DEST_TRAIN   = r"C:\Users\DELL\Desktop\Shahzeb\FYP\DentAI_dataset\train"
PREFIX       = "kaggle4_"

# Folder name → our target class (None = skip)
CLASS_MAP = {
    "Cavity":        "cavity",
    "Impacted Tooth":"impacted",
    "Normal":        "healthy",
    "Fillings":      None,
    "Implant":       None,
}

SPLITS = ["train", "valid", "test"]
# ────────────────────────────────────────────────────────────────────────────

for cls in ["cavity", "impacted", "healthy"]:
    os.makedirs(os.path.join(DEST_TRAIN, cls), exist_ok=True)

counters  = defaultdict(int)
skipped   = 0

for split in SPLITS:
    split_dir = os.path.join(KAGGLE4_ROOT, split)
    if not os.path.exists(split_dir):
        print(f"[WARN] Split folder not found: {split_dir}")
        continue

    for folder_name, target_class in CLASS_MAP.items():
        folder_path = os.path.join(split_dir, folder_name)
        if not os.path.exists(folder_path):
            continue
        if target_class is None:
            files = os.listdir(folder_path)
            skipped += len(files)
            continue

        files = [f for f in os.listdir(folder_path)
                 if f.lower().endswith((".jpg", ".jpeg", ".png"))]

        for fname in files:
            src = os.path.join(folder_path, fname)
            dest_name = PREFIX + fname
            dst = os.path.join(DEST_TRAIN, target_class, dest_name)

            # Avoid collision (same filename across splits)
            if os.path.exists(dst):
                base, ext = os.path.splitext(dest_name)
                dst = os.path.join(DEST_TRAIN, target_class, f"{base}_{split}{ext}")

            shutil.copy2(src, dst)
            counters[target_class] += 1

print("\n" + "="*50)
print("KAGGLE4 MERGE COMPLETE")
print("="*50)
for cls, cnt in sorted(counters.items()):
    print(f"  {cls:12s}: {cnt:4d} images added")
total = sum(counters.values())
print(f"  {'TOTAL':12s}: {total:4d} images added")
print(f"  Skipped (Fillings/Implant): {skipped}")

print("\nCumulative totals after Kaggle4:")
prev = {"cavity":811, "infection":206, "impacted":694, "healthy":226, "other":13}
for cls, cnt in counters.items():
    prev[cls] = prev.get(cls, 0) + cnt
for cls, cnt in sorted(prev.items()):
    print(f"  {cls:12s}: {cnt}")
print(f"  {'TOTAL':12s}: {sum(prev.values())}")