import json
import os
import shutil
from collections import Counter

# ── CONFIG ──────────────────────────────────────────────────────
DENTEX_ROOT = r"C:\Users\DELL\Desktop\Shahzeb\DATASETS\Huggingface"
OUTPUT_DIR  = r"C:\Users\DELL\Desktop\Shahzeb\FYP\DentAI_dataset"
# ───────────────────────────────────────────────────────────────

LABEL_MAP_TRIPLE = {
    0: "impacted",
    1: "cavity",
    2: "infection",
    3: "cavity",       # Deep Caries
}

# Turkish keyword → unified class
# label format: "quadrant-keyword-tooth"  e.g. "1-çürük-26"
TURKISH_LABEL_MAP = {
    "çürük":        "cavity",       # caries
    "derin-çürük":  "cavity",       # deep caries
    "kanal":        "infection",    # root canal / periapical lesion
    "apse":         "infection",    # abscess
    "gömülü":       "impacted",     # impacted tooth
    "kron":         "other",        # crown/broken
    "eksik":        "healthy",      # missing tooth - skip or healthy
    "kırık":        "other",       # fractured tooth
    "küretaj":      "infection",   # curettage = gum/bone infection
    "çekim":        "other",       # extraction needed
    "lezyon":       "infection",   # periapical lesion
    "saglam":         "healthy",
}

PRIORITY = {"impacted": 4, "infection": 3, "cavity": 2, "other": 1, "healthy": 0}


def copy_image(src_path, output_split, label, prefix="dentex"):
    dest_dir = os.path.join(OUTPUT_DIR, output_split, label)
    os.makedirs(dest_dir, exist_ok=True)
    fname = os.path.basename(src_path)
    dest  = os.path.join(dest_dir, f"{prefix}_{fname}")
    if os.path.exists(src_path):
        shutil.copy2(src_path, dest)
        return True
    return False


def best_label_triple(annotations):
    chosen = None
    for ann in annotations:
        label = LABEL_MAP_TRIPLE.get(ann.get("category_id_3"))
        if label is None:
            continue
        if chosen is None or PRIORITY[label] > PRIORITY[chosen]:
            chosen = label
    return chosen


def parse_turkish_label(raw_label):
    """
    Parse label strings like:
      '1-çürük-26'       → cavity
      '6-gömülü-38'      → impacted
      '3-kanal-36'       → infection
      '2-derin-çürük-14' → cavity
    """
    parts = raw_label.lower().strip().split("-")

    # Try two-word disease names first (e.g. 'derin-çürük')
    for i in range(len(parts) - 1):
        two_word = f"{parts[i]}-{parts[i+1]}"
        if two_word in TURKISH_LABEL_MAP:
            return TURKISH_LABEL_MAP[two_word]

    # Then single-word disease names
    for part in parts:
        if part in TURKISH_LABEL_MAP:
            return TURKISH_LABEL_MAP[part]

    return None  # unknown label


def best_label_turkish(shapes):
    """Pick the highest-priority label from all shapes in a test JSON."""
    chosen = None
    for shape in shapes:
        raw   = shape.get("label", "")
        label = parse_turkish_label(raw)
        if label is None or label == "healthy":
            continue
        if chosen is None or PRIORITY[label] > PRIORITY[chosen]:
            chosen = label
    return chosen if chosen else "healthy"


# ── PART 1: Training ────────────────────────────────────────────
def convert_train():
    img_dir  = os.path.join(DENTEX_ROOT,
                "training_data", "training_data",
                "quadrant-enumeration-disease", "xrays")
    ann_file = os.path.join(DENTEX_ROOT,
                "training_data", "training_data",
                "quadrant-enumeration-disease",
                "train_quadrant_enumeration_disease.json")

    if not os.path.exists(ann_file):
        print(f"[TRAIN] ❌ Not found: {ann_file}")
        return

    with open(ann_file, encoding="utf-8") as f:
        data = json.load(f)

    id_to_file = {img["id"]: img["file_name"] for img in data["images"]}
    id_to_anns = {}
    for ann in data["annotations"]:
        id_to_anns.setdefault(ann["image_id"], []).append(ann)

    copied, skipped, labels_used = 0, 0, []

    for img_id, anns in id_to_anns.items():
        label    = best_label_triple(anns)
        filename = id_to_file.get(img_id)
        if not label or not filename:
            skipped += 1
            continue
        src = os.path.join(img_dir, filename)
        if copy_image(src, "train", label, "dentex_train"):
            copied += 1
            labels_used.append(label)
        else:
            skipped += 1

    print(f"\n[TRAIN] ✅ Copied: {copied} | ⚠ Skipped: {skipped}")
    for cls, cnt in sorted(Counter(labels_used).items()):
        print(f"         {cls}: {cnt}")


