from types import SimpleNamespace

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet import (
    FusionNetDenoisingAlgorithm,
)


def test_fusionnet_panel_values_override_generic_similarity_aliases():
    ctx = SimpleNamespace(
        batch_id=None,
        params={
            # Generic fields are deliberately different; FusionNet's own
            # canonical fields must win.
            "work_scale": 0.50,
            "tile_size": 1024,
            "fusionnet_work_resolution": 0.25,
            "fusionnet_tile_size": 256,
        },
        alignment_selection_name=None,
    )

    resolved = FusionNetDenoisingAlgorithm()._resolve_config(ctx)

    assert resolved["work_scale"] == 0.25
    assert resolved["tile_size"] == 256


def test_batch_fusionnet_payload_is_authoritative():
    ctx = SimpleNamespace(
        batch_id=None,
        params={
            "fusionnet_work_resolution": 1.0,
            "fusionnet_tile_size": 1024,
            "fusionnet_params": {
                "fusionnet_work_resolution": 0.33,
                "fusionnet_tile_size": 512,
            },
        },
        alignment_selection_name=None,
    )

    resolved = FusionNetDenoisingAlgorithm()._resolve_config(ctx)

    assert resolved["work_scale"] == 0.33
    assert resolved["tile_size"] == 512


def test_fusionnet_default_ghost_penalty_maximum_is_one():
    ctx = SimpleNamespace(
        batch_id=None,
        params={},
        alignment_selection_name=None,
    )

    resolved = FusionNetDenoisingAlgorithm()._resolve_config(ctx)

    assert resolved["ghost_penalty"] == 1.0
    assert resolved["ghost_penalty_min"] == 0.65
