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
            
    # 3. Predictive Queue Velocity (Innovation)
    # Check if queue depth is rapidly increasing
    recent_queues = db.query(EventRecord).filter(
        EventRecord.store_id == store_id,
        EventRecord.event_type == 'BILLING_QUEUE_JOIN'
    ).order_by(EventRecord.timestamp.desc()).limit(2).all()
    
    if len(recent_queues) == 2:
        q_now = recent_queues[0]
        q_prev = recent_queues[1]
        depth_diff = q_now.metadata_json.get('queue_depth', 0) - q_prev.metadata_json.get('queue_depth', 0)
        time_diff = (q_now.timestamp - q_prev.timestamp).total_seconds()
        
        if depth_diff >= 2 and time_diff < 120:  # Queue grew by 2+ people in under 2 minutes
            anomalies.append({
                "type": "PREDICTIVE_QUEUE_SPIKE",
                "severity": "CRITICAL",
                "message": f"Queue velocity is dangerously high (+{depth_diff} people in {int(time_diff)}s).",
                "suggested_action": "Preemptively open a new billing counter before capacity is breached."
            })

    # 4. Dynamic Conversion Drop
    from sqlalchemy import func
    unique_visitors = db.query(EventRecord).filter(EventRecord.store_id == store_id, EventRecord.event_type == 'ENTRY').with_entities(func.count(func.distinct(EventRecord.visitor_id))).scalar() or 0
    
    if unique_visitors > 5:
        # If we have lots of visitors but the queue is empty, conversion is tanking
        queue_joins = db.query(EventRecord).filter(EventRecord.store_id == store_id, EventRecord.event_type == 'BILLING_QUEUE_JOIN').count()
        if queue_joins == 0:
            anomalies.append({
                "type": "CONVERSION_DROP",
                "severity": "CRITICAL",
                "message": f"Critical funnel dropoff: {unique_visitors} unique visitors but 0 entered the billing queue.",
                "suggested_action": "Investigate store layout or POS system status immediately."
            })
    # 5. Staff-to-Customer Ratio Alert (Innovation)
    # Check if there are many customers in a zone but no staff recently
    recent_zone_events = db.query(EventRecord).filter(
        EventRecord.store_id == store_id,
        EventRecord.timestamp >= now - timedelta(minutes=15),
        EventRecord.event_type.in_(['ZONE_ENTER', 'ZONE_DWELL'])
    ).all()
    
    zone_occupancy = {}
    for event in recent_zone_events:
        if event.zone_id not in zone_occupancy:
            zone_occupancy[event.zone_id] = {'customers': set(), 'staff': set()}
        
        if event.is_staff:
            zone_occupancy[event.zone_id]['staff'].add(event.visitor_id)
        else:
            zone_occupancy[event.zone_id]['customers'].add(event.visitor_id)
            
    for zone, counts in zone_occupancy.items():
        if len(counts['customers']) > 3 and len(counts['staff']) == 0:
            anomalies.append({
                "type": "UNDERSTAFFED_ZONE",
                "severity": "WARN",
                "message": f"Zone '{zone}' has {len(counts['customers'])} active customers but 0 staff members.",
                "suggested_action": f"Dispatch an associate to {zone} to assist customers and prevent abandonment."
            })
            
    return {"anomalies": anomalies}
