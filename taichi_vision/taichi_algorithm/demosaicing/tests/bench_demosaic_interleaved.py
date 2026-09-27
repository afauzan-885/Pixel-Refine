"""Interleaved in-process A/B benchmark for the demosaic families.

Absolute timings on a shared host drift by tens of percent between processes, and
even a byte-identical control method differed by 0.82x when each variant ran in
its own process.  This tool removes that class of error by loading *both* artifact
generations into one process and alternating between them inside each round, so
machine drift lands on both variants alike.

The loader root and its caches are switched directly (``_module_loader.tcm_dir``
plus the module and target-resolution caches) and the engine's own path-keyed
module cache is dropped for the previous root, so each variant really is loaded
from its own artifact.

Always pass an unchanged method as ``--control``: its ratio is the noise floor,
and no speed claim is meaningful unless the effect is well clear of it.

Example:
    python bench_demosaic_interleaved.py --root-a <baseline> --root-b <candidate> \\
        --methods hamilton arm dcb mlri-admm bilinear --control bilinear \\
        --sizes 1024 --rounds 5
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def deterministic_bayer(size: int) -> np.ndarray:
    rng = np.random.default_rng(20260924 + size)
    return rng.random((size, size), dtype=np.float32)


def switch_root(root: Path) -> None:
    """Point the loader at another artifact root and drop every cache.

    The root is owned by ``aot_api``, not by the ``taichi_aot`` facade, and the
    engine keeps its own path-keyed module cache, so all three are reset.
    """

    from taichi_vision.taichi_algorithm import aot_api

    loader = aot_api._module_loader
    loader.tcm_dir = str(root)
    loader._target_resolution_cache.clear()
    loader.cache.clear()
    modules = getattr(loader.engine, "modules", None)
    if isinstance(modules, dict):
        modules.clear()


def measure(api, method: str, size: int, runs: int, bayer: np.ndarray):
    """Return wall-clock and process-CPU medians plus the output.

    Wall clock on a shared host carries tens of percent of drift; process CPU
    time counts the work actually done and is far less sensitive to what else is
    running, so both are reported and the CPU ratio is the one to trust.
    """

    cmatrix = np.eye(3, dtype=np.float32)
    scalars = (1.4, 1.0, 1.6, 1.02, cmatrix, 0.0, 1.0, 0, 1, 3, 2)

    buffer = api.upload(bayer)
    wall = []
    cpu = []
    output = None
    try:
        warm = api.demosaic(buffer, *scalars, method=method, return_gpu=True)
        if hasattr(warm, "release"):
            warm.release()
        for _ in range(max(1, runs)):
            wall_started = time.perf_counter()
            cpu_started = time.process_time()
            candidate = api.demosaic(buffer, *scalars, method=method, return_gpu=True)
            elapsed = (time.perf_counter() - wall_started) * 1000.0
            cpu_elapsed = (time.process_time() - cpu_started) * 1000.0
            array = candidate.to_numpy() if hasattr(candidate, "to_numpy") else np.asarray(candidate)
            if hasattr(candidate, "release"):
                candidate.release()
            wall.append(elapsed)
            cpu.append(cpu_elapsed)
            output = array
    finally:
        if hasattr(buffer, "release"):
            buffer.release()
    return (
        float(statistics.median(wall)),
        float(statistics.median(cpu)),
        np.asarray(output, dtype=np.float32),
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root-a", type=Path, required=True)
    parser.add_argument("--root-b", type=Path, required=True)
    parser.add_argument("--label-a", default="baseline")
    parser.add_argument("--label-b", default="candidate")
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--methods", nargs="+", default=["hamilton", "arm", "dcb", "mlri-admm", "bilinear"])
    parser.add_argument("--control", default="bilinear")
    parser.add_argument("--sizes", nargs="+", type=int, default=[1024])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    os.environ["PIXEL_REFINE_AOT_ARCH"] = args.backend
    os.environ["AOT_ARCH"] = args.backend
    import taichi_vision.taichi_aot as api

    samples: dict[str, dict[str, dict[str, list[float]]]] = {"a": {}, "b": {}}
    cpu_samples: dict[str, dict[str, dict[str, list[float]]]] = {"a": {}, "b": {}}
    outputs: dict[str, dict[str, np.ndarray]] = {"a": {}, "b": {}}
    bayer_by_size = {size: deterministic_bayer(size) for size in args.sizes}

    for round_index in range(args.rounds):
        # Alternate which variant goes first so a linear drift within the round
        # cancels instead of favouring one side.
        order = (("a", args.root_a), ("b", args.root_b))
        if round_index % 2:
            order = tuple(reversed(order))
        for tag, root in order:
            switch_root(root)
            for method in args.methods:
                for size in args.sizes:
                    wall, cpu, array = measure(api, method, size, args.runs, bayer_by_size[size])
                    samples[tag].setdefault(method, {}).setdefault(str(size), []).append(wall)
                    cpu_samples[tag].setdefault(method, {}).setdefault(str(size), []).append(cpu)
                    outputs[tag][f"{method}_{size}"] = array
        print(f"round {round_index} done")

    def median(tag, method, size, table=cpu_samples):
        values = table[tag].get(method, {}).get(str(size))
        return statistics.median(values) if values else float("nan")

    def spread(tag, method, size, table=cpu_samples):
        values = table[tag].get(method, {}).get(str(size)) or [float("nan")]
        return max(values) / min(values) if min(values) else float("nan")

    header = (
        f"{'method':<12}{'size':>6}{'A cpu ms':>10}{'B cpu ms':>10}{'raw B/A':>9}"
        f"{'paired':>8}{'wall B/A':>10}{'max|diff|':>12}{'sprA':>7}{'sprB':>7}"
    )
    print("\n" + header)
    print("-" * len(header))

    control_ratio = {}
    for size in args.sizes:
        control_ratio[size] = median("a", args.control, size) / median("b", args.control, size)

    def paired_ratio(method, size):
        """Per-round ratio of (A/B) divided by the control's (A/B) in the same round.

        Comparing medians across rounds lets drift that happens *within* a round
        leak into the answer; pairing inside each round cancels it.
        """

        control_a = cpu_samples["a"].get(args.control, {}).get(str(size)) or []
        control_b = cpu_samples["b"].get(args.control, {}).get(str(size)) or []
        method_a = cpu_samples["a"].get(method, {}).get(str(size)) or []
        method_b = cpu_samples["b"].get(method, {}).get(str(size)) or []
        ratios = []
        for index in range(min(len(control_a), len(control_b), len(method_a), len(method_b))):
            control = control_a[index] / control_b[index] if control_b[index] else float("nan")
            raw = method_a[index] / method_b[index] if method_b[index] else float("nan")
            if control and control == control:
                ratios.append(raw / control)
        return statistics.median(ratios) if ratios else float("nan")

    report = {}
    for method in args.methods:
        for size in args.sizes:
            a = median("a", method, size)
            b = median("b", method, size)
            ratio = a / b if b else float("nan")
            normalised = paired_ratio(method, size)
            wall_a = median("a", method, size, samples)
            wall_b = median("b", method, size, samples)
            wall_ratio = wall_a / wall_b if wall_b else float("nan")
            key = f"{method}_{size}"
            diff = float("nan")
            if key in outputs["a"] and key in outputs["b"]:
                first, second = outputs["a"][key].astype(np.float64), outputs["b"][key].astype(np.float64)
                if first.shape == second.shape:
                    diff = float(np.max(np.abs(first - second)))
            report[key] = {
                "a_cpu_ms": a,
                "b_cpu_ms": b,
                "raw_ratio_a_over_b": ratio,
                "paired_control_normalised": normalised,
                "wall_ratio_a_over_b": wall_ratio,
                "max_abs_diff": diff,
            }
            print(
                f"{method:<12}{size:>6}{a:>10.2f}{b:>10.2f}{ratio:>8.2f}x{normalised:>7.2f}x"
                f"{wall_ratio:>9.2f}x{diff:>12.3e}"
                f"{spread('a', method, size):>6.2f}x{spread('b', method, size):>6.2f}x"
            )

    print(
        f"\ncontrol '{args.control}' is byte-identical between roots; its CPU ratio "
        f"{ {s: round(v, 3) for s, v in control_ratio.items()} } bounds what this host can resolve."
    )
    if args.report:
        args.report.write_text(
            json.dumps({"control_ratio": control_ratio, "cells": report}, indent=2), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
