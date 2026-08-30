import socket
import serial
import time

# --- NETWORK CONFIGURATION ---
UDP_IP = "0.0.0.0"       # Listen on all local interfaces
UDP_PORT = 5005

# --- SERIAL CONFIGURATION ---
# Primary GPIO UART port on Raspberry Pi Zero 2 W connected to Arduino Serial1
SERIAL_PORT = "/dev/ttyS0"  
BAUD_RATE = 115200

# Initialize Serial Connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow time for serial port to initialize
    print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"Error initializing serial port {SERIAL_PORT}: {e}")
    exit(1)

# Initialize UDP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"UDP Bridge listening on port {UDP_PORT}...")

try:
    while True:
        data, addr = sock.recvfrom(1024)  # Buffer size 1024 bytes
        message = data.decode('utf-8').strip()
        
        if message:
            # Forward formatted string directly over serial to Arduino
            ser.write((message + "\n").encode('utf-8'))
            
except KeyboardInterrupt:
    print("\nShutting down UDP-to-Serial bridge...")
    # Safely send home position to Arduino before exiting
    ser.write(b"90,90\n")
    ser.close()
    sock.close()
