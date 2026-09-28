# Product Requirements Document
## City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking and Urban Traffic Analytics
**SIH 2026 | Problem Statement ID: SIH26127**

---

## 1. Overview

A lightweight, open-source AI system that reads license plates from existing CCTV cameras, links detections across cameras into vehicle trajectories, fires real-time alerts, and displays everything on a city dashboard — with a clean web frontend built using Antigravity.

---

## 2. The Problem

- 84,000+ CCTV cameras across 100 Smart Cities operate in isolation
- Tracing one vehicle means checking footage camera by camera — manually
- MV Act cases nearly doubled in one year (94,450 → 1,91,828 in 2023)
- No unified system connects detections into a route

---

## 3. Goals

| Goal | Description |
|---|---|
| Detect | Read every license plate from camera feeds |
| Track | Build a vehicle's route across multiple cameras |
| Alert | Flag blacklisted, cloned, or looping vehicles instantly |
| Understand | Show city-wide traffic density in real time |
| Display | Serve everything through a clean web dashboard |

---

## 4. Users

| User | Need |
|---|---|
| Police / ICCC Operator | Search plate, see full route, acknowledge alerts |
| Traffic Manager | Monitor density per zone, spot jams early |
| Admin | Manage camera registry, blacklist, access |

---

## 5. Features

### 5.1 Core Pipeline
- Sample 1 frame every 1–2 seconds from video/CCTV feed
- YOLOv8n detects vehicles and locates plate region
- EasyOCR reads plate text; regex fixes to Indian format (XX00XX0000)
- Confidence filter: only pass detections ≥ 0.70
- Log every valid detection: plate, camera, timestamp, GPS, confidence

### 5.2 Alerts
- **Blacklist Alert** — plate matches known stolen/wanted list
- **Cloned Plate Alert** — same plate on 2 cameras with impossible travel time
- **Loop Alert** — same plate circles same zone 3+ times

### 5.3 Trajectory
- Show a plate's full journey: camera → time → speed
- Speed calculated using Haversine distance between camera GPS coords

### 5.4 Traffic Density
- Count vehicles per frame per camera (rolling average)
- Classify: LOW (<3), MEDIUM (3–11), HIGH (>11) vehicles per frame

### 5.5 Frontend (Antigravity)
- Live detection feed table
- Alert console (red highlight, acknowledge button)
- Plate search → full trajectory view
- City map with camera markers and density color codes
- Offline indicator (edge buffer mode)

---

## 6. Tech Stack

| Layer | Tool |
|---|---|
| Detection | YOLOv8n (ultralytics) |
| OCR | EasyOCR |
| Image Processing | OpenCV |
| Backend | FastAPI + Uvicorn |
| Frontend | Antigravity |
| Data Store | CSV (detections.csv, alerts.csv) |
| Map | Folium / Leaflet |
| Language | Python 3.11 |

---

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/detections` | Last 20 detections |
| GET | `/alerts` | All unacknowledged alerts |
| GET | `/trajectory/{plate}` | Full route for a plate |
| GET | `/density` | Current density per camera |
| POST | `/acknowledge/{alert_id}` | Mark alert as seen |

---

## 8. Data Model

### detections.csv
```
event_id, plate_number, camera_id, latitude, longitude, timestamp, confidence
```

### alerts.csv
```
alert_id, alert_type, plate_number, camera_id, timestamp, acknowledged
```

---

## 9. Constraints

| Constraint | How we handle it |
|---|---|
| No GPU | YOLOv8n runs on CPU |
| Low light / rain | OpenCV adaptive threshold |
| Network drop | Edge buffer → auto-sync when back |
| Dirty plates | Multi-frame check before logging |
| Privacy (DPDP 2023) | Role-based access, retention limits |

---

## 10. Out of Scope (for demo)

- Real live CCTV integration (use pre-recorded video)
- SQL database (CSV is sufficient for demo)
- Authentication system
- Multi-city deployment

---

## 11. Success Criteria for Demo

- [ ] Plate detected and logged from a video file
- [ ] Blacklist alert fires for a known plate
- [ ] Trajectory shown for a searched plate
- [ ] Dashboard updates live every 5 seconds
- [ ] Density shown as LOW / MED / HIGH per camera
