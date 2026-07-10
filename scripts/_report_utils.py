"""Shared helpers for the run_project*_real_*.py workflow scripts."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (backend must be set before this import)

__all__ = ["plt", "prepare_output_dirs", "write_report"]


def prepare_output_dirs(output_dir: Path) -> None:
    """Create ``output_dir`` plus its ``figures/`` and ``tables/`` subdirectories."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(exist_ok=True)
    (output_dir / "tables").mkdir(exist_ok=True)


def write_report(output_dir: Path, filename: str, content: str) -> None:
    """Write a workflow report to ``output_dir/filename``."""

    (output_dir / filename).write_text(content, encoding="utf-8")
