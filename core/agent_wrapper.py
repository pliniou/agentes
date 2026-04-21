from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


WRAPPER_PATH = Path(__file__).resolve()
RUNTIME_PATH = WRAPPER_PATH.with_name("runtime.py")


def _load_manifest(skill_dir: Path) -> dict[str, object]:
    return json.loads((skill_dir / "skill.json").read_text(encoding="utf-8"))


def _run_shared_runtime(skill_dir: Path, args_for_runtime: list[str]) -> int:
    from runtime import main as runtime_main

    return runtime_main(skill_dir, args_for_runtime)


def main() -> int:
    # Usage: python agent_wrapper.py <path_to_agent_dir> [prompt] [context]
    if len(sys.argv) < 2:
        print("Uso: agent_wrapper.py <diretorio_do_agente> [prompt] [contexto]", file=sys.stderr)
        return 1

    skill_dir = Path(sys.argv[1]).resolve()
    manifest_path = skill_dir / "skill.json"
    if not manifest_path.is_file():
        print(f"Manifesto nao encontrado: {manifest_path}", file=sys.stderr)
        return 1

    args_for_runtime = sys.argv[2:]
    manifest = _load_manifest(skill_dir)
    raw_entry_point = str(manifest.get("entry_point", "")).strip()

    if not raw_entry_point:
        return _run_shared_runtime(skill_dir, args_for_runtime)

    entry_point = (skill_dir / raw_entry_point).resolve()
    if entry_point in {WRAPPER_PATH, RUNTIME_PATH}:
        return _run_shared_runtime(skill_dir, args_for_runtime)

    if not entry_point.is_file():
        print(f"Entry point nao encontrado: {entry_point}", file=sys.stderr)
        return 1

    completed = subprocess.run(
        [sys.executable, str(entry_point), str(skill_dir), *args_for_runtime],
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
