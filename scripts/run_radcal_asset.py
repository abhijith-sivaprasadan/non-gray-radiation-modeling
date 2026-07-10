"""Run the downloaded RADCAL Windows asset with its Intel OpenMP runtime.

This is intentionally a smoke-test workflow, not a new validation claim. It
proves that the downloaded Firemodels RADCAL executable can be launched from the
portfolio and that its basic output files can be parsed.
"""

from __future__ import annotations

import _bootstrap

import csv
import glob
import os
from pathlib import Path
import re
import subprocess

PROJECT_ROOT = _bootstrap.PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "project5_radcal_asset"

RADCAL_EXE_CANDIDATES = [
    PROJECT_ROOT / "Assets from Github" / "RADCAL" / "radcal_win_64.exe",
]

# Common install locations that happen to bundle a redistributable Intel OpenMP runtime.
# These are generic "well-known Program Files layouts", not this machine's specific software
# versions. If none apply, set RADCAL_OPENMP_DLL_DIR to the folder containing libiomp5md.dll.
RUNTIME_GLOBS = [
    r"C:\Program Files\Intel\**\libiomp5md.dll",
    r"C:\Program Files (x86)\Intel\**\libiomp5md.dll",
]

RADCAL_INPUT = """# Portfolio RADCAL smoke-test input.
# Species list and namelist structure follow the downloaded Firemodels RADCAL example.
&HEADER TITLE="PORTFOLIO_RADCAL_SMOKE_TEST" CHID="PORTFOLIO_RADCAL_SMOKE_TEST" /

&BAND OMMIN = 50.0
      OMMAX = 10000.0 /
&WALL TWALL = 500.0 /

&PATH_SEGMENT
    T        = 300.0
    LENGTH   = 0.3175
    PRESSURE = 1.0
    XC2H4    = 0.01
    XCO2     = 0.0033
    XH2O     = 0.01
    XO2      = 0.21
    XN2      = 0.7667
    FV       = 1.0E-7 /
"""

SUMMARY_PATTERNS = {
    "path_length_m": re.compile(r"TOTAL PATH LENGTH \(M\):\s*([-+0-9.Ee]+)", re.I),
    "amean_cm-1": re.compile(r"AMEAN \(CM-1\):\s*([-+0-9.Ee]+)", re.I),
    "planck_mean_absorption_cm-1": re.compile(
        r"PLANCK MEAN ABSORPTION \(CM-1\):\s*([-+0-9.Ee]+)", re.I
    ),
    "total_emissivity": re.compile(r"TOTAL EMISSIVITY:\s*([-+0-9.Ee]+)", re.I),
    "received_flux_w_m2_str": re.compile(r"RECEIVED FLUX \(W/M2/STR\):\s*([-+0-9.Ee]+)", re.I),
    "total_transmissivity": re.compile(r"TOTAL TRANSMISSIVITY:\s*([-+0-9.Ee]+)", re.I),
}


def main() -> None:
    radcal_exe = first_existing(RADCAL_EXE_CANDIDATES, "RADCAL executable")
    runtime_dll = find_openmp_runtime()
    if runtime_dll is None:
        raise SystemExit(
            "Could not find libiomp5md.dll. Install the Intel OpenMP runtime, add its folder "
            "to PATH, or set the RADCAL_OPENMP_DLL_DIR environment variable to that folder."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    input_path = OUTPUT_DIR / "RADCAL.IN"
    input_path.write_text(RADCAL_INPUT, encoding="utf-8")

    env = os.environ.copy()
    env["PATH"] = str(runtime_dll.parent) + os.pathsep + env.get("PATH", "")
    proc = subprocess.run(
        [str(radcal_exe), "RADCAL.IN"],
        cwd=OUTPUT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    (OUTPUT_DIR / "radcal_stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (OUTPUT_DIR / "radcal_stderr.txt").write_text(proc.stderr, encoding="utf-8")

    radcal_out = OUTPUT_DIR / "RADCAL.OUT"
    if proc.returncode != 0:
        raise SystemExit(f"RADCAL exited with code {proc.returncode}; see radcal_stderr.txt")
    if not radcal_out.exists():
        raise SystemExit("RADCAL exited cleanly but did not create RADCAL.OUT")

    summary = parse_radcal_output(radcal_out.read_text(encoding="utf-8", errors="ignore"))
    write_summary_csv(summary)
    write_report(radcal_exe, runtime_dll, summary)

    print(f"Wrote {radcal_out}")
    print(f"Wrote {OUTPUT_DIR / 'radcal_summary.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'radcal_run_report.md'}")


def first_existing(paths: list[Path], label: str) -> Path:
    for path in paths:
        if path.exists():
            return path
    searched = "\n".join(f"  - {path}" for path in paths)
    raise SystemExit(f"Could not find {label}. Searched:\n{searched}")


def find_openmp_runtime() -> Path | None:
    env_dir = os.environ.get("RADCAL_OPENMP_DLL_DIR")
    if env_dir:
        candidate = Path(env_dir) / "libiomp5md.dll"
        if candidate.exists():
            return candidate
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        if not folder:
            continue
        candidate = Path(folder) / "libiomp5md.dll"
        if candidate.exists():
            return candidate
    for pattern in RUNTIME_GLOBS:
        for match in glob.glob(pattern, recursive=True):
            candidate = Path(match)
            if candidate.exists():
                return candidate
    return None


def parse_radcal_output(text: str) -> dict[str, str]:
    summary: dict[str, str] = {}
    first_line = text.splitlines()[0] if text.splitlines() else ""
    if first_line.startswith("CASEID:"):
        summary["case_line"] = first_line.strip()
    for key, pattern in SUMMARY_PATTERNS.items():
        match = pattern.search(text)
        if match:
            summary[key] = match.group(1)
    return summary


def write_summary_csv(summary: dict[str, str]) -> None:
    with (OUTPUT_DIR / "radcal_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in summary.items():
            writer.writerow([key, value])


def write_report(radcal_exe: Path, runtime_dll: Path, summary: dict[str, str]) -> None:
    lines = [
        "# RADCAL Asset Smoke Test",
        "",
        "This run verifies that the downloaded RADCAL Windows executable can be launched",
        "from the portfolio when the Intel OpenMP runtime folder is prepended to PATH.",
        "",
        f"- RADCAL executable: `{radcal_exe}`",
        f"- Intel OpenMP DLL: `{runtime_dll}`",
        f"- Working directory: `{OUTPUT_DIR}`",
        "",
        "## Parsed Output",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in summary.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "Generated files:",
            "",
            "- `RADCAL.IN`",
            "- `RADCAL.OUT`",
            "- `TRANS_PORTFOLIO_RADCAL_SMOKE_TEST.TEC`",
            "- `radcal_summary.csv`",
            "",
        ]
    )
    (OUTPUT_DIR / "radcal_run_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
