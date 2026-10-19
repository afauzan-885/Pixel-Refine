# -*- coding: utf-8 -*-
"""Neural model factories and Taichi execution.

Static WeightNet graphs use explicitly admitted FP32 native operators. Backend
and numerical qualification is profile-specific; unsupported graphs fail rather
than execute through a different inference framework. Neural .tcm files are
model archives, not compiled Taichi AOT modules.
"""

import io
import json
import os
from pathlib import Path
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
import zipfile

import numpy as np
import taichi as ti

# ==============================================================================
# 1. SPECIALIZED & FUSED TAICHI COMPUTE KERNELS
# ==============================================================================

@ti.kernel
def _ti_conv2d_generic(
    x: ti.types.ndarray(dtype=ti.f32, ndim=4),
    w: ti.types.ndarray(dtype=ti.f32, ndim=4),
    b: ti.types.ndarray(dtype=ti.f32, ndim=1),
    out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    pad_top: ti.i32, pad_left: ti.i32,
    stride_h: ti.i32, stride_w: ti.i32,
    dil_h: ti.i32, dil_w: ti.i32,
    group: ti.i32, has_bias: ti.i32,
    act_type: ti.i32,  # 0: None, 1: ReLU, 2: Sigmoid
):
    """Generic 2D Convolution with optional in-register activation fusion."""
    for n, oc, oh, ow in out:
        out_channels_per_group = out.shape[1] // group
        g = oc // out_channels_per_group
        in_channels_per_group = x.shape[1] // group

        acc = b[oc] if has_bias == 1 else 0.0

        for ic_idx in range(in_channels_per_group):
            ic = g * in_channels_per_group + ic_idx
            for kh in range(w.shape[2]):
                for kw in range(w.shape[3]):
                    ih = oh * stride_h - pad_top + kh * dil_h
                    iw = ow * stride_w - pad_left + kw * dil_w
                    if 0 <= ih < x.shape[2] and 0 <= iw < x.shape[3]:
                        acc += x[n, ic, ih, iw] * w[oc, ic_idx, kh, kw]

        if act_type == 1:
            acc = ti.max(0.0, acc)
        elif act_type == 2:
            acc = 1.0 / (1.0 + ti.exp(-acc))

        out[n, oc, oh, ow] = acc


@ti.kernel
def _ti_stem_c1_conv3x3_fused(
    x: ti.types.ndarray(dtype=ti.f32, ndim=4),
    w: ti.types.ndarray(dtype=ti.f32, ndim=4),
    b: ti.types.ndarray(dtype=ti.f32, ndim=1),
    out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    has_bias: ti.i32,
    act_type: ti.i32,
):
    """High-efficiency stem conv (Cin=1 -> Cout): caches 3x3 patch in registers and computes all Cout channels."""
    H = x.shape[2]
    W = x.shape[3]
    C_out = out.shape[1]
    for n, oh, ow in ti.ndrange(x.shape[0], H, W):
        p00, p01, p02 = 0.0, 0.0, 0.0
        p10, p11, p12 = 0.0, 0.0, 0.0
        p20, p21, p22 = 0.0, 0.0, 0.0

        if 1 <= oh < H - 1 and 1 <= ow < W - 1:
            p00 = x[n, 0, oh - 1, ow - 1]
            p01 = x[n, 0, oh - 1, ow]
            p02 = x[n, 0, oh - 1, ow + 1]
            p10 = x[n, 0, oh,     ow - 1]
            p11 = x[n, 0, oh,     ow]
            p12 = x[n, 0, oh,     ow + 1]
            p20 = x[n, 0, oh + 1, ow - 1]
            p21 = x[n, 0, oh + 1, ow]
            p22 = x[n, 0, oh + 1, ow + 1]
        else:
            for kh in ti.static(range(3)):
                for kw in ti.static(range(3)):
                    ih = oh - 1 + kh
                    iw = ow - 1 + kw
                    val = x[n, 0, ih, iw] if (0 <= ih < H and 0 <= iw < W) else 0.0
                    if kh == 0 and kw == 0: p00 = val
                    elif kh == 0 and kw == 1: p01 = val
                    elif kh == 0 and kw == 2: p02 = val
                    elif kh == 1 and kw == 0: p10 = val
                    elif kh == 1 and kw == 1: p11 = val
                    elif kh == 1 and kw == 2: p12 = val
                    elif kh == 2 and kw == 0: p20 = val
                    elif kh == 2 and kw == 1: p21 = val
                    elif kh == 2 and kw == 2: p22 = val

        for oc in range(C_out):
            acc = b[oc] if has_bias == 1 else 0.0
            acc += p00 * w[oc, 0, 0, 0] + p01 * w[oc, 0, 0, 1] + p02 * w[oc, 0, 0, 2]
            acc += p10 * w[oc, 0, 1, 0] + p11 * w[oc, 0, 1, 1] + p12 * w[oc, 0, 1, 2]
            acc += p20 * w[oc, 0, 2, 0] + p21 * w[oc, 0, 2, 1] + p22 * w[oc, 0, 2, 2]
            if act_type == 1:
                acc = ti.max(0.0, acc)
            elif act_type == 2:
                acc = 1.0 / (1.0 + ti.exp(-acc))
            out[n, oc, oh, ow] = acc


@ti.kernel
def _ti_depthwise_conv3x3_fused(
    x: ti.types.ndarray(dtype=ti.f32, ndim=4),
    w: ti.types.ndarray(dtype=ti.f32, ndim=4),
    b: ti.types.ndarray(dtype=ti.f32, ndim=1),
    out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    has_bias: ti.i32,
    act_type: ti.i32,  # 0: None, 1: ReLU, 2: Sigmoid
):
    """Unrolled 3x3 Depthwise Convolution with fused in-register activation."""
    for n, c, oh, ow in out:
        acc = b[c] if has_bias == 1 else 0.0

        for kh in ti.static(range(3)):
            for kw in ti.static(range(3)):
                ih = oh - 1 + kh
                iw = ow - 1 + kw
                if 0 <= ih < x.shape[2] and 0 <= iw < x.shape[3]:
                    acc += x[n, c, ih, iw] * w[c, 0, kh, kw]

        if act_type == 1:
            acc = ti.max(0.0, acc)
        elif act_type == 2:
            acc = 1.0 / (1.0 + ti.exp(-acc))

        out[n, c, oh, ow] = acc


