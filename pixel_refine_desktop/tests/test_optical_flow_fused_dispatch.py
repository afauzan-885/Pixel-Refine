from __future__ import annotations

import pytest

from taichi_vision.taichi_algorithm.aot_wrapper import _run_fused_flow_level
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.resident_pipeline import (
    _ResidentFlowBufferMixin,
)


class _RecordingModule:
    def __init__(self, fail=()):
        self.calls = []
        self.fail = set(fail)

    def run(self, graph_name, **kwargs):
        self.calls.append((graph_name, kwargs))
        if graph_name in self.fail:
            raise RuntimeError(f"injected failure: {graph_name}")


def _arguments():
    marker = object()
    track = {
        "prev": marker,
        "next": marker,
        "init_flow": marker,
        "grid_flow": marker,
        "grid_meta": marker,
        "grid_step": 16,
        "border_margin": 8,
        "win_radius": 8,
        "iterations": 16,
        "epsilon": 0.015,
    }
    dense = {
        "grid_flow": marker,
        "flow_out": marker,
        "grid_step": 16,
        "border_margin": 8,
        "max_flow_px": 64.0,
    }
    return track, dense


def test_blocky_clamped_uses_direct_graphs_and_preserves_mode():
    module = _RecordingModule()
    track, dense = _arguments()

    fused = _run_fused_flow_level(
        module, track, "blocky_clamped", dense, force_direct=True
    )

    assert fused is False
    assert [name for name, _ in module.calls] == [
        "flow_lk_grid_track",
        "flow_lk_dense_blocky_clamped",
    ]


def test_blocky_clamped_dense_failure_does_not_silently_enable_smoothing():
    module = _RecordingModule(fail={"flow_lk_dense_blocky_clamped"})
    track, dense = _arguments()

    with pytest.raises(RuntimeError, match="flow_lk_dense_blocky_clamped"):
        _run_fused_flow_level(
            module, track, "blocky_clamped", dense, force_direct=True
        )

    assert [name for name, _ in module.calls] == [
        "flow_lk_grid_track",
        "flow_lk_dense_blocky_clamped",
    ]


def test_smooth_mode_keeps_fused_graph_path():
    module = _RecordingModule()
    track, dense = _arguments()
    dense.pop("max_flow_px")
    dense["overlap"] = 0.5

    fused = _run_fused_flow_level(module, track, "smooth", dense)

    assert fused is True
    assert [name for name, _ in module.calls] == [
        "flow_lk_track_dense",
    ]


def test_quantized_resident_flow_does_not_replace_aot_destination():
    class _Buffer:
        def __init__(self, is_vector):
            self.shape = (24, 32, 2)
            self.dtype = "float32"
            self.is_vector = is_vector
            self.vector_dim = 2 if is_vector else 1
            self.handle = object()
            self.is_owner = True
            self.host_accessible = True
            self.size_bytes = 24 * 32 * 2 * 4
            self.engine = None

        def destroy(self):
            self.handle = None

    class _API:
        def __init__(self):
            self.engine = self
            self.sync_count = 0

        def upload(self, _array, is_vector=False):
            return _Buffer(is_vector)

        def sync(self):
            self.sync_count += 1

    aligner = _ResidentFlowBufferMixin()
    aligner._init_resident_flow_buffer()
    raw_destination = _Buffer(is_vector=False)
    aligner._resident_flow_buffer = raw_destination
    api = _API()

    quantized = aligner._store_quantized_flow(api, object())
    retained = aligner._resident_flow_view(quantized)

    assert aligner._resident_flow_buffer is raw_destination
    assert aligner._resident_quantized_flow_buffer is quantized
    assert raw_destination.is_vector is False
    assert quantized.is_vector is True
    assert retained._parent_ref is quantized

    aligner._close_resident_flow_buffer()
    assert raw_destination.handle is None
    assert quantized.handle is None
