# Project 2 Report: Published Particle Property Correlations

This workflow now uses Johansson's published gray particle correlations fitted to Mie
calculations, not a placeholder refractive-index curve.

Primary source:

R. Johansson, Efficient treatment of non-grey radiative properties of particles and gases in modelling of radiative heat transfer in combustion environments, International Journal of Heat and Mass Transfer 108 (2017) 519-528.

DOI: https://doi.org/10.1016/j.ijheatmasstransfer.2016.12.042

## Encoded Data

- Johansson Eq. (8): `1 / y^z = 1 / y0^z + 1 / y_inf^z`.
- Table 1 coal/char gray absorption and scattering efficiencies.
- Table 2 ash1 and ash2 gray absorption and scattering efficiencies.

The Aalto THERAD page is also relevant because it explicitly frames Mie absorption and
scattering cross sections as the design tool for spectrally selective particle coatings:
https://blogs.aalto.fi/fire/therad/

## Interpretation

These correlations are closer to the doctoral topic than the earlier soot-like placeholder:
they are particle-property approximations derived from Mie data and intended for combustion
radiation calculations. They are still not vegetation-specific optical constants, so the
next research step is FTIR characterization of real fuel particles.
