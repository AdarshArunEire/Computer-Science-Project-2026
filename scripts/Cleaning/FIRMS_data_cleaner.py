import pandas as pd

# 1. Load raw FIRMS data
df = pd.read_csv("data/FIRMS/FIRMSdataUncleaned.csv")

# 2. Drop all except acq_date
df = df[["acq_date"]]
df = df.rename(columns={"acq_date": "date_of_fire"})

# 3. Count rows with same date to get fire count per day
df = df.groupby("date_of_fire").size().reset_index(name="fire_count") # I ♥ vectorised code

# 4. Add classification column based on fire count
def classify_fire_count(count):
    if count == 0: # technically dont need but js in case
        return 0
    elif count <= 3:
        return 1
    elif count <= 15:
        return 2
    else:
        return 3
df["fire_risk_class"] = df["fire_count"].apply(classify_fire_count)

# 5. Export cleaned data
df.to_csv("data/FIRMS/FIRMSdataCleaned.csv", index=False)
print("df exported to data/FIRMS/FIRMSdataCleaned.csv!")