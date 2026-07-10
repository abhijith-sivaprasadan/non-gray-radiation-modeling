"""Check whether Firemodels executables are installed and reachable.

The cloned Firemodels repositories are source trees. The GUI can only launch
FDS/Smokeview/RADCAL runs after corresponding executables are built or installed.
This script records that boundary in generated JSON and Markdown reports.
"""

from __future__ import annotations

import _bootstrap

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil

PROJECT_ROOT = _bootstrap.PROJECT_ROOT
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

RELEASE_INFO = {
    "name": "FDS-6.11.0_SMV-6.11.0",
    "tag": "FDS-6.11.0",
    "commit": "369a20b",
    "release_date": "2026-05-18",
    "release_url": "https://github.com/firemodels/fds/releases/tag/FDS-6.11.0",
    "windows_installer": "FDS-6.11.0_SMV-6.11.0_win.exe",
    "windows_installer_url": (
        "https://github.com/firemodels/fds/releases/download/FDS-6.11.0/"
        "FDS-6.11.0_SMV-6.11.0_win.exe"
    ),
    "windows_installer_size_mb": 174,
    "windows_installer_sha256": (
        "b42281eb73b92a948fe21e80b22089da99c50574103d17c4d4ff609290a0ddb2"
    ),
}

TOOL_ALIASES = {
    "FDS solver": ["fds.exe", "fds"],
    "Smokeview": ["smokeview.exe", "smv.exe", "smokeview", "smv"],
    "RADCAL": ["radcal.exe", "radcal_win_64.exe", "radcal"],
}

ASSET_ROOTS = [
    PROJECT_ROOT / "Assets from Github",
]

DOWNLOADED_ASSETS = {
    "FDS/SMV Windows installer": {
        "role": "installer",
        "paths": [
            PROJECT_ROOT / "Assets from Github" / "FDS" / "FDS-6.11.0_SMV-6.11.0_win.exe",
        ],
        "sha256": RELEASE_INFO["windows_installer_sha256"],
    },
    "RADCAL Windows executable": {
        "role": "standalone_executable",
        "paths": [
            PROJECT_ROOT / "Assets from Github" / "RADCAL" / "radcal_win_64.exe",
        ],
        "sha256": None,
    },
    "Smokeview Windows installer": {
        "role": "installer",
        "paths": [
            PROJECT_ROOT / "Assets from Github" / "SmokeView" / "SMV-6.11.1_win.exe",
        ],
        "sha256": None,
    },
}

SOURCE_REPO_HINTS = {
    "fds": [PROJECT_ROOT / "fds"],
    "smv": [PROJECT_ROOT / "smv"],
    "radcal": [PROJECT_ROOT / "radcal"],
    "exp": [PROJECT_ROOT / "exp"],
    "cfast": [PROJECT_ROOT / "cfast"],
}

INSTALLER_CANDIDATES = [
    PROJECT_ROOT / RELEASE_INFO["windows_installer"],
    PROJECT_ROOT / "Assets from Github" / "FDS" / RELEASE_INFO["windows_installer"],
    Path.home() / "Downloads" / RELEASE_INFO["windows_installer"],
]

INSTALL_ROOTS = [
    Path(r"C:\Program Files\firemodels"),
    Path(r"C:\Program Files (x86)\firemodels"),
    Path(r"C:\Program Files\FDS"),
    Path(r"C:\Program Files (x86)\FDS"),
    Path(r"C:\Program Files\NIST"),
    Path(r"C:\Program Files (x86)\NIST"),
    PROJECT_ROOT,
    PROJECT_ROOT / "Assets from Github",
]


def main() -> None:
    """Write a machine-readable and human-readable Firemodels tool status."""

    status = build_status()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUTS_DIR / "firemodels_tool_status.json"
    md_path = OUTPUTS_DIR / "firemodels_tool_status.md"
    json_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(status), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(render_console_summary(status))


def build_status() -> dict[str, object]:
    tool_status = {
        tool: {
            "aliases": aliases,
            "path_matches": find_on_path(aliases),
            "local_matches": find_in_install_roots(aliases),
        }
        for tool, aliases in TOOL_ALIASES.items()
    }
    installer_status = inspect_installer_candidates()
    repo_status = inspect_source_repositories()
    asset_status = inspect_downloaded_assets()

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "release": RELEASE_INFO,
        "tools": tool_status,
        "installer_candidates": installer_status,
        "downloaded_assets": asset_status,
        "source_repositories": repo_status,
        "ready_for_gui_launch": {
            "fds": bool(tool_status["FDS solver"]["path_matches"]),
            "smokeview": bool(tool_status["Smokeview"]["path_matches"]),
            "radcal": bool(tool_status["RADCAL"]["path_matches"]),
        },
        "local_executable_assets": {
            "radcal": bool(tool_status["RADCAL"]["local_matches"]),
        },
        "workflow_readiness": {
            "radcal_asset_smoke_test": (
                bool(tool_status["RADCAL"]["local_matches"])
                and (PROJECT_ROOT / "outputs" / "project5_radcal_asset" / "RADCAL.OUT").exists()
            )
        },
    }


