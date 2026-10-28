"""Kernel parity tests: every pool kernel is exercised through a minimal ONNX
graph and compared against onnxruntime as the numeric oracle.

The compiled pool artifact is required. Build it with::

    python -m taichi_vision.taichi_aot.neural_universal.compile --backend cpu

Tests skip (rather than fail) when the artifact is absent so the suite stays
usable on a machine without a compiled pool.
"""

from __future__ import annotations

import zipfile
import os

# The pool artifact under test is the CPU one; select it before taichi_vision
# initialises its engine singleton.
os.environ.setdefault("AOT_ARCH", "cpu")

from pathlib import Path

import numpy as np
import onnx
import pytest
from onnx import TensorProto as T, helper as h, numpy_helper

from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedONNXOperatorError
from taichi_vision.taichi_aot.neural_universal.plan import Plan
from taichi_vision.taichi_aot.neural_universal.runtime import (
    _build_add_sqrt_clip_fusions,
    _build_binary_unary_fusions,
    _build_sub_sub_div_fusions,
    _build_sub_square_fusions,
    _build_sub_clip_sqrt_fusions,
    _build_unary_binary_fusions,
    _find_pool_tcm,
)

ATOL = 2e-6
RTOL = 0.0
CANDIDATE_POOL_DIR = (
    Path(__file__).resolve().parents[3]
    / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
    / "cpu/unary_binary_candidate_pool_v2"
)
SUB_SUB_DIV_CANDIDATE_POOL = (
    Path(__file__).resolve().parents[3]
    / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
    / "cpu/sub_sub_div_candidate_pool_v5"
)
CONV_SPATIAL_CANDIDATE_POOL = (
    Path(__file__).resolve().parents[3]
    / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
    / "cpu/conv4x4_spatial2x2_candidate_pool_v1"
)
CONV1X1_SPATIAL4_CANDIDATE_POOL = (
    Path(__file__).resolve().parents[3]
    / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
    / "cpu/conv1x1_spatial4_candidate_pool_v1"
)


def _pool_available(backend: str = "cpu") -> bool:
    return _find_pool_tcm(backend) is not None


pytestmark = pytest.mark.skipif(
    not _pool_available("cpu"),
    reason="universal pool artifact not compiled (run neural_universal.compile)",
)


def _session(model, backend="cpu", pool_dir=None):
    from taichi_vision.taichi_aot.neural_universal import UniversalSession

    return UniversalSession(model.SerializeToString(), backend=backend, pool_dir=pool_dir)


def _feed(shape, seed, dtype=np.float32):
    rng = np.random.default_rng(seed)
    if dtype == np.int64:
        return rng.integers(0, 2, size=shape, dtype=np.int64)
    return rng.uniform(-1.0, 1.0, size=shape).astype(dtype)


def _oracle(model):
    import onnxruntime as ort

    return ort.InferenceSession(model.SerializeToString(),
                                providers=["CPUExecutionProvider"])


def _run_both(nodes, inputs, outputs, feeds, opset=17, atol=ATOL, exact=False):
    graph = h.make_graph(nodes, "case", inputs, outputs)
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", opset)])
    model.ir_version = 10
    expected = _oracle(model).run(None, feeds)
    with _session(model) as session:
        actual = session.run(None, feeds)
    assert len(actual) == len(expected)
    for index, (got, want) in enumerate(zip(actual, expected)):
        got = np.asarray(got)
        want = np.asarray(want)
        assert got.shape == want.shape, f"output {index} shape {got.shape} != {want.shape}"
        if exact:
            np.testing.assert_array_equal(got, want, err_msg=f"output {index}")
        else:
            diff = np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))) if got.size else 0.0
            assert diff <= atol, f"output {index} max_abs={diff:.3e} > {atol:.1e}"


def _vi(name, shape, elem=T.FLOAT):
    return h.make_tensor_value_info(name, elem, shape)


def test_shape_host_result_is_available_to_following_gather():
    """Shape metadata outputs must be retained for later host-only steps."""
    graph = h.make_graph(
        [
            h.make_node("Shape", ["x"], ["shape"]),
            h.make_node("Constant", [], ["index"], value=numpy_helper.from_array(
                np.asarray(2, dtype=np.int64))),
            h.make_node("Gather", ["shape", "index"], ["y"], axis=0),
            h.make_node("Constant", [], ["multiplier"], value=numpy_helper.from_array(
                np.asarray(2, dtype=np.int64))),
            h.make_node("Mul", ["y", "multiplier"], ["scaled"]),
            h.make_node("Constant", [], ["axes"], value=numpy_helper.from_array(
                np.asarray([0, 1], dtype=np.int64))),
            h.make_node("Unsqueeze", ["scaled", "axes"], ["z"]),
        ],
        "shape_gather",
        [_vi("x", [2, 3, 4])],
        [_vi("z", [1, 1], T.INT64)],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed([2, 3, 4], 177)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_array_equal(actual, expected)


def test_repeated_run_retires_previous_invocation_buffers():
    shape = [1, 1, 4, 5]
    model = h.make_model(
        h.make_graph(
            [h.make_node("Relu", ["x"], ["y"])],
            "repeated_run_lifecycle",
            [_vi("x", shape)],
            [_vi("y", shape)],
        ),
        opset_imports=[h.make_opsetid("", 17)],
    )
    model.ir_version = 10
    feed = {"x": _feed(shape, 901)}
    with _session(model) as session:
        first = session.run(None, feed, borrowed_outputs=True)[0]
        previous = list(session._live)
        assert first.handle is not None
        second = session.run(None, feed, borrowed_outputs=True)[0]
        assert second.handle is not None
        assert first is second
        assert len(session._live) == len(previous)
        assert all(current is old for current, old in zip(session._live, previous))


# --------------------------------------------------------------- elementwise

@pytest.mark.parametrize("op", ["Relu", "Sigmoid", "Tanh", "Softplus", "Abs", "Sqrt",
                                "Neg", "Erf", "Exp", "Floor", "Sin", "Cos"])
def test_unary_matches_onnxruntime(op):
    shape = [1, 3, 7, 5]
    feed = {"x": np.abs(_feed(shape, 11)) if op == "Sqrt" else _feed(shape, 11)}
    _run_both([h.make_node(op, ["x"], ["y"])], [_vi("x", shape)], [_vi("y", shape)], feed)


def test_gelu_matches_onnxruntime():
    shape = [1, 4, 5, 3]
    graph = h.make_graph(
        [h.make_node("Gelu", ["x"], ["y"], domain="com.microsoft")],
        "gelu", [_vi("x", shape)], [_vi("y", shape)])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17),
                                              h.make_opsetid("com.microsoft", 1)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 12)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    diff = float(np.max(np.abs(np.asarray(actual) - expected)))
    assert diff <= 1e-6, f"gelu max_abs={diff:.3e}"


@pytest.mark.parametrize("slope_shape", [[4], [1, 3, 1, 1]])
def test_prelu_broadcast_matches_onnxruntime(slope_shape):
    shape = [2, 3, 5, 4]
    graph = h.make_graph(
        [h.make_node("PRelu", ["x", "slope"], ["y"])],
        "prelu",
        [_vi("x", shape), _vi("slope", slope_shape)],
        [_vi("y", shape)],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 301), "slope": _feed(slope_shape, 302)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0)


@pytest.mark.parametrize("op", ["Add", "Sub", "Mul", "Div", "Max", "Min"])
def test_binary_same_shape(op):
    shape = [2, 3, 5, 4]
    _run_both([h.make_node(op, ["a", "b"], ["y"])], [_vi("a", shape), _vi("b", shape)],
              [_vi("y", shape)], {"a": _feed(shape, 1), "b": _feed(shape, 2)})


@pytest.mark.parametrize("op", ["Add", "Sub", "Mul", "Div"])
@pytest.mark.parametrize("bshape", [[1, 3, 1, 1], [1, 1, 5, 1], [1, 1, 1, 4], [1, 3, 5, 4]])
def test_binary_broadcast(op, bshape):
    shape = [2, 3, 5, 4]
    _run_both([h.make_node(op, ["a", "b"], ["y"])], [_vi("a", shape), _vi("b", bshape)],
              [_vi("y", shape)], {"a": _feed(shape, 3), "b": _feed(bshape, 4)})


@pytest.mark.parametrize("op", ["Less", "Greater", "Equal"])
def test_comparison_produces_mask(op):
    shape = [2, 3, 4, 3]
    _run_both([h.make_node(op, ["a", "b"], ["y"])], [_vi("a", shape), _vi("b", shape)],
              [_vi("y", shape, T.BOOL)], {"a": _feed(shape, 5), "b": _feed(shape, 6)},
              exact=True)


