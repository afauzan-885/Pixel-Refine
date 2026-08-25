"""Deterministic parity checks for the portable image-family AOT wrappers.

Run one backend per process, for example::

    $env:AOT_ARCH = "cpu"
    python -m taichi_vision.taichi_algorithm.aot_py.tests.test_image_aot

The suite deliberately uses small NumPy invariants and a Pillow decode check
so it remains useful without requiring OpenCV in the compiler environment.
"""

from __future__ import annotations

import io

import numpy as np

from taichi_vision.taichi_algorithm.image_processing.extended_aot import (
    copy_make_border_aot,
    dilate_aot,
    enhance_image_aot,
    erode_aot,
    filter2d_aot,
    gaussian_window_aot,
    histogram_aot,
    joint_bilateral_guidance_aot,
    normalize_aot,
    ssim_aot,
    threshold_aot,
    warp_affine_aot,
)
from taichi_vision.taichi_algorithm.compression.jpeg_aot import (
    encode_grayscale_aot,
    encode_rgb_aot,
)


def _reflect101(index: int, size: int) -> int:
    if size <= 1:
        return 0
    period = 2 * (size - 1)
    value = index % period
    return value if value < size else period - value


def _morph_reference(src: np.ndarray, op: str) -> np.ndarray:
    out = np.empty_like(src)
    for y in range(src.shape[0]):
        for x in range(src.shape[1]):
            values = [
                src[
                    _reflect101(y + dy, src.shape[0]), _reflect101(x + dx, src.shape[1])
                ]
                for dy in (-1, 0, 1)
                for dx in (-1, 0, 1)
            ]
            out[y, x] = max(values) if op == "dilate" else min(values)
    return out


def run_accuracy_suite() -> dict[str, float]:
    source = np.arange(36, dtype=np.float32).reshape(6, 6)
    errors: dict[str, float] = {}

    errors["dilate"] = float(
        np.max(np.abs(dilate_aot(source, ksize=3) - _morph_reference(source, "dilate")))
    )
    errors["erode"] = float(
        np.max(np.abs(erode_aot(source, ksize=3) - _morph_reference(source, "erode")))
    )

    counts, _ = histogram_aot(source, bins=9, range=(0, 36))
    if int(counts.sum()) != source.size:
        raise AssertionError("histogram does not account for every pixel")
    errors["histogram"] = 0.0

    errors["ssim_identity"] = abs(float(ssim_aot(source, source, window_size=3)) - 1.0)
    identity = np.asarray([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
    errors["warp_identity"] = float(
        np.max(np.abs(warp_affine_aot(source, identity, (6, 6)) - source))
    )

    blur = np.ones((3, 3), dtype=np.float32) / 9.0
    filtered = filter2d_aot(source, blur)
    errors["filter_shape"] = float(filtered.shape != source.shape)

    bordered = copy_make_border_aot(source, 1, 1, 2, 2, "CONSTANT", value=7.0)
    if bordered.shape != (8, 10) or not np.all(bordered[[0, -1], :] == 7.0):
        raise AssertionError("constant border mismatch")
    rgb_border = copy_make_border_aot(
        np.repeat(source[..., None], 3, axis=2),
        1,
        1,
        1,
        1,
        "CONSTANT",
        value=(3.0, 5.0, 7.0),
    )
    if not (
        np.all(rgb_border[0, :, 0] == 3.0)
        and np.all(rgb_border[0, :, 1] == 5.0)
        and np.all(rgb_border[0, :, 2] == 7.0)
    ):
        raise AssertionError("per-channel constant border mismatch")
    errors["border"] = 0.0

    normalized = normalize_aot(source, 0.0, 1.0)
    errors["normalize"] = max(
        abs(float(normalized.min())), abs(float(normalized.max()) - 1.0)
    )

    _, binary = threshold_aot(source, 17.0, 255.0, "BINARY")
    expected_binary = np.where(source > 17.0, 255.0, 0.0)
    errors["threshold"] = float(np.max(np.abs(binary - expected_binary)))

    window = gaussian_window_aot(7, 7)
    errors["gaussian_window"] = (
        0.0 if np.all(np.isfinite(window)) and np.all(window > 0.0) else 1.0
    )

    guided = joint_bilateral_guidance_aot(source, source, radius=1)
    errors["joint_bilateral"] = float(np.max(np.abs(guided - source)))

    lut = np.arange(256, dtype=np.float32)
    enhanced = enhance_image_aot(source, source, lut)
    if enhanced.shape != source.shape or not np.isfinite(enhanced).all():
        raise AssertionError("enhancement output is invalid")
    errors["enhance"] = 0.0

    gray_jpeg = encode_grayscale_aot(source.astype(np.uint8), quality=75)
    rgb = np.repeat(source[..., None], 3, axis=2).astype(np.uint8)
    rgb_jpeg = encode_rgb_aot(rgb, quality=75, subsampling="420")
    if not (gray_jpeg.startswith(b"\xff\xd8") and gray_jpeg.endswith(b"\xff\xd9")):
        raise AssertionError("grayscale JPEG marker mismatch")
    if not (rgb_jpeg.startswith(b"\xff\xd8") and rgb_jpeg.endswith(b"\xff\xd9")):
        raise AssertionError("RGB JPEG marker mismatch")
    try:
        from PIL import Image

        Image.open(io.BytesIO(gray_jpeg)).load()
        Image.open(io.BytesIO(rgb_jpeg)).load()
    except ImportError:
        pass
    errors["jpeg"] = 0.0

    failures = {name: value for name, value in errors.items() if value > 2e-3}
    if failures:
        raise AssertionError(f"image AOT parity failures: {failures}")
    return errors


if __name__ == "__main__":
    print(run_accuracy_suite())
