"""Native full-frame smoke probe for the remap ``build_flow_maps`` graphs.

This probe is deliberately separate from the semantic block adapters.  A
successful run proves only that the selected target/device executed the
target-qualified remap graph for a small non-multiple shape; it does not
qualify block partitioning or GPU overlap.

Examples::

    $env:AOT_MODE = "1"
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_build_flow_maps_native --backend cpu
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_build_flow_maps_native --backend vulkan --device 0
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _reflect_idx(indices: np.ndarray, size: int) -> np.ndarray:
    values = np.abs(np.asarray(indices, dtype=np.int64))
    diff = values - (int(size) - 1)
    return np.clip(values - 2 * np.maximum(diff, 0), 0, int(size) - 1)


def _oracle(
    dx: np.ndarray, dy: np.ndarray, output_shape: tuple[int, int], sx: float, sy: float
):
    """Independent NumPy oracle for the remap graph's bilinear map formula."""

    dx = np.asarray(dx, dtype=np.float32)
    dy = np.asarray(dy, dtype=np.float32)
    h_flow, w_flow = dx.shape
    h_dst, w_dst = output_shape
    rows = np.arange(h_dst, dtype=np.float32)
    cols = np.arange(w_dst, dtype=np.float32)
    src_y = rows * np.float32(h_flow - 1) / np.float32(h_dst - 1)
    src_x = cols * np.float32(w_flow - 1) / np.float32(w_dst - 1)
    iy = np.floor(src_y).astype(np.int64)
    ix = np.floor(src_x).astype(np.int64)
    fy = src_y - iy.astype(np.float32)
    fx = src_x - ix.astype(np.float32)
    iy0, iy1 = _reflect_idx(iy, h_flow), _reflect_idx(iy + 1, h_flow)
    ix0, ix1 = _reflect_idx(ix, w_flow), _reflect_idx(ix + 1, w_flow)

    def sample(source: np.ndarray) -> np.ndarray:
        v00 = source[iy0[:, None], ix0[None, :]]
        v01 = source[iy0[:, None], ix1[None, :]]
        v10 = source[iy1[:, None], ix0[None, :]]
        v11 = source[iy1[:, None], ix1[None, :]]
        top = v00 * (np.float32(1.0) - fx[None, :]) + v01 * fx[None, :]
        bottom = v10 * (np.float32(1.0) - fx[None, :]) + v11 * fx[None, :]
        return top * (np.float32(1.0) - fy[:, None]) + bottom * fy[:, None]

    map_x = np.broadcast_to(cols[None, :], (h_dst, w_dst)) + sample(dx) * np.float32(sx)
    map_y = np.broadcast_to(rows[:, None], (h_dst, w_dst)) + sample(dy) * np.float32(sy)
    return np.ascontiguousarray(map_x, dtype=np.float32), np.ascontiguousarray(
        map_y, dtype=np.float32
    )


def _max_error(actual: Any, expected: Any) -> float:
    left = np.asarray(actual)
    right = np.asarray(expected)
    if left.shape != right.shape:
        return float("inf")
    return (
        float(np.max(np.abs(left.astype(np.float64) - right.astype(np.float64))))
        if left.size
        else 0.0
    )


def _release(value: Any) -> None:
    for item in value if isinstance(value, (tuple, list)) else (value,):
        try:
            item.destroy()
        except Exception:
            try:
                item.release()
            except Exception:
                pass


def run(backend: str, device: int = 0) -> dict[str, Any]:
    backend = str(backend).lower()
    if backend not in {"cpu", "vulkan", "opengl", "cuda"}:
        raise ValueError("backend must be cpu, vulkan, opengl, or cuda")
    os.environ["BACKEND"] = backend
    os.environ["AOT_ARCH"] = backend
    os.environ["AOT_DEVICE"] = str(int(device))
    if backend == "vulkan":
        os.environ.setdefault("TARGET_VENDOR", "nvidia")
    from taichi_vision.taichi_algorithm import aot_api as aot
    from taichi_vision.taichi_aot import engine

    rng = np.random.default_rng(20260810)
    flow = rng.normal(0.0, 0.25, size=(7, 11, 2)).astype(np.float32)
    full_h, full_w = 23, 29
    scale_x = np.float32(full_w / flow.shape[1])
    scale_y = np.float32(full_h / flow.shape[0])
    expected = _oracle(flow[..., 0], flow[..., 1], (full_h, full_w), scale_x, scale_y)
    cases = []
    for name, args, graphs in (
        (
            "build_flow_maps_from_2ch",
            (flow, full_h, full_w),
            ("remap", "build_flow_maps_from_2ch"),
        ),
        (
            "build_flow_maps",
            (flow[..., 0], flow[..., 1], full_h, full_w),
            ("remap", "build_flow_maps"),
        ),
    ):
        started = time.perf_counter()
        record: dict[str, Any] = {
            "case": name,
            "graphs": list(graphs),
            "input_shapes": (
                [list(flow.shape)]
                if name.endswith("2ch")
                else [list(flow[..., 0].shape), list(flow[..., 1].shape)]
            ),
            "output_shape": [full_h, full_w],
            "dtype": "float32",
            "partitioned": False,
            "native_runtime": False,
        }
        buffers = None
        try:
            buffers = aot.build_flow_maps(*args, scale_x=scale_x, scale_y=scale_y)
            actual = tuple(np.ascontiguousarray(item.to_numpy()) for item in buffers)
            errors = [_max_error(value, ref) for value, ref in zip(actual, expected)]
            record.update(
                {
                    "passed": bool(max(errors, default=0.0) == 0.0),
                    "max_abs_error": max(errors, default=0.0),
                    "finite": bool(all(np.isfinite(value).all() for value in actual)),
                    "native_runtime": True,
                }
            )
        except Exception as exc:
            record.update({"passed": False, "error": str(exc)[:512]})
        finally:
            _release(buffers)
        record["elapsed_seconds"] = float(time.perf_counter() - started)
        cases.append(record)
    return {
        "scope": "native_full_frame_build_flow_maps_smoke",
        "backend": str(getattr(engine, "arch", backend)),
        "device_id": int(getattr(engine, "device_id", device) or device),
        "device_name": str(
            getattr(engine, "gpu_name", "") or getattr(engine, "device_name", "")
        ),
        "cases": cases,
        "all_passed": bool(cases and all(item.get("passed") for item in cases)),
        "partitioned": False,
        "native_block_evidence": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend", choices=("cpu", "vulkan", "opengl", "cuda"), required=True
    )
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    payload = run(args.backend, args.device)
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
