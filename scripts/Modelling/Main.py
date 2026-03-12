from FireModel import model_risk, get_risk_thresholds
from HelperFunctions import visualise, improved_input
from WhatIfGenerator import dryspell_scenario#, extreme_scenario, custom_scenario

while True:
    # 1. Ask user if they want to model risk based on sensor data or what-if scenarios
    ans = improved_input("Model risk based on:\n[1] sensor data. \n[2] what if scenarios.\n[3] Exit\n(1/2/3): ", [1, 2, 3], "int")

    # 2 Run AR1 model, using sensor data
    if ans == 1:

        # 2.a Get file path 
        file_path = improved_input("Enter the filepath of the cleaned hourly data to model (use forward slashes),\n"
                                    "or press enter to use default data/MicrobitDataHourlyClean.csv: ", None, "string")
        if file_path == "":
            file_path = "data/MicrobitDataHourlyClean.csv"

        #2.b Run model
        df = model_risk(file_path)

        # 2.b Visualise results
        ans = improved_input("Do you want to visualise the results? (y/n): ", ["y", "n"], "string")
        if ans == "y":
            moderate_risk, high_risk, extreme_risk = get_risk_thresholds()
            visualise(df, moderate_risk, high_risk, extreme_risk)

    # 3. Run AR2 model, using what-if scenarios
    elif ans == 2:

        # 3.a Choose scenario to model
        ans = improved_input("Choose scenario:\n[1] Scenario 1: Dry Spell\n[2] Scenario 2\n[3] Scenario 3\n(1/2/3): ", [1, 2, 3], "int")
        if ans == 1:
            df = dryspell_scenario()
        elif ans == 2:
            df = "no" #extreme_scenario()
        elif ans == 3:
            df = "no" #custom_scenario()

        #3.b Run model
        df = model_risk(df) 

        # 3.c Visualise results
        ans = improved_input("Do you want to visualise the results? (y/n): ", ["y", "n"], "string")
        if ans == "y":
            moderate_risk, high_risk, extreme_risk = get_risk_thresholds()
            visualise(df, moderate_risk, high_risk, extreme_risk)
        
    else:
        print("Exiting program")
        break