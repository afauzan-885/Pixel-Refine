"""End-to-end: a real ONNX graph runs through the Rust session.

The gate for the whole chain — plan construction, shape inference, wire encoding,
lowering, primitives — because each link can be individually correct and the
combination still wrong.
"""

from __future__ import annotations

import numpy as np
import pytest

onnx = pytest.importorskip("onnx")
native = pytest.importorskip("taichi.taichi_python")
from onnx import TensorProto, helper, numpy_helper  # noqa: E402

from taichi_vision.taichi_algorithm.neural.universal import plan_wire  # noqa: E402
from taichi_vision.taichi_algorithm.neural.universal.plan import Plan  # noqa: E402


def _model(nodes, inputs, outputs, initializers=()):
    graph = helper.make_graph(list(nodes), "e2e", list(inputs), list(outputs), list(initializers))
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("ai.onnx", 18)])
    model.ir_version = 8
    return model.SerializeToString()


def _io(name, shape, elem=TensorProto.FLOAT):
    return helper.make_tensor_value_info(name, elem, shape)


def _session(model_bytes, feeds):
    plan = Plan.from_model_bytes(model_bytes)
    shapes = {name: np.asarray(value).shape for name, value in feeds.items()}
    blob = plan_wire.encode_plan(plan, shapes)
    session = native.NeuralSession(blob, backend="cpu")
    for name, value in plan_wire.constant_values(plan).items():
        session.set_constant(name, np.ascontiguousarray(value))
    for name, value in feeds.items():
        session.set_input(name, np.ascontiguousarray(value))
    return session


def test_add_then_relu_matches_numpy():
    model = _model(
        [
            helper.make_node("Add", ["x", "bias"], ["sum"]),
            helper.make_node("Relu", ["sum"], ["y"]),
        ],
        [_io("x", [4]), _io("bias", [4])],
        [_io("y", [4])],
    )
    x = np.asarray([-2.0, -0.5, 0.5, 2.0], dtype=np.float32)
    bias = np.asarray([1.0, -1.0, 0.0, 0.5], dtype=np.float32)
    session = _session(model, {"x": x, "bias": bias})
    out = session.run()["y"]
    np.testing.assert_allclose(out, np.maximum(x + bias, 0), rtol=1e-6, atol=1e-6)


def test_a_chain_of_elementwise_operators_is_correct():
    model = _model(
        [
            helper.make_node("Mul", ["x", "x"], ["sq"]),
            helper.make_node("Sqrt", ["sq"], ["mag"]),
            helper.make_node("Sigmoid", ["mag"], ["y"]),
        ],
        [_io("x", [5])],
        [_io("y", [5])],
    )
    x = np.asarray([-3.0, -1.0, 0.0, 1.5, 4.0], dtype=np.float32)
    session = _session(model, {"x": x})
    out = session.run()["y"]
    expected = 1.0 / (1.0 + np.exp(-np.abs(x)))
    np.testing.assert_allclose(out, expected, rtol=1e-6, atol=1e-6)


def test_broadcast_against_an_initializer_is_correct():
    scale = numpy_helper.from_array(np.asarray([2.0], dtype=np.float32), "scale")
    model = _model(
        [helper.make_node("Add", ["x", "scale"], ["y"])],
        [_io("x", [3])],
        [_io("y", [3])],
        [scale],
    )
    x = np.asarray([1.0, 2.0, 3.0], dtype=np.float32)
    session = _session(model, {"x": x})
    np.testing.assert_allclose(session.run()["y"], x + 2.0, rtol=1e-6)


def test_missing_ops_is_reported_before_running():
    # `Softmax` has no lowering in this build. It must be reported up front, not
    # discovered halfway through a run that already wrote intermediate buffers.
    model = _model(
        [helper.make_node("Softmax", ["x"], ["y"], axis=1)],
        [_io("x", [2, 3])],
        [_io("y", [2, 3])],
    )
    plan = Plan.from_model_bytes(model)
    blob = plan_wire.encode_plan(plan, {"x": (2, 3)})
    session = native.NeuralSession(blob, backend="cpu")
    assert "Softmax" in session.missing_ops
    session.set_input("x", np.zeros((2, 3), dtype=np.float32))
    with pytest.raises(RuntimeError, match="cannot execute"):
        session.run()


