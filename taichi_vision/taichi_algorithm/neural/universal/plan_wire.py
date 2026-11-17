"""Serialise a validated :class:`Plan` into the ``NPLN`` wire format.

Rust owns the executor; this module is the only writer of the plan bytes. One
implementation on each side of the boundary is deliberate: a plan encoded two ways
would drift, and the drift would show up as a wrong number rather than an error.

Layout (version 2)::

    magic "NPLN" | version u32 | slot count u32 | node count u32
    slots:  id u32 | role u8 | dtype | rank u32 | dims [u32] | name
    nodes:  op | in_count u32 | in [u32] | out_count u32 | out [u32]
            attr_count u32 | [key | tag u8 | value]

Attribute tags: 0 int, 1 float, 2 ints, 3 floats, 4 string. The tag is written
explicitly so an axis cannot arrive as a float.
"""

from __future__ import annotations

import struct
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from . import registry, shapeinfer
from .dtypes import F32, I32, I64
from .plan import GraphNode, Plan

MAGIC = b"NPLN"
VERSION = 2

# Slot roles, matching ``SlotRole`` in ``neural/plan.rs``.
ROLE_INPUT = 0
ROLE_CONST = 1
ROLE_TEMP = 2
ROLE_OUTPUT = 3

TAG_INT = 0
TAG_FLOAT = 1
TAG_INTS = 2
TAG_FLOATS = 3
TAG_STR = 4


class PlanEncodeError(ValueError):
    """An attribute or shape cannot be represented in the wire format."""


# --------------------------------------------------------------------- encoding


def _u32(value: int) -> bytes:
    if not 0 <= value <= 0xFFFFFFFF:
        raise PlanEncodeError(f"value {value} does not fit in u32")
    return struct.pack("<I", value)


def _string(text: str) -> bytes:
    raw = text.encode("utf-8")
    return _u32(len(raw)) + raw


def _attribute(value: Any, name: str) -> bytes:
    """Encode one attribute, refusing anything the format cannot carry exactly.

    Refusing rather than coercing is the point: an attribute silently dropped here
    would make the Rust executor run a different operator than the graph declared,
    and the result would be a plausible wrong number.
    """
    if isinstance(value, (np.integer, int)) and not isinstance(value, bool):
        return bytes([TAG_INT]) + struct.pack("<q", int(value))
    if isinstance(value, (np.floating, float)):
        return bytes([TAG_FLOAT]) + struct.pack("<d", float(value))
    if isinstance(value, str):
        return bytes([TAG_STR]) + _string(value)
    if isinstance(value, (bytes, bytearray)):
        return bytes([TAG_STR]) + _string(bytes(value).decode("utf-8"))

    if isinstance(value, np.ndarray):
        if value.ndim == 0:
            return _attribute(value.item(), name)
        if value.dtype.kind in "iu":
            return bytes([TAG_INTS]) + _sequence([int(v) for v in value.ravel()])
        if value.dtype.kind == "f":
            return bytes([TAG_FLOATS]) + _sequence([float(v) for v in value.ravel()])
        raise PlanEncodeError(
            f"attribute {name!r} is an array of dtype {value.dtype}, "
            f"which has no wire representation"
        )

    if isinstance(value, (list, tuple)):
        items = list(value)
        if not items:
            # An empty list carries no element type. `ints` matches how ONNX spells
            # an empty `axes`, and an empty float list is not a thing operators take.
            return bytes([TAG_INTS]) + _u32(0)
        if all(isinstance(v, (np.integer, int)) and not isinstance(v, bool) for v in items):
            return bytes([TAG_INTS]) + _sequence([int(v) for v in items])
        if all(isinstance(v, (np.floating, float)) for v in items):
            return bytes([TAG_FLOATS]) + _sequence([float(v) for v in items])
        raise PlanEncodeError(f"attribute {name!r} mixes element types: {items!r}")

    raise PlanEncodeError(
        f"attribute {name!r} has type {type(value).__name__}, "
        f"which has no wire representation"
    )


def _sequence(values: Sequence[Any]) -> bytes:
    out = [_u32(len(values))]
    for value in values:
        out.append(struct.pack("<q", value) if isinstance(value, int) else struct.pack("<d", value))
    return b"".join(out)


# ----------------------------------------------------------------------- shapes


