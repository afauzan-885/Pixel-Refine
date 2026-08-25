"""Compatibility entry point for the image-family AOT tests."""

import sys
from pathlib import Path
from runpy import run_module

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


if __name__ == "__main__":
    run_module(
        "taichi_vision.taichi_algorithm.aot_py.tests.test_image_aot",
        run_name="__main__",
    )
