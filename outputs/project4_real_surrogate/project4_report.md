# Project 4 Report: ML Surrogate for Published Radiative Property Fit

This surrogate is trained against the H2O Planck-mean absorption correlation from:

K. Singh and S. Hostikka, Non-gray radiation model optimized for hydrogen flames, Applied Thermal Engineering 294 (2026) 130593.

DOI: https://doi.org/10.1016/j.applthermaleng.2026.130593

## Metrics

| target              |   train_samples |   test_samples |   r2_log_space |   rmse_log10 |   mean_absolute_percentage_error_kappa |
|:--------------------|----------------:|---------------:|---------------:|-------------:|---------------------------------------:|
| log10(kappa_planck) |            4620 |           1540 |        0.99907 |    0.0216157 |                              0.0320063 |

## Interpretation

This is an honest ML acceleration demonstration based on a published radiative-property
correlation. It is intentionally modest: the real doctoral-level next
step is to train on HITEMP/HITRAN-derived RCFSK/FSCK tables or measured FTIR particle
properties.
