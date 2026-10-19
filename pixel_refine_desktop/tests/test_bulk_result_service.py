import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import config
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import plan_stages
from pixel_refine_desktop.enhance_stack.components.bulk_page.services import bulk_result_service as service
from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import ProcessingThread


def state_for(method="FusionNet", sr=False):
    return {
        config.KEY_ALIGNMENT: "Lucas Kanade",
        config.KEY_CHECKBOX_ALIGN: True,
        config.KEY_DENOISING: method,
        config.KEY_CHECKBOX_DENOISING: True,
        config.KEY_SUPER_RESOLUTION_ALGO: "splattingSR",
        config.KEY_CHECKBOX_SUPER_RES: sr,
    }


@pytest.mark.parametrize("method,suffix", [
    ("FusionNet", "fusionet"), ("Spatial AI", "fusionet"),
    ("Similarity", "similarity"), ("SpatialFusion", "similarity"),
    ("Average", "average"),
])
@pytest.mark.parametrize("settings", [
    {}, {"enable_linear_mode": True}, {"processing_format": "RAW Native"},
])
def test_exact_names_follow_catalogue_and_input_domain(method, suffix, settings):
    stages = plan_stages(service.batch_selections(state_for(method)))
    assert service.expected_output_names(stages, ["folder/Ref image-1.dng"], settings) == [
        f"Refimage-1_{suffix}.dng"
    ]


def test_disabled_denoiser_never_reuses_its_result():
    state = state_for()
    state[config.KEY_CHECKBOX_DENOISING] = False
    state[config.KEY_CHECKBOX_ALIGN] = False
    assert not plan_stages(service.batch_selections(state))


def test_mixed_raw_rgb_and_hdr_dynamic_reference_disable_cache():
    stages = plan_stages(service.batch_selections(state_for()))
    assert service.expected_output_names(stages, ["ref.dng", "support.tif"], {}) is None
    assert service.expected_output_names(stages, ["ref.nef", "support.nef"], {}) is None
    stages = plan_stages({"hdr": "Weighted HDR"})
    assert service.expected_output_names(stages, ["ref.dng"], {}) is None


def test_rgb_denoising_output_extension_follows_input_not_legacy_settings():
    stages = plan_stages(service.batch_selections(state_for()))
    assert service.expected_output_names(
        stages,
        ["folder/Ref image-1.tiff"],
        {"processing_format": "RAW Native", "enable_linear_mode": True},
    ) == ["Refimage-1_fusionet.tif"]


def test_exact_lookup_ignores_other_images_methods_numbered_copies_and_empty_files(tmp_path):
    for name in ("ref_fusionet_1.dng", "reference_fusionet.dng", "ref_similarity.dng", "other_fusionet.dng"):
        (tmp_path / name).write_bytes(b"other image")
    expected = "ref_fusionet.dng"
    (tmp_path / expected).write_bytes(b"")
    assert service.find_existing_outputs([expected], [str(tmp_path)]) == []
    (tmp_path / expected).write_bytes(b"exact image")
    assert service.find_existing_outputs([expected], [str(tmp_path)]) == [str(tmp_path / expected)]


def test_all_outputs_are_required_and_target_has_priority(tmp_path):
    stack, target = tmp_path / "stack", tmp_path / "target"
    stack.mkdir()
    target.mkdir()
    (stack / "ref_fusionet.tif").write_bytes(b"image")
    names = ["ref_fusionet.tif", "ref_splattingSR.tif"]
    assert service.find_existing_outputs(names, [str(target), str(stack)]) == []
    (target / names[1]).write_bytes(b"sr")
    assert service.find_existing_outputs(names, [str(target), str(stack)]) == [
        str(stack / names[0]), str(target / names[1])
    ]


def test_returned_paths_do_not_include_reference_or_preview():
    assert service.returned_output_paths({
        "reference_path": "input.dng", "ldr_path": "result.tif",
        "radiance_path": "radiance.tif", "preview_path": "preview.png",
    }) == ["result.tif", "radiance.tif"]


def test_copy_is_byte_verified_preserves_source_and_uses_exact_name(tmp_path):
    source, target = tmp_path / "result.dng", tmp_path / "out" / "result.dng"
    source.write_bytes(b"known image bytes")
    target.parent.mkdir()
    success, detail = service.copy_result(str(source), str(target))
    assert success, detail
    assert source.read_bytes() == target.read_bytes()
    assert list(target.parent.iterdir()) == [target]
    success, _ = service.copy_result(str(source), str(target))
    assert success
    assert source.exists()


