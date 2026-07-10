"""Project 2: published Johansson particle correlations fitted to Mie data."""

from __future__ import annotations

import _bootstrap  # noqa: F401

from pathlib import Path

import numpy as np
import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report

from thermal_radiation_modeling.particles import (
    johansson_2017_ash_efficiencies,
    johansson_2017_coal_char_efficiencies,
)
from thermal_radiation_modeling.published_data import SOURCES

OUTPUT_DIR = Path("outputs/project2_real_particles")


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    radii_um = np.geomspace(0.05, 500.0, 120)
    temperatures_k = np.array([700.0, 1000.0, 1500.0, 2000.0, 2500.0])
    rows = []
    for temperature in temperatures_k:
        coal_abs, coal_scat = johansson_2017_coal_char_efficiencies(radii_um, temperature)
        ash1_abs, ash1_scat = johansson_2017_ash_efficiencies(radii_um, temperature, "ash1")
        ash2_abs, ash2_scat = johansson_2017_ash_efficiencies(radii_um, temperature, "ash2")
        for i, radius in enumerate(radii_um):
            rows.append(
                {
                    "temperature_k": temperature,
                    "radius_um": radius,
                    "coal_char_q_abs": coal_abs[i],
                    "coal_char_q_scat": coal_scat[i],
                    "ash1_q_abs": ash1_abs[i],
                    "ash1_q_scat": ash1_scat[i],
                    "ash2_q_abs": ash2_abs[i],
                    "ash2_q_scat": ash2_scat[i],
                }
            )
    table = pd.DataFrame(rows)
    table.to_csv(OUTPUT_DIR / "tables/johansson_particle_efficiencies.csv", index=False)
    _write_parameter_table()
    _plot_radius_sweep(table)
    _plot_temperature_sweep()
    _write_report()
    print(f"Wrote {OUTPUT_DIR}")


def _write_parameter_table() -> None:
    pd.DataFrame(
        [
            {
                "correlation": "coal_char_q_abs",
                "y0": "(r_p T / 700)^1.1",
                "y_inf": "0.88 + 1680 / (r_p T)",
                "z": "1.6",
                "source": "Johansson 2017 Table 1",
            },
            {
                "correlation": "coal_char_q_scat",
                "y0": "(r_p T / 570)^3.9",
                "y_inf": "1.2 + 2600 / (r_p T)^1.2",
                "z": "0.65",
                "source": "Johansson 2017 Table 1",
            },
            {
                "correlation": "ash1_q_abs",
                "y0": "(r_p / (3.57 - 6.14 exp(-0.0014 T)))^1.09",
                "y_inf": "0.7 + 0.654 / r_p^0.22",
                "z": "1.1",
                "source": "Johansson 2017 Table 2",
            },
            {
                "correlation": "ash1_q_scat",
                "y0": "(r_p / (0.25 + 2.05 exp(-0.0019 T)))^4.0",
                "y_inf": "1.1 + 3.1 / r_p^0.97",
                "z": "0.42",
                "source": "Johansson 2017 Table 2",
            },
            {
                "correlation": "ash2_q_abs",
                "y0": "(r_p / (0.053 T - 32))^0.9",
                "y_inf": "0.7 + 1.16 / r_p^0.24",
                "z": "0.31 + 2.8e-4 T",
                "source": "Johansson 2017 Table 2",
            },
            {
                "correlation": "ash2_q_scat",
                "y0": "(r_p / (0.22 + 1.87 exp(-0.0015 T)))^4.0",
                "y_inf": "1.1 + 2.06 / r_p^0.4",
                "z": "0.54",
                "source": "Johansson 2017 Table 2",
            },
        ]
    ).to_csv(OUTPUT_DIR / "tables/johansson_correlation_parameters.csv", index=False)


def _plot_radius_sweep(table: pd.DataFrame) -> None:
    subset = table[table["temperature_k"] == 1500.0]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for axis, suffix, title in [
        (axes[0], "q_abs", "absorption efficiency"),
        (axes[1], "q_scat", "scattering efficiency"),
    ]:
        for prefix, label in [
            ("coal_char", "coal/char"),
            ("ash1", "ash1"),
            ("ash2", "ash2"),
        ]:
            axis.loglog(subset["radius_um"], subset[f"{prefix}_{suffix}"], label=label)
        axis.set_xlabel("particle radius [um]")
        axis.set_ylabel(title)
        axis.legend()
    fig.savefig(OUTPUT_DIR / "figures/johansson_radius_sweep_1500K.png", dpi=180)
    plt.close(fig)


def _plot_temperature_sweep() -> None:
    temperatures = np.linspace(700.0, 2500.0, 120)
    radius_um = 20.0
    coal_abs, coal_scat = johansson_2017_coal_char_efficiencies(radius_um, temperatures)
    ash1_abs, ash1_scat = johansson_2017_ash_efficiencies(radius_um, temperatures, "ash1")
    fig, axis = plt.subplots(figsize=(6, 4), constrained_layout=True)
    axis.plot(temperatures, coal_abs, label="coal/char Q_abs")
    axis.plot(temperatures, coal_scat, label="coal/char Q_scat")
    axis.plot(temperatures, ash1_abs, label="ash1 Q_abs")
    axis.plot(temperatures, ash1_scat, label="ash1 Q_scat")
    axis.set_xlabel("temperature [K]")
    axis.set_ylabel("efficiency at r_p = 20 um")
    axis.legend()
    fig.savefig(OUTPUT_DIR / "figures/johansson_temperature_sweep_20um.png", dpi=180)
    plt.close(fig)


def _write_report() -> None:
    source = SOURCES["johansson_2017"]
    therad = SOURCES["aalto_therad"]
    report = f"""# Project 2 Report: Published Particle Property Correlations

This workflow now uses Johansson's published gray particle correlations fitted to Mie
calculations, not a placeholder refractive-index curve.

Primary source:

{source.citation}

DOI: {source.url}

## Encoded Data

- Johansson Eq. (8): `1 / y^z = 1 / y0^z + 1 / y_inf^z`.
- Table 1 coal/char gray absorption and scattering efficiencies.
- Table 2 ash1 and ash2 gray absorption and scattering efficiencies.

The Aalto THERAD page is also relevant because it explicitly frames Mie absorption and
scattering cross sections as the design tool for spectrally selective particle coatings:
{therad.url}

## Interpretation

These correlations are closer to the doctoral topic than the earlier soot-like placeholder:
they are particle-property approximations derived from Mie data and intended for combustion
radiation calculations. They are still not vegetation-specific optical constants, so the
next research step is FTIR characterization of real fuel particles.
"""
    write_report(OUTPUT_DIR, "project2_report.md", report)


if __name__ == "__main__":
    main()
