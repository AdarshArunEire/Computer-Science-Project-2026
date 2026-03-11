import pandas as pd
import requests
from datetime import datetime, timedelta


def fetch_weather(lat, lon, dates):
    """Fetch hourly humidity and wind speed from Open-Meteo for a set of dates.
    Tries the forecast endpoint first (covers today), falls back to the archive
    for dates older than 5 days. Returns a DataFrame indexed by datetime."""

    # Split dates into recent (forecast) and old (archive)
    cutoff = datetime.now().date() - timedelta(days=5)
    recent = [d for d in dates if d >= cutoff]
    old    = [d for d in dates if d < cutoff]

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "relative_humidity_2m,wind_speed_10m",
        "timezone": "Europe/Dublin",
        "wind_speed_unit": "ms",
    }

    frames = []

    # Forecast endpoint covers roughly -2 to +14 days from today
    if recent:
        params["start_date"] = min(recent).isoformat()
        params["end_date"]   = max(recent).isoformat()
        try:
            r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
            r.raise_for_status()
            frames.append(_parse_meteo_response(r.json()))
        except Exception as e:
            print(f"Warning: forecast API call failed ({e}). Humidity/Wind will be NaN for recent dates.")

    # Archive endpoint covers up to ~5 days ago
    if old:
        params["start_date"] = min(old).isoformat()
        params["end_date"]   = max(old).isoformat()
        try:
            r = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=10)
            r.raise_for_status()
            frames.append(_parse_meteo_response(r.json()))
        except Exception as e:
            print(f"Warning: archive API call failed ({e}). Humidity/Wind will be NaN for old dates.")

    if not frames:
        return pd.DataFrame(columns=["Humidity", "Wind_Speed"])

    return pd.concat(frames)


def _parse_meteo_response(data):
    """Parse raw Open-Meteo JSON into a DataFrame indexed by hour."""
    hourly = data["hourly"]
    df = pd.DataFrame({
        "datetime": pd.to_datetime(hourly["time"]),
        "Humidity":   hourly["relative_humidity_2m"],
        "Wind_Speed": hourly["wind_speed_10m"],
    })
    return df.set_index("datetime")


def MicrobitDataCleaner(raw_df):

    # 1. Set column name
    df = raw_df.reset_index(drop=True)
    df.columns = ["Time", "Temperature", "Soil_Moisture", "Latitude", "Longitude"]

    # 2. Parse Time column to datetime, then remove duplicate times
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.drop_duplicates(subset="Time").reset_index(drop=True)


    # 3. Parse GPS coordinates to numeric — malformed strings become NaN
    df["Latitude"]  = pd.to_numeric(df["Latitude"],  errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    # 4. Sanity-check coordinates against Ireland bounding box
    #    Anything outside this survived parser corruption — null before spike check
    valid_lat = df["Latitude"].between(51.0, 56.0)
    valid_lon = df["Longitude"].between(-10.5, -5.5)
    invalid = ~(valid_lat & valid_lon) & (df["Latitude"].notna() | df["Longitude"].notna())
    if invalid.any():
        print(f"Warning: {invalid.sum()} rows have coordinates outside Ireland bounds — setting to NaN")
        df.loc[invalid, ["Latitude", "Longitude"]] = float("nan")

    # 4a. Spike detection for GPS — GPS should be very stable between readings
    #     (walking pace ~0.00001 degrees/second). A jump of more than 0.001 degrees
    #     (~110m) from the local median is almost certainly a parser glitch, not movement
    for col in ["Latitude", "Longitude"]:
        rolling_med = df[col].rolling(window=5, center=True, min_periods=1).median()
        spikes = (df[col] - rolling_med).abs() > 0.001
        if spikes.any():
            print(f"Warning: {spikes.sum()} {col} spike(s) detected — setting to NaN for forward-fill")
            df.loc[spikes, col] = float("nan")

    # 4b. Forward-fill then back-fill GPS
    df[["Latitude", "Longitude"]] = df[["Latitude", "Longitude"]].ffill().bfill()
    df = df.dropna(subset=["Latitude", "Longitude"]).reset_index(drop=True)

    # 5. Temperature to numeric
    df["Temperature"] = pd.to_numeric(df["Temperature"], errors="coerce")
    df["Temperature"] = df["Temperature"].interpolate(method="linear").round(1)

    # 6. Moisture to numeric
    df["Soil_Moisture"] = pd.to_numeric(df["Soil_Moisture"], errors="coerce")
    df["Soil_Moisture"] = df["Soil_Moisture"].interpolate(method="linear").round(1)

    # 7. Fetch weather enrichment from Open-Meteo API
    try:
        med_lat = round(df["Latitude"].median(), 4)
        med_lon = round(df["Longitude"].median(), 4)
        unique_dates = df["Time"].dt.date.unique().tolist()

        weather_df = fetch_weather(med_lat, med_lon, unique_dates)

        if not weather_df.empty:
            # Floor each timestamp to the hour to match Open-Meteo's hourly resolution
            df["hour"] = df["Time"].dt.floor("h")
            df = df.merge(weather_df, left_on="hour", right_index=True, how="left")
            df = df.drop(columns=["hour"])
            print(f"Weather enrichment complete — {df['Humidity'].notna().sum()} rows matched")
        else:
            df["Humidity"]   = float("nan")
            df["Wind_Speed"] = float("nan")
            print("Warning: No weather data returned — Humidity and Wind_Speed set to NaN")

    except Exception as e:
        df["Humidity"]   = float("nan")
        df["Wind_Speed"] = float("nan")
        print(f"Warning: Weather enrichment failed ({e}) — Humidity and Wind_Speed set to NaN")

    # 8. Sort by datetime
    df = df.sort_values("Time").reset_index(drop=True)
    
    # 9. Final drop of any remaining NaN rows and reset index
    df = df.dropna().reset_index(drop=True)

    # 10. Export cleaned data and return df for main pipeline
    df.to_csv('data/microbit/MicrobitDataCleaned.csv', index=False)
    print("df exported to data/microbit/MicrobitDataCleaned.csv!")
    return df


# 10. If run directly, prompt for filepath, validate, and clean
if __name__ == "__main__":
    while True:
        filepath = input("Enter the filepath of file to be cleaned (use forward slashes),\n"
                         "click enter to use the default (data/microbit/MicrobitDataUncleaned.csv): ")
        if filepath == "":
            filepath = "data/microbit/MicrobitDataUncleaned.csv"
        try:
            uncleaned_df = pd.read_csv(filepath)
            if uncleaned_df.empty:
                raise ValueError("No valid data")
        except FileNotFoundError:
            print("File Not Found; Check the path?")
        except ValueError:
            print("This file is empty")
        else:
            df = MicrobitDataCleaner(uncleaned_df)
            break