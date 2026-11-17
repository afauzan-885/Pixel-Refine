"""Native INT64 dispatch contract.

Two states must both be correct:

* **extension absent** — nothing changes: the runtime keeps refusing dynamic INT64
  device tensors with the same actionable message as before;
* **extension present** — the native path is offered, and it only claims the
  shapes it actually implements (flat elementwise, single-axis movement).

The Rust side owns the arithmetic; its own unit tests (`cargo test ... i64_native`)
cover values. These tests cover dispatch decisions, so they never need a device.
"""

from __future__ import annotations

import numpy as np
import pytest

from taichi_vision.taichi_algorithm.neural.universal import native_i64
from taichi_vision.taichi_algorithm.neural.universal.dtypes import F32, I32, I64


def test_native_module_probe_is_safe_without_extension():
    module = native_i64.native_module()
    if module is None:
        assert native_i64.available() is False
    else:
        assert native_i64.available() is True
        assert "i64_binary" in module.i64_capabilities()


def test_handle_of_only_accepts_a_real_device_pointer():
    """A slot index or a host copy must never be treated as a device address.

    ``buffer.handle`` is an opaque slot index and ``__array_interface__`` yields
    a host copy; dereferencing either from native code is an access violation,
    so only ``data_ptr`` counts.
    """

    class SlotIndexBuffer:
        handle = 1

        @property
        def __array_interface__(self):
            return {"data": (0x7FF000001000, False), "shape": (4,)}

    class DataPtrBuffer:
        handle = 1

        def data_ptr(self):
            return 0x7FF000002000

        @property
        def __array_interface__(self):
            return {"data": (0x7FF000001000, False), "shape": (4,)}

    class UnalignedBuffer:
        def data_ptr(self):
            return 0x7FF000002003  # not 8-byte aligned

    assert native_i64.handle_of(SlotIndexBuffer()) is None
    assert native_i64.handle_of(object()) is None
    assert native_i64.handle_of(None) is None
    assert native_i64.handle_of(UnalignedBuffer()) is None
    assert native_i64.handle_of(DataPtrBuffer()) == 0x7FF000002000


class _FakeCtx:
    """Minimal lowering context: records dispatches instead of running them."""

    def __init__(self):
        self.calls = []
        self.buffers = {}

    def alloc(self, name, shape, dtype=F32):
        buffer = type("B", (), {"handle": 0x2000, "shape": tuple(shape), "dtype": dtype})()
        self.buffers[name] = buffer
        return buffer

    class _Module:
        def __init__(self, owner):
            self.owner = owner

        def run(self, name, **kwargs):
            self.owner.calls.append((name, kwargs))

    @property
    def module(self):
        return self._Module(self)

    class _Engine:
        def sync(self):
            return None

    @property
    def engine(self):
        return self._Engine()

    def device(self, name):
        return type("B", (), {"handle": 0x3000, "shape": (2,), "dtype": F32})()


def test_binary_declines_broadcast_shapes():
    """Broadcast must be declined: faking it would compute the wrong result."""
    ctx = _FakeCtx()
    node = type("N", (), {"attrs": {}})()
    a = type("B", (), {"handle": 0x10})()
    b = type("B", (), {"handle": 0x20})()
    out = type("B", (), {"handle": 0x30})()
    assert native_i64.binary(ctx, node, "Add", a, b, out, (4,), (1,), (4,), 4) is False


def test_binary_declines_without_extension():
    if native_i64.available():
        pytest.skip("extension present: the native path is expected to answer")
    ctx = _FakeCtx()
    node = type("N", (), {"attrs": {}})()
    a = type("B", (), {"handle": 0x10})()
    out = type("B", (), {"handle": 0x30})()
    assert native_i64.binary(ctx, node, "Add", a, a, out, (4,), (4,), (4,), 4) is False


def test_transpose_declines_rank_other_than_four():
    ctx = _FakeCtx()
    node = type("N", (), {"attrs": {}})()
    buffer = type("B", (), {"handle": 0x10})()
    assert (
        native_i64.transpose(ctx, node, buffer, buffer, (2, 3), (3, 2), [1, 0])
        is False
    )


def test_concat_declines_mismatched_ranks():
    ctx = _FakeCtx()
    node = type("N", (), {"attrs": {}})()
    part = type("B", (), {"handle": 0x10})()
    out = type("B", (), {"handle": 0x20})()
    assert (
        native_i64.concat(ctx, node, [part], out, [(2, 3), (2,)], (2, 4), 1)
        is False
    )


def test_topk_declines_unsupported_dtype():
    ctx = _FakeCtx()
    node = type("N", (), {"attrs": {}})()
    buffer = type("B", (), {"handle": 0x10})()
    indices = type("B", (), {"handle": 0x20})()
    assert (
        native_i64.topk_last(ctx, node, buffer, buffer, indices, 1, 4, 2, I32) is False
    )


def test_i64_dtype_tokens_are_stable():
    """The native ABI takes numeric dtype tokens; they must not drift."""
    assert native_i64._DTYPE_TOKEN == {F32: 0, I32: 1, I64: 2}