def find_on_path(aliases: list[str]) -> list[str]:
    matches: list[str] = []
    for alias in aliases:
        hit = shutil.which(alias)
        if hit is not None:
            add_unique(matches, str(Path(hit)))
    return matches


def find_in_install_roots(aliases: list[str]) -> list[str]:
    names = {alias.lower() for alias in aliases}
    matches: list[str] = []
    for root in INSTALL_ROOTS:
        if not root.exists():
            continue
        for child in iter_depth_limited(root, max_depth=5):
            if child.is_file() and child.name.lower() in names:
                add_unique(matches, str(child))
    return matches


def iter_depth_limited(root: Path, max_depth: int):
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            children = list(current.iterdir())
        except (OSError, PermissionError):
            continue
        for child in children:
            yield child
            if not child.is_dir():
                continue
            try:
                depth = len(child.relative_to(root).parts)
            except ValueError:
                continue
            if depth < max_depth and child.name.lower() not in {".git", "__pycache__"}:
                stack.append(child)


def inspect_installer_candidates() -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    expected_hash = RELEASE_INFO["windows_installer_sha256"]
    for path in INSTALLER_CANDIDATES:
        exists = path.exists()
        item: dict[str, object] = {
            "path": str(path),
            "exists": exists,
            "sha256": None,
            "sha256_matches_release": False,
        }
        if exists and path.is_file():
            digest = sha256_file(path)
            item["sha256"] = digest
            item["sha256_matches_release"] = digest.lower() == expected_hash
            item["size_bytes"] = path.stat().st_size
        candidates.append(item)
    return candidates


def inspect_downloaded_assets() -> list[dict[str, object]]:
    assets: list[dict[str, object]] = []
    for label, spec in DOWNLOADED_ASSETS.items():
        expected_hash = spec["sha256"]
        assert isinstance(spec["paths"], list)
        for path in spec["paths"]:
            exists = path.exists()
            item: dict[str, object] = {
                "label": label,
                "role": spec["role"],
                "path": str(path),
                "exists": exists,
                "sha256": None,
                "sha256_matches_expected": None,
            }
            if exists and path.is_file():
                digest = sha256_file(path)
                item["sha256"] = digest
                item["size_bytes"] = path.stat().st_size
                if expected_hash is not None:
                    item["sha256_matches_expected"] = digest.lower() == str(expected_hash).lower()
            assets.append(item)
    return assets


def inspect_source_repositories() -> dict[str, list[dict[str, object]]]:
    repos: dict[str, list[dict[str, object]]] = {}
    for name, paths in SOURCE_REPO_HINTS.items():
        repos[name] = []
        for path in unique_paths(paths):
            repos[name].append(
                {
                    "path": str(path),
                    "exists": path.exists(),
                    "git_remote": read_git_remote(path),
                }
            )
    return repos


