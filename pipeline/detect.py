import cv2
from ultralytics import YOLO
import requests
import uuid
import time
from datetime import datetime, timezone
import json
import os
import torch
import ultralytics.nn.tasks

original_load = torch.load
def patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = patched_load

API_URL = os.environ.get("API_URL", "http://localhost:8000")
STORE_ID = os.environ.get("STORE_ID", "STORE_BLR_002")
CAMERA_ID = os.environ.get("CAMERA_ID", "CAM_ENTRY_01")
VIDEO_PATH = os.path.abspath(os.environ.get("VIDEO_PATH", "sample.mp4"))

# Mock zones since we don't have store_layout.json
# Coordinates as (x1, y1, x2, y2)
ZONES = {
    "ENTRY_THRESHOLD": (0, 0, 1920, 200),
    "SKINCARE": (0, 200, 960, 1080),
    "BILLING": (960, 200, 1920, 1080)
}

def get_zone(x, y):
    for zone_id, (x1, y1, x2, y2) in ZONES.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return zone_id
    return None

def emit_event(event_type, visitor_id, zone_id=None, dwell_ms=0, confidence=0.9, metadata=None):
    event = {
        "event_id": str(uuid.uuid4()),
        "store_id": STORE_ID,
        "camera_id": CAMERA_ID,
        "visitor_id": f"VIS_{visitor_id}",
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "zone_id": zone_id,
        "dwell_ms": dwell_ms,
        "is_staff": False,  # Mocking staff detection for brevity
        "confidence": float(confidence),
        "metadata": metadata
    }
    
    # Write to local JSONL for submission requirement
    try:
        with open("../events.jsonl", "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"Error writing to events.jsonl: {e}")

    try:
        response = requests.post(f"{API_URL}/events/ingest", json=[event])
        if response.status_code != 207:
            print(f"Failed to ingest event: {response.text}")
    except Exception as e:
        print(f"Error emitting event: {e}")

def main():
    model = YOLO("yolov8n.pt")  # Use nano model for speed
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error opening video file {VIDEO_PATH}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # State tracking
    visitor_states = {} # id: {"last_zone": str, "zone_entry_time": float, "has_entered": bool, "queue_joined": bool}
    
    frame_count = 0
    # Process video with ByteTrack
    results = model.track(source=VIDEO_PATH, stream=True, tracker="bytetrack.yaml", persist=True, classes=[0]) # class 0 is person
    
    for result in results:
        frame_count += 1
        
        # Stop after 50 frames for quick end-to-end testing
        if frame_count > 50:
            print("Reached 50 frames, stopping for quick E2E test.")
            break
            
        current_time_sec = frame_count / fps
        
        if result.boxes is None or result.boxes.id is None:
            continue
            
        boxes = result.boxes.xyxy.cpu().numpy()
        track_ids = result.boxes.id.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        
        current_visitors_in_queue = 0
        
        for box, track_id, conf in zip(boxes, track_ids, confidences):
            x_center = (box[0] + box[2]) / 2
            y_center = (box[1] + box[3]) / 2
            
            zone = get_zone(x_center, y_center)
            
            if track_id not in visitor_states:
                visitor_states[track_id] = {
                    "last_zone": None,
                    "zone_entry_time": current_time_sec,
                    "has_entered": False,
                    "queue_joined": False
                }
            
            state = visitor_states[track_id]
            
            # Entry Logic (simplified: first seen)
            if not state["has_entered"] and zone != "ENTRY_THRESHOLD":
                emit_event("ENTRY", track_id, confidence=conf)
                state["has_entered"] = True
                
            # Zone Logic
            if zone != state["last_zone"]:
                if state["last_zone"] is not None:
                    # Emit ZONE_EXIT for old zone
                    emit_event("ZONE_EXIT", track_id, zone_id=state["last_zone"], confidence=conf)
                    
                    # Emit ZONE_DWELL for old zone
                    dwell_time_ms = int((current_time_sec - state["zone_entry_time"]) * 1000)
                    if dwell_time_ms > 30000: # 30 seconds threshold
                        emit_event("ZONE_DWELL", track_id, zone_id=state["last_zone"], dwell_ms=dwell_time_ms, confidence=conf)
                
                if zone is not None:
                    # Emit ZONE_ENTER for new zone
                    emit_event("ZONE_ENTER", track_id, zone_id=zone, confidence=conf)
                    
                state["last_zone"] = zone
                state["zone_entry_time"] = current_time_sec
                
            # Billing Queue Logic
            if zone == "BILLING":
                current_visitors_in_queue += 1
                if not state["queue_joined"]:
                    emit_event("BILLING_QUEUE_JOIN", track_id, zone_id="BILLING", confidence=conf, metadata={"queue_depth": current_visitors_in_queue})
                    state["queue_joined"] = True
            elif state["queue_joined"] and zone != "BILLING":
                 emit_event("BILLING_QUEUE_ABANDON", track_id, zone_id="BILLING", confidence=conf)
                 state["queue_joined"] = False

    cap.release()

if __name__ == "__main__":
    main()
