#!/bin/bash

export API_URL="http://127.0.0.1:8000"

# Process Store 1 clips
export STORE_ID="STORE_1"

echo "Processing CAM 1 - zone"
export CAMERA_ID="CAM1"
export VIDEO_PATH="../Store 1/CAM 1 - zone.mp4"
python detect.py

echo "Processing CAM 3 - entry"
export CAMERA_ID="CAM3"
export VIDEO_PATH="../Store 1/CAM 3 - entry.mp4"
python detect.py

echo "Processing complete."
