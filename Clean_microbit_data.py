import pandas as pd
#print(raw_df.to_string())

def MicrobitDataCleaner(raw_df):
    # 2. Dropping duplicate rows and resetting index
    df = raw_df.drop_duplicates().reset_index(drop=True)
    df.columns = ["Time", "Temperature", "Light", "Soil_Moisture"]
    #print(df.to_string())

    # 3. Drop index column
    df = df.reset_index(drop=True)

    # 4. Replacing Rows where Temp greater than 100°c with NaN
    for i, temp in df["Temperature"].items():
        if temp > 100:
            df.loc[i, "Temperature"] = float("nan")
    #print(df.to_string())

    # 5. Replacing missing temperature values with an estimate value of the closest 2
    while df["Temperature"].isna().any() is True:
        for i, temp in df["Temperature"].items():
            if pd.isna(temp):
                if i == 0 or df["Temperature"].iloc[i - 1].isna():
                    next_val = df["Temperature"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["Temperature"]) - 1 or df["Temperature"].iloc[i + 1].isna():
                    prev_val = df["Temperature"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["Temperature"].iloc[i - 1]
                    next_val = df["Temperature"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "Temperature"] = (prev_val + next_val) / 2
    # print(df.to_string())

    # 6. Replacing Rows where Soil Moisture outside of analog range
    max_moisture = (3/3.3 * 1023) + 10 # max 3V from sensor of max 3.3V; which is mapped to 1023, +10 for error
    for i, moisture in df["Soil_Moisture"].items():
        if moisture > max_moisture:
            print(f"At index {i}, value of {moisture} is outside of typical range")
            df.loc[i, "Soil_Moisture"] = float("nan")
    #print(df.to_string())

    # 7. Replacing missing Moisture values with an estimate value of the closest 2
    while df["Soil_Moisture"].isna().any() is True:
        for i, temp in df["Soil_Moisture"].items():
            if pd.isna(temp):
                if i == 0 or df["Soil_Moisture"].iloc[i - 1].isna():
                    next_val = df["Soil_Moisture"].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df["Soil_Moisture"]) - 1 or df["Soil_Moisture"].iloc[i + 1].isna():
                    prev_val = df["Soil_Moisture"].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df["Soil_Moisture"].iloc[i - 1]
                    next_val = df["Soil_Moisture"].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, "Soil_Moisture"] = (prev_val + next_val) / 2
    #print(df.to_string())

    # 8. Return cleaned df for MAIN pipeline + Export Cleaned Data
    df = df.dropna().reset_index(drop=True)
    df.to_csv('MicrobitDataCleaned.csv', index=False)
    print("df exported to MicrobitDataCleaned.csv!")
    return df


# 9. If file ran directly, This code allows you to select a file to clean
if __name__ == "__main__":

    # 10. Ensure raw file exists and is not empty before cleaning
    while True:
        filepath = input("Enter the filename (excluding the .csv),\n"
                         "click enter to use the default (MicrobitDataUncleaned): ") + ".csv"
        if filepath == ".csv":
            filepath = "MicrobitDataUncleaned.csv"
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