"""Crash-isolated dtype probe for the public AOT image primitives.

The probe deliberately handles one dtype per process.  A failed graph
dispatch can poison a Taichi runtime, and running all dtypes in one process
would make later results misleading.  The report distinguishes buffer
round-trip support from actual graph support.

Example::

    $env:AOT_ARCH = "cpu"
    python taichi_vision/taichi_algorithm/aot_py/dtype_probe.py --dtype uint16
"""

from __future__ import annotations

import argparse
import json
import os
import traceback

import numpy as np


DTYPES = {
    "uint8": np.uint8,
    "uint16": np.uint16,
    "int16": np.int16,
    "int32": np.int32,
    "float16": np.float16,
    "float32": np.float32,
}


def _sample(dtype):
    raw = np.arange(16 * 16 * 3, dtype=np.int64).reshape(16, 16, 3)
    if np.issubdtype(dtype, np.signedinteger):
        raw = raw - 48
    if np.issubdtype(dtype, np.floating):
        raw = raw.astype(np.float64) / 255.0
    return raw.astype(dtype)


def _attempt(result, key, fn):
    try:
        value = fn()
        result[key] = {"status": "pass", **value}
    except Exception as exc:  # noqa: BLE001 - probe must report backend errors
        message = str(exc).strip().splitlines()
        result[key] = {
            "status": "fail",
            "error_type": type(exc).__name__,
            "error": (message[0] if message else repr(exc))[:240],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dtype", choices=sorted(DTYPES), required=True)
    parser.add_argument("--backend", default=os.environ.get("AOT_ARCH", "cpu"))
    parser.add_argument("--device", default=os.environ.get("AOT_DEVICE", "0"))
    args = parser.parse_args()
    os.environ["AOT_ARCH"] = args.backend
    os.environ["AOT_DEVICE"] = str(args.device)
    os.environ.setdefault("AOT_ALLOW_LEGACY_ARTIFACTS", "0")

    dtype = DTYPES[args.dtype]
    source = _sample(dtype)
    result = {
        "backend": args.backend,
        "device": str(args.device),
        "dtype": np.dtype(dtype).name,
        "buffer": {},
        "graphs": {},
        "channels": {},
    }

    try:
        from taichi_vision import taichi_aot as ta
        from taichi_vision.taichi_aot.engine import engine
    except Exception as exc:  # pragma: no cover - environment failure
        message = str(exc).strip().splitlines()
        result["runtime"] = {
            "status": "fail",
            "error_type": type(exc).__name__,
            "error": (message[0] if message else repr(exc))[:240],
        }
        print(json.dumps(result, indent=2))
        return 2

    try:
        buffer = engine.upload(source, is_vector=True, vector_dim=3)
        roundtrip = buffer.to_numpy()
        result["buffer"] = {
            "status": "pass",
            "roundtrip_dtype": np.dtype(roundtrip.dtype).name,
            "roundtrip_equal": bool(np.array_equal(source, roundtrip)),
        }
        # Exercise the bridge's compact signed-16 conversion independently of
        # the graph dtype under test.  OpenGL is expected to use its
        # synchronized host path; CPU/Vulkan/CUDA use the native bridge path.
        cast_source = np.array(
            [-40000.0, -12.75, 0.0, 1.9, 32767.0, np.nan], dtype=np.float32
        )
        cast_src = engine.upload(cast_source)
        cast_i16 = cast_src.cast(np.int16, host_accessible=True)
        cast_back = cast_i16.cast(np.float32, host_accessible=True).to_numpy()
        expected_i16 = np.array([-32768, -12, 0, 1, 32767, -32768], dtype=np.int16)
        cast_equal = bool(np.array_equal(cast_i16.to_numpy(), expected_i16))
        cast_roundtrip_equal = bool(
            np.array_equal(cast_back, expected_i16.astype(np.float32))
        )
        result["buffer"]["i16_cast"] = {
            "status": "pass" if cast_equal and cast_roundtrip_equal else "fail",
            "equal": cast_equal,
            "roundtrip_equal": cast_roundtrip_equal,
        }
        cast_src.release()
        cast_i16.release()
        if not cast_equal or not cast_roundtrip_equal:
            raise RuntimeError("native i16 cast parity failed")
        buffer.destroy()
    except Exception as exc:  # noqa: BLE001
        message = str(exc).strip().splitlines()
        result["buffer"] = {
            "status": "fail",
            "error_type": type(exc).__name__,
            "error": (message[0] if message else repr(exc))[:240],
        }

    def copy_graph():
        output = np.asarray(ta.copy(source))
        return {
            "output_dtype": np.dtype(output.dtype).name,
            "equal": bool(np.array_equal(source, output)),
        }

    def gray_graph():
        output = np.asarray(ta.rgb2gray(source))
        return {
            "output_dtype": np.dtype(output.dtype).name,
            "shape": list(output.shape),
        }

    def channel_graphs():
        extracted = np.asarray(ta.extract_channel(source, 1))
        channels = ta.split_3ch(source)
        merged = np.asarray(ta.merge_3ch(*channels))
        inserted = np.zeros_like(source)
        ta.insert_channel(source[:, :, 1], inserted, 1)
        return {
            "extract_equal": bool(np.array_equal(extracted, source[:, :, 1])),
            "split_dtypes": [np.dtype(channel.dtype).name for channel in channels],
            "merge_equal": bool(np.array_equal(merged, source)),
            "insert_equal": bool(np.array_equal(inserted[:, :, 1], source[:, :, 1])),
        }

    _attempt(result["graphs"], "copy", copy_graph)
    _attempt(result["graphs"], "rgb2gray", gray_graph)
    _attempt(result["channels"], "data_movement", channel_graphs)
    print(json.dumps(result, indent=2))
    return 0 if result["buffer"].get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
