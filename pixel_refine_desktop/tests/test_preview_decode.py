"""Preview decoder tests: embedded RAW preview, fallback, and 1280 px bound."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PIL import Image
from PySide6.QtWidgets import QApplication

from pixel_refine_desktop.enhance_stack.components.batch_page_v2.display_panel import (
    BurstPreloadWorker,
)

DNG_FIXTURE = Path(
    r"E:\Photo_Editor\360\Converts\lapangan\IMG_20250908_062022_EXP0-3.dng"
)
RGB_PREVIEW_DNG = Path(
    r"D:\Pixel Refine deep learning\test\IMG_20250415_181428_B005.dng"
)


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_worker_uses_bounded_parallelism():
    worker = BurstPreloadWorker([])
    assert worker.max_workers == 4
    assert worker.PREVIEW_MAX_SIDE == 1280


def test_standard_image_decodes_at_preview_size(qapp, tmp_path):
    path = tmp_path / "frame.jpg"
    Image.fromarray(np.full((2000, 3000, 3), 90, dtype=np.uint8)).save(
        path, quality=85
    )
    worker = BurstPreloadWorker([str(path)])
    _, image = worker._decode_frame(str(path))
    assert image is not None and not image.isNull()
    assert max(image.width(), image.height()) <= worker.PREVIEW_MAX_SIDE


@pytest.mark.skipif(
    not DNG_FIXTURE.is_file(), reason="local DNG burst fixture is unavailable"
)
def test_embedded_raw_preview_skips_demosaic(qapp, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import multi_threading

    def must_not_run(*args, **kwargs):
        raise AssertionError("demosaic must not run when a JPEG preview exists")

    monkeypatch.setattr(
        multi_threading, "load_raw_as_8bit_rgb_half_res", must_not_run
    )
    worker = BurstPreloadWorker([str(DNG_FIXTURE)])
    _, image = worker._decode_frame(str(DNG_FIXTURE))

    assert image is not None and not image.isNull()
    assert max(image.width(), image.height()) <= worker.PREVIEW_MAX_SIDE
    # Container orientation 6 must be applied: portrait after rotation.
    assert image.height() > image.width()


@pytest.mark.skipif(
    not DNG_FIXTURE.is_file(), reason="local DNG burst fixture is unavailable"
)
def test_missing_preview_falls_back_to_demosaic(qapp, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import multi_threading

    worker = BurstPreloadWorker([str(DNG_FIXTURE)])
    monkeypatch.setattr(worker, "_decode_embedded_raw_preview", lambda path: None)
    monkeypatch.setattr(
        multi_threading,
        "load_raw_as_8bit_rgb_half_res",
        lambda path, **kwargs: np.full((60, 80, 3), 40, dtype=np.uint8),
    )

    _, image = worker._decode_frame(str(DNG_FIXTURE))
    assert image is not None
    assert (image.width(), image.height()) == (80, 60)


def test_rgb_bitmap_preview_is_decoded(qapp, monkeypatch):
    import taichi

    width, height = 800, 600
    bitmap = np.zeros((height, width, 3), dtype=np.uint8)
    bitmap[..., 0] = 200
    payload = {
        "kind": "rgb",
        "width": width,
        "height": height,
        "compression": 1,
        "photometric": 2,
        "orientation": 3,
        "preview": bitmap.tobytes(),
    }
    monkeypatch.setattr(taichi, "imread", lambda path, mode="raw": payload)
    worker = BurstPreloadWorker([])

    out = worker._decode_embedded_raw_preview("synthetic.dng")
    assert out is not None
    assert out.shape == (height, width, 3)
    assert out[..., 0].mean() > 150


def test_tiny_bitmap_preview_is_rejected(qapp, monkeypatch):
    import taichi

    width, height = 256, 192
    payload = {
        "kind": "rgb",
        "width": width,
        "height": height,
        "compression": 1,
        "photometric": 2,
        "orientation": 3,
        "preview": bytes(width * height * 3),
    }
    monkeypatch.setattr(taichi, "imread", lambda path, mode="raw": payload)
    worker = BurstPreloadWorker([])

    assert worker._decode_embedded_raw_preview("synthetic.dng") is None


@pytest.mark.skipif(
    not RGB_PREVIEW_DNG.is_file(), reason="local RGB-preview DNG is unavailable"
)
def test_rgb_only_raw_falls_back_to_dcb(qapp, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import multi_threading

    worker = BurstPreloadWorker([str(RGB_PREVIEW_DNG)])
    assert worker._decode_embedded_raw_preview(str(RGB_PREVIEW_DNG)) is None
    monkeypatch.setattr(worker, "_decode_embedded_raw_preview", lambda path: None)

    captured = {}

    def fake_half_res(path, **kwargs):
        captured.update(kwargs)
        return np.full((60, 80, 3), 40, dtype=np.uint8)

    monkeypatch.setattr(
        multi_threading, "load_raw_as_8bit_rgb_half_res", fake_half_res
    )
    _, image = worker._decode_frame(str(RGB_PREVIEW_DNG))

    assert captured.get("method") == "dcb"
    assert captured.get("preview_max_side") == 1280
    assert captured.get("tone_map") is True
    assert image is not None
    assert (image.width(), image.height()) == (80, 60)
