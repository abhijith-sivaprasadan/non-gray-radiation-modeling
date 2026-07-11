"""Project 3 extension: how much does the DOM solver's missing scattering term matter?

docs/derivation_note.md discloses that solve_wsgg_dom couples particle *absorption* into
the local extinction coefficient but has no scattering source term - particle scattering
efficiencies computed by particles.py are never used by the RTE solver. This script
quantifies that gap rather than just stating it: it re-solves Project 3's radial-midline
case twice - once with the current absorption-only capability (particle scattering ignored,
exactly what solve_wsgg_dom does today), once with a real isotropic-scattering DOM solver
(dom1d.solve_gray_dom_with_isotropic_scattering, added alongside this script) that includes
the same particle scattering coefficient - and reports the difference in heat flux and
source term.

Scope: isotropic scattering is a simplification (real particle scattering is forward-peaked,
especially for particles large compared to the wavelength - see Project 2's Mie sweep
extension). This deliberately answers "how much does *some* scattering change the answer",
not "what does the *correct* phase function give" - a smaller, honest question with a
defensible answer, not a full scattering RTE implementation.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from pathlib import Path

import numpy as np
import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report

from thermal_radiation_modeling.constants import STEFAN_BOLTZMANN
from thermal_radiation_modeling.dom1d import (
    solve_gray_dom_with_isotropic_scattering,
    solve_pure_absorption_dom,
)
from thermal_radiation_modeling.particles import (
    absorption_coefficient_from_volume_fraction,
    johansson_2017_coal_char_efficiencies,
)
from thermal_radiation_modeling.published_data import (
    h2o_planck_mean_singh_hostikka_2026,
    singh_radial_case_fields,
)

OUTPUT_DIR = Path("outputs/project3_scattering_sensitivity")

PARTICLE_RADIUS_UM = 20.0
PARTICLE_VOLUME_FRACTION = 1.0e-6  # a dilute, representative particle loading


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    x = np.linspace(0.0, 1.0, 81)
    y_mid = np.array([0.5])
    temperature_field, mole_fraction_field = singh_radial_case_fields(x, y_mid)
    temperature = temperature_field[0]
    mole_fraction = mole_fraction_field[0]

    kappa_gas = h2o_planck_mean_singh_hostikka_2026(temperature, mole_fraction)
    kappa_particle, sigma_particle = _particle_coefficients(temperature)
    kappa_total = kappa_gas + kappa_particle

    blackbody = STEFAN_BOLTZMANN * temperature**4 / np.pi
    wall_t = max(float(temperature[0]), 1.0), max(float(temperature[-1]), 1.0)

    absorption_only = solve_pure_absorption_dom(
        x,
        temperature,
        kappa_total,
        quadrature_order=8,
        left_wall_temperature_k=wall_t[0],
        right_wall_temperature_k=wall_t[1],
    )
    left_wall_i = STEFAN_BOLTZMANN * wall_t[0] ** 4 / np.pi
    right_wall_i = STEFAN_BOLTZMANN * wall_t[1] ** 4 / np.pi
    with_scattering = solve_gray_dom_with_isotropic_scattering(
        x,
        kappa_total,
        sigma_particle,
        blackbody,
        left_wall_i,
        right_wall_i,
        quadrature_order=8,
    )

    comparison = pd.DataFrame(
        {
            "coordinate_m": x,
            "temperature_k": temperature,
            "kappa_gas_m-1": kappa_gas,
            "kappa_particle_m-1": kappa_particle,
            "sigma_particle_m-1": sigma_particle,
            "heat_flux_absorption_only_w_m2": absorption_only.heat_flux,
            "heat_flux_with_scattering_w_m2": with_scattering.heat_flux,
            "source_term_absorption_only_w_m3": absorption_only.source_term,
            "source_term_with_scattering_w_m3": with_scattering.source_term,
        }
    )
    # Normalized against the domain's peak |flux| rather than the local flux value: this
    # radial midline case is symmetric and the flux crosses exactly zero at the center, where
    # a local-value normalization blows up to a meaningless percentage for a near-zero
    # absolute difference.
    flux_scale = comparison["heat_flux_absorption_only_w_m2"].abs().max()
    comparison["heat_flux_error_percent_of_peak_flux"] = (
        100.0
        * (
            comparison["heat_flux_with_scattering_w_m2"]
            - comparison["heat_flux_absorption_only_w_m2"]
        )
        / flux_scale
    )
    comparison.to_csv(OUTPUT_DIR / "tables" / "scattering_sensitivity.csv", index=False)

    _plot(comparison)
    _write_report(comparison, sigma_particle)
    print(f"Wrote {OUTPUT_DIR}")


def _particle_coefficients(temperature: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    q_abs, q_scat = johansson_2017_coal_char_efficiencies(PARTICLE_RADIUS_UM, temperature)
    radius_m = PARTICLE_RADIUS_UM * 1e-6
    kappa_particle = absorption_coefficient_from_volume_fraction(
        PARTICLE_VOLUME_FRACTION, radius_m, q_abs
    )
    sigma_particle = absorption_coefficient_from_volume_fraction(
        PARTICLE_VOLUME_FRACTION, radius_m, q_scat
    )
    return kappa_particle, sigma_particle


def _plot(comparison: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    axes[0].plot(
        comparison["coordinate_m"],
        comparison["heat_flux_absorption_only_w_m2"],
        label="absorption only (current)",
    )
    axes[0].plot(
        comparison["coordinate_m"],
        comparison["heat_flux_with_scattering_w_m2"],
        "--",
        label="with isotropic scattering",
    )
    axes[0].set_xlabel("coordinate [m]")
    axes[0].set_ylabel("heat flux [W m^-2]")
    axes[0].legend(fontsize=8)

    axes[1].plot(comparison["coordinate_m"], comparison["heat_flux_error_percent_of_peak_flux"])
    axes[1].axhline(0.0, color="black", linewidth=0.8)
    axes[1].set_xlabel("coordinate [m]")
    axes[1].set_ylabel("heat flux error [% of peak |flux|]\n(scattering vs. absorption-only)")
    fig.savefig(OUTPUT_DIR / "figures" / "scattering_sensitivity.png", dpi=180)
    plt.close(fig)


def _write_report(comparison: pd.DataFrame, sigma_particle: np.ndarray) -> None:
    mean_abs_error = comparison["heat_flux_error_percent_of_peak_flux"].abs().mean()
    worst_row = comparison.loc[comparison["heat_flux_error_percent_of_peak_flux"].abs().idxmax()]
    mean_sigma = float(np.mean(sigma_particle))
    mean_kappa = float(comparison["kappa_gas_m-1"].mean() + comparison["kappa_particle_m-1"].mean())
    single_scattering_albedo = (
        mean_sigma / (mean_sigma + mean_kappa) if (mean_sigma + mean_kappa) > 0 else 0.0
    )

    report = f"""# Project 3 Extension: DOM Scattering Sensitivity Study

