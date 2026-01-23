"""
Taichi GPU Implementation - Hybrid GPU/CPU Pipeline
====================================================
This module provides a hybrid pipeline:
- GPU: Preprocessing and Warping (Taichi)
- CPU: Alignment Computation (C++ Backend)

Pipeline: GPU Preprocessing → C++ Alignment → GPU Warping
"""

import numpy as np
import cv2, os
import ctypes
import threading

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_flow import (
    compute_alignment_flow,
)

try:
    import taichi as ti
    import taichi.math as tm
    from ...taichi_algorithm import common, warp, preprocess, bilinear_interpolation

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    from typing import Any

    ti: Any = None
    tm: Any = None
    common: Any = None
    warp: Any = None
    preprocess: Any = None
    bilinear_interpolation: Any = None


@ti.data_oriented
class AlignmentTileTaichi:
    """GPU-accelerated alignment pipeline using Taichi."""

    def __init__(self, use_gpu=True):
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi is not installed or available.")

        # Store init thread to detect context mismatches
        self.init_thread_id = threading.get_ident()

        # Initialize Taichi (Lazy Init on first use)
        try:
            os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"
            try:
                ti.init(arch=ti.gpu, offline_cache=True)
            except Exception as e:
                if "already initialized" in str(e).lower():
                    pass
                else:
                    print(f"[Taichi] WARN: GPU init failed: {e}")
                    print("[Taichi] Fallback to CPU...")
                    try:
                        ti.init(arch=ti.cpu)
                    except Exception as ex:
                        if "already initialized" in str(ex).lower():
                            pass
                        else:
                            raise ex
        except Exception as e:
            print(f"[Taichi] ERROR: Init failed entirely: {e}")

        self.ref_preprocessed_gpu: any = None
        self.ref_work_res: any = None
        self.work_h: int = 0
        self.work_w: int = 0

    def set_reference_hybrid(
        self,
        ref_img,
        work_h,
        work_w,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
    ):
        """
        Set reference image for the alignment pipeline.
        Preprocesses on GPU and caches pre-resized work resolution image.
        """
        # 1. Preprocess reference on GPU (full resolution)
        self.ref_preprocessed_gpu = self.preprocess_image(
            ref_img, is_linear, proxy_scale, use_sharpen
        )

        # 2. Resize to work resolution on GPU to avoid download
        full_h, full_w = self.ref_preprocessed_gpu.shape[:2]

        self.ref_work_res = common.get_temp_buffer(
            (work_h, work_w), ti.f32, buffer_provider="pool"
        )

        bilinear_interpolation._bilinear_resize_kernel(
            self.ref_preprocessed_gpu, self.ref_work_res, full_h, full_w, work_h, work_w
        )

        self.work_h = work_h
        self.work_w = work_w

    def compute_alignment_and_warp_hybrid(
        self,
        comp_img,
        tile_h,
        tile_w,
        n_layers,
        align_lib,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
        search_dist=2.0,
    ):
        """
        Complete Alignment & Warp Pipeline: GPU Preprocess → GPU Alignment → GPU Warp.
        """
        if self.ref_work_res is None:
            raise RuntimeError("Reference not set. Call set_reference_hybrid first.")

        # === STEP 1: GPU Preprocessing ===
        comp_preprocessed_gpu = self.preprocess_image(
            comp_img, is_linear, proxy_scale, use_sharpen
        )

        # === STEP 2: Resize to work resolution for Alignment ===
        comp_work_res = common.get_temp_buffer(
            (self.work_h, self.work_w), ti.f32, buffer_provider="pool"
        )

        bilinear_interpolation._bilinear_resize_kernel(
            comp_preprocessed_gpu,
            comp_work_res,
            comp_preprocessed_gpu.shape[0],
            comp_preprocessed_gpu.shape[1],
            self.work_h,
            self.work_w,
        )

        # === STEP 3: Taichi Alignment ===
        flow_gpu = compute_alignment_flow(
            self.ref_work_res, comp_work_res, tile_h, tile_w, n_layers, search_dist
        )

        # Release comp aligned buffer
        common.release_temp_buffer(comp_work_res)

        if flow_gpu is None:
            raise RuntimeError("Taichi alignment failed to compute flow.")

        # === STEP 4: Scale flow to full resolution (GPU) ===
        full_h, full_w = comp_img.shape[:2]

        flow_full_gpu = common.get_temp_buffer(
            (full_h, full_w, 2), ti.f32, buffer_provider="pool"
        )

        scale_x = full_w / self.work_w
        scale_y = full_h / self.work_h

        self._resize_flow_gpu(flow_gpu, flow_full_gpu, scale_x, scale_y)

        # Release low res flow
        common.release_temp_buffer(flow_gpu)

        # === STEP 5: GPU Warping ===
        warped_img = self.warp_image(
            comp_img, flow_full_gpu, guidance=self.ref_preprocessed_gpu
        )

        # Release full res flow
        common.release_temp_buffer(flow_full_gpu)

        return warped_img

    @ti.kernel
    def _resize_flow_kernel(
        self,
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        scale_x: float,
        scale_y: float,
    ):
        # Simple bilinear resize + value scaling for (H, W, 2) flow fields
        for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
            # Normalized coordinates
            u = (x + 0.5) / float(dst.shape[1])  # horizontal
            v = (y + 0.5) / float(dst.shape[0])  # vertical

            # Map to src pixel coords
            src_x = u * float(src.shape[1]) - 0.5
            src_y = v * float(src.shape[0]) - 0.5

            x0 = int(ti.floor(src_x))
            y0 = int(ti.floor(src_y))
            fx = src_x - x0
            fy = src_y - y0

            # Clamp indices
            x0 = ti.max(0, ti.min(x0, src.shape[1] - 2))
            y0 = ti.max(0, ti.min(y0, src.shape[0] - 2))
            x1 = x0 + 1
            y1 = y0 + 1

            # Sample each channel
            for c in ti.static(range(2)):
                v00 = src[y0, x0, c]
                v10 = src[y0, x1, c]
                v01 = src[y1, x0, c]
                v11 = src[y1, x1, c]

                top = v00 * (1 - fx) + v10 * fx
                bottom = v01 * (1 - fx) + v11 * fx
                val = top * (1 - fy) + bottom * fy

                # Apply scaling factor based on channel
                scale = scale_x if c == 0 else scale_y
                dst[y, x, c] = val * scale

    def _resize_flow_gpu(self, src_flow, dst_flow, scale_x, scale_y):
        self._resize_flow_kernel(src_flow, dst_flow, scale_x, scale_y)

    def preprocess_image(
        self,
        img,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
    ):
        """Preprocess image on GPU returns GPU field."""
        input_bits = 0
        if img.dtype == np.uint16:
            input_bits = 16
        elif img.dtype == np.uint8:
            input_bits = 8

        # Call the robust preprocess module
        gray_gpu = preprocess.preprocess_gpu(
            img,
            scale=proxy_scale if is_linear else 1.0,
            apply_gamma=is_linear,
            input_bits=input_bits,
            gamma_pow=2.22,
            slope=4.5,
            cutoff=0.018,
            use_sharpen=use_sharpen,
        )

        # Optimized: Return GPU handle directly, NO to_numpy()
        return gray_gpu

    def warp_image(self, img, flow, guidance=None):
        """Warp image using provided flow field via warp module."""
        return warp.warp_image_gpu(img, flow, guidance=guidance)

    def resize_image(self, img, target_h, target_w):
        """Resize image on GPU using standardized bilinear module."""
        img_field, _ = common.ensure_taichi_field(img)
        h_src, w_src = img.shape[0], img.shape[1]

        resized = ti.ndarray(ti.f32, shape=(target_h, target_w))

        # Call kernel directly to share context (avoid double init)
        bilinear_interpolation._bilinear_resize_kernel(
            img_field, resized, h_src, w_src, target_h, target_w
        )

        return resized.to_numpy()


