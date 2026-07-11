"""Project 5 extension: run and interpret a real FDS verification case.

run_radcal_asset.py checks that a downloaded RADCAL executable launches and parses its
output - useful, but a smoke test, not familiarity with the tool the reference group
actually builds on daily. This runs one of FDS's own verification cases
(fds/Verification/Radiation/check_kappa.fds, vendored as a git submodule) with the real
FDS-6.11.0 executable, then extracts real gas absorption-coefficient values (FDS's own
internal RadCal-based calculation) via the bundled fds2ascii tool, and compares the
temperature trend against this repository's own H2O Planck-mean work.

check_kappa.fds sweeps a 10 (mass fraction) x 10 (temperature) grid of methane/air mixtures
and outputs the FDS-computed 'ABSORPTION COEFFICIENT' slice for each. This script extracts a
representative temperature sweep at fixed mass fraction (the "column 1" mesh blocks, X_CH4 =
0.1, T = 20, 220, 420, 620, 820 C) rather than the full 100-point grid, to keep the
fds2ascii interaction (which needs one subprocess call per slice - see below) tractable.

FDS on Windows requires launching fds.exe through its bundled Intel MPI mpiexec (even for a
single-process run) with both the FDS bin/ and bin/mpi/ directories on PATH - invoking
fds.exe directly fails silently (exit code with no output). This was discovered by trial and
error; see the git history for this file if that stops working on a different FDS install.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
from _report_utils import plt, prepare_output_dirs, write_report

PROJECT_ROOT = _bootstrap.PROJECT_ROOT
OUTPUT_DIR = Path("outputs/project5_fds_example")
CASE_SOURCE = PROJECT_ROOT / "fds" / "Verification" / "Radiation" / "check_kappa.fds"
CASE_CHID = "check_kappa"

# (fds2ascii slice index, temperature_C, mass_fraction) for the X_CH4=0.1 column.
# Derived from check_kappa.fds's own &INIT blocks: slice N corresponds to row
# (N-1)//10 (temperature, 100 C apart starting at 20 C) and column (N-1)%10 (mass
# fraction, 0.1 apart starting at 0.1) - slice 1 is column 1 of row 0, slice 21 is column 1
# of row 2, etc.
TEMPERATURE_SWEEP_SLICES = [(1, 20.0), (21, 220.0), (41, 420.0), (61, 620.0), (81, 820.0)]
MASS_FRACTION_CH4 = 0.1


def main() -> None:
    prepare_output_dirs(OUTPUT_DIR)

    fds_exe, mpiexec_exe = _locate_fds()
    if fds_exe is None or mpiexec_exe is None:
        print(
            "Skipping: FDS or its bundled mpiexec was not found. See scripts/check_firemodels_tools.py."
        )
        return

    case_path = OUTPUT_DIR / f"{CASE_CHID}.fds"
    shutil.copy(CASE_SOURCE, case_path)

    run_ok = _run_fds(fds_exe, mpiexec_exe, case_path)
    if not run_ok:
        print("Skipping: FDS run did not complete successfully - see check_kappa.out.")
        return

    rows = _extract_temperature_sweep(fds_exe)
    if not rows:
        print("FDS ran, but fds2ascii extraction failed - see fds2ascii_*.log files.")
        return

    table = pd.DataFrame(rows)
    table.to_csv(OUTPUT_DIR / "tables" / "fds_kappa_temperature_sweep.csv", index=False)
    _plot(table)
    _write_report(table)
    print(f"Wrote {OUTPUT_DIR}")


def _locate_fds() -> tuple[Path | None, Path | None]:
    fds_path = shutil.which("fds")
    if fds_path is None:
        return None, None
    bin_dir = Path(fds_path).resolve().parent
    fds_exe = bin_dir / "fds.exe"
    mpiexec_exe = bin_dir / "mpi" / "mpiexec.exe"
    if not fds_exe.is_file() or not mpiexec_exe.is_file():
        return None, None
    return fds_exe, mpiexec_exe


def _fds_env(fds_exe: Path, mpiexec_exe: Path) -> dict:
    env = os.environ.copy()
    mpi_dir = str(mpiexec_exe.parent)
    bin_dir = str(fds_exe.parent)
    env["I_MPI_ROOT"] = mpi_dir
    env["PATH"] = bin_dir + os.pathsep + mpi_dir + os.pathsep + env.get("PATH", "")
    return env


def _run_fds(fds_exe: Path, mpiexec_exe: Path, case_path: Path) -> bool:
    result = subprocess.run(
        [str(mpiexec_exe), "-localonly", "-n", "1", str(fds_exe), case_path.name],
        cwd=case_path.parent,
        env=_fds_env(fds_exe, mpiexec_exe),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    # mpiexec writes FDS's own progress/completion messages to stderr, not stdout.
    combined_output = result.stdout + result.stderr
    (OUTPUT_DIR / "fds_run_stdout.log").write_text(
        combined_output, encoding="utf-8", errors="ignore"
    )
    return result.returncode == 0 and "completed successfully" in combined_output


def _extract_temperature_sweep(fds_exe: Path) -> list[dict[str, float]]:
    fds2ascii_exe = fds_exe.parent / "fds2ascii.exe"
    if not fds2ascii_exe.is_file():
        return []

    rows = []
    for slice_index, temperature_c in TEMPERATURE_SWEEP_SLICES:
        out_name = f"kappa_slice_{slice_index}"
        stdin_text = f"{CASE_CHID}\n2\n1\nn\n0 0.3\n1\n{slice_index}\n{out_name}\n"
        result = subprocess.run(
            [str(fds2ascii_exe)],
            cwd=OUTPUT_DIR,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        (OUTPUT_DIR / f"fds2ascii_{slice_index}.log").write_text(
            result.stdout + result.stderr, encoding="utf-8", errors="ignore"
        )
        out_path = OUTPUT_DIR / out_name
        if not out_path.exists():
            continue
        last_line = out_path.read_text(encoding="utf-8", errors="ignore").strip().splitlines()[-1]
        kappa = float(last_line.split(",")[-1])
        rows.append(
            {
                "slice_index": slice_index,
                "temperature_c": temperature_c,
                "temperature_k": temperature_c + 273.15,
                "mass_fraction_ch4": MASS_FRACTION_CH4,
                "fds_absorption_coefficient_m-1": kappa,
            }
        )
    return rows


def _plot(table: pd.DataFrame) -> None:
    fig, axis = plt.subplots(figsize=(6, 4.5), constrained_layout=True)
    axis.plot(table["temperature_k"], table["fds_absorption_coefficient_m-1"], "o-")
    axis.set_xlabel("temperature [K]")
    axis.set_ylabel("FDS absorption coefficient [m^-1]")
    axis.set_title(f"FDS internal RadCal kappa, methane X={MASS_FRACTION_CH4}")
    fig.savefig(OUTPUT_DIR / "figures" / "fds_kappa_temperature_sweep.png", dpi=180)
    plt.close(fig)


def _write_report(table: pd.DataFrame) -> None:
    first_row = table.iloc[0]
    last_row = table.iloc[-1]
    report = f"""# Project 5 Extension: A Real FDS Verification Case

