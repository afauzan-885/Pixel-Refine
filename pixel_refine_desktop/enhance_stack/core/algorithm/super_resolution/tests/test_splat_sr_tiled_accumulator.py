"""Native tile parity, bounded allocation and backing-store lifecycle gates."""

from __future__ import annotations

import os

os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", "cpu")

import numpy as np
import pytest
import tifffile

from taichi_vision import taichi_aot
from taichi_vision.taichi_algorithm.buffer_session import BufferSession
from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.spatial_splat_runtime import (
    SessionHannAccumulator,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.tiled_accumulator import (
    DiskBackedRGB,
    RamAccumulatorBacking,
    TiledRGBResult,
    TiledHannAccumulator,
    _TileBacking,
)


class RecordingSession(BufferSession):
    def __init__(self):
        super().__init__()
        self.device_shapes = []

    def own(self, resource, *, releaser=None):
        if isinstance(resource, TaichiGPUBuffer):
            self.device_shapes.append(tuple(resource.shape))
        return super().own(resource, releaser=releaser)


@pytest.mark.parametrize("shape,block_size", [((45, 59), 64), ((513, 517), 1024)])
@pytest.mark.parametrize("storage", ["ram", "disk"])
def test_tiled_gpu_confidence_matches_resident_hann_with_motion(shape, block_size, storage, tmp_path, monkeypatch):
    monkeypatch.setenv("SPLATSR_SCRATCH_DIR", str(tmp_path))
    rng = np.random.default_rng(728)
    reference = rng.uniform(0.1, 0.85, (*shape, 3)).astype(np.float32)
    support = rng.uniform(0.1, 0.85, (*shape, 3)).astype(np.float32)
    y, x = np.mgrid[:shape[0], :shape[1]].astype(np.float32)
    flow = np.stack((0.35 + 0.2 * np.sin(y / 8), -0.23 + 0.15 * np.cos(x / 9)), axis=-1)
    confidence = (0.25 + 0.75 * x / max(1, shape[1] - 1)).astype(np.float32)
    confidence[shape[0] // 3:shape[0] // 2, shape[1] // 3:shape[1] // 2] = 0.0
    with BufferSession() as session:
        resident = SessionHannAccumulator(
            reference, session=session, block_size=block_size, overlap=0.25
        )
        resident.add_frame(reference, None, np.ones(shape, np.float32))
        resident.add_frame(support, flow, confidence)
        expected = resident.finalize()

    result = None
    session = RecordingSession()
    try:
        tiled = TiledHannAccumulator(
            reference, session=session, block_size=block_size, overlap=0.25,
            asset_dir=os.environ.get("SPLATSR_TEST_TILE_ASSETS"),
            backing_factory=RamAccumulatorBacking if storage == "ram" else _TileBacking,
        )
        tiled.add_frame(reference, None, None)
        device_confidence = session.own(taichi_aot.upload(confidence))
        tiled.add_frame(support, flow, device_confidence)
        assert session.borrowed_count == 0
        assert tiled.readbacks == tiled.tiles_processed
        result = tiled.finalize()
        scratch_directory = result.backing.directory.name if storage == "disk" else None
        session.close()
        assert not result.backing.closed  # explicit ownership transfer
        if storage == "ram":
            assert result.backing.denominator is None
            assert not list(tmp_path.glob("pixelrefine_splat_tiles_*"))
        else:
            assert os.path.isdir(scratch_directory)

        got = np.empty_like(expected)
        for y0, y1, x0, x1, tile in result.iter_tiles(block_size):
            got[y0:y1, x0:x1] = tile
        max_abs = float(np.max(np.abs(got - expected)))
        print(
            f"[TILED SR] backend={tiled.backend} input={reference.shape} "
            f"dtype=float32 tile={block_size} max_abs={max_abs:.8g} "
            f"device={taichi_aot.backend_info()}"
        )
        np.testing.assert_allclose(got, expected, rtol=1e-4, atol=1e-4)
        assert all(
            max(buffer_shape[-3:-1] if len(buffer_shape) == 4 else buffer_shape[:2])
            <= block_size + 7
            for buffer_shape in session.device_shapes
        )
        assert not any(buffer_shape == expected.shape for buffer_shape in session.device_shapes)
        assert tiled.output_shape[0] <= block_size + 7
        assert tiled.output_shape[1] <= block_size + 7
    finally:
        session.close()
        if result is not None:
            result.close()
    assert result.backing.closed
    if scratch_directory is not None:
        assert not os.path.exists(scratch_directory)


def test_requested_hann_configuration_change_only_affects_coverage_edges(tmp_path, monkeypatch):
    """Changing window size changes the existing absolute coverage cutoff.

    Keep that explicit instead of weakening native-graph parity tolerances.
    """
    monkeypatch.setenv("SPLATSR_SCRATCH_DIR", str(tmp_path))
    shape = (513, 517)
    rng = np.random.default_rng(728)
    reference = rng.uniform(0.1, 0.85, (*shape, 3)).astype(np.float32)
    support = rng.uniform(0.1, 0.85, (*shape, 3)).astype(np.float32)
    y, x = np.mgrid[:shape[0], :shape[1]].astype(np.float32)
    flow = np.stack((0.35 + 0.2 * np.sin(y / 8), -0.23 + 0.15 * np.cos(x / 9)), axis=-1)
    confidence = (0.25 + 0.75 * x / (shape[1] - 1)).astype(np.float32)
    with BufferSession() as session:
        resident = SessionHannAccumulator(reference, session=session)
        resident.add_frame(reference, None, np.ones(shape, np.float32))
        resident.add_frame(support, flow, confidence)
        expected = resident.finalize()
    result = None
    try:
        with BufferSession() as session:
            tiled = TiledHannAccumulator(
                reference, session=session,
                asset_dir=os.environ.get("SPLATSR_TEST_TILE_ASSETS"),
            )
            tiled.add_frame(reference, None, None)
            tiled.add_frame(support, flow, confidence)
            result = tiled.finalize()
        got = np.empty_like(expected)
        for y0, y1, x0, x1, tile in result.iter_tiles():
            got[y0:y1, x0:x1] = tile
        np.testing.assert_allclose(got[4:-4, 4:-4], expected[4:-4, 4:-4], atol=1e-4, rtol=1e-4)
        changed_pixels = np.count_nonzero(np.any(np.abs(got - expected) > 1e-4, axis=-1))
        print(f"[HANN CONFIG] backend={tiled.backend} changed_edge_pixels={changed_pixels} total_pixels={got.shape[0]*got.shape[1]} max_abs={np.max(np.abs(got-expected)):.8g}")
        assert changed_pixels <= 16
    finally:
        if result is not None:
            result.close()


def test_cancel_during_tiles_releases_backing_and_confidence_borrow(tmp_path, monkeypatch):
    monkeypatch.setenv("SPLATSR_SCRATCH_DIR", str(tmp_path))
    reference = np.full((45, 59, 3), 0.3, dtype=np.float32)
    checks = 0

    def check_cancelled():
        nonlocal checks
        checks += 1
        if checks == 2:
            raise RuntimeError("injected tile cancellation")

    session = BufferSession()
    accumulator = TiledHannAccumulator(
        reference, session=session, block_size=64, check_cancelled=check_cancelled,
        asset_dir=os.environ.get("SPLATSR_TEST_TILE_ASSETS"),
    )
    backing = accumulator.backing
    confidence = session.own(taichi_aot.upload(np.ones(reference.shape[:2], np.float32)))
    try:
        with pytest.raises(RuntimeError, match="injected tile cancellation"):
            accumulator.add_frame(reference, None, confidence)
        assert session.borrowed_count == 0
    finally:
        session.close()
    assert session.owned_count == 0
    assert backing.closed
    assert backing.numerator is backing.denominator is None
    assert not list(tmp_path.glob("pixelrefine_splat_tiles_*"))


@pytest.mark.parametrize("linear_dng", [False, True])
@pytest.mark.parametrize("storage", ["ram", "disk"])
def test_splat_save_reads_tiled_result_and_cleans_up(tmp_path, monkeypatch, linear_dng, storage):
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr import legacy
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.legacy import (
        _save_mfd_compatible_result,
    )

    image = np.random.default_rng(87).uniform(0.0, 1.0, (65, 77, 3)).astype(np.float32)
    backing = RamAccumulatorBacking(image.shape) if storage == "ram" else _TileBacking(image.shape, directory=tmp_path)
    with backing.region(backing.numerator_path, 0, 65, 0, 77, channels=3, writable=True) as tile:
        tile[:] = image
    result = TiledRGBResult(backing) if storage == "ram" else DiskBackedRGB(backing)
    with pytest.raises(TypeError, match="rectangular tiles"):
        np.asarray(result)
    output = tmp_path / "result.tif"
    reference_path = None
    if linear_dng:
        monkeypatch.setattr(legacy, "_mfd_linear_mode", lambda path: True)
        reference_path = str(tmp_path / "reference-not-present.dng")
    expected_path = output.with_suffix(".dng") if linear_dng else output
    assert _save_mfd_compatible_result(result, str(output), reference_path) == str(expected_path)
    expected_image = np.clip(image * 65535.0 + 0.5, 0.0, 65535.0).astype(np.uint16)
    if linear_dng:
        # Existing linear writer's channel-order contract is preserved.
        expected_image = expected_image[..., ::-1]
    np.testing.assert_array_equal(
        tifffile.imread(expected_path), expected_image,
    )
    assert backing.closed
    if storage == "disk":
        assert not os.path.exists(backing.directory.name)
    else:
        assert backing.numerator is backing.denominator is None


@pytest.mark.parametrize("storage", ["ram", "disk"])
def test_output_failure_closes_transferred_tiled_result(tmp_path, monkeypatch, storage):
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr import legacy

    backing = RamAccumulatorBacking((8, 9, 3)) if storage == "ram" else _TileBacking((8, 9, 3), directory=tmp_path)
    result = TiledRGBResult(backing) if storage == "ram" else DiskBackedRGB(backing)

    def fail_writer(*args, **kwargs):
        raise OSError("injected output failure")

    monkeypatch.setattr(legacy, "save_image_streaming", fail_writer)
    with pytest.raises(OSError, match="injected output failure"):
        legacy._save_mfd_compatible_result(result, str(tmp_path / "result.tif"))
    assert backing.closed
    if storage == "disk":
        assert not os.path.exists(backing.directory.name)
    else:
        assert backing.numerator is backing.denominator is None


@pytest.mark.parametrize("prefetch,refinement", [(0, 0), (2, 1), (4, 0)])
def test_public_pipeline_shared_spatial_and_refinement_cleanup(tmp_path, monkeypatch, prefetch, refinement):
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_SR import run_splat_sr_pipeline
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.streaming_pipeline import ImagePathSource

    monkeypatch.setenv("SPLATSR_SCRATCH_DIR", str(tmp_path))
    def forbid_disk(*args, **kwargs):
        raise AssertionError("active reconstruction must not create disk backing")
    monkeypatch.setattr(_TileBacking, "__init__", forbid_disk)
    rng = np.random.default_rng(812)
    reference = rng.uniform(0.05, 0.7, (96, 96, 3)).astype(np.float32)

    def load(self, index):
        # Decoder alone is replaced; AutoEnhance, alignment, shared spatial,
        # tile reconstruction, refinement and output writer remain native.
        return np.roll(reference, int(index), axis=1).copy()

    monkeypatch.setattr(ImagePathSource, "_load", load)
    output = tmp_path / "pipeline.tif"
    result = run_splat_sr_pipeline(
        ["ref.png", "support-a.png", "support-b.png"],
        output_path=str(output), prefetch_depth=prefetch,
        refinement_iterations=refinement,
    )
    assert result == str(output)
    image = tifffile.imread(output)
    assert image.shape == (192, 192, 3)
    assert image.dtype == np.uint16
    assert not list(tmp_path.glob("pixelrefine_splat_tiles_*"))


def test_repeated_jobs_and_empty_coverage_use_same_backend_bicubic(tmp_path, monkeypatch):
    monkeypatch.setenv("SPLATSR_SCRATCH_DIR", str(tmp_path))
    for shape in ((73, 89), (31, 41), (73, 89)):
        reference = np.random.default_rng(24).uniform(0.0, 0.8, (*shape, 3)).astype(np.float32)
        result = None
        session = BufferSession()
        try:
            tiled = TiledHannAccumulator(
                reference, session=session, block_size=64,
                asset_dir=os.environ.get("SPLATSR_TEST_TILE_ASSETS"),
            )
            tiled.add_frame(reference, None, np.zeros(shape, np.float32))
            result = tiled.finalize()
            expected = taichi_aot.resize(
                reference, (shape[1] * 2, shape[0] * 2),
                interpolation=taichi_aot.INTER_CUBIC,
            )
            got = np.empty_like(expected)
            for y0, y1, x0, x1, tile in result.iter_tiles(64):
                got[y0:y1, x0:x1] = tile
            # Bicubic resize uses fp32 local coordinates on a source halo;
            # allow < one uint16 level, rather than require bit-exact rounding.
            np.testing.assert_allclose(got, expected, atol=1e-5, rtol=1e-5)
        finally:
            session.close()
            if result is not None:
                result.close()
        assert session.owned_count == session.borrowed_count == 0
        assert not list(tmp_path.glob("pixelrefine_splat_tiles_*"))
