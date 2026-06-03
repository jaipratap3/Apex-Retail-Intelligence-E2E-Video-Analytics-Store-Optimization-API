# Architectural Choices

### 1. Detection Model
**Options considered**: MediaPipe, YOLOv8 (ultralytics), RT-DETR.
**What AI suggested**: Gemini suggested YOLOv8 for its extensive community support and easy-to-use tracking integrations (ByteTrack).
**What I chose and why**: YOLOv8 nano. It hits the sweet spot between accuracy and inference speed, allowing the script to process the video relatively quickly even on a CPU. The built-in ByteTrack integration eliminated the need to write custom tracking boilerplate.

### 2. Event Schema Design
**Options considered**: Flat JSON, Nested JSON with unbounded metadata.
**What AI suggested**: A fully normalised relational schema.
**What I chose and why**: I strictly followed the provided "Event Schema" from the PDF but chose to store the `metadata` object as a `JSON` column in SQLite. This maintains the semi-structured nature of the events (e.g., `queue_depth` only exists for some events) without requiring complex JOINs to reconstruct the event in the API.

### 3. API Architecture
**Options considered**: Flask, FastAPI, Node.js Express.
**What AI suggested**: FastAPI, citing its async capabilities and automatic OpenAPI docs.
**What I chose and why**: FastAPI. The automatic request validation via Pydantic perfectly handles the "Schema compliance" requirement, and returning a 422 for malformed events is built-in.
