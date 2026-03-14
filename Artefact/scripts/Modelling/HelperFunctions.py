import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import pandas as pd

# Get valid input either from a list of options and/or a type
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

# Plot graph from df output of model
def visualise(df, moderate_risk, high_risk, extreme_risk):
    df = df.copy()

    # Make sure Time is real datetime before plotting
    df["Time"] = pd.to_datetime(df["Time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["Time"]).sort_values("Time")

    fig, axes = plt.subplots(3, 1, figsize=(12, 18))

    # Plot 1: Final risk over time
    axes[0].plot(df["Time"], df["FinalWildfireRiskIndex"], linewidth=1.5)

    axes[0].set_title("Final Risk Over Time")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Final Risk (%)")
    axes[0].set_ylim(0, extreme_risk + 2)

    # Threshold lines
    axes[0].axhline(moderate_risk, color="orange", linestyle="--", linewidth=1)
    axes[0].axhline(high_risk, color="red", linestyle="--", linewidth=1)
    axes[0].axhline(extreme_risk, color="purple", linestyle="--", linewidth=1)

    # Background bands
    axes[0].axhspan(0, moderate_risk, alpha=0.08, color="green")
    axes[0].axhspan(moderate_risk, high_risk, alpha=0.08, color="yellow")
    axes[0].axhspan(high_risk, extreme_risk, alpha=0.08, color="orange")
    axes[0].axhspan(extreme_risk, extreme_risk + 2, alpha=0.08, color="red")

    # Cleaner x-axis dates
    locator = mdates.AutoDateLocator(minticks=4, maxticks=7)
    formatter = mdates.DateFormatter("%Y-%m-%d")

    axes[0].xaxis.set_major_locator(locator)
    axes[0].xaxis.set_major_formatter(formatter)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)
    axes[0].grid(axis="x", visible=False)
    axes[0].minorticks_off()

    # Plot 2: Count of each risk band
    band_order = ["Low", "Moderate", "High", "Extreme"]
    band_counts = df["FinalWildfireRiskBand"].value_counts().reindex(band_order, fill_value=0)
    axes[1].bar(band_counts.index, band_counts.values)
    axes[1].set_title("Count of Each Final Risk Band")
    axes[1].set_xlabel("Final Risk Band")
    axes[1].set_ylabel("Count")

    # Plot 3: Correlation heatmap
    corr_cols = [
        "Heat", "DrySoil", "DryAir", "Wind", "RainRelief",
        "InstantRisk", "DrynessInput", "CarryoverRisk", "CombinedRisk"
    ]
    corr = df[corr_cols].corr()

    im = axes[2].imshow(corr, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1)
    axes[2].set_title("Correlation Heatmap")
    axes[2].set_xticks(range(len(corr_cols)))
    axes[2].set_xticklabels(corr_cols, rotation=90)
    axes[2].set_yticks(range(len(corr_cols)))
    axes[2].set_yticklabels(corr_cols)

    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            value = corr.iloc[i, j]
            axes[2].text(j, i, f"{value:.2f}", ha="center", va="center")

    fig.colorbar(im, ax=axes[2])

    plt.tight_layout()
    plt.show()
    return