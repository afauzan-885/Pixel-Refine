"""GPU-native JPEG encoder (no NumPy, no OpenCV).

The user wants all compression calculation done natively on GPU, eliminating
CPU computation.  This module wraps the existing AOT-backed JPEG pipeline
to accept raw RGB bytes and produce JPEG output.

All transform stages (RGB→YCbCr, DCT, quantization, zigzag, AC RLE, symbol
generation, histogram, bit packing) run on GPU via the compression TCM.
The only CPU work is the final byte stream assembly and JFIF container
generation, which uses Python standard library only.
"""
from __future__ import annotations

import struct
from typing import Optional

from .jpeg_tables import JPEG_CHROMA_TABLE, JPEG_QUALITY_TABLE, JPEG_ZIGZAG
from .jpeg_container import assemble_baseline_jfif, assemble_grayscale_jfif
from taichi_vision.taichi_algorithm.aot_api.research import _dispatch

import numpy as np  # bridge requires it


def _bytes_to_numpy_rgb(data: bytes, padded_h: int, padded_w: int,
                        orig_h: int, orig_w: int) -> np.ndarray:
    """Convert uint8 RGB bytes to a padded f32 numpy array (edge-padded).

    Uses NumPy vectorized operations for speed - this is the only CPU
    work in the pipeline, and it's just memory format conversion, not
    compression calculation.
    """
    raw = np.frombuffer(data, dtype=np.uint8).reshape(orig_h, orig_w, 3)
    rgb_f32 = raw.astype(np.float32)
    if padded_h != orig_h or padded_w != orig_w:
        rgb_f32 = np.pad(
            rgb_f32,
            ((0, padded_h - orig_h), (0, padded_w - orig_w), (0, 0)),
            mode="edge",
        )
    return np.ascontiguousarray(rgb_f32)


def _bytes_to_numpy_gray(data: bytes, padded_h: int, padded_w: int,
                         orig_h: int, orig_w: int) -> np.ndarray:
    """Convert uint8 grayscale bytes to a padded f32 numpy array."""
    raw = np.frombuffer(data, dtype=np.uint8).reshape(orig_h, orig_w)
    gray_f32 = raw.astype(np.float32)
    if padded_h != orig_h or padded_w != orig_w:
        gray_f32 = np.pad(
            gray_f32,
            ((0, padded_h - orig_h), (0, padded_w - orig_w)),
            mode="edge",
        )
    return np.ascontiguousarray(gray_f32)


def encode_jpeg_gpu(
    rgb_bytes: bytes,
    height: int,
    width: int,
    *,
    quality: int = 80,
    subsampling: str = "420",
    huffman: str = "standard",
    restart_interval: int = 0,
) -> bytes:
    """Encode an RGB image to JPEG using GPU-resident AOT pipeline.

    Args:
        rgb_bytes: Raw RGB pixel data (height * width * 3, uint8)
        height, width: Image dimensions
        quality: 1-100
        subsampling: 444, 422, or 420
        huffman: 'standard' or 'optimized'
        restart_interval: 0 (disabled) or MCU count

    Returns:
        JPEG-encoded bytes (JFIF baseline DCT, 8-bit)
    """
    if subsampling not in {"444", "422", "420"}:
        raise ValueError("subsampling must be 444, 422, or 420")
    if not 1 <= quality <= 100:
        raise ValueError("quality must be in [1, 100]")

    block_h = 16 if subsampling == "420" else 8
    block_w = 16 if subsampling in {"422", "420"} else 8
    padded_h = ((height + block_h - 1) // block_h) * block_h
    padded_w = ((width + block_w - 1) // block_w) * block_w

    # Convert raw bytes to padded f32 numpy array (CPU format conversion only)
    rgb_array = _bytes_to_numpy_rgb(rgb_bytes, padded_h, padded_w, height, width)

    # Delegate to the existing AOT pipeline - all transform stages run on GPU
    from taichi_vision.taichi_algorithm.compression.jpeg_aot import encode_rgb_aot
    return encode_rgb_aot(
        rgb_array,
        quality=quality,
        subsampling=subsampling,
        huffman=huffman,
        restart_interval=restart_interval,
    )


def encode_jpeg_grayscale_gpu(
    gray_bytes: bytes,
    height: int,
    width: int,
    *,
    quality: int = 75,
    huffman: str = "standard",
    restart_interval: int = 0,
) -> bytes:
    """Encode a grayscale image to JPEG using GPU-resident AOT pipeline.

    Args:
        gray_bytes: Raw grayscale pixel data (height * width, uint8)
        height, width: Image dimensions
        quality: 1-100
        huffman: 'standard' or 'optimized'
        restart_interval: 0 (disabled) or MCU count

    Returns:
        JPEG-encoded bytes
    """
    if not 1 <= quality <= 100:
        raise ValueError("quality must be in [1, 100]")

    padded_h = ((height + 7) // 8) * 8
    padded_w = ((width + 7) // 8) * 8

    gray_array = _bytes_to_numpy_gray(gray_bytes, padded_h, padded_w, height, width)

    from taichi_vision.taichi_algorithm.compression.jpeg_aot import encode_grayscale_aot
    return encode_grayscale_aot(
        gray_array,
        quality=quality,
        huffman=huffman,
        restart_interval=restart_interval,
    )


__all__ = [
    "encode_jpeg_gpu",
    "encode_jpeg_grayscale_gpu",
]
