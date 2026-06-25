### Project Overview
- Create a satellite-inspired telemetry system using an esp32 along with an LDR, DHT22, and MPU.

### System architecture

The system is split into two main parts
- embedded telemetry unit
- computer ground station

Sensors ---> ESP32 Telemetry Controller ---> USB Serial ---> Python ground station

### Hardware used
- ESP32
- MPU-6050
- DHT22
- Photoresistor
- Mirco-usb to C data cable
- LED
- 220 Ohm resistor
- 10k Ohm resistor
- Breadboard
- Jumper Cables

### Pin Map
<img width="727" height="508" alt="image" src="https://github.com/user-attachments/assets/70c87019-24ab-4622-b830-83fe7fc80477" />

## Software Pipeline

### ESP32 Firmware

firmware/esp32_telemetry/esp32_telemetry.ino

This firmware runs on the ESP32. It reads sensor data from the DHT22, photoresistor, and MPU6050, controls an LED status indicator, and sends telemetry packets over USB serial.

### Live Ground Station

software/live_anomaly_ground_station.py

This Python script runs on the laptop. It reads live telemetry from the ESP32, displays live graphs, detects threshold-based anomalies, and saves the run as a CSV file.

### Analysis Dashboard

software/analysis_dashboard.py

This Python script analyzes saved CSV telemetry files after a run. It generates plots and produces an analyzed CSV file with derived values and anomaly detection results.

### Telemetry Format

The ESP32 sends one telemetry packet per line in CSV format
ex.
27515,23.40,65.70,1127,Light,0.62,-0.06,9.79,-0.07,0.03,-0.01,NOMINAL

## Final Demo
What I did during the final run
- Began with nominal conditions
- covered light sensor
- shined light sensor
- Moved the breadboard
- Breathed on the sensor
- Put a fan on the sensor
- Returned to nominal


### Anamoly detection
The system uses threshold-based anomaly detection to identify abnormal telemetry

For Acceleration
-  9.8 m/s^2 is expected. Thresholds are 8.8 and 11.2


For Gyro
- Threshold is 0.7 if gyro_mag >0.8 anamoly

For Light
- Threshild is 800 if light_raw < 800 low_light

For Temp
- Tresholds are 18 and 30

## Note
- Accelaeration and Gyro used magnitudes so x^2+y^2+z^2

