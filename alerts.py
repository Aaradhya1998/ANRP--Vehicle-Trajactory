import os
import uuid
from datetime import datetime
import pandas as pd

ALERTS_PATH = "data/alerts.csv"
BLACKLIST_PATH = "data/blacklist.txt"
ALERT_COLS = [
    "alert_id",
    "alert_type",
    "plate_number",
    "camera_id",
    "timestamp",
    "acknowledged",
]


def load_blacklist() -> set[str]:
    if not os.path.exists(BLACKLIST_PATH):
        return set()
    with open(BLACKLIST_PATH, "r") as f:
        return {line.strip().upper() for line in f if line.strip()}


def check_blacklist(plate: str) -> bool:
    return plate.upper() in load_blacklist()


def check_cloned(plate: str, detections_df: pd.DataFrame) -> bool:
    if detections_df.empty:
        return False
    p_df = detections_df[detections_df["plate_number"] == plate].copy()
    if len(p_df) < 2:
        return False
    p_df["dt"] = pd.to_datetime(p_df["timestamp"])
    p_df = p_df.sort_values("dt")
    last_two = p_df.iloc[-2:]
    c1, c2 = last_two.iloc[0]["camera_id"], last_two.iloc[1]["camera_id"]
    time_diff = (
        last_two.iloc[1]["dt"] - last_two.iloc[0]["dt"]
    ).total_seconds()
    return c1 != c2 and time_diff <= 300


def check_loop(
    plate: str, camera_id: str, detections_df: pd.DataFrame
) -> bool:
    if detections_df.empty:
        return False
    p_df = detections_df[
        (detections_df["plate_number"] == plate)
        & (detections_df["camera_id"] == camera_id)
    ].copy()
    if len(p_df) < 3:
        return False
    p_df["dt"] = pd.to_datetime(p_df["timestamp"])
    now = p_df["dt"].max()
    recent_10m = p_df[(now - p_df["dt"]).dt.total_seconds() <= 600]
    return len(recent_10m) >= 3


def save_alert(
    alert_type: str, plate: str, camera_id: str, timestamp: str = None
) -> None:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(ALERTS_PATH):
        pd.DataFrame(columns=ALERT_COLS).to_csv(ALERTS_PATH, index=False)
    ts = timestamp or datetime.now().isoformat()
    alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
    new_alert = pd.DataFrame(
        [[alert_id, alert_type, plate, camera_id, ts, False]],
        columns=ALERT_COLS,
    )
    new_alert.to_csv(ALERTS_PATH, mode="a", header=False, index=False)
if __name__ == "__main__":
    from logger import load_csv
    
    df = load_csv()
    if df.empty:
        print("No detections found.")
    else:
        for _, row in df.iterrows():
            plate = row["plate_number"]
            camera_id = row["camera_id"]
            timestamp = row["timestamp"]

            if check_blacklist(plate):
                save_alert("BLACKLIST", plate, camera_id, timestamp)
                print(f"BLACKLIST alert → {plate}")

            if check_cloned(plate, df):
                save_alert("CLONED_PLATE", plate, camera_id, timestamp)
                print(f"CLONED PLATE alert → {plate}")

            if check_loop(plate, camera_id, df):
                save_alert("LOOP", plate, camera_id, timestamp)
                print(f"LOOP alert → {plate}")

    print("Alert check done.")