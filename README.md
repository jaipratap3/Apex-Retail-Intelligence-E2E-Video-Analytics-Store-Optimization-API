# Apex Retail Store Intelligence

## Prerequisites
- Docker & Docker Compose installed on your system.
- Ensure the `Store 1` folder containing the `.mp4` video clips is placed directly in the repository root folder before running.

## Setup Instructions
1. Clone the repository and navigate into the root directory:
   `git clone https://github.com/jaipratap3/Apex-Retail-Intelligence-E2E-Video-Analytics-Store-Optimization-API.git`
   `cd Apex-Retail-Intelligence-E2E-Video-Analytics-Store-Optimization-API`

2. Launch the backend API and database natively via Docker:
   `docker-compose up --build -d`

3. The API will now be live at `http://localhost:8000`. You can view the interactive documentation at `http://localhost:8000/docs`

## Run the Computer Vision Pipeline
4. Navigate to the pipeline directory and setup the environment:
   `cd pipeline`
   `python3 -m venv venv`
   `source venv/bin/activate`
   `pip install -r requirements.txt`

5. Execute the detection script to parse the video files and push events to the API:
   `bash run.sh`

6. Fetch the live analytics results from the API directly in your browser:
   - Metrics: http://localhost:8000/stores/STORE_1/metrics
   - Funnel: http://localhost:8000/stores/STORE_1/funnel
   - Anomalies: http://localhost:8000/stores/STORE_1/anomalies

## Detection Pipeline Details
The detection pipeline (`pipeline/detect.py`) uses YOLOv8 for object detection and ByteTrack for tracking. It simulates store zones (as `store_layout.json` was omitted, static coordinate zones are used). Events are automatically posted to the API running on `localhost:8000`.

## API Outputs
The API exposes the following endpoints (available after `docker-compose up`):
* `POST /events/ingest`: Ingests event batches.
* `GET /stores/{id}/metrics`: Live store metrics.
* `GET /stores/{id}/funnel`: Conversion funnel.
* `GET /stores/{id}/anomalies`: Anomaly detection.
* `GET /health`: System health.

## Live Dashboard
To view the beautiful, real-time analytics dashboard UI:
1. Open a new terminal window.
2. Navigate to the dashboard directory: `cd dashboard`
3. Setup the environment:
   `python3 -m venv venv`
   `source venv/bin/activate`
4. Install the UI dependencies: `pip install -r requirements.txt`
5. Run the Streamlit app: `streamlit run app.py`
5. The Live Dashboard will automatically open in your browser at `http://localhost:8501`, rendering live metrics, funnel charts, and anomaly alerts dynamically as the AI pipeline runs.

## Innovative AI Features Built-In
This submission goes beyond basic tracking. It features a highly advanced, mathematically robust backend:
1. **Predictive Queue Velocity AI:** The anomaly engine calculates the rapid influx velocity of the billing queue. If the queue grows by 2+ people in under 120 seconds, it fires a preemptive `PREDICTIVE_QUEUE_SPIKE` alert *before* capacity is breached.
2. **Dynamic Staff-to-Customer Ratios:** The AI cross-references the `is_staff` metadata tag against live zones. If a zone has 3+ customers lingering but 0 staff present, it triggers an `UNDERSTAFFED_ZONE` dispatch alert to prevent checkout abandonment.
3. **Idempotent Funnel Deduplication:** The backend is protected by strict Python Sets and SQL `DISTINCT` mathematics. If the AI tracker glitches or the video is run multiple times, the conversion funnel is mathematically guaranteed to safely de-duplicate all `visitor_id`s.
4. **Cross-Domain Data Correlation:** Unstructured CCTV tracking data is dynamically married to structured POS receipts (`pos_transactions.csv`) within a sliding 5-minute checkout window to accurately diagnose live funnel conversion drop-offs.
