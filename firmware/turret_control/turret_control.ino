#include <Servo.h>

Servo panServo;
Servo tiltServo;

const int laserPin = 8; // Digital pin connected to 2N2222 Base via resistor

// Mechanical safety limits
const int tiltMin = 45; 
const int tiltMax = 135;
const int panMin = 45;
const int panMax = 135;

const int homePan = 90;
const int homeTilt = 90;

float currentPan = 90.0;
float currentTilt = 90.0;
int targetPan = 90;
int targetTilt = 90;

const float smoothing = 0.2; 

unsigned long lastUpdateTime = 0;
const int updateInterval = 15;

void setup() {
  Serial1.begin(115200); 
  
  panServo.attach(9); 
  tiltServo.attach(10);
  
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, HIGH); // Force Laser ON continuously for accuracy testing
  
  resetToOrigin();
}

void loop() {
  if (Serial1.available() > 0) {
    String data = Serial1.readStringUntil('\n');
    data.trim();
    
    if (data == "R") {
      resetToOrigin();
    } 
    else if (data == "F1") {
      digitalWrite(laserPin, HIGH);
    }
    else if (data == "F0") {
      digitalWrite(laserPin, LOW);
    }
    // Standard "Pan,Tilt" parsing
    else if (data.indexOf(',') != -1) {
      int commaIndex = data.indexOf(',');
      int incomingPan = data.substring(0, commaIndex).toInt();
      int incomingTilt = data.substring(commaIndex + 1).toInt();
      
      targetPan = constrain(incomingPan, panMin, panMax);
      targetTilt = constrain(incomingTilt, tiltMin, tiltMax);
    }
  }

  // Lerp smoothing loop
  if (millis() - lastUpdateTime >= updateInterval) {
    lastUpdateTime = millis();
    
    currentPan = currentPan + (targetPan - currentPan) * smoothing;
    currentTilt = currentTilt + (targetTilt - currentTilt) * smoothing;
    
    panServo.write((int)currentPan);
    tiltServo.write((int)currentTilt);
  }
}

void resetToOrigin() {
  targetPan = homePan;
  targetTilt = homeTilt;
  currentPan = homePan;
  currentTilt = homeTilt;
  panServo.write(homePan);
  tiltServo.write(homeTilt);
  digitalWrite(laserPin, HIGH); // Keep laser ON during reset
}
