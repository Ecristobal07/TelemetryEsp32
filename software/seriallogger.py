import serial
import csv
import time
import os

SERIAL_PORT = "COM5"   # Change if your ESP32 uses a different COM port
BAUD_RATE = 115200
FILE_PREFIX = "demo"   # Output files are named demo1.csv, demo2.csv, ...

def next_output_file(prefix=FILE_PREFIX):
    """Return the next unused filename: demo1.csv, demo2.csv, demo3.csv, ..."""
    n = 1
    while os.path.exists(f"{prefix}{n}.csv"):
        n += 1
    return f"{prefix}{n}.csv"

def main():
    OUTPUT_FILE = next_output_file()

    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    except serial.SerialException as e:
        print("Could not open serial port.")
        print(e)
        return

    time.sleep(2)

    print(f"Logging telemetry to {OUTPUT_FILE}. Press Ctrl+C to stop.")

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        try:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if not line:
                    continue

                print(line)

                parts = line.split(",")

                if len(parts) == 12:
                    writer.writerow(parts)
                    file.flush()

        except KeyboardInterrupt:
            print("\nLogging stopped by user.")

        finally:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
