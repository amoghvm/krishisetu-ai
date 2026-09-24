# KrishiSetu AI - Mobile Application

## Overview
This directory contains the cross-platform mobile application for KrishiSetu AI, primarily targeting Android smartphones used by farmers directly in the field.

## Architecture & Technology Stack
- **Framework**: React Native with Expo
- **Language**: TypeScript
- **Target Platform**: Android (primary for hackathon evaluation), iOS compatible
- **Camera & Sensors**: Expo Camera, Expo Location (farm-level GPS with explicit farmer confirmation)
- **Internationalization (i18n)**: Centralized translation architecture shared with web patterns
- **Speech / TTS**: Native Text-to-Speech synthesis for voice guidance
- **Backend Communication**: Shared FastAPI REST endpoints (`/api/v1`)

## Key Client Capabilities (Planned)
- Native mobile camera capture with leaf centering viewfinder
- Farm location picking (device GPS with explicit consent, manual search fallback)
- Offline-graceful UX with clear network error handling
- High-contrast, sunlight-readable UI tailored for field use
- Voice / audio playback of disease diagnosis and risk alerts in regional languages
- Direct prediction feedback ("Correct", "Incorrect", "Unsure")

## Current Status
**Phase 0 - Architectural Foundation.** No mobile code or dependencies are installed yet. Development will occur in parallel with shared backend API contracts.
