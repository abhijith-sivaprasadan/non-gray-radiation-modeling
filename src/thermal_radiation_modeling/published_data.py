"""Published-data fixtures extracted from the supplied papers and web sources."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SourceRef:
    key: str
    citation: str
    url: str
    # Bare filename of a locally-kept reference PDF, not a path. These PDFs are the author's
    # own copies of the cited papers and are not tracked in this repository.
    local_file: str | None = None


SOURCES = {
    "singh_hostikka_2026": SourceRef(
        key="singh_hostikka_2026",
        citation=(
            "K. Singh and S. Hostikka, Non-gray radiation model optimized for hydrogen "
            "flames, Applied Thermal Engineering 294 (2026) 130593."
        ),
        url="https://doi.org/10.1016/j.applthermaleng.2026.130593",
        local_file="1-s2.0-S1359431126009014-main.pdf",
    ),
    "rashidzadeh_2026_methanol": SourceRef(
        key="rashidzadeh_2026_methanol",
        citation=(
            "S. Rashidzadeh et al., Non-gray radiation modeling of methanol pool fires "
            "using the RC-FSK method in FDS, Fire Safety Journal 160 (2026) 104606."
        ),
        url="https://doi.org/10.1016/j.firesaf.2025.104606",
        local_file="1-s2.0-S037971122500270X-main.pdf",
    ),
    "hostikka_rashidzadeh_2026": SourceRef(
        key="hostikka_rashidzadeh_2026",
        citation=(
            "S. Hostikka and S. Rashidzadeh, Thermal radiation - From science to "
            "engineering, Fire Safety Journal 161 (2026) 104677."
        ),
        url="https://doi.org/10.1016/j.firesaf.2026.104677",
        local_file="1-s2.0-S0379711226000457-main.pdf",
    ),
    "johansson_2017": SourceRef(
        key="johansson_2017",
        citation=(
            "R. Johansson, Efficient treatment of non-grey radiative properties of "
            "particles and gases in modelling of radiative heat transfer in combustion "
            "environments, International Journal of Heat and Mass Transfer 108 (2017) "
            "519-528."
        ),
        url="https://doi.org/10.1016/j.ijheatmasstransfer.2016.12.042",
        local_file="johansson2017.pdf",
    ),
    "aalto_therad": SourceRef(
        key="aalto_therad",
        citation=(
            "Aalto Fire Safety Engineering, THERAD: Novel measurement and sensing "
            "technologies for thermal radiation of unwanted fires."
        ),
        url="https://blogs.aalto.fi/fire/therad/",
    ),
    "firemodels_fds": SourceRef(
        key="firemodels_fds",
        citation="firemodels/fds GitHub repository, Fire Dynamics Simulator.",
        url="https://github.com/firemodels/fds",
    ),
}


def h2o_planck_mean_singh_hostikka_2026(
    temperature_k: float | np.ndarray,
    mole_fraction_h2o: float | np.ndarray,
) -> np.ndarray:
    """Published H2O Planck-mean absorption fit from Singh & Hostikka Eq. (21).

    The paper states this fit was derived from HITEMP-2010 spectra for pure H2O
    and remains within 1 percent of exact Planck means at lower partial pressures.
    """

    temperature = np.asarray(temperature_k, dtype=float)
    mole_fraction = np.asarray(mole_fraction_h2o, dtype=float)
    if np.any(temperature <= 0):
        raise ValueError("temperature_k must be positive")
    if np.any(mole_fraction < 0):
        raise ValueError("mole_fraction_h2o must be non-negative")
    return mole_fraction * 3.8821e6 * temperature**-1.9811


def singh_radial_case_fields(x_m: np.ndarray, y_m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return T and X_H2O fields for the Singh & Hostikka radial test case."""

    x, y = np.meshgrid(np.asarray(x_m, dtype=float), np.asarray(y_m, dtype=float), indexing="xy")
    r2 = (x - 0.5) ** 2 + (y - 0.5) ** 2
    f = np.clip(1.0 - r2 / 0.5, 0.0, 1.0)
    temperature = 500.0 + (2000.0 - 500.0) * f
    mole_fraction = 0.01 + (0.30 - 0.01) * f
    return temperature, mole_fraction


