# Contributing to Android Agents

1. Create a branch for your feature.
2. Add new agents inside the appropriate `especialistas/[domain]/` folder.
3. Ensure new agents follow the centralized execution model (using `core/agent_wrapper.py`).
4. Ensure `skill.json` specifies the `"name"` in Portuguese and `"description"` in English.
5. Create tests in the `tests/` directory if modifying core logic.
