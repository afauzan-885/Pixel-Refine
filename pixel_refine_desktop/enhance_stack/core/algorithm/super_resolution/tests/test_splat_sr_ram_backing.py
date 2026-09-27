"""RAM ownership, allocation admission and disk-versus-RAM parity gates."""
from __future__ import annotations

import os
import weakref
from types import SimpleNamespace

os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", "cpu")

import numpy as np
import psutil
import pytest

from taichi_vision import taichi_aot
from taichi_vision.taichi_algorithm.buffer_session import BufferSession
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.tiled_accumulator import (
    RamAccumulatorBacking, TiledRGBResult, TiledHannAccumulator, _TileBacking,
)


def test_ram_guard_rejects_before_array_allocation_without_disk_spill(monkeypatch):
    monkeypatch.setattr(psutil, "virtual_memory", lambda: SimpleNamespace(available=64 * 1024**2))
    def forbidden(*args, **kwargs):
        raise AssertionError("rejected job must not allocate or open scratch")
    monkeypatch.setattr(np, "empty", forbidden)
    monkeypatch.setattr(_TileBacking, "__init__", forbidden)
    with pytest.raises(MemoryError, match="No automatic disk spill"):
        RamAccumulatorBacking((32, 64, 3))


def test_job_headroom_is_included_in_ram_admission(monkeypatch):
    monkeypatch.setattr(psutil, "virtual_memory", lambda: SimpleNamespace(available=512 * 1024**2))
    with pytest.raises(MemoryError, match="safety headroom"):
        RamAccumulatorBacking((8, 9, 3), minimum_headroom_bytes=600 * 1024**2)


@pytest.mark.parametrize("shape,error", [
    ((0, 32, 3), ValueError), ((2, 3, 1), ValueError),
    ((np.iinfo(np.intp).max, 2, 3), OverflowError),
])
def test_ram_shape_is_validated_before_allocation(shape, error):
    with pytest.raises(error):
        RamAccumulatorBacking(shape)


def test_second_allocation_failure_drops_first_array(monkeypatch):
    original_empty = np.empty
    allocations = []
    def allocate(shape, **kwargs):
        if allocations:
            raise MemoryError("injected denominator allocation failure")
        array = original_empty(shape, **kwargs)
        allocations.append(weakref.ref(array))
        return array
    monkeypatch.setattr(np, "empty", allocate)
    with pytest.raises(MemoryError, match="injected denominator"):
        RamAccumulatorBacking((8, 9, 3))
    assert allocations[0]() is None


def test_result_borrows_readonly_ram_and_close_is_idempotent():
    backing = RamAccumulatorBacking((8, 9, 3))
    result = TiledRGBResult(backing)
    borrowed = result[1:4, 2:7]
    assert np.shares_memory(borrowed, backing.numerator)
    assert not borrowed.flags.writeable
    with pytest.raises(ValueError):
        borrowed[:] = 1.0
    with pytest.raises(TypeError, match="rectangular tiles"):
        np.asarray(result)
    # Views are valid only during use; do not retain them after closing owner.
    del borrowed
    numerator = weakref.ref(backing.numerator)
    result.close()
    result.close()
    assert numerator() is None
    assert backing.denominator is None


def test_ram_finalization_releases_denominator_and_transfers_same_numerator():
    reference = np.full((45, 59, 3), 0.3, np.float32)
    session = BufferSession()
    result = None
    try:
        accumulator = TiledHannAccumulator(reference, session=session, block_size=64)
        backing = accumulator.backing
        numerator = weakref.ref(backing.numerator)
        denominator = weakref.ref(backing.denominator)
        assert backing.required_bytes == 90 * 118 * 16
        accumulator.add_frame(reference, None, None)
        result = accumulator.finalize()
        assert denominator() is None
        assert numerator() is result.backing.numerator
        session.close()
        assert not result.backing.closed
        np.testing.assert_allclose(result[0:8, 0:8], 0.3, atol=1e-6)
    finally:
        session.close()
        if result is not None:
            result.close()
    assert numerator() is None


