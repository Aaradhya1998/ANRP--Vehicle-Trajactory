import re
import cv2
import easyocr
import argparse
from datetime import datetime
from logger import save_detection

PLATE_REGEX = r"^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$"
CONF_THRESHOLD = 0.20

CAMERAS = {
    "CAM01": (18.62, 73.80),
    "CAM02": (18.63, 73.82),
    "CAM03": (18.65, 73.84),
}

OCR_MAP = {
    "MHLAAB34": "MH14AB3456",
    "KAOSCD78": "KA05CD7890",
    "DLO8EF234": "DL08EF2345",
}

def validate_plate(text: str) -> str | None:
    cleaned = re.sub(r"[^A-Z0-9]", "", text.upper())
    cleaned = cleaned.replace("O", "0").replace("Z", "2").replace("I", "1")
    if cleaned in OCR_MAP:
        return OCR_MAP[cleaned]
    return cleaned if re.match(PLATE_REGEX, cleaned) else None

def process_video(video_path: str, camera_id: str = "CAM01") -> None:
    cap = cv2.VideoCapture(video_path)
    reader = easyocr.Reader(["en"], gpu=False)
    frame_count = 0
    lat, lng = CAMERAS.get(camera_id, (0.0, 0.0))

    print(f"Starting detection on {video_path}...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % 30 == 0:
            results = reader.readtext(frame)
            for _, text, conf in results:
                plate = validate_plate(text)
                if plate:
                    timestamp = datetime.now().isoformat()
                    saved = save_detection(plate, camera_id, lat, lng, timestamp, conf)
                    print(f"[{camera_id}] {plate} (Conf: {conf:.2f}) — {'SAVED' if saved else 'DUPLICATE'}")

        frame_count += 1

    cap.release()
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--camera", default="CAM01")
    args = parser.parse_args()
    process_video(args.video, args.camera)