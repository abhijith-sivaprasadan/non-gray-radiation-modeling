"""Build a single self-contained HTML dashboard from generated portfolio outputs.

Unlike fortran_ui's write_html_dashboard (which only echoes [OK]/[missing] status
lines), this renders the actual generated figures (embedded as base64, so the file
is portable and works offline) and real CSV data as tables and stat tiles.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import base64
import html
from pathlib import Path

import pandas as pd

from thermal_radiation_modeling.published_data import (
    methanol_decoupled_metrics,
    singh_published_error_summary,
)

PROJECT_ROOT = _bootstrap.PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DASHBOARD_PATH = OUTPUT_DIR / "dashboard.html"

# Palette (see dataviz skill references/palette.md) - validated categorical/status colors.
CSS = """
:root {
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
  --grid: #e1e0d9; --border: rgba(11,11,11,0.10);
  --blue: #2a78d6; --aqua: #1baf7a; --yellow: #eda100; --violet: #4a3aa7;
  --good: #0ca30c; --warning: #fab219; --critical: #d03b3b;
}
@media (prefers-color-scheme: dark) {
  :root {
    --page: #0d0d0d; --surface: #1a1a19; --ink: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --border: rgba(255,255,255,0.10);
    --blue: #3987e5; --aqua: #199e70; --yellow: #c98500; --violet: #9085e9;
    --good: #0ca30c; --warning: #fab219; --critical: #d03b3b;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--page); color: var(--ink);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}
.layout { display: flex; min-height: 100vh; }
nav {
  width: 260px; flex: 0 0 260px; background: var(--surface); border-right: 1px solid var(--border);
  padding: 20px 0; position: sticky; top: 0; height: 100vh; overflow-y: auto;
}
nav .brand { padding: 0 20px 16px; font-weight: 650; font-size: 15px; border-bottom: 1px solid var(--border); margin-bottom: 8px; }
nav a {
  display: block; padding: 10px 20px; color: var(--ink-2); text-decoration: none; font-size: 14px;
  border-left: 3px solid transparent;
}
nav a:hover { color: var(--ink); background: var(--page); }
nav a.active { color: var(--blue); border-left-color: var(--blue); font-weight: 600; }
main { flex: 1; padding: 32px 40px 80px; max-width: 1080px; }
section { margin-bottom: 56px; scroll-margin-top: 20px; }
h1 { font-size: 26px; font-weight: 650; margin: 0 0 6px; }
h2 { font-size: 20px; font-weight: 650; margin: 0 0 4px; }
h3 { font-size: 15px; font-weight: 650; margin: 20px 0 8px; color: var(--ink-2); }
.subtitle { color: var(--ink-2); font-size: 14px; margin: 0 0 24px; }
.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 22px;
  margin-bottom: 16px;
}
.tiles { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0 20px; }
.tile {
  background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 18px; min-width: 150px; flex: 1 1 150px;
}
.tile .label { font-size: 12px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: .03em; }
.tile .value { font-size: 24px; font-weight: 650; margin-top: 4px; font-variant-numeric: tabular-nums; }
.tile .sub { font-size: 12px; color: var(--ink-2); margin-top: 2px; }
figure { margin: 16px 0; }
figure img { max-width: 100%; border-radius: 8px; border: 1px solid var(--border); display: block; }
figcaption { font-size: 12px; color: var(--ink-muted); margin-top: 6px; }
table { border-collapse: collapse; width: 100%; font-size: 13px; margin: 10px 0; }
th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--grid); font-variant-numeric: tabular-nums; }
th { color: var(--ink-2); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .02em; }
.note { font-size: 12px; color: var(--ink-muted); margin-top: 6px; }
code { background: var(--page); padding: 1px 6px; border-radius: 4px; font-size: 12.5px; }
pre code { display: block; padding: 12px 14px; overflow-x: auto; }
.status { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; padding: 2px 0; }
.status .dot { width: 8px; height: 8px; border-radius: 50%; }
.status.ok .dot { background: var(--good); } .status.ok { color: var(--ink-2); }
.status.missing .dot { background: var(--critical); } .status.missing { color: var(--critical); }
.eqn { background: var(--page); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; font-family: Consolas, monospace; font-size: 13.5px; }
"""

SECTIONS = [
    ("overview", "Overview"),
    ("project1", "Project 1: Hydrogen / H2O"),
    ("project2", "Project 2: Particle correlations"),
    ("project3", "Project 3: DOM on published fields"),
    ("project4", "Project 4: ML surrogate"),
    ("project5", "Project 5: RADCAL smoke test"),
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    body = []
    body.append(render_overview())
    body.append(render_project1())
    body.append(render_project2())
    body.append(render_project3())
    body.append(render_project4())
    body.append(render_project5())

    nav_links = "\n".join(
        f'<a href="#{anchor}">{html.escape(title)}</a>' for anchor, title in SECTIONS
    )
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Non-Gray Thermal Radiation Portfolio Dashboard</title>
<style>{CSS}</style></head>
<body>
<div class="layout">
<nav><div class="brand">Radiation Portfolio</div>{nav_links}</nav>
<main>
{"".join(body)}
</main>
</div>
</body></html>
"""
    DASHBOARD_PATH.write_text(page, encoding="utf-8")
    print(f"Wrote {DASHBOARD_PATH}")


