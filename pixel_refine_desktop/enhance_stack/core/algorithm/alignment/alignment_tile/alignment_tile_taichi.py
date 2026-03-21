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
import threading
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
TAICHI_AVAILABLE = TAICHI_JIT_AVAILABLE or (os.environ.get("PIXEL_REFINE_BACKEND") == "PRODUCTION")


# ============================================================================
# 1. PRODUCTION BACKEND (AOT via C++)
# ============================================================================
class AlignmentTileTaichiAOT:
    """GPU-accelerated modular alignment pipeline using Taichi AOT & C++ Driver."""

    def __init__(self, data_dir, arch="vulkan"):
        self.lib = None
        self.arch = arch
        self.data_dir = data_dir
        self.initialized = False
        self._setup_runtime_env()
        self._load_library()

    def _setup_runtime_env(self):
        """Ensure Taichi C-API can find its runtime libraries and dependencies."""
        try:
            import taichi as ti
            ti_path = ti.__path__[0]
            
            # 1. Set Ti Runtime Dir (For kernels)
            runtime_dir = os.path.join(ti_path, "_lib", "runtime")
            if os.path.exists(runtime_dir):
                os.environ["TI_LIB_DIR"] = runtime_dir
                print(f"[Taichi AOT] TI_LIB_DIR: {runtime_dir}")
            
            # 2. Add Bin to DLL Search Path (For Windows/Python 3.8+)
            # This is critical for loading dependencies like taichi_c_api.dll
            bin_dir = os.path.join(ti_path, "_lib", "c_api", "bin")
            if os.path.exists(bin_dir) and hasattr(os, "add_dll_directory"):
                os.add_dll_directory(bin_dir)
                print(f"[Taichi AOT] Added DLL directory: {bin_dir}")
                
                # Pre-load taichi_c_api.dll to avoid "Access Violation" on lazy load
                c_api_dll = os.path.join(bin_dir, "taichi_c_api.dll")
                if os.path.exists(c_api_dll):
                    ctypes.CDLL(c_api_dll)
                    
        except Exception as e:
            print(f"[Taichi AOT] Warning during setup: {e}")

    def _load_library(self):
        dll_path = os.path.join(self.data_dir, "alignment_tile_taichi_api.dll")
        if not os.path.exists(dll_path):
            print(f"[Taichi AOT] Warning: DLL not found at {dll_path}")
            return

        try:
            self.lib = ctypes.CDLL(dll_path)

            # Signatures
            self.lib.init_alignment_modular_tirt.argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
            ]
            self.lib.init_alignment_modular_tirt.restype = ctypes.c_int

            self.lib.set_reference_modular_tirt.argtypes = [
                ctypes.POINTER(ctypes.c_int32),
                ctypes.c_int,
                ctypes.c_int,
            ]
            self.lib.set_reference_modular_tirt.restype = ctypes.c_int
            if hasattr(self.lib, "set_reference_modular_tirt_ex"):
                self.lib.set_reference_modular_tirt_ex.argtypes = [
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                ]
                self.lib.set_reference_modular_tirt_ex.restype = ctypes.c_int

            self.lib.set_preprocess_config_modular_tirt.argtypes = [
                ctypes.c_float,
                ctypes.c_int,
            ]
            self.lib.set_preprocess_config_modular_tirt.restype = ctypes.c_int

            if hasattr(self.lib, "set_alignment_config_modular_tirt"):
                self.lib.set_alignment_config_modular_tirt.argtypes = [
                    ctypes.c_int,
                    ctypes.c_int,
                ]
                self.lib.set_alignment_config_modular_tirt.restype = ctypes.c_int

            self.lib.compute_alignment_modular_tirt.argtypes = [
                ctypes.POINTER(ctypes.c_int32),
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_float,
            ]
            self.lib.compute_alignment_modular_tirt.restype = ctypes.POINTER(
                ctypes.c_int32
            )
            if hasattr(self.lib, "compute_alignment_modular_tirt_ex"):
                self.lib.compute_alignment_modular_tirt_ex.argtypes = [
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_float,
                    ctypes.c_int,
                ]
                self.lib.compute_alignment_modular_tirt_ex.restype = ctypes.POINTER(
                    ctypes.c_int32
                )
            if hasattr(self.lib, "compute_alignment_modular_tirt_into_ex"):
                self.lib.compute_alignment_modular_tirt_into_ex.argtypes = [
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_float,
                    ctypes.c_int,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.lib.compute_alignment_modular_tirt_into_ex.restype = ctypes.c_int

            self.lib.clear_reference_modular_tirt.argtypes = []
            self.lib.clear_reference_modular_tirt.restype = None

            self.lib.free_u16_memory.argtypes = [ctypes.POINTER(ctypes.c_int32)]
            self.lib.free_u16_memory.restype = None

            # Initialize
            res = self.lib.init_alignment_modular_tirt(
                self.arch.encode("utf-8"), self.data_dir.encode("utf-8")
            )
            if res != 0:
                print(f"[Taichi AOT] Failed to initialize C++ backend: {res}")
            else:
                self.initialized = True
        except Exception as e:
            print(f"[Taichi AOT] Error loading DLL: {e}")

    def _configure_preprocess(self, is_linear=False, proxy_scale=1.0, use_sharpen=False):
        if not self.initialized or self.lib is None:
            return
        # Mirror preprocess_pipeline_gpu knobs:
        # scale_gamma = proxy_scale only when linear mode is enabled.
        scale_gamma = float(proxy_scale) if is_linear else 1.0
        sharpen_i = 1 if use_sharpen else 0
        self.lib.set_preprocess_config_modular_tirt(ctypes.c_float(scale_gamma), ctypes.c_int(sharpen_i))

    def _configure_alignment(self, downscale_factor=4, min_tile_size=8):
        if not self.initialized or self.lib is None:
            return
        if not hasattr(self.lib, "set_alignment_config_modular_tirt"):
            return
        self.lib.set_alignment_config_modular_tirt(
            ctypes.c_int(int(downscale_factor)),
            ctypes.c_int(int(min_tile_size)),
        )

    def set_reference(self, ref_img, is_linear=False, proxy_scale=1.0, use_sharpen=False, **kwargs):
        if not self.initialized or self.lib is None:
            return
        downscale_factor = kwargs.get("downscale_factor", 4)
        min_tile_size = kwargs.get("min_tile_size", kwargs.get("min_tile", 8))
        self._configure_alignment(downscale_factor=downscale_factor, min_tile_size=min_tile_size)
        self._configure_preprocess(is_linear=is_linear, proxy_scale=proxy_scale, use_sharpen=use_sharpen)
        h, w = ref_img.shape[:2]
        channels = 1 if ref_img.ndim == 2 else int(ref_img.shape[2])
        if channels not in (1, 3):
            channels = 1
        ref_i32 = ref_img.astype(np.int32).flatten()
        ref_ptr = ref_i32.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        if hasattr(self.lib, "set_reference_modular_tirt_ex"):
            self.lib.set_reference_modular_tirt_ex(ref_ptr, h, w, channels)
        else:
            self.lib.set_reference_modular_tirt(ref_ptr, h, w)

    def compute_alignment_and_warp(
        self,
        comp_img,
        tile_h=16,
        tile_w=16,
        n_layers=4,
        search_dist=2.0,
        is_linear=False,
        proxy_scale=1.0,
        use_sharpen=False,
        return_format: str = "numpy_u16",
        **kwargs
    ):
        if self.lib is None:
            return None
        downscale_factor = kwargs.get("downscale_factor", 4)
        min_tile_size = kwargs.get("min_tile_size", kwargs.get("min_tile", 8))
        self._configure_alignment(downscale_factor=downscale_factor, min_tile_size=min_tile_size)
        self._configure_preprocess(is_linear=is_linear, proxy_scale=proxy_scale, use_sharpen=use_sharpen)
        h, w = comp_img.shape[:2]
        channels = 1 if comp_img.ndim == 2 else int(comp_img.shape[2])
        if channels not in (1, 3):
            channels = 1
        comp_i32 = comp_img.astype(np.int32).flatten()
        comp_ptr = comp_i32.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

        out_count = h * w if channels == 1 else h * w * channels
        if hasattr(self.lib, "compute_alignment_modular_tirt_ex"):
            res_ptr = self.lib.compute_alignment_modular_tirt_ex(
                comp_ptr, tile_h, tile_w, n_layers, search_dist, channels
            )
        else:
            res_ptr = self.lib.compute_alignment_modular_tirt(
                comp_ptr, tile_h, tile_w, n_layers, search_dist
            )
        if not res_ptr:
            return None
        result_flat = np.fromiter(res_ptr, dtype=np.int32, count=out_count)
        self.lib.free_u16_memory(res_ptr)
        if channels == 1:
            warped_u16 = result_flat.reshape((h, w)).astype(np.uint16)
        else:
            warped_u16 = result_flat.reshape((h, w, channels)).astype(np.uint16)

        # AOT path always produces u16; convert to requested format if needed
        if return_format == "numpy_f32":
            return warped_u16.astype(np.float32) / 65535.0
        # "ti_ndarray" not applicable for AOT/C++ path — fall back to u16
        return warped_u16

    def clear_data(self):
        if self.lib:
            self.lib.clear_reference_modular_tirt()


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
        is_taichi_ndarray = hasattr(warped_img_gpu, 'to_numpy')

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
        
        # Detect best architecture (CUDA if NVIDIA, else Vulkan/CPU)
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
            data_dir = "pixel_refine_desktop/ui/data"
            if not os.path.exists(data_dir):
                data_dir = "ui/data"
            
            _PROCESSOR = AlignmentTileTaichiAOT(data_dir, arch=best_arch)
            if not _PROCESSOR.initialized:
                print(f"!!! [CRITICAL] AOT Backend failed to initialize on {best_arch.upper()} !!!")
            else:
                print(f"[Taichi] Mode: PRODUCTION (AOT) on {best_arch.upper()}")
        else:
            _PROCESSOR = AlignmentTileTaichiJIT()
            print(f"[Taichi] Mode: DEVELOPMENT (JIT) on {best_arch.upper()}")
    return _PROCESSOR


@ti_thread
def set_reference_hybrid_taichi(ref_img, work_h, work_w, **kwargs):
    _get_processor().set_reference(ref_img, work_h=work_h, work_w=work_w, **kwargs)


@ti_thread
def compute_alignment_and_warp_hybrid_taichi(
    comp_img, tile_h, tile_w, n_layers, align_lib,
    return_format: str = "numpy_u16",
    **kwargs
):
    return _get_processor().compute_alignment_and_warp(
        comp_img, tile_h, tile_w, n_layers,
        return_format=return_format,
        **kwargs
    )


@ti_thread
def clear_taichi_cache():
    if _PROCESSOR:
        _PROCESSOR.clear_data()
