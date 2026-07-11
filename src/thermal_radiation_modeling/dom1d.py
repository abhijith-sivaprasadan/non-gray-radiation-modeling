"""One-dimensional pure-absorption discrete ordinates solver."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from thermal_radiation_modeling.constants import STEFAN_BOLTZMANN
from thermal_radiation_modeling.lbl import planck_wavenumber_weight
from thermal_radiation_modeling.wsgg import WSGGModel


@dataclass(frozen=True)
class DOMResult:
    """Result arrays from the 1-D DOM sweep."""

    x_m: np.ndarray
    direction_cosines: np.ndarray
    quadrature_weights: np.ndarray
    intensity: np.ndarray
    incident_radiation: np.ndarray
    heat_flux: np.ndarray
    source_term: np.ndarray


def _symmetric_half_range_quadrature(order: int) -> tuple[np.ndarray, np.ndarray]:
    """Return mirrored half-range Gauss-Legendre ordinates on [-1, 1]."""

    positive_count = order // 2
    raw_mu, raw_weights = np.polynomial.legendre.leggauss(positive_count)
    positive_mu = 0.5 * (raw_mu + 1.0)
    positive_weights = 0.5 * raw_weights
    mu = np.concatenate([-positive_mu[::-1], positive_mu])
    weights = np.concatenate([positive_weights[::-1], positive_weights])
    return mu, weights


def _cell_widths_from_centers(x_m: np.ndarray) -> np.ndarray:
    if x_m.ndim != 1 or x_m.size < 2:
        raise ValueError("x_m must be a one-dimensional array with at least two points")
    if np.any(np.diff(x_m) <= 0):
        raise ValueError("x_m must be strictly increasing")

    midpoints = 0.5 * (x_m[1:] + x_m[:-1])
    left = x_m[0] - 0.5 * (x_m[1] - x_m[0])
    right = x_m[-1] + 0.5 * (x_m[-1] - x_m[-2])
    boundaries = np.concatenate([[left], midpoints, [right]])
    return np.diff(boundaries)


def solve_pure_absorption_dom(
    x_m: np.ndarray,
    temperature_k: np.ndarray,
    absorption_coefficient_m: np.ndarray | float,
    quadrature_order: int = 8,
    left_wall_temperature_k: float | None = None,
    right_wall_temperature_k: float | None = None,
) -> DOMResult:
    """Solve 1-D, non-scattering, pure-absorption RTE with first-order upwinding.

    The equation is ``mu dI/dx = kappa (I_b - I)`` with black-wall boundary conditions.
    """

    x = np.asarray(x_m, dtype=float)
    temperature = np.asarray(temperature_k, dtype=float)
    if temperature.shape != x.shape:
        raise ValueError("temperature_k must have the same shape as x_m")
    if np.any(temperature <= 0):
        raise ValueError("temperature_k must be positive")

    kappa = np.broadcast_to(np.asarray(absorption_coefficient_m, dtype=float), x.shape)
    if np.any(kappa < 0):
        raise ValueError("absorption_coefficient_m must be non-negative")

    left_wall_t = float(
        temperature[0] if left_wall_temperature_k is None else left_wall_temperature_k
    )
    right_wall_t = float(
        temperature[-1] if right_wall_temperature_k is None else right_wall_temperature_k
    )
    if left_wall_t <= 0 or right_wall_t <= 0:
        raise ValueError("wall temperatures must be positive")

    blackbody_intensity = STEFAN_BOLTZMANN * temperature**4 / np.pi
    left_wall_intensity = STEFAN_BOLTZMANN * left_wall_t**4 / np.pi
    right_wall_intensity = STEFAN_BOLTZMANN * right_wall_t**4 / np.pi

    return solve_gray_dom_with_source(
        x,
        absorption_coefficient_m=kappa,
        source_intensity=blackbody_intensity,
        left_boundary_intensity=left_wall_intensity,
        right_boundary_intensity=right_wall_intensity,
        quadrature_order=quadrature_order,
    )


def solve_gray_dom_with_source(
    x_m: np.ndarray,
    absorption_coefficient_m: np.ndarray | float,
    source_intensity: np.ndarray,
    left_boundary_intensity: float,
    right_boundary_intensity: float,
    quadrature_order: int = 8,
) -> DOMResult:
    """Solve a gray pure-absorption DOM problem with an arbitrary source intensity."""

    if quadrature_order < 2 or quadrature_order % 2 != 0:
        raise ValueError("quadrature_order must be an even integer >= 2")

    x = np.asarray(x_m, dtype=float)
    source = np.asarray(source_intensity, dtype=float)
    if source.shape != x.shape:
        raise ValueError("source_intensity must have the same shape as x_m")
    if np.any(source < 0):
        raise ValueError("source_intensity must be non-negative")

    kappa = np.broadcast_to(np.asarray(absorption_coefficient_m, dtype=float), x.shape)
    if np.any(kappa < 0):
        raise ValueError("absorption_coefficient_m must be non-negative")

    widths = _cell_widths_from_centers(x)
    mu, weights = _symmetric_half_range_quadrature(quadrature_order)
    intensity = np.zeros((quadrature_order, x.size), dtype=float)

    for direction_index, direction in enumerate(mu):
        if direction > 0:
            incoming = left_boundary_intensity
            for cell_index in range(x.size):
                beta = kappa[cell_index] * widths[cell_index] / direction
                cell_intensity = (incoming + beta * source[cell_index]) / (1.0 + beta)
                intensity[direction_index, cell_index] = cell_intensity
                incoming = cell_intensity
        else:
            incoming = right_boundary_intensity
            for cell_index in range(x.size - 1, -1, -1):
                beta = kappa[cell_index] * widths[cell_index] / abs(direction)
                cell_intensity = (incoming + beta * source[cell_index]) / (1.0 + beta)
                intensity[direction_index, cell_index] = cell_intensity
                incoming = cell_intensity

    incident_radiation = 2.0 * np.pi * np.sum(weights[:, None] * intensity, axis=0)
    heat_flux = 2.0 * np.pi * np.sum(weights[:, None] * mu[:, None] * intensity, axis=0)
    source_term = kappa * (4.0 * np.pi * source - incident_radiation)

    return DOMResult(
        x_m=x,
        direction_cosines=mu,
        quadrature_weights=weights,
        intensity=intensity,
        incident_radiation=incident_radiation,
        heat_flux=heat_flux,
        source_term=source_term,
    )


def solve_gray_dom_with_isotropic_scattering(
    x_m: np.ndarray,
    absorption_coefficient_m: np.ndarray | float,
    scattering_coefficient_m: np.ndarray | float,
    blackbody_source_intensity: np.ndarray,
    left_boundary_intensity: float,
    right_boundary_intensity: float,
    quadrature_order: int = 8,
    max_iterations: int = 100,
    tolerance: float = 1e-5,
) -> DOMResult:
    """Solve a gray DOM problem with absorption, emission, *and* isotropic scattering.

    This is the counterpart to :func:`solve_gray_dom_with_source` (which has no scattering
    term at all - see the module-level caveat on ``solve_wsgg_dom``) and to
    ``docs/derivation_note.md``'s documented DOM scattering limitation.

    Uses classical source iteration: at each outer iteration, the scattering-in term is
    treated as an additional isotropic source proportional to the *previous* iteration's
    incident radiation G, and the combined absorption+scattering+emission problem is solved
    with total extinction ``beta = kappa + sigma_s`` via a call to
    :func:`solve_gray_dom_with_source`. Iterates until the relative change in G falls below
    ``tolerance`` or ``max_iterations`` is reached. The returned ``source_term`` uses only
    the true absorption coefficient (scattering redistributes energy directionally but does
    not create or destroy it, so it must not appear in the local energy-source term).
    """

    x = np.asarray(x_m, dtype=float)
    kappa = np.broadcast_to(np.asarray(absorption_coefficient_m, dtype=float), x.shape)
    sigma = np.broadcast_to(np.asarray(scattering_coefficient_m, dtype=float), x.shape)
    if np.any(kappa < 0) or np.any(sigma < 0):
        raise ValueError(
            "absorption_coefficient_m and scattering_coefficient_m must be non-negative"
        )
    blackbody = np.asarray(blackbody_source_intensity, dtype=float)
    if blackbody.shape != x.shape:
        raise ValueError("blackbody_source_intensity must have the same shape as x_m")

    beta = kappa + sigma
    safe_beta = np.where(beta > 0, beta, 1.0)
    incident_radiation = np.zeros_like(x)
    result = None
    for _ in range(max_iterations):
        effective_source = np.where(
            beta > 0,
            (kappa * blackbody + (sigma / (4.0 * np.pi)) * incident_radiation) / safe_beta,
            blackbody,
        )
        result = solve_gray_dom_with_source(
            x,
            beta,
            effective_source,
            left_boundary_intensity,
            right_boundary_intensity,
            quadrature_order,
        )
        new_incident = result.incident_radiation
        denom = np.max(np.abs(new_incident))
        change = (
            float(np.max(np.abs(new_incident - incident_radiation)) / denom) if denom > 0 else 0.0
        )
        incident_radiation = new_incident
        if change < tolerance:
            break

    assert result is not None
    true_source_term = kappa * (4.0 * np.pi * blackbody - incident_radiation)
    return DOMResult(
        x_m=x,
        direction_cosines=result.direction_cosines,
        quadrature_weights=result.quadrature_weights,
        intensity=result.intensity,
        incident_radiation=incident_radiation,
        heat_flux=result.heat_flux,
        source_term=true_source_term,
    )


def solve_wsgg_dom(
    x_m: np.ndarray,
    temperature_k: np.ndarray,
    model: WSGGModel,
    pressure_scale: float | np.ndarray = 1.0,
    particle_absorption_coefficient_m: float | np.ndarray = 0.0,
    quadrature_order: int = 8,
    left_wall_temperature_k: float | None = None,
    right_wall_temperature_k: float | None = None,
) -> DOMResult:
    """Solve a WSGG DOM problem by summing gray-gas DOM sweeps.

    At each cell, the local absorption coefficient for gray gas ``j`` is
    ``local_kappa_j = model.absorption_coefficients[j] * pressure_scale + particle_absorption_coefficient_m``.
    ``pressure_scale`` is a dimensionless per-cell multiplier, not an absolute pressure: use
    ``pressure_scale=1.0`` (the default) when ``model.absorption_coefficients`` are already
    tabulated as local m^-1 absorption coefficients for the gas mixture in ``x_m``, or pass the
    local partial-pressure (e.g. atm) when the model's coefficients are tabulated per unit
    partial pressure (matching the convention documented on the ``pressure_paths`` argument
    of :func:`superposed_emissivity`).

    This solver only couples particle *absorption* into ``kappa`` via
    ``particle_absorption_coefficient_m``. It has no scattering source term or phase function,
    so particle scattering efficiencies computed elsewhere (Rayleigh/Mie/Johansson helpers in
    :mod:`thermal_radiation_modeling.particles`) are not represented here; see
    ``docs/derivation_note.md`` for the same caveat.
    """

    x = np.asarray(x_m, dtype=float)
    temperature = np.asarray(temperature_k, dtype=float)
    if temperature.shape != x.shape:
        raise ValueError("temperature_k must have the same shape as x_m")

    pressure = np.broadcast_to(np.asarray(pressure_scale, dtype=float), x.shape)
    particle_kappa = np.broadcast_to(
        np.asarray(particle_absorption_coefficient_m, dtype=float), x.shape
    )
    if np.any(pressure < 0) or np.any(particle_kappa < 0):
        raise ValueError("pressure_scale and particle absorption must be non-negative")

    left_wall_t = float(
        temperature[0] if left_wall_temperature_k is None else left_wall_temperature_k
    )
    right_wall_t = float(
        temperature[-1] if right_wall_temperature_k is None else right_wall_temperature_k
    )
    weights = model.weights(temperature)
    left_weights = model.weights(left_wall_t)
    right_weights = model.weights(right_wall_t)
    blackbody_intensity = STEFAN_BOLTZMANN * temperature**4 / np.pi
    left_blackbody = STEFAN_BOLTZMANN * left_wall_t**4 / np.pi
    right_blackbody = STEFAN_BOLTZMANN * right_wall_t**4 / np.pi

    total_intensity = None
    total_incident = np.zeros_like(x)
    total_flux = np.zeros_like(x)
    total_source = np.zeros_like(x)
    mu = gas_quad_weights = None

    for gas_index, gas_kappa in enumerate(model.absorption_coefficients):
        local_kappa = gas_kappa * pressure + particle_kappa
        result = solve_gray_dom_with_source(
            x,
            local_kappa,
            source_intensity=weights[:, gas_index] * blackbody_intensity,
            left_boundary_intensity=float(left_weights[gas_index] * left_blackbody),
            right_boundary_intensity=float(right_weights[gas_index] * right_blackbody),
            quadrature_order=quadrature_order,
        )
        if total_intensity is None:
            total_intensity = np.zeros_like(result.intensity)
            mu = result.direction_cosines
            gas_quad_weights = result.quadrature_weights
        total_intensity += result.intensity
        total_incident += result.incident_radiation
        total_flux += result.heat_flux
        total_source += result.source_term

    if total_intensity is None or mu is None or gas_quad_weights is None:
        raise ValueError("model contains no gases")

    return DOMResult(
        x_m=x,
        direction_cosines=mu,
        quadrature_weights=gas_quad_weights,
        intensity=total_intensity,
        incident_radiation=total_incident,
        heat_flux=total_flux,
        source_term=total_source,
    )


def solve_spectral_pure_absorption_dom(
    x_m: np.ndarray,
    temperature_k: np.ndarray,
    wavenumber_cm: np.ndarray,
    absorption_coefficient_m: np.ndarray,
    quadrature_order: int = 8,
    left_wall_temperature_k: float | None = None,
    right_wall_temperature_k: float | None = None,
) -> DOMResult:
    """Solve a spectral pure-absorption DOM problem and integrate over wavenumber."""

    x = np.asarray(x_m, dtype=float)
    temperature = np.asarray(temperature_k, dtype=float)
    eta = np.asarray(wavenumber_cm, dtype=float)
    kappa_eta = np.asarray(absorption_coefficient_m, dtype=float)
    if temperature.shape != x.shape:
        raise ValueError("temperature_k must have the same shape as x_m")
    if kappa_eta.shape != (eta.size, x.size):
        raise ValueError("absorption_coefficient_m must have shape (n_wavenumber, n_cells)")
    if np.any(kappa_eta < 0):
        raise ValueError("absorption coefficients must be non-negative")

    left_wall_t = float(
        temperature[0] if left_wall_temperature_k is None else left_wall_temperature_k
    )
    right_wall_t = float(
        temperature[-1] if right_wall_temperature_k is None else right_wall_temperature_k
    )

    source_spectral = _spectral_blackbody_intensity(eta, temperature)
    left_boundary = _spectral_blackbody_intensity(eta, np.array([left_wall_t]))[:, 0]
    right_boundary = _spectral_blackbody_intensity(eta, np.array([right_wall_t]))[:, 0]

    spectral_flux = []
    spectral_source = []
    spectral_incident = []
    spectral_intensity = []
    mu = quad_weights = None

    for spectral_index in range(eta.size):
        result = solve_gray_dom_with_source(
            x,
            kappa_eta[spectral_index],
            source_spectral[spectral_index],
            float(left_boundary[spectral_index]),
            float(right_boundary[spectral_index]),
            quadrature_order=quadrature_order,
        )
        spectral_flux.append(result.heat_flux)
        spectral_source.append(result.source_term)
        spectral_incident.append(result.incident_radiation)
        spectral_intensity.append(result.intensity)
        mu = result.direction_cosines
        quad_weights = result.quadrature_weights

    flux = np.trapezoid(np.asarray(spectral_flux), eta, axis=0)
    source = np.trapezoid(np.asarray(spectral_source), eta, axis=0)
    incident = np.trapezoid(np.asarray(spectral_incident), eta, axis=0)
    intensity = np.trapezoid(np.asarray(spectral_intensity), eta, axis=0)

    if mu is None or quad_weights is None:
        raise ValueError("wavenumber grid must not be empty")

    return DOMResult(
        x_m=x,
        direction_cosines=mu,
        quadrature_weights=quad_weights,
        intensity=intensity,
        incident_radiation=incident,
        heat_flux=flux,
        source_term=source,
    )


def _spectral_blackbody_intensity(
    wavenumber_cm: np.ndarray, temperature_k: np.ndarray
) -> np.ndarray:
    eta = np.asarray(wavenumber_cm, dtype=float)
    temperatures = np.asarray(temperature_k, dtype=float)
    values = np.zeros((eta.size, temperatures.size), dtype=float)
    for index, temperature in enumerate(temperatures):
        weights = planck_wavenumber_weight(eta, float(temperature))
        denominator = np.trapezoid(weights, eta)
        if denominator <= 0:
            raise ValueError("Planck weight integral must be positive")
        values[:, index] = (STEFAN_BOLTZMANN * temperature**4 / np.pi) * weights / denominator
    return values