# ── PART 2: Validation ──────────────────────────────────────────
def convert_val():
    img_dir  = os.path.join(DENTEX_ROOT,
                "validation_data", "validation_data",
                "quadrant_enumeration_disease", "xrays")
    ann_file = os.path.join(DENTEX_ROOT, "validation_triple.json")

    if not os.path.exists(ann_file):
        print(f"[VAL] ❌ Not found: {ann_file}")
        return

    with open(ann_file, encoding="utf-8") as f:
        data = json.load(f)

    id_to_file = {img["id"]: img["file_name"] for img in data["images"]}
    id_to_anns = {}
    for ann in data["annotations"]:
        id_to_anns.setdefault(ann["image_id"], []).append(ann)

    copied, skipped, labels_used = 0, 0, []

    for img_id, anns in id_to_anns.items():
        label    = best_label_triple(anns)
        filename = id_to_file.get(img_id)
        if not label or not filename:
            skipped += 1
            continue
        src = os.path.join(img_dir, filename)
        if copy_image(src, "val", label, "dentex_val"):
            copied += 1
            labels_used.append(label)
        else:
            skipped += 1

    print(f"\n[VAL] ✅ Copied: {copied} | ⚠ Skipped: {skipped}")
    for cls, cnt in sorted(Counter(labels_used).items()):
        print(f"       {cls}: {cnt}")


# ── PART 3: Test (Turkish per-file JSON format) ─────────────────
def convert_test():
    img_dir   = os.path.join(DENTEX_ROOT, "test_data", "disease", "input")
    label_dir = os.path.join(DENTEX_ROOT, "test_data", "disease", "label")

    if not os.path.exists(label_dir):
        print(f"[TEST] ❌ Label folder not found: {label_dir}")
        return

    copied, skipped, labels_used = 0, 0, []
    unknown_keywords = set()  # collect any Turkish words we don't recognize

    for json_file in sorted(os.listdir(label_dir)):
        if not json_file.endswith(".json"):
            continue

        json_path = os.path.join(label_dir, json_file)
        img_name  = json_file.replace(".json", ".png")
        src       = os.path.join(img_dir, img_name)

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            skipped += 1
            continue

        shapes = data.get("shapes", [])

        # Collect unknown keywords for debugging
        for shape in shapes:
            raw   = shape.get("label", "")
            parts = raw.lower().strip().split("-")
            for p in parts:
                if p not in TURKISH_LABEL_MAP and not p.isdigit():
                    unknown_keywords.add(p)

        label = best_label_turkish(shapes)

        if copy_image(src, "test", label, "dentex_test"):
            copied += 1
            labels_used.append(label)
        else:
            skipped += 1

    print(f"\n[TEST] ✅ Copied: {copied} | ⚠ Skipped: {skipped}")
    for cls, cnt in sorted(Counter(labels_used).items()):
        print(f"        {cls}: {cnt}")

    if unknown_keywords:
        print(f"\n  ⚠ Unrecognized Turkish keywords found: {unknown_keywords}")
        print("    → Paste these here and I'll add mappings for them.")


# ── MAIN ────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 52)
    print("   DENTEX → Unified Class Folders Converter")
    print("=" * 52)
    convert_train()
    convert_val()
    convert_test()
    print("\n" + "=" * 52)
    print("✅ ALL DONE! Output folder:", OUTPUT_DIR)
    print("=" * 52)