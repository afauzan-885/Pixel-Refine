"""Reproducible pre-demosaic RAW/DNG optical-flow contract harness.

The harness has two deliberately separate evidence levels:

* ``--native-smoke`` dispatches the target-qualified
  ``compression_raw_normalize_headroom_i32`` graph on a small synthetic
  strip-like DNG object and compares it with an independent sensor-code
  oracle.  A missing artifact is an error; no CPU or full-frame substitution
  is hidden by this script.
* the default 12/24/50/100 MP cases exercise the semantic DNG guide path and the
  explicit ``RawFlowTileContract`` stitching contract.  The deterministic
  test runner is intentionally local and has no pyramid/reduction state, so
  full-guide and tiled outputs can be compared exactly without claiming that
  Farneback/Lucas--Kanade are tile-safe or that GPU tiles overlap.
  ``--native-stress`` repeats those cases with native RAW normalization on
  the selected target while keeping the same deliberately local flow runner.

The synthetic source implements only the maintained strip/sample-region
contract.  It is not a Hasselblad decoder or a claim about arbitrary tiled,
malformed, or vendor-specific DNG layouts.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from taichi_vision.taichi_algorithm.compression.raw_pipeline import (
    RawFlowTileContract,
    raw_alignment_guide_dng,
    raw_optical_flow_dng,
)


PRESETS = {
    "12": (3000, 4000),
    "24": (4000, 6000),
    "50": (5000, 10000),
    # 100 MP sensor domain.  This deliberately uses a square synthetic
    # frame so the guide remains 50 MP while preserving the same packed
    # strip/sample-region contract as the smaller cases.
    "100": (10000, 10000),
}


class SyntheticStripDNG:
    """Lazy, strip-compatible synthetic DNG source for large stress cases."""

    def __init__(
        self,
        shape: tuple[int, int],
        *,
        bits_per_sample: int = 14,
        exposure_offset: int = 0,
    ) -> None:
        self.height, self.width = (int(shape[0]), int(shape[1]))
        self.bits_per_sample = int(bits_per_sample)
        self.compression = 1  # uncompressed strip profile
        self.exposure_offset = int(exposure_offset)
        white = (1 << self.bits_per_sample) - 1
        self.tags = {
            33422: (1, 0, 0, 1),
            50714: (0.0, 0.0, 0.0, 0.0),
            50717: (float(white),) * 4,
            "phase_origin": (0, 0),
            273: (0,),
            279: (self.height * self.width * (1 if self.bits_per_sample <= 8 else 2),),
        }

    def sample_region(self, y0: int, y1: int, x0: int, x1: int) -> np.ndarray:
        y0, y1, x0, x1 = (int(y0), int(y1), int(x0), int(x1))
        if not (0 <= y0 <= y1 <= self.height and 0 <= x0 <= x1 <= self.width):
            raise ValueError("synthetic DNG region is outside the frame")
        rows = np.arange(y0, y1, dtype=np.uint32)[:, None]
        cols = np.arange(x0, x1, dtype=np.uint32)[None, :]
        mask = np.uint32((1 << self.bits_per_sample) - 1)
        values = (
            rows * np.uint32(37)
            + cols * np.uint32(19)
            + np.uint32(self.exposure_offset * 101)
        ) & mask
        return values.astype(np.uint8 if self.bits_per_sample <= 8 else np.uint16)


def _rss_bytes() -> int:
    try:
        import psutil

        return int(psutil.Process().memory_info().rss)
    except Exception:
        return 0


def _runtime_info() -> dict[str, object]:
    """Return actual runtime identity only after the AOT engine is initialized."""
    from taichi_vision import taichi_aot

    runtime = taichi_aot.engine
    return {
        "backend_requested": os.environ.get(
            "BACKEND",
            os.environ.get("AOT_ARCH", "auto"),
        ),
        "backend_actual": str(getattr(runtime, "arch", "unknown")).lower(),
        "device_id": int(getattr(runtime, "device_id", 0)),
        "device_name": str(getattr(runtime, "gpu_name", "") or ""),
    }


def _sensor_values(shape: tuple[int, int], bits: int, offset: int) -> np.ndarray:
    height, width = (int(shape[0]), int(shape[1]))
    rows = np.arange(height, dtype=np.uint32)[:, None]
    cols = np.arange(width, dtype=np.uint32)[None, :]
    mask = np.uint32((1 << int(bits)) - 1)
    values = (
        rows * np.uint32(37) + cols * np.uint32(19) + np.uint32(offset * 101)
    ) & mask
    return values.astype(np.uint8 if bits <= 8 else np.uint16)


def _independent_green_guide(
    source: np.ndarray,
    *,
    bits: int,
    black: float = 0.0,
    white: float | None = None,
) -> np.ndarray:
    """Independent CFA guide oracle for the small native smoke."""
    white_value = float((1 << int(bits)) - 1 if white is None else white)
    normalized = np.maximum(source.astype(np.float32) - np.float32(black), 0.0)
    normalized /= np.float32(max(white_value - float(black), 1e-12))
    green_a = normalized[0::2, 0::2]
    green_b = normalized[1::2, 1::2]
    height = min(green_a.shape[0], green_b.shape[0])
    width = min(green_a.shape[1], green_b.shape[1])
    return np.ascontiguousarray(
        (green_a[:height, :width] + green_b[:height, :width]) * np.float32(0.5),
        dtype=np.float32,
    )


def _local_flow_runner(
    previous: np.ndarray, current: np.ndarray, **_kwargs
) -> np.ndarray:
    """Known-value local vector field used only for contract parity."""
    residual = np.ascontiguousarray(current - previous, dtype=np.float32)
    return np.stack((residual, residual), axis=-1)


def run_native_smoke(block_size: int) -> dict[str, object]:
    shape = (64, 96)
    bits = 14
    reference = SyntheticStripDNG(shape, bits_per_sample=bits, exposure_offset=0)
    current = SyntheticStripDNG(shape, bits_per_sample=bits, exposure_offset=3)
    source = _sensor_values(shape, bits, 0)
    started = time.perf_counter()
    rss_before = _rss_bytes()
    # native=True is intentionally not wrapped in a fallback.  If the active
    # target lacks compression_raw, the case is reported as failed.
    native_guide = raw_alignment_guide_dng(
        reference, block_size=block_size, apply_white_balance=False, native=True
    )
    rss_after = _rss_bytes()
    elapsed = time.perf_counter() - started
    oracle = _independent_green_guide(source, bits=bits)
    max_error = float(np.max(np.abs(native_guide - oracle)))
    runtime = _runtime_info()
    return {
        **runtime,
        "case": "native_guide_smoke",
        "native": True,
        "native_graph": "compression_raw_normalize_headroom_i32",
        "flow_runner": "not_run",
        "shape_sensor": list(shape),
        "shape_guide": list(native_guide.shape),
        "sensor_dtype": str(source.dtype),
        "guide_dtype": str(native_guide.dtype),
        "bits_per_sample": bits,
        "block_size_sensor": int(block_size),
        "max_abs_error_vs_independent_oracle": max_error,
        "elapsed_seconds": elapsed,
        "rss_delta_bytes": rss_after - rss_before,
        "memory_measurement": "host_rss_only",
        "passed": bool(
            native_guide.dtype == np.dtype(np.float32)
            and np.isfinite(native_guide).all()
            and max_error <= 2.0e-5
        ),
    }


def run_semantic_case(
    label: str,
    shape: tuple[int, int],
    block_size: int,
    *,
    native: bool = False,
) -> dict[str, object]:
    bits = 14
    reference = SyntheticStripDNG(shape, bits_per_sample=bits, exposure_offset=0)
    current = SyntheticStripDNG(shape, bits_per_sample=bits, exposure_offset=3)
    contract = RawFlowTileContract(halo=1)
    full_calls: list[tuple[int, ...]] = []
    tiled_calls: list[tuple[int, ...]] = []

    def full_runner(previous, current, **kwargs):
        full_calls.append(tuple(previous.shape))
        return _local_flow_runner(previous, current, **kwargs)

    def tiled_runner(previous, current, **kwargs):
        tiled_calls.append(tuple(previous.shape))
        return _local_flow_runner(previous, current, **kwargs)

    rss_before = _rss_bytes()
    started = time.perf_counter()
    full_flow = raw_optical_flow_dng(
        reference,
        current,
        block_size=block_size,
        native=native,
        flow_runner=full_runner,
        flow_mode="full_frame",
    )
    full_elapsed = time.perf_counter() - started
    started = time.perf_counter()
    tiled_flow = raw_optical_flow_dng(
        reference,
        current,
        block_size=block_size,
        native=native,
        flow_runner=tiled_runner,
        flow_contract=contract,
        flow_mode="auto",
    )
    tiled_elapsed = time.perf_counter() - started
    rss_after = _rss_bytes()
    max_error = float(np.max(np.abs(tiled_flow - full_flow)))
    expected = np.ascontiguousarray(full_flow, dtype=np.float32)
    runtime = (
        _runtime_info()
        if native
        else {
            "backend_requested": "semantic_reference",
            "backend_actual": "semantic_reference",
            "device_id": None,
            "device_name": "host",
        }
    )
    return {
        **runtime,
        "case": f"{'native' if native else 'semantic'}_{label}mp",
        "native": bool(native),
        "native_graph": "compression_raw_normalize_headroom_i32" if native else None,
        "flow_runner": "deterministic_local_vector_field",
        "flow_mode": "auto_with_explicit_contract",
        "shape_sensor": list(shape),
        "shape_guide": list(tiled_flow.shape[:2]),
        "sensor_dtype": "uint16",
        "guide_dtype": "float32",
        "flow_dtype": str(tiled_flow.dtype),
        "bits_per_sample": bits,
        "block_size_sensor": int(block_size),
        "halo_guide_pixels": int(contract.halo),
        "full_frame_calls": len(full_calls),
        "tiled_calls": len(tiled_calls),
        "first_tiled_input_shape": list(tiled_calls[0]) if tiled_calls else None,
        "full_frame_elapsed_seconds": full_elapsed,
        "tiled_elapsed_seconds": tiled_elapsed,
        "elapsed_seconds": tiled_elapsed,
        "rss_delta_bytes": rss_after - rss_before,
        "memory_measurement": "host_rss_only",
        "max_abs_error_vs_full_frame": max_error,
        "max_abs_error_vs_known_output": float(np.max(np.abs(tiled_flow - expected))),
        "finite": bool(np.isfinite(tiled_flow).all()),
        "passed": bool(
            tiled_flow.dtype == np.dtype(np.float32)
            and np.isfinite(tiled_flow).all()
            and max_error == 0.0
            and len(full_calls) == 1
            and len(tiled_calls) > 1
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sizes",
        default="12,24,50,100",
        help="semantic stress presets (12,24,50,100 MP)",
    )
    parser.add_argument("--block-size", type=int, default=2048)
    parser.add_argument("--native-smoke", action="store_true")
    parser.add_argument(
        "--native-stress",
        action="store_true",
        help="run 12/24/50 MP guide/contract cases through native RAW normalization",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    if args.block_size <= 0:
        raise SystemExit("--block-size must be positive")

    results: list[dict[str, object]] = []
    if args.native_smoke:
        try:
            results.append(run_native_smoke(args.block_size))
        except Exception as exc:
            # Native errors are surfaced as failed evidence; there is no
            # semantic fallback in this harness.
            results.append(
                {
                    "case": "native_guide_smoke",
                    "native": True,
                    "backend_requested": os.environ.get(
                        "BACKEND",
                        os.environ.get("AOT_ARCH", "auto"),
                    ),
                    "error": f"{type(exc).__name__}: {exc}",
                    "passed": False,
                }
            )

    for label in (item.strip() for item in str(args.sizes).split(",")):
        if not label:
            continue
        if label not in PRESETS:
            raise SystemExit(f"unknown size preset {label!r}; choose 12,24,50,100")
        if args.native_stress:
            try:
                results.append(
                    run_semantic_case(
                        label,
                        PRESETS[label],
                        args.block_size,
                        native=True,
                    )
                )
            except Exception as exc:
                results.append(
                    {
                        "case": f"native_{label}mp",
                        "native": True,
                        "backend_requested": os.environ.get(
                            "BACKEND",
                            os.environ.get("AOT_ARCH", "auto"),
                        ),
                        "shape_sensor": list(PRESETS[label]),
                        "error": f"{type(exc).__name__}: {exc}",
                        "passed": False,
                    }
                )
        else:
            results.append(run_semantic_case(label, PRESETS[label], args.block_size))
        gc.collect()

    payload = {
        "requested_backend": os.environ.get(
            "BACKEND",
            os.environ.get("AOT_ARCH", "auto"),
        ),
        "block_size_sensor": int(args.block_size),
        "results": results,
        "all_passed": bool(results)
        and all(bool(item.get("passed")) for item in results),
        "notes": [
            "semantic stress uses a synthetic strip/sample_region contract",
            "100 MP uses a 10000x10000 sensor and 50 MP guide; peak memory is host-RSS only",
            "host RSS only; no GPU VRAM or overlap claim",
            "default raw_optical_flow_dng remains full-guide unless a contract is supplied",
        ],
    }
    text = json.dumps(payload, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