# --- Global Instance & Safe Access ---

_GLOBAL_PROCESSOR = None


def _get_safe_processor():
    global _GLOBAL_PROCESSOR
    current_tid = threading.get_ident()

    if _GLOBAL_PROCESSOR is not None:
        if _GLOBAL_PROCESSOR.init_thread_id != current_tid:
            print(
                f"[Taichi] Thread Mismatch! (Init: {_GLOBAL_PROCESSOR.init_thread_id}, Curr: {current_tid}). Resetting Runtime..."
            )
            _GLOBAL_PROCESSOR = None
            try:
                # Cleanup internal cache before reset to drop stale references
                if common is not None:
                    common.cleanup_cache()
                ti.reset()
            except:
                pass

    if _GLOBAL_PROCESSOR is None:
        _GLOBAL_PROCESSOR = AlignmentTileTaichi()

    return _GLOBAL_PROCESSOR


def set_reference_hybrid_taichi(
    ref_img,
    work_h,
    work_w,
    is_linear=False,
    proxy_scale=1.0,
    use_sharpen=False,
):
    """Set reference for hybrid GPU/CPU pipeline."""
    try:
        proc = _get_safe_processor()
        proc.set_reference_hybrid(
            ref_img, work_h, work_w, is_linear, proxy_scale, use_sharpen
        )
    except RuntimeError as e:
        if "CUDA_ERROR_INVALID_CONTEXT" in str(e):
            print("[Taichi] Invalid Context detected. Forcing reset and retry...")
            global _GLOBAL_PROCESSOR
            _GLOBAL_PROCESSOR = None
            try:
                if common is not None:
                    common.cleanup_cache()
                ti.reset()
            except:
                pass

            # Retry once
            proc = _get_safe_processor()
            proc.set_reference_hybrid(
                ref_img, work_h, work_w, is_linear, proxy_scale, use_sharpen
            )
        else:
            raise e


def compute_alignment_and_warp_hybrid_taichi(
    comp_img,
    tile_h,
    tile_w,
    n_layers,
    align_lib,
    is_linear=False,
    proxy_scale=1.0,
    use_sharpen=False,
    search_dist=2.0,
):
    """
    Hybrid pipeline wrapper: GPU Preprocessing → C++ Alignment → GPU Warping

    Must call set_reference_hybrid_taichi first.
    """
    # Note: We use existing processor which must have reference set
    proc = _get_safe_processor()
    return proc.compute_alignment_and_warp_hybrid(
        comp_img,
        tile_h,
        tile_w,
        n_layers,
        align_lib,
        is_linear,
        proxy_scale,
        use_sharpen,
        search_dist,
    )


def preprocess_image_taichi(
    img,
    is_linear=False,
    proxy_scale=1.0,
    use_sharpen=False,
):
    """Preprocess image wrapper."""
    proc = _get_safe_processor()
    return proc.preprocess_image(img, is_linear, proxy_scale, use_sharpen)


def warp_image_taichi(img, flow):
    """Warp image wrapper."""
    proc = _get_safe_processor()
    return proc.warp_image(img, flow)


def resize_image_taichi(img, target_h, target_w):
    """Resize image wrapper."""
    proc = _get_safe_processor()
    return proc.resize_image(img, target_h, target_w)


def clear_taichi_cache():
    """Clear global processor cache."""
    global _GLOBAL_PROCESSOR
    _GLOBAL_PROCESSOR = None
    if TAICHI_AVAILABLE:
        common.cleanup_cache()
