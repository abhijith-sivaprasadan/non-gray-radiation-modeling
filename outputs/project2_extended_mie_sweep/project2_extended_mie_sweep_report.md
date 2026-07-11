# Project 2 Extension: Large-Particle Spectral Mie Sweep

This uses the same Mie solver as Project 2 (`particles.mie_efficiencies`, independently
verified against the `miepython` reference library) directly and spectrally resolved, at
particle radii (5-100 um) representative of wildland fuel char fragments - well beyond the
Rayleigh limit, and beyond what Johansson's *gray* correlations can show about
wavelength-dependence by construction.

## Honesty Boundary

Published optical constants specific to wildland vegetation/char at these wavelengths are
scarce - this is part of why FTIR characterization of real fuel particles is a genuine open
research need. This sweep uses a small, explicitly labeled range of representative
absorbing-particle refractive indices (weakly to strongly absorbing carbonaceous particles),
**not** a single measured vegetation dataset. Read the results as illustrating how much size
and wavelength matter for large fuel particles, not as a validated vegetation result.

## How Non-Gray Are Large Particles?

Relative spectral spread of Q_abs (max-min over 1-15 um, divided by the mean) by radius and
refractive index - full data in `tables/spectral_variation_summary.csv`:

|   radius_um | refractive_index_label            |   q_abs_mean |   q_abs_min |   q_abs_max |   relative_spectral_spread |
|------------:|:----------------------------------|-------------:|------------:|------------:|---------------------------:|
|           5 | moderately absorbing (m=1.7+0.5i) |     1.3685   |    0.972264 |    1.53891  |                  0.414061  |
|           5 | strongly absorbing (m=2.0+1.0i)   |     1.29837  |    0.883898 |    1.57618  |                  0.533194  |
|           5 | weakly absorbing (m=1.5+0.3i)     |     1.30314  |    1.01894  |    1.39827  |                  0.291089  |
|          20 | moderately absorbing (m=1.7+0.5i) |     1.05707  |    0.885641 |    1.19724  |                  0.294771  |
|          20 | strongly absorbing (m=2.0+1.0i)   |     0.964938 |    0.796752 |    1.0983   |                  0.312509  |
|          20 | weakly absorbing (m=1.5+0.3i)     |     1.10648  |    0.930449 |    1.25046  |                  0.289216  |
|          50 | moderately absorbing (m=1.7+0.5i) |     0.948386 |    0.863649 |    1.02041  |                  0.165293  |
|          50 | strongly absorbing (m=2.0+1.0i)   |     0.859756 |    0.773822 |    0.930769 |                  0.182549  |
|          50 | weakly absorbing (m=1.5+0.3i)     |     0.994573 |    0.908203 |    1.0685   |                  0.16117   |
|         100 | moderately absorbing (m=1.7+0.5i) |     0.90377  |    0.855346 |    0.945955 |                  0.100256  |
|         100 | strongly absorbing (m=2.0+1.0i)   |     0.815138 |    0.765066 |    0.85788  |                  0.113862  |
|         100 | weakly absorbing (m=1.5+0.3i)     |     0.948931 |    0.899834 |    0.991946 |                  0.0970695 |

Largest spread: r=5 um,
strongly absorbing (m=2.0+1.0i), relative spread
0.53.

## Comparison Against Johansson's Gray Correlation

Spectral mean Q_abs (this sweep) vs. Johansson's gray coal/char Q_abs at
T=1500 K, same radii - full data in
`tables/vs_johansson_gray_comparison.csv`:

|   radius_um | refractive_index_label            |   johansson_gray_q_abs |   mie_spectral_mean_q_abs |   ratio_mie_to_johansson |
|------------:|:----------------------------------|-----------------------:|--------------------------:|-------------------------:|
|           5 | weakly absorbing (m=1.5+0.3i)     |               1.09174  |                  1.30314  |                 1.19364  |
|           5 | moderately absorbing (m=1.7+0.5i) |               1.09174  |                  1.3685   |                 1.25351  |
|           5 | strongly absorbing (m=2.0+1.0i)   |               1.09174  |                  1.29837  |                 1.18927  |
|          20 | weakly absorbing (m=1.5+0.3i)     |               0.935295 |                  1.10648  |                 1.18303  |
|          20 | moderately absorbing (m=1.7+0.5i) |               0.935295 |                  1.05707  |                 1.1302   |
|          20 | strongly absorbing (m=2.0+1.0i)   |               0.935295 |                  0.964938 |                 1.03169  |
|          50 | weakly absorbing (m=1.5+0.3i)     |               0.902272 |                  0.994573 |                 1.1023   |
|          50 | moderately absorbing (m=1.7+0.5i) |               0.902272 |                  0.948386 |                 1.05111  |
|          50 | strongly absorbing (m=2.0+1.0i)   |               0.902272 |                  0.859756 |                 0.952879 |
|         100 | weakly absorbing (m=1.5+0.3i)     |               0.891163 |                  0.948931 |                 1.06482  |
|         100 | moderately absorbing (m=1.7+0.5i) |               0.891163 |                  0.90377  |                 1.01415  |
|         100 | strongly absorbing (m=2.0+1.0i)   |               0.891163 |                  0.815138 |                 0.91469  |

## Interpretation

A gray correlation necessarily reports one number per (radius, temperature); the spectral
sweep shows the real spread that number is averaging over. Where that spread is large, a
gray treatment is a coarser approximation - relevant to non-gray radiation modeling
specifically because it quantifies *how much* is lost by going gray for large fuel-sized
particles, rather than asserting it qualitatively.
