# Thermal Radiation Modeling

A non-gray thermal radiation modeling toolkit for fire/combustion applications: real
equations, tables, and benchmark metrics extracted from published papers, a 1-D discrete-
ordinates (DOM) radiative transfer solver, particle radiative-property correlations, a small
ML surrogate, and two ways to explore the results - a live interactive web dashboard and a
native Windows GUI.

The project does not manufacture synthetic spectra or fabricate benchmark numbers. Every
number quoted below is either a published, cited value or reproducibly computed by the
scripts in this repository - see [External Data Boundary](#external-data-boundary).

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
- `firemodels/fds` GitHub repository for project and implementation context.

## Quickstart

```powershell
python scripts/run_all.py        # regenerate every project's outputs
python -m pytest -q              # 61 tests: physics self-consistency, regression pins, error paths
ruff check .                     # scoped to src/scripts/tests, not the vendored submodules
black --check .
```

`pyproject.toml` declares the Python dependencies (`numpy`, `scipy`, `pandas`, `matplotlib`,
`scikit-learn`; `pytest`/`ruff`/`black` under the `dev` extra).

## Live Interactive Dashboard

The primary way to explore results is the live local web app:

```powershell
python scripts/dashboard_server.py
```

Then open the printed URL (`http://127.0.0.1:8765/`, override with the `DASHBOARD_PORT`
env var). It is a dependency-free `http.server`-based app (no Flask/Node/build step) that
serves a single-page app with:

- Real interactive charts (hover tooltips, log/linear scales) for the particle-efficiency
  sweeps, DOM heat-flux/source-term profiles, and the ML surrogate parity plot - not just
  static images.
- Sortable, filterable data tables for every generated CSV.
- `Run all` / per-project re-run buttons that trigger the underlying Python workflow and
  auto-refresh the page with the new results, so you don't need a terminal open.

Project 1's 2-D field plots stay as embedded PNGs (they're `matplotlib` heatmaps, not
re-implemented client-side). Everything is read fresh from `outputs/` on each request, so
regenerating data outside the app (e.g. `python scripts/run_all.py`) and hitting Refresh
picks it up immediately.

For a portable, offline, single-file snapshot to share (e.g. by email, no server needed),
use:

```powershell
python scripts/build_dashboard.py
```

which writes `outputs/dashboard.html` with the same figures/tables embedded as base64.

## Native Windows GUI

Build the Fortran dashboard executables:

```powershell
.\scripts\build_fortran_ui.ps1
```

Run the native Windows GUI executable:

```powershell
.\radiation_portfolio_gui.exe
```

The GUI is a Fortran/Win32 application: Fortran owns the dashboard state and reads the
generated CSV/PNG artifacts directly - a self-contained desktop app with no server and no
browser dependency. It is both a workflow launcher and a real viewer in its own right, not
just a launcher for the browser version:

- A Common-Controls-v6 manifest gives it modern themed controls (flat buttons/listbox
  instead of classic beveled Win32).
- Project 1-5's sections render the actual generated `matplotlib` PNG figures via GDI+
  (`GdipLoadImageFromFile`/`GdipDrawImageRectI`, aspect-fit into their space) and the actual
  CSV data in native `SysListView32` grid tables - not a text dump. Project 4 also gets
  stat tiles (R2/RMSE/MAPE/sample count).

Buttons:

- `Run All` regenerates every project output from inside the GUI.
- `Run Selected` regenerates the selected project and refreshes its charts/tables in place.
- `Refresh` reloads the generated artifacts into the current section.
- `Open Live` starts `scripts/dashboard_server.py` in the background (a no-op if it's
  already running) and opens the live interactive dashboard in your browser - the two are
  complementary: the native GUI for a self-contained desktop app, the browser dashboard for
  real interactivity (hover tooltips, sortable/filterable columns, a temperature selector).
- `Export HTML` writes the portable single-file `outputs\dashboard.html` snapshot.
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
For automated packaging checks, the GUI executable can also build the portable dashboard
snapshot non-interactively with:

```powershell
.\radiation_portfolio_gui.exe --export-html
```

