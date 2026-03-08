import pandas as pd

# 1. Note to self ill drop Light cuz no reliable mapping to any forest fire dataset column

def ForestFireDataCleaner(raw_df):
    # 2. Dropping duplicate rows and resetting index
    df = raw_df.drop_duplicates().reset_index(drop=True)
    #print(df.to_string())

    # 3. Dropping irrelevant columns: X, Y, month, day, DMC, DC, area
    df = df.drop(columns=["X", "Y", "month", "day", "DMC", "DC", "area"])
    #print(df.to_string())

    # 4. Replacing FFMC values outside of valid range (0-101) with NaN
    for i, ffmc in df["FFMC"].items():
        if ffmc < 0 or ffmc > 101:
            print(f"At index {i}, FFMC value of {ffmc} is outside of valid range (0-101)")
            df.loc[i, "FFMC"] = float("nan")
    #print(df.to_string())

    # 5. Replacing missing FFMC values with an estimate of the closest 2
    while df["FFMC"].isna().any() is True:
        for i, ffmc in df["FFMC"].items():
            if pd.isna(ffmc):
                if i == 0 or pd.isna(df["FFMC"].iloc[i - 1]):
                    next_val = df["FFMC"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["FFMC"]) - 1 or pd.isna(df["FFMC"].iloc[i + 1]):
                    prev_val = df["FFMC"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["FFMC"].iloc[i - 1]
                    next_val = df["FFMC"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "FFMC"] = (prev_val + next_val) / 2
    #print(df.to_string())

    # 6. Replacing ISI values outside of typical range (0-50) with NaN
    for i, isi in df["ISI"].items():
        if isi < 0 or isi > 50:
            print(f"At index {i}, ISI value of {isi} is outside of typical range (0-50)")
            df.loc[i, "ISI"] = float("nan")
    #print(df.to_string())

    # 7. Replacing missing ISI values with an estimate of the closest 2
    while df["ISI"].isna().any() is True:
        for i, isi in df["ISI"].items():
            if pd.isna(isi):
                if i == 0 or pd.isna(df["ISI"].iloc[i - 1]):
                    next_val = df["ISI"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["ISI"]) - 1 or pd.isna(df["ISI"].iloc[i + 1]):
                    prev_val = df["ISI"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["ISI"].iloc[i - 1]
                    next_val = df["ISI"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "ISI"] = (prev_val + next_val) / 2
    #print(df.to_string())

    # 8. Replacing temp values outside of typical range (-20 to 60°c) with NaN
    for i, temp in df["temp"].items():
        if temp < -20 or temp > 60:
            print(f"At index {i}, temp value of {temp} is outside of typical range (-20 to 60)")
            df.loc[i, "temp"] = float("nan")
    #print(df.to_string())

    # 9. Replacing missing temp values with an estimate of the closest 2
    while df["temp"].isna().any() is True:
        for i, temp in df["temp"].items():
            if pd.isna(temp):
                if i == 0 or pd.isna(df["temp"].iloc[i - 1]):
                    next_val = df["temp"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["temp"]) - 1 or pd.isna(df["temp"].iloc[i + 1]):
                    prev_val = df["temp"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["temp"].iloc[i - 1]
                    next_val = df["temp"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "temp"] = (prev_val + next_val) / 2
    #print(df.to_string())

    # 10. Replacing RH values outside of valid range (0-100%) with NaN
    for i, rh in df["RH"].items():
        if rh < 0 or rh > 100:
            print(f"At index {i}, RH value of {rh} is outside of valid range (0-100)")
            df.loc[i, "RH"] = float("nan")
    #print(df.to_string())

    # 11. Replacing missing RH values with an estimate of the closest 2
    while df["RH"].isna().any() is True:
        for i, rh in df["RH"].items():
            if pd.isna(rh):
                if i == 0 or pd.isna(df["RH"].iloc[i - 1]):
                    next_val = df["RH"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["RH"]) - 1 or pd.isna(df["RH"].iloc[i + 1]):
                    prev_val = df["RH"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["RH"].iloc[i - 1]
                    next_val = df["RH"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "RH"] = (prev_val + next_val) / 2
    #print(df.to_string())

    # 12. Replacing wind values outside of typical range (0-100 km/h) with NaN
    for i, wind in df["wind"].items():
        if wind < 0 or wind > 100:
            print(f"At index {i}, wind value of {wind} is outside of typical range (0-100)")
            df.loc[i, "wind"] = float("nan")
    #print(df.to_string())

    # 13. Replacing missing wind values with an estimate of the closest 2
    while df["wind"].isna().any() is True:
        for i, wind in df["wind"].items():
            if pd.isna(wind):
                if i == 0 or pd.isna(df["wind"].iloc[i - 1]):
                    next_val = df["wind"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["wind"]) - 1 or pd.isna(df["wind"].iloc[i + 1]):
                    prev_val = df["wind"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["wind"].iloc[i - 1]
                    next_val = df["wind"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "wind"] = (prev_val + next_val) / 2
    #print(df.to_string())

    # 14. Replacing rain values outside of typical range (0-300 mm) with NaN
    for i, rain in df["rain"].items():
        if rain < 0 or rain > 300:
            print(f"At index {i}, rain value of {rain} is outside of typical range (0-300)")
            df.loc[i, "rain"] = float("nan")
    #print(df.to_string())

    # 15. Replacing missing rain values with an estimate of the closest 2
    while df["rain"].isna().any() is True:
        for i, rain in df["rain"].items():
            if pd.isna(rain):
                if i == 0 or pd.isna(df["rain"].iloc[i - 1]):
                    next_val = df["rain"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["rain"]) - 1 or pd.isna(df["rain"].iloc[i + 1]):
                    prev_val = df["rain"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["rain"].iloc[i - 1]
                    next_val = df["rain"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "rain"] = (prev_val + next_val) / 2
    #print(df.to_string())

    # 16. Export cleaned data and return df
    df = df.dropna().reset_index(drop=True)
    df.to_csv("data\UCIForestFires\Simulated_forestfires_clean_data.csv", index=False)
    print("df exported to data\UCIForestFires\Simulated_forestfires_clean_data.csv!")
    return df

# 17. If file ran directly, allow user to pick a file
if __name__ == "__main__":

    # 18. Ensure raw file exists and is not empty before cleaning
    while True:
        filepath = input("Enter the filename (use forward slashes),\n"
                         "click enter to use the default (data/UCIForestFires/Simulated_forestfires_raw_data.csv): ")
        if filepath == "":
            filepath = "data/UCIForestFires/Simulated_forestfires_raw_data.csv"
        try:
            uncleaned_df = pd.read_csv(filepath)
            if uncleaned_df.empty:
                raise ValueError("No valid data")
        except FileNotFoundError:
            print("File Not Found; Check the path?")
        except ValueError:
            print("This file is empty")
        else:
            df = ForestFireDataCleaner(uncleaned_df)
            break