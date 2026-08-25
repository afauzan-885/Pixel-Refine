"""NumPy-free public entry point for the additive native compression ABI.

The historical ``taichi_vision.taichi_algorithm`` package eagerly imports
the broad image-processing compatibility surface, including NumPy-backed
modules.  Native compression callers need a narrow import that does not pay
that cost or claim a dependency-free path after the fact.  This facade loads
only the standard-library native dispatch and video-preparation modules from
the compression directory and exposes the same target-qualified TCM bridge.

The legacy encoder APIs remain unchanged.  Variable-length codec serializers
are still separate host-side stages; this module only exposes native tensor
graphs and fails closed when a graph or target artifact is unavailable.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any


def _load_stack() -> tuple[Any, Any]:
    root = Path(__file__).resolve().parent.parent
    compression = root / "taichi_vision" / "taichi_algorithm" / "compression"
    package_name = "taichi_vision._compression_native"
    package = sys.modules.get(package_name)
    if package is None:
        package = types.ModuleType(package_name)
        package.__path__ = [str(compression)]
        sys.modules[package_name] = package

    def load(name: str, path: Path) -> Any:
        existing = sys.modules.get(name)
        if existing is not None:
            return existing
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load native compression module: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    dispatch = load(
        f"{package_name}.native_dispatch",
        compression / "native_dispatch.py",
    )
    prep = load(
        f"{package_name}.native_video_prep",
        compression / "native_video_prep.py",
    )
    return dispatch, prep


_dispatch, _prep = _load_stack()

ABI_VERSION = _dispatch.ABI_VERSION
NativeTensor = _dispatch.NativeTensor
NativeTensorDescriptor = _dispatch.NativeTensorDescriptor
NativeAOTEngine = _dispatch.NativeAOTEngine
NativeGraphRequest = _dispatch.NativeGraphRequest
NativeDispatchError = _dispatch.NativeDispatchError
NativeDispatchUnavailable = _dispatch.NativeDispatchUnavailable
NativeDispatchContractError = _dispatch.NativeDispatchContractError
build_native_request = _dispatch.build_native_request
dispatch_native_graph = _dispatch.dispatch_native_graph
native_dispatch_report = _dispatch.native_dispatch_report
prepare_yuv_native = _prep.prepare_yuv_native
prepare_av1_dc_residual_native = _prep.prepare_av1_dc_residual_native
native_video_prep_capability_report = _prep.native_video_prep_capability_report


__all__ = [
    "ABI_VERSION",
    "NativeTensor",
    "NativeTensorDescriptor",
    "NativeAOTEngine",
    "NativeGraphRequest",
    "NativeDispatchError",
    "NativeDispatchUnavailable",
    "NativeDispatchContractError",
    "build_native_request",
    "dispatch_native_graph",
    "native_dispatch_report",
    "prepare_yuv_native",
    "prepare_av1_dc_residual_native",
    "native_video_prep_capability_report",
]
