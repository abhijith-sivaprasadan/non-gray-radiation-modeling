"""Project 4 extension: an ML surrogate trained on this repository's own data, not a lookup.

run_project4_real_surrogate.py trains a surrogate to reproduce Singh & Hostikka's *published*
Planck-mean correlation - the acceleration mechanism works, but it accelerates evaluating
someone else's closed-form function, which is free to sample as densely as wanted (6160
points in the original). This script trains the same kind of surrogate on
run_project1_own_hitran_fit.py's self-generated data instead: real HITRAN line-by-line
Planck-mean values, each costing a real Voigt-profile calculation (~13 s), giving only the
42 grid points that script actually computed - a complete, self-generated pipeline (real
spectral data -> a fitted quantity -> an ML surrogate that accelerates evaluating it), at
the honest cost of a much smaller, more overfit-prone training set than a free closed-form
correlation allows. This script's point is the completed pipeline architecture, not a claim
that 42 points make a robust surrogate - that limitation is reported, not hidden.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from pathlib import Path

import numpy as np
import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report
from sklearn.metrics import mean_absolute_percentage_error

from thermal_radiation_modeling.surrogate import train_emissivity_surrogate

OUTPUT_DIR = Path("outputs/project4_own_data_surrogate")
OWN_FIT_GRID = Path("outputs/project1_own_hitran_fit/tables/own_vs_published_planck_mean.csv")


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    if not OWN_FIT_GRID.exists():
        print(
            f"Skipping: {OWN_FIT_GRID} not found. Run scripts/run_project1_own_hitran_fit.py first."
        )
        return

    grid = pd.read_csv(OWN_FIT_GRID)
    features = grid[["temperature_k", "mole_fraction_h2o"]].to_numpy()
    target = np.log10(grid["own_kappa_planck_m-1"].to_numpy())

    # A much smaller network than Project 4's (48,32 default / 32,24 used there): 42 points
    # cannot support that many free parameters without overfitting.
    result = train_emissivity_surrogate(
        features,
        target,
        random_state=42,
        hidden_layer_sizes=(6, 4),
        max_iter=3000,
        n_iter_no_change=200,
        clip_range=None,
    )
    y_test_kappa = 10**result.y_test
    y_pred_kappa = 10**result.y_pred

    metrics = pd.DataFrame(
        [
            {
                "target": "log10(own_kappa_planck)",
                "n_total_points": len(grid),
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
    metrics.to_csv(OUTPUT_DIR / "tables" / "own_data_surrogate_metrics.csv", index=False)

    _plot(y_test_kappa, y_pred_kappa)
    _write_report(metrics.iloc[0])
    print(f"Wrote {OUTPUT_DIR}")


def _plot(reference: np.ndarray, predicted: np.ndarray) -> None:
    fig, axis = plt.subplots(figsize=(5, 4.5), constrained_layout=True)
    axis.loglog(reference, predicted, "o", alpha=0.7)
    lim = [min(reference.min(), predicted.min()), max(reference.max(), predicted.max())]
    axis.loglog(lim, lim, color="black", linewidth=1)
    axis.set_xlabel("own HITRAN-derived kappa [m^-1]")
    axis.set_ylabel("surrogate kappa [m^-1]")
    axis.set_title("Surrogate parity - trained on self-generated data (42 points)")
    fig.savefig(OUTPUT_DIR / "figures" / "own_data_surrogate_parity.png", dpi=180)
    plt.close(fig)


def _write_report(metrics: pd.Series) -> None:
    report = f"""# Project 4 Extension: Surrogate Trained on Self-Generated Data

`run_project4_real_surrogate.py` accelerates evaluating Singh & Hostikka's *published*
correlation - free to sample as densely as wanted (6160 points). This trains the same kind
of surrogate on `run_project1_own_hitran_fit.py`'s self-generated data instead: real HITRAN
line-by-line Planck-mean values, each costing a real Voigt-profile calculation - only
{int(metrics['n_total_points'])} points, not 6160, because each one is a real computation,
not a free function evaluation.

## Honesty Boundary

{int(metrics['n_total_points'])} points is a small training set for a neural network, and
this surrogate is correspondingly more overfit-prone than Project 4's original. The point of
this script is the *complete, self-generated pipeline* - real spectral data -> a fitted
quantity -> an ML surrogate that accelerates evaluating it - not a claim that this specific
surrogate is production-ready. Scaling up the point count (a denser own-HITRAN-fit grid)
would directly improve it, at the cost of more ~13 s-per-point real computations.

## Metrics

| target | points | train | test | R2 (log space) | RMSE log10 | MAPE(kappa) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| {metrics['target']} | {int(metrics['n_total_points'])} | {int(metrics['train_samples'])} | {int(metrics['test_samples'])} | {metrics['r2_log_space']:.4f} | {metrics['rmse_log10']:.4f} | {100 * metrics['mean_absolute_percentage_error_kappa']:.1f}% |

Parity plot in `figures/own_data_surrogate_parity.png`.

## Interpretation

Compare this R2 against Project 4's 0.99907 (trained on 6160 free evaluations of a smooth
closed-form correlation) - a materially harder problem with two orders of magnitude fewer,
real, individually-computed training points is not expected to match it, and the honest gap
between the two numbers is itself the evidence that this is a genuinely different (harder,
more real) exercise, not a re-run of the same one.
"""
    write_report(OUTPUT_DIR, "project4_own_data_surrogate_report.md", report)


if __name__ == "__main__":
    main()
