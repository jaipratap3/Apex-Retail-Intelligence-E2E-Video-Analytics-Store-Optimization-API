from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any
from .models import StoreEvent
from .database import get_db, EventRecord
import logging

logger = logging.getLogger("store_intelligence.ingest")

router = APIRouter()

@router.post("/events/ingest", status_code=status.HTTP_207_MULTI_STATUS)
async def ingest_events(events: List[Dict[Any, Any]], db: Session = Depends(get_db)):
    if len(events) > 500:
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 500 events")

    success_count = 0
    errors = []

    for index, event_data in enumerate(events):
        try:
            # Validate with Pydantic
            event = StoreEvent(**event_data)
            
            # Map to SQLAlchemy model
            db_event = EventRecord(
                event_id=event.event_id,
                store_id=event.store_id,
                camera_id=event.camera_id,
                visitor_id=event.visitor_id,
                event_type=event.event_type,
                timestamp=event.timestamp,
                zone_id=event.zone_id,
                dwell_ms=event.dwell_ms,
                is_staff=event.is_staff,
                confidence=event.confidence,
                metadata_json=event.metadata.model_dump() if event.metadata else None
            )
            
            db.add(db_event)
            db.commit()
            success_count += 1
            
        except IntegrityError:
            db.rollback()
            # Idempotency: if event_id already exists, we consider it a success (duplicate)
            success_count += 1
            logger.info(f"Duplicate event ignored: {event_data.get('event_id')}")
        except Exception as e:
            db.rollback()
            errors.append({
                "index": index,
                "event_id": event_data.get("event_id"),
                "error": str(e)
            })

    # If all failed, return 400
    if success_count == 0 and len(errors) > 0:
        raise HTTPException(status_code=400, detail={"message": "All events failed validation", "errors": errors})
    
    # If partial success or full success, return 207 Multi-Status
    return {
        "message": f"Processed {len(events)} events",
        "success_count": success_count,
        "error_count": len(errors),
        "errors": errors
    }
