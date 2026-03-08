import pandas as pd

# 1. Load raw SMAP data
df = pd.read_csv("data/SMAP/SMAPDataUncleaned.csv")

# 2. Keep ID, date, soil moisture and qual_flag + rename
df = df[
    [
    "Date", 
    "ID", 
    "SPL3SMP_009_Soil_Moisture_Retrieval_Data_AM_soil_moisture_dca", 
    "SPL3SMP_009_Soil_Moisture_Retrieval_Data_AM_retrieval_qual_flag_dca"
    ]]
df.columns = ["Date", "ID", "Soil_Moisture", "Qual_Flag"] # Ended up ignoring qual flag as many 

# print proportions of qual 0:7
#print("Proportions of qual flags:")
#print(df["Qual_Flag"].value_counts(normalize=True))

# 3. Drop rows with soil moisture value of -9999 (missing data)
df = df[df["Soil_Moisture"] != -9999]

# 4. Group based on date to combine 5 points per day
date_groups = df.groupby("Date", as_index=False)

# 5. Take mean of soil moisture values across 5 points each day
df = date_groups["Soil_Moisture"].mean().round(4)

# 6. Drop leftover Nan (if all days returned Nan)
df = df.dropna()

# 7. Convert date to datetime format
df["Date"] = pd.to_datetime(df["Date"])

# 8. Export cleaned data
df.to_csv("data/SMAP/SMAPDataCleaned.csv", index=False)
print("df exported to data/SMAP/SMAPDataCleaned.csv!")