from __future__ import annotations

import sys
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = REPO_DIR / "core"

for path in (REPO_DIR, CORE_DIR):
    as_text = str(path)
    if as_text not in sys.path:
        sys.path.insert(0, as_text)
