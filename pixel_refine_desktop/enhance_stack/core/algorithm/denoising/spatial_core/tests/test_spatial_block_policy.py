"""Pure tests for the spatial block execution gate.

These tests intentionally do not initialize Taichi or load a native TCM.  The
production gate must fail closed when a same-backend crop/stitch oracle has not
been recorded.
"""

import pytest
import numpy as np

import pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion as spatial_fusion

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion import (
    SPATIAL_BLOCK_PARITY_CERTIFIED,
    SpatialFusionProcessor,
    _normalize_spatial_block_size,
    _spatial_parity_report,
    run_spatial_block_parity_probe,
    _select_spatial_execution_mode,
)


def test_block_request_falls_back_until_parity_is_certified():
    assert SPATIAL_BLOCK_PARITY_CERTIFIED is False

    decision = _select_spatial_execution_mode(True, 1024)

    assert decision == {
        "requested": True,
        "enabled": False,
        "mode": "full_frame",
        "block_size": 1024,
        "reason": "spatial tile/halo stitch parity is not certified",
    }


def test_non_block_request_keeps_full_frame_mode():
    decision = _select_spatial_execution_mode(False, 1024)

    assert decision["requested"] is False
    assert decision["enabled"] is False
    assert decision["mode"] == "full_frame"
    assert decision["reason"] == "not requested"


def test_parity_report_checks_image_weight_and_count():
    image = np.ones((2, 3, 1), dtype=np.float32)
    weight = np.ones((2, 3), dtype=np.float32)
    result = (image, weight, 2)

    report = _spatial_parity_report(result, (image.copy(), weight.copy(), 2))

    assert report["passed"] is True
    assert report["reason"] == "parity passed"
    assert report["image"]["max_abs"] == 0.0
    assert report["weight"]["max_abs"] == 0.0
    assert report["image"]["rmse"] == 0.0
    assert report["weight"]["relative_l1"] == 0.0
    assert report["loss_score"] == 0.0
    assert report["quality_passed"] is True
    assert report["count"]["equal"] is True


def test_parity_report_fails_on_weight_or_count_mismatch():
    image = np.ones((2, 3, 1), dtype=np.float32)
    weight = np.ones((2, 3), dtype=np.float32)
    candidate_weight = weight.copy()
    candidate_weight[0, 0] += np.float32(2.0e-6)

    report = _spatial_parity_report(
        (image, weight, 2),
        (image.copy(), candidate_weight, 3),
    )

    assert report["passed"] is False
    assert report["reason"] == "image or weight mismatch"
    # The candidate is float32, so the representable increment is slightly
    # above the requested 2e-6 value.
    assert report["weight"]["max_abs"] == pytest.approx(2.0e-6, abs=5.0e-8)
    assert report["loss_score"] > 0.0
    # A low numeric loss cannot qualify a run with a processed-frame count
    # mismatch; quality qualification still requires structural parity.
    assert report["quality_passed"] is False
    assert report["count"]["equal"] is False


def test_parity_report_rejects_dtype_mismatch_even_when_values_match():
    image32 = np.ones((1, 2, 1), dtype=np.float32)
    weight32 = np.ones((1, 2), dtype=np.float32)
    image64 = image32.astype(np.float64)
    weight64 = weight32.astype(np.float64)

    report = _spatial_parity_report(
        (image32, weight32, 1),
        (image64, weight64, 1),
    )

    assert report["passed"] is False
    assert report["reason"] == "image or weight mismatch"
    assert report["image"]["dtype"]["equal"] is False


def test_native_probe_keeps_backend_metadata_and_does_not_open_gate():
    image = np.zeros((1, 1, 1), dtype=np.float32)
    weight = np.ones((1, 1), dtype=np.float32)

    report = run_spatial_block_parity_probe(
        lambda: (image, weight, 1),
        lambda: (image.copy(), weight.copy(), 1),
        backend="cuda",
        device="test-device",
        block_size=1024,
    )

    assert report["passed"] is True
    assert report["backend"] == "cuda"
    assert report["device"] == "test-device"
    assert report["block_size"] == 1024
    # A single synthetic pass is not sufficient to promote production mode.
    assert spatial_fusion.SPATIAL_BLOCK_PARITY_CERTIFIED is False


