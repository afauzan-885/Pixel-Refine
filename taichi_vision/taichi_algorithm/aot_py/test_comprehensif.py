"""Compatibility entry point for the standalone Performance Settings test."""

import sys
from pathlib import Path
from runpy import run_path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


if __name__ == "__main__":
    run_path(
        str(
            _PROJECT_ROOT
            / "pixel_refine_desktop"
            / "ui"
            / "views"
            / "settings"
            / "Perfomance"
            / "test_comprehensif.py"
        ),
        run_name="__main__",
    )
