"""Registry contract tests: admission, fail-closed behaviour, and coverage.

These tests are pure Python (no Taichi device) so they stay fast and can guard
the operator surface even on a machine without a compiled pool artifact.
"""

from __future__ import annotations

import onnx
import pytest
from onnx import TensorProto as T, helper as h

from taichi_vision.taichi_aot.neural_universal import registry
from taichi_vision.taichi_aot.neural_universal.compile import (
    VULKAN_UNSUPPORTED_I64_KERNELS,
    _kernels_for_backend,
)
from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedONNXOperatorError
from taichi_vision.taichi_aot.neural_universal.kernels import ALL_KERNELS
from taichi_vision.taichi_aot.neural_universal.plan import Plan

SHIPPED_MODELS = {
    "lightglue": (
        "Abs Add And AveragePool Cast Clip Concat ConstantOfShape Conv Cos Div Equal "
        "Erf Exp Expand Flatten Floor Gather GatherElements Greater Identity "
        "InstanceNormalization LayerNormalization Less Log LogSoftmax MatMul MaxPool "
        "Mod Mul MultiHeadAttention Neg NonZero PRelu Pad Pow Range ReduceL2 "
        "ReduceMean ReduceSum Relu Reshape Resize Shape Sigmoid Sin Slice Softmax "
        "Softplus SpaceToDepth Split Sqrt Squeeze Sub Tanh Tile TopK Transpose "
        "Unsqueeze Where"
    ).split(),
    "raft": (
        "Add AveragePool Cast Concat Conv Div Expand Floor Gather GatherElements "
        "Greater InstanceNormalization Less MatMul Mul Pad ReduceSum Relu Reshape "
        "Sigmoid Slice Softmax Split Sub Tanh Transpose Unsqueeze Where"
    ).split(),
    "weightnet": (
        "Abs Add AveragePool Clip Concat Conv ConvTranspose Div Erf Gelu Mul Pow "
        "ReduceMean Relu Reshape Resize Sigmoid Slice Softplus SpaceToDepth Sqrt Sub "
        "Tanh DmlFusedConv"
    ).split(),
}


def test_registry_declares_every_operator_the_shipped_models_need():
    needed = set().union(*SHIPPED_MODELS.values())
    missing = sorted(name for name in needed if name not in registry.OPS)
    assert not missing, f"registry is missing operators: {missing}"


def test_backend_pool_filter_is_scoped_to_vulkan_int64_limit():
    all_names = {kernel.__name__ for kernel in ALL_KERNELS}
    assert {kernel.__name__ for kernel in _kernels_for_backend("cpu")} == all_names
    assert {kernel.__name__ for kernel in _kernels_for_backend("cuda")} == all_names
    vulkan_names = {kernel.__name__ for kernel in _kernels_for_backend("vulkan")}
    assert all_names - vulkan_names == set(VULKAN_UNSUPPORTED_I64_KERNELS)


def test_registry_covers_the_full_inventory():
    """The inventory of the 15 target models contains 64 distinct operators."""
    needed = set().union(*SHIPPED_MODELS.values())
    assert len(needed) >= 64 - 2, "operator inventory shrank unexpectedly"
    assert registry.REQUIRED_FOR_SHIPPED_MODELS <= set(registry.OPS)


def test_unknown_operator_is_rejected_with_a_diagnosable_error():
    with pytest.raises(UnsupportedONNXOperatorError, match="NotARealOperator"):
        registry.require("NotARealOperator", "")


def test_custom_domain_is_enforced():
    # Gelu is only admitted from com.microsoft
    assert registry.require("Gelu", "com.microsoft").name == "Gelu"
    with pytest.raises(UnsupportedONNXOperatorError, match="com.microsoft"):
        registry.require("Gelu", "")


def test_registry_has_no_duplicates_and_every_entry_has_arity():
    names = [spec.name for spec in registry.OPS.values()]
    assert len(names) == len(set(names))
    for spec in registry.OPS.values():
        assert isinstance(spec.arity, tuple) and len(spec.arity) == 2


