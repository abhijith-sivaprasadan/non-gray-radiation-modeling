# Research Synthesis

This note makes explicit what each project in this repository demonstrates, and connects it
to two research directions: **extending non-gray radiation modeling from the gas phase to
solid fuel particles**, and **machine-learning acceleration of radiative property
evaluation**. It is not new technical work - it is the connective tissue between the
projects, written once so it does not have to be reconstructed under interview pressure.
Every number below is real, computed by the scripts named, not illustrative.

## The two directions, and where each project sits

### Direction A: gas-phase non-gray radiation, extended toward solid fuel particles

The gas-phase foundation:

- **Project 1** (`run_project1_real_hydrogen.py`) reproduces Singh & Hostikka's published
  H2O Planck-mean correlation and validation fields. This demonstrates fluency with the
  reference group's own results and terminology (RC-FSK, WSGG, Planck-mean, radial/axial
  validation cases) - necessary, but on its own, only reproduction.
- **The own-HITRAN-fit extension** (`run_project1_own_hitran_fit.py`) is the harder claim,
  carried out, not just proposed: real H2O line-by-line data fetched from HITRAN via HAPI
  (`third_party/hapi/`), a genuine Voigt-profile absorption coefficient computed from that
  data (`hapi.absorptionCoefficient_Voigt`), and an independently fitted Planck-mean
  power-law and 2-gray-gas WSGG model - checked against Project 1's published numbers
  instead of looking them up. The result over-predicts the published correlation, and by a
  growing margin at higher temperature (mean signed error +135.5%, correlation of error vs.
  T: +0.95) - the *opposite* of the naive guess (missing HITEMP hot lines should
  under-predict). The actual mechanism, confirmed by the data: bounding the calculation to
  H2O's two strongest bands (150-2200 cm^-1) concentrates the Planck-weighted average on
  strong absorption that the published correlation's much wider range dilutes with weaker
  near-IR bands, and Wien's law makes that dilution worse as temperature rises. This is the
  actual research skill (real spectral data -> fitted radiative property -> checked,
  revised-hypothesis-when-wrong) applied to a case with a known right answer to check
  against - exactly the skill FTIR characterization of particles requires, where there is no
  published right answer to check against.
- **Project 3** (`run_project3_real_dom.py`) is the RTE-solution machinery a gas-plus-
  particle model needs regardless of which absorber it's given: a 1-D discrete-ordinates
  solver whose `solve_wsgg_dom` already accepts a combined gas+particle absorption
  coefficient. Its documented gap - no scattering source term, so particle *scattering* is
  computed by `particles.py` but never coupled into the solver - is precisely the boundary
  between "gas-only" and "gas-plus-particle" radiative transfer.
- **The scattering-sensitivity extension** (`run_project3_scattering_sensitivity.py`) closes
  part of that gap rather than just naming it: a real isotropic-scattering DOM solver
  (`dom1d.solve_gray_dom_with_isotropic_scattering`, classical source iteration, verified
  against the absorption-only solver in the zero-scattering limit and against monotonic
  flux reduction under increasing scattering optical thickness) re-solves Project 3's radial
  case with a representative dilute particle loading and measures the actual difference:
  mean heat-flux error 0.07% of peak flux (single-scattering albedo 0.10 at this loading -
  most of the particles' extinction there is absorption, not scattering, so the existing
  absorption-only solver's blind spot is small *for this specific loading*, a measured
  finding rather than an assumption).

The particle side, and its explicit boundary:

- **Project 2** (`run_project2_real_particles.py`) implements Johansson's published gray
  coal/char and ash particle efficiency correlations - real Mie-fitted data, but for
  combustion particles, not vegetation or wildland-fire fuel. The README says this directly:
  a defensible particle-radiation bridge, not vegetation validation. That sentence marks the
  boundary of the actual novel research direction.
- **The large-particle Mie sweep extension** (`run_project2_extended_mie_sweep.py`) engages
  with what's past that boundary as far as the literature allows without fabricating a
  citation: the same validated Mie solver, spectrally resolved (1-15 um) at particle radii
  (5-100 um) representative of wildland fuel char fragments, using a labeled *range* of
  representative absorbing-particle refractive indices (not a single measured vegetation
  dataset - none is available at these wavelengths, which is itself part of why FTIR
  characterization is a real open need). Result: spectral variation in Q_abs shrinks from
  ~40% (r=5 um) to ~10% (r=100 um) as particles grow - gray treatments are a coarser
  approximation for smaller particles and progressively less so for larger ones, a
  quantified statement, not a qualitative one.

