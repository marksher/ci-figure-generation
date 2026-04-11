"""Scatter + dumbbell demo — modeled after a16z streaming prices chart"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import a16z_charts as a16z

a16z.use_theme()

# Dumbbell: streaming service price ranges (ads vs ad-free)
data = pd.DataFrame({
    "service":   ["Hulu", "Disney+", "HBO Max", "Netflix", "Peacock", "Paramount+"],
    "with_ads":  [7.99,   7.99,      9.99,      7.99,      5.99,      5.99],
    "ad_free":   [17.99,  13.99,     15.99,     22.99,     13.99,     11.99],
})

fig, ax = a16z.scatter_chart(
    data,
    x=None, y=None,
    title="Streaming Prices Keep Climbing",
    subtitle="Monthly price with ads vs. ad-free, 2025",
    source="Company websites",
    dumbbell=True,
    dumbbell_y="service",
    dumbbell_start="with_ads",
    dumbbell_end="ad_free",
)

ax.set_xlabel("Monthly Price ($)", color=a16z.TEXT_MID, fontfamily="sans-serif")
fig.savefig("examples/scatter_dumbbell_demo.png")
print("Saved: examples/scatter_dumbbell_demo.png")
