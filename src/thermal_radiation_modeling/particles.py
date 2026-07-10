"""Particle radiative-property helpers for Rayleigh-limit bridge calculations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import spherical_jn, spherical_yn


@dataclass(frozen=True)
class MieEfficiency:
    """Absorption, scattering, and extinction efficiencies for a spherical particle."""

    q_abs: np.ndarray
    q_sca: np.ndarray
    q_ext: np.ndarray


def size_parameter(radius_m: float | np.ndarray, wavelength_m: float | np.ndarray) -> np.ndarray:
    """Return the spherical-particle size parameter ``x = 2 pi r / lambda``."""

    radius = np.asarray(radius_m, dtype=float)
    wavelength = np.asarray(wavelength_m, dtype=float)
    if np.any(radius <= 0):
        raise ValueError("radius_m must be positive")
    if np.any(wavelength <= 0):
        raise ValueError("wavelength_m must be positive")
    return 2.0 * np.pi * radius / wavelength


def rayleigh_absorption_efficiency(
    refractive_index: complex | np.ndarray,
    radius_m: float | np.ndarray,
    wavelength_m: float | np.ndarray,
) -> np.ndarray:
    """Return Rayleigh-limit absorption efficiency for a small sphere.

    Validity requires size parameter much smaller than one and a spherical homogeneous
    particle. For larger particles, use a full Mie calculation and compare against this
    limit rather than extrapolating it.
    """

    m = np.asarray(refractive_index, dtype=complex)
    x = size_parameter(radius_m, wavelength_m)
    polarizability_ratio = (m**2 - 1.0) / (m**2 + 2.0)
    q_abs = 4.0 * x * np.imag(polarizability_ratio)
    return np.maximum(q_abs, 0.0)


def rayleigh_scattering_efficiency(
    refractive_index: complex | np.ndarray,
    radius_m: float | np.ndarray,
    wavelength_m: float | np.ndarray,
) -> np.ndarray:
    """Return Rayleigh-limit scattering efficiency for a small sphere."""

    m = np.asarray(refractive_index, dtype=complex)
    x = size_parameter(radius_m, wavelength_m)
    polarizability_ratio = (m**2 - 1.0) / (m**2 + 2.0)
    return (8.0 / 3.0) * x**4 * np.abs(polarizability_ratio) ** 2


def absorption_coefficient_from_volume_fraction(
    volume_fraction: float | np.ndarray,
    radius_m: float | np.ndarray,
    absorption_efficiency: float | np.ndarray,
) -> np.ndarray:
    """Convert particle absorption efficiency to absorption coefficient in m^-1.

    For monodisperse spheres with radius ``r`` and volume fraction ``f_v``:
    ``kappa = 3 f_v Q_abs / (4 r)``.
    """

    fv = np.asarray(volume_fraction, dtype=float)
    radius = np.asarray(radius_m, dtype=float)
    q_abs = np.asarray(absorption_efficiency, dtype=float)
    if np.any(fv < 0):
        raise ValueError("volume_fraction must be non-negative")
    if np.any(radius <= 0):
        raise ValueError("radius_m must be positive")
    if np.any(q_abs < 0):
        raise ValueError("absorption_efficiency must be non-negative")
    return 3.0 * fv * q_abs / (4.0 * radius)


def rayleigh_absorption_coefficient(
    volume_fraction: float | np.ndarray,
    refractive_index: complex | np.ndarray,
    radius_m: float | np.ndarray,
    wavelength_m: float | np.ndarray,
) -> np.ndarray:
    """Return Rayleigh-limit particle absorption coefficient in m^-1."""

    q_abs = rayleigh_absorption_efficiency(refractive_index, radius_m, wavelength_m)
    return absorption_coefficient_from_volume_fraction(volume_fraction, radius_m, q_abs)


def johansson_2017_correlation(
    y0: np.ndarray, y_inf: np.ndarray, z: float | np.ndarray
) -> np.ndarray:
    """Evaluate Johansson's Eq. (8) gray particle correlation form."""

    y0_values = np.asarray(y0, dtype=float)
    y_inf_values = np.asarray(y_inf, dtype=float)
    z_values = np.asarray(z, dtype=float)
    return (1.0 / (1.0 / y0_values**z_values + 1.0 / y_inf_values**z_values)) ** (1.0 / z_values)


