import cv2
import socket
import numpy as np
from ultralytics import YOLO

# --- NETWORK CONFIGURATION ---
PI_IP = "192.168.1.205"
PI_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- FRAME GEOMETRY & ADJUSTED CROSSHAIR BORESIGHT ---
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

CENTER_X = FRAME_WIDTH // 2   # 320 px

# Shifted UP to match the physical laser alignment on screen
TARGET_X = CENTER_X
TARGET_Y = 180                # Upward offset for laser baseline

# --- SERVO STATE, GAINS & DEADBAND ---
last_pan_cmd = 90
last_tilt_cmd = 90
current_pan_f = 90.0
current_tilt_f = 90.0

PAN_MIN, PAN_MAX = 45, 135
TILT_MIN, TILT_MAX = 45, 135

# Balanced gains to eliminate vertical hunting/shaking
KP_PAN = 0.04
KP_TILT = 0.035
DEADZONE_X = 4
DEADZONE_Y = 4

print("Loading YOLO11 Pose model...")
model = YOLO('yolo11n-pose.pt')

STREAM_URL = f"http://{PI_IP}:8090/?action=stream"
cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("Error: Could not open HTTP stream from Pi.")
    exit()

print("\nSYSTEM READY - STABILIZED BORESIGHT TRACKING ACTIVE.")

while True:
    for _ in range(2): cap.grab()
    ret, frame = cap.retrieve()
    if not ret or frame is None: continue

    raw_cx, raw_cy = None, None
    best_box = None

    # --- YOLO POSE DETECTOR ---
    results = model(frame, verbose=False)

    if len(results) > 0 and len(results[0].boxes) > 0:
        boxes = results[0].boxes
        keypoints = results[0].keypoints

        max_area = 0
        best_idx = 0

        for idx, box in enumerate(boxes):
            if int(box.cls[0]) == 0:  # Person class
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area = (x2 - x1) * (y2 - y1)
                if area > max_area:
                    max_area = area
                    best_idx = idx
                    best_box = (x1, y1, x2, y2)

        if best_box is not None:
            x1, y1, x2, y2 = best_box
            if keypoints is not None and len(keypoints.data) > best_idx:
                kpts = keypoints.data[best_idx].cpu().numpy()
                left_shoulder = kpts[5]
                right_shoulder = kpts[6]

                if left_shoulder[2] > 0.4 and right_shoulder[2] > 0.4:
                    raw_cx = int((left_shoulder[0] + right_shoulder[0]) / 2)
                    raw_cy = int((left_shoulder[1] + right_shoulder[1]) / 2)

            if raw_cx is None:
                raw_cx = (x1 + x2) // 2
                raw_cy = y1 + int((y2 - y1) * 0.35)

    # --- SMOOTH CLOSED-LOOP CONTROL ---
    if raw_cx is not None and raw_cy is not None:
        error_x = raw_cx - TARGET_X
        error_y = raw_cy - TARGET_Y

        if abs(error_x) > DEADZONE_X:
            current_pan_f -= error_x * KP_PAN

        if abs(error_y) > DEADZONE_Y:
            current_tilt_f += error_y * KP_TILT

        target_pan = int(np.clip(current_pan_f, PAN_MIN, PAN_MAX))
        target_tilt = int(np.clip(current_tilt_f, TILT_MIN, TILT_MAX))

        # Transmit UDP command only on actual integer step change
        if target_pan != last_pan_cmd or target_tilt != last_tilt_cmd:
            msg = f"{target_pan},{target_tilt}\n"
            sock.sendto(msg.encode('utf-8'), (PI_IP, PI_PORT))
            last_pan_cmd = target_pan
            last_tilt_cmd = target_tilt

    # --- HUD VISUALIZATION ---
    # Shifted Cyan Crosshair
    cv2.line(frame, (TARGET_X - 15, TARGET_Y), (TARGET_X + 15, TARGET_Y), (255, 255, 0), 1)
    cv2.line(frame, (TARGET_X, TARGET_Y - 15), (TARGET_X, TARGET_Y + 15), (255, 255, 0), 1)

    if best_box is not None and raw_cx is not None:
        x1, y1, x2, y2 = best_box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, (raw_cx, raw_cy), 5, (0, 0, 255), -1)
        
        cmd_txt = f"TRACKING: {last_pan_cmd}° | {last_tilt_cmd}°"
        cv2.putText(frame, cmd_txt, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow("Sentry HUD - Auto Laser Accuracy Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

sock.sendto(b"90,90\n", (PI_IP, PI_PORT))
cap.release()
cv2.destroyAllWindows()
