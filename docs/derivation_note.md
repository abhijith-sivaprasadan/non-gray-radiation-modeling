# Derivation Note

This note is the whiteboard-level derivation to accompany the code. The goal is to be able
to explain every modeled quantity without leaning on implementation details.

## Radiative Transfer Equation

For an absorbing, emitting, non-scattering medium in direction `s`, the spectral RTE is

```text
s . grad I_eta = kappa_eta (I_b,eta - I_eta)
```

where `I_eta` is spectral intensity, `kappa_eta` is spectral absorption coefficient, and
`I_b,eta` is blackbody spectral intensity. In the 1-D slab used here,

```text
mu dI_eta/dx = kappa_eta (I_b,eta - I_eta)
```

with black-wall boundary intensities entering from the left for `mu > 0` and from the right
for `mu < 0`.

## Total Emissivity From Spectra

For a uniform isothermal path, spectral emissivity is

```text
epsilon_eta = 1 - exp(-kappa_eta L)
```

The Planck-weighted total emissivity is

```text
epsilon(T,L) =
  integral epsilon_eta I_b,eta(T) d_eta / integral I_b,eta(T) d_eta
```

The code uses the relative Planck weight

```text
w_eta(T) = eta^3 / [exp(c2 eta / T) - 1]
```

because dimensional constants cancel in the ratio.

## WSGG Model

The weighted-sum-of-gray-gases approximation writes the total emissivity as

```text
epsilon(T,pL) = sum_j a_j(T) [1 - exp(-kappa_j pL)]
```

The transparent gas has `kappa_0 = 0`, so it contributes spectral windows without direct
absorption. Temperature weights are represented as polynomials in reduced temperature:

```text
T_r = T / T_ref
a_j(T) = sum_n b_j,n T_r^n
```

The fitted model enforces

```text
sum_j a_j(T) = 1
```

by parameterizing the transparent-gas coefficients as the complement of the gray-gas
coefficients. Negative weights are discouraged during fitting and clipped/renormalized
during model evaluation as a numerical guard.

## WSGG Superposition

For statistically uncorrelated species spectra, gray-gas combinations are formed by adding
absorption coefficients and multiplying weights:

```text
kappa_mix = sum_i kappa_i,j
a_mix = product_i a_i,j
```

This captures the same scaling issue discussed in the anchor paper: the number of gray-gas
combinations grows as the product of each species' gas count.

## Discrete Ordinates Solver

The 1-D DOM discretization uses half-range Gauss-Legendre quadrature mirrored across zero.
For a positive ordinate, first-order upwind marching gives

```text
I_i = (I_up + beta I_b,i) / (1 + beta)
beta = kappa_i Delta x_i / mu
```

For a negative ordinate the sweep proceeds from right to left using `abs(mu)`.

The integrated incident radiation, heat flux, and source term are

```text
G = 2 pi sum_m w_m I_m
q = 2 pi sum_m w_m mu_m I_m
S = kappa (4 pi I_b - G)
```

The spectral solver repeats this sweep for each wavenumber and integrates over `eta`.

`solve_wsgg_dom` reuses this same gray-gas sweep once per WSGG gray gas and sums the results,
weighted by that gas's temperature-dependent weight `a_j(T)`.

## Particle Absorption

For monodisperse spheres with radius `r`, volume fraction `f_v`, and absorption efficiency
`Q_abs`,

```text
kappa_p = 3 f_v Q_abs / (4 r)
```

