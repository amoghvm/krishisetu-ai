"""KrishiSetu AI - Dataset Pipeline & Preprocessing.

This module provides data loading, augmentation pipelines, and dataset inspection
utilities for the PlantVillage crop disease dataset.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image

import torch
from torch.utils.data import DataLoader, Dataset, Subset, random_split
from torchvision import transforms, datasets


# Standard ImageNet normalization constants (required for pre-trained ResNet18)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_train_transforms(image_size: int = 224) -> transforms.Compose:
    """Augmentation pipeline for training to prevent overfitting and improve field robustness."""
    return transforms.Compose([
        transforms.Resize((int(image_size * 1.14), int(image_size * 1.14))),
        transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_val_transforms(image_size: int = 224) -> transforms.Compose:
    """Deterministic validation/test preprocessing pipeline."""
    return transforms.Compose([
        transforms.Resize((int(image_size * 1.14), int(image_size * 1.14))),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


class TransformedSubset(Dataset):
    """Wrapper to apply specific transforms to a Subset of an ImageFolder."""

    def __init__(self, subset: Subset, transform: transforms.Compose):
        self.subset = subset
        self.transform = transform

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int]:
        image, target = self.subset[index]
        if self.transform is not None:
            image = self.transform(image)
        return image, target

    def __len__(self) -> int:
        return len(self.subset)


class RawImageFolder(Dataset):
    """ImageFolder that loads raw PIL images without transform (used with TransformedSubset)."""

    def __init__(self, root: str):
        self.inner = datasets.ImageFolder(root=root, transform=None)
        self.classes = self.inner.classes
        self.class_to_idx = self.inner.class_to_idx
        self.imgs = self.inner.imgs

    def __getitem__(self, index: int) -> Tuple[Image.Image, int]:
        path, target = self.imgs[index]
        with open(path, "rb") as f:
            img = Image.open(f).convert("RGB")
        return img, target

    def __len__(self) -> int:
        return len(self.inner)


def inspect_dataset(data_dir: str) -> Dict[str, Any]:
    """Inspect dataset directory structure, class balance, and image integrity."""
    path = Path(data_dir)
    if not path.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {data_dir}")

    # Check if directory has train/val structure or flat class folders
    subdirs = [p for p in path.iterdir() if p.is_dir()]
    is_split = any(p.name in ["train", "val", "test"] for p in subdirs)

    scan_target = path / "train" if (path / "train").exists() else path

    class_dirs = [p for p in scan_target.iterdir() if p.is_dir() and not p.name.startswith(".")]
    class_dirs.sort(key=lambda p: p.name)

    stats: Dict[str, Any] = {
        "dataset_path": str(path.resolve()),
        "is_pre_split": is_split,
        "num_classes": len(class_dirs),
        "classes": [],
        "total_images": 0,
        "class_distribution": {},
        "corrupted_images": []
    }

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for cdir in class_dirs:
        class_name = cdir.name
        img_files = [f for f in cdir.iterdir() if f.suffix.lower() in valid_extensions]
        count = len(img_files)
        stats["classes"].append(class_name)
        stats["class_distribution"][class_name] = count
        stats["total_images"] += count

        # Spot-check image integrity on a sample
        for img_path in img_files[:5]:
            try:
                with Image.open(img_path) as im:
                    im.verify()
            except Exception as e:
                stats["corrupted_images"].append({"file": str(img_path), "error": str(e)})

    return stats


def create_dataloaders(
    data_dir: str,
    batch_size: int = 32,
    image_size: int = 224,
    num_workers: int = 0,
    val_split: float = 0.15,
    test_split: float = 0.15,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader, List[str], Dict[str, int]]:
    """Build train, val, and test DataLoaders with stratified/random split and augmentations."""
    path = Path(data_dir)
    train_dir = path / "train"
    val_dir = path / "val"
    test_dir = path / "test"

    train_transform = get_train_transforms(image_size)
    val_transform = get_val_transforms(image_size)

    # Mode 1: Directory already pre-split into train / val / test
    if train_dir.exists() and val_dir.exists():
        train_dataset = datasets.ImageFolder(str(train_dir), transform=train_transform)
        val_dataset = datasets.ImageFolder(str(val_dir), transform=val_transform)

        if test_dir.exists():
            test_dataset = datasets.ImageFolder(str(test_dir), transform=val_transform)
        else:
            test_dataset = val_dataset

        class_names = train_dataset.classes
        class_to_idx = train_dataset.class_to_idx

    # Mode 2: Flat directory of class folders -> perform split
    else:
        raw_dataset = RawImageFolder(str(path))
        class_names = raw_dataset.classes
        class_to_idx = raw_dataset.class_to_idx

        total_len = len(raw_dataset)
        val_len = int(total_len * val_split)
        test_len = int(total_len * test_split)
        train_len = total_len - val_len - test_len

        generator = torch.Generator().manual_seed(seed)
        train_sub, val_sub, test_sub = random_split(
            raw_dataset, [train_len, val_len, test_len], generator=generator
        )

        train_dataset = TransformedSubset(train_sub, train_transform)
        val_dataset = TransformedSubset(val_sub, val_transform)
        test_dataset = TransformedSubset(test_sub, val_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )

    return train_loader, val_loader, test_loader, class_names, class_to_idx
