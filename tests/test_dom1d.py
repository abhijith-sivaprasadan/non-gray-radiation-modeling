import numpy as np
import pytest

from thermal_radiation_modeling.constants import STEFAN_BOLTZMANN
from thermal_radiation_modeling.dom1d import (
    solve_pure_absorption_dom,
    solve_spectral_pure_absorption_dom,
    solve_wsgg_dom,
)
from thermal_radiation_modeling.wsgg import WSGGModel


def test_isothermal_medium_has_zero_flux_and_source() -> None:
    x = np.linspace(0.0, 1.0, 20)
    temperature = np.full_like(x, 1000.0)
    result = solve_pure_absorption_dom(x, temperature, 2.0, quadrature_order=8)
    assert np.allclose(result.heat_flux, 0.0, atol=1e-8)
    assert np.allclose(result.source_term, 0.0, atol=1e-8)


def test_vacuum_between_black_walls_has_expected_flux() -> None:
    x = np.linspace(0.0, 1.0, 20)
    temperature = np.full_like(x, 500.0)
    left_wall_t = 1000.0
    right_wall_t = 500.0
    result = solve_pure_absorption_dom(
        x,
        temperature,
        0.0,
        quadrature_order=8,
        left_wall_temperature_k=left_wall_t,
        right_wall_temperature_k=right_wall_t,
    )
    expected_flux = STEFAN_BOLTZMANN * (left_wall_t**4 - right_wall_t**4)
    assert np.allclose(result.heat_flux, expected_flux)


def test_spectral_vacuum_between_black_walls_matches_total_flux() -> None:
    x = np.linspace(0.0, 1.0, 8)
    eta = np.linspace(100.0, 6000.0, 120)
    temperature = np.full_like(x, 500.0)
    kappa = np.zeros((eta.size, x.size))
    left_wall_t = 1000.0
    right_wall_t = 500.0
    result = solve_spectral_pure_absorption_dom(
        x,
        temperature,
        eta,
        kappa,
        quadrature_order=8,
        left_wall_temperature_k=left_wall_t,
        right_wall_temperature_k=right_wall_t,
    )
    expected_flux = STEFAN_BOLTZMANN * (left_wall_t**4 - right_wall_t**4)
    assert np.allclose(result.heat_flux, expected_flux, rtol=1e-3)


def _single_gray_gas_model(kappa: float) -> WSGGModel:
    # A single gray gas with a constant weight of 1 degenerates to a plain gray medium, which
    # lets solve_wsgg_dom be checked directly against solve_pure_absorption_dom.
    return WSGGModel(
        absorption_coefficients=np.array([kappa]),
        weight_coefficients=np.array([[1.0]]),
    )


def test_wsgg_dom_single_gray_gas_matches_pure_absorption() -> None:
    x = np.linspace(0.0, 1.0, 20)
    temperature = np.linspace(500.0, 1500.0, 20)
    model = _single_gray_gas_model(2.0)

    wsgg_result = solve_wsgg_dom(x, temperature, model, quadrature_order=8)
    pure_result = solve_pure_absorption_dom(x, temperature, 2.0, quadrature_order=8)

    assert np.allclose(wsgg_result.heat_flux, pure_result.heat_flux)
    assert np.allclose(wsgg_result.source_term, pure_result.source_term)


def test_wsgg_dom_pressure_scale_multiplies_gas_absorption_coefficient() -> None:
    x = np.linspace(0.0, 1.0, 20)
    temperature = np.linspace(500.0, 1500.0, 20)
    model = _single_gray_gas_model(1.0)

    scaled_result = solve_wsgg_dom(x, temperature, model, pressure_scale=3.0, quadrature_order=8)
    equivalent_pure_result = solve_pure_absorption_dom(x, temperature, 3.0, quadrature_order=8)

    assert np.allclose(scaled_result.heat_flux, equivalent_pure_result.heat_flux)


