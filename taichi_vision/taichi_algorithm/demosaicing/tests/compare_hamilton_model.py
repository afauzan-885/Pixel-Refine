"""Validate the float64 Hamilton model against the compiled AOT graph.

The parameter search in ``search_hamilton_params.py`` is only meaningful if the
model predicts the graph, so this comparison is the evidence that licenses it.
It is a tool rather than a unit test because it needs the CPU artifact and a
live engine, while the rest of the demosaic suite is deliberately backend free.

Passing criterion: the two agree to float32 precision almost everywhere, and the
only pixels that differ materially are the ones sitting exactly on a discrete
decision boundary (``dh < dv``, ``e1 < e2``, ``rg*bg < 0``), where a one-ULP
difference legitimately selects a different branch.  Those pixels are reported
as a rate, not hidden.

Example:
    python compare_hamilton_model.py --backend cpu --size 128
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_TESTS_DIR = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - repository invariant
        raise ImportError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


harness = _load("pixel_refine_model_harness", _TESTS_DIR / "demosaic_quality_harness.py")
model = _load("pixel_refine_model_reference", _TESTS_DIR / "hamilton_reference.py")

# A decision-boundary flip changes one pixel by a visible amount; anything above
# this rate means the two implementations differ systematically.
MAX_BOUNDARY_RATE = 0.001


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--size", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--cfa", nargs=4, type=int, default=[0, 1, 3, 2])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    os.environ["PIXEL_REFINE_AOT_ARCH"] = args.backend
    os.environ["AOT_ARCH"] = args.backend
    import taichi_vision.taichi_aot as taichi_aot

    rng = np.random.default_rng(args.seed)
    bayer = rng.random((args.size, args.size), dtype=np.float32)
    weights = (1.4, 1.0, 1.6, 1.02)
    cmatrix = np.eye(3, dtype=np.float32)
    scalars = (*weights, cmatrix, 0.0, 1.0, *args.cfa)

    observed, timing = harness.run_full_frame(
        taichi_aot, "hamilton", bayer, scalars, runs=1, resident=True
    )
    expected = model.hamilton_model(
        bayer, weights, 0.0, 1.0, tuple(args.cfa), model.HamiltonParams()
    ).astype(np.float32)

    if observed.shape != expected.shape:
        print(f"SHAPE MISMATCH observed={observed.shape} expected={expected.shape}")
        return 1

    diff = np.abs(observed.astype(np.float64) - expected.astype(np.float64))
    boundary = diff > 1e-3
    report = {
        "backend": args.backend,
        "size": args.size,
        "cfa": list(args.cfa),
        "shape": list(observed.shape),
        "max_abs_diff": float(diff.max()),
        "mean_abs_diff": float(diff.mean()),
        "p99_abs_diff": float(np.quantile(diff, 0.99)),
        "boundary_pixels": int(np.count_nonzero(boundary)),
        "boundary_rate": float(np.count_nonzero(boundary) / diff.size),
        "timing": timing,
    }
    verdict = "PASS" if report["boundary_rate"] <= MAX_BOUNDARY_RATE else "FAIL"
    report["verdict"] = verdict

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(
        f"\n{verdict}: model vs graph mean_abs_diff={report['mean_abs_diff']:.3e}, "
        f"p99={report['p99_abs_diff']:.3e}, decision-boundary pixels="
        f"{report['boundary_pixels']} ({100.0 * report['boundary_rate']:.3f}%)"
    )
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
