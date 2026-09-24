# KrishiSetu AI 🌾🤖

> **Intelligent, Weather-Integrated Crop Disease Identification & Early Outbreak Risk Advisory**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Phase 0 Completed](https://img.shields.io/badge/Status-Phase%200%20Completed-brightgreen.svg)]()
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)]()
[![ML: PyTorch](https://img.shields.io/badge/ML-PyTorch-EE4C2C.svg)]()
[![Web: React + Tailwind](https://img.shields.io/badge/Web-React%20%7C%20Tailwind-38B2AC.svg)]()
[![Mobile: React Native + Expo](https://img.shields.io/badge/Mobile-Expo%20Android-000020.svg)]()

---

## 1. Problem Statement & Mission
**Hackathon Problem Statement:**
> *"Create an image recognition and weather-integrated model to identify leaf pathogens from field photos and predict local pest migration risks to minimize chemical pesticide usage."*

Smallholder farmers often struggle with delayed plant disease diagnosis, leading to prophylactic blanket pesticide application that escalates operational costs, fosters chemical resistance, and damages agricultural ecosystems.

**KrishiSetu AI** bridges this gap by unifying:
1. **Early Leaf Pathogen Detection**: Computer vision classification of foliar crop diseases from mobile field photos.
2. **Hyper-Local Environmental Intelligence**: Real-time micro-climate retrieval (temperature, relative humidity, precipitation, wind) mapped directly to the farmer's plot.
3. **Outbreak Risk Advisory**: Decoupled environmental vulnerability scoring calculating disease sporulation and pest proliferation risk.
4. **Targeted Interventions**: Actionable cultural, biological, and localized physical steps designed to prevent unnecessary chemical overuse.

### Sustainable Development Goals (SDGs)
- **SDG 2**: Zero Hunger
- **SDG 12**: Responsible Consumption and Production
- **SDG 13**: Climate Action
- **SDG 15**: Life on Land

> **Ethical Notice & Scientific Integrity:**
> KrishiSetu AI is designed as a decision-support advisory tool. We do not claim measured reductions in chemical pesticide usage without empirical, real-world field verification data collected over crop seasons.

---

## 2. Current Development Status
- **Current Phase**: **Phase 0 (Project Foundation, Requirements & Architecture) — COMPLETED**
- **Next Phase**: **Phase 1 (PlantVillage Dataset & ML Training Pipeline) — PENDING APPROVAL**

Development strictly follows an incremental checkpoint methodology. No production models, UI features, or backend APIs are deployed without passing phase validation criteria.

---

## 3. Technology Stack

| Domain | Technologies | Architectural Rationale |
|---|---|---|
| **Shared Backend** | Python 3.10+, FastAPI, Pydantic | High-performance asynchronous REST endpoints, automated OpenAPI schemas, shared by web & mobile |
| **Database & ORM** | SQLAlchemy 2.0, SQLite (Dev) / PostgreSQL (Prod) | Rapid local file-based database for development with zero-overhead migration to PostgreSQL |
| **Machine Learning** | PyTorch, Torchvision, Transfer Learning (`ResNet18`) | Transfer learning on official PlantVillage dataset, optimized for CPU inference (< 300ms) |
| **Training Pipeline** | Google Colab (GPU) + Local CPU fallback | Accommodates 8 GB RAM developer hardware constraints with reproducible cloud training |
| **Weather Service** | Pluggable `WeatherService` (Open-Meteo candidate) | Abstracted micro-climate layer with caching (1 hr TTL) and regional fallback support |
| **Web Client** | React 18, TypeScript, Tailwind CSS | Rich desktop/tablet responsiveness, interactive location selection, judge/demo exploration |
| **Mobile Client** | React Native, Expo (Android target) | Direct field camera capture, offline-resilient UX, sunlight-readable UI, native TTS narration |
| **Localization & Voice** | Centralized i18n, Web Speech / Expo Speech | Support for 10 regional Indian languages with audio narration ("Listen" button) |

---

## 4. Repository Structure

```
krishisetu-ai/
│
├── backend/                  # Shared FastAPI RESTful service
│   └── README.md
├── frontend/                 # Web client (React + TypeScript + Tailwind CSS)
│   └── README.md
├── mobile/                   # Mobile client (React Native + Expo Android)
│   └── README.md
├── ml/                       # PyTorch training, evaluation, and Colab notebooks
│   └── README.md
├── models/                   # Model registry and metadata (weights excluded from Git)
│   └── README.md
├── data/                     # Data policies and sample assets (raw sets excluded from Git)
│   └── README.md
├── docs/                     # Architectural specifications and requirements
│   ├── requirements.md       # Complete Product Requirements Document (PRD)
│   ├── architecture.md       # Comprehensive System Architecture Specification
│   └── development-roadmap.md# Strict phase-by-phase checkpoint roadmap
├── .env.example              # Environment variables template
├── .gitignore                # Multi-language Git exclusion rules
├── docker-compose.yml        # Development container orchestration specification
└── README.md                 # Primary project overview
```

---

## 5. Architectural Highlights

### Decoupled AI & Risk Engine
Disease identification and outbreak risk assessment are strictly separated:
- **Image Model**: Answers *"What is this?"* (Leaf photo $\rightarrow$ Pathogen classification + confidence).
- **Risk Engine**: Answers *"What might happen?"* (Farm coordinates + Weather micro-climate $\rightarrow$ Outbreak risk level + contributing environmental factors).
- **Low-Confidence Safeguard**: If prediction confidence is below $0.60$, the system safely prompts the farmer to re-capture a clearer image rather than guessing.

### Farm-Centric Location Privacy
- Location belongs to the **Farm**, not permanently to the farmer's personal profile.
- Explicit farmer confirmation is required before coordinates are stored.
- Zero continuous or background tracking.
- External weather queries truncate coordinates to prevent micro-property leakage.

---

## 6. Development Roadmap & Checkpoints

```
[x] Phase 0: Requirements + Architecture (CURRENT)
[ ] Phase 1: PlantVillage & Reproducible ML Training Pipeline
[ ] Phase 2: Shared Backend Foundation & Database Models
[ ] Phase 3: First End-to-End Image Inference
[ ] Phase 4: Pluggable Weather Integration & Caching
[ ] Phase 5: Environmental Risk Engine
[ ] Phase 6: Complete PS-2A Unified Core Workflow (Web + Mobile)
[ ] Phase 7: Multilingual (10 Indian Languages), Voice & History
[ ] Phase 8: Comprehensive Testing & Benchmarking
[ ] Phase 9: Judge / Demo Mode Preparation
[ ] Phase 10: Optional Features (Post-Core Evaluation Only)
```

For complete checkpoint acceptance criteria, review [docs/development-roadmap.md](file:///c:/Users/vsm30/OneDrive/Documents/GitHub2.0/krishisetu-ai/docs/development-roadmap.md).

---

## 7. Developer Setup & Environment Notes

### Hardware Accommodations
- The development environment is configured to run smoothly on standard laptop hardware (**8 GB RAM, no dedicated local GPU**).
- **Inference**: Optimized for CPU execution ($\le 1.2$ GB peak RAM footprint).
- **Training**: Executed via reproducible Google Colab notebooks with GPU acceleration, alongside a CPU-compatible fallback script.

### Getting Started (Phase 0 Scope)
1. Clone the repository:
   ```bash
   git clone https://github.com/amoghvm/krishisetu-ai.git
   cd krishisetu-ai
   ```
2. Copy environment template:
   ```bash
   cp .env.example .env
   ```
3. Review project documentation:
   - [Product Requirements](file:///c:/Users/vsm30/OneDrive/Documents/GitHub2.0/krishisetu-ai/docs/requirements.md)
   - [System Architecture](file:///c:/Users/vsm30/OneDrive/Documents/GitHub2.0/krishisetu-ai/docs/architecture.md)
   - [Development Roadmap](file:///c:/Users/vsm30/OneDrive/Documents/GitHub2.0/krishisetu-ai/docs/development-roadmap.md)

---

## 8. Anti-Hallucination & Scientific Disclosures
1. **Dataset Integrity**: We use the official **PlantVillage** dataset. We explicitly acknowledge that PlantVillage is a controlled-setting dataset; validation accuracy does not guarantee identical field accuracy under natural outdoor noise.
2. **Risk Heuristics**: The risk engine in Phase 0–5 is founded upon transparent agronomic micro-climate thresholds, not an artificially claimed "predictive machine learning model," unless empirical historical outbreak records are provided.
3. **No Unverified Data**: All numbers and metrics will only be documented following reproducible automated benchmark execution.
