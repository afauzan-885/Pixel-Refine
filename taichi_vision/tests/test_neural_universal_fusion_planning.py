"""Planning-only tests for the universal neural fusion planner.

These tests never initialize a Taichi runtime or load a pool artifact: they
build small ONNX graphs, validate them through ``Plan.from_model_bytes``, and
assert on the resulting :class:`FusionPlan`.
"""

from __future__ import annotations

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
import pytest

from taichi_vision.taichi_algorithm.neural.universal import (
    UnsupportedONNXOperatorError,
    build_fusion_plan,
)
from taichi_vision.taichi_algorithm.neural.universal.fusions import _PATTERN_GRAPHS

ALL_POOL_GRAPHS = set(_PATTERN_GRAPHS.values())


def _build_model(nodes, inputs, outputs, initializers=()):
    graph = helper.make_graph(
        nodes,
        "fusion_test",
        inputs,
        outputs,
        initializer=list(initializers),
    )
    model = helper.make_model(
        graph,
        opset_imports=[helper.make_opsetid("", 13)],
        producer_name="fusion-planning-test",
    )
    model.ir_version = 8
    return model.SerializeToString()


def _value(name, rank=4):
    return helper.make_tensor_value_info(name, TensorProto.FLOAT, ["N"] * rank)


def _scalar(name, value):
    return numpy_helper.from_array(np.asarray([value], dtype=np.float32), name)


def _plan(model_bytes):
    from taichi_vision.taichi_algorithm.neural.universal.plan import Plan

    return Plan.from_model_bytes(model_bytes)


