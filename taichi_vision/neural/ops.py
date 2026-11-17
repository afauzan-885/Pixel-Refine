"""Operator-level API: call one primitive directly, without a model.

The session API runs a graph. This runs one operator, which is what a caller wants
when they are building something the plan does not cover, or checking a value
against a reference.

    import taichi_vision.neural as neural
    ops = neural.ops

    y = ops.relu(x)
    z = ops.add(a, b)
    g = ops.gelu(x, approximate="tanh")

## What these are, and are not

Each call is one primitive in the Taichi runtime, over caller arrays. It is not a
graph, not a session, and not a fusion: allocation, dtype checks and the shape rules
are the caller's business, and the result is a new array. Anything bigger belongs in
a model and :class:`~taichi_vision.neural.InferenceSession`.

## Two rules that are enforced

* **dtype is explicit, never guessed.** `ops.add` on two `float32` arrays returns
  `float32`; mixing `float32` and `int32` is refused rather than promoted, because
  a promotion rule invented here would diverge from ONNX's.
* **broadcasting follows ONNX**, so an operand of rank 0 or a `(1, C, 1, 1)` scale
  works the way it does in a model.

## Availability

:func:`capabilities` reports which operators exist in this build. A name that is
not there raises `NeuralError` with the list, rather than computing something else.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np

from .errors import NeuralError

try:  # pragma: no cover - the extension may be absent in a partial install
    import taichi.taichi_python as _native
except Exception as exc:  # pragma: no cover
    _native = None
    _IMPORT_ERROR: Optional[Exception] = exc
else:
    _IMPORT_ERROR = None


def _native_module():
    if _native is None:
        raise NeuralError(
            f"the operator API needs the taichi extension: {_IMPORT_ERROR}"
        )
    return _native


#: Unary operator name to primitive code, matching `nn/unary.rs`.
_UNARY_CODES: Dict[str, int] = {
    "identity": 0,
    "relu": 1,
    "sigmoid": 2,
    "tanh": 3,
    "gelu_exact": 4,
    "gelu_tanh": 5,
    "sqrt": 6,
    "abs": 7,
    "neg": 8,
    "erf": 9,
    "softplus": 10,
    "floor": 11,
    "exp": 12,
    "log": 13,
    "sin": 14,
    "cos": 15,
    "square": 16,
    "reciprocal": 17,
    "ceil": 18,
    "sign": 19,
    "leaky_relu": 20,
    "clip": 21,
}

#: Binary operator name to primitive code, matching `nn/binary.rs`.
_BINARY_CODES: Dict[str, int] = {
    "add": 0,
    "sub": 1,
    "mul": 2,
    "div": 3,
    "pow": 4,
    "min": 5,
    "max": 6,
    "mod": 7,
}

_FLOAT_DTYPES = (np.float32,)


def _as_float(array, name: str) -> np.ndarray:
    """Accept f32 or narrow f64, refuse anything that would lose information."""
    value = np.asarray(array)
    if value.dtype == np.float64:
        return np.ascontiguousarray(value, dtype=np.float32)
    if value.dtype not in (np.float32, np.float16):
        raise NeuralError(
            f"{name}: expected a float array, got {value.dtype}. "
            f"Cast explicitly so the conversion is visible"
        )
    return np.ascontiguousarray(value, dtype=np.float32)


def _strides(shape: Sequence[int], out_shape: Sequence[int]) -> List[int]:
    """Contiguous strides with zeros on broadcast axes."""
    if not shape:
        return []
    offset = len(out_shape) - len(shape)
    own = [1] * len(shape)
    running = 1
    for axis in range(len(shape) - 1, -1, -1):
        own[axis] = running
        running *= shape[axis]
    return [
        0 if shape[axis] == 1 and out_shape[axis + offset] != 1 else own[axis]
        for axis in range(len(shape))
    ]


def _unary(name: str, x, low: float = 0.0, high: float = 0.0) -> np.ndarray:
    module = _native_module()
    source = _as_float(x, name)
    out = np.empty_like(source)
    module.unary_f32(
        out.ctypes.data,
        source.ctypes.data,
        source.size,
        _UNARY_CODES[name],
        float(low),
        float(high),
    )
    return out


def capabilities() -> Dict[str, List[str]]:
    """What this build can execute, as reported by the extension."""
    return dict(_native_module().neural_capabilities())


def available() -> List[str]:
    """Operator names this module exposes, lowercase."""
    return sorted(list(_UNARY_CODES) + list(_BINARY_CODES))


# ------------------------------------------------------------------ unary


def identity(x) -> np.ndarray:
    return _unary("identity", x)


def relu(x) -> np.ndarray:
    return _unary("relu", x)


def sigmoid(x) -> np.ndarray:
    return _unary("sigmoid", x)


def tanh(x) -> np.ndarray:
    return _unary("tanh", x)


def gelu(x, approximate: str = "none") -> np.ndarray:
    """Gaussian error linear unit.

    `approximate="none"` is the exact erf definition, which is ONNX's default;
    `"tanh"` is the cheaper approximation. They differ by about 1e-3, which is small
    enough that swapping them silently changes results without looking wrong — so an
    unknown value is refused rather than defaulted.
    """
    if approximate == "none":
        return _unary("gelu_exact", x)
    if approximate == "tanh":
        return _unary("gelu_tanh", x)
    raise NeuralError(
        f"gelu: approximate must be 'none' or 'tanh', not {approximate!r}"
    )


def sqrt(x) -> np.ndarray:
    return _unary("sqrt", x)


def abs(x) -> np.ndarray:  # noqa: A001 - the name is the operator
    return _unary("abs", x)


def neg(x) -> np.ndarray:
    return _unary("neg", x)


def erf(x) -> np.ndarray:
    return _unary("erf", x)


def softplus(x) -> np.ndarray:
    return _unary("softplus", x)


def floor(x) -> np.ndarray:
    return _unary("floor", x)


def ceil(x) -> np.ndarray:
    return _unary("ceil", x)


def exp(x) -> np.ndarray:
    return _unary("exp", x)


def log(x) -> np.ndarray:
    return _unary("log", x)


def sin(x) -> np.ndarray:
    return _unary("sin", x)


def cos(x) -> np.ndarray:
    return _unary("cos", x)


def square(x) -> np.ndarray:
    return _unary("square", x)


def reciprocal(x) -> np.ndarray:
    return _unary("reciprocal", x)


def sign(x) -> np.ndarray:
    return _unary("sign", x)


def leaky_relu(x, alpha: float = 0.01) -> np.ndarray:
    return _unary("leaky_relu", x, alpha, 0.0)


def clip(x, min=None, max=None) -> np.ndarray:  # noqa: A002 - ONNX's attribute names
    """Clamp to `[min, max]`. Either bound may be omitted, meaning unbounded."""
    low = -np.inf if min is None else float(min)
    high = np.inf if max is None else float(max)
    if low > high:
        raise NeuralError(f"clip: min {low} is greater than max {high}")
    return _unary("clip", x, low, high)


# ----------------------------------------------------------------- binary


def _binary(name: str, a, b) -> np.ndarray:
    module = _native_module()
    left = _as_float(a, f"{name}.a")
    right = _as_float(b, f"{name}.b")
    out_shape = np.broadcast_shapes(left.shape, right.shape)
    out = np.empty(out_shape, dtype=np.float32)
    module.binary_f32(
        out.ctypes.data,
        left.ctypes.data,
        right.ctypes.data,
        list(out_shape),
        list(left.shape),
        list(right.shape),
        _strides(left.shape, out_shape),
        _strides(right.shape, out_shape),
        _BINARY_CODES[name],
    )
    return out


def add(a, b) -> np.ndarray:
    return _binary("add", a, b)


def sub(a, b) -> np.ndarray:
    return _binary("sub", a, b)


def mul(a, b) -> np.ndarray:
    return _binary("mul", a, b)


def div(a, b) -> np.ndarray:
    return _binary("div", a, b)


def pow(a, b) -> np.ndarray:  # noqa: A001
    return _binary("pow", a, b)


def minimum(a, b) -> np.ndarray:
    return _binary("min", a, b)


def maximum(a, b) -> np.ndarray:
    return _binary("max", a, b)


def mod(a, b) -> np.ndarray:
    """Floor-mod, matching ONNX `Mod` with `fmod=0`: the result takes b's sign."""
    return _binary("mod", a, b)