def test_same_folder_is_noop_and_different_destination_is_not_overwritten(tmp_path):
    source, target = tmp_path / "result.dng", tmp_path / "different.dng"
    source.write_bytes(b"image")
    target.write_bytes(b"different image")
    assert service.move_result(str(source), str(source))[0]
    assert not service.copy_result(str(source), str(target))[0]
    assert target.read_bytes() == b"different image"
    assert source.exists()


def test_missing_same_path_cannot_be_reported_as_saved(tmp_path):
    missing = str(tmp_path / "missing.dng")
    assert not service.move_result(missing, missing)[0]
    assert not service.copy_result(missing, missing)[0]


@pytest.mark.parametrize("settings,expected", [
    ({}, "ref_splattingSR.tif"),
    ({"enable_linear_mode": True}, "ref_splattingSR.dng"),
    ({"processing_format": "RAW Native"}, "ref_splattingSR.tif"),
])
def test_sr_extension_matches_existing_writer(settings, expected):
    assert service.expected_output_names(plan_stages({"super_resolution": "splattingSR"}),
                                         ["ref.dng"], settings) == [expected]


def test_same_size_corruption_is_detected_and_source_preserved(tmp_path, monkeypatch):
    source, target = tmp_path / "result.dng", tmp_path / "out" / "result.dng"
    source.write_bytes(b"1234")
    target.parent.mkdir()

    def corrupt(_source, temporary):
        Path(temporary).write_bytes(b"4321")

    monkeypatch.setattr(service.shutil, "copy2", corrupt)
    success, detail = service.copy_result(str(source), str(target))
    assert not success
    assert "does not match" in detail
    assert source.read_bytes() == b"1234"
    assert not list(target.parent.iterdir())


@pytest.fixture
def bulk_job(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    stack = tmp_path / "database" / "stack"
    stack.mkdir(parents=True)
    target = tmp_path / "out"
    target.mkdir()
    reference = tmp_path / "ref.dng"
    support = tmp_path / "support.dng"
    reference.write_bytes(b"input")
    support.write_bytes(b"input")
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"1": state_for()}), encoding="utf-8")
    monkeypatch.setattr(config, "GENERAL_SETTINGS_FILE", str(tmp_path / "general.json"))
    database = SimpleNamespace(db_path=str(tmp_path / "session.db"),
                               get_images_by_batch=lambda _id: [str(reference), str(support)])
    layout = SimpleNamespace(database_manager=database, json_path=str(state))
    moves = []

    def move(source, folder):
        moves.append(source)
        success, detail = service.move_result(source, str(Path(folder) / Path(source).name))
        layout._last_result_export_detail = detail
        return success

    layout._move_single_batch_result = move
    panel = SimpleNamespace(batch_id=1, sequential_batch_number=1, selected_algorithms={})
    job = ProcessingThread([(panel, 0)], layout, str(target))
    monkeypatch.setattr(job, "_process_batch", lambda panel, batch_id, callback: panel.process_all_batch(
        progress_callback=callback, stop_callback=lambda: not job._is_running,
    ))
    finished, summaries = [], []
    job.batch_finished.connect(lambda *args: finished.append(args))
    job.processing_complete.connect(lambda summary: summaries.append(summary))
    return SimpleNamespace(job=job, panel=panel, stack=stack, target=target, moves=moves,
                           finished=finished, summaries=summaries, state=state, layout=layout)


@pytest.mark.parametrize("location", ["stack", "target"])
def test_bulk_existing_exact_output_skips_algorithm(bulk_job, location):
    data = bulk_job
    existing = getattr(data, location) / "ref_fusionet.dng"
    existing.write_bytes(b"already computed output")

    def must_not_process(**_kwargs):
        pytest.fail("The existing output must skip stacking")

    data.panel.process_all_batch = must_not_process
    data.job.run()
    assert data.finished == [(0, True, "Success: Reused existing result")]
    assert (data.target / existing.name).read_bytes() == b"already computed output"
    assert existing.exists()
    assert not data.moves


def test_bulk_uses_declared_path_not_unrelated_folder_files(bulk_job):
    data = bulk_job
    (data.stack / "ref_similarity.tif").write_bytes(b"wrong process")
    calls = []

    def process(**kwargs):
        calls.append(kwargs)
        (data.stack / "unrelated_fusionet.dng").write_bytes(b"unrelated")
        output = data.stack / "ref_fusionet.dng"
        output.write_bytes(b"actual result")
        return [str(output)]

    data.panel.process_all_batch = process
    data.job.run()
    assert len(calls) == 1
    assert data.finished == [(0, True, "Success: Saved")]
    assert (data.target / "ref_fusionet.dng").read_bytes() == b"actual result"
    assert not (data.target / "unrelated_fusionet.dng").exists()
    assert (data.stack / "ref_similarity.tif").exists()


