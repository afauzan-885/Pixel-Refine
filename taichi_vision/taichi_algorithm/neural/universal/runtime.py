"""Native ONNX execution on top of the compiled universal kernel pool.

``UniversalSession`` loads one ``neural_{backend}.tcm`` artifact (a pool of
pre-compiled kernels, not a per-model graph) and executes an arbitrary admitted
ONNX model by dispatching pool kernels step by step.

Design rules that keep the runtime honest:

* **Fail-closed.** Every operator must have a lowering in :data:`LOWER`.
  An unknown operator or a missing lowering raises
  :class:`UnsupportedStepError`/``UnsupportedONNXOperatorError``; nothing is
  ever skipped silently.
* **Shapes are runtime state.** Nothing about tensor extents is baked at
  construction. The same session can run several input sizes.
* **Shape metadata lives on the host.** ``Shape``/``Range``/``Reshape``
  targets and the integer chains built on them are evaluated with NumPy;
  only data-plane tensors touch the device.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

from . import native_i64, shapeinfer
from .errors import UnsupportedONNXOperatorError, UnsupportedStepError
from .fusions import (
    BINARY_CODES as _BINARY_CODES,
    UNARY_CODES as _UNARY_CODES,
    build_fusion_plan,
    run_fused_dispatch,
)
from .plan import GraphNode, Plan
from .dtypes import F32, I32, I64, NUMPY_DTYPE, broadcast_strides, normalize_axis, pad_to, product

def _resolve_output(source, dst=None):
    """True when the result should stay resident (device-owned)."""
    from taichi.aot_engine import is_resident

    if dst is not None and is_resident(dst):
        return True
    if isinstance(source, dict):
        return any(is_resident(value) for value in source.values())
    if isinstance(source, (list, tuple)):
        return any(is_resident(value) for value in source)
    return is_resident(source)



Shape = Tuple[int, ...]
_MAX_RANGE_ELEMENTS = np.iinfo(np.int32).max
DEFAULT_POOL_DIR = Path("pixel_refine_desktop/ui/data/aot_assets/neural")
#: Archived spelling of the pool directory constant.
DEFAULT_AOT_NEURAL_DIR = DEFAULT_POOL_DIR
BACKEND_SUBDIRS = {"cuda": "nvidia", "vulkan": "vulkan", "opengl": "opengl", "cpu": "cpu"}


class _Ctx:
    """Mutable per-run state handed to every lowering."""

    def __init__(self, session: "UniversalSession"):
        self.session = session
        self.engine = session.engine
        self.module = session.module
        self.buffers: Dict[str, Any] = {}
        self.shapes: Dict[str, Shape] = {}
        self.host: Dict[str, np.ndarray] = {}
        self.dummy = session.dummy
        self.conv_activation_fusions: Dict[int, Tuple[int, str, int]] = {}
        self.fused_nodes: set = set()

    def value(self, name: str) -> np.ndarray:
        if name in self.host:
            return self.host[name]
        if name in self.session.plan.constants:
            return self.session.plan.constants[name]
        raise UnsupportedStepError(f"value {name} is not available on the host")

    def has_value(self, name: str) -> bool:
        return name in self.host or name in self.session.plan.constants

    def const_arg(self, node: GraphNode, position: int) -> Optional[np.ndarray]:
        if position >= len(node.inputs):
            return None
        name = node.inputs[position]
        if not name:
            return None
        if name in self.host:
            return self.host[name]
        return self.session.plan.constants.get(name)

    def const_args(self, node: GraphNode) -> Dict[int, np.ndarray]:
        out: Dict[int, np.ndarray] = {}
        for position, name in enumerate(node.inputs):
            if not name:
                continue
            if name in self.host:
                out[position] = self.host[name]
            elif name in self.session.plan.constants:
                out[position] = self.session.plan.constants[name]
        return out

    def device(self, name: str):
        buf = self.buffers.get(name)
        if buf is None:
            value = self.value(name)
            buf = self.session.upload(name, np.ascontiguousarray(value).reshape(-1))
            self.buffers[name] = buf
            self.shapes[name] = tuple(int(d) for d in np.asarray(value).shape)
        return buf

    def shape_of(self, name: str) -> Shape:
        shape = self.shapes.get(name)
        if shape is None:
            shape = tuple(int(d) for d in np.asarray(self.value(name)).shape)
            self.shapes[name] = shape
        return shape

    def device_i32(self, name: str):
        """Device buffer holding ``name`` as int32.

        ONNX index tensors are int64. The pool kernels index with int32, so a
        value that is still on the host is narrowed here; a device-resident
        int64 index tensor is rejected rather than silently truncated.
        """
        key = f"{name}__i32"
        buf = self.buffers.get(key)
        if buf is not None:
            return buf
        current = self.buffers.get(name)
        if current is not None:
            if getattr(current, "dtype", None) == np.int32:
                return current
            raise UnsupportedStepError(
                f"{name} is a device-resident {self.session.plan.dtypes[name]} index tensor; "
                "index tensors must be resolvable on the host in this profile"
            )
        value = np.asarray(self.value(name)).astype(np.int64).ravel()
        if value.size and (value.min() < -(2 ** 31) or value.max() > 2 ** 31 - 1):
            raise UnsupportedStepError(f"index tensor {name} exceeds the int32 range")
        buf = self.session.upload(key, value.astype(np.int32))
        self.buffers[key] = buf
        return buf

    def infer_out(self, node: GraphNode, in_shapes: Sequence[Optional[Shape]]) -> Shape:
        return shapeinfer.infer(
            node.op,
            node.attrs,
            in_shapes,
            self.const_args(node),
            [self.session.plan.dtypes.get(n, F32) for n in node.inputs],
        )

    def alloc(self, name: str, shape: Shape, dtype: str = F32, *, borrowed: bool = False):
        return self.session.alloc_slot(name, shape, dtype, self, borrowed=borrowed)

    def alloc_temp(self, prefix: str, shape: Shape, dtype: str):
        """Allocate a scratch value under a name disjoint from every ONNX value."""
        plan = self.session.plan
        occupied = (set(plan.input_names) | set(plan.constants) | set(plan.producer)
                    | set(plan.output_names) | set(self.buffers) | set(self.shapes))
        name = prefix
        suffix = 0
        while name in occupied:
            suffix += 1
            name = f"{prefix}_{suffix}"
        return self.alloc(name, shape, dtype)

    def candidate_status(self):
        """Allocate and clear the CPU candidate's scalar error-status word."""
        if not self.session.int64_candidate:
            raise UnsupportedStepError("dynamic INT64 requires the isolated CPU candidate pool")
        status = self.alloc("__nu_i64_candidate_status", (1,), I32)
        self.module.run("nu_fill_i32", y=status, n=1, value=0)
        return status

    def check_candidate_status(self, status, operation: str):
        self.engine.sync()
        code = int(np.asarray(status.to_numpy()).reshape(-1)[0])
        if code != 0:
            if operation == "Div":
                reason = "division by zero" if code & 1 else "signed INT64 division overflow"
            elif operation in ("Gather", "GatherElements"):
                reason = "out-of-range index"
            else:
                reason = "zero divisor"
            raise UnsupportedStepError(
                f"INT64 candidate {operation} failed closed: {reason} (status={code})"
            )


# --------------------------------------------------------------------------
# host (NumPy) evaluation of shape-metadata chains
# --------------------------------------------------------------------------


def _host_contiguous(value: Any) -> np.ndarray:
    array = np.asarray(value)
    return np.ascontiguousarray(array) if array.ndim > 0 else array


def _integer_range_spec(node: GraphNode, ctx: _Ctx) -> Tuple[int, int, int, int, str]:
    """Read ONNX integer Range operands without float conversion or precision loss."""
    dtype = ctx.session.plan.dtypes[node.output]
    if dtype not in (I32, I64):
        raise UnsupportedStepError(f"Range integer helper cannot handle output dtype {dtype}")
    values: List[int] = []
    for position in range(3):
        name = node.inputs[position]
        if ctx.session.plan.dtypes.get(name) != dtype:
            raise UnsupportedStepError("Range inputs must have the same admitted integer dtype")
        value = ctx.const_arg(node, position)
        if value is None:
            raise UnsupportedStepError(f"Range input {position} is unavailable on the host")
        array = np.asarray(value)
        if array.size != 1 or array.dtype.kind not in "iu":
            raise UnsupportedStepError(f"Range input {position} must be an integer scalar")
        values.append(int(array.reshape(-1)[0]))
    start, limit, delta = values
    if delta == 0:
        raise UnsupportedStepError("Range with zero step")
    if delta > 0:
        count = 0 if start >= limit else (limit - start - 1) // delta + 1
    else:
        step = -delta
        count = 0 if start <= limit else (start - limit - 1) // step + 1
    if count > _MAX_RANGE_ELEMENTS:
        raise UnsupportedStepError(
            f"Range output has {count} elements; this runtime's kernel ABI supports at most "
            f"{_MAX_RANGE_ELEMENTS}"
        )
    return start, limit, delta, count, dtype


