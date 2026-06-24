import serial
import csv
import time
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------------
# Settings
# -----------------------------
SERIAL_PORT = "COM5"       # Change if your ESP32 is on a different COM port
BAUD_RATE = 115200
OUTPUT_FILE = "live_telemetry_run.csv"

MAX_POINTS = 100           # Number of points shown live on the graph

# -----------------------------
# Data storage for live graph
# -----------------------------
time_s = deque(maxlen=MAX_POINTS)
temp_c = deque(maxlen=MAX_POINTS)
humidity = deque(maxlen=MAX_POINTS)
light_raw = deque(maxlen=MAX_POINTS)
accel_mag = deque(maxlen=MAX_POINTS)

# -----------------------------
# Connect to ESP32
# -----------------------------
print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
time.sleep(2)

print("Connected.")
print(f"Saving data to {OUTPUT_FILE}")

csv_file = open(OUTPUT_FILE, mode="w", newline="")
writer = csv.writer(csv_file)

columns = [
    "time_ms",
    "temp_c",
    "humidity_percent",
    "light_raw",
    "light_status",
    "accel_x",
    "accel_y",
    "accel_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "system_status"
]

writer.writerow(columns)

# -----------------------------
# Matplotlib setup
# -----------------------------
fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
fig.suptitle("Live ESP32 Satellite Telemetry Ground Station")

def update(frame):
    try:
        line = ser.readline().decode("utf-8", errors="ignore").strip()

        if not line:
            return

        print(line)

        parts = line.split(",")

        # We expect 12 telemetry columns
        if len(parts) != 12:
            return

        # Parse values
        t_ms = float(parts[0])
        temp = float(parts[1])
        hum = float(parts[2])
        light = float(parts[3])

        ax = float(parts[5])
        ay = float(parts[6])
        az = float(parts[7])

        # Acceleration magnitude
        a_mag = (ax**2 + ay**2 + az**2) ** 0.5

        status = parts[11]

        # Save to CSV
        writer.writerow(parts)
        csv_file.flush()

        # Store for live graph
        time_s.append(t_ms / 1000)
        temp_c.append(temp)
        humidity.append(hum)
        light_raw.append(light)
        accel_mag.append(a_mag)

        # Clear plots
        for ax_plot in axs:
            ax_plot.clear()

        # Temperature
        axs[0].plot(time_s, temp_c)
        axs[0].set_ylabel("Temp (°C)")
        axs[0].grid(True)

        # Humidity
        axs[1].plot(time_s, humidity)
        axs[1].set_ylabel("Humidity (%)")
        axs[1].grid(True)

        # Light
        axs[2].plot(time_s, light_raw)
        axs[2].set_ylabel("Light raw")
        axs[2].grid(True)

        # Acceleration magnitude
        axs[3].plot(time_s, accel_mag)
        axs[3].set_ylabel("Accel mag")
        axs[3].set_xlabel("Time (s)")
        axs[3].grid(True)

        fig.suptitle(f"Live ESP32 Satellite Telemetry Ground Station | Status: {status}")

    except ValueError:
        # Skip bad rows like headers or startup messages
        return

    except Exception as e:
        print("Error:", e)
        return

ani = FuncAnimation(fig, update, interval=500)

try:
    plt.show()

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    ser.close()
    csv_file.close()
    print("Serial port closed.")
    print("CSV file saved.")