`solve_wsgg_dom` couples particle *absorption* into the local extinction coefficient but has
no scattering source term (documented in `docs/derivation_note.md`). This re-solves the
Project 3 radial-midline case with and without a real isotropic-scattering term
(`dom1d.solve_gray_dom_with_isotropic_scattering`, added for this study) for a representative
dilute particle loading (Johansson coal/char at r={PARTICLE_RADIUS_UM:.0f} um, volume
fraction {PARTICLE_VOLUME_FRACTION:.1e}) and reports the actual difference, rather than just
asserting scattering matters.

## Scope

Isotropic scattering is a simplification - real particle scattering is forward-peaked,
especially for particles large compared to the relevant wavelengths. This answers "how much
does *some* scattering change the answer", not "what does the *correct* phase function
give" - a smaller, honestly-scoped question.

## Result

Mean single-scattering albedo (sigma / (kappa+sigma), averaged over the domain):
{single_scattering_albedo:.3f}.

Mean absolute heat-flux difference (with-scattering vs. absorption-only), as a percentage
of the domain's peak |flux| (normalized this way, not against the local flux value, because
this profile crosses exactly zero at the domain center - a local-value normalization blows
up to a meaningless percentage there for a near-zero absolute difference):
{mean_abs_error:.3f}%. Worst case at x={worst_row['coordinate_m']:.3f} m:
{worst_row['heat_flux_error_percent_of_peak_flux']:+.3f}%.

Full profile in `tables/scattering_sensitivity.csv`; figure in
`figures/scattering_sensitivity.png`.

## Interpretation

At this particle loading, the single-scattering albedo above indicates how much of the
particles' extinction is scattering rather than true absorption - a value near 0 means
scattering is negligible here regardless of whether the solver includes it; a value
approaching 1 means most of what the particles do to radiation is redirect it, not absorb
it, and the current absorption-only solver's blind spot matters more. The heat-flux error
reported above is the direct, measured consequence for this specific loading - not a general
claim about all particle loadings, which would need this same comparison repeated across
the loading/size range Project 2 covers.
"""
    write_report(OUTPUT_DIR, "project3_scattering_sensitivity_report.md", report)


if __name__ == "__main__":
    main()