def _host_eval(node: GraphNode, ctx: _Ctx) -> np.ndarray:
    op = node.op
    attrs = node.attrs

    def arg(position: int) -> np.ndarray:
        value = ctx.const_arg(node, position)
        if value is None:
            raise UnsupportedStepError(f"{op}: host input {position} missing")
        return np.asarray(value)

    if op == "Identity":
        return arg(0)
    if op == "Shape":
        source = ctx.shape_of(node.inputs[0])
        rank = len(source)
        start = int(attrs.get("start", 0))
        end = int(attrs.get("end", rank))
        start = normalize_axis(start, rank)
        end = rank if end < 0 else end
        return np.asarray(source[start:end], dtype=np.int64)
    if op == "Range":
        dtype = ctx.session.plan.dtypes[node.output]
        if dtype in (I32, I64):
            start, _limit, delta, count, dtype = _integer_range_spec(node, ctx)
            numpy_dtype = np.int32 if dtype == I32 else np.int64
            return np.fromiter(
                (start + delta * index for index in range(count)),
                dtype=numpy_dtype, count=count,
            )
        raise UnsupportedStepError(f"Range host lowering does not admit dtype {dtype}")
    if op == "ConstantOfShape":
        shape = tuple(int(v) for v in arg(0).ravel())
        value_attr = attrs.get("value")
        fill: Any = 0
        dtype = np.int64
        if value_attr is not None:
            array = np.asarray(value_attr)
            fill = array.ravel()[0] if array.size else 0
            if array.dtype.kind in "iufb":
                dtype = array.dtype
        return np.full(shape, fill, dtype=dtype)
    if op == "Gather":
        data = arg(0)
        indices = arg(1).astype(np.int64)
        axis = normalize_axis(int(attrs.get("axis", 0)), data.ndim)
        return np.take(data, indices, axis=axis)
    if op == "Concat":
        arrays = [arg(i) for i in range(len(node.inputs))]
        axis = normalize_axis(int(attrs["axis"]), arrays[0].ndim)
        return np.concatenate(arrays, axis=axis)
    if op == "Split":
        data = arg(0)
        axis = normalize_axis(int(attrs.get("axis", 0)), data.ndim)
        split = attrs.get("split")
        if split is None and ctx.const_arg(node, 1) is not None:
            split = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
        if split is None:
            count = int(attrs.get("num_outputs", 2))
            split = [data.shape[axis] // count] * count
        sizes = [int(v) for v in split]
        parts = np.split(data, np.cumsum(sizes)[:-1], axis=axis)
        ctx.host[node.outputs[0]] = _host_contiguous(parts[0])
        for extra, part in zip(node.outputs[1:], parts[1:]):
            ctx.host[extra] = _host_contiguous(part)
        return _host_contiguous(parts[0])
    if op == "Slice":
        data = arg(0)
        starts = [int(v) for v in arg(1).ravel()]
        ends = [int(v) for v in arg(2).ravel()]
        axes = (
            [int(v) for v in arg(3).ravel()]
            if ctx.const_arg(node, 3) is not None
            else list(range(len(starts)))
        )
        steps = (
            [int(v) for v in arg(4).ravel()]
            if ctx.const_arg(node, 4) is not None
            else [1] * len(starts)
        )
        out = data
        for start, end, axis, step in zip(starts, ends, axes, steps):
            axis = normalize_axis(axis, data.ndim)
            indexer = [slice(None)] * out.ndim
            indexer[axis] = slice(start, end, step)
            out = out[tuple(indexer)]
        return _host_contiguous(out)
    if op in ("Add", "Sub", "Mul", "Div", "Mod", "Pow", "Equal", "Less", "Greater",
              "And", "Or", "Xor", "Max", "Min", "Sum"):
        arrays = [arg(i) for i in range(len(node.inputs))]
        funcs = {
            "Add": np.add, "Sub": np.subtract, "Mul": np.multiply, "Div": np.divide,
            "Mod": np.mod, "Pow": np.power, "Equal": np.equal, "Less": np.less,
            "Greater": np.greater, "And": np.logical_and, "Or": np.logical_or,
            "Xor": np.logical_xor, "Sum": np.add,
        }
        if op in ("Max", "Min"):
            reduced = np.maximum.reduce(arrays) if op == "Max" else np.minimum.reduce(arrays)
            return _host_contiguous(reduced)
        result = arrays[0]
        for other in arrays[1:]:
            result = funcs[op](result, other)
        return _host_contiguous(result)
    if op in ("Neg", "Abs", "Not"):
        data = arg(0)
        if op == "Neg":
            return _host_contiguous(-data)
        if op == "Abs":
            return _host_contiguous(np.abs(data))
        return np.logical_not(data).astype(np.int32)
    if op == "Clip":
        data = arg(0)
        low = attrs.get("min")
        high = attrs.get("max")
        if ctx.const_arg(node, 1) is not None:
            low = float(np.asarray(ctx.const_arg(node, 1)).ravel()[0])
        if ctx.const_arg(node, 2) is not None:
            high = float(np.asarray(ctx.const_arg(node, 2)).ravel()[0])
        return _host_contiguous(
            np.clip(data, low if low is not None else -np.inf,
                    high if high is not None else np.inf)
        )
    if op == "Cast":
        from .dtypes import ONNX_CAST_TO

        target = ONNX_CAST_TO[int(attrs["to"])]
        return _host_contiguous(arg(0).astype(NUMPY_DTYPE[target]))
    if op == "Unsqueeze":
        data = arg(0)
        axes = attrs.get("axes")
        if axes is None:
            axes = [int(v) for v in arg(1).ravel()]
        return _host_contiguous(np.expand_dims(data, axis=tuple(int(a) for a in axes)))
    if op == "Squeeze":
        data = arg(0)
        axes = attrs.get("axes")
        if axes is None and ctx.const_arg(node, 1) is not None:
            axes = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
        if axes is None:
            return _host_contiguous(np.squeeze(data))
        return _host_contiguous(np.squeeze(data, axis=tuple(int(a) for a in axes)))
    if op == "Reshape":
        data = arg(0)
        target = [int(v) for v in arg(1).ravel()]
        allowzero = int(attrs.get("allowzero", 0))
        resolved: List[int] = []
        wildcard = -1
        for index, value in enumerate(target):
            if value == 0 and not allowzero:
                resolved.append(data.shape[index] if index < data.ndim else 1)
            elif value == -1:
                wildcard = index
                resolved.append(1)
            else:
                resolved.append(value)
        if wildcard >= 0:
            known = int(np.prod(resolved, dtype=np.int64))
            resolved[wildcard] = int(data.size) // known if known else 0
        return _host_contiguous(np.reshape(data, resolved))
    if op == "Flatten":
        data = arg(0)
        axis = normalize_axis(int(attrs.get("axis", 1)), data.ndim)
        head = int(np.prod(data.shape[:axis], dtype=np.int64)) if axis else 1
        tail = int(np.prod(data.shape[axis:], dtype=np.int64)) if axis < data.ndim else 1
        return _host_contiguous(np.reshape(data, (head or 1, tail or 1)))
    if op == "Where":
        return _host_contiguous(np.where(arg(0).astype(bool), arg(1), arg(2)))
    if op == "Tile":
        return _host_contiguous(np.tile(arg(0), [int(v) for v in arg(1).ravel()]))
    if op == "Expand":
        return _host_contiguous(
            np.broadcast_to(arg(0), tuple(int(v) for v in arg(1).ravel())).copy()
        )
    if op in ("ReduceSum", "ReduceProd", "ReduceMax", "ReduceMin", "ReduceMean"):
        data = arg(0)
        axes = attrs.get("axes")
        if axes is None and ctx.const_arg(node, 1) is not None:
            axes = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
        keep = bool(int(attrs.get("keepdims", 1)))
        func = {"ReduceSum": np.sum, "ReduceProd": np.prod, "ReduceMax": np.max,
                "ReduceMin": np.min, "ReduceMean": np.mean}[op]
        if axes is None or len(axes) == 0:
            result = func(data)
            if keep:
                return _host_contiguous(np.full(data.shape, result))
            return _host_contiguous(np.asarray(result))
        axis = tuple(normalize_axis(int(a), data.ndim) for a in axes)
        return _host_contiguous(func(data, axis=axis, keepdims=keep))
    raise UnsupportedStepError(f"no host lowering for {op}")


# --------------------------------------------------------------------------
# device lowerings
# --------------------------------------------------------------------------

_REDUCE_KERNELS = {
    "ReduceMean": "nu_reduce_mean", "ReduceSum": "nu_reduce_sum",
    "ReduceMax": "nu_reduce_max", "ReduceMin": "nu_reduce_min",
    "ReduceL2": "nu_reduce_l2",
}


def _lower_unary(node: GraphNode, ctx: _Ctx) -> None:
    op = node.op
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    n = product(so)
    if op == "Clip":
        low = float(node.attrs.get("min", -3.4028234663852886e38))
        high = float(node.attrs.get("max", 3.4028234663852886e38))
        if ctx.const_arg(node, 1) is not None:
            low = float(np.asarray(ctx.const_arg(node, 1)).ravel()[0])
        if ctx.const_arg(node, 2) is not None:
            high = float(np.asarray(ctx.const_arg(node, 2)).ravel()[0])
        ctx.module.run("nu_clip_f32", x=x, y=out, n=n, lo=low, hi=high)
        return
    if op == "LeakyRelu":
        ctx.module.run("nu_unary_f32", x=x, y=out, n=n, code=20,
                       lo=float(node.attrs.get("alpha", 0.01)), hi=0.0)
        return
    code = _UNARY_CODES.get(op)
    if code is None:
        raise UnsupportedStepError(f"no unary lowering for {op}")
    ctx.module.run("nu_unary_f32", x=x, y=out, n=n, code=code, lo=0.0, hi=0.0)


def _lower_prelu(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    slope = ctx.device(node.inputs[1])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si, ctx.shape_of(node.inputs[1])])
    out = ctx.alloc(node.output, so, F32)
    slope_strides = broadcast_strides(ctx.shape_of(node.inputs[1]), so)
    kwargs = {f"o{i}": value for i, value in enumerate(pad_to(so, 8))}
    kwargs.update({
        f"s{i}": value
        for i, value in enumerate(pad_to(slope_strides, 8, 0))
    })
    ctx.module.run("nu_prelu", x=x, slope=slope, y=out, n=product(so), **kwargs)


def _lower_binary(node: GraphNode, ctx: _Ctx) -> None:
    op = node.op
    a_name, b_name = node.inputs[0], node.inputs[1]
    sa, sb = ctx.shape_of(a_name), ctx.shape_of(b_name)
    so = ctx.infer_out(node, [sa, sb])
    out_dtype = ctx.session.plan.dtypes[node.output]
    out = ctx.alloc(node.output, so, out_dtype)
    a = ctx.device(a_name)
    b = ctx.device(b_name)
    n = product(so)
    if ctx.session.plan.dtypes.get(a_name) == I64 or ctx.session.plan.dtypes.get(b_name) == I64:
        if native_i64.binary(ctx, node, op, a, b, out, sa, sb, so, n):
            return
        if (not ctx.session.int64_candidate
                or op not in ("Add", "Sub", "Mul", "Div", "Mod", "Less", "Greater", "Equal")
                or max(len(sa), len(sb), len(so)) > 8):
            raise UnsupportedStepError(
                f"dynamic INT64 {op} requires a matching CPU candidate graph"
            )
        if op in ("Less", "Greater", "Equal"):
            cmp_code = {"Less": 0, "Greater": 1, "Equal": 2}[op]
            if sa == sb == so:
                ctx.module.run("nu_i64_cmp_flat", a=a, b=b, y=out, n=n, code=cmp_code)
            else:
                kwargs = {"a": a, "b": b, "y": out, "n": n, "code": cmp_code}
                kwargs.update({f"o{i}": value for i, value in enumerate(pad_to(so, 8))})
                kwargs.update({f"a{i}": value for i, value in enumerate(pad_to(broadcast_strides(sa, so), 8, 0))})
                kwargs.update({f"b{i}": value for i, value in enumerate(pad_to(broadcast_strides(sb, so), 8, 0))})
                ctx.module.run("nu_i64_cmp_broadcast_candidate", **kwargs)
            return
        code = {"Add": 0, "Sub": 1, "Mul": 2, "Mod": 3, "Div": 4}[op]
        if sa == sb == so:
            status = ctx.candidate_status()
            ctx.module.run("nu_i64_binary_flat", a=a, b=b, y=out, n=n,
                           code=code, fmod=int(node.attrs.get("fmod", 0)), status=status)
        elif product(sb) == 1 and sa == so:
            status = ctx.candidate_status()
            ctx.module.run("nu_i64_binary_scalar_rhs", a=a, b=b, y=out, n=n,
                           code=code, fmod=int(node.attrs.get("fmod", 0)), status=status)
        else:
            status = ctx.candidate_status()
            kwargs = {
                "a": a, "b": b, "y": out, "n": n, "code": code,
                "fmod": int(node.attrs.get("fmod", 0)), "status": status,
            }
            kwargs.update({f"o{i}": value for i, value in enumerate(pad_to(so, 8))})
            kwargs.update({f"a{i}": value for i, value in enumerate(pad_to(broadcast_strides(sa, so), 8, 0))})
            kwargs.update({f"b{i}": value for i, value in enumerate(pad_to(broadcast_strides(sb, so), 8, 0))})
            ctx.module.run("nu_i64_binary_broadcast_candidate", **kwargs)
        if op in ("Div", "Mod"):
            ctx.check_candidate_status(status, op)
        return
    if op == "And":
        ctx.module.run("nu_and_i32", a=a, b=b, y=out, n=n)
        return
    if op in ("Max", "Min"):
        code = 6 if op == "Max" else 5
        ctx.module.run("nu_binary_flat", a=a, b=b, y=out, n=n, code=code)
        return
    code = _BINARY_CODES[op]
    is_cmp = op in ("Less", "Greater", "Equal")
    flat = "nu_binary_cmp_flat" if is_cmp else "nu_binary_flat"
    scalar_rhs = "nu_binary_cmp_scalar_rhs" if is_cmp else "nu_binary_scalar_rhs"
    scalar_lhs = "nu_binary_cmp_scalar_lhs" if is_cmp else "nu_binary_scalar_lhs"
    broadcast = "nu_binary_cmp_broadcast" if is_cmp else "nu_binary_broadcast"
    if sa == sb == so:
        ctx.module.run(flat, a=a, b=b, y=out, n=n, code=code)
    elif product(sb) == 1:
        ctx.module.run(scalar_rhs, a=a, b=b, y=out, n=n, code=code)
    elif product(sa) == 1:
        ctx.module.run(scalar_lhs, a=a, b=b, y=out, n=n, code=code)
    else:
        kwargs = {"a": a, "b": b, "y": out, "n": n, "code": code}
        kwargs.update({f"o{i}": v for i, v in enumerate(pad_to(so, 8))})
        kwargs.update({f"a{i}": v for i, v in enumerate(pad_to(broadcast_strides(sa, so), 8, 0))})
        kwargs.update({f"b{i}": v for i, v in enumerate(pad_to(broadcast_strides(sb, so), 8, 0))})
        ctx.module.run(broadcast, **kwargs)


