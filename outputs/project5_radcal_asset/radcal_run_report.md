# RADCAL Asset Smoke Test

This run verifies that the downloaded RADCAL Windows executable can be launched
from the portfolio when the Intel OpenMP runtime folder is prepended to PATH.

- RADCAL executable: `E:\Thermal Radiation Modeling\Assets from Github\RADCAL\radcal_win_64.exe`
- Intel OpenMP DLL: `C:\Program Files\firemodels\FDS6\bin\libiomp5md.dll`
- Working directory: `E:\Thermal Radiation Modeling\outputs\project5_radcal_asset`

## Parsed Output

| Metric | Value |
| --- | ---: |
| `case_line` | `CASEID: PORTFOLIO_RADCAL_SMOKE_TEST TITLE: PORTFOLIO_RADCAL_SMOKE_TEST` |
| `path_length_m` | `0.317500000000000` |
| `amean_cm-1` | `4.079920581588056E-003` |
| `planck_mean_absorption_cm-1` | `9.468479800933764E-003` |
| `total_emissivity` | `0.121498337094944` |
| `received_flux_w_m2_str` | `1008.60961294082` |
| `total_transmissivity` | `0.878725505720467` |

Generated files:

- `RADCAL.IN`
- `RADCAL.OUT`
- `TRANS_PORTFOLIO_RADCAL_SMOKE_TEST.TEC`
- `radcal_summary.csv`
