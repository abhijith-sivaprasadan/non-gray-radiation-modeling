"""Template for extending the published-data workflows with live HAPI line lists."""

from __future__ import annotations

import _bootstrap  # noqa: F401

from thermal_radiation_modeling.hapi_adapter import (
    HAPIUnavailableError,
    default_fetch_plans,
    require_hapi,
)


def main() -> None:
    try:
        hapi = require_hapi()
    except HAPIUnavailableError as exc:
        print(exc)
        print()
        print("Planned fetches:")
        for plan in default_fetch_plans():
            print(
                f"- {plan.species_name}: table={plan.table_name}, molecule={plan.molecule_id}, "
                f"isotopologue={plan.isotopologue_id}, range="
                f"{plan.wavenumber_min_cm}-{plan.wavenumber_max_cm} cm^-1"
            )
        return

    print("HAPI is available. Use the plans below with hapi.fetch after configuring data access.")
    print(hapi)
    for plan in default_fetch_plans():
        print(plan)


if __name__ == "__main__":
    main()
