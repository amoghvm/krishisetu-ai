"""KrishiSetu AI - Model Evaluation & Verification Harness.

Computes comprehensive performance metrics on test/validation splits:
- Top-1 Accuracy
- Macro and Weighted Precision, Recall, and F1-Scores
- Per-class classification report
- Confusion Matrix (stored as JSON and matrix breakdown)
- Low-confidence prediction distribution (< threshold)
"""

import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support
)
from tqdm import tqdm

from dataset import create_dataloaders
from model import load_model, get_device


def evaluate_model(
    model: torch.nn.Module,
    test_loader: torch.utils.data.DataLoader,
    class_names: List[str],
    device: torch.device,
    confidence_threshold: float = 0.60
) -> Dict[str, Any]:
    """Execute model evaluation across the test DataLoader."""
    model.eval()
    all_preds = []
    all_targets = []
    all_confidences = []

    print("[INFO] Running evaluation on test set...")
    with torch.no_grad():
        for images, targets in tqdm(test_loader, desc="Evaluating", dynamic_ncols=True):
            images = images.to(device)
            outputs = model(images)
            probs = F.softmax(outputs, dim=1)

            confidences, preds = torch.max(probs, dim=1)

            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(targets.numpy().tolist())
            all_confidences.extend(confidences.cpu().numpy().tolist())

    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)
    confs = np.array(all_confidences)

    # 1. Top-1 Accuracy
    accuracy = float(accuracy_score(y_true, y_pred))

    # 2. Precision, Recall, F1 (macro and weighted)
    labels = list(range(len(class_names)))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="weighted", zero_division=0
    )

    # 3. Per-class metrics
    class_report_dict = classification_report(
        y_true, y_pred, labels=labels, target_names=class_names, output_dict=True, zero_division=0
    )

    # 4. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))

    # 5. Confidence Distribution Analysis (Safe Low-Confidence Handling)
    low_conf_mask = confs < confidence_threshold
    num_low_conf = int(np.sum(low_conf_mask))
    low_conf_pct = float(num_low_conf / len(confs) * 100) if len(confs) > 0 else 0.0

    # Accuracy on high-confidence vs low-confidence subsets
    high_conf_acc = (
        float(accuracy_score(y_true[~low_conf_mask], y_pred[~low_conf_mask]))
        if np.sum(~low_conf_mask) > 0 else 0.0
    )

    results: Dict[str, Any] = {
        "overall_accuracy": round(accuracy, 4),
        "macro_precision": round(float(p_macro), 4),
        "macro_recall": round(float(r_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "weighted_precision": round(float(p_weighted), 4),
        "weighted_recall": round(float(r_weighted), 4),
        "weighted_f1": round(float(f1_weighted), 4),
        "confidence_threshold": confidence_threshold,
        "total_test_samples": len(confs),
        "low_confidence_samples": num_low_conf,
        "low_confidence_percentage": round(low_conf_pct, 2),
        "high_confidence_accuracy": round(high_conf_acc, 4),
        "mean_confidence": round(float(np.mean(confs)), 4),
        "per_class_report": class_report_dict,
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
    }

    return results


def print_evaluation_summary(results: Dict[str, Any]):
    """Print readable evaluation summary to console."""
    print("\n" + "=" * 65)
    print("KRISHISETU AI - MODEL EVALUATION METRICS REPORT")
    print("=" * 65)
    print(f"Total Test Samples:       {results['total_test_samples']}")
    print(f"Overall Accuracy:         {results['overall_accuracy'] * 100:.2f}%")
    print(f"Weighted F1-Score:        {results['weighted_f1'] * 100:.2f}%")
    print(f"Macro F1-Score:           {results['macro_f1'] * 100:.2f}%")
    print(f"Macro Precision:          {results['macro_precision'] * 100:.2f}%")
    print(f"Macro Recall:             {results['macro_recall'] * 100:.2f}%")
    print(f"Mean Prediction Conf:     {results['mean_confidence'] * 100:.2f}%")
    print("-" * 65)
    print("Safe Low-Confidence Handling (< threshold):")
    print(f"Threshold:                {results['confidence_threshold']}")
    print(f"Low-Confidence Flagged:   {results['low_confidence_samples']} ({results['low_confidence_percentage']}%)")
    print(f"High-Confidence Accuracy: {results['high_confidence_accuracy'] * 100:.2f}%")
    print("=" * 65 + "\n")


def run_evaluation(
    weights_path: str,
    mapping_path: str,
    data_dir: str,
    output_report_path: str = "models/evaluation_report.json",
    confidence_threshold: float = 0.60,
    batch_size: int = 16,
    device: str = "auto"
) -> Dict[str, Any]:
    """Load model, mapping, dataset and run full evaluation."""
    dev = get_device(device)

    # 1. Load class mapping
    if not Path(mapping_path).exists():
        raise FileNotFoundError(f"Class mapping file not found: {mapping_path}")

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)
    class_names = mapping_data["class_names"]

    # 2. Load model
    print(f"[INFO] Loading model from {weights_path} onto {dev}...")
    model = load_model(weights_path=weights_path, num_classes=len(class_names), device=dev)

    # 3. Create test dataloader
    _, _, test_loader, _, _ = create_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
        num_workers=0
    )

    # 4. Evaluate
    results = evaluate_model(
        model=model,
        test_loader=test_loader,
        class_names=class_names,
        device=dev,
        confidence_threshold=confidence_threshold
    )

    print_evaluation_summary(results)

    # 5. Save report
    out_file = Path(output_report_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[INFO] Full evaluation report written to {out_file}")

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="KrishiSetu AI - Model Evaluation Harness")
    parser.add_argument("--weights", type=str, default="models/resnet18_plantvillage.pt", help="Path to model weights (.pt)")
    parser.add_argument("--mapping", type=str, default="models/class_mapping.json", help="Path to class_mapping.json")
    parser.add_argument("--data-dir", type=str, default="data/processed", help="Path to dataset folder")
    parser.add_argument("--output", type=str, default="models/evaluation_report.json", help="Path to export evaluation report")
    parser.add_argument("--batch-size", type=int, default=16, help="Evaluation batch size")
    parser.add_argument("--threshold", type=float, default=0.60, help="Confidence cutoff threshold")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu"], help="Compute device")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_evaluation(
        weights_path=args.weights,
        mapping_path=args.mapping,
        data_dir=args.data_dir,
        output_report_path=args.output,
        confidence_threshold=args.threshold,
        batch_size=args.batch_size,
        device=args.device
    )
