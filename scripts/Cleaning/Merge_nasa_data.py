import pandas as pd

# 1. Create base df with dates to act as link between datasets
df = pd.DataFrame({"Date": pd.date_range(start="2024-01-01", end="2025-12-31")})

# 2. Load cleaned datasets
smap_df = pd.read_csv("data/SMAP/SMAPDataCleaned.csv")
firms_df = pd.read_csv("data/FIRMS/FIRMSdataCleaned.csv")
power_df = pd.read_csv("data/POWER/POWERDataCleaned.csv")

# 3. convert date stringsto datetime objects
smap_df["Date"] = pd.to_datetime(smap_df["Date"])
firms_df["Date"] = pd.to_datetime(firms_df["Date"])
power_df["Date"] = pd.to_datetime(power_df["Date"])

# 4. Merge datasets on date
df = df.merge(firms_df, on="Date", how="left")
df = df.fillna(0) # No fires - no risk

'''
print("Fire Risk Class Proportion:")
print(df["fire_risk_class"].value_counts(normalize=True))
print("Fire Risk Class Distribution:")
print(df["fire_risk_class"].value_counts())
'''

df = df.merge(smap_df, on="Date", how="left")
df = df.merge(power_df, on="Date", how="left")

# 5. Drop rows with missing data
df = df.dropna().reset_index(drop=True)

# 6. Export merged data
df.to_csv("data/NASADataMerged.csv", index=False)
print("df exported to data/NASADataMerged.csv!")