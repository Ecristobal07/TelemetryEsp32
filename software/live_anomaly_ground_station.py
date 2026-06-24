import serial
import csv
import time
import os
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import CheckButtons, Button

# -----------------------------
# Settings
# -----------------------------
SERIAL_PORT = "COM5"       # Change if your ESP32 uses a different COM port
BAUD_RATE = 115200
OUTPUT_FILE = "live_anomaly_run.csv"
RAW_FILE_PREFIX = "demo"    # Raw seriallogger-style copy: demo1.csv, demo2.csv, ...

MAX_POINTS = 100


def next_output_file(prefix=RAW_FILE_PREFIX):
    """Return the next unused filename: demo1.csv, demo2.csv, ... (matches seriallogger.py)."""
    n = 1
    while os.path.exists(f"{prefix}{n}.csv"):
        n += 1
    return f"{prefix}{n}.csv"

# -----------------------------
# Anomaly thresholds
# Tune these based on your actual data
# -----------------------------
LIGHT_LOW_THRESHOLD = 800

TEMP_LOW_THRESHOLD = 18.0
TEMP_HIGH_THRESHOLD = 30.0

ACCEL_MAG_LOW_THRESHOLD = 8.8
ACCEL_MAG_HIGH_THRESHOLD = 11.2

GYRO_MAG_THRESHOLD = 0.8

# -----------------------------
# Live data storage
# -----------------------------
time_s = deque(maxlen=MAX_POINTS)
temp_c = deque(maxlen=MAX_POINTS)
humidity = deque(maxlen=MAX_POINTS)
light_raw = deque(maxlen=MAX_POINTS)
accel_mag = deque(maxlen=MAX_POINTS)
gyro_mag = deque(maxlen=MAX_POINTS)

# Separate anomaly markers
temp_anom_t = deque(maxlen=MAX_POINTS)
temp_anom_y = deque(maxlen=MAX_POINTS)

light_anom_t = deque(maxlen=MAX_POINTS)
light_anom_y = deque(maxlen=MAX_POINTS)

motion_anom_t = deque(maxlen=MAX_POINTS)
motion_anom_y = deque(maxlen=MAX_POINTS)

gyro_anom_t = deque(maxlen=MAX_POINTS)
gyro_anom_y = deque(maxlen=MAX_POINTS)

# -----------------------------
# Sensor panel definitions
# Each: (title, y-axis label, line color, data deque, anomaly-t deque, anomaly-y deque)
# Humidity has no anomaly rule, so its anomaly deques are None.
# -----------------------------
SENSORS = [
    ("Temperature", "Temp (°C)",        "tab:red",    temp_c,    temp_anom_t,  temp_anom_y),
    ("Humidity",    "Humidity (%)",     "tab:blue",   humidity,  None,         None),
    ("Light",       "Light (raw)",      "tab:orange", light_raw, light_anom_t, light_anom_y),
    ("Acceleration", "Accel mag (m/s²)", "tab:green",  accel_mag, motion_anom_t, motion_anom_y),
    ("Gyroscope",   "Gyro mag (rad/s)", "tab:purple", gyro_mag,  gyro_anom_t,  gyro_anom_y),
]

# UI state shared across callbacks
state = {
    "detail": None,      # None = overview grid, otherwise index into SENSORS
    "anomaly": True,     # show/hide anomaly markers (detection always runs)
    "status": "NOMINAL",
}

# -----------------------------
# Connect to ESP32
# -----------------------------
print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
time.sleep(2)

print("Connected.")

# Raw seriallogger-style copy: 12 fields, no header, auto-incrementing name
RAW_FILE = next_output_file()

print(f"Saving anomaly log to {OUTPUT_FILE}")
print(f"Saving raw seriallogger-style copy to {RAW_FILE}")

csv_file = open(OUTPUT_FILE, mode="w", newline="")
writer = csv.writer(csv_file)

raw_file = open(RAW_FILE, mode="w", newline="")
raw_writer = csv.writer(raw_file)

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
    "esp32_system_status",
    "python_anomaly_status"
]

