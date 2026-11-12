"""Dtype mapping, tensor specs, and symbolic integer values.

Shapes must be resolved at ``run()`` time so a single compiled pool can serve
several input sizes. Integer values that only describe shapes are carried as
small Python callables (``SVal``) evaluated against the concrete input shape
context; everything else becomes a device tensor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

F32 = "f32"
I32 = "i32"
I64 = "i64"
BOOL = "i32"

SUPPORTED_DTYPES = (F32, I32, I64)

# ONNX TensorProto element types that this profile admits.
ONNX_ELEM_TYPE = {
    1: F32,
    6: I32,
    7: I64,
    9: BOOL,
}

NUMPY_DTYPE = {
    F32: np.float32,
    I32: np.int32,
    I64: np.int64,
}

# ONNX attribute ``to`` value -> internal dtype.
ONNX_CAST_TO = {
    1: F32,
    6: I32,
    7: I64,
    9: BOOL,
    11: F32,  # float64 is demoted; the profile is single precision.
}


@dataclass(frozen=True)
class TensorSpec:
    """Static description of one graph value."""

    name: str
    dtype: str
    rank: Optional[int] = None


SVal = Callable[[Dict[str, Tuple[int, ...]]], int]
"""Symbolic integer: evaluated with ``{input_name: concrete_shape}``."""


def const(value: int) -> SVal:
    number = int(value)
    return lambda _ctx: number


def dim_of(name: str, axis: int) -> SVal:
    def resolve(ctx: Dict[str, Tuple[int, ...]]) -> int:
        shape = ctx[name]
        index = axis if axis >= 0 else len(shape) + axis
        return int(shape[index])

    return resolve


def prod_of(values: Iterable[SVal]) -> SVal:
    parts = list(values)
    return lambda ctx: int(np.prod([p(ctx) for p in parts], dtype=np.int64))


def evaluate(values: Sequence[SVal], ctx: Dict[str, Tuple[int, ...]]) -> List[int]:
    return [int(v(ctx)) for v in values]


def normalize_axis(axis: int, rank: int) -> int:
    return axis + rank if axis < 0 else axis


def numpy_shape(shape: Sequence[SVal], ctx: Dict[str, Tuple[int, ...]]) -> Tuple[int, ...]:
    return tuple(evaluate(shape, ctx))


def product(shape: Sequence[int]) -> int:
    total = 1
    for value in shape:
        total *= int(value)
    return total


def broadcast_shape(a: Sequence[int], b: Sequence[int]) -> Tuple[int, ...]:
    """NumPy-style broadcast of two concrete shapes."""
    rank = max(len(a), len(b))
    pa = (1,) * (rank - len(a)) + tuple(int(v) for v in a)
    pb = (1,) * (rank - len(b)) + tuple(int(v) for v in b)
    out: List[int] = []
    for da, db in zip(pa, pb):
        if da == db or db == 1:
            out.append(da)
        elif da == 1:
            out.append(db)
        else:
            raise ValueError(f"shapes {tuple(a)} and {tuple(b)} are not broadcastable")
    return tuple(out)


def broadcast_strides(shape: Sequence[int], out_shape: Sequence[int]) -> Tuple[int, ...]:
    """Contiguous strides of ``shape`` broadcast into ``out_shape`` (0 where expanded)."""
    rank = len(out_shape)
    padded = (1,) * (rank - len(shape)) + tuple(int(v) for v in shape)
    strides = [0] * rank
    running = 1
    for axis in range(rank - 1, -1, -1):
        if padded[axis] == 1 and out_shape[axis] != 1:
            strides[axis] = 0
        else:
            strides[axis] = running
        running *= padded[axis]
    return tuple(strides)


def pad_to(values: Sequence[int], size: int, fill: int = 1) -> List[int]:
    padded = list(values)[:size]
    if len(padded) < size:
        padded = [fill] * (size - len(padded)) + padded
    return padded


def as_numpy(value: Any, dtype: str) -> np.ndarray:
    return np.ascontiguousarray(value, dtype=NUMPY_DTYPE[dtype])


def dtype_of_array(value: np.ndarray) -> str:
    kind = value.dtype
    if kind == np.float32:
        return F32
    if kind == np.float64:
        return F32
    if kind == np.int32:
        return I32
    if kind in (np.int64, np.uint32, np.uint64):
        return I64
    if kind == np.bool_:
        return BOOL
    raise ValueError(f"unsupported numpy dtype {kind}")