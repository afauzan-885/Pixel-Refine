"""
YUV → RGB Converter - Taichi GPU
=================================
Konversi format kamera Android (YUV_420_888, NV21, NV12) ke RGB float32.
Ini adalah pintu masuk utama data dari Camera2 API ke pipeline Taichi.

Format yang didukung:
  - YUV_420_888: 3-plane (Y, U, V) - Camera2 default output
  - NV21: semi-planar Y + interleaved VU - Android legacy
  - NV12: semi-planar Y + interleaved UV

BT.601 conversion matrix (studio range):
  R = 1.164*(Y-16) + 1.596*(Cr-128)
  G = 1.164*(Y-16) - 0.813*(Cr-128) - 0.391*(Cb-128)
  B = 1.164*(Y-16) + 2.018*(Cb-128)

GPU Strategy:
  - One thread per output pixel (embarrassingly parallel)
  - Bilinear chroma upsampling built into kernel (420 → 444)
  - Output langsung float32 [0, 1] untuk pipeline Taichi
"""

import numpy as np
import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass


if TAICHI_AVAILABLE:

    # =========================================================================
    # Kernel: YUV_420_888 (3-plane) → RGB float32
    # =========================================================================
    @ti.kernel
    def _yuv420_3plane_to_rgb_kernel(
        y_plane: ti.types.ndarray(),    # (H, W) uint8
        u_plane: ti.types.ndarray(),    # (H/2, W/2) uint8
        v_plane: ti.types.ndarray(),    # (H/2, W/2) uint8
        dst: ti.types.ndarray(),        # (H, W, 3) float32
        h: int, w: int,
        y_row_stride: int, y_pixel_stride: int,
        u_row_stride: int, u_pixel_stride: int,
        v_row_stride: int, v_pixel_stride: int,
    ):
        """
        Konversi YUV_420_888 3-plane ke RGB float32 [0,1].
        Chroma subsampling di-handle via nearest-neighbor lookup (cepat).
        BT.601 studio range conversion.
        """
        for py, px in ti.ndrange(h, w):
            # Sample Y plane
            y_idx = py * y_row_stride + px * y_pixel_stride
            y_val = float(y_plane[y_idx]) - 16.0

            # Sample U/V plane (nearest for speed, 420 subsampled)
            cx = px // 2
            cy = py // 2
            u_idx = cy * u_row_stride + cx * u_pixel_stride
            v_idx = cy * v_row_stride + cx * v_pixel_stride
            u_val = float(u_plane[u_idx]) - 128.0
            v_val = float(v_plane[v_idx]) - 128.0

            # BT.601 conversion
            r = 1.164 * y_val + 1.596 * v_val
            g = 1.164 * y_val - 0.813 * v_val - 0.391 * u_val
            b = 1.164 * y_val + 2.018 * u_val

            # Clamp to [0, 1] and store RGB
            dst[py, px, 0] = tm.clamp(r / 255.0, 0.0, 1.0)
            dst[py, px, 1] = tm.clamp(g / 255.0, 0.0, 1.0)
            dst[py, px, 2] = tm.clamp(b / 255.0, 0.0, 1.0)

    # =========================================================================
    # Kernel: YUV_420_888 dengan Bilinear Chroma Upsampling (kualitas lebih baik)
    # =========================================================================
    @ti.kernel
    def _yuv420_bilinear_to_rgb_kernel(
        y_plane: ti.types.ndarray(),
        u_plane: ti.types.ndarray(),
        v_plane: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int, w: int,
        y_row_stride: int, y_pixel_stride: int,
        u_row_stride: int, u_pixel_stride: int,
        v_row_stride: int, v_pixel_stride: int,
    ):
        """
        Konversi YUV_420_888 dengan bilinear chroma upsampling.
        Menghasilkan kualitas lebih baik dari nearest-neighbor.
        """
        ch_h = h // 2
        ch_w = w // 2

        for py, px in ti.ndrange(h, w):
            # Y sample
            y_idx = py * y_row_stride + px * y_pixel_stride
            y_val = float(y_plane[y_idx]) - 16.0

            # Bilinear chroma upsampling
            # Koordinat di chroma plane (sub-pixel)
            cx_f = (float(px) + 0.5) / 2.0 - 0.5
            cy_f = (float(py) + 0.5) / 2.0 - 0.5

            # 4 neighbors
            cx0 = int(ti.floor(cx_f))
            cy0 = int(ti.floor(cy_f))
            cx1 = cx0 + 1
            cy1 = cy0 + 1

            # Clamp to valid chroma range
            cx0_c = tm.clamp(cx0, 0, ch_w - 1)
            cy0_c = tm.clamp(cy0, 0, ch_h - 1)
            cx1_c = tm.clamp(cx1, 0, ch_w - 1)
            cy1_c = tm.clamp(cy1, 0, ch_h - 1)

            # Bilinear weights
            fx = cx_f - float(cx0)
            fy = cy_f - float(cy0)

            # Sample U
            u00 = float(u_plane[cy0_c * u_row_stride + cx0_c * u_pixel_stride])
            u10 = float(u_plane[cy0_c * u_row_stride + cx1_c * u_pixel_stride])
            u01 = float(u_plane[cy1_c * u_row_stride + cx0_c * u_pixel_stride])
            u11 = float(u_plane[cy1_c * u_row_stride + cx1_c * u_pixel_stride])
            u_val = (u00 * (1-fx) * (1-fy) + u10 * fx * (1-fy) +
                     u01 * (1-fx) * fy + u11 * fx * fy) - 128.0

            # Sample V
            v00 = float(v_plane[cy0_c * v_row_stride + cx0_c * v_pixel_stride])
            v10 = float(v_plane[cy0_c * v_row_stride + cx1_c * v_pixel_stride])
            v01 = float(v_plane[cy1_c * v_row_stride + cx0_c * v_pixel_stride])
            v11 = float(v_plane[cy1_c * v_row_stride + cx1_c * v_pixel_stride])
            v_val = (v00 * (1-fx) * (1-fy) + v10 * fx * (1-fy) +
                     v01 * (1-fx) * fy + v11 * fx * fy) - 128.0

            # BT.601 conversion
            r = 1.164 * y_val + 1.596 * v_val
            g = 1.164 * y_val - 0.813 * v_val - 0.391 * u_val
            b = 1.164 * y_val + 2.018 * u_val

            dst[py, px, 0] = tm.clamp(r / 255.0, 0.0, 1.0)
            dst[py, px, 1] = tm.clamp(g / 255.0, 0.0, 1.0)
            dst[py, px, 2] = tm.clamp(b / 255.0, 0.0, 1.0)

    # =========================================================================
    # Kernel: NV21 (semi-planar) → RGB float32
    # =========================================================================
    @ti.kernel
    def _nv21_to_rgb_kernel(
        y_plane: ti.types.ndarray(),    # (H, W) uint8
        vu_interleaved: ti.types.ndarray(),  # (H/2, W) uint8 (VU VU VU...)
        dst: ti.types.ndarray(),        # (H, W, 3) float32
        h: int, w: int,
    ):
        """
        NV21 → RGB: Y plane + interleaved VU plane.
        NV21 = Android Camera1 default, masih banyak dipakai.
        """
        for py, px in ti.ndrange(h, w):
            y_val = float(y_plane[py * w + px]) - 16.0

            cx = px // 2
            cy = py // 2
            vu_idx = cy * w + cx * 2
            v_val = float(vu_interleaved[vu_idx]) - 128.0      # V first
            u_val = float(vu_interleaved[vu_idx + 1]) - 128.0  # U second

            r = 1.164 * y_val + 1.596 * v_val
            g = 1.164 * y_val - 0.813 * v_val - 0.391 * u_val
            b = 1.164 * y_val + 2.018 * u_val

            dst[py, px, 0] = tm.clamp(r / 255.0, 0.0, 1.0)
            dst[py, px, 1] = tm.clamp(g / 255.0, 0.0, 1.0)
            dst[py, px, 2] = tm.clamp(b / 255.0, 0.0, 1.0)

    # =========================================================================
    # Kernel: NV12 (semi-planar) → RGB float32
    # =========================================================================
    @ti.kernel
    def _nv12_to_rgb_kernel(
        y_plane: ti.types.ndarray(),
        uv_interleaved: ti.types.ndarray(),  # (H/2, W) uint8 (UV UV UV...)
        dst: ti.types.ndarray(),
        h: int, w: int,
    ):
        """NV12 → RGB: Y plane + interleaved UV plane."""
        for py, px in ti.ndrange(h, w):
            y_val = float(y_plane[py * w + px]) - 16.0

            cx = px // 2
            cy = py // 2
            uv_idx = cy * w + cx * 2
            u_val = float(uv_interleaved[uv_idx]) - 128.0      # U first
            v_val = float(uv_interleaved[uv_idx + 1]) - 128.0  # V second

            r = 1.164 * y_val + 1.596 * v_val
            g = 1.164 * y_val - 0.813 * v_val - 0.391 * u_val
            b = 1.164 * y_val + 2.018 * u_val

            dst[py, px, 0] = tm.clamp(r / 255.0, 0.0, 1.0)
            dst[py, px, 1] = tm.clamp(g / 255.0, 0.0, 1.0)
            dst[py, px, 2] = tm.clamp(b / 255.0, 0.0, 1.0)

    # =========================================================================
    # Kernel: YUV_420 → Grayscale float32 (untuk optical flow, alignment, dll)
    # =========================================================================
    @ti.kernel
    def _y_plane_to_gray_kernel(
        y_plane: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int, w: int,
        y_row_stride: int, y_pixel_stride: int,
    ):
        """
        Extract Y plane langsung ke grayscale float32 [0,1].
        Tidak perlu konversi warna - langsung copy Y.
        Berguna untuk optical flow, alignment, edge detection.
        """
        for py, px in ti.ndrange(h, w):
            y_idx = py * y_row_stride + px * y_pixel_stride
            dst[py, px] = float(y_plane[y_idx]) / 255.0


