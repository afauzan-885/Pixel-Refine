"""Bounded native moving-flow full-vs-explicit-block candidate probe.

The probe is intentionally evidence-only: it enables the block policy for one
synthetic frame pair, compares it with the same backend's full graph, and never
promotes the result to the native evidence registry automatically.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run(*, size: int = 64, block_size: int = 16) -> dict[str, object]:
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm import aot_api

    size = int(size)
    block_size = int(block_size)
    if size < 32 or block_size <= 0:
        raise ValueError("size must be >= 32 and block_size must be positive")
    rows = np.linspace(0.0, 1.0, size, dtype=np.float32)[:, None]
    cols = np.linspace(0.0, 1.0, size, dtype=np.float32)[None, :]
    reference = np.ascontiguousarray((rows + cols) * np.float32(100.0))
    current = np.empty_like(reference)
    current[:, 2:] = reference[:, :-2]
    current[:, :2] = reference[:, :2]
    params = dict(
        pyr_scale=0.5,
        num_levels=1,
        win_size=7,
        num_iters=1,
        poly_n=5,
        poly_sigma=1.1,
    )

    aot_api.set_block_mode(False, size=block_size, threshold_bytes=0)
    full = np.asarray(aot_api._farneback_flow_full(reference, current, **params))
    aot_api.set_block_mode(True, size=block_size, threshold_bytes=0)
    blocked = np.asarray(aot_api.farneback_flow(reference, current, **params))
    repeated = np.asarray(aot_api.farneback_flow(reference, current, **params))
    plan = getattr(taichi_aot.engine._local, "last_block_plan", None)
    max_error = float(np.max(np.abs(blocked - full)))
    return {
        "backend": str(getattr(taichi_aot.engine, "arch", "unknown")),
        "device": str(getattr(taichi_aot.engine, "gpu_name", "") or ""),
        "shape": list(blocked.shape),
        "block_size": block_size,
        "finite": bool(np.isfinite(blocked).all()),
        "max_abs_error_vs_same_backend_full": max_error,
        "mean_abs_error_vs_same_backend_full": float(np.mean(np.abs(blocked - full))),
        "repeat_max_abs_error": float(np.max(np.abs(blocked - repeated))),
        "deterministic_merge": bool(np.array_equal(blocked, repeated)),
        "same_backend": True,
        "block_plan": plan,
        "block_selected": bool(isinstance(plan, dict) and plan.get("selected")),
        "evidence_status": "candidate_only",
        "native_runtime": True,
        "passed": bool(
            blocked.shape == (size, size, 2)
            and np.isfinite(blocked).all()
            and max_error <= 1e-5
            and isinstance(plan, dict)
            and bool(plan.get("selected"))
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=64)
    parser.add_argument("--block-size", type=int, default=16)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    try:
        result = run(size=args.size, block_size=args.block_size)
    except Exception as exc:
        result = {
            "backend": os.environ.get("BACKEND", "auto"),
            "error": f"{type(exc).__name__}: {exc}",
            "evidence_status": "fail_closed",
            "native_runtime": False,
            "passed": False,
        }
    text = json.dumps(result, indent=2, sort_keys=True, default=str)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
