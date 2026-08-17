"""Small, reproducible benchmark/pressure harness for family pipelines.

This runner deliberately does not assume that a pipeline is safe to execute at
50 MP.  It records the estimated allocation first, skips a case that exceeds
the caller's explicit budget, and reports a skipped case separately from a
successful run.  The harness is useful for comparing existing algorithms and
for proving where a pipeline still performs a host readback.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import argparse
import importlib
import json
import os
import time
from typing import Any, Callable, Iterable, Sequence

import numpy as np


@dataclass
class BenchmarkCase:
    height: int
    width: int
    channels: int = 1
    dtype: str = "float32"

    @property
    def shape(self) -> tuple[int, ...]:
        return (self.height, self.width) if self.channels == 1 else (self.height, self.width, self.channels)

    @property
    def bytes_per_array(self) -> int:
        return int(np.prod(self.shape, dtype=np.int64)) * int(np.dtype(self.dtype).itemsize)

    @property
    def megapixels(self) -> float:
        return float(self.height * self.width) / 1_000_000.0


@dataclass
class BenchmarkResult:
    case: BenchmarkCase
    status: str
    elapsed_seconds: float | None = None
    output_shape: tuple[int, ...] | None = None
    output_dtype: str | None = None
    output_finite_fraction: float | None = None
    input_bytes: int = 0
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["case"] = asdict(self.case)
        return value


def default_cases() -> list[BenchmarkCase]:
    """Return smoke, 4K, and approximately 50 MP pressure cases."""

    return [
        BenchmarkCase(512, 512),
        BenchmarkCase(2048, 2048),
        BenchmarkCase(4096, 4096),
        BenchmarkCase(7072, 7072),
    ]


def synthetic_input(case: BenchmarkCase, *, seed: int = 1234) -> np.ndarray:
    """Create a deterministic image without using a full random float buffer."""

    rng = np.random.default_rng(int(seed))
    if case.channels == 1:
        return rng.random((case.height, case.width), dtype=np.float32)
    return rng.random((case.height, case.width, case.channels), dtype=np.float32)


def _resident_bytes() -> int | None:
    """Best-effort process RSS; native device memory is reported by the backend."""

    try:
        import psutil  # type: ignore

        return int(psutil.Process(os.getpid()).memory_info().rss)
    except Exception:
        return None


def run_benchmark(
    function: Callable[[np.ndarray], Any],
    *,
    cases: Sequence[BenchmarkCase] | None = None,
    repeats: int = 1,
    max_input_bytes: int | None = None,
    seed: int = 1234,
) -> list[BenchmarkResult]:
    """Run a one-image pipeline and record deterministic pressure results.

    Multi-frame algorithms can wrap their own stack generator and call this
    function with a callable that accepts the first synthetic image; the
    harness remains intentionally agnostic about algorithm-specific arguments.
    """

    if repeats < 1:
        raise ValueError("repeats must be at least one")
    selected = list(cases) if cases is not None else default_cases()
    results: list[BenchmarkResult] = []
    for index, case in enumerate(selected):
        input_bytes = case.bytes_per_array
        base = BenchmarkResult(case=case, status="pending", input_bytes=input_bytes)
        if max_input_bytes is not None and input_bytes > int(max_input_bytes):
            base.status = "skipped_budget"
            base.error = f"input requires {input_bytes} bytes; budget is {int(max_input_bytes)}"
            results.append(base)
            continue
        try:
            image = synthetic_input(case, seed=seed + index)
            timings = []
            output = None
            rss_before = _resident_bytes()
            for _ in range(repeats):
                started = time.perf_counter()
                output = function(image)
                timings.append(time.perf_counter() - started)
            elapsed = float(np.median(np.asarray(timings, dtype=np.float64)))
            output_array = np.asarray(output)
            base.status = "ok"
            base.elapsed_seconds = elapsed
            base.output_shape = tuple(int(value) for value in output_array.shape)
            base.output_dtype = str(output_array.dtype)
            base.output_finite_fraction = (
                float(np.isfinite(output_array).mean()) if output_array.size else 1.0
            )
            rss_after = _resident_bytes()
            base.metadata = {
                "rss_before": rss_before,
                "rss_after": rss_after,
                "repeats": int(repeats),
                "megapixels": case.megapixels,
            }
        except MemoryError as exc:
            base.status = "oom"
            base.error = str(exc) or "MemoryError"
        except Exception as exc:  # benchmark reports errors; it does not hide them
            base.status = "error"
            base.error = f"{type(exc).__name__}: {exc}"
        results.append(base)
    return results


def _load_callable(spec: str) -> Callable[[np.ndarray], Any]:
    if ":" not in spec:
        raise ValueError("callable must use module:function syntax")
    module_name, function_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    if not callable(function):
        raise TypeError(f"{spec} is not callable")
    return function


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("callable", help="module:function accepting one NumPy image")
    parser.add_argument("--max-input-bytes", type=int, default=None)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    results = run_benchmark(
        _load_callable(args.callable),
        repeats=args.repeats,
        max_input_bytes=args.max_input_bytes,
    )
    payload = [result.as_dict() for result in results]
    if args.json:
        print(json.dumps(payload, indent=2, default=str))
    else:
        for result in results:
            print(
                f"{result.case.height}x{result.case.width} ({result.case.megapixels:.1f} MP): "
                f"{result.status} {result.elapsed_seconds if result.elapsed_seconds is not None else ''}"
            )
            if result.error:
                print(f"  {result.error}")
    return 0 if all(result.status in {"ok", "skipped_budget"} for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BenchmarkCase",
    "BenchmarkResult",
    "default_cases",
    "synthetic_input",
    "run_benchmark",
]