def _lower_logical(node: GraphNode, ctx: _Ctx) -> None:
    op = node.op
    a_name = node.inputs[0]
    sa = ctx.shape_of(a_name)
    a = ctx.device(a_name)
    out = ctx.alloc(node.output, sa, ctx.session.plan.dtypes[node.output])
    n = product(sa)
    if op == "Not":
        ctx.module.run("nu_not_i32", a=a, y=out, n=n)
        return
    b_name = node.inputs[1]
    b = ctx.device(b_name)
    sb = ctx.shape_of(b_name)
    if sa != sb:
        raise UnsupportedStepError(f"{op} requires equal operand shapes, got {sa} and {sb}")
    kernel = {"Or": "nu_or_i32", "Xor": "nu_xor_i32", "And": "nu_and_i32"}[op]
    ctx.module.run(kernel, a=a, b=b, y=out, n=n)


def _lower_sum(node: GraphNode, ctx: _Ctx) -> None:
    """Elementwise sum of N operands, evaluated as a chain of binary adds."""
    shapes = [ctx.shape_of(name) for name in node.inputs]
    so = shapes[0]
    for other in shapes[1:]:
        if other != so:
            so = shapeinfer.infer("Add", node.attrs, [so, other], {}, [F32, F32])
    if len(node.inputs) == 1:
        out = ctx.alloc(node.output, so, F32)
        ctx.module.run("nu_copy_f32", x=ctx.device(node.inputs[0]), y=out, n=product(so))
        return
    current = ctx.device(node.inputs[0])
    for position in range(1, len(node.inputs)):
        last = position == len(node.inputs) - 1
        name = node.output if last else f"{node.output}__sum{position}"
        out = ctx.alloc(name, so, F32)
        ctx.module.run("nu_binary_flat", a=current, b=ctx.device(node.inputs[position]),
                       y=out, n=product(so), code=0)
        current = out


def _lower_where(node: GraphNode, ctx: _Ctx) -> None:
    cond = ctx.device(node.inputs[0])
    x = ctx.device(node.inputs[1])
    y = ctx.device(node.inputs[2])
    sc, sx, sy = ctx.shape_of(node.inputs[0]), ctx.shape_of(node.inputs[1]), ctx.shape_of(node.inputs[2])
    so = ctx.infer_out(node, [sc, sx, sy])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    n = product(so)
    if ctx.session.plan.dtypes[node.output] == I64:
        if not ctx.session.int64_candidate or max(len(sc), len(sx), len(sy), len(so)) > 8:
            raise UnsupportedStepError("dynamic INT64 Where requires CPU candidate graph")
        if sc == sx == sy == so:
            ctx.module.run("nu_where_i64_flat", cond=cond, x=x, other=y, out=out, n=n)
        else:
            if "nu_where_i64_broadcast_candidate" not in ctx.session.pool_graph_names:
                raise UnsupportedStepError("INT64 Where broadcast graph is missing from candidate pool")
            kwargs = {"cond": cond, "x": x, "other": y, "out": out, "n": n}
            kwargs.update({f"o{i}": v for i, v in enumerate(pad_to(so, 8))})
            kwargs.update({f"c{i}": v for i, v in enumerate(pad_to(broadcast_strides(sc, so), 8, 0))})
            kwargs.update({f"x{i}": v for i, v in enumerate(pad_to(broadcast_strides(sx, so), 8, 0))})
            kwargs.update({f"y{i}": v for i, v in enumerate(pad_to(broadcast_strides(sy, so), 8, 0))})
            ctx.module.run("nu_where_i64_broadcast_candidate", **kwargs)
        return
    if sc == sx == sy == so:
        ctx.module.run("nu_where_flat", cond=cond, x=x, y_in=y, out=out, n=n)
    elif product(sx) == 1 and sy == so and sc == so:
        ctx.module.run("nu_where_scalar_lhs", cond=cond, x=x, y_in=y, out=out, n=n)
    elif product(sy) == 1 and sx == so and sc == so:
        ctx.module.run("nu_where_scalar_rhs", cond=cond, x=x, y_in=y, out=out, n=n)
    else:
        kwargs = {"cond": cond, "x": x, "y_in": y, "out": out, "n": n}
        kwargs.update({f"o{i}": v for i, v in enumerate(pad_to(so, 8))})
        kwargs.update({f"c{i}": v for i, v in enumerate(pad_to(broadcast_strides(sc, so), 8, 0))})
        kwargs.update({f"x{i}": v for i, v in enumerate(pad_to(broadcast_strides(sx, so), 8, 0))})
        kwargs.update({f"y{i}": v for i, v in enumerate(pad_to(broadcast_strides(sy, so), 8, 0))})
        ctx.module.run("nu_where_broadcast", **kwargs)


def _conv_common(node: GraphNode, ctx: _Ctx):
    attrs = node.attrs
    x = ctx.device(node.inputs[0])
    w = ctx.device(node.inputs[1])
    si = ctx.shape_of(node.inputs[0])
    sw = ctx.shape_of(node.inputs[1])
    so = ctx.infer_out(node, [si, sw])
    out = ctx.alloc(node.output, so, F32)
    has_bias = len(node.inputs) > 2 and bool(node.inputs[2])
    bias = ctx.device(node.inputs[2]) if has_bias else ctx.dummy
    strides = [int(v) for v in attrs.get("strides", (1, 1))]
    dilations = [int(v) for v in attrs.get("dilations", (1, 1))]
    pads = shapeinfer.conv_pads(si[2:], sw[2:], attrs)
    act = 0
    if node.op == "FusedConv":
        act = {"relu": 1, "sigmoid": 2, "tanh": 3, "gelu": 4}.get(
            str(attrs.get("activation", "")).lower(), 0)
    elif node.op == "DmlFusedConv":
        act = {"relu": 1, "sigmoid": 2, "tanh": 3, "gelu": 4}.get(
            str(attrs.get("fused_activation", "")).lower(), 0)
    return x, w, bias, si, sw, so, out, has_bias, int(attrs.get("group", 1)), pads, strides, dilations, act


def _rust_conv_available() -> bool:
    """Whether the conv path can actually run against runtime buffers.

    The Rust kernels take raw device pointers. ``taichi_python`` exposes them,
    but the bridge buffer type does not, so this stays ``False`` until a device
    pointer is reachable — advertising it earlier would produce a crash rather
    than an acceleration.
    """
    try:
        from taichi import taichi_python  # noqa: F401
    except ImportError:
        return False
    if not hasattr(taichi_python, "conv2d_f32"):
        return False
    try:
        from taichi.aot_engine import TaichiGPUBuffer
    except ImportError:
        return False
    return hasattr(TaichiGPUBuffer, "data_ptr")


def _handle_of(buffer) -> Optional[int]:
    """Device address of an engine buffer, or ``None`` when not addressable."""
    data_ptr = getattr(buffer, "data_ptr", None)
    if data_ptr is None:
        return None
    try:
        address = int(data_ptr() if callable(data_ptr) else data_ptr)
    except (TypeError, ValueError, RuntimeError):
        return None
    return address or None


def _try_rust_conv(ctx: _Ctx, x, w, bias, out, si, sw, so, has_bias: bool,
                   group: int, pads, strides, dilations, act: int) -> bool:
    """Run the convolution through the Rust im2col+GEMM path when admitted.

    Admitted profile: f32, 4D NCHW, `group == 1`, `dilation == 1`. Everything
    else returns False so the existing Taichi dispatch handles it unchanged.
    The workspace is owned by the session, so no allocation happens in Rust.
    """
    session = ctx.session
    if not getattr(session, "use_rust_conv", False):
        return False
    if group != 1 or dilations != [1, 1]:
        return False
    if len(si) != 4 or len(so) != 4:
        return False
    if getattr(session, "_rust_conv_ready", None) is None:
        session._rust_conv_ready = _rust_conv_available()
    if not session._rust_conv_ready:
        return False

    n, ci, h, w_in = (int(v) for v in si)
    co, oh, ow = int(so[1]), int(so[2]), int(so[3])
    kh, kw = int(sw[2]), int(sw[3])
    elements = ci * kh * kw * oh * ow
    if elements <= 0:
        return False

    workspace = session.acquire_slot("__rust_conv_workspace", (elements,), F32)
    pointers = {
        "x": _handle_of(x),
        "w": _handle_of(w),
        "y": _handle_of(out),
        "workspace": _handle_of(workspace),
    }
    if any(value is None for value in pointers.values()):
        return False  # not a native buffer; leave it to the Taichi path
    bias_ptr = _handle_of(bias) if has_bias else 0
    if has_bias and bias_ptr is None:
        return False

    try:
        from taichi import taichi_python

        taichi_python.conv2d_f32(
            pointers["x"], pointers["w"], bias_ptr or 0, pointers["y"],
            n, ci, co, h, w_in, oh, ow, kh, kw,
            int(strides[0]), int(strides[1]), int(pads[0]), int(pads[1]),
            1 if has_bias else 0, int(act),
            pointers["workspace"], elements * 4,
        )
    except Exception:
        # Never mask a real run: fall back to the Taichi kernel and remember not
        # to try again for this session.
        session._rust_conv_ready = False
        return False
    session._rust_conv_used = True
    return True


def _lower_conv(node: GraphNode, ctx: _Ctx) -> None:
    (x, w, bias, si, sw, so, out, has_bias, group, pads,
     strides, dilations, act) = _conv_common(node, ctx)
    fusion = ctx.conv_activation_fusions.get(node.index)
    output_name = node.output
    if fusion is not None:
        _activation_index, output_name, fused_act = fusion
        act = fused_act
    out = ctx.alloc(output_name, so, F32)
    if _try_rust_conv(ctx, x, w, bias, out, si, sw, so, has_bias, group,
                      pads, strides, dilations, act):
        return
    if (sw[2:] == (3, 3) and group == si[1] == so[1] and strides == [1, 1]
            and dilations == [1, 1] and pads == [1, 1, 1, 1]):
        ctx.module.run("nu_conv2d_depthwise_3x3_s1p1", x=x, w=w, b=bias, y=out,
                       n_batch=si[0], channels=si[1], h=si[2], w_in=si[3],
                       has_bias=1 if has_bias else 0, act=act)
        return
    if (sw[2:] == (3, 3) and group == 1 and strides == [1, 1]
            and dilations == [1, 1] and pads == [1, 1, 1, 1]):
        ctx.module.run("nu_conv2d_3x3_s1p1", x=x, w=w, b=bias, y=out,
                       n_batch=si[0], ci=si[1], co=so[1], h=si[2], w_in=si[3],
                       has_bias=1 if has_bias else 0, act=act)
        return
    if (sw[2:] == (1, 1) and group == 1 and strides == [1, 1]
            and dilations == [1, 1] and pads == [0, 0, 0, 0]):
        ctx.module.run("nu_conv2d_1x1", x=x, w=w, b=bias, y=out, n_batch=si[0],
                       ci=si[1], co=so[1], hw=si[2] * si[3],
                       has_bias=1 if has_bias else 0, act=act)
        return
    if (sw[2:] == (4, 4) and strides == [2, 2] and dilations == [1, 1]
            and pads == [0, 0, 0, 0]):
        ctx.module.run(
            "nu_conv2d_4x4_s2", x=x, w=w, b=bias, y=out,
            n_batch=si[0], ci=si[1], co=so[1], h=si[2], w_in=si[3],
            oh=so[2], ow=so[3], group=group,
            has_bias=1 if has_bias else 0, act=act,
        )
        return
    if (sw[2:] == (4, 4) and group == 1 and strides == [1, 1]
            and dilations == [1, 1] and pads == [0, 0, 0, 0]
            and so[2] == si[2] - 3 and so[3] == si[3] - 3
            and "nu_conv2d_4x4_s1" in ctx.session.pool_graph_names):
        # Unrolled 4x4, stride 1, pad 0. Guarded by the artifact manifest, so the
        # generic kernel stays the fallback until the pool is rebuilt (blocker B1b).
        ctx.module.run(
            "nu_conv2d_4x4_s1", x=x, w=w, b=bias, y=out,
            n_batch=si[0], ci=si[1], co=so[1], h=si[2], w_in=si[3],
            oh=so[2], ow=so[3],
            has_bias=1 if has_bias else 0, act=act,
        )
        return
    ctx.module.run(
        "nu_conv2d", x=x, w=w, b=bias, y=out, n_batch=si[0], ci=si[1], co=so[1],
        h=si[2], w_in=si[3], oh=so[2], ow=so[3], kh=sw[2], kw=sw[3],
        sh=strides[0], sw=strides[1], ph=pads[0], pw=pads[1],
        dh=dilations[0], dw=dilations[1], group=group,
        has_bias=1 if has_bias else 0, act=act,
    )


