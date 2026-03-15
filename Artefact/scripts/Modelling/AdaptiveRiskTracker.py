import pandas as pd
from FireModel import dynamic_wildfire_risk_model
from HelperFunctions import improved_input
from time import sleep

###############################################################################

# Thresholds for adaptive risk tracking
change_threshold = 0.05  # Minimum change in risk score to count as increased/decreased
trend_window = 3         # Number of previous rows used to judge short trend direction
trend_threshold = 0.05   # Minimum difference from recent average to count as rising/falling

# Speed of ouput
duration = 5 # Seconds to complete program

###############################################################################


def adaptive_risk_tracker(risk_input):

# 1. Load the dataset adapting to either df or filepath input, intialise output df
    if isinstance(risk_input, pd.DataFrame):
        data_df = risk_input.copy()
    else:
        data_df = pd.read_csv(risk_input)

    df = data_df.copy()
    wait_time = duration / df.shape[0]
    

    # 1.a Make sure risk score is numeric
    df["FinalWildfireRiskIndex"] = pd.to_numeric(df["FinalWildfireRiskIndex"], errors="coerce")

    # 1.b Add adaptive tracking columns
    df["PreviousRiskIndex"] = pd.NA
    df["PreviousRiskBand"] = ""
    df["RiskChangeValue"] = pd.NA
    df["RiskChange"] = ""
    df["BandChange"] = ""
    df["Trend"] = ""

    # 2. Iterate through each row of the DataFrame,
    for i in range(len(df)):
        sleep(wait_time)
        row = df.iloc[i]

        # 2.a Extract the values from the row,
        time_value = row["Time"]
        current_risk = row["FinalWildfireRiskIndex"]
        current_band = row["FinalWildfireRiskBand"]

        # 2.b If its the first row, there is no previous row to compare against
        if i == 0:
            df.loc[i, "RiskChange"] = "No previous row yet"
            df.loc[i, "BandChange"] = f"Starting at {current_band}"
            df.loc[i, "Trend"] = "Building trend"

            print(f"{time_value} | No previous row yet | Starting at {current_band} | Trend: Building trend")

        # 2.c Otherwise, compare to the previous row
        else:
            previous_risk = df.loc[i - 1, "FinalWildfireRiskIndex"]
            previous_band = df.loc[i - 1, "FinalWildfireRiskBand"]
            risk_change_value = current_risk - previous_risk

            df.loc[i, "PreviousRiskIndex"] = previous_risk
            df.loc[i, "PreviousRiskBand"] = previous_band
            df.loc[i, "RiskChangeValue"] = risk_change_value

            # 2.d Work out whether risk increased, decreased, or stayed the same
            if risk_change_value > change_threshold:
                risk_change = "Risk increased"
            elif risk_change_value < -change_threshold:
                risk_change = "Risk decreased"
            else:
                risk_change = "Risk stayed the same"

            # 2.e Work out whether the risk band changed
            if current_band != previous_band:
                band_change = f"Band changed from {previous_band} to {current_band}"

            else:
                band_change = f"Band stayed at {current_band}"

            # 2.f Work out short trend direction from recent rows
            if i < trend_window:
                trend = "Building trend"
            else:
                recent_avg = df.loc[i - trend_window:i - 1, "FinalWildfireRiskIndex"].mean() # Spliced window of last {trend_window} row's mean

                if current_risk > recent_avg + trend_threshold:
                    trend = "Rising"
                elif current_risk < recent_avg - trend_threshold:
                    trend = "Falling"
                else:
                    trend = "Stable"

            df.loc[i, "RiskChange"] = risk_change
            df.loc[i, "BandChange"] = band_change
            df.loc[i, "Trend"] = trend

            if "changed" in band_change:
                print("#####################################################################################\n")
                print(
                    f"{time_value} | {risk_change} by {risk_change_value:.2f} | {band_change} | Trend: {trend}"
                )
                if "Extreme" in band_change:
                    print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
                    print("ALERT: WILDFIRE RISK IS BECOMING EXTREME; ALERT RELEVANT AUTHORITIES")
                    print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print("\n#####################################################################################")
                sleep(1)
            else:
                print(
                    f"{time_value} | {risk_change} by {risk_change_value:.2f} | {band_change} | Trend: {trend}"
                )


    # 3. Summerise, Export the final dataset
    print("\n#####################################################################################\n")
    print(f"Adaptive risk tracking complete, {len(df)} rows")
    band_changes = df[df["BandChange"].str.contains("changed", na=False)]
    print(f"Band changes detected: {len(band_changes)}")
    return df


# 4. When file ran directly, either load a RiskModel file or first run the wildfire model
if __name__ == "__main__":
    while True:
        file_path = improved_input(
            "Enter the filepath of the cleaned hourly data or risk model data to track adaptively (use forward slashes),\n"
            "or press Enter to use the default 'Artefact/data/MicrobitDataHourlyClean.csv': ",
            None,
            "string"
        )
        if file_path == "":
            file_path = "Artefact/data/MicrobitDataHourlyClean.csv"

        try:
            # 4.a If the file is not already a risk model output, run the wildfire model first
            if "RiskModel" not in file_path:
                model_df = dynamic_wildfire_risk_model(file_path)
                model_export_path = "Artefact/data/AR3DataRiskModel.csv"
                model_df.to_csv(model_export_path, index=False)
                print(f"CSV exported to {model_export_path}")

            # 4.b Otherwise load the already modelled risk data directly
            else:
                model_df = pd.read_csv(file_path)

            # 4.c Then run adaptive tracking
            df = adaptive_risk_tracker(model_df)
            adaptive_export_path = "Artefact/data/AdaptiveRiskTracking.csv"
            df.to_csv(adaptive_export_path, index=False)
            print(f"CSV exported to {adaptive_export_path}")
            break

        except FileNotFoundError:
            print(f"File not found at {file_path}, please try again.")
        except KeyError:
            print("This data isnt in the expected model format")