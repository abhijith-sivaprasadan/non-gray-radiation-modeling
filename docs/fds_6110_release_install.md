# FDS 6.11.0 / Smokeview 6.11.0 Release Target

The current official release target for this portfolio is the Firemodels
`FDS-6.11.0_SMV-6.11.0` package. The GitHub release page marks it as `Latest`,
with tag `FDS-6.11.0`, commit `369a20b`, and release date 18 May 2026.

## Windows Installer

- Release page: <https://github.com/firemodels/fds/releases/tag/FDS-6.11.0>
- Windows installer:
  <https://github.com/firemodels/fds/releases/download/FDS-6.11.0/FDS-6.11.0_SMV-6.11.0_win.exe>
- File name: `FDS-6.11.0_SMV-6.11.0_win.exe`
- Listed size: 174 MB
- Expected SHA256:
  `b42281eb73b92a948fe21e80b22089da99c50574103d17c4d4ff609290a0ddb2`

The cloned `fds`, `smv`, and `radcal` repositories are valuable source and
reference trees, but they are not the same thing as an installed executable
toolchain. The Fortran GUI can run the project workflows now; running actual
FDS cases from the GUI requires `fds.exe` to be installed or built and available
on PATH. Opening Smokeview output requires the Smokeview executable as well.

## Downloaded Assets Folder

The local asset folder is:

```text
E:\Thermal Radiation Modeling\Assets from Github
```

Detected high-value assets:

- `FDS\FDS-6.11.0_SMV-6.11.0_win.exe`: official FDS/SMV Windows installer.
  Its SHA256 matches the release checksum above.
- `RADCAL\radcal_win_64.exe`: standalone Windows RADCAL executable asset.
  It requires Intel OpenMP runtime `libiomp5md.dll`. The project wrapper
  `scripts/run_radcal_asset.py` finds a local copy of that DLL and prepends its
  folder to PATH for the RADCAL subprocess.
- `SmokeView\SMV-6.11.1_win.exe`: separate Smokeview Windows installer asset.
- `FDS\FDS_User_Guide.pdf`, `FDS_Technical_Reference_Guide.pdf`,
  `FDS_Verification_Guide.pdf`, and `FDS_Validation_Guide.pdf`: local docs
  useful for GUI-integrated examples and validation notes.

## Local Status Check

Run:

```powershell
python scripts/check_firemodels_tools.py
```

This writes:

- `outputs/firemodels_tool_status.json`
- `outputs/firemodels_tool_status.md`

The checker looks for:

- `fds.exe` / `fds`
- `smokeview.exe` / `smv.exe`
- `radcal.exe` / `radcal_win_64.exe` / `radcal`
- the official Windows installer in the project root, Downloads, the `E:`
  project folder, and nested `Assets from Github\FDS` folders
- downloaded RADCAL and Smokeview assets
- local source repositories under the current project root and
  `E:\Thermal Radiation Modeling`

## GUI Implication

Until `fds.exe` is detected, the GUI should keep using its current reliable
workflow buttons:

- `Run All`
- `Run Selected`
- `Refresh`
- `Export HTML`
- `Open HTML`
- `Outputs`

Once FDS and Smokeview are installed, the next clean extension is to add a
Fortran GUI section that lets the user choose a small `.fds` case, run `fds.exe`
from the GUI, and open generated Smokeview results.

RADCAL can already be smoke-tested from the GUI through the "Project 5: RADCAL
asset smoke test" section. It writes outputs under `outputs\project5_radcal_asset`.
