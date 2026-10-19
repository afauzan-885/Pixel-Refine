"""Ground-truth gates for the deployed resident Block Flow archive.

Run in a fresh process per backend. A candidate may be selected using
PIXEL_REFINE_AOT_TCM_ROOT before import, exactly as the native resolver does.
"""
import numpy as np
import pytest

from taichi_vision.taichi_algorithm.aot_py.tools.probe_compute_flow_quality import (
    quality_cases,
    run_flow,
)


@pytest.mark.parametrize("smooth", (False, True))
@pytest.mark.parametrize("case", list(quality_cases()), ids=lambda case: case[0])
def test_resident_flow_ground_truth(case, smooth):
    name, ref, comp, truth, mask, limit = case
    flow = run_flow(ref, comp, smooth=smooth)
    assert flow.shape == (*ref.shape, 2)
    assert flow.dtype == np.float32
    assert np.isfinite(flow).all()
    error = np.linalg.norm(flow[mask] - np.float32(truth), axis=1)
    assert error.mean() <= limit, (name, smooth, error.mean(), limit)
    if "sky" in name:
        assert error.max() <= .1, (name, smooth, error.max())


@pytest.mark.parametrize("smooth", (False, True))
@pytest.mark.parametrize("shape", ((31, 49), (64, 80), (127, 173), (128, 172)))
def test_partial_tiles_are_finite_and_cover_identity(shape, smooth):
    rng = np.random.default_rng(145)
    ref = np.float32(rng.random(shape))
    flow = run_flow(ref, ref.copy(), smooth=smooth)
    assert flow.shape == (*shape, 2)
    assert np.isfinite(flow).all()
    np.testing.assert_allclose(flow, 0., atol=.02, rtol=0.)


@pytest.mark.parametrize("shape", ((31, 49), (64, 80), (127, 173)))
def test_hann_blend_matches_numpy_with_half_tile_overlap(shape):
    from taichi_vision import taichi_aot as aot
    engine = aot.get_engine()
    h, w = shape
    roots_y, roots_x = (h + 15) // 16, (w + 15) // 16
    rng = np.random.default_rng(148)
    grid = rng.normal(size=(roots_y * 8, roots_x * 8, 2)).astype(np.float32)
    expected = np.zeros((h, w, 2), np.float64)
    weights = np.zeros((h, w), np.float64)
    hann = .5 - .5 * np.cos(2 * np.pi * (np.arange(32) + .5) / 32)
    window = hann[:, None] * hann[None, :]
    for iy in range(roots_y):
        for ix in range(roots_x):
            y, x = iy * 16, ix * 16
            th, tw = min(32, h - y), min(32, w - x)
            cells = np.repeat(np.repeat(grid[iy * 8:(iy + 1) * 8, ix * 8:(ix + 1) * 8], 4, 0), 4, 1)
            expected[y:y + th, x:x + tw] += cells[:th, :tw] * window[:th, :tw, None]
            weights[y:y + th, x:x + tw] += window[:th, :tw]
    expected /= weights[..., None]
    source = engine.allocate(grid.shape, dtype=np.float32, is_vector=False)
    engine.write_into(source, grid)
    output = engine.allocate((h, w, 2), dtype=np.float32, is_vector=False)
    try:
        aot.load_tcm("compute_flow").run("flow_adaptive_hann_stitch",
                                        grid_flow_l0=source, flow_l0_raw=output)
        engine.sync()
        # Shader cos() is approximate on graphics devices. The observed
        # deviation is below 0.0001 px; keep a 0.0002 px absolute gate there.
        tolerance = 2e-4 if aot.backend_info()["backend"] in {"vulkan", "opengl", "gles"} else 3e-6
        np.testing.assert_allclose(output.to_numpy(), expected, atol=tolerance, rtol=1e-5)
    finally:
        engine.sync()
        output.release()
        source.release()
