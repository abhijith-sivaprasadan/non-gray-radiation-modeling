# Thermal Radiation Modeling Portfolio

This repository implements a real-data portfolio for the Aalto University opening
**Doctoral Researcher in Non-gray Thermal Radiation Modelling, R47351**.

The earlier placeholder-spectra workflow has been removed from the default project path.
The current scripts use equations, tables, benchmark metrics, and implementation facts
extracted from supplied papers by Hostikka's research group and supporting
particle-radiation literature.

## Verified Posting Facts

The pasted Aalto Workday posting confirms:

- Location: Otaniemi, Espoo, Finland, with regular on-site presence.
- Supervisor: Professor Simo Hostikka, Fire Safety Engineering group.
- Application deadline: **15 August 2026**.
- Preferred start: **December 2026 / January 2027**.
- Starting salary: **3143 EUR/month gross**.
- Research scope: non-gray multi-phase radiation models, fuel particles in wildland fires,
  FTIR characterization, Fire Dynamics Simulator implementation, validation, and machine
  learning acceleration.

## Source Basis

The implemented real-data fixtures come from:

- Singh and Hostikka, *Applied Thermal Engineering* 294 (2026) 130593:
  hydrogen/H2O non-gray model, HITEMP-based Planck-mean correlation, radial and axial
  validation fields, model-error tables, CPU timing, and wall-emission error metrics.
- Rashidzadeh et al., *Fire Safety Journal* 160 (2026) 104606:
  RC-FSK implementation in FDS, methanol pool-fire PMC-LBL comparison metrics, HITEMP
  spectral settings, and global radiant-fraction table.
- Hostikka and Rashidzadeh, *Fire Safety Journal* 161 (2026) 104677:
  fire-CFD radiation-model review and FDS-focused engineering context.
- Johansson, *International Journal of Heat and Mass Transfer* 108 (2017) 519-528:
  Mie-fitted gray coal/char and ash particle correlations.
- Aalto THERAD page and `firemodels/fds` GitHub repository for project and implementation
  context.

## Run Everything

```powershell
python scripts/run_all.py
python -m pytest -q
ruff check .
black --check .
```

## Fortran UI and Windows GUI

Build the Fortran dashboard executables:

```powershell
.\scripts\build_fortran_ui.ps1
```

Run the native Windows GUI executable:

```powershell
.\radiation_portfolio_gui.exe
```

