"""Tests for resident Lucas–Kanade remap submission."""

import importlib
from types import SimpleNamespace

import numpy as np
import pytest

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade import (
    LucasKanade,
)


class _Buffer:
    def __init__(self, shape):
        self.shape = shape
        self.handle = object()
        self.nbytes = int(np.prod(shape)) * np.dtype(np.float32).itemsize
        self.released = False

    def release(self):
        self.released = True


@pytest.mark.parametrize("backend", ["cuda", "vulkan", "opengl", "cpu"])
def test_tiled_remap_is_queue_ordered_and_retires_flow_after_dispatch(
    monkeypatch, backend
):
    import taichi_vision
    engine_module = importlib.import_module("taichi_vision.taichi_aot.engine")

    sync_calls = []

    class _Engine:
        arch = backend

        @staticmethod
        def sync():
            sync_calls.append("sync")

        buffer_pool = SimpleNamespace(clear=lambda: None)

    captured = {}
    warped_gpu = _Buffer((4, 5, 3))
    fake_aot = SimpleNamespace(engine=_Engine())

    def remap_with_flow(*args, **kwargs):
        captured.update(kwargs)
        return warped_gpu

    fake_aot.remap_with_flow = remap_with_flow
    monkeypatch.setattr(taichi_vision, "taichi_aot", fake_aot)

    class _Lib:
        @staticmethod
        def write_to_gpu_buffer(*_args):
            return None

    monkeypatch.setattr(engine_module, "_LIB", _Lib())
    monkeypatch.setattr(engine_module, "_RUNTIME", object())

    worker = LucasKanade.__new__(LucasKanade)
    target_gpu = _Buffer((4, 5, 3))
    flow_gpu = _Buffer((4, 5, 2))
    worker._tile_buffers = {
        0: {
            "target_gpu": target_gpu,
            "ref_gray_gpu": _Buffer((4, 5)),
            "target_gray_gpu": _Buffer((4, 5)),
            "warped_gpu": warped_gpu,
            "target_host": np.empty((4, 5, 3), dtype=np.float32),
            "target_gray_host": np.empty((4, 5), dtype=np.float32),
        }
    }
    worker._calculate_flow_gpu_buffer = lambda *_args, **_kwargs: flow_gpu

    image = np.zeros((4, 5, 3), dtype=np.float32)
    profile = {
        "cpu_gray": 0.0,
        "upload_color": 0.0,
        "upload_gray": 0.0,
        "gpu_upload": 0.0,
        "flow_calc": 0.0,
        "warp": 0.0,
    }
    result = worker._warp_tile_gpu(
        {"roi": (0, 0, 5, 4)},
        image,
        image,
        {"conservative_vram": False},
        profile=profile,
        tile_idx=0,
        target_gray_full=np.zeros((4, 5), dtype=np.float32),
    )

    assert result is warped_gpu
    assert captured["return_gpu"] is True
    assert "synchronize" not in captured
    assert flow_gpu.released
    # These fences protect the upload and completed-flow input before remap;
    # the mock does not simulate the wrapper's backend-dependent final fence.
    assert sync_calls == ["sync", "sync"]


@pytest.mark.parametrize("backend", ["cuda", "vulkan", "opengl", "cpu"])
def test_standalone_remap_is_queue_ordered_and_retires_flow_after_dispatch(
    monkeypatch, backend
):
    import taichi_vision

    sync_calls = []

    class _Engine:
        arch = backend

        @staticmethod
        def sync():
            sync_calls.append("sync")

    captured = {}
    released = []
    warped_gpu = _Buffer((4, 5, 3))
    fake_aot = SimpleNamespace(engine=_Engine())

    def upload(array, is_vector=False):
        buffer = _Buffer(array.shape)
        buffer.is_vector = is_vector
        released.append(buffer)
        return buffer

    def make_gpu_result(*_args, **kwargs):
        buffer = _Buffer((4, 5))
        released.append(buffer)
        return buffer

    def remap_with_flow(*_args, **kwargs):
        captured.update(kwargs)
        return warped_gpu

    fake_aot.upload = upload
    fake_aot.box_filter = make_gpu_result
    fake_aot.enhance_grayscale = make_gpu_result
    fake_aot.remap_with_flow = remap_with_flow
    monkeypatch.setattr(taichi_vision, "taichi_aot", fake_aot)

    worker = LucasKanade.__new__(LucasKanade)
    flow_gpu = _Buffer((4, 5, 2))
    worker._calculate_flow_gpu_buffer = lambda *_args, **_kwargs: flow_gpu

    image = np.zeros((4, 5, 3), dtype=np.float32)
    result = worker._warp_tile_gpu(
        {"roi": (0, 0, 5, 4)}, image, image, {}, tile_idx=None
    )

    assert result is warped_gpu
    assert captured["return_gpu"] is True
    assert "synchronize" not in captured
    assert flow_gpu.released
    assert sync_calls == ["sync", "sync"]