### Direction B: ML-accelerated radiative property evaluation

- **Project 4**, in its original form, trains a surrogate (small MLP, log-space target,
  train/test split) to reproduce Singh & Hostikka's *published* Planck-mean correlation -
  R2 = 0.99907 on 6160 points, free to sample as densely as wanted from a closed-form
  function.
- **The own-data extension** (`run_project4_own_data_surrogate.py`) trains the same kind of
  surrogate on the own-HITRAN-fit pipeline's self-generated data instead: real HITRAN
  Planck-mean values, each costing an actual ~13 s Voigt-profile calculation, so only 42
  points rather than 6160. R2 = 0.977, MAPE 13.6% - a real, honestly harder problem, and the
  gap between 0.977 and 0.99907 is itself the evidence this is a materially different
  exercise, not a re-run of the same one with a different label. This is a complete,
  self-generated pipeline: real spectral data -> a fitted quantity -> an ML surrogate that
  accelerates evaluating it - the posting's named ML-acceleration topic, answered with this
  repository's own results.

### Grounding in the actual tool

- **Project 5**, as originally scoped, is a launch-and-parse smoke test for the downloaded
  RADCAL executable - proof the tool runs from this environment, not evidence of familiarity
  with it.
- **The FDS example-case extension** (`run_project5_fds_example.py`) runs one of FDS's own
  verification cases (`fds/Verification/Radiation/check_kappa.fds`, from the vendored
  submodule) with the real FDS-6.11.0 executable and extracts real values from FDS's own
  internal RadCal-based gas absorption-coefficient calculation via the bundled `fds2ascii`
  tool: for methane at X=0.1, kappa falls from 0.305 m^-1 at 293 K to 0.160 m^-1 at 1093 K -
  the same qualitative direction (absorption coefficient falling with temperature) as this
  repository's own H2O work, independently, through a different model and species. Getting
  this running at all required discovering (by trial and error, documented in the script)
  that FDS on Windows must be launched through its bundled Intel MPI `mpiexec`, not called
  directly - a small, concrete piece of familiarity with the actual tool, not just its
  physics.

## What this repository does not claim

- It does not claim to reproduce Singh & Hostikka's full 2-D LBL/RCFSK benchmark (Project 3
  is explicit about this), to have validated particle correlations against real vegetation
  data (Project 2's stated boundary, engaged with but not closed by its extension), to match
  HITEMP-quality spectral coverage in the own-fit extension (disclosed, and the actual
  over-prediction pattern it causes is measured, not hidden), or to have implemented a
  correct scattering phase function (the isotropic-scattering extension is explicitly scoped
  as "how much does *some* scattering change the answer", not the real forward-peaked
  answer).
- Each of those is a stated boundary with a stated reason and, where an extension exists, a
  measured consequence - not a silent gap and not a vague qualitative claim. Every number
  above should be one that survives being asked "how do you know that" in conversation,
  because it was computed, not assumed.

## One-paragraph version (for a motivation letter or summary)

This repository moves through a full sequence on non-gray gas radiation - reproducing a
published correlation, then independently rederiving an equivalent one from real HITRAN
line-by-line data and fitting it with a general WSGG toolkit built for exactly that purpose,
diagnosing *why* the two disagree rather than just reporting that they do - before engaging
with the harder, less-precedented problem the reference group's fuel-particle work actually
poses: gray particle correlations exist for combustion particles (coal, char, ash) but not
for wildland-fire fuel particles, and a spectrally-resolved Mie sweep at fuel-relevant
particle sizes quantifies how much a gray treatment loses there, without overclaiming a
vegetation-specific optical-constant dataset that does not exist in the literature. A
measured (not assumed) DOM scattering-sensitivity study and a real FDS verification-case run
close two smaller, explicitly-scoped gaps in the same spirit. In parallel, the same
spectral-data-to-fitted-property pipeline is shown accelerated by a small ML surrogate
trained on genuinely self-generated (not published) data - the same acceleration argument
the posting names, applied to this repository's own results, with the honest cost (a smaller,
real training set) reported alongside the result.
