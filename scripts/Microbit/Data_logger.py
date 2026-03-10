import serial
import time
import pandas as pd
from datetime import datetime
from Improved_input import improved_input


def parse_gpgga(sentence):
    """Extract decimal lat/lon from a $GPGGA sentence.
    Returns (latitude, longitude) as floats, or (None, None) if malformed."""
    try:
        parts = sentence.split(',')
        # Need at least 6 fields and a non-empty fix indicator
        if len(parts) < 6 or parts[6] == '0':
            return None, None

        raw_lat = parts[2]   # e.g. '5330.4677'
        lat_dir = parts[3]   # 'N' or 'S'
        raw_lon = parts[4]   # e.g. '00624.4671'
        lon_dir = parts[5]   # 'E' or 'W'

        if not raw_lat or not raw_lon:
            return None, None

        # NMEA lat must be DDMM.MMMM (min 7 chars), lon must be DDDMM.MMMM (min 8 chars)
        # Truncated fields (e.g. '0624.4671' instead of '00624.4671') produce wrong degree
        # extraction — reject them rather than silently logging a bad coordinate
        if len(raw_lat) < 7 or len(raw_lon) < 8:
            return None, None

        # NMEA format: DDDMM.MMMM — split into degrees and minutes
        lat_deg = int(float(raw_lat) / 100)
        lat_min = float(raw_lat) - lat_deg * 100
        latitude = lat_deg + lat_min / 60
        if lat_dir == 'S':
            latitude *= -1

        lon_deg = int(float(raw_lon) / 100)
        lon_min = float(raw_lon) - lon_deg * 100
        longitude = lon_deg + lon_min / 60
        if lon_dir == 'W':
            longitude *= -1

        return round(latitude, 6), round(longitude, 6)

    except (ValueError, IndexError):
        return None, None


def Microbit_datalogger(filepath):
    # 1. Initialise serial
    ser = serial.Serial()
    ser.baudrate = 115200
    while True:
        port = improved_input('Enter the COM port number your Microbit is connected to (eg 3 for COM3): ', None, 'int')
        ser.port = f"COM{port}"
        try:
            ser.open()
            print(f"Port COM{port} connected")
            break
        except:
            print(f"Failed to connect to port COM{port}. Check by typing mode into powershell.")

    df = pd.DataFrame(columns=["time", "temp", "moisture", "latitude", "longitude"])
    current = {}
    csv_file = filepath
    rows_logged = 0
    last_lat = None   # Most recent valid GPS fix — carried forward each row
    last_lon = None

    # 2. Check file exists, if not ask if user wants to make new file
    try:
        exists = pd.read_csv(csv_file)
    except FileNotFoundError:
        if improved_input(f"File not found, do you want to create a file with path {csv_file}? (y/n) ", ["y", "n"], None) == "y":
            print("Created file at " + csv_file + " !")
            df.to_csv(csv_file, index=False)
            exists = True
        else:
            exists = False
    else:
        exists = True

    try:
        if exists:
            print("Use Ctrl+C to exit data logger")
            session_starttime = datetime.now()

        while exists:
            # 3. Read next line from Micro:Bit
            line = ser.readline().decode('utf-8').strip()

            # 4. Handle GPS block — Micro:Bit sends GPSSTART, raw NMEA chunks, then GPSEND
            if line == "GPSSTART":
                gps_string = ""
                start_time = time.time()
                while time.time() - start_time < 3:
                    chunk = ser.readline().decode("utf-8").strip()
                    if chunk == "GPSEND":
                        if gps_string.startswith("$GPGGA") and len(gps_string) > 10:
                            lat, lon = parse_gpgga(gps_string)
                            if lat is not None:
                                last_lat, last_lon = lat, lon
                        break
                    gps_string += chunk
                continue  # GPS block handled — back to top of loop

            # 5. Handle key:value sensor lines
            if ':' not in line:
                continue  # Noise lines (e.g. RSSI readings) — skip silently

            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            if "temp" in key:
                try:
                    current["temp"] = int(value)
                except ValueError:
                    current["temp"] = pd.NA
            elif "moisture" in key:
                try:
                    current["moisture"] = int(value)
                except ValueError:
                    current["moisture"] = pd.NA
            else:
                continue  # Unrecognised key — skip silently

            # 6. Once both temp and moisture received, write row with last known GPS fix
            if len(current) == 2:
                rows_logged += 1
                current["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current["latitude"] = last_lat
                current["longitude"] = last_lon
                df.loc[len(df)] = current
                df.to_csv(csv_file, mode='a', header=False, index=False)
                print("logged row:\n", df.tail(1), "\n")
                current = {}

    except KeyboardInterrupt:
        pass
    finally:
        if exists:
            # 7. Safely close port and print session summary
            ser.close()
            session_endtime = datetime.now()
            duration = session_endtime - session_starttime
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            print(f"Data logged! {rows_logged} rows logged over {hours}h {minutes}m {seconds}s")
        else:
            print("No data logged.")


# 8. If run directly, prompt for filepath
if __name__ == "__main__":
    filepath = input("Enter the filepath to append to,\n"
                     "click enter to use the default (data/microbit/MicrobitDataUncleaned.csv): ")
    if filepath == "":
        filepath = "data/microbit/MicrobitDataUncleaned.csv"

    Microbit_datalogger(filepath)