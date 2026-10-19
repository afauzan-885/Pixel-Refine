"""Focused CPU-JIT parity tests for the experimental Mul -> Clip kernel."""

import json
import os
import statistics
import time

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
import onnxruntime as ort
import pytest
import taichi as ti

from taichi_vision.taichi_aot.fused_mul_clip import (
    _fused_mul_clip_kernel,
    fused_mul_clip,
)


@ti.kernel
def _mul_reference(lhs: ti.types.ndarray(ti.f32, 1),
                   rhs: ti.types.ndarray(ti.f32, 1),
                   product: ti.types.ndarray(ti.f32, 1)):
    for index in product:
        product[index] = lhs[index] * rhs[index]


@ti.kernel
def _clip_reference(product: ti.types.ndarray(ti.f32, 1),
                    output: ti.types.ndarray(ti.f32, 1),
                    low: ti.f32, high: ti.f32):
    for index in output:
        value = product[index]
        if value != value:
            output[index] = value
        else:
            output[index] = ti.min(ti.max(value, low), high)


@pytest.fixture(scope="module", autouse=True)
def cpu_runtime():
    arch = ti.cuda if os.environ.get("PIXEL_REFINE_MUL_CLIP_CUDA_BENCH") == "1" else ti.cpu
    ti.init(arch=arch, fast_math=False, enable_fallback=False)
    yield
    ti.sync()


def _taichi_array(values):
    values = np.ascontiguousarray(values, dtype=np.float32).reshape(-1)
    array = ti.ndarray(ti.f32, shape=(values.size,))
    array.from_numpy(values)
    return array


def _assert_fp32_equal_with_nan(actual, expected):
    actual = np.asarray(actual, dtype=np.float32).reshape(-1)
    expected = np.asarray(expected, dtype=np.float32).reshape(-1)
    np.testing.assert_array_equal(np.isnan(actual), np.isnan(expected))
    finite_or_inf = ~np.isnan(expected)
    np.testing.assert_array_equal(
        actual[finite_or_inf].view(np.uint32),
        expected[finite_or_inf].view(np.uint32),
    )


def _ort_mul_clip(lhs, rhs, low, high):
    logical_shape = list(lhs.shape)
    graph = helper.make_graph(
        [
            helper.make_node("Mul", ["lhs", "rhs"], ["product"]),
            helper.make_node("Clip", ["product", "low", "high"], ["output"]),
        ],
        "mul_clip_reference",
        [
            helper.make_tensor_value_info("lhs", TensorProto.FLOAT, logical_shape),
            helper.make_tensor_value_info("rhs", TensorProto.FLOAT, logical_shape),
        ],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, logical_shape)],
        initializer=[
            numpy_helper.from_array(np.asarray(low, dtype=np.float32), "low"),
            numpy_helper.from_array(np.asarray(high, dtype=np.float32), "high"),
        ],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
    model.ir_version = min(model.ir_version, 10)
    session = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"]
    )
    return session.run(None, {"lhs": lhs, "rhs": rhs})[0]


def _run_kernel(lhs_values, rhs_values, low=0.0, high=1.0):
    lhs = _taichi_array(lhs_values)
    rhs = _taichi_array(rhs_values)
    output = ti.ndarray(ti.f32, shape=lhs.shape)
    fused_mul_clip(lhs, rhs, output, low, high)
    return output.to_numpy()


@pytest.mark.parametrize(
    ("profile", "shape", "rhs_range"),
    [
        ("gpu512_mul5_clip2", (1, 1, 127, 127), (0.0, 1.0)),
        ("gpu1024_mul5_clip2", (1, 1, 255, 255), (0.0, 1.0)),
        ("gpu512_mul6_clip3", (1, 1, 512, 512), (1.1064, 5000.0)),
        ("gpu1024_mul6_clip3", (1, 1, 1024, 1024), (1.1064, 5000.0)),
    ],
)
def test_bundle_candidate_shapes_fp32_parity_with_numpy_and_ort(
    profile, shape, rhs_range
):
    rng = np.random.default_rng(sum(shape) + len(profile))
    lhs = rng.uniform(0.0, 1.0, size=shape).astype(np.float32)
    rhs = rng.uniform(*rhs_range, size=shape).astype(np.float32)
    with np.errstate(invalid="ignore", over="ignore"):
        sequential = np.clip(np.multiply(lhs, rhs), np.float32(0.0), np.float32(1.0))
    ort_result = _ort_mul_clip(lhs, rhs, 0.0, 1.0)
    actual = _run_kernel(lhs, rhs)

    _assert_fp32_equal_with_nan(ort_result, sequential)
    _assert_fp32_equal_with_nan(actual, sequential)


def test_nan_infinity_negative_and_signed_zero_match_numpy_and_ort():
    lhs = np.array(
        [0.0, 1.0, -0.0, 1.0, -1.0, np.inf, 0.0, np.nan], dtype=np.float32
    )
    rhs = np.array(
        [np.inf, -np.inf, 1.0, -0.0, np.inf, 0.0, np.inf, 1.0], dtype=np.float32
    )
    with np.errstate(invalid="ignore", over="ignore"):
        sequential = np.clip(np.multiply(lhs, rhs), np.float32(0.0), np.float32(1.0))
    ort_result = _ort_mul_clip(lhs, rhs, 0.0, 1.0)
    actual = _run_kernel(lhs, rhs)

    _assert_fp32_equal_with_nan(ort_result, sequential)
    _assert_fp32_equal_with_nan(actual, sequential)


