"""Experimental pointwise Mul -> Clip fusion for flat FP32 Taichi buffers.

This prototype targets WeightNet's ``Mul_5 -> Clip_2`` pattern. It accepts
equal-length one-dimensional Taichi ndarrays and scalar, non-NaN Clip bounds.
Exact elementwise input/output aliasing is safe; callers must not provide
partially overlapping storage. It is not wired into ``NativeGraph``.
"""

import math
from numbers import Real

import taichi as ti


@ti.kernel
def _fused_mul_clip_kernel(
    lhs: ti.types.ndarray(ti.f32, 1),
    rhs: ti.types.ndarray(ti.f32, 1),
    output: ti.types.ndarray(ti.f32, 1),
    low: ti.f32,
    high: ti.f32,
):
    for index in output:
        product = lhs[index] * rhs[index]
        # ONNX Runtime and NumPy preserve NaN through Clip. Explicit handling
        # avoids backend min/max instructions that may otherwise select a
        # numeric operand when one operand is NaN.
        if product != product:
            output[index] = product
        else:
            output[index] = ti.min(ti.max(product, low), high)


def _validate_array(name, value):
    shape = getattr(value, "shape", None)
    if shape is None or len(shape) != 1:
        raise ValueError(f"{name} must be a one-dimensional Taichi ndarray")
    if getattr(value, "dtype", None) != ti.f32:
        raise TypeError(f"{name} must have dtype ti.f32")
    return tuple(shape)


def fused_mul_clip(lhs, rhs, output, low, high):
    """Run ``Clip(lhs * rhs, low, high)`` on equal-length FP32 buffers.

    Bounds may be finite or infinite scalar numbers but cannot be NaN. The
    kernel is elementwise, so ``output`` may be the exact same ndarray object
    as either input. Distinct views over partially overlapping storage are not
    supported.
    """
    lhs_shape = _validate_array("lhs", lhs)
    rhs_shape = _validate_array("rhs", rhs)
    output_shape = _validate_array("output", output)
    if lhs_shape != rhs_shape or lhs_shape != output_shape:
        raise ValueError(
            "lhs, rhs, and output must have identical one-dimensional shapes"
        )
    if not isinstance(low, Real) or not isinstance(high, Real):
        raise TypeError("Clip bounds must be scalar numbers")
    low = float(low)
    high = float(high)
    if math.isnan(low) or math.isnan(high):
        raise ValueError("NaN Clip bounds are not supported by this prototype")
    _fused_mul_clip_kernel(lhs, rhs, output, low, high)


__all__ = ["fused_mul_clip"]