**Scattering is not coupled into the RTE solver.** `particles.py` computes both absorption
and scattering efficiencies (Rayleigh, Mie, and Johansson's published gray correlations), but
`solve_wsgg_dom` only adds particle *absorption* into the local `kappa` used above -- there is
no scattering source term or phase function anywhere in `dom1d.py`. Any `Q_sca`/`Q_scat` value
computed by `particles.py` is therefore reported (e.g. in Project 2's tables) but not yet
exercised by the RTE solver. Adding a scattering source term (e.g. isotropic scattering, or a
Henyey-Greenstein phase function) is future work, not a claim made by the current DOM solver.

The Rayleigh-limit absorption efficiency for complex refractive index `m` is

```text
Q_abs = 4 x Im[(m^2 - 1)/(m^2 + 2)]
x = 2 pi r / lambda
```

The Mie solver computes spherical-particle efficiencies from the standard electric and
magnetic Mie coefficients. This is appropriate for homogeneous spheres, not for realistic
vegetation particles without further validation.

## Published Hydrogen Planck Mean

For the hydrogen/H2O validation cases, the repository uses the Singh and Hostikka 2026
Planck-mean fit:

```text
kappa_planck = X_H2O * 3.8821e6 * T^-1.9811
```

This is not a fitted value from this repository; it is a published HITEMP-derived
correlation encoded as real input data.

## Johansson Particle Correlation

For coal/char and ash particle efficiencies, the repository uses Johansson's correlation
form:

```text
1 / y^z = 1 / y0^z + 1 / y_inf^z
```

with `y0`, `y_inf`, and `z` taken from Johansson Tables 1-2. This replaces the earlier
placeholder refractive-index curve.

## Own HITRAN Fit (Project 1 Extension)

`scripts/run_project1_own_hitran_fit.py` computes an H2O Planck-mean correlation and WSGG
model independently of the published lookup above: real line-by-line data fetched from
HITRAN via HAPI (`third_party/hapi/`), a Voigt-profile absorption coefficient
(`hapi.absorptionCoefficient_Voigt`), and the same Planck-mean/total-emissivity reduction
(`lbl.planck_mean_absorption`, `lbl.total_emissivity_from_spectrum`) used elsewhere in this
repository.

Two boundaries versus Singh & Hostikka's published correlation, and they pull in *opposite*
directions:

1. HAPI's interactive `fetch()` only reaches the standard HITRAN database, not HITEMP (the
   paper's source, distributed as large static archive files impractical to fetch here).
   HITRAN omits weak hot lines HITEMP includes, so this should **under-predict** absorption,
   worsening at higher temperature.
2. The wavenumber range is bounded to H2O's two strongest IR bands (the pure rotational band
   and the 6.3 um fundamental), not the paper's full ~150-6500 cm^-1 coverage, for
   tractability (~13 s per line-by-line evaluation at the full range and 0.05 cm^-1
   resolution). Concentrating the Planck-weighted average on only the strongest-absorbing
   bands, instead of the much wider range the paper averages over (most of which absorbs
   more weakly), should make this **over-predict**.

Which effect dominates is empirical, not assumed - and the full 42-point (T, X_H2O) grid in
`outputs/project1_own_hitran_fit/` settled it: **boundary 2 dominates across the entire
grid**, and the size of that dominance *grows* with temperature rather than shrinking. Mean
signed relative error +135.5% (over-prediction), correlation of error against T: +0.95. The
mechanism is Wien's law: as T rises, the blackbody weighting shifts toward higher
wavenumber, moving progressively more of the published, full-range average into the near-IR
combination/overtone bands above 2200 cm^-1 that this repository's own fit excludes
entirely. Those excluded bands absorb more weakly than the two strong bands kept here, so
the published average is increasingly pulled down by them as T rises, while the own
average - concentrated on only the strong bands - is not. Boundary 1 (HITRAN's missing hot
lines) is real but evidently smaller than this effect throughout the grid; it would show up
as the over-prediction *shrinking* at high T, which is the opposite of what was observed.

The exponent B in `kappa_planck = X_H2O * A * T^B`, fit to the own grid, is -1.31 versus the
published -1.98 - both negative (Planck-mean absorption falls with temperature in both), but
the own fit falls off more slowly, consistent with the same mechanism: the own fit is
increasingly blind to the weaker high-wavenumber absorption that pulls the published
correlation down faster as T rises. The own-fitted 2-gray-gas WSGG model (fit to a separate,
fixed-X_H2O, varying-path-length emissivity grid from the same LBL spectra) matches its own
target data well - mean absolute emissivity error 0.0037 - which says the WSGG toolkit and
fitting procedure work correctly; it says nothing about matching the published correlation,
which is a different exercise entirely (see above).
