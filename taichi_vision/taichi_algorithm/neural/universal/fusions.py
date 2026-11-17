"""Planning-level ONNX graph fusion for the universal kernel pool.

Fusion here is a *planning* concern: :func:`build_fusion_plan` inspects a
validated :class:`~taichi_vision.taichi_algorithm.neural.universal.plan.Plan`
once and returns a :class:`FusionPlan` describing every fused dispatch the run
loop may execute. Runtime-only facts (concrete shapes, broadcast strides) are
re-checked at dispatch time by :func:`run_fused_dispatch`, so a candidate whose
shapes do not match falls back to the next alternative or to the ordinary
per-node lowerings — nothing is ever skipped silently.

Execution semantics match the original inline fusion blocks:

* One trigger node may carry several *alternatives* (ordered), e.g. a
  ``Mul→Clip`` edge is planned as ``mul_scalar_clip`` → ``mul_clip`` →
  ``binary_unary`` broadcast; the loop tries them in order and stops at the
  first success.
* Cross-pattern priority emerges from plan order at run time: the first
  dispatch that executes marks its absorbed nodes fused, so a
  ``Sigmoid→Mul→Clip`` chain (triggered earlier in the graph) naturally wins
  over the shorter ``Mul→Clip``.
* Conv activation folding is decided at planning time and always applies (the
  generic conv kernels take an ``act`` parameter), matching the original
  unconditional activation skip.

Every dynamic pattern is guarded by ``pool_graphs``: a fused graph the staged
pool TCM does not contain is planned as ordinary ONNX steps instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Mapping, Optional, Sequence, Set, Tuple

import numpy as np

from .dtypes import F32, broadcast_strides, pad_to, product
from .plan import GraphNode, Plan

# ---------------------------------------------------------------------------
# opcode tables shared with the runtime lowerings
# ---------------------------------------------------------------------------

UNARY_CODES: Dict[str, int] = {
    "Relu": 1, "Sigmoid": 2, "Tanh": 3, "Gelu": 4, "Abs": 7, "Sqrt": 6,
    "Neg": 8, "Erf": 9, "Softplus": 10, "Floor": 11, "Exp": 12, "Log": 13,
    "Sin": 14, "Cos": 15, "Ceil": 18, "Sign": 19, "Reciprocal": 17,
}

BINARY_CODES: Dict[str, int] = {
    "Add": 0, "Sub": 1, "Mul": 2, "Div": 3, "Pow": 4, "Max": 5, "Min": 6,
    "Less": 7, "Greater": 8, "Equal": 9, "Mod": 10, "And": 11,
}

#: Unary whitelist for the fused binary→unary kernel. Sigmoid, Relu, and Erf
#: are excluded until their NaN edge behavior is reconciled with the ORT
#: oracle for this fused context (LeakyRelu has no entry either, matching the
#: original parameter helper).
UNARY_BINARY_CODES: Dict[str, int] = {
    "Tanh": 3, "Softplus": 10, "Log": 13,
}
UNARY_BINARY_OP_CODES: Dict[str, int] = {"Add": 0, "Sub": 1, "Mul": 2}

CLIP_CODE = 21
SQRT_CODE = 6

_F32_MIN = -3.4028234663852886e38
_F32_MAX = 3.4028234663852886e38


# ---------------------------------------------------------------------------
# plan structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FusedDispatch:
    """One planned fused kernel dispatch, keyed by its trigger node."""

    kind: str
    graph_name: str
    output_name: str
    trigger_index: int
    fused_nodes: Tuple[int, ...]
    params: Mapping[str, object]


@dataclass
class FusionPlan:
    """Every fusion decided for one plan; consumed by the runtime run loop."""

    #: trigger node index -> ordered alternative dispatches (first wins)
    dispatches: Dict[int, Tuple[FusedDispatch, ...]] = field(default_factory=dict)
    #: union of all absorbed node indices (documentation/testing; the run loop
    #: skips a node only after some dispatch actually executed)
    fused_nodes: FrozenSet[int] = frozenset()
    #: conv node index -> (activation node index, output name, activation code)
    conv_activation: Dict[int, Tuple[int, str, int]] = field(default_factory=dict)
    #: activation nodes folded into their Conv producer (always skippable)
    conv_activation_skipped: FrozenSet[int] = frozenset()


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------


def _consumers(plan: Plan) -> Dict[str, List[GraphNode]]:
    consumers: Dict[str, List[GraphNode]] = {}
    for node in plan.nodes:
        for name in node.inputs:
            if name:
                consumers.setdefault(name, []).append(node)
    return consumers


def _clip_bounds(
    node: GraphNode, plan: Plan, *, require_f32: bool = False
) -> Optional[Tuple[float, float]]:
    """Scalar FP32 Clip bounds, or ``None`` when a bound is not usable.

    Attribute bounds fall back to the full f32 range; input bounds must be
    compile-time constants. ``require_f32`` mirrors the stricter checker the
    original code applied to Add→Sqrt→Clip / Sub→Clip→Sqrt chains.
    """
    low = _F32_MIN
    high = _F32_MAX
    for position, bound_name, fallback in ((1, "min", _F32_MIN), (2, "max", _F32_MAX)):
        if position >= len(node.inputs) or not node.inputs[position]:
            value = node.attrs.get(bound_name, fallback)
        else:
            name = node.inputs[position]
            constant = plan.constants.get(name)
            if constant is None or np.asarray(constant).size == 0:
                return None
            if require_f32 and plan.dtypes.get(name) != F32:
                return None
            array = np.asarray(constant)
            if require_f32 and not np.isfinite(array).all():
                return None
            value = float(array.reshape(-1)[0])
        if position == 1:
            low = float(value)
        else:
            high = float(value)
    return low, high


def _scalar_constant(name: Optional[str], plan: Plan) -> Optional[Tuple[float, Tuple[int, ...]]]:
    """The finite scalar value and shape of a compile-time constant."""
    if not name:
        return None
    constant = plan.constants.get(name)
    if constant is None:
        return None
    array = np.asarray(constant)
    if array.size != 1 or not np.isfinite(array).all():
        return None
    return float(array.reshape(-1)[0]), tuple(int(d) for d in array.shape)


# ---------------------------------------------------------------------------
# individual pattern collectors
#
# Each returns (trigger_index, FusedDispatch) candidates. The assembler keeps
# every candidate: dispatches for the same trigger become ordered alternatives.
# ---------------------------------------------------------------------------


def _collect_sub_sub_div(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """Private standard-domain FP32 ``Sub -> Sub -> Div`` chains.

    Runtime checks require equal shapes for all four operands and each
    intermediate/output. Fanout, requested intermediates, attributes, mixed
    dtype, duplicate external operands, or shape mismatch all decline.
    """
    candidates: List[Tuple[int, FusedDispatch]] = []
    graph_names = set(plan.dtypes) | set(plan.constants)
    graph_names.update(plan.input_names)
    graph_names.update(plan.output_names)
    for graph_node in plan.nodes:
        graph_names.update(name for name in graph_node.inputs if name)
        graph_names.update(name for name in graph_node.outputs if name)

    for first in plan.nodes:
        if first.domain != "ai.onnx" or first.op != "Sub":
            continue
        if first.attrs or len(first.inputs) != 2 or len(first.outputs) != 1:
            continue
        first_mid = first.output
        if first_mid in requested or plan.dtypes.get(first_mid) != F32:
            continue
        if any(plan.dtypes.get(name) != F32 for name in first.inputs):
            continue
        first_uses = consumers.get(first_mid, ())
        if len(first_uses) != 1:
            continue
        second = first_uses[0]
        if second.index != first.index + 1:
            continue
        if (second.domain != "ai.onnx" or second.op != "Sub" or second.attrs
                or len(second.inputs) != 2 or second.inputs.count(first_mid) != 1
                or len(second.outputs) != 1):
            continue
        second_mid = second.output
        if second_mid in requested or plan.dtypes.get(second_mid) != F32:
            continue
        other_second = second.inputs[1 - second.inputs.index(first_mid)]
        if plan.dtypes.get(other_second) != F32:
            continue
        second_uses = consumers.get(second_mid, ())
        if len(second_uses) != 1:
            continue
        last = second_uses[0]
        if last.index != second.index + 1:
            continue
        if (last.domain != "ai.onnx" or last.op != "Div" or last.attrs
                or len(last.inputs) != 2 or last.inputs.count(second_mid) != 1
                or len(last.outputs) != 1):
            continue
        other_last = last.inputs[1 - last.inputs.index(second_mid)]
        if plan.dtypes.get(other_last) != F32 or plan.dtypes.get(last.output) != F32:
            continue
        external = [first.inputs[0], first.inputs[1], other_second, other_last]
        if len(set(external)) != 4:
            continue
        scratch_first = f"__nu_fused_sub_sub_div_{first.index}_first"
        scratch_second = f"__nu_fused_sub_sub_div_{first.index}_second"
        if {scratch_first, scratch_second} & graph_names:
            continue
        candidates.append((first.index, FusedDispatch(
            kind="sub_sub_div",
            graph_name="nu_fused_sub_sub_div",
            output_name=last.output,
            trigger_index=first.index,
            fused_nodes=(second.index, last.index),
            params={
                "a": external[0], "b": external[1],
                "c": external[2], "d": external[3],
                "first_tmp": scratch_first, "second_tmp": scratch_second,
                "trigger_node": first.index,
            },
        )))
    return candidates


def _collect_unary_binary(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """Standard-domain FP32 ``unary -> binary`` edges with unique private inputs.

    A binary node with two eligible unary producers is deliberately left
    unfused; this pass composes exactly one unary producer and one binary node.
    """
    candidates: List[Tuple[int, FusedDispatch]] = []
    per_binary: Dict[int, List[Tuple[GraphNode, str, int, int]]] = {}
    for unary in plan.nodes:
        unary_code = UNARY_BINARY_CODES.get(unary.op)
        if unary.domain != "ai.onnx" or unary_code is None:
            continue
        if unary.attrs or len(unary.inputs) != 1 or len(unary.outputs) != 1:
            continue
        intermediate = unary.output
        if intermediate in requested or plan.dtypes.get(intermediate) != F32:
            continue
        if plan.dtypes.get(unary.inputs[0]) != F32:
            continue
        uses = consumers.get(intermediate, ())
        if len(uses) != 1:
            continue
        binary = uses[0]
        binary_code = UNARY_BINARY_OP_CODES.get(binary.op)
        if binary.domain != "ai.onnx" or binary_code is None:
            continue
        if binary.attrs or len(binary.inputs) != 2 or len(binary.outputs) != 1:
            continue
        if binary.inputs.count(intermediate) != 1:
            continue
        if plan.dtypes.get(binary.output) != F32:
            continue
        other_input = binary.inputs[1 - binary.inputs.index(intermediate)]
        if plan.dtypes.get(other_input) != F32:
            continue
        per_binary.setdefault(binary.index, []).append(
            (unary, other_input, unary_code, binary_code)
        )

    for binary_index, matches in per_binary.items():
        if len(matches) != 1:
            continue
        unary, other_input, unary_code, binary_code = matches[0]
        binary = plan.nodes[binary_index]
        unary_is_left = 1 if binary.inputs[0] == unary.output else 0
        candidates.append((unary.index, FusedDispatch(
            kind="unary_binary",
            graph_name="nu_fused_unary_binary",
            output_name=binary.output,
            trigger_index=unary.index,
            fused_nodes=(binary.index,),
            params={
                "x": unary.inputs[0], "other": other_input,
                "unary_code": unary_code, "binary_code": binary_code,
                "unary_is_left": unary_is_left, "lo": 0.0, "hi": 0.0,
                "trigger_node": unary.index,
            },
        )))
    return candidates


def _collect_add_sqrt_clip(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """Standard-domain ``Add -> Sqrt -> Clip`` with scalar FP32 bounds."""
    candidates: List[Tuple[int, FusedDispatch]] = []
    for binary in plan.nodes:
        if binary.domain != "ai.onnx" or binary.op != "Add":
            continue
        if binary.output in requested:
            continue
        if plan.dtypes.get(binary.output) != F32 or any(
            plan.dtypes.get(name) != F32 for name in binary.inputs
        ):
            continue
        first_uses = consumers.get(binary.output, ())
        if len(first_uses) != 1:
            continue
        middle = first_uses[0]
        if (middle.op != "Sqrt" or len(middle.inputs) != 1
                or middle.inputs[0] != binary.output
                or middle.domain != "ai.onnx"
                or middle.output in requested
                or plan.dtypes.get(middle.output) != F32):
            continue
        second_uses = consumers.get(middle.output, ())
        if len(second_uses) != 1:
            continue
        clip = second_uses[0]
        if (clip.op != "Clip" or not 1 <= len(clip.inputs) <= 3
                or clip.inputs[0] != middle.output
                or clip.domain != "ai.onnx"
                or plan.dtypes.get(clip.output) != F32):
            continue
        bounds = _clip_bounds(clip, plan, require_f32=True)
        if bounds is None:
            continue
        clip_lo, clip_hi = bounds
        candidates.append((binary.index, FusedDispatch(
            kind="add_sqrt_clip",
            graph_name="nu_add_sqrt_clip_broadcast",
            output_name=clip.output,
            trigger_index=binary.index,
            fused_nodes=(middle.index, clip.index),
            params={
                "a": binary.inputs[0], "b": binary.inputs[1],
                "clip_lo": clip_lo, "clip_hi": clip_hi,
                "trigger_node": binary.index,
            },
        )))
    return candidates


def _collect_sub_clip_sqrt(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """Standard-domain ``Sub -> Clip -> Sqrt`` with scalar FP32 bounds."""
    candidates: List[Tuple[int, FusedDispatch]] = []
    for binary in plan.nodes:
        if binary.domain != "ai.onnx" or binary.op != "Sub":
            continue
        if binary.output in requested:
            continue
        if plan.dtypes.get(binary.output) != F32 or any(
            plan.dtypes.get(name) != F32 for name in binary.inputs
        ):
            continue
        first_uses = consumers.get(binary.output, ())
        if len(first_uses) != 1:
            continue
        clip = first_uses[0]
        if (clip.op != "Clip" or not 1 <= len(clip.inputs) <= 3
                or clip.inputs[0] != binary.output or clip.domain != "ai.onnx"
                or clip.output in requested
                or plan.dtypes.get(clip.output) != F32):
            continue
        bounds = _clip_bounds(clip, plan, require_f32=True)
        if bounds is None:
            continue
        clip_lo, clip_hi = bounds
        second_uses = consumers.get(clip.output, ())
        if len(second_uses) != 1:
            continue
        sqrt = second_uses[0]
        if (sqrt.op != "Sqrt" or len(sqrt.inputs) != 1
                or sqrt.inputs[0] != clip.output or sqrt.domain != "ai.onnx"
                or plan.dtypes.get(sqrt.output) != F32):
            continue
        candidates.append((binary.index, FusedDispatch(
            kind="sub_clip_sqrt",
            graph_name="nu_sub_clip_sqrt_broadcast",
            output_name=sqrt.output,
            trigger_index=binary.index,
            fused_nodes=(clip.index, sqrt.index),
            params={
                "a": binary.inputs[0], "b": binary.inputs[1],
                "clip_lo": clip_lo, "clip_hi": clip_hi,
                "trigger_node": binary.index,
            },
        )))
    return candidates


def _collect_sigmoid_mul_clip(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """Private FP32 ``Sigmoid -> Mul -> Clip`` (WeightNet gate head).

    The kernel evaluates ``clip(sigmoid(a) * b)`` element-wise, so the runtime
    requires the sigmoid input, the other Mul operand, and the output to share
    one flat shape.
    """
    candidates: List[Tuple[int, FusedDispatch]] = []
    for sigmoid in plan.nodes:
        if sigmoid.domain != "ai.onnx" or sigmoid.op != "Sigmoid":
            continue
        if sigmoid.attrs or len(sigmoid.inputs) != 1 or len(sigmoid.outputs) != 1:
            continue
        if sigmoid.output in requested or plan.dtypes.get(sigmoid.output) != F32:
            continue
        if plan.dtypes.get(sigmoid.inputs[0]) != F32:
            continue
        mul_uses = consumers.get(sigmoid.output, ())
        if len(mul_uses) != 1:
            continue
        mul = mul_uses[0]
        if (mul.domain != "ai.onnx" or mul.op != "Mul" or mul.attrs
                or len(mul.inputs) != 2 or mul.inputs.count(sigmoid.output) != 1
                or mul.output in requested
                or plan.dtypes.get(mul.output) != F32):
            continue
        other = mul.inputs[1 - mul.inputs.index(sigmoid.output)]
        if plan.dtypes.get(other) != F32:
            continue
        clip_uses = consumers.get(mul.output, ())
        if len(clip_uses) != 1:
            continue
        clip = clip_uses[0]
        if (clip.op != "Clip" or not 1 <= len(clip.inputs) <= 3
                or clip.inputs[0] != mul.output or clip.domain != "ai.onnx"
                or plan.dtypes.get(clip.output) != F32):
            continue
        bounds = _clip_bounds(clip, plan, require_f32=True)
        if bounds is None:
            continue
        clip_lo, clip_hi = bounds
        candidates.append((sigmoid.index, FusedDispatch(
            kind="sigmoid_mul_clip",
            graph_name="nu_sigmoid_mul_clip",
            output_name=clip.output,
            trigger_index=sigmoid.index,
            fused_nodes=(mul.index, clip.index),
            params={
                "a": sigmoid.inputs[0], "b": other,
                "clip_lo": clip_lo, "clip_hi": clip_hi,
                "trigger_node": sigmoid.index,
            },
        )))
    return candidates


def _collect_sub_square(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """FP32 ``Sub -> Pow(exponent=2)`` for the generic square kernel."""
    candidates: List[Tuple[int, FusedDispatch]] = []
    for node in plan.nodes:
        if node.op != "Sub" or node.output in requested:
            continue
        if plan.dtypes.get(node.output) != F32:
            continue
        if any(plan.dtypes.get(name) != F32 for name in node.inputs):
            continue
        uses = consumers.get(node.output, ())
        if len(uses) != 1:
            continue
        power = uses[0]
        if power.op != "Pow" or len(power.inputs) != 2 or power.inputs[0] != node.output:
            continue
        if plan.dtypes.get(power.output) != F32:
            continue
        if plan.dtypes.get(power.inputs[1]) != F32:
            continue
        exponent = plan.constants.get(power.inputs[1])
        if exponent is None:
            continue
        exponent = np.asarray(exponent)
        if exponent.size != 1 or not np.isfinite(exponent).all():
            continue
        if float(exponent.reshape(-1)[0]) != 2.0:
            continue
        candidates.append((node.index, FusedDispatch(
            kind="sub_square",
            graph_name="nu_sub_square",
            output_name=power.output,
            trigger_index=node.index,
            fused_nodes=(power.index,),
            params={
                "a": node.inputs[0], "b": node.inputs[1],
                "trigger_node": node.index,
            },
        )))
    return candidates


def _collect_mul_scalar_clip(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """FP32 ``Mul(scalar constant) -> Clip(scalar bounds)``."""
    candidates: List[Tuple[int, FusedDispatch]] = []
    for node in plan.nodes:
        if node.domain != "ai.onnx" or node.op != "Mul":
            continue
        if node.attrs or node.output in requested:
            continue
        if plan.dtypes.get(node.output) != F32:
            continue
        left = _scalar_constant(node.inputs[0], plan)
        right = _scalar_constant(node.inputs[1], plan)
        if left is not None and right is not None:
            continue
        if right is not None:
            a_name, scalar = node.inputs[0], right
        elif left is not None:
            a_name, scalar = node.inputs[1], left
        else:
            continue
        if not a_name or plan.dtypes.get(a_name) != F32:
            continue
        uses = consumers.get(node.output, ())
        if len(uses) != 1:
            continue
        clip = uses[0]
        if (clip.op != "Clip" or not 1 <= len(clip.inputs) <= 3
                or clip.inputs[0] != node.output or clip.domain != "ai.onnx"
                or plan.dtypes.get(clip.output) != F32):
            continue
        bounds = _clip_bounds(clip, plan)
        if bounds is None:
            continue
        clip_lo, clip_hi = bounds
        scalar_value, scalar_shape = scalar
        candidates.append((node.index, FusedDispatch(
            kind="mul_scalar_clip",
            graph_name="nu_mul_scalar_clip",
            output_name=clip.output,
            trigger_index=node.index,
            fused_nodes=(clip.index,),
            params={
                "a": a_name, "b": scalar_value, "scalar_shape": scalar_shape,
                "clip_lo": clip_lo, "clip_hi": clip_hi,
                "trigger_node": node.index,
            },
        )))
    return candidates


def _collect_mul_clip(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """FP32 same-shape ``Mul -> Clip`` with scalar bounds."""
    candidates: List[Tuple[int, FusedDispatch]] = []
    for node in plan.nodes:
        if node.op != "Mul" or node.output in requested:
            continue
        if plan.dtypes.get(node.output) != F32:
            continue
        uses = consumers.get(node.output, ())
        if len(uses) != 1 or uses[0].op != "Clip":
            continue
        clip = uses[0]
        if clip.output in plan.host_int_values or plan.dtypes.get(clip.output) != F32:
            continue
        bounds = _clip_bounds(clip, plan)
        if bounds is None:
            continue
        clip_lo, clip_hi = bounds
        candidates.append((node.index, FusedDispatch(
            kind="mul_clip",
            graph_name="nu_mul_clip",
            output_name=clip.output,
            trigger_index=node.index,
            fused_nodes=(clip.index,),
            params={
                "a": node.inputs[0], "b": node.inputs[1],
                "clip_lo": clip_lo, "clip_hi": clip_hi,
                "trigger_node": node.index,
            },
        )))
    return candidates


def _collect_add_relu(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """FP32 same-shape ``Add -> Relu`` (residual blocks in RAFT/WeightNet).

    Planned ahead of the generic ``binary_unary`` broadcast alternative; the
    broadcast variant stays available for shapes that do not match exactly.
    """
    candidates: List[Tuple[int, FusedDispatch]] = []
    for node in plan.nodes:
        if node.domain != "ai.onnx" or node.op != "Add":
            continue
        if node.attrs or node.output in requested:
            continue
        if plan.dtypes.get(node.output) != F32 or any(
            plan.dtypes.get(name) != F32 for name in node.inputs
        ):
            continue
        uses = consumers.get(node.output, ())
        if len(uses) != 1:
            continue
        relu = uses[0]
        if (relu.op != "Relu" or len(relu.inputs) != 1
                or relu.inputs[0] != node.output or relu.domain != "ai.onnx"
                or len(relu.outputs) != 1
                or plan.dtypes.get(relu.output) != F32):
            continue
        candidates.append((node.index, FusedDispatch(
            kind="add_relu",
            graph_name="nu_add_relu",
            output_name=relu.output,
            trigger_index=node.index,
            fused_nodes=(relu.index,),
            params={
                "a": node.inputs[0], "b": node.inputs[1],
                "trigger_node": node.index,
            },
        )))
    return candidates


def _collect_binary_unary(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> List[Tuple[int, FusedDispatch]]:
    """FP32 ``binary -> unary`` edges where the unary is the sole consumer.

    Kept as the broadcast-capable fallback for the ``Add→Sqrt`` / ``Sub→Clip``
    / ``Mul→Clip`` edges the dedicated chain patterns also plan.
    """
    candidates: List[Tuple[int, FusedDispatch]] = []
    for node in plan.nodes:
        binary_code = BINARY_CODES.get(node.op)
        if binary_code is None or node.output in requested:
            continue
        if plan.dtypes.get(node.output) != F32:
            continue
        uses = consumers.get(node.output, ())
        if len(uses) != 1:
            continue
        unary = uses[0]
        if len(unary.inputs) != 1 or unary.inputs[0] != node.output:
            continue
        if plan.dtypes.get(unary.output) != F32:
            continue
        low = 0.0
        high = 0.0
        if unary.op == "Clip":
            code = CLIP_CODE
            bounds = _clip_bounds(unary, plan)
            if bounds is None:
                continue
            low, high = bounds
        else:
            code = UNARY_CODES.get(unary.op)
            if code is None:
                continue
        candidates.append((node.index, FusedDispatch(
            kind="binary_unary",
            graph_name="nu_binary_unary_broadcast",
            output_name=unary.output,
            trigger_index=node.index,
            fused_nodes=(unary.index,),
            params={
                "a": node.inputs[0], "b": node.inputs[1],
                "binary_code": binary_code, "unary_code": code,
                "lo": low, "hi": high,
                "trigger_node": node.index,
            },
        )))
    return candidates


def _collect_conv_activation(
    plan: Plan, requested: Set[str], consumers: Dict[str, List[GraphNode]]
) -> Tuple[Dict[int, Tuple[int, str, int]], FrozenSet[int]]:
    """Fold a Conv's sole pointwise activation consumer into the ``act`` param.

    Unsupported activations, requested intermediate outputs, multi-consumer
    Conv values, and all other graph shapes retain the ordinary ONNX steps.
    """
    activation_codes = {"Relu": 1, "Sigmoid": 2, "Tanh": 3, "Softplus": 6}
    fusions: Dict[int, Tuple[int, str, int]] = {}
    skipped: Set[int] = set()
    for node in plan.nodes:
        if node.op != "Conv" or node.output in requested:
            continue
        uses = consumers.get(node.output, ())
        if len(uses) != 1:
            continue
        activation = uses[0]
        if len(activation.inputs) != 1 or activation.inputs[0] != node.output:
            continue
        if activation.op == "Gelu":
            approximate = str(activation.attrs.get("approximate", "none")).lower()
            code = 4 if approximate == "tanh" else 5
        else:
            code = activation_codes.get(activation.op, 0)
        if code == 0 or plan.dtypes.get(activation.output) != F32:
            continue
        fusions[node.index] = (activation.index, activation.output, code)
        skipped.add(activation.index)
    return fusions, frozenset(skipped)


#: Pattern collectors in the original run-loop check order. Dispatches for the
#: same trigger accumulate into ordered alternatives; earlier patterns win.
_PATTERN_ORDER = (
    _collect_sub_sub_div,
    _collect_unary_binary,
    _collect_add_sqrt_clip,
    _collect_sub_clip_sqrt,
    _collect_sigmoid_mul_clip,
    _collect_sub_square,
    _collect_mul_scalar_clip,
    _collect_mul_clip,
    _collect_add_relu,
    _collect_binary_unary,
)

#: Pool graph each dynamic dispatch depends on (conv activation is a param).
_PATTERN_GRAPHS = {
    "sub_sub_div": "nu_fused_sub_sub_div",
    "add_sqrt_clip": "nu_add_sqrt_clip_broadcast",
    "sub_clip_sqrt": "nu_sub_clip_sqrt_broadcast",
    "sigmoid_mul_clip": "nu_sigmoid_mul_clip",
    "unary_binary": "nu_fused_unary_binary",
    "binary_unary": "nu_binary_unary_broadcast",
    "sub_square": "nu_sub_square",
    "add_relu": "nu_add_relu",
    "mul_scalar_clip": "nu_mul_scalar_clip",
    "mul_clip": "nu_mul_clip",
}


def build_fusion_plan(
    plan: Plan,
    requested_outputs: Set[str],
    pool_graphs: Set[str],
) -> FusionPlan:
    """Decide every safe fusion for ``plan`` against the staged pool graphs."""
    requested = set(requested_outputs)
    consumers = _consumers(plan)

    grouped: Dict[int, List[FusedDispatch]] = {}
    fused: Set[int] = set()
    for collector in _PATTERN_ORDER:
        for trigger, dispatch in collector(plan, requested, consumers):
            if _PATTERN_GRAPHS[dispatch.kind] not in pool_graphs:
                continue
            grouped.setdefault(trigger, []).append(dispatch)
            fused.update(dispatch.fused_nodes)

    conv_activation, conv_skipped = _collect_conv_activation(plan, requested, consumers)
    return FusionPlan(
        dispatches={trigger: tuple(alternatives) for trigger, alternatives in grouped.items()},
        fused_nodes=frozenset(fused),
        conv_activation=conv_activation,
        conv_activation_skipped=conv_skipped,
    )


# ---------------------------------------------------------------------------
# runtime dispatch
# ---------------------------------------------------------------------------


def run_fused_dispatch(dispatch: FusedDispatch, ctx) -> bool:
    """Execute one planned fusion; ``False`` means "try the next alternative".

    Shape/broadcast facts are re-checked here because the plan carries no
    compile-time extents. A declined dispatch leaves every absorbed node to be
    executed through its ordinary lowering.
    """
    plan = ctx.session.plan
    trigger = plan.nodes[dispatch.params["trigger_node"]]

    if dispatch.kind == "sub_sub_div":
        names = (dispatch.params["a"], dispatch.params["b"],
                 dispatch.params["c"], dispatch.params["d"])
        shapes = tuple(ctx.shape_of(name) for name in names)
        if not shapes or any(shape != shapes[0] for shape in shapes):
            return False
        second_node = plan.nodes[dispatch.fused_nodes[0]]
        last_node = plan.nodes[dispatch.fused_nodes[1]]
        try:
            first_shape = ctx.infer_out(trigger, [shapes[0], shapes[1]])
            second_shape = ctx.infer_out(second_node, [first_shape, shapes[2]])
            final_shape = ctx.infer_out(last_node, [second_shape, shapes[3]])
        except (ValueError, TypeError):
            return False
        if first_shape != second_shape or second_shape != final_shape or final_shape != shapes[0]:
            return False
        output = ctx.alloc(dispatch.output_name, final_shape, F32)
        first_tmp = ctx.alloc(dispatch.params["first_tmp"], final_shape, F32)
        second_tmp = ctx.alloc(dispatch.params["second_tmp"], final_shape, F32)
        ctx.module.run(
            "nu_fused_sub_sub_div",
            a=ctx.device(names[0]), b=ctx.device(names[1]),
            c=ctx.device(names[2]), d=ctx.device(names[3]), y=output,
            first_tmp=first_tmp, second_tmp=second_tmp,
            n=product(final_shape),
        )
        return True

    if dispatch.kind == "unary_binary":
        unary_shape = ctx.shape_of(dispatch.params["x"])
        other_shape = ctx.shape_of(dispatch.params["other"])
        if dispatch.params["unary_is_left"]:
            left_shape, right_shape = unary_shape, other_shape
        else:
            left_shape, right_shape = other_shape, unary_shape
        if max(len(left_shape), len(right_shape)) > 8:
            return False
        try:
            binary_node = plan.nodes[dispatch.fused_nodes[0]]
            output_shape = ctx.infer_out(binary_node, [left_shape, right_shape])
        except (ValueError, TypeError):
            return False
        unary_strides = broadcast_strides(unary_shape, output_shape)
        other_strides = broadcast_strides(other_shape, output_shape)
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        kwargs = {
            f"o{i}": value for i, value in enumerate(pad_to(output_shape, 8))
        }
        kwargs.update({
            f"x{i}": value for i, value in enumerate(pad_to(unary_strides, 8, 0))
        })
        kwargs.update({
            f"b{i}": value for i, value in enumerate(pad_to(other_strides, 8, 0))
        })
        ctx.module.run(
            "nu_fused_unary_binary",
            x=ctx.device(dispatch.params["x"]),
            other=ctx.device(dispatch.params["other"]),
            y=output, n=product(output_shape),
            unary_code=dispatch.params["unary_code"],
            binary_code=dispatch.params["binary_code"],
            unary_is_left=dispatch.params["unary_is_left"],
            lo=dispatch.params["lo"], hi=dispatch.params["hi"],
            **kwargs,
        )
        return True

    if dispatch.kind in ("add_sqrt_clip", "sub_clip_sqrt"):
        left_shape = ctx.shape_of(dispatch.params["a"])
        right_shape = ctx.shape_of(dispatch.params["b"])
        if max(len(left_shape), len(right_shape)) > 8:
            return False
        if (plan.dtypes.get(dispatch.params["a"]) != F32
                or plan.dtypes.get(dispatch.params["b"]) != F32):
            return False
        output_shape = ctx.infer_out(trigger, [left_shape, right_shape])
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        kwargs = {
            f"o{i}": value for i, value in enumerate(pad_to(output_shape, 8))
        }
        kwargs.update({
            f"a{i}": value for i, value in enumerate(
                pad_to(broadcast_strides(left_shape, output_shape), 8, 0)
            )
        })
        kwargs.update({
            f"b{i}": value for i, value in enumerate(
                pad_to(broadcast_strides(right_shape, output_shape), 8, 0)
            )
        })
        ctx.module.run(
            dispatch.graph_name,
            a=ctx.device(dispatch.params["a"]), b=ctx.device(dispatch.params["b"]),
            y=output, n=product(output_shape),
            clip_lo=dispatch.params["clip_lo"], clip_hi=dispatch.params["clip_hi"],
            **kwargs,
        )
        return True

    if dispatch.kind == "binary_unary":
        left_shape = ctx.shape_of(dispatch.params["a"])
        right_shape = ctx.shape_of(dispatch.params["b"])
        if max(len(left_shape), len(right_shape)) > 8:
            return False
        if (plan.dtypes.get(dispatch.params["a"]) != F32
                or plan.dtypes.get(dispatch.params["b"]) != F32):
            return False
        output_shape = ctx.infer_out(trigger, [left_shape, right_shape])
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        kwargs = {
            f"o{i}": value for i, value in enumerate(pad_to(output_shape, 8))
        }
        kwargs.update({
            f"a{i}": value for i, value in enumerate(
                pad_to(broadcast_strides(left_shape, output_shape), 8, 0)
            )
        })
        kwargs.update({
            f"b{i}": value for i, value in enumerate(
                pad_to(broadcast_strides(right_shape, output_shape), 8, 0)
            )
        })
        ctx.module.run(
            "nu_binary_unary_broadcast",
            a=ctx.device(dispatch.params["a"]), b=ctx.device(dispatch.params["b"]),
            y=output, n=product(output_shape),
            binary_code=dispatch.params["binary_code"],
            unary_code=dispatch.params["unary_code"],
            lo=dispatch.params["lo"], hi=dispatch.params["hi"],
            **kwargs,
        )
        return True

    if dispatch.kind == "sub_square":
        left_shape = ctx.shape_of(dispatch.params["a"])
        right_shape = ctx.shape_of(dispatch.params["b"])
        output_shape = ctx.infer_out(trigger, [left_shape, right_shape])
        if left_shape != right_shape or right_shape != output_shape:
            return False
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        ctx.module.run(
            "nu_sub_square",
            a=ctx.device(dispatch.params["a"]), b=ctx.device(dispatch.params["b"]),
            y=output, n=product(output_shape),
        )
        return True

    if dispatch.kind == "mul_clip":
        left_shape = ctx.shape_of(dispatch.params["a"])
        right_shape = ctx.shape_of(dispatch.params["b"])
        output_shape = ctx.infer_out(trigger, [left_shape, right_shape])
        if left_shape != right_shape or right_shape != output_shape:
            return False
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        ctx.module.run(
            "nu_mul_clip",
            a=ctx.device(dispatch.params["a"]), b=ctx.device(dispatch.params["b"]),
            y=output, n=product(output_shape),
            lo=dispatch.params["clip_lo"], hi=dispatch.params["clip_hi"],
        )
        return True

    if dispatch.kind == "add_relu":
        left_shape = ctx.shape_of(dispatch.params["a"])
        right_shape = ctx.shape_of(dispatch.params["b"])
        output_shape = ctx.infer_out(trigger, [left_shape, right_shape])
        if left_shape != right_shape or right_shape != output_shape:
            return False
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        ctx.module.run(
            "nu_add_relu",
            a=ctx.device(dispatch.params["a"]), b=ctx.device(dispatch.params["b"]),
            y=output, n=product(output_shape),
        )
        return True

    if dispatch.kind == "mul_scalar_clip":
        a_shape = ctx.shape_of(dispatch.params["a"])
        output_shape = ctx.infer_out(
            trigger, [a_shape, tuple(dispatch.params["scalar_shape"])]
        )
        if a_shape != output_shape:
            return False
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        ctx.module.run(
            "nu_mul_scalar_clip",
            a=ctx.device(dispatch.params["a"]), y=output,
            n=product(output_shape),
            b=dispatch.params["b"],
            lo=dispatch.params["clip_lo"], hi=dispatch.params["clip_hi"],
        )
        return True

    if dispatch.kind == "sigmoid_mul_clip":
        a_shape = ctx.shape_of(dispatch.params["a"])
        b_shape = ctx.shape_of(dispatch.params["b"])
        mul_node = plan.nodes[dispatch.fused_nodes[0]]
        output_shape = ctx.infer_out(mul_node, [a_shape, b_shape])
        if a_shape != b_shape or b_shape != output_shape:
            return False
        output = ctx.alloc(dispatch.output_name, output_shape, F32)
        ctx.module.run(
            "nu_sigmoid_mul_clip",
            a=ctx.device(dispatch.params["a"]), b=ctx.device(dispatch.params["b"]),
            y=output, n=product(output_shape),
            lo=dispatch.params["clip_lo"], hi=dispatch.params["clip_hi"],
        )
        return True

    raise AssertionError(f"unknown fusion kind {dispatch.kind!r}")


__all__ = [
    "FusedDispatch",
    "FusionPlan",
    "build_fusion_plan",
    "run_fused_dispatch",
    "UNARY_CODES",
    "BINARY_CODES",
    "UNARY_BINARY_CODES",
    "UNARY_BINARY_OP_CODES",
    "CLIP_CODE",
    "SQRT_CODE",
]
