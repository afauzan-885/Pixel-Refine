"""Catalogue contracts across selectors, saved aliases and runtime dispatch."""

import os
import subprocess
import sys
from types import SimpleNamespace
from dataclasses import replace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QWidget

import config
from pixel_refine_desktop.enhance_stack.core.algorithm import catalog


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


def test_listing_catalog_does_not_load_algorithm_runtimes():
    code = """
import sys
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import CATEGORIES, get_names
for category in CATEGORIES:
    assert get_names(category)
for module in ('taichi', 'onnxruntime', 'cv2', 'torch'):
    assert module not in sys.modules, module
assert not any(name.endswith('.MFDenoiser') for name in sys.modules)
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("category", catalog.CATEGORIES)
def test_batch_and_bulk_selectors_use_the_same_catalog(category):
    from pixel_refine_desktop.enhance_stack.models.algorithm_list import get_algorithm_names

    assert get_algorithm_names(category) == catalog.get_names(category)
    assert catalog.get_names(category, context="bulk_edit") == catalog.get_names(category)


@pytest.mark.parametrize("category", ("alignment", "denoising"))
def test_mfdenoiser_selector_is_a_catalog_facade(category):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import get_algorithm_options

    assert get_algorithm_options(category) == catalog.get_options(category)


def test_bulk_dialog_includes_block_flow_and_available_sr(qapp):
    from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import MassAlgorithmEditDialog

    dialog = MassAlgorithmEditDialog([])
    try:
        assert dialog.align_combo.findText("Block Flow") >= 0
        assert dialog.sr_combo.findText("splattingSR") >= 0
        for category, combo in (("alignment", dialog.align_combo), ("denoising", dialog.denoise_combo),
                                ("super_resolution", dialog.sr_combo)):
            assert [combo.itemText(i) for i in range(1, combo.count())] == catalog.get_names(category, context="bulk_edit")
    finally:
        dialog.close()
        dialog.deleteLater()


def test_resident_panel_matches_catalog_and_resolves_alias(qapp):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.switchable_parameter_panel import SwitchableParameterPanel

    panel = SwitchableParameterPanel()
    try:
        assert [panel.align_dropdown.itemText(i) for i in range(panel.align_dropdown.count())] == catalog.get_names("alignment", context="resident")
        assert panel._normalize_alignment_name("compute_flow") == "Block Flow"
        assert "Block Flow" in panel.alignment_pages
    finally:
        panel.close()
        panel.deleteLater()


@pytest.mark.parametrize("category,alias,canonical", [
    ("alignment", "compute_flow", "Block Flow"),
    ("alignment", "FlowNet", "Block Flow"),
    ("alignment", "optical_flow", "Block Flow"),
    ("alignment", "ORB", "OFB"),
    ("alignment", "Lucas Kanade GPU Optical Flow", "Lucas Kanade"),
    ("alignment", "Block Matching Optical Flow", "Block Matching GPU"),
    ("alignment", "Farneback Optical Flow", "Farneback"),
    ("denoising", "Spatial AI", "FusionNet"),
    ("hdr", "SPDE-MR (Patch-Based)", "SPDE-MR HDR Fusion"),
])
def test_aliases_roundtrip_through_one_identity(category, alias, canonical):
    spec = catalog.get_spec(category, alias)
    assert spec.name == canonical
    assert catalog.get_spec(category, spec.key) is spec
    assert catalog.normalize_name(category, alias.swapcase()) == canonical


@pytest.mark.parametrize("name,context", (("RAFT", "array"), ("Light Glue", "standalone")))
def test_optional_alignment_can_be_restricted_to_specific_processes(name, context):
    assert name in catalog.get_names("alignment", context=context)
    assert name not in catalog.get_names("alignment", context="bulk_edit")
    with pytest.raises(ValueError, match="unavailable"):
        catalog.get_spec("alignment", name, context="resident")


def test_registry_aliases_share_instances_and_class_metadata():
    registry = catalog.create_registry("alignment")
    assert registry["FlowNet"] is registry["Block Flow"]
    assert registry["Lucas Kanade"] is registry["Lucas Kanade GPU Optical Flow"]
    for spec in catalog.get_specs("alignment"):
        assert registry[spec.name].NAME == spec.implementation_name
        assert registry[spec.name].DESCRIPTION == spec.description


def test_process_restriction_is_shared_by_ui_and_runtime(qapp, monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.switchable_parameter_panel import SwitchableParameterPanel

    restricted = replace(catalog.get_spec("alignment", "ofb"), processes=("fusionnet",))
    monkeypatch.setattr(catalog, "_SPECS", tuple(
        restricted if spec.category == "alignment" and spec.key == "ofb" else spec
        for spec in catalog._SPECS
    ))
    monkeypatch.setattr(catalog, "_INDEX", catalog._build_index())
    panel = SwitchableParameterPanel()
    try:
        panel.current_denoising_algo = "Similarity"
        panel._repopulate_alignment_combo()
        assert panel.align_dropdown.findText("OFB") == -1
        with pytest.raises(ValueError, match="unavailable"):
            catalog.get_spec("alignment", "OFB", context="resident", process="similarity")
        panel.current_denoising_algo = "FusionNet"
        panel._repopulate_alignment_combo()
        assert panel.align_dropdown.findText("OFB") >= 0
        assert catalog.get_spec("alignment", "OFB", context="resident", process="fusionnet") is restricted
    finally:
        panel.close()
        panel.deleteLater()


@pytest.mark.parametrize("alias", ("Block Flow", "compute_flow", "FlowNet", "Dense Optical Flow"))
def test_saved_block_flow_parameters_are_selected_through_catalog(monkeypatch, alias):
    from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager as params

    monkeypatch.setattr(params, "load_json_state", lambda: {"7": {
        config.KEY_ALIGNMENT_ALGO: alias, config.KEY_CHECKBOX_ALIGN: True,
        "block_flow_params": {"smooth": False},
    }})
    result = params.get_batch_alignment_runtime_snapshot(7)
    assert result[config.KEY_ALIGNMENT_ALGO] == "Block Flow"
    assert result["params"] == {"smooth": False}


def test_start_flushes_active_batch_warp_settings_before_runtime_snapshot(
    monkeypatch, qapp, tmp_path
):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.right_panel import (
        RightPanel,
    )
    from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager
    from UILibrary import DataStore

    parameter_path = tmp_path / "batch_parameter.json"
    store = DataStore()
    store.bind_to_file(str(parameter_path))
    store.update_bulk(
        {
            "7.alignment_algo": "OFB",
            "7.checkbox_align_images": True,
            "7.ofb_params": {"warp_method": "homography", "mode": "fast"},
            "8.alignment_algo": "OFB",
            "8.checkbox_align_images": True,
            "8.ofb_params": {"warp_method": "homography", "mode": "fast"},
        },
        save=False,
    )

    class ParameterPage:
        def flush_pending_config(self):
            store.update_bulk(
                {"7.ofb_params": {"warp_method": "apap", "mode": "balance"}},
                save=True,
            )

    parameter_page = ParameterPage()
    parameter_panel = SimpleNamespace(
        alignment_pages={"OFB": SimpleNamespace(widget=lambda: parameter_page)}
    )

    class Card:
        is_checked = False

        def get_value(self):
            return "No Denoising"

    class StartHarness:
        snapshot_settings_for_start = RightPanel.snapshot_settings_for_start
        flush_pending_batch_settings = RightPanel.flush_pending_batch_settings
        _flush_active_alignment_parameter_page = (
            RightPanel._flush_active_alignment_parameter_page
        )

        current_batch_id = 7
        _store = store
        _sync_store_timer = SimpleNamespace(stop=lambda: None)
        _is_syncing = False
        left_panel = SimpleNamespace(
            display_panel=SimpleNamespace(param_panel=parameter_panel)
        )
        align_form = SimpleNamespace(get_value=lambda: "OFB")
        sr_card = Card()
        hdr_card = Card()
        denoise_card = Card()
        _last_emitted_settings = None

        def _collect_ui_settings(self):
            return {
                config.KEY_ALIGNMENT: "OFB",
                config.KEY_SUPER_RESOLUTION: "No Super Resolution",
                config.KEY_DENOISING: "No Denoising",
                config.KEY_HDR: "No HDR",
                config.KEY_CHECKBOX_ALIGN: True,
                config.KEY_CHECKBOX_SUPER_RES: False,
                config.KEY_CHECKBOX_DENOISING: False,
                config.KEY_CHECKBOX_HDR: False,
            }

        def _publish_settings(self, settings):
            self._last_emitted_settings = dict(settings)

        def _save_batch_settings(self):
            store.update_bulk(
                {
                    "7.alignment_algo": "OFB",
                    "7.checkbox_align_images": True,
                },
                save=True,
            )

    monkeypatch.setattr(batch_parameter_manager, "BATCH_PARAMETER_PATH", str(parameter_path))
    snapshot = StartHarness().snapshot_settings_for_start()
    saved = batch_parameter_manager.get_batch_alignment_runtime_snapshot(7)
    other_batch = batch_parameter_manager.get_batch_alignment_runtime_snapshot(8)

    assert snapshot[config.KEY_ALIGNMENT] == "OFB"
    assert saved["params"] == {"warp_method": "apap", "mode": "balance"}
    assert other_batch["params"] == {"warp_method": "homography", "mode": "fast"}

    from pixel_refine_desktop.enhance_stack.components.batch_page_v2 import (
        right_panel as right_panel_module,
    )
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.MFDenoiser_parameter_settings import (
        AlignmentParameterPage,
    )

    reload_page = AlignmentParameterPage("OFB")
    try:
        reload_page._active_batch_id = lambda: 8
        reload_page.reload_from_active_batch()
        assert reload_page.controls["warp_method"][1].input.currentText() == "Homography"
        reload_page._active_batch_id = lambda: 7
        reload_page.reload_from_active_batch()
        assert reload_page.controls["warp_method"][1].input.currentText() == "APAP"
    finally:
        reload_page.close()
        reload_page.deleteLater()

    process_all_observations = []

    class ProcessDialog:
        def __init__(self, batches, parent, owner):
            self.panels_to_process_with_rows = []

        def exec(self):
            process_all_observations.append(
                batch_parameter_manager.get_batch_alignment_runtime_snapshot(7)[
                    "params"
                ]
            )
            return 0

    class ProcessAllHarness(StartHarness):
        _on_process_all_clicked = RightPanel._on_process_all_clicked
        controller = SimpleNamespace(get_all_batches=lambda: [SimpleNamespace(id=7)])
        _active_process_dialog = None
        parent = lambda self: None
        _sync_batch_queue_rows = lambda self: None
        _remember_successful_batch_rows = lambda self, dialog: None

    monkeypatch.setattr(right_panel_module, "BatchProcessDialog", ProcessDialog)
    ProcessAllHarness()._on_process_all_clicked()
    assert process_all_observations == [{"warp_method": "apap", "mode": "balance"}]


def test_apap_full_input_keeps_all_841_control_rows_without_sampling():
    import numpy as np

    from taichi_vision.taichi_algorithm.alignment import apap

    rows = cols = 29
    xx, yy = np.meshgrid(np.linspace(0, 4095, cols), np.linspace(0, 3071, rows))
    source = np.column_stack((xx.ravel(), yy.ravel()))
    x = source[:, 0] / 4095.0
    y = source[:, 1] / 3071.0
    bump = np.exp(-(((x - 0.63) ** 2 + (y - 0.52) ** 2) / 0.018))
    target = source.copy()
    target[:, 0] += 8.0 * bump + 1.1 * np.sin(y * 2 * np.pi)
    target[:, 1] += 5.5 * bump + 0.8 * np.sin(x * 2 * np.pi)

    assert not hasattr(apap, "_sample_tps_control_indices")
    assert not hasattr(apap, "MAX_NATIVE_TPS_CONTROLS")
    warp = apap.fit_apap_reference(
        source,
        target,
        grid_shape=(2, 2),
        max_controls_per_node=16,
        enable_residual_spline=False,
    )
    assert len(warp.source_points) == len(source) == 841
    assert len(warp.target_points) == len(target) == 841
    np.testing.assert_array_equal(warp.source_points, source)
    np.testing.assert_array_equal(warp.target_points, target)


def test_apap_caller_applies_ransac_mask_once_and_preserves_order():
    import numpy as np

    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.resident_pipeline import (
        _select_ransac_inlier_correspondences,
    )

    source = np.arange(16, dtype=np.float32).reshape(8, 2)
    target = source + np.array([2.0, -3.0], dtype=np.float32)
    mask = np.array([[0], [1], [0], [1], [1], [0], [1], [0]], dtype=np.uint8)
    selected_source, selected_target = _select_ransac_inlier_correspondences(
        source, target, mask
    )
    np.testing.assert_array_equal(selected_source, source[[1, 3, 4, 6]])
    np.testing.assert_array_equal(selected_target, target[[1, 3, 4, 6]])

    unfiltered_source, unfiltered_target = _select_ransac_inlier_correspondences(
        source, target, None
    )
    np.testing.assert_array_equal(unfiltered_source, source)
    np.testing.assert_array_equal(unfiltered_target, target)
    with pytest.raises(ValueError, match="mask has 7 rows for 8 correspondences"):
        _select_ransac_inlier_correspondences(source, target, mask[:7])


def test_apap_caller_reads_gpu_ransac_mask_before_cleanup():
    import numpy as np

    from taichi_vision.taichi_aot import upload
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.resident_pipeline import (
        _select_ransac_inlier_correspondences,
    )

    source = np.arange(16, dtype=np.float32).reshape(8, 2)
    target = source + np.array([-1.0, 4.0], dtype=np.float32)
    mask_gpu = upload(np.array([1, 0, 1, 0, 0, 1, 0, 1], dtype=np.uint8))
    try:
        selected_source, selected_target = _select_ransac_inlier_correspondences(
            source, target, mask_gpu
        )
    finally:
        mask_gpu.destroy()
    np.testing.assert_array_equal(selected_source, source[[0, 2, 5, 7]])
    np.testing.assert_array_equal(selected_target, target[[0, 2, 5, 7]])


@pytest.mark.parametrize("key", ("block_matching_gpu_params", "block_matching_params"))
def test_block_matching_parameter_storage_aliases_are_retained(monkeypatch, key):
    from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager as params

    monkeypatch.setattr(params, "load_json_state", lambda: {"7": {
        config.KEY_ALIGNMENT_ALGO: "Block Matching", config.KEY_CHECKBOX_ALIGN: True,
        key: {"mode": "high"},
    }})
    result = params.get_batch_alignment_runtime_snapshot(7)
    assert result["params"] == {"mode": "high"}


def test_parameter_saver_uses_catalog_name_for_ui_and_storage(monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment import alignment_config_provider as provider

    selected, saved = [], []
    panel = SimpleNamespace(
        current_batch_id=7,
        align_form=SimpleNamespace(set_value=selected.append),
        _store=SimpleNamespace(update_bulk=lambda data, **kwargs: saved.append(data)),
    )
    monkeypatch.setattr(provider, "find_active_right_panel", lambda: panel)
    provider.save_alignment_config_for_active_batch("Block Matching", "block_matching_params", {"mode": "high"})
    assert selected == ["Block Matching GPU"]
    assert saved[0]["7.alignment_algo"] == "Block Matching GPU"
    assert saved[0]["7.block_matching_params"] == {"mode": "high"}


@pytest.mark.parametrize("category,name,extra", [
    ("alignment", "Block Flow", {"alignment_backend": "Block Flow", "merging_mode": "none"}),
    ("denoising", "Spatial AI", {"merging_mode": "FusionNet", "output_suffix": "fusionet"}),
    ("super_resolution", "splattingSR", {}),
    ("hdr", "SPDE-MR (Patch-Based)", {"algorithm_name": "SPDE-MR HDR Fusion"}),
])
def test_dispatch_uses_catalog_entrypoint_and_arguments(monkeypatch, category, name, extra):
    calls = []

    def load(path):
        return lambda **kwargs: calls.append((path, kwargs))

    monkeypatch.setattr(catalog, "_load_symbol", load)
    parent = object()
    catalog.run_algorithm(category, name, parent, batch_id=7)
    assert calls == [(catalog.get_spec(category, name).entrypoint, {"parent": parent, "batch_id": 7, **extra})]


def test_internal_pipelines_own_alignment_in_the_common_stage_plan():
    stages = catalog.plan_stages({"alignment": "Block Flow", "denoising": "FusionNet"})
    assert [spec.name for spec in stages] == ["FusionNet"]
    stages = catalog.plan_stages({"alignment": "Block Flow"})
    assert [spec.name for spec in stages] == ["Block Flow"]
    stages = catalog.plan_stages({"alignment": "OFB", "super_resolution": "splattingSR", "hdr": "Weighted HDR"})
    assert [spec.name for spec in stages] == ["splattingSR", "Weighted HDR"]


def test_standalone_block_flow_reaches_mfdenoiser(qapp, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import algorithm_processor as processor

    calls, errors = [], []
    monkeypatch.setattr(processor, "running_mf_denoiser", lambda **kwargs: calls.append(kwargs))
    parent = QWidget()
    thread = processor.AlgorithmProcessorThread(7, {
        config.KEY_ALIGNMENT: "compute_flow", config.KEY_CHECKBOX_ALIGN: True,
    }, parent)
    thread.error_occurred.connect(errors.append)
    thread._run_in_process()
    assert not errors
    assert len(calls) == 1
    assert calls[0]["alignment_backend"] == "Block Flow"
    assert calls[0]["merging_mode"] == "none"


def test_unknown_alignment_does_not_silently_become_block_flow():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process import resident_pipeline

    with pytest.raises(ValueError, match="Unknown alignment"):
        resident_pipeline.create_resident_aligner("unregistered flow", object())


@pytest.mark.parametrize("name", ("Block Flow", "optical_flow", "compute_flow"))
def test_block_flow_resident_route_keeps_adaptive_aligner(monkeypatch, name):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process import resident_pipeline as resident
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine import flownet_inference

    monkeypatch.setattr(resident, "_own_component", lambda obj: obj)
    monkeypatch.setattr(flownet_inference, "AOTOpticalFlowAligner", lambda *args, **kwargs: kwargs)
    result = resident.create_resident_aligner(name, object(), work_scale=1.0, noise_score=0.2)
    assert result["adaptive"] is True
    assert result["tile_size"] == 32
    assert result["work_scale"] == 1.0
    assert result["noise_score"] == 0.2


@pytest.mark.parametrize("name,expected", [
    ("OFB", "FeatureMatchingGPUAligner"), ("AKAZE", "FeatureMatchingGPUAligner"),
    ("Farneback Optical Flow", "FarnebackResidentAligner"),
    ("Lucas Kanade GPU Optical Flow", "LucasKanadeResidentAligner"),
    ("Block Matching", "BlockMatchingResidentAligner"),
    ("No Alignment", "NoAlignmentGPUAligner"),
])
def test_resident_factory_keeps_each_concrete_algorithm(monkeypatch, name, expected):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process import resident_pipeline as resident

    monkeypatch.setattr(resident, "_own_component", lambda obj: obj)
    monkeypatch.setattr(resident, expected, lambda *args, **kwargs: SimpleNamespace(kind=expected))
    assert resident.create_resident_aligner(name, object()).kind == expected
