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

# Process Store 2 clips
export STORE_ID="STORE_2"

echo "Processing Store 2 - entry 1"
export CAMERA_ID="CAM_ENTRY1"
export VIDEO_PATH="../Store 2/entry 1.mp4"
python detect.py

echo "Processing Store 2 - entry 2"
export CAMERA_ID="CAM_ENTRY2"
export VIDEO_PATH="../Store 2/entry 2.mp4"
python detect.py

echo "Processing Store 2 - zone"
export CAMERA_ID="CAM_ZONE"
export VIDEO_PATH="../Store 2/zone.mp4"
python detect.py

echo "Processing Store 2 - billing"
export CAMERA_ID="CAM_BILLING"
export VIDEO_PATH="../Store 2/billing_area.mp4"
python detect.py

echo "Processing complete."
