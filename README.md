# Advanced Data Analysis and Visualization in Logistics

**Week 3 Task | Prepared by: Shruti Rani**

This project explores a simulated logistics dataset of 300 shipments. It covers data-quality checks, descriptive statistics, correlation, KPI calculation, IQR outlier checks and 11 charts (10 in matplotlib, 1 in seaborn), and the findings are written up in a Word report.

## Project files
- `Week_3_Logistics_Analysis_Report.docx` – full report with embedded charts, interpretations, KPIs, outlier analysis, limitations and recommendations.
- `logistics_dataset.csv` – 300 simulated shipment records (1 Jan to 27 Oct 2026).
- `logistics_analysis.py` – runs the whole analysis, saves the charts and writes the two summary CSVs.
- `charts/` – the 11 PNG charts created by the script.
- `kpi_summary.csv` – key KPI values (written by the script).
- `outlier_analysis.csv` – IQR bounds and flagged counts per numeric variable (written by the script).
- `submission_description.txt` – short description of the submission.
- `requirements.txt` – Python packages needed.

## How to run
1. Install Python 3.9 or newer.
2. Install the packages: `pip install -r requirements.txt`
3. Keep the script and the CSV in the same folder.
4. Run: `python logistics_analysis.py`
5. Charts appear in `charts/`; `kpi_summary.csv` and `outlier_analysis.csv` are refreshed.

## Important notes
- All shipment data is hypothetical and was generated for learning. Nothing here describes a real company.
- The 3-day on-time threshold and the 80% line in the on-time chart are assumptions for this exercise, not industry standards.
- Weather delay is zero for most shipments, so the IQR outlier rule is not meaningful for that column (see `outlier_analysis.csv`).
- Correlation does not prove causation. Validate any finding on real operational data before acting on it.
