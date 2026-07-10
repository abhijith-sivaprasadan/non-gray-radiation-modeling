import numpy as np
import pytest

from thermal_radiation_modeling.particles import (
    absorption_coefficient_from_volume_fraction,
    johansson_2017_ash_efficiencies,
    mie_efficiencies,
    rayleigh_absorption_coefficient,
    rayleigh_absorption_efficiency,
    rayleigh_scattering_efficiency,
    size_parameter,
)


def test_size_parameter_formula() -> None:
    assert np.isclose(size_parameter(1e-6, 10e-6), 2.0 * np.pi * 0.1)


def test_rayleigh_efficiencies_are_non_negative() -> None:
    refractive_index = 1.8 + 0.4j
    q_abs = rayleigh_absorption_efficiency(refractive_index, 50e-9, 5e-6)
    q_sca = rayleigh_scattering_efficiency(refractive_index, 50e-9, 5e-6)
    assert q_abs >= 0.0
    assert q_sca >= 0.0


def test_absorption_coefficient_uses_spherical_volume_fraction_relation() -> None:
    kappa = absorption_coefficient_from_volume_fraction(1e-6, 2e-6, 0.8)
    assert np.isclose(kappa, 3.0 * 1e-6 * 0.8 / (4.0 * 2e-6))


def test_rayleigh_absorption_coefficient_matches_two_step_calculation() -> None:
    refractive_index = 1.8 + 0.4j
    q_abs = rayleigh_absorption_efficiency(refractive_index, 50e-9, 5e-6)
    expected = absorption_coefficient_from_volume_fraction(1e-7, 50e-9, q_abs)
    actual = rayleigh_absorption_coefficient(1e-7, refractive_index, 50e-9, 5e-6)
    assert np.isclose(actual, expected)


def test_mie_efficiencies_are_energy_consistent() -> None:
    efficiencies = mie_efficiencies(1.7 + 0.3j, 1e-6, 5e-6)
    assert efficiencies.q_ext >= 0.0
    assert efficiencies.q_sca >= 0.0
    assert efficiencies.q_abs >= 0.0
    assert np.isclose(efficiencies.q_ext, efficiencies.q_abs + efficiencies.q_sca)


def test_size_parameter_rejects_non_positive_radius() -> None:
    with pytest.raises(ValueError, match="radius_m"):
        size_parameter(0.0, 1e-6)


def test_size_parameter_rejects_non_positive_wavelength() -> None:
    with pytest.raises(ValueError, match="wavelength_m"):
        size_parameter(1e-6, 0.0)


def test_absorption_coefficient_from_volume_fraction_rejects_negative_volume_fraction() -> None:
    with pytest.raises(ValueError, match="volume_fraction"):
        absorption_coefficient_from_volume_fraction(-1e-6, 1e-6, 0.5)


def test_absorption_coefficient_from_volume_fraction_rejects_non_positive_radius() -> None:
    with pytest.raises(ValueError, match="radius_m"):
        absorption_coefficient_from_volume_fraction(1e-6, 0.0, 0.5)


def test_johansson_ash_efficiencies_rejects_unknown_ash_type() -> None:
    with pytest.raises(ValueError, match="ash_type"):
        johansson_2017_ash_efficiencies(20.0, 1500.0, "ash3")
