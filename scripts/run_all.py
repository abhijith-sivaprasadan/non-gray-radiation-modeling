"""Run all portfolio workflows in sequence."""

from __future__ import annotations

import _bootstrap  # noqa: F401

import run_project1_real_hydrogen
import run_project2_real_particles
import run_project3_real_dom
import run_project4_real_surrogate


def main() -> None:
    run_project1_real_hydrogen.main()
    run_project2_real_particles.main()
    run_project3_real_dom.main()
    run_project4_real_surrogate.main()


if __name__ == "__main__":
    main()
