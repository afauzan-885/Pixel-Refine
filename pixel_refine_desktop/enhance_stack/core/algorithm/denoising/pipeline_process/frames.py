"""Host frame decoding and GPU upload for the resident pipeline.

Owns the RGB host normalisation, EXIF orientation handling, the RAW extension
table, and the single-image GPU loader. Cross-module helpers are reached
through the resident facade so monkeypatched entry points stay live.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer

from .facade import api as _facade


__all__ = [
    "_RAW_EXTENSIONS",
    "_read_orientation",
    "_apply_orientation",
    "_normalize_rgb_host_frame",
    "load_frame_to_gpu",
]


_RAW_EXTENSIONS = frozenset(
    {
        ".dng",
        ".cr2",
        ".cr3",
        ".nef",
        ".arw",
        ".rw2",
        ".orf",
        ".raf",
        ".pef",
        ".srw",
    }
)


def _read_orientation(path: Path) -> int:
    from PIL import Image

    try:
        with Image.open(path) as img:
            exif = img.getexif()
            return int(exif.get(0x0112, 1))
    except Exception:
        return 1


def _apply_orientation(image: np.ndarray, orientation: int) -> np.ndarray:
    if orientation == 2:
        return np.fliplr(image)
    if orientation == 3:
        return np.rot90(image, 2)
    if orientation == 4:
        return np.flipud(image)
    if orientation == 5:
        return np.rot90(np.fliplr(image), -1)
    if orientation == 6:
        return np.rot90(image, -1)
    if orientation == 7:
        return np.rot90(np.fliplr(image), 1)
    if orientation == 8:
        return np.rot90(image, 1)
    return image


def _normalize_rgb_host_frame(image: np.ndarray) -> np.ndarray:
    """Convert one decoded RGB frame with one reusable float32 allocation."""
    source_dtype = image.dtype
    normalized = np.array(image, dtype=np.float32, copy=True, order="C")
    if np.issubdtype(source_dtype, np.integer):
        scale = np.float32(65535.0 if source_dtype == np.uint16 else 255.0)
        np.divide(normalized, scale, out=normalized)
    np.clip(normalized, 0.0, 1.0, out=normalized)
    return normalized


def load_frame_to_gpu(
    path: str | Path,
    is_raw: bool = False,
) -> TaichiGPUBuffer:
    """Load a single image directly to GPU VRAM as float32 [0,1] RGB.

    RAW/DNG:  demosaic (Hamilton) -> GPU float32 RGB
    Standard: imread -> GPU uint8 BGR -> cvtColor BGR->RGB -> GPU float32
    """
    from taichi_vision import taichi_aot
    taichi_aot = _facade()._managed_api(taichi_aot)

    path = Path(path)
    is_raw_file = is_raw or path.suffix.lower() in _RAW_EXTENSIONS

    if is_raw_file:
        rgb_gpu = taichi_aot.demosaic(
            str(path),
            method="hamilton",
            return_gpu=True,
        )
        if rgb_gpu.dtype in (np.uint8, np.uint16):
            # Keep the conversion in the Taichi Vision/native cast boundary.
            # Hamilton currently emits f32, but this compatibility branch is
            # still needed for older uint8/uint16 demosaic artifacts.
            converted_gpu = taichi_aot.cast(
                rgb_gpu, np.float32, host_accessible=True
            )
            if converted_gpu is not rgb_gpu:
                _facade()._destroy_work_item(rgb_gpu)
            return converted_gpu
        return rgb_gpu

    from PIL import Image, ImageOps

    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode in ("RGBA", "LA", "P", "L"):
                img = img.convert("RGB")
            img_rgb = np.array(img)
    except Exception as e_pil:
        raise ValueError(f"Failed to read image '{path}' with PIL: {e_pil}")

    rgb_f32 = _facade()._normalize_rgb_host_frame(img_rgb)
    del img_rgb

    return taichi_aot.upload(rgb_f32)
