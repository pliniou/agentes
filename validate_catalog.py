from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
REQUIRED_FIELDS = {
    "name": str,
    "description": str,
    "language": str,
    "entry_point": str,
    "arguments": list,
    "aliases": list,
    "tags": list,
    "deliverables": list,
    "input_contract": dict,
    "output_contract": dict,
    "activation_criteria": str,
    "fallback_behavior": str,
}


def iter_manifests() -> list[Path]:
    return sorted(BASE_DIR.rglob("skill.json"))


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid json: {exc}"]

    for field, expected_type in REQUIRED_FIELDS.items():
        value = data.get(field)
        if value is None:
            errors.append(f"{path}: missing field '{field}'")
            continue
        if not isinstance(value, expected_type):
            errors.append(f"{path}: field '{field}' must be {expected_type.__name__}")

    if data.get("language") != "python":
        errors.append(f"{path}: language must be python")

    entry_path = path.parent / data.get("entry_point", "")
    if not entry_path.is_file():
        errors.append(f"{path}: entry point not found: {entry_path}")

    for list_field in ("aliases", "tags", "deliverables"):
        values = data.get(list_field, [])
        if not values:
            errors.append(f"{path}: field '{list_field}' must not be empty")
        elif not all(isinstance(item, str) and item.strip() for item in values):
            errors.append(f"{path}: field '{list_field}' must contain non-empty strings")

    return errors


def smoke_test_agent(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entry_path = (path.parent / data["entry_point"]).resolve()
    if data["name"] == "workflow-orchestrator":
        command = [sys.executable, str(entry_path), "--dry-run", "smoke orchestration for tests and review"]
    else:
        command = [sys.executable, str(entry_path), str(path.parent), f"smoke test for {data['name']}", '{"original_prompt":"smoke"}']

    completed = subprocess.run(
        command,
        cwd=str(path.parent),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return [f"{path}: smoke test failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"]
    return []


def main() -> int:
    manifests = iter_manifests()
    if not manifests:
        print("No manifests found.", file=sys.stderr)
        return 1

    errors: list[str] = []
    names: dict[str, Path] = {}

    for manifest in manifests:
        errors.extend(validate_manifest(manifest))
        data = json.loads(manifest.read_text(encoding="utf-8"))
        name = data["name"]
        if name in names:
            errors.append(f"Duplicate agent name '{name}': {names[name]} and {manifest}")
        else:
            names[name] = manifest

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    smoke_errors: list[str] = []
    for manifest in manifests:
        smoke_errors.extend(smoke_test_agent(manifest))

    if smoke_errors:
        print("\n".join(smoke_errors), file=sys.stderr)
        return 1

    print(f"Validated {len(manifests)} manifests and smoke-tested all agents successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
