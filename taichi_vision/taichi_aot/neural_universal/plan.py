"""ONNX graph validation, dtype analysis, and host/device value classification.

The plan deliberately keeps **no compile-time shape information** for device
tensors. Buffer shapes are computed at ``run()`` time from the concrete input
shapes, so one compiled ``neural_{backend}.tcm`` serves several input sizes.

Shape-metadata subgraphs (``Shape``/``Range``/``ConstantOfShape`` and the
integer arithmetic built on them) are classified as *host integer* values and
evaluated with NumPy during the run. Everything else lives on the device.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

import numpy as np

from . import registry
from .errors import UnsupportedONNXOperatorError
from .dtypes import F32, I32, I64, ONNX_ELEM_TYPE

#: Ops whose integer output is always shape metadata, regardless of its inputs.
HOST_INT_SOURCES: FrozenSet[str] = frozenset({
    "Shape", "Constant", "Range", "ConstantOfShape",
})

#: Ops that stay on the host only when every input is already a host integer.
HOST_INT_PROPAGATORS: FrozenSet[str] = frozenset({
    "Gather", "Concat", "Slice", "Split", "Add", "Sub", "Mul", "Div", "Mod",
    "Cast", "Unsqueeze", "Squeeze", "Reshape", "Flatten", "Where", "Equal",
    "Identity", "Neg", "Abs", "Clip", "ReduceSum", "ReduceProd", "Tile",
    "Expand", "Max", "Min", "Not", "And", "Or", "Xor", "Less", "Greater",
    "ReduceMax", "ReduceMin", "Pow", "Sum",
})

#: Ops whose output is just a reinterpretation of the input buffer.
ALIAS_OPS: FrozenSet[str] = frozenset(
    {"Reshape", "Squeeze", "Unsqueeze", "Flatten", "Identity"}
)

#: Ops producing a boolean mask (stored as i32 in this profile).
MASK_OPS: FrozenSet[str] = frozenset({"Less", "Greater", "Equal", "And", "Or", "Xor", "Not"})

#: Ops allowed to produce more than one output in this profile.
MULTI_OUTPUT_OPS: FrozenSet[str] = frozenset({"Split", "TopK"})


@dataclass
class GraphNode:
    index: int
    op: str
    domain: str
    name: str
    inputs: List[str]
    outputs: List[str]
    attrs: Dict[str, Any]
    spec: registry.OpSpec

    @property
    def output(self) -> str:
        return self.outputs[0]

@dataclass
class Plan:
    """Validated static description of a model."""

    input_names: List[str]
    input_ranks: Dict[str, int]
    output_names: List[str]
    nodes: List[GraphNode]
    dtypes: Dict[str, str]
    constants: Dict[str, np.ndarray]
    host_int_values: Set[str]
    alias_nodes: Dict[int, str]
    data_dependent: List[str]
    producer: Dict[str, "GraphNode"] = field(default_factory=dict)

    # ------------------------------------------------------------------ build

    @classmethod
    def from_model_bytes(cls, model_bytes: bytes) -> "Plan":
        import onnx

        model = onnx.load_model_from_string(model_bytes)
        return cls.from_graph(model)

    @classmethod
    def from_graph(cls, model) -> "Plan":
        from onnx import numpy_helper

        graph = model.graph
        opsets = {(o.domain or "ai.onnx"): int(o.version) for o in model.opset_import}
        for domain, version in opsets.items():
            if domain in ("ai.onnx", "") and version < 7:
                raise UnsupportedONNXOperatorError(
                    f"opset {version} is too old; minimum admitted is 7"
                )

        dtypes: Dict[str, str] = {}
        constants: Dict[str, np.ndarray] = {}

        for init in graph.initializer:
            array = numpy_helper.to_array(init)
            if array.dtype == np.float64:
                array = array.astype(np.float32)
            array = np.ascontiguousarray(array) if array.ndim > 0 else np.asarray(array)
            constants[init.name] = array
            dtypes[init.name] = _numpy_to_dtype(array)

        input_names: List[str] = []
        input_ranks: Dict[str, int] = {}
        for value in graph.input:
            if value.name in constants:
                continue
            elem = ONNX_ELEM_TYPE.get(value.type.tensor_type.elem_type)
            if elem is None:
                raise UnsupportedONNXOperatorError(
                    f"input {value.name} has unsupported element type "
                    f"{value.type.tensor_type.elem_type}"
                )
            dims = [d.dim_value for d in value.type.tensor_type.shape.dim]
            if not dims:
                raise UnsupportedONNXOperatorError(f"input {value.name} must declare a rank")
            dtypes[value.name] = elem
            input_ranks[value.name] = len(dims)
            input_names.append(value.name)

        nodes: List[GraphNode] = []
        defined: Set[str] = set(constants) | set(input_names)
        producer: Dict[str, GraphNode] = {}

        for index, node in enumerate(graph.node):
            spec = registry.require(node.op_type, node.domain)
            if not node.output:
                raise UnsupportedONNXOperatorError(f"{node.op_type} has no outputs")
            if len(node.output) != 1 and node.op_type not in MULTI_OUTPUT_OPS:
                raise UnsupportedONNXOperatorError(
                    f"{node.op_type} must produce exactly one output in this profile"
                )
            minimum, maximum = spec.arity
            if len(node.input) < minimum or (maximum is not None and len(node.input) > maximum):
                raise UnsupportedONNXOperatorError(
                    f"{node.op_type} expects {minimum}..{maximum} inputs, got {len(node.input)}"
                )
            attribute_names = [a.name for a in node.attribute]
            if len(set(attribute_names)) != len(attribute_names):
                raise UnsupportedONNXOperatorError(f"{node.op_type} has duplicate attributes")
            for attribute_name in attribute_names:
                if attribute_name not in spec.allowed_attrs:
                    raise UnsupportedONNXOperatorError(
                        f"{node.op_type} has unsupported attribute {attribute_name}"
                    )
            missing = spec.required_attrs - set(attribute_names)
            if missing:
                raise UnsupportedONNXOperatorError(
                    f"{node.op_type} is missing required attribute(s) {sorted(missing)}"
                )
            for position in spec.constant_inputs:
                if position < len(node.input) and node.input[position]:
                                name = node.input[position]
                                if name in constants:
                                    continue
                                # Computed integer chains (Shape -> Gather -> Concat) are
                                # resolved at run time; a float tensor here can never be.
                                if dtypes.get(name) in (I32, I64):
                                    continue
                                raise UnsupportedONNXOperatorError(
                                    f"{node.op_type} input {position} must be a constant or an "
                                    f"integer shape value in this profile"
                                )
            unknown = [name for name in node.input if name and name not in defined]
            if unknown:
                raise UnsupportedONNXOperatorError(
                    f"{node.op_type} references undefined input(s) {unknown}"
                )
            for name in node.output:
                if not name:
                    raise UnsupportedONNXOperatorError(
                        f"{node.op_type} output elision is not admitted"
                    )
                if name in defined:
                    raise UnsupportedONNXOperatorError(f"{node.op_type} redefines tensor {name}")

            attrs = {a.name: _attribute_value(a) for a in node.attribute}
            info = GraphNode(index, node.op_type, node.domain or "ai.onnx", node.name or "",
                             list(node.input), list(node.output), attrs, spec)
            nodes.append(info)

            if node.op_type == "Constant":
                value = attrs.get("value")
                if value is None:
                    raise UnsupportedONNXOperatorError("Constant without value attribute")
                array = np.asarray(value)
                if array.ndim > 0:
                    array = np.ascontiguousarray(array)
                if array.dtype == np.float64:
                    array = array.astype(np.float32)
                constants[info.output] = array
                dtypes[info.output] = _numpy_to_dtype(array)
            else:
                for out_name in info.outputs:
                    dtypes[out_name] = _output_dtype(info, dtypes, out_name)
            for name in node.output:
                defined.add(name)
                producer[name] = info

        output_names = [value.name for value in graph.output]
        for name in output_names:
            if name not in dtypes:
                raise UnsupportedONNXOperatorError(f"graph output {name} is never produced")

        host_int = _classify_host_int(nodes, constants, dtypes)
        alias_nodes = {
            node.index: node.inputs[0]
            for node in nodes
            if node.op in ALIAS_OPS and node.output not in host_int
        }
        data_dependent = [node.output for node in nodes if node.op == "NonZero"]

        return cls(
            input_names=input_names,
            input_ranks=input_ranks,
            output_names=output_names,
            nodes=nodes,
            dtypes=dtypes,
            constants=constants,
            host_int_values=host_int,
            alias_nodes=alias_nodes,
            data_dependent=data_dependent,
            producer=producer,
        )

    # --------------------------------------------------------------- queries

    def is_host_int(self, name: str) -> bool:
        return name in self.host_int_values

    def dtype(self, name: str) -> str:
        return self.dtypes[name]


def _classify_host_int(nodes: Sequence[GraphNode], constants: Dict[str, np.ndarray],
                       dtypes: Dict[str, str]) -> Set[str]:
    """Fixed-point classification of shape-metadata integer values."""
    host: Set[str] = set()
    for name, array in constants.items():
        if array.dtype.kind in "iub":
            host.add(name)

    changed = True
    while changed:
        changed = False
        for node in nodes:
            if node.op == "Constant":
                continue
            out = node.output
            if out in host or dtypes.get(out) not in (I32, I64):
                continue
            if node.op in HOST_INT_SOURCES:
                host.add(out)
                changed = True
                continue
            if node.op in HOST_INT_PROPAGATORS:
                operands = [name for name in node.inputs if name]
                if operands and all(name in host for name in operands):
                    host.add(out)
                    changed = True
    return host


def _numpy_to_dtype(array: np.ndarray) -> str:
    if array.dtype in (np.float32, np.float64):
        return F32
    if array.dtype == np.int32:
        return I32
    if array.dtype in (np.int64, np.uint32, np.uint64):
        return I64
    if array.dtype == np.bool_:
        return I32
    raise UnsupportedONNXOperatorError(f"unsupported constant dtype {array.dtype}")


def _attribute_value(attribute) -> Any:
    import onnx
    from onnx import helper, numpy_helper

    value = helper.get_attribute_value(attribute)
    if isinstance(value, onnx.TensorProto):
        array = numpy_helper.to_array(value)
        if array.dtype == np.float64:
            array = array.astype(np.float32)
        return np.ascontiguousarray(array) if array.ndim > 0 else np.asarray(array)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _output_dtype(node: GraphNode, dtypes: Dict[str, str], out_name: str) -> str:
    op = node.op
    if op in MASK_OPS:
        return I32
    if op == "Shape":
        return I64
    if op == "TopK":
        if not node.inputs or dtypes.get(node.inputs[0]) != F32:
            input_dtype = dtypes.get(node.inputs[0]) if node.inputs else None
            raise UnsupportedONNXOperatorError(
                f"TopK input dtype {input_dtype!r} is unsupported; this profile admits FP32 only"
            )
        return F32 if out_name == node.outputs[0] else I64
    if op == "NonZero":
        if not node.inputs or dtypes.get(node.inputs[0]) not in (F32, I32):
            input_dtype = dtypes.get(node.inputs[0]) if node.inputs else None
            raise UnsupportedONNXOperatorError(
                f"NonZero input dtype {input_dtype!r} is unsupported; this profile admits FP32 and I32/BOOL"
            )
        return I64
    if op == "ArgMax":
        return I32
    if op == "Cast":
        from .dtypes import ONNX_CAST_TO

        target = int(node.attrs["to"])
        if target not in ONNX_CAST_TO:
            raise UnsupportedONNXOperatorError(f"Cast to unsupported element type {target}")
        return ONNX_CAST_TO[target]
    if op == "ConstantOfShape":
        value = node.attrs.get("value")
        if value is None:
            return I64
        array = np.asarray(value)
        if array.dtype == np.int32:
            return I32
        if array.dtype.kind in "iu":
            return I64
        return F32
    if op == "Range":
        return dtypes.get(node.inputs[0], F32) if node.inputs else F32
    if op == "Where":
        return dtypes.get(node.inputs[1], F32) if len(node.inputs) > 1 else F32
    if op == "Split":
        return dtypes.get(node.inputs[0], F32)
    first = node.inputs[0] if node.inputs else None
    if first and first in dtypes:
        return dtypes[first]
    return F32
