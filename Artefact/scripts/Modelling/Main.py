from FireModel import dynamic_wildfire_risk_model, get_risk_thresholds
from HelperFunctions import visualise, improved_input
from WhatIfGenerator import dryspell_scenario, extreme_scenario, custom_scenario
from AdaptiveRiskTracker import adaptive_risk_tracker
import pandas as pd


while True:
    # 1. Ask user what they want to run
    ans = improved_input(
        "\n################################################################\n"
        "\nChoose what part of the project to run:\n"
        "[1] AR1 - Model wildfire risk using sensor data\n"
        "[2] AR2 - Run what-if scenarios\n"
        "[3] AR3 - Adaptive risk tracking\n"
        "[4] Exit\n"
        "(1/2/3/4): ",
        [1, 2, 3, 4],
        "int"
    )

    # 2. Run AR1 model, using sensor data
    if ans == 1:
        print("AR1 chosen: Sensor data wildfire risk modelling")
        print("\n################################################################\n")

        # 2.a Get file path
        file_path = improved_input(
            "Enter the filepath of the cleaned hourly data to model (use forward slashes),\n"
            "or press enter to use default Artefact/data/MicrobitDataHourlyClean.csv: ",
            None,
            "string"
        )
        if file_path == "":
            file_path = "Artefact/data/MicrobitDataHourlyClean.csv"

        # 2.b Run model and export
        df = dynamic_wildfire_risk_model(file_path)
        export_path = "Artefact/data/MicrobitDataRiskModel.csv"
        df.to_csv(export_path, index=False)
        print(f"CSV exported to {export_path}")

        # 2.c Visualise results
        print("\n################################################################\n")
        ans2 = improved_input(
            "Do you want to visualise the results? (y/n): ",
            ["y", "n"],
            "string"
        )
        if ans2 == "y":
            moderate_risk, high_risk, extreme_risk = get_risk_thresholds()
            visualise(df, moderate_risk, high_risk, extreme_risk)

        # 2.d Run AR3 adaptive tracking on the same output
        print("\n################################################################\n")
        ans3 = improved_input(
            "Do you want to run adaptive risk tracking as well? (AR3) (y/n): ",
            ["y", "n"],
            "string"
        )
        if ans3 == "y":
            adaptive_df = adaptive_risk_tracker(df)
            adaptive_export_path = "Artefact/data/AdaptiveRiskTracking.csv"
            adaptive_df.to_csv(adaptive_export_path, index=False)
            print(f"CSV exported to {adaptive_export_path}")

    # 3. Run AR2 model, using what-if scenarios
    elif ans == 2:
        print("AR2 chosen: What-if scenarios")
        print("\n################################################################\n")

        # 3.a Choose scenario to model
        ans2 = improved_input(
            "Choose scenario:\n"
            "[1] Scenario 1: Dry Spell\n"
            "[2] Scenario 2: Extreme Heat/Wind\n"
            "[3] Scenario 3: Custom\n"
            "(1/2/3): ",
            [1, 2, 3],
            "int"
        )

        if ans2 == 1:
            scenario_df = dryspell_scenario()
            export_path = "Artefact/data/DrySpellRiskModel.csv"
            print("\n################################################################\n")
            print("Running preset: Dry-spell simulation")

        elif ans2 == 2:
            scenario_df = extreme_scenario()
            export_path = "Artefact/data/ExtremeHeatWindRiskModel.csv"
            print("\n################################################################\n")
            print("Running preset: Extreme heat and wind simulation")

        elif ans2 == 3:
            scenario_df = custom_scenario()
            export_path = "Artefact/data/CustomScenarioRiskModel.csv"
            print("\n################################################################\n")
            print("Running custom simulation")

        # 3.b Run model and export
        df = dynamic_wildfire_risk_model(scenario_df)
        df.to_csv(export_path, index=False)
        print(f"CSV exported to {export_path}")

        # 3.c Visualise results
        print("\n################################################################\n")
        ans3 = improved_input(
            "Do you want to visualise the results? (y/n): ",
            ["y", "n"],
            "string"
        )
        if ans3 == "y":
            moderate_risk, high_risk, extreme_risk = get_risk_thresholds()
            visualise(df, moderate_risk, high_risk, extreme_risk)

        # 3.d Run AR3 adaptive tracking on the same output
        print("\n################################################################\n")
        ans4 = improved_input(
            "Do you want to run adaptive risk tracking as well? (AR3) (y/n): ",
            ["y", "n"],
            "string"
        )
        if ans4 == "y":
            adaptive_df = adaptive_risk_tracker(df)

            if ans2 == 1:
                adaptive_export_path = "Artefact/data/DrySpellAdaptiveTracking.csv"
            elif ans2 == 2:
                adaptive_export_path = "Artefact/data/ExtremeHeatWindAdaptiveTracking.csv"
            else:
                adaptive_export_path = "Artefact/data/CustomScenarioAdaptiveTracking.csv"

            adaptive_df.to_csv(adaptive_export_path, index=False)
            print(f"CSV exported to {adaptive_export_path}")

    # 4. Run AR3 directly from chosen cleaned hourly data
    elif ans == 3:
        print("AR3 chosen: Adaptive risk tracking")
        print("\n################################################################\n")

        # 4.a Get file path
        file_path = improved_input(
            "Enter the filepath of the cleaned hourly data to track adaptively (use forward slashes),\n"
            "or press enter to use default Artefact/data/MicrobitDataHourlyClean.csv: ",
            None,
            "string"
        )
        if file_path == "":
            file_path = "Artefact/data/MicrobitDataHourlyClean.csv"

        if "RiskModel" not in file_path:
            # 4.b Run model first, because AR3 depends on wildfire risk output
            model_df = dynamic_wildfire_risk_model(file_path)
            model_df.to_csv("Artefact/data/AR3DataRiskModel.csv", index=False)
            print("CSV exported to Artefact/data/AR3DataRiskModel.csv")
        else:
            model_df = pd.read_csv(file_path)

        # 4.c Then run adaptive tracking
        adaptive_df = adaptive_risk_tracker(model_df)
        adaptive_df.to_csv("Artefact/data/AdaptiveRiskTracking.csv", index=False)
        print("CSV exported to Artefact/data/AdaptiveRiskTracking.csv")

    else:
        print("\n################################################################\n")
        print("Exiting program\n")
        break