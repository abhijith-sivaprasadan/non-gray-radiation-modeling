# Project 4 Extension: Surrogate Trained on Self-Generated Data

`run_project4_real_surrogate.py` accelerates evaluating Singh & Hostikka's *published*
correlation - free to sample as densely as wanted (6160 points). This trains the same kind
of surrogate on `run_project1_own_hitran_fit.py`'s self-generated data instead: real HITRAN
line-by-line Planck-mean values, each costing a real Voigt-profile calculation - only
42 points, not 6160, because each one is a real computation,
not a free function evaluation.

## Honesty Boundary

42 points is a small training set for a neural network, and
this surrogate is correspondingly more overfit-prone than Project 4's original. The point of
this script is the *complete, self-generated pipeline* - real spectral data -> a fitted
quantity -> an ML surrogate that accelerates evaluating it - not a claim that this specific
surrogate is production-ready. Scaling up the point count (a denser own-HITRAN-fit grid)
would directly improve it, at the cost of more ~13 s-per-point real computations.

## Metrics

| target | points | train | test | R2 (log space) | RMSE log10 | MAPE(kappa) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| log10(own_kappa_planck) | 42 | 31 | 11 | 0.9774 | 0.0703 | 13.6% |

Parity plot in `figures/own_data_surrogate_parity.png`.

## Interpretation

Compare this R2 against Project 4's 0.99907 (trained on 6160 free evaluations of a smooth
closed-form correlation) - a materially harder problem with two orders of magnitude fewer,
real, individually-computed training points is not expected to match it, and the honest gap
between the two numbers is itself the evidence that this is a genuinely different (harder,
more real) exercise, not a re-run of the same one.