def render_overview() -> str:
    rows = {row["case"]: row for row in singh_published_error_summary()}
    radial = rows["radial_source_peak_error"]
    methanol = {(row["model"], row["gray_gases"]): row for row in methanol_decoupled_metrics()}
    r2 = None
    metrics_path = OUTPUT_DIR / "project4_real_surrogate" / "tables" / "surrogate_metrics.csv"
    if metrics_path.exists():
        r2 = float(pd.read_csv(metrics_path)["r2_log_space"].iloc[0])

    tiles = [
        tile(
            "RC-FSK radial peak error",
            f"{radial['rcfsk_4_transformed_percent']:.0f}%",
            "vs. WSGG/Planck mean below",
        ),
        tile("WSGG radial peak error", f"{radial['wsgg_percent']:.0f}%"),
        tile("Planck-mean radial peak error", f"{radial['planck_mean_percent']:.0f}%"),
        tile(
            "Methanol RC-FSK (6 gases)",
            f"{methanol[('RC-FSK', 6)]['source_total_error_percent']:.1f}%",
            "source term error vs. RadCal's 34.8%",
        ),
        tile("Surrogate R2 (log kappa)", f"{r2:.5f}" if r2 is not None else "not yet run"),
    ]

    return f"""
<section id="overview">
<h1>Non-Gray Thermal Radiation Portfolio</h1>
<p class="subtitle">Real data extracted from published papers (Singh &amp; Hostikka 2026, Rashidzadeh et al. 2026,
Johansson 2017) - equations, benchmark tables, and a transparent DOM/ML pipeline built on top of them.</p>
<div class="tiles">{"".join(tiles)}</div>
<div class="card">
<h3>Artifact status</h3>
{artifact_status_list([
    ("Project 1", OUTPUT_DIR / "project1_real_hydrogen" / "project1_report.md"),
    ("Project 2", OUTPUT_DIR / "project2_real_particles" / "project2_report.md"),
    ("Project 3", OUTPUT_DIR / "project3_real_dom" / "project3_report.md"),
    ("Project 4", OUTPUT_DIR / "project4_real_surrogate" / "project4_report.md"),
    ("Project 5", OUTPUT_DIR / "project5_radcal_asset" / "radcal_run_report.md"),
])}
<p class="note">Regenerate everything with <code>python scripts/run_all.py</code> (Projects 1-4) and
<code>python scripts/run_radcal_asset.py</code> (Project 5), then rebuild this page with
<code>python scripts/build_dashboard.py</code>.</p>
</div>
</section>
"""


def render_project1() -> str:
    project_dir = OUTPUT_DIR / "project1_real_hydrogen"
    return f"""
<section id="project1">
<h2>Project 1: Published Hydrogen / H2O Radiation Data</h2>
<p class="subtitle">Singh &amp; Hostikka 2026 - HITEMP-derived H2O Planck-mean fit and validation fields.</p>
<div class="eqn">kappa_planck = X_H2O &times; 3.8821e6 &times; T^-1.9811</div>
{figure_row(project_dir / "figures", ["radial_fields.png", "axial_fields.png"])}
<h3>Published model-error summary</h3>
{csv_table(project_dir / "tables" / "singh_model_error_summary.csv")}
</section>
"""


def render_project2() -> str:
    project_dir = OUTPUT_DIR / "project2_real_particles"
    return f"""
<section id="project2">
<h2>Project 2: Johansson Particle Correlations</h2>
<p class="subtitle">Gray coal/char and ash absorption/scattering efficiencies fitted to Mie data (Johansson 2017, Eq. 8).</p>
{figure_row(project_dir / "figures", ["johansson_radius_sweep_1500K.png", "johansson_temperature_sweep_20um.png"])}
<h3>Correlation parameters</h3>
{csv_table(project_dir / "tables" / "johansson_correlation_parameters.csv")}
</section>
"""


