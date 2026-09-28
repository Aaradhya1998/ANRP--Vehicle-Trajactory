import os
import uuid
from datetime import datetime
import pandas as pd

CSV_PATH = "data/detections.csv"
COLS = [
    "event_id",
    "plate_number",
    "camera_id",
    "latitude",
    "longitude",
    "timestamp",
    "confidence",
]


def load_csv() -> pd.DataFrame:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=COLS).to_csv(CSV_PATH, index=False)
    return pd.read_csv(CSV_PATH)


def is_duplicate(plate: str, camera_id: str, timestamp: str) -> bool:
    df = load_csv()
    if df.empty:
        return False
    dt = datetime.fromisoformat(timestamp)
    df["dt"] = pd.to_datetime(df["timestamp"])
    matches = df[
        (df["plate_number"] == plate) & (df["camera_id"] == camera_id)
    ]
    recent = matches[
        (dt - matches["dt"]).dt.total_seconds().abs() <= 30
    ]
    return not recent.empty


def save_detection(
    plate: str,
    camera_id: str,
    lat: float,
    lng: float,
    timestamp: str,
    confidence: float,
) -> bool:
    if is_duplicate(plate, camera_id, timestamp):
        return False
    event_id = f"EVT-{uuid.uuid4().hex[:6].upper()}"
    new_row = pd.DataFrame(
        [[event_id, plate, camera_id, lat, lng, timestamp, confidence]],
        columns=COLS,
    )
    new_row.to_csv(CSV_PATH, mode="a", header=False, index=False)
    return True
