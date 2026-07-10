import numpy as np
import pytest

from thermal_radiation_modeling.lbl import (
    planck_mean_absorption,
    planck_wavenumber_weight,
    total_emissivity_from_spectrum,
)


def test_planck_weight_is_positive_for_positive_wavenumber() -> None:
    eta = np.linspace(100.0, 3000.0, 50)
    weight = planck_wavenumber_weight(eta, 1200.0)
    assert np.all(weight > 0.0)


def test_planck_mean_constant_spectrum_returns_constant() -> None:
    eta = np.linspace(100.0, 3000.0, 100)
    kappa = np.full_like(eta, 2.5)
    assert np.isclose(planck_mean_absorption(eta, kappa, 1000.0), 2.5)


def test_total_emissivity_constant_spectrum_matches_gray_expression() -> None:
    eta = np.linspace(100.0, 3000.0, 100)
    kappa = np.full_like(eta, 1.7)
    path = 0.4
    expected = 1.0 - np.exp(-1.7 * path)
    assert np.isclose(total_emissivity_from_spectrum(eta, kappa, path, 1000.0), expected)


def test_planck_wavenumber_weight_rejects_non_positive_temperature() -> None:
    eta = np.linspace(100.0, 3000.0, 50)
    with pytest.raises(ValueError, match="positive"):
        planck_wavenumber_weight(eta, 0.0)


def test_planck_mean_absorption_rejects_shape_mismatch() -> None:
    eta = np.linspace(100.0, 3000.0, 50)
    with pytest.raises(ValueError, match="same shape"):
        planck_mean_absorption(eta, np.zeros(49), 1000.0)


def test_total_emissivity_from_spectrum_rejects_negative_path_length() -> None:
    eta = np.linspace(100.0, 3000.0, 50)
    kappa = np.full_like(eta, 1.0)
    with pytest.raises(ValueError, match="non-negative"):
        total_emissivity_from_spectrum(eta, kappa, -0.1, 1000.0)


def test_total_emissivity_from_spectrum_rejects_shape_mismatch() -> None:
    eta = np.linspace(100.0, 3000.0, 50)
    with pytest.raises(ValueError, match="same shape"):
        total_emissivity_from_spectrum(eta, np.zeros(49), 0.4, 1000.0)
