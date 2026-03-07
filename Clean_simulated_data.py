import pandas as pd

# Note to self ill drop Light cuz no reliable mapping to any forest fire dataset column

def replace_out_of_range(df, column, min_val, max_val):
    # Replacing values outside of valid range with NaN
    for i, val in df[column].items():
        if val < min_val or val > max_val:
            print(f"At index {i}, {column} value of {val} is outside of valid range ({min_val}-{max_val})")
            df.loc[i, column] = float("nan")
    return df

def fill_missing_with_average(df, column):
    # Replacing missing values with an estimate of the closest 2
    while df[column].isna().any() is True:
        for i, val in df[column].items():
            if pd.isna(val):
                if i == 0 or pd.isna(df[column].iloc[i - 1]):
                    next_val = df[column].iloc[i + 1]
                    prev_val = next_val
                elif i == len(df[column]) - 1 or pd.isna(df[column].iloc[i + 1]):
                    prev_val = df[column].iloc[i - 1]
                    next_val = prev_val
                else:
                    prev_val = df[column].iloc[i - 1]
                    next_val = df[column].iloc[i + 1]
                if not pd.isna(prev_val) and not pd.isna(next_val):
                    df.loc[i, column] = (prev_val + next_val) / 2
    return df

def ForestFireDataCleaner(raw_df):
    # 2. Dropping duplicate rows and resetting index
    df = raw_df.drop_duplicates().reset_index(drop=True)
    #print(df.to_string())

    # 3. Dropping irrelevant columns: X, Y, month, day, DMC, DC, area
    # month/day dropped - temporal data not relevant to risk prediction
    # DMC/DC dropped - long term indices, redundant given FFMC and ISI focus
    # area dropped - outcome variable, not a risk indicator
    df = df.drop(columns=["X", "Y", "month", "day", "DMC", "DC", "area"])
    #print(df.to_string())

    # 4. Valid ranges for each column: (column, min, max)
    column_ranges = [
        ("FFMC", 0, 101),    # FFMC valid range by definition
        ("ISI",  0, 50),     # ISI typical range, rarely exceeds 50
        ("temp", -20, 60),   # temp typical range in celsius
        ("RH",   0, 100),    # RH valid range as a percentage
        ("wind", 0, 100),    # wind typical range in km/h
        ("rain", 0, 300),    # rain typical range in mm
    ]

    # 5. Replacing out of range values with NaN, then filling with average, per column
    for column, min_val, max_val in column_ranges:
        df = replace_out_of_range(df, column, min_val, max_val)
        df = fill_missing_with_average(df, column)
        #print(df.to_string())

    # 16. Export cleaned data and return df
    df = df.dropna().reset_index(drop=True)
    df.to_csv("Simulated_forestfires_clean_data.csv", index=False)
    print("df exported to simulated_forestfires_cleaned.csv!")
    return df

# 17. If file ran directly, clean the simulated forest fire dataset
if __name__ == "__main__":

    # 18. Ensure raw file exists and is not empty before cleaning
    while True:
        filepath = input("Enter the filename (excluding the .csv),\n"
                         "click enter to use the default (Simulated_forestfires_raw_data): ") + ".csv"
        if filepath == ".csv":
            filepath = "Simulated_forestfires_raw_data.csv"
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