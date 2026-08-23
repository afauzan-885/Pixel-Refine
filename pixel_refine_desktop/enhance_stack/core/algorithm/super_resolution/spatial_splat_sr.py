"""Deterministic burst super-resolution by robust sub-pixel splatting.

This module is deliberately backend-neutral.  It is the reference/oracle
implementation for the future AOT graph: samples are placed on an HR grid,
weighted by a rejection map, and normalized by coverage.  The implementation
does not silently claim to be the CUDA/Vulkan/OpenGL path; it is used for
known-value validation and as a safe CPU fallback.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np


def _as_float_frames(frames: np.ndarray) -> tuple[np.ndarray, bool]:
    arr = np.asarray(frames)
    if arr.ndim == 3:
        arr = arr[..., None]
        squeeze = True
    elif arr.ndim == 4:
        squeeze = False
    else:
        raise ValueError("frames must have shape (N,H,W) or (N,H,W,C)")
    if arr.shape[0] == 0 or arr.shape[1] == 0 or arr.shape[2] == 0:
        raise ValueError("frames must be non-empty")
    return np.ascontiguousarray(arr, dtype=np.float32), squeeze


def _normalize_flow(flow: Optional[np.ndarray], n: int, h: int, w: int) -> np.ndarray:
    if flow is None:
        return np.zeros((n, h, w, 2), dtype=np.float32)
    arr = np.asarray(flow, dtype=np.float32)
    if arr.shape == (n, 2):
        out = np.broadcast_to(arr[:, None, None, :], (n, h, w, 2)).copy()
    elif arr.shape == (n, h, w, 2):
        out = np.ascontiguousarray(arr)
    else:
        raise ValueError("flow must have shape (N,2) or (N,H,W,2)")
    if not np.isfinite(out).all():
        raise ValueError("flow contains NaN or infinity")
    return out


def _normalize_confidence(confidence: Optional[np.ndarray], n: int, h: int, w: int) -> np.ndarray:
    if confidence is None:
        return np.ones((n, h, w), dtype=np.float32)
    arr = np.asarray(confidence, dtype=np.float32)
    if arr.shape != (n, h, w):
        raise ValueError("confidence must have shape (N,H,W)")
    return np.clip(np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0)


def _bilinear_sample(image: np.ndarray, y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Sample a single HxW image at vectorized floating-point coordinates."""
    h, w = image.shape
    # Keep every intermediate in float32.  Python float literals otherwise
    # promote large 12MP coordinate planes to float64 and can add hundreds of
    # MiB of transient allocations during confidence generation.
    y = np.asarray(y, dtype=np.float32)
    x = np.asarray(x, dtype=np.float32)
    y = np.clip(y, np.float32(0.0), np.float32(h - 1))
    x = np.clip(x, np.float32(0.0), np.float32(w - 1))
    y0 = np.floor(y).astype(np.int32)
    x0 = np.floor(x).astype(np.int32)
    y1 = np.minimum(y0 + 1, h - 1)
    x1 = np.minimum(x0 + 1, w - 1)
    wy = (y - y0).astype(np.float32, copy=False)
    wx = (x - x0).astype(np.float32, copy=False)
    one = np.float32(1.0)
    top = (one - wx) * image[y0, x0] + wx * image[y0, x1]
    bottom = (one - wx) * image[y1, x0] + wx * image[y1, x1]
    return np.asarray((one - wy) * top + wy * bottom, dtype=np.float32)


