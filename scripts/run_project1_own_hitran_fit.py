"""Project 1 extension: an own HITRAN-derived H2O fit, independent of the published lookup.

run_project1_real_hydrogen.py reproduces Singh & Hostikka's *published* Planck-mean
correlation - a real number, but their number. This script computes an independent one:
fetches real H2O line-by-line data from HITRAN via HAPI, computes a Voigt-profile absorption
coefficient, reduces it to Planck-mean absorption and total emissivity (reusing lbl.py),
fits both an own power-law correlation (same functional form as the published one, for a
direct apples-to-apples comparison) and a real multi-gray-gas WSGG model (using this
repository's own wsgg.py/fitting.py toolkit), and validates both against the published
values.

Two disclosed boundaries versus the reference paper - see own_hitran_fit.py's module
docstring and docs/derivation_note.md for the full discussion:

1. Uses HITRAN (via HAPI's interactive fetch), not HITEMP (the paper's source; not
   practically fetchable here). HITRAN omits weak hot lines HITEMP includes, which should
   make this *under*-predict absorption, worsening at higher T.
2. Covers H2O's two strongest IR bands (rotational + 6.3 um) rather than the paper's full
   ~150-6500 cm^-1 range, for tractability. Concentrating the Planck-mean average on just
   the two strongest bands (rather than including the paper's full range, most of which
   absorbs more weakly) should make this *over*-predict absorption - the opposite direction
   from boundary 1.

These two boundaries pull in opposite directions, not the same one - which of them
dominates is an empirical question, not something to assert from first principles. A single
narrow-band smoke test (150 K, T=1200 K, X_H2O=0.10, 1000-1010 cm^-1 only) during development
of this script gave an over-prediction, suggesting boundary 2 dominates in-band, but the full
grid below is what actually settles it, not that guess.

This script makes real network requests (to hitran.org) and can take several minutes
(observed: ~13s per (T, X_H2O) grid point for the full 150-2200 cm^-1 range at 0.05 cm^-1
resolution).
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import time
from pathlib import Path

import numpy as np
import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report

from thermal_radiation_modeling.fitting import fit_polynomial_wsgg
from thermal_radiation_modeling.hapi_adapter import HAPIUnavailableError
from thermal_radiation_modeling.io import save_wsgg_model_csv
from thermal_radiation_modeling.own_hitran_fit import (
    fetch_h2o_lines,
    fit_own_power_law,
    h2o_absorption_coefficient_cm,
    own_planck_mean_and_emissivity,
)
from thermal_radiation_modeling.published_data import SOURCES, h2o_planck_mean_singh_hostikka_2026

OUTPUT_DIR = Path("outputs/project1_own_hitran_fit")
HAPI_DATA_DIR = OUTPUT_DIR / "hapi_data"

# Bounded to H2O's pure-rotational band and the 6.3 um fundamental - see module docstring.
WAVENUMBER_MIN_CM = 150.0
WAVENUMBER_MAX_CM = 2200.0
WAVENUMBER_STEP_CM = 0.05

TEMPERATURES_K = [400.0, 700.0, 1000.0, 1300.0, 1600.0, 1900.0, 2200.0]
MOLE_FRACTIONS_H2O = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30]

WSGG_FIXED_MOLE_FRACTION = 0.10
WSGG_PATH_LENGTHS_M = np.geomspace(0.01, 3.0, 6)
WSGG_GRAY_GAS_COUNT = 2
WSGG_POLYNOMIAL_DEGREE = 2


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    try:
        table_name = fetch_h2o_lines(WAVENUMBER_MIN_CM, WAVENUMBER_MAX_CM, HAPI_DATA_DIR)
    except HAPIUnavailableError as exc:
        print(f"Skipping: {exc}")
        return

    grid_rows = _compute_planck_mean_grid(table_name)
    grid_table = pd.DataFrame(grid_rows)
    grid_table.to_csv(OUTPUT_DIR / "tables" / "own_vs_published_planck_mean.csv", index=False)

    own_a, own_b = fit_own_power_law(
        grid_table["temperature_k"].to_numpy(),
        grid_table["mole_fraction_h2o"].to_numpy(),
        grid_table["own_kappa_planck_m-1"].to_numpy(),
    )

    wsgg_fit, wsgg_table = _fit_own_wsgg(table_name)
    wsgg_table.to_csv(OUTPUT_DIR / "tables" / "own_wsgg_fit_quality.csv", index=False)
    save_wsgg_model_csv(wsgg_fit.model, OUTPUT_DIR / "tables" / "own_wsgg_model_coefficients.csv")

    _plot_parity(grid_table)
    _plot_kappa_curves(grid_table)
    _write_report(grid_table, own_a, own_b, wsgg_fit)
    print(f"Wrote {OUTPUT_DIR}")


def _compute_planck_mean_grid(table_name: str) -> list[dict[str, float]]:
    rows = []
    total = len(TEMPERATURES_K) * len(MOLE_FRACTIONS_H2O)
    count = 0
    for temperature in TEMPERATURES_K:
        for mole_fraction in MOLE_FRACTIONS_H2O:
            start = time.time()
            point = own_planck_mean_and_emissivity(
                WAVENUMBER_MIN_CM,
                WAVENUMBER_MAX_CM,
                WAVENUMBER_STEP_CM,
                temperature,
                mole_fraction,
                table_name,
                path_length_m=1.0,
            )
            published_kappa = float(h2o_planck_mean_singh_hostikka_2026(temperature, mole_fraction))
            count += 1
            elapsed = time.time() - start
            print(
                f"[{count}/{total}] T={temperature:.0f} K, X_H2O={mole_fraction:.2f}: "
                f"own kappa={point.planck_mean_kappa_m:.4g} m^-1, published={published_kappa:.4g} m^-1 "
                f"({elapsed:.1f}s)"
            )
            rows.append(
                {
                    "temperature_k": temperature,
                    "mole_fraction_h2o": mole_fraction,
                    "own_kappa_planck_m-1": point.planck_mean_kappa_m,
                    "published_kappa_planck_m-1": published_kappa,
                    "relative_error_percent": 100.0
                    * (point.planck_mean_kappa_m - published_kappa)
                    / published_kappa,
                }
            )
    return rows


def _fit_own_wsgg(table_name: str):
    from thermal_radiation_modeling.lbl import total_emissivity_from_spectrum

    emissivity = np.zeros((len(TEMPERATURES_K), len(WSGG_PATH_LENGTHS_M)))
    for t_index, temperature in enumerate(TEMPERATURES_K):
        nu, kappa_cm = h2o_absorption_coefficient_cm(
            WAVENUMBER_MIN_CM,
            WAVENUMBER_MAX_CM,
            WAVENUMBER_STEP_CM,
            temperature,
            WSGG_FIXED_MOLE_FRACTION,
            table_name,
        )
        kappa_m = kappa_cm * 100.0
        for p_index, path_length in enumerate(WSGG_PATH_LENGTHS_M):
            emissivity[t_index, p_index] = total_emissivity_from_spectrum(
                nu, kappa_m, float(path_length), temperature
            )

    fit = fit_polynomial_wsgg(
        np.array(TEMPERATURES_K),
        WSGG_PATH_LENGTHS_M,
        emissivity,
        gray_gas_count=WSGG_GRAY_GAS_COUNT,
        polynomial_degree=WSGG_POLYNOMIAL_DEGREE,
    )
    quality_table = pd.DataFrame(
        [
            {
                "gray_gas_count": WSGG_GRAY_GAS_COUNT,
                "polynomial_degree": WSGG_POLYNOMIAL_DEGREE,
                "mean_abs_error": fit.mean_abs_error,
                "max_abs_error": fit.max_abs_error,
                "rms_error": fit.rms_error,
                "optimizer_success": fit.optimizer_success,
            }
        ]
    )
    return fit, quality_table


def _plot_parity(grid_table: pd.DataFrame) -> None:
    fig, axis = plt.subplots(figsize=(5.5, 5), constrained_layout=True)
    axis.loglog(
        grid_table["published_kappa_planck_m-1"],
        grid_table["own_kappa_planck_m-1"],
        "o",
        alpha=0.7,
    )
    lo = min(
        grid_table["published_kappa_planck_m-1"].min(), grid_table["own_kappa_planck_m-1"].min()
    )
    hi = max(
        grid_table["published_kappa_planck_m-1"].max(), grid_table["own_kappa_planck_m-1"].max()
    )
    axis.loglog([lo, hi], [lo, hi], color="black", linewidth=1, label="y = x")
    axis.set_xlabel("published kappa_planck [m^-1] (Singh & Hostikka)")
    axis.set_ylabel("own HITRAN-derived kappa_planck [m^-1]")
    axis.set_title("Own vs. published H2O Planck-mean absorption")
    axis.legend()
    fig.savefig(OUTPUT_DIR / "figures" / "own_vs_published_parity.png", dpi=180)
    plt.close(fig)


def _plot_kappa_curves(grid_table: pd.DataFrame) -> None:
    fig, axis = plt.subplots(figsize=(6.5, 4.5), constrained_layout=True)
    for mole_fraction in sorted(grid_table["mole_fraction_h2o"].unique()):
        subset = grid_table[grid_table["mole_fraction_h2o"] == mole_fraction].sort_values(
            "temperature_k"
        )
        axis.semilogy(
            subset["temperature_k"],
            subset["own_kappa_planck_m-1"],
            "o-",
            label=f"own X={mole_fraction:.2f}",
        )
        axis.semilogy(
            subset["temperature_k"],
            subset["published_kappa_planck_m-1"],
            "--",
            color=axis.lines[-1].get_color(),
            alpha=0.6,
        )
    axis.set_xlabel("temperature [K]")
    axis.set_ylabel("kappa_planck [m^-1]")
    axis.set_title("Own (solid+markers) vs. published (dashed) - by mole fraction")
    axis.legend(fontsize=7, ncol=2)
    fig.savefig(OUTPUT_DIR / "figures" / "own_vs_published_by_temperature.png", dpi=180)
    plt.close(fig)


def _write_report(grid_table: pd.DataFrame, own_a: float, own_b: float, wsgg_fit) -> None:
    source = SOURCES["singh_hostikka_2026"]
    mean_error = grid_table["relative_error_percent"].mean()
    mean_abs_error = grid_table["relative_error_percent"].abs().mean()
    worst_row = grid_table.loc[grid_table["relative_error_percent"].abs().idxmax()]
    best_row = grid_table.loc[grid_table["relative_error_percent"].abs().idxmin()]
    temperature_trend_corr = grid_table["temperature_k"].corr(grid_table["relative_error_percent"])
    trend_word = (
        "grows"
        if temperature_trend_corr > 0.1
        else ("shrinks" if temperature_trend_corr < -0.1 else "does not clearly trend")
    )
    sign_word = "over-predicts" if mean_error > 0 else "under-predicts"

    if mean_error > 0 and temperature_trend_corr > 0.1:
        dominance_explanation = f"""Boundary 2 (range truncation) dominates over boundary 1 (missing hot lines) across this
