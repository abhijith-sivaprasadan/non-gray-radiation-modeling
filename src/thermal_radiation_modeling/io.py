"""Small CSV helpers for WSGG models and workflow outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from thermal_radiation_modeling.wsgg import WSGGModel


def save_wsgg_model_csv(model: WSGGModel, path: str | Path) -> None:
    """Save a WSGG model to a tidy coefficient CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for gas_index, (kappa, coeffs) in enumerate(
        zip(model.absorption_coefficients, model.weight_coefficients)
    ):
        row = {
            "gas_index": gas_index,
            "absorption_coefficient": kappa,
            "reference_temperature_k": model.reference_temperature_k,
        }
        for order, coefficient in enumerate(coeffs):
            row[f"b{order}"] = coefficient
        rows.append(row)
    pd.DataFrame(rows).to_csv(output_path, index=False)


def load_wsgg_model_csv(path: str | Path) -> WSGGModel:
    """Load a WSGG model saved by :func:`save_wsgg_model_csv`."""

    frame = pd.read_csv(path).sort_values("gas_index")
    coefficient_columns = [column for column in frame.columns if column.startswith("b")]
    coefficient_columns.sort(key=lambda value: int(value[1:]))
    return WSGGModel(
        absorption_coefficients=frame["absorption_coefficient"].to_numpy(float),
        weight_coefficients=frame[coefficient_columns].to_numpy(float),
        reference_temperature_k=float(frame["reference_temperature_k"].iloc[0]),
    )