`fds/Verification/Radiation/check_kappa.fds` is one of FDS's own verification cases - not
downloaded from a paper, and not the RADCAL smoke test's launch-and-parse check. This runs
it with the real FDS-6.11.0 executable and extracts real gas absorption-coefficient values
(FDS's own internal RadCal-based gray-gas calculation) via the bundled `fds2ascii` tool.

## The Case

A 10x10 grid of methane/air mixtures (mass fraction 0.1-1.0, temperature 20-920 C, 1%
background O2), each in its own small mesh block, with an `ABSORPTION COEFFICIENT` slice
output per block. This script extracts the X_CH4={MASS_FRACTION_CH4} column across
temperature (5 of the 10 available points) rather than the full grid, to keep the
per-slice `fds2ascii` interaction tractable.

## Result

{table.to_markdown(index=False)}

At X_CH4={MASS_FRACTION_CH4}, FDS's own RadCal-based absorption coefficient falls from
{first_row['fds_absorption_coefficient_m-1']:.4f} m^-1 at {first_row['temperature_k']:.0f} K
to {last_row['fds_absorption_coefficient_m-1']:.4f} m^-1 at {last_row['temperature_k']:.0f}
K - the same qualitative direction (absorption coefficient falling with temperature) as this
repository's own H2O Planck-mean work in Project 1 and its own-HITRAN-fit extension, though
for a different species (methane vs. water vapor) computed through a different model
(FDS's internal RadCal gray-gas treatment vs. a direct Voigt-profile HITRAN calculation) -
not a quantitative validation of one against the other, but the same underlying physical
trend (higher temperature broadens and redistributes absorption lines, generally reducing a
gray or Planck-mean absorption coefficient) showing up independently in both.

Full data in `tables/fds_kappa_temperature_sweep.csv`; figure in
`figures/fds_kappa_temperature_sweep.png`; raw FDS run log in `fds_run_stdout.log`.

## Notes on Running FDS on Windows

`fds.exe` must be launched through its bundled Intel MPI `mpiexec.exe` (even for a single
process) with both `bin/` and `bin/mpi/` on `PATH` - calling `fds.exe` directly fails
silently (nonzero exit, no output). See `_run_fds` in this script for the exact invocation.
"""
    write_report(OUTPUT_DIR, "project5_fds_example_report.md", report)


if __name__ == "__main__":
    main()
