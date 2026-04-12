"""Sparkline example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import sparkline as _src
from chart_library import sparkline, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return sparkline(
        _src._df,
        x="month",
        y=["GPT-4o", "Claude", "Gemini"],
        end_dot=True,
        theme="care-indeed",
        width=300,
        height=80,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline.png"))
    save_svg(fig, os.path.join(OUT, "sparkline.svg"))
    fig.write_html(os.path.join(OUT, "sparkline.html"))
    print("sparkline.png + sparkline.svg written")
