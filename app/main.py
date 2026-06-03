import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pythonjsonlogger import jsonlogger
import time
import uuid

# Configure structured logging
logger = logging.getLogger("store_intelligence")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Apex Retail Store Intelligence API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    process_time_ms = (time.time() - start_time) * 1000
    
    logger.info(
        "Request processed",
        extra={
            "trace_id": trace_id,
            "endpoint": request.url.path,
            "method": request.method,
            "latency_ms": process_time_ms,
            "status_code": response.status_code,
        }
    )
    
    response.headers["X-Trace-Id"] = trace_id
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", extra={"error": str(exc), "endpoint": request.url.path})
    return JSONResponse(
        status_code=503,
        content={"error": "Service Unavailable", "message": "An unexpected error occurred."}
    )

from app.ingestion import router as ingestion_router
from app.metrics import router as metrics_router
from app.funnel import router as funnel_router
from app.anomalies import router as anomalies_router
from app.database import get_db, EventRecord
from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # Check for stale feeds
    stores = db.query(EventRecord.store_id).distinct().all()
    store_status = {}
    has_stale_feed = False
    
    # We will simulate "now" as the absolute max timestamp across all stores since data is historical
    max_event = db.query(EventRecord).order_by(EventRecord.timestamp.desc()).first()
    now = max_event.timestamp if max_event else datetime.utcnow()
    
    for (store_id,) in stores:
        last_event = db.query(EventRecord).filter(EventRecord.store_id == store_id).order_by(EventRecord.timestamp.desc()).first()
        lag = now - last_event.timestamp
        status_msg = "OK"
        if lag > timedelta(minutes=10):
            status_msg = "STALE_FEED"
            has_stale_feed = True
            
        store_status[store_id] = {
            "last_event_timestamp": last_event.timestamp,
            "status": status_msg
        }
        
    return {
        "status": "WARN" if has_stale_feed else "OK",
        "stores": store_status
    }

app.include_router(ingestion_router)
app.include_router(metrics_router)
app.include_router(funnel_router)
app.include_router(anomalies_router)
