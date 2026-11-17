"""Public-facade contract tests for ``taichi_vision.neural``.

These tests never initialize a GPU device. They verify the onnxruntime-shaped
public surface, the resolver's strategy decisions, and that refusals carry
structured, actionable detail.
"""

from __future__ import annotations

import pytest
from onnx import TensorProto, helper, numpy_helper

import taichi_vision.neural as neural
from taichi_vision.neural.capabilities import NATIVE_GRAPH_OPS
from taichi_vision.neural.errors import CapabilityMissingError
from taichi_vision.neural.resolver import resolve


def _value(name, rank=4):
    return helper.make_tensor_value_info(name, TensorProto.FLOAT, [1] * rank)


def _model(nodes, inputs, outputs, initializers=()):
    graph = helper.make_graph(nodes, "facade_test", inputs, outputs,
                              initializer=list(initializers))
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    model.ir_version = 8
    return model.SerializeToString()


def _native_only_model():
    """Add+Relu: covered by the native graph operator set."""
    return _model(
        [
            helper.make_node("Add", ["x", "y"], ["t"]),
            helper.make_node("Relu", ["t"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
    )


def test_onnxruntime_shaped_surface_exists():
    assert neural.Session is neural.InferenceSession
    options = neural.SessionOptions()
    options.graph_optimization_level = neural.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.log_severity_level = 3
    assert options.graph_optimization_level == 99
    assert options.log_severity_level == 3
    assert isinstance(options, neural.SessionOptions)
    assert neural.GraphOptimizationLevel.ORT_ENABLE_BASIC == 1
    assert neural.get_available_providers()


def test_session_options_record_inert_settings():
    options = neural.SessionOptions()
    inert = options.inert_settings()
    assert "graph_optimization_level" in inert
    assert inert["graph_optimization_level"] == neural.GraphOptimizationLevel.ORT_DISABLE_ALL


def test_node_arg_exposes_name_and_shape():
    arg = neural.NodeArg(name="input", shape=(1, 3, 8, 8))
    assert arg.name == "input"
    assert tuple(arg.shape) == (1, 3, 8, 8)
    assert "tensor(float)" == arg.type


def test_native_operator_set_is_reported():
    assert "Add" in NATIVE_GRAPH_OPS
    assert "Gather" not in NATIVE_GRAPH_OPS, (
        "Gather must not be advertised as natively supported"
    )


def test_resolver_resolves_native_strategy_for_small_graph():
    resolution = resolve(_native_only_model(), backend="cpu", model_name="unit_native")
    assert resolution.strategy in {"pool", "native"}
    assert resolution.record.status == "resolved"
    assert resolution.record.reasons


def test_resolver_refusal_is_structured():
    """A graph with an operator outside every strategy must refuse with detail."""
    model = _model(
        [helper.make_node("Shrink", ["x"], ["out"])],
        [_value("x")],
        [_value("out")],
    )
    with pytest.raises(CapabilityMissingError) as excinfo:
        resolve(model, backend="cpu", model_name="unit_unsupported")
    error = excinfo.value
    assert error.attempts, "refusal must list the attempted strategies"
    # `Shrink` is outside the registry, so the pool attempt explains it.
    assert any("registry" in attempt or "native" in attempt for attempt in error.attempts)


def test_capabilities_reports_backend_and_blockers():
    summary = neural.capabilities("cpu")
    assert summary["backend"] == "cpu"
    assert "registry_operators" in summary
    assert isinstance(summary["blockers"], list)
    names = {item["name"] for item in summary["strategies"]}
    assert {"pool", "resident", "native"} <= names


def test_describe_reports_strategy_without_hidden_claims():
    session = neural.InferenceSession(_native_only_model(), backend="cpu")
    try:
        report = neural.describe(session)
        assert f"strategy={session.strategy}" in report
        assert session.get_providers()[0].startswith("Taichi")
    finally:
        session.close()


def test_session_is_context_manager_and_closes():
    with neural.InferenceSession(_native_only_model(), backend="cpu") as session:
        assert session.get_providers()
    session.close()  # idempotent