def test_wsgg_dom_particle_absorption_matches_pure_absorption_with_same_kappa() -> None:
    x = np.linspace(0.0, 1.0, 20)
    temperature = np.linspace(500.0, 1500.0, 20)
    transparent_model = _single_gray_gas_model(0.0)

    wsgg_result = solve_wsgg_dom(
        x,
        temperature,
        transparent_model,
        particle_absorption_coefficient_m=2.0,
        quadrature_order=8,
    )
    pure_result = solve_pure_absorption_dom(x, temperature, 2.0, quadrature_order=8)

    assert np.allclose(wsgg_result.heat_flux, pure_result.heat_flux)
    assert np.allclose(wsgg_result.source_term, pure_result.source_term)


def test_wsgg_dom_raises_for_negative_pressure_scale() -> None:
    x = np.linspace(0.0, 1.0, 10)
    temperature = np.full_like(x, 1000.0)
    model = _single_gray_gas_model(1.0)
    with pytest.raises(ValueError, match="non-negative"):
        solve_wsgg_dom(x, temperature, model, pressure_scale=-1.0)


def test_wsgg_dom_raises_for_negative_particle_absorption() -> None:
    x = np.linspace(0.0, 1.0, 10)
    temperature = np.full_like(x, 1000.0)
    model = _single_gray_gas_model(1.0)
    with pytest.raises(ValueError, match="non-negative"):
        solve_wsgg_dom(x, temperature, model, particle_absorption_coefficient_m=-1.0)


def test_wsgg_dom_raises_when_model_has_no_gases() -> None:
    # With normalize_weights=True (the WSGGModel default), an empty gas set already fails
    # inside WSGGModel.weights() (tested separately below), so normalize_weights=False is used
    # here to actually reach solve_wsgg_dom's own "model contains no gases" guard.
    x = np.linspace(0.0, 1.0, 10)
    temperature = np.full_like(x, 1000.0)
    empty_model = WSGGModel(
        absorption_coefficients=np.zeros(0),
        weight_coefficients=np.zeros((0, 1)),
        normalize_weights=False,
    )
    with pytest.raises(ValueError, match="no gases"):
        solve_wsgg_dom(x, temperature, empty_model)


def test_wsgg_model_with_no_gases_fails_weight_normalization_by_default() -> None:
    empty_model = WSGGModel(
        absorption_coefficients=np.zeros(0),
        weight_coefficients=np.zeros((0, 1)),
    )
    with pytest.raises(ValueError, match="sum to zero"):
        empty_model.weights(1000.0)


def test_solve_pure_absorption_dom_rejects_temperature_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="same shape"):
        solve_pure_absorption_dom(np.linspace(0.0, 1.0, 10), np.full(5, 1000.0), 1.0)


def test_solve_pure_absorption_dom_rejects_non_positive_temperature() -> None:
    x = np.linspace(0.0, 1.0, 5)
    with pytest.raises(ValueError, match="positive"):
        solve_pure_absorption_dom(x, np.full_like(x, 0.0), 1.0)


def test_solve_pure_absorption_dom_rejects_negative_absorption_coefficient() -> None:
    x = np.linspace(0.0, 1.0, 5)
    with pytest.raises(ValueError, match="non-negative"):
        solve_pure_absorption_dom(x, np.full_like(x, 1000.0), -1.0)


def test_solve_pure_absorption_dom_rejects_odd_quadrature_order() -> None:
    x = np.linspace(0.0, 1.0, 5)
    with pytest.raises(ValueError, match="even"):
        solve_pure_absorption_dom(x, np.full_like(x, 1000.0), 1.0, quadrature_order=7)


def test_solve_spectral_pure_absorption_dom_rejects_kappa_shape_mismatch() -> None:
    x = np.linspace(0.0, 1.0, 4)
    eta = np.linspace(100.0, 1000.0, 6)
    with pytest.raises(ValueError, match="shape"):
        solve_spectral_pure_absorption_dom(
            x, np.full_like(x, 1000.0), eta, np.zeros((eta.size, x.size + 1))
        )
