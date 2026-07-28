"""Background, isolated multi-backend AOT compilation orchestrator."""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SUITE = Path(__file__).with_name("compile_aot_backend_suite.py")


def compile_backend(backend: str, timeout: int = 900):
    env = os.environ.copy()
    env["PIXEL_REFINE_AOT_ARCH"] = backend
    env["PIXEL_REFINE_AOT_COMPILE_ONLY"] = "1"
    proc = subprocess.run(
        [sys.executable, str(SUITE), "--backend", backend],
        cwd=str(ROOT), env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return {"backend": backend, "returncode": proc.returncode,
            "ok": proc.returncode == 0, "output": proc.stdout[-12000:]}


def compile_all(backends, workers=None):
    workers = workers or min(len(backends), 3)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(compile_backend, backend) for backend in backends]
        return [future.result() for future in futures]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backends", nargs="+", default=["cpu", "vulkan", "opengl"],
                        choices=("cpu", "vulkan", "opengl"))
    parser.add_argument("--workers", type=int, default=0)
    args = parser.parse_args()
    import json
    print(json.dumps(compile_all(args.backends, args.workers or None), indent=2))
