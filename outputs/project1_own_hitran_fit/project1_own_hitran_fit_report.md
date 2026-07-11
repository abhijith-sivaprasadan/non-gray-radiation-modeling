# Project 1 Extension: Own HITRAN LBL Fit vs. the Published Correlation

This is an independently computed result, not a lookup of published numbers. It fetches
real H2O line-by-line data from HITRAN via HAPI, computes a Voigt-profile absorption
coefficient, and fits both a power-law Planck-mean correlation and a multi-gray-gas WSGG
model from scratch - then checks both against:

K. Singh and S. Hostikka, Non-gray radiation model optimized for hydrogen flames, Applied Thermal Engineering 294 (2026) 130593.

DOI: https://doi.org/10.1016/j.applthermaleng.2026.130593

## Disclosed Boundaries (read before trusting the numbers)

1. **HITRAN, not HITEMP.** HAPI's interactive fetch only reaches the standard HITRAN
   database. Singh & Hostikka's correlation was built from HITEMP2010, which includes many
   weak hot lines HITRAN omits. HITEMP is distributed as large static archive files
   impractical to fetch in this environment. This should make the own fit
   **under-predict**, worsening at higher T.
2. **Bounded wavenumber range.** 150-2200 cm^-1
   (H2O's pure-rotational band and 6.3 um fundamental) rather than the paper's full
   ~150-6500 cm^-1 coverage, for tractability. Concentrating the Planck-weighted average on
   only the two strongest-absorbing bands (instead of the paper's much wider range, most of
   which absorbs more weakly) should make the own fit **over-predict**.

These two boundaries pull in *opposite* directions - which one dominates is an empirical
question, answered below by the actual grid, not assumed going in.

## Own vs. Published Planck-Mean Absorption

The own fit **over-predicts** on average (mean signed relative error: +135.5%),
and that error **grows** with temperature (correlation of error vs. T:
+0.95).

Boundary 2 (range truncation) dominates over boundary 1 (missing hot lines) across this
entire grid, and the size of that dominance **grows** with temperature rather than
shrinking. The mechanism is Wien's law: as T rises, the blackbody weighting shifts toward
higher wavenumber, moving progressively more of the "true" (published, full-range) average
into the near-IR combination/overtone bands above 2200 cm^-1 that this
script excludes entirely. Those excluded bands absorb more weakly than the two strong bands
this script keeps, so the published average is increasingly pulled down by them as T rises,
while this script's average - concentrated on only the strong bands - is not. Boundary 1
(HITRAN's missing hot lines) is real but evidently smaller than this effect across this
grid; it would show up as the over-prediction *shrinking* at high T, which is not what the
data below shows.

Mean absolute relative error: 135.5%. Worst case: T=1900 K,
X_H2O=0.30, error +209.9%.
Best case: T=400 K, X_H2O=0.30,
error +4.3%.

Full grid in `tables/own_vs_published_planck_mean.csv`; parity plot in
`figures/own_vs_published_parity.png`; per-mole-fraction curves in
`figures/own_vs_published_by_temperature.png`.

## Own Power-Law Fit

Fitting `kappa_planck = X_H2O * A * T^B` (same functional form as the published
correlation) to the own-computed grid:

| | A | B |
| --- | ---: | ---: |
| Published (Singh & Hostikka) | 3.8821e6 | -1.9811 |
| Own (HITRAN-derived) | 7.486e+04 | -1.3072 |

The exponent B is the more physically informative comparison: it describes how fast
Planck-mean absorption falls off with temperature, and is far less sensitive to the missing-
line-strength boundaries above than the prefactor A is.

## Own WSGG Fit

A 2-gray-gas WSGG model (polynomial degree 2)
fit via this repository's own `fitting.fit_polynomial_wsgg` to the own-computed total-
emissivity grid (fixed X_H2O=0.1, path lengths
0.010-3.00 m):

- Mean absolute error: 0.0037
- Max absolute error: 0.0124
- Optimizer converged: True

Coefficients in `tables/own_wsgg_model_coefficients.csv`; fit-quality summary in
`tables/own_wsgg_fit_quality.csv`. This is the WSGG toolkit (`wsgg.py`/`fitting.py`/`io.py`)
that was previously held ready pending a real target emissivity table - this own-computed
LBL grid is that table.

## Interpretation

This is genuinely independent work: real spectroscopic data, in, fitted coefficients, out.
It is not expected to match the published correlation closely - the disclosed boundaries
above are real, and this run's actual sign and temperature-trend of disagreement (reported
above, not assumed) says which one currently dominates. Closing the gap for real would mean
fetching HITEMP instead of HITRAN and covering the paper's full spectral range instead of
the two strongest bands - both a larger-scope step this repository documents but does not
claim to have done.
