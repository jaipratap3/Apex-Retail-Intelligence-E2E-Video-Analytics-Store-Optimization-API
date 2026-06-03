# Architecture Overview

## Detection Pipeline
The detection pipeline is implemented as a Python script (`pipeline/detect.py`) using Ultralytics YOLOv8n. I chose the nano variant for real-time inference speed without requiring a GPU. It uses the `bytetrack` algorithm built into Ultralytics for tracking across frames.

## Intelligence API
The API is built using FastAPI due to its performance, native Pydantic validation, and excellent developer experience. SQLite is used as the storage engine to simplify the deployment architecture to a single container while satisfying the challenge's constraints.

## AI-Assisted Decisions

1. **Database Selection**: I used Gemini to discuss options for the storage layer. It suggested PostgreSQL for a true production environment but highlighted SQLite's ease of containerisation for a take-home challenge. I agreed with SQLite to ensure a smooth, zero-dependency `docker compose up` experience.
2. **Schema Simplification**: An LLM suggested using raw SQL queries for analytics. However, I overrode this and chose SQLAlchemy ORM. While slightly slower, the ORM prevents SQL injection and provides a cleaner codebase for a hiring evaluation.
3. **Tracking Heuristics**: I asked an LLM how to implement multi-camera Re-ID. It suggested complex feature extraction using `torchreid`. Given the time constraints and edge cases, I chose a simpler heuristic based on Entry/Exit spatial zoning to fulfill the base requirements.
