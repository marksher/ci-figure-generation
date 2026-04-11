"""Table chart demo — modeled after a16z SaaS Scoreboard"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import a16z_charts as a16z

a16z.use_theme()

data = pd.DataFrame({
    "Company":       ["Salesforce", "ServiceNow", "Workday", "HubSpot", "Zendesk", "Freshworks"],
    "Rev Growth %":  [8.7, 22.4, 16.1, 20.3, 9.1, 14.2],
    "NRR %":         [111, 125, 119, 108, 113, 107],
    "Gross Margin %":[76.4, 79.1, 74.8, 83.2, 78.5, 68.9],
    "Rule of 40":    [31, 48, 35, 29, 22, 18],
    "YoY Δ":         [2.1, 5.4, -1.2, 3.8, -3.1, 1.9],
})

fig, ax = a16z.table_chart(
    data,
    title="SaaS Performance Scoreboard",
    subtitle="Key metrics for enterprise SaaS leaders, Q1 2025",
    source="Company filings, a16z Research",
    color_positive=["YoY Δ"],
    pct_columns=["Rev Growth %", "Gross Margin %"],
)

fig.savefig("examples/table_demo.png")
print("Saved: examples/table_demo.png")
