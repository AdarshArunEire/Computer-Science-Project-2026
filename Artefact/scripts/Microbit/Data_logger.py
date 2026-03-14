import serial
import time
import pandas as pd
from datetime import datetime
from GPSlogger import parse_gpgga

# Helper function to get valid inputs
def improved_input(prompt, list_ans, ans_type):
    
    while True:
        ans = input(prompt).lower()
        
        if ans_type is not None:
            if ans_type == "int":
                try:
                    ans = int(ans)
                except:
                    print("Please enter an integer")
                    continue
            elif ans_type == "float":
                try:
                    ans = float(ans)
                except:
                    print("Plese enter a number")
                    continue
                
        if list_ans is not None:
            if ans not in list_ans:
                print("Input not valid, try again")
                continue
        
        return ans


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