def test_a_wrongly_shaped_feed_is_refused():
    model = _model(
        [helper.make_node("Relu", ["x"], ["y"])],
        [_io("x", [4])],
        [_io("y", [4])],
    )
    session = _session(model, {"x": np.zeros(4, dtype=np.float32)})
    with pytest.raises(ValueError, match="expects shape"):
        session.set_input("x", np.zeros(3, dtype=np.float32))


def test_a_constant_slot_cannot_be_fed_as_an_input():
    scale = numpy_helper.from_array(np.asarray([2.0], dtype=np.float32), "scale")
    model = _model(
        [helper.make_node("Mul", ["x", "scale"], ["y"])],
        [_io("x", [2])],
        [_io("y", [2])],
        [scale],
    )
    plan = Plan.from_model_bytes(model)
    blob = plan_wire.encode_plan(plan, {"x": (2,)})
    session = native.NeuralSession(blob, backend="cpu")
    with pytest.raises(ValueError, match="only inputs"):
        session.set_input("scale", np.zeros(1, dtype=np.float32))


def test_repeated_runs_are_identical():
    model = _model(
        [
            helper.make_node("Div", ["x", "two"], ["half"]),
            helper.make_node("Tanh", ["half"], ["y"]),
        ],
        [_io("x", [32])],
        [_io("y", [32])],
        [numpy_helper.from_array(np.asarray([2.0], dtype=np.float32), "two")],
    )
    rng = np.random.default_rng(3)
    x = rng.uniform(-4, 4, size=32).astype(np.float32)
    session = _session(model, {"x": x})
    first = session.run()["y"]
    for _ in range(50):
        again = session.run()["y"]
        np.testing.assert_array_equal(
            first.view(np.uint32), again.view(np.uint32), "output changed between runs"
        )


def test_transpose_through_a_plan_matches_numpy():
    model = _model(
        [helper.make_node("Transpose", ["x"], ["y"], perm=[1, 0])],
        [_io("x", [2, 3])],
        [_io("y", [3, 2])],
    )
    x = np.arange(6, dtype=np.float32).reshape(2, 3)
    session = _session(model, {"x": x})
    np.testing.assert_array_equal(session.run()["y"], x.T)


def test_reshape_through_a_plan_matches_numpy():
    shape_init = numpy_helper.from_array(
        np.asarray([3, 2], dtype=np.int64), "shape"
    )
    model = _model(
        [helper.make_node("Reshape", ["x", "shape"], ["y"])],
        [_io("x", [2, 3])],
        [_io("y", [3, 2])],
        [shape_init],
    )
    x = np.arange(6, dtype=np.float32).reshape(2, 3)
    session = _session(model, {"x": x})
    np.testing.assert_array_equal(session.run()["y"], x.reshape(3, 2))


def test_a_chain_of_movement_and_math_is_correct():
    # Transpose then a per-element op: proves the two families share buffers
    # correctly rather than each assuming a different layout.
    model = _model(
        [
            helper.make_node("Transpose", ["x"], ["t"], perm=[1, 0]),
            helper.make_node("Relu", ["t"], ["y"]),
        ],
        [_io("x", [2, 3])],
        [_io("y", [3, 2])],
    )
    x = np.asarray([[-1.0, 2.0, -3.0], [4.0, -5.0, 6.0]], dtype=np.float32)
    session = _session(model, {"x": x})
    expected = np.maximum(x.T, 0)
    np.testing.assert_array_equal(session.run()["y"], expected)


