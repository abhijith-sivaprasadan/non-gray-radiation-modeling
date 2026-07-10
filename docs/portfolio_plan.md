# Five-Week Portfolio Plan

Dates: **10 July 2026 to 15 August 2026**.

The strategic choice is depth over volume. Projects 1 and 3 are the core evidence. Project 2
is an illustrative bridge to fuel particles. Project 4 is optional.

Implementation status in this repository: Projects 1-4 now have runnable scripts, tests,
reports, figures, and CSV outputs based on published equations/tables/metrics from the
supplied papers. The remaining upgrade is reproducing the underlying HITEMP/HITRAN line-list
calculations and obtaining verified vegetation/char optical constants.

## Week 1: 10-16 July 2026

- Read the 2021 Sadeghi, Hostikka, Fraga, and Bordbar paper twice.
- Reproduce the governing equations by hand:
  - radiative transfer equation,
  - total emissivity integral,
  - WSGG emissivity sum,
  - polynomial temperature weights,
  - species superposition,
  - DOM discretization.
- Read the relevant chapters in Modest, *Radiative Heat Transfer*.
- Read the key Hostikka/Bordbar/Fraga group papers for WSGG and LBL validation context.
- Set up Python tooling for `numpy`, `scipy`, `pandas`, `matplotlib`, HAPI, and a Mie library.
- Send a short outreach email to Professor Hostikka during this week.

Deliverable: derivation note, annotated bibliography, and working local toolchain.

## Weeks 2-3: 17-30 July 2026

Project 1: HAPI line-by-line to WSGG fit.

- Start with one accessible species, preferably CO or CO2 depending on line-list size.
- Compute high-resolution absorption coefficients over a fire-relevant temperature grid.
- Compute Planck-weighted total emissivity over path lengths spanning roughly 0.01-10 atm m.
- Fit a 4-gray-gas plus transparent-gas WSGG model with fifth-order temperature weights.
- Compare the fitted emissivity surface against the LBL surface.

Deliverable: notebook/report with emissivity surfaces, fitted coefficients, and error table.

## Weeks 3-4: 24 July-6 August 2026

Project 3: 1-D discrete ordinates RTE solver.

- Validate a gray pure-absorption case first.
- Add WSGG property treatment.
- Compare gray, WSGG, and LBL-style property treatments on the same temperature profile.
- Report radiative heat flux and source-term differences.

Deliverable: solver, verification tests, and one concise figure set.

## Week 4: 31 July-6 August 2026

Project 2: particle radiative properties.

- Reproduce the Rayleigh-limit logic used for soot-like particles.
- Use a Mie package for larger spherical particles only after the Rayleigh case is understood.
- Combine gas absorption and particle absorption in the 1-D solver as a demonstrator.

Deliverable: short note and plots of size parameter, absorption efficiency, and absorption
coefficient with caveats.

## Week 5: 7-15 August 2026

Project 4: optional ML surrogate and application package.

- Train a small surrogate only if Projects 1 and 3 are already stable.
- Predict emissivity or WSGG coefficients from thermodynamic inputs.
- Compare speed and error against direct LBL-derived evaluation.
- Finalize README, project summary, CV, motivation letter, thesis summary, and referee list.

Deliverable: clean repository and complete application package before **15 August 2026**.
