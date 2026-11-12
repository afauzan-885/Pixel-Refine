"""Declarative operator registry for the neural universal runtime.

The registry is the single source of truth for **which operators are admitted**
and **what shape of graph node each one may describe**. Adding support for a new
ONNX operator means adding one :class:`OpSpec` here plus one lowering function in
:mod:`plan`; ``runtime`` never needs to change.

Anything not present here must be rejected during planning. That is what keeps
the runtime fail-closed instead of silently skipping nodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Optional, Tuple

from .errors import UnsupportedONNXOperatorError
from .dtypes import F32, I32, I64

STANDARD_DOMAINS: FrozenSet[str] = frozenset({"", "ai.onnx"})
CUSTOM_DOMAINS: Dict[str, str] = {
    "Gelu": "com.microsoft",
    "FusedConv": "com.microsoft",
    "FusedMatMul": "com.microsoft",
    "MultiHeadAttention": "com.microsoft",
    "DmlFusedConv": "com.microsoft.dml",
}


@dataclass(frozen=True)
class OpSpec:
    """Admission contract for one ONNX operator."""

    name: str
    arity: Tuple[int, Optional[int]]
    allowed_attrs: FrozenSet[str] = frozenset()
    required_attrs: FrozenSet[str] = frozenset()
    #: Input positions that must resolve to compile-time constants.
    constant_inputs: FrozenSet[int] = frozenset()
    #: Input positions that must be constant integer vectors (shapes, axes...).
    integer_vector_inputs: FrozenSet[int] = frozenset()
    #: Input positions that may hold integer *data* (indices) on the device.
    index_inputs: FrozenSet[int] = frozenset()
    #: Dtypes the operator may consume. Empty means "float only".
    input_dtypes: FrozenSet[str] = frozenset({F32})
    #: Dtype of the first output when it is not F32.
    output_dtype: Optional[str] = None
    #: Set when the lowering is implemented. False keeps the op rejected.
    implemented: bool = True
    domain: str = "ai.onnx"

    def domain_expected(self) -> str:
        return CUSTOM_DOMAINS.get(self.name, "ai.onnx")


def _spec(name: str, arity, attrs=(), required=(), const=(), ivec=(), index=(),
          input_dtypes=None, output_dtype=None, implemented=True) -> OpSpec:
    return OpSpec(
        name=name,
        arity=arity,
        allowed_attrs=frozenset(attrs),
        required_attrs=frozenset(required),
        constant_inputs=frozenset(const),
        integer_vector_inputs=frozenset(ivec),
        index_inputs=frozenset(index),
        input_dtypes=frozenset(input_dtypes or {F32}),
        output_dtype=output_dtype,
        implemented=implemented,
        domain=CUSTOM_DOMAINS.get(name, "ai.onnx"),
    )


_SPEC_LIST = [
    # ------------------------------------------------------------- convolution
    _spec("Conv", (2, 3), attrs=("auto_pad", "dilations", "group", "kernel_shape", "pads", "strides"),
          index=(2,)),
    _spec("FusedConv", (2, 3), attrs=("activation", "auto_pad", "dilations", "group",
                                      "kernel_shape", "pads", "strides"),
          required=("activation",), index=(2,)),
    _spec("DmlFusedConv", (2, 3), attrs=("fused_activation", "fused_activation_domain",
                                         "fused_activation_since_version", "auto_pad",
                                         "dilations", "group", "kernel_shape", "pads",
                                         "strides"),
          required=("fused_activation",), index=(2,)),
    _spec("ConvTranspose", (2, 3), attrs=("auto_pad", "dilations", "group", "kernel_shape",
                                          "output_padding", "output_shape", "pads", "strides"),
          index=(2,)),
    # ------------------------------------------------------------------ linear
    _spec("MatMul", (2, 2)),
    _spec("Gemm", (2, 3), attrs=("alpha", "beta", "transA", "transB")),
    _spec("FusedMatMul", (2, 2), attrs=("alpha", "transA", "transB", "transBatchA", "transBatchB")),
    # --------------------------------------------------------------- unary
    _spec("Relu", (1, 1)),
    _spec("Sigmoid", (1, 1)),
    _spec("Tanh", (1, 1)),
    _spec("Gelu", (1, 1), attrs=("approximate",)),
    _spec("Softplus", (1, 1)),
    _spec("Abs", (1, 1)),
    _spec("Sqrt", (1, 1)),
    _spec("Neg", (1, 1)),
    _spec("Erf", (1, 1)),
    _spec("Exp", (1, 1)),
    _spec("Log", (1, 1)),
    _spec("Floor", (1, 1)),
    _spec("Ceil", (1, 1)),
    _spec("Sin", (1, 1)),
    _spec("Cos", (1, 1)),
    _spec("Reciprocal", (1, 1)),
    _spec("Sign", (1, 1)),
    _spec("LeakyRelu", (1, 1), attrs=("alpha",)),
    _spec("Clip", (1, 3), attrs=("max", "min"), const=(1, 2)),
    _spec("PRelu", (2, 2)),
    _spec("Identity", (1, 1)),
    _spec("Cast", (1, 1), attrs=("to",), required=("to",), input_dtypes=(F32, I32, I64)),
    _spec("Not", (1, 1), input_dtypes=(I32,), output_dtype=I32),
    # -------------------------------------------------------------- binary
    _spec("Add", (2, 2)),
    _spec("Sub", (2, 2)),
    _spec("Mul", (2, 2)),
    _spec("Div", (2, 2)),
    _spec("Pow", (2, 2)),
    _spec("Mod", (2, 2), attrs=("fmod",)),
    _spec("Max", (2, None)),
    _spec("Min", (2, None)),
    _spec("Sum", (1, None)),
    _spec("Less", (2, 2), input_dtypes=(F32, I32), output_dtype=I32),
    _spec("Greater", (2, 2), input_dtypes=(F32, I32), output_dtype=I32),
    _spec("Equal", (2, 2), input_dtypes=(F32, I32, I64), output_dtype=I32),
    _spec("And", (2, 2), input_dtypes=(I32,), output_dtype=I32),
    _spec("Or", (2, 2), input_dtypes=(I32,), output_dtype=I32),
    _spec("Xor", (2, 2), input_dtypes=(I32,), output_dtype=I32),
    _spec("Where", (3, 3), input_dtypes=(I32,)),
    # --------------------------------------------------------------- norm
    _spec("InstanceNormalization", (2, 3), attrs=("epsilon",)),
    _spec("LayerNormalization", (2, 3), attrs=("axis", "epsilon", "stash_type")),
    _spec("BatchNormalization", (5, 5), attrs=("epsilon", "momentum", "training_mode"),
          ),
    _spec("Softmax", (1, 1), attrs=("axis",)),
    _spec("LogSoftmax", (1, 1), attrs=("axis",)),
    # -------------------------------------------------------------- reduce
    _spec("ReduceMean", (1, 2), attrs=("axes", "keepdims", "noop_with_empty_axes"), const=(1,),
          ivec=(1,)),
    _spec("ReduceSum", (1, 2), attrs=("axes", "keepdims", "noop_with_empty_axes"), const=(1,),
          ivec=(1,)),
    _spec("ReduceMax", (1, 2), attrs=("axes", "keepdims", "noop_with_empty_axes"), const=(1,),
          ivec=(1,)),
    _spec("ReduceMin", (1, 2), attrs=("axes", "keepdims", "noop_with_empty_axes"), const=(1,),
          ivec=(1,)),
    _spec("ReduceL2", (1, 2), attrs=("axes", "keepdims", "noop_with_empty_axes"), const=(1,),
          ivec=(1,)),
    # ------------------------------------------------------------- movement
    _spec("Gather", (2, 2), attrs=("axis",), index=(1,)),
    _spec("GatherElements", (2, 2), attrs=("axis",), index=(1,)),
    _spec("Concat", (1, None), attrs=("axis",), required=("axis",)),
    _spec("Split", (1, 2), attrs=("axis", "num_outputs", "split"), const=(1,), ivec=(1,)),
    _spec("Slice", (3, 5), const=(1, 2, 3, 4), ivec=(1, 2, 3, 4)),
    _spec("Pad", (2, 3), attrs=("mode",), const=(1, 2), ivec=(1,)),
    _spec("Transpose", (1, 1), attrs=("perm",)),
    _spec("Expand", (2, 2), const=(1,), ivec=(1,)),
    _spec("Tile", (2, 2), const=(1,), ivec=(1,)),
    _spec("SpaceToDepth", (1, 1), attrs=("blocksize",), required=("blocksize",)),
    _spec("DepthToSpace", (1, 1), attrs=("blocksize", "mode"), required=("blocksize",)),
    _spec("Resize", (1, 4), attrs=("coordinate_transformation_mode", "cubic_coeff_a",
                                   "exclude_outside", "extrapolation_value", "mode",
                                   "nearest_mode", "antialias", "keep_aspect_ratio_policy"),
          const=(1, 2, 3), ivec=(3,)),
    _spec("Reshape", (2, 2), attrs=("allowzero",), const=(1,), ivec=(1,)),
    _spec("Flatten", (1, 1), attrs=("axis",)),
    _spec("Squeeze", (1, 2), attrs=("axes",), const=(1,), ivec=(1,)),
    _spec("Unsqueeze", (1, 2), attrs=("axes",), const=(1,), ivec=(1,)),
    # --------------------------------------------------------------- pooling
    _spec("AveragePool", (1, 1), attrs=("auto_pad", "ceil_mode", "count_include_pad",
                                        "kernel_shape", "pads", "strides"),
          required=("kernel_shape",)),
    _spec("MaxPool", (1, 1), attrs=("auto_pad", "ceil_mode", "dilations", "kernel_shape",
                                    "pads", "storage_order", "strides"),
          required=("kernel_shape",)),
    _spec("GlobalAveragePool", (1, 1)),
    # ------------------------------------------------------- index / metadata
        _spec("Constant", (0, 0), attrs=("value",), required=("value",)),
        _spec("Shape", (1, 1), attrs=("start", "end"), output_dtype=I64),
    _spec("ConstantOfShape", (1, 1), attrs=("value",), const=(0,), ivec=(0,)),
    _spec("Range", (3, 3), input_dtypes=(F32, I32, I64)),
    _spec("NonZero", (1, 1), output_dtype=I64),
    _spec("TopK", (2, 2), attrs=("axis", "largest", "sorted"), const=(1,), ivec=(1,)),
    _spec("ArgMax", (1, 2), attrs=("axis", "keepdims", "select_last_index"), const=(1,), ivec=(1,)),
    # ------------------------------------------------------------- attention
    _spec("MultiHeadAttention", (3, 3), attrs=("num_heads", "mask_filter_value", "unidirectional"),
          required=("num_heads",)),
]

OPS: Dict[str, OpSpec] = {spec.name: spec for spec in _SPEC_LIST}

if len(OPS) != len(_SPEC_LIST):
    duplicates = len(_SPEC_LIST) - len(OPS)
    raise RuntimeError(f"duplicate operator names in registry: {duplicates}")

#: Operators the shipped model families need. Kept explicit so a regression in
#: the registry fails loudly instead of shrinking silently.
REQUIRED_FOR_SHIPPED_MODELS: FrozenSet[str] = frozenset({
    "Abs", "Add", "And", "AveragePool", "Cast", "Clip", "Concat", "ConstantOfShape",
    "Conv", "ConvTranspose", "Cos", "Div", "DmlFusedConv", "Equal", "Erf", "Exp",
    "Expand", "Flatten", "Floor", "Gather", "GatherElements", "Gelu", "Greater",
    "Identity", "InstanceNormalization", "LayerNormalization", "Less", "Log",
    "LogSoftmax", "MatMul", "MaxPool", "Mod", "Mul", "MultiHeadAttention", "Neg",
    "NonZero", "PRelu", "Pad", "Pow", "Range", "ReduceL2", "ReduceMean", "ReduceSum",
    "Relu", "Reshape", "Resize", "Shape", "Sigmoid", "Sin", "Slice", "Softmax",
    "Softplus", "SpaceToDepth", "Split", "Sqrt", "Squeeze", "Sub", "Tanh", "Tile",
    "TopK", "Transpose", "Unsqueeze", "Where",
})

_MISSING = REQUIRED_FOR_SHIPPED_MODELS - set(OPS)
if _MISSING:
    raise RuntimeError(f"registry is missing operators required by shipped models: {sorted(_MISSING)}")


def require(name: str, domain: Optional[str] = None) -> OpSpec:
    """Return the spec for ``name`` or raise a diagnosable error."""
    spec = OPS.get(name)
    if spec is None:
        raise UnsupportedONNXOperatorError(
            f"Unsupported ONNX operator: {domain or 'ai.onnx'}::{name}. "
            f"Add an OpSpec to neural_universal/registry.py to admit it."
        )
    if not spec.implemented:
        raise UnsupportedONNXOperatorError(
            f"Operator {name} is registered but has no lowering implementation yet."
        )
    expected = spec.domain_expected()
    actual = domain or "ai.onnx"
    if actual != expected:
        raise UnsupportedONNXOperatorError(
            f"{name} requires domain {expected}, got {actual}"
        )
    return spec


def implemented_names() -> Tuple[str, ...]:
    return tuple(sorted(name for name, spec in OPS.items() if spec.implemented))


__all__ = [
    "OpSpec",
    "OPS",
    "REQUIRED_FOR_SHIPPED_MODELS",
    "require",
    "implemented_names",
    "CUSTOM_DOMAINS",
    "STANDARD_DOMAINS",
]