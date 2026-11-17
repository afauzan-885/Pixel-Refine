"""Native PNG/JPEG/TIFF reader parity gates."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import taichi

Image = pytest.importorskip("PIL.Image")


def _gradient(height: int, width: int, channels: int, dtype=np.uint8) -> np.ndarray:
    y, x = np.mgrid[:height, :width]
    base = np.stack(
        (
            (x * 255 // max(1, width - 1)),
            (y * 255 // max(1, height - 1)),
            ((x + y) * 255 // max(1, width + height - 2)),
        ),
        axis=-1,
    )
    if channels == 1:
        base = base[..., :1]
    return base.astype(dtype)


def _decode(path: Path) -> tuple[object, np.ndarray, dict]:
    result = taichi.imread(path)
    metadata = getattr(result, "metadata", result)
    if hasattr(result, "to_numpy"):
        return result, result.to_numpy(), metadata
    return result, np.asarray(result["data"]), metadata


def test_standard_images_return_direct_taichi_buffers(tmp_path: Path) -> None:
    source = _gradient(32, 48, 3)
    path = tmp_path / "direct.png"
    Image.fromarray(source, mode="RGB").save(path)
    result, decoded, metadata = _decode(path)
    assert hasattr(result, "_rust_buf")
    assert metadata["format"] == "png"
    assert np.array_equal(decoded, source)


def test_png_rgb8_matches_pillow(tmp_path: Path) -> None:
    source = _gradient(64, 96, 3)
    path = tmp_path / "rgb8.png"
    Image.fromarray(source, mode="RGB").save(path)
    _, decoded, metadata = _decode(path)
    assert metadata["format"] == "png"
    assert decoded.shape == (64, 96, 3)
    assert np.array_equal(decoded, source)


def test_png_rgba8_drops_alpha_in_rgb_contract(tmp_path: Path) -> None:
    source = _gradient(32, 48, 3)
    alpha = np.full((32, 48, 1), 128, dtype=np.uint8)
    rgba = np.concatenate((source, alpha), axis=-1)
    path = tmp_path / "rgba8.png"
    Image.fromarray(rgba, mode="RGBA").save(path)
    _, decoded, _ = _decode(path)
    assert decoded.shape == (32, 48, 3)
    assert np.array_equal(decoded, source)


def test_png_gray8_is_replicated(tmp_path: Path) -> None:
    gray = _gradient(24, 32, 1)[..., 0]
    path = tmp_path / "gray8.png"
    Image.fromarray(gray, mode="L").save(path)
    _, decoded, _ = _decode(path)
    assert np.array_equal(decoded[..., 0], gray)
    assert np.array_equal(decoded[..., 1], gray)
    assert np.array_equal(decoded[..., 2], gray)


def test_jpeg_baseline_matches_pillow_within_codec_tolerance(tmp_path: Path) -> None:
    source = _gradient(48, 64, 3)
    path = tmp_path / "photo.jpg"
    Image.fromarray(source, mode="RGB").save(path, quality=95)
    _, decoded, metadata = _decode(path)
    reference = np.asarray(Image.open(path).convert("RGB"))
    assert metadata["format"] == "jpeg"
    assert decoded.shape == reference.shape
    assert float(np.mean(np.abs(decoded.astype(np.int16) - reference.astype(np.int16)))) <= 3.0


def test_tiff_rgb8_and_rgb16_are_exact(tmp_path: Path) -> None:
    tifffile = pytest.importorskip("tifffile")
    source8 = _gradient(40, 56, 3)
    path8 = tmp_path / "rgb8.tif"
    tifffile.imwrite(path8, source8, photometric="rgb")
    _, decoded8, _ = _decode(path8)
    assert np.array_equal(decoded8, source8)

    source16 = (_gradient(40, 56, 3).astype(np.uint16) * 257)
    path16 = tmp_path / "rgb16.tif"
    tifffile.imwrite(path16, source16, photometric="rgb")
    _, decoded16, metadata16 = _decode(path16)
    assert metadata16["bits_per_sample"] == 16
    assert decoded16.dtype == np.uint16
    assert np.array_equal(decoded16, source16)


def test_tiff_uint32_and_float32_are_exact(tmp_path: Path) -> None:
    tifffile = pytest.importorskip("tifffile")

    source_u32 = np.array(
        [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]], dtype=np.uint32
    )
    path_u32 = tmp_path / "rgb32.tif"
    tifffile.imwrite(path_u32, source_u32, photometric="rgb")
    _, decoded_u32, metadata_u32 = _decode(path_u32)
    assert metadata_u32["bits_per_sample"] == 32
    assert decoded_u32.dtype == np.uint32
    assert np.array_equal(decoded_u32, source_u32)

    source_f32 = np.array(
        [[[0.5, 1.5, 2.5], [3.5, 4.5, 5.5]], [[6.5, 7.5, 8.5], [9.5, 10.5, 11.5]]],
        dtype=np.float32,
    )
    path_f32 = tmp_path / "rgbF32.tif"
    tifffile.imwrite(path_f32, source_f32, photometric="rgb")
    _, decoded_f32, metadata_f32 = _decode(path_f32)
    assert metadata_f32["bits_per_sample"] == 32
    assert decoded_f32.dtype == np.float32
    assert np.array_equal(decoded_f32, source_f32)


@pytest.mark.parametrize("compression", ["lzw", "deflate"])
def test_tiff_compressions_are_exact(compression: str, tmp_path: Path) -> None:
    tifffile = pytest.importorskip("tifffile")
    source = (_gradient(32, 48, 1)[..., 0].astype(np.uint16) * 257)
    path = tmp_path / f"gray16_{compression}.tif"
    try:
        tifffile.imwrite(path, source, compression=compression)
    except KeyError as exc:
        pytest.skip(f"tifffile cannot write {compression} without imagecodecs: {exc}")
    _, decoded, _ = _decode(path)
    assert np.array_equal(decoded[..., 0], source)
    assert np.array_equal(decoded[..., 1], source)