writer.writerow(columns)

# -----------------------------
# Anomaly detection function
# -----------------------------
def detect_anomalies(temp, light, a_mag, g_mag):
    anomalies = []

    if light < LIGHT_LOW_THRESHOLD:
        anomalies.append("LOW_LIGHT")

    if temp < TEMP_LOW_THRESHOLD:
        anomalies.append("TEMP_LOW")

    if temp > TEMP_HIGH_THRESHOLD:
        anomalies.append("TEMP_HIGH")

    if a_mag < ACCEL_MAG_LOW_THRESHOLD or a_mag > ACCEL_MAG_HIGH_THRESHOLD:
        anomalies.append("MOTION_ANOMALY")

    if g_mag > GYRO_MAG_THRESHOLD:
        anomalies.append("GYRO_ANOMALY")

    if not anomalies:
        return ["NOMINAL"]

    return anomalies

# -----------------------------
# Matplotlib setup
# -----------------------------
fig = plt.figure(figsize=(12, 8))

# Persistent widget + axis references (kept alive so callbacks keep working)
widgets = {}
plot_axes = []   # list of (axis, sensor_index) currently drawn


def draw_sensor(ax, idx, detail=False):
    """Draw a single sensor panel into the given axis."""
    title, ylabel, color, data, anom_t, anom_y = SENSORS[idx]
    ax.clear()
    ax.plot(time_s, data, color=color, label=title)

    if state["anomaly"] and anom_t is not None and len(anom_t) > 0:
        ax.scatter(list(anom_t), list(anom_y), color="red", marker="x",
                   s=60, zorder=5, label="Anomaly")

    ax.set_ylabel(ylabel)
    ax.grid(True)

    if detail:
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel("Time (s)")
        ax.legend(loc="upper left")
    else:
        ax.set_title(f"{title}  (click to expand)", fontsize=9)


def build_layout():
    """Rebuild the figure for the current view (overview grid or single detail)."""
    fig.clf()
    plot_axes.clear()

    # Anomaly on/off toggle (top-left, always present)
    cax = fig.add_axes([0.01, 0.93, 0.20, 0.06])
    cax.set_frame_on(False)
    check = CheckButtons(cax, ["Show anomalies"], [state["anomaly"]])
    check.on_clicked(toggle_anomaly)
    widgets["check"] = check

    if state["detail"] is None:
        # ---- Overview: 3x2 grid of clickable panels ----
        gs = fig.add_gridspec(3, 2, top=0.88, bottom=0.07,
                              left=0.07, right=0.97,
                              hspace=0.55, wspace=0.22)
        positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
        for idx, (r, c) in enumerate(positions):
            ax = fig.add_subplot(gs[r, c])
            draw_sensor(ax, idx, detail=False)
            plot_axes.append((ax, idx))

        # Live status banner in the empty grid cell
        info_ax = fig.add_subplot(gs[2, 1])
        info_ax.axis("off")
        widgets["info_ax"] = info_ax
    else:
        # ---- Detail: one large panel + Back button ----
        back_ax = fig.add_axes([0.22, 0.93, 0.12, 0.06])
        back_btn = Button(back_ax, "← Back")
        back_btn.on_clicked(go_back)
        widgets["back"] = back_btn

        ax = fig.add_axes([0.08, 0.10, 0.88, 0.78])
        idx = state["detail"]
        draw_sensor(ax, idx, detail=True)
        plot_axes.append((ax, idx))

    update_title()


def update_title():
    """Refresh the figure-level status banner."""
    status = state["status"] if state["anomaly"] else "anomaly display off"
    fig.suptitle(
        f"Live ESP32 Satellite Telemetry  |  Status: {status}",
        fontsize=12, fontweight="bold",
    )

    # In overview, also fill the status text cell
    if state["detail"] is None and "info_ax" in widgets:
        info_ax = widgets["info_ax"]
        info_ax.clear()
        info_ax.axis("off")
        shown = state["status"] if state["anomaly"] else "(anomaly display off)"
        color = "green" if (shown == "NOMINAL" or not state["anomaly"]) else "red"
        info_ax.text(0.5, 0.5, f"System status\n{shown}",
                     ha="center", va="center", fontsize=13,
                     color=color, fontweight="bold",
                     transform=info_ax.transAxes)


