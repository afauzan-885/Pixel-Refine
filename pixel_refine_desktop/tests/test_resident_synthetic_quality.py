"""Analytic scene and metric contracts; production AOT probe is a separate CLI."""
import numpy as np
import pytest

from test_algorithm.validate_resident_burst_quality import mosaic, region_metrics, scene


def test_four_frame_scene_has_known_jitter_and_independent_motion():
    reference, ref_mask, jitter = scene(512, 0)
    assert reference.shape == (512, 512, 3)
    assert reference.dtype == np.float32
    assert jitter == (0., 0.)
    np.testing.assert_array_equal(reference, scene(512, 0)[0])
    assert 0 < reference.min() < reference.max() < 1
    for index, expected in enumerate(((.8, -1.3), (-1.1, .6), (1.5, 1.)), 1):
        support, _, camera = scene(512, index)
        assert camera == expected
        world, mask, _ = scene(512, index, jitter=False)
        assert np.any(mask != ref_mask)
        assert np.mean(np.abs(world[ref_mask] - reference[ref_mask])) > .02
        assert not np.array_equal(support, world)
    cfa = mosaic(reference)
    np.testing.assert_array_equal(cfa[::2, ::2], reference[::2, ::2, 0])
    np.testing.assert_array_equal(cfa[1::2, 1::2], reference[1::2, 1::2, 2])


def test_metric_truth_and_naive_ghost_controls_have_known_scores():
    truth = np.zeros((16, 16, 3), np.float32)
    naive = np.ones_like(truth) * .2
    noisy_ref = np.ones_like(truth) * .1
    masks = {"static": np.ones((16, 16), bool), "moving": np.ones((16, 16), bool)}
    clean = region_metrics(truth, truth, noisy_ref, naive, masks)
    ghost = region_metrics(naive, truth, noisy_ref, naive, masks)
    assert clean["static"]["noise_rmse_reduction_percent"] == 100.
    assert clean["moving"]["ghost_projection_percent"] == 0.
    assert ghost["moving"]["ghost_projection_percent"] == pytest.approx(100.)
    with pytest.raises(AssertionError):
        region_metrics(np.full_like(truth, np.nan), truth, noisy_ref, naive, masks)