def render_project3() -> str:
    project_dir = OUTPUT_DIR / "project3_real_dom"
    return f"""
<section id="project3">
<h2>Project 3: DOM on Published Fields</h2>
<p class="subtitle">1-D discrete-ordinates sweep through the radial and axial Singh &amp; Hostikka fields.
Not a reproduction of the paper's 2-D LBL/RCFSK benchmark.</p>
{figure_row(project_dir / "figures", ["published_field_dom_profiles.png"])}
<h3>Radial midline profile (preview)</h3>
{csv_table(project_dir / "tables" / "radial_midline_dom_profile.csv", max_rows=10)}
</section>
"""


def render_project4() -> str:
    project_dir = OUTPUT_DIR / "project4_real_surrogate"
    metrics_path = project_dir / "tables" / "surrogate_metrics.csv"
    tiles_html = ""
    if metrics_path.exists():
        row = pd.read_csv(metrics_path).iloc[0]
        tiles_html = (
            '<div class="tiles">'
            + tile("R2 (log space)", f"{row['r2_log_space']:.5f}")
            + tile("RMSE log10(kappa)", f"{row['rmse_log10']:.5f}")
            + tile("MAPE(kappa)", f"{100 * row['mean_absolute_percentage_error_kappa']:.2f}%")
            + tile(
                "Train / test samples", f"{int(row['train_samples'])} / {int(row['test_samples'])}"
            )
            + "</div>"
        )
    return f"""
<section id="project4">
<h2>Project 4: ML Surrogate for the Published H2O Correlation</h2>
<p class="subtitle">A small MLP trained to reproduce log10(kappa_planck) from the Singh &amp; Hostikka correlation.</p>
{tiles_html}
{figure_row(project_dir / "figures", ["surrogate_kappa_parity.png"])}
</section>
"""


def render_project5() -> str:
    project_dir = OUTPUT_DIR / "project5_radcal_asset"
    return f"""
<section id="project5">
<h2>Project 5: RADCAL Asset Smoke Test</h2>
<p class="subtitle">Launches the downloaded Firemodels RADCAL executable and parses its output.
A launch/parsing smoke test, not a validation claim.</p>
<h3>Parsed summary</h3>
{csv_table(project_dir / "radcal_summary.csv", value_columns=("metric", "value"))}
</section>
"""


# --- rendering helpers -------------------------------------------------------


def tile(label: str, value: str, sub: str | None = None) -> str:
    sub_html = f'<div class="sub">{html.escape(sub)}</div>' if sub else ""
    return (
        f'<div class="tile"><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div>{sub_html}</div>'
    )


def figure_row(figures_dir: Path, filenames: list[str]) -> str:
    figures = []
    for name in filenames:
        path = figures_dir / name
        if not path.exists():
            figures.append(
                f'<div class="note">Missing figure: <code>{html.escape(str(path))}</code>. '
                f"Run <code>python scripts/run_all.py</code>.</div>"
            )
            continue
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        figures.append(
            f'<figure><img src="data:image/png;base64,{encoded}" alt="{html.escape(name)}">'
            f"<figcaption>{html.escape(name)}</figcaption></figure>"
        )
    return "".join(figures)


def csv_table(path: Path, max_rows: int = 20, value_columns: tuple[str, str] | None = None) -> str:
    if not path.exists():
        return f'<p class="note">Missing table: <code>{html.escape(str(path))}</code>.</p>'
    frame = pd.read_csv(path)
    truncated = len(frame) > max_rows
    preview = frame.head(max_rows)

    header = "".join(f"<th>{html.escape(str(col))}</th>" for col in preview.columns)
    rows_html = []
    for _, row in preview.iterrows():
        cells = "".join(f"<td>{html.escape(format_cell(value))}</td>" for value in row)
        rows_html.append(f"<tr>{cells}</tr>")

    note = ""
    if truncated:
        note = f'<p class="note">Showing {max_rows} of {len(frame)} rows. Full data in <code>{html.escape(str(path))}</code>.</p>'
    return (
        f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>{note}"
    )


def format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def artifact_status_list(entries: list[tuple[str, Path]]) -> str:
    items = []
    for label, path in entries:
        if path.exists():
            items.append(
                f'<div class="status ok"><span class="dot"></span>{html.escape(label)} report generated</div>'
            )
        else:
            items.append(
                f'<div class="status missing"><span class="dot"></span>{html.escape(label)} not generated yet</div>'
            )
    return "".join(items)


if __name__ == "__main__":
    main()
