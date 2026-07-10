"""Build a single self-contained HTML dashboard from generated portfolio outputs.

This is the portable, offline, single-file export (figures embedded as base64).
For the live, interactive version with charts/sortable tables/re-run buttons, run
scripts/dashboard_server.py instead. Both read the same data through
scripts/_dashboard_data.py.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import base64
import html
from pathlib import Path

from _dashboard_data import build_payload

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
.status { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; padding: 2px 0; }
.status .dot { width: 8px; height: 8px; border-radius: 50%; }
.status.ok .dot { background: var(--good); } .status.ok { color: var(--ink-2); }
.status.missing .dot { background: var(--critical); } .status.missing { color: var(--critical); }
.eqn { background: var(--page); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; font-family: Consolas, monospace; font-size: 13.5px; }
.banner { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 12px 18px; margin-bottom: 24px; font-size: 13px; color: var(--ink-2); }
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
    payload = build_payload(OUTPUT_DIR)

    body = [
        render_overview(payload["overview"]),
        render_project1(payload["project1"]),
        render_project2(payload["project2"]),
        render_project3(payload["project3"]),
        render_project4(payload["project4"]),
        render_project5(payload["project5"]),
    ]

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
<div class="banner">This is the static, portable export. For live re-runs and interactive charts,
run <code>python scripts/dashboard_server.py</code> and open the printed URL.</div>
{"".join(body)}
</main>
</div>
</body></html>
"""
    DASHBOARD_PATH.write_text(page, encoding="utf-8")
    print(f"Wrote {DASHBOARD_PATH}")


def render_overview(data: dict) -> str:
    tiles = "".join(tile(t["label"], t["value"], t.get("sub")) for t in data["tiles"])
    artifacts = "".join(status_line(a["label"], a["ok"]) for a in data["artifacts"])
    return f"""
<section id="overview">
<h1>Non-Gray Thermal Radiation Portfolio</h1>
<p class="subtitle">Real data extracted from published papers (Singh &amp; Hostikka 2026, Rashidzadeh et al. 2026,
Johansson 2017) - equations, benchmark tables, and a transparent DOM/ML pipeline built on top of them.</p>
<div class="tiles">{tiles}</div>
<div class="card">
<h3>Artifact status</h3>
{artifacts}
<p class="note">Regenerate everything with <code>python scripts/run_all.py</code> (Projects 1-4) and
<code>python scripts/run_radcal_asset.py</code> (Project 5), then rebuild this page with
<code>python scripts/build_dashboard.py</code>.</p>
</div>
</section>
"""


def render_project1(data: dict) -> str:
    figures = "".join(embed_figure(f) for f in data["figures"])
    return f"""
<section id="project1">
<h2>Project 1: Published Hydrogen / H2O Radiation Data</h2>
<p class="subtitle">Singh &amp; Hostikka 2026 - HITEMP-derived H2O Planck-mean fit and validation fields.</p>
<div class="eqn">{html.escape(data['equation'])}</div>
{figures}
<h3>Published model-error summary</h3>
{records_table(data["error_summary"])}
</section>
"""


def render_project2(data: dict) -> str:
    figures_dir = OUTPUT_DIR / "project2_real_particles" / "figures"
    figures = "".join(
        embed_figure(
            {"name": name, "exists": (figures_dir / name).exists(), "path": str(figures_dir / name)}
        )
        for name in ["johansson_radius_sweep_1500K.png", "johansson_temperature_sweep_20um.png"]
    )
    return f"""
<section id="project2">
<h2>Project 2: Johansson Particle Correlations</h2>
<p class="subtitle">Gray coal/char and ash absorption/scattering efficiencies fitted to Mie data (Johansson 2017, Eq. 8).</p>
{figures}
<h3>Correlation parameters</h3>
{records_table(data["params"])}
</section>
"""


