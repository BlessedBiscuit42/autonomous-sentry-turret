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
```

---

## Hardware Specifications & Bill of Materials

| Component | Quantity | Specification / Role |
| :--- | :--- | :--- |
| **Raspberry Pi Zero 2 W** | 1 | Edge compute host for video streaming & network bridge |
| **Arduino Mega 2560** | 1 | Real-time PWM servo timing & GPIO payload control |
| **InnoMaker 1080P UVC Camera** | 1 | 130° wide-angle USB vision sensor |
| **TP-Link Powered USB OTG Hub** | 1 | Self-powered hub to prevent Pi brownouts under peripheral load |
| **MG90D Servo Motors** | 2 | High-torque PWM actuation for horizontal/vertical tracking |
| **2N2222 NPN Transistor** | 1 | Low-side GPIO switch for laser firing circuit |
| **Red Laser Diode (5V)** | 1 | Targeted firing payload |
| **Passive Components** | Misc | 1kΩ base resistor (current limiting), 100µF decoupling capacitor |

> **Hardware & Power Note:** The Pi Zero 2 W is powered via a TP-Link self-powered USB OTG hub to handle power delivery for external peripherals without risking voltage brownouts. Network communication between the host laptop and the Pi utilizes a direct Ethernet connection to eliminate wireless jitter and maintain minimal MJPEG stream latency.

---

## Wiring & Pinout Mapping

**Raspberry Pi Zero 2 W → Arduino Mega 2560 (UART Serial Interface):**

- Pi **TX (GPIO 14)** → Mega **RX1 (Pin 19)**
- Pi **RX (GPIO 15)** → Mega **TX1 (Pin 18)**
- Pi **GND** → Mega **GND** (Common Ground Reference)

**Arduino Mega 2560 → Actuators & Circuitry:**

- **Pin D9:** Pan Servo PWM Signal
- **Pin D10:** Tilt Servo PWM Signal
- **Pin D8:** Transistor Base (via 1kΩ resistor) → Laser Module Power

---

## System Execution Setup

### 1. Arduino Firmware

Flash `firmware/turret_control/turret_control.ino` to the Arduino Mega using the Arduino IDE.

### 2. Multi-Terminal System Launch

```bash
# ==========================================
# Terminal 1: USB Camera Video Stream (Raspberry Pi SSH)
# ==========================================
cd ~/autonomous-sentry-turret
source venv/bin/activate

# Stream USB UVC camera feed over network port 8554
mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 640x480 -f 30" -o "output_http.so -p 8554 -w ./www"
```

```bash
# ==========================================
# Terminal 2: Hardware Serial Bridge (Raspberry Pi SSH)
# ==========================================
cd ~/autonomous-sentry-turret/software
source venv/bin/activate

# Run UDP socket to hardware UART bridge
python3 bridge.py
```

```bash
# ==========================================
# Terminal 3: Launch Vision Engine & Sentry HUD (Mac Host)
# ==========================================
cd ~/autonomous-sentry-turret/software
source venv/bin/activate

# Launch OpenCV/YOLO targeting interface & Pygame HUD
python3 sentry_ui_auto.py
```
