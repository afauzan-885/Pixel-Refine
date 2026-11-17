"""Public ONNX inference facade: one import, onnxruntime-shaped.

    import taichi_vision.neural as neural

    session = neural.InferenceSession("model.onnx")
    session.run(None, {"input": array})

The facade owns no kernels. It resolves an execution strategy (pool, resident or
native) and delegates every call to the internal implementation, so callers never
declare kernels, buffers, or backend plumbing themselves.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from .capabilities import (
    DEFAULT_NEURAL_DIR,
    NATIVE_GRAPH_OPS,
    capabilities as _capabilities,
    find_prebaked_artifact,
    neural_asset_dir,
    pool_artifact_path,
)
from .errors import BackendUnavailable, CapabilityMissingError, ModelNotRunnable, NeuralError
from .options import GraphOptimizationLevel, NodeArg, SessionOptions, node_arg_from_shape
from .resolver import Resolution, ResolutionRecord, resolve, resolve_backend


def _read_model(
    model_path_or_bytes: Union[str, Path, bytes, bytearray, memoryview],
) -> tuple[bytes, str]:
    if isinstance(model_path_or_bytes, (str, Path)):
        path = Path(model_path_or_bytes)
        if not path.is_file():
            raise FileNotFoundError(f"ONNX model not found: {path}")
        return path.read_bytes(), path.stem
    if isinstance(model_path_or_bytes, (bytes, bytearray, memoryview)):
        return bytes(model_path_or_bytes), "neural_model"
    raise TypeError(
        f"expected a model path or serialized ONNX bytes, got {type(model_path_or_bytes)}"
    )


class InferenceSession:
    """Drop-in replacement for ``onnxruntime.InferenceSession`` on Taichi.

    Accepts the same constructor shape used by application code: a model path or
    serialized bytes, ``providers``, and ``sess_options``. The strategy is chosen
    automatically and reported through :func:`describe`.
    """

    def __init__(
        self,
        path_or_bytes: Union[str, Path, bytes, bytearray, memoryview],
        sess_options: Optional[SessionOptions] = None,
        providers: Optional[Sequence[Any]] = None,
        provider_options: Optional[Sequence[Dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        model_bytes, model_name = _read_model(path_or_bytes)
        backend = kwargs.pop("backend", None)
        if providers is not None:
            backend = _backend_from_providers(providers, fallback=backend)
        asset_dir = kwargs.pop("asset_dir", None)

        self.options = sess_options if isinstance(sess_options, SessionOptions) else None
        if sess_options is not None and self.options is None:
            raise TypeError("sess_options must be a taichi_vision.neural.SessionOptions")
        self.provider_options = tuple(provider_options or ())
        self.model_name = model_name
        self.model_bytes = model_bytes

        resolution = resolve(
            model_bytes,
            backend=backend,
            model_name=model_name,
            asset_dir=Path(asset_dir) if asset_dir else None,
        )
        self.resolution = resolution
        self.backend = resolution.backend
        self.strategy = resolution.strategy
        self._impl = _instantiate(resolution)

    # ------------------------------------------------------------- delegates

    def run(
        self,
        output_names: Optional[Sequence[str]] = None,
        input_feed: Optional[Dict[str, Any]] = None,
        run_options: Any = None,
        **kwargs: Any,
    ) -> List[Any]:
        """Execute the model, matching the onnxruntime call shape."""
        return self._impl.run(
            output_names=output_names,
            input_feed=input_feed or {},
            **kwargs,
        )

    def get_inputs(self) -> List[NodeArg]:
        return list(self._impl.get_inputs())

    def get_outputs(self) -> List[NodeArg]:
        return list(self._impl.get_outputs())

    def get_providers(self) -> List[str]:
        return [f"{_provider_prefix(self.strategy)}_{self.backend.upper()}"]

    def get_provider_options(self) -> List[Dict[str, Any]]:
        return list(self.provider_options)

    def close(self) -> None:
        closer = getattr(self._impl, "close", None)
        if closer is not None:
            closer()

    def __enter__(self) -> "InferenceSession":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            f"<taichi_vision.neural.InferenceSession backend={self.backend} "
            f"strategy={self.strategy} provider={self.get_providers()[0]}>"
        )


def load(
    model_path_or_bytes: Union[str, Path, bytes, bytearray, memoryview],
    *,
    backend: Optional[str] = None,
    sess_options: Optional[SessionOptions] = None,
    asset_dir: Optional[Union[str, Path]] = None,
) -> InferenceSession:
    """Explicit alias for :class:`InferenceSession` with keyword-only options."""
    return InferenceSession(
        model_path_or_bytes,
        sess_options=sess_options,
        backend=backend,
        asset_dir=asset_dir,
    )


def describe(session: InferenceSession) -> str:
    """Human-readable report: chosen strategy, artifact, reasons, inert options."""
    record: ResolutionRecord = session.resolution.record
    lines = [record.describe()]
    if session.options is not None:
        inert = session.options.inert_settings()
        lines.append(
            "session_options: recorded but inert on the Taichi runtime "
            f"({', '.join(f'{k}={v!s}' for k, v in inert.items())})"
        )
    return "\n".join(lines)


def capabilities(backend: Optional[str] = None, asset_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Report what the neural runtime can execute right now (no device init)."""
    return _capabilities(
        backend=resolve_backend(backend),
        base=Path(asset_dir) if asset_dir else None,
    )


