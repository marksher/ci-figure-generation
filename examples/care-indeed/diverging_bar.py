"""Diverging bar chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import diverging_bar as _src
from chart_library import diverging_bar, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return diverging_bar(
        _src._df,
        y="city",
        x="pct_change",
        title="Percent Change in Homicide in 31 Cities",
        subtitle="2019–2025",
        source="Council on Criminal Justice",
        positive_label="Increase",
        negative_label="Decrease",
        sorted=True,
        theme="care-indeed",
        width=700,
        height=820,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "diverging_bar.png"))
    save_svg(fig, os.path.join(OUT, "diverging_bar.svg"))
    fig.write_html(os.path.join(OUT, "diverging_bar.html"))
    print("diverging_bar.png + diverging_bar.svg written")