def _lower_conv_transpose(node: GraphNode, ctx: _Ctx) -> None:
    (x, w, bias, si, sw, so, out, has_bias, group, pads,
     strides, dilations, _act) = _conv_common(node, ctx)
    ctx.module.run(
        "nu_conv_transpose2d", x=x, w=w, b=bias, y=out, n_batch=si[0],
        ci=si[1], co=so[1], h=si[2], w_in=si[3], oh=so[2], ow=so[3],
        kh=sw[2], kw=sw[3], sh=strides[0], sw=strides[1], ph=pads[0],
        pw=pads[1], dh=dilations[0], dw=dilations[1], group=group,
        has_bias=1 if has_bias else 0, act=0,
    )


def _lower_matmul(node: GraphNode, ctx: _Ctx) -> None:
    a_name, b_name = node.inputs[0], node.inputs[1]
    sa, sb = ctx.shape_of(a_name), ctx.shape_of(b_name)
    so = ctx.infer_out(node, [sa, sb])
    out = ctx.alloc(node.output, so, F32)
    a = ctx.device(a_name)
    b = ctx.device(b_name)
    m, k, n_dim = sa[-2], sa[-1], sb[-1]
    batch_a = product(sa[:-2]) if len(sa) > 2 else 1
    batch_b = product(sb[:-2]) if len(sb) > 2 else 1
    trans_b = node.op == "FusedMatMul" and int(node.attrs.get("transB", 0)) != 0
    kernel = "nu_matmul_transb" if trans_b else "nu_matmul"
    batch = max(batch_a, batch_b)
    ctx.module.run(
        kernel, a=a, b=b, y=out, batch=batch, m=m, k=k, n=n_dim,
        a_batch_stride=m * k if batch_a > 1 else 0,
        b_batch_stride=(n_dim * k if trans_b else k * n_dim) if batch_b > 1 else 0,
    )


def _lower_gemm(node: GraphNode, ctx: _Ctx) -> None:
    attrs = node.attrs
    a = ctx.device(node.inputs[0])
    b = ctx.device(node.inputs[1])
    sa, sb = ctx.shape_of(node.inputs[0]), ctx.shape_of(node.inputs[1])
    so = ctx.infer_out(node, [sa, sb])
    out = ctx.alloc(node.output, so, F32)
    trans_a = int(attrs.get("transA", 0))
    trans_b = int(attrs.get("transB", 0))
    k = sa[1] if trans_a == 0 else sa[0]
    has_c = len(node.inputs) > 2 and bool(node.inputs[2])
    c = ctx.device(node.inputs[2]) if has_c else ctx.dummy
    ctx.module.run(
        "nu_gemm", a=a, b=b, c=c, y=out, m=so[0], k=k, n=so[1],
        trans_a=trans_a, trans_b=trans_b,
        alpha=float(attrs.get("alpha", 1.0)), beta=float(attrs.get("beta", 1.0)),
        has_c=1 if has_c else 0,
    )


def _lower_reduce(node: GraphNode, ctx: _Ctx) -> None:
    op = node.op
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    if op == "ArgMax":
        ctx.module.run("nu_argmax_last", x=x, y=out, rows=product(si[:-1]), cols=si[-1])
        return
    axes = node.attrs.get("axes")
    if axes is None and ctx.const_arg(node, 1) is not None:
        axes = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
    rank = len(si)
    if axes is None or len(axes) == 0:
        axes = list(range(rank))
    axes = sorted(normalize_axis(int(a), rank) for a in axes)
    kernel = _REDUCE_KERNELS[op]
    if len(axes) == rank:
        # Deterministic single-axis reduction over the flattened tensor; the
        # atomic-accumulate variant is avoided because its summation order is
        # not reproducible and drifts from the reference by a large margin.
        if op == "ReduceSum":
            ctx.module.run("nu_reduce_sum", x=x, y=out, outer_size=1,
                           axis_dim=product(si), inner_size=1)
        elif op == "ReduceMean":
            ctx.module.run("nu_reduce_mean", x=x, y=out, outer_size=1,
                           axis_dim=product(si), inner_size=1)
        else:
            ctx.module.run(kernel, x=x, y=out, outer_size=1, axis_dim=product(si),
                           inner_size=1)
        return
    current = x
    current_shape = si
    for position, axis in enumerate(reversed(axes)):
        real_axis = axis if position == 0 else axis
        interim_shape = tuple(d for i, d in enumerate(current_shape) if i != real_axis)
        last = position == len(axes) - 1
        if last:
            interim = ctx.alloc(node.output, so, F32)
        else:
            interim = ctx.alloc(f"{node.output}__r{position}", interim_shape, F32)
        outer = product(current_shape[:real_axis]) if real_axis else 1
        inner = product(current_shape[real_axis + 1:]) if real_axis + 1 < len(current_shape) else 1
        ctx.module.run(kernel, x=current, y=interim, outer_size=outer,
                       axis_dim=current_shape[real_axis], inner_size=inner)
        current = interim
        current_shape = interim_shape
    if current_shape != so:
        ctx.module.run("nu_copy_f32", x=current, y=out, n=product(so))


def _lower_norm(node: GraphNode, ctx: _Ctx) -> None:
    op = node.op
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, F32)
    eps = float(node.attrs.get("epsilon", 1e-5))
    if op == "InstanceNormalization":
        if ctx.session.plan.dtypes[node.inputs[0]] != F32:
            raise UnsupportedStepError("InstanceNormalization in this profile requires FP32 input")
        if len(si) != 4:
            raise UnsupportedStepError("InstanceNormalization in this profile requires rank-4 NCHW input")
        spatial = product(si[2:])
        if spatial <= 0:
            raise UnsupportedStepError("InstanceNormalization requires a non-empty spatial dimension")
        has_scale = len(node.inputs) > 1 and bool(node.inputs[1])
        has_bias = len(node.inputs) > 2 and bool(node.inputs[2])
        if has_scale:
            if ctx.session.plan.dtypes[node.inputs[1]] != F32:
                raise UnsupportedStepError("InstanceNormalization scale must be FP32")
            if ctx.shape_of(node.inputs[1]) != (si[1],):
                raise UnsupportedStepError("InstanceNormalization scale must have shape [channels]")
        if has_bias:
            if ctx.session.plan.dtypes[node.inputs[2]] != F32:
                raise UnsupportedStepError("InstanceNormalization bias must be FP32")
            if ctx.shape_of(node.inputs[2]) != (si[1],):
                raise UnsupportedStepError("InstanceNormalization bias must have shape [channels]")
        scale = ctx.device(node.inputs[1]) if has_scale else ctx.dummy
        bias = ctx.device(node.inputs[2]) if has_bias else ctx.dummy
        candidate_graph = "nu_instance_norm_packet4_affine_candidate"
        if (len(si) == 4 and ctx.session.int64_candidate
                and candidate_graph in ctx.session.pool_graph_names):
            ctx.module.run(candidate_graph, x=x, scale=scale, bias=bias, y=out,
                           n_batch=si[0], channels=si[1], spatial=spatial,
                           eps=eps, has_scale=1 if has_scale else 0,
                           has_bias=1 if has_bias else 0)
            return
        ctx.module.run("nu_instance_norm", x=x, scale=scale, bias=bias, y=out,
                       n_batch=si[0], channels=si[1], spatial=si[2] * si[3],
                       eps=eps, has_scale=1 if has_scale else 0,
                       has_bias=1 if has_bias else 0, act=0)
        return
    if op == "LayerNormalization":
        axis = normalize_axis(int(node.attrs.get("axis", -1)), len(si))
        outer = product(si[:axis]) if axis else 1
        has_scale = len(node.inputs) > 1 and bool(node.inputs[1])
        has_bias = len(node.inputs) > 2 and bool(node.inputs[2])
        scale = ctx.device(node.inputs[1]) if has_scale else ctx.dummy
        bias = ctx.device(node.inputs[2]) if has_bias else ctx.dummy
        ctx.module.run("nu_layer_norm", x=x, scale=scale, bias=bias, y=out,
                       outer_size=outer, axis_dim=product(si[axis:]), eps=eps,
                       has_scale=1 if has_scale else 0,
                       has_bias=1 if has_bias else 0, act=0)
        return
    if op == "BatchNormalization":
        ctx.module.run(
            "nu_batch_norm", x=x, scale=ctx.device(node.inputs[1]),
            bias=ctx.device(node.inputs[2]), mean=ctx.device(node.inputs[3]),
            var=ctx.device(node.inputs[4]), y=out, n_batch=si[0], channels=si[1],
            spatial=product(si[2:]), eps=eps, act=0,
        )
        return
    axis = normalize_axis(int(node.attrs.get("axis", -1)), len(si))
    outer = product(si[:axis]) if axis else 1
    inner = product(si[axis + 1:]) if axis + 1 < len(si) else 1
    kernel = "nu_softmax" if op == "Softmax" else "nu_log_softmax"
    ctx.module.run(kernel, x=x, y=out, outer_size=outer, axis_dim=si[axis], inner_size=inner)


def _lower_gather(node: GraphNode, ctx: _Ctx) -> None:
    data_name, index_name = node.inputs[0], node.inputs[1]
    data = ctx.device(data_name)
    data_dtype = ctx.session.plan.dtypes[data_name]
    index_dtype = ctx.session.plan.dtypes[index_name]
    dynamic_i64_indices = index_dtype == I64 and index_name in ctx.buffers
    native_path = (data_dtype == I64 or index_dtype == I64) and native_i64.available()
    if node.op == "Gather" and data_dtype == I64:
        indices = None  # Promoted/checked below, before any narrowing.
    elif node.op == "GatherElements" and index_dtype == I64:
        if native_path:
            indices = ctx.device(index_name)
        elif data_dtype not in (F32, I64) or not ctx.session.int64_candidate:
            raise UnsupportedStepError("INT64 GatherElements requires supported data dtype and CPU candidate graph")
        else:
            indices = ctx.device(index_name)
    elif node.op == "Gather" and dynamic_i64_indices:
        if native_path:
            indices = ctx.device(index_name)
        elif not ctx.session.int64_candidate or data_dtype not in (F32, I64):
            raise UnsupportedStepError("dynamic INT64 Gather indices require CPU candidate graph")
        else:
            indices = ctx.device(index_name)
    else:
        indices = ctx.device_i32(index_name)
    sd, si = ctx.shape_of(node.inputs[0]), ctx.shape_of(node.inputs[1])
    so = ctx.infer_out(node, [sd, si])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    axis = normalize_axis(int(node.attrs.get("axis", 0)), len(sd))
    outer = product(sd[:axis]) if axis else 1
    inner = product(sd[axis + 1:]) if axis + 1 < len(sd) else 1
    if node.op == "Gather":
        if data_dtype == I64 or (dynamic_i64_indices and index_dtype == I64):
            # `data` may be a compile-time constant with no device buffer yet;
            # the native path uploads it on demand. The index operand must itself
            # be i64 — a narrowed i32 buffer is a different layout.
            if native_i64.gather(ctx, node, data if data_name in ctx.buffers else None,
                                 indices, out, sd, si, so, axis):
                return
        if data_dtype == I64:
            if (not ctx.session.int64_candidate
                    or "nu_gather_i64_indices_i64_candidate" not in ctx.session.pool_graph_names):
                raise UnsupportedStepError("INT64 Gather data requires the checked CPU candidate graph")
            if index_dtype == I32:
                indices_i32 = ctx.device(index_name)
                indices = ctx.alloc_temp(f"__nu_gather_i64_indices_{node.index}", si, I64)
                ctx.module.run("nu_cast_i32_i64", x=indices_i32, y=indices, n=product(si))
            elif index_dtype == I64:
                indices = ctx.device(index_name)
            else:
                raise UnsupportedStepError(
                    f"INT64 Gather data with index dtype {index_dtype} is unsupported"
                )
            status = ctx.candidate_status()
            ctx.module.run("nu_gather_i64_indices_i64_candidate", data=data,
                           indices=indices, y=out, status=status, outer_size=outer,
                           indices_size=product(si), axis_dim=sd[axis], inner_size=inner)
            ctx.check_candidate_status(status, "Gather")
            return
        if dynamic_i64_indices:
            status = ctx.candidate_status()
            kernel = ("nu_gather_i64_indices_i64_candidate" if data_dtype == I64
                      else "nu_gather_i64_indices_f32_candidate")
            ctx.module.run(kernel, data=data, indices=indices, y=out, status=status,
                           outer_size=outer, indices_size=product(si),
                           axis_dim=sd[axis], inner_size=inner)
            ctx.check_candidate_status(status, "Gather")
        elif data_dtype == I64:
            if not ctx.session.int64_candidate:
                raise UnsupportedStepError("INT64 Gather data requires the CPU candidate graph")
            ctx.module.run("nu_gather_i64_candidate", data=data, indices=indices, y=out,
                           outer_size=outer, indices_size=product(si),
                           axis_dim=sd[axis], inner_size=inner)
        else:
            ctx.module.run("nu_gather", data=data, indices=indices, y=out,
                           outer_size=outer, indices_size=product(si),
                           axis_dim=sd[axis], inner_size=inner)
    else:
        if index_dtype == I64:
            status = ctx.candidate_status()
            kernel = ("nu_gather_elements_i64_data_i64_indices_candidate"
                      if data_dtype == I64 else "nu_gather_elements_i64_indices_candidate")
            ctx.module.run(kernel, data=data,
                           indices=indices, y=out, status=status, outer_size=outer,
                           axis_dim_data=sd[axis], axis_dim_idx=si[axis], inner_size=inner)
            ctx.check_candidate_status(status, "GatherElements")
        else:
            ctx.module.run("nu_gather_elements", data=data, indices=indices, y=out,
                           outer_size=outer, axis_dim_data=sd[axis],
                           axis_dim_idx=si[axis], inner_size=inner)


