"""Focused native operator semantics and ownership tests (CPU)."""
import math

import numpy as np
import onnx
from onnx import helper as h, numpy_helper as nh, TensorProto as T
import pytest
import taichi as ti

from taichi_vision.taichi_aot import onnx_native_graph as graph_ops
from taichi_vision.taichi_aot.onnx_native_graph import NativeGraph, UnsupportedONNXOperatorError
from taichi_vision.taichi_aot import neural_engine


@pytest.fixture(scope="module", autouse=True)
def runtime():
    ti.init(arch=ti.cpu, fast_math=False, enable_fallback=False)
    yield
    ti.sync()


def graph(nodes, inputs, outputs, constants=None):
    return h.make_graph(nodes,"test",[h.make_tensor_value_info(k,T.FLOAT,s) for k,s in inputs.items()],
                        [h.make_tensor_value_info(k,T.FLOAT,s) for k,s in outputs.items()],
                        initializer=[nh.from_array(np.asarray(v),k) for k,v in (constants or {}).items()])


@pytest.mark.parametrize("activation",["Sigmoid","Softplus"])
def test_fused_activation_is_not_assumed_relu(activation):
    x=np.array([-20,-2,-1e-4,0,1e-4,2,20,80],np.float32).reshape(1,1,2,4)
    g=graph([h.make_node("DmlFusedConv",["x","w","b"],["y"],domain="com.microsoft.dml",fused_activation=activation)],
            {"x":x.shape},{"y":x.shape},{"w":np.ones((1,1,1,1),np.float32),"b":np.zeros(1,np.float32)})
    opsets = [h.make_opsetid("", 18), h.make_opsetid("com.microsoft.dml", 1)]
    y=NativeGraph(g, opsets).run({"x":x})["y"]
    expected=1/(1+np.exp(-x.astype(np.float64))) if activation=="Sigmoid" else np.logaddexp(0,x.astype(np.float64))
    np.testing.assert_allclose(y,expected,atol=2e-7,rtol=2e-6)


def test_dml_fused_conv_activation_metadata_is_admitted_and_validated():
    x = np.ones((1, 1, 2, 2), np.float32)
    weights = np.ones((1, 1, 1, 1), np.float32)
    opsets = [h.make_opsetid("", 18), h.make_opsetid("com.microsoft.dml", 1)]

    valid = graph(
        [h.make_node(
            "DmlFusedConv", ["x", "w"], ["y"], domain="com.microsoft.dml",
            fused_activation="Sigmoid", fused_activation_domain="",
            fused_activation_since_version=13,
        )],
        {"x": x.shape}, {"y": x.shape}, {"w": weights},
    )
    model = NativeGraph(valid, opsets)
    assert model.steps[0]["activation"] == 2

    unsupported_domain = graph(
        [h.make_node(
            "DmlFusedConv", ["x", "w"], ["y"], domain="com.microsoft.dml",
            fused_activation="Sigmoid", fused_activation_domain="com.vendor",
            fused_activation_since_version=13,
        )],
        {"x": x.shape}, {"y": x.shape}, {"w": weights},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="standard ONNX domain"):
        NativeGraph(unsupported_domain, opsets)

    unavailable_version = graph(
        [h.make_node(
            "DmlFusedConv", ["x", "w"], ["y"], domain="com.microsoft.dml",
            fused_activation="Sigmoid", fused_activation_domain="",
            fused_activation_since_version=19,
        )],
        {"x": x.shape}, {"y": x.shape}, {"w": weights},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="since_version"):
        NativeGraph(unavailable_version, opsets)


def _weightnet_abs_conv_test_graph(*, activation="Sigmoid", abs_branch=False):
    x_shape = (1, 3, 2, 4)
    y_shape = (1, 1, 2, 4)
    nodes = [
        h.make_node("Abs", ["/Div_output_0"], ["/Abs_1_output_0"]),
        h.make_node(
            "DmlFusedConv",
            ["/Abs_1_output_0", "weights", "bias"],
            ["/phase_gate/phase_gate.1/Sigmoid_output_0"],
            domain="com.microsoft.dml",
            kernel_shape=[1, 1], strides=[1, 1], pads=[0, 0, 0, 0],
            group=1, fused_activation=activation,
        ),
        h.make_node(
            "Mul", ["/Div_output_0", "mask"], ["/source_branch_output_0"],
        ),
        h.make_node(
            "Identity", ["/phase_gate/phase_gate.1/Sigmoid_output_0"], ["y"],
        ),
    ]
    outputs = {"y": y_shape, "/source_branch_output_0": x_shape}
    if abs_branch:
        nodes.append(h.make_node("Identity", ["/Abs_1_output_0"], ["abs_branch"]))
        outputs["abs_branch"] = x_shape
    constants = {
        "weights": np.array([[[[0.25]], [[-0.5]], [[1.25]]]], np.float32),
        "bias": np.array([0.125], np.float32),
        "mask": np.linspace(0.5, 1.25, 2 * 4, dtype=np.float32).reshape(1, 1, 2, 4),
    }
    model_graph = graph(nodes, {"/Div_output_0": x_shape}, outputs, constants)
    opsets = [h.make_opsetid("", 18), h.make_opsetid("com.microsoft.dml", 1)]
    return model_graph, opsets


def test_weightnet_abs_conv_fusion_preserves_values_and_source_fanout():
    model_graph, opsets = _weightnet_abs_conv_test_graph()
    unfused = NativeGraph(model_graph, opsets)
    fused = NativeGraph(model_graph, opsets, enable_weightnet_abs_conv_fusion=True)
    assert unfused.fusion_stats["weightnet_abs_conv"] == 0
    assert fused.fusion_stats["weightnet_abs_conv"] == 1
    assert len(unfused.steps) == len(fused.steps) + 1
    assert fused.steps[0]["op"] == "WeightNetAbsConvSigmoid"
    assert fused.steps[0]["inputs"][0] == "/Div_output_0"

    x = np.array(
        [[[[0.0, -0.0, -1.0, 2.0], [3.0, -4.0, 0.5, -0.25]],
          [[-2.0, 1.0, -0.5, 4.0], [0.0, -3.0, 2.5, -1.5]],
          [[1.0, -2.0, 3.0, -4.0], [-0.5, 0.25, -1.0, 2.0]]]],
        np.float32,
    )
    expected = unfused.run({"/Div_output_0": x})
    actual = fused.run({"/Div_output_0": x})
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name])


@pytest.mark.parametrize("kwargs", [{"activation": "Relu"}, {"abs_branch": True}])
def test_weightnet_abs_conv_fusion_fails_closed(kwargs):
    model_graph, opsets = _weightnet_abs_conv_test_graph(**kwargs)
    model = NativeGraph(model_graph, opsets, enable_weightnet_abs_conv_fusion=True)
    assert model.fusion_stats["weightnet_abs_conv"] == 0
    assert any(step["op"] == "Abs" for step in model.steps)
    assert any(step["op"] == "DmlFusedConv" for step in model.steps)


def _weightnet_pool_abs_concat_test_graph(
        *, count_include_pad=1, abs_branch=False, swap_concat_inputs=False):
    height, width = 4, 5
    four_shape = (1, 4, height, width)
    three_shape = (1, 3, height, width)
    concat_inputs = [
        "/SpaceToDepth_output_0", "/SpaceToDepth_1_output_0",
        "/Sub_output_0", "/Abs_output_0", "/Mul_output_0", "/Mul_1_output_0",
    ]
    if swap_concat_inputs:
        concat_inputs[3], concat_inputs[4] = concat_inputs[4], concat_inputs[3]
    nodes = [
        h.make_node(
            "AveragePool", ["/Sub_output_0"], ["/AveragePool_output_0"],
            kernel_shape=[3, 3], strides=[1, 1], pads=[1, 1, 1, 1],
            count_include_pad=count_include_pad,
        ),
        h.make_node("Abs", ["/AveragePool_output_0"], ["/Abs_output_0"]),
        h.make_node("Concat", concat_inputs, ["/Concat_output_0"], axis=1),
        h.make_node("Identity", ["/Concat_output_0"], ["y"]),
    ]
    outputs = {"y": (1, 23, height, width)}
    if abs_branch:
        nodes.append(h.make_node("Identity", ["/Abs_output_0"], ["abs_tap"]))
        outputs["abs_tap"] = four_shape
    graph_inputs = {
        "/SpaceToDepth_output_0": four_shape,
        "/SpaceToDepth_1_output_0": four_shape,
        "/Sub_output_0": four_shape,
        "/Mul_output_0": four_shape,
        "/Mul_1_output_0": three_shape,
    }
    return graph(nodes, graph_inputs, outputs)


def test_weightnet_pool_abs_concat_fusion_preserves_padding_and_segment_order():
    model_graph = _weightnet_pool_abs_concat_test_graph()
    unfused = NativeGraph(
        model_graph, [h.make_opsetid("", 18)], enable_concat_gather=True,
    )
    fused = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_concat_gather=True,
        enable_weightnet_pool_abs_concat_fusion=True,
    )
    assert unfused.fusion_stats["weightnet_pool_abs_concat"] == 0
    assert fused.fusion_stats["weightnet_pool_abs_concat"] == 1
    assert len(unfused.steps) == len(fused.steps) + 2
    assert fused.steps[0]["op"] == "WeightNetConcatPoolAbsGather"
    assert fused.steps[0]["inputs"][2] == fused.steps[0]["inputs"][3]
    assert unfused.concat_stats["gather_nodes"] == 1
    assert fused.concat_stats["gather_nodes"] == 0

    rng = np.random.default_rng(210)
    feeds = {
        "/SpaceToDepth_output_0": rng.normal(size=(1, 4, 4, 5)).astype(np.float32),
        "/SpaceToDepth_1_output_0": rng.normal(size=(1, 4, 4, 5)).astype(np.float32),
        "/Sub_output_0": np.linspace(-20.0, 10.0, 4 * 4 * 5, dtype=np.float32).reshape(1, 4, 4, 5),
        "/Mul_output_0": rng.normal(size=(1, 4, 4, 5)).astype(np.float32),
        "/Mul_1_output_0": rng.normal(size=(1, 3, 4, 5)).astype(np.float32),
    }
    np.testing.assert_array_equal(fused.run(feeds)["y"], unfused.run(feeds)["y"])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"count_include_pad": 0},
        {"abs_branch": True},
        {"swap_concat_inputs": True},
    ],
)
def test_weightnet_pool_abs_concat_fusion_fails_closed(kwargs):
    model = NativeGraph(
        _weightnet_pool_abs_concat_test_graph(**kwargs),
        [h.make_opsetid("", 18)],
        enable_weightnet_pool_abs_concat_fusion=True,
    )
    assert model.fusion_stats["weightnet_pool_abs_concat"] == 0
    assert any(step["op"] == "AveragePool" for step in model.steps)
    assert any(step["op"] == "Abs" for step in model.steps)
    assert any(step["op"] == "Concat" for step in model.steps)


def test_conv_transpose_kernel_shape_matches_weight_dimensions():
    x = np.ones((1, 1, 2, 2), np.float32)
    weights = np.ones((1, 1, 8, 8), np.float32)
    valid = graph(
        [h.make_node(
            "ConvTranspose", ["x", "w"], ["y"], kernel_shape=[8, 8],
            strides=[4, 4], pads=[0, 0, 0, 0],
        )],
        {"x": x.shape}, {"y": (1, 1, 12, 12)}, {"w": weights},
    )
    model = NativeGraph(valid)
    assert model.shapes["y"] == (1, 1, 12, 12)

    mismatched = graph(
        [h.make_node(
            "ConvTranspose", ["x", "w"], ["y"], kernel_shape=[4, 8],
            strides=[4, 4], pads=[0, 0, 0, 0],
        )],
        {"x": x.shape}, {"y": (1, 1, 12, 12)}, {"w": weights},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="kernel_shape must match"):
        NativeGraph(mismatched)


@pytest.mark.parametrize(
    ("op", "domain", "opset_imports"),
    [
        ("Gelu", "com.microsoft", [h.make_opsetid("", 18)]),
        ("Gelu", "com.microsoft", [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 2)]),
        ("Relu", "com.microsoft", [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)]),
    ],
)
def test_operator_domain_and_custom_opset_fail_closed(op, domain, opset_imports):
    x = np.ones((1, 1, 2, 2), np.float32)
    g = graph(
        [h.make_node(op, ["x"], ["y"], domain=domain)],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError):
        NativeGraph(g, opset_imports)


