from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_DIR = Path(__file__).resolve().parents[1]
SPECIALISTS_DIR = REPO_DIR / "especialistas"
ORCHESTRATORS_DIR = REPO_DIR / "orchestrators"
MANIFEST_FILENAME = "skill.json"
MANIFEST_TYPE_SPECIALIST = "specialist"
MANIFEST_TYPE_ORCHESTRATOR = "orchestrator"
VALID_MANIFEST_TYPES = {
    MANIFEST_TYPE_SPECIALIST,
    MANIFEST_TYPE_ORCHESTRATOR,
}


def iter_manifest_paths(include_types: set[str] | None = None) -> list[Path]:
    requested_types = include_types or VALID_MANIFEST_TYPES
    manifests: list[Path] = []

    if MANIFEST_TYPE_SPECIALIST in requested_types and SPECIALISTS_DIR.is_dir():
        manifests.extend(SPECIALISTS_DIR.rglob(MANIFEST_FILENAME))
    if MANIFEST_TYPE_ORCHESTRATOR in requested_types and ORCHESTRATORS_DIR.is_dir():
        manifests.extend(ORCHESTRATORS_DIR.rglob(MANIFEST_FILENAME))

    return sorted(manifests)


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifests(include_types: set[str] | None = None) -> list[dict[str, Any]]:
    manifests: list[dict[str, Any]] = []
    for manifest_path in iter_manifest_paths(include_types):
        data = load_manifest(manifest_path)
        data["manifest_path"] = str(manifest_path)
        data["skill_dir"] = str(manifest_path.parent)
        manifests.append(data)
    return sorted(manifests, key=lambda item: item["name"])