def test_parity_report_rejects_identical_empty_native_fallbacks():
    """Two zero-count fallbacks are not evidence that native parity passed.

    The spatial pipeline deliberately catches backend errors and returns an
    empty raw result so the caller can recover.  The native parity harness
    must therefore require a positive processed-frame count; otherwise a
    missing/quarantined TCM could produce two identical zero arrays and a
    false green parity result.
    """
    image = np.zeros((2, 2, 1), dtype=np.float32)
    weight = np.zeros((2, 2), dtype=np.float32)

    report = _spatial_parity_report(
        (image, weight, 0),
        (image.copy(), weight.copy(), 0),
    )

    assert report["passed"] is False
    assert report["count"]["equal"] is True
    assert report["count"]["positive"] is False
    assert report["reason"] == "no processed frames; native runner likely failed"


def test_block_size_is_aligned_and_bounded_for_diagnostics():
    assert _normalize_spatial_block_size(None) == 1024
    assert _normalize_spatial_block_size("bad") == 1024
    assert _normalize_spatial_block_size(513) == 512
    assert _normalize_spatial_block_size(7) == 64


def test_uncertified_crop_helper_fails_closed():
    with pytest.raises(RuntimeError, match="parity has not been certified"):
        SpatialFusionProcessor._process_image_blocks(
            images=[],
            reference_image_float=None,
            ref_image_h=1,
            ref_image_w=1,
            backend_args={},
            block_size=1024,
            halo=16,
        )


def test_certified_crop_path_stitches_normalized_oracle(monkeypatch):
    """The crop path must match one full-frame raw-sum oracle.

    This deliberately substitutes a deterministic backend function.  It tests
    the host-side halo/crop/stitch contract without loading a TCM or claiming
    native backend parity.
    """
    monkeypatch.setattr(spatial_fusion, "SPATIAL_BLOCK_PARITY_CERTIFIED", True)
    reference = np.arange(8 * 10 * 3, dtype=np.float32).reshape(8, 10, 3)

    def fake_process_in_gpu(**kwargs):
        crop = np.asarray(kwargs["reference_image_float"], dtype=np.float32)
        raw_sum = crop * np.float32(2.0) + np.float32(1.0)
        weights = np.ones(crop.shape[:2], dtype=np.float32)
        return 1, raw_sum, weights, 0.0

    monkeypatch.setattr(spatial_fusion, "process_in_gpu", fake_process_in_gpu)
    args = {
        "images": [reference],
        "reference_image_float": reference,
        "ref_image_h": 8,
        "ref_image_w": 10,
        "ref_channels_buffer": 3,
        "ref_dtype": np.float32,
        "work_res_h": 8,
        "work_res_w": 10,
        "tile_h": 2,
        "tile_w": 2,
        "overlap": 0.0,
        "row_starts": np.asarray([0, 2, 4, 6], dtype=np.int32),
        "col_starts": np.asarray([0, 2, 4, 6, 8], dtype=np.int32),
        "base_window": None,
    }
    _, stitched, weights, _ = SpatialFusionProcessor._process_image_blocks(
        images=[reference],
        reference_image_float=reference,
        ref_image_h=8,
        ref_image_w=10,
        backend_args=args,
        block_size=4,
        halo=1,
        return_raw=False,
    )

    expected = reference * np.float32(2.0) + np.float32(1.0)
    np.testing.assert_allclose(stitched, expected, rtol=0.0, atol=0.0)
    np.testing.assert_array_equal(weights, np.ones((8, 10), dtype=np.float32))


def test_certified_crop_path_preserves_raw_sum_mode(monkeypatch):
    monkeypatch.setattr(spatial_fusion, "SPATIAL_BLOCK_PARITY_CERTIFIED", True)
    reference = np.arange(5 * 7 * 2, dtype=np.float32).reshape(5, 7, 2)

    def fake_process_in_gpu(**kwargs):
        crop = np.asarray(kwargs["reference_image_float"], dtype=np.float32)
        return 2, crop + np.float32(3.0), np.ones(crop.shape[:2], dtype=np.float32), 0.0

    monkeypatch.setattr(spatial_fusion, "process_in_gpu", fake_process_in_gpu)
    args = {
        "tile_h": 2,
        "tile_w": 2,
        "row_starts": np.asarray([0, 2, 4], dtype=np.int32),
        "col_starts": np.asarray([0, 2, 4], dtype=np.int32),
    }
    processed, raw_sum, weights, _ = SpatialFusionProcessor._process_image_blocks(
        images=[reference],
        reference_image_float=reference,
        ref_image_h=5,
        ref_image_w=7,
        backend_args=args,
        block_size=4,
        halo=1,
        return_raw=True,
    )

    assert processed == 2
    np.testing.assert_array_equal(raw_sum, reference + np.float32(3.0))
    np.testing.assert_array_equal(weights, np.ones((5, 7), dtype=np.float32))
