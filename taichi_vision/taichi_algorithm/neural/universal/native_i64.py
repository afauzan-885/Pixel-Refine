"""Native INT64 operator dispatch.

The Taichi pool refuses every dynamic INT64 device tensor unless an INT64
candidate artifact is present and validated. No such artifact can be built today
(the pool compiler is not exposed), so those tensors used to fail closed even
though the runtime supports them.

``taichi.python.i64_native`` implements the same operators natively, with the
same semantics and the same status-word error reporting. This module is the thin
adapter between a lowering context and those functions: it only decides whether
the native path applies and converts buffer handles; it contains no arithmetic.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

from .dtypes import F32, I32, I64, broadcast_strides, pad_to, product

_DTYPE_TOKEN = {F32: 0, I32: 1, I64: 2}


def native_module():
    """The native extension when it exposes the INT64 surface, else ``None``."""
    try:
        from taichi import taichi_python
    except ImportError:
        return None
    if not hasattr(taichi_python, "i64_capabilities"):
        return None
    return taichi_python


def available() -> bool:
    """Whether the extension exposes the native INT64 surface."""
    return native_module() is not None


def usable() -> bool:
    """Whether the native surface can actually run against runtime buffers.

    ``available()`` only proves the functions exist. They take raw device
    pointers, and the bridge buffer type in use does not expose one
    (``buffer.handle`` is a slot index and ``__array_interface__`` yields a host
    copy). Until a device pointer is available, the native path cannot be used
    from the pool runtime and callers must keep their Taichi kernels.
    """
    if not available():
        return False
    from taichi.aot_engine import TaichiGPUBuffer

    return hasattr(TaichiGPUBuffer, "data_ptr")


#: Smallest plausible host address. Engine handles are slot indices (1, 2, ...),
#: never real addresses, so anything below this is not a pointer.
_MIN_PLAUSIBLE_ADDRESS = 0x10000


def handle_of(buffer) -> Optional[int]:
    """Device address of a buffer, or ``None`` when it is not safely addressable.

    Two traps this avoids:

    * ``buffer.handle`` is an opaque **slot index** (``1``, ``2``, ...), never an
      address.
    * ``__array_interface__`` on a bridge buffer materialises a **host copy** for
      NumPy. Writing through that address mutates the copy, not the device
      buffer, and the bridge may free it afterwards — which is exactly how an
      access violation happens.

    So a buffer is only used natively when it exposes a real device pointer via
    ``data_ptr``. Without that, the caller keeps its Taichi path.
    """
    data_ptr = getattr(buffer, "data_ptr", None)
    if data_ptr is None:
        return None
    try:
        address = int(data_ptr() if callable(data_ptr) else data_ptr)
    except (TypeError, ValueError, RuntimeError):
        return None
    if address < _MIN_PLAUSIBLE_ADDRESS or address % 8 != 0:
        return None
    return address


def _all_native(*buffers) -> Optional[Tuple[int, ...]]:
    pointers = [handle_of(buffer) for buffer in buffers]
    if any(pointer is None for pointer in pointers):
        return None
    return tuple(pointers)


def _status_code(pointer: int) -> int:
    """Read a 1-element i32 status buffer produced by the native path."""
    return int(np.asarray(pointer).reshape(-1)[0])


def check_status(ctx, status_pointer: int, operation: str) -> None:
    """Mirror ``_Ctx.check_candidate_status`` for the native status word."""
    from .errors import UnsupportedStepError

    ctx.engine.sync()
    code = _status_code(status_pointer)
    if code == 0:
        return
    if code & 4:
        reason = "out-of-range index"
    elif code & 1:
        reason = "division by zero"
    elif code & 2:
        reason = "signed INT64 division overflow"
    else:
        reason = f"status {code}"
    raise UnsupportedStepError(f"native INT64 {operation} failed closed: {reason}")


def _status_buffer(ctx):
    status = ctx.alloc("__native_i64_status", (1,), I32)
    ctx.module.run("nu_fill_i32", y=status, n=1, value=0)
    return status


def _is_scalar_shape(shape) -> bool:
    return product(shape) == 1


def binary(ctx, node, op: str, a, b, out, sa, sb, so, n: int) -> Optional[bool]:
    """Native INT64 binary/compare for flat or broadcastable operands.

    Broadcast is expressed with the same strides the Taichi kernels use
    (``broadcast_strides``), so a singular axis or a scalar operand is repeated
    instead of being read out of bounds.
    """
    module = native_module()
    if module is None:
        return False

    pointers = _all_native(a, b, out)
    if pointers is None:
        return False
    a_ptr, b_ptr, y_ptr = pointers

    dims: Sequence[int] = ()
    a_strides: Sequence[int] = ()
    b_strides: Sequence[int] = ()
    if not (sa == sb == so):
        try:
            from .dtypes import broadcast_shape

            if tuple(broadcast_shape(sa, sb)) != tuple(so):
                return False
        except ValueError:
            return False
        dims = [int(value) for value in so]
        a_strides = [int(value) for value in broadcast_strides(sa, so)]
        b_strides = [int(value) for value in broadcast_strides(sb, so)]

    if op in ("Less", "Greater", "Equal"):
        code = {"Less": 0, "Greater": 1, "Equal": 2}[op]
        module.i64_cmp(a_ptr, b_ptr, y_ptr, n, code, dims, a_strides, b_strides)
        return True
    if op == "Mod":
        code, fmod = 3, int(node.attrs.get("fmod", 0))
    else:
        code = {"Add": 0, "Sub": 1, "Mul": 2, "Div": 4}[op]
        fmod = 0
    status = _status_buffer(ctx)
    module.i64_binary(
        a_ptr, b_ptr, y_ptr, n, code, fmod, handle_of(status),
        dims, a_strides, b_strides,
    )
    if op in ("Div", "Mod"):
        ctx.engine.sync()
        value = int(np.asarray(status.to_numpy()).reshape(-1)[0])
        if value != 0:
            from .errors import UnsupportedStepError

            if value & 4:
                reason = "out-of-range index"
            elif value & 1:
                reason = "division by zero"
            else:
                reason = "signed INT64 division overflow"
            raise UnsupportedStepError(
                f"native INT64 {op} failed closed: {reason} (status={value})"
            )
    return True


def ensure_device(ctx, name: str):
    """Materialise a value on the device so the native ABI has a pointer.

    Constants and host metadata live only as NumPy arrays; the native path needs
    a device buffer, so upload once and cache it under the same name.
    """
    buffer = ctx.buffers.get(name)
    if buffer is not None:
        return buffer
    value = ctx.session.plan.constants.get(name)
    if value is None and name in ctx.host:
        value = ctx.host[name]
    if value is None:
        return None
    array = np.ascontiguousarray(value)
    buffer = ctx.session.upload(name, array.reshape(-1))
    ctx.buffers[name] = buffer
    ctx.shapes[name] = tuple(int(d) for d in array.shape)
    return buffer


def buffer_elements(buffer) -> Optional[int]:
    """Element count of a device buffer, from its declared shape."""
    interface = getattr(buffer, "__array_interface__", None)
    if interface is None:
        return None
    shape = interface.get("shape")
    if shape is None:
        elements = getattr(buffer, "nbytes", None)
        shape = None
    if shape is None:
        total = getattr(buffer, "nbytes", None)
        return int(total // 8) if total else None
    total = 1
    for value in shape:
        total *= int(value)
    return total


def gather(ctx, node, data, indices, out, sd, si, so, axis: int) -> bool:
    """Native INT64 Gather / GatherElements along ``axis``."""
    module = native_module()
    if module is None:
        return False
    data_name = node.inputs[0]
    index_name = node.inputs[1]
    if data is None:
        data = ensure_device(ctx, data_name)
    if indices is None:
        indices = ensure_device(ctx, index_name)
    if data is None or indices is None:
        return False
    pointers = _all_native(data, indices, out)
    if pointers is None:
        return False
    data_ptr, indices_ptr, y_ptr = pointers
    outer = product(sd[:axis]) if axis else 1
    inner = product(sd[axis + 1:]) if axis + 1 < len(sd) else 1
    axis_dim = sd[axis]
    indices_size = product(si)

    # The native kernel dereferences these regions directly, so the declared
    # shapes must match what the buffers really hold. A mismatch (for example an
    # index buffer narrowed to i32 elsewhere) must fall back, not read past the
    # allocation.
    expected = {
        "data": product(sd),
        "indices": indices_size,
        "out": product(so),
    }
    actual = {
        "data": buffer_elements(data),
        "indices": buffer_elements(indices),
        "out": buffer_elements(out),
    }
    for name, want in expected.items():
        have = actual[name]
        if have is not None and have < want:
            return False

    status = _status_buffer(ctx)
    if node.op == "Gather":
        module.gather_i64(
            data_ptr, indices_ptr, y_ptr, outer, indices_size, axis_dim, inner,
            handle_of(status),
        )
    else:
        # GatherElements: the index tensor may be shorter on the axis than the
        # data, so both axis dimensions are passed (same as nu_gather_elements).
        module.gather_elements_i64(
            data_ptr, indices_ptr, y_ptr, outer, axis_dim, si[axis], inner,
            handle_of(status),
        )
    ctx.engine.sync()
    value = int(np.asarray(status.to_numpy()).reshape(-1)[0])
    if value != 0:
        from .errors import UnsupportedStepError

        raise UnsupportedStepError(
            f"native INT64 {node.op} failed closed: out-of-range index (status={value})"
        )
    return True


def transpose(ctx, node, x, out, si, so, perm: Sequence[int]) -> bool:
    """Native INT64 Transpose for rank-4 tensors only."""
    module = native_module()
    if module is None or len(si) != 4:
        return False
    pointers = _all_native(x, out)
    if pointers is None:
        return False
    module.transpose4_i64(
        pointers[0], pointers[1],
        int(si[0]), int(si[1]), int(si[2]), int(si[3]),
        [int(value) for value in perm],
    )
    return True


def slice_axis(ctx, node, x, out, si, so, axis: int, start: int, step: int) -> bool:
    """Native INT64 Slice on one axis."""
    module = native_module()
    if module is None:
        return False
    pointers = _all_native(x, out)
    if pointers is None:
        return False
    outer = product(si[:axis]) if axis else 1
    inner = product(si[axis + 1:]) if axis + 1 < len(si) else 1
    module.slice_axis_i64(
        pointers[0], pointers[1], outer, si[axis], inner, start, step, so[axis]
    )
    return True


def concat(ctx, node, parts, out, shapes, so, axis: int) -> bool:
    """Native INT64 Concat on one axis."""
    module = native_module()
    if module is None:
        return False
    if not all(len(shape) == len(shapes[0]) for shape in shapes):
        return False
    pointers = _all_native(*parts, out)
    if pointers is None:
        return False
    outer = product(shapes[0][:axis]) if axis else 1
    inner = product(shapes[0][axis + 1:]) if axis + 1 < len(shapes[0]) else 1
    module.concat_axis_i64(
        list(pointers[:-1]),
        [int(shape[axis]) for shape in shapes],
        pointers[-1], outer, so[axis], inner, 0,
    )
    return True


def topk_last(ctx, node, x, values, indices, rows: int, cols: int, k: int,
              dtype: str) -> bool:
    """Native INT64 TopK on the last axis."""
    module = native_module()
    if module is None:
        return False
    token = _DTYPE_TOKEN.get(dtype)
    if token not in (0, 2):
        return False
    pointers = _all_native(x, values, indices)
    if pointers is None:
        return False
    module.topk_last_i64(
        pointers[0], pointers[1], pointers[2], rows, cols, k, token
    )
    return True


def split(ctx, node, x, out, si, so, axis: int, offset: int) -> bool:
    """Native INT64 Split on one axis."""
    module = native_module()
    if module is None:
        return False
    pointers = _all_native(x, out)
    if pointers is None:
        return False
    outer = product(si[:axis]) if axis else 1
    inner = product(si[axis + 1:]) if axis + 1 < len(si) else 1
    module.split_axis_i64(
        pointers[0], pointers[1], outer, si[axis], so[axis], inner, offset
    )
    return True


def expand(ctx, node, x, out, si, so) -> bool:
    """Native INT64 Expand via broadcast strides."""
    module = native_module()
    if module is None:
        return False
    pointers = _all_native(x, out)
    if pointers is None:
        return False
    rank = len(so)
    module.expand_i64(
        pointers[0], pointers[1], max(1, product(si)), rank,
        [int(value) for value in so],
        [int(value) for value in broadcast_strides(si, so)],
        product(so),
    )
    return True


def nonzero(ctx, node, x, out, count, si) -> bool:
    """Native INT64 NonZero; ``count`` receives how many positions were written."""
    module = native_module()
    if module is None:
        return False
    pointers = _all_native(x, out, count)
    if pointers is None:
        return False
    total = product(si)
    module.nonzero_i64(
        pointers[0], pointers[1], pointers[2],
        len(si), [int(value) for value in si], total,
    )
    return True


def cast_i64(ctx, node, x, out, si, src: str, dst: str) -> bool:
    """Native INT64-aware Cast (f32/i32/i64 in any admitted direction)."""
    module = native_module()
    if module is None:
        return False
    src_token = _DTYPE_TOKEN.get(src)
    dst_token = _DTYPE_TOKEN.get(dst)
    if src_token is None or dst_token is None:
        return False
    pointers = _all_native(x, out)
    if pointers is None:
        return False
    module.cast(pointers[0], pointers[1], product(si), src_token, dst_token)
    return True


def fill_i64(ctx, node, out, shape, value: float, dtype: str) -> bool:
    """Native INT64/i32 fill; only integer fills are admitted."""
    module = native_module()
    if module is None:
        return False
    token = _DTYPE_TOKEN.get(dtype)
    if token not in (1, 2):
        return False
    pointer = handle_of(out)
    if pointer is None:
        return False
    module.fill(pointer, product(shape), int(value), token)
    return True


def range_i64(ctx, node, out, count: int, start: int, delta: int) -> bool:
    """Native INT64 Range."""
    module = native_module()
    if module is None:
        return False
    pointer = handle_of(out)
    if pointer is None:
        return False
    module.range_i64(pointer, count, start, delta)
    return True


__all__ = [
    "native_module",
    "available",
    "handle_of",
    "binary",
    "gather",
    "transpose",
    "slice_axis",
    "concat",
    "topk_last",
    "split",
    "expand",
    "nonzero",
    "cast_i64",
    "fill_i64",
    "range_i64",
]
