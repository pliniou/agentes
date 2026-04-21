from __future__ import annotations

import catalog
from execution import ExecutionOrderPlanner


def test_iter_manifest_paths_is_scoped_to_catalog_directories(tmp_path, monkeypatch) -> None:
    specialists_dir = tmp_path / "especialistas"
    orchestrators_dir = tmp_path / "orchestrators"
    ignored_dir = tmp_path / "tmp"

    for path in (
        specialists_dir / "one" / "skill.json",
        orchestrators_dir / "router" / "skill.json",
        ignored_dir / "rogue" / "skill.json",
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(catalog, "SPECIALISTS_DIR", specialists_dir)
    monkeypatch.setattr(catalog, "ORCHESTRATORS_DIR", orchestrators_dir)

    manifests = catalog.iter_manifest_paths()

    assert manifests == sorted(
        [
            specialists_dir / "one" / "skill.json",
            orchestrators_dir / "router" / "skill.json",
        ]
    )


def test_dependency_planner_injects_missing_dependencies_from_catalog() -> None:
    selected = [{"name": "especialista-planejamento", "depends_on": ["especialista-analise-projeto"]}]
    available = [
        {"name": "especialista-planejamento", "depends_on": ["especialista-analise-projeto"]},
        {"name": "especialista-analise-projeto", "depends_on": []},
    ]

    plan = ExecutionOrderPlanner.plan_by_dependencies(selected, available_agents=available)

    assert [item["name"] for item in plan] == [
        "especialista-analise-projeto",
        "especialista-planejamento",
    ]


def test_get_execution_plan_respects_dependencies_even_in_sequential_mode() -> None:
    selected = [{"name": "especialista-planejamento", "depends_on": ["especialista-analise-projeto"]}]
    available = [
        {"name": "especialista-planejamento", "depends_on": ["especialista-analise-projeto"]},
        {"name": "especialista-analise-projeto", "depends_on": []},
    ]

    plan = ExecutionOrderPlanner.get_execution_plan(selected, available_agents=available)

    assert [item["name"] for item in plan] == [
        "especialista-analise-projeto",
        "especialista-planejamento",
    ]


def test_dependency_planner_rejects_missing_catalog_dependency() -> None:
    selected = [{"name": "especialista-planejamento", "depends_on": ["especialista-inexistente"]}]

    try:
        ExecutionOrderPlanner.plan_by_dependencies(selected)
    except ValueError as exc:
        assert "especialista-inexistente" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unresolved dependency")
