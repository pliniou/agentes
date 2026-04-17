from __future__ import annotations

import argparse
import json
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parents[1]
SHARED_DIR = REPO_DIR / "core"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from context import AgentContext, create_context_from_prompt, serialize_context
from execution import ExecutionOrderPlanner, determine_execution_strategy


STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "de",
    "do",
    "e",
    "em",
    "for",
    "in",
    "na",
    "no",
    "of",
    "on",
    "or",
    "para",
    "the",
    "to",
    "um",
    "uma",
    "with",
}


def normalize_text(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = "".join(ch if ch.isalnum() else " " for ch in ascii_text.lower())
    return " ".join(cleaned.split())


def tokenize(value: str) -> set[str]:
    return {
        token
        for token in normalize_text(value).split()
        if len(token) > 1 and token not in STOPWORDS
    }


def load_skills() -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for skill_file in REPO_DIR.rglob("skill.json"):
        data = json.loads(skill_file.read_text(encoding="utf-8"))
        if data["name"] == "workflow-orchestrator":
            continue
        data["skill_dir"] = str(skill_file.parent)
        skills.append(data)
    return sorted(skills, key=lambda item: item["name"])


def score_skill(skill: dict[str, Any], prompt: str, tokens: set[str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    name_tokens = tokenize(skill["name"].replace("-", " "))
    alias_tokens = [normalize_text(alias) for alias in skill.get("aliases", [])]
    tag_tokens = [normalize_text(tag) for tag in skill.get("tags", [])]
    description_tokens = tokenize(skill.get("description", ""))

    if normalize_text(skill["name"]) in prompt:
        score += 10
        reasons.append("name")

    alias_hits = [alias for alias in alias_tokens if alias and alias in prompt]
    if alias_hits:
        score += len(alias_hits) * 5
        reasons.append("aliases=" + ", ".join(alias_hits))

    overlap = sorted((name_tokens | description_tokens | set(tag_tokens)).intersection(tokens))
    if overlap:
        score += len(overlap)
        reasons.append("tokens=" + ", ".join(overlap[:6]))

    return score, reasons


def select_skills(prompt: str, skills: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    normalized_prompt = normalize_text(prompt)
    prompt_tokens = tokenize(prompt)
    ranked: list[dict[str, Any]] = []

    for skill in skills:
        score, reasons = score_skill(skill, normalized_prompt, prompt_tokens)
        if score <= 0:
            continue
        ranked.append({"skill": skill, "score": score, "reasons": reasons})

    ranked.sort(key=lambda item: (-item["score"], item["skill"]["name"]))
    selected = [item["skill"] for item in ranked[:3]]
    return selected, ranked


def execute_skill(skill: dict[str, Any], prompt: str, context: dict[str, Any]) -> str:
    skill_dir = Path(skill["skill_dir"])
    wrapper = REPO_DIR / "core" / "agent_wrapper.py"
    command = [sys.executable, str(wrapper), str(skill_dir), prompt, serialize_context(context)]
    completed = subprocess.run(command, cwd=str(skill_dir), capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Roteia prompts para os agentes especializados do repositorio.")
    parser.add_argument("prompt", nargs="*", help="Prompt a ser roteado.")
    parser.add_argument("--list", action="store_true", help="Lista os agentes disponiveis.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o plano sem executar.")
    parser.add_argument("--explain", action="store_true", help="Mostra os criterios de roteamento.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    skills = load_skills()

    if args.list:
        for skill in skills:
            print(f"- {skill['name']}: {skill['description']}")
        return 0

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("Prompt obrigatorio.", file=sys.stderr)
        return 1

    selected, ranked = select_skills(prompt, skills)
    if not selected:
        print("Nenhum agente correspondente encontrado.")
        return 1

    context = AgentContext()
    context.update(create_context_from_prompt(prompt))
    context_dict = context.to_dict()
    planner_context = {"original_prompt": prompt, **context_dict.get("data", {})}

    plan_input = []
    for skill in selected:
        plan_input.append(
            {
                "name": skill["name"],
                "aliases": skill.get("aliases", []),
                "tags": skill.get("tags", []),
                "depends_on": skill.get("depends_on", []),
            }
        )

    strategy = determine_execution_strategy(prompt)
    ordered_plan = ExecutionOrderPlanner.get_execution_plan(
        plan_input,
        strategy=strategy,
        context=planner_context,
    )
    ordered_names = [item["name"] for item in ordered_plan]
    ordered_skills = sorted(selected, key=lambda item: ordered_names.index(item["name"]))

    if args.explain or args.dry_run or len(ordered_skills) > 1:
        print("Routing plan:")
        for item in ranked[:5]:
            print(f"- {item['skill']['name']} score={item['score']:.2f} reasons={'; '.join(item['reasons'])}")
        print(f"Execution strategy: {strategy.value}")
        print("Execution order: " + ", ".join(ordered_names))
        if args.dry_run:
            return 0

    outputs = []
    for skill in ordered_skills:
        result = execute_skill(skill, prompt, context_dict)
        outputs.append({"agent": skill["name"], "result": result})

    if len(outputs) == 1:
        print(outputs[0]["result"])
        return 0

    print("# workflow-orchestrator")
    print("")
    print("Selected agents:")
    for output in outputs:
        print(f"- {output['agent']}")
    print("")
    print("Combined output:")
    for output in outputs:
        print("")
        print(output["result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