def singh_axial_case_fields(x_m: np.ndarray, y_m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return T and X_H2O fields for the Singh & Hostikka axial test case."""

    x_values = np.asarray(x_m, dtype=float)
    y_values = np.asarray(y_m, dtype=float)
    lx = 2.0
    ly = 4.0
    sx = 0.5
    x, y = np.meshgrid(x_values, y_values, indexing="xy")
    f = (1.0 - y / ly) * np.exp(-(((x - lx / 2.0) / sx) ** 2))
    f = np.clip(f, 0.0, 1.0)
    temperature = 300.0 + (2000.0 - 300.0) * f
    mole_fraction = 0.01 + (0.30 - 0.01) * f
    return temperature, mole_fraction


def singh_thermodynamic_grid_table() -> list[dict[str, str | float]]:
    """Table 1 from Singh & Hostikka 2026."""

    return [
        {
            "quantity": "Mole fraction of H2O",
            "range": "0.01-0.05",
            "interval": "0.01",
        },
        {
            "quantity": "Mole fraction of H2O",
            "range": "0.05-0.25",
            "interval": "0.05",
        },
        {
            "quantity": "Mole fraction of H2O",
            "range": "0.25-1.00",
            "interval": "0.25",
        },
        {"quantity": "Temperature (K)", "range": "300-2400", "interval": "100"},
    ]


def singh_cpu_time_table() -> list[dict[str, float | int | str]]:
    """Table 2 from Singh & Hostikka 2026."""

    return [
        {"model": "RCFSK", "rte_count": 4, "overhead_1000_s": 0.34, "rte_solver_s": 14.05},
        {"model": "WSGG", "rte_count": 4, "overhead_1000_s": 1.13, "rte_solver_s": 13.61},
        {
            "model": "Planck-mean",
            "rte_count": 1,
            "overhead_1000_s": 0.10,
            "rte_solver_s": 3.41,
        },
    ]


def singh_wall_emission_error_table() -> list[dict[str, float]]:
    """Table 3 from Singh & Hostikka 2026."""

    return [
        {
            "wall_temperature_k": 500.0,
            "aed_planck_at_wall_temperature_percent": 11.7,
            "aed_planck_at_mean_temperature_percent": 10.3,
            "aef_planck_at_wall_temperature_percent": 5.34,
            "aef_planck_at_mean_temperature_percent": 5.04,
        },
        {
            "wall_temperature_k": 1000.0,
            "aed_planck_at_wall_temperature_percent": 11.3,
            "aed_planck_at_mean_temperature_percent": 12.7,
            "aef_planck_at_wall_temperature_percent": 6.01,
            "aef_planck_at_mean_temperature_percent": 5.95,
        },
        {
            "wall_temperature_k": 1400.0,
            "aed_planck_at_wall_temperature_percent": 15.0,
            "aed_planck_at_mean_temperature_percent": 15.1,
            "aef_planck_at_wall_temperature_percent": 3.01,
            "aef_planck_at_mean_temperature_percent": 3.00,
        },
    ]


def singh_published_error_summary() -> list[dict[str, float | str]]:
    """Published model-comparison metrics from Singh & Hostikka 2026 text."""

    return [
        {
            "case": "radial_source_peak_error",
            "rcfsk_4_transformed_percent": 14.0,
            "wsgg_percent": 43.0,
            "planck_mean_percent": 150.0,
            "note": "RCFSK reported below 14%; WSGG about 43%; Planck mean about 150%.",
        },
        {
            "case": "axial_wall_flux_peak_error",
            "rcfsk_4_transformed_percent": 7.0,
            "wsgg_percent": np.nan,
            "planck_mean_percent": np.nan,
            "note": "RCFSK wall net heat-flux error remains within 7%.",
        },
        {
            "case": "sandia_plume_side_wall_flux_peak_error",
            "rcfsk_4_transformed_percent": 6.0,
            "wsgg_percent": 51.0,
            "planck_mean_percent": np.nan,
            "note": "2D decoupled Sandia plume comparison against LBL benchmark.",
        },
        {
            "case": "sandia_plume_source_peak_error",
            "rcfsk_4_transformed_percent": 15.0,
            "wsgg_percent": 35.0,
            "planck_mean_percent": np.nan,
            "note": "RCFSK about 15%; WSGG around 35%.",
        },
    ]


def methanol_decoupled_metrics() -> list[dict[str, float | int | str]]:
    """Metrics extracted from Rashidzadeh et al. 2026 methanol/FDS paper."""

    return [
        {
            "model": "RadCal",
            "gray_gases": 1,
            "decoupled_time_s": 2058.0,
            "relative_time": 1.0,
            "source_total_error_percent": 34.8,
            "pool_flux_mean_error_percent": 4.2,
            "pool_flux_bias_factor": 1.073,
        },
        {
            "model": "RC-FSK",
            "gray_gases": 4,
            "decoupled_time_s": 9161.0,
            "relative_time": 4.45,
            "source_total_error_percent": 15.9,
            "pool_flux_mean_error_percent": 3.4,
            "pool_flux_bias_factor": np.nan,
        },
        {
            "model": "RC-FSK",
            "gray_gases": 6,
            "decoupled_time_s": 13520.0,
            "relative_time": 6.56,
            "source_total_error_percent": 6.4,
            "pool_flux_mean_error_percent": 2.7,
            "pool_flux_bias_factor": 1.007,
        },
    ]


def methanol_global_radiation_table() -> list[dict[str, float | str]]:
    """Table 2 from Rashidzadeh et al. 2026."""

    return [
        {
            "case": "Experimental",
            "radiant_fraction": 0.24,
            "radiant_fraction_uncertainty": 0.06,
            "radiative_heat_feedback_fraction": 0.055,
            "radiative_heat_feedback_uncertainty": 0.011,
            "emission_fraction": np.nan,
        },
        {
            "case": "RadCal",
            "radiant_fraction": 0.218,
            "radiant_fraction_uncertainty": np.nan,
            "radiative_heat_feedback_fraction": 0.042,
            "radiative_heat_feedback_uncertainty": np.nan,
            "emission_fraction": 0.258,
        },
        {
            "case": "RC-FSK",
            "radiant_fraction": 0.218,
            "radiant_fraction_uncertainty": np.nan,
            "radiative_heat_feedback_fraction": 0.054,
            "radiative_heat_feedback_uncertainty": np.nan,
            "emission_fraction": 0.337,
        },
    ]


def fds_rcfsk_implementation_facts() -> list[dict[str, str]]:
    """Implementation facts from Rashidzadeh et al. 2026 and firemodels/fds."""

    return [
        {
            "topic": "FDS role",
            "fact": (
                "RC-FSK was implemented as a subroutine within the radiation module of "
                "Fire Dynamics Simulator."
            ),
        },
        {
            "topic": "Spectral database",
            "fact": (
                "H2O, CO2 and CO k-distribution curves were generated from HITEMP 2010 "
                "spectral absorption coefficients at 0.01 cm^-1 resolution."
            ),
        },
        {
            "topic": "Line shape",
            "fact": "Lorentz broadening with a 500 cm^-1 line-wing cutoff was used.",
        },
        {
            "topic": "Lookup grid",
            "fact": (
                "Methanol paper lookup curves used nine molar fractions between 0.001 "
                "and 0.35 and temperatures from 300 K to 2000 K in 50 K steps."
            ),
        },
        {
            "topic": "FDS repository",
            "fact": (
                "The public firemodels/fds repository is the implementation target for "
                "FDS and is Fortran-heavy."
            ),
        },
    ]