def _slot_names(plan: Plan) -> List[str]:
    """Every tensor that needs a slot, in a stable order.

    Constants come first so their slot ids are low and stable, then inputs, then
    everything a node produces. Stability matters because the plan is cached by
    signature: ids that shifted between two builds of the same graph would defeat
    the cache.
    """
    ordered: List[str] = []
    seen = set()

    def add(name: str) -> None:
        if name and name not in seen:
            seen.add(name)
            ordered.append(name)

    for name in plan.constants:
        add(name)
    for name in plan.input_names:
        add(name)
    for node in plan.nodes:
        for name in node.outputs:
            add(name)
    return ordered


def _concrete_shapes(
    plan: Plan, input_shapes: Dict[str, Sequence[int]]
) -> Dict[str, Tuple[int, ...]]:
    """Run shape inference once for one concrete input signature.

    Deliberately one pass per signature: the plan carries final shapes so the Rust
    side never re-derives a shape, which is where an off-by-one in stride arithmetic
    would hide.

    Multi-output operators need care: `shapeinfer.infer` returns the shape of one
    part for `Split`, not a shape per output. Applying that single shape to every
    output would be wrong when the parts differ, and applying it to only the first
    leaves the rest unknown — which surfaced as "Sub: first input shape is unknown"
    on a real model. Both cases are handled explicitly below.
    """
    shapes: Dict[str, Tuple[int, ...]] = {}
    for name, array in plan.constants.items():
        shapes[name] = tuple(int(v) for v in array.shape)
    for name in plan.input_names:
        if name not in input_shapes:
            raise PlanEncodeError(f"input {name!r} has no shape for this signature")
        given = tuple(int(v) for v in input_shapes[name])
        rank = plan.input_ranks[name]
        if len(given) != rank:
            raise PlanEncodeError(
                f"input {name!r} was declared with rank {rank} but given shape {given}"
            )
        shapes[name] = given

    for node in plan.nodes:
        if node.op == "Constant":
            # The value is already in `plan.constants`, and the loop above seeded
            # it; running shape inference on it would look up the attribute again.
            continue
        in_shapes = [shapes.get(name) if name else None for name in node.inputs]
        int_args: Dict[int, np.ndarray] = {}
        for position, name in enumerate(node.inputs):
            if name and name in plan.constants:
                array = plan.constants[name]
                if array.dtype.kind in "iu":
                    int_args[position] = array
        dtypes = [plan.dtypes.get(name, F32) if name else F32 for name in node.inputs]
        inferred = shapeinfer.infer(node.op, node.attrs, in_shapes, int_args, dtypes)

        if node.op == "Split":
            shapes.update(_split_shapes(node, in_shapes[0], int_args, inferred))
            continue
        shapes[node.output] = tuple(int(v) for v in inferred)
    return shapes


