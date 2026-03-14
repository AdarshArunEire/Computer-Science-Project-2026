import pandas as pd 
import numpy as np
import datetime
from HelperFunctions import improved_input

# Generate temp values based on daylight cycle
def generate_temperature_values(hour, min_temp, max_temp):
    a = (min_temp + max_temp) / 2 # Midway line
    b = (max_temp - min_temp) / 2 # Amplitude
    c = (2 * np.pi) / 24          # Frequency (every 24h)
    x = hour - 15                 # Shift graph's peak to 3pm (hour 15)

    return a + b * np.cos(c * x) + np.random.normal(0, 1) # Add some noise

# Generate soil moisture values based on rainfall and drying factors
def update_soil_moisture(previous_moisture, rain, temp, wind):

    drying = 0.6 * temp + 0.4 * wind # Temp and wind are factors in drying
    rain_gain = rain * 300 # Rain increases soil moisture drastically
    new_moisture = previous_moisture + rain_gain - drying * 0.3

    return np.clip(new_moisture, 200, 800)

# 1. Generate a df of a dryspell scenario
def dryspell_scenario():

    # 1.a generate times column, initial soil mositure and empty df
    total_rows = 24 * 14 # 14 day period
    times = pd.date_range(start="2026-07-01 00:00:00", periods=total_rows, freq="h")

    df = pd.DataFrame()
    moisture = 700

    # 1.b generate values per row, with NO rainfall casuing soil to dry out, all other variables regular
    for i in range(total_rows):
        row = {}

        hour = times[i].hour
        temp = generate_temperature_values(hour, 12, 24) # 12°c-24°c is not extradonary
        humidity = 80
        wind = 5
        rain = 0 # no rain event
        moisture = update_soil_moisture(moisture, rain, temp, wind)

    # 1.c Build row, append to df
        row = {
            "Time": times[i],
            "Temperature": round(temp, 2),
            "Soil_Moisture": round(moisture, 2),
            "Humidity": humidity,
            "Wind_Speed": wind,
            "Rainfall": rain
        }

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    print(df)
    return df

# 2. Generate a df of an extreme hot/windy scenario
def extreme_scenario():

    # 2.a generate times column, initial soil mositure and empty df
    total_rows = 24 * 14  # 14 day period
    times = pd.date_range(start="2026-08-01 00:00:00", periods=total_rows, freq="h")
    df = pd.DataFrame()
    moisture = 500

    for i in range(total_rows):
        row = {}

        hour = times[i].hour
        temp = generate_temperature_values(hour, 23, 38)
        humidity = 50
        wind = 5
        rain = 0

        # Short rain event around day 6
        if 24 * 6 <= i < 24 * 6 + 3:
            rain = 2
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

# 3. Allow user to input their own variables and get a risk score back
def custom_scenario():

    # 3.a Time = time of request
    time = pd.Timestamp(datetime.datetime.now().replace(microsecond=0))
    row_count = 0
    df = pd.DataFrame()

    # 3.b Ask for values
    while True:
        print("\n##############################################################\n")
        print("Building row ", row_count + 1)
        current_time = time + pd.Timedelta(hours=row_count)
        print("Time:", current_time)

        temp = improved_input("Enter a temperature (°C): ", None, "float")
        humidity = improved_input("Enter a relative humidity value (0%-100%): ", None, "float")
        wind = improved_input("Enter a windspeed (km/h): ", None, "float") / 3.6
        rain = improved_input("Enter rainfall for the hour (mm, light rainfall is 1 mm over an hour): ", None, "float")
        moisture = improved_input("Enter a soil moisture value (200 is dry, 800 is wet, sensor range is 0-1023): ", None, "float")

        # 3.c Append row
        row = {
            "Time": current_time,
            "Temperature": round(temp, 2),
            "Soil_Moisture": round(moisture, 2),
            "Humidity": round(humidity, 2),
            "Wind_Speed": round(wind, 2),   # stored in m/s
            "Rainfall": round(rain, 2)
        }

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        row_count += 1

        # 3.d Ask user if they want another row
        if row_count < 6:
            print(f"Model uses previous rows to calculate carryover risk; only {row_count} row(s) entered so far is not ideal.")

        ans = improved_input("Do you want to add another row? (y/n): ", ["y", "n"], None)
        if ans == "n":
            return df