def spatial_rejection_map(
    frames: np.ndarray,
    flow: Optional[np.ndarray] = None,
    noise_sigma: float = 0.02,
    sensitivity: float = 1.0,
) -> np.ndarray:
    """Return a per-frame confidence map compatible with Spatial Fusion.

    ``flow`` maps a source pixel toward reference coordinates in LR pixels.
    The reference frame receives confidence 1.  Other frames are compared at
    their flow-warped coordinates, so sub-pixel motion is not destroyed by a
    preliminary integer warp.  The AOT Spatial Fusion provider can replace
    this oracle later while preserving this exact output contract.
    """
    arr, _ = _as_float_frames(frames)
    n, h, w, _ = arr.shape
    flow_arr = _normalize_flow(flow, n, h, w)
    sigma = np.float32(max(float(noise_sigma), 1e-6))
    ref = arr[0].mean(axis=-1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = np.ones((n, h, w), dtype=np.float32)
    for k in range(1, n):
        fy = yy + flow_arr[k, ..., 1]
        fx = xx + flow_arr[k, ..., 0]
        ref_at_source = _bilinear_sample(ref, fy, fx)
        current = arr[k].mean(axis=-1)
        residual = current - ref_at_source
        # Robust confidence: Gaussian core plus a bounded motion penalty.
        local = np.abs(residual)
        confidence = np.exp(
            np.float32(-0.5)
            * np.square(local / sigma, dtype=np.float32)
            * np.float32(max(float(sensitivity), 1e-6)),
            dtype=np.float32,
        )
        out[k] = np.clip(confidence, 0.0, 1.0).astype(np.float32)
    return out


def robust_subpixel_splat(
    frames: np.ndarray,
    flow: Optional[np.ndarray] = None,
    confidence: Optional[np.ndarray] = None,
    *,
    scale: int = 2,
    block_size: Optional[int] = None,
    kernel_radius: float = 1.5,
    sigma: float = 0.85,
    fallback: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Reconstruct an HR image and return ``(image, coverage)``.

    The implementation is a deterministic Gaussian splat.  ``block_size``
    limits the output working set; each block owns its pixels, so block and
    full-frame results are numerically equivalent up to floating-point order.
    Coordinates use ``flow[..., 0] = dx`` and ``flow[..., 1] = dy`` in LR
    pixels.  A coverage-aware fallback prevents holes when motion samples do
    not fully cover the target grid.
    """
    arr, squeeze = _as_float_frames(frames)
    n, h, w, channels = arr.shape
    if int(scale) < 1:
        raise ValueError("scale must be >= 1")
    scale = int(scale)
    flow_arr = _normalize_flow(flow, n, h, w)
    conf = _normalize_confidence(confidence, n, h, w)
    hr_h, hr_w = h * scale, w * scale
    if block_size is None:
        block_size = max(hr_h, hr_w)
    block_size = max(int(block_size), 1)
    radius = max(float(kernel_radius), 0.5)
    kernel_sigma = max(float(sigma), 1e-4)
    fallback_arr = None
    if fallback is not None:
        fallback_arr, fallback_squeeze = _as_float_frames(fallback)
        if fallback_arr.shape[0] != 1 or fallback_arr.shape[1:3] != (h, w):
            raise ValueError("fallback must be one image with the LR spatial shape")
        if fallback_arr.shape[3] != channels:
            raise ValueError("fallback channel count does not match frames")

    result = np.zeros((hr_h, hr_w, channels), dtype=np.float32)
    coverage = np.zeros((hr_h, hr_w), dtype=np.float32)
    # Source coordinates are generated per output block.  ``np.add.at`` is
    # deterministic for a fixed traversal and avoids cross-block races.
    support = int(math.ceil(radius * 2.0))
    # Streaming mode calls this function with one frame at a time.  Cache its
    # source coordinate planes once instead of rebuilding a full HxW mesh for
    # every output block (which otherwise multiplies host work by the number
    # of blocks).
    cached_planes = None
    if n == 1:
        cached_planes = []
        src_y, src_x = np.mgrid[0:h, 0:w].astype(np.float32)
        target_x = (src_x + flow_arr[0, ..., 0]) * np.float32(scale)
        target_y = (src_y + flow_arr[0, ..., 1]) * np.float32(scale)
        cached_planes.append(
            (
                target_x,
                target_y,
                np.floor(target_x).astype(np.int32),
                np.floor(target_y).astype(np.int32),
            )
        )
    for y0 in range(0, hr_h, block_size):
        y1 = min(y0 + block_size, hr_h)
        for x0 in range(0, hr_w, block_size):
            x1 = min(x0 + block_size, hr_w)
            local_num = np.zeros((y1 - y0, x1 - x0, channels), dtype=np.float32)
            local_den = np.zeros((y1 - y0, x1 - x0), dtype=np.float32)
            for k in range(n):
                if cached_planes is not None:
                    target_x, target_y, base_x, base_y = cached_planes[k]
                else:
                    src_y, src_x = np.mgrid[0:h, 0:w].astype(np.float32)
                    target_x = (src_x + flow_arr[k, ..., 0]) * scale
                    target_y = (src_y + flow_arr[k, ..., 1]) * scale
                    base_x = np.floor(target_x).astype(np.int32)
                    base_y = np.floor(target_y).astype(np.int32)
                sample_weight = conf[k]
                for oy in range(-support, support + 1):
                    for ox in range(-support, support + 1):
                        yi = base_y + oy
                        xi = base_x + ox
                        inside = (yi >= y0) & (yi < y1) & (xi >= x0) & (xi < x1)
                        if not np.any(inside):
                            continue
                        # Pixel coordinates are represented at integer sample
                        # locations throughout the pipeline.  Adding a half
                        # pixel here would shift the reference frame and blur
                        # exact integer-aligned samples.
                        dy = yi.astype(np.float32) - target_y
                        dx = xi.astype(np.float32) - target_x
                        kernel = np.exp(-(dx * dx + dy * dy) / (2.0 * kernel_sigma * kernel_sigma))
                        weight = (kernel * sample_weight) * inside
                        ly = (yi[inside] - y0).ravel()
                        lx = (xi[inside] - x0).ravel()
                        ww = weight[inside].ravel().astype(np.float32)
                        np.add.at(local_den, (ly, lx), ww)
                        for c in range(channels):
                            np.add.at(local_num[..., c], (ly, lx), ww * arr[k, ..., c][inside].ravel())
            valid = local_den > 1e-8
            local_out = np.zeros_like(local_num)
            local_out[valid] = local_num[valid] / local_den[valid, None]
            if fallback_arr is not None:
                fy = np.arange(y0, y1, dtype=np.float32) / scale
                fx = np.arange(x0, x1, dtype=np.float32) / scale
                gy, gx = np.meshgrid(fy, fx, indexing="ij")
                for c in range(channels):
                    fb = _bilinear_sample(fallback_arr[0, ..., c], gy, gx)
                    local_out[..., c] = np.where(valid, local_out[..., c], fb)
            result[y0:y1, x0:x1] = local_out
            coverage[y0:y1, x0:x1] = local_den
    if squeeze:
        result = result[..., 0]
    return result, coverage


def robust_subpixel_splat_stream(
    frames: np.ndarray,
    flow_provider,
    confidence_provider,
    *,
    scale: int = 2,
    block_size: int = 1024,
    progress_callback=None,
) -> tuple[np.ndarray, np.ndarray]:
    """Accumulate splats one frame at a time using bounded output blocks.

    This is the low-RAM counterpart of :func:`robust_subpixel_splat`.  It
    deliberately does not materialize ``flow[N,H,W,2]`` or
    ``confidence[N,H,W]`` for the entire burst.  Each frame contributes its
    weighted numerator and coverage, then its temporary arrays are released.
    The result is mathematically equivalent to a weighted multi-frame merge.
    """
    arr, squeeze = _as_float_frames(frames)
    n, h, w, channels = arr.shape
    hr_h, hr_w = h * int(scale), w * int(scale)
    numerator = np.zeros((hr_h, hr_w, channels), dtype=np.float32)
    denominator = np.zeros((hr_h, hr_w), dtype=np.float32)
    for k in range(n):
        one_flow = np.ascontiguousarray(flow_provider(k), dtype=np.float32)
        one_conf = np.ascontiguousarray(confidence_provider(k), dtype=np.float32)
        one_result, one_coverage = robust_subpixel_splat(
            arr[k : k + 1],
            flow=one_flow[None, ...],
            confidence=one_conf[None, ...],
            scale=scale,
            block_size=block_size,
        )
        numerator += one_result * one_coverage[..., None]
        denominator += one_coverage
        if progress_callback:
            progress_callback(k + 1, n)
        del one_flow, one_conf, one_result, one_coverage
    result = np.zeros_like(numerator)
    valid = denominator > np.float32(1e-6)
    result[valid] = numerator[valid] / denominator[valid, None]
    if squeeze:
        result = result[..., 0]
    return result, denominator


__all__ = [
    "spatial_rejection_map",
    "robust_subpixel_splat",
    "robust_subpixel_splat_stream",
]