def test_plan_rejects_operator_outside_the_registry():
    graph = h.make_graph(
        [h.make_node("NotARealOperator", ["x"], ["y"])],
        "bad",
        [h.make_tensor_value_info("x", T.FLOAT, [1, 4])],
        [h.make_tensor_value_info("y", T.FLOAT, [1, 4])],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    with pytest.raises(UnsupportedONNXOperatorError, match="NotARealOperator"):
        Plan.from_model_bytes(model.SerializeToString())


def test_plan_rejects_unsupported_attribute():
    graph = h.make_graph(
        [h.make_node("Relu", ["x"], ["y"], some_unknown_attr=1)],
        "bad",
        [h.make_tensor_value_info("x", T.FLOAT, [1, 4])],
        [h.make_tensor_value_info("y", T.FLOAT, [1, 4])],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    with pytest.raises(UnsupportedONNXOperatorError, match="some_unknown_attr"):
        Plan.from_model_bytes(model.SerializeToString())


def test_plan_rejects_missing_required_input():
    graph = h.make_graph(
        [h.make_node("MatMul", ["x"], ["y"])],
        "bad",
        [h.make_tensor_value_info("x", T.FLOAT, [2, 2])],
        [h.make_tensor_value_info("y", T.FLOAT, [2, 2])],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    with pytest.raises(UnsupportedONNXOperatorError, match="expects"):
        Plan.from_model_bytes(model.SerializeToString())


def test_plan_rejects_undefined_input_reference():
    graph = h.make_graph(
        [h.make_node("Add", ["x", "ghost"], ["y"])],
        "bad",
        [h.make_tensor_value_info("x", T.FLOAT, [1, 4])],
        [h.make_tensor_value_info("y", T.FLOAT, [1, 4])],
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    with pytest.raises(UnsupportedONNXOperatorError, match="undefined"):
        Plan.from_model_bytes(model.SerializeToString())


def test_plan_classifies_shape_metadata_as_host_integers():
    """``Shape`` chains must stay on the host, not become device tensors."""
    shape = [1, 3, 8, 8]
    graph = h.make_graph(
        [
            h.make_node("Shape", ["x"], ["shp"]),
            h.make_node("Gather", ["shp", "idx"], ["h"], axis=0),
            h.make_node("Unsqueeze", ["h", "ax"], ["h_vec"]),
            h.make_node("Concat", ["h_vec", "one"], ["newshape"], axis=0),
            h.make_node("Reshape", ["x", "newshape"], ["y"]),
        ],
        "meta",
        [h.make_tensor_value_info("x", T.FLOAT, shape)],
        [h.make_tensor_value_info("y", T.FLOAT, [1, 3, 8, 8])],
    )
    from onnx import numpy_helper

    for name, value in (("idx", [2]), ("ax", [0]), ("one", [8])):
        graph.initializer.append(
            numpy_helper.from_array(__import__("numpy").array(value, dtype=__import__("numpy").int64), name)
        )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    plan = Plan.from_model_bytes(model.SerializeToString())
    assert "shp" in plan.host_int_values
    assert "newshape" in plan.host_int_values


def test_alias_ops_do_not_allocate():
    graph = h.make_graph(
        [h.make_node("Relu", ["x"], ["r"]), h.make_node("Reshape", ["r", "s"], ["y"])],
        "alias",
        [h.make_tensor_value_info("x", T.FLOAT, [1, 4])],
        [h.make_tensor_value_info("y", T.FLOAT, [2, 2])],
    )
    from onnx import numpy_helper

    graph.initializer.append(
        numpy_helper.from_array(__import__("numpy").array([2, 2], dtype=__import__("numpy").int64), "s")
    )
    model = h.make_model(graph, opset_imports=[h.make_opsetid("", 17)])
    plan = Plan.from_model_bytes(model.SerializeToString())
    assert len(plan.alias_nodes) == 1


def test_every_registered_operator_has_a_lowering_or_is_alias_or_host_only():
    from taichi_vision.taichi_aot.neural_universal import runtime

    alias = {"Identity", "Reshape", "Squeeze", "Unsqueeze", "Flatten"}
    host_only = {"Shape", "ConstantOfShape", "Range", "Constant"}
    missing = sorted(
        name
        for name, spec in registry.OPS.items()
        if spec.implemented
        and name not in runtime.LOWER
        and name not in alias
        and name not in host_only
    )
    assert not missing, f"operators admitted but with no execution path: {missing}"
