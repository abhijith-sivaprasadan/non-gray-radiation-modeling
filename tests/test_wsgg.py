import numpy as np
import pytest

from thermal_radiation_modeling.wsgg import WSGGModel, superposed_emissivity


def test_wsgg_weights_are_normalized() -> None:
    model = WSGGModel(
        absorption_coefficients=np.array([0.0, 1.0, 10.0]),
        weight_coefficients=np.array(
            [
                [0.5, 0.0],
                [0.3, 0.0],
                [0.2, 0.0],
            ]
        ),
    )
    weights = model.weights(np.array([500.0, 1000.0, 1500.0]))
    assert np.allclose(np.sum(weights, axis=-1), 1.0)


def test_wsgg_single_gray_matches_gray_emissivity() -> None:
    model = WSGGModel(
        absorption_coefficients=np.array([2.0]),
        weight_coefficients=np.array([[1.0]]),
    )
    assert np.isclose(model.emissivity(1000.0, 0.25), 1.0 - np.exp(-0.5))


def test_superposed_emissivity_matches_manual_two_species_case() -> None:
    model_a = WSGGModel(np.array([0.0, 1.0]), np.array([[0.5], [0.5]]))
    model_b = WSGGModel(np.array([0.0, 3.0]), np.array([[0.25], [0.75]]))
    value = superposed_emissivity([model_a, model_b], 1000.0, [0.2, 0.4])

    expected = 0.0
    for weight_a, kappa_a in [(0.5, 0.0), (0.5, 1.0)]:
        for weight_b, kappa_b in [(0.25, 0.0), (0.75, 3.0)]:
            expected += weight_a * weight_b * (1.0 - np.exp(-(kappa_a * 0.2 + kappa_b * 0.4)))

    assert np.isclose(value, expected)


def test_wsgg_model_rejects_mismatched_coefficient_shapes() -> None:
    with pytest.raises(ValueError, match="one weight-coefficient row"):
        WSGGModel(
            absorption_coefficients=np.array([0.0, 1.0]),
            weight_coefficients=np.array([[1.0]]),
        )


def test_wsgg_model_rejects_negative_absorption_coefficients() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        WSGGModel(
            absorption_coefficients=np.array([-1.0]),
            weight_coefficients=np.array([[1.0]]),
        )


def test_wsgg_model_rejects_non_positive_reference_temperature() -> None:
    with pytest.raises(ValueError, match="positive"):
        WSGGModel(
            absorption_coefficients=np.array([1.0]),
            weight_coefficients=np.array([[1.0]]),
            reference_temperature_k=0.0,
        )


def test_wsgg_model_weights_rejects_non_positive_temperature() -> None:
    model = WSGGModel(np.array([1.0]), np.array([[1.0]]))
    with pytest.raises(ValueError, match="positive"):
        model.weights(0.0)


def test_wsgg_model_emissivity_rejects_negative_path_length() -> None:
    model = WSGGModel(np.array([1.0]), np.array([[1.0]]))
    with pytest.raises(ValueError, match="non-negative"):
        model.emissivity(1000.0, -0.1)


def test_superposed_emissivity_rejects_mismatched_lengths() -> None:
    model = WSGGModel(np.array([1.0]), np.array([[1.0]]))
    with pytest.raises(ValueError, match="same length"):
        superposed_emissivity([model], 1000.0, [0.1, 0.2])


def test_superposed_emissivity_rejects_empty_model_list() -> None:
    with pytest.raises(ValueError, match="at least one model"):
        superposed_emissivity([], 1000.0, [])


def test_superposed_emissivity_rejects_negative_pressure_paths() -> None:
    model = WSGGModel(np.array([1.0]), np.array([[1.0]]))
    with pytest.raises(ValueError, match="non-negative"):
        superposed_emissivity([model], 1000.0, [-0.1])