The build script (`scripts/build_fortran_ui.ps1`) compiles the manifest resource and links
GDI+/ComCtl32/Dwmapi, then stages the gfortran runtime DLLs into both `build\` and the
project root. See the inline comments there for a toolchain quirk it works around: `windres`
silently produces no output whenever its own install path or the project path contains a
space.

## FDS/Smokeview Executable Status

The vendored Firemodels repositories (see [Vendored Firemodels Source](#vendored-firemodels-source)
below) are source/reference trees. To run actual FDS or Smokeview jobs from the GUI, install
or build the released executables and make them available on PATH. Check the local state
with:

```powershell
python scripts/check_firemodels_tools.py
```

The checker writes `outputs/firemodels_tool_status.md` and
`outputs/firemodels_tool_status.json`. See `docs/fds_6110_release_install.md` for the
FDS-6.11.0/SMV-6.11.0 Windows release target and checksum; the downloaded installer assets
live in the local-only, gitignored `Assets from Github/` folder (938 MB, not tracked - see
that doc for how to fetch them again).

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
WSGG about 43%, and Planck mean about 150% - pinned by `tests/test_published_data.py`.

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
particle absorption/scattering efficiencies fitted to Mie data. The underlying Mie solver
(`src/thermal_radiation_modeling/particles.py`) is independently verified against the
`miepython` reference library.

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
It does not claim to reproduce the paper's 2-D LBL/RCFSK benchmark. The solver couples
particle *absorption* into the local extinction coefficient but has no scattering source
term - see `docs/derivation_note.md` for that limitation in full.

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

`tests/test_surrogate.py` reproduces this exact grid/hyperparameter combination and pins the
R2 value, so a change to the shared `surrogate.py` helper can't silently drift it.

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

This workflow uses the downloaded `radcal_win_64.exe` asset and locates its Intel OpenMP
runtime (`libiomp5md.dll`) via PATH or the `RADCAL_OPENMP_DLL_DIR` env var, prepending its
folder to PATH only for the subprocess. It is a launch and parsing smoke test, not a
validation claim.

## External Data Boundary

This repository does not manufacture spectra, and does not include proprietary or
credentialed data that are not present in the workspace:

- HITEMP/HITRAN line lists must be fetched separately through HAPI or another authorized
  route - see `src/thermal_radiation_modeling/hapi_adapter.py`, which raises a clear error
  rather than fabricating data when HAPI isn't installed.
- Singh and Hostikka's supplementary RCFSK tables are referenced by DOI but not bundled here.
- The methanol paper states the RC-FSK model will be available through `firemodels/fds`; this
  repo documents that path but does not vendor a patched FDS.
- Real vegetation/char particle optical constants require FTIR measurements or published
  datasets; Johansson's coal/ash correlations are used as a defensible particle-radiation
  bridge, not as vegetation validation.

## Vendored Firemodels Source

`fds/`, `cfast/`, `smv/`, `fds-smv/`, `bot/`, `exp/`, `radcal/`, and `test_bundles/` are git
submodules pointing at the corresponding `firemodels/*` repositories (see `.gitmodules`) -
reference source trees for cross-checking implementation direction, not code this project
owns or modifies. Clone with `git clone --recurse-submodules`, or run
`git submodule update --init` after a plain clone.

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
- `fortran_ui/app.manifest`, `app.rc` - Common-Controls-v6 manifest resource for the GUI.
- `scripts/run_radcal_asset.py` - RADCAL executable smoke-test workflow using downloaded
  Firemodels assets.
- `scripts/run_project*_real_*.py` - real-data workflows.
- `scripts/_report_utils.py` - shared output-directory/report-writing helpers for the
  `run_project*` scripts.
- `scripts/_dashboard_data.py` - shared JSON-serializable data loader consumed by both
  dashboards below, so they never drift apart.
- `scripts/dashboard_server.py`, `dashboard_app.py` - the live, interactive local dashboard
  (stdlib-only HTTP server + single-page app).
- `scripts/build_dashboard.py` - the portable, single-file `outputs/dashboard.html` export.
- `scripts/check_firemodels_tools.py` - detects installed FDS/Smokeview/RADCAL executables
  and downloaded release assets.
- `docs/` - derivation notes, source maps, annotated bibliography, and FDS integration notes.
- `docs/fds_clone_scan.md` - local scan of the cloned `firemodels/fds` tree and radiation hooks.
- `outputs/` - generated reports, figures, and CSV tables (tracked in git as the
  demonstrated results; regenerate anytime with `python scripts/run_all.py`).
- `tests/` - unit tests, physics self-consistency checks, regression pins for the published
  benchmark numbers, and error-path coverage for the `ValueError` guards throughout `src/`.

## Testing Notes

- `ruff`/`black` are scoped (via `pyproject.toml`) to `src/`, `scripts/`, and `tests/` only -
  not the vendored `firemodels/*` submodules, which are someone else's code with someone
  else's style.
- Tests that reproduce ML training (`tests/test_surrogate.py`) pin against a tolerance, not
  bit-exact floats, since exact neural-net output can vary slightly across `scikit-learn`
  versions; everything else that has a known closed-form answer is pinned exactly.