def test_shape_dtype_and_clip_bound_contracts_are_explicit():
    lhs = _taichi_array(np.ones(4, np.float32))
    rhs = _taichi_array(np.ones(4, np.float32))
    output = ti.ndarray(ti.f32, shape=(3,))
    with pytest.raises(ValueError, match="identical"):
        fused_mul_clip(lhs, rhs, output, 0.0, 1.0)

    matrix = ti.ndarray(ti.f32, shape=(2, 2))
    with pytest.raises(ValueError, match="one-dimensional"):
        fused_mul_clip(matrix, matrix, matrix, 0.0, 1.0)

    output = ti.ndarray(ti.f32, shape=(4,))
    with pytest.raises(TypeError, match="scalar numbers"):
        fused_mul_clip(lhs, rhs, output, [0.0], 1.0)
    with pytest.raises(ValueError, match="NaN Clip bounds"):
        fused_mul_clip(lhs, rhs, output, np.nan, 1.0)


def test_exact_elementwise_input_alias_is_safe():
    lhs = _taichi_array(np.array([0.25, 2.0, -2.0, 0.5], np.float32))
    rhs = _taichi_array(np.array([2.0, 1.0, 1.0, 0.5], np.float32))
    expected = np.clip(lhs.to_numpy() * rhs.to_numpy(), 0.0, 1.0)
    fused_mul_clip(lhs, rhs, lhs, 0.0, 1.0)
    _assert_fp32_equal_with_nan(lhs.to_numpy(), expected)


@pytest.mark.skipif(
    os.environ.get("PIXEL_REFINE_MUL_CLIP_CUDA_BENCH") != "1",
    reason="run only when the coordinator assigns the CUDA benchmark slot",
)
def test_cuda_microbenchmark():
    """Optional per-kernel latency and ndarray-allocation probe, not graph A/B."""
    reports = []
    profiles = [
        ("gpu512_mul5_clip2", (1, 1, 127, 127)),
        ("gpu1024_mul5_clip2", (1, 1, 255, 255)),
        ("gpu512_mul6_clip3", (1, 1, 512, 512)),
        ("gpu1024_mul6_clip3", (1, 1, 1024, 1024)),
    ]
    for profile, shape in profiles:
        count = int(np.prod(shape))
        rng = np.random.default_rng(count)
        lhs_host = rng.uniform(0.0, 1.0, count).astype(np.float32)
        rhs_host = rng.uniform(0.0, 2.0, count).astype(np.float32)
        lhs = _taichi_array(lhs_host)
        rhs = _taichi_array(rhs_host)
        product = ti.ndarray(ti.f32, shape=(count,))
        sequential_output = ti.ndarray(ti.f32, shape=(count,))
        fused_output = ti.ndarray(ti.f32, shape=(count,))

        def sequential():
            _mul_reference(lhs, rhs, product)
            _clip_reference(product, sequential_output, 0.0, 1.0)

        def fused():
            _fused_mul_clip_kernel(lhs, rhs, fused_output, 0.0, 1.0)

        # Exercise the checked entry point once outside timing. Both timed paths
        # then use their already allocated device ndarrays and compiled kernels.
        fused_mul_clip(lhs, rhs, fused_output, 0.0, 1.0)
        ti.sync()
        for _ in range(20):
            sequential()
            fused()
        ti.sync()

        sequential_ms = []
        fused_ms = []
        for iteration in range(120):
            order = ((sequential, sequential_ms), (fused, fused_ms))
            if iteration % 2:
                order = tuple(reversed(order))
            for operation, samples in order:
                started = time.perf_counter_ns()
                operation()
                ti.sync()
                samples.append((time.perf_counter_ns() - started) / 1e6)

        _assert_fp32_equal_with_nan(
            fused_output.to_numpy(), sequential_output.to_numpy()
        )
        item_bytes = count * np.dtype(np.float32).itemsize
        reports.append(
            {
                "profile": profile,
                "shape": shape,
                "dtype": "float32",
                "taichi_arch": str(ti.cfg.arch),
                "samples": len(fused_ms),
                "sequential_p50_ms": statistics.median(sequential_ms),
                "sequential_p95_ms": float(np.percentile(sequential_ms, 95)),
                "fused_p50_ms": statistics.median(fused_ms),
                "fused_p95_ms": float(np.percentile(fused_ms, 95)),
                "sequential_path_buffer_bytes": item_bytes * 4,
                "fused_path_buffer_bytes": item_bytes * 3,
                "intermediate_bytes_eliminated": item_bytes,
                "timing_boundary": "host launch through ti.sync per operation",
                "scope": "microkernel only; graph is not integrated",
            }
        )
    print("MUL_CLIP_CUDA_MICROBENCH=" + json.dumps(reports, sort_keys=True))
