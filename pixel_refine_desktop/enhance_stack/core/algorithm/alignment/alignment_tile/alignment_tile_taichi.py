"""
Taichi Dual Backend Architecture - JIT & AOT Support
====================================================
This module provides a unified interface for image alignment:
1. DEVELOPMENT Mode (JIT): Uses Taichi Python kernels (Just-in-Time).
2. PRODUCTION Mode (AOT): Uses C++ Modular TiRT Backend (Ahead-of-Time).

Controlled by os.environ["PIXEL_REFINE_BACKEND"]
"""

import os
import numpy as np
import ctypes
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.taichi_worker import (
    ti_thread,
)

# --- JIT Dependencies ---
try:
    import taichi as ti
    from ...taichi_algorithm import common, warp, preprocess, bilinear_interpolation
    from .compute_flow import compute_alignment_flow

    TAICHI_JIT_AVAILABLE = True
except ImportError:
    TAICHI_JIT_AVAILABLE = False
    ti = None

# Global flag for other modules to detect if Taichi-based alignment is supported
# It's True if either JIT is possible or if we are in PRODUCTION mode (AOT)
TAICHI_AVAILABLE = TAICHI_JIT_AVAILABLE or (
    os.environ.get("PIXEL_REFINE_BACKEND") == "PRODUCTION"
)