@ti.kernel
def _ti_pointwise_conv1x1_tiled4_fused(
    x: ti.types.ndarray(dtype=ti.f32, ndim=4),
    w: ti.types.ndarray(dtype=ti.f32, ndim=4),
    b: ti.types.ndarray(dtype=ti.f32, ndim=1),
    out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    has_bias: ti.i32,
    act_type: ti.i32,  # 0: None, 1: ReLU, 2: Sigmoid
):
    """Channel-tiled 1x1 Pointwise Convolution reusing input channel loads across 4 output channels."""
    N = x.shape[0]
    C_in = x.shape[1]
    H = x.shape[2]
    W = x.shape[3]
    C_out = out.shape[1]
    blocks = C_out // 4

    for n, blk, oh, ow in ti.ndrange(N, blocks, H, W):
        oc0 = blk * 4
        oc1 = oc0 + 1
        oc2 = oc0 + 2
        oc3 = oc0 + 3

        acc0 = b[oc0] if has_bias == 1 else 0.0
        acc1 = b[oc1] if has_bias == 1 else 0.0
        acc2 = b[oc2] if has_bias == 1 else 0.0
        acc3 = b[oc3] if has_bias == 1 else 0.0

        for ic in range(C_in):
            val = x[n, ic, oh, ow]
            acc0 += val * w[oc0, ic, 0, 0]
            acc1 += val * w[oc1, ic, 0, 0]
            acc2 += val * w[oc2, ic, 0, 0]
            acc3 += val * w[oc3, ic, 0, 0]

        if act_type == 1:
            acc0 = ti.max(0.0, acc0)
            acc1 = ti.max(0.0, acc1)
            acc2 = ti.max(0.0, acc2)
            acc3 = ti.max(0.0, acc3)
        elif act_type == 2:
            acc0 = 1.0 / (1.0 + ti.exp(-acc0))
            acc1 = 1.0 / (1.0 + ti.exp(-acc1))
            acc2 = 1.0 / (1.0 + ti.exp(-acc2))
            acc3 = 1.0 / (1.0 + ti.exp(-acc3))

        out[n, oc0, oh, ow] = acc0
        out[n, oc1, oh, ow] = acc1
        out[n, oc2, oh, ow] = acc2
        out[n, oc3, oh, ow] = acc3

    if blocks * 4 < C_out:
        rem_start = blocks * 4
        for n, oc, oh, ow in ti.ndrange(N, (rem_start, C_out), H, W):
            acc = b[oc] if has_bias == 1 else 0.0
            for ic in range(C_in):
                acc += x[n, ic, oh, ow] * w[oc, ic, 0, 0]
            if act_type == 1:
                acc = ti.max(0.0, acc)
            elif act_type == 2:
                acc = 1.0 / (1.0 + ti.exp(-acc))
            out[n, oc, oh, ow] = acc


@ti.kernel
def _ti_simam_row_reduce_sum_and_sumsq(
    x: ti.types.ndarray(dtype=ti.f32, ndim=4),
    row_sums: ti.types.ndarray(dtype=ti.f32, ndim=4),
    row_sumsq: ti.types.ndarray(dtype=ti.f32, ndim=4)
):
    """High-efficiency parallel 1st stage row reduction for spatial mean and variance."""
    for n, c, h in ti.ndrange(x.shape[0], x.shape[1], x.shape[2]):
        s = 0.0
        sq = 0.0
        for w in range(x.shape[3]):
            v = x[n, c, h, w]
            s += v
            sq += v * v
        row_sums[n, c, h, 0] = s
        row_sumsq[n, c, h, 0] = sq


@ti.kernel
def _ti_simam_row_reduce_stage2(
    row_sums: ti.types.ndarray(dtype=ti.f32, ndim=4),
    row_sumsq: ti.types.ndarray(dtype=ti.f32, ndim=4),
    mean_out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    var_out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    total_elements: ti.f32,
    denom: ti.f32
):
    """Parallel 2nd stage reduction computing spatial mean and variance."""
    for n, c in ti.ndrange(row_sums.shape[0], row_sums.shape[1]):
        s = 0.0
        sq = 0.0
        for h in range(row_sums.shape[2]):
            s += row_sums[n, c, h, 0]
            sq += row_sumsq[n, c, h, 0]
        mean_val = s / total_elements
        mean_out[n, c, 0, 0] = mean_val
        ss = sq - (s * s) / total_elements
        var_out[n, c, 0, 0] = ti.max(0.0, ss) / denom


@ti.kernel
def _ti_simam_forward_add_fused(
    x: ti.types.ndarray(dtype=ti.f32, ndim=4),
    mean: ti.types.ndarray(dtype=ti.f32, ndim=4),
    var: ti.types.ndarray(dtype=ti.f32, ndim=4),
    residual: ti.types.ndarray(dtype=ti.f32, ndim=4),
    out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    has_residual: ti.i32,
    eps: ti.f32,
):
    """Fused SimAM Sigmoid scaling and optional residual addition in 1 kernel with pre-inverted denominator."""
    for n, c, h, w in out:
        m = mean[n, c, 0, 0]
        v = var[n, c, 0, 0]
        inv_denom = 1.0 / (4.0 * (v + eps))
        val = x[n, c, h, w]

        d = val - m
        scaled = (d * d) * inv_denom + 0.5
        sigmoid_val = 1.0 / (1.0 + ti.exp(-scaled))
        
        res = val * sigmoid_val
        if has_residual == 1:
            res += residual[n, c, h, w]
        out[n, c, h, w] = res


@ti.kernel
def _ti_binary_broadcast_4d(
    a: ti.types.ndarray(dtype=ti.f32, ndim=4),
    b: ti.types.ndarray(dtype=ti.f32, ndim=4),
    out: ti.types.ndarray(dtype=ti.f32, ndim=4),
    sa_n: ti.i32, sa_c: ti.i32, sa_h: ti.i32, sa_w: ti.i32,
    sb_n: ti.i32, sb_c: ti.i32, sb_h: ti.i32, sb_w: ti.i32,
    op_type: ti.i32,
):
    for n, c, h, w in out:
        ia_n = 0 if sa_n == 1 else n
        ia_c = 0 if sa_c == 1 else c
        ia_h = 0 if sa_h == 1 else h
        ia_w = 0 if sa_w == 1 else w

        ib_n = 0 if sb_n == 1 else n
        ib_c = 0 if sb_c == 1 else c
        ib_h = 0 if sb_h == 1 else h
        ib_w = 0 if sb_w == 1 else w

        va = a[ia_n, ia_c, ia_h, ia_w]
        vb = b[ib_n, ib_c, ib_h, ib_w]
        res = 0.0
        if op_type == 0:
            res = va + vb
        elif op_type == 1:
            res = va - vb
        elif op_type == 2:
            res = va * vb
        elif op_type == 3:
            res = va / vb
        elif op_type == 4:
            if vb == 2.0:
                res = va * va
            else:
                res = ti.abs(va) ** vb
        out[n, c, h, w] = res


@ti.kernel
def _ti_relu_4d(x: ti.types.ndarray(dtype=ti.f32, ndim=4), out: ti.types.ndarray(dtype=ti.f32, ndim=4)):
    for n, c, h, w in out:
        out[n, c, h, w] = ti.max(0.0, x[n, c, h, w])


@ti.kernel
def _ti_sigmoid_4d(x: ti.types.ndarray(dtype=ti.f32, ndim=4), out: ti.types.ndarray(dtype=ti.f32, ndim=4)):
    for n, c, h, w in out:
        out[n, c, h, w] = 1.0 / (1.0 + ti.exp(-x[n, c, h, w]))


@ti.kernel
def _ti_spatial_reduce_mean_4d(x: ti.types.ndarray(dtype=ti.f32, ndim=4), out: ti.types.ndarray(dtype=ti.f32, ndim=4)):
    for n, c in ti.ndrange(out.shape[0], out.shape[1]):
        acc = 0.0
        H = x.shape[2]
        W = x.shape[3]
        for h in range(H):
            for w in range(W):
                acc += x[n, c, h, w]
        out[n, c, 0, 0] = acc / (H * W)


# ==============================================================================
# 2. VRAM SCRATCHPAD BUFFER POOL
# ==============================================================================