# ------------------------------------------------------------- structure


def where(condition, x, y) -> np.ndarray:
    """`condition != 0 ? x : y`, with ONNX broadcasting across all three."""
    module = _native_module()
    cond = np.asarray(condition)
    # The profile stores a bool as int32; a numpy bool array is one byte per
    # element, so it is widened here rather than refused.
    if cond.dtype == np.bool_:
        cond = cond.astype(np.int32)
    elif cond.dtype != np.int32:
        raise NeuralError(
            f"where: condition must be bool or int32, got {cond.dtype}"
        )
    cond = np.ascontiguousarray(cond)
    left = _as_float(x, "where.x")
    right = _as_float(y, "where.y")
    out_shape = np.broadcast_shapes(cond.shape, left.shape, right.shape)
    out = np.empty(out_shape, dtype=np.float32)
    module.where_f32(
        out.ctypes.data,
        cond.ctypes.data,
        left.ctypes.data,
        right.ctypes.data,
        list(out_shape),
        list(cond.shape),
        list(left.shape),
        list(right.shape),
        _strides(cond.shape, out_shape),
        _strides(left.shape, out_shape),
        _strides(right.shape, out_shape),
    )
    return out


__all__ = [
    "available",
    "capabilities",
    # unary
    "identity",
    "relu",
    "sigmoid",
    "tanh",
    "gelu",
    "sqrt",
    "abs",
    "neg",
    "erf",
    "softplus",
    "floor",
    "ceil",
    "exp",
    "log",
    "sin",
    "cos",
    "square",
    "reciprocal",
    "sign",
    "leaky_relu",
    "clip",
    # binary
    "add",
    "sub",
    "mul",
    "div",
    "pow",
    "minimum",
    "maximum",
    "mod",
    # structure
    "where",
]