def test_reduce_mean_through_a_plan_matches_numpy():
    model = _model(
        [helper.make_node("ReduceMean", ["x"], ["y"], axes=[1], keepdims=1)],
        [_io("x", [2, 3, 2])],
        [_io("y", [2, 1, 2])],
    )
    rng = np.random.default_rng(13)
    x = rng.uniform(-2, 2, size=(2, 3, 2)).astype(np.float32)
    session = _session(model, {"x": x})
    np.testing.assert_allclose(
        session.run()["y"], np.mean(x, axis=1, keepdims=True), rtol=1e-6, atol=1e-6
    )


def test_average_pool_through_a_plan_matches_numpy():
    model = _model(
        [
            helper.make_node(
                "AveragePool", ["x"], ["y"], kernel_shape=[2, 2], strides=[2, 2]
            )
        ],
        [_io("x", [1, 1, 4, 4])],
        [_io("y", [1, 1, 2, 2])],
    )
    x = np.arange(16, dtype=np.float32).reshape(1, 1, 4, 4)
    session = _session(model, {"x": x})
    # `(n, c, 2, 2, 2, 2)` splits each spatial axis into blocks and offsets, so the
    # within-block axes are 3 and 5 — averaging over 2 and 4 would pick the wrong
    # elements and still look plausible.
    expected = x.reshape(1, 1, 2, 2, 2, 2).mean(axis=(3, 5))
    np.testing.assert_allclose(session.run()["y"], expected, rtol=1e-6, atol=1e-6)


def test_average_pool_through_a_plan_matches_numpy_with_padding():
    # Padding exercises the window clipping, which is where an off-by-one shows up
    # as a different divisor rather than as an out-of-range read.
    model = _model(
        [
            helper.make_node(
                "AveragePool",
                ["x"],
                ["y"],
                kernel_shape=[2, 2],
                strides=[1, 1],
                pads=[1, 1, 1, 1],
            )
        ],
        [_io("x", [1, 1, 3, 3])],
        [_io("y", [1, 1, 4, 4])],
    )
    x = np.arange(9, dtype=np.float32).reshape(1, 1, 3, 3)
    session = _session(model, {"x": x})
    padded = np.pad(x, ((0, 0), (0, 0), (1, 1), (1, 1)))
    expected = np.zeros((1, 1, 4, 4), dtype=np.float32)
    for i in range(4):
        for j in range(4):
            window = padded[:, :, i : i + 2, j : j + 2]
            # count_include_pad defaults to 0, so divide by the real count.
            h0, w0 = i - 1, j - 1
            real_h = max(0, min(2, 3 - h0) - max(0, -h0))
            real_w = max(0, min(2, 3 - w0) - max(0, -w0))
            expected[:, :, i, j] = window.sum(axis=(2, 3)) / (real_h * real_w)
    np.testing.assert_allclose(session.run()["y"], expected, rtol=1e-6, atol=1e-6)


def test_slice_through_a_plan_matches_numpy():
    model = _model(
        [helper.make_node("Slice", ["x", "starts", "ends"], ["y"])],
        [_io("x", [4, 6])],
        [_io("y", [2, 3])],
        [
            numpy_helper.from_array(np.asarray([1, 2], dtype=np.int64), "starts"),
            numpy_helper.from_array(np.asarray([3, 5], dtype=np.int64), "ends"),
        ],
    )
    x = np.arange(24, dtype=np.float32).reshape(4, 6)
    session = _session(model, {"x": x})
    np.testing.assert_array_equal(session.run()["y"], x[1:3, 2:5])


def test_concat_through_a_plan_matches_numpy():
    model = _model(
        [helper.make_node("Concat", ["a", "b"], ["y"], axis=0)],
        [_io("a", [2, 3]), _io("b", [1, 3])],
        [_io("y", [3, 3])],
    )
    a = np.arange(6, dtype=np.float32).reshape(2, 3)
    b = np.arange(3, dtype=np.float32).reshape(1, 3) + 100
    session = _session(model, {"a": a, "b": b})
    np.testing.assert_array_equal(session.run()["y"], np.concatenate([a, b], axis=0))


