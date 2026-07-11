"""Own HITRAN line-by-line H2O calculation, independent of published_data.py's lookup.

published_data.h2o_planck_mean_singh_hostikka_2026 encodes Singh & Hostikka's *published*
Planck-mean correlation - a real number, but their number. This module computes an
independent one: real H2O line-by-line data fetched from HITRAN via HAPI, a Voigt-profile
absorption coefficient, and a Planck-mean/total-emissivity reduction (reusing lbl.py) that
this repository's own fitting.py can then fit a WSGG model to.

Two disclosed boundaries versus the reference paper, documented in full in
docs/derivation_note.md - they pull in *opposite* directions, not the same one:

1. HAPI's fetch() only reaches the interactive *HITRAN* database, not *HITEMP*. Singh &
   Hostikka's correlation was built from HITEMP2010, which includes many weak hot lines that
   HITRAN omits. HITEMP is distributed as large static archive files impractical to fetch
   here. This should make the own fit *under*-predict absorption, worse at higher T.
2. The wavenumber range used is a bounded subset (H2O's two strongest IR bands - the pure
   rotational band and the 6.3 um fundamental) rather than the paper's full ~150-6500 cm^-1
   coverage, for tractability. Concentrating the Planck-weighted average on only the
   strongest-absorbing bands (instead of the paper's much wider range, most of which
   absorbs more weakly) should make the own fit *over*-predict absorption.

Which effect dominates is an empirical question this module's own results answer, not
something assumed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from thermal_radiation_modeling.hapi_adapter import require_hapi
from thermal_radiation_modeling.lbl import planck_mean_absorption, total_emissivity_from_spectrum

CM_TO_M = 100.0  # multiply a cm^-1 absorption coefficient by this to get m^-1
H2O_MOLECULE_ID = 1
H2O_ISOTOPOLOGUE_ID = 1


@dataclass(frozen=True)
class OwnSpectralPoint:
    """One (T, X_H2O) result from the own LBL pipeline."""

    temperature_k: float
    mole_fraction_h2o: float
    planck_mean_kappa_m: float
    total_emissivity: float


def fetch_h2o_lines(
    wavenumber_min_cm: float,
    wavenumber_max_cm: float,
    data_dir: str | Path,
    table_name: str = "H2O_own_fit",
) -> str:
    """Fetch (or reuse a local cache of) real H2O line-by-line data from HITRAN via HAPI."""

    hapi = require_hapi()
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    hapi.db_begin(str(data_dir))
    header_path = data_dir / f"{table_name}.header"
    if not header_path.exists():
        hapi.fetch(
            table_name, H2O_MOLECULE_ID, H2O_ISOTOPOLOGUE_ID, wavenumber_min_cm, wavenumber_max_cm
        )
    return table_name


def h2o_absorption_coefficient_cm(
    wavenumber_min_cm: float,
    wavenumber_max_cm: float,
    wavenumber_step_cm: float,
    temperature_k: float,
    mole_fraction_h2o: float,
    table_name: str,
    total_pressure_atm: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a real Voigt-profile H2O absorption coefficient spectrum, in cm^-1.

    Self- and air-broadening are mixed according to ``mole_fraction_h2o`` (HITRAN's
    ``Diluent`` mechanism), and the third element of ``Components`` overrides the natural
    terrestrial isotopic abundance with the actual mole fraction, so the returned coefficient
    already reflects the real absorber number density at ``total_pressure_atm``.
    """

    if not 0.0 < mole_fraction_h2o <= 1.0:
        raise ValueError("mole_fraction_h2o must be in (0, 1]")

    hapi = require_hapi()
    nu, coef = hapi.absorptionCoefficient_Voigt(
        Components=[(H2O_MOLECULE_ID, H2O_ISOTOPOLOGUE_ID, mole_fraction_h2o)],
        SourceTables=table_name,
        Environment={"T": temperature_k, "p": total_pressure_atm},
        WavenumberRange=(wavenumber_min_cm, wavenumber_max_cm),
        WavenumberStep=wavenumber_step_cm,
        HITRAN_units=False,
        Diluent={"self": mole_fraction_h2o, "air": max(0.0, 1.0 - mole_fraction_h2o)},
    )
    return np.asarray(nu, dtype=float), np.asarray(coef, dtype=float)


def own_planck_mean_and_emissivity(
    wavenumber_min_cm: float,
    wavenumber_max_cm: float,
    wavenumber_step_cm: float,
    temperature_k: float,
    mole_fraction_h2o: float,
    table_name: str,
    path_length_m: float = 1.0,
    total_pressure_atm: float = 1.0,
) -> OwnSpectralPoint:
    """Compute one real (T, X_H2O) Planck-mean kappa and total-emissivity point."""

    nu, kappa_cm = h2o_absorption_coefficient_cm(
        wavenumber_min_cm,
        wavenumber_max_cm,
        wavenumber_step_cm,
        temperature_k,
        mole_fraction_h2o,
        table_name,
        total_pressure_atm,
    )
    kappa_m = kappa_cm * CM_TO_M
    planck_mean = planck_mean_absorption(nu, kappa_m, temperature_k)
    emissivity = total_emissivity_from_spectrum(nu, kappa_m, path_length_m, temperature_k)
    return OwnSpectralPoint(temperature_k, mole_fraction_h2o, planck_mean, emissivity)


def fit_own_power_law(
    temperatures_k: np.ndarray, mole_fractions: np.ndarray, kappa_planck_m: np.ndarray
) -> tuple[float, float]:
    """Fit kappa_planck = X_H2O * A * T^B to a (flattened) own-computed grid.

    Mirrors the functional form of Singh & Hostikka's published correlation
    (published_data.h2o_planck_mean_singh_hostikka_2026), so the fitted (A, B) are directly
    comparable to their published (3.8821e6, -1.9811).
    """

    valid = kappa_planck_m > 0.0
    log_kappa_over_x = np.log(kappa_planck_m[valid] / mole_fractions[valid])
    log_t = np.log(temperatures_k[valid])
    slope, intercept = np.polyfit(log_t, log_kappa_over_x, 1)
    exponent_b = float(slope)
    coefficient_a = float(np.exp(intercept))
    return coefficient_a, exponent_b