def get_available_providers() -> List[str]:
    """Providers this runtime can serve, mirroring ``ort.get_available_providers``.

    The list contains the Taichi provider names *and* the onnxruntime provider
    aliases the facade accepts (``CPUExecutionProvider`` etc.), so caller code
    that filters its preferred providers by availability keeps working.
    """
    from taichi.aot_engine import get_backend_name

    backend = str(get_backend_name()).lower()
    available = [f"TaichiPool_{backend.upper()}", "TaichiNative"]
    alias = {
        "cpu": "CPUExecutionProvider",
        "cuda": "CUDAExecutionProvider",
        "vulkan": "VulkanExecutionProvider",
        "opengl": "OpenGLExecutionProvider",
    }.get(backend)
    if alias:
        available.append(alias)
    # CPU is always an accepted preference; the runtime decides the real device.
    if "CPUExecutionProvider" not in available:
        available.append("CPUExecutionProvider")
    return available


# ---------------------------------------------------------------------------
# internals
# ---------------------------------------------------------------------------


def _backend_from_providers(providers: Sequence[Any], fallback: Optional[str]) -> Optional[str]:
    for provider in providers:
        token = str(provider[0] if isinstance(provider, (tuple, list)) else provider).lower()
        for name in ("cuda", "vulkan", "opengl", "cpu"):
            if name in token:
                return name
    return fallback


def _provider_prefix(strategy: str) -> str:
    return {"pool": "TaichiPool", "resident": "TaichiResident", "native": "TaichiNative"}.get(
        strategy, "Taichi"
    )


def _instantiate(resolution: Resolution) -> Any:
    """Construct the internal implementation for a resolved strategy."""
    if resolution.strategy == "pool":
        from ..taichi_algorithm.neural.universal import UniversalSession

        return UniversalSession(
            resolution.graph_model_bytes,
            backend=resolution.backend,
            model_name=resolution.model_name,
        )
    if resolution.strategy == "resident":
        from ..taichi_algorithm.neural.neural import InferenceSession as ResidentSession

        return ResidentSession(resolution.artifact, backend=resolution.backend)
    if resolution.strategy == "native":
        # The native strategy now runs through the Rust plan executor. The previous
        # target (`neural_engine.onnx`) was a per-node Python loop, which is what
        # this whole effort replaces.
        from .native_session import NativeSession

        return NativeSession(
            resolution.graph_model_bytes,
            backend=resolution.backend,
            model_name=resolution.model_name,
        )
    raise NeuralError(f"unknown resolved strategy {resolution.strategy!r}")


__all__ = [
    "InferenceSession",
    "load",
    "describe",
    "capabilities",
    "get_available_providers",
    "SessionOptions",
    "GraphOptimizationLevel",
    "NodeArg",
    "neural_asset_dir",
    "pool_artifact_path",
    "find_prebaked_artifact",
    "NATIVE_GRAPH_OPS",
    "NeuralError",
    "BackendUnavailable",
    "CapabilityMissingError",
    "ModelNotRunnable",
]
