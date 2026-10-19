# -*- coding: utf-8 -*-
"""Preprocessing and color conversion adapters for Taichi Neural Engine.

This module provides standalone color conversion and shape adaptation utilities
intended to be called BEFORE passing tensors to the NeuralModel.
Keeping these adapters separate preserves strict single-responsibility in the
neural execution engine.
"""

from typing import Any, Tuple, Union
import numpy as np
import taichi as ti


@ti.kernel
def _ti_bgr_hwc_to_gray_nchw(
    src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=4),
):
    """Converts BGR HWC float32 image to Grayscale NCHW using ITU-R BT.601."""
    for h, w in ti.ndrange(src.shape[0], src.shape[1]):
        b = src[h, w, 0]
        g = src[h, w, 1]
        r = src[h, w, 2]
        dst[0, 0, h, w] = 0.299 * r + 0.587 * g + 0.114 * b


@ti.kernel
def _ti_rgb_hwc_to_gray_nchw(
    src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=4),
):
    """Converts RGB HWC float32 image to Grayscale NCHW using ITU-R BT.601."""
    for h, w in ti.ndrange(src.shape[0], src.shape[1]):
        r = src[h, w, 0]
        g = src[h, w, 1]
        b = src[h, w, 2]
        dst[0, 0, h, w] = 0.299 * r + 0.587 * g + 0.114 * b


@ti.kernel
def _ti_hwc_to_nchw(
    src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=4),
):
    """Transposes HWC float32 image to NCHW."""
    for h, w, c in src:
        dst[0, c, h, w] = src[h, w, c]


@ti.kernel
def _ti_gray_to_rgb_nchw(
    src: ti.types.ndarray(dtype=ti.f32, ndim=4),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=4),
):
    """Replicates 1-channel Grayscale NCHW into 3-channel RGB NCHW."""
    for n, h, w in ti.ndrange(src.shape[0], src.shape[2], src.shape[3]):
        v = src[n, 0, h, w]
        dst[n, 0, h, w] = v
        dst[n, 1, h, w] = v
        dst[n, 2, h, w] = v


def adapt_image_to_nchw(
    image: Any,
    expected_channels: int = 1,
    is_bgr: bool = False,
    normalize: bool = True,
) -> np.ndarray:
    """Preprocesses arbitrary host images to contiguous float32 NCHW tensors.

    Args:
        image: NumPy array, list, or PyTorch tensor.
        expected_channels: Expected channel count (e.g. 1 for Grayscale, 3 for RGB).
        is_bgr: True if 3-channel input is BGR format (e.g. OpenCV).
        normalize: If True and input is uint8, normalizes values to [0.0, 1.0].

    Returns:
        np.ndarray: Contiguous float32 array with shape (1, expected_channels, H, W).
    """
    if hasattr(image, "detach") and hasattr(image, "cpu") and hasattr(image, "numpy"):
        arr = image.detach().cpu().numpy()
    elif hasattr(image, "to_numpy"):
        arr = image.to_numpy()
    else:
        arr = np.asarray(image)

    # Normalize uint8 -> float32
    if normalize and arr.dtype == np.uint8:
        arr = arr.astype(np.float32) * (1.0 / 255.0)
    else:
        arr = arr.astype(np.float32)

    ndim = arr.ndim
    if ndim == 2:
        # (H, W) -> (1, 1, H, W)
        arr = arr[np.newaxis, np.newaxis, :, :]
        if expected_channels == 3:
            arr = np.repeat(arr, 3, axis=1)
    elif ndim == 3:
        if arr.shape[2] in (1, 3, 4):
            # HWC format
            H, W, C = arr.shape
            if C in (3, 4) and expected_channels == 1:
                # ITU-R BT.601 formula
                if is_bgr:
                    gray = 0.299 * arr[:, :, 2] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 0]
                else:
                    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
                arr = gray[np.newaxis, np.newaxis, :, :]
            elif C == 1 and expected_channels == 3:
                arr = np.repeat(arr.transpose(2, 0, 1)[np.newaxis, :, :, :], 3, axis=1)
            else:
                arr = np.transpose(arr[:, :, :3 if C > 3 else C], (2, 0, 1))[np.newaxis, :, :, :]
        else:
            # CHW format -> (1, C, H, W)
            arr = arr[np.newaxis, :, :, :]
    elif ndim == 4:
        pass
    else:
        raise ValueError(f"Unsupported image dimension: {ndim}; expected 2D, 3D, or 4D image.")

    return np.ascontiguousarray(arr, dtype=np.float32)

