import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(title="ANPR API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DET_PATH = "data/detections.csv"
ALT_PATH = "data/alerts.csv"


def read_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


@app.get("/detections")
def get_detections():
    df = read_df(DET_PATH)
    return df.tail(20).to_dict(orient="records") if not df.empty else []


@app.get("/alerts")
def get_alerts():
    df = read_df(ALT_PATH)
    if df.empty:
        return []
    unack = df[df["acknowledged"].astype(str).str.upper() == "FALSE"]
    return unack.to_dict(orient="records")


@app.get("/trajectory/{plate}")
def get_trajectory(plate: str):
    df = read_df(DET_PATH)
    if df.empty:
        return []
    p_df = df[df["plate_number"] == plate.upper()].copy()
    if p_df.empty:
        return []
    p_df["dt"] = pd.to_datetime(p_df["timestamp"])
    return p_df.sort_values("dt").to_dict(orient="records")


@app.get("/density")
def get_density():
    df = read_df(DET_PATH)
    if df.empty:
        return {}
    df["dt"] = pd.to_datetime(df["timestamp"])
    now = df["dt"].max()
    recent = df[(now - df["dt"]).dt.total_seconds() <= 60]
    counts = recent.groupby("camera_id").size().to_dict()
    density = {}
    for cam, count in counts.items():
        if count < 3:
            density[cam] = "LOW"
        elif count <= 11:
            density[cam] = "MEDIUM"
        else:
            density[cam] = "HIGH"
    return density


@app.post("/acknowledge/{alert_id}")
def acknowledge_alert(alert_id: str):
    if not os.path.exists(ALT_PATH):
        raise HTTPException(status_code=404, detail="Alerts file not found")
    df = pd.read_csv(ALT_PATH)
    if alert_id not in df["alert_id"].values:
        raise HTTPException(status_code=404, detail="Alert not found")
    df.loc[df["alert_id"] == alert_id, "acknowledged"] = True
    df.to_csv(ALT_PATH, index=False)
    return {"status": "success", "alert_id": alert_id}
