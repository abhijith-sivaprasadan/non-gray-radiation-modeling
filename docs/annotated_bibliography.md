# Annotated Bibliography

This is a working reading map for the Aalto R47351 portfolio.

## Anchor Paper

Sadeghi, Hostikka, Fraga, and Bordbar, *Fire Safety Journal* 125, 103420, 2021.

- Builds WSGG models for hydrocarbon fuel vapors, CH4, CO, and soot.
- Uses 4 gray gases plus a transparent gas for gases, with fifth-order temperature
  polynomials and `T_ref = 1400 K`.
- Validates against line-by-line calculations in 1-D slab cases and a 3-D heptane pool-fire
  benchmark.
- Treats soot through Rayleigh-regime particulate absorption, which is the conceptual bridge
  to solid-particle modeling.
- Main limitation for portfolio discussion: superposition becomes expensive as species count
  grows, and WSGG is less reliable in absorption-dominated regimes.

## Current Research-Team Papers Added To This Repo

Hostikka and Rashidzadeh, *Fire Safety Journal*, 2026, "Thermal radiation - From science to engineering."

- Review of radiation-property and RTE-solver models with emphasis on FDS.
- Connects scientific radiation modeling to engineering fire-CFD implementation.
- This repo uses it as the context for FDS, PMC-LBL benchmarking, vegetation particles, and engineering model hierarchy.

Rashidzadeh et al., *Fire Safety Journal*, 2026, "Non-gray radiation modeling of methanol pool fires using the RC-FSK method in FDS."

- RC-FSK implemented as an FDS radiation-module subroutine.
- HITEMP 2010 data at 0.01 cm^-1 resolution, Lorentz broadening, and 500 cm^-1 line-wing cutoff.
- Provides real methanol pool-fire PMC-LBL comparison metrics and global radiant-fraction data encoded in this repo.

Singh and Hostikka, *Applied Thermal Engineering*, 2026, "Non-gray radiation model optimized for hydrogen flames."

- Provides analytic radial and axial validation fields, H2O Planck-mean correlation, RCFSK/WSGG/Planck-mean error comparisons, CPU timings, and wall-emission error table.
- This is the main real-data source for Projects 1, 3, and 4.

## Group Context

Bordbar, Wecel, and Hyppanen, *Combustion and Flame*, 2014.

- Foundational LBL-based WSGG model for inhomogeneous CO2-H2O in oxy-fired combustion.
- Useful for understanding why HITEMP-derived emissivity databases are central to the group.

Bordbar, Fraga, and Hostikka, *International Communications in Heat and Mass Transfer*, 2020.

- Extends CO2-H2O WSGG coverage over molar-fraction ratios.
- Useful comparison point for the Project 1 WSGG fitting method.

Fraga, Bordbar, Hostikka, and Franca, *Journal of Heat Transfer*, 2020.

- Provides 3-D LBL benchmark methodology.
- Useful for discussing validation hierarchy: LBL as ground truth, global models as
  engineering approximations.

Rashidzadeh, Fraga, Bordbar, and Hostikka, *Journal of Quantitative Spectroscopy and
Radiative Transfer*, 2024.

- Compares non-gray global models such as RC-FSK, RC-SLW, and WSGG against high-fidelity
  references.
- Useful for explaining the cost-accuracy trade-off behind the doctoral topic.

Alinejad, Bordbar, and Hostikka, 2020-2021 condensed-phase FSCK papers.

- Relevant to in-depth radiation penetration in liquids and condensed fuels.
- Provides context for moving beyond gas-phase radiation.

## Methods References

Modest, *Radiative Heat Transfer*, 3rd ed.

- Core reference for RTE, DOM, WSGG, k-distribution, SLW, and FSCK.
- Use this to defend derivations in an interview.

Bohren and Huffman, *Absorption and Scattering of Light by Small Particles*.

- Core reference for Rayleigh and Mie scattering/absorption.
- Relevant to Project 2 and to caveats about spherical-particle assumptions.

Kochanov et al., HAPI paper and HAPI manual.

- Practical reference for HITRAN/HITEMP line-list workflows.
- Needed when reproducing HITEMP-derived spectral databases from first principles.

Zhou, Wang, and Ren, *JQSRT*, 2020.

- Example of machine-learning acceleration of full-spectrum gas-radiation property
  evaluation.
- Motivates the modest Project 4 surrogate.
