import math
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


def test_fusionnet_default_ghost_penalty_maximum_is_one(monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising import (
        fusionnet_parameter_settings,
    )

    monkeypatch.setattr(
        fusionnet_parameter_settings,
        "load_fusionnet_config_for_batch",
        lambda _batch_id: {
            "ghost_penalty": 1.0,
            "ghost_penalty_min": 0.65,
        },
    )
    ctx = SimpleNamespace(
        batch_id=None,
        params={},
        alignment_selection_name=None,
    )

    resolved = FusionNetDenoisingAlgorithm()._resolve_config(ctx)

    assert resolved["ghost_penalty"] == 1.0
    assert resolved["ghost_penalty_min"] == 0.65


def test_pixel_resolution_percent_is_total_pixel_fraction(monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising import (
        fusionnet_parameter_settings,
    )

    context = SimpleNamespace(
        batch_id=None,
        params={},
        alignment_selection_name=None,
    )

    for pixel_fraction, expected_scale in (
        (0.25, 0.50),
        (0.50, math.sqrt(0.50)),
        (1.0, 1.0),
    ):
        monkeypatch.setattr(
            fusionnet_parameter_settings,
            "load_fusionnet_config_for_batch",
            lambda _batch_id, fraction=pixel_fraction: {
                "fusionnet_work_pixel_fraction": fraction
            },
        )
        resolved = FusionNetDenoisingAlgorithm()._resolve_config(context)

        assert resolved["work_pixel_fraction"] == pixel_fraction
        assert math.isclose(resolved["work_scale"], expected_scale)


def test_legacy_linear_resolution_keeps_its_previous_effective_dimensions():
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.fusionnet_parameter_settings import (
        _normalize_fusionnet_config,
    )

    migrated = _normalize_fusionnet_config({"fusionnet_work_resolution": 0.50})

    assert migrated["fusionnet_work_pixel_fraction"] == 0.25
    context = SimpleNamespace(
        batch_id=None,
        params={"fusionnet_work_resolution": 0.50},
        alignment_selection_name=None,
    )
    resolved = FusionNetDenoisingAlgorithm()._resolve_config(context)
    assert resolved["work_pixel_fraction"] == 0.25
    assert resolved["work_scale"] == 0.50


def test_deep_analysis_candidate_controls_resolve_and_clamp():
    context = SimpleNamespace(
        batch_id=None,
        params={
            "fusionnet_denoising_mode": "deep_analysis",
            "fusionnet_max_neighbor_candidates": 9,
            "fusionnet_patch_search_radius": 12,
        },
        alignment_selection_name=None,
    )

    resolved = FusionNetDenoisingAlgorithm()._resolve_config(context)

    assert resolved["denoising_mode"] == "deep_analysis"
    assert resolved["max_neighbor_candidates"] == 9
    assert resolved["patch_search_radius"] == 12

    context.params.update(
        {
            "fusionnet_max_neighbor_candidates": 99,
            "fusionnet_patch_search_radius": 0,
        }
    )
    clamped = FusionNetDenoisingAlgorithm()._resolve_config(context)
    assert clamped["max_neighbor_candidates"] == 16
    assert clamped["patch_search_radius"] == 1


def test_deep_analysis_neighbor_controls_are_sliders_with_defaults():
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.fusionnet_parameter_settings import (
        FUSIONNET_DEFAULTS,
        PARAMETER_SCHEMA,
        _normalize_fusionnet_config,
    )

    fields = {item["key"]: item for item in PARAMETER_SCHEMA}
    for key, expected_default in (
        ("fusionnet_max_neighbor_candidates", 4),
        ("fusionnet_patch_search_radius", 5),
    ):
        assert FUSIONNET_DEFAULTS[key] == expected_default
        assert fields[key]["type"] == "slider"
        assert fields[key]["min"] == 1
        assert fields[key]["max"] == 16
    normalized = _normalize_fusionnet_config(
        {
            "fusionnet_max_neighbor_candidates": "8",
            "fusionnet_patch_search_radius": "bad",
        }
    )
    assert normalized["fusionnet_max_neighbor_candidates"] == 8
    assert normalized["fusionnet_patch_search_radius"] == 5


def test_deep_analysis_neighbor_controls_persist_globally_and_per_batch(
    tmp_path, monkeypatch
):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment import (
        alignment_config_provider,
    )
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising import (
        fusionnet_parameter_settings,
    )

    settings_path = tmp_path / "algorithm-parameters.json"
    monkeypatch.setattr(
        fusionnet_parameter_settings,
        "ALGORITHM_PARAMETER_SETTINGS_FILE",
        str(settings_path),
    )
    monkeypatch.setattr(fusionnet_parameter_settings, "CONFIG_DIR", str(tmp_path))
    requested = {
        "fusionnet_denoising_mode": "deep_analysis",
        "fusionnet_max_neighbor_candidates": 7,
        "fusionnet_patch_search_radius": 11,
    }

    fusionnet_parameter_settings.save_fusionnet_config(requested)
    global_config = fusionnet_parameter_settings.load_fusionnet_config()
    assert global_config["fusionnet_max_neighbor_candidates"] == 7
    assert global_config["fusionnet_patch_search_radius"] == 11

    class Store:
        def __init__(self):
            self.values = {}

        def update_bulk(self, values, save=True):
            assert save is True
            self.values.update(values)

    store = Store()
    panel = SimpleNamespace(current_batch_id="batch-1", _store=store)
    monkeypatch.setattr(
        alignment_config_provider,
        "find_active_right_panel",
        lambda: panel,
    )
    fusionnet_parameter_settings.save_fusionnet_config_for_active_batch(requested)

    batch_config = store.values["batch-1.fusionnet_params"]
    assert batch_config["fusionnet_denoising_mode"] == "deep_analysis"
    assert batch_config["fusionnet_max_neighbor_candidates"] == 7
    assert batch_config["fusionnet_patch_search_radius"] == 11
    canonical = store.values["batch-1.algorithm_params"]
    assert canonical["denoising"]["fusionnet"] == batch_config


def test_saved_batch_deep_mode_is_loaded_for_fusionnet_worker(monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising import (
        fusionnet_parameter_settings,
    )

    monkeypatch.setattr(
        fusionnet_parameter_settings,
        "load_fusionnet_config",
        lambda: dict(fusionnet_parameter_settings.FUSIONNET_DEFAULTS),
    )
    monkeypatch.setattr(
        "pixel_refine_desktop.enhance_stack.core.logic.batch_parameter_manager.load_json_state",
        lambda: {
            "batch-7": {
                "algorithm_params": {
                    "denoising": {
                        "fusionnet": {
                            "fusionnet_denoising_mode": "deep_analysis",
                            "fusionnet_max_neighbor_candidates": 6,
                            "fusionnet_patch_search_radius": 9,
                        }
                    }
                }
            }
        },
    )

    loaded = fusionnet_parameter_settings.load_fusionnet_config_for_batch("batch-7")
    context = SimpleNamespace(
        batch_id="batch-7", params={}, alignment_selection_name=None
    )
    resolved = FusionNetDenoisingAlgorithm()._resolve_config(context)

    assert loaded["fusionnet_denoising_mode"] == "deep_analysis"
    assert resolved["denoising_mode"] == "deep_analysis"
    assert resolved["max_neighbor_candidates"] == 6
    assert resolved["patch_search_radius"] == 9


def test_deep_analysis_controls_are_visible_only_in_deep_mode():
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.fusionnet_parameter_settings import (
        PARAMETER_SCHEMA,
    )

    fields = {item["key"]: item for item in PARAMETER_SCHEMA}
    expected = {"fusionnet_denoising_mode": "deep_analysis"}
    assert fields["fusionnet_max_neighbor_candidates"]["visible_if"] == expected
    assert fields["fusionnet_patch_search_radius"]["visible_if"] == expected


def test_fusionnet_parameter_page_saves_through_provider_callbacks():
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.MFDenoiser_parameter_settings import (
        DenoisingParameterPage,
    )

    calls = []

    class PageStub:
        algorithm_name = "FusionNet"
        provider = {
            "save": lambda config: calls.append(("global", config)),
            "save_batch": lambda config: calls.append(("batch", config)),
        }

    config = {"fusionnet_denoising_mode": "deep_analysis"}
    DenoisingParameterPage._save_config_for_batch(PageStub(), config)

    assert calls == [("global", config), ("batch", config)]


def test_pixel_resolution_schema_displays_percentage_of_total_pixels():
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.fusionnet_parameter_settings import (
        PARAMETER_SCHEMA,
    )
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.MFDenoiser_parameter_settings import (
        _dropdown_display_value,
        _dropdown_stored_value,
    )

    field = next(
        item for item in PARAMETER_SCHEMA
        if item["key"] == "fusionnet_work_pixel_fraction"
    )

    assert field["label"] == "Pixel Resolution"
    assert _dropdown_display_value(field, 0.50) == "50%"
    assert float(_dropdown_stored_value(field, "25%")) == 0.25
    assert "total working pixels" in field["tooltip"]
