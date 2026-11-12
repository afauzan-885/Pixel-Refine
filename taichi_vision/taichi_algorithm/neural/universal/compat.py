"""Backward-compatible helpers carried over from the archived universal runtime.

The archived implementation (``.backups/neural_universal_source``) exposed three
module-level helpers that downstream code and tools already call. They are kept
here with identical names and semantics so the public API survives the move:

* :func:`calc_4d_strides`
* :func:`collapse_broadcast_shapes`
* :func:`prepare_static_model`

The private alias ``_calc_4d_strides`` is also provided because the archived
module used that name internally.
"""

from __future__ import annotations

import os
from typing import Dict, Optional, Sequence, Tuple

Shape = Tuple[int, ...]


def calc_4d_strides(shape: Sequence[int]) -> Tuple[int, int, int, int]:
    """Strides for a 4D broadcast where singleton axes get stride 0."""
    s = tuple(int(v) for v in shape)
    if len(s) != 4:
        raise ValueError(f"expected a rank-4 shape, got {tuple(shape)}")
    sw = 1 if s[3] > 1 else 0
    sh = s[3] if s[2] > 1 else 0
    sc = (s[2] * s[3]) if s[1] > 1 else 0
    sn = (s[1] * s[2] * s[3]) if s[0] > 1 else 0
    return sn, sc, sh, sw


#: Archived private spelling kept for source compatibility.
_calc_4d_strides = calc_4d_strides


def collapse_broadcast_shapes(
    shape_a: Sequence[int], shape_b: Sequence[int]
) -> Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[int, ...]]:
    """Align two broadcastable shapes and coalesce adjacent dimensions.

    Leading ones are added so both operands share the output rank, then
    neighbouring axes merge whenever both operands behave identically across
    them. The result is ``(collapsed_a, collapsed_b, collapsed_out)``, each
    padded on the left to rank 4.

    This is the exact algorithm the archived runtime used to shrink a
    broadcast into a cheaper kernel dispatch.
    """
    max_rank = max(len(shape_a), len(shape_b))
    if max_rank == 0:
        return (1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 1)
    sa = [1] * (max_rank - len(shape_a)) + [int(v) for v in shape_a]
    sb = [1] * (max_rank - len(shape_b)) + [int(v) for v in shape_b]
    so = [max(a, b) for a, b in zip(sa, sb)]

    ca, cb, co = [], [], []
    curr_a, curr_b, curr_o = sa[-1], sb[-1], so[-1]

    for i in range(max_rank - 2, -1, -1):
        a_i, b_i, o_i = sa[i], sb[i], so[i]
        can_merge = False
        if a_i == 1 and b_i == 1:
            can_merge = True
        elif a_i == o_i and b_i == o_i and curr_a == curr_o and curr_b == curr_o:
            can_merge = True
        elif a_i == 1 and b_i == o_i and curr_a == 1 and curr_b == curr_o:
            can_merge = True
        elif b_i == 1 and a_i == o_i and curr_b == 1 and curr_a == curr_o:
            can_merge = True

        if can_merge:
            curr_a *= a_i
            curr_b *= b_i
            curr_o *= o_i
        else:
            ca.append(curr_a)
            cb.append(curr_b)
            co.append(curr_o)
            curr_a, curr_b, curr_o = a_i, b_i, o_i

    ca.append(curr_a)
    cb.append(curr_b)
    co.append(curr_o)
    ca, cb, co = ca[::-1], cb[::-1], co[::-1]

    while len(co) < 4:
        ca.insert(0, 1)
        cb.insert(0, 1)
        co.insert(0, 1)

    return tuple(ca), tuple(cb), tuple(co)


def prepare_static_model(
    model_bytes: bytes,
    input_shapes: Optional[Dict[str, Sequence[int]]] = None,
) -> bytes:
    """Bind static input shapes and constant-fold metadata nodes.

    ``Shape``/``Range``/``ConstantOfShape`` chains only become foldable once the
    input extents are known. When ``input_shapes`` is supplied this rewrites the
    model through onnxruntime's extended optimizer so those chains collapse into
    constants at plan time.

    Returns the original bytes unchanged when no shape is given or when the
    optimizer cannot run; the caller must treat the result as opaque bytes.
    """
    if not input_shapes:
        return model_bytes

    import onnx
    import onnxruntime as ort
    import tempfile

    model = onnx.load_model_from_string(model_bytes)
    has_dynamic = False
    for inp in model.graph.input:
        if inp.name not in input_shapes:
            continue
        dims = list(input_shapes[inp.name])
        for index, dim in enumerate(inp.type.tensor_type.shape.dim):
            if index >= len(dims):
                break
            if dim.dim_param or dim.dim_value != dims[index]:
                try:
                    dim.ClearField("dim_param")
                except Exception:  # noqa: BLE001
                    dim.dim_param = ""
                dim.dim_value = int(dims[index])
                has_dynamic = True
    if not has_dynamic:
        return model_bytes

    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
    in_path = out_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as handle_in:
            in_path = handle_in.name
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as handle_out:
            out_path = handle_out.name
        onnx.save(model, in_path)
        options.optimized_model_filepath = out_path
        _ = ort.InferenceSession(in_path, options, providers=["CPUExecutionProvider"])
        return onnx.load(out_path).SerializeToString()
    except Exception:  # noqa: BLE001
        return onnx.load(in_path).SerializeToString() if in_path else model_bytes
    finally:
        for path in (in_path, out_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


__all__ = [
    "calc_4d_strides",
    "_calc_4d_strides",
    "collapse_broadcast_shapes",
    "prepare_static_model",
]