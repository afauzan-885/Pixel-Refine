"""Shared runtime contracts for the demosaic algorithm family.

The demosaic kernels remain family-specific, but their runtime inputs, graph
metadata, and temporary-buffer ownership follow the same small contract.  The
helpers in this module are intentionally internal: they do not select a
backend, register graphs, or change the AOT engine lifecycle.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from taichi_vision.taichi_aot.engine import (
    InputArray,
    OutputArray,
    engine as default_engine,
)


@dataclass(frozen=True)
class DemosaicInputs:
    """Logical inputs shared by Bayer demosaic families.

    The values are deliberately left in their caller-provided representation;
    conversion to AOT buffers belongs to :class:`DemosaicBufferSet`.
    """

    bayer: Any
    wb: Optional[Sequence[float]] = None
    black_level: float = 0.0
    white_level: float = 1.0
    cfa: Optional[Sequence[int]] = None
    cmatrix: Any = None
    dst: Any = None
    mode: str = "default"

    def as_mapping(self) -> Dict[str, Any]:
        """Return non-null values using the canonical input field names."""

        return {
            name: value
            for name, value in (
                ("bayer", self.bayer),
                ("wb", self.wb),
                ("black_level", self.black_level),
                ("white_level", self.white_level),
                ("cfa", self.cfa),
                ("cmatrix", self.cmatrix),
                ("dst", self.dst),
                ("mode", self.mode),
            )
            if value is not None
        }


@dataclass(frozen=True)
class DemosaicGraphSpec:
    """Describe one canonical graph and the buffers it expects."""

    family: str
    graph_name: str
    required_inputs: Tuple[str, ...] = field(default_factory=tuple)
    scratch_buffers: Tuple[str, ...] = field(default_factory=tuple)
    stages: Tuple[str, ...] = field(default_factory=tuple)
    output_shape: Optional[Tuple[int, ...]] = None
    output_dtype: Any = None
    variant: str = "default"

    def __post_init__(self) -> None:
        if not self.family or not self.graph_name:
            raise ValueError("family and graph_name are required")

    def missing_inputs(self, values: Mapping[str, Any]) -> Tuple[str, ...]:
        """Return required input names absent from ``values``."""

        return tuple(
            name
            for name in self.required_inputs
            if name not in values or values[name] is None
        )

    def validate_inputs(self, values: Mapping[str, Any]) -> None:
        """Raise a concise error when a graph input is missing."""

        missing = self.missing_inputs(values)
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"{self.graph_name} requires demosaic input(s): {names}")


class DemosaicRunner:
    """Resolve a graph contract and delegate execution to a dispatcher.

    The dispatcher owns the family-specific ABI.  This runner only converts
    the shared input container to a mapping, validates required names, and
    forwards ``(graph_name, values)`` unchanged with optional keyword context.
    """

    def __init__(self, spec: DemosaicGraphSpec, dispatcher) -> None:
        if not isinstance(spec, DemosaicGraphSpec):
            raise TypeError("spec must be a DemosaicGraphSpec")
        if not callable(dispatcher):
            raise TypeError("dispatcher must be callable")
        self.spec = spec
        self.dispatcher = dispatcher

    def resolve_inputs(self, values: Any) -> Dict[str, Any]:
        """Normalize supported input containers and validate the graph ABI."""

        if isinstance(values, DemosaicInputs):
            resolved = values.as_mapping()
        elif isinstance(values, Mapping):
            resolved = dict(values)
        elif hasattr(values, "as_mapping") and callable(values.as_mapping):
            resolved = dict(values.as_mapping())
        else:
            raise TypeError("values must be DemosaicInputs or a mapping")
        self.spec.validate_inputs(resolved)
        return resolved

    def run(self, values: Any, **kwargs):
        """Validate ``values`` and invoke the configured graph dispatcher."""

        resolved = self.resolve_inputs(values)
        return self.dispatcher(self.spec.graph_name, resolved, **kwargs)


class DemosaicBufferSet:
    """Own and release AOT buffers used by one demosaic invocation.

    CPU inputs are uploaded with :func:`InputArray`; output and scratch
    buffers are allocated with :func:`OutputArray` or the existing engine.
    Buffers supplied by a caller (for example a ``TaichiGPUBuffer``) are
    borrowed by default and are never released by this context manager.
    """

    def __init__(self, runtime_engine=None):
        self.engine = default_engine if runtime_engine is None else runtime_engine
        self._buffers: Dict[str, Any] = {}
        self._owned: Dict[str, Any] = {}
        self._closed = False

    def __enter__(self) -> "DemosaicBufferSet":
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        # Preserve the original operation error; cleanup remains best effort
        # when the body is already unwinding.
        self.close(raise_errors=exc_type is None)
        return False

    def __getitem__(self, name: str) -> Any:
        return self._buffers[name]

    def get(self, name: str, default: Any = None) -> Any:
        """Return a registered buffer, or ``default`` if absent."""

        return self._buffers.get(name, default)

    def detach(self, name: str) -> Any:
        """Transfer ownership of a buffer to the caller.

        This is used for ``return_gpu=True`` results.  The buffer remains
        registered for lookup, but the context will no longer release it.
        """

        self._ensure_open()
        if name not in self._buffers:
            raise KeyError(f"demosaic buffer {name!r} is not registered")
        return self._owned.pop(name, self._buffers[name])

    def items(self):
        """Iterate over registered ``(name, buffer)`` pairs."""

        return self._buffers.items()

    def register(self, name: str, buffer: Any, *, owned: bool = False) -> Any:
        """Register an existing buffer and return it.

        ``owned=False`` is the safe default for buffers passed in by callers.
        Set ``owned=True`` only when this set created or explicitly adopted the
        buffer and therefore owns its release lifecycle.
        """

        self._ensure_open()
        self._reserve(name)
        self._buffers[name] = buffer
        if owned:
            self._owned[name] = buffer
        return buffer

    def input(
        self,
        name: str,
        data: Any,
        *,
        is_vector: bool = False,
        vector_dim: Optional[int] = None,
    ) -> Any:
        """Upload ``data`` unless it is already an AOT buffer."""

        self._ensure_open()
        self._reserve(name)
        buffer = InputArray(data, is_vector=is_vector, vector_dim=vector_dim)
        self._buffers[name] = buffer
        if buffer is not data:
            self._owned[name] = buffer
        return buffer

    def output(
        self,
        name: str,
        shape: Sequence[int],
        *,
        dtype=None,
        is_vector: bool = False,
        vector_dim: Optional[int] = None,
        host_accessible: bool = False,
    ) -> Any:
        """Allocate and register an output buffer owned by this set."""

        self._ensure_open()
        self._reserve(name)
        kwargs = {
            "is_vector": is_vector,
            "vector_dim": vector_dim,
            "host_accessible": host_accessible,
        }
        if dtype is not None:
            kwargs["dtype"] = dtype
        buffer = OutputArray(shape, **kwargs)
        self._buffers[name] = buffer
        self._owned[name] = buffer
        return buffer

    def scratch(
        self,
        name: str,
        shape: Sequence[int],
        *,
        dtype=None,
        is_vector: bool = False,
        vector_dim: Optional[int] = None,
        host_accessible: bool = False,
    ) -> Any:
        """Allocate an engine-managed temporary buffer."""

        self._ensure_open()
        self._reserve(name)
        kwargs = {
            "is_vector": is_vector,
            "vector_dim": vector_dim,
            "host_accessible": host_accessible,
        }
        if dtype is not None:
            kwargs["dtype"] = dtype
        buffer = self.engine.allocate(shape, **kwargs)
        self._buffers[name] = buffer
        self._owned[name] = buffer
        return buffer

    def close(self, *, raise_errors: bool = True) -> None:
        """Synchronize and release owned buffers exactly once."""

        if self._closed:
            return
        errors = []
        try:
            if self._owned:
                self.engine.sync()
        except Exception as exc:  # pragma: no cover - backend-specific
            errors.append(exc)
        finally:
            for name, buffer in reversed(tuple(self._owned.items())):
                try:
                    release = getattr(buffer, "release", None)
                    if release is None:
                        raise RuntimeError(f"Owned demosaic buffer {name!r} is not releasable")
                    release()
                except Exception as exc:  # pragma: no cover - backend-specific
                    errors.append(exc)
            self._owned.clear()
            self._closed = True

        if errors and raise_errors:
            raise RuntimeError("Failed to clean up demosaic AOT buffers") from errors[0]

    def _reserve(self, name: str) -> None:
        if not name:
            raise ValueError("demosaic buffer name must not be empty")
        if name in self._buffers:
            raise KeyError(f"demosaic buffer {name!r} is already registered")

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("DemosaicBufferSet is already closed")


__all__ = [
    "DemosaicInputs",
    "DemosaicGraphSpec",
    "DemosaicRunner",
    "DemosaicBufferSet",
]
