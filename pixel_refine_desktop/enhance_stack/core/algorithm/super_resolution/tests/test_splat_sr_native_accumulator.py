"""Numerical and lifetime gates for native accumulation without image readbacks."""
import os
os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", "cpu")
import numpy as np
import pytest
from taichi_vision import taichi_aot
from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
from taichi_vision.taichi_algorithm.buffer_session import BufferSession
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.tiled_accumulator import (
    NativeAccumulatorBacking, RamAccumulatorBacking, TiledHannAccumulator,
)


def materialize(result):
    array = np.empty(result.shape, np.float32)
    for y0, y1, x0, x1, tile in result.iter_tiles(64):
        array[y0:y1, x0:x1] = tile
    return array


@pytest.mark.parametrize("shape,block", [((45, 59), 64), ((129, 137), 64), ((513, 517), 1024)])
@pytest.mark.parametrize("empty", [False, True])
def test_native_matches_ram_without_image_readback(shape, block, empty, monkeypatch):
    rng = np.random.default_rng(951)
    reference = rng.uniform(.1, .8, (*shape, 3)).astype(np.float32)
    support = rng.uniform(.1, .8, (*shape, 3)).astype(np.float32)
    y, x = np.mgrid[:shape[0], :shape[1]].astype(np.float32)
    flow = np.stack((.35 + .2 * np.sin(y / 8), -.23 + .15 * np.cos(x / 9)), axis=-1)
    confidence = (.25 + .75 * x / max(1, shape[1]-1)).astype(np.float32)
    confidence[shape[0]//3:shape[0]//2, shape[1]//3:shape[1]//2] = 0
    if empty:
        confidence.fill(0)
    with BufferSession() as session:
        oracle = TiledHannAccumulator(reference, session=session, block_size=block,
                                      backing_factory=RamAccumulatorBacking)
        if not empty:
            oracle.add_frame(reference, None, None)
        oracle.add_frame(support, flow, confidence)
        result = oracle.finalize()
    try:
        expected = materialize(result)
    finally:
        result.close()

    def forbidden(*args, **kwargs):
        raise AssertionError("native accumulation must not read image buffers to NumPy")
    monkeypatch.setattr(TaichiGPUBuffer, "to_numpy", forbidden)
    result = None
    try:
        with BufferSession() as session:
            accumulator = TiledHannAccumulator(reference, session=session, block_size=block,
                                               backing_factory=NativeAccumulatorBacking)
            if not empty:
                accumulator.add_frame(reference, None, None)
            gpu_confidence = session.own(taichi_aot.upload(confidence))
            accumulator.add_frame(support, flow, gpu_confidence)
            assert session.borrowed_count == 0
            assert accumulator.readbacks == 0
            assert accumulator.host_packed is accumulator.confidence_scratch is None
            result = accumulator.finalize()
            assert accumulator.backing.acc_den is None
        got = materialize(result)  # Output remains mapped after the job session closes.
        error = float(np.max(np.abs(got - expected)))
        print(f"[NATIVE SR] device={taichi_aot.backend_info()} shape={reference.shape} "
              f"dtype=float32 empty={empty} max_abs={error:.9g}")
        np.testing.assert_allclose(got, expected, atol=1e-5, rtol=1e-5)
        assert not result[0:4, 0:4].flags.writeable
    finally:
        if result is not None:
            result.close()
    assert accumulator.backing.acc_num is None
    assert accumulator.backing.closed


def test_native_cancel_and_dispatch_failure_cleanup(monkeypatch):
    reference = np.full((45, 59, 3), .3, np.float32)
    with BufferSession() as session:
        accumulator = TiledHannAccumulator(reference, session=session, block_size=64,
                                           backing_factory=NativeAccumulatorBacking)
        def fail(*args, **kwargs):
            raise RuntimeError("injected native accumulation fault")
        monkeypatch.setattr(taichi_aot, "accumulate_packed_tile", fail)
        with pytest.raises(RuntimeError, match="injected native accumulation fault"):
            accumulator.add_frame(reference, None, None)
    assert accumulator.backing.closed
    assert accumulator.backing.acc_num is accumulator.backing.acc_den is None


@pytest.mark.parametrize("stage", ["add", "finalize", "map"])
def test_native_cancellation_and_mapping_failure_release_owner(stage, monkeypatch):
    reference = np.full((45, 59, 3), .3, np.float32)
    def cancel():
        raise RuntimeError("injected cancellation")
    with pytest.raises(RuntimeError, match="injected"):
        with BufferSession() as session:
            accumulator = TiledHannAccumulator(reference, session=session, block_size=64,
                                               backing_factory=NativeAccumulatorBacking)
            if stage == "add":
                accumulator.check_cancelled = cancel
            confidence = session.own(taichi_aot.upload(np.ones(reference.shape[:2], np.float32)))
            try:
                accumulator.add_frame(reference, None, confidence)
            finally:
                assert session.borrowed_count == 0
            if stage == "finalize":
                accumulator.check_cancelled = cancel
            if stage == "map":
                def fail_map(*args, **kwargs):
                    raise RuntimeError("injected mapping failure")
                monkeypatch.setattr(TaichiGPUBuffer, "map", fail_map)
            accumulator.finalize()
    assert accumulator.backing.closed
    assert accumulator.backing.acc_num is accumulator.backing.acc_den is None


def test_native_rejects_negative_headroom():
    with pytest.raises(ValueError, match="headroom"):
        NativeAccumulatorBacking((16, 16, 3), minimum_device_headroom_bytes=-1)


@pytest.mark.parametrize("mode", ["tiff", "linear_dng", "failure"])
def test_native_output_writer_owns_and_releases_mapping(tmp_path, monkeypatch, mode):
    import tifffile
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr import legacy
    reference = np.random.default_rng(156).uniform(.1, .7, (45, 59, 3)).astype(np.float32)
    with BufferSession() as session:
        accumulator = TiledHannAccumulator(reference, session=session, block_size=64,
                                           backing_factory=NativeAccumulatorBacking)
        accumulator.add_frame(reference, None, None)
        result = accumulator.finalize()
    try:
        expected = materialize(result)
        output = str(tmp_path / "native.tif")
        if mode == "failure":
            def fail_writer(*args, **kwargs):
                raise OSError("injected writer failure")
            monkeypatch.setattr(legacy, "save_image_streaming", fail_writer)
            with pytest.raises(OSError, match="injected writer failure"):
                legacy._save_mfd_compatible_result(result, output)
        else:
            reference_path = None
            if mode == "linear_dng":
                monkeypatch.setattr(legacy, "_mfd_linear_mode", lambda path: True)
                reference_path = str(tmp_path / "reference.dng")
            saved = legacy._save_mfd_compatible_result(result, output, reference_path)
            expected = np.clip(expected * 65535.0 + .5, 0, 65535).astype(np.uint16)
            if mode == "linear_dng":
                expected = expected[..., ::-1]
            np.testing.assert_array_equal(tifffile.imread(saved), expected)
        assert accumulator.backing.closed
        assert accumulator.backing.acc_num is accumulator.backing.acc_den is None
    finally:
        result.close()
