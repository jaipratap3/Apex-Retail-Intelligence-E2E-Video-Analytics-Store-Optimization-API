# Apex Retail Store Intelligence

## Setup Instructions

1. `git clone <repository_url> && cd store-intelligence`
2. **IMPORTANT**: Place the `Store 1` folder containing the video clips (`CAM 1 - zone.mp4`, etc.) directly into the `store-intelligence` root directory.
3. `docker compose up -d`
4. `cd pipeline`
5. `python3 -m venv venv && source venv/bin/activate`
6. `pip install -r requirements.txt`
7. `bash run.sh`

## Detection Pipeline
The detection pipeline (`pipeline/detect.py`) uses YOLOv8 for object detection and ByteTrack for tracking. It simulates store zones (as `store_layout.json` was omitted, static coordinate zones are used). Events are automatically posted to the API running on `localhost:8000`.

## API Outputs
The API exposes the following endpoints (available after `docker compose up`):
* `POST /events/ingest`: Ingests event batches.
* `GET /stores/{id}/metrics`: Live store metrics.
* `GET /stores/{id}/funnel`: Conversion funnel.
* `GET /stores/{id}/anomalies`: Anomaly detection.
* `GET /health`: System health.
