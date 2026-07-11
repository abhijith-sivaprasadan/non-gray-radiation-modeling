"""Project 2 extension: large, non-Rayleigh particle Mie sweep toward the vegetation/char gap.

Project 2 (run_project2_real_particles.py) implements Johansson's *gray* (wavelength-
integrated) coal/char and ash correlations - real published data, but for combustion
particles, and gray by construction, so it cannot show how much a particle's radiative
properties actually vary across the thermal-IR spectrum.

This script uses the same, already-validated Mie solver (particles.mie_efficiencies,
verified against the independent miepython library) directly, spectrally resolved, at
particle sizes representative of wildland fuel char fragments (tens of microns - well beyond
the Rayleigh limit Project 2's small-radius end sits in) - and compares the result against
Johansson's gray correlation at the same sizes.

Honesty boundary: published optical constants (complex refractive index) specific to
wildland vegetation/char at these wavelengths are scarce in the literature - this is part of
why FTIR characterization of real fuel particles is a real, open research need, not a solved
problem. This sweep therefore uses a small, explicitly labeled *range* of representative
absorbing-particle refractive indices spanning weakly to strongly absorbing carbonaceous
particles (broadly consistent with values reported across the combustion/biomass-burning
literature), not a single measured vegetation dataset. Read the results as illustrating
*how much size and wavelength matter* for large fuel particles, not as a validated
vegetation radiative-property result.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from pathlib import Path

import numpy as np
import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report

from thermal_radiation_modeling.particles import (
    johansson_2017_coal_char_efficiencies,
    mie_efficiencies,
)

OUTPUT_DIR = Path("outputs/project2_extended_mie_sweep")

RADII_UM = [5.0, 20.0, 50.0, 100.0]
WAVELENGTHS_UM = np.linspace(1.0, 15.0, 60)
REFRACTIVE_INDICES = {
    "weakly absorbing (m=1.5+0.3i)": 1.5 + 0.3j,
    "moderately absorbing (m=1.7+0.5i)": 1.7 + 0.5j,
    "strongly absorbing (m=2.0+1.0i)": 2.0 + 1.0j,
}
JOHANSSON_REFERENCE_TEMPERATURE_K = 1500.0


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    sweep_rows = _compute_sweep()
    sweep_table = pd.DataFrame(sweep_rows)
    sweep_table.to_csv(OUTPUT_DIR / "tables" / "mie_sweep_qabs_qsca.csv", index=False)

    variation_table = _compute_spectral_variation(sweep_table)
    variation_table.to_csv(OUTPUT_DIR / "tables" / "spectral_variation_summary.csv", index=False)

    comparison_table = _compare_against_johansson(sweep_table)
    comparison_table.to_csv(OUTPUT_DIR / "tables" / "vs_johansson_gray_comparison.csv", index=False)

    _plot_spectral_curves(sweep_table)
    _write_report(variation_table, comparison_table)
    print(f"Wrote {OUTPUT_DIR}")


def _compute_sweep() -> list[dict[str, float | str]]:
    rows = []
    for radius_um in RADII_UM:
        radius_m = radius_um * 1e-6
        for label, refractive_index in REFRACTIVE_INDICES.items():
            for wavelength_um in WAVELENGTHS_UM:
                wavelength_m = wavelength_um * 1e-6
                efficiencies = mie_efficiencies(refractive_index, radius_m, wavelength_m)
                rows.append(
                    {
                        "radius_um": radius_um,
                        "refractive_index_label": label,
                        "wavelength_um": wavelength_um,
                        "q_abs": float(efficiencies.q_abs),
                        "q_sca": float(efficiencies.q_sca),
                        "q_ext": float(efficiencies.q_ext),
                    }
                )
    return rows


def _compute_spectral_variation(sweep_table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = sweep_table.groupby(["radius_um", "refractive_index_label"])
    for (radius_um, label), group in grouped:
        mean_qabs = group["q_abs"].mean()
        spread = (
            (group["q_abs"].max() - group["q_abs"].min()) / mean_qabs
            if mean_qabs > 0
            else float("nan")
        )
        rows.append(
            {
                "radius_um": radius_um,
                "refractive_index_label": label,
                "q_abs_mean": mean_qabs,
                "q_abs_min": group["q_abs"].min(),
                "q_abs_max": group["q_abs"].max(),
                "relative_spectral_spread": spread,
            }
        )
    return pd.DataFrame(rows)


def _compare_against_johansson(sweep_table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for radius_um in RADII_UM:
        johansson_qabs, _ = johansson_2017_coal_char_efficiencies(
            radius_um, JOHANSSON_REFERENCE_TEMPERATURE_K
        )
        for label in REFRACTIVE_INDICES:
            subset = sweep_table[
                (sweep_table["radius_um"] == radius_um)
                & (sweep_table["refractive_index_label"] == label)
            ]
            mie_mean_qabs = subset["q_abs"].mean()
            rows.append(
                {
                    "radius_um": radius_um,
                    "refractive_index_label": label,
                    "johansson_gray_q_abs": float(johansson_qabs),
                    "mie_spectral_mean_q_abs": float(mie_mean_qabs),
                    "ratio_mie_to_johansson": (
                        float(mie_mean_qabs / johansson_qabs) if johansson_qabs else float("nan")
                    ),
                }
            )
    return pd.DataFrame(rows)


def _plot_spectral_curves(sweep_table: pd.DataFrame) -> None:
    fig, axes = plt.subplots(
        1, len(RADII_UM), figsize=(4.2 * len(RADII_UM), 4), constrained_layout=True, sharey=True
    )
    for axis, radius_um in zip(axes, RADII_UM):
        subset_radius = sweep_table[sweep_table["radius_um"] == radius_um]
        for label in REFRACTIVE_INDICES:
            subset = subset_radius[subset_radius["refractive_index_label"] == label].sort_values(
                "wavelength_um"
            )
            axis.plot(subset["wavelength_um"], subset["q_abs"], label=label)
        axis.set_title(f"r = {radius_um:.0f} um")
        axis.set_xlabel("wavelength [um]")
    axes[0].set_ylabel("Q_abs")
    axes[-1].legend(fontsize=7)
    fig.savefig(OUTPUT_DIR / "figures" / "qabs_vs_wavelength_by_radius.png", dpi=180)
    plt.close(fig)


def _write_report(variation_table: pd.DataFrame, comparison_table: pd.DataFrame) -> None:
    worst_spread_row = variation_table.loc[variation_table["relative_spectral_spread"].idxmax()]
    report = f"""# Project 2 Extension: Large-Particle Spectral Mie Sweep

