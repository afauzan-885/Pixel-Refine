"""Experimental pointwise fusion kernels for the WeightNet adaptive gate.

This module is intentionally standalone. It does not modify or register a
fusion in the production ONNX graph executor.
"""

import numpy as np
import taichi as ti


@ti.func
def _stable_softplus(x):
    """Match the stable FP32 Softplus implementation in onnx_native_graph."""
    u = ti.exp(-ti.abs(x))
    v = 1.0 + u
    correction = u
    if v != 1.0:
        correction = ti.log(v) * (u / (v - 1.0))
    return ti.max(x, 0.0) + correction


@ti.kernel
def _weightnet_gate_flat_kernel(
    conv: ti.types.ndarray(dtype=ti.f32, ndim=1),
    safety_softplus: ti.types.ndarray(dtype=ti.f32, ndim=1),
    out: ti.types.ndarray(dtype=ti.f32, ndim=1),
    batch: ti.i32,
    height: ti.i32,
    width: ti.i32,
):
    """Fuse gate operations over flat NCHW buffers without reshape copies."""
    plane_size = height * width
    for idx in range(batch * plane_size):
        n = idx // plane_size
        pixel = idx % plane_size
        channel0_idx = n * 2 * plane_size + pixel
        channel1_idx = channel0_idx + plane_size
        channel0 = _stable_softplus(conv[channel0_idx]) + 0.5
        channel1_minus_safety = (
            _stable_softplus(conv[channel1_idx]) - safety_softplus[idx]
        )
        product = channel0 * channel1_minus_safety
        out[idx] = 1.0 / (1.0 + ti.exp(-product))


def _validate_array(name: str, value: np.ndarray) -> None:
    if not isinstance(value, np.ndarray):
        raise TypeError(f"{name} must be a NumPy ndarray")
    if value.dtype != np.float32:
        raise TypeError(f"{name} must have dtype float32; got {value.dtype}")
    if not value.flags.c_contiguous:
        raise ValueError(f"{name} must be C-contiguous")


def fused_weightnet_adaptive_gate(
    conv_output: np.ndarray,
    safety_softplus: np.ndarray,
    out: np.ndarray | None = None,
) -> np.ndarray:
    """Run the experimental fused pointwise WeightNet adaptive-gate kernel.

    Expected inputs are NCHW FP32 arrays from the ONNX subgraph:

    ``conv_output`` has two channels and ``safety_softplus`` has one channel.
    The returned/materialized gate has shape ``[N, 1, H, W]``. Contiguous
    NumPy views are flattened without copying before dispatch. The caller must
    initialize Taichi for the desired backend before calling this function.
    Inputs and output must be non-overlapping to avoid in-place read/write races.
    """
    _validate_array("conv_output", conv_output)
    _validate_array("safety_softplus", safety_softplus)

    if conv_output.ndim != 4 or conv_output.shape[1] != 2:
        raise ValueError("conv_output must have shape [N, 2, H, W]")
    n, _, height, width = conv_output.shape
    if n <= 0 or height <= 0 or width <= 0:
        raise ValueError("batch and spatial dimensions must be positive")
    expected_safety = (n, 1, height, width)
    if safety_softplus.shape != expected_safety:
        raise ValueError(
            "safety_softplus must have shape "
            f"{expected_safety}; got {safety_softplus.shape}"
        )

    if out is None:
        out = np.empty(expected_safety, dtype=np.float32)
    else:
        _validate_array("out", out)
        if out.shape != expected_safety:
            raise ValueError(f"out must have shape {expected_safety}; got {out.shape}")
        if not out.flags.writeable:
            raise ValueError("out must be writable")

    if np.shares_memory(out, conv_output) or np.shares_memory(out, safety_softplus):
        raise ValueError("out must not overlap either input")

    _weightnet_gate_flat_kernel(
        conv_output.reshape(-1),
        safety_softplus.reshape(-1),
        out.reshape(-1),
        n,
        height,
        width,
    )
    return out