def read_git_remote(path: Path) -> str | None:
    config = path / ".git" / "config"
    if not config.exists():
        return None
    for line in config.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("url = "):
            return stripped.removeprefix("url = ").strip()
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_markdown(status: dict[str, object]) -> str:
    release = status["release"]
    assert isinstance(release, dict)
    lines = [
        "# Firemodels Tool Status",
        "",
        f"Generated UTC: `{status['generated_at_utc']}`",
        "",
        "## Official Release Target",
        "",
        f"- Release: [{release['name']}]({release['release_url']})",
        f"- Tag: `{release['tag']}`",
        f"- Commit: `{release['commit']}`",
        f"- Windows installer: [`{release['windows_installer']}`]"
        f"({release['windows_installer_url']})",
        f"- Expected SHA256: `{release['windows_installer_sha256']}`",
        "",
        "## Executable Detection",
        "",
        "| Tool | PATH result | Local executable search |",
        "| --- | --- | --- |",
    ]

    tools = status["tools"]
    assert isinstance(tools, dict)
    for name, details in tools.items():
        assert isinstance(details, dict)
        path_matches = render_matches(details["path_matches"])
        local_matches = render_matches(details["local_matches"])
        lines.append(f"| {name} | {path_matches} | {local_matches} |")

    lines.extend(
        [
            "",
            "## Installer Candidates",
            "",
            "| Path | Present | SHA256 status |",
            "| --- | ---: | --- |",
        ]
    )
    for item in status["installer_candidates"]:
        assert isinstance(item, dict)
        present = "yes" if item["exists"] else "no"
        hash_status = "not checked"
        if item["sha256"] is not None:
            hash_status = "matches release" if item["sha256_matches_release"] else "does not match"
        lines.append(f"| `{item['path']}` | {present} | {hash_status} |")

    lines.extend(
        [
            "",
            "## Downloaded GitHub Assets",
            "",
            "| Asset | Role | Path | Present | SHA256 status |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for item in status["downloaded_assets"]:
        assert isinstance(item, dict)
        present = "yes" if item["exists"] else "no"
        hash_status = "not checked"
        if item["sha256_matches_expected"] is True:
            hash_status = "matches expected release hash"
        elif item["sha256_matches_expected"] is False:
            hash_status = "does not match expected release hash"
        elif item["sha256"] is not None:
            hash_status = str(item["sha256"])
        lines.append(
            f"| {item['label']} | `{item['role']}` | `{item['path']}` | "
            f"{present} | {hash_status} |"
        )

    lines.extend(
        [
            "",
            "## Source Repositories",
            "",
            "| Repo | Local path | Present | Remote |",
            "| --- | --- | ---: | --- |",
        ]
    )
    repos = status["source_repositories"]
    assert isinstance(repos, dict)
    for repo, entries in repos.items():
        assert isinstance(entries, list)
        for entry in entries:
            assert isinstance(entry, dict)
            present = "yes" if entry["exists"] else "no"
            remote = entry["git_remote"] or ""
            lines.append(f"| `{repo}` | `{entry['path']}` | {present} | `{remote}` |")

    workflows = status["workflow_readiness"]
    assert isinstance(workflows, dict)
    lines.extend(
        [
            "",
            "## Workflow Readiness",
            "",
            "| Workflow | Status | Evidence |",
            "| --- | --- | --- |",
            (
                "| RADCAL asset smoke test | "
                f"{'ready' if workflows['radcal_asset_smoke_test'] else 'not ready'} | "
                "`outputs/project5_radcal_asset/RADCAL.OUT` |"
            ),
        ]
    )

    lines.extend(
        [
            "",
            "## Meaning For The GUI",
            "",
            "The Fortran GUI can regenerate and view this portfolio today. Full FDS, "
            "or Smokeview launch buttons should only be treated as operational after the "
            "corresponding executable is installed on PATH and smoke-tested from the project "
            "working directory.",
            "",
            "The RADCAL asset workflow is GUI-runnable through the wrapper script when the "
            "smoke-test output is marked ready above.",
            "",
            "Current next action:",
            render_next_action(status),
            "",
        ]
    )
    return "\n".join(lines)


def render_matches(matches: object) -> str:
    assert isinstance(matches, list)
    if not matches:
        return "not detected"
    return "<br>".join(f"`{match}`" for match in matches)


def render_next_action(status: dict[str, object]) -> str:
    ready = status["ready_for_gui_launch"]
    assert isinstance(ready, dict)
    if ready["fds"] and ready["smokeview"]:
        return "- FDS and Smokeview are detectable on PATH; GUI run/open buttons can target them."
    if ready["fds"]:
        return "- FDS is detectable, but Smokeview is not; GUI FDS run support can be added first."
    workflows = status["workflow_readiness"]
    assert isinstance(workflows, dict)
    if workflows["radcal_asset_smoke_test"]:
        return (
            "- RADCAL is ready through the GUI wrapper; install or build the official "
            "FDS/Smokeview release before adding real FDS run buttons."
        )
    return (
        "- Install or build the official FDS/Smokeview release before adding real FDS run "
        "buttons to the GUI; resolve the RADCAL invocation before treating it as verified."
    )


def render_console_summary(status: dict[str, object]) -> str:
    ready = status["ready_for_gui_launch"]
    assert isinstance(ready, dict)
    detected = [name for name, is_ready in ready.items() if is_ready]
    if detected:
        return "PATH-ready executable detected: " + ", ".join(detected)
    local_assets = status["local_executable_assets"]
    assert isinstance(local_assets, dict)
    asset_hits = [name for name, is_present in local_assets.items() if is_present]
    workflows = status["workflow_readiness"]
    assert isinstance(workflows, dict)
    if workflows["radcal_asset_smoke_test"]:
        return "RADCAL asset workflow is smoke-tested; FDS/Smokeview are not PATH-ready."
    if asset_hits:
        return "Local executable asset detected outside PATH: " + ", ".join(asset_hits)
    return "No FDS, Smokeview, or RADCAL executable was detected."


def add_unique(items: list[str], value: str) -> None:
    normalized = os.path.normcase(os.path.abspath(value))
    existing = {os.path.normcase(os.path.abspath(item)) for item in items}
    if normalized not in existing:
        items.append(value)


def unique_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        normalized = os.path.normcase(os.path.abspath(path))
        if normalized not in seen:
            seen.add(normalized)
            unique.append(path)
    return unique


if __name__ == "__main__":
    main()
