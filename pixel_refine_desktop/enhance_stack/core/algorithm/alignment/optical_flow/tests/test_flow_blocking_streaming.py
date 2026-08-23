"""Regression tests for bounded optical-flow tile streaming."""

from types import SimpleNamespace
from unittest.mock import patch
import sys

import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    _cached_coordinate_grid,
    _cached_weight_mask,
    _accumulate_weighted_tile,
    _should_parallelize,
    align_with_block_flow,
    align_with_tiled_flow,
)


def _zero_flow(gray, _target):
    return np.zeros((*gray.shape, 2), dtype=np.float32)


def test_tiled_streaming_preserves_accumulation_order():
    rng = np.random.default_rng(20260822)
    reference = rng.integers(0, 256, (80, 96, 3), dtype=np.uint8)
    target = reference.copy()

    sequential = align_with_tiled_flow(
        reference,
        target,
        _zero_flow,
        cols=3,
        rows=2,
        use_multi_core=False,
    )
    streamed = align_with_tiled_flow(
        reference,
        target,
        _zero_flow,
        cols=3,
        rows=2,
        use_multi_core=True,
    )

    assert np.array_equal(streamed, sequential)


def test_small_tiled_frame_avoids_local_thread_pool():
    """Small previews stay sequential; API callers need no new flag."""
    rng = np.random.default_rng(20260823)
    reference = rng.integers(0, 256, (128, 160, 3), dtype=np.uint8)

    with patch(
        "pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow"
        ".optical_flow_utils.flow_blocking.concurrent.futures.ThreadPoolExecutor"
    ) as executor:
        result = align_with_tiled_flow(
            reference,
            reference.copy(),
            _zero_flow,
            cols=3,
            rows=2,
            use_multi_core=True,
        )

    assert result is not None
    executor.assert_not_called()


def test_parallel_threshold_respects_shared_executor_and_override(monkeypatch):
    assert not _should_parallelize(128, 160, 6, True, None)
    assert _should_parallelize(128, 160, 6, True, object())

    monkeypatch.setenv("PIXEL_REFINE_FLOW_PARALLEL_MIN_PIXELS", "1")
    assert _should_parallelize(128, 160, 2, True, None)


def test_tile_coordinate_and_weight_buffers_are_reused_for_small_tiles():
    first_grid = _cached_coordinate_grid(32, 48)
    second_grid = _cached_coordinate_grid(32, 48)
    first_mask = _cached_weight_mask(32, 48)
    second_mask = _cached_weight_mask(32, 48)

    assert first_grid is second_grid
    assert first_mask is second_mask
    assert not first_grid[0].flags.writeable
    assert not first_mask.flags.writeable


def test_large_coordinate_grid_is_not_retained_by_cache():
    # A full-resolution image must not be pinned by the process-wide cache.
    assert _cached_coordinate_grid(2048, 2048) is None


def test_uncovered_pixels_restore_target_without_float_copy():
    rng = np.random.default_rng(20260824)
    target = rng.integers(0, 65535, (64, 80, 3), dtype=np.uint16)
    calls = 0

    def stop_after_three_tiles():
        nonlocal calls
        calls += 1
        return calls > 3

    result = align_with_tiled_flow(
        target,
        target.copy(),
        _zero_flow,
        cols=2,
        rows=2,
        use_multi_core=False,
        stop_requested=stop_after_three_tiles,
    )

    assert result.dtype == target.dtype
    # The last 2x2 tile is cancelled and therefore restored directly from
    # the target; processed tiles may differ by one uint16 interpolation LSB.
    assert np.array_equal(result[32:, 40:], target[32:, 40:])


def test_in_place_weighted_tile_accumulation_matches_reference_expression():
    rng = np.random.default_rng(20260825)
    warped = rng.random((7, 9, 3), dtype=np.float32)
    weight = rng.random((7, 9), dtype=np.float32)
    expected = np.zeros_like(warped)
    expected += warped * weight[..., None]

    actual = np.zeros_like(warped)
    height, width = _accumulate_weighted_tile(
        actual, warped.copy(), weight, 0, 0
    )

    assert (height, width) == (7, 9)
    np.testing.assert_array_equal(actual, expected)


def test_block_flow_accepts_lazy_block_iterator(monkeypatch):
    """Large runtime grids must not require ``len(blocks)`` or list materialization."""
    class _Config:
        enabled = True

        @staticmethod
        def normalized_size():
            return 4

    def lazy_blocks(width, height, halo=0):
        for y0 in (0, 4):
            for x0 in (0, 4):
                yield {
                    "valid": (x0, y0, min(x0 + 4, width), min(y0 + 4, height)),
                    "roi": (x0, y0, min(x0 + 4, width), min(y0 + 4, height)),
                }

    fake_aot = SimpleNamespace(get_block_config=lambda: _Config())
    fake_package = SimpleNamespace(taichi_aot=fake_aot)
    monkeypatch.setitem(sys.modules, "taichi_vision", fake_package)
    monkeypatch.setattr(
        "pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow"
        ".optical_flow_utils.flow_blocking.iter_runtime_flow_blocks",
        lazy_blocks,
    )

    def zero_flow(gray, _target):
        return np.zeros((*gray.shape, 2), dtype=np.float32)

    image = np.zeros((8, 8), dtype=np.uint8)
    result = align_with_block_flow(
        image,
        image.copy(),
        zero_flow,
        use_multi_core=False,
    )

    assert result.shape == image.shape
    assert result.dtype == image.dtype
    np.testing.assert_array_equal(result, image)


def test_block_flow_counts_rectangular_runtime_blocks(monkeypatch):
    """Tuple-valued normalized sizes must not crash block dispatch."""
    class _Config:
        enabled = True

        @staticmethod
        def normalized_size():
            return (4, 8)

    def blocks(width, height, halo=0):
        for y0 in range(0, height, 4):
            for x0 in range(0, width, 8):
                yield {
                    "valid": (x0, y0, min(x0 + 8, width), min(y0 + 4, height)),
                    "roi": (x0, y0, min(x0 + 8, width), min(y0 + 4, height)),
                }

    fake_aot = SimpleNamespace(get_block_config=lambda: _Config())
    monkeypatch.setitem(
        sys.modules,
        "taichi_vision",
        SimpleNamespace(taichi_aot=fake_aot),
    )
    monkeypatch.setattr(
        "pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow"
        ".optical_flow_utils.flow_blocking.iter_runtime_flow_blocks",
        blocks,
    )

    image = np.zeros((8, 16), dtype=np.uint8)
    result = align_with_block_flow(image, image.copy(), _zero_flow, use_multi_core=False)
    assert result.shape == image.shape
    np.testing.assert_array_equal(result, image)
