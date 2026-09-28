# ANPR Trajectory Tracker
### SIH 2026 | Problem Statement SIH26127

A city-wide license plate detection and vehicle tracking system built with Python, YOLOv8, and Antigravity.

---

## What It Does

- Reads plates from any video file (simulating CCTV feeds)
- Tracks where a vehicle went across multiple cameras
- Fires alerts for blacklisted, cloned, or looping vehicles
- Shows everything live on a web dashboard

---

## Project Structure

```
anpr/
├── detector.py       # YOLOv8n + EasyOCR → reads plates from video
├── logger.py         # Saves valid detections to CSV
├── alerts.py         # Checks blacklist, cloned plates, loops
├── api.py            # FastAPI backend (5 endpoints)
├── dashboard/        # Antigravity frontend
│   ├── index.html
│   ├── app.js
│   └── style.css
├── data/
│   ├── detections.csv
│   ├── alerts.csv
│   └── blacklist.txt
├── cameras.json      # Camera registry (id, name, lat, lng)
└── requirements.txt
```

---

## Setup

```bash
# Clone and enter project
git clone <repo-url>
cd anpr

# Install dependencies
pip install -r requirements.txt

# Add your video file
cp your_traffic_video.mp4 data/sample.mp4
```

---

## Run

```bash
# Step 1 — Start detection (reads video, logs to CSV)
python detector.py --video data/sample.mp4 --camera CAM01

# Step 2 — Start backend API
uvicorn api:app --reload --port 8000

# Step 3 — Open frontend
# Open dashboard/index.html in browser
# or serve with Antigravity
```

---

## requirements.txt

```
ultralytics
easyocr
opencv-python
fastapi
uvicorn
pandas
folium
python-multipart
```

---

## Camera Registry (cameras.json)

```json
[
  { "id": "CAM01", "name": "Junction 01", "lat": 18.62, "lng": 73.80 },
  { "id": "CAM02", "name": "Junction 02", "lat": 18.63, "lng": 73.82 },
  { "id": "CAM03", "name": "Junction 03", "lat": 18.65, "lng": 73.84 }
]
```

---

## Blacklist (data/blacklist.txt)

```
MH12AB1234
DL01CA9999
KA03MN5678
```
One plate per line. Alerts fire instantly on match.

---

## API Reference

| Endpoint | Returns |
|---|---|
| `GET /detections` | Last 20 plate detections |
| `GET /alerts` | Unacknowledged alerts |
| `GET /trajectory/{plate}` | Full camera journey for a plate |
| `GET /density` | Traffic density per camera |
| `POST /acknowledge/{alert_id}` | Mark alert as read |

---

## Alert Types

| Type | Trigger |
|---|---|
| `BLACKLIST` | Plate found in blacklist.txt |
| `CLONED_PLATE` | Same plate at 2 cameras with impossible travel time |
| `LOOP` | Same plate seen 3+ times in same zone |

---

## Detection Record Format

```
event_id, plate_number, camera_id, latitude, longitude, timestamp, confidence
E-10482,  MH12AB1234,  CAM01,     18.62,    73.80,     09:42:17,  0.94
```

---

## Team
**SIH 2026 | [Team Name] | Problem ID: SIH26127**
