"""Planck-weighted line-by-line style spectral integration helpers."""

from __future__ import annotations

import numpy as np

from thermal_radiation_modeling.constants import SECOND_RADIATION_CONSTANT_CM_K


def planck_wavenumber_weight(wavenumber_cm: np.ndarray, temperature_k: float) -> np.ndarray:
    """Return the relative Planck spectral weight per wavenumber.

    The multiplicative dimensional constant cancels in Planck-weighted ratios, so this
    function returns only ``eta^3 / (exp(c2 eta / T) - 1)`` for wavenumber ``eta`` in cm^-1.
    """

    eta = np.asarray(wavenumber_cm, dtype=float)
    if temperature_k <= 0:
        raise ValueError("temperature_k must be positive")

    exponent = SECOND_RADIATION_CONSTANT_CM_K * eta / temperature_k
    denominator = np.expm1(np.clip(exponent, 0.0, 700.0))
    weight = np.divide(eta**3, denominator, out=np.zeros_like(eta), where=denominator > 0)
    return np.where(eta > 0, weight, 0.0)


def planck_mean_absorption(
    wavenumber_cm: np.ndarray,
    absorption_coefficient_m: np.ndarray,
    temperature_k: float,
) -> float:
    """Compute a Planck-mean absorption coefficient from spectral data."""

    eta = np.asarray(wavenumber_cm, dtype=float)
    kappa = np.asarray(absorption_coefficient_m, dtype=float)
    if eta.shape != kappa.shape:
        raise ValueError("wavenumber_cm and absorption_coefficient_m must have the same shape")

    weight = planck_wavenumber_weight(eta, temperature_k)
    denominator = np.trapezoid(weight, eta)
    if denominator <= 0:
        raise ValueError("Planck weight integral must be positive")
    return float(np.trapezoid(kappa * weight, eta) / denominator)


def total_emissivity_from_spectrum(
    wavenumber_cm: np.ndarray,
    absorption_coefficient_m: np.ndarray,
    path_length_m: float,
    temperature_k: float,
) -> float:
    """Compute total emissivity from a spectral absorption coefficient.

    ``absorption_coefficient_m`` is assumed to be in m^-1 and ``path_length_m`` in m.
    """

    if path_length_m < 0:
        raise ValueError("path_length_m must be non-negative")

    eta = np.asarray(wavenumber_cm, dtype=float)
    kappa = np.asarray(absorption_coefficient_m, dtype=float)
    if eta.shape != kappa.shape:
        raise ValueError("wavenumber_cm and absorption_coefficient_m must have the same shape")

    weight = planck_wavenumber_weight(eta, temperature_k)
    denominator = np.trapezoid(weight, eta)
    if denominator <= 0:
        raise ValueError("Planck weight integral must be positive")

    spectral_emissivity = 1.0 - np.exp(-np.maximum(kappa, 0.0) * path_length_m)
    return float(np.trapezoid(spectral_emissivity * weight, eta) / denominator)
