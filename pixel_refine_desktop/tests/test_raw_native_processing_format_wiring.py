"""Input source descriptors select the denoising RAW or RGB pipeline."""

import pytest

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


def test_dng_routes_to_raw_pipeline_independent_of_legacy_settings(tmp_path, monkeypatch):
    paths = [str(tmp_path / name) for name in ("a.DNG", "b.dng", "c.Dng")]

    ctx = _prepare_context(
        monkeypatch,
        paths,
        {"processing_format": "RGB Linear", "enable_linear_mode": False},
    )

    assert ctx.source_descriptor.kind == "raw"
    assert ctx.is_raw_pipeline is True


def test_mixed_raw_and_rgb_burst_fails_closed(tmp_path, monkeypatch):
    paths = [str(tmp_path / "a.dng"), str(tmp_path / "b.jpg")]

    with pytest.raises(ValueError, match="cannot mix RAW and RGB"):
        _prepare_context(monkeypatch, paths, {})


def test_non_dng_raw_fails_without_rgb_demosaic_fallback(tmp_path, monkeypatch):
    paths = [str(tmp_path / "a.NEF"), str(tmp_path / "b.nef")]

    with pytest.raises(ValueError, match="provider currently supports DNG only"):
        _prepare_context(monkeypatch, paths, {})


def test_standard_rgb_formats_use_rgb_pipeline_even_with_legacy_raw_setting(
    tmp_path, monkeypatch
):
    paths = [str(tmp_path / "a.tiff"), str(tmp_path / "b.JPG")]
    ctx = _prepare_context(
        monkeypatch, paths, {"processing_format": "RAW Native"}
    )
    assert ctx.source_descriptor.kind == "rgb"
    assert ctx.is_raw_pipeline is False


def test_standard_rgb_routes_without_processing_format_setting(tmp_path, monkeypatch):
    paths = [str(tmp_path / "a.png"), str(tmp_path / "b.png")]

    ctx = _prepare_context(monkeypatch, paths, {})

    assert ctx.source_descriptor.kind == "rgb"
    assert ctx.is_raw_pipeline is False
