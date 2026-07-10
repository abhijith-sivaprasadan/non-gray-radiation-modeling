"""Project 3: DOM calculations on published Singh & Hostikka validation fields."""

from __future__ import annotations

import _bootstrap  # noqa: F401

from pathlib import Path

import numpy as np
import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report

from thermal_radiation_modeling.dom1d import solve_pure_absorption_dom
from thermal_radiation_modeling.published_data import (
    SOURCES,
    h2o_planck_mean_singh_hostikka_2026,
    singh_axial_case_fields,
    singh_published_error_summary,
    singh_radial_case_fields,
)

OUTPUT_DIR = Path("outputs/project3_real_dom")


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    radial_x = np.linspace(0.0, 1.0, 81)
    radial_y_mid = np.array([0.5])
    radial_t, radial_xh2o = singh_radial_case_fields(radial_x, radial_y_mid)
    radial_profile = _solve_profile(
        "radial_midline",
        radial_x,
        radial_t[0],
        radial_xh2o[0],
        left_wall_temperature_k=0.0,
        right_wall_temperature_k=0.0,
    )

    axial_y = np.linspace(0.0, 4.0, 161)
    axial_x_mid = np.array([1.0])
    axial_t, axial_xh2o = singh_axial_case_fields(axial_x_mid, axial_y)
    axial_profile = _solve_profile(
        "axial_centerline",
        axial_y,
        axial_t[:, 0],
        axial_xh2o[:, 0],
        left_wall_temperature_k=0.0,
        right_wall_temperature_k=0.0,
    )

    pd.DataFrame(singh_published_error_summary()).to_csv(
        OUTPUT_DIR / "tables/published_model_error_summary.csv", index=False
    )
    _plot_profiles(radial_profile, axial_profile)
    _write_report()
    print(f"Wrote {OUTPUT_DIR}")


def _solve_profile(name, coordinate, temperature, mole_fraction, **walls):
    kappa = h2o_planck_mean_singh_hostikka_2026(temperature, mole_fraction)
    # The paper uses cold black walls for the axial case. The 1-D solver cannot use
    # exactly 0 K because blackbody intensity and validation checks require positive
    # temperature, so use a numerically negligible wall temperature.
    left_wall = max(float(walls["left_wall_temperature_k"]), 1.0)
    right_wall = max(float(walls["right_wall_temperature_k"]), 1.0)
    result = solve_pure_absorption_dom(
        coordinate,
        temperature,
        kappa,
        quadrature_order=8,
        left_wall_temperature_k=left_wall,
        right_wall_temperature_k=right_wall,
    )
    frame = pd.DataFrame(
        {
            "coordinate_m": coordinate,
            "temperature_k": temperature,
            "mole_fraction_h2o": mole_fraction,
            "planck_mean_kappa_m-1": kappa,
            "heat_flux_w_m2": result.heat_flux,
            "source_term_w_m3": result.source_term,
            "incident_radiation_w_m2": result.incident_radiation,
        }
    )
    frame.to_csv(OUTPUT_DIR / "tables" / f"{name}_dom_profile.csv", index=False)
    return name, frame


def _plot_profiles(*profiles) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for name, frame in profiles:
        axes[0].plot(frame["coordinate_m"], frame["heat_flux_w_m2"], label=name)
        axes[1].plot(frame["coordinate_m"], frame["source_term_w_m3"], label=name)
    axes[0].set_xlabel("coordinate [m]")
    axes[0].set_ylabel("heat flux [W m^-2]")
    axes[1].set_xlabel("coordinate [m]")
    axes[1].set_ylabel("source term [W m^-3]")
    axes[0].legend()
    axes[1].legend()
    fig.savefig(OUTPUT_DIR / "figures/published_field_dom_profiles.png", dpi=180)
    plt.close(fig)


def _write_report() -> None:
    source = SOURCES["singh_hostikka_2026"]
    report = f"""# Project 3 Report: DOM on Published Hydrogen/H2O Fields

This script uses the analytic radial and axial fields and H2O Planck-mean correlation from:

{source.citation}

DOI: {source.url}

## What Is Computed Here

- A 1-D S8 DOM sweep through the radial test case midline.
- A 1-D S8 DOM sweep through the axial test case centerline.
- Local H2O Planck-mean absorption using the paper's Eq. (21).

## What Is Not Claimed

This is not a reproduction of the paper's 2-D LBL/RCFSK benchmark. The paper's published
comparison metrics are stored separately in `tables/published_model_error_summary.csv`.
The purpose here is to demonstrate a transparent DOM implementation on the same published
thermodynamic fields, while keeping the high-fidelity benchmark values tied to the paper.
"""
    write_report(OUTPUT_DIR, "project3_report.md", report)


if __name__ == "__main__":
    main()
