# Reproduce the scientific Python core

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/run_all.py
```

The Linux CI runs tests and the self-contained Projects 1–4 workflow. This is
distinct from optional Windows GUI, downloaded RADCAL/FDS executables,
authenticated HITRAN retrieval and extension scripts. Core CI intentionally does
not initialise external submodules because those upstream integrations are not
required by these Python workflows. Their presence is not evidence of core authorship.

Tests include published fixture checks, DOM behaviour, correlation regressions
and deterministic surrogate checks. Passing these tests is not independent
experimental validation of every model or reproduction of every README extension.

The dependency ranges are compatible-install constraints, not an exact archived
environment. Dependency locking, input/output manifests and a complete file-level
third-party licence inventory remain release gates. No blanket licence is granted
over Firemodels submodules or other third-party code/data; see `PROVENANCE.md`.
