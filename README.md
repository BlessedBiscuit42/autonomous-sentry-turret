# Autonomous Target-Tracking Sentry Turret

An end-to-end embedded hardware and computer vision system featuring real-time YOLO11 pose estimation, low-latency socket communication, custom hardware integration, and exponential target vector smoothing.

---

## Technical Architecture

```text
[MacBook Pro (UI / OpenCV / YOLO)] 
        │
        │ UDP Socket Stream
        ▼
[Raspberry Pi Zero 2 W (bridge.py)] 
        │
        │ Hardware UART (Tx/Rx)
        ▼
[Arduino Mega 2560 (turret_control.ino)]
        │
        ├── Pin D8  ──► 2N2222 NPN Transistor ──► Red Laser Diode Module
        ├── Pin D9  ──► Pan Servo PWM Motor
        └── Pin D10 ──► Tilt Servo PWM Motor
