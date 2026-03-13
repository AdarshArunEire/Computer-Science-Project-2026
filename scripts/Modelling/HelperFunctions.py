import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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

    # Set style
    sns.set_style("whitegrid")

    # Create figure and axes
    fig, axes = plt.subplots(3, 1, figsize=(12, 18))

    # Plot 1: Line plot of final risk over time
    sns.lineplot(x="Time", y="FinalWildfireRiskIndex", data=df, ax=axes[0], marker="")

    axes[0].set_title("Final Risk Over Time")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Final Risk (%)")
    axes[0].set_ylim(0, 100)

    # Threshold lines
    axes[0].axhline(moderate_risk, color="orange", linestyle="--", linewidth=1)
    axes[0].axhline(high_risk, color="red", linestyle="--", linewidth=1)
    axes[0].axhline(extreme_risk, color="purple", linestyle="--", linewidth=1)

    # Background bands
    axes[0].axhspan(0, moderate_risk, alpha=0.08, color="green")
    axes[0].axhspan(moderate_risk, high_risk, alpha=0.08, color="yellow")
    axes[0].axhspan(high_risk, extreme_risk, alpha=0.08, color="orange")
    axes[0].axhspan(extreme_risk, 100, alpha=0.08, color="red")

    # Plot 2: Bar plot of count of each risk band
    sns.countplot(x="FinalWildfireRiskBand", data=df, order=["Low", "Moderate", "High", "Extreme"], ax=axes[1])
    axes[1].set_title("Count of Each Final Risk Band")
    axes[1].set_xlabel("Final Risk Band")
    axes[1].set_ylabel("Count")

    # Plot 3: Heatmap of correlation between variables
    corr = df[["Heat", "DrySoil", "DryAir", "Wind", "RainRelief", "InstantRisk", "DrynessInput", "CarryoverRisk", "CombinedRisk"]].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=axes[2])
    axes[2].set_title("Correlation Heatmap")

    plt.tight_layout()
    plt.show()
    
    return