def _split_shapes(
    node: GraphNode,
    source: Sequence[int],
    int_args: Dict[int, np.ndarray],
    inferred: Sequence[int],
) -> Dict[str, Tuple[int, ...]]:
    """One shape per `Split` output, from the split sizes or an even division.

    The part sizes come from the attribute or the constant input; falling back to
    an even division only when neither says otherwise. A remainder is refused: ONNX
    requires the axis to divide evenly in that case, and approximating it would
    size a buffer wrongly.
    """
    rank = len(source)
    axis = int(node.attrs.get("axis", 0))
    if axis < 0:
        axis += rank

    sizes = node.attrs.get("split")
    if sizes is None and 1 in int_args:
        sizes = [int(v) for v in np.asarray(int_args[1]).ravel()]
    if sizes is None:
        count = int(node.attrs.get("num_outputs", len(node.outputs)))
        if source[axis] % count != 0:
            raise PlanEncodeError(
                f"Split: axis {axis} has extent {source[axis]} which does not divide "
                f"evenly into {count} parts"
            )
        sizes = [source[axis] // count] * count

    sizes = [int(v) for v in sizes]
    if len(sizes) != len(node.outputs):
        raise PlanEncodeError(
            f"Split: {len(sizes)} part sizes for {len(node.outputs)} outputs"
        )
    if sum(sizes) != source[axis]:
        raise PlanEncodeError(
            f"Split: part sizes {sizes} sum to {sum(sizes)} but axis {axis} has "
            f"extent {source[axis]}"
        )
    if tuple(inferred) != tuple(sizes):
        # `shapeinfer` already ran; a disagreement means one of the two is wrong and
        # guessing which would be exactly the kind of silent divergence to avoid.
        raise PlanEncodeError(
            f"Split: shape inference returned {tuple(inferred)} but the part sizes "
            f"are {tuple(sizes)}"
        )

    out: Dict[str, Tuple[int, ...]] = {}
    for name, extent in zip(node.outputs, sizes):
        shape = list(source)
        shape[axis] = extent
        out[name] = tuple(int(v) for v in shape)
    return out


# ---------------------------------------------------------------------- encoder


def encode_plan(plan: Plan, input_shapes: Dict[str, Sequence[int]]) -> bytes:
    """Encode ``plan`` for one concrete input signature."""
    names = _slot_names(plan)
    index = {name: position for position, name in enumerate(names)}
    shapes = _concrete_shapes(plan, input_shapes)

    inputs = set(plan.input_names)
    outputs = set(plan.output_names)

    chunks: List[bytes] = [
        MAGIC,
        _u32(VERSION),
        _u32(len(names)),
        _u32(len(plan.nodes)),
    ]

    for position, name in enumerate(names):
        if name in inputs:
            role = ROLE_INPUT
        elif name in plan.constants:
            role = ROLE_CONST
        elif name in outputs:
            role = ROLE_OUTPUT
        else:
            role = ROLE_TEMP
        shape = shapes.get(name)
        if shape is None:
            raise PlanEncodeError(f"no shape was derived for tensor {name!r}")
        dtype = plan.dtypes.get(name)
        if dtype is None:
            raise PlanEncodeError(f"no dtype was declared for tensor {name!r}")
        chunks.extend(
            [
                _u32(position),
                bytes([role]),
                _string(dtype),
                _u32(len(shape)),
                b"".join(_u32(dim) for dim in shape),
                _string(name),
            ]
        )

    for node in plan.nodes:
        # ONNX spells an omitted optional input as an empty name. Those are always
        # trailing (`Clip` is `[x, min?, max?]`), so dropping them from the end is
        # exactly right and the lowering reads the attribute form instead. An empty
        # name *before* a real one is refused: the wire has no "absent" marker, and
        # silently shifting the remaining inputs would bind the wrong tensor.
        names = list(node.inputs)
        while names and not names[-1]:
            names.pop()
        if any(not name for name in names):
            first_empty = names.index("")
            raise PlanEncodeError(
                f"{node.op} (node {node.index}) leaves input {first_empty} empty "
                f"before a later input; optional inputs are only supported at the end"
            )
        chunks.extend(
            [
                _string(node.op),
                _u32(len(names)),
                b"".join(_u32(index[name]) for name in names),
                _u32(len(node.outputs)),
                b"".join(_u32(index[name]) for name in node.outputs),
                _u32(len(node.attrs)),
            ]
        )
        for key in sorted(node.attrs):
            chunks.append(_string(key))
            chunks.append(_attribute(node.attrs[key], key))

    return b"".join(chunks)


def slot_names(plan: Plan) -> List[str]:
    """Tensor names in wire order, so a caller can pair them with an executor's
    outputs without reimplementing the ordering."""
    return _slot_names(plan)


def output_names(plan: Plan) -> List[str]:
    """Declared graph outputs, in wire order."""
    declared = set(plan.output_names)
    return [name for name in _slot_names(plan) if name in declared]


def constant_values(plan: Plan) -> Dict[str, np.ndarray]:
    """The constant tensors a session must upload, keyed by tensor name.

    Kept next to the encoder because the two must agree on which names are
    constants: an encoder that called a tensor constant while the uploader skipped
    it would leave a slot holding uninitialised memory.

    A scalar constant keeps rank 0. ``np.ascontiguousarray`` would promote it to
    rank 1, and a rank-1 ``(1,)`` operand broadcasts differently from a scalar in
    the shape the executor was given.
    """
    out: Dict[str, np.ndarray] = {}
    for name, array in plan.constants.items():
        value = np.asarray(array)
        out[name] = value if value.ndim == 0 else np.ascontiguousarray(value)
    return out


__all__ = [
    "MAGIC",
    "VERSION",
    "PlanEncodeError",
    "encode_plan",
    "constant_values",
]