def render_project3(data: dict) -> str:
    figures_dir = OUTPUT_DIR / "project3_real_dom" / "figures"
    figure_path = figures_dir / "published_field_dom_profiles.png"
    figures = embed_figure(
        {
            "name": "published_field_dom_profiles.png",
            "exists": figure_path.exists(),
            "path": str(figure_path),
        }
    )
    return f"""
<section id="project3">
<h2>Project 3: DOM on Published Fields</h2>
<p class="subtitle">1-D discrete-ordinates sweep through the radial and axial Singh &amp; Hostikka fields.
Not a reproduction of the paper's 2-D LBL/RCFSK benchmark.</p>
{figures}
<h3>Radial midline profile (preview)</h3>
{records_table(data["radial"], max_rows=10)}
</section>
"""


def render_project4(data: dict) -> str:
    figures_dir = OUTPUT_DIR / "project4_real_surrogate" / "figures"
    figure_path = figures_dir / "surrogate_kappa_parity.png"
    figures = embed_figure(
        {
            "name": "surrogate_kappa_parity.png",
            "exists": figure_path.exists(),
            "path": str(figure_path),
        }
    )
    tiles_html = ""
    metrics = data["metrics"]
    if metrics is not None:
        tiles_html = (
            '<div class="tiles">'
            + "".join(
                [
                    tile("R2 (log space)", f"{metrics['r2_log_space']:.5f}"),
                    tile("RMSE log10(kappa)", f"{metrics['rmse_log10']:.5f}"),
                    tile(
                        "MAPE(kappa)",
                        f"{100 * metrics['mean_absolute_percentage_error_kappa']:.2f}%",
                    ),
                    tile(
                        "Train / test samples",
                        f"{int(metrics['train_samples'])} / {int(metrics['test_samples'])}",
                    ),
                ]
            )
            + "</div>"
        )
    return f"""
<section id="project4">
<h2>Project 4: ML Surrogate for the Published H2O Correlation</h2>
<p class="subtitle">A small MLP trained to reproduce log10(kappa_planck) from the Singh &amp; Hostikka correlation.</p>
{tiles_html}
{figures}
</section>
"""


def render_project5(data: dict) -> str:
    return f"""
<section id="project5">
<h2>Project 5: RADCAL Asset Smoke Test</h2>
<p class="subtitle">Launches the downloaded Firemodels RADCAL executable and parses its output.
A launch/parsing smoke test, not a validation claim.</p>
<h3>Parsed summary</h3>
{records_table(data["summary"])}
</section>
"""


# --- rendering helpers -------------------------------------------------------


def tile(label: str, value: str, sub: str | None = None) -> str:
    sub_html = f'<div class="sub">{html.escape(sub)}</div>' if sub else ""
    return (
        f'<div class="tile"><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div>{sub_html}</div>'
    )


def status_line(label: str, ok: bool) -> str:
    css_class = "ok" if ok else "missing"
    suffix = "report generated" if ok else "not generated yet"
    return f'<div class="status {css_class}"><span class="dot"></span>{html.escape(label)} {suffix}</div>'


def embed_figure(figure: dict) -> str:
    if not figure["exists"]:
        return (
            f'<div class="note">Missing figure: <code>{html.escape(figure["path"])}</code>. '
            f"Run <code>python scripts/run_all.py</code>.</div>"
        )
    encoded = base64.b64encode(Path(figure["path"]).read_bytes()).decode("ascii")
    return (
        f'<figure><img src="data:image/png;base64,{encoded}" alt="{html.escape(figure["name"])}">'
        f"<figcaption>{html.escape(figure['name'])}</figcaption></figure>"
    )


def records_table(data: dict | None, max_rows: int = 20) -> str:
    if data is None:
        return '<p class="note">Not generated yet.</p>'
    header = "".join(f"<th>{html.escape(str(col))}</th>" for col in data["columns"])
    preview_rows = data["rows"][:max_rows]
    rows_html = []
    for row in preview_rows:
        cells = "".join(
            f"<td>{html.escape(format_cell(row.get(col)))}</td>" for col in data["columns"]
        )
        rows_html.append(f"<tr>{cells}</tr>")
    note = ""
    if data["total_rows"] > len(preview_rows):
        note = f'<p class="note">Showing {len(preview_rows)} of {data["total_rows"]} rows.</p>'
    return (
        f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>{note}"
    )


def format_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


if __name__ == "__main__":
    main()
