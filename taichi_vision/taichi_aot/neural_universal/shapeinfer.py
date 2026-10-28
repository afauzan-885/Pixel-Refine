"""Runtime shape inference for the admitted operator set.

Shapes are resolved per ``run()`` so a single compiled artifact serves every
input size. Integer subgraphs that only describe shapes are evaluated by
:mod:`runtime` first; this module receives those values as ``int_args``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

from .errors import UnsupportedONNXOperatorError

Shape = Tuple[int, ...]


def _as_tuple(values: Sequence[int]) -> Shape:
    return tuple(int(v) for v in values)


def _axis(axis: int, rank: int) -> int:
    return axis + rank if axis < 0 else axis


def _broadcast(a: Shape, b: Shape) -> Shape:
    rank = max(len(a), len(b))
    pa = (1,) * (rank - len(a)) + tuple(a)
    pb = (1,) * (rank - len(b)) + tuple(b)
    out = []
    for da, db in zip(pa, pb):
        if da == db or db == 1:
            out.append(da)
        elif da == 1:
            out.append(db)
        else:
            raise UnsupportedONNXOperatorError(f"cannot broadcast {a} with {b}")
    return tuple(out)


def _pair(values, default):
    if values is None:
        return list(default)
    return [int(v) for v in values]


def _conv_out(size: int, k: int, s: int, p0: int, p1: int, d: int) -> int:
    return (size + p0 + p1 - d * (k - 1) - 1) // s + 1


def _pool_out(size: int, k: int, s: int, p0: int, p1: int, d: int, ceil: int) -> int:
    numerator = size + p0 + p1 - d * (k - 1) - 1
    if ceil:
        return -(-numerator // s) + 1
    return numerator // s + 1


def conv_pads(input_hw: Sequence[int], kernel_hw: Sequence[int], attrs: Dict[str, Any]) -> List[int]:
    """Resolve ONNX Conv pads in ``[top,left,bottom,right]`` order."""
    strides = _pair(attrs.get("strides"), (1, 1))
    dilations = _pair(attrs.get("dilations"), (1, 1))
    auto_pad = str(attrs.get("auto_pad", "NOTSET")).upper()
    if auto_pad == "VALID":
        return [0, 0, 0, 0]
    if auto_pad in ("SAME_UPPER", "SAME_LOWER"):
        resolved = []
        for size, kernel, stride, dilation in zip(input_hw, kernel_hw, strides, dilations):
            out_size = (int(size) + stride - 1) // stride
            effective_kernel = dilation * (int(kernel) - 1) + 1
            total = max((out_size - 1) * stride + effective_kernel - int(size), 0)
            before = (total + 1) // 2 if auto_pad == "SAME_LOWER" else total // 2
            resolved.append((before, total - before))
        return [resolved[0][0], resolved[1][0], resolved[0][1], resolved[1][1]]
    pads = _pair(attrs.get("pads"), (0, 0, 0, 0))
    if len(pads) == 2:
        pads = [pads[0], pads[1], pads[0], pads[1]]
    if len(pads) != 4:
        raise UnsupportedONNXOperatorError(f"Conv expects 2 or 4 pad values, got {pads}")
    return pads


def infer(
    op: str,
    attrs: Dict[str, Any],
    in_shapes: Sequence[Optional[Shape]],
    int_args: Dict[int, Optional[np.ndarray]],
    input_dtypes: Sequence[str],
) -> Shape:
    """Return the concrete output shape of one node."""

    first = in_shapes[0] if in_shapes else None
    if first is None:
        raise UnsupportedONNXOperatorError(f"{op}: first input shape is unknown")

    if op in ("Relu", "Sigmoid", "Tanh", "Gelu", "Softplus", "Abs", "Sqrt", "Neg",
              "Erf", "Exp", "Log", "Floor", "Ceil", "Sin", "Cos", "Reciprocal",
              "Sign", "LeakyRelu", "Clip", "Identity", "Softmax", "LogSoftmax",
              "InstanceNormalization", "LayerNormalization", "BatchNormalization",
              "Softmax", "Sin", "Cos", "Not", "MultiHeadAttention", "FusedMatMul"):
        return first

    if op == "Cast":
        return first

    if op in ("Add", "Sub", "Mul", "Div", "Pow", "Mod", "Less", "Greater", "Equal",
              "And", "Or", "Xor", "PRelu", "Max", "Min"):
        out = first
        for other in in_shapes[1:]:
            if other is None:
                raise UnsupportedONNXOperatorError(f"{op}: unknown operand shape")
            out = _broadcast(out, other)
        return out

    if op == "Sum":
        out = first
        for other in in_shapes[1:]:
            out = _broadcast(out, other or first)
        return out

    if op == "Where":
        out = in_shapes[0] or first
        for other in in_shapes[1:]:
            if other is not None:
                out = _broadcast(out, other)
        return out

    if op in ("Conv", "FusedConv", "DmlFusedConv"):
        weight = in_shapes[1]
        if weight is None:
            raise UnsupportedONNXOperatorError(f"{op}: weight shape is unknown")
        n, c, h, w = first[0], first[1], first[2], first[3]
        co = weight[0]
        kh, kw = weight[2], weight[3]
        pads = conv_pads((h, w), (kh, kw), attrs)
        strides = _pair(attrs.get("strides"), (1, 1))
        dilations = _pair(attrs.get("dilations"), (1, 1))
        oh = _conv_out(h, kh, strides[0], pads[0], pads[2], dilations[0])
        ow = _conv_out(w, kw, strides[1], pads[1], pads[3], dilations[1])
        return (n, co, oh, ow)

    if op == "ConvTranspose":
        weight = in_shapes[1]
        if weight is None:
            raise UnsupportedONNXOperatorError(f"{op}: weight shape is unknown")
        n, c, h, w = first[0], first[1], first[2], first[3]
        co = weight[1] * int(attrs.get("group", 1))
        kh, kw = weight[2], weight[3]
        pads = _pair(attrs.get("pads"), (0, 0, 0, 0))
        strides = _pair(attrs.get("strides"), (1, 1))
        dilations = _pair(attrs.get("dilations"), (1, 1))
        output_padding = _pair(attrs.get("output_padding"), (0, 0))
        if len(pads) == 2:
            pads = [pads[0], pads[1], pads[0], pads[1]]
        oh = (h - 1) * strides[0] - pads[0] - pads[2] + dilations[0] * (kh - 1) + 1 + output_padding[0]
        ow = (w - 1) * strides[1] - pads[1] - pads[3] + dilations[1] * (kw - 1) + 1 + output_padding[1]
        return (n, co, oh, ow)

    if op in ("MatMul", "FusedMatMul"):
        b_shape = in_shapes[1]
        if b_shape is None:
            raise UnsupportedONNXOperatorError(f"{op}: right operand shape unknown")
        a, b = first, b_shape
        if len(a) == 2 and len(b) == 2:
            return (a[0], b[1])
        batch_a, batch_b = a[:-2], b[:-2]
        return _broadcast(batch_a, batch_b) + (a[-2], b[-1])

    if op == "Gemm":
        m = first[0] if int(attrs.get("transA", 0)) == 0 else first[1]
        b_shape = in_shapes[1]
        if b_shape is None:
            raise UnsupportedONNXOperatorError("Gemm: right operand shape unknown")
        n = b_shape[1] if int(attrs.get("transB", 0)) == 0 else b_shape[0]
        return (m, n)

    if op == "AveragePool" or op == "MaxPool":
        kernel = attrs.get("kernel_shape")
        if not kernel:
            raise UnsupportedONNXOperatorError(f"{op}: kernel_shape is required")
        n, c, h, w = first[0], first[1], first[2], first[3]
        strides = _pair(attrs.get("strides"), [1] * len(kernel))
        dilations = _pair(attrs.get("dilations"), [1] * len(kernel))
        pads = _pair(attrs.get("pads"), [0] * (2 * len(kernel)))
        ceil = int(attrs.get("ceil_mode", 0))
        if len(pads) == len(kernel):
            pads = pads + pads
        oh = _pool_out(h, int(kernel[0]), strides[0], pads[0], pads[2],
                       dilations[0], ceil)
        ow = _pool_out(w, int(kernel[1]), strides[1], pads[1], pads[3],
                       dilations[1], ceil)
        return (n, c, oh, ow)

    if op == "GlobalAveragePool":
        return (first[0], first[1], 1, 1)

    if op in ("ReduceMean", "ReduceSum", "ReduceMax", "ReduceMin", "ReduceL2",
              "ArgMax"):
        axes = attrs.get("axes")
        if axes is None and int_args.get(1) is not None:
            axes = [int(v) for v in np.asarray(int_args[1]).ravel()]
        rank = len(first)
        if axes is None or len(axes) == 0:
            axes = list(range(rank))
        axes = [_axis(int(a), rank) for a in axes]
        keep = int(attrs.get("keepdims", 1))
        if op == "ArgMax" and not keep:
            return tuple(d for i, d in enumerate(first) if i not in axes)
        if keep:
            return tuple(1 if i in axes else d for i, d in enumerate(first))
        return tuple(d for i, d in enumerate(first) if i not in axes)

    if op == "Gather":
        axis = _axis(int(attrs.get("axis", 0)), len(first))
        indices = in_shapes[1]
        if indices is None:
            raise UnsupportedONNXOperatorError("Gather: indices shape unknown")
        return first[:axis] + tuple(indices) + first[axis + 1:]

    if op == "GatherElements":
        indices = in_shapes[1]
        if indices is None:
            raise UnsupportedONNXOperatorError("GatherElements: indices shape unknown")
        return tuple(indices)

    if op == "Concat":
        axis = _axis(int(attrs["axis"]), len(first))
        total = 0
        for shape in in_shapes:
            if shape is None:
                raise UnsupportedONNXOperatorError("Concat: unknown input shape")
            total += shape[axis]
        out = list(first)
        out[axis] = total
        return tuple(out)

    if op == "Split":
        axis = _axis(int(attrs.get("axis", 0)), len(first))
        split = attrs.get("split")
        if split is None and int_args.get(1) is not None:
            split = [int(v) for v in np.asarray(int_args[1]).ravel()]
        if split is None:
            count = int(attrs.get("num_outputs", 2))
            base = first[axis] // count
            return tuple(base for _ in range(count))
        return tuple(int(v) for v in split)

    if op == "Slice":
        starts = int_args.get(1)
        ends = int_args.get(2)
        axes = int_args.get(3)
        steps = int_args.get(4)
        if starts is None or ends is None:
            raise UnsupportedONNXOperatorError("Slice requires constant starts/ends")
        starts = [int(v) for v in np.asarray(starts).ravel()]
        ends = [int(v) for v in np.asarray(ends).ravel()]
        axes = [int(v) for v in np.asarray(axes).ravel()] if axes is not None else list(range(len(starts)))
        steps = [int(v) for v in np.asarray(steps).ravel()] if steps is not None else [1] * len(starts)
        out = list(first)
        for start, end, axis, step in zip(starts, ends, axes, steps):
            axis = _axis(axis, len(first))
            dim = first[axis]
            if step == 0:
                raise UnsupportedONNXOperatorError("Slice step must be non-zero")
            if start < 0:
                start += dim
            if end < 0:
                end += dim
            if step > 0:
                start = max(0, min(start, dim))
                end = max(0, min(end, dim))
                out[axis] = max(0, -(-(end - start) // step))
            else:
                start = max(-1, min(start, dim - 1))
                end = max(-1, end)
                out[axis] = max(0, -(-(start - end) // (-step)))
        return tuple(out)

    if op == "Pad":
        pads = int_args.get(1)
        if pads is None:
            raise UnsupportedONNXOperatorError("Pad requires constant pads")
        pads = [int(v) for v in np.asarray(pads).ravel()]
        rank = len(first)
        half = len(pads) // 2
        return tuple(first[i] + pads[i] + pads[i + half] for i in range(rank))

    if op == "Transpose":
        perm = attrs.get("perm")
        if perm is None:
            perm = list(range(len(first)))[::-1]
        return tuple(first[int(p)] for p in perm)

    if op in ("Expand", "Tile"):
        target = int_args.get(1)
        if target is None:
            raise UnsupportedONNXOperatorError(f"{op} requires constant repeats/shape")
        values = [int(v) for v in np.asarray(target).ravel()]
        if op == "Expand":
            return _broadcast(first, tuple(values))
        rank = len(values)
        padded = (1,) * (rank - len(first)) + tuple(first)
        return tuple(padded[i] * values[i] for i in range(rank))

    if op == "SpaceToDepth":
        block = int(attrs["blocksize"])
        n, c, h, w = first[0], first[1], first[2], first[3]
        return (n, c * block * block, h // block, w // block)

    if op == "DepthToSpace":
        block = int(attrs["blocksize"])
        n, c, h, w = first[0], first[1], first[2], first[3]
        return (n, c // (block * block), h * block, w * block)

    if op == "Resize":
        sizes = int_args.get(3)
        if sizes is not None:
            return tuple(int(v) for v in np.asarray(sizes).ravel())
        scales = int_args.get(2)
        if scales is None:
            raw = attrs.get("scales")
            scales = raw
        if scales is None:
            raise UnsupportedONNXOperatorError("Resize requires scales or sizes")
        scales = [float(v) for v in np.asarray(scales).ravel()]
        return tuple(int(np.floor(first[i] * scales[i])) for i in range(len(first)))

    if op == "Reshape":
        target = int_args.get(1)
        if target is None:
            raise UnsupportedONNXOperatorError("Reshape requires a constant target shape")
        values = [int(v) for v in np.asarray(target).ravel()]
        total = int(np.prod(first, dtype=np.int64))
        allowzero = int(attrs.get("allowzero", 0))
        out = []
        wildcard = -1
        for index, value in enumerate(values):
            if value == 0 and allowzero == 0:
                out.append(first[index] if index < len(first) else 1)
            elif value == -1:
                wildcard = index
                out.append(1)
            else:
                out.append(value)
        if wildcard >= 0:
            known = int(np.prod(out, dtype=np.int64))
            out[wildcard] = total // known if known else 0
        return tuple(out)

    if op == "Flatten":
        axis = _axis(int(attrs.get("axis", 1)), len(first))
        head = int(np.prod(first[:axis], dtype=np.int64)) if axis else 1
        tail = int(np.prod(first[axis:], dtype=np.int64)) if axis < len(first) else 1
        return (head, tail)

    if op == "Squeeze":
        axes = attrs.get("axes")
        if axes is None and int_args.get(1) is not None:
            axes = [int(v) for v in np.asarray(int_args[1]).ravel()]
        if axes is None:
            return tuple(d for d in first if d != 1)
        axes = {
            _axis(int(a), len(first)) for a in axes
        }
        return tuple(d for i, d in enumerate(first) if i not in axes)

    if op == "Unsqueeze":
        axes = attrs.get("axes")
        if axes is None and int_args.get(1) is not None:
            axes = [int(v) for v in np.asarray(int_args[1]).ravel()]
        if axes is None:
            raise UnsupportedONNXOperatorError("Unsqueeze requires axes")
        out_rank = len(first) + len(axes)
        normalized = sorted(_axis(int(a), out_rank) for a in axes)
        out = list(first)
        for position in normalized:
            out.insert(position, 1)
        return tuple(out)

    if op == "TopK":
        k_values = int_args.get(1)
        if k_values is None:
            raise UnsupportedONNXOperatorError("TopK requires a constant k")
        k = int(np.asarray(k_values).ravel()[0])
        axis = _axis(int(attrs.get("axis", -1)), len(first))
        out = list(first)
        out[axis] = k
        return tuple(out)

    if op == "NonZero":
        return (len(first), int(np.prod(first, dtype=np.int64)))

    if op in ("Shape", "ConstantOfShape", "Range", "Constant"):
        raise UnsupportedONNXOperatorError(
            f"{op} must be resolved as an integer value, not a device tensor"
        )

    raise UnsupportedONNXOperatorError(f"no shape inference rule for {op}")
