"""KrishiSetu AI - Model Architecture & Management.

This module defines the ResNet18 transfer learning backbone, model initialization,
parameter freezing, device resolution (CUDA GPU vs. CPU fallback), and serialization.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import torch
import torch.nn as nn
from torchvision import models


def get_device(preferred: Optional[str] = None) -> torch.device:
    """Resolve compute device prioritizing CUDA GPU on Colab with seamless CPU fallback."""
    if preferred and preferred.lower() == "cpu":
        return torch.device("cpu")
    if preferred and preferred.lower() == "cuda":
        if torch.cuda.is_available():
            return torch.device("cuda")
        print("[WARNING] CUDA requested but not available. Falling back to CPU.")
        return torch.device("cpu")

    # Auto mode
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def build_model(
    num_classes: int,
    pretrained: bool = True,
    freeze_backbone: bool = False
) -> nn.Module:
    """Build ResNet18 transfer learning classifier tailored for PlantVillage classes.

    Args:
        num_classes: Number of disease categories in dataset (e.g., 38 for PlantVillage).
        pretrained: If True, initialize with ImageNet pre-trained weights.
        freeze_backbone: If True, freeze feature extraction layers and only train linear head.
    """
    weights = models.ResNet18_Weights.DEFAULT if pretrained else None
    model = models.resnet18(weights=weights)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace ImageNet 1000-class head with our custom plant pathogen classification head
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    return model


def get_model_summary(model: nn.Module) -> Dict[str, Any]:
    """Calculate parameter counts and approximate memory size."""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    param_size_mb = (total_params * 4) / (1024 * 1024)  # 4 bytes per float32 parameter

    return {
        "architecture": "ResNet18",
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "frozen_parameters": total_params - trainable_params,
        "parameter_size_mb": round(param_size_mb, 2),
    }


def save_model_artifacts(
    model: nn.Module,
    output_dir: str,
    class_names: List[str],
    metadata: Optional[Dict[str, Any]] = None,
    filename: str = "resnet18_plantvillage.pt"
) -> Dict[str, str]:
    """Save PyTorch weights, class mapping, and metadata to the output directory."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    weights_file = out_path / filename
    mapping_file = out_path / "class_mapping.json"
    metadata_file = out_path / "model_metadata.json"

    # 1. Save PyTorch state dictionary
    torch.save(model.state_dict(), weights_file)

    # 2. Save class index mapping
    idx_to_class = {idx: name for idx, name in enumerate(class_names)}
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}
    mapping_data = {
        "num_classes": len(class_names),
        "class_names": class_names,
        "idx_to_class": idx_to_class,
        "class_to_idx": class_to_idx,
    }
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(mapping_data, f, indent=2)

    # 3. Save training metadata
    meta = metadata or {}
    meta.update({
        "architecture": "ResNet18",
        "num_classes": len(class_names),
        "weights_file": filename,
        "input_size": [3, 224, 224],
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        }
    })
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return {
        "weights_path": str(weights_file),
        "mapping_path": str(mapping_file),
        "metadata_path": str(metadata_file),
    }


def load_model(
    weights_path: str,
    num_classes: int,
    device: Union[str, torch.device] = "cpu"
) -> nn.Module:
    """Load trained ResNet18 model for CPU inference or continued training."""
    dev = torch.device(device) if isinstance(device, str) else device
    model = build_model(num_classes=num_classes, pretrained=False)

    # Use mmap=True for zero-copy memory mapping on memory-constrained systems
    state_dict = torch.load(weights_path, map_location=dev, mmap=True, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(dev)
    model.eval()

    return model
