"""
Generate all.html — a gallery of all 7 chart types using the care-indeed theme.
Each section shows: <chart type name> / interactive Plotly chart / PNG side by side.
Run from the repo root: python examples/care-indeed/generate_all.py
"""

import os
import sys
import base64

import importlib.util

# Add scripts/ to path so chart_library is importable from example files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))

# Add a16z-news to sys.path so care-indeed modules can resolve their data imports.
# Do NOT add care-indeed itself — that causes circular name collisions since
# both directories share the same filenames (bar.py, line.py, …).
sys.path.insert(0, os.path.join(EXAMPLES_DIR, "../a16z-news"))


def _load(name: str):
    """Load a care-indeed example module by file path, avoiding sys.modules collisions."""
    path = os.path.join(EXAMPLES_DIR, f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"ci_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bar_ex     = _load("bar")
line_ex    = _load("line")
area_ex    = _load("area")
scatter_ex = _load("scatter")
pie_ex     = _load("pie")
table_ex   = _load("table")
map_ex     = _load("map")

# ── Chart registry: (display name, figure, png filename) ─────────────────────

CHARTS = [
    ("Bar",     bar_ex.make_fig(),     "bar_stacked.png"),
    ("Line",    line_ex.make_fig(),    "line.png"),
    ("Area",    area_ex.make_fig(),    "area.png"),
    ("Scatter", scatter_ex.make_fig(), "scatter.png"),
    ("Pie",     pie_ex.make_fig(),     "pie.png"),
    ("Table",   table_ex.make_fig(),   "table.png"),
    ("Map",     map_ex.make_fig(),     "map.png"),
]


def encode_png(png_path: str) -> str:
    with open(png_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ── Build HTML sections ───────────────────────────────────────────────────────

sections = []
for i, (name, fig, png_name) in enumerate(CHARTS):
    png_path = os.path.join(EXAMPLES_DIR, png_name)
    b64 = encode_png(png_path)

    fig.update_layout(autosize=True)

    include_plotlyjs = "cdn" if i == 0 else False
    chart_html = fig.to_html(include_plotlyjs=include_plotlyjs, full_html=False,
                              config={"displayModeBar": False, "responsive": True})

    section = f"""
  <section class="chart-section">
    <h2>{name}</h2>
    <div class="chart-row">
      <div class="chart-pane chart-interactive">
        <div class="pane-label">Interactive</div>
        {chart_html}
      </div>
      <div class="chart-pane chart-static">
        <div class="pane-label">PNG export</div>
        <img src="data:image/png;base64,{b64}" alt="{name} chart PNG" />
      </div>
    </div>
  </section>"""
    sections.append(section)

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chart Library — Care Indeed Theme</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: Montserrat, Roboto, sans-serif;
      background: #FFFAF7;
      color: #1F1C1B;
      padding: 40px 32px 80px;
    }

    header {
      margin-bottom: 56px;
      border-bottom: 2px solid #D9D6D5;
      padding-bottom: 24px;
    }

    header h1 {
      font-size: 28px;
      font-weight: bold;
      color: #1F1C1B;
      margin-bottom: 6px;
    }

    header p {
      font-size: 13px;
      color: #7A7470;
      font-style: italic;
    }

    .chart-section {
      margin-bottom: 72px;
    }

    .chart-section h2 {
      font-size: 20px;
      font-weight: bold;
      color: #FF6B35;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid #E5E4E3;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .chart-row {
      display: flex;
      gap: 24px;
      align-items: flex-start;
    }

    .chart-pane {
      flex: 1;
      background: #FFFAF7;
      border: 1px solid #E5E4E3;
      border-radius: 4px;
      padding: 16px;
      min-width: 0;
    }

    .pane-label {
      font-size: 10px;
      font-weight: bold;
      color: #9E9691;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 12px;
    }

    .chart-pane img {
      width: 100%;
      height: auto;
      display: block;
    }

    .chart-interactive .plotly-graph-div {
      width: 100% !important;
    }

    @media (max-width: 900px) {
      .chart-row { flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Chart Library</h1>
    <p>All chart types — interactive Plotly (left) vs. PNG export (right). Theme: care-indeed.</p>
  </header>
""" + "\n".join(sections) + """
</body>
</html>
"""

out_path = os.path.join(EXAMPLES_DIR, "all.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"all.html written to {out_path}")
