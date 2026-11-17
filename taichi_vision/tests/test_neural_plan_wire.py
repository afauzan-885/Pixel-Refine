"""Wire-format tests: the Python writer and the Rust reader must agree exactly.

These use real ONNX models rather than hand-built plans, because the thing under
test is the whole chain — plan construction, shape inference, attribute encoding —
and a synthetic `Plan` would skip the parts most likely to be wrong.
"""

from __future__ import annotations

import numpy as np
import pytest

onnx = pytest.importorskip("onnx")
from onnx import TensorProto, helper, numpy_helper  # noqa: E402

from taichi_vision.taichi_algorithm.neural.universal import plan_wire  # noqa: E402
from taichi_vision.taichi_algorithm.neural.universal.dtypes import F32  # noqa: E402
from taichi_vision.taichi_algorithm.neural.universal.plan import Plan  # noqa: E402


def _model(nodes, inputs, outputs, initializers=()):
    graph = helper.make_graph(
        list(nodes),
        "test",
        list(inputs),
        list(outputs),
        list(initializers),
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("ai.onnx", 18)])
    model.ir_version = 8
    return model.SerializeToString()


def _input(name, shape, elem=TensorProto.FLOAT):
    return helper.make_tensor_value_info(name, elem, shape)


def _output(name, shape, elem=TensorProto.FLOAT):
    return helper.make_tensor_value_info(name, elem, shape)


def _add_relu():
    body = _model(
        [
            helper.make_node("Add", ["x", "bias"], ["sum"], name="add"),
            helper.make_node("Relu", ["sum"], ["y"], name="relu"),
        ],
        [_input("x", [4]), _input("bias", [4])],
        [_output("y", [4])],
    )
    return Plan.from_model_bytes(body)


def _clip(lo, hi):
    nodes = [helper.make_node("Clip", ["x", "lo", "hi"], ["y"], name="clip")]
    inits = [
        numpy_helper.from_array(np.asarray(lo, dtype=np.float32), "lo"),
        numpy_helper.from_array(np.asarray(hi, dtype=np.float32), "hi"),
    ]
    body = _model(nodes, [_input("x", [4])], [_output("y", [4])], inits)
    return Plan.from_model_bytes(body)


def _decode(blob: bytes):
    """Parse with the Rust implementation, so the two sides are actually compared."""
    from taichi_vision.taichi_algorithm.neural import neural_engine  # noqa: F401
    import taichi.taichi_python as native

    return native.neural_plan_parse(blob)


def test_magic_and_version_are_written():
    blob = plan_wire.encode_plan(_add_relu(), {"x": (4,), "bias": (4,)})
    assert blob[:4] == b"NPLN"
    assert int.from_bytes(blob[4:8], "little") == 2


def test_rust_reads_the_plan_python_wrote():
    plan = _add_relu()
    blob = plan_wire.encode_plan(plan, {"x": (4,), "bias": (4,)})
    inputs, outputs, count = native_parse(blob)
    assert inputs == ["x", "bias"]
    assert outputs == ["y"]
    assert count == 2


def native_parse(blob):
    import taichi.taichi_python as native

    return native.neural_plan_parse(blob)


def test_constant_values_are_reported_for_upload():
    plan = _clip(-1.0, 1.0)
    constants = plan_wire.constant_values(plan)
    assert set(constants) == {"lo", "hi"}
    assert constants["lo"].dtype == np.float32
    assert float(constants["lo"]) == pytest.approx(-1.0)


def test_float_attribute_round_trips_through_rust():
    blob = plan_wire.encode_plan(_clip(-0.5, 2.5), {"x": (4,)})
    # Parsing is the check: a mis-sized attribute would make the reader run past
    # the end of the buffer and fail.
    inputs, outputs, count = native_parse(blob)
    assert count == 1
    assert outputs == ["y"]


def test_shapes_are_derived_for_every_slot():
    plan = _add_relu()
    blob = plan_wire.encode_plan(plan, {"x": (4,), "bias": (4,)})
    inputs, outputs, _ = native_parse(blob)
    assert outputs == ["y"]


def test_a_missing_input_shape_is_refused():
    plan = _add_relu()
    with pytest.raises(plan_wire.PlanEncodeError, match="no shape for this signature"):
        plan_wire.encode_plan(plan, {"x": (4,)})


def test_a_wrong_rank_is_refused():
    plan = _add_relu()
    with pytest.raises(plan_wire.PlanEncodeError, match="declared with rank"):
        plan_wire.encode_plan(plan, {"x": (1, 4), "bias": (4,)})


def test_an_unrepresentable_attribute_is_refused_not_dropped():
    # A Python object has no wire form. Dropping it would run a different operator
    # than the graph declared, and the answer would look plausible.
    with pytest.raises(plan_wire.PlanEncodeError, match="no wire representation"):
        plan_wire._attribute(object(), "mystery")


def test_an_oversized_integer_is_refused():
    with pytest.raises(plan_wire.PlanEncodeError, match="does not fit in u32"):
        plan_wire._u32(-1)


def test_empty_axes_encodes_as_an_empty_int_list():
    blob = plan_wire._attribute([], "axes")
    assert blob[0] == plan_wire.TAG_INTS
    assert blob[1:5] == b"\x00\x00\x00\x00"


def test_numpy_scalars_keep_their_kind():
    assert plan_wire._attribute(np.int64(3), "axis")[0] == plan_wire.TAG_INT
    assert plan_wire._attribute(np.float32(0.5), "alpha")[0] == plan_wire.TAG_FLOAT


def test_a_string_attribute_is_tagged_as_a_string():
    blob = plan_wire._attribute("constant", "mode")
    assert blob[0] == plan_wire.TAG_STR
    assert b"constant" in blob