This uses the same Mie solver as Project 2 (`particles.mie_efficiencies`, independently
verified against the `miepython` reference library) directly and spectrally resolved, at
particle radii (5-100 um) representative of wildland fuel char fragments - well beyond the
Rayleigh limit, and beyond what Johansson's *gray* correlations can show about
wavelength-dependence by construction.

## Honesty Boundary

Published optical constants specific to wildland vegetation/char at these wavelengths are
scarce - this is part of why FTIR characterization of real fuel particles is a genuine open
research need. This sweep uses a small, explicitly labeled range of representative
absorbing-particle refractive indices (weakly to strongly absorbing carbonaceous particles),
**not** a single measured vegetation dataset. Read the results as illustrating how much size
and wavelength matter for large fuel particles, not as a validated vegetation result.

## How Non-Gray Are Large Particles?

Relative spectral spread of Q_abs (max-min over 1-15 um, divided by the mean) by radius and
refractive index - full data in `tables/spectral_variation_summary.csv`:

{variation_table.to_markdown(index=False)}

Largest spread: r={worst_spread_row['radius_um']:.0f} um,
{worst_spread_row['refractive_index_label']}, relative spread
{worst_spread_row['relative_spectral_spread']:.2f}.

## Comparison Against Johansson's Gray Correlation

Spectral mean Q_abs (this sweep) vs. Johansson's gray coal/char Q_abs at
T={JOHANSSON_REFERENCE_TEMPERATURE_K:.0f} K, same radii - full data in
`tables/vs_johansson_gray_comparison.csv`:

{comparison_table.to_markdown(index=False)}

## Interpretation

A gray correlation necessarily reports one number per (radius, temperature); the spectral
sweep shows the real spread that number is averaging over. Where that spread is large, a
gray treatment is a coarser approximation - relevant to non-gray radiation modeling
specifically because it quantifies *how much* is lost by going gray for large fuel-sized
particles, rather than asserting it qualitatively.
"""
    write_report(OUTPUT_DIR, "project2_extended_mie_sweep_report.md", report)


if __name__ == "__main__":
    main()
