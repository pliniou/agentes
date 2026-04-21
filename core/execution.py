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
    def expand_dependencies(
        agents: list[dict[str, Any]],
        available_agents: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        registry = {agent["name"]: agent for agent in (available_agents or agents)}
        selected_names = list(dict.fromkeys(agent["name"] for agent in agents))
        expanded: dict[str, dict[str, Any]] = {}
        visiting: set[str] = set()

        def visit(agent_name: str) -> None:
            if agent_name in expanded:
                return
            if agent_name in visiting:
                cycle = ", ".join(sorted(visiting | {agent_name}))
                raise ValueError(f"Circular dependency detected: {cycle}")

            agent = registry.get(agent_name)
            if agent is None:
                raise ValueError(f"Missing dependency declaration target: {agent_name}")

            visiting.add(agent_name)
            for dependency in agent.get("depends_on", []):
                visit(dependency)
            visiting.remove(agent_name)
            expanded[agent_name] = agent

        for name in selected_names:
            visit(name)

        return list(expanded.values())

    @staticmethod
    def plan_by_dependencies(
        agents: list[dict[str, Any]],
        available_agents: list[dict[str, Any]] | None = None,
        preferred_order: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        expanded_agents = ExecutionOrderPlanner.expand_dependencies(agents, available_agents)
        known_agents = {agent["name"] for agent in expanded_agents}
        preferred_index = {
            name: index
            for index, name in enumerate(preferred_order or [agent["name"] for agent in expanded_agents])
        }
        graph = {
            agent["name"]: {dep for dep in agent.get("depends_on", []) if dep in known_agents}
            for agent in expanded_agents
        }
        registry = {agent["name"]: agent for agent in expanded_agents}
        ordered: list[dict[str, Any]] = []

        while graph:
            ready = sorted(
                (name for name, deps in graph.items() if not deps),
                key=lambda name: (preferred_index.get(name, len(preferred_index)), name),
            )
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
        available_agents: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        expanded_agents = ExecutionOrderPlanner.expand_dependencies(agents, available_agents)

        if strategy == ExecutionStrategy.ADAPTIVE:
            adaptive_plan = ExecutionOrderPlanner.plan_adaptive(expanded_agents, context or {})
            return ExecutionOrderPlanner.plan_by_dependencies(
                adaptive_plan,
                available_agents=expanded_agents,
                preferred_order=[agent["name"] for agent in adaptive_plan],
            )

        if strategy == ExecutionStrategy.DEPENDENCY_BASED:
            return ExecutionOrderPlanner.plan_by_dependencies(
                expanded_agents,
                available_agents=expanded_agents,
            )

        if any(agent.get("depends_on") for agent in expanded_agents):
            return ExecutionOrderPlanner.plan_by_dependencies(
                expanded_agents,
                available_agents=expanded_agents,
                preferred_order=[agent["name"] for agent in expanded_agents],
            )

        return ExecutionOrderPlanner.plan_sequential(expanded_agents)


def determine_execution_strategy(prompt: str) -> ExecutionStrategy:
    lowered = prompt.lower()
    if any(token in lowered for token in ("antes", "depois", "depende", "pipeline", "etapas")):
        return ExecutionStrategy.DEPENDENCY_BASED
    if any(token in lowered for token in ("condicional", "conforme resultado", "dependendo do resultado")):
        return ExecutionStrategy.ADAPTIVE
    return ExecutionStrategy.SEQUENTIAL
