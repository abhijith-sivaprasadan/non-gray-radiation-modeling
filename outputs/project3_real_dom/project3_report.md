# Project 3 Report: DOM on Published Hydrogen/H2O Fields

This script uses the analytic radial and axial fields and H2O Planck-mean correlation from:

K. Singh and S. Hostikka, Non-gray radiation model optimized for hydrogen flames, Applied Thermal Engineering 294 (2026) 130593.

DOI: https://doi.org/10.1016/j.applthermaleng.2026.130593

## What Is Computed Here

- A 1-D S8 DOM sweep through the radial test case midline.
- A 1-D S8 DOM sweep through the axial test case centerline.
- Local H2O Planck-mean absorption using the paper's Eq. (21).

## What Is Not Claimed

This is not a reproduction of the paper's 2-D LBL/RCFSK benchmark. The paper's published
comparison metrics are stored separately in `tables/published_model_error_summary.csv`.
The purpose here is to demonstrate a transparent DOM implementation on the same published
thermodynamic fields, while keeping the high-fidelity benchmark values tied to the paper.
