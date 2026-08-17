"""Small native smoke/parity probe for an isolated LLVM20 Python profile.

Run this file with the target bundle first on ``PYTHONPATH``.  It deliberately
rejects Taichi's adaptive CPU fallback so a green result proves that the
requested backend actually compiled and executed a kernel.
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import taichi as ti
from taichi.lang import impl


ARCHES = {
    "cpu": ti.cpu,
    "cuda": ti.cuda,
    "vulkan": ti.vulkan,
    "opengl": ti.opengl,
}
DTYPES = {
    "u8": (ti.u8, np.uint8),
    "u16": (ti.u16, np.uint16),
    "i16": (ti.i16, np.int16),
    "u32": (ti.u32, np.uint32),
    "i32": (ti.i32, np.int32),
    "f16": (ti.f16, np.float16),
    "f32": (ti.f32, np.float32),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=tuple(ARCHES), required=True)
    parser.add_argument("--dtype", choices=tuple(DTYPES), default="f32")
    parser.add_argument("--size", type=int, default=64)
    args = parser.parse_args()
    if args.size < 4:
        raise SystemExit("--size must be >= 4")

    requested = ARCHES[args.backend]
    ti.init(arch=requested, offline_cache=False, log_level=ti.ERROR)
    active = impl.current_cfg().arch
    if active != requested:
        raise RuntimeError(
            f"native backend mismatch: requested={requested}, active={active}"
        )

    n = args.size
    taichi_dtype, numpy_dtype = DTYPES[args.dtype]
    values = ti.field(dtype=taichi_dtype, shape=(n, n))

    @ti.kernel
    def fill():
        for i, j in values:
            if ti.static(args.dtype in ("u8", "u16", "i16", "u32", "i32")):
                values[i, j] = i * 3 + j
            else:
                values[i, j] = ti.cast(i, ti.f32) * 0.25 + ti.cast(j, ti.f32) * 1.5

    started = time.perf_counter()
    fill()
    elapsed = time.perf_counter() - started
    result = values.to_numpy()
    if args.dtype in ("u8", "u16", "i16", "u32", "i32"):
        expected = (
            np.arange(n, dtype=np.int32)[:, None] * 3
            + np.arange(n, dtype=np.int32)[None, :]
        ).astype(numpy_dtype)
    else:
        expected = (
            np.arange(n, dtype=np.float32)[:, None] * np.float32(0.25)
            + np.arange(n, dtype=np.float32)[None, :] * np.float32(1.5)
        ).astype(numpy_dtype)
    error = float(np.max(np.abs(result - expected)))
    tolerance = 1e-3 if args.dtype == "f16" else 1e-6
    payload = {
        "backend": args.backend,
        "requested_arch": str(requested),
        "active_arch": str(active),
        "shape": [n, n],
        "dtype": args.dtype,
        "max_abs_error": error,
        "finite": bool(np.isfinite(result).all()),
        "elapsed_seconds": elapsed,
        "pass": bool(error <= tolerance and np.isfinite(result).all()),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