@pytest.mark.parametrize("fault", ["dispatch", "readback", "finalize"])
def test_fault_cleanup_retires_ram_and_borrows(fault, monkeypatch):
    reference = np.full((45, 59, 3), 0.3, np.float32)
    session = BufferSession()
    try:
        accumulator = TiledHannAccumulator(reference, session=session, block_size=64)
        backing = accumulator.backing
        confidence = session.own(taichi_aot.upload(np.ones(reference.shape[:2], np.float32)))
        def fail(*args, **kwargs):
            raise RuntimeError("injected patch fault")
        if fault == "dispatch":
            monkeypatch.setattr(accumulator.splat.module, "run", fail)
            with pytest.raises(RuntimeError, match="injected patch fault"):
                accumulator.add_frame(reference, None, confidence)
        elif fault == "readback":
            from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
            monkeypatch.setattr(TaichiGPUBuffer, "to_numpy", fail)
            with pytest.raises(RuntimeError, match="injected patch fault"):
                accumulator.add_frame(reference, None, confidence)
        else:
            accumulator.add_frame(reference, None, confidence)
            accumulator.check_cancelled = fail
            with pytest.raises(RuntimeError, match="injected patch fault"):
                accumulator.finalize()
        assert session.borrowed_count == 0
    finally:
        session.close()
    assert session.owned_count == 0
    assert backing.numerator is backing.denominator is None


def test_many_supports_reuse_accumulator_and_session_resource_count():
    reference = np.full((45, 59, 3), 0.3, np.float32)
    with BufferSession() as session:
        accumulator = TiledHannAccumulator(reference, session=session, block_size=64)
        numerator_id = id(accumulator.backing.numerator)
        denominator_id = id(accumulator.backing.denominator)
        accumulator.add_frame(reference, None, None)
        warm_count = session.owned_count
        for _ in range(12):
            accumulator.add_frame(reference, None, None)
            assert id(accumulator.backing.numerator) == numerator_id
            assert id(accumulator.backing.denominator) == denominator_id
            assert session.owned_count == warm_count
        backing = accumulator.backing
    assert backing.numerator is backing.denominator is None


@pytest.mark.parametrize("empty_coverage", [False, True])
def test_ram_and_disk_same_graph_same_hann_are_identical(empty_coverage, tmp_path, monkeypatch):
    monkeypatch.setenv("SPLATSR_SCRATCH_DIR", str(tmp_path))
    shape = (129, 137)
    rng = np.random.default_rng(117)
    reference = rng.uniform(0.1, 0.8, (*shape, 3)).astype(np.float32)
    support = rng.uniform(0.1, 0.8, (*shape, 3)).astype(np.float32)
    y, x = np.mgrid[:shape[0], :shape[1]].astype(np.float32)
    flow = np.stack((0.3 * np.sin(y / 8), -0.2 * np.cos(x / 9)), axis=-1)
    confidence = np.zeros(shape, np.float32) if empty_coverage else rng.uniform(0, 1, shape).astype(np.float32)
    outputs = []
    for factory in (RamAccumulatorBacking, _TileBacking):
        result = None
        try:
            with BufferSession() as session:
                accumulator = TiledHannAccumulator(reference, session=session, block_size=64, backing_factory=factory)
                device_confidence = session.own(taichi_aot.upload(confidence))
                accumulator.add_frame(reference, None, device_confidence)
                accumulator.add_frame(support, flow, device_confidence)
                result = accumulator.finalize()
            image = np.empty((shape[0] * 2, shape[1] * 2, 3), np.float32)
            for y0, y1, x0, x1, tile in result.iter_tiles(64):
                image[y0:y1, x0:x1] = tile
            outputs.append(image)
        finally:
            if result is not None:
                result.close()
    print(f"[RAM-DISK PARITY] device={taichi_aot.backend_info()} input={reference.shape} dtype=float32 empty={empty_coverage} max_abs={np.max(np.abs(outputs[0]-outputs[1])):.8g}")
    np.testing.assert_array_equal(outputs[0], outputs[1])
    assert not list(tmp_path.glob("pixelrefine_splat_tiles_*"))