# ============================================================================
# 1. PRODUCTION BACKEND (AOT via C++ TiRT Bridge)
# ============================================================================
class AlignmentTileTaichiAOT:
    """Production-ready AOT alignment backend using C++ TiRT Bridge."""

    def __init__(self, data_dir=None, arch="vulkan"):
        self.arch = arch
        # Jika data_dir tidak diberikan, asumsikan default
        if data_dir is None:
            # Let's find pixel_refine_desktop folder reliably
            curr = os.path.abspath(__file__)
            # Go up until we find enhance_stack or reached root
            while "enhance_stack" in curr:
                curr = os.path.dirname(curr)
            
            # Now curr should be pixel_refine_desktop folder
            data_dir = os.path.join(curr, "ui", "data")

        # Path DLL di ui/data
        self.lib_path = os.path.abspath(os.path.join(data_dir, "preprocessing_aot.dll"))
        # Path AOT Module di ui/data/aot_assets/preprocess
        self.aot_module_path = os.path.abspath(os.path.join(data_dir, "aot_assets", "preprocess"))

        self.lib = None
        self.initialized = False
        self.ref_img_gpu = None
        self.ref_work_res = None
        self.work_h = 0
        self.work_w = 0

        # Try to load the library
        try:
            if os.path.exists(self.lib_path):
                self.lib = ctypes.CDLL(self.lib_path)

                # Define function signatures
                self.lib.init_taichi_aot_runtime.argtypes = [ctypes.c_char_p]
                self.lib.init_taichi_aot_runtime.restype = ctypes.c_int

                self.lib.compute_preprocess_aot.argtypes = [
                    ctypes.POINTER(ctypes.c_int32),  # src_ptr
                    ctypes.POINTER(ctypes.c_float),  # dst_ptr
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,  # src h, w, c
                    ctypes.c_int,
                    ctypes.c_int,  # dst h, w
                    ctypes.c_float, # scale_norm
                    ctypes.c_int,   # apply_gamma
                    ctypes.c_float, # scale_gamma
                    ctypes.c_float, # gamma_pow
                    ctypes.c_float, # slope
                    ctypes.c_float, # cutoff
                    ctypes.c_int,   # use_sharpen
                ]
                self.lib.compute_preprocess_aot.restype = ctypes.c_int

                # Initialize runtime
                res = self.lib.init_taichi_aot_runtime(
                    self.aot_module_path.encode("utf-8")
                )
                if res == 0:
                    self.initialized = True
                    print(
                        f"[TaichiAOT] Mode: PRODUCTION (AOT) initialized on {self.arch.upper()}"
                    )
                else:
                    print(f"[TaichiAOT] Initialization failed with code: {res}")
            else:
                print(f"[TaichiAOT] DLL not found at: {self.lib_path}")
        except Exception as e:
            print(f"[TaichiAOT] Error loading AOT bridge: {e}")

    def set_reference(
        self,
        ref_img,
        work_h,
        work_w,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
        **kwargs,
    ):
        """Preprocess reference image using AOT GPU pipeline."""
        if not self.initialized:
            print("[TaichiAOT] Backend not initialized, skipping set_reference.")
            return

        # 1. Upload original reference to GPU (untuk warping nanti)
        self.ref_img_gpu, _ = common.ensure_taichi_field(
            ref_img, buffer_provider="pool"
        )

        h, w = ref_img.shape[:2]
        c = ref_img.shape[2] if len(ref_img.shape) == 3 else 1

        # Determine normalization scale
        dtype = ref_img.dtype
        scale_norm = (
            float(np.iinfo(dtype).max) if np.issubdtype(dtype, np.integer) else 1.0
        )
        scale_gamma = proxy_scale if is_linear else 1.0

        # 2. Preprocess via AOT (Hasilnya NumPy)
        res_np = np.zeros((work_h, work_w), dtype=np.float32)

        # Ensure input is int32 for the AOT graph compat
        if ref_img.dtype != np.int32:
            ref_img_int = ref_img.astype(np.int32)
        else:
            ref_img_int = ref_img

        src_ptr = ref_img_int.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        dst_ptr = res_np.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        if self.lib:
            self.lib.compute_preprocess_aot(
                src_ptr,
                dst_ptr,
                h,
                w,
                c,
                work_h,
                work_w,
                scale_norm,
                int(is_linear),
                scale_gamma,
                kwargs.get("gamma_pow", 2.22),
                kwargs.get("slope", 4.5),
                kwargs.get("cutoff", 0.018),
                int(use_sharpen),
            )

        # 3. Convert back to Taichi Field agar bisa diproses oleh kernel JIT lainnya
        self.ref_work_res, _ = common.ensure_taichi_field(
            res_np, buffer_provider="pool"
        )

        self.work_h, self.work_w = work_h, work_w

    def compute_alignment_and_warp(
        self,
        comp_img,
        tile_h,
        tile_w,
        n_layers,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
        search_dist=2.0,
        return_format: str = "numpy_u16",
        **kwargs,
    ):
        """Alignment via Hybrid AOT-JIT Pipeline."""
        if not self.initialized or self.ref_work_res is None:
            return None

        full_h, full_w = comp_img.shape[:2]
        c = comp_img.shape[2] if len(comp_img.shape) == 3 else 1
        comp_img_gpu, _ = common.ensure_taichi_field(comp_img, buffer_provider="pool")

        # Determine normalization scale
        dtype = comp_img.dtype
        scale_norm = (
            float(np.iinfo(dtype).max) if np.issubdtype(dtype, np.integer) else 1.0
        )
        scale_gamma = proxy_scale if is_linear else 1.0

        # 1. Preprocess Comparison Frame via AOT (Hasilnya NumPy)
        res_np = np.zeros((self.work_h, self.work_w), dtype=np.float32)

        if comp_img.dtype != np.int32:
            comp_img_int = comp_img.astype(np.int32)
        else:
            comp_img_int = comp_img

        src_ptr = comp_img_int.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        dst_ptr = res_np.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        if self.lib:
            self.lib.compute_preprocess_aot(
                src_ptr,
                dst_ptr,
                full_h,
                full_w,
                c,
                self.work_h,
                self.work_w,
                scale_norm,
                int(is_linear),
                scale_gamma,
                kwargs.get("gamma_pow", 2.22),
                kwargs.get("slope", 4.5),
                kwargs.get("cutoff", 0.018),
                int(use_sharpen),
            )

        # Convert back to Taichi Field for JIT kernels
        comp_work_res, _ = common.ensure_taichi_field(res_np, buffer_provider="pool")

        # 2. Compute Flow (JIT)
        flow_low_gpu = compute_alignment_flow(
            self.ref_work_res, comp_work_res, tile_h, tile_w, n_layers, search_dist
        )
        common.release_temp_buffer(comp_work_res)

        if flow_low_gpu is None:
            common.release_temp_buffer(comp_img_gpu)
            return None

        # 3. Upsample Flow (JIT)
        flow_full_gpu = common.get_temp_buffer(
            (full_h, full_w, 2), ti.f32, buffer_provider="pool"
        )
        self._resize_flow_gpu(
            flow_low_gpu, flow_full_gpu, full_w / self.work_w, full_h / self.work_h
        )
        common.release_temp_buffer(flow_low_gpu)

        # 4. Warp Image (JIT)
        warped_img_gpu = warp.warp_image_gpu(
            comp_img_gpu, flow_full_gpu, guidance=self.ref_img_gpu
        )
        common.release_temp_buffer(comp_img_gpu)
        common.release_temp_buffer(flow_full_gpu)

        # --- Return format dispatch ---
        is_taichi_ndarray = hasattr(warped_img_gpu, "to_numpy")

        if return_format == "ti_ndarray":
            return warped_img_gpu
        elif return_format == "numpy_f32":
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.float32) / 65535.0
            if is_taichi_ndarray:
                common.release_temp_buffer(warped_img_gpu)
            return result
        else:  # "numpy_u16"
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.uint16)
            if is_taichi_ndarray:
                common.release_temp_buffer(warped_img_gpu)
            return result

    def _resize_flow_gpu(self, src, dst, sx, sy):
        # Local kernel to avoid global scope issues
        @ti.kernel
        def _resize_k(s: ti.types.ndarray(), d: ti.types.ndarray(), x: float, y: float):
            for r, c in ti.ndrange(d.shape[0], d.shape[1]):
                u, v = (c + 0.5) / d.shape[1], (r + 0.5) / d.shape[0]
                sr, sc = v * s.shape[0] - 0.5, u * s.shape[1] - 0.5
                r0, c0 = int(ti.floor(sr)), int(ti.floor(sc))
                fr, fc = sr - r0, sc - c0
                r0, r1 = ti.max(0, ti.min(r0, s.shape[0] - 2)), ti.max(
                    0, ti.min(r0 + 1, s.shape[0] - 1)
                )
                c0, c1 = ti.max(0, ti.min(c0, s.shape[1] - 2)), ti.max(
                    0, ti.min(c0 + 1, s.shape[1] - 1)
                )
                for i in ti.static(range(2)):
                    v00, v01, v10, v11 = (
                        s[r0, c0, i],
                        s[r0, c1, i],
                        s[r1, c0, i],
                        s[r1, c1, i],
                    )
                    val = (
                        v00 * (1 - fc) * (1 - fr)
                        + v01 * fc * (1 - fr)
                        + v10 * (1 - fc) * fr
                        + v11 * fc * fr
                    )
                    d[r, c, i] = val * (x if i == 0 else y)

        _resize_k(src, dst, sx, sy)

    def clear_data(self):
        if self.ref_img_gpu:
            common.release_temp_buffer(self.ref_img_gpu)
            self.ref_img_gpu = None
        if self.ref_work_res:
            common.release_temp_buffer(self.ref_work_res)
            self.ref_work_res = None
        common.cleanup_cache()


