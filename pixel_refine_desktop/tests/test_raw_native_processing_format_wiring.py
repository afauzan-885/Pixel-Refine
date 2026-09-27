"""Settings -> MFDenoiser context wiring for the RAW Native processing format.

The General Settings ``processing_format`` value selects between the resident
RGB route and the pre-demosaic CFA route.  These tests pin the resolution
rules, the fail-closed guard, and the settings read, so the wiring cannot
silently disappear again (it was dropped during the pipeline_process
migration and left ``raw_native`` permanently False).
"""

import json

import pytest

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import MFDenoiser
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    MFDenoiserAlgorithm,
    PipelineContext,
)


def _prepare_context(monkeypatch, paths, params):
    processor = MFDenoiserAlgorithm(db_path="unused-session.db")
    monkeypatch.setattr(
        processor, "_get_image_paths", lambda batch_id=None: list(paths)
    )
    ctx = PipelineContext(db_path="unused-session.db")
    ctx.params = dict(params)
    return processor.prepare_input_paths(ctx)


def test_raw_native_selects_cfa_route_for_homogeneous_dng_burst(tmp_path, monkeypatch):
    paths = [str(tmp_path / name) for name in ("a.dng", "b.dng", "c.dng")]

    ctx = _prepare_context(
        monkeypatch,
        paths,
        {"processing_format": "RAW Native", "enable_linear_mode": False},
    )

    assert ctx.is_raw_native is True
    # Linear sensor data is implied by the CFA route, independent of the
    # separately stored enable_linear_mode flag.
    assert ctx.is_linear_mode is True


def test_raw_native_fails_closed_on_mixed_burst(tmp_path, monkeypatch):
    paths = [str(tmp_path / "a.dng"), str(tmp_path / "b.jpg")]

    with pytest.raises(ValueError, match="RAW Native requires every frame"):
        _prepare_context(monkeypatch, paths, {"processing_format": "RAW Native"})


def test_rgb_linear_keeps_resident_demosaic_route(tmp_path, monkeypatch):
    paths = [str(tmp_path / "a.dng"), str(tmp_path / "b.dng")]

    ctx = _prepare_context(
        monkeypatch,
        paths,
        {"processing_format": "RGB Linear", "enable_linear_mode": False},
    )

    assert ctx.is_raw_native is False
    assert ctx.is_linear_mode is False
    assert ctx.processing_format == "RGB Linear"


def test_missing_processing_format_defaults_to_rgb_linear(tmp_path, monkeypatch):
    paths = [str(tmp_path / "a.dng"), str(tmp_path / "b.dng")]

    ctx = _prepare_context(monkeypatch, paths, {})

    assert ctx.processing_format == "RGB Linear"
    assert ctx.is_raw_native is False


def test_load_params_reads_processing_format_from_general_settings(
    tmp_path, monkeypatch
):
    settings = tmp_path / "app_setting.json"
    settings.write_text(
        json.dumps({"processing_format": "RAW Native", "enable_linear_mode": False}),
        encoding="utf-8",
    )
    monkeypatch.setattr(MFDenoiser, "GENERAL_SETTINGS_FILE", str(settings))

    params = MFDenoiserAlgorithm(db_path="unused-session.db")._load_params()

    assert params["processing_format"] == "RAW Native"


def test_load_params_defaults_when_settings_file_is_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(
        MFDenoiser, "GENERAL_SETTINGS_FILE", str(tmp_path / "missing.json")
    )

    params = MFDenoiserAlgorithm(db_path="unused-session.db")._load_params()

    assert params["processing_format"] == "RGB Linear"
