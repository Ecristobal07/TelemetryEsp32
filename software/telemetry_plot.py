import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "demo1.csv"
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

df = pd.read_csv(CSV_FILE, names=columns)

# Convert numeric columns from text to numbers
numeric_columns = [
    "time_ms",
    "temp_c",
    "humidity_percent",
    "light_raw",
    "accel_x",
    "accel_y",
    "accel_z",
    "gyro_x",
    "gyro_y",
    "gyro_z"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove bad/header/error rows
df = df.dropna(subset=["time_ms", "temp_c", "humidity_percent", "light_raw"])

# Convert time from milliseconds to seconds
df["time_s"] = df["time_ms"] / 1000

print(df.head())

plt.figure()
plt.plot(df["time_s"], df["temp_c"])
plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature vs Time")
plt.grid(True)
plt.show()

plt.figure()
plt.plot(df["time_s"], df["humidity_percent"])
plt.xlabel("Time (s)")
plt.ylabel("Humidity (%)")
plt.title("Humidity vs Time")
plt.grid(True)
plt.show()

plt.figure()
plt.plot(df["time_s"], df["light_raw"])
plt.xlabel("Time (s)")
plt.ylabel("Light Raw Value")
plt.title("Light Sensor vs Time")
plt.grid(True)
plt.show()

plt.figure()
plt.plot(df["time_s"], df["accel_x"], label="Accel X")
plt.plot(df["time_s"], df["accel_y"], label="Accel Y")
plt.plot(df["time_s"], df["accel_z"], label="Accel Z")
plt.xlabel("Time (s)")
plt.ylabel("Acceleration (m/s²)")
plt.title("MPU6050 Acceleration vs Time")
plt.legend()
plt.grid(True)
plt.show()