def test_clip_respects_bounds():
    shape = [1, 2, 6, 6]
    graph = h.make_graph([h.make_node("Clip", ["x", "lo", "hi"], ["y"])], "clip",
                         [_vi("x", shape)], [_vi("y", shape)])
    graph.initializer.extend([
        numpy_helper.from_array(np.array(-0.25, dtype=np.float32), "lo"),
        numpy_helper.from_array(np.array(0.5, dtype=np.float32), "hi"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 7)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_allclose(np.asarray(actual), expected, atol=1e-6, rtol=0)


def test_where_selects_per_element():
    cond = _feed([1, 2, 4, 4], 8, np.int64)
    a = _feed([1, 2, 4, 4], 9)
    b = _feed([1, 2, 4, 4], 10)
    _run_both([h.make_node("Where", ["c", "a", "b"], ["y"])],
              [_vi("c", [1, 2, 4, 4], T.BOOL), _vi("a", [1, 2, 4, 4]), _vi("b", [1, 2, 4, 4])],
              [_vi("y", [1, 2, 4, 4])], {"c": cond.astype(bool), "a": a, "b": b})


# --------------------------------------------------------------------- conv

@pytest.mark.parametrize("group", [1, 2])
@pytest.mark.parametrize("pads", [[0, 0, 0, 0], [1, 1, 1, 1]])
@pytest.mark.parametrize("strides", [[1, 1], [2, 2]])
def test_conv_matches_onnxruntime(group, pads, strides):
    x_shape = [1, 4, 9, 9]
    w_shape = [4, 4 // group, 3, 3]
    nodes = [
        h.make_node("Conv", ["x", "w", "b"], ["y"], group=group, pads=pads,
                    strides=strides, dilations=[1, 1]),
    ]
    graph = h.make_graph(nodes, "conv", [_vi("x", x_shape)],
                         [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.extend([
        numpy_helper.from_array(_feed(w_shape, 20), "w"),
        numpy_helper.from_array(_feed([4], 21), "b"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(x_shape, 22)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert np.asarray(actual).shape == expected.shape
    diff = float(np.max(np.abs(np.asarray(actual) - expected)))
    assert diff <= 1e-5, f"conv max_abs={diff:.3e}"


@pytest.mark.parametrize("backend", ["cpu", "vulkan"])
def test_conv_4x4_stride2_specialization_matches_onnxruntime(backend):
    if backend == "vulkan" and _find_pool_tcm("vulkan") is None:
        pytest.skip("compile the universal Vulkan pool first")
    x_shape = [1, 4, 17, 17]
    w_shape = [5, 4, 4, 4]
    graph = h.make_graph(
        [h.make_node("Conv", ["x", "w", "b"], ["y"], strides=[2, 2])],
        "conv4x4_s2",
        [_vi("x", x_shape)],
        [h.make_tensor_value_info("y", T.FLOAT, None)],
    )
    graph.initializer.extend([
        numpy_helper.from_array(_feed(w_shape, 921), "w"),
        numpy_helper.from_array(_feed([5], 922), "b"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(x_shape, 923)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model, backend=backend) as session:
        actual = session.run(None, feeds)[0]
    # Per-op reduction order is allowed 2e-6; full-model outputs keep the
    # stricter 1e-6 end-to-end acceptance gate.
    np.testing.assert_allclose(actual, expected, atol=2e-6, rtol=0)


@pytest.mark.skipif(
    not (CONV_SPATIAL_CANDIDATE_POOL / "neural_cpu.tcm").is_file(),
    reason="compile the isolated spatial 2x2 Conv candidate CPU pool first",
)
@pytest.mark.parametrize("with_gelu", [False, True])
def test_conv4x4_spatial2x2_matches_base_and_ort_on_weightnet_shape(with_gelu):
    x_shape = [1, 23, 256, 256]
    w_shape = [20, 23, 4, 4]
    nodes = [
        h.make_node("Conv", ["x", "w", "b"], ["conv"], strides=[2, 2]),
    ]
    output_name = "conv"
    imports = [h.make_opsetid("", 17)]
    if with_gelu:
        nodes.append(h.make_node("Gelu", ["conv"], ["y"], domain="com.microsoft"))
        output_name = "y"
        imports.append(h.make_opsetid("com.microsoft", 1))
    graph = h.make_graph(
        nodes,
        "conv4x4_spatial2x2_weightnet_shape",
        [_vi("x", x_shape)],
        [h.make_tensor_value_info(output_name, T.FLOAT, None)],
    )
    # Keep fan-in output magnitude representative of trained FP32 filters so
    # the ORT convolution reduction oracle remains within the documented gate.
    weights = _feed(w_shape, 20261028) * np.float32(0.01)
    bias = _feed([20], 20261029) * np.float32(0.01)
    graph.initializer.extend([
        numpy_helper.from_array(weights, "w"),
        numpy_helper.from_array(bias, "b"),
    ])
    model = h.make_model(graph, opset_imports=imports)
    model.ir_version = 10
    feeds = {"x": _feed(x_shape, 20261027)}
    expected = _oracle(model).run(None, feeds)[0]
    act = 5 if with_gelu else 0

    with _session(model, pool_dir=CONV_SPATIAL_CANDIDATE_POOL) as session:
        x_buffer = session.upload("spatial_test_x", feeds["x"].reshape(-1))
        w_buffer = session.upload("spatial_test_w", weights.reshape(-1))
        b_buffer = session.upload("spatial_test_b", bias.reshape(-1))
        base_output = session.engine.allocate(
            (expected.size,), dtype=np.float32, is_vector=False
        )
        candidate_output = session.engine.allocate(
            (expected.size,), dtype=np.float32, is_vector=False
        )
        session._live.extend((base_output, candidate_output))
        kwargs = {
            "x": x_buffer, "w": w_buffer, "b": b_buffer,
            "n_batch": 1, "ci": 23, "co": 20, "h": 256, "w_in": 256,
            "oh": 127, "ow": 127, "group": 1, "has_bias": 1, "act": act,
        }
        session.module.run("nu_conv2d_4x4_s2", y=base_output, **kwargs)
        session.module.run(
            "nu_conv2d_4x4_s2_spatial_2x2", y=candidate_output, **kwargs
        )
        base = base_output.to_numpy().reshape(expected.shape)
        candidate = candidate_output.to_numpy().reshape(expected.shape)

    np.testing.assert_array_equal(candidate, base)
    diff = candidate.astype(np.float64) - expected.astype(np.float64)
    max_abs = float(np.max(np.abs(diff)))
    rmse = float(np.sqrt(np.mean(diff * diff)))
    exact_count = int(np.count_nonzero(candidate == expected))
    print(
        f"Conv spatial 2x2 Gelu={with_gelu}: max_abs={max_abs:.9g}, "
        f"rmse={rmse:.9g}, exact={exact_count}/{expected.size}"
    )
    assert max_abs <= 1e-6, f"Conv spatial 2x2 max_abs={max_abs:.3e} > 1e-6"
    assert np.isfinite(candidate).all()


@pytest.mark.skipif(
    not (CONV1X1_SPATIAL4_CANDIDATE_POOL / "neural_cpu.tcm").is_file(),
    reason="compile the isolated Conv1x1 spatial-four CPU pool first",
)
@pytest.mark.parametrize(
    "width,ci,co,has_bias,activation",
    [
        (127, 23, 44, True, "Gelu"),
        (127, 3, 5, False, None),
        (255, 4, 3, True, "Softplus"),
    ],
)
def test_conv1x1_spatial4_matches_base_and_ort_with_tails(
    width, ci, co, has_bias, activation
):
    x_shape = [1, ci, width, width]
    w_shape = [co, ci, 1, 1]
    nodes = [h.make_node("Conv", ["x", "w", "b"], ["conv"])]
    output_name = "conv"
    imports = [h.make_opsetid("", 17)]
    if activation == "Gelu":
        nodes.append(h.make_node("Gelu", ["conv"], ["y"], domain="com.microsoft"))
        output_name = "y"
        imports.append(h.make_opsetid("com.microsoft", 1))
    elif activation == "Softplus":
        nodes.append(h.make_node("Softplus", ["conv"], ["y"]))
        output_name = "y"
    graph = h.make_graph(
        nodes,
        "conv1x1_spatial4_tails",
        [_vi("x", x_shape)],
        [h.make_tensor_value_info(output_name, T.FLOAT, None)],
    )
    weights = _feed(w_shape, 20261030) * np.float32(0.01)
    graph.initializer.append(numpy_helper.from_array(weights, "w"))
    if has_bias:
        bias = _feed([co], 20261031) * np.float32(0.01)
        graph.initializer.append(numpy_helper.from_array(bias, "b"))
        has_bias_arg = 1
    else:
        bias = np.zeros([co], dtype=np.float32)
        graph.initializer.append(numpy_helper.from_array(bias, "b"))
        has_bias_arg = 0
    model = h.make_model(graph, opset_imports=imports)
    model.ir_version = 10
    feeds = {"x": _feed(x_shape, 20261032)}
    expected = _oracle(model).run(None, feeds)[0]
    activation_code = {None: 0, "Gelu": 5, "Softplus": 6}[activation]

    with _session(model, pool_dir=CONV1X1_SPATIAL4_CANDIDATE_POOL) as session:
        x_buffer = session.upload("spatial4_test_x", feeds["x"].reshape(-1))
        w_buffer = session.upload("spatial4_test_w", weights.reshape(-1))
        b_buffer = session.upload("spatial4_test_b", bias.reshape(-1))
        base_output = session.engine.allocate(
            (expected.size,), dtype=np.float32, is_vector=False
        )
        candidate_output = session.engine.allocate(
            (expected.size,), dtype=np.float32, is_vector=False
        )
        session._live.extend((base_output, candidate_output))
        kwargs = {
            "x": x_buffer, "w": w_buffer, "b": b_buffer,
            "n_batch": 1, "ci": ci, "co": co, "hw": width * width,
            "has_bias": has_bias_arg, "act": activation_code,
        }
        session.module.run("nu_conv2d_1x1", y=base_output, **kwargs)
        session.module.run(
            "nu_conv2d_1x1_spatial4", y=candidate_output, **kwargs
        )
        base = base_output.to_numpy().reshape(expected.shape)
        candidate = candidate_output.to_numpy().reshape(expected.shape)
    baseline_diff = candidate.astype(np.float64) - base.astype(np.float64)
    expected_diff = candidate.astype(np.float64) - expected.astype(np.float64)
    baseline_max = float(np.max(np.abs(baseline_diff)))
    expected_max = float(np.max(np.abs(expected_diff)))
    baseline_rmse = float(np.sqrt(np.mean(baseline_diff * baseline_diff)))
    expected_rmse = float(np.sqrt(np.mean(expected_diff * expected_diff)))
    print(
        f"Conv1x1 spatial4 width={width} activation={activation}: "
        f"baseline max/rmse={baseline_max:.9g}/{baseline_rmse:.9g}, "
        f"ORT max/rmse={expected_max:.9g}/{expected_rmse:.9g}"
    )
    assert baseline_max <= 1e-6, (
        f"Conv1x1 spatial4 baseline max_abs={baseline_max:.3e} > 1e-6"
    )
    assert expected_max <= 1e-6, f"Conv1x1 spatial4 ORT max_abs={expected_max:.3e} > 1e-6"
    assert np.isfinite(candidate).all()


@pytest.mark.parametrize("backend", ["cpu", "vulkan"])
def test_profile_only_conv4x4_kahan_unrolled_kernel_matches_onnxruntime(backend):
    if backend == "vulkan" and _find_pool_tcm("vulkan") is None:
        pytest.skip("compile the universal Vulkan pool first")
    x_shape = [1, 4, 17, 17]
    w_shape = [5, 4, 4, 4]
    graph = h.make_graph(
        [h.make_node("Conv", ["x", "w", "b"], ["y"], strides=[2, 2])],
        "conv4x4_s2_unrolled",
        [_vi("x", x_shape)],
        [h.make_tensor_value_info("y", T.FLOAT, None)],
    )
    weights = _feed(w_shape, 921)
    bias = _feed([5], 922)
    graph.initializer.extend([
        numpy_helper.from_array(weights, "w"),
        numpy_helper.from_array(bias, "b"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feed = _feed(x_shape, 923)
    expected = _oracle(model).run(None, {"x": feed})[0]
    output_shape = tuple(int(dim) for dim in expected.shape)
    with _session(model, backend=backend) as session:
        x_buffer = session.upload("test_x", feed.reshape(-1))
        w_buffer = session.upload("test_w", weights.reshape(-1))
        b_buffer = session.upload("test_b", bias.reshape(-1))
        output = session.engine.allocate(
            (int(np.prod(output_shape)),), dtype=np.float32, is_vector=False
        )
        session._live.append(output)
        session.module.run(
            "nu_conv2d_4x4_s2_kahan_unrolled",
            x=x_buffer, w=w_buffer, b=b_buffer, y=output,
            n_batch=1, ci=4, co=5, h=17, w_in=17,
            oh=output_shape[2], ow=output_shape[3],
            group=1, has_bias=1, act=0,
        )
        actual = output.to_numpy().reshape(output_shape)
    np.testing.assert_allclose(actual, expected, atol=2e-6, rtol=0)


@pytest.mark.parametrize("backend", ["cpu", "vulkan"])
@pytest.mark.parametrize(
    "kernel_name",
    [
        "nu_conv2d_4x4_s2_kahan_unrolled",
        "nu_conv2d_4x4_s2_plain",
    ],
)
def test_profile_conv4x4_variant_kernel_matches_onnxruntime(backend, kernel_name):
    if backend == "vulkan" and _find_pool_tcm("vulkan") is None:
        pytest.skip("compile the universal Vulkan pool first")
    x_shape = [1, 4, 17, 17]
    w_shape = [5, 4, 4, 4]
    x = _feed(x_shape, 923)
    weights = _feed(w_shape, 921)
    bias = _feed([5], 922)
    graph = h.make_graph(
        [h.make_node("Conv", ["x", "w", "b"], ["y"], strides=[2, 2])],
        "conv4x4_s2_kahan_unrolled",
        [_vi("x", x_shape)],
        [h.make_tensor_value_info("y", T.FLOAT, None)],
    )
    graph.initializer.extend([
        numpy_helper.from_array(weights, "w"),
        numpy_helper.from_array(bias, "b"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    expected = _oracle(model).run(None, {"x": x})[0]
    with _session(model, backend=backend) as session:
        x_buffer = session.upload("unroll_x", x.reshape(-1))
        w_buffer = session.upload("unroll_w", weights.reshape(-1))
        b_buffer = session.upload("unroll_b", bias.reshape(-1))
        output = session.engine.allocate(
            (int(np.prod(expected.shape)),), dtype=np.float32, is_vector=False
        )
        session._live.append(output)
        session.module.run(
            kernel_name,
            x=x_buffer, w=w_buffer, b=b_buffer, y=output,
            n_batch=1, ci=4, co=5, h=17, w_in=17,
            oh=expected.shape[2], ow=expected.shape[3],
            group=1, has_bias=1, act=0,
        )
        actual = output.to_numpy().reshape(expected.shape)
    np.testing.assert_allclose(actual, expected, atol=2e-6, rtol=0)


@pytest.mark.parametrize("activation,domain", [("Gelu", "com.microsoft"), ("Softplus", "")])
def test_conv_pointwise_activation_fusion_matches_onnxruntime(activation, domain):
    x_shape = [1, 2, 8, 8]
    w_shape = [3, 2, 1, 1]
    nodes = [
        h.make_node("Conv", ["x", "w", "b"], ["conv_out"]),
        h.make_node(activation, ["conv_out"], ["y"], domain=domain),
    ]
    imports = [h.make_opsetid("", 17)]
    if domain:
        imports.append(h.make_opsetid(domain, 1))
    graph = h.make_graph(
        nodes,
        "conv_activation_fusion",
        [_vi("x", x_shape)],
        [_vi("y", [1, 3, 8, 8])],
    )
    graph.initializer.extend([
        numpy_helper.from_array(_feed(w_shape, 931), "w"),
        numpy_helper.from_array(_feed([3], 932), "b"),
    ])
    model = h.make_model(graph, opset_imports=imports)
    model.ir_version = 10
    feeds = {"x": _feed(x_shape, 933)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0)


def test_mul_clip_fusion_matches_onnxruntime_and_respects_requested_intermediate():
    shape = [1, 3, 5, 7]
    graph = h.make_graph(
        [
            h.make_node("Mul", ["a", "b"], ["product"]),
            h.make_node("Clip", ["product", "lo", "hi"], ["y"]),
        ],
        "mul_clip_fusion",
        [_vi("a", shape), _vi("b", shape)],
        [_vi("y", shape)],
    )
    graph.initializer.extend([
        numpy_helper.from_array(np.asarray(-0.2, np.float32), "lo"),
        numpy_helper.from_array(np.asarray(0.3, np.float32), "hi"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"a": _feed(shape, 941), "b": _feed(shape, 942)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
        intermediate = session.run(["product"], feeds)[0]
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0)
    np.testing.assert_allclose(intermediate, feeds["a"] * feeds["b"], atol=1e-6, rtol=0)


def test_conv_transpose_matches_onnxruntime():
    x_shape = [1, 3, 5, 5]
    w_shape = [3, 2, 3, 3]
    graph = h.make_graph(
        [h.make_node("ConvTranspose", ["x", "w"], ["y"], strides=[2, 2], pads=[1, 1, 1, 1])],
        "ct", [_vi("x", x_shape)], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.append(numpy_helper.from_array(_feed(w_shape, 30), "w"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(x_shape, 31)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert np.asarray(actual).shape == expected.shape
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-5


# ------------------------------------------------------------------- linear

def test_matmul_batched_matches_onnxruntime():
    a_shape, b_shape = [2, 3, 4, 5], [2, 3, 5, 6]
    _run_both([h.make_node("MatMul", ["a", "b"], ["y"])],
              [_vi("a", a_shape), _vi("b", b_shape)],
              [h.make_tensor_value_info("y", T.FLOAT, None)],
              {"a": _feed(a_shape, 40), "b": _feed(b_shape, 41)}, atol=1e-5)


def test_gemm_matches_onnxruntime():
    a_shape, b_shape = [4, 6], [6, 3]
    graph = h.make_graph([h.make_node("Gemm", ["a", "b"], ["y"])], "gemm",
                         [_vi("a", a_shape)], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.append(numpy_helper.from_array(_feed(b_shape, 42), "b"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"a": _feed(a_shape, 43)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-5


# ---------------------------------------------------------------- norm/reduce

def test_instance_norm_matches_onnxruntime():
    shape = [1, 4, 6, 5]
    graph = h.make_graph(
        [h.make_node("InstanceNormalization", ["x", "s", "b"], ["y"], epsilon=1e-5)],
        "inorm", [_vi("x", shape)], [_vi("y", shape)])
    graph.initializer.extend([
        numpy_helper.from_array(_feed([4], 50).ravel(), "s"),
        numpy_helper.from_array(_feed([4], 51).ravel(), "b"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 52)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-5


def test_layer_norm_matches_onnxruntime():
    shape = [2, 5, 8]
    graph = h.make_graph(
        [h.make_node("LayerNormalization", ["x", "s", "b"], ["y"], axis=-1, epsilon=1e-5)],
        "lnorm", [_vi("x", shape)], [_vi("y", shape)])
    graph.initializer.extend([
        numpy_helper.from_array(_feed([8], 60).ravel(), "s"),
        numpy_helper.from_array(_feed([8], 61).ravel(), "b"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 62)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-5


@pytest.mark.parametrize("op", ["Softmax", "LogSoftmax"])
@pytest.mark.parametrize("shape", [[1, 4, 6], [2, 3, 5, 4]])
def test_softmax_family(op, shape):
    graph = h.make_graph([h.make_node(op, ["x"], ["y"], axis=-1)], "sm",
                         [_vi("x", shape)], [_vi("y", shape)])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 70)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-6


@pytest.mark.parametrize("op", ["ReduceMean", "ReduceSum", "ReduceL2"])
@pytest.mark.parametrize("axes", [[1], [2, 3], [1, 2, 3]])
def test_reduce_multi_axis(op, axes):
    shape = [1, 3, 4, 5]
    graph = h.make_graph(
        [h.make_node(op, ["x", "ax"], ["y"], keepdims=1)], "red",
        [_vi("x", shape)], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.append(
        numpy_helper.from_array(np.array(axes, dtype=np.int64), "ax"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 80)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert np.asarray(actual).shape == expected.shape
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-5


# ---------------------------------------------------------------- movement

def test_transpose_matches_onnxruntime():
    shape = [2, 3, 4, 5]
    _run_both([h.make_node("Transpose", ["x"], ["y"], perm=[0, 2, 3, 1])], [_vi("x", shape)],
              [h.make_tensor_value_info("y", T.FLOAT, None)], {"x": _feed(shape, 90)})


def test_concat_three_inputs_matches_onnxruntime():
    a, b, c = [1, 2, 4, 3], [1, 5, 4, 3], [1, 1, 4, 3]
    _run_both([h.make_node("Concat", ["a", "b", "c"], ["y"], axis=1)],
              [_vi("a", a), _vi("b", b), _vi("c", c)],
              [h.make_tensor_value_info("y", T.FLOAT, None)],
              {"a": _feed(a, 91), "b": _feed(b, 92), "c": _feed(c, 93)})


def test_split_matches_onnxruntime():
    shape = [1, 6, 4]
    graph = h.make_graph([h.make_node("Split", ["x", "sp"], ["y0", "y1"], axis=1)], "sp",
                         [_vi("x", shape)],
                         [h.make_tensor_value_info("y0", T.FLOAT, None),
                          h.make_tensor_value_info("y1", T.FLOAT, None)])
    graph.initializer.append(numpy_helper.from_array(np.array([2, 4], dtype=np.int64), "sp"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 100)}
    expected = _oracle(model).run(None, feeds)
    with _session(model) as session:
        actual = session.run(None, feeds)
    for got, want in zip(actual, expected):
        assert np.asarray(got).shape == np.asarray(want).shape
        assert float(np.max(np.abs(np.asarray(got) - want))) <= 1e-6


def test_slice_multi_axis_matches_onnxruntime():
    shape = [1, 4, 6, 6]
    graph = h.make_graph([h.make_node("Slice", ["x", "st", "en", "ax"], ["y"])], "sl",
                         [_vi("x", shape)], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.extend([
        numpy_helper.from_array(np.array([1, 2], dtype=np.int64), "st"),
        numpy_helper.from_array(np.array([3, 5], dtype=np.int64), "en"),
        numpy_helper.from_array(np.array([2, 3], dtype=np.int64), "ax"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 110)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert np.asarray(actual).shape == expected.shape
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-6


def test_pad_constant_matches_onnxruntime():
    shape = [1, 2, 4, 4]
    graph = h.make_graph([h.make_node("Pad", ["x", "pads", "val"], ["y"], mode="constant")],
                         "pad", [_vi("x", shape)],
                         [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.extend([
        numpy_helper.from_array(np.array([0, 0, 1, 2, 0, 0, 1, 2], dtype=np.int64), "pads"),
        numpy_helper.from_array(np.array(0.5, dtype=np.float32), "val"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 120)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert np.asarray(actual).shape == expected.shape
    np.testing.assert_array_equal(np.asarray(actual), expected)


def test_tile_matches_onnxruntime():
    shape = [1, 2, 3]
    graph = h.make_graph([h.make_node("Tile", ["x", "rep"], ["y"])], "tile",
                         [_vi("x", shape)], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.append(numpy_helper.from_array(np.array([1, 3, 2], dtype=np.int64), "rep"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 130)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_array_equal(np.asarray(actual), expected)


def test_space_to_depth_matches_onnxruntime():
    shape = [1, 2, 4, 4]
    _run_both([h.make_node("SpaceToDepth", ["x"], ["y"], blocksize=2)], [_vi("x", shape)],
              [h.make_tensor_value_info("y", T.FLOAT, None)], {"x": _feed(shape, 140)},
              exact=True)


def test_resize_linear_half_pixel_matches_onnxruntime():
    shape = [1, 2, 4, 4]
    graph = h.make_graph(
        [h.make_node("Resize", ["x", "", "scales"], ["y"], mode="linear",
                     coordinate_transformation_mode="half_pixel", nearest_mode="floor")],
        "rs", [_vi("x", shape)], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.append(
        numpy_helper.from_array(np.array([1.0, 1.0, 2.0, 2.0], dtype=np.float32), "scales"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 150)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert np.asarray(actual).shape == expected.shape
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-6


def test_gather_and_gather_elements_match_onnxruntime():
    data = [1, 4, 5]
    graph = h.make_graph([h.make_node("Gather", ["d", "i"], ["y"], axis=1)], "g",
                         [_vi("d", data)], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.append(numpy_helper.from_array(np.array([0, 2, 1], dtype=np.int64), "i"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"d": _feed(data, 160)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_array_equal(np.asarray(actual), expected)


# ------------------------------------------------------------------ pooling

@pytest.mark.parametrize("op", ["AveragePool", "MaxPool"])
def test_pool_matches_onnxruntime(op):
    shape = [1, 3, 8, 8]
    _run_both([h.make_node(op, ["x"], ["y"], kernel_shape=[3, 3], strides=[2, 2],
                           pads=[1, 1, 1, 1])], [_vi("x", shape)],
              [h.make_tensor_value_info("y", T.FLOAT, None)], {"x": _feed(shape, 170)},
              exact=(op == "MaxPool"), atol=1e-6)


# --------------------------------------------------------------- index / meta

def test_topk_last_axis_matches_onnxruntime():
    shape = [2, 6]
    graph = h.make_graph([h.make_node("TopK", ["x", "k"], ["v", "i"], axis=-1,
                                     largest=1, sorted=1)], "tk",
                         [_vi("x", shape)],
                         [h.make_tensor_value_info("v", T.FLOAT, None),
                          h.make_tensor_value_info("i", T.INT64, None)])
    graph.initializer.append(numpy_helper.from_array(np.array([3], dtype=np.int64), "k"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 180)}
    expected = _oracle(model).run(None, feeds)
    with _session(model) as session:
        actual = session.run(None, feeds)
    np.testing.assert_allclose(np.asarray(actual[0]), expected[0], atol=1e-6, rtol=0)
    np.testing.assert_array_equal(np.asarray(actual[1]), expected[1])


@pytest.mark.parametrize("count,shape", [(5, [5]), (7, [4, 4])])
def test_range_matches_onnxruntime(count, shape):
    total = int(np.prod(shape))
    graph = h.make_graph([h.make_node("Range", ["s", "l", "d"], ["y"])], "rg", [],
                         [h.make_tensor_value_info("y", T.FLOAT, None)])
    for name, value in (("s", 0.0), ("l", float(total)), ("d", 1.0)):
        graph.initializer.append(
            numpy_helper.from_array(np.array(value, dtype=np.float32), name))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    expected = _oracle(model).run(None, {})[0]
    with _session(model) as session:
        actual = session.run(None, {})[0]
    np.testing.assert_allclose(np.asarray(actual), expected, atol=1e-6, rtol=0)


def test_constant_of_shape_matches_onnxruntime():
    graph = h.make_graph(
        [h.make_node("ConstantOfShape", ["s"], ["y"],
                     value=numpy_helper.from_array(np.array([2.5], dtype=np.float32)))],
        "cos", [], [h.make_tensor_value_info("y", T.FLOAT, None)])
    graph.initializer.append(numpy_helper.from_array(np.array([2, 3], dtype=np.int64), "s"))
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    expected = _oracle(model).run(None, {})[0]
    with _session(model) as session:
        actual = session.run(None, {})[0]
    np.testing.assert_array_equal(np.asarray(actual), expected)


def test_cast_between_dtypes_matches_onnxruntime():
    shape = [1, 5]
    graph = h.make_graph([h.make_node("Cast", ["x"], ["y"], to=T.INT32)], "cast",
                         [_vi("x", shape)],
                         [h.make_tensor_value_info("y", T.INT32, shape)])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"x": _feed(shape, 190)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_array_equal(np.asarray(actual), expected)


# --------------------------------------------------------------- attention

def test_multi_head_attention_matches_onnxruntime():
    batch, seq, heads, head_dim = 1, 6, 2, 4
    hidden = heads * head_dim
    shape = [batch, seq, hidden]
    graph = h.make_graph(
            [h.make_node("MultiHeadAttention", ["q", "k", "v"], ["y"], num_heads=heads,
                         domain="com.microsoft")],
            "mha", [_vi("q", shape), _vi("k", shape), _vi("v", shape)], [_vi("y", shape)])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17),
                                              h.make_opsetid("com.microsoft", 1)])
    model.ir_version = 10
    feeds = {"q": _feed(shape, 200), "k": _feed(shape, 201), "v": _feed(shape, 202)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    assert float(np.max(np.abs(np.asarray(actual) - expected))) <= 1e-5


# ------------------------------------------------------------ fused / macros


@pytest.mark.skipif(
    not (CANDIDATE_POOL_DIR / "neural_cpu.tcm").is_file(),
    reason="compile the isolated unary-binary candidate pool first",
)
@pytest.mark.parametrize(
    "unary_op,binary_op,unary_is_left",
    [
        ("Softplus", "Add", True),
        ("Log", "Add", True),
        ("Tanh", "Sub", False),
        ("Tanh", "Mul", True),
    ],
)
def test_unary_binary_candidate_matches_ort_with_broadcast_and_edge_values(
    unary_op, binary_op, unary_is_left
):
    x_shape = [1, 1, 1, 7]
    other_shape = [1]
    intermediate = "u"
    binary_inputs = [intermediate, "b"] if unary_is_left else ["b", intermediate]
    graph = h.make_graph(
        [
            h.make_node(unary_op, ["x"], [intermediate]),
            h.make_node(binary_op, binary_inputs, ["y"]),
        ],
        f"{unary_op}_{binary_op}_fusion",
        [_vi("x", x_shape), _vi("b", other_shape)],
        [_vi("y", x_shape)],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    plan = Plan.from_model_bytes(model.SerializeToString())
    matches = _build_unary_binary_fusions(plan, set(plan.output_names))
    assert len(matches) == 1

    x = np.asarray([-np.inf, -0.0, 0.0, 1e-5, -1.0, np.inf, np.nan], dtype=np.float32).reshape(x_shape)
    other = np.asarray([-0.0], dtype=np.float32)
    if binary_op == "Div":
        other = np.asarray([1.0], dtype=np.float32)
    feeds = {"x": x, "b": other}
    expected = _oracle(model).run(None, feeds)[0]

    def run(pool_dir=None):
        calls = []
        with _session(model, pool_dir=pool_dir) as session:
            original_run = session.module.run

            def traced_run(name, *args, **kwargs):
                calls.append(name)
                return original_run(name, *args, **kwargs)

            session.module.run = traced_run
        try:
            output = session.run(None, feeds)[0]
        finally:
            session.module.run = original_run
        return np.asarray(output), calls

    generic, generic_calls = run()
    fused, fused_calls = run(CANDIDATE_POOL_DIR)
    assert "nu_fused_unary_binary" not in generic_calls
    assert fused_calls.count("nu_fused_unary_binary") == 1
    assert len(fused_calls) == len(generic_calls) - 1
    assert np.array_equal(fused, generic, equal_nan=True)
    assert np.array_equal(np.isnan(fused), np.isnan(expected))
    assert np.array_equal(np.isposinf(fused), np.isposinf(expected))
    assert np.array_equal(np.isneginf(fused), np.isneginf(expected))
    zero_mask = np.isfinite(fused) & (fused == 0.0)
    assert np.array_equal(np.signbit(fused[zero_mask]), np.signbit(expected[zero_mask]))
    finite = np.isfinite(fused) & np.isfinite(expected)
    diff = fused[finite].astype(np.float64) - expected[finite].astype(np.float64)
    max_abs = float(np.max(np.abs(diff))) if diff.size else 0.0
    assert max_abs <= 1e-6, f"{unary_op}->{binary_op} max_abs={max_abs:.3e}"


@pytest.mark.skipif(
    not (CANDIDATE_POOL_DIR / "neural_cpu.tcm").is_file(),
    reason="compile the isolated unary-binary candidate pool first",
)
def test_unary_binary_candidate_falls_back_for_fanout_requested_and_ambiguous_inputs():
    shape = [1, 1, 1, 5]
    branch_graph = h.make_graph(
        [
            h.make_node("Softplus", ["x"], ["u"]),
            h.make_node("Add", ["u", "b"], ["y"]),
            h.make_node("Neg", ["u"], ["branch"]),
        ],
        "unary_binary_fanout",
        [_vi("x", shape), _vi("b", [1])],
        [_vi("y", shape), _vi("branch", shape)],
    )
    branch_model = h.make_model(branch_graph, opset_imports=[h.make_opsetid("", 17)])
    branch_model.ir_version = 10
    branch_plan = Plan.from_model_bytes(branch_model.SerializeToString())
    assert not _build_unary_binary_fusions(branch_plan, set())

    ambiguous_graph = h.make_graph(
        [
            h.make_node("Softplus", ["x"], ["u1"]),
            h.make_node("Tanh", ["z"], ["u2"]),
            h.make_node("Sub", ["u1", "u2"], ["y"]),
        ],
        "unary_binary_ambiguous",
        [_vi("x", shape), _vi("z", shape)],
        [_vi("y", shape)],
    )
    ambiguous_model = h.make_model(
        ambiguous_graph, opset_imports=[h.make_opsetid("", 17)]
    )
    ambiguous_model.ir_version = 10
    ambiguous_plan = Plan.from_model_bytes(ambiguous_model.SerializeToString())
    assert not _build_unary_binary_fusions(ambiguous_plan, set())

    feeds = {
        "x": np.asarray([-1.0, -0.0, 0.0, 1.0, np.nan], dtype=np.float32).reshape(shape),
        "b": np.ones([1], dtype=np.float32),
        "z": np.asarray([-np.inf, -1.0, 0.0, 1.0, np.inf], dtype=np.float32).reshape(shape),
    }
    for model in (branch_model, ambiguous_model):
        oracle = _oracle(model)
        model_feeds = {meta.name: feeds[meta.name] for meta in oracle.get_inputs()}
        expected = oracle.run(None, model_feeds)[0]
        with _session(model, pool_dir=CANDIDATE_POOL_DIR) as session:
            calls = []
            original = session.module.run

            def traced(name, *args, **kwargs):
                calls.append(name)
                return original(name, *args, **kwargs)

            session.module.run = traced
            try:
                actual = np.asarray(session.run(None, model_feeds)[0])
            finally:
                session.module.run = original
        assert "nu_fused_unary_binary" not in calls
        np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0, equal_nan=True)

    # Requesting the intermediate makes the otherwise valid chain observable.
    valid_graph = h.make_graph(
        [h.make_node("Softplus", ["x"], ["u"]), h.make_node("Add", ["u", "b"], ["y"])],
        "unary_binary_requested_intermediate",
        [_vi("x", shape), _vi("b", [1])],
        [_vi("u", shape), _vi("y", shape)],
    )
    valid_model = h.make_model(valid_graph, opset_imports=[h.make_opsetid("", 17)])
    valid_model.ir_version = 10
    plan = Plan.from_model_bytes(valid_model.SerializeToString())
    assert not _build_unary_binary_fusions(plan, {"u", "y"})
    with _session(valid_model, pool_dir=CANDIDATE_POOL_DIR) as session:
        calls = []
        original = session.module.run

        def traced(name, *args, **kwargs):
            calls.append(name)
            return original(name, *args, **kwargs)

        session.module.run = traced
        try:
            valid_feeds = {"x": feeds["x"], "b": feeds["b"]}
            expected_outputs = _oracle(valid_model).run(None, valid_feeds)
            expected = expected_outputs[1]
            actual_outputs = session.run(None, valid_feeds)
            actual = np.asarray(actual_outputs[1])
        finally:
            session.module.run = original
    assert "nu_fused_unary_binary" not in calls
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0, equal_nan=True)


@pytest.mark.skipif(
    not (SUB_SUB_DIV_CANDIDATE_POOL / "neural_cpu.tcm").is_file(),
    reason="compile the isolated Sub-Sub-Div candidate CPU pool first",
)
def test_sub_sub_div_candidate_matches_ort_generic_and_edge_values():
    shape = [1, 1, 1, 9]
    graph = h.make_graph(
        [
            h.make_node("Sub", ["a", "b"], ["u"]),
            h.make_node("Sub", ["u", "c"], ["v"]),
            h.make_node("Div", ["v", "d"], ["y"]),
        ],
        "sub_sub_div_candidate",
        [_vi(name, shape) for name in ("a", "b", "c", "d")],
        [_vi("y", shape)],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    plan = Plan.from_model_bytes(model.SerializeToString())
    candidates = _build_sub_sub_div_fusions(plan, {"y"})
    assert len(candidates) == 1
    assert candidates[0][:3] == (1, 2, "y")

    feeds = {
        "a": np.asarray([-0.0, 0.0, 1.0, -1.0, np.inf, -np.inf, np.finfo(np.float32).max, 2.0, np.nan], dtype=np.float32).reshape(shape),
        "b": np.asarray([0.0, -0.0, 1.0, 1.0, 1.0, 1.0, -np.finfo(np.float32).max, 1.0, 0.0], dtype=np.float32).reshape(shape),
        "c": np.asarray([0.0, -0.0, -2.0, 2.0, -np.inf, np.inf, np.finfo(np.float32).max, -1.0, np.inf], dtype=np.float32).reshape(shape),
        "d": np.asarray([1.0, 1.0, 0.0, -0.0, 1.0, 1.0, 1.0, 3.0, 1.0], dtype=np.float32).reshape(shape),
    }
    expected = _oracle(model).run(None, feeds)[0]
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        first_fp32 = np.subtract(feeds["a"], feeds["b"], dtype=np.float32)
        second_fp32 = np.subtract(first_fp32, feeds["c"], dtype=np.float32)
        expected_fp32 = np.divide(second_fp32, feeds["d"], dtype=np.float32)
    assert np.isposinf(first_fp32.reshape(-1)[6])
    assert np.isposinf(second_fp32.reshape(-1)[6])
    assert np.isposinf(expected_fp32.reshape(-1)[6])
    assert np.isposinf(expected.reshape(-1)[6])

    def run(pool_dir=None):
        calls = []
        with _session(model, pool_dir=pool_dir) as session:
            original_run = session.module.run

            def traced_run(name, *args, **kwargs):
                calls.append(name)
                return original_run(name, *args, **kwargs)

            session.module.run = traced_run
            try:
                output = session.run(None, feeds)[0]
            finally:
                session.module.run = original_run
        return np.asarray(output), calls

    generic, generic_calls = run()
    fused, fused_calls = run(SUB_SUB_DIV_CANDIDATE_POOL)
    assert "nu_fused_sub_sub_div" not in generic_calls
    assert fused_calls.count("nu_fused_sub_sub_div") == 1
    assert len(fused_calls) == len(generic_calls) - 2
    assert np.array_equal(fused, generic, equal_nan=True)
    assert np.array_equal(np.isnan(fused), np.isnan(expected))
    assert np.array_equal(np.isposinf(fused), np.isposinf(expected))
    assert np.array_equal(np.isneginf(fused), np.isneginf(expected))
    zero_mask = np.isfinite(fused) & (fused == 0.0)
    assert np.array_equal(np.signbit(fused[zero_mask]), np.signbit(expected[zero_mask]))
    finite = np.isfinite(fused) & np.isfinite(expected)
    error = fused[finite].astype(np.float64) - expected[finite].astype(np.float64)
    max_abs = float(np.max(np.abs(error))) if error.size else 0.0
    assert max_abs <= 1e-6, f"Sub->Sub->Div edge max_abs={max_abs:.3e}"


def test_sub_sub_div_matcher_fails_closed_for_liveness_dtype_and_attrs():
    shape = [1, 1, 1, 4]

    def make_plan(nodes, inputs):
        graph = h.make_graph(
            nodes, "sub_sub_div_guards", inputs, [_vi("y", shape)]
        )
        model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
        model.ir_version = 10
        return Plan.from_model_bytes(model.SerializeToString())

    inputs = [_vi(name, shape) for name in ("a", "b", "c", "d")]
    chain = [
        h.make_node("Sub", ["a", "b"], ["u"]),
        h.make_node("Sub", ["u", "c"], ["v"]),
        h.make_node("Div", ["v", "d"], ["y"]),
    ]
    valid_plan = make_plan(chain, inputs)
    assert not _build_sub_sub_div_fusions(valid_plan, {"u", "y"})
    assert not _build_sub_sub_div_fusions(valid_plan, {"v", "y"})
    dtype_plan = make_plan(chain, inputs)
    dtype_plan.dtypes["c"] = "i32"
    assert not _build_sub_sub_div_fusions(dtype_plan, set())

    fanout_plan = make_plan(
        chain[:1] + [h.make_node("Neg", ["u"], ["branch"])] + chain[1:], inputs
    )
    assert not _build_sub_sub_div_fusions(fanout_plan, set())

    attr_plan = make_plan(chain, inputs)
    attr_plan.nodes[0].attrs["unexpected"] = 1
    assert not _build_sub_sub_div_fusions(attr_plan, set())

    duplicate_plan = make_plan(
        [
            h.make_node("Sub", ["a", "b"], ["u"]),
            h.make_node("Sub", ["u", "a"], ["v"]),
            h.make_node("Div", ["v", "d"], ["y"]),
        ],
        inputs,
    )
    assert not _build_sub_sub_div_fusions(duplicate_plan, set())


@pytest.mark.skipif(
    not (SUB_SUB_DIV_CANDIDATE_POOL / "neural_cpu.tcm").is_file(),
    reason="compile the isolated Sub-Sub-Div candidate CPU pool first",
)
def test_sub_sub_div_candidate_falls_back_for_broadcast_shape_mismatch():
    shape = [1, 1, 1, 4]
    graph = h.make_graph(
        [
            h.make_node("Sub", ["a", "b"], ["u"]),
            h.make_node("Sub", ["u", "c"], ["v"]),
            h.make_node("Div", ["v", "d"], ["y"]),
        ],
        "sub_sub_div_broadcast_fallback",
        [
            _vi("a", shape), _vi("b", shape), _vi("c", [1]), _vi("d", shape),
        ],
        [_vi("y", shape)],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {
        "a": np.asarray([2.0, -1.0, 0.0, 5.0], dtype=np.float32).reshape(shape),
        "b": np.asarray([1.0, 0.0, -0.0, 2.0], dtype=np.float32).reshape(shape),
        "c": np.asarray([0.5], dtype=np.float32),
        "d": np.asarray([1.0, 2.0, -1.0, 3.0], dtype=np.float32).reshape(shape),
    }
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model, pool_dir=SUB_SUB_DIV_CANDIDATE_POOL) as session:
        calls = []
        original_run = session.module.run

        def traced_run(name, *args, **kwargs):
            calls.append(name)
            return original_run(name, *args, **kwargs)

        session.module.run = traced_run
        try:
            actual = np.asarray(session.run(None, feeds)[0])
        finally:
            session.module.run = original_run
    assert "nu_fused_sub_sub_div" not in calls
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0, equal_nan=True)


@pytest.mark.skipif(
    not (SUB_SUB_DIV_CANDIDATE_POOL / "neural_cpu.tcm").is_file(),
    reason="compile the isolated Sub-Sub-Div candidate CPU pool first",
)
def test_sub_sub_div_candidate_rejects_scratch_name_collision_without_mutating_input():
    shape = [1, 1, 1, 4]
    collision_name = "__nu_fused_sub_sub_div_0_first"
    graph = h.make_graph(
        [
            h.make_node("Sub", [collision_name, "b"], ["u"]),
            h.make_node("Sub", ["u", "c"], ["v"]),
            h.make_node("Div", ["v", "d"], ["y"]),
        ],
        "sub_sub_div_scratch_name_collision",
        [_vi(name, shape) for name in (collision_name, "b", "c", "d")],
        [_vi("y", shape)],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    plan = Plan.from_model_bytes(model.SerializeToString())
    assert not _build_sub_sub_div_fusions(plan, {"y"})

    feeds = {
        collision_name: np.asarray([1.0, -2.0, 0.0, 4.0], dtype=np.float32).reshape(shape),
        "b": np.asarray([0.5, 1.0, -0.0, 2.0], dtype=np.float32).reshape(shape),
        "c": np.asarray([0.25, -1.0, 1.0, 1.0], dtype=np.float32).reshape(shape),
        "d": np.asarray([2.0, 3.0, -1.0, 4.0], dtype=np.float32).reshape(shape),
    }
    original_inputs = {name: value.copy() for name, value in feeds.items()}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model, pool_dir=SUB_SUB_DIV_CANDIDATE_POOL) as session:
        calls = []
        original_run = session.module.run

        def traced_run(name, *args, **kwargs):
            calls.append(name)
            return original_run(name, *args, **kwargs)

        session.module.run = traced_run
        try:
            actual = np.asarray(session.run(None, feeds)[0])
        finally:
            session.module.run = original_run
    assert "nu_fused_sub_sub_div" not in calls
    for name, original_input in original_inputs.items():
        np.testing.assert_array_equal(feeds[name], original_input)
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0, equal_nan=True)

def test_mul_clip_chain_matches_onnxruntime():
    shape = [1, 1, 4, 4]
    graph = h.make_graph([h.make_node("Mul", ["a", "b"], ["m"]),
                          h.make_node("Clip", ["m", "lo", "hi"], ["y"])], "mulclip",
                         [_vi("a", shape), _vi("b", shape)], [_vi("y", shape)])
    graph.initializer.extend([
        numpy_helper.from_array(np.array(0.0, dtype=np.float32), "lo"),
        numpy_helper.from_array(np.array(1.0, dtype=np.float32), "hi"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"a": _feed(shape, 210), "b": _feed(shape, 211)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_allclose(np.asarray(actual), expected, atol=1e-6, rtol=0)


def test_sub_square_fusion_matches_onnxruntime_and_guards_unsafe_patterns():
    delta = "delta"
    graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], [delta]),
         h.make_node("Pow", [delta, "exponent"], ["squared"])],
        "sub_square",
        [_vi("a", [2, 3]), _vi("b", [2, 3])],
        [_vi("squared", [2, 3])],
    )
    graph.initializer.append(
        numpy_helper.from_array(np.asarray(2.0, dtype=np.float32), "exponent")
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    plan = Plan.from_model_bytes(model.SerializeToString())
    assert _build_sub_square_fusions(plan, {"squared"}) == {0: (1, "squared")}

    feeds = {"a": _feed([2, 3], 220), "b": _feed([2, 3], 221)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_allclose(np.asarray(actual), expected, atol=1e-6, rtol=0)

    # Unsupported exponent and intermediate observability keep ordinary ONNX
    # dispatch available instead of rejecting the graph or applying the fusion.
    graph.initializer[0].CopyFrom(
        numpy_helper.from_array(np.asarray(3.0, dtype=np.float32), "exponent")
    )
    non_square = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    non_square.ir_version = 10
    assert not _build_sub_square_fusions(
        Plan.from_model_bytes(non_square.SerializeToString()), set()
    )
    assert not _build_sub_square_fusions(plan, {"delta"})

    graph.initializer[0].CopyFrom(
        numpy_helper.from_array(np.asarray(2, dtype=np.int32), "exponent")
    )
    integer_exponent = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    integer_exponent.ir_version = 10
    assert not _build_sub_square_fusions(
        Plan.from_model_bytes(integer_exponent.SerializeToString()), set()
    )

    branch_graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], ["delta"]),
         h.make_node("Pow", ["delta", "exponent"], ["squared"]),
         h.make_node("Abs", ["delta"], ["branch"])],
        "sub_square_branch",
        [_vi("a", [2, 3]), _vi("b", [2, 3])],
        [_vi("squared", [2, 3]), _vi("branch", [2, 3])],
    )
    branch_graph.initializer.append(
        numpy_helper.from_array(np.asarray(2.0, dtype=np.float32), "exponent")
    )
    branch_model = h.make_model(
        branch_graph, opset_imports=[h.make_opsetid("", 17)]
    )
    branch_model.ir_version = 10
    assert not _build_sub_square_fusions(
        Plan.from_model_bytes(branch_model.SerializeToString()), set()
    )

    dynamic_graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], ["delta"]),
         h.make_node("Pow", ["delta", "exponent"], ["squared"])],
        "sub_square_dynamic_exponent",
        [_vi("a", [2, 3]), _vi("b", [2, 3]), _vi("exponent", [1])],
        [_vi("squared", [2, 3])],
    )
    dynamic_model = h.make_model(
        dynamic_graph, opset_imports=[h.make_opsetid("", 17)]
    )
    dynamic_model.ir_version = 10
    assert not _build_sub_square_fusions(
        Plan.from_model_bytes(dynamic_model.SerializeToString()), set()
    )

    integer_graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], ["delta"]),
         h.make_node("Pow", ["delta", "exponent"], ["squared"])],
        "sub_square_integer",
        [_vi("a", [2, 3], T.INT32), _vi("b", [2, 3], T.INT32)],
        [_vi("squared", [2, 3], T.INT32)],
    )
    integer_graph.initializer.append(
        numpy_helper.from_array(np.asarray(2, dtype=np.int32), "exponent")
    )
    integer_model = h.make_model(
        integer_graph, opset_imports=[h.make_opsetid("", 17)]
    )
    integer_model.ir_version = 10
    assert not _build_sub_square_fusions(
        Plan.from_model_bytes(integer_model.SerializeToString()), set()
    )


def test_sub_square_shape_mismatch_falls_back_to_ordinary_onnx_steps():
    graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], ["delta"]),
         h.make_node("Pow", ["delta", "exponent"], ["squared"])],
        "sub_square_broadcast",
        [_vi("a", [2, 3]), _vi("b", [1, 3])],
        [_vi("squared", [2, 3])],
    )
    graph.initializer.append(
        numpy_helper.from_array(np.asarray(2.0, dtype=np.float32), "exponent")
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    feeds = {"a": _feed([2, 3], 222), "b": _feed([1, 3], 223)}
    expected = _oracle(model).run(None, feeds)[0]

    with _session(model) as session:
        calls = []
        original_run = session.module.run

        def record_run(name, **kwargs):
            calls.append(name)
            return original_run(name, **kwargs)

        session.module.run = record_run
        actual = session.run(None, feeds)[0]

    assert "nu_sub_square" not in calls
    np.testing.assert_allclose(np.asarray(actual), expected, atol=1e-6, rtol=0)


def test_binary_clip_fusion_rejects_dynamic_bounds():
    graph = h.make_graph(
        [h.make_node("Add", ["a", "b"], ["sum"]),
         h.make_node("Clip", ["sum", "low", "high"], ["y"])],
        "dynamic_clip_bounds",
        [_vi("a", [2, 3]), _vi("b", [2, 3]), _vi("low", [1]), _vi("high", [1])],
        [_vi("y", [2, 3])],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    with pytest.raises(UnsupportedONNXOperatorError, match="constant"):
        Plan.from_model_bytes(model.SerializeToString())


@pytest.mark.parametrize("backend", ["cpu", "vulkan"])
def test_add_sqrt_clip_fusion_matches_ort_on_edge_values_and_guards_liveness(backend):
    if backend == "vulkan" and _find_pool_tcm("vulkan") is None:
        pytest.skip("compile the universal Vulkan pool first")
    graph = h.make_graph(
        [h.make_node("Add", ["a", "b"], ["sum"]),
         h.make_node("Sqrt", ["sum"], ["root"]),
         h.make_node("Clip", ["root", "low", "high"], ["y"])],
        "add_sqrt_clip",
        [_vi("a", [7]), _vi("b", [7])],
        [_vi("y", [7])],
    )
    graph.initializer.extend([
        numpy_helper.from_array(np.asarray(0.0, dtype=np.float32), "low"),
        numpy_helper.from_array(np.asarray(1.5, dtype=np.float32), "high"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    plan = Plan.from_model_bytes(model.SerializeToString())
    expected_candidate = {0: (1, 2, "y", 0.0, 1.5)}
    assert _build_add_sqrt_clip_fusions(plan, {"y"}) == expected_candidate

    values = np.asarray([-4.0, -0.0, 0.0, 4.0, np.inf, -np.inf, np.nan], dtype=np.float32)
    feeds = {"a": values, "b": np.zeros_like(values)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model, backend=backend) as session:
        calls = []
        original_run = session.module.run

        def record_run(name, **kwargs):
            calls.append(name)
            return original_run(name, **kwargs)

        session.module.run = record_run
        actual = session.run(None, feeds)[0]
    assert "nu_add_sqrt_clip_broadcast" in calls
    actual = np.asarray(actual)
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0, equal_nan=True)
    assert np.array_equal(np.signbit(actual[1:3]), np.signbit(expected[1:3]))

    # A side consumer or requesting either intermediate keeps the ordinary
    # node sequence observable and disables the candidate.
    branch_graph = h.make_graph(
        [h.make_node("Add", ["a", "b"], ["sum"]),
         h.make_node("Sqrt", ["sum"], ["root"]),
         h.make_node("Clip", ["root", "low", "high"], ["y"]),
         h.make_node("Abs", ["sum"], ["branch"])],
        "add_sqrt_clip_branch",
        [_vi("a", [7]), _vi("b", [7])],
        [_vi("y", [7]), _vi("branch", [7])],
    )
    branch_graph.initializer.extend([
        numpy_helper.from_array(np.asarray(0.0, dtype=np.float32), "low"),
        numpy_helper.from_array(np.asarray(1.5, dtype=np.float32), "high"),
    ])
    branch_model = h.make_model(
        branch_graph, opset_imports=[h.make_opsetid("", 17)]
    )
    branch_model.ir_version = 10
    branch_plan = Plan.from_model_bytes(branch_model.SerializeToString())
    assert not _build_add_sqrt_clip_fusions(branch_plan, set())
    assert not _build_add_sqrt_clip_fusions(plan, {"root"})
    plan.nodes[0].domain = "com.microsoft"
    assert not _build_add_sqrt_clip_fusions(plan, {"y"})


def test_binary_two_unary_fusion_falls_back_for_non_scalar_clip_bounds():
    graph = h.make_graph(
        [h.make_node("Add", ["a", "b"], ["sum"]),
         h.make_node("Sqrt", ["sum"], ["root"]),
         h.make_node("Clip", ["root", "low", "high"], ["y"])],
        "add_sqrt_vector_clip",
        [_vi("a", [2, 2]), _vi("b", [2, 2])],
        [_vi("y", [2, 2])],
    )
    graph.initializer.extend([
        numpy_helper.from_array(np.asarray([0.0, 0.5], dtype=np.float32), "low"),
        numpy_helper.from_array(np.asarray(1.5, dtype=np.float32), "high"),
    ])
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    plan = Plan.from_model_bytes(model.SerializeToString())
    assert not _build_add_sqrt_clip_fusions(plan, set())


@pytest.mark.parametrize("backend", ["cpu", "vulkan"])
def test_sub_clip_sqrt_fusion_matches_ort_on_edge_values_and_guards_liveness(backend):
    if backend == "vulkan" and _find_pool_tcm("vulkan") is None:
        pytest.skip("compile the universal Vulkan pool first")
    graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], ["delta"]),
         h.make_node("Clip", ["delta", "low", ""], ["clipped"]),
         h.make_node("Sqrt", ["clipped"], ["y"])],
        "sub_clip_sqrt",
        [_vi("a", [7]), _vi("b", [7])],
        [_vi("y", [7])],
    )
    graph.initializer.append(
        numpy_helper.from_array(np.asarray(1e-5, dtype=np.float32), "low")
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    plan = Plan.from_model_bytes(model.SerializeToString())
    expected_candidate = {
        0: (1, 2, "y", float(np.float32(1e-5)), 3.4028234663852886e38)
    }
    assert _build_sub_clip_sqrt_fusions(plan, {"y"}) == expected_candidate

    values = np.asarray([-np.inf, -0.0, 0.0, 1e-5, 1.0, np.inf, np.nan], dtype=np.float32)
    feeds = {"a": values, "b": np.zeros_like(values)}
    expected = _oracle(model).run(None, feeds)[0]
    with _session(model, backend=backend) as session:
        calls = []
        original_run = session.module.run

        def record_run(name, **kwargs):
            calls.append(name)
            return original_run(name, **kwargs)

        session.module.run = record_run
        actual = session.run(None, feeds)[0]
    assert "nu_sub_clip_sqrt_broadcast" in calls
    np.testing.assert_allclose(
        np.asarray(actual), expected, atol=1e-6, rtol=0, equal_nan=True
    )

    branch_graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], ["delta"]),
         h.make_node("Clip", ["delta", "low", ""], ["clipped"]),
         h.make_node("Sqrt", ["clipped"], ["y"]),
         h.make_node("Abs", ["delta"], ["branch"])],
        "sub_clip_sqrt_branch",
        [_vi("a", [7]), _vi("b", [7])],
        [_vi("y", [7]), _vi("branch", [7])],
    )
    branch_graph.initializer.append(
        numpy_helper.from_array(np.asarray(1e-5, dtype=np.float32), "low")
    )
    branch_model = h.make_model(
        branch_graph, opset_imports=[h.make_opsetid("", 17)]
    )
    branch_model.ir_version = 10
    branch_plan = Plan.from_model_bytes(branch_model.SerializeToString())
    assert not _build_sub_clip_sqrt_fusions(branch_plan, set())
    assert not _build_sub_clip_sqrt_fusions(plan, {"clipped"})


def test_sub_clip_sqrt_fusion_rejects_non_scalar_and_mixed_dtype_bounds():
    graph = h.make_graph(
        [h.make_node("Sub", ["a", "b"], ["delta"]),
         h.make_node("Clip", ["delta", "low", ""], ["clipped"]),
         h.make_node("Sqrt", ["clipped"], ["y"])],
        "sub_clip_sqrt_vector_bound",
        [_vi("a", [2, 2]), _vi("b", [2, 2])],
        [_vi("y", [2, 2])],
    )
    graph.initializer.append(
        numpy_helper.from_array(np.asarray([1e-5, 2e-5], dtype=np.float32), "low")
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    model.ir_version = 10
    assert not _build_sub_clip_sqrt_fusions(
        Plan.from_model_bytes(model.SerializeToString()), set()
    )

    graph.initializer[0].CopyFrom(
        numpy_helper.from_array(np.asarray(1, dtype=np.int32), "low")
    )
    mixed_dtype = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    mixed_dtype.ir_version = 10
    assert not _build_sub_clip_sqrt_fusions(
        Plan.from_model_bytes(mixed_dtype.SerializeToString()), set()
    )
