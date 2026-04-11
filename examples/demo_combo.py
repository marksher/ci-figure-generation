"""Combo chart demo — modeled after a16z 'Seed Dollars Up, Deal Count Falling'"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import a16z_charts as a16z

a16z.use_theme()

data = pd.DataFrame({
    "quarter":       ["Q1 '25", "Q2 '25", "Q3 '25", "Q4 '25", "Q1 '26"],
    "invested_b":    [9.2,      8.7,      9.5,      10.1,     11.3],
    "deal_count":    [5800,     5200,     4900,     4600,     4400],
})

fig, ax1, ax2 = a16z.combo_chart(
    data,
    x="quarter",
    bar_y="invested_b",
    line_y="deal_count",
    title="Seed Dollars Are Up, But Deal Count Is Falling",
    subtitle="Global seed and angel investment by quarter",
    source="Crunchbase",
    bar_label="Total $ Invested (B)",
    line_label="Number of Deals",
)

ax1.set_ylabel("Investment ($B)", color=a16z.TEXT_MID, fontfamily="sans-serif")
ax2.set_ylabel("Deal Count", color=a16z.TEXT_MID, fontfamily="sans-serif")
fig.savefig("examples/combo_demo.png")
print("Saved: examples/combo_demo.png")
