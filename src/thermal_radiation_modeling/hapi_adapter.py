"""Optional HAPI/HITEMP integration hooks.

The default portfolio uses published equations and tables extracted from papers. Use this
module when HAPI is installed and a HITRAN/HITEMP data access workflow has been configured.
The functions avoid silently fabricating data: if HAPI is unavailable, they raise clear
errors.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

VENDORED_HAPI_DIR = Path(__file__).resolve().parents[2] / "third_party" / "hapi"


class HAPIUnavailableError(RuntimeError):
    """Raised when a HAPI operation is requested without HAPI installed."""


@dataclass(frozen=True)
class HAPIFetchPlan:
    species_name: str
    table_name: str
    molecule_id: int
    isotopologue_id: int
    wavenumber_min_cm: float
    wavenumber_max_cm: float


def require_hapi():
    """Import and return HAPI (vendored under third_party/hapi/), or raise a clear setup error."""

    if VENDORED_HAPI_DIR.is_dir() and str(VENDORED_HAPI_DIR) not in sys.path:
        sys.path.insert(0, str(VENDORED_HAPI_DIR))
    try:
        import hapi  # type: ignore
    except ModuleNotFoundError as exc:
        raise HAPIUnavailableError(
            "HAPI is not available. Expected third_party/hapi/hapi.py (vendored from "
            "https://hitran.org/static/hapi/hapi.py) or a hapi module importable some other "
            "way; configure your line-list access before running live fetches."
        ) from exc
    return hapi


def default_fetch_plans() -> list[HAPIFetchPlan]:
    """Return reasonable starting ranges for live HAPI/HITEMP reproduction work."""

    return [
        HAPIFetchPlan("CO2", "CO2_main", 2, 1, 500.0, 5000.0),
        HAPIFetchPlan("H2O", "H2O_main", 1, 1, 150.0, 6500.0),
        HAPIFetchPlan("CO", "CO_main", 5, 1, 1800.0, 2400.0),
        HAPIFetchPlan("CH4", "CH4_main", 6, 1, 1000.0, 3400.0),
    ]
