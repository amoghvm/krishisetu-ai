# KrishiSetu AI - Machine Learning & Training Pipeline

## Overview
This directory houses the reproducible training pipelines, evaluation harnesses, data preprocessing scripts, and Google Colab notebooks for KrishiSetu AI's disease classification models.

## ML Architecture Principles
1. **Decoupled System**:
   - **Disease Classifier (Image Model)**: Answers *"What is this pathogen/disease on the leaf?"*
   - **Risk Engine**: Answers *"What might happen given micro-climate and historical risk factors?"*
   - These two systems are kept completely independent and are never conflated into an artificial combined model.
2. **Official Dataset**:
   - PlantVillage is the official hackathon dataset for crop disease classification.
   - **Dataset Limitations**: PlantVillage consists of laboratory/controlled setting images. Validation accuracy on PlantVillage does *not* equate to guaranteed field accuracy.
   - Low-confidence predictions (< threshold) will be handled safely by the inference engine with user prompts to capture clearer imagery.
3. **Training & Compute Constraints**:
   - Primary Training: Executed on Google Colab GPU (NVIDIA T4 / V100).
   - Local Fallback: Fully reproducible on standard 8 GB RAM developer machines using CPU execution.
   - Baseline Architecture: **ResNet18** with PyTorch / Torchvision transfer learning (pre-trained on ImageNet).
   - Inference Architecture: Designed for low-latency CPU evaluation (< 250ms) within the shared FastAPI backend.

## Contents (Planned for Phase 1)
- `train.py`: CLI training script with configurable hyperparameters and device detection (`cuda` vs `cpu`).
- `evaluate.py`: Model evaluation script computing per-class metrics, confusion matrices, Precision, Recall, and F1.
- `dataset.py`: PyTorch `Dataset` and `DataLoader` with augmentations.
- `notebooks/krishisetu_training_colab.ipynb`: One-click reproducible Google Colab training notebook.

## Current Status
**Phase 0 - Architectural Foundation.** No training code or weights are implemented. Training will begin in Phase 1 upon confirmation.