The GUI is a Fortran/Win32 application, following the same native-executable direction as
the referenced `E:\thermotwin-f` project: Fortran owns the dashboard state and reads the
generated CSV artifacts directly. The build script also stages common gfortran runtime DLLs
into both `build\` and the project root for easier transfer and double-click launching.

The GUI is now a workflow launcher, not just a viewer:

- `Run All` regenerates every project output from inside the GUI.
- `Run Selected` regenerates the selected project.
- `Refresh` reloads the generated artifacts.
- `Export HTML` writes `outputs\fortran_gui_dashboard.html`.
- `Open HTML` opens the exported report with an absolute Windows path.
- `Outputs` opens the generated outputs folder.

Run the interactive terminal UI:

```powershell
.\build\radiation_portfolio_ui.exe
```

Non-interactive summary and HTML export:

```powershell
.\build\radiation_portfolio_ui.exe --summary
.\build\radiation_portfolio_ui.exe --html
```

The terminal HTML dashboard is written to `outputs/fortran_dashboard.html`.
The GUI export button writes `outputs/fortran_gui_dashboard.html`.
For automated packaging checks, the GUI executable can also write the same export with:

```powershell
.\radiation_portfolio_gui.exe --export-html
```

## FDS/Smokeview Executable Status

The cloned Firemodels repositories are source/reference trees. To run actual FDS or
Smokeview jobs from the GUI, install or build the released executables and make them
available on PATH. Check the local state with:

```powershell
python scripts/check_firemodels_tools.py
```

The checker writes `outputs/firemodels_tool_status.md` and
`outputs/firemodels_tool_status.json`. See `docs/fds_6110_release_install.md` for the
FDS-6.11.0/SMV-6.11.0 Windows release target, checksum, and the downloaded
`E:\Thermal Radiation Modeling\Assets from Github` asset folder.

## Project 1: Published Hydrogen/H2O Radiation Data

Command:

```powershell
python scripts/run_project1_real_hydrogen.py
```

Outputs:

- `outputs/project1_real_hydrogen/tables/radial_case_fields.csv`
- `outputs/project1_real_hydrogen/tables/axial_case_fields.csv`
- `outputs/project1_real_hydrogen/tables/singh_table1_thermodynamic_grid.csv`
- `outputs/project1_real_hydrogen/tables/singh_table2_cpu_times.csv`
- `outputs/project1_real_hydrogen/tables/singh_table3_wall_emission_errors.csv`
- `outputs/project1_real_hydrogen/tables/singh_model_error_summary.csv`
- `outputs/project1_real_hydrogen/figures/*_fields.png`
- `outputs/project1_real_hydrogen/project1_report.md`

Encoded equation:

```text
kappa_planck = X_H2O * 3.8821e6 * T^-1.9811
```

Published error summary includes RC-FSK source peak error below 14% in the radial case,
WSGG about 43%, and Planck mean about 150%.

## Project 2: Published Particle Correlations

Command:

```powershell
python scripts/run_project2_real_particles.py
```

Outputs:

- `outputs/project2_real_particles/tables/johansson_correlation_parameters.csv`
- `outputs/project2_real_particles/tables/johansson_particle_efficiencies.csv`
- `outputs/project2_real_particles/figures/johansson_radius_sweep_1500K.png`
- `outputs/project2_real_particles/figures/johansson_temperature_sweep_20um.png`
- `outputs/project2_real_particles/project2_report.md`

This implements Johansson's Eq. (8) and Tables 1-2 for coal/char, ash1, and ash2 gray
particle absorption/scattering efficiencies fitted to Mie data.

## Project 3: DOM on Published Fields

Command:

```powershell
python scripts/run_project3_real_dom.py
```

Outputs:

- `outputs/project3_real_dom/tables/radial_midline_dom_profile.csv`
- `outputs/project3_real_dom/tables/axial_centerline_dom_profile.csv`
- `outputs/project3_real_dom/tables/published_model_error_summary.csv`
- `outputs/project3_real_dom/figures/published_field_dom_profiles.png`
- `outputs/project3_real_dom/project3_report.md`

This is a transparent 1-D DOM exercise on the published radial/axial thermodynamic fields.
It does not claim to reproduce the paper's 2-D LBL/RCFSK benchmark.

## Project 4: ML Surrogate on Published Correlation

Command:

```powershell
python scripts/run_project4_real_surrogate.py
```

Outputs:

- `outputs/project4_real_surrogate/tables/surrogate_training_grid.csv`
- `outputs/project4_real_surrogate/tables/surrogate_predictions.csv`
- `outputs/project4_real_surrogate/tables/surrogate_metrics.csv`
- `outputs/project4_real_surrogate/figures/surrogate_kappa_parity.png`
- `outputs/project4_real_surrogate/project4_report.md`

Current metrics:

| target | R2 | RMSE log10 | MAPE kappa |
| --- | ---: | ---: | ---: |
| log10(kappa_planck) | 0.99907 | 0.02162 | 0.03201 |

## Project 5: RADCAL Asset Smoke Test

Command:

```powershell
python scripts/run_radcal_asset.py
```

Outputs:

- `outputs/project5_radcal_asset/RADCAL.IN`
- `outputs/project5_radcal_asset/RADCAL.OUT`
- `outputs/project5_radcal_asset/TRANS_PORTFOLIO_RADCAL_SMOKE_TEST.TEC`
- `outputs/project5_radcal_asset/radcal_summary.csv`
- `outputs/project5_radcal_asset/radcal_run_report.md`

This workflow uses the downloaded `radcal_win_64.exe` asset and automatically prepends a
locally installed `libiomp5md.dll` folder to PATH for the subprocess. It is a launch and
parsing smoke test, not a validation claim.

## External Data Boundary

This repository no longer manufactures spectra. It also does not include proprietary or
credentialed data that are not present in the workspace:

- HITEMP/HITRAN line lists must be fetched separately through HAPI or another authorized
  route.
- Singh and Hostikka's supplementary RCFSK tables are referenced by DOI but not bundled here.
- The methanol paper states the RC-FSK model will be available through `firemodels/fds`; this
  repo documents that path but does not vendor FDS.
- Real vegetation/char particle optical constants require FTIR measurements or published
  datasets; Johansson's coal/ash correlations are used as a defensible particle-radiation
  bridge, not as vegetation validation.

## Repository Layout

- `src/thermal_radiation_modeling/published_data.py` - paper-extracted equations, tables,
  and metrics.
- `src/thermal_radiation_modeling/particles.py` - Rayleigh/Mie helpers plus Johansson
  published particle correlations.
- `src/thermal_radiation_modeling/dom1d.py` - 1-D DOM solver, including a WSGG-coupled sweep
  (`solve_wsgg_dom`) that sums per-gray-gas DOM solves weighted by a `WSGGModel`.
- `src/thermal_radiation_modeling/wsgg.py`, `fitting.py`, `io.py` - a general WSGG toolkit
  (model evaluation, penalized least-squares coefficient fitting, and CSV round-tripping),
  covered by unit tests but not yet wired into a numbered project: fitting a WSGG model
  needs a real target emissivity table (e.g. an HITEMP-derived RCFSK/WSGG grid), and this
  repository does not fabricate one. This toolkit is held ready for that step once the
  HAPI/HITEMP extension in `hapi_adapter.py` is configured.
- `src/thermal_radiation_modeling/surrogate.py` - MLP surrogate training helper, used by
  Project 4.
- `src/thermal_radiation_modeling/hapi_adapter.py` - explicit HAPI/HITEMP extension hooks.
- `fortran_ui/radiation_portfolio_ui.f90` - Fortran terminal and HTML dashboard.
- `fortran_ui/radiation_portfolio_gui.f90` - native Windows Fortran/Win32 GUI dashboard.
- `scripts/run_radcal_asset.py` - RADCAL executable smoke-test workflow using downloaded
  Firemodels assets.
- `scripts/run_project*_real_*.py` - real-data workflows.
- `docs/` - posting brief, derivation note, source map, FDS notes, and application checklist.
- `docs/fds_clone_scan.md` - local scan of the cloned `firemodels/fds` tree and radiation hooks.
- `outputs/` - generated reports, figures, and CSV tables.

## AI-Assisted Coding Disclosure

Use a consistent, honest disclosure:

> Problem formulation, choice of methods, decision variables, validation design, and
> interpretation are my own; I used AI-assisted coding tools to help implement portions of
> the code, and I have personally verified the results against published benchmarks.
