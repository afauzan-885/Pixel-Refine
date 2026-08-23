"""Opt-in same-backend spatial block parity harness.

The test is skipped by default because it initializes the active AOT runtime
and executes the native spatial TCM twice.  Run it in a fresh process with
``PIXEL_REFINE_RUN_SPATIAL_NATIVE_PARITY=1`` and an explicit
``PIXEL_REFINE_AOT_ARCH`` (cpu/cuda/vulkan/opengl) to collect evidence for one
backend/device/shape/dtype configuration.  Passing this test does not by
itself promote the global production gate; promotion requires the documented
matrix of target devices and parameters.
"""

import os

import numpy as np
import pytest


pytestmark = pytest.mark.skipif(
    os.environ.get("PIXEL_REFINE_RUN_SPATIAL_NATIVE_PARITY") != "1",
    reason="native spatial parity is opt-in and requires a fresh AOT process",
)


def test_native_spatial_block_matches_same_backend_full_frame(monkeypatch):
    monkeypatch.setenv("AOT_MODE", "1")
    arch = os.environ.get("PIXEL_REFINE_AOT_ARCH")
    if not arch:
        pytest.skip("set PIXEL_REFINE_AOT_ARCH explicitly for native evidence")

    import taichi_vision.taichi_aot as taichi_aot
    import pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion as spatial_fusion

    engine = taichi_aot.engine
    module_path = spatial_fusion.process_in_gpu.__module__
    assert module_path.endswith("spatial_pipeline")

    # Small, deterministic RGB stack with enough area for multiple 64px
    # blocks.  Both runs use the same engine/context and parameters.
    height, width = 96, 112
    yy, xx = np.mgrid[:height, :width]
    base = np.stack(
        (
            (xx / max(1, width - 1)),
            (yy / max(1, height - 1)),
            ((xx + yy) / max(1, width + height - 2)),
        ),
        axis=-1,
    ).astype(np.float32)
    images = [base.copy(), np.roll(base, 1, axis=1)]
    reference = base.copy()
    processor = spatial_fusion.SpatialFusionProcessor()

    def run(requested):
        result = processor.process(
            images=[frame.copy() for frame in images],
            ref_image_h=height,
            ref_image_w=width,
            ref_channels_buffer=3,
            ref_dtype=np.float32,
            reference_image_float=reference.copy(),
            tile_size=(16, 16),
            overlap=0.25,
            motion_sensitivity=150.0,
            noise_offset_factor=0.15,
            enable_alignment=False,
            return_raw=True,
            spatial_block_requested=requested,
            spatial_block_size=64,
            spatial_block_halo=16,
        )
        # The raw contract is (image_sum, weight_sum, processed_count).
        return result

    full_result = run(False)
    # This opt-in test deliberately exercises the guarded candidate.  The
    # production module remains fail-closed after the test process exits.
    monkeypatch.setattr(spatial_fusion, "SPATIAL_BLOCK_PARITY_CERTIFIED", True)
    block_result = run(True)
    report = spatial_fusion.run_spatial_block_parity_probe(
        lambda: full_result,
        lambda: block_result,
        backend=str(getattr(engine, "arch", arch)),
        device=str(getattr(engine, "device_name", "unknown")),
        block_size=64,
        atol=spatial_fusion.SPATIAL_BLOCK_PARITY_ATOL,
        rtol=spatial_fusion.SPATIAL_BLOCK_PARITY_RTOL,
    )

    # Backend float32 reductions may differ by a few ulps while retaining a
    # very small relative loss.  The relaxed quality gate is the acceptance
    # criterion for this probe; strict max-abs status remains in the report.
    assert report["quality_passed"], report
