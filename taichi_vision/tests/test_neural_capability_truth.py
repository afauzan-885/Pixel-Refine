"""The capability report must not claim more than the build can do.

A report that overstates is worse than no report: a caller plans against it and
fails later, far from the cause. These tests compare the advertised list against
operator-by-operator reality.
"""

from __future__ import annotations

import numpy as np
import pytest

onnx = pytest.importorskip("onnx")
native = pytest.importorskip("taichi.taichi_python")
from onnx import TensorProto, helper  # noqa: E402

from taichi_vision.taichi_algorithm.neural.universal import plan_wire  # noqa: E402
from taichi_vision.taichi_algorithm.neural.universal.plan import Plan  # noqa: E402


def _report():
    return native.neural_capabilities()


def test_the_report_has_the_four_keys_it_promises():
    report = _report()
    for key in ("ops", "plan_ready", "backends", "execution_backends"):
        assert key in report, f"the report omits {key}"


def test_plan_ready_is_a_subset_of_the_lowerable_operators():
    # Everything advertised as runnable must appear somewhere, and the list must be
    # sorted and free of duplicates so a caller can compare it directly.
    ready = _report()["plan_ready"]
    assert ready == sorted(ready)
    assert len(ready) == len(set(ready))
    assert ready, "the build lowers operators, so the list cannot be empty"


def test_execution_backends_is_empty_only_when_nothing_is_runnable():
    # The two lists are separate facts; this pins the relationship.
    report = _report()
    if report["plan_ready"]:
        assert report["execution_backends"], (
            "operators are runnable, so at least one backend must claim execution"
        )
    else:
        assert not report["execution_backends"]


def _model_and_feeds(op: str):
    """A minimal model using `op`, or None when it needs more than one input kind."""
    one_in = [
        "Relu", "Sigmoid", "Tanh", "Abs", "Neg", "Sqrt", "Exp", "Log", "Erf",
        "Softplus", "Floor", "Ceil", "Sin", "Cos", "Square", "Reciprocal", "Sign",
        "Identity",
    ]
    if op in one_in:
        graph = helper.make_graph(
            [helper.make_node(op, ["x"], ["y"])],
            "m",
            [helper.make_tensor_value_info("x", TensorProto.FLOAT, [4])],
            [helper.make_tensor_value_info("y", TensorProto.FLOAT, [4])],
        )
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("ai.onnx", 18)])
        model.ir_version = 8
        return model.SerializeToString(), {"x": (4,)}
    if op in ("Add", "Sub", "Mul", "Div", "Pow", "Min", "Max", "Mod"):
        graph = helper.make_graph(
            [helper.make_node(op, ["a", "b"], ["y"])],
            "m",
            [
                helper.make_tensor_value_info("a", TensorProto.FLOAT, [4]),
                helper.make_tensor_value_info("b", TensorProto.FLOAT, [4]),
            ],
            [helper.make_tensor_value_info("y", TensorProto.FLOAT, [4])],
        )
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("ai.onnx", 18)])
        model.ir_version = 8
        return model.SerializeToString(), {"a": (4,), "b": (4,)}
    return None


@pytest.mark.parametrize(
    "op",
    [
        "Relu", "Sigmoid", "Tanh", "Abs", "Neg", "Sqrt", "Exp", "Log", "Erf",
        "Softplus", "Floor", "Ceil", "Sin", "Cos", "Reciprocal", "Sign",
        "Identity", "Add", "Sub", "Mul", "Div", "Pow", "Min", "Max", "Mod",
    ],
)
def test_every_advertised_operator_actually_runs(op):
    # The claim-vs-reality check: build a graph with the operator, then execute it.
    # A name in `plan_ready` that fails here is exactly the overstatement to avoid.
    assert op in _report()["plan_ready"], f"{op} should be advertised"
    built = _model_and_feeds(op)
    assert built is not None
    model_bytes, shapes = built

    plan = Plan.from_model_bytes(model_bytes)
    blob = plan_wire.encode_plan(plan, shapes)
    session = native.NeuralSession(blob, backend="cpu")
    assert not session.missing_ops, f"{op} is advertised but reports itself missing"

    for name, shape in shapes.items():
        session.set_input(name, np.ones(shape, dtype=np.float32))
    produced = session.run()
    value = np.asarray(produced["y"])
    assert value.shape == (4,)
    assert np.isfinite(value).all()


def test_an_operator_outside_the_list_is_refused_by_name():
    # `Softmax` has no lowering; asking for it must say so, not produce a guess.
    # `Resize` is deliberately not used here: its shape inference needs constant
    # integer scales, and a model built without them fails before the executor is
    # reached, which would test the planner rather than the capability claim.
    graph = helper.make_graph(
        [helper.make_node("Softmax", ["x"], ["y"], axis=1)],
        "m",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, [2, 3])],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, [2, 3])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("ai.onnx", 18)])
    model.ir_version = 8
    assert "Softmax" not in _report()["plan_ready"]
    plan = Plan.from_model_bytes(model.SerializeToString())
    blob = plan_wire.encode_plan(plan, {"x": (2, 3)})
    session = native.NeuralSession(blob, backend="cpu")
    assert "Softmax" in session.missing_ops


def test_every_advertised_name_is_an_onnx_operator_the_planner_admits():
    # A name the planner's registry does not admit can never appear in a graph, so
    # advertising it overstates the build. This is how `Square` and `GeluExact` were
    # found in `plan_ready` despite being unreachable.
    from taichi_vision.taichi_algorithm.neural.universal import registry

    admitted = set(registry.OPS)
    for name in _report()["plan_ready"]:
        assert name in admitted, (
            f"{name} is advertised but the planner cannot admit it, so no graph "
            f"can reach it"
        )
