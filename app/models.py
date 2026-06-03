from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EventMetadata(BaseModel):
    queue_depth: Optional[int] = None
    sku_zone: Optional[str] = None
    session_seq: Optional[int] = None

class StoreEvent(BaseModel):
    event_id: str = Field(..., description="Globally unique UUID for the event")
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: datetime
    zone_id: Optional[str] = None
    dwell_ms: int = 0
    is_staff: bool = False
    confidence: float
    metadata: Optional[EventMetadata] = None
