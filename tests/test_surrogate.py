import numpy as np
import pytest

from thermal_radiation_modeling.published_data import h2o_planck_mean_singh_hostikka_2026
from thermal_radiation_modeling.surrogate import train_emissivity_surrogate


def test_project4_surrogate_reproduces_published_readme_r2() -> None:
    # Reproduces the exact grid and hyperparameters used by
    # scripts/run_project4_real_surrogate.py, which README.md advertises as achieving
    # R2 = 0.99907 for log10(kappa_planck). This pins that headline number so a change to
    # the surrogate helper (e.g. a different default learning rate) cannot silently drift it.
    temperatures = np.linspace(300.0, 2400.0, 140)
    mole_fractions = np.concatenate(
        [
            np.linspace(0.01, 0.05, 9),
            np.linspace(0.06, 0.25, 20),
            np.linspace(0.30, 1.00, 15),
        ]
    )
    rows = [
        (
            temperature,
            mole_fraction,
            h2o_planck_mean_singh_hostikka_2026(temperature, mole_fraction),
        )
        for temperature in temperatures
        for mole_fraction in mole_fractions
    ]
    grid = np.array(rows)
    features = grid[:, :2]
    target = np.log10(grid[:, 2])

    result = train_emissivity_surrogate(
        features,
        target,
        random_state=42,
        hidden_layer_sizes=(32, 24),
        learning_rate_init=0.001,
        max_iter=2500,
        n_iter_no_change=50,
        clip_range=None,
    )

    assert result.r2 == pytest.approx(0.99907, abs=1e-4)


def test_train_emissivity_surrogate_clips_to_default_emissivity_range() -> None:
    rng = np.random.default_rng(0)
    features = rng.uniform(0.0, 1.0, size=(80, 2))
    emissivity = np.clip(features[:, 0] * 0.5 + features[:, 1] * 0.5, 0.0, 1.0)

    result = train_emissivity_surrogate(features, emissivity, random_state=0, max_iter=200)

    assert np.all(result.y_pred >= 0.0)
    assert np.all(result.y_pred <= 1.0)


def test_train_emissivity_surrogate_clip_range_none_allows_unbounded_targets() -> None:
    # With clip_range=(0, 1) (the default), a target that ranges well outside [0, 1] would
    # have its predictions clamped and its R2 corrupted, exactly as would have happened had
    # run_project4_real_surrogate.py naively reused the default emissivity clipping for its
    # log10(kappa) target. clip_range=None must avoid that corruption.
    rng = np.random.default_rng(0)
    features = rng.uniform(0.0, 1.0, size=(200, 2))
    unbounded_target = features[:, 0] * 10.0 - 5.0

    clipped = train_emissivity_surrogate(features, unbounded_target, random_state=0, max_iter=300)
    unclipped = train_emissivity_surrogate(
        features, unbounded_target, random_state=0, max_iter=300, clip_range=None
    )

    assert np.all(clipped.y_pred >= 0.0) and np.all(clipped.y_pred <= 1.0)
    assert clipped.r2 < 0.5
    assert unclipped.r2 > 0.9


def test_train_emissivity_surrogate_rejects_wrong_feature_ndim() -> None:
    with pytest.raises(ValueError, match="two-dimensional"):
        train_emissivity_surrogate(np.zeros(10), np.zeros(10))


def test_train_emissivity_surrogate_rejects_misaligned_target_length() -> None:
    with pytest.raises(ValueError, match="aligned to features"):
        train_emissivity_surrogate(np.zeros((10, 2)), np.zeros(5))
