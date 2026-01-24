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
            # Check if already initialized to avoid redundant logs/overhead
            is_initialized = False
            try:
                if ti.lang.impl.get_runtime().prog is not None:
                    is_initialized = True
            except:
                pass

            if not is_initialized:
                try:
                    ti.init(arch=ti.gpu, offline_cache=True, device_memory_GB=2.0)
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
            else:
                # Already initialized, continue using existing context
                pass
        except Exception as e:
            print(f"[Taichi] ERROR: Init failed entirely: {e}")

        # Store references to avoid garbage collection
        self.ref_img_gpu: any = None
        self.ref_work_res: any = None
        self.work_h: int = 0
        self.work_w: int = 0

    def clear_data(self):
        """Release image buffers without destroying the processor object or Taichi context."""
        if self.ref_img_gpu is not None:
            common.release_temp_buffer(self.ref_img_gpu)
            self.ref_img_gpu = None
        if self.ref_work_res is not None:
            common.release_temp_buffer(self.ref_work_res)
            self.ref_work_res = None
        self.work_h = 0
        self.work_w = 0
        # Explicitly clear the buffer cache to free all VRAM while keeping kernels
        common.cleanup_cache()

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
        Set reference image. Uploads 16-bit original to GPU for guidance
        and creates a low-res version for alignment.
        """
        # 1. Upload original reference to GPU (uint16/uint8)
        # ensure_taichi_field with dtype=None will pick native u16 if available
        self.ref_img_gpu, _ = common.ensure_taichi_field(
            ref_img, buffer_provider="pool"
        )

        # 2. Resize to work resolution on GPU for alignment (1-channel flow compute)
        # We use a specialized kernel that extract Green while resizing
        self.ref_work_res = common.get_temp_buffer(
            (work_h, work_w), ti.f32, buffer_provider="pool"
        )

        full_h, full_w = ref_img.shape[:2]

        # Correct bit detection: float=0, u16=16, u8=8
        input_bits = 0
        if ref_img.dtype == np.uint16:
            input_bits = 16
        elif ref_img.dtype == np.uint8:
            input_bits = 8

        # Use fused kernel to get low-res grayscale for alignment
        preprocess._fused_preprocess_kernel(
            self.ref_img_gpu,
            self.ref_work_res,
            full_h,
            full_w,
            work_h,
            work_w,
            proxy_scale if is_linear else 1.0,
            int(is_linear),
            input_bits,
            int(use_sharpen),
            2.22,
            4.5,
            0.018,  # default gamma params
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
        Modified Pipeline:
        1. Upload Comp (Original)
        2. Create Comp Work Res (Low-res Gray)
        3. Alignment (Compute Flow)
        4. Warp (Guided by Original Ref)
        """
        if self.ref_work_res is None:
            raise RuntimeError("Reference not set. Call set_reference_hybrid first.")

        # === STEP 1: Upload Original ===
        comp_img_gpu, _ = common.ensure_taichi_field(comp_img, buffer_provider="pool")

        # === STEP 2: Create low-res version for Alignment ===
        comp_work_res = common.get_temp_buffer(
            (self.work_h, self.work_w), ti.f32, buffer_provider="pool"
        )

        full_h, full_w = comp_img.shape[:2]

        # Correct bit detection: float=0, u16=16, u8=8
        input_bits = 0
        if comp_img.dtype == np.uint16:
            input_bits = 16
        elif comp_img.dtype == np.uint8:
            input_bits = 8

        preprocess._fused_preprocess_kernel(
            comp_img_gpu,
            comp_work_res,
            full_h,
            full_w,
            self.work_h,
            self.work_w,
            proxy_scale if is_linear else 1.0,
            int(is_linear),
            input_bits,
            int(use_sharpen),
            2.22,
            4.5,
            0.018,
        )

        # === STEP 3: Taichi Alignment ===
        flow_low_gpu = compute_alignment_flow(
            self.ref_work_res, comp_work_res, tile_h, tile_w, n_layers, search_dist
        )

        # Release comp aligned buffer (low res)
        common.release_temp_buffer(comp_work_res)

        if flow_low_gpu is None:
            common.release_temp_buffer(comp_img_gpu)
            raise RuntimeError("Taichi alignment failed to compute flow.")

        # === STEP 4: Scale flow to full resolution (GPU) ===
        flow_full_gpu = common.get_temp_buffer(
            (full_h, full_w, 2), ti.f32, buffer_provider="pool"
        )

        scale_x = full_w / self.work_w
        scale_y = full_h / self.work_h

        self._resize_flow_gpu(flow_low_gpu, flow_full_gpu, scale_x, scale_y)

        # Release low res flow
        common.release_temp_buffer(flow_low_gpu)

        # === STEP 5: GPU Warping (Directly from Original) ===
        # We pass self.ref_img_gpu as guidance!
        warped_img = self.warp_image(
            comp_img_gpu, flow_full_gpu, guidance=self.ref_img_gpu
        )

        # Release Resources
        common.release_temp_buffer(comp_img_gpu)
        common.release_temp_buffer(flow_full_gpu)

        return warped_img

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
    """Clear global processor data but keep the object and kernels alive."""
    global _GLOBAL_PROCESSOR
    # Important: Do NOT set _GLOBAL_PROCESSOR to None here.
    # We want to reuse the object and its compiled kernels in VRAM.
    if _GLOBAL_PROCESSOR is not None:
        try:
            _GLOBAL_PROCESSOR.clear_data()
            print("[Taichi] VRAM data cleared (Kernels persistent).")
        except Exception as e:
            print(f"[Taichi] Error clearing data: {e}")
            _GLOBAL_PROCESSOR = None  # Fallback: force recreation if clearing failed
    else:
        # If it was already None, just ensure cache is clean
        if TAICHI_AVAILABLE:
            common.cleanup_cache()
