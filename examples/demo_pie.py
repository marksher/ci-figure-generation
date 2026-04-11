"""Donut chart demo — modeled after a16z enterprise AI penetration"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import a16z_charts as a16z

a16z.use_theme()

data = pd.DataFrame({
    "segment": ["Using AI", "Evaluating", "Not Yet"],
    "pct":     [29, 38, 33],
})

fig, ax = a16z.donut_chart(
    data,
    labels="segment",
    values="pct",
    title="Enterprise AI Adoption — Fortune 500",
    subtitle="Share of companies by adoption stage, 2025",
    source="a16z Research",
)

fig.savefig("examples/pie_demo.png")
print("Saved: examples/pie_demo.png")
