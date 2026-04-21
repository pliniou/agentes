from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from core.catalog import load_manifests


BASE_DIR = Path(__file__).resolve().parent


def iter_skills() -> list[dict[str, Any]]:
    return load_manifests()


def find_skill(skills: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    normalized = name.strip().lower()
    for skill in skills:
        aliases = [alias.lower() for alias in skill.get("aliases", [])]
        if skill["name"].lower() == normalized or normalized in aliases:
            return skill
    return None


def run_skill(skill: dict[str, Any], prompt: str, context: dict[str, Any] | None = None) -> int:
    skill_dir = Path(skill["skill_dir"])
    wrapper = BASE_DIR / "core" / "agent_wrapper.py"
    command = [sys.executable, str(wrapper), str(skill_dir), prompt]
    if context is not None:
        command.append(json.dumps(context, ensure_ascii=False))

    completed = subprocess.run(command, cwd=str(skill_dir), check=False)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lista e executa agentes deste repositorio a partir dos manifestos skill.json."
    )
    parser.add_argument("skill", nargs="?", help="Nome ou alias do agente.")
    parser.add_argument("prompt", nargs="*", help="Prompt a ser enviado ao agente.")
    parser.add_argument("--list", action="store_true", help="Lista os agentes disponiveis.")
    parser.add_argument(
        "--context-json",
        help="Objeto JSON serializado com contexto extra para o agente.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    skills = iter_skills()

    if args.list or not args.skill:
        for skill in skills:
            print(f"- {skill['name']}: {skill['description']}")
        return 0

    skill = find_skill(skills, args.skill)
    if skill is None:
        print(f"Agente nao encontrado: {args.skill}", file=sys.stderr)
        return 1

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("Prompt obrigatorio.", file=sys.stderr)
        return 1

    context = None
    if args.context_json:
        context = json.loads(args.context_json)

    return run_skill(skill, prompt, context)


if __name__ == "__main__":
    raise SystemExit(main())
