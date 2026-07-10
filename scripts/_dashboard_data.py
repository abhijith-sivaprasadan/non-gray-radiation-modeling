"""Shared JSON-serializable data loading for the static and live dashboards.

Both scripts/build_dashboard.py (single-file static export) and
scripts/dashboard_server.py (live local app) read the same generated CSV/report
artifacts through this module, so they never drift apart.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from thermal_radiation_modeling.published_data import (
    methanol_decoupled_metrics,
    singh_published_error_summary,
)


def records(path: Path, max_rows: int | None = None) -> dict | None:
    """Load a CSV as {columns, rows, total_rows} with NaN replaced by None."""

    if not path.exists():
        return None
    frame = pd.read_csv(path)
    total_rows = len(frame)
    if max_rows is not None and total_rows > max_rows:
        frame = frame.head(max_rows)
    clean = frame.astype(object).where(pd.notnull(frame), None)
    rows = clean.to_dict(orient="records")
    return {
        "columns": list(frame.columns),
        "rows": [_json_safe_row(row) for row in rows],
        "total_rows": total_rows,
    }


def _json_safe_row(row: dict) -> dict:
    return {key: _json_safe_value(value) for key, value in row.items()}


def _json_safe_value(value: object) -> object:
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def build_payload(output_dir: Path) -> dict:
    payload: dict = {
        "overview": _overview(output_dir),
        "project1": _project1(output_dir),
        "project2": _project2(output_dir),
        "project3": _project3(output_dir),
        "project4": _project4(output_dir),
        "project5": _project5(output_dir),
    }
    return payload


def _overview(output_dir: Path) -> dict:
    rows = {row["case"]: row for row in singh_published_error_summary()}
    radial = rows["radial_source_peak_error"]
    methanol = {(row["model"], row["gray_gases"]): row for row in methanol_decoupled_metrics()}

    r2 = None
    metrics_path = output_dir / "project4_real_surrogate" / "tables" / "surrogate_metrics.csv"
    if metrics_path.exists():
        r2 = float(pd.read_csv(metrics_path)["r2_log_space"].iloc[0])

    tiles = [
        {
            "label": "RC-FSK radial peak error",
            "value": f"{radial['rcfsk_4_transformed_percent']:.0f}%",
            "sub": "vs. WSGG/Planck mean below",
        },
        {"label": "WSGG radial peak error", "value": f"{radial['wsgg_percent']:.0f}%"},
        {
            "label": "Planck-mean radial peak error",
            "value": f"{radial['planck_mean_percent']:.0f}%",
        },
        {
            "label": "Methanol RC-FSK (6 gases)",
            "value": f"{methanol[('RC-FSK', 6)]['source_total_error_percent']:.1f}%",
            "sub": "source term error vs. RadCal's 34.8%",
        },
        {
            "label": "Surrogate R2 (log kappa)",
            "value": f"{r2:.5f}" if r2 is not None else "not yet run",
        },
    ]

    report_paths = {
        "Project 1": output_dir / "project1_real_hydrogen" / "project1_report.md",
        "Project 2": output_dir / "project2_real_particles" / "project2_report.md",
        "Project 3": output_dir / "project3_real_dom" / "project3_report.md",
        "Project 4": output_dir / "project4_real_surrogate" / "project4_report.md",
        "Project 5": output_dir / "project5_radcal_asset" / "radcal_run_report.md",
    }
    artifacts = [{"label": label, "ok": path.exists()} for label, path in report_paths.items()]

    return {"tiles": tiles, "artifacts": artifacts}


def _project1(output_dir: Path) -> dict:
    project_dir = output_dir / "project1_real_hydrogen"
    return {
        "equation": "kappa_planck = X_H2O * 3.8821e6 * T^-1.9811",
        "figures": _figure_urls(project_dir, ["radial_fields.png", "axial_fields.png"]),
        "error_summary": records(project_dir / "tables" / "singh_model_error_summary.csv"),
    }


def _project2(output_dir: Path) -> dict:
    project_dir = output_dir / "project2_real_particles"
    return {
        "params": records(project_dir / "tables" / "johansson_correlation_parameters.csv"),
        "efficiencies": records(project_dir / "tables" / "johansson_particle_efficiencies.csv"),
    }


def _project3(output_dir: Path) -> dict:
    project_dir = output_dir / "project3_real_dom"
    return {
        "radial": records(project_dir / "tables" / "radial_midline_dom_profile.csv"),
        "axial": records(project_dir / "tables" / "axial_centerline_dom_profile.csv"),
    }


def _project4(output_dir: Path) -> dict:
    project_dir = output_dir / "project4_real_surrogate"
    metrics = records(project_dir / "tables" / "surrogate_metrics.csv")
    return {
        "metrics": metrics["rows"][0] if metrics else None,
        "predictions": records(project_dir / "tables" / "surrogate_predictions.csv"),
    }


def _project5(output_dir: Path) -> dict:
    project_dir = output_dir / "project5_radcal_asset"
    return {"summary": records(project_dir / "radcal_summary.csv")}


def _figure_urls(project_dir: Path, filenames: list[str]) -> list[dict]:
    figures = []
    for name in filenames:
        path = project_dir / "figures" / name
        figures.append({"name": name, "exists": path.exists(), "path": str(path)})
    return figures
