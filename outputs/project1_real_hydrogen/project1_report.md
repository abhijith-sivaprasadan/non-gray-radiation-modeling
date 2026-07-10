# Project 1 Report: Published Hydrogen/H2O Radiation Case Data

This project now uses real published equations and tables from:

K. Singh and S. Hostikka, Non-gray radiation model optimized for hydrogen flames, Applied Thermal Engineering 294 (2026) 130593.

DOI: https://doi.org/10.1016/j.applthermaleng.2026.130593

## Encoded Data

- Radial test case fields from Eqs. (15)-(18): 1 m x 1 m domain, temperature
  500-2000 K, H2O mole fraction 0.01-0.30.
- Axial test case fields from Eq. (20): 2 m x 4 m domain, temperature 300-2000 K,
  H2O mole fraction 0.01-0.30.
- H2O Planck-mean absorption correlation from Eq. (21):
  `kappa_planck = X_H2O * 3.8821e6 * T^-1.9811`.
- Thermodynamic tabulation ranges from Table 1.
- CPU timings from Table 2.
- Wall-emission errors from Table 3.
- Published RCFSK/WSGG/Planck-mean error summary from the results text.

## Why This Replaces the Synthetic Workflow

The previous workflow generated artificial spectra to exercise numerical machinery. This
report does not do that. It encodes equations, tables, and validation metrics extracted from
the research-team paper and writes them as reproducible CSV/PNG artifacts.

## Remaining External Boundary

The paper's supplementary RCFSK tables and HITEMP line-list calculations are not bundled in
this workspace. The repository therefore encodes the published derived quantities and table
values, while the HAPI/HITEMP adapter remains the path for reproducing spectral databases
from first principles.
