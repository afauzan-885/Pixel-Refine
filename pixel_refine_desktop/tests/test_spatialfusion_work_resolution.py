"""Routing contract for SpatialFusion's dedicated work resolution control."""

from types import SimpleNamespace

import pytest

from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
    PARAMETER_SCHEMA,
    normalize_similarity_spatial_config,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.SpatialFusion import (
    SpatialFusionDenoisingAlgorithm,
)


def test_spatial_resolution_has_full_size_default_and_own_ui_field():
    field = next(
        item for item in PARAMETER_SCHEMA
        if item["key"] == "similarity_spatial_work_resolution"
    )
    assert field["default"] == 1.0
    assert 0.5 in field["options"]
    assert normalize_similarity_spatial_config(
        {"work_resolution_scale": 0.5}
    )["similarity_spatial_work_resolution"] == 1.0


@pytest.mark.parametrize("scale", [1.0, 0.75, 0.5, 0.33, 0.25])
def test_spatial_resolution_reaches_both_analysis_grids(monkeypatch, scale):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process import (
        resident_pipeline,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import SpatialFusion

    received = {}

    def run_stub(_paths, **kwargs):
        received.update(kwargs)
        return None, 0.0

    monkeypatch.setattr(resident_pipeline, "run_resident_pipeline", run_stub)
    monkeypatch.setattr(SpatialFusion, "active_backend", lambda: "cpu")
    monkeypatch.setattr(
        SpatialFusionDenoisingAlgorithm,
        "load_config",
        staticmethod(lambda: {"work_resolution_scale": 0.5}),
    )
    ctx = SimpleNamespace(
        image_paths=["reference.dng", "support.dng"],
        params={"similarity_spatial_work_resolution": scale},
        alignment_selection_name="Farneback",
        is_linear_mode=True,
        is_raw_native=True,
        stop_requested=None,
        update_progress=None,
    )

    assert SpatialFusionDenoisingAlgorithm().run(ctx) is None
    assert received["weight_engine"] == "spatial_fusion"
    assert received["work_scale"] == scale
    assert received["flownet_work_scale"] == scale
    assert received["weightnet_work_scale"] == scale
    assert received["max_work_dimension"] is None


def test_batch_spatial_resolution_overrides_global_default():
    config = SpatialFusionDenoisingAlgorithm()._resolve_config(
        SimpleNamespace(
            params={
                "similarity_spatial_work_resolution": 1.0,
                "similarity_params": {"similarity_spatial_work_resolution": 0.5},
            }
        )
    )
    assert config["similarity_spatial_work_resolution"] == 0.5
