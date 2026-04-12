"""
Sparkline — stripped-down trend line for inline / small-space use.

No axes, no title, no legend. Just the line. End-dot optional.
Useful in tables, dashboards, or anywhere a full chart is too heavy.
"""

from __future__ import annotations

from typing import Union, Optional
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme


def sparkline(
    data,
    x: str,
    y: Union[str, list],
    end_dot: bool = True,
    theme="a16z-news",
    width: int = 200,
    height: int = 60,
) -> go.Figure:
    """
    Minimal sparkline — line only, no decorations.

    Parameters
    ----------
    data     : pd.DataFrame or list-of-dicts
    x        : column name for x-axis values (not displayed)
    y        : column name or list of names for the line(s)
    end_dot  : show a filled dot at the last data point
    theme    : 'a16z-news' | path to YAML | Theme object | None

    Returns
    -------
    plotly.graph_objects.Figure
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty")

    t = load_theme(theme)
    palette = t.palette if t else ["#1C2B3A"]
    bg = t.background if t else "#FFFFFF"
    line_w = t.line.get("width", 2) if t else 2

    y_cols = [y] if isinstance(y, str) else list(y)

    fig = go.Figure()

    for i, col in enumerate(y_cols):
        color = palette[i % len(palette)]
        vals = list(df[col])
        n = len(vals)

        # End dot: visible only on last point
        sizes = [0] * (n - 1) + [5] if (end_dot and n > 0) else [0] * n

        fig.add_trace(go.Scatter(
            x=df[x],
            y=vals,
            mode="lines+markers",
            line=dict(color=color, width=line_w),
            marker=dict(color=color, size=sizes),
            showlegend=False,
        ))

    fig.update_layout(
        width=width,
        height=height,
        margin=dict(t=4, b=4, l=4, r=4),
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        showlegend=False,
    )

    fig.update_xaxes(visible=False, showgrid=False, zeroline=False)
    fig.update_yaxes(visible=False, showgrid=False, zeroline=False)

    return fig
