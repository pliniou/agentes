from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parent.parent
WRAPPER_PATH = REPO_DIR / "core" / "agent_wrapper.py"


def _write_manifest(skill_dir: Path, manifest: dict[str, object]) -> None:
    (skill_dir / "skill.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def test_wrapper_executes_custom_entry_point(tmp_path) -> None:
    skill_dir = tmp_path / "custom-skill"
    skill_dir.mkdir()
    (skill_dir / "custom_entry.py").write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import json",
                "import sys",
                'print(json.dumps({"argv": sys.argv[1:]}))',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_manifest(
        skill_dir,
        {
            "type": "specialist",
            "name": "custom-skill",
            "description": "custom",
            "language": "python",
            "entry_point": "custom_entry.py",
            "arguments": ["prompt"],
            "aliases": ["custom"],
            "tags": ["custom"],
            "deliverables": ["custom"],
            "input_contract": {"type": "string", "description": "desc", "format": "text"},
            "output_contract": {"type": "text/markdown", "description": "desc", "format": "md"},
            "activation_criteria": "custom",
            "fallback_behavior": "custom",
            "depends_on": [],
        },
    )

    completed = subprocess.run(
        [sys.executable, str(WRAPPER_PATH), str(skill_dir), "hello", '{"k":"v"}'],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert json.loads(completed.stdout)["argv"] == [str(skill_dir), "hello", '{"k":"v"}']


def test_wrapper_falls_back_to_shared_runtime_when_manifest_points_to_wrapper(tmp_path) -> None:
    skill_dir = tmp_path / "runtime-skill"
    skill_dir.mkdir()
    relative_wrapper = os.path.relpath(WRAPPER_PATH, skill_dir).replace("\\", "/")
    _write_manifest(
        skill_dir,
        {
            "type": "specialist",
            "name": "runtime-skill",
            "description": "runtime",
            "language": "python",
            "entry_point": relative_wrapper,
            "arguments": ["prompt"],
            "aliases": ["runtime"],
            "tags": ["runtime"],
            "deliverables": ["runtime"],
            "input_contract": {"type": "string", "description": "desc", "format": "text"},
            "output_contract": {"type": "text/markdown", "description": "desc", "format": "md"},
            "activation_criteria": "runtime",
            "fallback_behavior": "runtime",
            "depends_on": [],
        },
    )

    completed = subprocess.run(
        [sys.executable, str(WRAPPER_PATH), str(skill_dir), "hello runtime"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "# runtime-skill" in completed.stdout
    assert "Prompt: hello runtime" in completed.stdout
