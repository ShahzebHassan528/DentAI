import os
import csv
import shutil
from collections import defaultdict

# ── CONFIG ──────────────────────────────────────────────────────────────────
KAGGLE3_ROOT  = r"C:\Users\DELL\Desktop\Shahzeb\DATASETS\Kaggle\Dental Radiography"
DEST_TRAIN    = r"C:\Users\DELL\Desktop\Shahzeb\FYP\DentAI_dataset\train"
PREFIX        = "kaggle3_"

# Class mapping: CSV label → our target class (None = skip)
CLASS_MAP = {
    "Cavity":        "cavity",
    "Impacted Tooth":"impacted",
    "Implant":       None,   # not a disease — skip
    "Fillings":      None,   # existing dental work — skip
}

# Priority if multiple useful classes in one image (higher = wins)
PRIORITY = {"cavity": 2, "impacted": 1}

# Splits to process (use all three to maximise images)
SPLITS = ["train", "valid", "test"]
# ────────────────────────────────────────────────────────────────────────────

os.makedirs(os.path.join(DEST_TRAIN, "cavity"),   exist_ok=True)
os.makedirs(os.path.join(DEST_TRAIN, "impacted"),  exist_ok=True)

counters   = defaultdict(int)
skipped    = 0
not_found  = 0

for split in SPLITS:
    split_dir = os.path.join(KAGGLE3_ROOT, split)
    csv_path  = os.path.join(split_dir, "_annotations.csv")

    if not os.path.exists(csv_path):
        print(f"[WARN] No annotations CSV in {split} — skipping")
        continue

    # Build per-image → best class mapping
    image_class = {}   # filename → best target class so far

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            filename  = row["filename"].strip()
            raw_class = row["class"].strip()
            target    = CLASS_MAP.get(raw_class)
            if target is None:
                continue  # Fillings / Implant — skip
            # Keep highest-priority class for this image
            current = image_class.get(filename)
            if current is None or PRIORITY[target] > PRIORITY[current]:
                image_class[filename] = target

    print(f"\n[{split}] Useful images found: {len(image_class)}")

    for filename, target_class in image_class.items():
        src = os.path.join(split_dir, filename)
        if not os.path.exists(src):
            print(f"  [MISSING] {src}")
            not_found += 1
            continue

        dest_name = PREFIX + filename
        dst = os.path.join(DEST_TRAIN, target_class, dest_name)

        # Avoid overwrite collision
        if os.path.exists(dst):
            base, ext = os.path.splitext(dest_name)
            dst = os.path.join(DEST_TRAIN, target_class, f"{base}_{split}{ext}")

        shutil.copy2(src, dst)
        counters[target_class] += 1

print("\n" + "="*50)
print("KAGGLE3 MERGE COMPLETE")
print("="*50)
for cls, cnt in sorted(counters.items()):
    print(f"  {cls:12s}: {cnt:4d} images added")
total = sum(counters.values())
print(f"  {'TOTAL':12s}: {total:4d} images added")
if skipped:   print(f"  Skipped (Fillings/Implant): {skipped}")
if not_found: print(f"  Missing files: {not_found}")
print("\nCumulative totals after Kaggle3:")
prev = {"cavity":546, "infection":206, "impacted":448, "healthy":226, "other":13}
for cls, cnt in sorted(counters.items()):
    prev[cls] = prev.get(cls, 0) + cnt
for cls, cnt in sorted(prev.items()):
    print(f"  {cls:12s}: {cnt}")
print(f"  {'TOTAL':12s}: {sum(prev.values())}")