class VRAMBufferPool:
    """Manages reusable device ti.ndarray allocations to eliminate VRAM alloc/free overhead."""

    def __init__(self):
        self._pool: Dict[Tuple[int, ...], List[Any]] = {}
        self._allocated_count = 0
        self._lock = threading.Lock()

    def acquire(self, shape: Tuple[int, ...]) -> Any:
        with self._lock:
            pool_list = self._pool.setdefault(shape, [])
            if pool_list:
                return pool_list.pop()
            buf = ti.ndarray(dtype=ti.f32, shape=shape)
            self._allocated_count += 1
            return buf

    def release(self, buf: Any):
        shape = tuple(buf.shape)
        with self._lock:
            self._pool.setdefault(shape, []).append(buf)

    def clear(self):
        with self._lock:
            self._pool.clear()
            self._allocated_count = 0


# ==============================================================================
# 3. HIGH-PERFORMANCE NEURAL MODEL (ONNX & PYTORCH EXECUTABLE)
# ==============================================================================

class NeuralModel:
    """High-efficiency executable neural network representation on Taichi Vision.

    Supports zero-copy GPU residency, kernel fusion, smart channel conversion,
    and standalone Ahead-of-Time (.tcm) persistence.
    """

    def __init__(
        self,
        execution_plan: List[Dict[str, Any]],
        device_weights: Dict[str, Any],
        constants: Dict[str, np.ndarray],
        input_names: List[str],
        output_names: List[str],
        expected_channels: int = 1,
        arch_name: str = "vulkan",
    ):
        self.execution_plan = execution_plan
        self.device_weights = device_weights
        self.constants = constants
        self.input_names = input_names
        self.output_names = output_names
        self.expected_channels = expected_channels
        self.arch_name = arch_name.lower().strip()
        self.pool = VRAMBufferPool()
        self._execution_lock = threading.Lock()
        self.dummy_bias_dev = ti.ndarray(dtype=ti.f32, shape=(1,))
        self._native_graph = None

    def __call__(
        self,
        image_or_tensor: Any,
        is_bgr: bool = False,
        normalize: bool = True,
        return_gpu: bool = False,
        borrowed_outputs: bool = False,
    ) -> Any:
        """Friendly callable execution.

        Args:
            image_or_tensor: NumPy ndarray, ti.ndarray, torch.Tensor, or TaichiGPUBuffer.
            is_bgr: True if 3-channel input is BGR (OpenCV standard), False if RGB.
            normalize: Auto-normalize uint8 [0..255] to float32 [0.0..1.0].
            return_gpu: If True, returns caller-owned device ti.ndarray without
                downloading to host RAM; the model will not recycle returned buffers.
            borrowed_outputs: Return device views without copies. Graph-buffer views
                are valid until the next model execution; Identity-like outputs may
                alias the supplied input. Requires return_gpu. Host inputs are
                synchronized before return so temporary input storage stays valid.
        """
        if borrowed_outputs and not return_gpu:
            raise ValueError("borrowed_outputs requires return_gpu=True")
        if borrowed_outputs and self._native_graph is None:
            raise ValueError("borrowed_outputs is supported only by the native ONNX graph")
        input_handle = image_or_tensor.handle if hasattr(image_or_tensor, "handle") \
            and hasattr(image_or_tensor, "shape") else image_or_tensor
        caller_device_input = isinstance(input_handle, ti.Ndarray)
        input_device = getattr(input_handle, "device", None)
        if borrowed_outputs and input_device is not None \
                and str(input_device).lower() not in ("cpu", "cpu:0") \
                and not caller_device_input:
            raise RuntimeError(
                "borrowed_outputs cannot import a foreign device tensor directly; "
                "convert it to a Taichi ndarray explicitly"
            )
        if self._native_graph is not None and not caller_device_input and not borrowed_outputs:
            primary_input_name = self.input_names[0] if self.input_names else "input"
            if hasattr(image_or_tensor, "cpu") and hasattr(image_or_tensor, "numpy"):
                arr = image_or_tensor.detach().cpu().numpy()
            elif hasattr(image_or_tensor, "to_numpy"):
                arr = image_or_tensor.to_numpy()
            else:
                arr = np.asarray(image_or_tensor)
            expected_shape = self._native_graph.shapes.get(primary_input_name)
            if expected_shape is not None and tuple(arr.shape) != expected_shape:
                raise ValueError(
                    f"Input '{primary_input_name}' shape mismatch: expected {expected_shape}, got {arr.shape}"
                )
            if arr.dtype != np.float32:
                arr = arr.astype(np.float32)
            inputs = {primary_input_name: np.ascontiguousarray(arr)}
            results = self.execute(inputs, return_gpu=return_gpu, borrowed_outputs=borrowed_outputs)
            primary_output_name = self.output_names[0] if self.output_names else "output"
            return results.get(primary_output_name, results)

        adapted_dev = self._validate_and_bind_input(
            image_or_tensor,
            input_name=self.input_names[0] if self.input_names else "input",
            flatten_device=borrowed_outputs,
        )
        primary_input_name = self.input_names[0] if self.input_names else "input"
        inputs = {primary_input_name: adapted_dev}

        results = self.execute(inputs, return_gpu=return_gpu, borrowed_outputs=borrowed_outputs)
        if not caller_device_input and (borrowed_outputs or not return_gpu):
            if borrowed_outputs:
                # Preserve the completion guarantee before returning a
                # temporary borrowed-input allocation to the pool.
                ti.sync()
            # Identity-like graphs may return this exact allocation. Keep it
            # caller-owned in that case; otherwise recycle the temporary input.
            if all(output is not adapted_dev for output in results.values()):
                self.pool.release(adapted_dev)
        primary_output_name = self.output_names[0] if self.output_names else "output"
        return results.get(primary_output_name, results)

    def run(
        self,
        output_names: Optional[Sequence[str]] = None,
        input_feed: Optional[Dict[str, Any]] = None,
        return_gpu: bool = False,
        borrowed_outputs: bool = False,
        **kwargs: Any,
    ) -> List[Any]:
        """Drop-in inference runner compatible with session.run(output_names, input_feed)."""
        if input_feed is None:
            input_feed = {}
        if self._native_graph is not None:
            validated_inputs = {}
            for name, data in input_feed.items():
                if hasattr(data, "to_numpy") and hasattr(data, "shape") and not isinstance(data, np.ndarray):
                    validated_inputs[name] = self._validate_and_bind_input(
                        data, input_name=name, flatten_device=borrowed_outputs
                    )
                else:
                    if hasattr(data, "cpu") and hasattr(data, "numpy"):
                        arr = data.detach().cpu().numpy()
                    elif hasattr(data, "to_numpy"):
                        arr = data.to_numpy()
                    else:
                        arr = np.asarray(data)
                    expected_shape = self._native_graph.shapes.get(name)
                    if expected_shape is not None and tuple(arr.shape) != expected_shape:
                        raise ValueError(f"Input '{name}' shape mismatch: expected {expected_shape}, got {arr.shape}")
                    if arr.dtype != np.float32:
                        arr = arr.astype(np.float32)
                    validated_inputs[name] = np.ascontiguousarray(arr)
        else:
            validated_inputs = {
                name: self._validate_and_bind_input(data, input_name=name, flatten_device=borrowed_outputs)
                for name, data in input_feed.items()
            }
        results = self.execute(validated_inputs, return_gpu=return_gpu, borrowed_outputs=borrowed_outputs)
        if output_names is None:
            return list(results.values())
        return [results.get(name) for name in output_names]

    def get_providers(self) -> List[str]:
        """Returns active execution provider info."""
        return [f"TaichiVision_{self.arch_name.upper()}ExecutionProvider"]

    def get_inputs(self) -> List[Any]:
        """Returns input tensor metadata."""
        class _InputMeta:
            def __init__(self, name: str, channels: int):
                self.name = name
                self.shape = [1, channels, None, None]
        result = [_InputMeta(name, self.expected_channels) for name in self.input_names]
        if self._native_graph is not None:
            for meta in result:
                meta.shape = list(self._native_graph.shapes[meta.name])
        return result

    def get_outputs(self) -> List[Any]:
        """Returns output tensor metadata."""
        class _OutputMeta:
            def __init__(self, name: str):
                self.name = name
        result = [_OutputMeta(name) for name in self.output_names]
        if self._native_graph is not None:
            for meta in result:
                meta.shape = list(self._native_graph.shapes[meta.name])
        return result

    def _validate_and_bind_input(
        self,
        data: Any,
        input_name: Optional[str] = None,
        flatten_device: bool = False,
    ) -> Any:
        """Validates input tensor against model contract and returns a device buffer.

        Enforces strict dimension, channel, and dtype checks without implicit color
        conversion or axis permutation. Keeps data 100% resident in Taichi device memory.
        """
        if input_name is None:
            input_name = self.input_names[0] if self.input_names else "input"

        expected_shape = None
        if self._native_graph is not None and input_name in self._native_graph.shapes:
            expected_shape = self._native_graph.shapes[input_name]

        expected_channels = self.expected_channels
        if expected_shape is not None and len(expected_shape) >= 2 and expected_shape[1] is not None:
            expected_channels = expected_shape[1]

        channel_desc = "Grayscale (1 channel)" if expected_channels == 1 else f"Multi-channel ({expected_channels} channels)"

        # Unwrap TaichiGPUBuffer if passed
        if hasattr(data, "handle") and hasattr(data, "shape"):
            data = data.handle

        # 1. Device input (ti.Ndarray)
        if hasattr(data, "to_numpy") and hasattr(data, "shape") and not isinstance(data, np.ndarray):
            if hasattr(data, "dtype") and data.dtype != ti.f32:
                raise ValueError(
                    f"Input '{input_name}' dtype mismatch: model expects ti.f32, "
                    f"but received {data.dtype}. Please cast to float32 before calling NeuralModel."
                )

            if flatten_device:
                expected_elem_count = int(np.prod(expected_shape)) if expected_shape is not None else None
                if len(data.shape) == 1 and expected_elem_count is not None and data.shape[0] == expected_elem_count:
                    return data
                raise ValueError(
                    f"Input '{input_name}': borrowed_outputs requires a flat 1D Taichi input with "
                    f"{expected_elem_count} elements, but received shape {data.shape}."
                )

            if len(data.shape) != 4:
                raise ValueError(
                    f"Input '{input_name}' dimension mismatch: model expects 4D tensor (N, C, H, W), "
                    f"but received {len(data.shape)}D tensor with shape {data.shape}. "
                    "Color conversion and dimension preprocessing must be handled outside NeuralModel."
                )

            actual_channels = data.shape[1]
            if actual_channels != expected_channels:
                raise ValueError(
                    f"Input '{input_name}' channel/color mismatch: model requires {expected_channels} channel(s) ({channel_desc}), "
                    f"but received tensor with {actual_channels} channel(s) (shape={data.shape}). "
                    "Please perform color conversion (e.g. RGB/BGR to Grayscale) before feeding into NeuralModel."
                )

            if expected_shape is not None:
                for dim_idx, (exp_d, act_d) in enumerate(zip(expected_shape, data.shape)):
                    if exp_d is not None and exp_d != act_d:
                        raise ValueError(
                            f"Input '{input_name}' shape mismatch at dimension {dim_idx}: "
                            f"expected {exp_d}, but received {act_d} (expected_shape={expected_shape}, actual={data.shape})."
                        )
            return data

        # 2. Host input (torch.Tensor, NumPy ndarray)
        if hasattr(data, "cpu") and hasattr(data, "numpy"):
            arr = data.detach().cpu().numpy()
        elif hasattr(data, "to_numpy"):
            arr = data.to_numpy()
        else:
            arr = np.asarray(data)

        if arr.dtype != np.float32:
            raise ValueError(
                f"Input '{input_name}' dtype mismatch: model expects float32 normalized tensor, "
                f"but received dtype '{arr.dtype}'. "
                "Normalization and dtype conversion must be handled outside NeuralModel."
            )

        if arr.ndim != 4:
            raise ValueError(
                f"Input '{input_name}' dimension mismatch: model expects 4D tensor (N, C, H, W), "
                f"but received {arr.ndim}D array with shape {arr.shape}. "
                "Color conversion and dimension preprocessing (e.g. HWC to NCHW) must be handled outside NeuralModel."
            )

        actual_channels = arr.shape[1]
        if actual_channels != expected_channels:
            raise ValueError(
                f"Input '{input_name}' channel/color mismatch: model requires {expected_channels} channel(s) ({channel_desc}), "
                f"but received array with {actual_channels} channel(s) (shape={arr.shape}). "
                "Please perform color conversion (e.g. RGB/BGR to Grayscale) before feeding into NeuralModel."
            )

        if expected_shape is not None:
            for dim_idx, (exp_d, act_d) in enumerate(zip(expected_shape, arr.shape)):
                if exp_d is not None and exp_d != act_d:
                    raise ValueError(
                        f"Input '{input_name}' shape mismatch at dimension {dim_idx}: "
                        f"expected {exp_d}, but received {act_d} (expected_shape={expected_shape}, actual={arr.shape})."
                    )

        # Upload host data ONCE to device memory
        arr = np.ascontiguousarray(arr, dtype=np.float32)
        if flatten_device:
            dev_buf = self.pool.acquire((arr.size,))
            dev_buf.from_numpy(arr.reshape(-1))
        else:
            dev_buf = self.pool.acquire(arr.shape)
            dev_buf.from_numpy(arr)
        return dev_buf

    # Backward compatibility alias
    _adapt_input = _validate_and_bind_input

    def execute(
        self,
        inputs: Dict[str, Any],
        return_gpu: bool = False,
        borrowed_outputs: bool = False,
    ) -> Dict[str, Any]:
        """Executes the fused graph with 100% VRAM device residency."""
        if self._native_graph is not None:
            return self._native_graph.run(
                inputs, return_gpu=return_gpu, borrowed_outputs=borrowed_outputs
            )
        if borrowed_outputs:
            raise ValueError("borrowed_outputs is supported only by the native ONNX graph")
        with self._execution_lock:
            return self._execute_legacy_graph(inputs, return_gpu)

    def _execute_legacy_graph(
        self, inputs: Dict[str, Any], return_gpu: bool = False
    ) -> Dict[str, Any]:
        # Dispatch general ONNX graphs (attention, pooling, resizing) to high-speed general runner
        is_general_graph = any(
            step.get("op") in (
                "AveragePool", "Resize", "ConvTranspose", "Gelu", "Softplus",
                "Slice", "Concat", "Reshape", "DmlFusedConv"
            )
            for step in self.execution_plan
        )
        if is_general_graph:
            raise RuntimeError("General graph requires a validated native plan; reload using onnx(). PyTorch fallback is disabled.")

        device_tensors: Dict[str, Any] = {}
        allocated_buffers: List[Any] = []

        def get_tensor(name: str):
            if name in device_tensors:
                return device_tensors[name]
            if name in self.device_weights:
                return self.device_weights[name]
            if name in self.constants:
                arr = self.constants[name]
                ti_c = ti.ndarray(dtype=ti.f32, shape=arr.shape if arr.ndim > 0 else (1,))
                ti_c.from_numpy(arr if arr.ndim > 0 else arr.reshape(1,))
                self.device_weights[name] = ti_c
                return ti_c
            return None

        # 1. Bind inputs
        for name, data in inputs.items():
            if hasattr(data, "to_numpy") and hasattr(data, "shape") and not isinstance(data, np.ndarray):
                device_tensors[name] = data
            else:
                arr = np.ascontiguousarray(data, dtype=np.float32)
                ti_buf = self.pool.acquire(arr.shape)
                ti_buf.from_numpy(arr)
                device_tensors[name] = ti_buf
                allocated_buffers.append(ti_buf)

        # 2. Execute plan
        for step in self.execution_plan:
            op = step["op"]
            out_name = step["output"]

            if op == "Constant":
                continue

            if op == "Identity":
                src = get_tensor(step["node"].input[0])
                device_tensors[out_name] = src
                continue

            if op == "FUSED_CONV":
                node = step["node"]
                x_dev = get_tensor(node.input[0])
                w_dev = get_tensor(node.input[1])
                has_bias = len(node.input) > 2 and bool(node.input[2])
                b_dev = get_tensor(node.input[2]) if has_bias else self.dummy_bias_dev

                pads = [0, 0, 0, 0]
                strides = [1, 1]
                dilations = [1, 1]
                group = 1
                for attr in node.attribute:
                    if attr.name == "pads": pads = list(attr.ints)
                    elif attr.name == "strides": strides = list(attr.ints)
                    elif attr.name == "dilations": dilations = list(attr.ints)
                    elif attr.name == "group": group = int(attr.i)

                N, C_in, H, W = x_dev.shape
                C_out, _, kH, kW = w_dev.shape
                out_H = (H + pads[0] + pads[2] - dilations[0] * (kH - 1) - 1) // strides[0] + 1
                out_W = (W + pads[1] + pads[3] - dilations[1] * (kW - 1) - 1) // strides[1] + 1

                out_dev = self.pool.acquire((N, C_out, out_H, out_W))
                allocated_buffers.append(out_dev)

                if C_in == 1 and kH == 3 and kW == 3 and strides == [1, 1] and pads == [1, 1, 1, 1] and group == 1:
                    _ti_stem_c1_conv3x3_fused(x_dev, w_dev, b_dev, out_dev, 1 if has_bias else 0, step["act_type"])
                elif group == C_in and C_in == C_out and kH == 3 and kW == 3 and strides == [1, 1] and pads == [1, 1, 1, 1]:
                    _ti_depthwise_conv3x3_fused(x_dev, w_dev, b_dev, out_dev, 1 if has_bias else 0, step["act_type"])
                elif kH == 1 and kW == 1 and group == 1 and strides == [1, 1] and pads == [0, 0, 0, 0]:
                    _ti_pointwise_conv1x1_tiled4_fused(x_dev, w_dev, b_dev, out_dev, 1 if has_bias else 0, step["act_type"])
                else:
                    _ti_conv2d_generic(
                        x_dev, w_dev, b_dev, out_dev,
                        pads[0], pads[1], strides[0], strides[1], dilations[0], dilations[1],
                        group, 1 if has_bias else 0, step["act_type"]
                    )
                device_tensors[out_name] = out_dev

            elif op == "FUSED_SIMAM":
                x_dev = get_tensor(step["input"])
                has_res = 1 if step["has_residual"] else 0
                res_dev = get_tensor(step["residual"]) if step["has_residual"] else x_dev

                row_sums_dev = self.pool.acquire((x_dev.shape[0], x_dev.shape[1], x_dev.shape[2], 1))
                row_sumsq_dev = self.pool.acquire((x_dev.shape[0], x_dev.shape[1], x_dev.shape[2], 1))
                mean_dev = self.pool.acquire((x_dev.shape[0], x_dev.shape[1], 1, 1))
                var_dev = self.pool.acquire((x_dev.shape[0], x_dev.shape[1], 1, 1))
                out_dev = self.pool.acquire(x_dev.shape)

                tot_el = float(x_dev.shape[2] * x_dev.shape[3])
                denom = max(1.0, tot_el - 1.0)
                _ti_simam_row_reduce_sum_and_sumsq(x_dev, row_sums_dev, row_sumsq_dev)
                _ti_simam_row_reduce_stage2(row_sums_dev, row_sumsq_dev, mean_dev, var_dev, tot_el, denom)
                _ti_simam_forward_add_fused(x_dev, mean_dev, var_dev, res_dev, out_dev, has_res, step["eps"])
                
                # Immediate release of reduction scratchpads to maximize L2 cache hit rate
                self.pool.release(row_sums_dev)
                self.pool.release(row_sumsq_dev)
                self.pool.release(mean_dev)
                self.pool.release(var_dev)

                allocated_buffers.append(out_dev)
                device_tensors[out_name] = out_dev

            elif op in ("Add", "Sub", "Mul", "Div", "Pow"):
                node = step["node"]
                op_code = {"Add": 0, "Sub": 1, "Mul": 2, "Div": 3, "Pow": 4}[op]
                a_dev = get_tensor(node.input[0])
                b_dev = get_tensor(node.input[1])
                a_is_scalar = tuple(a_dev.shape) == (1,)
                b_is_scalar = tuple(b_dev.shape) == (1,)

                if a_is_scalar and len(b_dev.shape) == 4:
                    out_dev = self.pool.acquire(b_dev.shape)
                    allocated_buffers.append(out_dev)
                    _ti_binary_scalar_4d(a_dev, b_dev, out_dev, op_code, 1)
                elif b_is_scalar and len(a_dev.shape) == 4:
                    out_dev = self.pool.acquire(a_dev.shape)
                    allocated_buffers.append(out_dev)
                    _ti_binary_scalar_4d(a_dev, b_dev, out_dev, op_code, 0)
                elif len(a_dev.shape) == 4 and len(b_dev.shape) == 4:
                    out_shape = [max(a_dev.shape[k], b_dev.shape[k]) for k in range(4)]
                    out_dev = self.pool.acquire(tuple(out_shape))
                    allocated_buffers.append(out_dev)
                    _ti_binary_broadcast_4d(
                        a_dev, b_dev, out_dev,
                        a_dev.shape[0], a_dev.shape[1], a_dev.shape[2], a_dev.shape[3],
                        b_dev.shape[0], b_dev.shape[1], b_dev.shape[2], b_dev.shape[3],
                        op_code
                    )
                else:
                    raise UnsupportedONNXOperatorError(
                        f"ONNX {op} executor received unsupported runtime shapes "
                        f"{tuple(a_dev.shape)} and {tuple(b_dev.shape)}"
                    )
                device_tensors[out_name] = out_dev

            elif op == "Relu":
                x_dev = get_tensor(step["node"].input[0])
                out_dev = self.pool.acquire(x_dev.shape)
                allocated_buffers.append(out_dev)
                _ti_relu_4d(x_dev, out_dev)
                device_tensors[out_name] = out_dev

            elif op == "Sigmoid":
                x_dev = get_tensor(step["node"].input[0])
                out_dev = self.pool.acquire(x_dev.shape)
                allocated_buffers.append(out_dev)
                _ti_sigmoid_4d(x_dev, out_dev)
                device_tensors[out_name] = out_dev

            elif op == "Conv":
                node = step["node"]
                x_dev = get_tensor(node.input[0])
                w_dev = get_tensor(node.input[1])
                has_bias = len(node.input) > 2 and bool(node.input[2])
                b_dev = get_tensor(node.input[2]) if has_bias else self.dummy_bias_dev
                pads = [0, 0, 0, 0]
                strides = [1, 1]
                dilations = [1, 1]
                group = 1
                for attr in node.attribute:
                    if attr.name == "pads": pads = list(attr.ints)
                    elif attr.name == "strides": strides = list(attr.ints)
                    elif attr.name == "dilations": dilations = list(attr.ints)
                    elif attr.name == "group": group = int(attr.i)

                N, C_in, H, W = x_dev.shape
                C_out, _, kH, kW = w_dev.shape
                out_H = (H + pads[0] + pads[2] - dilations[0] * (kH - 1) - 1) // strides[0] + 1
                out_W = (W + pads[1] + pads[3] - dilations[1] * (kW - 1) - 1) // strides[1] + 1
                out_dev = self.pool.acquire((N, C_out, out_H, out_W))
                allocated_buffers.append(out_dev)
                _ti_conv2d_generic(
                    x_dev, w_dev, b_dev, out_dev,
                    pads[0], pads[1], strides[0], strides[1], dilations[0], dilations[1],
                    group, 1 if has_bias else 0, 0
                )
                device_tensors[out_name] = out_dev

            elif op == "ReduceMean":
                x_dev = get_tensor(step["node"].input[0])
                out_dev = self.pool.acquire((x_dev.shape[0], x_dev.shape[1], 1, 1))
                allocated_buffers.append(out_dev)
                _ti_spatial_reduce_mean_4d(x_dev, out_dev)
                device_tensors[out_name] = out_dev

        # 3. Readback final outputs
        results = {}
        for name in self.output_names:
            out_buf = device_tensors[name]
            if return_gpu:
                results[name] = out_buf
            else:
                results[name] = out_buf.to_numpy()

        # 4. Recycle intermediates, but transfer returned GPU outputs out of
        #    the pool so a later invocation cannot overwrite caller-owned data.
        returned_buffer_ids = (
            {id(output) for output in results.values()} if return_gpu else set()
        )
        for buf in allocated_buffers:
            if id(buf) not in returned_buffer_ids:
                self.pool.release(buf)

        return results

    def _execute_general_graph(self, inputs: Dict[str, Any], return_gpu: bool = False) -> Dict[str, Any]:
        """Compatibility entry point for the validated native executor."""
        if self._native_graph is None:
            raise RuntimeError("Reload the ONNX graph to construct a validated native plan")
        return self._native_graph.run(inputs, return_gpu=return_gpu)

    def save_tcm(self, output_path: Union[str, Path]):
        """Exports the model to a standalone Ahead-of-Time (.tcm) archive.

        The exported .tcm can be loaded without requiring PyTorch or ONNX Runtime.
        """
        export_neural_tcm(self, output_path)


