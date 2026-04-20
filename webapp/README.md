# Paste-to-Chart Web App

Paste tab-separated data from Excel, Google Sheets, or any spreadsheet and get an interactive Plotly chart instantly.

## Setup

```bash
cd webapp
pip install -r requirements.txt
python app.py
```

Opens at [http://localhost:5000](http://localhost:5000).

## Usage

1. **Paste data** — copy rows from a spreadsheet (tab-separated). The first row is treated as column headers.
2. **Pick columns** — X and Y column selects auto-populate after pasting.
3. **Choose chart type** — bar, line, area, scatter, pie, table, map, or diverging bar.
4. **Set options** — title, subtitle, source, theme, dimensions, stacked (for bar charts).
5. **Generate** — click Generate to render an interactive chart.
6. **Export** — click Download JSON to get a config file compatible with the chart library's `make_fig()` pattern.

## Supported data formats

- Numbers are auto-detected (integers, floats)
- `H:MM` or `H:MM:SS` durations are converted to decimal hours
- Everything else is treated as a string
- Empty cells become `None`

## Themes

All bundled themes are available: `news`, `care-indeed`, `quitemailingyourself`, and `default` (plain Plotly defaults).

## Architecture

```
webapp/
  app.py                 # Flask app — routes: /, /columns, /generate
  requirements.txt       # flask, pandas, plotly, kaleido
  static/
    pretext.js           # Pretext text layout library
  templates/
    index.html           # Single-page UI
```

The app imports chart functions directly from `scripts/chart_library`, so the repo must be cloned (not just the webapp folder).
