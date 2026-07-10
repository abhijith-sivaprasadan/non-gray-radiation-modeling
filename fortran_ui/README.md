# Fortran Portfolio UI

This folder contains Fortran-first dashboards for the real-data thermal radiation portfolio:

- `radiation_portfolio_ui.f90` builds a terminal dashboard and HTML exporter.
- `radiation_portfolio_gui.f90` builds a native Windows GUI `.exe` using the Win32 API from
  Fortran.

It is deliberately a standalone Fortran program rather than a Python/Streamlit app because
the Aalto posting names scientific programming, including Fortran, as an advantage and FDS is
Fortran-heavy.

## Build

```powershell
.\scripts\build_fortran_ui.ps1
```

or directly:

```powershell
gfortran -std=f2008 -Wall -Wextra -O2 -J build -o build\radiation_portfolio_ui.exe fortran_ui\radiation_portfolio_ui.f90
gfortran -std=f2008 -Wall -Wextra -O2 -J build -o build\radiation_portfolio_gui.exe fortran_ui\radiation_portfolio_gui.f90 -mwindows -luser32 -lgdi32 -lkernel32 -lshell32
```

## Run

Native Windows GUI:

```powershell
.\radiation_portfolio_gui.exe
```

The build script also leaves a copy at `build\radiation_portfolio_gui.exe`, but the root
copy is the launch-ready one because it resolves `outputs\...` relative to the project
folder.

The GUI has workflow controls:

- `Run All` runs `python scripts\run_all.py`.
- `Run Selected` runs the selected project workflow.
- `Export HTML` writes `outputs\fortran_gui_dashboard.html`.
- `Open HTML` opens the exported file with an absolute path.
- `Outputs` opens the output folder.

Interactive mode:

```powershell
.\build\radiation_portfolio_ui.exe
```

Non-interactive summary:

```powershell
.\build\radiation_portfolio_ui.exe --summary
```

Generate an HTML dashboard:

```powershell
.\build\radiation_portfolio_ui.exe --html
```

The HTML file is written to `outputs/fortran_dashboard.html`.
The GUI export button writes `outputs/fortran_gui_dashboard.html`.
The GUI executable also supports an automated export mode:

```powershell
.\radiation_portfolio_gui.exe --export-html
```
