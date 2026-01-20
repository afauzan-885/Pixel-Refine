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


class AlignmentTileTaichi:
    """Hybrid GPU/CPU class: GPU preprocessing/warping + C++ alignment computation."""

    def __init__(self, use_gpu=True):
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi is not installed or available.")

        # Initialize Taichi (Lazy Init on first use)
        try:
            os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"

            if not ti.get_runtime().is_initialized:
                ti.init(arch=ti.gpu, offline_cache=True)
        except:
            try:
                ti.init(arch=ti.cpu)
            except:
                pass

        self.ref_preprocessed_gpu: np.ndarray | None = None
        self.ref_work_res: np.ndarray | None = None
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
        Set reference image for hybrid pipeline.
        Preprocesses on GPU and caches for C++ backend.
        """
        # 1. Preprocess reference on GPU (full resolution)
        self.ref_preprocessed_gpu = self.preprocess_image(
            ref_img, is_linear, proxy_scale, use_sharpen
        )

        # 2. Resize to work resolution for C++ backend
        self.ref_work_res = cv2.resize(
            self.ref_preprocessed_gpu, (work_w, work_h), interpolation=cv2.INTER_LINEAR
        ).astype(np.float32)

        self.ref_work_res = np.ascontiguousarray(self.ref_work_res)
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
        Hybrid pipeline: GPU Preprocessing → C++ Alignment → GPU Warping

        Args:
            comp_img: Original comparison image (uint8/uint16)
            tile_h, tile_w: Tile size for C++ alignment
            n_layers: Number of pyramid layers for C++ backend
            align_lib: C++ library handle (ctypes.CDLL)
            is_linear: Whether image is in linear color space
            proxy_scale: Gamma proxy scale for linear images
            use_sharpen: Whether to apply contrast reduction
            search_dist: Search distance for C++ alignment

        Returns:
            Warped image (same dtype as input)
        """
        if self.ref_work_res is None:
            raise RuntimeError("Reference not set. Call set_reference_hybrid first.")

        if align_lib is None:
            raise RuntimeError("C++ alignment library not provided.")

        # === STEP 1: GPU Preprocessing ===
        comp_preprocessed_gpu = self.preprocess_image(
            comp_img, is_linear, proxy_scale, use_sharpen
        )

        # === STEP 2: Resize to work resolution for C++ ===
        comp_work_res = cv2.resize(
            comp_preprocessed_gpu,
            (int(self.work_w), int(self.work_h)),
            interpolation=cv2.INTER_LINEAR,
        ).astype(np.float32)
        comp_work_res = np.ascontiguousarray(comp_work_res)

        # === STEP 3: C++ Backend Alignment Computation ===
        ref_work_ptr = self.ref_work_res.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        comp_work_ptr = comp_work_res.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        flow_ptr = align_lib.compute_alignment_flow(
            ref_work_ptr,
            comp_work_ptr,
            self.work_h,
            self.work_w,
            tile_h,
            tile_w,
            n_layers,
            search_dist,
        )

        if not flow_ptr:
            raise RuntimeError("C++ alignment failed to compute flow.")

        # === STEP 4: Read flow from C++ memory ===
        flow_work_res = np.empty(
            (int(self.work_h), int(self.work_w), 2), dtype=np.float32
        )
        ctypes.memmove(
            flow_work_res.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            flow_ptr,
            flow_work_res.nbytes,
        )

        # Free C++ memory
        align_lib.free_flow_memory(flow_ptr)

        # === STEP 5: Scale flow to full resolution ===
        full_h, full_w = comp_img.shape[:2]
        flow_full_res = self._scale_flow_to_full_res(
            flow_work_res, self.work_h, self.work_w, full_h, full_w
        )

        # === STEP 6: GPU Warping ===
        # Use the preprocessed reference (grayscale) as guidance to refine flow edges
        warped_img = self.warp_image(
            comp_img, flow_full_res, guidance=self.ref_preprocessed_gpu
        )

        return warped_img

    def _scale_flow_to_full_res(self, flow, work_h, work_w, full_h, full_w):
        """Scale flow from work resolution to full resolution."""
        scale_x = full_w / work_w
        scale_y = full_h / work_h

        # Resize flow field
        flow_full = cv2.resize(flow, (full_w, full_h), interpolation=cv2.INTER_LINEAR)

        # Scale flow values
        flow_full[:, :, 0] *= scale_x  # dx
        flow_full[:, :, 1] *= scale_y  # dy

        return flow_full

    def preprocess_image(
        self,
        img,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
    ):
        """Preprocess image on GPU using standardized preprocess module."""
        # Detect input bits based on dtype. If already float, assume [0, 1] (bits=0)
        input_bits = 0
        if img.dtype == np.uint16:
            input_bits = 16
        elif img.dtype == np.uint8:
            input_bits = 8

        # print(f"[Taichi] Preprocessing input: {img.shape}, {img.dtype}, bits={input_bits}, linear={is_linear}, sharpen={use_sharpen}")

        # Call the robust preprocess module (now includes sharpening and custom gamma)
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

        # Handle return to numpy
        if hasattr(gray_gpu, "to_numpy"):
            return gray_gpu.to_numpy()
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


# --- Compatibility Wrappers ---

_GLOBAL_PROCESSOR = None


def set_reference_hybrid_taichi(
    ref_img,
    work_h,
    work_w,
    is_linear=False,
    proxy_scale=1.0,
    use_sharpen=False,
):
    """Set reference for hybrid GPU/CPU pipeline."""
    global _GLOBAL_PROCESSOR
    if _GLOBAL_PROCESSOR is None:
        _GLOBAL_PROCESSOR = AlignmentTileTaichi()

    _GLOBAL_PROCESSOR.set_reference_hybrid(
        ref_img, work_h, work_w, is_linear, proxy_scale, use_sharpen
    )


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
    global _GLOBAL_PROCESSOR
    if _GLOBAL_PROCESSOR is None:
        raise RuntimeError(
            "Processor not initialized. Call set_reference_hybrid_taichi first."
        )

    return _GLOBAL_PROCESSOR.compute_alignment_and_warp_hybrid(
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
    global _GLOBAL_PROCESSOR
    if _GLOBAL_PROCESSOR is None:
        _GLOBAL_PROCESSOR = AlignmentTileTaichi()

    return _GLOBAL_PROCESSOR.preprocess_image(img, is_linear, proxy_scale, use_sharpen)


def warp_image_taichi(img, flow):
    """Warp image wrapper."""
    global _GLOBAL_PROCESSOR
    if _GLOBAL_PROCESSOR is None:
        _GLOBAL_PROCESSOR = AlignmentTileTaichi()

    return _GLOBAL_PROCESSOR.warp_image(img, flow)


def resize_image_taichi(img, target_h, target_w):
    """Resize image wrapper."""
    global _GLOBAL_PROCESSOR
    if _GLOBAL_PROCESSOR is None:
        _GLOBAL_PROCESSOR = AlignmentTileTaichi()

    return _GLOBAL_PROCESSOR.resize_image(img, target_h, target_w)


def clear_taichi_cache():
    """Clear global processor cache."""
    global _GLOBAL_PROCESSOR
    _GLOBAL_PROCESSOR = None
    if TAICHI_AVAILABLE:
        common.cleanup_cache()
