import pandas as pd

# 1. Load raw POWER data
df = pd.read_csv("data/POWER/POWERDataUncleaned.csv")

df.columns = ["year", "month", "day", "Temperature", "Light"]

# 2. Merge date columns into a single datetime column
df["Date"] = pd.to_datetime(df[["year", "month", "day"]])

# 3. Keep needed columns
df = df[["Date", "Temperature", "Light"]]

# 4. Drop empty
df = df.dropna().reset_index(drop=True)

# 5. Export cleaned data
df.to_csv("data/POWER/POWERDataCleaned.csv", index=False)
print("df exported to data/POWER/POWERDataCleaned.csv!")