# ==============================================================================
# 4. TCM SERIALIZATION & DESERIALIZATION ENGINE
# ==============================================================================

def export_neural_tcm(model: NeuralModel, output_path: Union[str, Path]):
    """Packages a NeuralModel into a self-contained .tcm zip archive."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if model._native_graph is not None:
        # Keep the original graph/typed constants so reload repeats admission.
        # This archive needs the ONNX parser, but never ONNX Runtime or torch.
        with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("tcm_manifest.json", json.dumps({
                "magic": "PIXEL_REFINE_TCM", "format_version": 2,
                "type": "native_graph_source", "target_backend": model.arch_name,
            }))
            archive.writestr("native_graph.onnx", model._native_onnx_bytes)
        return

    # 1. Prepare weights dictionary as numpy arrays
    weights_np = {}
    for name, ti_arr in model.device_weights.items():
        weights_np[name] = ti_arr.to_numpy()

    # 2. Serialize execution plan (stripping non-serializable node objects)
    serializable_plan = []
    for step in model.execution_plan:
        step_copy = {k: v for k, v in step.items() if k != "node"}
        if "node" in step:
            node = step["node"]
            step_copy["node_meta"] = {
                "op_type": node.op_type,
                "input": list(node.input),
                "output": list(node.output),
                "attributes": {
                    attr.name: list(attr.ints) if attr.ints else (
                        int(attr.i) if attr.type == 2 else float(attr.f)
                    )
                    for attr in node.attribute
                }
            }
        serializable_plan.append(step_copy)

    # 3. Build TCM manifest
    manifest = {
        "magic": "PIXEL_REFINE_TCM",
        "format_version": 1,
        "type": "neural_engine_module",
        "target_backend": model.arch_name,
        "input_names": model.input_names,
        "output_names": model.output_names,
        "expected_channels": model.expected_channels,
        "created_timestamp": time.time(),
    }

    # 4. Write zip archive
    with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("tcm_manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("graph.json", json.dumps(serializable_plan, indent=2))
        
        # Save weights
        buf = io.BytesIO()
        np.savez_compressed(buf, **weights_np)
        zf.writestr("weights.npz", buf.getvalue())

        # Save constants
        if model.constants:
            buf_c = io.BytesIO()
            np.savez_compressed(buf_c, **model.constants)
            zf.writestr("constants.npz", buf_c.getvalue())

    print(f"[Taichi AOT] Model successfully packaged to .tcm archive: {out_file} ({out_file.stat().st_size / 1024:.1f} KB)")


def load_neural_tcm(tcm_path: Union[str, Path], arch: str = "auto") -> NeuralModel:
    """Loads a NeuralModel directly from a .tcm archive (Zero PyTorch / ONNX dependency)."""
    tcm_file = Path(tcm_path)
    if not tcm_file.exists():
        raise FileNotFoundError(f"TCM file not found: {tcm_file}")

    with zipfile.ZipFile(tcm_file, "r") as zf:
        manifest = json.loads(zf.read("tcm_manifest.json").decode("utf-8"))
        if manifest.get("magic") != "PIXEL_REFINE_TCM":
            raise ValueError("Invalid neural archive magic")
        if manifest.get("type") == "native_graph_source":
            if manifest.get("format_version") != 2:
                raise ValueError("Unsupported neural archive version")
            return onnx(zf.read("native_graph.onnx"), backend=arch)
        target_arch = _resolve_backend(arch)
        _ensure_taichi_initialized(target_arch)
        raw_plan = json.loads(zf.read("graph.json").decode("utf-8"))
        
        # Load weights
        weights_bytes = io.BytesIO(zf.read("weights.npz"))
        weights_npz = np.load(weights_bytes)
        device_weights = {}
        for k in weights_npz.files:
            arr = weights_npz[k]
            ti_arr = ti.ndarray(dtype=ti.f32, shape=arr.shape if arr.ndim > 0 else (1,))
            ti_arr.from_numpy(arr if arr.ndim > 0 else arr.reshape(1,))
            device_weights[k] = ti_arr

        # Load constants
        constants = {}
        if "constants.npz" in zf.namelist():
            c_bytes = io.BytesIO(zf.read("constants.npz"))
            c_npz = np.load(c_bytes)
            for k in c_npz.files:
                constants[k] = c_npz[k]

    # Reconstruct execution plan with lightweight MockNode
    class _MockNode:
        def __init__(self, meta):
            self.op_type = meta.get("op_type", "")
            self.input = meta.get("input", [])
            self.output = meta.get("output", [])
            attrs = []
            for k, v in meta.get("attributes", {}).items():
                class _Attr:
                    pass
                a = _Attr()
                a.name = k
                if isinstance(v, list): a.ints = v
                elif isinstance(v, int): a.i = v; a.type = 2
                elif isinstance(v, float): a.f = v; a.type = 1
                attrs.append(a)
            self.attribute = attrs

    execution_plan = []
    for step in raw_plan:
        step_obj = dict(step)
        if "node_meta" in step:
            step_obj["node"] = _MockNode(step["node_meta"])
        execution_plan.append(step_obj)

    print(f"[Taichi AOT] Loaded .tcm model ({manifest.get('type')}) on {target_arch}")
    return NeuralModel(
        execution_plan=execution_plan,
        device_weights=device_weights,
        constants=constants,
        input_names=manifest.get("input_names", ["input"]),
        output_names=manifest.get("output_names", ["output"]),
        expected_channels=manifest.get("expected_channels", 1),
        arch_name=str(target_arch).split(".")[-1],
    )


# ==============================================================================
# 5. PUBLIC FACTORIES: taichi_aot.onnx & taichi_aot.pytorch
# ==============================================================================

def _resolve_backend(arch_name: str) -> Any:
    name = arch_name.lower().strip()
    if name in ("auto", "default"):
        # Default to Vulkan for high-speed mobile/desktop GPU, fallback to CUDA or CPU
        return ti.vulkan
    mapping = {
        "vulkan": ti.vulkan, "vk": ti.vulkan,
        "cuda": ti.cuda,
        "cpu": ti.cpu, "x64": ti.cpu, "x86_64": ti.cpu,
        "opengl": ti.opengl, "gl": ti.opengl
    }
    arch = mapping.get(name)
    if arch is None:
        raise ValueError(f"Unsupported backend {arch_name}; choose vulkan, cuda, cpu, or opengl")
    return arch


_INITIALIZED_ARCH = None
_OPENGL_CONTEXT_INFO = None


def _get_opengl_context_info() -> Dict[str, Optional[str]]:
    """Read the renderer attached to the current native OpenGL context."""
    if os.name == "nt":
        import ctypes

        gl = ctypes.WinDLL("opengl32", use_last_error=True)
        gl.wglGetCurrentContext.restype = ctypes.c_void_p
        context = gl.wglGetCurrentContext()
        if not context:
            return {"context": None, "vendor": None, "renderer": None, "version": None}
        gl.glGetString.argtypes = [ctypes.c_uint]
        gl.glGetString.restype = ctypes.c_char_p

        def read_string(key):
            raw = gl.glGetString(key)
            return raw.decode("utf-8", errors="replace") if raw else None

        return {
            "context": hex(context),
            "vendor": read_string(0x1F00),
            "renderer": read_string(0x1F01),
            "version": read_string(0x1F02),
        }
    try:
        from OpenGL import GL
        def read_string(key):
            raw = GL.glGetString(key)
            return raw.decode("utf-8", errors="replace") if raw else None
        return {
            "context": "current",
            "vendor": read_string(GL.GL_VENDOR),
            "renderer": read_string(GL.GL_RENDERER),
            "version": read_string(GL.GL_VERSION),
        }
    except Exception as exc:
        return {"context": None, "vendor": None, "renderer": None,
                "version": None, "error": str(exc)}


def _validate_opengl_context(info: Dict[str, Optional[str]], expected_vendor: str) -> None:
    if not expected_vendor:
        return
    actual = " ".join(value or "" for value in (info.get("vendor"), info.get("renderer"))).strip()
    if not actual or expected_vendor.lower() not in actual.lower():
        raise RuntimeError(
            "Taichi OpenGL renderer mismatch: requested "
            f"{expected_vendor!r}, active renderer is {actual or 'unavailable'!r}. "
            "The requested GPU was not selected; no CPU fallback was attempted."
        )

def _ensure_taichi_initialized(arch: Any):
    global _INITIALIZED_ARCH, _OPENGL_CONTEXT_INFO
    if ti.lang.impl.get_runtime().prog is not None:
        active = ti.lang.impl.current_cfg().arch
        if active != arch:
            raise RuntimeError(f"Taichi already initialized on {active}; requested {arch}. Use a separate process.")
    else:
        ti.init(arch=arch, enable_fallback=False, fast_math=False)
    if arch == ti.opengl:
        _OPENGL_CONTEXT_INFO = _get_opengl_context_info()
        expected_vendor = (
            os.environ.get("OPENGL_EXPECTED_VENDOR")
            or os.environ.get("PIXEL_REFINE_TARGET_VENDOR")
            or os.environ.get("TARGET_VENDOR")
            or ""
        ).strip()
        _validate_opengl_context(_OPENGL_CONTEXT_INFO, expected_vendor)
    _INITIALIZED_ARCH = arch


def onnx(
    model_source: Union[str, Path, bytes],
    backend: str = "auto",
    channels: Union[int, str] = "auto",
    enable_fusion: bool = True,
) -> NeuralModel:
    """Loads an ONNX model natively into Taichi AOT without offline conversion.

    Args:
        model_source: Path to the .onnx file, or serialized ONNX bytes.
        backend: "auto", "vulkan", "cuda", "cpu", or "opengl".
        channels: Expected input channels (1 for grayscale, 3 for RGB, or "auto").
        enable_fusion: Enable kernel fusion for the legacy basic-operator path.
    """
    model_path = None if isinstance(model_source, bytes) else Path(model_source)
    if model_path is not None and not model_path.exists():
        raise FileNotFoundError(f"ONNX model not found: {model_path}")

    # Check if actually a .tcm archive
    if model_path is not None and model_path.suffix.lower() == ".tcm":
        return load_neural_tcm(model_path, arch=backend)

    import onnx as onnx_lib
    from onnx import numpy_helper

    onnx_model = (onnx_lib.load_model_from_string(model_source) if model_path is None
                  else onnx_lib.load(str(model_path)))
    graph = onnx_model.graph

    target_arch = _resolve_backend(backend)
    native_graph = None
    if any(n.op_type in ("AveragePool", "Resize", "ConvTranspose", "Gelu", "Softplus",
                         "Slice", "Concat", "Reshape", "DmlFusedConv", "FusedConv",
                         "SpaceToDepth", "Transpose", "Split") for n in graph.node):
        from .onnx_native_graph import NativeGraph
        # Validate before device initialization; unsupported operators fail closed.
        native_graph = NativeGraph(
            graph,
            onnx_model.opset_import,
            enable_conv_gelu_fusion=True,
            enable_concat_gather=True,
            enable_weightnet_gate_fusion=True,
            enable_mul_clip_fusion=True,
            enable_weightnet_sigmoid_product_clip_fusion=True,
            enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
            enable_weightnet_stats_tanh_fusion=True,
            enable_weightnet_stats_tanh_algebraic_simplification=True,
            enable_constant_pow2_mul_lowering=True,
            enable_weightnet_pow2_reduce_mean_fusion=(target_arch == ti.cuda),
            enable_weightnet_full_range_slice_alias=True,
            enable_weightnet_concat_conv_gelu_fusion=True,
            enable_weightnet_conv_transpose_mul_clip_fusion=True,
            enable_weightnet_abs_conv_fusion=True,
            enable_weightnet_pool_abs_concat_fusion=True,
            enable_weightnet_fused_heads_and_gate_fusion=True,
            enable_weightnet_phase_gate_concat23_fusion=True,
        )
    _ensure_taichi_initialized(target_arch)
    if native_graph is not None:
        native_graph.backend = str(target_arch).split(".")[-1].lower()

    # Upload weights to VRAM
    device_weights = {}
    for init in graph.initializer:
        if native_graph is not None:
            continue
        arr = numpy_helper.to_array(init).astype(np.float32)
        ti_arr = ti.ndarray(dtype=ti.f32, shape=arr.shape if arr.ndim > 0 else (1,))
        ti_arr.from_numpy(arr if arr.ndim > 0 else arr.reshape(1,))
        device_weights[init.name] = ti_arr

    # Constants
    constants = {}
    for node in graph.node:
        if node.op_type == "Constant":
            for attr in node.attribute:
                if attr.name == "value":
                    constants[node.output[0]] = numpy_helper.to_array(attr.t)

    initializer_names = {v.name for v in graph.initializer}
    input_names = [inp.name for inp in graph.input if inp.name not in initializer_names]
    output_names = [out.name for out in graph.output]

    # Detect expected input channels
    expected_c = 1
    if channels != "auto":
        expected_c = int(channels)
    else:
        for inp in graph.input:
            if inp.name in input_names:
                try:
                    shape = [dim.dim_value for dim in inp.type.tensor_type.shape.dim]
                    if len(shape) >= 2 and shape[1] > 0:
                        expected_c = shape[1]
                except Exception:
                    pass

    # Compile fused execution plan
    plan = _compile_fused_graph(graph, enable_fusion=enable_fusion)

    model = NeuralModel(
        execution_plan=plan,
        device_weights=device_weights,
        constants=constants,
        input_names=input_names,
        output_names=output_names,
        expected_channels=expected_c,
        arch_name=str(target_arch).split(".")[-1],
    )
    model._native_graph = native_graph
    if native_graph is not None:
        model._native_onnx_bytes = onnx_model.SerializeToString()
    return model


def pytorch(
    model_or_checkpoint: Union[str, Path, Any],
    model_def: Optional[Any] = None,
    backend: str = "auto",
    channels: Union[int, str] = "auto",
    enable_fusion: bool = True,
    sample_input_shape: Tuple[int, ...] = (1, 1, 256, 256),
) -> NeuralModel:
    """Loads a PyTorch checkpoint (.pth/.pt) or nn.Module natively into Taichi AOT.

    Args:
        model_or_checkpoint: Path to .pth file or a torch.nn.Module instance.
        model_def: Optional model architecture instance if checkpoint only contains state_dict.
        backend: "auto", "vulkan", "cuda", "cpu", or "opengl".
        channels: Expected input channels (1, 3, or "auto").
        enable_fusion: Enable automatic kernel fusion pass.
        sample_input_shape: Example tensor shape for tracing.
    """
    import torch

    target_arch = _resolve_backend(backend)
    _ensure_taichi_initialized(target_arch)

    # 1. Resolve nn.Module
    if isinstance(model_or_checkpoint, (str, Path)):
        ckpt_path = Path(model_or_checkpoint)
        if ckpt_path.suffix.lower() == ".tcm":
            return load_neural_tcm(ckpt_path, arch=backend)

        if not ckpt_path.exists():
            raise FileNotFoundError(f"PyTorch checkpoint not found: {ckpt_path}")

        raw_obj = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
        if isinstance(raw_obj, torch.nn.Module):
            model = raw_obj
        else:
            state_dict = raw_obj.get("state_dict", raw_obj.get("model_state_dict", raw_obj))
            if model_def is None:
                # Try auto-detecting known project models
                try:
                    from test_algorithm.export_nano_burst_onnx import StudentNanoBurstNet, load_checkpoint
                    model_inst = StudentNanoBurstNet()
                    load_checkpoint(model_inst, str(ckpt_path))
                    model = model_inst.encoder
                except Exception as e:
                    raise ValueError(
                        f"Checkpoint contains state_dict only. Please pass model_def=<your_module> to taichi_aot.pytorch(): {e}"
                    )
            else:
                model = model_def
                model.load_state_dict(state_dict, strict=False)
    else:
        model = model_or_checkpoint

    model.eval()

    # 2. Trace to in-memory ONNX representation
    dummy_in = torch.ones(sample_input_shape, dtype=torch.float32)
    buf = io.BytesIO()
    torch.onnx.export(
        model, (dummy_in,), buf,
        opset_version=17,
        input_names=["input"],
        output_names=["output"],
        do_constant_folding=True
    )
    buf.seek(0)

    return onnx(buf.read(), backend=backend, channels=channels, enable_fusion=enable_fusion)


# ==============================================================================
# 6. GRAPH REWRITER PASS: AUTOMATIC KERNEL FUSION
# ==============================================================================

def _compile_fused_graph(graph: Any, enable_fusion: bool = True) -> List[Dict[str, Any]]:
    active_nodes = [n for n in graph.node if n.op_type != "Constant"]
    if not enable_fusion:
        return [{"op": n.op_type, "node": n, "output": n.output[0]} for n in active_nodes]

    plan = []
    i = 0
    N = len(active_nodes)
    fused_count = 0

    while i < N:
        node = active_nodes[i]

        # 1. SimAM Attention Block Fusion Pattern:
        # Pattern A (ONNX export with ReduceSum -> Div): 12 nodes
        if (node.op_type == "ReduceMean" and i + 11 < N and
            [m.op_type for m in active_nodes[i:i+12]] == [
                'ReduceMean', 'Sub', 'Pow', 'ReduceSum', 'Div', 'Add',
                'Mul', 'Div', 'Add', 'Sigmoid', 'Mul', 'Add'
            ]):
            
            input_tensor = node.input[0]
            final_add_node = active_nodes[i+11]
            mul_node = active_nodes[i+10]
            
            if final_add_node.input[0] == mul_node.output[0]:
                residual_tensor = final_add_node.input[1]
            else:
                residual_tensor = final_add_node.input[0]

            plan.append({
                "op": "FUSED_SIMAM",
                "input": input_tensor,
                "residual": residual_tensor,
                "has_residual": True,
                "output": final_add_node.output[0],
                "eps": 1e-4,
            })
            fused_count += 12
            i += 12
            continue

        # Pattern B (PyTorch traced with ReduceMean): 11 nodes
        if (node.op_type == "ReduceMean" and i + 10 < N and
            [m.op_type for m in active_nodes[i:i+11]] == [
                'ReduceMean', 'Sub', 'Pow', 'ReduceMean', 'Add',
                'Mul', 'Div', 'Add', 'Sigmoid', 'Mul', 'Add'
            ]):
            
            input_tensor = node.input[0]
            final_add_node = active_nodes[i+10]
            mul_node = active_nodes[i+9]
            
            if final_add_node.input[0] == mul_node.output[0]:
                residual_tensor = final_add_node.input[1]
            else:
                residual_tensor = final_add_node.input[0]

            plan.append({
                "op": "FUSED_SIMAM",
                "input": input_tensor,
                "residual": residual_tensor,
                "has_residual": True,
                "output": final_add_node.output[0],
                "eps": 1e-4,
            })
            fused_count += 11
            i += 11
            continue

        # 2. Conv + Relu / Sigmoid Fusion
        if node.op_type == "Conv" and i + 1 < N and active_nodes[i+1].op_type in ("Relu", "Sigmoid"):
            next_node = active_nodes[i+1]
            if next_node.input[0] == node.output[0]:
                act_type = 1 if next_node.op_type == "Relu" else 2
                plan.append({
                    "op": "FUSED_CONV",
                    "node": node,
                    "act_type": act_type,
                    "output": next_node.output[0],
                })
                fused_count += 2
                i += 2
                continue

        # Fallback single node
        plan.append({"op": node.op_type, "node": node, "output": node.output[0]})
        i += 1

    return plan