def _lower_concat(node: GraphNode, ctx: _Ctx) -> None:
    first_shape = ctx.shape_of(node.inputs[0])
    axis = normalize_axis(int(node.attrs["axis"]), len(first_shape))
    so = ctx.infer_out(node, [ctx.shape_of(n) for n in node.inputs])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    is_i64 = ctx.session.plan.dtypes[node.output] == I64
    if is_i64 and not ctx.session.int64_candidate:
        shapes = [ctx.shape_of(name) for name in node.inputs]
        parts = [ctx.device(name) for name in node.inputs]
        if native_i64.concat(ctx, node, parts, out, shapes, so, axis):
            return
        raise UnsupportedStepError("INT64 Concat requires the isolated CPU candidate pool")
    outer = product(so[:axis]) if axis else 1
    inner = product(so[axis + 1:]) if axis + 1 < len(so) else 1
    if len(node.inputs) == 2:
        ctx.module.run("nu_concat2_i64_candidate" if is_i64 else "nu_concat2", a=ctx.device(node.inputs[0]),
                       b=ctx.device(node.inputs[1]), y=out, outer_size=outer,
                       dim_a=ctx.shape_of(node.inputs[0])[axis],
                       dim_b=ctx.shape_of(node.inputs[1])[axis], inner_size=inner)
        return
    offset = 0
    for name in node.inputs:
        shape = ctx.shape_of(name)
        ctx.module.run("nu_copy_concat_axis_i64_candidate" if is_i64 else "nu_copy_concat_axis", src=ctx.device(name), dst=out,
                       outer_size=outer, src_axis_dim=shape[axis],
                       dst_axis_dim=so[axis], axis_offset=offset, inner_size=inner)
        offset += shape[axis]


