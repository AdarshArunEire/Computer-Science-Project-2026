import serial
import time
import pandas as pd
from datetime import datetime

def parse_gpgga(sentence):
    #Extract decimal lat/lon from a $GPGGA sentence.
    #Returns (latitude, longitude) as floats, or (None, None) if malformed.
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
        # Truncated fields (e.g. '0624.4671' instead of '00624.4671') produce value
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
    

ser = serial.Serial()
ser.baudrate = 115200
ser.port = "com15"
ser.open()

while True:
    line = ser.readline().decode('utf-8').strip()
    gps_string =""
    
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
            print(gps_string)
        continue 
        