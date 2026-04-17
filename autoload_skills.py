from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def iter_skills() -> list[dict]:
    skills: list[dict] = []
    for skill_file in BASE_DIR.rglob("skill.json"):
        try:
            data = json.loads(skill_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Manifesto invalido: {skill_file}: {exc}") from exc

        data["manifest_path"] = str(skill_file)
        data["skill_dir"] = str(skill_file.parent)
        skills.append(data)

    return sorted(skills, key=lambda item: item["name"])


def find_skill(skills: list[dict], name: str) -> dict | None:
    normalized = name.strip().lower()
    for skill in skills:
        aliases = [alias.lower() for alias in skill.get("aliases", [])]
        if skill["name"].lower() == normalized or normalized in aliases:
            return skill
    return None


def run_skill(skill: dict, prompt: str, context: dict | None = None) -> int:
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
