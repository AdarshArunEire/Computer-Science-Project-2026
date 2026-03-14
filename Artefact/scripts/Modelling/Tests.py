import numpy as np
import HelperFunctions
import WhatIfGenerator
import FireModel

##########################################################################################
# TEST 1 — STANDARD CASE
# Overall Purpose: To test the 'normalise()' function in HelperFunctions,
# which is responsible for scaling values from 0 to 1.
# Code Tested: normalise(25, 10, 40) — checks if the function correctly scales
# 25 within the range 10 to 40 and returns 0.5.
# Why this matters: the model depends on normalised values before combining them,
# so if this scaling is wrong then every later risk score will also be wrong.
##########################################################################################
print("TEST 1 — STANDARD CASE")

expected_value = 0.5   # Calculated Pen and Paper: (25 - 10) / (40 - 10) = 15 / 30 = 0.5
actual_value = HelperFunctions.normalise(25, 10, 40)

# We want this to pass because the model needs correctly scaled values
# before it can compare heat, soil, humidity, wind, and rain fairly.
if round(expected_value, 6) == round(actual_value, 6):
    print("Result: PASS")
else:
    print("Result: FAIL")

print("Expected calculated using Pen and Paper:", expected_value)
print("Actual calculated using Function .normalise():", actual_value)

##########################################################################################
# TEST 2 — STANDARD AND BOUNDARY CASE
# Overall Purpose: To test the 'update_soil_moisture()' function in WhatIfGenerator,
# which updates soil moisture based on rainfall and drying factors.
# Code Tested: One standard case with no rain, and one boundary case where rainfall
# is high enough to push the result above the maximum allowed value.
# Why this matters: the what-if scenarios rely on soil moisture being updated realistically,
# so this needs to work both in normal conditions and at the limits.
##########################################################################################
print("\nTEST 2 — STANDARD AND BOUNDARY CASE")

# Test 2.1: Standard case
expected_moisture = 695.8  # Pen and Paper: 700 + (0 * 300) - ((0.6*20 + 0.4*5) * 0.3)
actual_moisture = WhatIfGenerator.update_soil_moisture(700, 0, 20, 5)

# We want this to pass because the scenario generator needs to reduce soil moisture
# properly over time if it is going to simulate drying conditions correctly.
if round(expected_moisture, 1) == round(actual_moisture, 1):
    print("Result: PASS")
else:
    print("Result: FAIL")

print("Expected calculated using Pen and Paper:", expected_moisture)
print("Actual calculated using Function .update_soil_moisture():", round(actual_moisture, 1))
print()

# Test 2.2: Boundary case - should clip to 800
expected_boundary = 800.0
actual_boundary = WhatIfGenerator.update_soil_moisture(790, 2, 10, 0)

# We want this to pass because the model should not allow impossible soil moisture values.
# Boundary testing checks that the function stays inside realistic limits.
if expected_boundary == actual_boundary:
    print("Result: PASS")
else:
    print("Result: FAIL")

print("Expected:", expected_boundary)
print("Actual:", actual_boundary)

##########################################################################################
# TEST 3 — INTEGRATION TEST
# Overall Purpose: To test that the 'extreme_scenario()' generator and the
# 'dynamic_wildfire_risk_model()' function work together correctly.
# Code Tested: extreme_scenario() creates a 14 day hourly dataset, then
# dynamic_wildfire_risk_model() processes it and returns a wildfire risk output
# with the same number of rows.
# Why this matters: even if each function works on its own, the full project still needs
# the scenario data to pass cleanly into the wildfire model and produce valid outputs.
##########################################################################################
print("\nTEST 3 — INTEGRATION TEST")

np.random.seed(42)
scenario_df = WhatIfGenerator.extreme_scenario()
model_df = FireModel.dynamic_wildfire_risk_model(scenario_df)

expected_rows = 336
actual_rows = len(model_df)

# We want this to pass because the model should process every hourly row created
# by the scenario generator, without losing or skipping data.
if expected_rows == actual_rows:
    print("Result 1: PASS")
else:
    print("Result 1: FAIL")

print("Expected number of rows:", expected_rows)
print("Actual number of rows:", actual_rows)
print()

expected_no_nan = True
actual_no_nan = not model_df.isna().any().any()

# We want this to pass because the final model output should be complete.
# If NaN values remain, then some part of the risk calculation was not filled properly.
if expected_no_nan == actual_no_nan:
    print("Result 2: PASS")
else:
    print("Result 2: FAIL")

print("Expected: No NaN values in model output")
print("Actual:", actual_no_nan)

if not actual_no_nan:
    print("NaN count by column:")
    print(model_df.isna().sum())
print()

expected_high_or_extreme = True
actual_high_or_extreme = (
    (model_df["FinalWildfireRiskBand"] == "High") |
    (model_df["FinalWildfireRiskBand"] == "Extreme")
).any()

# We want this to pass because an extreme scenario should actually push the model
# into higher danger bands. If it never reaches High or Extreme, the scenario or model
# may not be reacting strongly enough.
if expected_high_or_extreme == actual_high_or_extreme:
    print("Result 3: PASS")
else:
    print("Result 3: FAIL")

print("Expected: At least one High or Extreme risk row")
print("Actual:", actual_high_or_extreme, "! ",
      (model_df["FinalWildfireRiskBand"] == "High").sum(), "High risk rows and",
      (model_df["FinalWildfireRiskBand"] == "Extreme").sum(), "Extreme risk rows")