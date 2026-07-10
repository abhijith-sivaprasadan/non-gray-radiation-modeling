"""WSGG coefficient fitting utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares

from thermal_radiation_modeling.constants import DEFAULT_WSGG_REFERENCE_TEMPERATURE
from thermal_radiation_modeling.wsgg import WSGGModel


@dataclass(frozen=True)
class WSGGFitResult:
    """Result of a WSGG fit against an emissivity grid."""

    model: WSGGModel
    temperatures_k: np.ndarray
    pressure_paths: np.ndarray
    target_emissivity: np.ndarray
    fitted_emissivity: np.ndarray
    residuals: np.ndarray
    mean_abs_error: float
    max_abs_error: float
    rms_error: float
    optimizer_cost: float
    optimizer_success: bool
    optimizer_message: str


def fit_polynomial_wsgg(
    temperatures_k: np.ndarray,
    pressure_paths: np.ndarray,
    emissivity: np.ndarray,
    gray_gas_count: int = 4,
    polynomial_degree: int = 5,
    reference_temperature_k: float = DEFAULT_WSGG_REFERENCE_TEMPERATURE,
    max_nfev: int = 5000,
) -> WSGGFitResult:
    """Fit a transparent-gas + gray-gas WSGG model by penalized least squares.

    The transparent-gas polynomial coefficients are parameterized as the complement of the
    gray-gas coefficients, which enforces ``sum_j a_j(T) = 1`` for every temperature. A
    penalty discourages negative polynomial weights on the fitted temperature grid.
    """

    temperatures = np.asarray(temperatures_k, dtype=float)
    paths = np.asarray(pressure_paths, dtype=float)
    target = np.asarray(emissivity, dtype=float)
    if target.shape != (temperatures.size, paths.size):
        raise ValueError("emissivity must have shape (n_temperatures, n_pressure_paths)")
    if np.any((target < 0.0) | (target > 1.0)):
        raise ValueError("emissivity values must lie between 0 and 1")
    if gray_gas_count < 1:
        raise ValueError("gray_gas_count must be positive")
    if polynomial_degree < 0:
        raise ValueError("polynomial_degree must be non-negative")

    initial_kappas = np.geomspace(0.08, 120.0, gray_gas_count)
    initial_gray_weights = np.linspace(0.24, 0.10, gray_gas_count)
    initial_gray_weights *= 0.72 / np.sum(initial_gray_weights)

    x0 = np.concatenate(
        [
            np.log(initial_kappas),
            _initial_weight_coefficients(initial_gray_weights, gray_gas_count, polynomial_degree),
        ]
    )

    lower = np.concatenate(
        [
            np.full(gray_gas_count, np.log(1e-4)),
            np.full(gray_gas_count * (polynomial_degree + 1), -4.0),
        ]
    )
    upper = np.concatenate(
        [
            np.full(gray_gas_count, np.log(1e4)),
            np.full(gray_gas_count * (polynomial_degree + 1), 4.0),
        ]
    )

    def residual_vector(params: np.ndarray) -> np.ndarray:
        fitted = _predict_emissivity(
            params,
            temperatures,
            paths,
            gray_gas_count,
            polynomial_degree,
            reference_temperature_k,
        )
        coeffs = _weight_coefficients(params, gray_gas_count, polynomial_degree)
        weights = _evaluate_weights(coeffs, temperatures, reference_temperature_k)
        negative_weight_penalty = 8.0 * np.minimum(weights, 0.0).ravel()
        coefficient_penalty = 1e-4 * params[gray_gas_count:]
        return np.concatenate(
            [(fitted - target).ravel(), negative_weight_penalty, coefficient_penalty]
        )

    result = least_squares(
        residual_vector,
        x0,
        bounds=(lower, upper),
        x_scale="jac",
        ftol=1e-10,
        xtol=1e-10,
        gtol=1e-10,
        max_nfev=max_nfev,
    )

    model = _model_from_params(
        result.x,
        gray_gas_count,
        polynomial_degree,
        reference_temperature_k,
    )
    fitted = model.emissivity(temperatures[:, None], paths[None, :])
    residuals = fitted - target
    return WSGGFitResult(
        model=model,
        temperatures_k=temperatures,
        pressure_paths=paths,
        target_emissivity=target,
        fitted_emissivity=fitted,
        residuals=residuals,
        mean_abs_error=float(np.mean(np.abs(residuals))),
        max_abs_error=float(np.max(np.abs(residuals))),
        rms_error=float(np.sqrt(np.mean(residuals**2))),
        optimizer_cost=float(result.cost),
        optimizer_success=bool(result.success),
        optimizer_message=str(result.message),
    )


def _initial_weight_coefficients(
    initial_gray_weights: np.ndarray,
    gray_gas_count: int,
    polynomial_degree: int,
) -> np.ndarray:
    coefficients = np.zeros((gray_gas_count, polynomial_degree + 1), dtype=float)
    coefficients[:, 0] = initial_gray_weights
    return coefficients.ravel()


def _weight_coefficients(
    params: np.ndarray,
    gray_gas_count: int,
    polynomial_degree: int,
) -> np.ndarray:
    gray_coeffs = params[gray_gas_count:].reshape(gray_gas_count, polynomial_degree + 1)
    transparent_coeffs = np.zeros(polynomial_degree + 1, dtype=float)
    transparent_coeffs[0] = 1.0
    transparent_coeffs -= np.sum(gray_coeffs, axis=0)
    return np.vstack([transparent_coeffs, gray_coeffs])


def _evaluate_weights(
    coefficients: np.ndarray,
    temperatures_k: np.ndarray,
    reference_temperature_k: float,
) -> np.ndarray:
    reduced = np.asarray(temperatures_k, dtype=float) / reference_temperature_k
    powers = np.stack([reduced**order for order in range(coefficients.shape[1])], axis=-1)
    return powers @ coefficients.T


def _predict_emissivity(
    params: np.ndarray,
    temperatures_k: np.ndarray,
    pressure_paths: np.ndarray,
    gray_gas_count: int,
    polynomial_degree: int,
    reference_temperature_k: float,
) -> np.ndarray:
    kappas = np.concatenate([[0.0], np.exp(params[:gray_gas_count])])
    coeffs = _weight_coefficients(params, gray_gas_count, polynomial_degree)
    weights = _evaluate_weights(coeffs, temperatures_k, reference_temperature_k)
    gray_emissivity = 1.0 - np.exp(-pressure_paths[None, :, None] * kappas[None, None, :])
    return np.sum(weights[:, None, :] * gray_emissivity, axis=-1)


def _model_from_params(
    params: np.ndarray,
    gray_gas_count: int,
    polynomial_degree: int,
    reference_temperature_k: float,
) -> WSGGModel:
    kappas = np.concatenate([[0.0], np.exp(params[:gray_gas_count])])
    coeffs = _weight_coefficients(params, gray_gas_count, polynomial_degree)
    order = np.argsort(kappas)
    return WSGGModel(
        absorption_coefficients=kappas[order],
        weight_coefficients=coeffs[order],
        reference_temperature_k=reference_temperature_k,
        clip_negative_weights=True,
        normalize_weights=True,
    )
