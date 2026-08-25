"""Shared native-Taichi YUV preparation for HEIF/AVIF image payloads.

This module deliberately stops at a fixed-shape numeric boundary.  RGB range
conversion, padding, Y/Cb/Cr conversion, and chroma reduction can use the
``compression_image.tcm`` graphs; variable-length HEVC/AV1 syntax remains the
responsibility of the codec-specific writers.  The returned dictionary keeps
the original dimensions so a container cannot accidentally advertise padded
pixels.
"""
from __future__ import annotations

import os

import numpy as np

from taichi_vision.taichi_algorithm.aot_api.research import _dispatch


_SUBSAMPLING = {"444": "444", "422": "422", "420": "420"}


def _normalize_rgb(image, bit_depth: int) -> tuple[np.ndarray, np.ndarray | None]:
    bit_depth = int(bit_depth)
    if bit_depth not in (8, 10, 12):
        raise ValueError("video preparation supports 8, 10, or 12 bits")
    array = np.asarray(image)
    if array.ndim == 2:
        array = array[..., None]
    if array.ndim != 3 or array.shape[2] not in (1, 2, 3, 4):
        raise ValueError("expected a HxWx1/2/3/4 image")
    if array.shape[0] <= 0 or array.shape[1] <= 0:
        raise ValueError("image dimensions must be positive")
    work = np.ascontiguousarray(array, dtype=np.float32)
    peak = float((1 << bit_depth) - 1)
    finite_max = float(np.max(work))
    if not np.isfinite(work).all() or finite_max > peak + 1e-3 or float(np.min(work)) < -1e-3:
        raise ValueError("image samples are outside the selected bit-depth range")
    if finite_max <= 1.0 + 1e-6 and np.issubdtype(array.dtype, np.floating):
        work *= peak
    alpha = None
    if work.shape[2] in (2, 4):
        alpha = work[..., -1].copy()
        alpha = np.clip(alpha, 0.0, peak)
        work = work[..., :1] if work.shape[2] == 2 else work[..., :3]
    if work.shape[2] == 1:
        work = np.repeat(work, 3, axis=2)
    # The existing Taichi conversion graph is defined over the 8-bit numeric
    # range.  Convert back to the requested nominal range after the graph.
    work = np.ascontiguousarray(work * (255.0 / peak), dtype=np.float32)
    return work, alpha


def _host_ycbcr(rgb: np.ndarray) -> np.ndarray:
    red, green, blue = (rgb[..., index] for index in range(3))
    output = np.empty_like(rgb, dtype=np.float32)
    output[..., 0] = 0.299 * red + 0.587 * green + 0.114 * blue
    output[..., 1] = -0.168736 * red - 0.331264 * green + 0.5 * blue + 128.0
    output[..., 2] = 0.5 * red - 0.418688 * green - 0.081312 * blue + 128.0
    return output


def _pad_edge(plane: np.ndarray, height: int, width: int) -> np.ndarray:
    return np.pad(
        plane,
        ((0, height - plane.shape[0]), (0, width - plane.shape[1])),
        mode="edge",
    ).astype(np.float32, copy=False)


def _allow_host_fallback() -> bool:
    return os.environ.get("AOT_ALLOW_HOST_FALLBACK", "0") == "1"


def prepare_yuv_aot(image, *, bit_depth: int = 8, subsampling: str = "420") -> dict:
    """Prepare a YUV image using the native AOT conversion/subsampling graphs.

    ``subsampling`` accepts ``444``, ``422``, and ``420``.  If the selected
    target lacks the matching graph, the function fails closed unless the
    caller explicitly sets ``AOT_ALLOW_HOST_FALLBACK=1``.  This makes an
    accidental CPU substitution observable in a production pipeline.
    """

    mode = str(subsampling).replace(":", "")
    try:
        mode = _SUBSAMPLING[mode]
    except KeyError as exc:
        raise ValueError("subsampling must be 444, 422, or 420") from exc
    rgb, alpha = _normalize_rgb(image, int(bit_depth))
    height, width = rgb.shape[:2]
    padded_height = height if mode == "444" else height
    padded_width = width if mode == "444" else width + (width & 1)
    if mode == "420":
        padded_height += padded_height & 1
    padded_rgb = np.pad(
        rgb,
        ((0, padded_height - height), (0, padded_width - width), (0, 0)),
        mode="edge",
    ).astype(np.float32, copy=False)
    used_host_fallback = False
    try:
        ycbcr = _dispatch(
            "compression_image",
            "compression_rgb_to_ycbcr",
            inputs={"src": padded_rgb},
            outputs={"dst": (padded_rgb.shape, np.float32)},
            scalars={"h": int(padded_height), "w": int(padded_width)},
        )
        if mode == "444":
            cb = ycbcr[..., 1]
            cr = ycbcr[..., 2]
        else:
            chroma_shape = (
                padded_height,
                padded_width // 2,
            ) if mode == "422" else (
                padded_height // 2,
                padded_width // 2,
            )
            graph = "compression_jpeg_subsample_422_pair" if mode == "422" else "compression_jpeg_subsample_420_pair"
            chroma_pair = _dispatch(
                "compression_image",
                graph,
                inputs={"src": ycbcr},
                outputs={"dst": (chroma_shape + (2,), np.float32)},
                scalars={"h": int(padded_height), "w": int(padded_width)},
            )
            cb, cr = chroma_pair[..., 0], chroma_pair[..., 1]
        y = ycbcr[..., 0]
    except Exception as exc:
        if not _allow_host_fallback():
            raise RuntimeError(
                "native YUV preparation is unavailable for the selected AOT target; "
                "compile compression_image.tcm or set AOT_ALLOW_HOST_FALLBACK=1 "
                "for an explicit reference run"
            ) from exc
        used_host_fallback = True
        ycbcr = _host_ycbcr(padded_rgb)
        y = ycbcr[..., 0]
        if mode == "444":
            cb, cr = ycbcr[..., 1], ycbcr[..., 2]
        elif mode == "422":
            cb = 0.5 * (ycbcr[..., 1][:, 0::2] + ycbcr[..., 1][:, 1::2])
            cr = 0.5 * (ycbcr[..., 2][:, 0::2] + ycbcr[..., 2][:, 1::2])
        else:
            cb = 0.25 * (
                ycbcr[..., 1][0::2, 0::2]
                + ycbcr[..., 1][0::2, 1::2]
                + ycbcr[..., 1][1::2, 0::2]
                + ycbcr[..., 1][1::2, 1::2]
            )
            cr = 0.25 * (
                ycbcr[..., 2][0::2, 0::2]
                + ycbcr[..., 2][0::2, 1::2]
                + ycbcr[..., 2][1::2, 0::2]
                + ycbcr[..., 2][1::2, 1::2]
            )
    peak = float((1 << int(bit_depth)) - 1)
    scale = peak / 255.0
    result = {
        "y": np.ascontiguousarray(y[:height, :width] * scale, dtype=np.float32),
        "cb": np.ascontiguousarray(cb * scale, dtype=np.float32),
        "cr": np.ascontiguousarray(cr * scale, dtype=np.float32),
        "alpha": None if alpha is None else np.ascontiguousarray(alpha, dtype=np.float32),
        "width": int(width),
        "height": int(height),
        "padded_width": int(padded_width),
        "padded_height": int(padded_height),
        "bit_depth": int(bit_depth),
        "subsampling": mode,
        "used_host_fallback": used_host_fallback,
    }
    return result


__all__ = ["prepare_yuv_aot"]
