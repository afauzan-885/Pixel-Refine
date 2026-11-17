"""The native execution strategy: a model run by the Rust session.

## What this replaces

The `native` strategy used to point at `taichi_algorithm.neural.neural_engine.onnx`,
a Python per-node loop. This module is the same role, but the graph is lowered once
into a plan and executed by the Rust session in one call.

## Why the plan is built per input signature

ONNX shape inference needs concrete shapes, and those are only known when the caller
first feeds the model. The plan is therefore built once per signature and cached;
a second call with the same shapes reuses it. A call with different shapes rebuilds,
which is correct and is the reason the cache is keyed by shape rather than by model.

## What is refused, and where

An operator without a lowering is reported by `missing_ops` **before** any buffer is
written, so a partially executed graph cannot leave plausible intermediate values.
The message names the operators, because "model not runnable" is not actionable and
"this build lacks ConvTranspose" is.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..taichi_algorithm.neural.universal import plan_wire
from ..taichi_algorithm.neural.universal.plan import Plan
from .errors import NeuralError

try:  # pragma: no cover - the extension may be absent in a partial install
    import taichi.taichi_python as _native
except Exception as exc:  # pragma: no cover
    _native = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class NativeSession:
    """Run an ONNX model through the Rust plan executor."""

    def __init__(
        self,
        model_bytes: bytes,
        backend: str = "cpu",
        model_name: Optional[str] = None,
    ) -> None:
        if _native is None:
            raise NeuralError(
                f"the native strategy needs the taichi extension: {_IMPORT_ERROR}"
            )
        self.backend = backend
        self.model_name = model_name or "<bytes>"
        self.plan = Plan.from_model_bytes(model_bytes)
        self._session = None
        self._signature: Optional[Tuple[Tuple[str, Tuple[int, ...]], ...]] = None

    # ------------------------------------------------------------------ setup

    def _ensure_session(self, feeds: Dict[str, np.ndarray]) -> Any:
        """Build (or reuse) the session for this input signature."""
        signature = tuple(
            (name, tuple(int(v) for v in value.shape))
            for name, value in sorted(feeds.items())
        )
        if self._session is not None and signature == self._signature:
            return self._session

        shapes = {name: value.shape for name, value in feeds.items()}
        blob = plan_wire.encode_plan(self.plan, shapes)
        session = _native.NeuralSession(blob, backend=self.backend)

        missing = session.missing_ops
        if missing:
            raise NeuralError(
                f"{self.model_name}: this build cannot execute "
                f"{', '.join(missing)}; the model needs operators that have no "
                f"native lowering yet"
            )

        for name, value in plan_wire.constant_values(self.plan).items():
            session.set_constant(name, np.ascontiguousarray(value))
        self._session = session
        self._signature = signature
        return session

    # -------------------------------------------------------------- interface

    def run(
        self,
        output_names: Optional[Sequence[str]] = None,
        input_feed: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> List[Any]:
        feeds = dict(input_feed or {})
        missing = [name for name in self.plan.input_names if name not in feeds]
        if missing:
            raise NeuralError(
                f"{self.model_name}: missing inputs {missing}"
            )
        prepared: Dict[str, np.ndarray] = {}
        for name in self.plan.input_names:
            array = np.ascontiguousarray(feeds[name])
            dtype = self.plan.dtypes[name]
            prepared[name] = array.astype(
                {"f32": np.float32, "i32": np.int32, "i64": np.int64}[dtype],
                copy=False,
            )

        session = self._ensure_session(prepared)
        for name, value in prepared.items():
            session.set_input(name, value)
        produced = session.run()

        names = list(output_names) if output_names else list(self.plan.output_names)
        unknown = [name for name in names if name not in produced]
        if unknown:
            raise NeuralError(
                f"{self.model_name}: the plan does not produce {unknown}; "
                f"available outputs are {sorted(produced)}"
            )
        return [produced[name] for name in names]

    def get_inputs(self) -> List[Any]:
        return [_Arg(name, self.plan.dtypes[name]) for name in self.plan.input_names]

    def get_outputs(self) -> List[Any]:
        return [_Arg(name, self.plan.dtypes[name]) for name in self.plan.output_names]

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None
        self._signature = None


class _Arg:
    """Minimal stand-in for onnxruntime's `NodeArg`.

    Only what a caller actually reads is provided: the name and the dtype. Shape is
    deliberately absent because it depends on the input signature and a cached
    number here would be wrong for the next call.
    """

    def __init__(self, name: str, dtype: str) -> None:
        self.name = name
        self.type = dtype

    def __repr__(self) -> str:
        return f"<NodeArg name={self.name!r} type={self.type}>"


__all__ = ["NativeSession"]
