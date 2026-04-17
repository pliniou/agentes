from __future__ import annotations

import sys
from pathlib import Path

def main() -> int:
    # Usage: python agent_wrapper.py <path_to_agent_dir> [prompt] [context]
    if len(sys.argv) < 2:
        print("Uso: agent_wrapper.py <diretorio_do_agente> [prompt] [contexto]", file=sys.stderr)
        return 1

    skill_dir = Path(sys.argv[1]).resolve()
    
    # We pass the remaining arguments starting from index 2 to runtime.py
    args_for_runtime = sys.argv[2:]

    # Import runtime
    from runtime import main as runtime_main
    return runtime_main(skill_dir, args_for_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
