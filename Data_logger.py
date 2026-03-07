import serial
import pandas as pd
from datetime import datetime
from Improved_input import improved_input

def Microbit_datalogger(filepath):
    # 1. Initialise serial and variables
    ser = serial.Serial()
    ser.baudrate = 115200
    for port in range(0, 21):
        try:
            ser.port = f"COM{port}"
            ser.open()
            print(f"Port COM{port} connected")
            break
        except:
            pass
    df = pd.DataFrame(columns=["time", "temp", "light", "moisture"])
    current = {}
    csv_file = filepath
    rows_logged = 0

    # 2. Check file exists, if not ask if user wants to make new file
    try:
        exists = pd.read_csv(csv_file)
    except FileNotFoundError:
        if improved_input("File not found," +
        f"do you want to create a file with path {csv_file}? (y/n) ", ["y", "n"], None) == "y":
            print("Created file at " + csv_file + " !")
            df.to_csv(csv_file, index=False)
            exists = True
        else:
            exists = False
    else:
        exists = True
            
    try:
        print("Use Ctrl+C to exit data logger")
        session_starttime = datetime.now()
        while exists:
            
            # 3. Read line coming from Micro:Bit
            line = ser.readline().decode('utf-8').strip()
            if ':' not in line:
                print("Bad line! Should look into this....")
                continue
            key, value = line.split(':')
            key = key.strip()
            value = value.strip()

            # 4. Deduce what the line's value repersents, and assign to corresponding key in current (dict)
            if "temp" in key:
                try:
                    current["temp"] = int(value)
                except:
                    current["temp"] = pd.NA
            elif "light" in key:
                try:
                    current["light"] = int(value)
                except:
                    current["light"] = pd.NA
            elif "moisture" in key:
                try:
                    current["moisture"] = int(value)
                except:
                    current["moisture"] = pd.NA
            else:
                print("Bad line! Should look into this....")
                continue     

            # 5. If all three values have been found, append to csv with timestamp
            if len(current) == 3:
                rows_logged += 1
                current["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[len(df)] = current
                df.to_csv(csv_file, mode='a', header=False, index=False)
                print("logged row:\n", df.tail(1), "\n")
                current = {}
    except KeyboardInterrupt:
        pass
    finally:
        # 6. If loop exited, print some data and safely close port
        ser.close()
        if exists:
            session_endtime = datetime.now()
            duration = session_endtime - session_starttime
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            print(f"Data logged! {rows_logged} rows logged over {hours}h {minutes}m {seconds}s")
        else:
            print("No Data logged.")

# 7. If file ran directly, This code allows you to select a file to append logs into        
if __name__ == "__main__":
    filepath = input("Enter the filename (excluding the .csv),\n"
                         "click enter to use the default (MicrobitDataUnclean): ") + ".csv"
    if filepath == ".csv":
        filepath = "MicrobitDataUnclean.csv"
    Microbit_datalogger(filepath)
