import importlib.util
import os
import sys


def _load_runner():
    here = os.path.dirname(os.path.abspath(__file__))
    runner_path = os.path.join(
        here,
        "taichi_algorithm",
        "aot_py",
        "tools",
        "experiment.py",
    )
    spec = importlib.util.spec_from_file_location("_pixel_refine_aot_experiment", runner_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    return _load_runner().main()


if __name__ == "__main__":
    sys.exit(main())