# =========================================================================
# Public API
# =========================================================================

@ti_thread
def yuv420_to_rgb(
    y_plane, u_plane, v_plane,
    height, width,
    y_row_stride=None, y_pixel_stride=1,
    u_row_stride=None, u_pixel_stride=1,
    v_row_stride=None, v_pixel_stride=1,
    bilinear_chroma=True,
    buffer_provider="pool",
):
    """
    Konversi YUV_420_888 (3-plane) ke RGB float32.

    Dioptimasi untuk Camera2 API output:
      image = reader.acquireLatestImage()
      y = image.getPlanes()[0].getBuffer()  # Y plane
      u = image.getPlanes()[1].getBuffer()  # U plane
      v = image.getPlanes()[2].getBuffer()  # V plane

    Args:
        y_plane: NumPy array (H*W,) atau (H, W) uint8
        u_plane: NumPy array (H/2 * W/2,) atau (H/2, W/2) uint8
        v_plane: NumPy array (H/2 * W/2,) atau (H/2, W/2) uint8
        height, width: Frame dimensions
        *_row_stride: Row stride bytes (dari Image.getPlanes()[i].getRowStride())
        *_pixel_stride: Pixel stride bytes (dari Image.getPlanes()[i].getPixelStride())
        bilinear_chroma: True = bilinear upsampling (kualitas), False = nearest (cepat)
        buffer_provider: Buffer pool provider

    Returns:
        RGB float32 array (H, W, 3) range [0, 1]
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Default strides (contiguous layout)
    if y_row_stride is None:
        y_row_stride = width
    if u_row_stride is None:
        u_row_stride = width // 2
    if v_row_stride is None:
        v_row_stride = width // 2

    # Flatten planes jika multi-dimensional
    y_flat = y_plane.ravel()
    u_flat = u_plane.ravel()
    v_flat = v_plane.ravel()

    # Upload to GPU
    y_gpu, y_temp = common.ensure_taichi_field(y_flat, dtype=ti.u8, buffer_provider=buffer_provider)
    u_gpu, u_temp = common.ensure_taichi_field(u_flat, dtype=ti.u8, buffer_provider=buffer_provider)
    v_gpu, v_temp = common.ensure_taichi_field(v_flat, dtype=ti.u8, buffer_provider=buffer_provider)

    # Allocate output
    dst_gpu = common.get_temp_buffer((height, width, 3), ti.f32, buffer_provider)

    # Dispatch kernel
    if bilinear_chroma:
        _yuv420_bilinear_to_rgb_kernel(
            y_gpu, u_gpu, v_gpu, dst_gpu,
            height, width,
            y_row_stride, y_pixel_stride,
            u_row_stride, u_pixel_stride,
            v_row_stride, v_pixel_stride,
        )
    else:
        _yuv420_3plane_to_rgb_kernel(
            y_gpu, u_gpu, v_gpu, dst_gpu,
            height, width,
            y_row_stride, y_pixel_stride,
            u_row_stride, u_pixel_stride,
            v_row_stride, v_pixel_stride,
        )

    # Cleanup input buffers
    if y_temp:
        common.release_temp_buffer(y_gpu)
    if u_temp:
        common.release_temp_buffer(u_gpu)
    if v_temp:
        common.release_temp_buffer(v_gpu)

    return dst_gpu


@ti_thread
def nv21_to_rgb(nv21_data, height, width, buffer_provider="pool"):
    """
    Konversi NV21 byte array ke RGB float32.

    Args:
        nv21_data: NumPy array (H*1.5*W,) uint8 - NV21 raw bytes
        height, width: Frame dimensions

    Returns:
        RGB float32 array (H, W, 3) range [0, 1]
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Split Y and VU
    y_size = height * width
    y_plane = nv21_data[:y_size]
    vu_plane = nv21_data[y_size:]

    y_gpu, y_temp = common.ensure_taichi_field(y_plane, dtype=ti.u8, buffer_provider=buffer_provider)
    vu_gpu, vu_temp = common.ensure_taichi_field(vu_plane, dtype=ti.u8, buffer_provider=buffer_provider)

    dst_gpu = common.get_temp_buffer((height, width, 3), ti.f32, buffer_provider)

    _nv21_to_rgb_kernel(y_gpu, vu_gpu, dst_gpu, height, width)

    if y_temp:
        common.release_temp_buffer(y_gpu)
    if vu_temp:
        common.release_temp_buffer(vu_gpu)

    return dst_gpu


