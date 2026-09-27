"""Paired baseline-versus-candidate benchmark for the demosaic families.

Absolute timings on a shared machine drift far more than the effect being
measured -- repeating an untouched method gave swings of 1.6x or more -- so the
only defensible number is a *paired* comparison of two artifact generations
measured alternately in separate processes.  This tool does that: it points
``PIXEL_REFINE_AOT_TCM_ROOT`` at a baseline root and a candidate root in turn,
aggregates medians over several rounds, and also compares the two generations'
outputs on identical input so "accuracy equal or better" is checked rather than
assumed.

Prepare the roots with ``make_ab_roots.py`` (baseline from ``git HEAD``).

Example:
    python bench_demosaic_ab.py --baseline-root <dir> --current-root <dir> \\
        --methods hamilton arm dcb mlri-admm bilinear --sizes 512 1024 --rounds 3
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Canonical names accepted by ``aot_api.demosaic``; MLRI is the one whose
# canonical spelling differs from its standalone entry point.
METHODS = ("hamilton", "arm", "dcb", "mlri-admm", "bilinear")


def deterministic_bayer(size: int) -> np.ndarray:
    rng = np.random.default_rng(20260924 + size)
    return rng.random((size, size), dtype=np.float32)


def worker(args) -> int:
    """Measure every requested method under the ambient TCM root."""

    os.environ["PIXEL_REFINE_AOT_ARCH"] = args.backend
    os.environ["AOT_ARCH"] = args.backend
    import taichi_vision.taichi_aot as api

    report = {"tcm_root": os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "<ambient>"), "results": {}}
    outputs = {}
    cmatrix = np.eye(3, dtype=np.float32)

    for method in args.methods:
        entry = {}
        for size in args.sizes:
            bayer = deterministic_bayer(size)
            scalars = (1.4, 1.0, 1.6, 1.02, cmatrix, 0.0, 1.0, 0, 1, 3, 2)

            buffer = api.upload(bayer)
            timings = []
            output = None
            try:
                warm = api.demosaic(buffer, *scalars, method=method, return_gpu=True)
                if hasattr(warm, "release"):
                    warm.release()
                for _ in range(max(1, args.runs)):
                    started = time.perf_counter()
                    candidate = api.demosaic(buffer, *scalars, method=method, return_gpu=True)
                    elapsed = (time.perf_counter() - started) * 1000.0
                    array = candidate.to_numpy() if hasattr(candidate, "to_numpy") else np.asarray(candidate)
                    if hasattr(candidate, "release"):
                        candidate.release()
                    timings.append(elapsed)
                    output = array
            finally:
                if hasattr(buffer, "release"):
                    buffer.release()

            entry[str(size)] = {
                "median_ms": float(statistics.median(timings)),
                "runs": timings,
                "output_shape": list(np.shape(output)),
            }
            outputs[f"{method}_{size}"] = np.asarray(output, dtype=np.float32)
        report["results"][method] = entry

    if args.worker_report:
        Path(args.worker_report).write_text(json.dumps(report), encoding="utf-8")
    if args.worker_outputs:
        Path(args.worker_outputs).parent.mkdir(parents=True, exist_ok=True)
        np.savez(args.worker_outputs, **outputs)
    print(json.dumps(report))
    return 0


def run_worker(args, root: Path, tag: str) -> tuple[dict, dict]:
    env = dict(os.environ)
    env["PIXEL_REFINE_AOT_TCM_ROOT"] = str(root)
    report = Path(args.workdir) / f"ab_{tag}.json"
    outputs = Path(args.workdir) / f"ab_{tag}.npz"
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--backend",
        args.backend,
        "--methods",
        *args.methods,
        "--sizes",
        *[str(s) for s in args.sizes],
        "--runs",
        str(args.runs),
        "--worker-report",
        str(report),
        "--worker-outputs",
        str(outputs),
    ]
    result = subprocess.run(command, capture_output=True, text=True, env=env, cwd=str(ROOT))
    if result.returncode != 0:
        print(result.stdout[-3000:])
        print(result.stderr[-3000:])
        raise SystemExit(f"worker failed for {tag}")
    return json.loads(report.read_text(encoding="utf-8")), dict(np.load(outputs))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--current-root", type=Path)
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--methods", nargs="+", default=list(METHODS))
    parser.add_argument("--sizes", nargs="+", type=int, default=[512, 1024])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--workdir", type=Path, default=Path("."))
    parser.add_argument("--worker-report", type=Path)
    parser.add_argument("--worker-outputs", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    args.workdir.mkdir(parents=True, exist_ok=True)

    if args.worker:
        return worker(args)

    if args.baseline_root is None or args.current_root is None:
        parser.error("--baseline-root and --current-root are required for a comparison")

    samples = {"baseline": {}, "current": {}}
    outputs = {"baseline": None, "current": None}
    for round_index in range(args.rounds):
        for tag, root in (("baseline", args.baseline_root), ("current", args.current_root)):
            payload, arrays = run_worker(args, root, f"{tag}_{round_index}")
            outputs[tag] = arrays
            for method, sizes in payload["results"].items():
                for size, entry in sizes.items():
                    samples[tag].setdefault(method, {}).setdefault(size, []).append(entry["median_ms"])
            print(f"round {round_index} {tag:9s} done")

    def median(tag, method, size):
        values = samples[tag].get(method, {}).get(str(size))
        return statistics.median(values) if values else float("nan")

    print("\npaired dispatch medians (ms) over rounds")
    header = f"{'method':<12}{'size':>6}{'baseline':>11}{'current':>11}{'speedup':>10}{'max|diff|':>12}"
    print(header)
    print("-" * len(header))
    verdicts = {}
    for method in args.methods:
        for size in args.sizes:
            base = median("baseline", method, size)
            cand = median("current", method, size)
            speedup = base / cand if cand else float("nan")
            key = f"{method}_{size}"
            diff = float("nan")
            if outputs["baseline"] is not None and key in outputs["baseline"]:
                a = outputs["baseline"][key].astype(np.float64)
                b = outputs["current"][key].astype(np.float64)
                if a.shape == b.shape:
                    diff = float(np.max(np.abs(a - b)))
            verdicts[key] = {"baseline_ms": base, "current_ms": cand, "speedup": speedup, "max_abs_diff": diff}
            print(f"{method:<12}{size:>6}{base:>11.3f}{cand:>11.3f}{speedup:>9.2f}x{diff:>12.3e}")

    if args.report:
        args.report.write_text(json.dumps(verdicts, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
