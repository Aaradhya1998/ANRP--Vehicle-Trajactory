# makevideo.py
import cv2
import numpy as np

out = cv2.VideoWriter('data/sample.mp4',
      cv2.VideoWriter_fourcc(*'mp4v'), 25, (640, 480))

# makevideo.py - use plates with no ambiguous chars
plates = ["MH14AB3456", "KA05CD7890", "DL08EF2345"]

for i in range(750):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    plate = plates[i // 250]
    # bigger white rectangle
    cv2.rectangle(frame, (50, 150), (590, 330), (255, 255, 255), -1)
    # bigger bolder text
    cv2.putText(frame, plate, (60, 295),
                cv2.FONT_HERSHEY_DUPLEX, 3.2, (0, 0, 0), 6)
    out.write(frame)

out.release()
print("Video created!")