@ti_thread
def nv12_to_rgb(nv12_data, height, width, buffer_provider="pool"):
    """
    Konversi NV12 byte array ke RGB float32.

    Args:
        nv12_data: NumPy array (H*1.5*W,) uint8 - NV12 raw bytes
        height, width: Frame dimensions

    Returns:
        RGB float32 array (H, W, 3) range [0, 1]
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    y_size = height * width
    y_plane = nv12_data[:y_size]
    uv_plane = nv12_data[y_size:]

    y_gpu, y_temp = common.ensure_taichi_field(y_plane, dtype=ti.u8, buffer_provider=buffer_provider)
    uv_gpu, uv_temp = common.ensure_taichi_field(uv_plane, dtype=ti.u8, buffer_provider=buffer_provider)

    dst_gpu = common.get_temp_buffer((height, width, 3), ti.f32, buffer_provider)

    _nv12_to_rgb_kernel(y_gpu, uv_gpu, dst_gpu, height, width)

    if y_temp:
        common.release_temp_buffer(y_gpu)
    if uv_temp:
        common.release_temp_buffer(uv_gpu)

    return dst_gpu


@ti_thread
def yuv_to_gray(y_plane, height, width, y_row_stride=None, y_pixel_stride=1,
                buffer_provider="pool"):
    """
    Extract Y plane langsung ke grayscale float32 [0,1].
    Zero-conversion cost - langsung copy Y channel.

    Berguna untuk:
      - Optical flow computation (farneback_flow butuh grayscale)
      - Feature detection (canny, sobel)
      - Alignment (phase_correlation, NCC)
      - Edge processing

    Args:
        y_plane: NumPy array (H*W,) atau (H, W) uint8
        height, width: Frame dimensions
        y_row_stride: Row stride (dari Camera2 Image plane)
        y_pixel_stride: Pixel stride

    Returns:
        Grayscale float32 (H, W) range [0, 1]
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    if y_row_stride is None:
        y_row_stride = width

    y_flat = y_plane.ravel()
    y_gpu, y_temp = common.ensure_taichi_field(y_flat, dtype=ti.u8, buffer_provider=buffer_provider)

    dst_gpu = common.get_temp_buffer((height, width), ti.f32, buffer_provider)

    _y_plane_to_gray_kernel(y_gpu, dst_gpu, height, width, y_row_stride, y_pixel_stride)

    if y_temp:
        common.release_temp_buffer(y_gpu)

    return dst_gpu