# ============================================================================
# 2. DEVELOPMENT BACKEND (JIT via Python)
# ============================================================================
class AlignmentTileTaichiJIT:
    """Original JIT-based alignment using Taichi Python Kernels."""

    def __init__(self):
        if not TAICHI_JIT_AVAILABLE:
            raise ImportError("Taichi JIT components not found.")
        self.ref_img_gpu = None
        self.ref_work_res = None
        self.work_h = 0
        self.work_w = 0

    def set_reference(
        self,
        ref_img,
        work_h,
        work_w,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
        **kwargs,
    ):
        # 1. Upload original reference to GPU
        self.ref_img_gpu, _ = common.ensure_taichi_field(
            ref_img, buffer_provider="pool"
        )

        # 2. Preprocess (Normalize -> Green -> Resize)
        self.ref_work_res = preprocess.preprocess_pipeline_gpu(
            ref_img,
            normalize=True,
            apply_gamma=is_linear,
            extract_green=True,
            use_sharpen=use_sharpen,
            scale=proxy_scale,
            target_size=(work_h, work_w),
            buffer_provider="pool",
            return_numpy=False,
        )
        self.work_h, self.work_w = work_h, work_w

    def compute_alignment_and_warp(
        self,
        comp_img,
        tile_h,
        tile_w,
        n_layers,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
        search_dist=2.0,
        return_format: str = "numpy_u16",
        **kwargs,
    ):
        if self.ref_work_res is None:
            return None

        full_h, full_w = comp_img.shape[:2]
        comp_img_gpu, _ = common.ensure_taichi_field(comp_img, buffer_provider="pool")

        # Preprocess comparison frame
        comp_work_res = preprocess.preprocess_pipeline_gpu(
            comp_img,
            normalize=True,
            apply_gamma=is_linear,
            extract_green=True,
            use_sharpen=use_sharpen,
            scale=proxy_scale,
            target_size=(self.work_h, self.work_w),
            buffer_provider="pool",
            return_numpy=False,
        )

        # Compute Flow (JIT)
        flow_low_gpu = compute_alignment_flow(
            self.ref_work_res, comp_work_res, tile_h, tile_w, n_layers, search_dist
        )
        common.release_temp_buffer(comp_work_res)

        if flow_low_gpu is None:
            common.release_temp_buffer(comp_img_gpu)
            return None

        # Upsample Flow
        flow_full_gpu = common.get_temp_buffer(
            (full_h, full_w, 2), ti.f32, buffer_provider="pool"
        )
        self._resize_flow_gpu(
            flow_low_gpu, flow_full_gpu, full_w / self.work_w, full_h / self.work_h
        )
        common.release_temp_buffer(flow_low_gpu)

        # Warp (result is ti.ndarray in VRAM)
        warped_img_gpu = warp.warp_image_gpu(
            comp_img_gpu, flow_full_gpu, guidance=self.ref_img_gpu
        )
        common.release_temp_buffer(comp_img_gpu)
        common.release_temp_buffer(flow_full_gpu)

        # --- Return format dispatch ---
        # warp_image_gpu() may return a Taichi ndarray (VRAM) OR a plain numpy array.
        # Use hasattr guard to handle both cases safely.
        is_taichi_ndarray = hasattr(warped_img_gpu, "to_numpy")

        if return_format == "ti_ndarray":
            # Caller owns the buffer; must call common.release_temp_buffer() when done.
            # If already numpy, wrap it — caller should treat it as read-only numpy.
            return warped_img_gpu
        elif return_format == "numpy_f32":
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.float32) / 65535.0
            if is_taichi_ndarray:
                common.release_temp_buffer(warped_img_gpu)
            return result
        else:  # "numpy_u16" (default) — most memory-efficient for CPU merging
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.uint16)
            if is_taichi_ndarray:
                common.release_temp_buffer(warped_img_gpu)
            return result

    def _resize_flow_gpu(self, src, dst, sx, sy):
        # Local kernel to avoid global scope issues
        @ti.kernel
        def _resize_k(s: ti.types.ndarray(), d: ti.types.ndarray(), x: float, y: float):
            for r, c in ti.ndrange(d.shape[0], d.shape[1]):
                u, v = (c + 0.5) / d.shape[1], (r + 0.5) / d.shape[0]
                sr, sc = v * s.shape[0] - 0.5, u * s.shape[1] - 0.5
                r0, c0 = int(ti.floor(sr)), int(ti.floor(sc))
                fr, fc = sr - r0, sc - c0
                r0, r1 = ti.max(0, ti.min(r0, s.shape[0] - 2)), ti.max(
                    0, ti.min(r0 + 1, s.shape[0] - 1)
                )
                c0, c1 = ti.max(0, ti.min(c0, s.shape[1] - 2)), ti.max(
                    0, ti.min(c0 + 1, s.shape[1] - 1)
                )
                for i in ti.static(range(2)):
                    v00, v01, v10, v11 = (
                        s[r0, c0, i],
                        s[r0, c1, i],
                        s[r1, c0, i],
                        s[r1, c1, i],
                    )
                    val = (
                        v00 * (1 - fc) * (1 - fr)
                        + v01 * fc * (1 - fr)
                        + v10 * (1 - fc) * fr
                        + v11 * fc * fr
                    )
                    d[r, c, i] = val * (x if i == 0 else y)

        _resize_k(src, dst, sx, sy)

    def clear_data(self):
        if self.ref_img_gpu:
            common.release_temp_buffer(self.ref_img_gpu)
            self.ref_img_gpu = None
        if self.ref_work_res:
            common.release_temp_buffer(self.ref_work_res)
            self.ref_work_res = None
        common.cleanup_cache()


