# FDS Integration Notes

The FDS repository is the implementation target named by the user and by the research-team
papers.

## Relevant Facts

- The public repository is `https://github.com/firemodels/fds`.
- The repository description identifies FDS as a large-eddy simulation code for low-speed
  fire flows, smoke, and heat transport.
- The repository is Fortran-heavy, so a credible portfolio should avoid pretending that a
  Python prototype is an FDS implementation.
- Rashidzadeh et al. 2026 states that RC-FSK was implemented as a subroutine in the FDS
  radiation module and that the model will be available through `firemodels/fds`.

## Sensible Portfolio Boundary

This repo should be presented as:

```text
a Python research prototype and paper-data reproduction package aligned with FDS radiation modeling
```

not as:

```text
a working FDS code modification
```

## Next Implementation Step

After cloning FDS locally, inspect:

- radiation module source files,
- existing RadCal/WSGG interfaces,
- lookup-table loading conventions,
- validation case structure under `Validation` and `Verification`.

Then create a small FDS-facing design note mapping the Python data structures in
`published_data.py` to the Fortran table format expected by the radiation module.

## Fortran UI Added

The repository now includes `fortran_ui/radiation_portfolio_ui.f90`, a standalone Fortran
terminal dashboard that reads the generated CSV artifacts and can write
`outputs/fortran_dashboard.html`. This is not an FDS modification, but it gives a concrete
Fortran artifact aligned with the implementation language used by FDS.
