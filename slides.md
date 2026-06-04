---
marp: true
theme: default
class: lead
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

# **Apex Retail Intelligence**
### E2E Video Analytics & Store Optimization API
**Purplle Tech Challenge 2026**

---

# **Architecture Overview**
**1. Computer Vision (Edge)**
- **YOLOv8 & ByteTrack:** High-speed real-time detection & temporal tracking of individuals.
- **Coordinate Mapping:** Translates pixel coordinates into store zones (Entry, Zone Visit, Billing).

**2. Intelligence API (Cloud/Server)**
- **FastAPI Backend:** Handles heavy ingestion loads safely.
- **SQLite Database:** Zero-configuration, scalable persistence layer.

---

# **Addressing Edge Cases**

- **Staff Exclusion:** Employs explicit `is_staff` schema tagging. Filtered out of all metric pipelines.
- **Re-Entry Handling:** Uses mathematical `Set()` aggregation by `visitor_id` to prevent conversion funnel inflation.
- **Queue Buildup:** Continuously calculates Queue Depth. Pushes dynamic `BILLING_QUEUE_SPIKE` alerts to operations.
- **Occlusion Resilience:** Pushes detection `confidence` scores natively to the database for post-filtering.

---

# **The Conversion Funnel**

The system actively maps POS transactions (`pos_transactions.csv`) against the raw video-extracted timeline to provide a literal 4-stage checkout funnel:

1. **Entry** (Crossed Threshold)
2. **Zone Visit** (Engaged with layout)
3. **Billing Queue** (Intent to buy)
4. **Purchase** (Confirmed POS match)

---

# **Innovative AI Features Built-In**

We went beyond basic tracking to build a **Predictive Operations Engine**:

- **Predictive Queue Velocity AI**: Mathematically detects rapid queue influx (+2 people in < 120s) and triggers preemptive register alerts *before* capacity is breached.
- **Dynamic Staff-to-Customer Ratios**: Autonomously dispatches employees if a zone exceeds 3 customers with 0 staff present.
- **Idempotent Funnel Deduplication**: Safely mitigates YOLO tracking glitches using robust SQL mathematical bounds.

---

# **Deployment & Scalability**
- **100% Dockerized:** Instantly runs on any system using `docker-compose up`.
- **Live Visual Dashboard:** A real-time Streamlit UI (`dashboard/app.py`) natively polls the API to render dynamic charts.
- **Stateless Intelligence:** The FastAPI server maintains zero state, meaning it can be load-balanced horizontally across multiple store locations.
