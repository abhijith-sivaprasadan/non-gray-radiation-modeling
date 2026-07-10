"""Weighted-sum-of-gray-gases model utilities."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Sequence

import numpy as np

from thermal_radiation_modeling.constants import DEFAULT_WSGG_REFERENCE_TEMPERATURE


@dataclass(frozen=True)
class WSGGModel:
    """A WSGG model with polynomial temperature-dependent weights.

    ``absorption_coefficients`` and rows of ``weight_coefficients`` must align. Include a
    transparent gas explicitly by giving it absorption coefficient zero.
    """

    absorption_coefficients: np.ndarray
    weight_coefficients: np.ndarray
    reference_temperature_k: float = DEFAULT_WSGG_REFERENCE_TEMPERATURE
    clip_negative_weights: bool = True
    normalize_weights: bool = True

    def __post_init__(self) -> None:
        kappa = np.asarray(self.absorption_coefficients, dtype=float)
        coeffs = np.asarray(self.weight_coefficients, dtype=float)
        if kappa.ndim != 1:
            raise ValueError("absorption_coefficients must be a one-dimensional array")
        if coeffs.ndim != 2:
            raise ValueError("weight_coefficients must be a two-dimensional array")
        if coeffs.shape[0] != kappa.size:
            raise ValueError("one weight-coefficient row is required per gas")
        if self.reference_temperature_k <= 0:
            raise ValueError("reference_temperature_k must be positive")
        if np.any(kappa < 0):
            raise ValueError("absorption coefficients must be non-negative")

        object.__setattr__(self, "absorption_coefficients", kappa)
        object.__setattr__(self, "weight_coefficients", coeffs)

    @property
    def gas_count(self) -> int:
        return int(self.absorption_coefficients.size)

    def raw_weights(self, temperature_k: float | np.ndarray) -> np.ndarray:
        """Evaluate polynomial weights without clipping or normalization."""

        temperature = np.asarray(temperature_k, dtype=float)
        if np.any(temperature <= 0):
            raise ValueError("temperature_k must be positive")

        reduced_temperature = temperature / self.reference_temperature_k
        powers = np.stack(
            [reduced_temperature**order for order in range(self.weight_coefficients.shape[1])],
            axis=-1,
        )
        return powers @ self.weight_coefficients.T

    def weights(self, temperature_k: float | np.ndarray) -> np.ndarray:
        """Evaluate non-negative, normalized WSGG weights."""

        weights = self.raw_weights(temperature_k)
        if self.clip_negative_weights:
            weights = np.maximum(weights, 0.0)
        if self.normalize_weights:
            totals = np.sum(weights, axis=-1, keepdims=True)
            if np.any(totals <= 0):
                raise ValueError("WSGG weights sum to zero; cannot normalize")
            weights = weights / totals
        return weights

    def emissivity(
        self, temperature_k: float | np.ndarray, path_length: float | np.ndarray
    ) -> np.ndarray:
        """Evaluate total emissivity for a path length matching the coefficient units."""

        path = np.asarray(path_length, dtype=float)
        if np.any(path < 0):
            raise ValueError("path_length must be non-negative")

        weights = self.weights(temperature_k)
        kappa = self.absorption_coefficients.reshape((1,) * (weights.ndim - 1) + (-1,))
        path_expanded = np.expand_dims(path, axis=-1)
        gray_emissivity = 1.0 - np.exp(-kappa * path_expanded)
        return np.sum(weights * gray_emissivity, axis=-1)


def superposed_emissivity(
    models: Sequence[WSGGModel],
    temperature_k: float | np.ndarray,
    pressure_paths: Sequence[float],
) -> np.ndarray:
    """Evaluate a statistically uncorrelated superposition of species WSGG models.

    ``pressure_paths`` must already contain each species' pressure-path quantity in units
    compatible with that species model's absorption coefficients.
    """

    if len(models) != len(pressure_paths):
        raise ValueError("models and pressure_paths must have the same length")
    if not models:
        raise ValueError("at least one model is required")

    species_weights = [model.weights(temperature_k) for model in models]
    species_kappa = [model.absorption_coefficients for model in models]
    paths = np.asarray(pressure_paths, dtype=float)
    if np.any(paths < 0):
        raise ValueError("pressure paths must be non-negative")

    result = np.zeros(np.shape(np.asarray(temperature_k, dtype=float)), dtype=float)
    index_ranges = [range(model.gas_count) for model in models]

    for gas_indices in product(*index_ranges):
        combo_weight = 1.0
        combo_optical_depth = 0.0
        for species_index, gas_index in enumerate(gas_indices):
            combo_weight = combo_weight * species_weights[species_index][..., gas_index]
            combo_optical_depth += species_kappa[species_index][gas_index] * paths[species_index]
        result = result + combo_weight * (1.0 - np.exp(-combo_optical_depth))

    return result
