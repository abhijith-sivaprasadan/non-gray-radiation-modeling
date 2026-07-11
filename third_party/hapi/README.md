# HAPI (HITRAN Application Programming Interface)

Vendored, unmodified copy of `hapi.py` v1.3.0.0 from the official HITRANonline distribution:
<https://hitran.org/static/hapi/hapi.py>, fetched 2026-07-11.

- License: MIT, Copyright 2021 HITRAN team - see the header of `hapi.py`.
- Not part of this project's own code (`src/thermal_radiation_modeling/`); this is a
  third-party tool used to fetch and process HITRAN/HITEMP line-by-line spectroscopic data.
- `src/thermal_radiation_modeling/hapi_adapter.py` adds this directory to `sys.path` before
  importing it.
