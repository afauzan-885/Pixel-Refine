"""Burst frame loading and normalisation for resident WeightNet fusion.

Decodes RGB linear float32 frames from files or in-memory bytes (RAW via
Taichi AOT Hamilton demosaic, standard via PIL/cv2), applies EXIF
orientation through shared_utils, and normalises burst stacks.
"""

from pathlib import Path
from typing import Optional, Sequence

import numpy as np
import cv2
from PIL import Image

from pixel_refine_desktop.enhance_stack.core.algorithm.shared_utils import (
    RAW_EXTENSIONS,
    apply_orientation as _apply_orientation,
    read_orientation as _read_image_orientation,
)

__all__ = [
    "RAW_EXTENSIONS",
    "load_rgb_linear_image",
    "load_rgb_linear_image_bytes",
    "load_burst_images",
    "normalize_burst_frames",
    "burst_images_to_array",
]

def load_rgb_linear_image(path: str | Path, is_raw: bool = False) -> np.ndarray:
    """
    Loads an image in pure linear [0.0, 1.0] RGB float32.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    from taichi_vision import taichi_aot

    if is_raw or path.suffix.lower() in RAW_EXTENSIONS:
        try:
            demosaiced = taichi_aot.demosaic(
                str(path),
                method="hamilton",
                return_gpu=False,
            )
            img_np = np.asarray(demosaiced, dtype=np.float32)
        except Exception as exc:
            import rawpy

            with rawpy.imread(str(path)) as raw:
                rgb = raw.postprocess(
                    gamma=(1, 1),
                    no_auto_bright=True,
                    output_bps=16,
                    use_camera_wb=True,
                    highlight_mode=rawpy.HighlightMode.Blend,
                )
            img_np = rgb.astype(np.float32) / 65535.0
        if img_np.ndim != 3 or img_np.shape[2] != 3:
            raise ValueError(
                f"Raw decoding failed for {path}, got shape {img_np.shape}"
            )
        max_v = float(np.max(img_np)) if img_np.size > 0 else 1.0
        if max_v > 1.5:
            scale = 65535.0 if max_v > 255.0 else 255.0
            img_np /= scale
        return np.ascontiguousarray(np.clip(img_np, 0.0, 1.0), dtype=np.float32)

    image_bgr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image_bgr is None:
        raise ValueError(f"Failed to read image: {path}")

    orientation = _read_image_orientation(path)
    if orientation != 1:
        image_bgr = _apply_orientation(image_bgr, orientation)

    if image_bgr.ndim == 2:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    del image_bgr

    if np.issubdtype(image_rgb.dtype, np.integer):
        scale = 65535.0 if image_rgb.dtype == np.uint16 else 255.0
        return np.ascontiguousarray(
            image_rgb.astype(np.float32) / scale, dtype=np.float32
        )
    return np.ascontiguousarray(image_rgb.astype(np.float32), dtype=np.float32)


def load_rgb_linear_image_bytes(
    path: str | Path,
    encoded: bytes | bytearray | memoryview,
    is_raw: bool = False,
) -> np.ndarray:
    """Decode unchanged source-file bytes into the canonical linear RGB format.

    This mirrors :func:`load_rgb_linear_image` while avoiding a second disk read
    after a source payload has been prefetched into the RAM Queue.
    """
    from io import BytesIO

    path = Path(path)
    encoded_bytes = bytes(encoded)
    if not encoded_bytes:
        raise ValueError(f"Image payload is empty: {path}")

    from taichi_vision import taichi_aot

    if is_raw or path.suffix.lower() in RAW_EXTENSIONS:
        try:
            import rawpy

            with rawpy.imread(BytesIO(encoded_bytes)) as raw:
                demosaiced = taichi_aot.demosaic(
                    raw,
                    method="hamilton",
                    return_gpu=False,
                )
            img_np = np.asarray(demosaiced, dtype=np.float32)
        except Exception:
            import rawpy

            with rawpy.imread(BytesIO(encoded_bytes)) as raw:
                rgb = raw.postprocess(
                    gamma=(1, 1),
                    no_auto_bright=True,
                    output_bps=16,
                    use_camera_wb=True,
                    highlight_mode=rawpy.HighlightMode.Blend,
                )
            img_np = rgb.astype(np.float32) / 65535.0
        if img_np.ndim != 3 or img_np.shape[2] != 3:
            raise ValueError(
                f"Raw decoding failed for {path}, got shape {img_np.shape}"
            )
        max_v = float(np.max(img_np)) if img_np.size > 0 else 1.0
        if max_v > 1.5:
            scale = 65535.0 if max_v > 255.0 else 255.0
            img_np /= scale
        return np.ascontiguousarray(np.clip(img_np, 0.0, 1.0), dtype=np.float32)

    image_bgr = cv2.imdecode(
        np.frombuffer(encoded_bytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED
    )
    if image_bgr is None:
        raise ValueError(f"Failed to decode image bytes: {path}")

    try:
        with Image.open(BytesIO(encoded_bytes)) as image:
            orientation = int(image.getexif().get(0x0112, 1))
    except Exception:
        orientation = 1
    if orientation != 1:
        image_bgr = _apply_orientation(image_bgr, orientation)

    if image_bgr.ndim == 2:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    del image_bgr

    if np.issubdtype(image_rgb.dtype, np.integer):
        scale = 65535.0 if image_rgb.dtype == np.uint16 else 255.0
        return np.ascontiguousarray(
            image_rgb.astype(np.float32) / scale, dtype=np.float32
        )
    return np.ascontiguousarray(image_rgb.astype(np.float32), dtype=np.float32)


def load_burst_images(paths: Sequence[str | Path]) -> list[np.ndarray]:
    """
    Loads burst images and applies AutoEnhance:
    - Analyzes histogram metrics ONCE on reference frame (paths[0]).
    - Applies AutoEnhance with the derived parameters to reference and all support frames.
    """
    if not paths:
        raise ValueError("Burst is empty.")

    from taichi_vision import taichi_aot

    # 1. Load Reference Frame
    ref_linear = load_rgb_linear_image(paths[0])
    target_h, target_w = ref_linear.shape[:2]

    # 2. Analyze Reference Frame ONCE
    params = taichi_aot.analyze_auto_enhance_params(ref_linear, mode="analysis")
    print(
        f"[AutoEnhance Burst] Analyzed ref={Path(paths[0]).name} -> "
        f"gain={params['gain']:.4f}, white={params['white_level']:.4f}, "
        f"shadow={params['shadow_lift']:.4f}, contrast={params['global_contrast']:.2f}"
    )

    # 3. Apply AutoEnhance to Reference Frame
    ref_enhanced = taichi_aot.AutoEnhance(ref_linear, params=params)
    normalized = [np.ascontiguousarray(ref_enhanced, dtype=np.float32)]

    # 4. Apply AutoEnhance to Support Frames
    for source_path in paths[1:]:
        supp_linear = load_rgb_linear_image(source_path)
        supp_enhanced = taichi_aot.AutoEnhance(supp_linear, params=params)

        if supp_enhanced.shape[:2] != (target_h, target_w):
            supp_enhanced = taichi_aot.resize(
                supp_enhanced,
                (target_w, target_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )

        normalized.append(np.ascontiguousarray(supp_enhanced, dtype=np.float32))

    return normalized


def normalize_burst_frames(
    frames: Sequence[np.ndarray],
    is_raw: bool = False,
) -> list[np.ndarray]:
    """
    Normalizes a list of in-memory image frames (e.g. from FlowNet alignment):
    - Scales integer types (uint8, uint16) to float32 in [0.0, 1.0].
    """
    if not frames:
        raise ValueError("Frames list is empty.")

    target_h, target_w = frames[0].shape[:2]

    def _to_f32(img):
        img_arr = np.asarray(img)
        if np.issubdtype(img_arr.dtype, np.integer):
            scale = 65535.0 if img_arr.dtype.itemsize > 1 else 255.0
            return np.ascontiguousarray(
                img_arr.astype(np.float32) / scale, dtype=np.float32
            )
        elif np.issubdtype(img_arr.dtype, np.floating):
            max_v = float(np.max(img_arr)) if img_arr.size > 0 else 1.0
            if max_v > 1.5:
                scale = 65535.0 if max_v > 255.0 else 255.0
                return np.ascontiguousarray(
                    img_arr.astype(np.float32) / scale, dtype=np.float32
                )
            return np.ascontiguousarray(
                img_arr.astype(np.float32, copy=False), dtype=np.float32
            )
        return np.ascontiguousarray(img_arr.astype(np.float32), dtype=np.float32)

    normalized = []
    for f in frames:
        f32 = _to_f32(f)
        if f32.shape[:2] != (target_h, target_w):
            from taichi_vision import taichi_aot

            f32 = taichi_aot.resize(
                f32,
                (target_w, target_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )
        normalized.append(np.ascontiguousarray(f32, dtype=np.float32))

    return normalized


def burst_images_to_array(images: Sequence[np.ndarray]) -> np.ndarray:
    if not images:
        raise ValueError("Cannot convert an empty burst to an array.")
    stacked = np.stack(images, axis=0)  # [N, H, W, 3]
    array = np.transpose(stacked, (0, 3, 1, 2))[np.newaxis, ...]  # [1, N, 3, H, W]
    return np.ascontiguousarray(array, dtype=np.float32)
