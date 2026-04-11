"""Bar chart demo — modeled after a16z 'Where the Money's Flowing in Enterprise AI'"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import a16z_charts as a16z

a16z.use_theme()

data = pd.DataFrame({
    "category": [
        "Coding & Dev Tools", "Data & Analytics", "Customer Support",
        "Sales & Marketing", "Healthcare", "Legal & Compliance",
        "Finance & Accounting", "HR & Recruiting",
    ],
    "investment_b": [4.2, 3.1, 2.8, 2.3, 1.9, 1.4, 1.1, 0.8],
})

fig, ax = a16z.bar_chart(
    data,
    x="category",
    y="investment_b",
    title="Where the Money's Flowing in Enterprise AI",
    subtitle="Venture investment by category, 2024 ($B)",
    source="PitchBook, a16z Research",
    orientation="h",
)

ax.set_xlabel("Investment ($B)", color=a16z.TEXT_MID, fontfamily="sans-serif")
fig.savefig("examples/bar_demo.png")
print("Saved: examples/bar_demo.png")
