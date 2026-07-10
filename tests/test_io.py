import numpy as np

from thermal_radiation_modeling.io import load_wsgg_model_csv, save_wsgg_model_csv
from thermal_radiation_modeling.wsgg import WSGGModel


def test_save_and_load_wsgg_model(tmp_path) -> None:
    model = WSGGModel(
        absorption_coefficients=np.array([0.0, 1.0, 5.0]),
        weight_coefficients=np.array([[0.3, 0.0], [0.4, 0.1], [0.3, -0.1]]),
    )
    path = tmp_path / "model.csv"
    save_wsgg_model_csv(model, path)
    loaded = load_wsgg_model_csv(path)
    assert np.allclose(loaded.absorption_coefficients, model.absorption_coefficients)
    assert np.allclose(loaded.weight_coefficients, model.weight_coefficients)
