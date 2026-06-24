import os
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Settings
# -----------------------------
CSV_FILE = "demo_run_01.csv"   # Change this to your actual CSV file name
PLOTS_DIR = "plots"

os.makedirs(PLOTS_DIR, exist_ok=True)

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

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(CSV_FILE)

# If the CSV was saved without headers, uncomment this instead:
# df = pd.read_csv(CSV_FILE, names=columns)

# Convert numeric columns
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

df = df.dropna(subset=numeric_columns)

# Convert time
df["time_s"] = df["time_ms"] / 1000

# Normalize time to start at 0 seconds
df["time_s"] = df["time_s"] - df["time_s"].iloc[0]

# -----------------------------
# Derived values
# -----------------------------
df["accel_mag"] = (
    df["accel_x"]**2 +
    df["accel_y"]**2 +
    df["accel_z"]**2
) ** 0.5

df["gyro_mag"] = (
    df["gyro_x"]**2 +
    df["gyro_y"]**2 +
    df["gyro_z"]**2
) ** 0.5

# -----------------------------
# Baselines
# -----------------------------
temp_mean = df["temp_c"].mean()
temp_std = df["temp_c"].std()

accel_mean = df["accel_mag"].mean()
accel_std = df["accel_mag"].std()

gyro_mean = df["gyro_mag"].mean()
gyro_std = df["gyro_mag"].std()

# -----------------------------
# Anomaly rules
# -----------------------------
LIGHT_LOW_THRESHOLD = 800

df["low_light_anomaly"] = df["light_raw"] < LIGHT_LOW_THRESHOLD

df["temp_anomaly"] = abs(df["temp_c"] - temp_mean) > (2 * temp_std)

df["motion_anomaly"] = abs(df["accel_mag"] - accel_mean) > (2 * accel_std)

df["gyro_anomaly"] = abs(df["gyro_mag"] - gyro_mean) > (2 * gyro_std)

df["any_anomaly"] = (
    df["low_light_anomaly"] |
    df["temp_anomaly"] |
    df["motion_anomaly"] |
    df["gyro_anomaly"]
)

# -----------------------------
# Print summary
# -----------------------------
print("Anomaly Detection Summary")
print("-------------------------")
print(f"Total samples: {len(df)}")
print(f"Low light anomalies: {df['low_light_anomaly'].sum()}")
print(f"Temperature anomalies: {df['temp_anomaly'].sum()}")
print(f"Motion anomalies: {df['motion_anomaly'].sum()}")
print(f"Gyro anomalies: {df['gyro_anomaly'].sum()}")
print(f"Total anomalous samples: {df['any_anomaly'].sum()}")

# Save analyzed data
OUTPUT_ANALYZED = "analyzed_telemetry.csv"
df.to_csv(OUTPUT_ANALYZED, index=False)
print(f"Analyzed data saved to {OUTPUT_ANALYZED}")

# -----------------------------
# Plot 1: Light anomalies
# -----------------------------
plt.figure()
plt.plot(df["time_s"], df["light_raw"], label="Light raw")

anomalies = df[df["low_light_anomaly"]]
plt.scatter(anomalies["time_s"], anomalies["light_raw"], label="Low light anomaly")

plt.xlabel("Time (s)")
plt.ylabel("Light raw value")
plt.title("Light Sensor Anomaly Detection")
plt.legend()
plt.grid(True)
plt.savefig(f"{PLOTS_DIR}/light_anomaly_detection.png", dpi=300, bbox_inches="tight")
plt.show()

# -----------------------------
# Plot 2: Temperature anomalies
# -----------------------------
plt.figure()
plt.plot(df["time_s"], df["temp_c"], label="Temperature")

anomalies = df[df["temp_anomaly"]]
plt.scatter(anomalies["time_s"], anomalies["temp_c"], label="Temperature anomaly")

plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Anomaly Detection")
plt.legend()
plt.grid(True)
plt.savefig(f"{PLOTS_DIR}/temperature_anomaly_detection.png", dpi=300, bbox_inches="tight")
plt.show()

# -----------------------------
# Plot 3: Motion anomalies
# -----------------------------
plt.figure()
plt.plot(df["time_s"], df["accel_mag"], label="Acceleration magnitude")

anomalies = df[df["motion_anomaly"]]
plt.scatter(anomalies["time_s"], anomalies["accel_mag"], label="Motion anomaly")

plt.xlabel("Time (s)")
plt.ylabel("Acceleration magnitude (m/s²)")
plt.title("Motion Anomaly Detection")
plt.legend()
plt.grid(True)
plt.savefig(f"{PLOTS_DIR}/motion_anomaly_detection.png", dpi=300, bbox_inches="tight")
plt.show()

# -----------------------------
# Plot 4: Gyro anomalies
# -----------------------------
plt.figure()
plt.plot(df["time_s"], df["gyro_mag"], label="Gyro magnitude")

anomalies = df[df["gyro_anomaly"]]
plt.scatter(anomalies["time_s"], anomalies["gyro_mag"], label="Gyro anomaly")

plt.xlabel("Time (s)")
plt.ylabel("Gyro magnitude (rad/s)")
plt.title("Gyroscope Anomaly Detection")
plt.legend()
plt.grid(True)
plt.savefig(f"{PLOTS_DIR}/gyro_anomaly_detection.png", dpi=300, bbox_inches="tight")
plt.show()