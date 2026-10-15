"""
Advanced Data Analysis and Visualization in Logistics
Week 3 Task | Prepared by: Shruti Rani

Tools    : pandas, numpy, matplotlib, seaborn
Run      : python logistics_analysis.py   (keep this file and logistics_dataset.csv in the same folder)
Outputs  : charts/*.png, kpi_summary.csv, outlier_analysis.csv

Note: every shipment record is simulated for learning purposes. The 3-day on-time
threshold and the 80% chart target are assumptions made for this exercise, not
industry standards.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_FILE = Path("logistics_dataset.csv")
OUT = Path("charts")
OUT.mkdir(exist_ok=True)

ON_TIME_LIMIT_DAYS = 3      # assumed service level (project assumption)
TARGET_ON_TIME_PCT = 80     # illustrative target line used in one chart only

df = pd.read_csv(DATA_FILE, parse_dates=["Shipment_Date"])

numeric = ["Distance_km", "Shipment_Volume_kg", "Delivery_Time_days",
           "Transportation_Cost_INR", "Weather_Delay_days"]
modes = ["Road", "Rail", "Air"]


def save(name):
    """Tidy the layout, save the current figure into charts/ and close it."""
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=160)
    plt.close()


# ---------------------------------------------------------------------------
# 1. Data quality checks
# ---------------------------------------------------------------------------
print("Shape:", df.shape)
print("\nMissing values:\n", df.isna().sum())
print("\nDuplicate shipment IDs:", df["Shipment_ID"].duplicated().sum())
print("\nInvalid / non-positive distance rows:", (df["Distance_km"] <= 0).sum())
print("\nInvalid / negative cost rows:", (df["Transportation_Cost_INR"] < 0).sum())
print("\nDate range:", df["Shipment_Date"].min().date(), "to", df["Shipment_Date"].max().date())

# ---------------------------------------------------------------------------
# 2. Descriptive statistics and correlation
# ---------------------------------------------------------------------------
print("\nDescriptive statistics:\n", df[numeric].describe().round(2).T)
print("\nCorrelation matrix:\n", df[numeric].corr().round(2))

# ---------------------------------------------------------------------------
# 3. IQR outlier detection (records are flagged, never deleted automatically)
# ---------------------------------------------------------------------------
outlier_rows = []
for col in numeric:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    count = int(((df[col] < lower) | (df[col] > upper)).sum())
    note = ""
    if col == "Weather_Delay_days":
        # Most shipments have zero weather delay, so Q1 = Q3 = 0 and IQR = 0.
        # Every non-zero value then gets flagged, which is not a real outlier signal.
        note = ("Zero-inflated variable (IQR = 0): flagged rows are simply shipments "
                "with a weather delay, not true outliers")
    outlier_rows.append({"Variable": col, "Q1": q1, "Q3": q3, "IQR": iqr,
                         "Lower_Bound": lower, "Upper_Bound": upper,
                         "Outlier_Count": count, "Note": note})
    print(f"{col}: IQR bounds=({lower:.2f}, {upper:.2f}), flagged={count}")
pd.DataFrame(outlier_rows).round(2).to_csv("outlier_analysis.csv", index=False)

# ---------------------------------------------------------------------------
# 4. KPI engineering
# ---------------------------------------------------------------------------
df["On_Time_Flag"] = (df["Delivery_Time_days"] <= ON_TIME_LIMIT_DAYS).astype(int)
df["Cost_per_km"] = df["Transportation_Cost_INR"] / df["Distance_km"]
df["Cost_per_kg"] = df["Transportation_Cost_INR"] / df["Shipment_Volume_kg"]

kpis = {
    "Total shipments": len(df),
    "On-time rate (%)": df["On_Time_Flag"].mean() * 100,
    "Delayed shipments (%)": (1 - df["On_Time_Flag"].mean()) * 100,
    "Average delivery time (days)": df["Delivery_Time_days"].mean(),
    "Median delivery time (days)": df["Delivery_Time_days"].median(),
    "Average transportation cost (INR)": df["Transportation_Cost_INR"].mean(),
    "Median transportation cost (INR)": df["Transportation_Cost_INR"].median(),
    "Average cost per km (INR/km)": df["Cost_per_km"].mean(),
    "Average cost per kg (INR/kg)": df["Cost_per_kg"].mean(),
}
print("\nKPI summary:")
for name, value in kpis.items():
    print(f"  {name}: {value:.2f}")
pd.DataFrame({"KPI": list(kpis), "Value": [round(v, 2) for v in kpis.values()]}) \
    .to_csv("kpi_summary.csv", index=False)

# ---------------------------------------------------------------------------
# 5. Transport mode and region summaries
# ---------------------------------------------------------------------------
def summarise(by):
    out = df.groupby(by).agg(
        Shipments=("Shipment_ID", "count"),
        Avg_Delivery_Days=("Delivery_Time_days", "mean"),
        Avg_Cost_INR=("Transportation_Cost_INR", "mean"),
        Avg_Cost_per_km=("Cost_per_km", "mean"),
        On_Time_Rate=("On_Time_Flag", "mean"),
    )
    out["On_Time_Rate"] *= 100
    return out.round(2)


print("\nBy transport mode:\n", summarise("Transport_Mode"))
print("\nBy region:\n", summarise("Region"))

# ---------------------------------------------------------------------------
# 6. Charts (matplotlib)
# ---------------------------------------------------------------------------
# Figure 1 - distribution of delivery time
plt.figure(figsize=(8, 5))
plt.hist(df["Delivery_Time_days"], bins=18, edgecolor="black")
plt.title("Distribution of Delivery Times")
plt.xlabel("Delivery time (days)"); plt.ylabel("Number of shipments")
save("delivery_time_distribution.png")

# Figure 2 - delivery time by transport mode
plt.figure(figsize=(8, 5))
plt.boxplot([df.loc[df["Transport_Mode"] == m, "Delivery_Time_days"] for m in modes],
            tick_labels=modes)          # tick_labels needs matplotlib >= 3.9
plt.title("Delivery Time by Transportation Mode")
plt.xlabel("Transportation mode"); plt.ylabel("Delivery time (days)")
save("delivery_by_mode.png")

# Figure 3 - distance vs cost
plt.figure(figsize=(8, 5))
plt.scatter(df["Distance_km"], df["Transportation_Cost_INR"], alpha=0.65)
plt.title("Distance vs Transportation Cost")
plt.xlabel("Distance (km)"); plt.ylabel("Transportation cost (INR)")
save("distance_vs_cost.png")

# Figure 4 - average delivery time by region
region_avg = df.groupby("Region")["Delivery_Time_days"].mean().sort_values()
plt.figure(figsize=(8, 5))
plt.bar(region_avg.index, region_avg.values)
plt.title("Average Delivery Time by Region")
plt.xlabel("Region"); plt.ylabel("Average delivery time (days)")
save("region_delivery.png")

# Figure 5 - correlation matrix
corr = df[numeric].corr()
plt.figure(figsize=(7, 6))
plt.imshow(corr, vmin=-1, vmax=1, aspect="auto")
plt.colorbar(label="Correlation coefficient")
plt.xticks(range(len(numeric)), numeric, rotation=45, ha="right")
plt.yticks(range(len(numeric)), numeric)
for i in range(len(numeric)):
    for j in range(len(numeric)):
        plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
plt.title("Correlation Matrix of Numeric Variables")
save("correlation_matrix.png")

# Figure 6 - average cost by mode
mode_cost = df.groupby("Transport_Mode")["Transportation_Cost_INR"].mean().reindex(modes)
plt.figure(figsize=(8, 5))
plt.bar(mode_cost.index, mode_cost.values)
plt.title("Average Transportation Cost by Mode")
plt.xlabel("Transportation mode"); plt.ylabel("Average cost (INR)")
save("cost_by_mode.png")

# Figure 7 - monthly shipment volume
# The data runs from 1 Jan to 27 Oct 2026, so October is a partial month.
df["Month"] = df["Shipment_Date"].dt.to_period("M").astype(str)
monthly = df.groupby("Month").size()
plt.figure(figsize=(9, 5))
plt.plot(monthly.index, monthly.values, marker="o")
plt.title("Monthly Shipment Volume (October is a partial month)")
plt.xlabel("Month"); plt.ylabel("Number of shipments")
plt.xticks(rotation=45)
plt.yticks(range(int(monthly.min()) - 1, int(monthly.max()) + 2))   # whole numbers only
save("monthly_shipment_volume.png")

# Figure 8 - on-time rate by region
region_ontime = (df.groupby("Region")["On_Time_Flag"].mean() * 100).sort_values(ascending=False)
plt.figure(figsize=(8, 5))
plt.bar(region_ontime.index, region_ontime.values)
plt.axhline(TARGET_ON_TIME_PCT, linestyle="--", color="red",
            label=f"Illustrative {TARGET_ON_TIME_PCT}% target")
plt.ylim(0, 100)
plt.title("On-Time Delivery Rate by Region")
plt.xlabel("Region"); plt.ylabel("On-time rate (%)")
plt.legend(loc="upper right")
save("region_ontime_rate.png")

# Figure 9 - shipment volume vs delivery time
plt.figure(figsize=(8, 5))
plt.scatter(df["Shipment_Volume_kg"], df["Delivery_Time_days"], alpha=0.65)
plt.title("Shipment Volume vs Delivery Time")
plt.xlabel("Shipment volume (kg)"); plt.ylabel("Delivery time (days)")
save("volume_vs_delivery.png")

# Figure 10 - region x mode heatmap of average delivery time
pivot = df.pivot_table(index="Region", columns="Transport_Mode",
                       values="Delivery_Time_days", aggfunc="mean")
plt.figure(figsize=(8, 5))
plt.imshow(pivot, aspect="auto")
plt.colorbar(label="Average delivery time (days)")
plt.xticks(range(len(pivot.columns)), pivot.columns)
plt.yticks(range(len(pivot.index)), pivot.index)
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        if pd.notna(pivot.iloc[i, j]):
            plt.text(j, i, f"{pivot.iloc[i, j]:.1f}", ha="center", va="center",
                     fontsize=9, color="white")
plt.title("Average Delivery Time: Region x Transport Mode")
save("region_mode_delivery_heatmap.png")

# ---------------------------------------------------------------------------
# 7. Seaborn chart
# Figure 3 shows two separate bands of points. Colouring each shipment by
# transport mode and fitting a trend line per mode explains why.
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid")
plt.figure(figsize=(9, 5.5))
sns.scatterplot(data=df, x="Distance_km", y="Transportation_Cost_INR",
                hue="Transport_Mode", hue_order=modes, alpha=0.7)
for m in modes:
    sns.regplot(data=df[df["Transport_Mode"] == m], x="Distance_km",
                y="Transportation_Cost_INR", scatter=False, ci=None, line_kws={"linewidth": 1.2})
plt.title("Distance vs Transportation Cost by Mode (with trend lines)")
plt.xlabel("Distance (km)"); plt.ylabel("Transportation cost (INR)")
plt.legend(title="Transport mode")
save("seaborn_cost_vs_distance_by_mode.png")
sns.reset_orig()

print(f"\nCharts saved to {OUT.resolve()}")
