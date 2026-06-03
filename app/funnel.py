from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
import pandas as pd
from typing import Dict, Any
from .database import get_db, EventRecord
from .metrics import get_pos_data

router = APIRouter()

@router.get("/stores/{store_id}/funnel")
async def get_conversion_funnel(store_id: str, db: Session = Depends(get_db)):
    base_query = db.query(EventRecord).filter(EventRecord.store_id == store_id, EventRecord.is_staff == False)
    
    # 1. Entry
    entered_visitors = set(r.visitor_id for r in base_query.filter(EventRecord.event_type == 'ENTRY').all())
    
    # 2. Zone Visit
    zone_visited_visitors = set(r.visitor_id for r in base_query.filter(EventRecord.event_type.in_(['ZONE_ENTER', 'ZONE_DWELL'])).all())
    
    # intersection with entered (though technically a session could start inside if tracking fails, funnel usually strictly follows)
    zone_visited_visitors = zone_visited_visitors.intersection(entered_visitors)
    
    # 3. Billing Queue
    billing_queue_visitors = set(r.visitor_id for r in base_query.filter(EventRecord.event_type == 'BILLING_QUEUE_JOIN').all())
    billing_queue_visitors = billing_queue_visitors.intersection(zone_visited_visitors)
    
    # 4. Purchase
    purchased_visitors = set()
    df = get_pos_data()
    if df is not None and not df.empty:
        store_pos = df[df['store_id'] == store_id]
        
        # Get all billing queue events
        billing_events = base_query.filter(EventRecord.event_type == 'BILLING_QUEUE_JOIN').all()
        for v in billing_events:
            if v.visitor_id in billing_queue_visitors:
                t = v.timestamp
                t_end = t + timedelta(minutes=5)
                mask = (store_pos['timestamp'] >= t) & (store_pos['timestamp'] <= t_end)
                if mask.any():
                    purchased_visitors.add(v.visitor_id)

    def safe_div(a, b):
        return round((a / b * 100), 2) if b > 0 else 0.0

    stages = [
        {"stage": "Entry", "count": len(entered_visitors), "dropoff_percent": 0.0},
        {"stage": "Zone Visit", "count": len(zone_visited_visitors), "dropoff_percent": safe_div(len(entered_visitors) - len(zone_visited_visitors), len(entered_visitors))},
        {"stage": "Billing Queue", "count": len(billing_queue_visitors), "dropoff_percent": safe_div(len(zone_visited_visitors) - len(billing_queue_visitors), len(zone_visited_visitors))},
        {"stage": "Purchase", "count": len(purchased_visitors), "dropoff_percent": safe_div(len(billing_queue_visitors) - len(purchased_visitors), len(billing_queue_visitors))},
    ]

    return {"funnel": stages}
