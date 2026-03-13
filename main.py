from __future__ import annotations

"""Entry point para execução local simples via `python main.py`."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from etl_dq.cli import main


if __name__ == "__main__":
    main()
