import pandas as pd
import requests
from datetime import datetime, timedelta


# Fetches hourly humidity, wind speed and rainfall from the Open-Meteo archive API
def fetch_weather(lat, lon, dates):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "relative_humidity_2m,wind_speed_10m,precipitation",
        "timezone": "Europe/Dublin",
        "wind_speed_unit": "ms",
        "start_date": min(dates).isoformat(),
        "end_date": max(dates).isoformat(),
    }
    try:
        r = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=10)
        r.raise_for_status()
        return _parse_meteo_response(r.json())
    except Exception as e:
        print(f"Warning: archive API call failed ({e})")
        return pd.DataFrame(columns=["Humidity", "Wind_Speed", "Rainfall"])


# Parses the raw JSON response from Open-Meteo into a DataFrame indexed by hour
def _parse_meteo_response(data):
    hourly = data["hourly"]
    df = pd.DataFrame({
        "datetime":   pd.to_datetime(hourly["time"]),
        "Humidity":   hourly["relative_humidity_2m"],
        "Wind_Speed": hourly["wind_speed_10m"],
        "Rainfall":   hourly["precipitation"],
    })
    return df.set_index("datetime")

def MicrobitDataCleaner(raw_df):

    # 1. Set column names, parse time, drop duplicates
    df = raw_df.reset_index(drop=True)
    df.columns = ["Time", "Temperature", "Soil_Moisture", "Latitude", "Longitude"]
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"])
    df = df.drop_duplicates(subset="Time").reset_index(drop=True)

    # 2. GPS to numeric, remove coordinates outside Ireland bounding box
    df["Latitude"]  = pd.to_numeric(df["Latitude"],  errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    valid_lat = df["Latitude"].between(51.0, 56.0)
    valid_lon = df["Longitude"].between(-10.5, -5.5)
    invalid = ~(valid_lat & valid_lon) & (df["Latitude"].notna() | df["Longitude"].notna())
    if invalid.any():
        print(f"Warning: {invalid.sum()} rows outside Ireland bounds — setting to NaN")
        df.loc[invalid, ["Latitude", "Longitude"]] = float("nan")

    # 3. Fill NaN coords, bfill then ffill
    if df["Latitude"].isna().all() or df["Longitude"].isna().all():
        raise ValueError("No valid GPS coordinates")
    df[["Latitude", "Longitude"]] = df[["Latitude", "Longitude"]].bfill().ffill()

    # 4. Temperature and moisture to numeric, interpolate any missing values
    df["Temperature"]   = pd.to_numeric(df["Temperature"],   errors="coerce")
    df["Soil_Moisture"] = pd.to_numeric(df["Soil_Moisture"], errors="coerce")
    df["Temperature"]   = df["Temperature"].interpolate(method="linear")
    df["Soil_Moisture"] = df["Soil_Moisture"].interpolate(method="linear")

    # 5. Export raw cleaned data (every log entry)
    df_raw = df[["Time", "Temperature", "Soil_Moisture", "Latitude", "Longitude"]].copy()
    df_raw = df_raw.sort_values("Time").reset_index(drop=True)
    df_raw.to_csv("Artefact/data/MicrobitDataClean.csv", index=False)
    print(f"Raw export complete, {len(df_raw)} rows at data/MicrobitDataClean.csv")

    # 6. Fetch weather for all dates in the dataset
    med_lat = round(df["Latitude"].median(), 4)
    med_lon = round(df["Longitude"].median(), 4)
    unique_dates = df["Time"].dt.date.unique().tolist()
    weather_df = fetch_weather(med_lat, med_lon, unique_dates)

    # 7. Floor timestamps to the hour, average all readings in each hour, merge weather
    df_h = df.copy()
    df_h["Time"] = df_h["Time"].dt.floor("h")

    df_h = df_h.groupby("Time", as_index=False).agg(
        Temperature  =("Temperature",   "mean"),
        Soil_Moisture=("Soil_Moisture",  "mean"),
    )
    df_h["Temperature"]   = df_h["Temperature"].round(1)
    df_h["Soil_Moisture"] = df_h["Soil_Moisture"].round(1)

    if not weather_df.empty:
        df_h = df_h.merge(weather_df, left_on="Time", right_index=True, how="left")
        print(f"Weather API call successful! Merged weather data for {len(weather_df)} hours")
    else:
        df_h["Humidity"]   = float("nan")
        df_h["Wind_Speed"] = float("nan")
        df_h["Rainfall"]   = float("nan")

    # 8. Final clean for cleaned hourly data, export
    df_h = df_h.sort_values("Time").dropna().reset_index(drop=True)
    df_h.to_csv("Artefact/data/MicrobitDataHourlyClean.csv", index=False)
    print(f"Hourly export complete, {len(df_h)} rows at data/MicrobitDataHourlyClean.csv")

    # 9. Aggregate to one row per day
    df_d = df_h.copy()
    df_d["Date"] = pd.to_datetime(df_d["Time"].dt.date)


    # 10. Find rows at noon, set daily data, export
    noon_rows = df_d[df_d["Time"].dt.hour == 12].set_index("Date")

    df_daily = df_d.groupby("Date").agg(
        Soil_Moisture=("Soil_Moisture", "mean"), # Mean moisture
        Rainfall     =("Rainfall",      "sum"), # Total rainfall
    ).round(2)
    df_daily["Temperature"] = noon_rows["Temperature"].round(2) # Temperature at noon
    df_daily["Humidity"]    = noon_rows["Humidity"].round(2) # Humidity at noon
    df_daily["Wind_Speed"]  = noon_rows["Wind_Speed"].round(2) # Wind speed at noon

    df_daily = df_daily[["Temperature", "Soil_Moisture", "Humidity", "Wind_Speed", "Rainfall"]]
    df_daily = df_daily.dropna().reset_index()
    df_daily.to_csv("Artefact/data/MicrobitDataDailyClean.csv", index=False)
    print(f"Daily export complete, {len(df_daily)} rows at artefact/data/MicrobitDataDailyClean.csv")
    return df_raw, df_h, df_daily


# If run directly, prompt for filepath, validate, and clean
if __name__ == "__main__":
    while True:
        filepath = input("Enter the filepath of file to be cleaned (use forward slashes),\n"
                         "click enter to use the default (data/MicrobitDataUncleaned.csv): ")
        if filepath == "":
            filepath = "artefact/data/MicrobitDataUncleaned.csv"
        try:
            uncleaned_df = pd.read_csv(filepath)
            if uncleaned_df.empty:
                raise ValueError("No valid data")
        except FileNotFoundError:
            print("File Not Found; Check the path?")
        except ValueError:
            print("This file is empty")
        else:
            raw_df, hourly_df, daily_df = MicrobitDataCleaner(uncleaned_df)
            break