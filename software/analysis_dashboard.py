"""
Post-run interactive telemetry dashboard.

Loads a saved CSV, runs the same 2-sigma statistical anomaly detection as
anomaly_detection.py, and shows a clickable 3x2 panel grid:
  - click any panel to expand it full-size (Back button to return)
  - toggle anomaly markers on/off with the checkbox

Usage:
    python analysis_dashboard.py                # uses CSV_FILE below
    python analysis_dashboard.py demo1.csv      # or pass a file on the command line
"""

import sys

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Button

# -----------------------------
# Settings
# -----------------------------
CSV_FILE = "finalrun.csv"   # default; override with a command-line arg
LIGHT_LOW_THRESHOLD = 800             # same fixed light rule as anomaly_detection.py

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
    "system_status",
]

numeric_columns = [
    "time_ms", "temp_c", "humidity_percent", "light_raw",
    "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z",
]


# -----------------------------
# Load + prepare data
# -----------------------------
def load_csv(path):
    """Load a telemetry CSV whether or not it has a header row, and whether it
    has 12 raw columns or extra ones (e.g. live_anomaly_run.csv). Keeps the
    first 12 standard columns."""
    raw = pd.read_csv(path, header=None, dtype=str)

    # Drop a header row if the first cell isn't a number
    first_cell = str(raw.iloc[0, 0]).strip()
    try:
        float(first_cell)
    except ValueError:
        raw = raw.iloc[1:].reset_index(drop=True)

    raw = raw.iloc[:, :12]
    raw.columns = columns
    return raw


csv_path = sys.argv[1] if len(sys.argv) > 1 else CSV_FILE
print(f"Loading {csv_path} ...")
df = load_csv(csv_path)

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_columns).reset_index(drop=True)

# Time in seconds, normalized to start at 0
df["time_s"] = df["time_ms"] / 1000
df["time_s"] = df["time_s"] - df["time_s"].iloc[0]

# Derived magnitudes
df["accel_mag"] = (df["accel_x"]**2 + df["accel_y"]**2 + df["accel_z"]**2) ** 0.5
df["gyro_mag"] = (df["gyro_x"]**2 + df["gyro_y"]**2 + df["gyro_z"]**2) ** 0.5

# -----------------------------
# 2-sigma statistical anomalies (matches anomaly_detection.py)
# -----------------------------
temp_mean, temp_std = df["temp_c"].mean(), df["temp_c"].std()
accel_mean, accel_std = df["accel_mag"].mean(), df["accel_mag"].std()
gyro_mean, gyro_std = df["gyro_mag"].mean(), df["gyro_mag"].std()

df["temp_anomaly"] = abs(df["temp_c"] - temp_mean) > (2 * temp_std)
df["low_light_anomaly"] = df["light_raw"] < LIGHT_LOW_THRESHOLD
df["motion_anomaly"] = abs(df["accel_mag"] - accel_mean) > (2 * accel_std)
df["gyro_anomaly"] = abs(df["gyro_mag"] - gyro_mean) > (2 * gyro_std)
df["any_anomaly"] = (
    df["temp_anomaly"] | df["low_light_anomaly"] |
    df["motion_anomaly"] | df["gyro_anomaly"]
)

print("Anomaly Detection Summary")
print("-------------------------")
print(f"Total samples: {len(df)}")
print(f"Temperature anomalies: {df['temp_anomaly'].sum()}")
print(f"Low light anomalies:   {df['low_light_anomaly'].sum()}")
print(f"Motion anomalies:      {df['motion_anomaly'].sum()}")
print(f"Gyro anomalies:        {df['gyro_anomaly'].sum()}")
print(f"Total anomalous samples: {df['any_anomaly'].sum()}")

# -----------------------------
# Panel definitions: (title, y-label, color, value column, anomaly mask column)
# Humidity has no anomaly rule -> mask column is None.
# -----------------------------
SENSORS = [
    ("Temperature",  "Temp (°C)",        "tab:red",    "temp_c",      "temp_anomaly"),
    ("Humidity",     "Humidity (%)",     "tab:blue",   "humidity_percent", None),
    ("Light",        "Light (raw)",      "tab:orange", "light_raw",   "low_light_anomaly"),
    ("Acceleration", "Accel mag (m/s²)", "tab:green",  "accel_mag",   "motion_anomaly"),
    ("Gyroscope",    "Gyro mag (rad/s)", "tab:purple", "gyro_mag",    "gyro_anomaly"),
]

state = {"detail": None, "anomaly": True}

# -----------------------------
# Figure + interaction
# -----------------------------
fig = plt.figure(figsize=(12, 8))
widgets = {}
plot_axes = []   # list of (axis, sensor_index)


def draw_sensor(ax, idx, detail=False):
    title, ylabel, color, value_col, mask_col = SENSORS[idx]
    ax.clear()
    ax.plot(df["time_s"], df[value_col], color=color, label=title)

    if state["anomaly"] and mask_col is not None:
        hits = df[df[mask_col]]
        if len(hits) > 0:
            ax.scatter(hits["time_s"], hits[value_col], color="red", marker="x",
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
    fig.clf()
    plot_axes.clear()

    cax = fig.add_axes([0.01, 0.93, 0.20, 0.06])
    cax.set_frame_on(False)
    check = CheckButtons(cax, ["Show anomalies"], [state["anomaly"]])
    check.on_clicked(toggle_anomaly)
    widgets["check"] = check

    if state["detail"] is None:
        gs = fig.add_gridspec(3, 2, top=0.88, bottom=0.07,
                              left=0.07, right=0.97, hspace=0.55, wspace=0.22)
        positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
        for idx, (r, c) in enumerate(positions):
            ax = fig.add_subplot(gs[r, c])
            draw_sensor(ax, idx, detail=False)
            plot_axes.append((ax, idx))

        info_ax = fig.add_subplot(gs[2, 1])
        info_ax.axis("off")
        widgets["info_ax"] = info_ax
    else:
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
    total = int(df["any_anomaly"].sum())
    status = f"{total} anomalous samples" if state["anomaly"] else "anomaly display off"
    fig.suptitle(f"Telemetry Analysis — {csv_path}  |  {status}",
                 fontsize=12, fontweight="bold")

    if state["detail"] is None and "info_ax" in widgets:
        info_ax = widgets["info_ax"]
        info_ax.clear()
        info_ax.axis("off")
        if state["anomaly"]:
            txt = (
                f"Summary  ({len(df)} samples)\n"
                f"Temp:   {int(df['temp_anomaly'].sum())}\n"
                f"Light:  {int(df['low_light_anomaly'].sum())}\n"
                f"Motion: {int(df['motion_anomaly'].sum())}\n"
                f"Gyro:   {int(df['gyro_anomaly'].sum())}"
            )
            color = "green" if total == 0 else "red"
        else:
            txt = "(anomaly display off)"
            color = "gray"
        info_ax.text(0.5, 0.5, txt, ha="center", va="center", fontsize=11,
                     color=color, fontweight="bold", family="monospace",
                     transform=info_ax.transAxes)


def redraw():
    detail = state["detail"] is not None
    for ax, idx in plot_axes:
        draw_sensor(ax, idx, detail=detail)
    update_title()


def on_click(event):
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

build_layout()
plt.show()
