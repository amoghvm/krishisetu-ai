"""KrishiSetu AI - Disease Classification Model Service."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DiseaseModelService:
    """Service for loading and running the disease classification model."""

    # Standard ImageNet normalization (same as training/eval pipeline)
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    # Supported image formats
    SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

    def __init__(self):
        self.settings = get_settings()
        # Resolve model path relative to project root (parent of backend/)
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.model: Optional[nn.Module] = None
        self.class_mapping: Optional[Dict] = None
        self.class_names: Optional[List[str]] = None
        self.idx_to_class: Optional[Dict[int, str]] = None
        self.device: Optional[torch.device] = None
        self.transform: Optional[transforms.Compose] = None
        self._model_loaded = False
        self._load_error: Optional[str] = None

    def load_model(self) -> bool:
        """Load the model, class mapping, and prepare transforms."""
        try:
            # Resolve device
            device_str = self.settings.INFERENCE_DEVICE
            if device_str.lower() == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available, falling back to CPU")
                device_str = "cpu"
            self.device = torch.device(device_str)
            logger.info(f"Using device: {self.device}")

            # Load class mapping
            weights_path = self.project_root / self.settings.MODEL_WEIGHTS_PATH
            mapping_path = weights_path.parent / "class_mapping.json"

            if not weights_path.exists():
                self._load_error = f"Model weights not found at {weights_path}"
                logger.error(self._load_error)
                return False

            if not mapping_path.exists():
                self._load_error = f"Class mapping not found at {mapping_path}"
                logger.error(self._load_error)
                return False

            with open(mapping_path, "r", encoding="utf-8") as f:
                self.class_mapping = json.load(f)

            self.class_names = self.class_mapping["class_names"]
            self.idx_to_class = {int(k): v for k, v in self.class_mapping["idx_to_class"].items()}

            num_classes = self.class_mapping["num_classes"]
            if num_classes != self.settings.MODEL_NUM_CLASSES:
                logger.warning(f"Model has {num_classes} classes, expected {self.settings.MODEL_NUM_CLASSES}")

            # Build and load model
            self.model = self._build_model(num_classes)
            state_dict = torch.load(
                weights_path,
                map_location=self.device,
                mmap=True,
                weights_only=True
            )
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()

            # Prepare validation transforms (same as eval pipeline)
            self.transform = transforms.Compose([
                transforms.Resize((int(224 * 1.14), int(224 * 1.14))),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.IMAGENET_MEAN, std=self.IMAGENET_STD),
            ])

            self._model_loaded = True
            logger.info(f"Model loaded successfully: {num_classes} classes on {self.device}")
            return True

        except Exception as e:
            self._load_error = f"Failed to load model: {str(e)}"
            logger.exception(self._load_error)
            return False

    def _build_model(self, num_classes: int) -> nn.Module:
        """Build ResNet18 model architecture matching the trained model."""
        model = models.resnet18(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
        return model

    def is_loaded(self) -> bool:
        """Check if model is loaded and ready."""
        return self._model_loaded

    def get_load_error(self) -> Optional[str]:
        """Get the last load error if any."""
        return self._load_error

    def validate_image(self, image: Image.Image) -> Tuple[bool, Optional[str]]:
        """Validate image format and integrity."""
        if image.format not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {image.format}. Supported: {', '.join(self.SUPPORTED_FORMATS)}"

        try:
            # Verify image integrity by loading it fully
            image.load()
        except Exception as e:
            return False, f"Corrupted or invalid image: {str(e)}"

        return True, None

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for model inference."""
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Apply transforms
        tensor = self.transform(image)
        # Add batch dimension
        tensor = tensor.unsqueeze(0)
        return tensor

    def parse_class_name(self, class_name: str) -> Tuple[str, str]:
        """Parse raw class name into crop and disease."""
        if "___" in class_name:
            crop_part, disease_part = class_name.split("___", 1)
        else:
            crop_part = "Unknown"
            disease_part = class_name

        crop = crop_part.replace("_", " ").strip()
        disease = disease_part.replace("_", " ").strip()

        return crop, disease

    def predict(self, image: Image.Image) -> Dict:
        """
        Run inference on a single image.

        Returns:
            Dict with keys: class_name, crop, disease, confidence, low_confidence
        """
        if not self._model_loaded or self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Validate image
        is_valid, error = self.validate_image(image)
        if not is_valid:
            raise ValueError(error)

        # Preprocess
        input_tensor = self.preprocess_image(image)
        input_tensor = input_tensor.to(self.device)

        # Inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, dim=1)

        predicted_idx = predicted_idx.item()
        confidence = confidence.item()

        # Get class name
        class_name = self.idx_to_class.get(predicted_idx, f"Unknown_{predicted_idx}")
        crop, disease = self.parse_class_name(class_name)

        # Check confidence threshold
        threshold = self.settings.MODEL_CONFIDENCE_THRESHOLD
        low_confidence = confidence < threshold

        return {
            "class_name": class_name,
            "crop": crop,
            "disease": disease,
            "confidence": confidence,
            "low_confidence": low_confidence,
            "threshold": threshold,
        }

    def get_model_info(self) -> Dict:
        """Get model metadata for health/check endpoints."""
        return {
            "architecture": self.settings.MODEL_ARCHITECTURE,
            "version": self.settings.MODEL_VERSION,
            "num_classes": self.settings.MODEL_NUM_CLASSES,
            "input_size": self.settings.MODEL_INPUT_SIZE,
            "device": str(self.device) if self.device else "unknown",
        }


# Global model service instance
_model_service: Optional[DiseaseModelService] = None


def get_model_service() -> DiseaseModelService:
    """Get or create the global model service instance."""
    global _model_service
    if _model_service is None:
        _model_service = DiseaseModelService()
    return _model_service