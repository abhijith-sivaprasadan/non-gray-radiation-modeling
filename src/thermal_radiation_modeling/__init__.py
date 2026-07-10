"""Numerical helpers for a non-gray thermal-radiation portfolio."""

from thermal_radiation_modeling.dom1d import (
    DOMResult,
    solve_pure_absorption_dom,
    solve_spectral_pure_absorption_dom,
    solve_wsgg_dom,
)
from thermal_radiation_modeling.fitting import WSGGFitResult, fit_polynomial_wsgg
from thermal_radiation_modeling.wsgg import WSGGModel, superposed_emissivity

__all__ = [
    "DOMResult",
    "WSGGModel",
    "WSGGFitResult",
    "fit_polynomial_wsgg",
    "solve_pure_absorption_dom",
    "solve_spectral_pure_absorption_dom",
    "solve_wsgg_dom",
    "superposed_emissivity",
]
