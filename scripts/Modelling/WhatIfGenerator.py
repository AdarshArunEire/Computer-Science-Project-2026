import pandas as pd 
import numpy as np

# Generate temp values based on daylight cycle
def generate_temperature_values(hour, min_temp, max_temp):
    a = (min_temp + max_temp) / 2 # Midway line
    b = (max_temp - min_temp) / 2 # Amplitude
    c = (2 * np.pi) / 24          # Frequency (every 24h)
    x = hour - 15                 # Shift graph's peak to 3pm (hour 15)

    return a + b * np.cos(c * x) + np.random.normal(0, 5) # Add some noise for realism

# Generate soil moisture values based on rainfall and drying factors
def update_soil_moisture(previous_moisture, rain, temp, wind):

    drying = 0.6 * temp + 0.4 * wind # Temp and wind are factors in drying
    rain_gain = rain * 300 # Rain increases soil moisture drastically
    new_moisture = previous_moisture + rain_gain - drying * 0.3

    return np.clip(new_moisture, 200, 800)

# 1. Generate a df of a dryspell scenario
def dryspell_scenario():

    total_rows = 24 * 14 # 14 day period
    times = pd.date_range(start="2026-07-01 00:00:00", periods=total_rows, freq="h")

    df = pd.DataFrame()
    moisture = 700

    for i in range(total_rows):
        hour = times[i].hour
        row = {}

        temp = generate_temperature_values(hour, 12, 24) 
        humidity = 80
        wind = 5
        rain = 0
        moisture = update_soil_moisture(moisture, rain, temp, wind)

        row = {
            "Time": times[i],
            "Temperature": round(temp, 2),
            "Soil_Moisture": round(moisture, 2),
            "Humidity": humidity,
            "Wind_Speed": wind,
            "Rainfall": rain
        }

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    return df