def redraw():
    """Redraw whatever panels are currently visible with the latest data."""
    detail = state["detail"] is not None
    for ax, idx in plot_axes:
        draw_sensor(ax, idx, detail=detail)
    update_title()


# -----------------------------
# Interaction callbacks
# -----------------------------
def on_click(event):
    # Only react to clicks on a panel while in the overview
    if state["detail"] is not None or event.inaxes is None:
        return
    for ax, idx in plot_axes:
        if event.inaxes is ax:
            state["detail"] = idx
            build_layout()
            fig.canvas.draw_idle()
            return


def go_back(event):
    state["detail"] = None
    build_layout()
    fig.canvas.draw_idle()


def toggle_anomaly(label):
    state["anomaly"] = not state["anomaly"]
    redraw()
    fig.canvas.draw_idle()


fig.canvas.mpl_connect("button_press_event", on_click)


# -----------------------------
# Animation / data acquisition
# -----------------------------
def update(frame):
    try:
        line = ser.readline().decode("utf-8", errors="ignore").strip()

        if not line:
            return

        parts = line.split(",")

        # Expected 12 columns from ESP32
        if len(parts) != 12:
            return

        # Parse ESP32 telemetry packet
        t_ms = float(parts[0])
        temp = float(parts[1])
        hum = float(parts[2])
        light = float(parts[3])

        ax = float(parts[5])
        ay = float(parts[6])
        az = float(parts[7])

        gx = float(parts[8])
        gy = float(parts[9])
        gz = float(parts[10])

        esp32_status = parts[11]

        # Derived values
        a_mag = (ax**2 + ay**2 + az**2) ** 0.5
        g_mag = (gx**2 + gy**2 + gz**2) ** 0.5

        anomalies = detect_anomalies(temp, light, a_mag, g_mag)
        python_status = "|".join(anomalies)
        state["status"] = python_status

        t = t_ms / 1000

        # Print live status
        print(
            f"t={t:.1f}s | "
            f"T={temp:.2f}C | "
            f"H={hum:.1f}% | "
            f"Light={light:.0f} | "
            f"AccelMag={a_mag:.2f} | "
            f"GyroMag={g_mag:.2f} | "
            f"Status={python_status}"
        )

        # Save to CSV (detection always runs and is always logged)
        writer.writerow(parts + [python_status])
        csv_file.flush()

        # Save raw seriallogger-style copy: the 12 fields, no header
        raw_writer.writerow(parts)
        raw_file.flush()

        # Store live data
        time_s.append(t)
        temp_c.append(temp)
        humidity.append(hum)
        light_raw.append(light)
        accel_mag.append(a_mag)
        gyro_mag.append(g_mag)

        # Store anomaly markers on their matching plots
        if "TEMP_LOW" in anomalies or "TEMP_HIGH" in anomalies:
            temp_anom_t.append(t)
            temp_anom_y.append(temp)

        if "LOW_LIGHT" in anomalies:
            light_anom_t.append(t)
            light_anom_y.append(light)

        if "MOTION_ANOMALY" in anomalies:
            motion_anom_t.append(t)
            motion_anom_y.append(a_mag)

        if "GYRO_ANOMALY" in anomalies:
            gyro_anom_t.append(t)
            gyro_anom_y.append(g_mag)

        redraw()

    except ValueError:
        return

    except Exception as e:
        print("Error:", e)
        return


# Initial layout, then start streaming
build_layout()
ani = FuncAnimation(fig, update, interval=500, cache_frame_data=False)

try:
    plt.show()

finally:
    print("Closing ground station...")

    if ser.is_open:
        ser.close()

    csv_file.close()
    raw_file.close()

    print("Serial port closed.")
    print("CSV files saved.")
