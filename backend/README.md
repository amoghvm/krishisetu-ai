# KrishiSetu AI - Backend Service

## Overview
This directory will host the shared RESTful API backend serving both the Web application (`frontend/`) and Mobile application (`mobile/`).

## Architecture & Technology Stack
- **Framework**: Python 3.10+ with FastAPI
- **ORM / Data Access**: SQLAlchemy 2.0+
- **Database**: SQLite (initial local development) -> PostgreSQL ready
- **Authentication**: Stateless JWT (JSON Web Tokens) with bcrypt password hashing
- **Inference Runtime**: PyTorch (CPU-optimized for inference)
- **External Integrations**: Pluggable `WeatherService` abstraction

## Core Responsibilities
- User & Farmer authentication and profile management
- Farm location management (lat/long, geocoding metadata, boundary, crop associations)
- Image ingest and preprocessing for disease classification
- Leaf pathogen classification invocation (`ImageModel`)
- Micro-climate weather retrieval and caching (`WeatherService`)
- Outbreak and pest risk evaluation (`RiskEngine`)
- Actionable, targeted non-blanket recommendations
- Analysis history persistence and farmer prediction feedback

## Current Status
**Phase 0 - Architectural Foundation.** No API endpoints, database migrations, or business logic are implemented yet. See `docs/development-roadmap.md` for phase checkpoints.