# ============================================================================
# 3. DISPATCHER & GLOBAL INTERFACE
# ============================================================================
_PROCESSOR = None


def _get_processor():
    global _PROCESSOR
    if _PROCESSOR is None:
        mode = os.environ.get("PIXEL_REFINE_BACKEND", "DEVELOPMENT")

        # Detect best architecture
        best_arch = "vulkan"
        try:
            import taichi as ti

            if ti._lib.core.is_cuda_available():
                best_arch = "cuda"
            elif not ti._lib.core.is_vulkan_available():
                best_arch = "cpu"
        except:
            pass

        if mode == "PRODUCTION":
            # Ganti ke path absolut agar lebih robust
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(script_dir, "../../../../../", "ui", "data")
            data_dir = os.path.abspath(data_dir)
            _PROCESSOR = AlignmentTileTaichiAOT(data_dir, arch=best_arch)
        else:
            _PROCESSOR = AlignmentTileTaichiJIT()
            print(f"[Taichi] Mode: DEVELOPMENT (JIT) on {best_arch.upper()}")
    return _PROCESSOR


@ti_thread
def set_reference_hybrid_taichi(ref_img, work_h, work_w, **kwargs):
    _get_processor().set_reference(ref_img, work_h=work_h, work_w=work_w, **kwargs)


@ti_thread
def compute_alignment_and_warp_hybrid_taichi(
    comp_img,
    tile_h,
    tile_w,
    n_layers,
    align_lib,
    return_format: str = "numpy_u16",
    **kwargs,
):
    return _get_processor().compute_alignment_and_warp(
        comp_img, tile_h, tile_w, n_layers, return_format=return_format, **kwargs
    )


@ti_thread
def clear_taichi_cache():
    if _PROCESSOR:
        _PROCESSOR.clear_data()
