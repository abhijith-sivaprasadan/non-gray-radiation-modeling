"""Project 1: real published hydrogen/H2O radiation data fixtures."""

from __future__ import annotations

import _bootstrap  # noqa: F401

from pathlib import Path

import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report

from thermal_radiation_modeling.published_data import (
    SOURCES,
    h2o_planck_mean_singh_hostikka_2026,
    singh_axial_case_fields,
    singh_cpu_time_table,
    singh_published_error_summary,
    singh_radial_case_fields,
    singh_thermodynamic_grid_table,
    singh_wall_emission_error_table,
)

OUTPUT_DIR = Path("outputs/project1_real_hydrogen")


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    radial_x = pd.Series([i * 0.025 for i in range(41)], name="x_m").to_numpy()
    radial_y = pd.Series([i * 0.025 for i in range(41)], name="y_m").to_numpy()
    axial_x = pd.Series([i * 0.025 for i in range(81)], name="x_m").to_numpy()
    axial_y = pd.Series([i * 0.025 for i in range(161)], name="y_m").to_numpy()

    radial_t, radial_xh2o = singh_radial_case_fields(radial_x, radial_y)
    axial_t, axial_xh2o = singh_axial_case_fields(axial_x, axial_y)
    radial_kappa = h2o_planck_mean_singh_hostikka_2026(radial_t, radial_xh2o)
    axial_kappa = h2o_planck_mean_singh_hostikka_2026(axial_t, axial_xh2o)

    _write_field_table("radial", radial_x, radial_y, radial_t, radial_xh2o, radial_kappa)
    _write_field_table("axial", axial_x, axial_y, axial_t, axial_xh2o, axial_kappa)
    _plot_field("radial", radial_x, radial_y, radial_t, radial_xh2o, radial_kappa)
    _plot_field("axial", axial_x, axial_y, axial_t, axial_xh2o, axial_kappa)

    pd.DataFrame(singh_thermodynamic_grid_table()).to_csv(
        OUTPUT_DIR / "tables/singh_table1_thermodynamic_grid.csv", index=False
    )
    pd.DataFrame(singh_cpu_time_table()).to_csv(
        OUTPUT_DIR / "tables/singh_table2_cpu_times.csv", index=False
    )
    pd.DataFrame(singh_wall_emission_error_table()).to_csv(
        OUTPUT_DIR / "tables/singh_table3_wall_emission_errors.csv", index=False
    )
    pd.DataFrame(singh_published_error_summary()).to_csv(
        OUTPUT_DIR / "tables/singh_model_error_summary.csv", index=False
    )
    _write_report()
    print(f"Wrote {OUTPUT_DIR}")


def _write_field_table(name, x_values, y_values, temperature, mole_fraction, kappa) -> None:
    rows = []
    for row_index, y in enumerate(y_values):
        for col_index, x in enumerate(x_values):
            rows.append(
                {
                    "x_m": x,
                    "y_m": y,
                    "temperature_k": temperature[row_index, col_index],
                    "mole_fraction_h2o": mole_fraction[row_index, col_index],
                    "planck_mean_kappa_m-1": kappa[row_index, col_index],
                }
            )
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "tables" / f"{name}_case_fields.csv", index=False)


def _plot_field(name, x_values, y_values, temperature, mole_fraction, kappa) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4), constrained_layout=True)
    extent = [x_values[0], x_values[-1], y_values[0], y_values[-1]]
    for axis, data, title in [
        (axes[0], temperature, "temperature [K]"),
        (axes[1], mole_fraction, "H2O mole fraction"),
        (axes[2], kappa, "Planck mean kappa [m^-1]"),
    ]:
        image = axis.imshow(data, origin="lower", extent=extent, aspect="auto")
        axis.set_xlabel("x [m]")
        axis.set_ylabel("y [m]")
        axis.set_title(title)
        fig.colorbar(image, ax=axis)
    fig.savefig(OUTPUT_DIR / "figures" / f"{name}_fields.png", dpi=180)
    plt.close(fig)


def _write_report() -> None:
    source = SOURCES["singh_hostikka_2026"]
    report = f"""# Project 1 Report: Published Hydrogen/H2O Radiation Case Data

This project now uses real published equations and tables from:

{source.citation}

DOI: {source.url}

## Encoded Data

- Radial test case fields from Eqs. (15)-(18): 1 m x 1 m domain, temperature
  500-2000 K, H2O mole fraction 0.01-0.30.
- Axial test case fields from Eq. (20): 2 m x 4 m domain, temperature 300-2000 K,
  H2O mole fraction 0.01-0.30.
- H2O Planck-mean absorption correlation from Eq. (21):
  `kappa_planck = X_H2O * 3.8821e6 * T^-1.9811`.
- Thermodynamic tabulation ranges from Table 1.
- CPU timings from Table 2.
- Wall-emission errors from Table 3.
- Published RCFSK/WSGG/Planck-mean error summary from the results text.

## Why This Replaces the Synthetic Workflow

The previous workflow generated artificial spectra to exercise numerical machinery. This
report does not do that. It encodes equations, tables, and validation metrics extracted from
the research-team paper and writes them as reproducible CSV/PNG artifacts.

## Remaining External Boundary

The paper's supplementary RCFSK tables and HITEMP line-list calculations are not bundled in
this workspace. The repository therefore encodes the published derived quantities and table
values, while the HAPI/HITEMP adapter remains the path for reproducing spectral databases
from first principles.
"""
    write_report(OUTPUT_DIR, "project1_report.md", report)


if __name__ == "__main__":
    main()