def test_where_through_a_plan_matches_numpy():
    model = _model(
        [helper.make_node("Where", ["cond", "a", "b"], ["y"])],
        [
            _io("cond", [3], TensorProto.BOOL),
            _io("a", [3]),
            _io("b", [3]),
        ],
        [_io("y", [3])],
    )
    # The profile stores a bool as `int32` (see `dtypes.BOOL`), so the feed must be
    # `int32` too: a numpy `bool` array is one byte per element and would be rejected
    # as the wrong size against a slot the plan sized at four.
    cond = np.asarray([1, 0, 1], dtype=np.int32)
    a = np.asarray([1.0, 2.0, 3.0], dtype=np.float32)
    b = np.asarray([9.0, 8.0, 7.0], dtype=np.float32)
    session = _session(model, {"cond": cond, "a": a, "b": b})
    np.testing.assert_array_equal(
        session.run()["y"], np.where(cond.astype(bool), a, b)
    )


def test_cast_float_to_int_through_a_plan_matches_numpy():
    model = _model(
        [helper.make_node("Cast", ["x"], ["y"], to=TensorProto.INT32)],
        [_io("x", [4])],
        [_io("y", [4], TensorProto.INT32)],
    )
    x = np.asarray([2.9, -2.9, 0.5, -0.5], dtype=np.float32)
    session = _session(model, {"x": x})
    got = session.run()["y"]
    assert got.dtype == np.int32
    np.testing.assert_array_equal(got, np.trunc(x).astype(np.int32))


def test_a_where_with_an_overlapping_condition_is_correct_when_disjoint():
    # The primitive refuses aliasing, so a correct graph must still work when the
    # three operands are distinct tensors of the same shape.
    model = _model(
        [
            helper.make_node("Greater", ["x", "zero"], ["cond"]),
            helper.make_node("Where", ["cond", "x", "zero"], ["y"]),
        ],
        [_io("x", [5])],
        [_io("y", [5])],
        [numpy_helper.from_array(np.asarray([0.0], dtype=np.float32), "zero")],
    )
    # `Greater` has no lowering yet, so this documents the gap rather than passing.
    plan = Plan.from_model_bytes(model)
    blob = plan_wire.encode_plan(plan, {"x": (5,)})
    session = native.NeuralSession(blob, backend="cpu")
    assert "Greater" in session.missing_ops
    model = _model(
        [helper.make_node("Pad", ["x", "pads"], ["y"], mode="constant")],
        [_io("x", [2, 3])],
        [_io("y", [3, 4])],
        [numpy_helper.from_array(np.asarray([1, 0, 0, 1], dtype=np.int64), "pads")],
    )
    x = np.arange(6, dtype=np.float32).reshape(2, 3)
    session = _session(model, {"x": x})
    expected = np.pad(x, ((1, 0), (0, 1)), mode="constant", constant_values=0.0)
    np.testing.assert_array_equal(session.run()["y"], expected)


def _conv_reference(x, w, b, stride, pads, group):
    n, ci, h, wid = x.shape
    co, ci_per_group, kh, kw = w.shape
    sh, sw = stride
    ph, pw = pads
    co_per_group = co // group
    xp = np.pad(x.astype(np.float64), ((0, 0), (0, 0), (ph, ph), (pw, pw)))
    oh = (h + 2 * ph - kh) // sh + 1
    ow = (wid + 2 * pw - kw) // sw + 1
    out = np.zeros((n, co, oh, ow), dtype=np.float64)
    for g in range(group):
        for oc in range(co_per_group):
            target = g * co_per_group + oc
            for i in range(oh):
                for j in range(ow):
                    window = xp[
                        :,
                        g * ci_per_group : (g + 1) * ci_per_group,
                        i * sh : i * sh + kh,
                        j * sw : j * sw + kw,
                    ]
                    out[:, target, i, j] = np.sum(
                        window * w[target][None, :, :, :], axis=(1, 2, 3)
                    )
    if b is not None:
        out += b.astype(np.float64)[None, :, None, None]
    return out.astype(np.float32)


