"""
Paste-to-chart Flask app.
Paste tab-separated data (from Excel, Sheets, etc.), pick a chart type, generate.
"""

import json
import os
import sys

from flask import Flask, render_template, request, jsonify

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pandas as pd
from chart_library import (
    bar, line, area, scatter, pie, table, map_chart, diverging_bar
)

app = Flask(__name__)

CHART_FNS = {
    "bar": bar,
    "line": line,
    "area": area,
    "scatter": scatter,
    "pie": pie,
    "table": table,
    "map": map_chart,
    "diverging_bar": diverging_bar,
}

THEMES = ["news", "care-indeed", "quitemailingyourself", "default"]


def parse_tsv(text: str) -> dict:
    """Parse tab-separated text into a dict-of-lists suitable for pd.DataFrame."""
    lines = [l for l in text.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        raise ValueError("Need at least a header row and one data row.")

    headers = [h.strip() for h in lines[0].split("\t")]
    columns = {h: [] for h in headers}

    for line_text in lines[1:]:
        values = [v.strip() for v in line_text.split("\t")]
        # Pad or trim to match header count
        while len(values) < len(headers):
            values.append("")
        for h, v in zip(headers, values):
            columns[h].append(_coerce(v))

    return columns


def _coerce(v: str):
    """Coerce a string value to int, float, duration-as-float, or string."""
    if v == "":
        return None
    # H:MM or H:MM:SS duration → decimal hours
    if ":" in v:
        parts = v.split(":")
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2]) if len(parts) > 2 else 0
            return round(hours + minutes / 60 + seconds / 3600, 4)
        except (ValueError, IndexError):
            pass
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", themes=THEMES, chart_types=list(CHART_FNS.keys()))


@app.route("/columns", methods=["POST"])
def columns():
    """Return column names from pasted TSV."""
    tsv = request.json.get("tsv", "")
    try:
        data = parse_tsv(tsv)
        return jsonify({"columns": list(data.keys())})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/generate", methods=["POST"])
def generate():
    """Generate a chart from form data and return Plotly HTML div + JSON config."""
    payload = request.json

    try:
        data = parse_tsv(payload["tsv"])
    except Exception as e:
        return jsonify({"error": f"Parse error: {e}"}), 400

    df = pd.DataFrame(data)

    chart_type = payload.get("chart_type", "bar")
    fn = CHART_FNS.get(chart_type)
    if not fn:
        return jsonify({"error": f"Unknown chart type: {chart_type}"}), 400

    kwargs = {
        "title": payload.get("title", ""),
        "subtitle": payload.get("subtitle", ""),
        "source": payload.get("source", ""),
        "theme": payload.get("theme", "news") or None,
        "width": int(payload.get("width", 900)),
        "height": int(payload.get("height", 560)),
    }

    x_col = payload.get("x_col", "")
    y_cols = payload.get("y_cols", [])

    # Chart-specific params
    if chart_type in ("bar", "line", "area", "scatter", "diverging_bar"):
        if x_col:
            kwargs["x"] = x_col
        if y_cols:
            kwargs["y"] = y_cols if len(y_cols) > 1 else y_cols[0]
        if chart_type == "bar":
            kwargs["stacked"] = payload.get("stacked", False)

    elif chart_type == "pie":
        if x_col:
            kwargs["labels"] = x_col
        if y_cols:
            kwargs["values"] = y_cols[0]

    elif chart_type == "map":
        if x_col:
            kwargs["locations"] = x_col
        if y_cols:
            kwargs["values"] = y_cols[0]

    # table uses df directly, no x/y needed

    try:
        fig = fn(df, **kwargs)
    except Exception as e:
        return jsonify({"error": f"Chart error: {e}"}), 400

    chart_html = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={"displayModeBar": False, "responsive": True},
    )

    # Build exportable JSON config
    config = {
        "data": data,
        "chart_type": chart_type,
        **{k: v for k, v in kwargs.items() if v not in (None, "", [])},
    }
    if x_col:
        config["x"] = x_col
    if y_cols:
        config["y"] = y_cols if len(y_cols) > 1 else y_cols[0]

    return jsonify({"chart_html": chart_html, "config": config})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
