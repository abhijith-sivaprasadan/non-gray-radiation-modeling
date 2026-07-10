import numpy as np

from thermal_radiation_modeling.particles import (
    johansson_2017_ash_efficiencies,
    johansson_2017_coal_char_efficiencies,
)
from thermal_radiation_modeling.published_data import (
    h2o_planck_mean_singh_hostikka_2026,
    methanol_decoupled_metrics,
    methanol_global_radiation_table,
    singh_axial_case_fields,
    singh_published_error_summary,
    singh_radial_case_fields,
)


def test_singh_planck_mean_correlation_matches_paper_formula() -> None:
    value = h2o_planck_mean_singh_hostikka_2026(1000.0, 0.1)
    expected = 0.1 * 3.8821e6 * 1000.0**-1.9811
    assert np.isclose(value, expected)


def test_singh_radial_case_has_center_peak() -> None:
    x = np.array([0.0, 0.5, 1.0])
    y = np.array([0.0, 0.5, 1.0])
    temperature, mole_fraction = singh_radial_case_fields(x, y)
    assert temperature[1, 1] == 2000.0
    assert np.isclose(mole_fraction[1, 1], 0.30)
    assert temperature[0, 0] == 500.0


def test_singh_axial_case_bounds_are_paper_ranges() -> None:
    temperature, mole_fraction = singh_axial_case_fields(np.array([1.0]), np.array([0.0, 4.0]))
    assert np.isclose(temperature[0, 0], 2000.0)
    assert np.isclose(temperature[1, 0], 300.0)
    assert np.isclose(mole_fraction[0, 0], 0.30)
    assert np.isclose(mole_fraction[1, 0], 0.01)


def test_johansson_particle_efficiencies_are_positive() -> None:
    coal_abs, coal_scat = johansson_2017_coal_char_efficiencies(20.0, 1500.0)
    ash_abs, ash_scat = johansson_2017_ash_efficiencies(20.0, 1500.0, "ash1")
    assert coal_abs > 0.0
    assert coal_scat > 0.0
    assert ash_abs > 0.0
    assert ash_scat > 0.0


def test_singh_radial_peak_error_summary_matches_published_headline_numbers() -> None:
    # README.md advertises these three figures (RC-FSK <14%, WSGG ~43%, Planck-mean ~150%)
    # as the portfolio's headline result; pin them so an edit to published_data.py cannot
    # silently drift the numbers away from the paper without a test failure.
    rows = {row["case"]: row for row in singh_published_error_summary()}
    radial = rows["radial_source_peak_error"]
    assert radial["rcfsk_4_transformed_percent"] == 14.0
    assert radial["wsgg_percent"] == 43.0
    assert radial["planck_mean_percent"] == 150.0

    axial = rows["axial_wall_flux_peak_error"]
    assert axial["rcfsk_4_transformed_percent"] == 7.0


def test_methanol_decoupled_metrics_match_published_table() -> None:
    # Rashidzadeh et al. 2026, methanol pool-fire decoupled comparison: RadCal vs. RC-FSK at
    # 4 and 6 gray gases.
    metrics = {(row["model"], row["gray_gases"]): row for row in methanol_decoupled_metrics()}
    assert metrics[("RadCal", 1)]["source_total_error_percent"] == 34.8
    assert metrics[("RC-FSK", 4)]["source_total_error_percent"] == 15.9
    assert metrics[("RC-FSK", 6)]["source_total_error_percent"] == 6.4


def test_methanol_global_radiation_table_matches_published_experimental_row() -> None:
    rows = {row["case"]: row for row in methanol_global_radiation_table()}
    assert rows["Experimental"]["radiant_fraction"] == 0.24
    assert rows["Experimental"]["radiant_fraction_uncertainty"] == 0.06
