"""NumPy-free public byte API for native DNG/TIFF compression.

This facade deliberately loads only the standard-library DNG container,
bitstream, and Deflate modules.  The legacy ndarray API remains available
through ``taichi_vision.taichi_algorithm.compression.dng_aot``; callers that
need a native byte/memoryview boundary should use this module instead.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any


def _load_dng_module() -> Any:
    root = Path(__file__).resolve().parent.parent
    compression = root / "taichi_vision" / "taichi_algorithm" / "compression"
    package_name = "taichi_vision._native_dng"
    package = sys.modules.get(package_name)
    if package is None:
        package = types.ModuleType(package_name)
        package.__path__ = [str(compression)]
        sys.modules[package_name] = package

    for module_name in ("bitstream", "dng_deflate"):
        qualified = f"{package_name}.{module_name}"
        if qualified in sys.modules:
            continue
        path = compression / f"{module_name}.py"
        spec = importlib.util.spec_from_file_location(qualified, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load native DNG dependency: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified] = module
        spec.loader.exec_module(module)

    qualified = f"{package_name}.dng_aot"
    existing = sys.modules.get(qualified)
    if existing is not None:
        return existing
    path = compression / "dng_aot.py"
    spec = importlib.util.spec_from_file_location(qualified, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load native DNG module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified] = module
    spec.loader.exec_module(module)
    return module


_dng = _load_dng_module()

encode_dng_bytes = _dng.encode_dng_bytes
decode_dng_bytes = _dng.decode_dng_bytes
read_dng = _dng.read_dng_aot


__all__ = ["encode_dng_bytes", "decode_dng_bytes", "read_dng"]