def test_conv_with_asymmetric_padding_uses_the_right_index():
    # ONNX orders `pads` as [top, left, bottom, right]. A build that read
    # `pads[2]` for the horizontal pad would pass any symmetric test and fail here.
    rng = np.random.default_rng(97)
    x = rng.uniform(-1, 1, size=(1, 1, 5, 5)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(1, 1, 2, 2)).astype(np.float32)
    pads = [0, 2, 0, 2]  # left and right only, no vertical padding
    oh = 5 - 2 + 1
    ow = 5 + 2 + 2 - 2 + 1
    model = _model(
        [
            helper.make_node(
                "Conv", ["x", "w"], ["y"], strides=[1, 1], pads=pads, group=1
            )
        ],
        [_io("x", [1, 1, 5, 5])],
        [_io("y", [1, 1, oh, ow])],
        [numpy_helper.from_array(w, "w")],
    )
    session = _session(model, {"x": x})
    expected = _conv_reference(x, w, None, (1, 1), (pads[0], pads[1]), 1)
    got = session.run()["y"]
    assert got.shape == expected.shape, f"shape {got.shape} vs {expected.shape}"
    np.testing.assert_allclose(got, expected, rtol=1e-5, atol=1e-5)


def test_conv_through_a_plan_matches_numpy():
    rng = np.random.default_rng(61)
    x = rng.uniform(-1, 1, size=(1, 3, 6, 6)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(4, 3, 3, 3)).astype(np.float32)
    b = rng.uniform(-1, 1, size=(4,)).astype(np.float32)
    model = _model(
        [
            helper.make_node(
                "Conv", ["x", "w", "b"], ["y"], strides=[1, 1], pads=[1, 1, 1, 1], group=1
            )
        ],
        [_io("x", [1, 3, 6, 6])],
        [_io("y", [1, 4, 6, 6])],
        [
            numpy_helper.from_array(w, "w"),
            numpy_helper.from_array(b, "b"),
        ],
    )
    session = _session(model, {"x": x})
    expected = _conv_reference(x, w, b, (1, 1), (1, 1), 1)
    np.testing.assert_allclose(session.run()["y"], expected, rtol=1e-5, atol=1e-5)


def test_depthwise_conv_through_a_plan_matches_numpy():
    rng = np.random.default_rng(67)
    x = rng.uniform(-1, 1, size=(1, 4, 5, 5)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(4, 1, 3, 3)).astype(np.float32)
    model = _model(
        [
            helper.make_node(
                "Conv", ["x", "w"], ["y"], strides=[1, 1], pads=[1, 1, 1, 1], group=4
            )
        ],
        [_io("x", [1, 4, 5, 5])],
        [_io("y", [1, 4, 5, 5])],
        [numpy_helper.from_array(w, "w")],
    )
    session = _session(model, {"x": x})
    expected = _conv_reference(x, w, None, (1, 1), (1, 1), 4)
    np.testing.assert_allclose(session.run()["y"], expected, rtol=1e-5, atol=1e-5)


def test_conv_with_dilation_is_refused():
    # The primitive has no dilated path. Ignoring the attribute would compute a
    # different convolution that still looks like a plausible image.
    rng = np.random.default_rng(71)
    x = rng.uniform(-1, 1, size=(1, 1, 5, 5)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(1, 1, 2, 2)).astype(np.float32)
    model = _model(
        [helper.make_node("Conv", ["x", "w"], ["y"], dilations=[2, 2])],
        [_io("x", [1, 1, 5, 5])],
        [_io("y", [1, 1, 3, 3])],
        [numpy_helper.from_array(w, "w")],
    )
    plan = Plan.from_model_bytes(model)
    blob = plan_wire.encode_plan(plan, {"x": (1, 1, 5, 5)})
    session = native.NeuralSession(blob, backend="cpu")
    session.set_constant("w", w)
    session.set_input("x", x)
    with pytest.raises(ValueError, match="dilations"):
        session.run()
