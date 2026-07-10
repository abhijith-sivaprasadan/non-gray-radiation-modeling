# Firemodels Tool Status

Generated UTC: `2026-07-10T22:17:11+00:00`

## Official Release Target

- Release: [FDS-6.11.0_SMV-6.11.0](https://github.com/firemodels/fds/releases/tag/FDS-6.11.0)
- Tag: `FDS-6.11.0`
- Commit: `369a20b`
- Windows installer: [`FDS-6.11.0_SMV-6.11.0_win.exe`](https://github.com/firemodels/fds/releases/download/FDS-6.11.0/FDS-6.11.0_SMV-6.11.0_win.exe)
- Expected SHA256: `b42281eb73b92a948fe21e80b22089da99c50574103d17c4d4ff609290a0ddb2`

## Executable Detection

| Tool | PATH result | Local executable search |
| --- | --- | --- |
| FDS solver | `C:\Program Files\firemodels\FDS6\bin\fds.exe` | `C:\Program Files\firemodels\FDS6\bin\fds.exe` |
| Smokeview | `C:\Program Files\firemodels\SMV6\smokeview.exe` | `C:\Program Files\firemodels\SMV6\smokeview.exe` |
| RADCAL | not detected | `E:\Thermal Radiation Modeling\Assets from Github\RADCAL\radcal_win_64.exe` |

## Installer Candidates

| Path | Present | SHA256 status |
| --- | ---: | --- |
| `E:\Thermal Radiation Modeling\FDS-6.11.0_SMV-6.11.0_win.exe` | no | not checked |
| `E:\Thermal Radiation Modeling\Assets from Github\FDS\FDS-6.11.0_SMV-6.11.0_win.exe` | yes | matches release |
| `C:\Users\prasa\Downloads\FDS-6.11.0_SMV-6.11.0_win.exe` | no | not checked |

## Downloaded GitHub Assets

| Asset | Role | Path | Present | SHA256 status |
| --- | --- | --- | ---: | --- |
| FDS/SMV Windows installer | `installer` | `E:\Thermal Radiation Modeling\Assets from Github\FDS\FDS-6.11.0_SMV-6.11.0_win.exe` | yes | matches expected release hash |
| RADCAL Windows executable | `standalone_executable` | `E:\Thermal Radiation Modeling\Assets from Github\RADCAL\radcal_win_64.exe` | yes | 63adaacd4682e1b599df102aad3543d145c6209a03eb6ce0dfb3a539b8888766 |
| Smokeview Windows installer | `installer` | `E:\Thermal Radiation Modeling\Assets from Github\SmokeView\SMV-6.11.1_win.exe` | yes | a5505933b709989f1d443eac53e84c40ca92418d432a64329615b2acfd4c1b48 |

## Source Repositories

| Repo | Local path | Present | Remote |
| --- | --- | ---: | --- |
| `fds` | `E:\Thermal Radiation Modeling\fds` | yes | `https://github.com/firemodels/fds.git` |
| `smv` | `E:\Thermal Radiation Modeling\smv` | yes | `https://github.com/firemodels/smv.git` |
| `radcal` | `E:\Thermal Radiation Modeling\radcal` | yes | `https://github.com/firemodels/radcal.git` |
| `exp` | `E:\Thermal Radiation Modeling\exp` | yes | `https://github.com/firemodels/exp.git` |
| `cfast` | `E:\Thermal Radiation Modeling\cfast` | yes | `https://github.com/firemodels/cfast.git` |

## Workflow Readiness

| Workflow | Status | Evidence |
| --- | --- | --- |
| RADCAL asset smoke test | ready | `outputs/project5_radcal_asset/RADCAL.OUT` |

## Meaning For The GUI

The Fortran GUI can regenerate and view this portfolio today. Full FDS, or Smokeview launch buttons should only be treated as operational after the corresponding executable is installed on PATH and smoke-tested from the project working directory.

The RADCAL asset workflow is GUI-runnable through the wrapper script when the smoke-test output is marked ready above.

Current next action:
- FDS and Smokeview are detectable on PATH; GUI run/open buttons can target them.
