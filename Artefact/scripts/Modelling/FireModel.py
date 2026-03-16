import pandas as pd
import numpy as np
from HelperFunctions import improved_input, normalise

###############################################################################

# Weights for the different factors
                 # How much:                            for instant risk:
w_heat = 0.40    #          current temperature matters 
w_soil = 0.10    #          dry soil matters right now
w_air = 0.20     #          dry air matters right now
w_wind = 0.20    #          wind matters right now
w_rain = 0.10    #          rain pulls current risk down

                 # How much:                built-up dryness over time:
d_soil = 0.50    #          dry soil drives
d_heat = 0.20    #          heat builds 
d_air = 0.10     #          dry air builds 
d_rain = 0.20    #          rain reduces 

m_memory = 0.75  # how much the last hour still matters
m_input = 0.25   # how much this hour feeds into carryover

f_instant = 0.65 # how much current conditions matter in the final risk
f_memory = 0.35  # how much built-up dryness matters in the final risk

risk_floor = 0.0125   # The minimum final risk score, used to rescale the final risk score to an index 0-20
risk_ceiling = 0.11 # The final risk score that corresponds to max risk, used to rescale the final risk score to an index 0-20

###############################################################################

# Bands for final wildfire risk index (out of 20)
moderate_risk = 5
high_risk = 10
extreme_risk = 15

###############################################################################

# For visualisation
def get_risk_thresholds():
    return moderate_risk, high_risk, extreme_risk


def dynamic_wildfire_risk_model(data_input):

# 1. Load the dataset adapting to either df or filepath input, intialise output df
    if isinstance(data_input, pd.DataFrame):
        data_df = data_input.copy()
    else:
        data_df = pd.read_csv(data_input)

    df = pd.DataFrame(columns=
                ["Time", "Heat", "DrySoil", "DryAir", "Wind", "RainRelief",             # Enviromental variables
                "InstantRisk", "DrynessInput", "CarryoverRisk",                         # Sub Risk scores
                    "CombinedRisk", "FinalWildfireRiskIndex", "FinalWildfireRiskBand"]) # Final Risk scores

    # 2. Iterate through each row of the DataFrame,
    for i in range(len(data_df)):
        row = data_df.iloc[i]

        # 2.a Extract the values from the row,
        time_value = row["Time"]
        temp_value = row["Temperature"]
        soil_value = row["Soil_Moisture"]
        humidity_value = row["Humidity"]
        wind_value = row["Wind_Speed"]
        rain_value = row["Rainfall"]

        #2.b Set normalised values and inverted values to get risk-relevent values scaled,
        Heat_t = normalise(temp_value, 10, 40)
        DrySoil_t = 1 - normalise(soil_value, 200, 800)
        DryAir_t = 1 - normalise(humidity_value, 0, 100)
        Wind_t = normalise(wind_value, 0, 20)
        RainRelief_t = normalise(rain_value, 0, 10)

        # 2.c Calculate the instant risk score for the current row,
        InstantRisk_t = ( w_heat * Heat_t 
                        + w_soil * DrySoil_t 
                        + w_air * DryAir_t 
                        + w_wind * Wind_t
                        - w_rain * RainRelief_t
                        )
        
        # 2.d Calculate the dryness input score for the current row
        DrynessInput_t = ( d_soil * DrySoil_t 
                        + d_heat * Heat_t 
                        + d_air * DryAir_t 
                        - d_rain * RainRelief_t
                        )
        
        # 2.e Append row into df
        df.loc[i] = [time_value, Heat_t, DrySoil_t, DryAir_t, Wind_t, RainRelief_t,
                    InstantRisk_t, DrynessInput_t, np.nan, np.nan, np.nan, ""]
        
    # 3. Iterate through each row again to calculate carryover risk and final risk,
    for i in range(len(df)):
        DrynessInput_t = df.loc[i, "DrynessInput"]
        InstantRisk_t = df.loc[i, "InstantRisk"]

        # 3a. If its the first row, just use dryness input
        if i == 0:
            CarryoverRisk_t = DrynessInput_t  # Base case

        # 3b. Otherwise, calculate carryover risk recursively
        else:
            CarryoverRisk_previous = df.loc[i-1, "CarryoverRisk"]
            CarryoverRisk_t = (m_memory * CarryoverRisk_previous) + (m_input * DrynessInput_t)
        df.loc[i, "CarryoverRisk"] = CarryoverRisk_t
            
        # 3c. Calculate final risks
        FinalRisk_t = (f_instant * InstantRisk_t) * (f_memory * CarryoverRisk_t) # * repersents AND, instead of + representing OR
        df.loc[i, "CombinedRisk"] = FinalRisk_t

        AdjustedRisk_t = max(0, FinalRisk_t - risk_floor) # Offset to allow normal weather to be low
        FinalRiskScore_t = AdjustedRisk_t / (risk_ceiling - risk_floor) * 20 # Rescale to index
        df.loc[i, "FinalWildfireRiskIndex"] = FinalRiskScore_t


        if FinalRiskScore_t >= extreme_risk:
            df.loc[i, "FinalWildfireRiskBand"] = "Extreme"
        elif FinalRiskScore_t >= high_risk:
            df.loc[i, "FinalWildfireRiskBand"] = "High"
        elif FinalRiskScore_t >= moderate_risk:
            df.loc[i, "FinalWildfireRiskBand"] = "Moderate"
        else:
            df.loc[i, "FinalWildfireRiskBand"] = "Low"

    # 4. Export the final dataset
    print(f"Risk model complete, {len(df)} rows")
    return df


# 5. When file ran directly, run model and prompt for graphs
if __name__ == "__main__":
    while True:
        file_path = improved_input("Enter the filepath of the cleaned hourly data to model (use forward slashes),\n"
                        "or press Enter to use the default 'data/MicrobitDataHourlyClean.csv': ", None, "string")
        if file_path == "":
            file_path = "data/MicrobitDataHourlyClean.csv"
        try:
            df = dynamic_wildfire_risk_model(file_path)
            df.to_csv("data/MicrobitDataRiskModel.csv", index=False)
            print("csv exported to path data/MicrobitDataRiskModel.csv")
            break
        except FileNotFoundError:
            print(f"File not found at {file_path}, please try again.")
        except KeyError:
            print("This data isnt hourly")
            

