from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_DELIVERABLES = [
    "analise do estado atual",
    "riscos e conflitos relevantes",
    "plano de acao priorizado",
    "criterios de validacao",
]


def _load_manifest(skill_dir: Path) -> dict[str, Any]:
    return json.loads((skill_dir / "skill.json").read_text(encoding="utf-8"))


def _load_context(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_context": raw}


def _guess_focus(manifest: dict[str, Any], prompt: str) -> list[str]:
    focus: list[str] = []
    lowered = prompt.lower()
    for token in manifest.get("aliases", []) + manifest.get("tags", []):
        normalized = str(token).strip().lower()
        if normalized and normalized in lowered and normalized not in focus:
            focus.append(normalized)
    if not focus:
        focus.extend(manifest.get("tags", [])[:4])
    return focus[:6]


def _deliverables(manifest: dict[str, Any]) -> list[str]:
    output_description = manifest.get("output_contract", {}).get("description", "")
    deliverables = manifest.get("deliverables")
    if isinstance(deliverables, list) and deliverables:
        return deliverables[:5]
    if output_description:
        return [output_description]
    return DEFAULT_DELIVERABLES


def render_response(skill_dir: Path, prompt: str, raw_context: str | None = None) -> str:
    manifest = _load_manifest(skill_dir)
    context = _load_context(raw_context)
    focus = _guess_focus(manifest, prompt)
    deliverables = _deliverables(manifest)
    dependencies = manifest.get("depends_on", [])

    lines = [
        f"# {manifest['name']}",
        "",
        f"Purpose: {manifest['description']}",
        f"Prompt: {prompt}",
    ]

    if focus:
        lines.append(f"Focus: {', '.join(focus)}")
    if dependencies:
        lines.append(f"Depends on: {', '.join(dependencies)}")
    if context:
        lines.append("Context keys: " + ", ".join(sorted(context.keys())))

    lines.extend(["", "Recommended output:", *[f"- {item}" for item in deliverables]])

    activation = manifest.get("activation_criteria")
    fallback = manifest.get("fallback_behavior")
    if activation:
        lines.extend(["", f"Activation criteria: {activation}"])
    if fallback:
        lines.append(f"Fallback behavior: {fallback}")

    return "\n".join(lines) + "\n"


def main(skill_dir: Path | None = None, argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    current_skill_dir = skill_dir or Path(__file__).resolve().parent

    prompt = args[0].strip() if args else ""
    if not prompt:
        print("Prompt obrigatorio.", file=sys.stderr)
        return 1

    raw_context = args[1] if len(args) > 1 else None
    print(render_response(current_skill_dir, prompt, raw_context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