def test_bulk_missing_output_is_reported_in_failure_summary(bulk_job):
    data = bulk_job
    data.panel.process_all_batch = lambda **kwargs: []
    data.job.run()
    assert data.finished[0][1] is False
    assert "ref_fusionet.dng" in data.finished[0][2]
    assert data.summaries[0][0]["id"] == 1


def test_bulk_incomplete_multi_stage_result_is_not_exported(bulk_job):
    data = bulk_job
    data.state.write_text(json.dumps({"1": state_for(sr=True)}), encoding="utf-8")
    output = data.stack / "ref_fusionet.dng"

    def process(**kwargs):
        output.write_bytes(b"one result only")
        return str(output)

    data.panel.process_all_batch = process
    data.job.run()
    assert data.finished[0][1] is False
    assert "Incomplete output set" in data.finished[0][2]
    assert not list(data.target.iterdir())


def test_both_layouts_share_exact_export_without_numbered_copies(tmp_path):
    from pixel_refine_desktop.enhance_stack.components.bulk_page.bulk_page_layout import BulkPageLayout
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_page_v2_layout import BatchPageV2Layout

    source = tmp_path / "ref_fusionet.dng"
    destination = tmp_path / "out"
    destination.mkdir()
    source.write_bytes(b"image")
    (destination / source.name).write_bytes(b"image")
    for layout_type in (BulkPageLayout, BatchPageV2Layout):
        layout = SimpleNamespace()
        assert layout_type._move_single_batch_result(layout, str(source), str(destination))
        assert layout._last_result_export_detail == "identical destination already exists"
    assert [path.name for path in destination.iterdir()] == [source.name]


def test_actual_panel_returns_declared_algorithm_output(bulk_job, monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.bulk_page.widgets import bulk_combined_panel

    data = bulk_job
    config_path = Path("database/align/batch_parameter.json")
    config_path.parent.mkdir(parents=True)
    config_path.write_text(data.state.read_text(), encoding="utf-8")
    data.panel.database_manager = data.layout.database_manager
    data.panel._exists_flags = lambda paths: [True] * len(paths)
    data.panel._last_result = None
    output = data.stack / "ref_fusionet.dng"
    calls = []

    def run(category, key, parent, **kwargs):
        calls.append((category, key, kwargs))
        return str(output)

    monkeypatch.setattr(bulk_combined_panel, "run_algorithm", run)
    result = bulk_combined_panel.CombinedPanel.process_all_batch(data.panel)
    assert result == [str(output)]
    assert len(calls) == 1
    assert calls[0][0:2] == ("denoising", "fusionnet")
    assert calls[0][2]["alignment_backend"] == "Lucas Kanade"


def test_bulk_cancelled_algorithm_does_not_export(bulk_job):
    data = bulk_job

    def process(**kwargs):
        output = data.stack / "ref_fusionet.dng"
        output.write_bytes(b"result")
        data.job.stop()
        return str(output)

    data.panel.process_all_batch = process
    data.job.run()
    assert not data.finished
    assert not data.moves
    assert not list(data.target.iterdir())


def test_bulk_exports_every_declared_hdr_path(bulk_job):
    data = bulk_job
    data.state.write_text(json.dumps({"1": {
        config.KEY_HDR_ALGO: "Weighted HDR", config.KEY_CHECKBOX_HDR: True,
        config.KEY_CHECKBOX_ALIGN: False,
    }}), encoding="utf-8")

    def process(**kwargs):
        paths = {}
        for key, suffix in (("ldr_path", "ldr"), ("radiance_path", "radiance")):
            output = data.stack / f"fallback_ref_weighted_hdr_{suffix}.tif"
            output.write_bytes(key.encode())
            paths[key] = str(output)
        paths["reference_path"] = "input.dng"
        return paths

    data.panel.process_all_batch = process
    data.job.run()
    assert data.finished[0][1]
    assert len(list(data.target.iterdir())) == 2
    assert len(data.moves) == 2


@pytest.mark.parametrize("cancelled", [False, True])
def test_completion_does_not_label_cancelled_queue_as_100_percent(cancelled):
    from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import BatchProcessDialog

    labels, updates = {}, []
    dialog = SimpleNamespace(
        reset_dialog_state=lambda: None, _was_cancelled=cancelled,
        panels_to_process_with_rows=[1, 2, 3, 4], processed_count=2,
        _update_progress_and_eta=lambda percent, message: updates.append((percent, message)),
        progress_status_tag=SimpleNamespace(setText=lambda text: labels.update(status=text)),
        eta_label=SimpleNamespace(setText=lambda text: labels.update(eta=text)),
    )
    BatchProcessDialog.on_processing_complete(dialog, [{"error": "Could not save"}])
    assert updates[0][0] == (50 if cancelled else 100)
    assert labels["status"] == ("Cancelled" if cancelled else "Completed with errors")
