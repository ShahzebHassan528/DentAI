import os
import shutil
from collections import Counter

# ── CONFIG ──────────────────────────────────────────────────────
KAGGLE1_ROOT = r"C:\Users\DELL\Desktop\Shahzeb\DATASETS\Kaggle\Dental OPG Xray\Dental OPG XRAY Dataset\Dental OPG (Classification)"
OUTPUT_DIR   = r"C:\Users\DELL\Desktop\Shahzeb\FYP\DentAI_dataset"
SPLIT        = "train"   # We'll put all of this into train
PREFIX       = "kaggle1"
# ────────────────────────────────────────────────────────────────

# Folder name → unified class
FOLDER_MAP = {
    "Caries":          "cavity",
    "Healthy Teeth":   "healthy",
    "Impacted teeth":  "impacted",
    "Infection":       "infection",
    "Fractured Teeth": "other",
    "BDC-BDR":         None,   # SKIP - unclassifiable
}

def run():
    copied, skipped, labels_used = 0, 0, []

    for folder_name, label in FOLDER_MAP.items():
        src_dir = os.path.join(KAGGLE1_ROOT, folder_name)

        if not os.path.exists(src_dir):
            print(f"  ⚠ Not found: {src_dir}")
            continue

        if label is None:
            count = len([f for f in os.listdir(src_dir) if f.endswith(".jpg")])
            print(f"  ⏭ Skipping '{folder_name}' ({count} images) — no matching class")
            continue

        dest_dir = os.path.join(OUTPUT_DIR, SPLIT, label)
        os.makedirs(dest_dir, exist_ok=True)

        for fname in os.listdir(src_dir):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            src  = os.path.join(src_dir, fname)
            dest = os.path.join(dest_dir, f"{PREFIX}_{fname}")
            # Avoid overwriting if file already exists
            if os.path.exists(dest):
                base, ext = os.path.splitext(fname)
                dest = os.path.join(dest_dir, f"{PREFIX}_{base}_2{ext}")
            shutil.copy2(src, dest)
            copied += 1
            labels_used.append(label)

        print(f"  ✅ '{folder_name}' → {label}: {len(os.listdir(src_dir))} images")

    print(f"\n[KAGGLE1] Total copied: {copied} | Skipped folders: {skipped}")
    print("\nClass distribution added:")
    for cls, cnt in sorted(Counter(labels_used).items()):
        print(f"  {cls}: {cnt}")

if __name__ == "__main__":
    print("=" * 50)
    print("  Kaggle Dataset 1: Dental OPG XRAY → train/")
    print("=" * 50)
    run()
    print("\n✅ Done!")