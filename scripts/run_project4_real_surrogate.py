"""Project 4: ML surrogate for a published H2O Planck-mean absorption correlation."""

from __future__ import annotations

import _bootstrap  # noqa: F401

from pathlib import Path

import numpy as np
import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report
from sklearn.metrics import mean_absolute_percentage_error

from thermal_radiation_modeling.published_data import (
    SOURCES,
    h2o_planck_mean_singh_hostikka_2026,
)
from thermal_radiation_modeling.surrogate import train_emissivity_surrogate

OUTPUT_DIR = Path("outputs/project4_real_surrogate")


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    temperatures = np.linspace(300.0, 2400.0, 140)
    mole_fractions = np.concatenate(
        [
            np.linspace(0.01, 0.05, 9),
            np.linspace(0.06, 0.25, 20),
            np.linspace(0.30, 1.00, 15),
        ]
    )
    rows = []
    for temperature in temperatures:
        for mole_fraction in mole_fractions:
            kappa = h2o_planck_mean_singh_hostikka_2026(temperature, mole_fraction)
            rows.append(
                {
                    "temperature_k": temperature,
                    "mole_fraction_h2o": mole_fraction,
                    "planck_mean_kappa_m-1": float(kappa),
                }
            )
    table = pd.DataFrame(rows)
    features = table[["temperature_k", "mole_fraction_h2o"]].to_numpy()
    target = np.log10(table["planck_mean_kappa_m-1"].to_numpy())

    # log10(kappa) is not bounded to [0, 1] like an emissivity, so disable the
    # surrogate helper's default emissivity clipping (clip_range=None).
    result = train_emissivity_surrogate(
        features,
        target,
        random_state=42,
        hidden_layer_sizes=(32, 24),
        learning_rate_init=0.001,  # sklearn's MLPRegressor default, matching the original fit
        max_iter=2500,
        n_iter_no_change=50,
        clip_range=None,
    )
    y_test_kappa = 10**result.y_test
    y_pred_kappa = 10**result.y_pred
    metrics = pd.DataFrame(
        [
            {
                "target": "log10(kappa_planck)",
                "train_samples": result.y_train.size,
                "test_samples": result.y_test.size,
                "r2_log_space": result.r2,
                "rmse_log10": result.rms_error,
                "mean_absolute_percentage_error_kappa": mean_absolute_percentage_error(
                    y_test_kappa, y_pred_kappa
                ),
            }
        ]
    )
    table.to_csv(OUTPUT_DIR / "tables/surrogate_training_grid.csv", index=False)
    pd.DataFrame(
        {
            "temperature_k": result.x_test[:, 0],
            "mole_fraction_h2o": result.x_test[:, 1],
            "reference_kappa_m-1": y_test_kappa,
            "predicted_kappa_m-1": y_pred_kappa,
        }
    ).to_csv(OUTPUT_DIR / "tables/surrogate_predictions.csv", index=False)
    metrics.to_csv(OUTPUT_DIR / "tables/surrogate_metrics.csv", index=False)
    _plot(y_test_kappa, y_pred_kappa)
    _write_report(metrics)
    print(f"Wrote {OUTPUT_DIR}")


def _plot(reference, predicted) -> None:
    fig, axis = plt.subplots(figsize=(5, 4.5), constrained_layout=True)
    axis.loglog(reference, predicted, ".", alpha=0.65)
    lim = [min(reference.min(), predicted.min()), max(reference.max(), predicted.max())]
    axis.loglog(lim, lim, color="black", linewidth=1)
    axis.set_xlabel("published-correlation kappa [m^-1]")
    axis.set_ylabel("surrogate kappa [m^-1]")
    axis.set_title("Surrogate parity for H2O Planck mean")
    fig.savefig(OUTPUT_DIR / "figures/surrogate_kappa_parity.png", dpi=180)
    plt.close(fig)


def _write_report(metrics: pd.DataFrame) -> None:
    source = SOURCES["singh_hostikka_2026"]
    report = f"""# Project 4 Report: ML Surrogate for Published Radiative Property Fit

This surrogate is trained against the H2O Planck-mean absorption correlation from:

{source.citation}

DOI: {source.url}

## Metrics

{metrics.to_markdown(index=False)}

## Interpretation

This is an honest ML acceleration demonstration based on a published radiative-property
correlation. It is intentionally modest: the real doctoral-level next
step is to train on HITEMP/HITRAN-derived RCFSK/FSCK tables or measured FTIR particle
properties.
"""
    write_report(OUTPUT_DIR, "project4_report.md", report)


if __name__ == "__main__":
    main()
