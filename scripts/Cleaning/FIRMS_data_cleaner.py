import pandas as pd

# 1. Load raw FIRMS data
df = pd.read_csv("data/FIRMS/FIRMSdataUncleaned.csv")

# 2. Drop all except acq_date + rename + format
df = df[["acq_date"]]
df.columns = ["Date"]

# 3. Count rows with same date to get fire count per day
df = df.groupby("Date").size().reset_index(name="fire_count") # I ♥ vectorised code

# 4. Replace fire count with risk class
def classify_fire_count(count):
    if count == 0:
        return 0
    elif count == 1:
        return 1
    else:
        return 2
df["fire_count"] = df["fire_count"].apply(classify_fire_count)
df.columns = ["Date", "fire_risk_class"]

# 5. Export cleaned data
df.to_csv("data/FIRMS/FIRMSdataCleaned.csv", index=False)
print("df exported to data/FIRMS/FIRMSdataCleaned.csv!")