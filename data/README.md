# KrishiSetu AI - Data Directory

## Data Management & Dataset Policy
In compliance with project requirements, **no raw or processed datasets are committed to Git**. The `.gitignore` excludes all large image archives, CSVs, and bulk directories.

## Directory Layout
- `data/raw/` *(Git Ignored)*: Raw downloaded archives (e.g., PlantVillage dataset zip/tar files).
- `data/processed/` *(Git Ignored)*: Train/Val/Test image folders split according to pipeline requirements.
- `data/samples/`: Small set of representative evaluation test images (royalty-free/licensed) for automated regression testing and offline demo modes.

## Dataset Guidelines: PlantVillage
- PlantVillage is the official reference dataset for KrishiSetu AI's disease classification model.
- Download instructions, automated extraction scripts, and preprocessing pipelines will be introduced in Phase 1.
- **Privacy Notice**: Real farmer images uploaded through the app are stored in a secure upload directory with privacy guardrails and are strictly isolated from general training sets until explicit consent and human validation protocols are met.
