"""KrishiSetu AI - Model Training Pipeline.

Reproducible PyTorch training script for ResNet18 transfer learning on the PlantVillage dataset.
Supports NVIDIA CUDA GPU execution (Google Colab) with automatic CPU fallback.
"""

import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Tuple

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from tqdm import tqdm

from dataset import create_dataloaders, inspect_dataset
from model import build_model, get_device, get_model_summary, save_model_artifacts


def train_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device
) -> Tuple[float, float]:
    """Train the model for one full epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc="Training", leave=False, dynamic_ncols=True)
    for images, targets in pbar:
        images = images.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

        pbar.set_postfix({
            "loss": f"{loss.item():.4f}",
            "acc": f"{correct / total:.4f}"
        })

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


def validate_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Tuple[float, float]:
    """Evaluate the model on validation split."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, targets in dataloader:
            images = images.to(device)
            targets = targets.to(device)

            outputs = model(images)
            loss = criterion(outputs, targets)

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == targets).sum().item()
            total += targets.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


def run_training(args: argparse.Namespace) -> Dict[str, Any]:
    """Main training execution function."""
    torch.manual_seed(args.seed)
    device = get_device(args.device)

    print("=" * 60)
    print("KrishiSetu AI - ResNet18 Training Pipeline")
    print(f"Device: {device} | CUDA Available: {torch.cuda.is_available()}")
    print(f"Dataset Path: {args.data_dir}")
    print("=" * 60)

    # 1. Dataset Inspection & Dataloader creation
    stats = inspect_dataset(args.data_dir)
    print(f"Detected {stats['num_classes']} classes across {stats['total_images']} images.")

    train_loader, val_loader, test_loader, class_names, class_to_idx = create_dataloaders(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        image_size=args.image_size,
        val_split=args.val_split,
        test_split=args.test_split,
        seed=args.seed
    )

    print(f"Dataset splits: Train={len(train_loader.dataset)} | Val={len(val_loader.dataset)} | Test={len(test_loader.dataset)}")

    # 2. Build model architecture
    model = build_model(
        num_classes=len(class_names),
        pretrained=args.pretrained,
        freeze_backbone=args.freeze_backbone
    )
    model.to(device)

    summary = get_model_summary(model)
    print(f"Model Summary: {summary['trainable_parameters']:,} trainable / {summary['total_parameters']:,} total parameters ({summary['parameter_size_mb']} MB)")

    # 3. Optimization Setup
    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr,
        weight_decay=args.weight_decay
    )
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)

    # 4. Training Loop
    best_val_loss = float("inf")
    best_val_acc = 0.0
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    epochs_no_improve = 0

    start_time = time.time()

    for epoch in range(1, args.epochs + 1):
        epoch_start = time.time()

        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate_one_epoch(model, val_loader, criterion, device)

        scheduler.step(val_loss)

        epoch_duration = time.time() - epoch_start
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        print(
            f"Epoch [{epoch:02d}/{args.epochs:02d}] ({epoch_duration:.1f}s) "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc * 100:.2f}% | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc * 100:.2f}%"
        )

        # Check for improvement
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_acc = val_acc
            epochs_no_improve = 0

            # Save best checkpoint
            save_model_artifacts(
                model=model,
                output_dir=args.output_dir,
                class_names=class_names,
                filename="resnet18_plantvillage.pt",
                metadata={
                    "best_epoch": epoch,
                    "val_loss": round(best_val_loss, 4),
                    "val_accuracy": round(best_val_acc, 4),
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "hyperparameters": {
                        "epochs": args.epochs,
                        "batch_size": args.batch_size,
                        "lr": args.lr,
                        "weight_decay": args.weight_decay,
                        "seed": args.seed,
                        "device": str(device),
                    }
                }
            )
            print(f" -> Best checkpoint saved to {args.output_dir}/ (Val Acc: {best_val_acc * 100:.2f}%)")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= args.patience:
                print(f"[INFO] Early stopping triggered after {epoch} epochs (no improvement for {args.patience} epochs).")
                break

    total_training_time = time.time() - start_time
    print("=" * 60)
    print(f"Training completed in {total_training_time / 60:.2f} minutes.")
    print(f"Best Validation Loss: {best_val_loss:.4f} | Best Validation Accuracy: {best_val_acc * 100:.2f}%")
    print("=" * 60)

    return {
        "best_val_loss": best_val_loss,
        "best_val_acc": best_val_acc,
        "history": history,
        "class_names": class_names,
        "total_training_time_seconds": round(total_training_time, 2)
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="KrishiSetu AI - ResNet18 Training on PlantVillage")
    parser.add_argument("--data-dir", type=str, default="data/processed", help="Path to dataset root folder")
    parser.add_argument("--output-dir", type=str, default="models", help="Directory to export model weights and mappings")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Mini-batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Initial learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="AdamW weight decay")
    parser.add_argument("--image-size", type=int, default=224, help="Input image dimension (pixels)")
    parser.add_argument("--val-split", type=float, default=0.15, help="Validation split proportion")
    parser.add_argument("--test-split", type=float, default=0.15, help="Test split proportion")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu"], help="Compute device")
    parser.add_argument("--pretrained", action="store_true", default=True, help="Use ImageNet pre-trained weights")
    parser.add_argument("--freeze-backbone", action="store_true", default=False, help="Freeze backbone feature extractor")
    parser.add_argument("--patience", type=int, default=4, help="Early stopping patience")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_training(args)
