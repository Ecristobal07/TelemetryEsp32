# Software

This folder contains the two main python scripts used on the computer side ground station and post-run analysis.

## live_anamoly_ground_Station.py
Reads live telemetry data from the ESP32 over USB serial, displays interactive live plots, performs threshold- based anomaly detection, and saves telemetry to a csv file. 

## analysis_dashboard.py
Loads saved telemetry CSV files, generates plots, and analyzes telemetry data after live_anamoly_ground_Station.py is closed. More suitable for post-analysus

## Requirements

Install dependecnies with:
python -m pip install pyserial pandas matplotlib

## Usage
1. Upload the ESP32 firmware.
2. Close the Arduino Serial Monitor
3. Run the live ground station.

live_anamoly_ground_Station.py

4, Annalyze a saved run

analysis_dashboard.py
