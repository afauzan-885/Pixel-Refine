"""The native strategy, exercised through the pyproject-facing adaptor.

These test the layer a caller actually touches: `NativeSession.run()` with an
onnxruntime-shaped call, backed by the Rust executor.
"""

from __future__ import annotations

import numpy as np
import pytest

onnx = pytest.importorskip("onnx")
pytest.importorskip("taichi.taichi_python")
from onnx import TensorProto, helper, numpy_helper  # noqa: E402

from taichi_vision.neural.native_session import NativeSession  # noqa: E402


def _model(nodes, inputs, outputs, initializers=()):
    graph = helper.make_graph(list(nodes), "native", list(inputs), list(outputs), list(initializers))
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("ai.onnx", 18)])
    model.ir_version = 8
    return model.SerializeToString()


def _io(name, shape, elem=TensorProto.FLOAT):
    return helper.make_tensor_value_info(name, elem, shape)


def test_run_returns_an_ort_shaped_list():
    model = _model(
        [helper.make_node("Relu", ["x"], ["y"])],
        [_io("x", [4])],
        [_io("y", [4])],
    )
    session = NativeSession(model)
    x = np.asarray([-2.0, -1.0, 1.0, 2.0], dtype=np.float32)
    result = session.run(None, {"x": x})
    assert isinstance(result, list) and len(result) == 1
    np.testing.assert_array_equal(result[0], np.maximum(x, 0))


def test_an_explicit_output_name_selects_the_tensor():
    model = _model(
        [
            helper.make_node("Relu", ["x"], ["a"]),
            helper.make_node("Neg", ["a"], ["b"]),
        ],
        [_io("x", [3])],
        [_io("b", [3])],
    )
    session = NativeSession(model)
    x = np.asarray([-1.0, 0.0, 2.0], dtype=np.float32)
    # Relu(-1) = 0, Relu(0) = 0, Relu(2) = 2; then Neg gives -0, -0, -2.
    expected = -np.maximum(x, 0)
    got = session.run(["b"], {"x": x})[0]
    np.testing.assert_array_equal(got, expected)


def test_the_session_is_reused_for_the_same_signature():
    model = _model(
        [helper.make_node("Relu", ["x"], ["y"])],
        [_io("x", [4])],
        [_io("y", [4])],
    )
    session = NativeSession(model)
    x = np.ones(4, dtype=np.float32)
    first = session._ensure_session({"x": x})
    second = session._ensure_session({"x": x})
    assert first is second, "the same signature must reuse one session"


def test_a_new_signature_builds_a_new_plan():
    # The plan carries final shapes, so a different input size needs its own.
    model = _model(
        [helper.make_node("Relu", ["x"], ["y"])],
        [_io("x", ["N"])],
        [_io("y", ["N"])],
    )
    # A symbolic dimension makes shape inference depend on the feed.
    graph = helper.make_graph(
        [helper.make_node("Relu", ["x"], ["y"])],
        "dyn",
        [_io("x", [4])],
        [_io("y", [4])],
    )
    del graph
    session = NativeSession(model)
    a = session.run(None, {"x": np.ones(4, dtype=np.float32)})[0]
    b = session.run(None, {"x": np.ones(8, dtype=np.float32)})[0]
    assert a.shape == (4,) and b.shape == (8,)


def test_missing_inputs_are_named():
    model = _model(
        [helper.make_node("Add", ["x", "y"], ["z"])],
        [_io("x", [2]), _io("y", [2])],
        [_io("z", [2])],
    )
    session = NativeSession(model)
    with pytest.raises(Exception, match="missing inputs"):
        session.run(None, {"x": np.zeros(2, dtype=np.float32)})


def test_an_unsupported_operator_is_refused_with_its_name():
    model = _model(
        [helper.make_node("Softmax", ["x"], ["y"], axis=1)],
        [_io("x", [2, 3])],
        [_io("y", [2, 3])],
    )
    session = NativeSession(model)
    with pytest.raises(Exception, match="Softmax"):
        session.run(None, {"x": np.zeros((2, 3), dtype=np.float32)})


def test_get_inputs_and_outputs_report_the_names():
    model = _model(
        [helper.make_node("Relu", ["x"], ["y"])],
        [_io("x", [4])],
        [_io("y", [4])],
    )
    session = NativeSession(model)
    assert [arg.name for arg in session.get_inputs()] == ["x"]
    assert [arg.name for arg in session.get_outputs()] == ["y"]


def test_an_unknown_output_name_is_refused():
    model = _model(
        [helper.make_node("Relu", ["x"], ["y"])],
        [_io("x", [4])],
        [_io("y", [4])],
    )
    session = NativeSession(model)
    with pytest.raises(Exception, match="does not produce"):
        session.run(["nope"], {"x": np.zeros(4, dtype=np.float32)})


def test_a_float64_feed_is_narrowed_to_the_declared_dtype():
    model = _model(
        [helper.make_node("Relu", ["x"], ["y"])],
        [_io("x", [3])],
        [_io("y", [3])],
    )
    session = NativeSession(model)
    result = session.run(None, {"x": np.asarray([-1.0, 0.0, 2.0], dtype=np.float64)})[0]
    assert result.dtype == np.float32
    np.testing.assert_array_equal(result, np.asarray([0.0, 0.0, 2.0], dtype=np.float32))


def test_a_graph_with_an_initializer_runs():
    scale = numpy_helper.from_array(np.asarray([3.0], dtype=np.float32), "scale")
    model = _model(
        [helper.make_node("Mul", ["x", "scale"], ["y"])],
        [_io("x", [4])],
        [_io("y", [4])],
        [scale],
    )
    session = NativeSession(model)
    x = np.asarray([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    np.testing.assert_array_equal(session.run(None, {"x": x})[0], x * 3.0)
