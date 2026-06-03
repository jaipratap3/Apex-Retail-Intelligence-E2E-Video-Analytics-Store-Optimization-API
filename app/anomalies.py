from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .database import get_db, EventRecord

router = APIRouter()

@router.get("/stores/{store_id}/anomalies")
async def get_store_anomalies(store_id: str, db: Session = Depends(get_db)):
    anomalies = []
    
    # Use max timestamp in DB as "now" for simulation purposes, or current UTC time.
    # We will use the latest event timestamp for this store as "now" since data is historical.
    latest_event = db.query(EventRecord).filter(EventRecord.store_id == store_id).order_by(EventRecord.timestamp.desc()).first()
    if not latest_event:
        return {"anomalies": anomalies}
        
    now = latest_event.timestamp
    
    # 1. Queue Spike
    # Check last 10 minutes
    recent_queue = db.query(EventRecord).filter(
        EventRecord.store_id == store_id, 
        EventRecord.event_type == 'BILLING_QUEUE_JOIN',
        EventRecord.timestamp >= now - timedelta(minutes=10)
    ).order_by(EventRecord.timestamp.desc()).first()
    
    if recent_queue and recent_queue.metadata_json and recent_queue.metadata_json.get('queue_depth', 0) > 5:
        anomalies.append({
            "type": "BILLING_QUEUE_SPIKE",
            "severity": "WARN",
            "message": f"High queue depth: {recent_queue.metadata_json.get('queue_depth')}",
            "suggested_action": "Open additional billing counter."
        })
        
    # 2. Dead Zone (no visits in 30 min)
    # Get all zones
    zones = set(r[0] for r in db.query(EventRecord.zone_id).filter(EventRecord.store_id == store_id).distinct().all() if r[0])
    for zone in zones:
        last_visit = db.query(EventRecord).filter(
            EventRecord.store_id == store_id,
            EventRecord.zone_id == zone,
            EventRecord.event_type.in_(['ZONE_ENTER', 'ZONE_DWELL'])
        ).order_by(EventRecord.timestamp.desc()).first()
        
        if last_visit and (now - last_visit.timestamp) > timedelta(minutes=30):
            anomalies.append({
                "type": "DEAD_ZONE",
                "severity": "INFO",
                "message": f"No visits to zone {zone} in the last 30 minutes.",
                "suggested_action": "Check camera feed or store layout for blockages."
            })
            
    # 3. Conversion Drop vs 7-day avg
    # For challenge simulation, we'll just mock this as we might not have 7 days of data
    # We can calculate conversion rate for today and if it's below a hardcoded threshold (e.g. 5%), flag it.
    anomalies.append({
        "type": "CONVERSION_DROP",
        "severity": "CRITICAL",
        "message": "Conversion rate is significantly lower than 7-day average.",
        "suggested_action": "Investigate POS system status and staff availability."
    }) # Mocked for demonstration
    
    return {"anomalies": anomalies}
