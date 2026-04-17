from __future__ import annotations

from enum import Enum
from typing import Any


class ExecutionStrategy(Enum):
    SEQUENTIAL = "sequential"
    DEPENDENCY_BASED = "dependency_based"
    ADAPTIVE = "adaptive"


class ExecutionOrderPlanner:
    @staticmethod
    def plan_sequential(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return list(agents)

    @staticmethod
    def plan_by_dependencies(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        known_agents = {agent["name"] for agent in agents}
        graph = {
            agent["name"]: {dep for dep in agent.get("depends_on", []) if dep in known_agents}
            for agent in agents
        }
        registry = {agent["name"]: agent for agent in agents}
        ordered: list[dict[str, Any]] = []

        while graph:
            ready = sorted(name for name, deps in graph.items() if not deps)
            if not ready:
                cycle = ", ".join(sorted(graph))
                raise ValueError(f"Circular dependency detected: {cycle}")

            for name in ready:
                ordered.append(registry[name])
                graph.pop(name)
            for deps in graph.values():
                deps.difference_update(ready)

        return ordered

    @staticmethod
    def plan_adaptive(agents: list[dict[str, Any]], context: dict[str, Any]) -> list[dict[str, Any]]:
        prompt = context.get("original_prompt", "").lower()
        weighted = []
        for index, agent in enumerate(agents):
            score = 0
            tags = [tag.lower() for tag in agent.get("tags", [])]
            aliases = [alias.lower() for alias in agent.get("aliases", [])]
            for token in tags + aliases:
                if token and token in prompt:
                    score += 1
            weighted.append((score, index, agent))

        weighted.sort(key=lambda item: (-item[0], item[1]))
        return [agent for _, _, agent in weighted]

    @staticmethod
    def get_execution_plan(
        agents: list[dict[str, Any]],
        strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if strategy == ExecutionStrategy.DEPENDENCY_BASED:
            return ExecutionOrderPlanner.plan_by_dependencies(agents)
        if strategy == ExecutionStrategy.ADAPTIVE:
            return ExecutionOrderPlanner.plan_adaptive(agents, context or {})
        return ExecutionOrderPlanner.plan_sequential(agents)


def determine_execution_strategy(prompt: str) -> ExecutionStrategy:
    lowered = prompt.lower()
    if any(token in lowered for token in ("antes", "depois", "depende", "pipeline", "etapas")):
        return ExecutionStrategy.DEPENDENCY_BASED
    if any(token in lowered for token in ("condicional", "conforme resultado", "dependendo do resultado")):
        return ExecutionStrategy.ADAPTIVE
    return ExecutionStrategy.SEQUENTIAL
