"""Resident ONNX completion must not raise when the native error slot is empty.

A successful ``sync_runtime`` leaves no native error text. The legacy helper
``_raise_native_engine_error`` raises unconditionally, so calling it without a
gate produced a phantom ``unknown native failure`` fault after the DNG output
had already been written.
"""

import threading
from types import SimpleNamespace

import pytest


def _fake_graph():
    engine = SimpleNamespace(
        runtime=1234,
        _generation=1,
        _destroyed=False,
        _lock=threading.RLock(),
        sync=lambda: None,
        _assert_native_context_owner=lambda context: None,
    )
    return SimpleNamespace(
        engine=engine,
        _invocations=SimpleNamespace(slot=SimpleNamespace(closed=False)),
        _view_thread=threading.get_ident(),
        _view_owner=(id(engine), engine.runtime, 1),
        _view_guard=lambda: None,
    )


def _graph_class():
    from taichi_vision.taichi_algorithm.denoising.onnx_resident_aot import (
        ResidentONNXGraph,
    )

    return ResidentONNXGraph


def test_completed_sync_without_native_error_is_success(monkeypatch):
    import taichi.native_bridge as native_bridge

    monkeypatch.setattr(native_bridge, "last_error", lambda runtime: "")

    _graph_class()._view_sync(_fake_graph())


def test_completed_sync_with_native_error_still_raises(monkeypatch):
    import taichi.native_bridge as native_bridge

    monkeypatch.setattr(
        native_bridge, "last_error", lambda runtime: "device lost"
    )

    with pytest.raises(RuntimeError, match="device lost"):
        _graph_class()._view_sync(_fake_graph())
