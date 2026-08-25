"""Minimal packaged LLVM20 API regression entry point.

The script is intentionally independent from the Qt application.  A
PyInstaller build embeds the release ``bundles`` directory next to this
module; each process selects one native backend via ``--backend`` and runs a
small finite-output matrix through the public AOT facade.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("cpu", "cuda", "vulkan", "opengl"), default="cpu")
    args = parser.parse_args()

    # PyInstaller extracts data under _MEIPASS.  Point the normal resolver at
    # that embedded payload before importing the runtime facade.
    packed_root = getattr(sys, "_MEIPASS", None)
    if packed_root and os.path.isdir(os.path.join(packed_root, "bundles")):
        os.environ["PIXEL_REFINE_RUNTIME_ROOT"] = packed_root
        # The production package intentionally excludes the pip ``taichi``
        # module (and therefore its import-time TI_LIB_DIR setup).  The C-API
        # still needs the matching runtime directory for graph allocation.
        target = {
            "cpu": "cpu_x86_64_windows",
            "cuda": "cuda_x86_64_windows_nvidia",
            "vulkan": "vulkan_x86_64_windows",
            "opengl": "opengl_x86_64_windows",
        }[args.backend]
        runtime_dir = os.path.join(
            packed_root, "bundles", target, "python", "taichi", "_lib", "runtime"
        )
        if os.path.isdir(runtime_dir):
            os.environ["TI_LIB_DIR"] = runtime_dir
    os.environ["AOT_ARCH"] = args.backend
    os.environ.setdefault("AOT_DEVICE", "0")
    os.environ["AOT_STRICT_BACKEND"] = "1"

    from taichi_vision import taichi_aot

    src = np.linspace(0.0, 1.0, 64 * 64 * 3, dtype=np.float32).reshape(64, 64, 3)
    copied = np.asarray(taichi_aot.copy(src))
    gray = np.asarray(taichi_aot.rgb2gray(src))
    blurred = np.asarray(taichi_aot.gaussian_blur(src, sigma=1.0, kernel_size=5))
    resized = np.asarray(taichi_aot.resize(src, (32, 32)))
    outputs = {"copy": copied, "rgb2gray": gray, "gaussian_blur": blurred, "resize": resized}
    if not np.array_equal(copied, src):
        raise AssertionError("copy is not exact")
    if any(not np.isfinite(value).all() for value in outputs.values()):
        raise AssertionError("non-finite packaged API output")
    print(json.dumps({
        "backend": args.backend,
        "copy_exact": True,
        "finite": True,
        "shapes": {name: list(value.shape) for name, value in outputs.items()},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
