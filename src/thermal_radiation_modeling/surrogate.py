"""Machine-learning surrogate helpers for emissivity data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class SurrogateTrainingResult:
    model: Pipeline
    x_train: np.ndarray
    x_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    y_pred: np.ndarray
    mean_abs_error: float
    rms_error: float
    r2: float


def train_emissivity_surrogate(
    features: np.ndarray,
    emissivity: np.ndarray,
    random_state: int = 42,
    hidden_layer_sizes: tuple[int, ...] = (48, 32),
    activation: str = "tanh",
    alpha: float = 1e-4,
    learning_rate_init: float = 0.01,
    max_iter: int = 3000,
    n_iter_no_change: int = 80,
    clip_range: tuple[float, float] | None = (0.0, 1.0),
) -> SurrogateTrainingResult:
    """Train a small MLP surrogate for a bounded radiative-property target.

    ``clip_range`` clamps predictions to a known-valid range and defaults to ``(0.0, 1.0)``
    for true emissivity targets. Pass ``clip_range=None`` for unbounded targets (for example
    ``log10(kappa)``), where clipping to ``[0, 1]`` would corrupt the predictions.
    """

    x = np.asarray(features, dtype=float)
    y = np.asarray(emissivity, dtype=float)
    if x.ndim != 2:
        raise ValueError("features must be a two-dimensional array")
    if y.ndim != 1 or y.size != x.shape[0]:
        raise ValueError("emissivity must be a one-dimensional array aligned to features")

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=random_state,
    )
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "mlp",
                MLPRegressor(
                    hidden_layer_sizes=hidden_layer_sizes,
                    activation=activation,
                    alpha=alpha,
                    learning_rate_init=learning_rate_init,
                    max_iter=max_iter,
                    random_state=random_state,
                    early_stopping=True,
                    n_iter_no_change=n_iter_no_change,
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    if clip_range is not None:
        y_pred = np.clip(y_pred, clip_range[0], clip_range[1])
    return SurrogateTrainingResult(
        model=model,
        x_train=x_train,
        x_test=x_test,
        y_train=y_train,
        y_test=y_test,
        y_pred=y_pred,
        mean_abs_error=float(mean_absolute_error(y_test, y_pred)),
        rms_error=float(mean_squared_error(y_test, y_pred) ** 0.5),
        r2=float(r2_score(y_test, y_pred)),
    )


def build_surrogate_table(
    species_names: list[str],
    temperatures_k: np.ndarray,
    pressure_paths: np.ndarray,
    emissivity_by_species: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Build feature and target arrays from species emissivity grids."""

    features = []
    targets = []
    ordered_species = list(species_names)
    for species_index, species_name in enumerate(ordered_species):
        grid = emissivity_by_species[species_name]
        for i, temperature in enumerate(temperatures_k):
            for j, pressure_path in enumerate(pressure_paths):
                one_hot = np.zeros(len(ordered_species), dtype=float)
                one_hot[species_index] = 1.0
                features.append(
                    np.concatenate(
                        [
                            one_hot,
                            np.array(
                                [
                                    temperature / 1500.0,
                                    np.log10(pressure_path),
                                ]
                            ),
                        ]
                    )
                )
                targets.append(grid[i, j])
    feature_names = [f"species_{name}" for name in ordered_species] + [
        "temperature_scaled",
        "log10_pressure_path",
    ]
    return np.asarray(features), np.asarray(targets), feature_names
