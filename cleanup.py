import os
import random

HEALTHY_DIR = r"C:\Users\DELL\Desktop\Shahzeb\FYP\DentAI_dataset\train\healthy"
TARGET_MAX  = 800

all_files    = os.listdir(HEALTHY_DIR)
kaggle4_files = [f for f in all_files if f.startswith("kaggle4_")]
other_files   = [f for f in all_files if not f.startswith("kaggle4_")]

print(f"Total healthy     : {len(all_files)}")
print(f"  kaggle4 images  : {len(kaggle4_files)}")
print(f"  other images    : {len(other_files)}")

# How many kaggle4 images to KEEP
slots_for_kaggle4 = max(0, TARGET_MAX - len(other_files))
print(f"\nKeeping {len(other_files)} non-kaggle4 + {slots_for_kaggle4} kaggle4 = {len(other_files)+slots_for_kaggle4} total")

# Randomly select which kaggle4 to keep
random.seed(42)
keep   = set(random.sample(kaggle4_files, min(slots_for_kaggle4, len(kaggle4_files))))
remove = [f for f in kaggle4_files if f not in keep]

print(f"Deleting {len(remove)} excess kaggle4 healthy images...")
for f in remove:
    os.remove(os.path.join(HEALTHY_DIR, f))

final = os.listdir(HEALTHY_DIR)
print(f"\nHealthy class now: {len(final)} images ✅")