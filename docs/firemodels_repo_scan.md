# Firemodels Repository Scan

Local scan target: `E:\Thermal Radiation Modeling`.

## Local Clones Found

| Repo | Remote | Local role |
| --- | --- | --- |
| `fds` | `https://github.com/firemodels/fds.git` | Main Fire Dynamics Simulator Fortran codebase. |
| `radcal` | `https://github.com/firemodels/radcal.git` | Radiative properties of gaseous species and soot. |
| `smv` | `https://github.com/firemodels/smv.git` | Smokeview visualization source code. |
| `cfast` | `https://github.com/firemodels/cfast.git` | Zone fire model related to FDS/Smokeview. |
| `exp` | `https://github.com/firemodels/exp.git` | Fire Research Division experimental database. |
| `fds-smv` | `https://github.com/firemodels/fds-smv.git` | FDS/Smokeview website and documentation pages. |
| `bot` | `https://github.com/firemodels/bot.git` | Build, verification, and bundle automation scripts. |
| `test_bundles` | `https://github.com/firemodels/test_bundles.git` | Release/test bundle metadata and scripts. |

The GitHub organization also lists `out`, `fig`, `cor`, `cad`, and
`fds-smv_deprecated`, but those folders were not present in the local project
folder during this scan.

## Counts And Useful Assets

| Area | Local evidence |
| --- | --- |
| FDS source | 33 `fds\Source\*.f90` files. |
| FDS radiation cases | 73 `fds\Verification\Radiation\*.fds` input files. |
| FDS WUI radiation cases | 3 `fds\Verification\WUI\*radi*.fds` input files. |
| FDS deep fuel bed validation | 110 `fds\Validation\USFS_Deep_Fuel_Beds\FDS_Input_Files\*.fds` files. |
| RADCAL source | `Source\main.f90`, `Source\rcal.f90`, `Source\rmod.f90`. |
| RADCAL methanol evidence | `SUBROUTINE CH3OH` in `radcal\Source\rcal.f90`, plus methanol verification PDFs. |
| EXP deep fuel bed data | `exp\USFS_Deep_Fuel_Beds\exp_params.csv` has 110 rows. |
| Waterloo methanol data | `exp\Waterloo_Methanol` points to `Submodules\macfp-db`, but that submodule content was not populated locally. |

No `fds`, `smokeview`, `smv`, or `radcal` executable was found on PATH or in
the local clones. The repositories are usable now as source/reference/data
assets; running full FDS, Smokeview, or RADCAL workflows from the GUI requires
building or installing the corresponding executables.

## Relevance To This Portfolio

### Highest Value

`radcal` is the strongest new repo for the non-gray radiation portfolio. Its
README states that it computes spectral properties of participating gaseous
species and soot and returns Planck mean and path/effective mean absorption
coefficients by spectral band. The source exposes:

- `MODULE RADCAL_VAR`
- `MODULE RADCAL_CALC`
- `SUBROUTINE INIT_RADCAL`
- `SUBROUTINE SUB_RADCAL`
- species routines including `CH3OH` for methanol

This directly supports the methanol RC-FSK/FDS paper and explains the gas
property side of FDS radiation modelling.

`fds` remains the main implementation target. The key files are:

- `fds\Source\radi.f90`: radiation heat transfer, WSGG arrays, Mie machinery,
  RADCAL lookup table integration, FVM radiation solve.
- `fds\Source\rcal.f90`: RADCAL-related gas absorption calculations.
- `fds\Source\part.f90`: Lagrangian particle implementation.
- `fds\Source\vege.f90`: vegetation and wildland-fire structures.

`exp` is the strongest validation-data repo. The most relevant populated local
dataset for the Aalto posting is `USFS_Deep_Fuel_Beds`, because it connects to
wildland fuels, fuel spacing/depth/moisture, spread, and burn percentage.

### Supporting Value

`smv` is useful for visualization once Smokeview is built or installed. The
current local clone does not include a ready-to-run Smokeview binary.

`cfast` is useful as broader fire-modelling context, but it is not the primary
non-gray radiation implementation target.

`fds-smv`, `bot`, and `test_bundles` are useful for documentation, automation,
and understanding the upstream release/test workflow. They are not immediate
physics inputs for the portfolio.

## Practical Next Steps

1. Add a RADCAL-focused project workflow: parse a small `RADCAL.IN` case,
   document available species, and compare RADCAL Planck/path means with the
   simplified H2O and methanol portfolio correlations.
2. Add a USFS Deep Fuel Beds data workflow: summarize the 110 experimental
   cases and connect spacing/depth/moisture to burn/spread outcomes.
3. Extend the Fortran GUI with a "Firemodels Repos" view that reports the
   presence/status of `fds`, `radcal`, `exp`, and `smv`.
4. Only add "Run FDS" or "Open Smokeview" buttons after validated executables
   are available locally.