def test_space_to_depth_channel_order():
    x=np.arange(32,dtype=np.float32).reshape(1,2,4,4)
    g=graph([h.make_node("SpaceToDepth",["x"],["y"],blocksize=2)],{"x":x.shape},{"y":(1,8,2,2)})
    expected=np.concatenate([x[:,:,dy::2,dx::2] for dy in range(2) for dx in range(2)],axis=1)
    np.testing.assert_array_equal(NativeGraph(g).run({"x":x})["y"],expected)


def test_axis_and_scalar_reduce_mean():
    x=np.arange(120,dtype=np.float32).reshape(2,3,4,5)
    g=graph([h.make_node("ReduceMean",["x","axis"],["channels"],keepdims=1),
             h.make_node("ReduceMean",["x"],["scalar"],keepdims=0)],
            {"x":x.shape},{"channels":(2,1,4,5),"scalar":()}, {"axis":np.array([1],np.int64)})
    model = NativeGraph(g)
    assert model.buffer_plan_stats["scratch_bytes"] == 4
    assert model.buffer_plan_stats["dummy_buffer_bytes"] == 4
    assert model.buffer_plan_stats["return_gpu_copy_bytes_per_call"] == 164
    result=model.run({"x":x})
    np.testing.assert_array_equal(result["channels"],x.mean(axis=1,keepdims=True))
    np.testing.assert_array_equal(result["scalar"],x.mean())