def _lower_split(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    is_i64 = ctx.session.plan.dtypes[node.inputs[0]] == I64
    axis = normalize_axis(int(node.attrs.get("axis", 0)), len(si))
    split = node.attrs.get("split")
    if split is None and ctx.const_arg(node, 1) is not None:
        split = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
    if split is None:
        count = int(node.attrs.get("num_outputs", len(node.outputs)))
        sizes = [si[axis] // count] * count
    else:
        sizes = [int(v) for v in split]
    outer = product(si[:axis]) if axis else 1
    inner = product(si[axis + 1:]) if axis + 1 < len(si) else 1
    if is_i64 and not ctx.session.int64_candidate and native_i64.available():
        offset = 0
        for name, size in zip(node.outputs, sizes):
            out_shape = tuple(size if i == axis else d for i, d in enumerate(si))
            out = ctx.alloc(name, out_shape, ctx.session.plan.dtypes[name])
            if not native_i64.split(ctx, node, x, out, si, out_shape, axis, offset):
                raise UnsupportedStepError("INT64 Split requires the isolated CPU candidate pool")
            offset += size
        return
    if is_i64 and not ctx.session.int64_candidate:
        raise UnsupportedStepError("INT64 Split requires the isolated CPU candidate pool")
    offset = 0
    for name, size in zip(node.outputs, sizes):
        out_shape = tuple(size if i == axis else d for i, d in enumerate(si))
        out = ctx.alloc(name, out_shape, ctx.session.plan.dtypes[name])
        ctx.module.run("nu_copy_split_axis_i64_candidate" if is_i64 else "nu_copy_split_axis", src=x, dst=out, outer_size=outer,
                       src_axis_dim=si[axis], dst_axis_dim=size,
                       axis_offset=offset, inner_size=inner)
        offset += size


def _lower_slice(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    is_i64 = ctx.session.plan.dtypes[node.inputs[0]] == I64
    starts = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
    ends = [int(v) for v in np.asarray(ctx.const_arg(node, 2)).ravel()]
    axes = (
        [int(v) for v in np.asarray(ctx.const_arg(node, 3)).ravel()]
        if ctx.const_arg(node, 3) is not None
        else list(range(len(starts)))
    )
    steps = (
        [int(v) for v in np.asarray(ctx.const_arg(node, 4)).ravel()]
        if ctx.const_arg(node, 4) is not None
        else [1] * len(starts)
    )
    if is_i64 and not ctx.session.int64_candidate:
        if len(axes) == 1:
            so_native = ctx.infer_out(node, [si])
            output = ctx.alloc(node.output, so_native, ctx.session.plan.dtypes[node.output])
            if native_i64.slice_axis(
                ctx, node, x, output, si, so_native,
                normalize_axis(axes[0], len(si)), starts[0], steps[0],
            ):
                return
        raise UnsupportedStepError("INT64 Slice requires the isolated CPU candidate pool")
    so = ctx.infer_out(node, [si])
    current = x
    current_shape = si
    for position, (start, end, raw_axis, step) in enumerate(zip(starts, ends, axes, steps)):
        axis = normalize_axis(raw_axis, len(si))
        dim = current_shape[axis]
        resolved_start = start + dim if start < 0 else start
        resolved_end = end + dim if end < 0 else end
        if step > 0:
            resolved_start = max(0, min(resolved_start, dim))
            resolved_end = max(0, min(resolved_end, dim))
            count = max(0, -(-(resolved_end - resolved_start) // step))
        else:
            resolved_start = max(-1, min(resolved_start, dim - 1))
            resolved_end = max(-1, resolved_end)
            count = max(0, -(-(resolved_start - resolved_end) // (-step)))
        out_shape = tuple(count if i == axis else d for i, d in enumerate(current_shape))
        last = position == len(starts) - 1
        name = node.output if last else f"{node.output}__s{position}"
        out = ctx.alloc(name, out_shape, ctx.session.plan.dtypes[node.output])
        outer = product(current_shape[:axis]) if axis else 1
        inner = product(current_shape[axis + 1:]) if axis + 1 < len(current_shape) else 1
        ctx.module.run("nu_slice_axis_i64_candidate" if is_i64 else "nu_slice_axis", src=current, dst=out, outer_size=outer,
                       src_axis_dim=current_shape[axis], dst_axis_dim=count,
                       start=resolved_start, step=step, inner_size=inner)
        current = out
        current_shape = out_shape
    if current_shape != so:
        ctx.module.run("nu_copy_i64_candidate" if is_i64 else "nu_copy_f32", x=current, y=ctx.buffers[node.output],
                       n=product(so))


def _lower_pad(node: GraphNode, ctx: _Ctx) -> None:
    mode = str(node.attrs.get("mode", "constant"))
    if mode != "constant":
        raise UnsupportedStepError(f"Pad mode {mode} is not admitted")
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    pads = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
    value = 0.0
    if ctx.const_arg(node, 2) is not None:
        value = float(np.asarray(ctx.const_arg(node, 2)).ravel()[0])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    if len(si) != 4:
        raise UnsupportedStepError(f"Pad admits rank-4 inputs only, got {si}")
    ctx.module.run("nu_pad_4d_constant", x=x, y=out, nc=si[0] * si[1],
                   h_in=si[2], w_in=si[3], h_out=so[2], w_out=so[3],
                   pad_top=pads[2], pad_left=pads[3], value=value)


def _lower_transpose(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    perm = node.attrs.get("perm")
    if perm is None:
        perm = list(range(len(si)))[::-1]
    strides = [1] * len(si)
    running = 1
    for axis in range(len(si) - 1, -1, -1):
        strides[axis] = running
        running *= si[axis]
    mapped = [strides[int(p)] for p in perm]
    kwargs = {"x": x, "y": out, "total": product(so)}
    kwargs.update({f"d{i}": v for i, v in enumerate(pad_to(so, 8))})
    kwargs.update({f"s{i}": v for i, v in enumerate(pad_to(mapped, 8, 0))})
    if ctx.session.plan.dtypes[node.inputs[0]] == I64:
        if not ctx.session.int64_candidate:
            if native_i64.transpose(ctx, node, x, out, si, so, perm):
                return
            raise UnsupportedStepError("INT64 Transpose requires the isolated CPU candidate pool")
        ctx.module.run("nu_transpose_general_i64_candidate", **kwargs)
    else:
        ctx.module.run("nu_transpose_general", **kwargs)


def _lower_expand(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    kwargs = {"x": x, "y": out, "total": product(so)}
    kwargs.update({f"d{i}": v for i, v in enumerate(pad_to(so, 8))})
    kwargs.update({f"s{i}": v for i, v in enumerate(pad_to(broadcast_strides(si, so), 8, 0))})
    if ctx.session.plan.dtypes[node.inputs[0]] == I64:
        if not ctx.session.int64_candidate:
            if si != so and native_i64.expand(ctx, node, x, out, si, so):
                return
            raise UnsupportedStepError("INT64 Expand requires the isolated CPU candidate pool")
        ctx.module.run("nu_transpose_general_i64_candidate", **kwargs)
    else:
        ctx.module.run("nu_transpose_general", **kwargs)


def _lower_tile(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, ctx.session.plan.dtypes[node.output])
    repeats = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
    rank = max(len(si), len(repeats))
    padded_in = pad_to(si, rank)
    padded_rep = pad_to(repeats, rank)
    inner = [padded_in[i] for i in range(rank)]
    kwargs = {"x": x, "y": out, "total": product(so)}
    kwargs.update({f"d{i}": v for i, v in enumerate(pad_to(so, 8))})
    kwargs.update({f"i{i}": v for i, v in enumerate(pad_to(inner, 8, 1))})
    kwargs.update({f"t{i}": v for i, v in enumerate(pad_to(padded_rep, 8, 1))})
    ctx.module.run("nu_tile_general", **kwargs)


def _lower_space_to_depth(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, F32)
    kernel = "nu_space_to_depth" if node.op == "SpaceToDepth" else "nu_depth_to_space"
    ctx.module.run(kernel, x=x, y=out, n_batch=si[0], channels=si[1],
                   h=si[2], w=si[3], block=int(node.attrs["blocksize"]))


def _lower_pool(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, F32)
    if node.op == "GlobalAveragePool":
        ctx.module.run("nu_global_average_pool2d", x=x, y=out, n_batch=si[0],
                       channels=si[1], spatial=product(si[2:]))
        return
    kernel = [int(v) for v in node.attrs["kernel_shape"]]
    strides = [int(v) for v in node.attrs.get("strides", (1, 1))]
    dilations = [int(v) for v in node.attrs.get("dilations", (1, 1))]
    pads = [int(v) for v in node.attrs.get("pads", (0,) * (2 * len(kernel)))]
    if len(pads) == len(kernel):
        pads = pads + pads
    if node.op == "AveragePool":
        vertical_graph = "nu_average_pool2d_2x2_vertical_candidate"
        has_vertical_candidate = (
            ctx.session.int64_candidate
            and vertical_graph in ctx.session.pool_graph_names
        )
        if has_vertical_candidate:
            vertical_candidate_matches = (
                node.domain == "ai.onnx"
                and ctx.session.plan.dtypes[node.inputs[0]] == F32
                and len(si) == 4
                and all(dimension > 0 for dimension in si)
                and kernel == [2, 2]
                and strides == [2, 2]
                and pads == [0, 0, 0, 0]
                and str(node.attrs.get("auto_pad", "NOTSET")) == "NOTSET"
                and int(node.attrs.get("ceil_mode", 0)) == 0
                and int(node.attrs.get("count_include_pad", 0)) == 1
                and so == (si[0], si[1], si[2] // 2, si[3] // 2)
            )
            if vertical_candidate_matches:
                ctx.module.run(
                    vertical_graph, x=x, y=out, n_batch=si[0], channels=si[1],
                    h=si[2], w=si[3], oh=so[2], ow=so[3],
                )
                return
            # The V18 candidate pool carries both reduction-order graphs. If
            # the exact vertical-order guard misses, continue to normal lowering.
        elif (ctx.session.int64_candidate and kernel == [2, 2]
                and "nu_average_pool2d_2x2_pair_candidate" in ctx.session.pool_graph_names):
            ctx.module.run(
                "nu_average_pool2d_2x2_pair_candidate", x=x, y=out,
                n_batch=si[0], channels=si[1], h=si[2], w=si[3],
                oh=so[2], ow=so[3], sh=strides[0], sw=strides[1],
                ph=pads[0], pw=pads[1],
                count_include_pad=int(node.attrs.get("count_include_pad", 0)),
            )
            return
        ctx.module.run("nu_average_pool2d", x=x, y=out, n_batch=si[0],
                       channels=si[1], h=si[2], w=si[3], oh=so[2], ow=so[3],
                       kh=kernel[0], kw=kernel[1], sh=strides[0], sw=strides[1],
                       ph=pads[0], pw=pads[1],
                       count_include_pad=int(node.attrs.get("count_include_pad", 0)))
    else:
        ctx.module.run("nu_max_pool2d", x=x, y=out, n_batch=si[0], channels=si[1],
                       h=si[2], w=si[3], oh=so[2], ow=so[3], kh=kernel[0],
                       kw=kernel[1], sh=strides[0], sw=strides[1],
                       ph=pads[0], pw=pads[1], dh=dilations[0], dw=dilations[1])


def _lower_resize(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [si])
    out = ctx.alloc(node.output, so, F32)
    scales = ctx.const_arg(node, 2)
    if scales is None:
        scale_h = si[2] / so[2]
        scale_w = si[3] / so[3]
    else:
        values = [float(v) for v in np.asarray(scales).ravel()]
        scale_h, scale_w = values[2], values[3]
    mode_attr = str(node.attrs.get("mode", "nearest"))
    mode = 0 if mode_attr in ("linear", "bilinear") else 1
    ctm = str(node.attrs.get("coordinate_transformation_mode", "half_pixel"))
    half_pixel = {"half_pixel": 1, "asymmetric": 0, "align_corners": 2}.get(ctm, 1)
    ctx.module.run("nu_resize_2d", x=x, y=out, n_batch=si[0], channels=si[1],
                   h_in=si[2], w_in=si[3], h_out=so[2], w_out=so[3],
                   scale_h=scale_h, scale_w=scale_w, mode=mode, half_pixel=half_pixel)


def _lower_topk(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    k = int(np.asarray(ctx.const_arg(node, 1)).ravel()[0])
    axis = normalize_axis(int(node.attrs.get("axis", -1)), len(si))
    output_shape = tuple(k if i == axis else d for i, d in enumerate(si))
    values = ctx.alloc(node.outputs[0], output_shape, F32)
    index_dtype = ctx.session.plan.dtypes[node.outputs[1]]
    if index_dtype == I64:
        if (not ctx.session.int64_candidate
                or "nu_topk_axis_i64_indices_candidate" not in ctx.session.pool_graph_names):
            if axis == len(si) - 1:
                indices = ctx.alloc(node.outputs[1], output_shape, I64)
                data_dtype = ctx.session.plan.dtypes[node.inputs[0]]
                if native_i64.topk_last(
                    ctx, node, x, values, indices,
                    product(si[:-1]), si[-1], k, data_dtype,
                ):
                    return
            raise UnsupportedStepError("ONNX TopK INT64 indices require the isolated CPU candidate graph")
        indices = ctx.alloc(node.outputs[1], output_shape, I64)
        outer = product(si[:axis]) if axis else 1
        inner = product(si[axis + 1:]) if axis + 1 < len(si) else 1
        taken = ctx.alloc(f"{node.outputs[0]}__taken", (outer * inner * si[axis],), I32)
        ctx.module.run("nu_topk_axis_i64_indices_candidate", x=x, values=values,
                       indices=indices, taken=taken, outer_size=outer,
                       axis_dim=si[axis], inner_size=inner, k=k,
                       largest=int(node.attrs.get("largest", 1)))
        return
    if axis != len(si) - 1:
        raise UnsupportedStepError("TopK admits the last axis only in this profile")
    indices = ctx.alloc(node.outputs[1], output_shape, index_dtype)
    taken = ctx.alloc(f"{node.outputs[0]}__taken", (si[-1],), I32)
    ctx.module.run("nu_fill_i32", y=taken, n=si[-1], value=0)
    ctx.module.run("nu_topk_last", x=x, values=values, indices=indices, taken=taken,
                   rows=product(si[:-1]), cols=si[-1], k=k,
                   largest=int(node.attrs.get("largest", 1)))


def _lower_nonzero(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    total = product(si)
    rank = len(si)
    counter = ctx.alloc(f"{node.output}__counter", (1,), I32)
    ctx.module.run("nu_fill_i32", y=counter, n=1, value=0)
    nonzero_input_dtype = ctx.session.plan.dtypes[node.inputs[0]]
    serial_nonzero_graph = None
    if ctx.session.int64_candidate:
        if (nonzero_input_dtype == F32
                and "nu_nonzero_scatter_serial_i64_candidate" in ctx.session.pool_graph_names):
            serial_nonzero_graph = "nu_nonzero_scatter_serial_i64_candidate"
        elif (nonzero_input_dtype == I32
                and "nu_nonzero_scatter_serial_i32_i64_candidate" in ctx.session.pool_graph_names):
            serial_nonzero_graph = "nu_nonzero_scatter_serial_i32_i64_candidate"
    serial_nonzero = serial_nonzero_graph is not None
    if not serial_nonzero and native_i64.available():
        # Native path: same (rank, capacity) layout the reader expects, so
        # `record_nonzero`/reshape at readback stays identical.
        out_native = ctx.alloc(node.output, (rank, total), I64)
        if native_i64.nonzero(ctx, node, x, out_native, counter, si):
            ctx.session.record_nonzero(node.output, counter, rank)
            return
    out = ctx.alloc(node.output, (rank, total), I64 if serial_nonzero else I32)
    kwargs = {"x": x, "out": out, "counter": counter, "total": total,
              "capacity": total, "rank": rank}
    kwargs.update({f"d{i}": v for i, v in enumerate(pad_to(si, 8))})
    if serial_nonzero:
        ctx.module.run(serial_nonzero_graph, **kwargs)
    else:
        ctx.module.run("nu_nonzero_scatter", **kwargs)
    ctx.session.record_nonzero(node.output, counter, rank)


def _lower_attention(node: GraphNode, ctx: _Ctx) -> None:
    q = ctx.device(node.inputs[0])
    k = ctx.device(node.inputs[1])
    v = ctx.device(node.inputs[2])
    sq = ctx.shape_of(node.inputs[0])
    so = ctx.infer_out(node, [sq])
    out = ctx.alloc(node.output, so, F32)
    heads = int(node.attrs["num_heads"])
    hidden = sq[-1]
    if hidden % heads:
        raise UnsupportedStepError(f"MHA hidden {hidden} not divisible by heads {heads}")
    ctx.module.run("nu_attention", q=q, k=k, v=v, y=out,
                   n_batch=product(sq[:-2]) if len(sq) > 2 else 1, seq=sq[-2],
                   hidden=hidden, heads=heads,
                   scale=1.0 / math.sqrt(hidden // heads))


def _lower_fill(node: GraphNode, ctx: _Ctx) -> None:
    shape_arg = ctx.const_arg(node, 0)
    if shape_arg is None:
        raise UnsupportedStepError("ConstantOfShape requires a constant shape")
    shape = tuple(int(v) for v in np.asarray(shape_arg).ravel())
    dtype = ctx.session.plan.dtypes[node.output]
    out = ctx.alloc(node.output, shape, dtype)
    value = 0.0
    if node.attrs.get("value") is not None:
        value = float(np.asarray(node.attrs["value"]).ravel()[0])
    if native_i64.fill_i64(ctx, node, out, shape, value, dtype):
        return
    kernel = {"f32": "nu_fill_f32", "i32": "nu_fill_i32", "i64": "nu_fill_i64"}[dtype]
    ctx.module.run(kernel, y=out, n=product(shape), value=value)


def _lower_range(node: GraphNode, ctx: _Ctx) -> None:
    dtype = ctx.session.plan.dtypes[node.output]
    if dtype in (I32, I64):
        start, _limit, delta, count, dtype = _integer_range_spec(node, ctx)
    else:
        values = [float(np.asarray(ctx.const_arg(node, i)).ravel()[0]) for i in range(3)]
        if values[2] == 0:
            raise UnsupportedStepError("Range with zero step")
        count = max(0, int(math.ceil((values[1] - values[0]) / values[2])))
        if count > _MAX_RANGE_ELEMENTS:
            raise UnsupportedStepError("Range output exceeds the supported kernel element count")
    out = ctx.alloc(node.output, (count,), dtype)
    if dtype == F32:
        ctx.module.run("nu_range_f32", y=out, n=count, start=values[0], delta=values[2])
    elif dtype == I32:
        ctx.module.run("nu_range_i32", y=out, n=count, start=start, delta=delta)
    else:
        ctx.module.run("nu_range_i64", y=out, n=count, start=start, delta=delta)


def _lower_cast(node: GraphNode, ctx: _Ctx) -> None:
    x = ctx.device(node.inputs[0])
    si = ctx.shape_of(node.inputs[0])
    src = ctx.session.plan.dtypes[node.inputs[0]]
    dst = ctx.session.plan.dtypes[node.output]
    out = ctx.alloc(node.output, si, dst)
    n = product(si)
    if src == dst and src == I64:
        # Same-dtype i64 "cast" is a copy; the pool copy graph needs the
        # candidate artifact, so use the native path when it is available.
        if native_i64.cast_i64(ctx, node, x, out, si, src, dst):
            return
    if src != dst and (src == I64 or dst == I64):
        # The pool's i64 copy/cast graphs need the candidate artifact; the native
        # conversion covers every admitted direction without it.
        if native_i64.cast_i64(ctx, node, x, out, si, src, dst):
            return
    if src == dst:
        kernel = {"f32": "nu_copy_f32", "i32": "nu_copy_i32", "i64": "nu_copy_i64"}[src]
        ctx.module.run(kernel, x=x, y=out, n=n)
        return
    ctx.module.run(f"nu_cast_{src}_{dst}", x=x, y=out, n=n)


LOWER: Dict[str, Any] = {
    "Relu": _lower_unary, "Sigmoid": _lower_unary, "Tanh": _lower_unary,
    "Gelu": _lower_unary, "Softplus": _lower_unary, "Abs": _lower_unary,
    "Sqrt": _lower_unary, "Neg": _lower_unary, "Erf": _lower_unary,
    "Exp": _lower_unary, "Log": _lower_unary, "Floor": _lower_unary,
    "Ceil": _lower_unary, "Sin": _lower_unary, "Cos": _lower_unary,
    "Reciprocal": _lower_unary, "Sign": _lower_unary, "LeakyRelu": _lower_unary,
    "Clip": _lower_unary, "PRelu": _lower_prelu,
    "Add": _lower_binary, "Sub": _lower_binary, "Mul": _lower_binary,
    "Div": _lower_binary, "Pow": _lower_binary, "Max": _lower_binary,
    "Min": _lower_binary, "Mod": _lower_binary, "Less": _lower_binary,
    "Greater": _lower_binary, "Equal": _lower_binary, "And": _lower_binary,
        "Or": _lower_logical, "Xor": _lower_logical, "Not": _lower_logical,
        "Sum": _lower_sum,
        "Where": _lower_where,
    "Conv": _lower_conv, "FusedConv": _lower_conv, "DmlFusedConv": _lower_conv,
    "ConvTranspose": _lower_conv_transpose,
    "MatMul": _lower_matmul, "FusedMatMul": _lower_matmul, "Gemm": _lower_gemm,
    "ReduceMean": _lower_reduce, "ReduceSum": _lower_reduce,
    "ReduceMax": _lower_reduce, "ReduceMin": _lower_reduce,
    "ReduceL2": _lower_reduce, "ArgMax": _lower_reduce,
    "InstanceNormalization": _lower_norm, "LayerNormalization": _lower_norm,
    "BatchNormalization": _lower_norm, "Softmax": _lower_norm, "LogSoftmax": _lower_norm,
    "Gather": _lower_gather, "GatherElements": _lower_gather,
    "Concat": _lower_concat, "Split": _lower_split, "Slice": _lower_slice,
    "Pad": _lower_pad, "Transpose": _lower_transpose, "Expand": _lower_expand,
    "Tile": _lower_tile, "SpaceToDepth": _lower_space_to_depth,
    "DepthToSpace": _lower_space_to_depth,
    "AveragePool": _lower_pool, "MaxPool": _lower_pool,
    "GlobalAveragePool": _lower_pool, "Resize": _lower_resize,
    "TopK": _lower_topk, "NonZero": _lower_nonzero,
    "MultiHeadAttention": _lower_attention, "ConstantOfShape": _lower_fill,
    "Range": _lower_range, "Cast": _lower_cast,
}


def _check_backend_dtype_support(plan: Plan, backend: str) -> None:
    """Reject runtime tensor dtypes omitted from a backend-qualified pool."""
    if backend != "vulkan":
        return
    device_i64 = sorted(
        name for name, dtype in plan.dtypes.items()
        if dtype == I64 and name not in plan.constants and name not in plan.host_int_values
    )
    if device_i64:
        raise UnsupportedONNXOperatorError(
            "Vulkan neural pool does not support dynamic INT64 tensors in this "
            f"profile; values={device_i64[:8]}. Use a backend with INT64 kernels "
            "or a model profile that keeps INT64 values in host shape metadata."
        )


def _read_pool_graph_names(tcm_path: Path) -> set:
    """Read the graph manifest so optional fusions never call a missing graph."""
    import zipfile

    try:
        with zipfile.ZipFile(tcm_path) as archive:
            content = archive.read("__content__").decode("utf-8", errors="replace")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise UnsupportedONNXOperatorError(
            f"cannot read universal pool graph manifest from {tcm_path}: {exc}"
        ) from exc
    return {
        line.split(":", 1)[1].strip()
        for line in content.splitlines()
        if line.startswith("cgraph:")
    }


def _validate_candidate_manifest_v2(candidate: dict, pool_path: Path) -> bool:
    """Validate source-qualified candidate compiler policy and target provenance."""
    try:
        import taichi as ti

        from .static_graph import (
            _configured_runtime_abi,
            _kernel_source_fingerprint,
            _sha256_file,
            _target_identity,
        )

        return (
            candidate.get("schema_version") == 2
            and candidate.get("backend") == "cpu"
            and candidate.get("runtime_abi") == _configured_runtime_abi()
            and candidate.get("target_identity") == _target_identity("cpu")
            and candidate.get("taichi_version") == ".".join(str(part) for part in ti.__version__)
            and candidate.get("kernel_sources_sha256") == _kernel_source_fingerprint()
            and candidate.get("tcm_sha256") == _sha256_file(pool_path)
            and candidate.get("compile_options") == {"fast_math": False}
        )
    except (OSError, TypeError, ValueError, ImportError):
        return False


class UniversalInferenceSession:
    """Drop-in ONNX inference session backed by the universal kernel pool.

    The constructor mirrors the archived universal runtime so existing callers
    keep working unchanged: ``model_path_or_bytes``, ``backend``, ``providers``,
    ``model_name``, ``weights_source`` and ``input_shapes``.
    """

    def __init__(
        self,
        model_path_or_bytes: Union[str, Path, bytes],
        backend: str = "auto",
        providers: Optional[Sequence[str]] = None,
        model_name: Optional[str] = None,
        weights_source: Optional[Union[str, Path, bytes, dict]] = None,
        input_shapes: Optional[Dict[str, Sequence[int]]] = None,
        pool_dir: Optional[Union[str, Path]] = None,
        ring_slots: int = 2,
        use_buffer_session: bool = True,
        use_rust_conv: bool = True,
    ):
        from taichi.aot_engine import (
            AOTEngine,
            engine as global_engine,
            get_backend_name,
        )

        if providers:
            backend = _resolve_provider_backend(providers, fallback=backend)
        resolved = str(backend).strip().lower()
        if resolved in ("auto", "default", ""):
            resolved = str(get_backend_name()).lower()
        self.backend = resolved
        self.model_name = model_name
        self.weights_source = weights_source
        self.input_shapes = dict(input_shapes) if input_shapes else None
        self.ring_slots = max(1, int(ring_slots))
        self.use_buffer_session = bool(use_buffer_session)
        #: Route admitted Conv shapes through the Rust im2col+GEMM path.
        self.use_rust_conv = bool(use_rust_conv)
        self._rust_conv_ready: Optional[bool] = None
        self._rust_conv_used = False

        current = str(global_engine.arch).lower()
        if current != self.backend:
            os.environ["AOT_ARCH"] = self.backend
            self.engine = AOTEngine(arch=self.backend)
        else:
            self.engine = global_engine._live() if hasattr(global_engine, "_live") else global_engine

        if isinstance(model_path_or_bytes, (str, Path)):
            path = Path(model_path_or_bytes).resolve()
            if not path.is_file():
                raise FileNotFoundError(f"Model not found: {path}")
            model_bytes = path.read_bytes()
        else:
            model_bytes = bytes(model_path_or_bytes)

        if self.input_shapes:
            from .compat import prepare_static_model

            model_bytes = prepare_static_model(model_bytes, self.input_shapes)
        self.model_bytes = model_bytes
        self.plan = Plan.from_model_bytes(model_bytes)
        _check_backend_dtype_support(self.plan, self.backend)

        base = Path(pool_dir) if pool_dir is not None else None
        pool_path = _find_pool_tcm(self.backend, base)
        if pool_path is None:
            raise FileNotFoundError(
                f"universal pool TCM for backend '{self.backend}' not found under "
                f"{base or os.environ.get('PIXEL_REFINE_NEURAL_POOL_DIR') or DEFAULT_POOL_DIR}; "
                "stage the C++ pipeline artifact as universal/<backend>/neural_<backend>.tcm "
                "and verify its cgraph manifest against kernels.KERNEL_NAMES"
            )
        self.pool_path = pool_path
        self.pool_graph_names = _read_pool_graph_names(pool_path)
        self.int64_candidate = False
        marker = pool_path.parent / "candidate_manifest.json"
        if marker.is_file():
            try:
                import json

                candidate = json.loads(marker.read_text(encoding="utf-8"))
                required = set(candidate.get("graphs", ()))
                if candidate.get("kind") in {
                    "neural_universal_int64_cpu_candidate_v17",
                    "neural_universal_int64_cpu_candidate_v18",
                }:
                    self.int64_candidate = (
                        self.backend == "cpu"
                        and _validate_candidate_manifest_v2(candidate, pool_path)
                        and bool(required)
                        and required.issubset(self.pool_graph_names)
                    )
                else:
                    self.int64_candidate = (
                        self.backend == "cpu"
                        and candidate.get("kind") in {
                        "neural_universal_int64_cpu_candidate_v1",
                        "neural_universal_int64_cpu_candidate_v2",
                        "neural_universal_int64_cpu_candidate_v3",
                        "neural_universal_int64_cpu_candidate_v4",
                        "neural_universal_int64_cpu_candidate_v5",
                        "neural_universal_int64_cpu_candidate_v6",
                        "neural_universal_int64_cpu_candidate_v7",
                        "neural_universal_int64_cpu_candidate_v8",
                        "neural_universal_int64_cpu_candidate_v9",
                        "neural_universal_int64_cpu_candidate_v10",
                        "neural_universal_int64_cpu_candidate_v11",
                        "neural_universal_int64_cpu_candidate_v12",
                        "neural_universal_int64_cpu_candidate_v13",
                        "neural_universal_int64_cpu_candidate_v14",
                        "neural_universal_int64_cpu_candidate_v15",
                        }
                        and bool(required)
                        and required.issubset(self.pool_graph_names)
                    )
            except (OSError, ValueError, TypeError):
                self.int64_candidate = False
        # Archived spelling of the loaded pool artifact.
        self.tcm_path = pool_path
        self.module = self.engine.load(str(pool_path))
        self.dummy = self.engine.allocate((1,), dtype=np.float32, is_vector=False)
        self._live: List[Any] = []
        self._run_buffer_cache: Dict[Tuple[str, Shape, str], Any] = {}
        self._run_signature: Optional[Tuple[Any, ...]] = None
        self._run_needs_sync = False
        self._nz: Dict[str, Tuple[Any, int]] = {}
        #: Buffers currently owned by the session, keyed by tensor name.
        self.buffers: Dict[str, Any] = {}
        #: Tagged scratch/ring ownership for this session. Steady-state runs
        #: already reuse cached slots, so the session adds cross-signature reuse,
        #: ring slots for borrowed outputs, and one auditable owner for cleanup.
        self.buffer_session = self._open_buffer_session()
        #: Names whose buffers must survive a run (inputs, borrowed outputs).
        self._kept_buffers: set = set()

    # ------------------------------------------------------------- helpers

    def _open_buffer_session(self):
        """Create the tagged scratch/ring owner for this session.

        ``BufferSession`` is the venv's native ownership facade. It is optional:
        when the installed ``taichi`` build does not expose it, the session keeps
        its previous engine-only allocation path and reports that fact.
        """
        if not self.use_buffer_session:
            self.buffer_session_available = False
            return None
        try:
            from taichi.buffer_session import BufferSession
        except ImportError:
            self.buffer_session_available = False
            return None
        session = BufferSession(
            engine=self.engine, sync_on_exit=False,
            tag=f"neural_universal_{self.backend}", ring_slots=self.ring_slots,
        )
        self.buffer_session_available = True
        return session

    def acquire_slot(self, name: str, shape: Shape, dtype: str):
        """Allocate a slot owned by the buffer session.

        Allocation deliberately goes through ``engine.allocate`` — the same call
        the runtime used before — and the session then *adopts* the buffer. That
        keeps memory placement and host accessibility byte-identical to the
        measured baseline while giving the session one owner for lifecycle.
        """
        np_dtype = NUMPY_DTYPE[dtype]
        flat_shape = (max(1, product(shape)),)
        buffer = self.engine.allocate(flat_shape, dtype=np_dtype, is_vector=False)
        if self.buffer_session is not None:
            try:
                self.buffer_session.own(buffer)
            except Exception:
                pass
        return buffer

    def acquire_output_slot(self, name: str, shape: Shape, dtype: str):
        """Allocate an output that may outlive the call (borrowed output)."""
        np_dtype = NUMPY_DTYPE[dtype]
        flat_shape = (max(1, product(shape)),)
        if self.buffer_session is not None:
            return self.buffer_session.view(
                flat_shape, dtype=np_dtype, tag=f"output::{name}"
            )
        return self.engine.allocate(flat_shape, dtype=np_dtype, is_vector=False)

    def download(self, name: str, buffer):
        """Host readback into the session's host scratch slot."""
        if self.buffer_session is not None:
            host = self.buffer_session.acquire_host(
                buffer.shape, dtype=buffer.dtype, tag=f"host::{name}"
            )
            native_read = getattr(buffer, "to_numpy", None)
            if native_read is not None:
                return native_read(out=host)
        return buffer.to_numpy()

    def upload(self, name: str, array: np.ndarray):
        contiguous = np.ascontiguousarray(array)
        key = (name, tuple(contiguous.shape), np.dtype(contiguous.dtype).str)
        buf = self._run_buffer_cache.get(key)
        if buf is not None and getattr(buf, "handle", None) is not None:
            self.engine.write_into(buf, contiguous, synchronize=False)
            return buf
        if self.buffer_session is not None:
            # Identity-cached upload: identical host data is not re-uploaded,
            # and mutating the same array updates the resident copy in place.
            buf, _cached = self.buffer_session.upload_if_needed(
                contiguous, tag=f"upload::{name}"
            )
        else:
            buf = self.engine.upload(contiguous, is_vector=False)
        self._run_buffer_cache[key] = buf
        self._live.append(buf)
        self._kept_buffers.add(name)
        return buf

    def alloc_slot(self, name: str, shape: Shape, dtype: str, ctx: _Ctx, *, borrowed: bool = False):
        np_dtype = NUMPY_DTYPE[dtype]
        key = (name, (max(1, product(shape)),), np.dtype(np_dtype).str)
        buf = self._run_buffer_cache.get(key)
        if buf is None or getattr(buf, "handle", None) is None:
            if borrowed:
                buf = self.acquire_output_slot(name, shape, dtype)
                self._kept_buffers.add(name)
            else:
                buf = self.acquire_slot(name, shape, dtype)
            self._run_buffer_cache[key] = buf
            self._live.append(buf)
        ctx.buffers[name] = buf
        ctx.shapes[name] = tuple(shape)
        return buf

    def record_nonzero(self, name: str, counter, rank: int) -> None:
        self._nz[name] = (counter, rank)

    def _release_run_buffers(self, *, synchronize: bool = False) -> None:
        """Retire cached invocation buffers when the input signature changes."""
        if synchronize and self._run_signature is not None:
            self.engine.sync()
        self._run_needs_sync = False
        previous = self._live
        self._live = []
        self.buffers = {}
        self._run_buffer_cache.clear()
        self._run_signature = None
        self._kept_buffers = set()
        session = getattr(self, "buffer_session", None)
        if session is not None:
            # The buffer session owns every slot it handed out; releasing them
            # through it keeps one owner and avoids double-free on destroy().
            try:
                session.release_all_except()
                return
            except Exception:
                pass
        for buffer in previous:
            try:
                buffer.destroy()
            except Exception:
                pass

    # ---------------------------------------------------------------- run

    def run(
        self,
        output_names: Optional[Sequence[str]] = None,
        input_feed: Optional[Dict[str, Any]] = None,
        
        borrowed_outputs: bool = False,
        step_limit: Optional[int] = None,
        step_callback: Optional[Any] = None,
    ) -> List[Any]:
        """Execute the model.

        The signature matches the archived universal runtime so existing callers
        keep working: ``output_names``, ``input_feed``, ``_resident_output``,
        ``borrowed_outputs``, ``step_limit`` and ``step_callback``.

        ``borrowed_outputs`` returns device buffers that stay valid until the
        next call to :meth:`run`; ``step_limit`` stops after N graph steps and
        ``step_callback`` is invoked as ``callback(step_index, step)``.
        """
        plan = self.plan
        _resident_output = _resolve_output(input_feed)
        input_feed = dict(input_feed or {})
        if set(input_feed) != set(plan.input_names):
            alt = [f"input_{i}" for i in range(len(plan.input_names))]
            if set(input_feed) == set(alt):
                input_feed = {plan.input_names[i]: input_feed[alt[i]] for i in range(len(alt))}
            else:
                raise ValueError(
                    f"expected inputs {sorted(plan.input_names)}, got {sorted(input_feed)}"
                )

        requested = list(output_names) if output_names else list(plan.output_names)
        fusion_plan = build_fusion_plan(plan, set(requested), self.pool_graph_names)

        input_arrays: Dict[str, np.ndarray] = {}
        for name in plan.input_names:
            value = input_feed[name]
            if hasattr(value, "detach"):
                array = value.detach().cpu().numpy()
            elif hasattr(value, "to_numpy") and not isinstance(value, np.ndarray):
                array = value.to_numpy()
            else:
                array = np.asarray(value)
            if array.ndim != plan.input_ranks[name]:
                raise ValueError(
                    f"input {name} rank {array.ndim} != model rank {plan.input_ranks[name]}"
                )
            array = np.ascontiguousarray(array.astype(NUMPY_DTYPE[plan.dtypes[name]], copy=False))
            input_arrays[name] = array

        signature = tuple(
            (name, tuple(array.shape), np.dtype(array.dtype).str)
            for name, array in input_arrays.items()
        )
        if self._run_signature == signature:
            # The previous invocation may have returned borrowed output buffers.
            # Synchronize once, then safely overwrite/reuse buffers in this session.
            if self._run_needs_sync:
                self.engine.sync()
                self._run_needs_sync = False
            self.buffers = {}
        else:
            self._release_run_buffers(synchronize=self._run_needs_sync)
            self._run_signature = signature

        ctx = _Ctx(self)
        ctx.conv_activation_fusions = fusion_plan.conv_activation
        ctx.fused_nodes = set(fusion_plan.conv_activation_skipped)
        self._nz.clear()
        for name, array in input_arrays.items():
            ctx.buffers[name] = self.upload(name, array.reshape(-1))
            ctx.shapes[name] = tuple(int(d) for d in array.shape)

        for step_index, node in enumerate(plan.nodes):
            if step_limit is not None and step_index >= step_limit:
                break
            if step_callback is not None:
                step_callback(step_index, node)
            if node.index in ctx.fused_nodes:
                continue
            if node.op == "Constant":
                continue
            if node.outputs[0] in plan.host_int_values:
                try:
                    host_value = np.asarray(_host_eval(node, ctx))
                except Exception as exc:  # noqa: BLE001
                    input_shapes = []
                    for name in node.inputs:
                        if not name:
                            input_shapes.append(None)
                        elif name in ctx.host:
                            input_shapes.append(tuple(ctx.host[name].shape))
                        elif name in plan.constants:
                            input_shapes.append(tuple(plan.constants[name].shape))
                        else:
                            input_shapes.append(ctx.shapes.get(name))
                    raise UnsupportedStepError(
                        f"host metadata node {node.index} {node.op} "
                        f"name={node.name!r} input_shapes={input_shapes}: {exc}"
                    ) from exc
                if node.output not in ctx.host:
                    ctx.host[node.output] = (
                        np.ascontiguousarray(host_value)
                        if host_value.ndim > 0
                        else host_value
                    )
                continue
            if node.index in plan.alias_nodes:
                source = plan.alias_nodes[node.index]
                ctx.buffers[node.output] = ctx.device(source)
                ctx.shapes[node.output] = _alias_target(node, ctx, ctx.shape_of(source))
                continue
            dispatched = False
            for dispatch in fusion_plan.dispatches.get(node.index, ()):
                if run_fused_dispatch(dispatch, ctx):
                    ctx.fused_nodes.update(dispatch.fused_nodes)
                    dispatched = True
                    break
            if dispatched:
                continue
            lowering = LOWER.get(node.op)
            if lowering is None:
                raise UnsupportedStepError(
                    f"operator {node.op} is registered but has no device lowering"
                )
            try:
                lowering(node, ctx)
            except UnsupportedStepError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise type(exc)(
                    f"{exc} [node {node.index} {node.op} name={node.name!r} "
                    f"inputs={node.inputs} in_shapes="
                    f"{[ctx.shapes.get(n) or (tuple(np.asarray(ctx.value(n)).shape) if ctx.has_value(n) else None) for n in node.inputs]}]"
                ) from exc

        results: List[Any] = []
        readbacks = 0
        for name in requested:
            if name in ctx.host:
                results.append(ctx.host[name])
            elif name in ctx.buffers:
                if _resident_output or borrowed_outputs:
                    results.append(ctx.buffers[name])
                    continue
                shape = ctx.shapes[name]
                array = ctx.buffers[name].to_numpy()
                readbacks += 1
                if name in self._nz:
                    counter, rank = self._nz[name]
                    count = int(np.asarray(counter.to_numpy()).ravel()[0])
                    results.append(array.reshape(rank, -1)[:, :count].astype(np.int64))
                else:
                    results.append(array.reshape(shape))
            elif name in plan.constants:
                results.append(plan.constants[name])
            else:
                raise UnsupportedStepError(f"output {name} was never produced")
        # Buffers stay owned by the session so borrowed outputs remain valid
        # until the next run.
        self.buffers = dict(ctx.buffers)
        self._run_needs_sync = bool(ctx.buffers) and readbacks == 0
        return results

    def get_inputs(self):
        from types import SimpleNamespace

        return [SimpleNamespace(name=name, shape=plan_shape(self.plan, name))
                for name in self.plan.input_names]

    def get_outputs(self):
        from types import SimpleNamespace

        return [SimpleNamespace(name=name, shape=plan_shape(self.plan, name))
                for name in self.plan.output_names]

    def get_providers(self) -> List[str]:
        return [f"TaichiUniversal_{self.backend.upper()}ExecutionProvider"]

    # ------------------------------------------------------------ cleanup

    def close(self) -> None:
        self._release_run_buffers(synchronize=self._run_needs_sync)
        try:
            self.dummy.destroy()
        except Exception:
            pass
        session = getattr(self, "buffer_session", None)
        if session is not None:
            try:
                session.close()
            except Exception:
                pass
            self.buffer_session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


def plan_shape(plan: Plan, name: str) -> Tuple[int, ...]:
    hint = plan.shapes_hint.get(name) if hasattr(plan, "shapes_hint") else None
    if hint is not None:
        return tuple(hint)
    if name in plan.constants:
        return tuple(int(d) for d in plan.constants[name].shape)
    return ()


def _alias_target(node: GraphNode, ctx: _Ctx, source_shape: Shape) -> Shape:
    if node.op == "Identity":
        return source_shape
    if node.op == "Reshape":
        target = [int(v) for v in np.asarray(ctx.const_arg(node, 1)).ravel()]
        allowzero = int(node.attrs.get("allowzero", 0))
        resolved: List[int] = []
        wildcard = -1
        for index, value in enumerate(target):
            if value == 0 and not allowzero:
                resolved.append(source_shape[index] if index < len(source_shape) else 1)
            elif value == -1:
                wildcard = index
                resolved.append(1)
            else:
                resolved.append(value)
        if wildcard >= 0:
            known = int(np.prod(resolved, dtype=np.int64))
            resolved[wildcard] = product(source_shape) // known if known else 0
        return tuple(resolved)
    return shapeinfer.infer(node.op, node.attrs, [source_shape], ctx.const_args(node),
                            [ctx.session.plan.dtypes.get(n, F32) for n in node.inputs])


def _resolve_provider_backend(providers: Sequence[str], fallback: str = "auto") -> str:
    for provider in providers:
        text = str(provider).lower()
        for name in ("cuda", "vulkan", "opengl", "cpu"):
            if name in text:
                return name
    return fallback


def _find_pool_tcm(backend: str, base_dir: Optional[Path] = None) -> Optional[Path]:
    if base_dir is None:
        override = os.environ.get("PIXEL_REFINE_NEURAL_POOL_DIR")
        base_dir = Path(override) if override else DEFAULT_POOL_DIR
    base_dir = Path(base_dir)
    subdir = BACKEND_SUBDIRS.get(backend, backend)
    filename = f"neural_{backend}.tcm"
    candidates = (
        base_dir / filename,
        base_dir / "universal" / subdir / filename,
        base_dir / subdir / filename,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def find_universal_tcm(
    backend: str,
    base_dir: Path = DEFAULT_AOT_NEURAL_DIR,
) -> Optional[Path]:
    """Search for the pre-compiled universal operator pool TCM.

    Kept with the archived name and signature so callers written against the
    backup implementation keep working. The ``PIXEL_REFINE_NEURAL_POOL_DIR``
    override applies when no explicit directory is requested.
    """
    directory = Path(base_dir)
    if directory == DEFAULT_AOT_NEURAL_DIR:
        override = os.environ.get("PIXEL_REFINE_NEURAL_POOL_DIR")
        if override:
            directory = Path(override)
    return _find_pool_tcm(backend, directory)


#: Archived session class name.
UniversalSession = UniversalInferenceSession