def johansson_2017_coal_char_efficiencies(
    radius_um: float | np.ndarray,
    temperature_k: float | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return published gray coal/char Q_abs and Q_scat from Johansson Table 1."""

    rp_t = np.asarray(radius_um, dtype=float) * np.asarray(temperature_k, dtype=float)
    if np.any(rp_t <= 0):
        raise ValueError("radius_um and temperature_k must be positive")
    q_abs = johansson_2017_correlation((rp_t / 700.0) ** 1.1, 0.88 + 1680.0 / rp_t, 1.6)
    q_scat = johansson_2017_correlation(
        (rp_t / 570.0) ** 3.9,
        1.2 + 2600.0 / rp_t**1.2,
        0.65,
    )
    return q_abs, q_scat


def johansson_2017_ash_efficiencies(
    radius_um: float | np.ndarray,
    temperature_k: float | np.ndarray,
    ash_type: str = "ash1",
) -> tuple[np.ndarray, np.ndarray]:
    """Return published gray ash Q_abs and Q_scat from Johansson Table 2."""

    rp = np.asarray(radius_um, dtype=float)
    temperature = np.asarray(temperature_k, dtype=float)
    if np.any(rp <= 0) or np.any(temperature <= 0):
        raise ValueError("radius_um and temperature_k must be positive")

    if ash_type == "ash1":
        q_abs = johansson_2017_correlation(
            (rp / (3.57 - 6.14 * np.exp(-0.0014 * temperature))) ** 1.09,
            0.7 + 0.654 / rp**0.22,
            1.1,
        )
        q_scat = johansson_2017_correlation(
            (rp / (0.25 + 2.05 * np.exp(-0.0019 * temperature))) ** 4.0,
            1.1 + 3.1 / rp**0.97,
            0.42,
        )
    elif ash_type == "ash2":
        q_abs = johansson_2017_correlation(
            (rp / (0.053 * temperature - 32.0)) ** 0.9,
            0.7 + 1.16 / rp**0.24,
            0.31 + 2.8e-4 * temperature,
        )
        q_scat = johansson_2017_correlation(
            (rp / (0.22 + 1.87 * np.exp(-0.0015 * temperature))) ** 4.0,
            1.1 + 2.06 / rp**0.4,
            0.54,
        )
    else:
        raise ValueError("ash_type must be 'ash1' or 'ash2'")
    return q_abs, q_scat


def mie_efficiencies(
    refractive_index: complex | np.ndarray,
    radius_m: float | np.ndarray,
    wavelength_m: float | np.ndarray,
) -> MieEfficiency:
    """Compute Mie efficiencies for homogeneous spherical particles.

    This internal implementation is meant for portfolio-scale calculations. It uses the
    standard Bohren-Huffman coefficients and falls back to Rayleigh formulas at very small
    size parameter where direct Mie sums become ill-conditioned.
    """

    m, radius, wavelength = np.broadcast_arrays(
        np.asarray(refractive_index, dtype=complex),
        np.asarray(radius_m, dtype=float),
        np.asarray(wavelength_m, dtype=float),
    )
    q_abs = np.zeros(m.shape, dtype=float)
    q_sca = np.zeros(m.shape, dtype=float)
    q_ext = np.zeros(m.shape, dtype=float)

    for index in np.ndindex(m.shape):
        x = float(size_parameter(radius[index], wavelength[index]))
        if x < 1e-3:
            abs_eff = float(
                rayleigh_absorption_efficiency(m[index], radius[index], wavelength[index])
            )
            sca_eff = float(
                rayleigh_scattering_efficiency(m[index], radius[index], wavelength[index])
            )
            q_abs[index] = abs_eff
            q_sca[index] = sca_eff
            q_ext[index] = abs_eff + sca_eff
            continue
        # The public API uses the optics convention m = n + i k with k >= 0 for absorbing
        # media. The Mie coefficient recurrence below follows the opposite time convention.
        ext, sca = _mie_scalar(np.conjugate(m[index]), x)
        q_ext[index] = max(ext, 0.0)
        q_sca[index] = max(sca, 0.0)
        q_abs[index] = max(q_ext[index] - q_sca[index], 0.0)

    return MieEfficiency(q_abs=q_abs, q_sca=q_sca, q_ext=q_ext)


def mie_absorption_coefficient(
    volume_fraction: float | np.ndarray,
    refractive_index: complex | np.ndarray,
    radius_m: float | np.ndarray,
    wavelength_m: float | np.ndarray,
) -> np.ndarray:
    """Return Mie absorption coefficient in m^-1 for monodisperse spheres."""

    efficiencies = mie_efficiencies(refractive_index, radius_m, wavelength_m)
    return absorption_coefficient_from_volume_fraction(
        volume_fraction,
        radius_m,
        efficiencies.q_abs,
    )


def _mie_scalar(refractive_index: complex, size_x: float) -> tuple[float, float]:
    n_stop = int(np.ceil(size_x + 4.0 * size_x ** (1.0 / 3.0) + 2.0))
    q_ext_sum = 0.0
    q_sca_sum = 0.0
    mx = refractive_index * size_x

    for n in range(1, n_stop + 1):
        psi_x = _riccati_psi(n, size_x)
        psi_x_prime = _riccati_psi_prime(n, size_x)
        psi_mx = _riccati_psi(n, mx)
        psi_mx_prime = _riccati_psi_prime(n, mx)
        xi_x = _riccati_xi(n, size_x)
        xi_x_prime = _riccati_xi_prime(n, size_x)

        a_num = refractive_index * psi_mx * psi_x_prime - psi_x * psi_mx_prime
        a_den = refractive_index * psi_mx * xi_x_prime - xi_x * psi_mx_prime
        b_num = psi_mx * psi_x_prime - refractive_index * psi_x * psi_mx_prime
        b_den = psi_mx * xi_x_prime - refractive_index * xi_x * psi_mx_prime
        a_n = a_num / a_den
        b_n = b_num / b_den
        coefficient = 2 * n + 1
        q_ext_sum += coefficient * np.real(a_n + b_n)
        q_sca_sum += coefficient * (abs(a_n) ** 2 + abs(b_n) ** 2)

    factor = 2.0 / size_x**2
    return float(factor * q_ext_sum), float(factor * q_sca_sum)


def _riccati_psi(n: int, z: complex | float) -> complex:
    return z * spherical_jn(n, z)


def _riccati_psi_prime(n: int, z: complex | float) -> complex:
    return spherical_jn(n, z) + z * spherical_jn(n, z, derivative=True)


def _riccati_chi(n: int, z: float) -> complex:
    return -z * spherical_yn(n, z)


def _riccati_chi_prime(n: int, z: float) -> complex:
    return -(spherical_yn(n, z) + z * spherical_yn(n, z, derivative=True))


def _riccati_xi(n: int, z: float) -> complex:
    return _riccati_psi(n, z) + 1j * _riccati_chi(n, z)


def _riccati_xi_prime(n: int, z: float) -> complex:
    return _riccati_psi_prime(n, z) + 1j * _riccati_chi_prime(n, z)