@pytest.mark.parametrize("axis", [4, -5])
def test_reduce_mean_rejects_axis_outside_onnx_rank_range(axis):
    x = np.arange(120, dtype=np.float32).reshape(2, 3, 4, 5)
    g = graph(
        [h.make_node("ReduceMean", ["x", "axis"], ["y"], keepdims=1)],
        {"x": x.shape}, {"y": x.shape},
        {"axis": np.array([axis], np.int64)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="ReduceMean axis must be"):
        NativeGraph(g)


def test_reduce_mean_normalizes_valid_negative_axis():
    x = np.arange(120, dtype=np.float32).reshape(2, 3, 4, 5)
    g = graph(
        [h.make_node("ReduceMean", ["x", "axis"], ["y"], keepdims=1)],
        {"x": x.shape}, {"y": (2, 3, 4, 1)},
        {"axis": np.array([-1], np.int64)},
    )
    model = NativeGraph(g)
    assert model.steps[0]["axes"] == [3]
    np.testing.assert_allclose(model.run({"x": x})["y"], x.mean(axis=-1, keepdims=True), rtol=0, atol=1e-6)


@pytest.mark.parametrize(
    ("op", "primitive_name", "numpy_name"),
    [("Add", "add", "add"), ("Sub", "subtract", "subtract"),
     ("Mul", "multiply", "multiply"), ("Div", "divide", "divide")],
)
def test_same_shape_binary_uses_tensor_primitive_with_exact_parity(monkeypatch, op, primitive_name, numpy_name):
    x = np.array([2, 8, -6, 12], np.float32).reshape(1, 1, 2, 2)
    rhs = np.array([1, 2, 3, 4], np.float32).reshape(x.shape)
    g = graph(
        [h.make_node(op, ["x", "rhs"], ["y"])],
        {"x": x.shape, "rhs": rhs.shape}, {"y": x.shape},
    )
    model = NativeGraph(g)
    primitive = getattr(ti.tensor, primitive_name)
    called = {"count": 0}

    def tracked_primitive(*args):
        called["count"] += 1
        return primitive(*args)

    def fail_generic(*args, **kwargs):
        raise AssertionError("same-shape binary should use ti.tensor primitive")

    monkeypatch.setattr(ti.tensor, primitive_name, tracked_primitive)
    monkeypatch.setattr(graph_ops, "_binary", fail_generic)
    actual = model.run({"x": x, "rhs": rhs})["y"]
    expected = getattr(np, numpy_name)(x, rhs)
    np.testing.assert_array_equal(actual, expected)
    assert called["count"] == 1


def test_broadcast_binary_keeps_generic_kernel_with_exact_parity(monkeypatch):
    x = np.arange(16, dtype=np.float32).reshape(1, 1, 2, 8)
    rhs = np.arange(2, 10, dtype=np.float32).reshape(1, 1, 1, 8)
    g = graph(
        [h.make_node("Mul", ["x", "rhs"], ["y"])],
        {"x": x.shape}, {"y": x.shape}, {"rhs": rhs},
    )
    model = NativeGraph(g)
    generic = graph_ops._binary
    called = {"count": 0}

    def tracked_generic(*args, **kwargs):
        called["count"] += 1
        return generic(*args, **kwargs)

    monkeypatch.setattr(graph_ops, "_binary", tracked_generic)
    actual = model.run({"x": x})["y"]
    np.testing.assert_array_equal(actual, x * rhs)
    assert called["count"] == 1


def test_full_reduce_mean_reuses_max_scratch_without_stale_chunks():
    large = np.arange(1024, dtype=np.float32).reshape(1, 1, 32, 32)
    small = np.arange(16, dtype=np.float32).reshape(1, 1, 4, 4)
    g = graph(
        [
            h.make_node("ReduceMean", ["large"], ["large_mean"], keepdims=0),
            h.make_node("ReduceMean", ["small"], ["small_mean"], keepdims=0),
        ],
        {"large": large.shape, "small": small.shape},
        {"large_mean": (), "small_mean": ()},
    )
    model = NativeGraph(g)
    assert model.buffer_plan_stats["scratch_bytes"] == 16
    result = model.run({"large": large, "small": small})
    assert model.scratch["large_mean"] is model.scratch["small_mean"]
    assert model.scratch["small_mean"].shape == (4,)
    np.testing.assert_allclose(result["large_mean"], large.mean(), rtol=0.0, atol=1e-6)
    np.testing.assert_allclose(result["small_mean"], small.mean(), rtol=0.0, atol=1e-6)


def test_failed_device_allocation_does_not_commit_partial_graph_state(monkeypatch):
    x = np.ones((1, 1, 2, 2), np.float32)
    g = graph(
        [h.make_node("Relu", ["x"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
    )
    model = NativeGraph(g)
    native_ndarray = ti.ndarray
    calls = 0

    def fail_second_allocation(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise MemoryError("injected allocation failure")
        return native_ndarray(*args, **kwargs)

    monkeypatch.setattr(ti, "ndarray", fail_second_allocation)
    with pytest.raises(MemoryError, match="injected"):
        model.allocate()
    assert model.buffers == {}
    assert model.scratch == {}
    assert model.dummy is None
    assert not model._allocated

    monkeypatch.setattr(ti, "ndarray", native_ndarray)
    model.allocate()
    assert model._allocated
    assert set(model.buffers) == {"x", "y"}


def test_reshape_allowzero_and_inferred_dimension_reject_invalid_target():
    x = np.ones((1, 1, 4, 4), np.float32)
    g = graph(
        [h.make_node("Reshape", ["x", "shape"], ["y"], allowzero=1)],
        {"x": x.shape},
        {"y": x.shape},
        {"shape": np.array([0, -1], np.int64)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="allowzero.*-1"):
        NativeGraph(g)


def test_split_rejects_elided_outputs_before_execution():
    x = np.arange(8, dtype=np.float32).reshape(1, 2, 2, 2)
    g = graph(
        [h.make_node("Split", ["x"], ["left", ""], axis=1, split=[1, 1])],
        {"x": x.shape},
        {"left": (1, 1, 2, 2)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="output elision"):
        NativeGraph(g)


def test_operator_input_arity_and_required_slots_fail_closed():
    x = np.ones((1, 1, 2, 2), np.float32)
    extra_input = graph(
        [h.make_node("Add", ["x", "x", "x"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="expects 2..2 inputs"):
        NativeGraph(extra_input)

    omitted_input = graph(
        [h.make_node("Relu", [""], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="omits a required input"):
        NativeGraph(omitted_input)

    variadic_concat = graph(
        [h.make_node("Concat", ["x", "x", "x"], ["y"], axis=1)],
        {"x": x.shape},
        {"y": (1, 3, 2, 2)},
    )
    # Concat has a variadic input schema; the generic arity guard must preserve it.
    NativeGraph(variadic_concat)


def test_graph_value_names_and_node_dependencies_fail_closed():
    x = np.ones((1, 1, 2, 2), np.float32)
    undefined_input = graph(
        [h.make_node("Relu", ["missing"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="undefined input"):
        NativeGraph(undefined_input)

    duplicate_producer = graph(
        [h.make_node("Relu", ["x"], ["y"]), h.make_node("Identity", ["x"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="newly defined"):
        NativeGraph(duplicate_producer)

    missing_output = graph(
        [h.make_node("Relu", ["x"], ["y"])],
        {"x": x.shape},
        {"missing": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="Graph output is not defined"):
        NativeGraph(missing_output)


def test_spatial_operator_parameters_fail_closed_before_lowering():
    x = np.ones((1, 1, 3, 3), np.float32)
    w = np.ones((1, 1, 1, 1), np.float32)
    invalid_conv_stride = graph(
        [h.make_node("Conv", ["x", "w"], ["y"], strides=[0, 1])],
        {"x": x.shape},
        {"y": x.shape},
        {"w": w},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="Invalid Conv"):
        NativeGraph(invalid_conv_stride)

    invalid_pool_kernel = graph(
        [h.make_node("AveragePool", ["x"], ["y"], kernel_shape=[0, 1])],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="Invalid AveragePool"):
        NativeGraph(invalid_pool_kernel)

    invalid_space_to_depth = graph(
        [h.make_node("SpaceToDepth", ["x"], ["y"], blocksize=0)],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="Invalid SpaceToDepth"):
        NativeGraph(invalid_space_to_depth)


def test_control_inputs_require_supported_constant_metadata():
    x = np.ones((1, 1, 2, 2), np.float32)
    dynamic_reshape_shape = graph(
        [h.make_node("Reshape", ["x", "shape"], ["y"])],
        {"x": x.shape, "shape": (4,)},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="must be a constant tensor"):
        NativeGraph(dynamic_reshape_shape)

    float_reshape_shape = graph(
        [h.make_node("Reshape", ["x", "shape"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
        {"shape": np.array([1, 1, 2, 2], np.float32)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="1D int64"):
        NativeGraph(float_reshape_shape)

    valid_reshape_shape = graph(
        [h.make_node("Reshape", ["x", "shape"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
        {"shape": np.array([1, 1, 2, 2], np.int64)},
    )
    reshape_model = NativeGraph(valid_reshape_shape)
    assert "shape" not in reshape_model.runtime_constant_names
    assert reshape_model.buffer_plan_stats["constant_bytes"] == 0
    reshape_model.allocate()
    assert "shape" not in reshape_model.buffers

    nonscalar_clip_bound = graph(
        [h.make_node("Clip", ["x", "low"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
        {"low": np.array([-1.0, 1.0], np.float32)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="scalar FP32"):
        NativeGraph(nonscalar_clip_bound)


def test_operator_attributes_are_explicit_and_unambiguous():
    x = np.ones((1, 1, 2, 2), np.float32)
    unknown_attribute = graph(
        [h.make_node("Relu", ["x"], ["y"], alpha=0.25)],
        {"x": x.shape},
        {"y": x.shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="unsupported attribute"):
        NativeGraph(unknown_attribute)

    missing_required_attribute = graph(
        [h.make_node("Concat", ["x", "x"], ["y"])],
        {"x": x.shape},
        {"y": (1, 2, 2, 2)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="missing required attribute"):
        NativeGraph(missing_required_attribute)

    mixed_clip_bounds = graph(
        [h.make_node("Clip", ["x", "low"], ["y"], min=-1.0)],
        {"x": x.shape},
        {"y": x.shape},
        {"low": np.array(-1.0, np.float32)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="cannot mix bound"):
        NativeGraph(mixed_clip_bounds)


def test_non_fp32_initializer_cannot_be_silently_cast_as_data():
    x = np.ones((1, 1, 2, 2), np.float32)
    integer_operand = graph(
        [h.make_node("Add", ["x", "integer"], ["y"])],
        {"x": x.shape},
        {"y": x.shape},
        {"integer": np.array(1, np.int64)},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="data input 1 must be FP32"):
        NativeGraph(integer_operand)

    integer_graph_output = graph(
        [h.make_node("Constant", [], ["y"], value=nh.from_array(np.array(1, np.int64)))],
        {},
        {"y": ()},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="Graph output must be FP32"):
        NativeGraph(integer_graph_output)


def test_transpose_conv_overlap_add():
    x=np.arange(6,dtype=np.float32).reshape(1,1,2,3)
    w=np.arange(9,dtype=np.float32).reshape(1,1,3,3)/10
    g=graph([h.make_node("ConvTranspose",["x","w"],["y"],strides=[2,2])],
            {"x":x.shape},{"y":(1,1,5,7)},{"w":w})
    expected=np.zeros((1,1,5,7),np.float32)
    for iy in range(2):
        for ix in range(3):
            expected[:,:,iy*2:iy*2+3,ix*2:ix*2+3]+=x[0,0,iy,ix]*w
    np.testing.assert_allclose(NativeGraph(g).run({"x":x})["y"],expected,atol=1e-6)


def test_optimized_conv_matches_scalar_signed_and_tail():
    rng=np.random.default_rng(48)
    x=rng.normal(size=(1,3,7,9)).astype(np.float32)
    w=rng.normal(size=(8,3,3,3)).astype(np.float32)
    b=rng.normal(size=8).astype(np.float32)
    g=graph([h.make_node("Conv",["x","w","b"],["y"],pads=[1]*4)],{"x":x.shape},{"y":(1,8,7,9)},{"w":w,"b":b})
    model=NativeGraph(g)
    actual=model.run({"x":x})["y"]
    model.optimized=False
    expected=model.run({"x":x})["y"]
    np.testing.assert_array_equal(actual,expected)


def test_resident_output_ownership_and_shape():
    x=np.arange(16,dtype=np.float32).reshape(1,1,4,4)
    g=graph([h.make_node("SpaceToDepth",["x"],["y"],blocksize=2)],{"x":x.shape},{"y":(1,4,2,2)})
    model=NativeGraph(g)
    device=ti.ndarray(ti.f32,x.shape)
    device.from_numpy(x)
    first=model.run({"x":device},return_gpu=True)["y"]
    saved=first.to_numpy()
    model.run({"x":np.zeros_like(x)})
    np.testing.assert_array_equal(first.to_numpy(),saved)
    np.testing.assert_array_equal(saved,model.run({"x":x})["y"])


def test_borrowed_resident_output_reuses_graph_storage_without_device_copies(monkeypatch):
    x=np.arange(16,dtype=np.float32).reshape(1,1,4,4)
    g=graph([h.make_node("SpaceToDepth",["x"],["y"],blocksize=2)],
            {"x":x.shape},{"y":(1,4,2,2)})
    model=NativeGraph(g)
    device=ti.ndarray(ti.f32,(x.size,))
    device.from_numpy(x.reshape(-1))

    def fail_copy(*args,**kwargs):
        raise AssertionError("borrowed resident path must not copy device input/output")
    monkeypatch.setattr("taichi_vision.taichi_aot.onnx_native_graph._upload_device",fail_copy)
    monkeypatch.setattr("taichi_vision.taichi_aot.onnx_native_graph._download_device",fail_copy)

    first=model.run({"x":device},return_gpu=True,borrowed_outputs=True)["y"]
    assert first is model.buffers["y"]
    saved=device.to_numpy()
    expected=np.concatenate([x[:,:,dy::2,dx::2] for dy in range(2) for dx in range(2)],axis=1)
    np.testing.assert_array_equal(first.to_numpy().reshape(1,4,2,2),expected)
    np.testing.assert_array_equal(device.to_numpy(),saved)

    # A borrowed result aliases executor storage and is overwritten by the next run.
    model.run({"x":np.zeros_like(x)})
    np.testing.assert_array_equal(first.to_numpy(),np.zeros((16,),np.float32))


def test_borrowed_outputs_require_device_return():
    x=np.arange(16,dtype=np.float32).reshape(1,1,4,4)
    g=graph([h.make_node("SpaceToDepth",["x"],["y"],blocksize=2)],
            {"x":x.shape},{"y":(1,4,2,2)})
    with pytest.raises(ValueError,match="requires return_gpu=True"):
        NativeGraph(g).run({"x":x},borrowed_outputs=True)
    device=ti.ndarray(ti.f32,x.shape)
    device.from_numpy(x)
    with pytest.raises(ValueError,match="must be flat 1D"):
        NativeGraph(g).run({"x":device},return_gpu=True,borrowed_outputs=True)


def test_neural_model_call_flattens_host_input_for_borrowed_output():
    x=np.arange(16,dtype=np.float32).reshape(1,1,4,4)
    g=graph([h.make_node("SpaceToDepth",["x"],["y"],blocksize=2)],
            {"x":x.shape},{"y":(1,4,2,2)})
    proto=h.make_model(g,opset_imports=[h.make_opsetid("",18)])
    model=neural_engine.onnx(proto.SerializeToString(),backend="cpu")
    result=model(x,return_gpu=True,borrowed_outputs=True)
    expected=np.concatenate([x[:,:,dy::2,dx::2] for dy in range(2) for dx in range(2)],axis=1)
    np.testing.assert_array_equal(result.to_numpy().reshape(expected.shape),expected)
    assert len(model.pool._pool[(x.size,)]) == 1


def test_liveness_planner_reuses_equal_sized_storage_after_last_consumer():
    x=np.linspace(-2,2,16,dtype=np.float32).reshape(1,1,4,4)
    g=graph([h.make_node("Relu",["x"],["a"]),
             h.make_node("Sigmoid",["a"],["b"]),
             h.make_node("Tanh",["b"],["y"])],
            {"x":x.shape},{"y":x.shape})
    model=NativeGraph(g)
    actual=model.run({"x":x})["y"]
    expected=np.tanh(1.0/(1.0+np.exp(-np.maximum(x,0)))).astype(np.float32)
    np.testing.assert_allclose(actual,expected,atol=2e-7,rtol=2e-6)
    assert model.buffers["a"] is model.buffers["y"]
    assert model.buffer_plan_stats["reused_value_count"] > 0
    assert model.buffer_plan_stats["estimated_tensor_bytes_saved"] > 0


def test_liveness_planner_pins_all_graph_outputs_until_return():
    x=np.linspace(-2,2,16,dtype=np.float32).reshape(1,1,4,4)
    g=graph([h.make_node("Relu",["x"],["intermediate"]),
             h.make_node("Tanh",["intermediate"],["y"])],
            {"x":x.shape},{"intermediate":x.shape,"y":x.shape})
    model=NativeGraph(g)
    result=model.run({"x":x})
    np.testing.assert_array_equal(result["intermediate"],np.maximum(x,0))
    np.testing.assert_allclose(result["y"],np.tanh(np.maximum(x,0)),atol=1e-7,rtol=1e-7)
    assert model.buffers["intermediate"] is not model.buffers["y"]


@pytest.mark.parametrize(
    ("axis", "input_shapes"),
    [
        (0, ((2,), (3,))),
        (-1, ((2, 1), (2, 2), (2, 3))),
        (1, ((2, 1, 2), (2, 2, 2), (2, 1, 2))),
        (1, ((2, 1, 2, 3), (2, 2, 2, 3), (2, 1, 2, 3),
             (2, 3, 2, 3), (2, 2, 2, 3), (2, 1, 2, 3))),
    ],
)
def test_concat_gather_matches_legacy_for_input_counts_axes_and_fanout(axis, input_shapes):
    input_names = [f"input_{index}" for index in range(len(input_shapes))]
    rank = len(input_shapes[0])
    normalized_axis = axis + rank if axis < 0 else axis
    output_shape = tuple(
        sum(shape[dim] for shape in input_shapes) if dim == normalized_axis else input_shapes[0][dim]
        for dim in range(rank)
    )
    inputs = {name: shape for name, shape in zip(input_names, input_shapes)}
    nodes = [
        h.make_node("Concat", input_names, ["joined"], axis=axis),
        h.make_node("Relu", ["joined"], ["relu_out"]),
        h.make_node("Sigmoid", ["joined"], ["sigmoid_out"]),
    ]
    g = graph(
        nodes,
        inputs,
        {"joined": output_shape, "relu_out": output_shape, "sigmoid_out": output_shape},
    )
    feeds = {
        name: np.linspace(-2.0 + index * 0.1, 2.0 + index * 0.1,
                          num=math.prod(shape), dtype=np.float32).reshape(shape)
        for index, (name, shape) in enumerate(zip(input_names, input_shapes))
    }
    opsets = [h.make_opsetid("", 18)]
    legacy = NativeGraph(g, opsets)
    gather = NativeGraph(g, opsets, enable_concat_gather=True)

    assert legacy.concat_stats["gather_nodes"] == 0
    assert gather.concat_stats["gather_nodes"] == 1
    assert not legacy.steps[0].get("use_concat_gather", False)
    assert gather.steps[0]["use_concat_gather"] is True

    legacy.allocate()
    gather.allocate()
    legacy_dispatches = []
    gather_dispatches = []
    legacy._dispatch(legacy.steps[0], emit=lambda kernel, *args: legacy_dispatches.append(kernel))
    gather._dispatch(gather.steps[0], emit=lambda kernel, *args: gather_dispatches.append(kernel))
    assert len(legacy_dispatches) == len(input_shapes)
    assert gather_dispatches == [graph_ops._concat_gather]

    expected_joined = np.concatenate([feeds[name] for name in input_names], axis=axis)
    expected = {
        "joined": expected_joined,
        "relu_out": np.maximum(expected_joined, 0),
        "sigmoid_out": 1.0 / (1.0 + np.exp(-expected_joined)),
    }
    legacy_outputs = legacy.run(feeds)
    gather_outputs = gather.run(feeds)
    for name in ("joined", "relu_out", "sigmoid_out"):
        np.testing.assert_array_equal(gather_outputs[name], legacy_outputs[name])
        if name == "sigmoid_out":
            np.testing.assert_allclose(legacy_outputs[name], expected[name], atol=2e-7, rtol=2e-7)
        else:
            np.testing.assert_array_equal(legacy_outputs[name], expected[name])


@pytest.mark.parametrize("axis", [3, -4])
def test_concat_rejects_axis_outside_onnx_rank(axis):
    x_shape = (2, 3, 4)
    g = graph(
        [h.make_node("Concat", ["x", "x"], ["y"], axis=axis)],
        {"x": x_shape},
        {"y": x_shape},
    )
    with pytest.raises(UnsupportedONNXOperatorError, match="Concat axis must be in \\[-3, 2\\]"):
        NativeGraph(g, [h.make_opsetid("", 18)], enable_concat_gather=True)


def test_concat_gather_falls_back_without_restricting_more_than_eight_inputs():
    input_names = [f"input_{index}" for index in range(9)]
    input_shape = (1, 1, 2, 2)
    output_shape = (1, 9, 2, 2)
    feeds = {
        name: np.full(input_shape, index - 4, dtype=np.float32)
        for index, name in enumerate(input_names)
    }
    g = graph(
        [h.make_node("Concat", input_names, ["joined"], axis=1)],
        {name: input_shape for name in input_names},
        {"joined": output_shape},
    )
    model = NativeGraph(g, [h.make_opsetid("", 18)], enable_concat_gather=True)
    assert model.concat_stats == {"gather_nodes": 0, "legacy_fallback_nodes": 1}
    expected = np.concatenate([feeds[name] for name in input_names], axis=1)
    np.testing.assert_array_equal(model.run(feeds)["joined"], expected)


def _weightnet_gate_test_graph(add_intermediate_branch=False):
    shape = (1, 1, 2, 3)
    gate_shape = (1, 1, 2, 3)
    nodes = [
        h.make_node("Conv", ["x", "gate_w", "gate_b"], ["gate_conv"]),
        h.make_node(
            "DmlFusedConv",
            ["safe_x", "safe_w", "safe_b"],
            ["safety_softplus"],
            domain="com.microsoft.dml",
            fused_activation="Softplus",
        ),
        h.make_node("Slice", ["gate_conv", "start0", "end1", "axis1", "step1"], ["slice0"]),
        h.make_node("Softplus", ["slice0"], ["softplus0"]),
        h.make_node("Add", ["softplus0", "half"], ["plus_half"]),
        h.make_node("Slice", ["gate_conv", "start1", "end2", "axis1", "step1"], ["slice1"]),
        h.make_node("Softplus", ["slice1"], ["softplus1"]),
        h.make_node("Sub", ["softplus1", "safety_softplus"], ["minus_safety"]),
        h.make_node("Mul", ["plus_half", "minus_safety"], ["gate_product"]),
        h.make_node("Sigmoid", ["gate_product"], ["gate"]),
        h.make_node("Mul", ["gate", "consumer_scale"], ["weighted"]),
    ]
    outputs = {"gate_conv": (1, 2, 2, 3), "gate": gate_shape, "weighted": gate_shape}
    if add_intermediate_branch:
        nodes.append(h.make_node("Relu", ["plus_half"], ["plus_branch"]))
        outputs["plus_branch"] = gate_shape
    constants = {
        "gate_w": np.array([1.0, -0.75], np.float32).reshape(2, 1, 1, 1),
        "gate_b": np.array([0.1, -0.2], np.float32),
        "safe_w": np.array([0.5], np.float32).reshape(1, 1, 1, 1),
        "safe_b": np.array([-0.1], np.float32),
        "start0": np.array([0], np.int64),
        "end1": np.array([1], np.int64),
        "start1": np.array([1], np.int64),
        "end2": np.array([2], np.int64),
        "axis1": np.array([1], np.int64),
        "step1": np.array([1], np.int64),
        "half": np.array(0.5, np.float32),
        "consumer_scale": np.ones(gate_shape, np.float32),
    }
    model_graph = graph(
        nodes,
        {"x": shape, "safe_x": shape},
        outputs,
        constants,
    )
    return model_graph, [h.make_opsetid("", 18), h.make_opsetid("com.microsoft.dml", 1)]


def test_weightnet_gate_fusion_is_opt_in_and_preserves_materialized_gate():
    model_graph, opsets = _weightnet_gate_test_graph()
    unfused = NativeGraph(model_graph, opsets)
    fused = NativeGraph(model_graph, opsets, enable_weightnet_gate_fusion=True)
    feeds = {
        "x": np.linspace(-2.0, 2.0, 6, dtype=np.float32).reshape(1, 1, 2, 3),
        "safe_x": np.linspace(-1.0, 1.0, 6, dtype=np.float32).reshape(1, 1, 2, 3),
    }

    assert unfused.fusion_stats["weightnet_gate"] == 0
    assert fused.fusion_stats["weightnet_gate"] == 1
    assert len(unfused.steps) == len(fused.steps) + 7
    fused_step = next(step for step in fused.steps if step["op"] == "WeightNetAdaptiveGate")
    assert fused_step["output"] == "gate"
    assert fused_step["inputs"] == ["gate_conv", "safety_softplus"]
    assert fused.buffer_plan_stats["dynamic_value_count"] < unfused.buffer_plan_stats["dynamic_value_count"]

    expected = unfused.run(feeds)
    actual = fused.run(feeds)
    assert fused.buffers["gate"] is not fused.buffers["gate_conv"]
    for name in expected:
        np.testing.assert_allclose(actual[name], expected[name], atol=2e-7, rtol=2e-6)


def test_weightnet_gate_fusion_rejects_live_private_intermediates():
    model_graph, opsets = _weightnet_gate_test_graph(add_intermediate_branch=True)
    model = NativeGraph(model_graph, opsets, enable_weightnet_gate_fusion=True)
    assert model.fusion_stats["weightnet_gate"] == 0
    assert not any(step["op"] == "WeightNetAdaptiveGate" for step in model.steps)


def test_mul_clip_fusion_is_opt_in_and_matches_unfused_graph():
    shape = (1, 1, 2, 3)
    model_graph = graph(
        [
            h.make_node("Mul", ["x", "scale"], ["product"]),
            h.make_node("Clip", ["product", "low", "high"], ["clipped"]),
            h.make_node("Relu", ["clipped"], ["relu_out"]),
        ],
        {"x": shape},
        {"product": shape, "clipped": shape, "relu_out": shape},
        {
            "scale": np.array([[[[2.0, -1.0, 0.5], [4.0, 1.0, 3.0]]]], np.float32),
            "low": np.array(0.0, np.float32),
            "high": np.array(1.0, np.float32),
        },
    )
    unfused = NativeGraph(model_graph)
    fused = NativeGraph(model_graph, enable_mul_clip_fusion=True)
    feeds = {"x": np.array([[[[0.25, 0.5, -2.0], [0.5, 1.5, 0.25]]]], np.float32)}

    assert unfused.fusion_stats["mul_clip"] == 0
    assert fused.fusion_stats["mul_clip"] == 0  # Mul output is also a graph output.
    output_barrier_graph = graph(
        list(model_graph.node),
        {"x": shape},
        {"clipped": shape, "relu_out": shape},
        {key: value for key, value in {
            "scale": np.array([[[[2.0, -1.0, 0.5], [4.0, 1.0, 3.0]]]], np.float32),
            "low": np.array(0.0, np.float32),
            "high": np.array(1.0, np.float32),
        }.items()},
    )
    fused = NativeGraph(output_barrier_graph, enable_mul_clip_fusion=True)
    unfused = NativeGraph(output_barrier_graph)
    assert fused.fusion_stats["mul_clip"] == 1
    assert len(unfused.steps) == len(fused.steps) + 1
    assert next(step for step in fused.steps if step["op"] == "FusedMulClip")["output"] == "clipped"
    expected = unfused.run(feeds)
    actual = fused.run(feeds)
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name])


def _sigmoid_product_clip_graph(*, low=np.array(0.0, np.float32),
                                high=np.array(1.0, np.float32),
                                expose_product=False):
    shape = (1, 1, 2, 4)
    outputs = {"clipped": shape}
    if expose_product:
        outputs["product"] = shape
    model_graph = graph(
        [
            h.make_node("Sigmoid", ["x"], ["sigmoid_x"]),
            h.make_node("Sigmoid", ["y"], ["sigmoid_y"]),
            h.make_node("Mul", ["sigmoid_x", "sigmoid_y"], ["product"]),
            h.make_node("Clip", ["product", "low", "high"], ["clipped"]),
        ],
        {"x": shape, "y": shape}, outputs,
        {"low": np.asarray(low), "high": np.asarray(high)},
    )
    return model_graph


def test_weightnet_sigmoid_product_clip_fusion_is_opt_in_and_exact_on_finite_values():
    shape = (1, 1, 2, 4)
    model_graph = _sigmoid_product_clip_graph()
    baseline = NativeGraph(model_graph)
    candidate = NativeGraph(
        model_graph,
        enable_weightnet_sigmoid_product_clip_fusion=True,
    )
    assert baseline.fusion_stats["weightnet_sigmoid_product_clip"] == 0
    assert candidate.fusion_stats["weightnet_sigmoid_product_clip"] == 1
    assert len(candidate.steps) == len(baseline.steps) - 1
    fused_step = next(
        step for step in candidate.steps
        if step["op"] == "WeightNetSigmoidProduct"
    )
    assert fused_step["inputs"] == ["sigmoid_x", "sigmoid_y"]
    assert fused_step["output"] == "clipped"
    assert candidate.buffer_plan_stats["dynamic_value_count"] < baseline.buffer_plan_stats["dynamic_value_count"]

    values = np.array(
        [-np.inf, -100.0, -2.0, -0.0, 0.0, 2.0, 100.0, np.inf],
        dtype=np.float32,
    ).reshape(shape)
    feeds = {"x": values, "y": values[::-1].copy()}
    expected = baseline.run(feeds)["clipped"]
    actual = candidate.run(feeds)["clipped"]
    np.testing.assert_array_equal(actual, expected)
    assert np.all((actual >= 0.0) & (actual <= 1.0))


def test_weightnet_sigmoid_product_clip_preserves_nan_and_matches_ort_cpu():
    ort = pytest.importorskip("onnxruntime")
    shape = (1, 1, 2, 4)
    model_graph = _sigmoid_product_clip_graph()
    candidate = NativeGraph(
        model_graph,
        enable_weightnet_sigmoid_product_clip_fusion=True,
    )
    model = h.make_model(model_graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = min(model.ir_version, 10)
    oracle = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"],
    )
    x = np.array(
        [-np.inf, -100.0, -2.0, -0.0, 0.0, 2.0, 100.0, np.inf],
        dtype=np.float32,
    ).reshape(shape)
    y = np.array(
        [np.inf, 100.0, 2.0, 0.0, -0.0, -2.0, -100.0, -np.inf],
        dtype=np.float32,
    ).reshape(shape)
    x[0, 0, 0, 0] = np.nan
    feeds = {"x": x, "y": y}
    actual = candidate.run(feeds)["clipped"]
    expected = oracle.run(["clipped"], feeds)[0]
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0, equal_nan=True)
    assert np.isnan(actual[0, 0, 0, 0])


def test_weightnet_sigmoid_product_clip_fusion_fails_closed_for_non_sigmoid_and_live_values():
    graph_kwargs = {}
    wrong_bounds = NativeGraph(
        _sigmoid_product_clip_graph(high=np.array(2.0, np.float32)),
        enable_weightnet_sigmoid_product_clip_fusion=True,
    )
    live_product = NativeGraph(
        _sigmoid_product_clip_graph(expose_product=True),
        enable_weightnet_sigmoid_product_clip_fusion=True,
    )
    assert wrong_bounds.fusion_stats["weightnet_sigmoid_product_clip"] == 0
    assert live_product.fusion_stats["weightnet_sigmoid_product_clip"] == 0

    shape = (1, 1, 2, 4)
    non_sigmoid = graph(
        [
            h.make_node("Relu", ["x"], ["relu_x"]),
            h.make_node("Sigmoid", ["y"], ["sigmoid_y"]),
            h.make_node("Mul", ["relu_x", "sigmoid_y"], ["product"]),
            h.make_node("Clip", ["product", "low", "high"], ["clipped"]),
        ],
        {"x": shape, "y": shape}, {"clipped": shape},
        {
            "low": np.array(0.0, np.float32),
            "high": np.array(1.0, np.float32),
        },
    )
    rejected = NativeGraph(
        non_sigmoid,
        enable_weightnet_sigmoid_product_clip_fusion=True,
    )
    assert rejected.fusion_stats["weightnet_sigmoid_product_clip"] == 0
    assert [step["op"] for step in rejected.steps][-2:] == ["Mul", "Clip"]


def test_weightnet_sigmoid_product_clip_accepts_fused_sigmoid_conv_output():
    shape = (1, 1, 2, 2)
    model_graph = graph(
        [
            h.make_node(
                "DmlFusedConv", ["x", "weights", "bias"], ["fused_sigmoid"],
                domain="com.microsoft.dml", fused_activation="Sigmoid",
            ),
            h.make_node("Sigmoid", ["y"], ["sigmoid_y"]),
            h.make_node("Mul", ["fused_sigmoid", "sigmoid_y"], ["product"]),
            h.make_node("Clip", ["product", "low", "high"], ["clipped"]),
        ],
        {"x": shape, "y": shape}, {"clipped": shape},
        {
            "weights": np.ones((1, 1, 1, 1), np.float32),
            "bias": np.zeros((1,), np.float32),
            "low": np.array(0.0, np.float32),
            "high": np.array(1.0, np.float32),
        },
    )
    opsets = [h.make_opsetid("", 18), h.make_opsetid("com.microsoft.dml", 1)]
    baseline = NativeGraph(model_graph, opsets)
    candidate = NativeGraph(
        model_graph, opsets,
        enable_weightnet_sigmoid_product_clip_fusion=True,
    )
    assert candidate.fusion_stats["weightnet_sigmoid_product_clip"] == 1
    feeds = {"x": np.zeros(shape, np.float32), "y": np.ones(shape, np.float32)}
    np.testing.assert_array_equal(
        candidate.run(feeds)["clipped"], baseline.run(feeds)["clipped"],
    )


def _constant_pow2_test_graph(*, exponent=np.array(2.0, np.float32), dynamic=False):
    shape = (1, 1, 2, 4)
    nodes = [h.make_node("Pow", ["x", "exponent"], ["y"])]
    inputs = {"x": shape}
    constants = {}
    if dynamic:
        inputs["exponent"] = (1,)
    else:
        constants["exponent"] = exponent
    return graph(nodes, inputs, {"y": shape}, constants)


def test_constant_pow2_lowering_is_opt_in_and_matches_ort_cpu():
    ort = pytest.importorskip("onnxruntime")
    model_graph = _constant_pow2_test_graph()
    unfused = NativeGraph(model_graph, [h.make_opsetid("", 18)])
    lowered = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_constant_pow2_mul_lowering=True,
    )
    assert unfused.fusion_stats["constant_pow2_mul_lowering"] == 0
    assert lowered.fusion_stats["constant_pow2_mul_lowering"] == 1
    assert unfused.steps[0]["op"] == "Pow"
    assert lowered.steps[0]["op"] == "Square"
    assert lowered.steps[0]["inputs"] == ["x"]
    assert lowered.steps[0]["lowered_from"] == "Pow(base, scalar_fp32(2.0))"
    assert "exponent" in unfused.runtime_constant_names
    assert "exponent" not in lowered.runtime_constant_names

    values = np.array(
        [-3.0, -0.0, np.nextafter(np.float32(0.0), np.float32(1.0)),
         np.nextafter(np.float32(1.0), np.float32(2.0)), 0.5, 2.0,
         1.0e20, np.inf],
        dtype=np.float32,
    ).reshape(1, 1, 2, 4)
    feeds = {"x": values}
    model = h.make_model(model_graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = min(model.ir_version, 10)
    oracle = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"],
    )
    expected = oracle.run(["y"], feeds)[0]
    actual = lowered.run(feeds)["y"]
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0, equal_nan=True)


@pytest.mark.parametrize(
    ("exponent", "dynamic"),
    [
        (np.array([2.0], np.float32), False),
        (np.array(2.0000002, np.float32), False),
        (np.array(-2.0, np.float32), False),
        (None, True),
    ],
)
def test_constant_pow2_lowering_fails_closed_for_non_scalar_or_non_two_exponent(
        exponent, dynamic):
    model_graph = _constant_pow2_test_graph(exponent=exponent, dynamic=dynamic)
    model = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_constant_pow2_mul_lowering=True,
    )
    assert model.fusion_stats["constant_pow2_mul_lowering"] == 0
    assert model.steps[0]["op"] == "Pow"


def _weightnet_full_range_slice_test_graph(
        *, end2=4, end3=4, start2=0, start3=0,
        graph_output_slice=False, branch_slice=False):
    shape = (1, 1, 4, 4)
    start2, end2, _ = slice(start2, end2).indices(shape[2])
    shape2 = (shape[0], shape[1], max(0, end2 - start2), shape[3])
    start3, end3, _ = slice(start3, end3).indices(shape2[3])
    shape3 = (shape2[0], shape2[1], shape2[2], max(0, end3 - start3))
    nodes = [
        h.make_node("Slice", ["/ConvTranspose_output_0", "starts2", "ends2", "axes2", "steps2"],
                    ["/Slice_2_output_0"]),
        h.make_node("Slice", ["/Slice_2_output_0", "starts3", "ends3", "axes3", "steps3"],
                    ["/Slice_3_output_0"]),
        h.make_node("Identity", ["/Slice_3_output_0"], ["y"]),
    ]
    constants = {
        "starts2": np.array([start2], np.int64),
        "ends2": np.array([end2], np.int64),
        "axes2": np.array([2], np.int64),
        "steps2": np.array([1], np.int64),
        "starts3": np.array([start3], np.int64),
        "ends3": np.array([end3], np.int64),
        "axes3": np.array([3], np.int64),
        "steps3": np.array([1], np.int64),
    }
    outputs = {"y": shape3}
    if graph_output_slice:
        outputs["slice_output"] = shape2
        nodes.append(h.make_node("Identity", ["/Slice_2_output_0"], ["slice_output"]))
    if branch_slice:
        nodes.append(h.make_node("Relu", ["/Slice_3_output_0"], ["slice_branch"]))
        outputs["slice_branch"] = shape3
    return graph(nodes, {"/ConvTranspose_output_0": shape}, outputs, constants)


def test_weightnet_full_range_slices_alias_without_changing_values():
    model_graph = _weightnet_full_range_slice_test_graph()
    unfused = NativeGraph(model_graph, [h.make_opsetid("", 18)])
    aliased = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_weightnet_full_range_slice_alias=True,
    )
    assert unfused.fusion_stats["weightnet_full_range_slice_alias"] == 0
    assert aliased.fusion_stats["weightnet_full_range_slice_alias"] == 2
    assert len(unfused.steps) == len(aliased.steps) + 2
    assert "/Slice_2_output_0" not in aliased.buffer_plan
    assert "/Slice_3_output_0" not in aliased.buffer_plan
    assert aliased.aliases["/Slice_2_output_0"] == "/ConvTranspose_output_0"
    assert aliased.aliases["/Slice_3_output_0"] == "/Slice_2_output_0"
    values = np.arange(16, dtype=np.float32).reshape(1, 1, 4, 4)
    feeds = {"/ConvTranspose_output_0": values}
    np.testing.assert_array_equal(aliased.run(feeds)["y"], unfused.run(feeds)["y"])


def _weightnet_transpose_mul_clip_test_graph(
        *, slice2_end=12, clip_low=0.0, branch_mul=False,
        expose_conv_output=False):
    x_shape = (1, 1, 2, 3)
    conv_shape = (1, 1, 12, 16)
    slice_shape = (1, 1, slice2_end, 16)
    scale = np.linspace(
        -0.5, 2.0, slice2_end * 16, dtype=np.float32,
    ).reshape(1, 1, slice2_end, 16)
    nodes = [
        h.make_node(
            "ConvTranspose", ["x", "weights"], ["/ConvTranspose_output_0"],
            kernel_shape=[8, 8], strides=[4, 4], pads=[0, 0, 0, 0],
        ),
        h.make_node(
            "Slice",
            ["/ConvTranspose_output_0", "starts2", "ends2", "axes2", "steps2"],
            ["/Slice_2_output_0"],
        ),
        h.make_node(
            "Slice",
            ["/Slice_2_output_0", "starts3", "ends3", "axes3", "steps3"],
            ["/Slice_3_output_0"],
        ),
        h.make_node("Mul", ["/Slice_3_output_0", "inv_hann_norm"], ["/Mul_6_output_0"]),
        h.make_node(
            "Clip", ["/Mul_6_output_0", "clip_low", "clip_high"], ["/Clip_3_output_0"],
        ),
        h.make_node("Identity", ["/Clip_3_output_0"], ["y"]),
    ]
    outputs = {"y": slice_shape}
    if branch_mul:
        nodes.append(h.make_node("Identity", ["/Mul_6_output_0"], ["mul_branch"]))
        outputs["mul_branch"] = slice_shape
    if expose_conv_output:
        nodes.append(h.make_node("Identity", ["/ConvTranspose_output_0"], ["conv_tap"]))
        outputs["conv_tap"] = conv_shape
    constants = {
        "weights": np.linspace(-0.25, 0.25, 8 * 8, dtype=np.float32).reshape(1, 1, 8, 8),
        "inv_hann_norm": scale,
        "starts2": np.array([0], np.int64),
        "ends2": np.array([slice2_end], np.int64),
        "axes2": np.array([2], np.int64),
        "steps2": np.array([1], np.int64),
        "starts3": np.array([0], np.int64),
        "ends3": np.array([16], np.int64),
        "axes3": np.array([3], np.int64),
        "steps3": np.array([1], np.int64),
        "clip_low": np.array(clip_low, np.float32),
        "clip_high": np.array(1.0, np.float32),
    }
    return graph(nodes, {"x": x_shape}, outputs, constants)


def test_weightnet_conv_transpose_mul_clip_fusion_preserves_operation_order():
    model_graph = _weightnet_transpose_mul_clip_test_graph()
    unfused = NativeGraph(model_graph, [h.make_opsetid("", 18)])
    fused = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_weightnet_conv_transpose_mul_clip_fusion=True,
    )
    assert unfused.fusion_stats["weightnet_conv_transpose_mul_clip"] == 0
    assert fused.fusion_stats["weightnet_conv_transpose_mul_clip"] == 1
    assert len(unfused.steps) == len(fused.steps) + 4
    assert fused.steps[0]["op"] == "WeightNetConvTransposeMulClip"
    assert fused.steps[0]["output"] == "/Clip_3_output_0"
    assert (fused.buffer_plan_stats["estimated_tensor_bytes_after"]
            < unfused.buffer_plan_stats["estimated_tensor_bytes_after"])

    x = np.array([[[[-1.0, -0.5, 0.0], [0.25, 0.75, 1.0]]]], np.float32)
    expected = unfused.run({"x": x})["y"]
    actual = fused.run({"x": x})["y"]
    np.testing.assert_array_equal(actual, expected)
    assert np.all(actual >= 0.0) and np.all(actual <= 1.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"slice2_end": 11},
        {"clip_low": -1.0},
        {"branch_mul": True},
        {"expose_conv_output": True},
    ],
)
def test_weightnet_conv_transpose_mul_clip_fusion_fails_closed(kwargs):
    model = NativeGraph(
        _weightnet_transpose_mul_clip_test_graph(**kwargs),
        [h.make_opsetid("", 18)],
        enable_weightnet_conv_transpose_mul_clip_fusion=True,
    )
    assert model.fusion_stats["weightnet_conv_transpose_mul_clip"] == 0
    assert any(step["op"] == "ConvTranspose" for step in model.steps)
    assert any(step["op"] == "Mul" for step in model.steps)
    assert any(step["op"] == "Clip" for step in model.steps)


@pytest.mark.parametrize(
    ("graph_kwargs", "expected_count"),
    [
        ({"end2": 3}, 0),
        ({"end3": 3}, 0),
        ({"start2": 1}, 0),
        ({"start3": 1}, 0),
        ({"graph_output_slice": True}, 0),
        ({"branch_slice": True}, 0),
    ],
)
def test_weightnet_full_range_slice_alias_fails_closed(graph_kwargs, expected_count):
    model_graph = _weightnet_full_range_slice_test_graph(**graph_kwargs)
    model = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_weightnet_full_range_slice_alias=True,
    )
    assert model.fusion_stats["weightnet_full_range_slice_alias"] == expected_count
    if expected_count == 0:
        assert sum(step["op"] == "Slice" for step in model.steps) == 2


def _weightnet_concat_conv_gelu_test_graph(*, fanout=False, output_channels=4):
    height = width = 2
    source_shapes = ((1, 20, height, width), (1, 2, height, width), (1, 1, height, width))
    concat_shape = (1, 23, height, width)
    conv_shape = (1, output_channels, height, width)
    nodes = [
        h.make_node("Concat", ["features", "gate", "stats"], ["/Concat_2_output_0"], axis=1),
        h.make_node(
            "Conv", ["/Concat_2_output_0", "weights", "bias"],
            ["/tile_reasoner/tile_reasoner.0/Conv_output_0"],
            kernel_shape=[1, 1], strides=[1, 1], pads=[0, 0, 0, 0], group=1,
        ),
        h.make_node(
            "Gelu", ["/tile_reasoner/tile_reasoner.0/Conv_output_0"],
            ["/tile_reasoner/tile_reasoner.1/Mul_1_output_0"], domain="com.microsoft",
        ),
    ]
    outputs = {"/tile_reasoner/tile_reasoner.1/Mul_1_output_0": conv_shape}
    if fanout:
        nodes.append(h.make_node("Relu", ["/Concat_2_output_0"], ["concat_branch"]))
        outputs["concat_branch"] = concat_shape
    constants = {
        "weights": np.linspace(-0.08, 0.07, output_channels * 23, dtype=np.float32).reshape(output_channels, 23, 1, 1),
        "bias": np.linspace(-0.2, 0.2, output_channels, dtype=np.float32),
    }
    model_graph = graph(
        nodes,
        {"features": source_shapes[0], "gate": source_shapes[1], "stats": source_shapes[2]},
        outputs,
        constants,
    )
    return model_graph


def test_weightnet_concat_conv_gelu_fusion_matches_unfused_and_ort_cpu():
    ort = pytest.importorskip("onnxruntime")
    model_graph = _weightnet_concat_conv_gelu_test_graph()
    opsets = [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)]
    unfused = NativeGraph(model_graph, opsets, enable_conv_gelu_fusion=True)
    fused = NativeGraph(
        model_graph,
        opsets,
        enable_conv_gelu_fusion=True,
        enable_weightnet_concat_conv_gelu_fusion=True,
    )
    assert unfused.fusion_stats["weightnet_concat_conv_gelu"] == 0
    assert fused.fusion_stats["weightnet_concat_conv_gelu"] == 1
    assert len(unfused.steps) == len(fused.steps) + 1
    assert "/Concat_2_output_0" not in fused.buffer_plan
    fused_step = next(step for step in fused.steps if step["op"] == "WeightNetConcatConvGelu")
    assert fused_step["inputs"] == ["features", "gate", "stats", "weights", "bias"]
    assert fused_step["source_channels"] == (20, 2, 1)

    rng = np.random.default_rng(20261018)
    feeds = {
        "features": rng.normal(0.2, 0.7, (1, 20, 2, 2)).astype(np.float32),
        "gate": rng.normal(-0.1, 0.5, (1, 2, 2, 2)).astype(np.float32),
        "stats": np.array([[[[0.2, -0.4], [0.7, -0.9]]]], dtype=np.float32),
    }
    output_name = "/tile_reasoner/tile_reasoner.1/Mul_1_output_0"
    expected_native = unfused.run(feeds)[output_name]
    actual = fused.run(feeds)[output_name]
    np.testing.assert_allclose(actual, expected_native, rtol=2e-6, atol=2e-7)

    model = h.make_model(model_graph, opset_imports=opsets)
    model.ir_version = min(model.ir_version, 10)
    oracle = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"],
    )
    expected_ort = oracle.run([output_name], feeds)[0]
    np.testing.assert_allclose(actual, expected_ort, rtol=2e-5, atol=2e-6)


def test_weightnet_concat_conv_gelu_fusion_fails_closed_for_concat_fanout():
    model_graph = _weightnet_concat_conv_gelu_test_graph(fanout=True)
    model = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)],
        enable_conv_gelu_fusion=True,
        enable_weightnet_concat_conv_gelu_fusion=True,
    )
    assert model.fusion_stats["weightnet_concat_conv_gelu"] == 0
    assert any(step["op"] == "Concat" for step in model.steps)


def _weightnet_pow2_reduce_mean_test_graph(
        *, exponent=np.array(2.0, np.float32), axes=np.array([1], np.int64),
        keepdims=1, graph_output_pow=False, branch_pow=False):
    base_shape = (1, 4, 2, 2)
    normalized_axes = {int(axis) % len(base_shape) for axis in np.asarray(axes).ravel()}
    output_shape = (
        tuple(1 if axis in normalized_axes else dim for axis, dim in enumerate(base_shape))
        if keepdims else tuple(dim for axis, dim in enumerate(base_shape) if axis not in normalized_axes)
    )
    nodes = [
        h.make_node("SpaceToDepth", ["x"], ["/SpaceToDepth_output_0"], blocksize=2),
        h.make_node("Pow", ["/SpaceToDepth_output_0", "exponent"], ["/Pow_1_output_0"]),
        h.make_node(
            "ReduceMean", ["/Pow_1_output_0", "axes"], ["/ReduceMean_1_output_0"],
            keepdims=keepdims,
        ),
    ]
    outputs = {"/ReduceMean_1_output_0": output_shape}
    if graph_output_pow:
        outputs["pow_out"] = base_shape
        nodes.append(h.make_node("Identity", ["/Pow_1_output_0"], ["pow_out"]))
    if branch_pow:
        nodes.append(h.make_node("Relu", ["/Pow_1_output_0"], ["pow_branch"]))
        outputs["pow_branch"] = base_shape
    model_graph = graph(
        nodes,
        {"x": (1, 1, 4, 4)},
        outputs,
        {"exponent": exponent, "axes": axes},
    )
    return model_graph


def test_weightnet_pow2_reduce_mean_fusion_is_opt_in_and_matches_ort_cpu():
    ort = pytest.importorskip("onnxruntime")
    model_graph = _weightnet_pow2_reduce_mean_test_graph()
    unfused = NativeGraph(model_graph, [h.make_opsetid("", 18)])
    fused = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_weightnet_pow2_reduce_mean_fusion=True,
    )
    assert unfused.fusion_stats["weightnet_pow2_reduce_mean"] == 0
    assert fused.fusion_stats["weightnet_pow2_reduce_mean"] == 1
    assert len(unfused.steps) == len(fused.steps) + 1
    assert "/Pow_1_output_0" in unfused.buffer_plan
    assert "/Pow_1_output_0" not in fused.buffer_plan
    assert "exponent" in unfused.runtime_constant_names
    assert "exponent" not in fused.runtime_constant_names
    fused_step = next(
        step for step in fused.steps if step["op"] == "WeightNetSquareReduceMean"
    )
    assert fused_step["inputs"] == ["/SpaceToDepth_output_0"]
    assert fused_step["output"] == "/ReduceMean_1_output_0"

    values = np.array(
        [-2.0, -0.0, 0.125, 1.25, 0.0, -0.5, 3.0, 0.25,
         np.nextafter(np.float32(0.0), np.float32(1.0)), 1.0, -1.0, 2.0,
         4.0, -3.0, 0.75, -0.25],
        dtype=np.float32,
    ).reshape(1, 1, 4, 4)
    feeds = {"x": values}
    expected = unfused.run(feeds)["/ReduceMean_1_output_0"]
    actual = fused.run(feeds)["/ReduceMean_1_output_0"]
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0)

    model = h.make_model(model_graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = min(model.ir_version, 10)
    oracle = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"],
    )
    expected_ort = oracle.run(["/ReduceMean_1_output_0"], feeds)[0]
    np.testing.assert_allclose(actual, expected_ort, rtol=0.0, atol=0.0)


@pytest.mark.parametrize(
    ("graph_kwargs", "expected_count"),
    [
        ({"exponent": np.array([2.0], np.float32)}, 0),
        ({"exponent": np.array(2.0000002, np.float32)}, 0),
        ({"axes": np.array([0], np.int64)}, 0),
        ({"keepdims": 0}, 0),
        ({"graph_output_pow": True}, 0),
        ({"branch_pow": True}, 0),
    ],
)
def test_weightnet_pow2_reduce_mean_fusion_fails_closed(graph_kwargs, expected_count):
    model_graph = _weightnet_pow2_reduce_mean_test_graph(**graph_kwargs)
    model = NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        enable_weightnet_pow2_reduce_mean_fusion=True,
    )
    assert model.fusion_stats["weightnet_pow2_reduce_mean"] == expected_count
    if expected_count == 0:
        assert not any(step["op"] == "WeightNetSquareReduceMean" for step in model.steps)


def test_neural_factory_enables_square_reduce_mean_only_for_cuda(monkeypatch):
    model_graph = _weightnet_pow2_reduce_mean_test_graph()
    proto = h.make_model(model_graph, opset_imports=[h.make_opsetid("", 18)])
    raw_model = proto.SerializeToString()
    monkeypatch.setattr(neural_engine, "_ensure_taichi_initialized", lambda arch: None)

    monkeypatch.setattr(neural_engine, "_resolve_backend", lambda backend: ti.cuda)
    cuda_model = neural_engine.onnx(raw_model, backend="cuda")
    assert cuda_model._native_graph.fusion_stats["weightnet_pow2_reduce_mean"] == 1

    monkeypatch.setattr(neural_engine, "_resolve_backend", lambda backend: ti.cpu)
    cpu_model = neural_engine.onnx(raw_model, backend="cpu")
    assert cpu_model._native_graph.fusion_stats["weightnet_pow2_reduce_mean"] == 0


def _weightnet_pow2_sub_clip_sqrt_test_graph(
        *, pow_shape=(1, 1, 2, 4), average_shape=(1, 1, 2, 4),
        exponent=None, clip_min=None, include_clip_max=False,
        reverse_sub=False, graph_outputs=(), branch_edges=()):
    pow_shape = tuple(pow_shape)
    average_shape = tuple(average_shape)
    pow_output_shape = pow_shape
    sub_shape = tuple(np.broadcast_shapes(pow_output_shape, average_shape))
    nodes = [
        h.make_node(
            "AveragePool", ["pow_input"], ["/AveragePool_2_output_0"],
            kernel_shape=[1, 1], strides=[1, 1],
        ),
        h.make_node(
            "Pow", ["/AveragePool_2_output_0", "exponent"], ["/Pow_2_output_0"],
        ),
        h.make_node(
            "AveragePool", ["average_input"], ["/AveragePool_3_output_0"],
            kernel_shape=[1, 1], strides=[1, 1],
        ),
        h.make_node(
            "Sub",
            (["/Pow_2_output_0", "/AveragePool_3_output_0"] if reverse_sub
             else ["/AveragePool_3_output_0", "/Pow_2_output_0"]),
            ["/Sub_2_output_0"],
        ),
        h.make_node(
            "Clip",
            (["/Sub_2_output_0", "clip_min", "clip_max"] if include_clip_max
             else ["/Sub_2_output_0", "clip_min", ""]),
            ["/Clip_1_output_0"],
        ),
        h.make_node("Sqrt", ["/Clip_1_output_0"], ["/Sqrt_1_output_0"]),
    ]
    shapes = {
        "/AveragePool_2_output_0": pow_output_shape,
        "/Pow_2_output_0": pow_output_shape,
        "/AveragePool_3_output_0": average_shape,
        "/Sub_2_output_0": sub_shape,
        "/Clip_1_output_0": sub_shape,
        "/Sqrt_1_output_0": sub_shape,
    }
    outputs = {"/Sqrt_1_output_0": sub_shape}
    for name in graph_outputs:
        outputs[name] = shapes[name]
    for index, name in enumerate(branch_edges):
        branch_name = f"branch_{index}"
        nodes.append(h.make_node("Relu", [name], [branch_name]))
        outputs[branch_name] = shapes[name]
    constants = {
        "exponent": np.asarray(2.0, np.float32) if exponent is None else np.asarray(exponent),
        "clip_min": np.asarray(1.0e-5, np.float32) if clip_min is None else np.asarray(clip_min),
    }
    if include_clip_max:
        constants["clip_max"] = np.asarray(np.inf, np.float32)
    model_graph = graph(
        nodes,
        {"pow_input": pow_shape, "average_input": average_shape},
        outputs,
        constants,
    )
    return model_graph, shapes


def _weightnet_pow2_sub_clip_sqrt_model(model_graph, **kwargs):
    return NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        **kwargs,
    )


def test_weightnet_pow2_sub_clip_sqrt_fusion_is_opt_in_and_matches_ort_cpu():
    ort = pytest.importorskip("onnxruntime")
    shape = (1, 1, 2, 4)
    model_graph, _ = _weightnet_pow2_sub_clip_sqrt_test_graph()
    unfused = _weightnet_pow2_sub_clip_sqrt_model(model_graph)
    fused = _weightnet_pow2_sub_clip_sqrt_model(
        model_graph, enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
    )
    assert unfused.fusion_stats["weightnet_pow2_sub_clip_sqrt"] == 0
    assert fused.fusion_stats["weightnet_pow2_sub_clip_sqrt"] == 1
    assert len(unfused.steps) == len(fused.steps) + 3
    assert fused.buffer_plan_stats["dynamic_value_count"] == (
        unfused.buffer_plan_stats["dynamic_value_count"] - 3
    )
    # The allocator may already reuse slots for the three serial intermediates.
    assert fused.buffer_plan_stats["dynamic_slot_count"] <= (
        unfused.buffer_plan_stats["dynamic_slot_count"]
    )
    assert not any(
        name in fused.buffer_plan
        for name in ("/Pow_2_output_0", "/Sub_2_output_0", "/Clip_1_output_0")
    )
    fused_step = next(
        step for step in fused.steps if step["op"] == "WeightNetPow2SubClipSqrt"
    )
    assert fused_step["inputs"] == ["/AveragePool_3_output_0", "/AveragePool_2_output_0"]
    assert fused_step["output"] == "/Sqrt_1_output_0"

    pow_input = np.array(
        [-2.0, -0.0, np.nextafter(np.float32(0.0), np.float32(1.0)), 1.0e20,
         0.0, 1.0, 0.5, -1.25],
        np.float32,
    ).reshape(shape)
    average_input = np.array(
        [4.00001, 1.0e-5, 2.0e-5, 0.0, 1.0001e-5, 1.05, 0.2501, 2.0],
        np.float32,
    ).reshape(shape)
    feeds = {"pow_input": pow_input, "average_input": average_input}
    actual = fused.run(feeds)["/Sqrt_1_output_0"]
    native_reference = unfused.run(feeds)["/Sqrt_1_output_0"]
    np.testing.assert_allclose(actual, native_reference, rtol=1e-6, atol=1e-7)

    model = h.make_model(model_graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = min(model.ir_version, 10)
    session = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"],
    )
    ort_reference = session.run(["/Sqrt_1_output_0"], feeds)[0]
    np.testing.assert_allclose(actual, ort_reference, rtol=1e-6, atol=1e-7)


def test_weightnet_pow2_sub_clip_sqrt_fusion_matches_edge_values():
    model_graph, _ = _weightnet_pow2_sub_clip_sqrt_test_graph()
    unfused = _weightnet_pow2_sub_clip_sqrt_model(model_graph)
    fused = _weightnet_pow2_sub_clip_sqrt_model(
        model_graph, enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
    )
    pow_input = np.array(
        [-0.0, 0.0, np.nextafter(np.float32(0.0), np.float32(1.0)), 1.0e20,
         np.inf, -np.inf, np.nan, -2.0],
        np.float32,
    ).reshape(1, 1, 2, 4)
    average_input = np.array(
        [-0.0, 0.0, 2.0e-5, 0.0, np.inf, 0.0, 1.0, 0.0],
        np.float32,
    ).reshape(1, 1, 2, 4)
    feeds = {"pow_input": pow_input, "average_input": average_input}
    actual = fused.run(feeds)["/Sqrt_1_output_0"]
    expected = unfused.run(feeds)["/Sqrt_1_output_0"]
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0, equal_nan=True)


@pytest.mark.parametrize(
    ("graph_kwargs", "error"),
    [
        ({"exponent": np.array([2.0], np.float32)}, None),
        ({"exponent": np.array(2.0000002, np.float32)}, None),
        ({"reverse_sub": True}, None),
        ({"clip_min": np.array(1.0e-4, np.float32)}, None),
        ({"include_clip_max": True}, None),
        ({"average_shape": (1, 1, 1, 4)}, None),
        ({"exponent": np.array(2.0, np.float64)}, "FP32"),
    ],
)
def test_weightnet_pow2_sub_clip_sqrt_fusion_fails_closed_for_semantics_and_shapes(
        graph_kwargs, error):
    model_graph, _ = _weightnet_pow2_sub_clip_sqrt_test_graph(**graph_kwargs)
    if error:
        with pytest.raises(UnsupportedONNXOperatorError, match=error):
            _weightnet_pow2_sub_clip_sqrt_model(
                model_graph, enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
            )
        return
    model = _weightnet_pow2_sub_clip_sqrt_model(
        model_graph, enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
    )
    assert model.fusion_stats["weightnet_pow2_sub_clip_sqrt"] == 0
    assert not any(step["op"] == "WeightNetPow2SubClipSqrt" for step in model.steps)


@pytest.mark.parametrize(
    ("graph_output", "branch_edge"),
    [
        ("/Pow_2_output_0", None),
        ("/Sub_2_output_0", None),
        ("/Clip_1_output_0", None),
        (None, "/Pow_2_output_0"),
        (None, "/Sub_2_output_0"),
        (None, "/Clip_1_output_0"),
    ],
)
def test_weightnet_pow2_sub_clip_sqrt_fusion_fails_closed_for_live_intermediates(
        graph_output, branch_edge):
    model_graph, _ = _weightnet_pow2_sub_clip_sqrt_test_graph(
        graph_outputs=(() if graph_output is None else (graph_output,)),
        branch_edges=(() if branch_edge is None else (branch_edge,)),
    )
    model = _weightnet_pow2_sub_clip_sqrt_model(
        model_graph, enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
    )
    assert model.fusion_stats["weightnet_pow2_sub_clip_sqrt"] == 0
    assert not any(step["op"] == "WeightNetPow2SubClipSqrt" for step in model.steps)


def test_weightnet_pow2_sub_clip_sqrt_fusion_rejects_aliased_intermediates():
    model_graph, _ = _weightnet_pow2_sub_clip_sqrt_test_graph()
    model = _weightnet_pow2_sub_clip_sqrt_model(model_graph)
    model.aliases["/Pow_2_output_0"] = "/AveragePool_2_output_0"
    assert model._fuse_weightnet_pow2_sub_clip_sqrt() == 0
    assert not any(step["op"] == "WeightNetPow2SubClipSqrt" for step in model.steps)


def test_weightnet_pow2_sub_clip_sqrt_fusion_rejects_sqrt_shape_mismatch():
    model_graph, _ = _weightnet_pow2_sub_clip_sqrt_test_graph()
    model = _weightnet_pow2_sub_clip_sqrt_model(model_graph)
    model.shapes["/Sqrt_1_output_0"] = (1, 1, 2, 3)
    assert model._fuse_weightnet_pow2_sub_clip_sqrt() == 0
    assert not any(step["op"] == "WeightNetPow2SubClipSqrt" for step in model.steps)


def test_weightnet_pow2_sub_clip_sqrt_fusion_rejects_non_fp32_base():
    model_graph, _ = _weightnet_pow2_sub_clip_sqrt_test_graph()
    next(value for value in model_graph.input if value.name == "pow_input").type.tensor_type.elem_type = T.DOUBLE
    with pytest.raises(UnsupportedONNXOperatorError, match="Static FP32 input required"):
        _weightnet_pow2_sub_clip_sqrt_model(
            model_graph, enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
        )


def _weightnet_stats_tanh_test_graph(
        *, shape=(2, 4, 8, 8), axes=(1,), scale=8.0,
        scale_shape=(), count_include_pad=1, pool_kernel=(4, 4),
        graph_outputs=(), branch_edges=()):
    n, channels, height, width = shape
    reduce_shape = list(shape)
    for axis in axes:
        reduce_shape[axis] = 1
    reduce_shape = tuple(reduce_shape)
    pool_h = (reduce_shape[2] - pool_kernel[0]) // 2 + 1
    pool_w = (reduce_shape[3] - pool_kernel[1]) // 2 + 1
    pool_shape = (reduce_shape[0], reduce_shape[1], pool_h, pool_w)
    nodes = [
        h.make_node("Sub", ["left", "right"], ["/Sub_3_output_0"]),
        h.make_node("Mul", ["/Sub_3_output_0", "/Sub_3_output_0"], ["/Mul_2_output_0"]),
        h.make_node(
            "ReduceMean", ["/Mul_2_output_0", "/Constant_12_output_0"],
            ["/ReduceMean_3_output_0"], keepdims=1, noop_with_empty_axes=0,
        ),
        h.make_node("Sqrt", ["/ReduceMean_3_output_0"], ["/Sqrt_2_output_0"]),
        h.make_node(
            "AveragePool", ["/Sqrt_2_output_0"], ["/AveragePool_4_output_0"],
            kernel_shape=list(pool_kernel), strides=[2, 2], pads=[0, 0, 0, 0],
            ceil_mode=0, count_include_pad=count_include_pad, auto_pad="NOTSET",
        ),
        h.make_node(
            "Mul", ["/AveragePool_4_output_0", "/Constant_20_output_0"],
            ["/Mul_3_output_0"],
        ),
        h.make_node("Tanh", ["/Mul_3_output_0"], ["/Tanh_output_0"]),
    ]
    shapes = {
        "/Sub_3_output_0": tuple(shape),
        "/Mul_2_output_0": tuple(shape),
        "/ReduceMean_3_output_0": reduce_shape,
        "/Sqrt_2_output_0": reduce_shape,
        "/AveragePool_4_output_0": pool_shape,
        "/Mul_3_output_0": pool_shape,
        "/Tanh_output_0": pool_shape,
    }
    for index, name in enumerate(branch_edges):
        branch = f"branch_{index}"
        nodes.append(h.make_node("Relu", [name], [branch]))
        shapes[branch] = shapes[name]
    outputs = {"/Tanh_output_0": pool_shape}
    for name in graph_outputs:
        outputs[name] = shapes[name]
    model_graph = graph(
        nodes,
        {"left": shape, "right": shape},
        outputs,
        {
            "/Constant_12_output_0": np.asarray(axes, np.int64),
            "/Constant_20_output_0": np.asarray(scale, np.float32).reshape(scale_shape),
        },
    )
    return model_graph, shapes


def _weightnet_stats_tanh_model(model_graph, **kwargs):
    return NativeGraph(
        model_graph,
        [h.make_opsetid("", 18)],
        **kwargs,
    )


def test_weightnet_stats_tanh_fusion_is_opt_in_and_matches_ort_cpu():
    ort = pytest.importorskip("onnxruntime")
    model_graph, shapes = _weightnet_stats_tanh_test_graph(
        branch_edges=("/Sub_3_output_0",),
    )
    unfused = _weightnet_stats_tanh_model(model_graph)
    fused = _weightnet_stats_tanh_model(
        model_graph, enable_weightnet_stats_tanh_fusion=True,
    )
    assert unfused.fusion_stats["weightnet_stats_tanh"] == 0
    assert fused.fusion_stats["weightnet_stats_tanh"] == 1
    assert len(unfused.steps) == len(fused.steps) + 5
    assert fused.buffer_plan_stats["dynamic_value_count"] == (
        unfused.buffer_plan_stats["dynamic_value_count"] - 5
    )
    assert not any(
        name in fused.buffer_plan
        for name in (
            "/Mul_2_output_0", "/ReduceMean_3_output_0", "/Sqrt_2_output_0",
            "/AveragePool_4_output_0", "/Mul_3_output_0",
        )
    )
    assert any(step["output"] == "/Sub_3_output_0" for step in fused.steps)
    fused_step = next(step for step in fused.steps if step["op"] == "WeightNetStatsTanh")
    assert fused_step["inputs"] == ["/Sub_3_output_0"]
    assert fused_step["output"] == "/Tanh_output_0"
    assert fused.shapes["/Tanh_output_0"] == shapes["/Tanh_output_0"]

    rng = np.random.default_rng(8104)
    feeds = {
        "left": rng.normal(0.0, 0.3, shapes["/Sub_3_output_0"]).astype(np.float32),
        "right": rng.normal(0.0, 0.3, shapes["/Sub_3_output_0"]).astype(np.float32),
    }
    expected = unfused.run(feeds)
    actual = fused.run(feeds)
    for name in expected:
        np.testing.assert_allclose(actual[name], expected[name], rtol=2e-6, atol=2e-7)

    model = h.make_model(model_graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = min(model.ir_version, 10)
    session = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"],
    )
    ort_reference = session.run(list(expected), feeds)
    for name, value in zip(expected, ort_reference):
        np.testing.assert_allclose(actual[name], value, rtol=2e-6, atol=2e-7)


def test_weightnet_stats_tanh_algebraic_simplification_matches_ort_cpu():
    ort = pytest.importorskip("onnxruntime")
    model_graph, shapes = _weightnet_stats_tanh_test_graph(shape=(1, 4, 8, 8))
    fused = _weightnet_stats_tanh_model(
        model_graph, enable_weightnet_stats_tanh_fusion=True,
    )
    simplified = _weightnet_stats_tanh_model(
        model_graph,
        enable_weightnet_stats_tanh_fusion=True,
        enable_weightnet_stats_tanh_algebraic_simplification=True,
    )
    assert fused.fusion_stats["weightnet_stats_tanh_algebraic_simplification"] == 0
    assert simplified.fusion_stats["weightnet_stats_tanh"] == 1
    assert simplified.fusion_stats["weightnet_stats_tanh_algebraic_simplification"] == 1
    simplified_step = next(
        step for step in simplified.steps if step["op"] == "WeightNetStatsTanh"
    )
    assert simplified_step["simplify_power_of_two_scale"] is True

    rng = np.random.default_rng(20261019)
    left = rng.normal(0.0, 0.3, shapes["/Sub_3_output_0"]).astype(np.float32)
    right = np.zeros_like(left)
    left[0, 0, 0, 0] = np.nextafter(np.float32(0.0), np.float32(1.0))
    left[0, 1, 0, 1] = -0.0
    left[0, 2, 1, 1] = np.float32(1.0e10)
    left[0, 3, 1, 2] = -np.float32(1.0e10)
    feeds = {"left": left, "right": right}

    expected = fused.run(feeds)["/Tanh_output_0"]
    actual = simplified.run(feeds)["/Tanh_output_0"]
    np.testing.assert_allclose(actual, expected, rtol=2e-6, atol=2e-7)

    model = h.make_model(model_graph, opset_imports=[h.make_opsetid("", 18)])
    model.ir_version = min(model.ir_version, 10)
    session = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"],
    )
    ort_reference = session.run(["/Tanh_output_0"], feeds)[0]
    np.testing.assert_allclose(actual, ort_reference, rtol=2e-6, atol=2e-7)


def test_weightnet_stats_tanh_algebraic_simplification_fails_closed_without_fusion():
    model_graph, _ = _weightnet_stats_tanh_test_graph(count_include_pad=0)
    model = _weightnet_stats_tanh_model(
        model_graph,
        enable_weightnet_stats_tanh_fusion=True,
        enable_weightnet_stats_tanh_algebraic_simplification=True,
    )
    assert model.fusion_stats["weightnet_stats_tanh"] == 0
    assert model.fusion_stats["weightnet_stats_tanh_algebraic_simplification"] == 0
    assert not any(step.get("simplify_power_of_two_scale") for step in model.steps)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"axes": (0,)},
        {"scale": 4.0},
        {"scale_shape": (1,)},
        {"count_include_pad": 0},
        {"pool_kernel": (3, 4)},
        {"graph_outputs": ("/ReduceMean_3_output_0",)},
        {"branch_edges": ("/Mul_2_output_0",)},
    ],
)
def test_weightnet_stats_tanh_fusion_fails_closed(kwargs):
    model_graph, _ = _weightnet_stats_tanh_test_graph(**kwargs)
    model = _weightnet_stats_tanh_model(
        model_graph, enable_weightnet_stats_tanh_fusion=True,
    )
    assert model.fusion_stats["weightnet_stats_tanh"] == 0
    assert not any(step["op"] == "WeightNetStatsTanh" for step in model.steps)


def test_weightnet_stats_tanh_fusion_matches_edge_values():
    model_graph, shapes = _weightnet_stats_tanh_test_graph(shape=(1, 4, 8, 8))
    unfused = _weightnet_stats_tanh_model(model_graph)
    fused = _weightnet_stats_tanh_model(
        model_graph, enable_weightnet_stats_tanh_fusion=True,
    )
    left = np.zeros(shapes["/Sub_3_output_0"], np.float32)
    right = np.zeros_like(left)
    left[0, 0, 0, 0] = np.nextafter(np.float32(0.0), np.float32(1.0))
    left[0, 1, 0, 1] = -0.0
    left[0, 2, 1, 0] = np.float32(1.0e10)
    left[0, 3, 1, 1] = -np.float32(1.0e10)
    feeds = {"left": left, "right": right}
    actual = fused.run(feeds)["/Tanh_output_0"]
    expected = unfused.run(feeds)["/Tanh_output_0"]
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0, equal_nan=True)


def test_opengl_renderer_vendor_guard_rejects_wrong_icd():
    neural_engine._validate_opengl_context(
        {"vendor":"NVIDIA Corporation","renderer":"GeForce MX150"},"NVIDIA"
    )
    with pytest.raises(RuntimeError,match="renderer mismatch.*requested 'NVIDIA'"):
        neural_engine._validate_opengl_context(
            {"vendor":"Intel","renderer":"Intel UHD Graphics 620"},"NVIDIA"
        )
    with pytest.raises(RuntimeError,match="renderer mismatch.*unavailable"):
        neural_engine._validate_opengl_context(
            {"vendor":None,"renderer":None},"NVIDIA"
        )


def test_archive_repeats_admission_and_preserves_typed_constants(tmp_path):
    x=np.arange(16,dtype=np.float32).reshape(1,1,4,4)
    g=graph([h.make_node("SpaceToDepth",["x"],["y"],blocksize=2)],{"x":x.shape},{"y":(1,4,2,2)})
    proto=h.make_model(g,opset_imports=[h.make_opsetid("",18)])
    model=neural_engine.onnx(proto.SerializeToString(),backend="cpu")
    path=tmp_path/"graph.tcm"
    model.save_tcm(path)
    loaded=neural_engine.load_neural_tcm(path,arch="cpu")
    np.testing.assert_array_equal(model.run(None,{"x":x})[0],loaded.run(None,{"x":x})[0])


def test_unsupported_node_fails_before_allocating():
    g=graph([h.make_node("Nonexistent",["x"],["y"])],{"x":(1,1,2,2)},{"y":(1,1,2,2)})
    with pytest.raises(UnsupportedONNXOperatorError,match="Nonexistent"):
        NativeGraph(g)


def test_wrong_shape_and_dtype_rejected():
    g=graph([h.make_node("SpaceToDepth",["x"],["y"],blocksize=2)],{"x":(1,1,4,4)},{"y":(1,4,2,2)})
    model=NativeGraph(g)
    with pytest.raises(ValueError,match="expected float32"):
        model.run({"x":np.ones((1,1,4,4),np.float64)})
    with pytest.raises(ValueError,match="expected float32"):
        model.run({"x":np.ones((1,1,2,2),np.float32)})


def test_application_native_failure_is_not_replaced_with_heuristic():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import infer_single_support_weight_map
    class FailingNativeSession:
        runtime="taichi_cuda"
        def get_inputs(self):
            return []
        def get_providers(self):
            return ["TaichiVision_CUDAExecutionProvider"]
        def run(self,*args):
            raise RuntimeError("native execution failed")
    x=np.ones((1,4,4),np.float32)
    with pytest.raises(RuntimeError,match="native execution failed"):
        infer_single_support_weight_map(FailingNativeSession(),x,x,tile_size=4,overlap=0)


def _conv_gelu_test_graph(outputs=None):
    x_shape = (1, 1, 2, 4)
    y_shape = (1, 4, 2, 4)
    nodes = [
        h.make_node("Conv", ["x", "w", "b"], ["conv_out"]),
        h.make_node("Gelu", ["conv_out"], ["gelu_out"], domain="com.microsoft"),
    ]
    if outputs is None:
        outputs = {"gelu_out": y_shape}
    return graph(
        nodes,
        {"x": x_shape},
        outputs,
        {
            "w": np.array([0.25, -0.5, 1.0, 2.0], np.float32).reshape(4, 1, 1, 1),
            "b": np.array([-0.1, 0.0, 0.2, -0.4], np.float32),
        },
    )


def test_conv_gelu_fusion_is_opt_in_and_matches_unfused_exactly():
    x = np.linspace(-2.0, 2.0, 8, dtype=np.float32).reshape(1, 1, 2, 4)
    g = _conv_gelu_test_graph()
    opsets = [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)]
    unfused = NativeGraph(g, opsets)
    fused = NativeGraph(g, opsets, enable_conv_gelu_fusion=True)

    assert unfused.fusion_stats["conv_gelu"] == 0
    assert fused.fusion_stats["conv_gelu"] == 1
    assert len(unfused.steps) == len(fused.steps) + 1
    assert fused.steps[0]["activation"] == 4
    assert fused.aliases["gelu_out"] == "conv_out"
    assert fused.buffer_plan_stats["dynamic_value_count"] == (
        unfused.buffer_plan_stats["dynamic_value_count"] - 1
    )
    assert fused.buffer_plan_stats["estimated_tensor_bytes_after"] <= (
        unfused.buffer_plan_stats["estimated_tensor_bytes_after"]
    )

    expected = unfused.run({"x": x})["gelu_out"]
    actual = fused.run({"x": x})["gelu_out"]
    np.testing.assert_array_equal(actual, expected)
    assert fused.buffers["gelu_out"] is fused.buffers["conv_out"]


def test_conv_gelu_fusion_fails_closed_for_branch_and_conv_graph_output():
    shape = (1, 4, 2, 4)
    x = np.ones((1, 1, 2, 4), np.float32)
    branch = _conv_gelu_test_graph({"gelu_out": shape, "branch_out": shape})
    branch.node.append(h.make_node("Relu", ["conv_out"], ["branch_out"]))
    branched = NativeGraph(
        branch,
        [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)],
        enable_conv_gelu_fusion=True,
    )
    assert branched.fusion_stats["conv_gelu"] == 0
    assert len(branched.steps) == 3

    graph_output = _conv_gelu_test_graph({"conv_out": shape, "gelu_out": shape})
    output_barrier = NativeGraph(
        graph_output,
        [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)],
        enable_conv_gelu_fusion=True,
    )
    assert output_barrier.fusion_stats["conv_gelu"] == 0
    assert len(output_barrier.steps) == 2
    assert x.shape == (1, 1, 2, 4)


def test_conv_gelu_fusion_preserves_gelu_graph_output_and_two_consumers():
    shape = (1, 4, 2, 4)
    x = np.linspace(-2.0, 2.0, 8, dtype=np.float32).reshape(1, 1, 2, 4)
    g = _conv_gelu_test_graph({
        "gelu_out": shape,
        "relu_out": shape,
        "sigmoid_out": shape,
    })
    g.node.extend([
        h.make_node("Relu", ["gelu_out"], ["relu_out"]),
        h.make_node("Sigmoid", ["gelu_out"], ["sigmoid_out"]),
    ])
    opsets = [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)]
    unfused = NativeGraph(g, opsets)
    fused = NativeGraph(g, opsets, enable_conv_gelu_fusion=True)

    assert fused.fusion_stats["conv_gelu"] == 1
    assert fused.aliases["gelu_out"] == "conv_out"

    expected = unfused.run({"x": x})
    actual = fused.run({"x": x})
    assert fused.buffers["gelu_out"] is fused.buffers["conv_out"]
    for name in ("gelu_out", "relu_out", "sigmoid_out"):
        np.testing.assert_array_equal(actual[name], expected[name])


def test_conv_gelu_fusion_fails_closed_when_shapes_disagree():
    g = _conv_gelu_test_graph()
    model = NativeGraph(
        g,
        [h.make_opsetid("", 18), h.make_opsetid("com.microsoft", 1)],
    )
    model.shapes["gelu_out"] = (1, 4, 2, 3)
    assert model._fuse_conv_gelu() == 0
    assert len(model.steps) == 2


@pytest.mark.parametrize(
    ("profile", "member", "expected_nodes"),
    [
        ("cpu_512", "weightnet_512_cpu_1c_fp32.onnx", 82),
        ("cpu_1024", "weightnet_1024_cpu_1c_fp32.onnx", 82),
        ("gpu_512", "weightnet_512_gpu_1c_fp32.onnx", 70),
        ("gpu_1024", "weightnet_1024_gpu_1c_fp32.onnx", 70),
        ("ui_gpu_batch2", "pixel_refine_desktop/ui/data/models/weightnet_512_gpu_2b_1c_fp32.onnx", 70),
    ],
)
def test_weightnet_profiles_match_all_five_conv_gelu_pairs(profile, member, expected_nodes):
    from pathlib import Path
    import zipfile

    root = Path(__file__).resolve().parents[3]
    if profile == "ui_gpu_batch2":
        path = root / member
        if not path.is_file():
            pytest.skip(f"Optional source profile is not present: {path}")
        raw = path.read_bytes()
    else:
        bundle = root / "database/Learning_Model/weightNet/weightnet_master.bundle"
        if not bundle.is_file():
            pytest.skip(f"WeightNet source bundle is not present: {bundle}")
        with zipfile.ZipFile(bundle) as archive:
            try:
                raw = archive.read(member)
            except KeyError:
                pytest.skip(f"WeightNet source member is not present: {member}")

    proto = onnx.load_model_from_string(raw)
    assert len(proto.graph.node) == expected_nodes
    unfused = NativeGraph(proto.graph, proto.opset_import)
    if profile.startswith("gpu_") or profile == "ui_gpu_batch2":
        variance_fused = NativeGraph(
            proto.graph,
            proto.opset_import,
            enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
        )
        assert variance_fused.fusion_stats["weightnet_pow2_sub_clip_sqrt"] == 1, profile
        assert len(unfused.steps) == len(variance_fused.steps) + 3, profile
        stats_fused = NativeGraph(
            proto.graph,
            proto.opset_import,
            enable_weightnet_stats_tanh_fusion=True,
        )
        assert stats_fused.fusion_stats["weightnet_stats_tanh"] == 1, profile
        assert len(unfused.steps) == len(stats_fused.steps) + 5, profile
    fused = NativeGraph(
        proto.graph,
        proto.opset_import,
        enable_conv_gelu_fusion=True,
    )
    assert fused.fusion_stats["conv_gelu"] == 5, profile
    assert len(unfused.steps) - len(fused.steps) == 5, profile
    if profile.startswith("gpu_") or profile == "ui_gpu_batch2":
        conv_gelu_only = NativeGraph(
            proto.graph,
            proto.opset_import,
            enable_conv_gelu_fusion=True,
        )
        conv_gelu_concat = NativeGraph(
            proto.graph,
            proto.opset_import,
            enable_conv_gelu_fusion=True,
            enable_concat_gather=True,
        )
        concat_count = sum(step["op"] == "Concat" for step in conv_gelu_only.steps)
        assert concat_count == 3, profile
        assert conv_gelu_concat.concat_stats == {
            "gather_nodes": concat_count,
            "legacy_fallback_nodes": 0,
        }, profile
        assert len(conv_gelu_concat.steps) == len(conv_gelu_only.steps), profile
        assert conv_gelu_concat.buffer_plan_stats == conv_gelu_only.buffer_plan_stats, profile

        experimental = NativeGraph(
            proto.graph,
            proto.opset_import,
            enable_conv_gelu_fusion=True,
            enable_concat_gather=True,
            enable_weightnet_gate_fusion=True,
            enable_mul_clip_fusion=True,
        )
        expected_mul_clip = 1 if profile == "ui_gpu_batch2" else 2
        assert experimental.fusion_stats["weightnet_gate"] == 1, profile
        assert experimental.fusion_stats["mul_clip"] == expected_mul_clip, profile
        assert experimental.concat_stats["gather_nodes"] == 3, profile
