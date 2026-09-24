# KrishiSetu AI - Model Registry & Artifacts

## Model File Storage Policy
Model weights and large binary checkpoint files are **excluded from Git tracking** via `.gitignore` to keep the repository lightweight and adhere to software engineering best practices.

### Artifact Specifications
- **Expected Artifact Name**: `resnet18_plantvillage.pt` (TorchScript or state_dict format)
- **Class Label Mapping**: `class_mapping.json` (maps integer class index to crop species and disease names)
- **Metadata**: `model_metadata.json` (records model architecture, training timestamp, validation metrics, input resolution, normalization mean/std)

### Distribution & Loading Strategy
- Model weights generated from Google Colab or local training will be downloaded into this directory.
- For local development and demonstration, a lightweight benchmark checkpoint or automated download script will be provided.
- The backend dynamically verifies the presence and integrity of `models/resnet18_plantvillage.pt` at boot time.
