"""onnxruntime-compatible option holders for the public neural facade.

These types exist so a caller written against ``onnxruntime`` keeps the same
source shape after switching the import to :mod:`taichi_vision.neural`:

    opts = neural.SessionOptions()
    opts.graph_optimization_level = neural.GraphOptimizationLevel.ORT_ENABLE_ALL
    opts.log_severity_level = 3

They are *value holders*. The Taichi runtime has no ONNX Runtime graph
optimizer, so the recorded values do not change execution; they are surfaced by
:func:`taichi_vision.neural.describe` so nothing is silently ignored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, ClassVar, List, Optional, Sequence, Tuple


class GraphOptimizationLevel(IntEnum):
    """Mirrors ``onnxruntime.GraphOptimizationLevel`` numeric values."""

    ORT_DISABLE_ALL = 0
    ORT_ENABLE_BASIC = 1
    ORT_ENABLE_EXTENDED = 2
    ORT_ENABLE_ALL = 99


class ExecutionMode(IntEnum):
    """Mirrors ``onnxruntime.ExecutionMode`` numeric values."""

    ORT_SEQUENTIAL = 0
    ORT_PARALLEL = 1


@dataclass
class SessionOptions:
    """Value holder mirroring the ``onnxruntime.SessionOptions`` surface we use.

    Only the fields application code actually sets are modelled. Unknown
    attributes still work because instances keep ``extra`` and allow attribute
    assignment, matching onnxruntime's plain-attribute style.
    """

    graph_optimization_level: GraphOptimizationLevel = GraphOptimizationLevel.ORT_DISABLE_ALL
    log_severity_level: int = 2
    intra_op_num_threads: int = 0
    inter_op_num_threads: int = 0
    enable_mem_pattern: bool = True
    enable_cpu_mem_arena: bool = True
    execution_mode: int = 0
    extra: dict = field(default_factory=dict)
    session_config_entries: dict = field(default_factory=dict)

    #: Recorded but inert settings, reported by ``describe()``.
    INERT_FIELDS: ClassVar[Tuple[str, ...]] = (
        "graph_optimization_level",
        "log_severity_level",
        "intra_op_num_threads",
        "inter_op_num_threads",
        "enable_mem_pattern",
        "enable_cpu_mem_arena",
        "execution_mode",
    )

    def add_session_config_entry(self, key: str, value: str) -> None:
        """Record a provider/session config entry (inert on the Taichi runtime)."""
        self.session_config_entries[str(key)] = str(value)

    def get_session_config_entry(self, key: str) -> Optional[str]:
        return self.session_config_entries.get(str(key))

    def __setattr__(self, name: str, value: Any) -> None:
        known = name in type(self).__dataclass_fields__ or name in {"extra"}
        object.__setattr__(self, name, value)
        if not known:
            self.extra[name] = value

    def inert_settings(self) -> dict:
        """Settings recorded but with no effect on the Taichi runtime."""
        return {
            name: getattr(self, name)
            for name in self.INERT_FIELDS
            if name in type(self).__dataclass_fields__
        }


@dataclass(frozen=True)
class NodeArg:
    """Graph input/output metadata, shaped like ``onnxruntime.NodeArg``."""

    name: str
    shape: Sequence[Optional[int]] = ()
    type: str = "tensor(float)"
    doc_string: str = ""

    def __repr__(self) -> str:
        return f"NodeArg(name={self.name!r}, shape={list(self.shape)!r}, type={self.type!r})"


def node_arg_from_shape(name: str, shape: Sequence[Optional[int]], dtype: str = "f32") -> NodeArg:
    """Build a :class:`NodeArg` from an internal dtype token."""
    onnx_type = {
        "f32": "tensor(float)",
        "i32": "tensor(int32)",
        "i64": "tensor(int64)",
    }.get(dtype, "tensor(float)")
    return NodeArg(name=name, shape=tuple(shape), type=onnx_type)


__all__ = [
    "GraphOptimizationLevel",
    "SessionOptions",
    "NodeArg",
    "node_arg_from_shape",
]
