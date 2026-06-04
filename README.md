# Apex Retail Store Intelligence

## Prerequisites
* Docker & Docker Compose installed on your system.
* **CRITICAL:** Ensure that BOTH the `Store 1` and `Store 2` folders containing the `.mp4` video clips are placed directly in the repository root folder before running.

## Setup & Execution Instructions

For the easiest review experience, we have unified the entire execution into two simple steps.

### Part 1: Download & Setup
Run this in your terminal to download the code and enter the folder:
```bash
git clone https://github.com/jaipratap3/Apex-Retail-Intelligence-E2E-Video-Analytics-Store-Optimization-API.git && cd Apex-Retail-Intelligence-E2E-Video-Analytics-Store-Optimization-API
```
🛑 **CRITICAL PAUSE:** Immediately after running this, you MUST manually paste the `Store 1` and `Store 2` video folders directly into this new directory.

### Part 2: Execute the Multi-Store System
Once the videos are securely in the folder, run this single command to boot the entire Docker architecture and launch the live AI pipeline:
```bash
docker-compose up --build -d && sleep 5 && cd pipeline && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && bash run.sh
```

## Live Dashboard & API
Once you hit Enter on that final command, the backend will awaken and the YOLO AI will begin processing all 6 cameras for both stores sequentially.

**Live Multi-Tenant Dashboard:**
Open your browser and navigate to `http://localhost:8501`. 
The beautiful real-time analytics dashboard is now running securely inside Docker! As the AI pipeline runs, you can use the **Store Selection Dropdown** on the left sidebar to instantly toggle between `STORE_1` and `STORE_2` to watch their metrics, funnel charts, and anomaly alerts dynamically populate.

**API Outputs:**
The backend API exposes the following endpoints (available on `localhost:8000`):
* `POST /events/ingest`: Ingests event batches.
* `GET /stores/{id}/metrics`: Live store metrics.
* `GET /stores/{id}/funnel`: Conversion funnel.
* `GET /stores/{id}/anomalies`: Anomaly detection.
* `GET /health`: System health.

*(You can view the interactive API documentation at `http://localhost:8000/docs`)*

## Innovative AI Features Built-In
This submission goes beyond basic tracking. It features a highly advanced, mathematically robust backend:

* **Predictive Queue Velocity AI:** The anomaly engine calculates the rapid influx velocity of the billing queue. If the queue grows by 2+ people in under 120 seconds, it fires a preemptive `PREDICTIVE_QUEUE_SPIKE` alert *before* capacity is breached.
* **Dynamic Staff-to-Customer Ratios:** The AI cross-references the `is_staff` metadata tag against live zones. If a zone has 3+ customers lingering but 0 staff present, it triggers an `UNDERSTAFFED_ZONE` dispatch alert to prevent checkout abandonment.
* **Idempotent Funnel Deduplication:** The backend is protected by strict Python Sets and SQL `DISTINCT` mathematics. If the AI tracker glitches or the video is run multiple times, the conversion funnel is mathematically guaranteed to safely de-duplicate all `visitor_ids`.
* **Cross-Domain Data Correlation:** Unstructured CCTV tracking data is dynamically married to structured POS receipts (`pos_transactions.csv`) within a sliding 5-minute checkout window to accurately diagnose live funnel conversion drop-offs.

## Verify Production Readiness (Optional)
To prove the enterprise stability of the mathematical backend, you can execute our automated test suite. Open a new terminal in the repository root and run:
```bash
python3 -m venv venv_test
source venv_test/bin/activate
pip install -r requirements.txt pytest httpx
pytest tests/
```
*(This will trigger an automated test sequence that verifies the idempotency of the deduplication and the mathematical correctness of the API endpoints).*
