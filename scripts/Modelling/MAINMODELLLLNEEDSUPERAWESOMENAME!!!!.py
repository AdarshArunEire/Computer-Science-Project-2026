import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

risk_floor = 0.000   # The minimum final risk score, used to rescale the final risk score to a percentage
risk_ceiling = 0.090 # The final risk score that corresponds to 100% risk, used to rescale the final risk score to a percentage

###############################################################################

# Bands for final risk
moderate_risk = 0.25 * risk_ceiling
high_risk = 0.5 * risk_ceiling
extreme_risk = 0.75 * risk_ceiling

###############################################################################

# Helper function to get valid inputs
def improved_input(prompt, list_ans, ans_type):
    
    while True:
        ans = input(prompt).lower()
        
        if ans_type is not None:
            if ans_type == "int":
                try:
                    ans = int(ans)
                except:
                    print("Please enter an integer")
                    continue
            elif ans_type == "float":
                try:
                    ans = float(ans)
                except:
                    print("Plese enter a number")
                    continue
                
        if list_ans is not None:
            if ans not in list_ans:
                print("Input not valid, try again")
                continue
        
        return ans

# Scales value given based on min and max, clipping from 0 to 1
def normalise(value, min_val, max_val):
    total_range = max_val - min_val
    value_dist = value - min_val
    return np.clip(value_dist / total_range, 0, 1) 

def model_risk(file_path):

    # 1. Load the dataset, intialise empty df
    data_df = pd.read_csv(file_path)
    df = pd.DataFrame(columns=
                    ["Time", "Heat", "DrySoil", "DryAir", "Wind", "RainRelief", # Enviromental variables
                    "InstantRisk", "DrynessInput", "CarryoverRisk",            # Sub Risk scores
                        "FinalRisk", "FinalRiskScore", "FinalRiskBand"])         # Final Risk

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
        df.loc[i, "FinalRisk"] = FinalRisk_t

        AdjustedRisk_t = max(0, FinalRisk_t - risk_floor) # Offset to allow normal weather to be low
        FinalRiskScore_t = AdjustedRisk_t / (risk_ceiling - risk_floor) * 100 # Rescale to percent
        df.loc[i, "FinalRiskScore"] = FinalRiskScore_t


        if FinalRiskScore_t >= extreme_risk:
            df.loc[i, "FinalRiskBand"] = "Extreme"
        elif FinalRiskScore_t >= high_risk:
            df.loc[i, "FinalRiskBand"] = "High"
        elif FinalRiskScore_t >= moderate_risk:
            df.loc[i, "FinalRiskBand"] = "Moderate"
        else:
            df.loc[i, "FinalRiskBand"] = "Low"

    # 4. Export the final dataset
    df.to_csv("data/MicrobitDataRiskModel.csv", index=False)
    print(f"Risk model complete, {len(df)} rows at {file_path}")
    return df


def visualise(df):

    print(df["FinalRisk"].describe())
    print(df["FinalRiskScore"].describe())

    # Set style
    sns.set_style("whitegrid")

    # Create figure and axes
    fig, axes = plt.subplots(3, 1, figsize=(12, 18))

    # Plot 1: Line plot of final risk score over time
    sns.lineplot(x="Time", y="FinalRiskScore", data=df, ax=axes[0], marker="o")
    axes[0].set_title("Final Risk Score Over Time")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Final Risk Score (%)")

    # Plot 2: Bar plot of count of each risk band
    sns.countplot(x="FinalRiskBand", data=df, order=["Low", "Moderate", "High", "Extreme"], ax=axes[1])
    axes[1].set_title("Count of Each Final Risk Band")
    axes[1].set_xlabel("Final Risk Band")
    axes[1].set_ylabel("Count")

    # Plot 3: Heatmap of correlation between variables
    corr = df[["Heat", "DrySoil", "DryAir", "Wind", "RainRelief", "InstantRisk", "DrynessInput", "CarryoverRisk", "FinalRisk"]].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=axes[2])
    axes[2].set_title("Correlation Heatmap")

    plt.tight_layout()
    plt.show()
    
    return


# 5. When file ran directly, run model and prompt for graphs
if __name__ == "__main__":
    while True:
        file_path = improved_input("Enter the filepath of the cleaned hourly data to model (use forward slashes),\n"
                        "or press Enter to use the default 'data/MicrobitDataHourlyClean.csv': ", None, "string")
        if file_path == "":
            file_path = "data/MicrobitDataHourlyClean.csv"
        try:
            df = model_risk(file_path)
            break
        except FileNotFoundError:
            print(f"File not found at {file_path}, please try again.")

    while True:
        graph_ans = improved_input("Would you like to see some graphs of the modelled data? (y/n): ", ["y", "n"], "string")
        if graph_ans == "y":
            visualise(df)
            break
        elif graph_ans == "n":
            print("Okay goodbye!")
            break