entire grid, and the size of that dominance **grows** with temperature rather than
shrinking. The mechanism is Wien's law: as T rises, the blackbody weighting shifts toward
higher wavenumber, moving progressively more of the "true" (published, full-range) average
into the near-IR combination/overtone bands above {WAVENUMBER_MAX_CM:.0f} cm^-1 that this
script excludes entirely. Those excluded bands absorb more weakly than the two strong bands
this script keeps, so the published average is increasingly pulled down by them as T rises,
while this script's average - concentrated on only the strong bands - is not. Boundary 1
(HITRAN's missing hot lines) is real but evidently smaller than this effect across this
grid; it would show up as the over-prediction *shrinking* at high T, which is not what the
data below shows."""
    elif mean_error < 0 and temperature_trend_corr < -0.1:
        dominance_explanation = """Boundary 1 (HITRAN's missing hot lines, absent from the standard database but present in
HITEMP) dominates over boundary 2 (range truncation) across this grid, worsening at higher
temperature as expected - more hot-line absorption is missing at higher T, and that missing
absorption is not compensated by the range-truncation effect pulling the other way."""
    else:
        dominance_explanation = """Neither boundary cleanly dominates across the whole grid - the sign and/or the
temperature-trend of the disagreement are not consistent enough to attribute to one
mechanism over the other from this grid alone."""

    report = f"""# Project 1 Extension: Own HITRAN LBL Fit vs. the Published Correlation

This is an independently computed result, not a lookup of published numbers. It fetches
real H2O line-by-line data from HITRAN via HAPI, computes a Voigt-profile absorption
coefficient, and fits both a power-law Planck-mean correlation and a multi-gray-gas WSGG
model from scratch - then checks both against:

{source.citation}

DOI: {source.url}

## Disclosed Boundaries (read before trusting the numbers)

1. **HITRAN, not HITEMP.** HAPI's interactive fetch only reaches the standard HITRAN
   database. Singh & Hostikka's correlation was built from HITEMP2010, which includes many
   weak hot lines HITRAN omits. HITEMP is distributed as large static archive files
   impractical to fetch in this environment. This should make the own fit
   **under-predict**, worsening at higher T.
2. **Bounded wavenumber range.** {WAVENUMBER_MIN_CM:.0f}-{WAVENUMBER_MAX_CM:.0f} cm^-1
   (H2O's pure-rotational band and 6.3 um fundamental) rather than the paper's full
   ~150-6500 cm^-1 coverage, for tractability. Concentrating the Planck-weighted average on
   only the two strongest-absorbing bands (instead of the paper's much wider range, most of
   which absorbs more weakly) should make the own fit **over-predict**.

These two boundaries pull in *opposite* directions - which one dominates is an empirical
question, answered below by the actual grid, not assumed going in.

## Own vs. Published Planck-Mean Absorption

The own fit **{sign_word}** on average (mean signed relative error: {mean_error:+.1f}%),
and that error **{trend_word}** with temperature (correlation of error vs. T:
{temperature_trend_corr:+.2f}).

{dominance_explanation}

Mean absolute relative error: {mean_abs_error:.1f}%. Worst case: T={worst_row['temperature_k']:.0f} K,
X_H2O={worst_row['mole_fraction_h2o']:.2f}, error {worst_row['relative_error_percent']:+.1f}%.
Best case: T={best_row['temperature_k']:.0f} K, X_H2O={best_row['mole_fraction_h2o']:.2f},
error {best_row['relative_error_percent']:+.1f}%.

Full grid in `tables/own_vs_published_planck_mean.csv`; parity plot in
`figures/own_vs_published_parity.png`; per-mole-fraction curves in
`figures/own_vs_published_by_temperature.png`.

## Own Power-Law Fit

Fitting `kappa_planck = X_H2O * A * T^B` (same functional form as the published
correlation) to the own-computed grid:

| | A | B |
| --- | ---: | ---: |
| Published (Singh & Hostikka) | 3.8821e6 | -1.9811 |
| Own (HITRAN-derived) | {own_a:.4g} | {own_b:.4f} |

The exponent B is the more physically informative comparison: it describes how fast
Planck-mean absorption falls off with temperature, and is far less sensitive to the missing-
line-strength boundaries above than the prefactor A is.

## Own WSGG Fit

A {WSGG_GRAY_GAS_COUNT}-gray-gas WSGG model (polynomial degree {WSGG_POLYNOMIAL_DEGREE})
fit via this repository's own `fitting.fit_polynomial_wsgg` to the own-computed total-
emissivity grid (fixed X_H2O={WSGG_FIXED_MOLE_FRACTION}, path lengths
{WSGG_PATH_LENGTHS_M.min():.3f}-{WSGG_PATH_LENGTHS_M.max():.2f} m):

- Mean absolute error: {wsgg_fit.mean_abs_error:.4f}
- Max absolute error: {wsgg_fit.max_abs_error:.4f}
- Optimizer converged: {wsgg_fit.optimizer_success}

Coefficients in `tables/own_wsgg_model_coefficients.csv`; fit-quality summary in
`tables/own_wsgg_fit_quality.csv`. This is the WSGG toolkit (`wsgg.py`/`fitting.py`/`io.py`)
that was previously held ready pending a real target emissivity table - this own-computed
LBL grid is that table.

## Interpretation

This is genuinely independent work: real spectroscopic data, in, fitted coefficients, out.
It is not expected to match the published correlation closely - the disclosed boundaries
above are real, and this run's actual sign and temperature-trend of disagreement (reported
above, not assumed) says which one currently dominates. Closing the gap for real would mean
fetching HITEMP instead of HITRAN and covering the paper's full spectral range instead of
the two strongest bands - both a larger-scope step this repository documents but does not
claim to have done.
"""
    write_report(OUTPUT_DIR, "project1_own_hitran_fit_report.md", report)


if __name__ == "__main__":
    main()
