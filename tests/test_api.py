# PROMPT: Generate FastAPI test cases using pytest and httpx for the ingest, metrics, and funnel endpoints. Include edge cases for idempotency, empty stores, and zero purchases.
# CHANGES MADE: Adapted the prompt's generic response to specifically use our StoreEvent Pydantic schema and integrated the local SQLite testing database.

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
import uuid
from datetime import datetime, timezone

# Setup test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_ingest_event_and_idempotency():
    event_id = str(uuid.uuid4())
    payload = [{
        "event_id": event_id,
        "store_id": "STORE_TEST",
        "camera_id": "CAM1",
        "visitor_id": "VIS_1",
        "event_type": "ENTRY",
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "confidence": 0.95
    }]
    
    # First ingest
    response1 = client.post("/events/ingest", json=payload)
    assert response1.status_code == 207
    assert response1.json()["success_count"] == 1
    
    # Second ingest (idempotency check)
    response2 = client.post("/events/ingest", json=payload)
    assert response2.status_code == 207
    assert response2.json()["success_count"] == 1

def test_empty_store_metrics():
    # Store with no events
    response = client.get("/stores/STORE_EMPTY/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["unique_visitors"] == 0
    assert data["conversion_rate_percent"] == 0.0

def test_zero_purchases():
    # Setup visitor without purchase
    client.post("/events/ingest", json=[{
        "event_id": str(uuid.uuid4()),
        "store_id": "STORE_NOPURCHASE",
        "camera_id": "CAM1",
        "visitor_id": "VIS_2",
        "event_type": "ENTRY",
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "confidence": 0.9
    }])
    
    response = client.get("/stores/STORE_NOPURCHASE/metrics")
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 1
    assert response.json()["conversion_rate_percent"] == 0.0

def test_staff_exclusion():
    # Staff event
    client.post("/events/ingest", json=[{
        "event_id": str(uuid.uuid4()),
        "store_id": "STORE_STAFF",
        "camera_id": "CAM1",
        "visitor_id": "VIS_STAFF",
        "event_type": "ENTRY",
        "is_staff": True,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "confidence": 0.99
    }])
    
    response = client.get("/stores/STORE_STAFF/metrics")
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 0
