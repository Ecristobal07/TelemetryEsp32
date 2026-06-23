import serial
import csv
import time

SERIAL_PORT = "COM5"   # Change if your ESP32 uses a different COM port
BAUD_RATE = 115200
OUTPUT_FILE = "telemetry.csv"

def main():
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
