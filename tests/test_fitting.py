import numpy as np
import pytest

from thermal_radiation_modeling.fitting import fit_polynomial_wsgg
from thermal_radiation_modeling.wsgg import WSGGModel


def test_fit_polynomial_wsgg_recovers_simple_gray_mixture() -> None:
    temperatures = np.linspace(700.0, 1300.0, 4)
    paths = np.logspace(-2.0, 0.5, 6)
    truth = WSGGModel(
        absorption_coefficients=np.array([0.0, 2.0]),
        weight_coefficients=np.array([[0.35], [0.65]]),
        normalize_weights=True,
    )
    emissivity = truth.emissivity(temperatures[:, None], paths[None, :])
    fit = fit_polynomial_wsgg(
        temperatures,
        paths,
        emissivity,
        gray_gas_count=1,
        polynomial_degree=0,
        max_nfev=1000,
    )
    assert fit.mean_abs_error < 1e-3
    assert fit.max_abs_error < 5e-3


def test_fit_polynomial_wsgg_rejects_mismatched_emissivity_shape() -> None:
    with pytest.raises(ValueError, match="shape"):
        fit_polynomial_wsgg(
            np.linspace(700.0, 1300.0, 4),
            np.logspace(-2.0, 0.5, 6),
            np.zeros((3, 6)),
        )


def test_fit_polynomial_wsgg_rejects_out_of_range_emissivity() -> None:
    temperatures = np.linspace(700.0, 1300.0, 4)
    paths = np.logspace(-2.0, 0.5, 6)
    with pytest.raises(ValueError, match="between 0 and 1"):
        fit_polynomial_wsgg(temperatures, paths, np.full((4, 6), 1.5))


def test_fit_polynomial_wsgg_rejects_non_positive_gray_gas_count() -> None:
    temperatures = np.linspace(700.0, 1300.0, 4)
    paths = np.logspace(-2.0, 0.5, 6)
    with pytest.raises(ValueError, match="gray_gas_count"):
        fit_polynomial_wsgg(temperatures, paths, np.full((4, 6), 0.5), gray_gas_count=0)


def test_fit_polynomial_wsgg_rejects_negative_polynomial_degree() -> None:
    temperatures = np.linspace(700.0, 1300.0, 4)
    paths = np.logspace(-2.0, 0.5, 6)
    with pytest.raises(ValueError, match="polynomial_degree"):
        fit_polynomial_wsgg(temperatures, paths, np.full((4, 6), 0.5), polynomial_degree=-1)
