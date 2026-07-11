# Project 5 Extension: A Real FDS Verification Case

`fds/Verification/Radiation/check_kappa.fds` is one of FDS's own verification cases - not
downloaded from a paper, and not the RADCAL smoke test's launch-and-parse check. This runs
it with the real FDS-6.11.0 executable and extracts real gas absorption-coefficient values
(FDS's own internal RadCal-based gray-gas calculation) via the bundled `fds2ascii` tool.

## The Case

A 10x10 grid of methane/air mixtures (mass fraction 0.1-1.0, temperature 20-920 C, 1%
background O2), each in its own small mesh block, with an `ABSORPTION COEFFICIENT` slice
output per block. This script extracts the X_CH4=0.1 column across
temperature (5 of the 10 available points) rather than the full grid, to keep the
per-slice `fds2ascii` interaction tractable.

## Result

|   slice_index |   temperature_c |   temperature_k |   mass_fraction_ch4 |   fds_absorption_coefficient_m-1 |
|--------------:|----------------:|----------------:|--------------------:|---------------------------------:|
|             1 |              20 |          293.15 |                 0.1 |                          0.30522 |
|            21 |             220 |          493.15 |                 0.1 |                          0.30157 |
|            41 |             420 |          693.15 |                 0.1 |                          0.27274 |
|            61 |             620 |          893.15 |                 0.1 |                          0.231   |
|            81 |             820 |         1093.15 |                 0.1 |                          0.16048 |

At X_CH4=0.1, FDS's own RadCal-based absorption coefficient falls from
0.3052 m^-1 at 293 K
to 0.1605 m^-1 at 1093
K - the same qualitative direction (absorption coefficient falling with temperature) as this
repository's own H2O Planck-mean work in Project 1 and its own-HITRAN-fit extension, though
for a different species (methane vs. water vapor) computed through a different model
(FDS's internal RadCal gray-gas treatment vs. a direct Voigt-profile HITRAN calculation) -
not a quantitative validation of one against the other, but the same underlying physical
trend (higher temperature broadens and redistributes absorption lines, generally reducing a
gray or Planck-mean absorption coefficient) showing up independently in both.

Full data in `tables/fds_kappa_temperature_sweep.csv`; figure in
`figures/fds_kappa_temperature_sweep.png`; raw FDS run log in `fds_run_stdout.log`.

## Notes on Running FDS on Windows

`fds.exe` must be launched through its bundled Intel MPI `mpiexec.exe` (even for a single
process) with both `bin/` and `bin/mpi/` on `PATH` - calling `fds.exe` directly fails
silently (nonzero exit, no output). See `_run_fds` in this script for the exact invocation.
