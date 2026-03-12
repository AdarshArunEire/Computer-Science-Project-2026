from FireModel import model_risk, get_risk_thresholds
from HelperFunctions import visualise, improved_input
from WhatIfGenerator import dryspell_scenario, extreme_scenario, custom_scenario

while True:
    # 1. Ask user if they want to model risk based on sensor data or what-if scenarios
    ans = improved_input(
        "\n################################################################\n"
        "\nChoose data to use to model risk off:\n[1] Sensor data\n[2] What-if scenarios\n[3] Exit\n(1/2/3): ",
        [1, 2, 3],
        "int"
    )

    # 2. Run AR1 model, using sensor data
    if ans == 1:
        print("Sensor data chosen")
        print("\n################################################################\n")

        # 2.a Get file path
        file_path = improved_input(
            "Enter the filepath of the cleaned hourly data to model (use forward slashes),\n"
            "or press enter to use default data/MicrobitDataHourlyClean.csv: ",
            None,
            "string"
        )
        if file_path == "":
            file_path = "data/MicrobitDataHourlyClean.csv"

        # 2.b Run model and export
        df = model_risk(file_path)
        export_path = "data/MicrobitDataRiskModel.csv"
        df.to_csv(export_path, index=False)
        print(f"CSV exported to {export_path}")

        # 2.c Visualise results
        print("\n################################################################\n")
        ans = improved_input("Do you want to visualise the results? (y/n): ", ["y", "n"], "string")
        if ans == "y":
            moderate_risk, high_risk, extreme_risk = get_risk_thresholds()
            visualise(df, moderate_risk, high_risk, extreme_risk)

    # 3. Run AR2 model, using what-if scenarios
    elif ans == 2:
        print("What-if scenarios chosen")
        print("\n################################################################\n")

        # 3.a Choose scenario to model
        ans = improved_input(
            "Choose scenario:\n"
            "[1] Scenario 1: Dry Spell\n"
            "[2] Scenario 2: Extreme Heat/Wind\n"
            "[3] Scenario 3: Custom\n"
            "(1/2/3): ",
            [1, 2, 3],
            "int"
        )

        if ans == 1:
            scenario_df = dryspell_scenario()
            export_path = "data/DrySpellRiskModel.csv"
            print("\n################################################################\n")
            print("Running preset: Dry-spell simulation")

        elif ans == 2:
            scenario_df = extreme_scenario()
            export_path = "data/ExtremeHeatWindRiskModel.csv"
            print("\n################################################################\n")
            print("Running preset: Extreme heat and wind simulation")

        elif ans == 3:
            scenario_df = custom_scenario()
            export_path = "data/CustomScenarioRiskModel.csv"
            print("\n################################################################\n")
            print("Running custom simulation")

        # 3.b Run model and export
        df = model_risk(scenario_df)
        df.to_csv(export_path, index=False)
        print(f"CSV exported to {export_path}")

        # 3.c Visualise results
        print("\n################################################################\n")
        ans = improved_input("Do you want to visualise the results? (y/n): ", ["y", "n"], "string")
        if ans == "y":
            moderate_risk, high_risk, extreme_risk = get_risk_thresholds()
            visualise(df, moderate_risk, high_risk, extreme_risk)

    else:
        print("Exiting program")
        break