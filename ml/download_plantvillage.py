"""KrishiSetu AI - PlantVillage Dataset Acquisition & Smoke-Test Utilities.

This module provides:
1. Utilities to verify or acquire the PlantVillage crop disease dataset.
2. A lightweight synthetic smoke-test data generator allowing full pipeline
   verification (DataLoader, Training, Evaluation, Model Export) locally on
   CPU without requiring a multi-gigabyte download on 8GB RAM hardware.
"""

import argparse
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image, ImageDraw


# Core representative classes used for local CPU smoke tests
SMOKE_TEST_CLASSES: List[str] = [
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
]


def generate_synthetic_leaf_image(class_name: str, size: int = 224, seed: int = 0) -> Image.Image:
    """Generate a synthetic leaf-like image with texture variations for pipeline smoke testing."""
    rng = np.random.default_rng(seed)

    # Base green leaf hue
    if "healthy" in class_name:
        bg_color = (rng.integers(30, 60), rng.integers(120, 190), rng.integers(30, 60))
    elif "Late_blight" in class_name:
        bg_color = (rng.integers(60, 90), rng.integers(70, 110), rng.integers(30, 50))  # dark watersoaked
    elif "Early_blight" in class_name:
        bg_color = (rng.integers(80, 120), rng.integers(100, 140), rng.integers(20, 40))  # brown concentric
    else:
        bg_color = (rng.integers(40, 70), rng.integers(100, 150), rng.integers(30, 60))

    img = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw vein patterns
    for _ in range(5):
        x1, y1 = rng.integers(20, size - 20), rng.integers(20, size - 20)
        x2, y2 = rng.integers(20, size - 20), rng.integers(20, size - 20)
        draw.line([(x1, y1), (x2, y2)], fill=(40, 120, 40), width=2)

    # Draw necrotic lesion spots for unhealthy classes
    if "healthy" not in class_name:
        num_spots = rng.integers(3, 8)
        for _ in range(num_spots):
            sx = rng.integers(30, size - 30)
            sy = rng.integers(30, size - 30)
            rad = rng.integers(5, 18)
            spot_color = (rng.integers(80, 130), rng.integers(40, 80), rng.integers(10, 40))
            draw.ellipse([sx - rad, sy - rad, sx + rad, sy + rad], fill=spot_color)

    return img


def create_smoke_test_dataset(output_dir: str = "data/smoke_test", images_per_class: int = 15) -> str:
    """Generate a lightweight synthetic dataset to verify training/evaluation pipelines on CPU."""
    out_path = Path(output_dir)
    if out_path.exists():
        shutil.rmtree(out_path)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Creating synthetic smoke-test dataset at {out_path}...")
    total = 0
    for c_idx, class_name in enumerate(SMOKE_TEST_CLASSES):
        c_dir = out_path / class_name
        c_dir.mkdir(parents=True, exist_ok=True)

        for i in range(images_per_class):
            seed = (c_idx * 1000) + i
            img = generate_synthetic_leaf_image(class_name, size=224, seed=seed)
            img.save(c_dir / f"leaf_{i:03d}.jpg", quality=90)
            total += 1

    print(f"[SUCCESS] Generated {total} synthetic images across {len(SMOKE_TEST_CLASSES)} classes.")
    return str(out_path)


def print_download_instructions():
    """Print instructions for acquiring the full official PlantVillage dataset."""
    instructions = """
================================================================================
PLANTVILLAGE DATASET ACQUISITION INSTRUCTIONS
================================================================================
The official PlantVillage dataset contains 54,306 images across 38 crop disease classes.

Because the full dataset is ~1.5 GB, it should be downloaded directly in Google Colab
or on your training machine:

Option A: Google Colab (Recommended)
-----------------------------------
Use our pre-configured notebook:
  ml/notebooks/krishisetu_colab_training.ipynb

Option B: Manual Kaggle CLI Download
------------------------------------
1. Ensure Kaggle API credentials are configured (~/.kaggle/kaggle.json).
2. Execute:
   kaggle datasets download -d emmarex/plantdisease -p data/raw --unzip
3. Organize into:
   data/processed/
      ├── Apple___Apple_scab/
      ├── Tomato___Late_blight/
      └── ...

Option C: Local Smoke Test (Lightweight CPU Verification)
--------------------------------------------------------
To test the entire training and evaluation pipeline on your local laptop without
downloading the full dataset:
   python ml/download_plantvillage.py --create-smoke-test

================================================================================
"""
    print(instructions)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="KrishiSetu AI - PlantVillage Dataset Utilities")
    parser.add_argument("--create-smoke-test", action="store_true", help="Generate lightweight synthetic test dataset for CPU verification")
    parser.add_argument("--output-dir", type=str, default="data/smoke_test", help="Destination folder for synthetic dataset")
    parser.add_argument("--images-per-class", type=int, default=15, help="Number of images per class for smoke test")
    parser.add_argument("--info", action="store_true", help="Display download instructions for full dataset")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.create_smoke_test:
        create_smoke_test_dataset(args.output_dir, args.images_per_class)
    else:
        print_download_instructions()
