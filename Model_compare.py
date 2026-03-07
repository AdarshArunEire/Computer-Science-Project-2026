import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, root_mean_squared_error
from sklearn.preprocessing import StandardScaler

# 1. Load cleaned forest fire data
df = pd.read_csv("Simulated_forestfires_clean_data.csv")

rows_before = len(df)
df = df.dropna().reset_index(drop=True)
rows_after = len(df)
if rows_before != rows_after:
    print(f"Dropped {rows_before - rows_after} rows with NaN values after loading")

# 2. Define features and targets
# Features: temp and rain - what the Microbit collects (light dropped, RH/wind out of scope)
# Targets: FFMC (ignition risk) and ISI (spread risk)
X = df[["temp", "rain"]]
y_ffmc = df["FFMC"]
y_isi = df["ISI"]

# 3. Split data into training and testing sets (80/20 split)
X_train, X_test, y_ffmc_train, y_ffmc_test = train_test_split(X, y_ffmc, test_size=0.2, random_state=42)
X_train, X_test, y_isi_train,  y_isi_test  = train_test_split(X, y_isi,  test_size=0.2, random_state=42)

# 4. Scale features - required for SVR and KNN to perform correctly
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# 5. Define the 4 models to compare
models = {
    "Linear Regression" : LinearRegression(),
    "Random Forest"     : RandomForestRegressor(random_state=42),
    "KNN"               : KNeighborsRegressor(),
    "SVR"               : SVR(),
}

# 6. Train each model and store predictions and scores for FFMC and ISI
ffmc_results = {}
isi_results  = {}

for name, model in models.items():
    # 7. Linear Regression does not benefit from scaling, others do
    if name == "Linear Regression":
        model.fit(X_train, y_ffmc_train)
        ffmc_pred = model.predict(X_test)
        model.fit(X_train, y_isi_train)
        isi_pred  = model.predict(X_test)
    else:
        model.fit(X_train_scaled, y_ffmc_train)
        ffmc_pred = model.predict(X_test_scaled)
        model.fit(X_train_scaled, y_isi_train)
        isi_pred  = model.predict(X_test_scaled)

    # 8. Store R2, RMSE, actual and predicted values for charting
    ffmc_results[name] = {
        "r2"        : r2_score(y_ffmc_test, ffmc_pred),
        "rmse"      : root_mean_squared_error(y_ffmc_test, ffmc_pred),
        "actual"    : y_ffmc_test,
        "predicted" : ffmc_pred,
        "residuals" : y_ffmc_test - ffmc_pred,
    }
    isi_results[name] = {
        "r2"        : r2_score(y_isi_test, isi_pred),
        "rmse"      : root_mean_squared_error(y_isi_test, isi_pred),
        "actual"    : y_isi_test,
        "predicted" : isi_pred,
        "residuals" : y_isi_test - isi_pred,
    }

# 9. Chart 1 - R2 score comparison (how well each model explains the data)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("R² Score Comparison (higher is better)")

ax1.bar(ffmc_results.keys(), [v["r2"] for v in ffmc_results.values()])
ax1.set_title("FFMC - Ignition Risk")
ax1.set_ylabel("R² Score")
ax1.set_ylim(0, 1)

ax2.bar(isi_results.keys(), [v["r2"] for v in isi_results.values()])
ax2.set_title("ISI - Spread Risk")
ax2.set_ylabel("R² Score")
ax2.set_ylim(0, 1)

plt.tight_layout()
plt.show()

# 10. Chart 2 - RMSE comparison (average prediction error, lower is better)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("RMSE Comparison (lower is better)")

ax1.bar(ffmc_results.keys(), [v["rmse"] for v in ffmc_results.values()])
ax1.set_title("FFMC - Ignition Risk")
ax1.set_ylabel("RMSE")

ax2.bar(isi_results.keys(), [v["rmse"] for v in isi_results.values()])
ax2.set_title("ISI - Spread Risk")
ax2.set_ylabel("RMSE")

plt.tight_layout()
plt.show()

# 11. Chart 3 - Actual vs Predicted scatter plot (perfect model = diagonal line)
fig, axes = plt.subplots(2, 4, figsize=(18, 10))
fig.suptitle("Actual vs Predicted (perfect model = diagonal line)")

for col, (name, vals) in enumerate(ffmc_results.items()):
    axes[0, col].scatter(vals["actual"], vals["predicted"])
    axes[0, col].plot([y_ffmc_test.min(), y_ffmc_test.max()],
                      [y_ffmc_test.min(), y_ffmc_test.max()], "r--")
    axes[0, col].set_title(f"FFMC - {name}")
    axes[0, col].set_xlabel("Actual")
    axes[0, col].set_ylabel("Predicted")

for col, (name, vals) in enumerate(isi_results.items()):
    axes[1, col].scatter(vals["actual"], vals["predicted"])
    axes[1, col].plot([y_isi_test.min(), y_isi_test.max()],
                      [y_isi_test.min(), y_isi_test.max()], "r--")
    axes[1, col].set_title(f"ISI - {name}")
    axes[1, col].set_xlabel("Actual")
    axes[1, col].set_ylabel("Predicted")

plt.tight_layout()
plt.show()

# 12. Chart 4 - Residual plot (errors should be random, not patterned)
fig, axes = plt.subplots(2, 4, figsize=(18, 10))
fig.suptitle("Residual Plot (random scatter = good, patterns = bad)")

for col, (name, vals) in enumerate(ffmc_results.items()):
    axes[0, col].scatter(vals["predicted"], vals["residuals"])
    axes[0, col].axhline(0, color="r", linestyle="--")
    axes[0, col].set_title(f"FFMC - {name}")
    axes[0, col].set_xlabel("Predicted")
    axes[0, col].set_ylabel("Residual")

for col, (name, vals) in enumerate(isi_results.items()):
    axes[1, col].scatter(vals["predicted"], vals["residuals"])
    axes[1, col].axhline(0, color="r", linestyle="--")
    axes[1, col].set_title(f"ISI - {name}")
    axes[1, col].set_xlabel("Predicted")
    axes[1, col].set_ylabel("Residual")

plt.tight_layout()
plt.show()

# 13. Chart 5 - Inverse RMSE pie chart (larger slice = lower error = better model)
# Inverse RMSE normalised to 100% so slices represent relative performance
model_names        = list(ffmc_results.keys())
ffmc_inv_rmse      = [1 / v["rmse"] for v in ffmc_results.values()]
isi_inv_rmse       = [1 / v["rmse"] for v in isi_results.values()]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle("Relative Performance by Model - Inverse RMSE (larger slice = lower error = better)")

ax1.pie(ffmc_inv_rmse, labels=model_names, autopct="%1.1f%%")
ax1.set_title("FFMC - Ignition Risk")

ax2.pie(isi_inv_rmse, labels=model_names, autopct="%1.1f%%")
ax2.set_title("ISI - Spread Risk")

plt.tight_layout()
plt.show()