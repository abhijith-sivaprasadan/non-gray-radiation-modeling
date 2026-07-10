# HAPI/HITEMP Reproduction Workflow

The default repository now uses published equations, tables, and metrics extracted from the
provided papers. It does not fabricate spectra.

Use this workflow only when you want to reproduce the underlying HITEMP/HITRAN spectral
databases from first principles.

## Published Settings To Reproduce

From Rashidzadeh et al. 2026 methanol/FDS paper:

- Participating gases: H2O, CO2, CO.
- Spectral source: HITEMP 2010.
- Resolution: 0.01 cm^-1.
- Line shape: Lorentz broadening.
- Line-wing cutoff: 500 cm^-1.
- Molar fractions: nine values between 0.001 and 0.35.
- Temperatures: 300 K to 2000 K in 50 K steps.

From Singh and Hostikka 2026 hydrogen paper:

- Participating gas: H2O.
- Spectral range: 0.1 to 100 micrometers.
- Thermodynamic grid: H2O mole fraction 0.01-1.00 and temperature 300-2400 K.
- Published derived Planck-mean correlation:
  `kappa_planck = X_H2O * 3.8821e6 * T^-1.9811`.

## Steps

1. Install HAPI from HITRANonline or the officially recommended distribution.
2. Configure authorized HITRAN/HITEMP data access.
3. Run `python scripts/hapi_fetch_template.py` to inspect molecule IDs and ranges.
4. Fetch line lists into `data/raw/hapi`.
5. Generate absorption coefficients using the same line shape, resolution, and cutoff as the papers.
6. Compare derived Planck means against Singh and Hostikka Eq. (21).
7. Build RCFSK/FSK tables and compare against the paper's published error metrics.

## Disclosure

Until this reproduction is done, describe this repository as:

```text
published-data implementation using equations, tables, and metrics extracted from supplied papers
```

Do not claim that the repository contains HITEMP line lists or reproduced LBL spectra.