def test_add_relu_fuses_with_relu_absorbed():
    model = _build_model(
        [
            helper.make_node("Add", ["x", "y"], ["t"]),
            helper.make_node("Relu", ["t"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    add_node = plan.nodes[0]
    assert add_node.op == "Add"
    dispatches = fusion.dispatches.get(add_node.index, ())
    assert dispatches, "Add+Relu must be planned"
    assert dispatches[0].kind == "add_relu"
    assert dispatches[0].graph_name == "nu_add_relu"
    assert dispatches[0].output_name == "out"
    assert dispatches[0].fused_nodes == (add_node.index + 1,)


def test_add_relu_declines_without_pool_graph_and_falls_back_to_broadcast():
    model = _build_model(
        [
            helper.make_node("Add", ["x", "y"], ["t"]),
            helper.make_node("Relu", ["t"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
    )
    plan = _plan(model)
    pool = ALL_POOL_GRAPHS - {"nu_add_relu"}
    fusion = build_fusion_plan(plan, set(), pool)
    add_node = plan.nodes[0]
    kinds = [dispatch.kind for dispatch in fusion.dispatches.get(add_node.index, ())]
    assert "add_relu" not in kinds
    assert "binary_unary" in kinds, "broadcast variant must stay available"


def test_mul_scalar_clip_prefers_scalar_variant():
    model = _build_model(
        [
            helper.make_node("Mul", ["x", "s"], ["t"]),
            helper.make_node("Clip", ["t", "lo", "hi"], ["out"]),
        ],
        [_value("x")],
        [_value("out")],
        initializers=[_scalar("s", 2.5), _scalar("lo", 0.0), _scalar("hi", 1.0)],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    mul_node = plan.nodes[0]
    kinds = [dispatch.kind for dispatch in fusion.dispatches.get(mul_node.index, ())]
    assert kinds[0] == "mul_scalar_clip"
    assert kinds[1] == "mul_clip"
    # Clip bounds supplied as inputs make the unary 3-input, so the original
    # binary_unary broadcast variant never planned this edge.
    assert "binary_unary" not in kinds
    scalar_dispatch = fusion.dispatches[mul_node.index][0]
    assert scalar_dispatch.params["b"] == 2.5
    assert scalar_dispatch.params["clip_lo"] == 0.0
    assert scalar_dispatch.params["clip_hi"] == 1.0


def test_mul_clip_with_tensor_operand():
    model = _build_model(
        [
            helper.make_node("Mul", ["x", "y"], ["t"]),
            helper.make_node("Clip", ["t", "lo", "hi"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
        initializers=[_scalar("lo", 0.0), _scalar("hi", 6.0)],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    mul_node = plan.nodes[0]
    kinds = [dispatch.kind for dispatch in fusion.dispatches.get(mul_node.index, ())]
    assert kinds == ["mul_clip"]


def test_mul_clip_with_attribute_bounds_has_broadcast_fallback():
    model = _build_model(
        [
            helper.make_node("Mul", ["x", "y"], ["t"]),
            helper.make_node("Clip", ["t"], ["out"], min=0.0, max=1.0),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    mul_node = plan.nodes[0]
    kinds = [dispatch.kind for dispatch in fusion.dispatches.get(mul_node.index, ())]
    assert kinds == ["mul_clip", "binary_unary"]


def test_sigmoid_mul_clip_chain_wins_over_shorter_patterns():
    model = _build_model(
        [
            helper.make_node("Sigmoid", ["x"], ["g"]),
            helper.make_node("Mul", ["g", "y"], ["t"]),
            helper.make_node("Clip", ["t", "lo", "hi"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
        initializers=[_scalar("lo", 0.0), _scalar("hi", 1.0)],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    sigmoid_node = plan.nodes[0]
    assert sigmoid_node.op == "Sigmoid"
    dispatches = fusion.dispatches.get(sigmoid_node.index, ())
    assert dispatches and dispatches[0].kind == "sigmoid_mul_clip"
    assert dispatches[0].fused_nodes == (sigmoid_node.index + 1, sigmoid_node.index + 2)
    # Runtime resolves the overlap first-come: the Sigmoid dispatch executes
    # earlier in the plan and marks the Mul/Clip nodes fused, so the Mul's own
    # (redundant) dispatch never runs. Planning may still contain it.
    mul_node = plan.nodes[sigmoid_node.index + 1]
    for dispatch in fusion.dispatches.get(mul_node.index, ()):
        assert dispatch.fused_nodes == (mul_node.index + 1,)


def test_sub_clip_sqrt_and_add_sqrt_clip_chains():
    sub_model = _build_model(
        [
            helper.make_node("Sub", ["x", "y"], ["t"]),
            helper.make_node("Clip", ["t", "lo", "hi"], ["m"]),
            helper.make_node("Sqrt", ["m"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
        initializers=[_scalar("lo", 0.0), _scalar("hi", 1.0)],
    )
    plan = _plan(sub_model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    sub_dispatch = fusion.dispatches[plan.nodes[0].index]
    assert sub_dispatch[0].kind == "sub_clip_sqrt"

    add_model = _build_model(
        [
            helper.make_node("Add", ["x", "y"], ["t"]),
            helper.make_node("Sqrt", ["t"], ["m"]),
            helper.make_node("Clip", ["m", "lo", "hi"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
        initializers=[_scalar("lo", 0.0), _scalar("hi", 1.0)],
    )
    plan = _plan(add_model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    add_dispatch = fusion.dispatches[plan.nodes[0].index]
    assert add_dispatch[0].kind == "add_sqrt_clip"


def test_sub_square_fusion():
    two = numpy_helper.from_array(np.asarray([2.0], dtype=np.float32), "two")
    model = _build_model(
        [
            helper.make_node("Sub", ["x", "y"], ["t"]),
            helper.make_node("Pow", ["t", "two"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
        initializers=[two],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    sub_dispatch = fusion.dispatches[plan.nodes[0].index]
    assert sub_dispatch[0].kind == "sub_square"
    assert sub_dispatch[0].output_name == "out"


def test_unary_binary_fuses_tanh_add():
    model = _build_model(
        [
            helper.make_node("Tanh", ["x"], ["t"]),
            helper.make_node("Add", ["t", "y"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    tanh_node = plan.nodes[0]
    dispatches = fusion.dispatches.get(tanh_node.index, ())
    assert dispatches and dispatches[0].kind == "unary_binary"
    assert dispatches[0].params["unary_is_left"] == 1


def test_sub_sub_div_chain():
    model = _build_model(
        [
            helper.make_node("Sub", ["a", "b"], ["m1"]),
            helper.make_node("Sub", ["m1", "c"], ["m2"]),
            helper.make_node("Div", ["m2", "d"], ["out"]),
        ],
        [_value("a"), _value("b"), _value("c"), _value("d")],
        [_value("out")],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    first_sub = plan.nodes[0]
    dispatches = fusion.dispatches.get(first_sub.index, ())
    assert dispatches and dispatches[0].kind == "sub_sub_div"
    assert dispatches[0].fused_nodes == (1, 2)


def test_conv_activation_folds_into_act_parameter():
    weight = numpy_helper.from_array(
        np.zeros((1, 1, 3, 3), dtype=np.float32), "w"
    )
    model = _build_model(
        [
            helper.make_node("Conv", ["x", "w"], ["t"]),
            helper.make_node("Relu", ["t"], ["out"]),
        ],
        [_value("x")],
        [_value("out")],
        initializers=[weight],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS)
    conv_node = plan.nodes[0]
    assert conv_node.op == "Conv"
    assert fusion.conv_activation[conv_node.index] == (conv_node.index + 1, "out", 1)
    assert fusion.conv_activation_skipped == frozenset({conv_node.index + 1})
    assert not fusion.dispatches, "conv activation is a lowering param, not a dispatch"


def test_requested_intermediate_blocks_fusion():
    model = _build_model(
        [
            helper.make_node("Add", ["x", "y"], ["t"]),
            helper.make_node("Relu", ["t"], ["out"]),
        ],
        [_value("x"), _value("y")],
        [_value("out")],
    )
    plan = _plan(model)
    fusion = build_fusion_plan(plan, set(), ALL_POOL_GRAPHS, )
    assert fusion.dispatches, "unfused baseline must plan Add+Relu"

    plan = _plan(model)
    fusion = build_fusion_plan(plan, {"t"}, ALL_POOL_GRAPHS)
    assert not fusion.dispatches, "requested intermediate must not be fused"


def test_unknown_operator_fails_closed():
    model = _build_model(
        [helper.make_node("Shrink", ["x"], ["out"])],
        [_value("x")],
        [_value("out")],
    )
    with pytest.raises(UnsupportedONNXOperatorError):
        _plan(model)
