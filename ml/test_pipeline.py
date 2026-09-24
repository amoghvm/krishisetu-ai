"""KrishiSetu AI - End-to-End Pipeline Smoke Test.

Validates that:
1. inspect_dataset reads and validates class distributions.
2. create_dataloaders properly splits data and applies augmentations.
3. train.py runs 1 epoch on CPU, calculates loss, and exports weights + mapping.
4. evaluate.py loads the exported weights and computes accuracy + confusion matrix.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
from pathlib import Path

# Add ml folder to path
sys.path.insert(0, str(Path(__file__).parent))

from dataset import inspect_dataset, create_dataloaders
from model import build_model, get_model_summary, load_model
from train import run_training
from evaluate import run_evaluation
import argparse

def main():
    print("=== STEP 1: Verify Dataset Inspection ===")
    stats = inspect_dataset("data/smoke_test")
    print(f"Detected {stats['num_classes']} classes, {stats['total_images']} images.")
    assert stats['num_classes'] == 8, f"Expected 8 classes, got {stats['num_classes']}"
    assert stats['total_images'] == 80, f"Expected 80 images, got {stats['total_images']}"
    print("-> Inspection passed.")

    print("\n=== STEP 2: Verify DataLoader Creation ===")
    tr, val, te, class_names, class_to_idx = create_dataloaders(
        "data/smoke_test", batch_size=4, seed=42
    )
    print(f"Train samples: {len(tr.dataset)}, Val samples: {len(val.dataset)}, Test samples: {len(te.dataset)}")
    batch_img, batch_target = next(iter(tr))
    print(f"Batch image shape: {batch_img.shape}, Batch target shape: {batch_target.shape}")
    assert batch_img.shape == (4, 3, 224, 224), f"Unexpected shape {batch_img.shape}"
    print("-> DataLoader passed.")

    print("\n=== STEP 3: Verify Model Build & Summary ===")
    model = build_model(num_classes=8, pretrained=False)
    summary = get_model_summary(model)
    print(f"Parameters: {summary['total_parameters']:,} ({summary['parameter_size_mb']} MB)")
    assert summary['trainable_parameters'] > 10_000_000, "Unexpected param count"
    print("-> Model build passed.")

    print("\n=== STEP 4: Verify Training Pipeline (1 Epoch on CPU) ===")
    train_args = argparse.Namespace(
        data_dir="data/smoke_test",
        output_dir="models",
        epochs=1,
        batch_size=4,
        lr=0.001,
        weight_decay=1e-4,
        image_size=224,
        val_split=0.20,
        test_split=0.20,
        device="cpu",
        pretrained=False,
        freeze_backbone=False,
        patience=2,
        seed=42
    )
    train_res = run_training(train_args)
    print(f"Training run completed with train_loss={train_res['history']['train_loss'][0]:.4f}")
    assert Path("models/resnet18_plantvillage.pt").exists(), "Weights file not created"
    assert Path("models/class_mapping.json").exists(), "Class mapping not created"
    assert Path("models/model_metadata.json").exists(), "Metadata not created"
    print("-> Training execution & export passed.")

    print("\n=== STEP 5: Verify Evaluation Pipeline ===")
    eval_res = run_evaluation(
        weights_path="models/resnet18_plantvillage.pt",
        mapping_path="models/class_mapping.json",
        data_dir="data/smoke_test",
        output_report_path="models/evaluation_report.json",
        confidence_threshold=0.60,
        device="cpu"
    )
    print(f"Evaluation completed. Accuracy: {eval_res['overall_accuracy'] * 100:.2f}%")
    assert "confusion_matrix" in eval_res, "Confusion matrix missing"
    assert "per_class_report" in eval_res, "Class report missing"
    print("-> Evaluation passed.")

    print("\n[ALL PIPELINE CHECKS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    main()
