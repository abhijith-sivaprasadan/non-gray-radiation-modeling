# FDS Clone Scan

This note records what was found in the local FDS clone under
`E:\Thermal Radiation Modeling\fds` and how it can support this portfolio.

## What The Clone Is

The clone is the `firemodels/fds` codebase for Fire Dynamics Simulator and
Smokeview. The root README describes FDS as a large-eddy simulation code for
low-speed flows, smoke, and heat transport from fires. The FDS source README
states that the source code is Fortran 2018 compliant and that `Source\main.f90`
is the controlling program.

The local clone contains:

- `Source\*.f90`: 33 Fortran source files.
- `Source\radi.f90`: the radiation heat-transfer implementation.
- `Source\rcal.f90`: RADCAL-related gas absorption calculations.
- `Source\part.f90`: Lagrangian particle implementation.
- `Source\vege.f90`: vegetation and wildland-fire structures.
- `Verification\Radiation\*.fds`: 73 radiation verification cases.
- `Verification\WUI\*radi*.fds`: gas/vegetation radiation consistency examples.

## Radiation Entry Points

`Source\radi.f90` contains the most relevant existing implementation points:

- `MODULE SPECDATA`: spectral-property data.
- `MODULE WSGG_ARRAYS`: WSGG parameter arrays.
- `MODULE MIEV`: Mie scattering and absorption machinery.
- `SUBROUTINE MEAN_CROSS_SECTIONS`: mean particle cross sections by radiation
  band and particle size group.
- `MODULE RAD`: main radiation heat-transfer module.
- `SUBROUTINE INIT_RADIATION`: radiation-array and property-table setup.
- `SUBROUTINE COMPUTE_RADIATION`: top-level per-mesh radiation call.
- `SUBROUTINE RADIATION_FVM`: finite-volume radiation transport solver.

The relevant local lines inspected in `radi.f90` show RADCAL gas absorption
tables, WSGG model branches, particle absorption/scattering work arrays, and
FVM radiation coupling to gas, wall, particle, and geometry fields.

## How We Can Use It

This portfolio should not claim to be a patched FDS branch yet. The practical
use is to align our standalone work with FDS:

- Treat `Source\radi.f90` as the implementation map for future non-gray
  radiation work.
- Use the Python workflows as reproducible data-generation/reporting steps.
- Use the native Fortran GUI as the launcher and review surface for generated
  artifacts.
- Add future Fortran kernels with FDS-like inputs and outputs before attempting
  an actual FDS patch.
- Use FDS radiation and WUI verification cases as future benchmark candidates.

See `docs/firemodels_repo_scan.md` for the broader local scan of the additional
Firemodels repositories now present in `E:\Thermal Radiation Modeling`,
including `radcal`, `exp`, `smv`, `cfast`, `bot`, `fds-smv`, and
`test_bundles`.
