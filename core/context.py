from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


FILE_PATTERN = re.compile(r"[\w./\\-]+\.(?:py|kt|ts|tsx|js|jsx|java|go|rs|json|ya?ml|toml|md)")


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentContext:
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    data: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.history.append({"action": "set", "key": key, "timestamp": _timestamp()})

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def update(self, values: dict[str, Any]) -> None:
        self.data.update(values)
        self.history.append(
            {"action": "update", "keys": sorted(values.keys()), "timestamp": _timestamp()}
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "data": self.data.copy(),
            "history": self.history.copy(),
        }


def create_context_from_prompt(prompt: str) -> dict[str, Any]:
    lowered = prompt.lower()
    technologies = [
        token
        for token in (
            "python",
            "kotlin",
            "java",
            "compose",
            "jetpack",
            "android",
            "room",
            "retrofit",
            "hilt",
            "workmanager",
            "navigation",
            "gradle",
            "ios",
            "backend",
            "frontend",
            "api",
            "database",
            "ci",
            "cd",
        )
        if token in lowered
    ]
    return {
        "original_prompt": prompt,
        "prompt_length": len(prompt),
        "prompt_words": prompt.split(),
        "referenced_files": FILE_PATTERN.findall(prompt),
        "mentioned_technologies": technologies,
        "timestamp": _timestamp(),
    }


def serialize_context(context: Any) -> str:
    payload = context.to_dict() if hasattr(context, "to_dict") else context
    return json.dumps(payload, ensure_ascii=False)


def deserialize_context(context_str: str) -> dict[str, Any]:
    try:
        return json.loads(context_str)
    except json.JSONDecodeError:
        return {"error": "invalid_context", "raw": context_str}
