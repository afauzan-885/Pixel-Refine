import os
# Suppress Vulkan loader registry warnings on Windows
os.environ["VK_LOADER_DEBUG"] = "error"
import sys
import numpy as np

# Path resolution to find the bridge
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Legacy JIT imports removed as we now use AOT (TCM) exclusively


# Import the Generic AOT Engine and Buffer Pool
from .engine import AOTEngine, TaichiGPUBuffer, InputArray, OutputArray
from .engine import enable_experiment_mode, is_experiment_mode
from .engine import INTER_CUBIC, INTER_LINEAR, INTER_NEAREST, INTER_AREA
from .engine import COLOR_BGR2GRAY, COLOR_RGB2GRAY, COLOR_GRAY2BGR
from taichi_library.taichi_algorithm.taichi_worker import ti_thread

# Bridge to specialized AOT functions
# Moved to lazy imports in wrapper functions below to avoid circular imports

# Initialize the Singleton Engine
engine = AOTEngine()

# --- Lazy-Load TCM Module Cache ---
# Modules are NOT loaded at startup. Loaded on first use, cached permanently.
# Saves ~200MB of idle VRAM compared to eager loading all 15 modules.
_tcm_dir = os.path.abspath(os.path.join(file_dir, "../taichi_algorithm/aot_tcm"))
_module_cache = {}  # name -> AOTModuleWrapper (loaded on demand)


def _mod(name: str):
    """Lazy-load and cache a TCM module by name. Thread-safe via GIL."""
    cached = _module_cache.get(name)
    if cached is not None and (
        getattr(cached, "module_ptr", None)
        and getattr(cached, "engine_generation", None)
        == getattr(engine, "_generation", 0)
    ):
        return cached
    if name in _module_cache:
        _module_cache.pop(name, None)

    if name not in _module_cache:
        path_dir = os.path.join(_tcm_dir, name)
        if os.path.isdir(path_dir):
            _module_cache[name] = engine.load(path_dir)
        else:
            path_file = os.path.join(_tcm_dir, f"{name}.tcm")
            _module_cache[name] = engine.load(path_file)
    return _module_cache[name]


def load_tcm(name):
    """Public helper for external callers (backward compat). Uses lazy cache."""
    return _mod(name)


def unload_all_modules():
    """Release all cached TCM modules. Call after heavy processing to free VRAM."""
    _module_cache.clear()
    engine.modules.clear()
    engine.clear_pipelines()

# --- OpenCV-style Constants ---
INTER_NEAREST = 0
INTER_LINEAR = 1
INTER_CUBIC = 2
INTER_AREA = 3
INTER_LANCZOS4 = 4

# --- Core API ---


def upload(arr: np.ndarray, is_vector=False, force_8bit=False) -> TaichiGPUBuffer:
    """Upload a NumPy array to GPU VRAM, optionally forcing 16-bit to 8-bit to optimize memory."""
    if force_8bit and isinstance(arr, np.ndarray) and arr.dtype == np.uint16:
        arr = (arr >> 8).astype(np.uint8)
    return engine.upload(arr, is_vector=is_vector)


# -------------------------------------------------------------------------
# Helper Functions (AOT-Optimized Utility)
# -------------------------------------------------------------------------


def copy_field(src, dst):
    """Zero-overhead AOT copy."""
    is_3ch = len(src.shape) == 3
    graph = "copy_i32_2d"
    if is_3ch:
        graph = "copy_vec3_2d" if src.dtype == np.float32 else "copy_vec3_i32_2d"
    elif src.dtype == np.float32:
        graph = "copy_f32_2d"

    src_v, dst_v = src, dst
    if is_3ch:
        if not getattr(src, "is_vector", False):
            src_v = src.view_as_vector(True)
        if not getattr(dst, "is_vector", False):
            dst_v = dst.view_as_vector(True)

    _mod("common").run(graph, src=src_v, dst=dst_v)


def extract_channel(src, ch):
    """AOT Optimized channel extraction."""
    h, w = src.shape[0], src.shape[1]
    dst = engine.allocate((h, w), dtype=src.dtype)
    src_v = src
    if len(src.shape) == 3 and not getattr(src, "is_vector", False):
        src_v = src.view_as_vector(True)

    graph = "extract_channel_f32" if src.dtype == np.float32 else "extract_channel_i32"
    _mod("common").run(graph, src=src_v, dst=dst, ch=int(ch))
    return dst


def split_3ch(src):
    """Fused 3-channel split."""
    h, w = src.shape[0], src.shape[1]
    dst_dtype = src.dtype
    c0 = engine.allocate((h, w), dtype=dst_dtype)
    c1 = engine.allocate((h, w), dtype=dst_dtype)
    c2 = engine.allocate((h, w), dtype=dst_dtype)
    src_v = src
    if not getattr(src, "is_vector", False):
        src_v = src.view_as_vector(True)

    graph = "split_3ch_f32" if dst_dtype == np.float32 else "split_3ch_i32"
    _mod("common").run(graph, src=src_v, c0=c0, c1=c1, c2=c2)
    return [c0, c1, c2]


def merge_3ch(c0, c1, c2):
    """Fused 3-channel merge."""
    h, w = c0.shape[0], c0.shape[1]
    dst_dtype = c0.dtype
    dst = engine.allocate((h, w), dtype=dst_dtype, is_vector=True, vector_dim=3)

    graph = "merge_3ch_f32" if dst_dtype == np.float32 else "merge_3ch_i32"
    _mod("common").run(graph, c0=c0, c1=c1, c2=c2, dst=dst.view_as_vector(True, 3))
    return dst


def insert_channel(src, dst, ch):
    """AOT Optimized channel insertion (in-place on GPU)."""
    src_v = src
    dst_v = dst
    if len(dst.shape) == 3 and not getattr(dst, "is_vector", False):
        dst_v = dst.view_as_vector(True)

    graph = "insert_channel_f32" if src.dtype == np.float32 else "insert_channel_i32"
    _mod("common").run(graph, src=src_v, dst=dst_v, ch=int(ch))


def generate_hanning_window_2d(shape, exclude_boundary=False, dtype=np.float32) -> TaichiGPUBuffer:
    """AOT Optimized 2D Hanning window generation."""
    h, w = shape
    dst = engine.allocate((h, w), dtype=dtype)
    _mod("common").run("generate_hanning_window_2d", dst=dst, H=int(h), W=int(w), exclude_boundary=int(exclude_boundary))
    return dst


def mean_division(sum_img: TaichiGPUBuffer, sum_weight: TaichiGPUBuffer, ref_img: TaichiGPUBuffer, dst: TaichiGPUBuffer = None) -> TaichiGPUBuffer:
    """AOT Optimized final mean division and fallback."""
    if dst is None:
        dst = engine.allocate(sum_img.shape, dtype=sum_img.dtype, is_vector=getattr(sum_img, "is_vector", False), vector_dim=getattr(sum_img, "vector_dim", 1))

    is_vec = len(sum_img.shape) == 3 or getattr(sum_img, "is_vector", False)
    graph = "mean_division_vec3_f32" if is_vec else "mean_division_f32"

    sum_img_v = sum_img
    ref_img_v = ref_img
    dst_v = dst

    if is_vec:
        if not getattr(sum_img, "is_vector", False):
            sum_img_v = sum_img.view_as_vector(True)
        if not getattr(ref_img, "is_vector", False):
            ref_img_v = ref_img.view_as_vector(True)
        if not getattr(dst, "is_vector", False):
            dst_v = dst.view_as_vector(True)

    _mod("common").run(graph, sum_img=sum_img_v, sum_weight=sum_weight, ref_img=ref_img_v, dst=dst_v)
    return dst


# NumPy-like aliases for JIT/AOT consistency
hanning = generate_hanning_window_2d
divide = mean_division



def rgb2gray(src, dst=None):
    """AOT Optimized RGB to Gray conversion."""
    h, w = src.shape[0], src.shape[1]
    if dst is None:
        dst = engine.allocate((h, w), dtype=src.dtype)
    src_v = src
    if len(src.shape) == 3 and not getattr(src, "is_vector", False):
        src_v = src.view_as_vector(True)

    graph = "rgb2gray_f32" if src.dtype == np.float32 else "rgb2gray_i32"
    _mod("common").run(graph, src=src_v, dst=dst)
    return dst


def absdiff(src1, src2):
    """AOT Optimized absolute difference."""
    is_3d = len(src1.shape) == 3
    dst = engine.allocate(src1.shape, dtype=src1.dtype, is_vector=is_3d)

    src1_v, src2_v, dst_v = src1, src2, dst
    if is_3d:
        if not getattr(src1, "is_vector", False):
            src1_v = src1.view_as_vector(True, 3)
        if not getattr(src2, "is_vector", False):
            src2_v = src2.view_as_vector(True, 3)
        if not getattr(dst, "is_vector", False):
            dst_v = dst.view_as_vector(True, 3)
        graph = "absdiff_vec3_f32"
    else:
        graph = "absdiff_f32_2d" if src1.dtype == np.float32 else "absdiff_i32_2d"

    _mod("common").run(graph, src1=src1_v, src2=src2_v, dst=dst_v)
    return dst


def cvtColor(src, code):
    """AOT Optimized color conversion (OpenCV Parity)."""
    # OpenCV Constants
    COLOR_BGR2GRAY = 6
    COLOR_RGB2GRAY = 7

    src_buf = InputArray(src)

    if code in [COLOR_BGR2GRAY, COLOR_RGB2GRAY]:
        h, w = src_buf.shape[0], src_buf.shape[1]
        dst = OutputArray((h, w), dtype=src_buf.dtype)
        src_v = src_buf
        if len(src_buf.shape) == 3 and not getattr(src_buf, "is_vector", False):
            src_v = src_buf.view_as_vector(True, 3)

        graph = "rgb2gray_f32" if code == COLOR_RGB2GRAY else "bgr2gray_f32"
        _mod("common").run(graph, src=src_v, dst=dst)
        return dst

    return src


# -------------------------------------------------------------------------
# Algorithm APIs
# -------------------------------------------------------------------------


def normalize_image(
    src: InputArray, dtype: np.dtype, out: OutputArray = None
) -> TaichiGPUBuffer:
    """High-level normalization [0, 1] using AOT."""
    from . import engine  # Use relative or local engine
    from ..alignment.alignment_features.taichi_bridge import normalize_image_gpu

    src_gpu = upload(src) if not isinstance(src, TaichiGPUBuffer) else src
    return normalize_image_gpu(src_gpu, dtype, out_gpu=out)


def to_gamma_proxy(
    src: InputArray, scale: float = 1.0, out: OutputArray = None
) -> TaichiGPUBuffer:
    """High-level Gamma Proxy transformation using AOT."""
    from ..alignment.alignment_features.taichi_bridge import to_gamma_proxy_gpu

    src_gpu = upload(src) if not isinstance(src, TaichiGPUBuffer) else src
    return to_gamma_proxy_gpu(src_gpu, scale=scale, dst_gpu=out)


def resize(src, dsize, interpolation=INTER_CUBIC, return_gpu=False, dst=None):
    """Taichi AOT Resize (OpenCV Parity API)"""
    target_w, target_h = dsize
    src_buf = InputArray(src)

    if isinstance(src, TaichiGPUBuffer) and len(src_buf.shape) == 3:
        # Force vector for any 3D arrays (RGB or Flow)
        src_buf = src_buf.view_as_vector(True)

    h_src, w_src = src_buf.shape[0], src_buf.shape[1]
    is_vec = getattr(src_buf, "is_vector", False)
    is_3d = (len(src_buf.shape) == 3) or is_vec

    # If it's a vector field but shape is 2D (like placeholders), we need to ensure dst_shape has the vector dim
    v_dim = (
        src_buf.vector_dim
        if is_vec
        else (src_buf.shape[2] if len(src_buf.shape) == 3 else 1)
    )

    if dst is None:
        if is_3d:
            dst_shape = (target_h, target_w, v_dim)
        else:
            dst_shape = (target_h, target_w)

        dst_buf = OutputArray(
            dst_shape, dtype=src_buf.dtype, is_vector=is_vec, vector_dim=v_dim
        )
    else:
        dst_buf = dst

    is_vec = getattr(src_buf, "is_vector", False)

    if interpolation == INTER_CUBIC:
        graph_name = "bicubic_resize_f32_3d" if is_vec else "bicubic_resize_f32_2d"
        if src_buf.dtype != np.float32:
            graph_name = graph_name.replace("f32", "i32")
        _mod("bicubic").run(
            graph_name,
            src=src_buf,
            dst=dst_buf,
            h_src=h_src,
            w_src=w_src,
            h_dst=target_h,
            w_dst=target_w,
        )
    elif interpolation == INTER_LINEAR:
        graph_name = "bilinear_resize_f32_3d" if is_vec else "bilinear_resize_f32_2d"
        _mod("bilinear").run(
            graph_name,
            src=src_buf,
            dst=dst_buf,
            h_src=h_src,
            w_src=w_src,
            h_dst=target_h,
            w_dst=target_w,
        )
    elif interpolation == INTER_AREA:
        graph_name = "inter_area_vec3_f32" if is_vec else "inter_area_f32"
        _mod("area").run(
            graph_name,
            src=src_buf,
            dst=dst_buf,
            sh=h_src,
            sw=w_src,
            dh=target_h,
            dw=target_w,
        )
    else:
        raise NotImplementedError(
            f"Interpolation mode {interpolation} is not supported in AOT currently."
        )

    return dst_buf if return_gpu else dst_buf.to_numpy()


def box_filter(src, kernel_size=3, return_gpu=False, dst=None):
    """AOT Implementation of Box Filter."""
    src_buf = InputArray(src)
    h, w = src_buf.shape[:2]
    radius = kernel_size // 2
    is_3d = len(src_buf.shape) == 3

    if dst is None:
        dst_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_3d)
    else:
        dst_buf = dst

    is_vec = getattr(src_buf, "is_vector", False)

    if kernel_size == 3:
        target = "box_filter_fused_3x3_1ch_f32"
        if is_3d:
            target = (
                "box_filter_fused_3x3_vec3_f32"
                if is_vec
                else "box_filter_fused_3x3_3ch_f32"
            )
        _mod("box_filter").run(target, src=src_buf, dst=dst_buf, h=h, w=w)
    else:
        tmp_buf = engine.allocate(src_buf.shape, dtype=src_buf.dtype, is_vector=is_vec)
        target = "box_filter_separable_generic_1ch_f32"
        if is_3d:
            target = (
                "box_filter_separable_generic_vec3_f32"
                if is_vec
                else "box_filter_separable_generic_3ch_f32"
            )
        _mod("box_filter").run(
            target, src=src_buf, tmp=tmp_buf, dst=dst_buf, h=h, w=w, radius=radius
        )
        del tmp_buf

    return dst_buf if return_gpu else dst_buf.to_numpy()



def gaussian_blur(src, sigma=1.0, kernel_size=None, return_gpu=False, dst=None):
    """AOT Implementation of Gaussian Blur.

    Supports:
      - 2D single-channel (H, W)              -> uses gaussian_blur_x/y_1ch_f32
      - 3D scalar (H, W, 3)                   -> uses gaussian_blur_x/y_3ch_f32
      - 3D vector field (H, W) is_vector=True -> uses gaussian_blur_x/y_vec3_f32

    Args:
        src:         Input buffer (TaichiGPUBuffer or np.ndarray).
        sigma:       Gaussian standard deviation.
        kernel_size: Kernel size (must be odd). Auto-computed from sigma if None.
        return_gpu:  If True, returns TaichiGPUBuffer; otherwise returns np.ndarray.
        dst:         Optional pre-allocated TaichiGPUBuffer to reuse (same shape as src).
                     When provided, output is written directly into this buffer
                     and the same buffer is returned, saving a VRAM allocation.
    """
    src_buf = InputArray(src)

    if kernel_size is None or kernel_size <= 0:
        kernel_size = int(np.ceil(3 * sigma)) * 2 + 1
    radius = kernel_size // 2
    h, w = src_buf.shape[:2]
    is_vec = getattr(src_buf, "is_vector", False)
    is_2d = (len(src_buf.shape) == 2) and not is_vec

    from taichi_library.taichi_algorithm.gaussian import (
        compute_gaussian_weights,
    )

    weights_np = compute_gaussian_weights(sigma, radius).astype(np.float32)
    weights_buf = InputArray(weights_np)

    # Intermediate buffer (always freshly allocated — must be separate from src)
    tmp_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_vec)

    # Output: reuse caller-supplied dst if shape and dtype match, otherwise allocate
    if dst is not None and dst.shape == src_buf.shape and dst.dtype == src_buf.dtype:
        dst_buf = dst
    else:
        dst_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_vec)

    if is_2d:
        # Single-channel 2D path
        target_x = "gaussian_blur_x_1ch_f32"
        target_y = "gaussian_blur_y_1ch_f32"
    elif is_vec:
        target_x = "gaussian_blur_x_vec3_f32"
        target_y = "gaussian_blur_y_vec3_f32"
    else:
        target_x = "gaussian_blur_x_3ch_f32"
        target_y = "gaussian_blur_y_3ch_f32"

    _mod("gaussian").run(
        target_x, src=src_buf, dst=tmp_buf, h=h, w=w, weights=weights_buf, radius=radius
    )
    _mod("gaussian").run(
        target_y, src=tmp_buf, dst=dst_buf, h=h, w=w, weights=weights_buf, radius=radius
    )

    engine.sync()
    tmp_buf.release()
    if hasattr(weights_buf, "release"):
        weights_buf.release()
    elif hasattr(weights_buf, "destroy"):
        weights_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()



def image_pyramid(src, levels=4, return_gpu=False):
    """AOT Implementation of Image Pyramid (Downsampling)"""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    is_3d = len(src_buf.shape) == 3

    curr_buf = src_buf
    graph = "downsample_2x_3ch_f32" if is_3d else "downsample_2x_f32"

    for _ in range(levels):
        h, w = curr_buf.shape[0], curr_buf.shape[1]
        next_h, next_w = h // 2, w // 2
        if next_h < 1 or next_w < 1:
            break

        dst_shape = (next_h, next_w, src_buf.shape[2]) if is_3d else (next_h, next_w)
        dst_buf = engine.allocate(dst_shape, dtype=src_buf.dtype)
        _mod("pyramid").run(graph, src=curr_buf, dst=dst_buf)

        if curr_buf is not src_buf:
            del curr_buf

        curr_buf = dst_buf

    return curr_buf if return_gpu else curr_buf.to_numpy()



def median_filter(src, return_gpu=False, **kwargs):
    """AOT Median Filter 3x3."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]

    is_flow = len(src_buf.shape) == 3 and src_buf.shape[2] == 2
    is_3ch = len(src_buf.shape) == 3 and src_buf.shape[2] == 3

    # Use vector for flow, but scalar 3D for RGB to avoid field_dim warnings in Taichi AOT
    src_v = src_buf.view_as_vector(True) if is_flow else src_buf.view_as_vector(False)

    dst_buf = engine.allocate(src_buf.shape, dtype=src_buf.dtype, is_vector=is_flow)
    dst_v = dst_buf.view_as_vector(True) if is_flow else dst_buf.view_as_vector(False)

    if is_flow:
        graph = "median_flow_3x3_f32"
    elif is_3ch:
        graph = "median_3ch_3x3_f32"
    else:
        graph = "median_3x3_f32" if src_buf.dtype == np.float32 else "median_3x3"

    _mod("median_filter").run(graph, src=src_v, dst=dst_v, h=h, w=w)
    return dst_buf if return_gpu else dst_buf.to_numpy()


def fft2(src, use_hanning=False):
    """AOT Implementation of 2D FFT."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h_src, w_src = src_buf.shape[:2]

    # FFT requires power-of-two dimensions
    h = 1 << (h_src - 1).bit_length()
    w = 1 << (w_src - 1).bit_length()

    complex_buf = engine.allocate((h, w, 2), is_vector=True)
    _mod("fft").run(
        "fft_real_to_complex_f32", src=src_buf, dst=complex_buf, h=h_src, w=w_src
    )

    if use_hanning:
        # Hanning window works on real part (complex_buf.x)
        # We need a temp real buffer to apply it before R2C or after R2C
        # Actually our fft_hanning_window_f32 takes a real ndarray.
        # Let's apply it to src_buf if it's already on GPU, or a copy.
        src_padded = engine.allocate((h, w), dtype=np.float32)
        # Copy src to padded and apply window
        # For simplicity, we can use a kernel that does both,
        # but let's just use existing graphs.
        _mod("common").run(
            "copy_f32_2d", src=src_buf, dst=src_padded
        )  # This might fail if shapes differ
        # Wait, copy_f32_2d needs same shape.
        # Better: use fft_real_to_complex first, then apply window to the complex x-channel.
        # But our hanning graph takes f32 ndarray.
        # Let's just create a quick hanning window on the src_buf if we can.

    # Actually, let's just apply Hanning to the complex_buf.x after R2C
    if use_hanning:
        _mod("fft").run("fft_complex_hanning_f32", data=complex_buf, h=h_src, w=w_src)

    def run_fft_1d(buf, h, w, is_inverse, is_col):
        n = h if is_col else w
        bits = (n - 1).bit_length()
        temp_buf = engine.allocate((h, w, 2), is_vector=True)
        _mod("fft").run(
            "fft_bit_reverse_f32",
            src=buf,
            dst=temp_buf,
            bits=bits,
            is_col=1 if is_col else 0,
        )
        buf.handle, temp_buf.handle = temp_buf.handle, buf.handle
        for stage in range(1, bits + 1):
            _mod("fft").run(
                "fft_stage_f32",
                data=buf,
                n=n,
                stage_len=1 << stage,
                is_inverse=1 if is_inverse else 0,
                is_col=1 if is_col else 0,
            )
        if is_inverse:
            _mod("fft").run("fft_normalize_f32", data=buf, scale=1.0 / n)
        del temp_buf

    run_fft_1d(complex_buf, h, w, False, False)
    run_fft_1d(complex_buf, h, w, False, True)
    return complex_buf


def ifft2(complex_buf, target_shape=None):
    """AOT Implementation of 2D IFFT."""
    h, w = complex_buf.shape[:2]

    def run_fft_1d(buf, h, w, is_inverse, is_col):
        n = h if is_col else w
        bits = (n - 1).bit_length()
        temp_buf = engine.allocate((h, w, 2), is_vector=True)
        _mod("fft").run(
            "fft_bit_reverse_f32",
            src=buf,
            dst=temp_buf,
            bits=bits,
            is_col=1 if is_col else 0,
        )
        buf.handle, temp_buf.handle = temp_buf.handle, buf.handle
        for stage in range(1, bits + 1):
            _mod("fft").run(
                "fft_stage_f32",
                data=buf,
                n=n,
                stage_len=1 << stage,
                is_inverse=1 if is_inverse else 0,
                is_col=1 if is_col else 0,
            )
        if is_inverse:
            _mod("fft").run("fft_normalize_f32", data=buf, scale=1.0 / n)
        del temp_buf

    run_fft_1d(complex_buf, h, w, True, True)
    run_fft_1d(complex_buf, h, w, True, False)

    out_h, out_w = target_shape if target_shape else (h, w)
    dst_buf = engine.allocate((out_h, out_w))
    _mod("fft").run(
        "fft_complex_to_real_f32", src=complex_buf, dst=dst_buf, h=out_h, w=out_w
    )
    return dst_buf


def sobel(src, return_gpu=False):
    """AOT Sobel."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    src_v = src_buf if not is_3d else src_buf.view_as_vector(True)

    dx = engine.allocate((h, w))
    dy = engine.allocate((h, w))

    # Use 3ch graph if 3d
    graph = "sobel_vec3_f32" if is_3d else "sobel_f32"

    _mod("gradients").run(graph, src=src_v, dst_dx=dx, dst_dy=dy, h=h, w=w)
    return (dx, dy) if return_gpu else (dx.to_numpy(), dy.to_numpy())


def laplacian(src, return_gpu=False):
    """AOT Laplacian."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    dst = engine.allocate((h, w))
    _mod("gradients").run("laplacian_f32", src=src_buf, dst=dst, h=h, w=w)
    return dst if return_gpu else dst.to_numpy()


def ransac_flow_cleanup(flow, threshold=1.0, return_gpu=False):
    """AOT RANSAC Flow Cleanup."""
    return ransac_flow_cleanup_aot(flow, threshold=threshold, return_gpu=return_gpu)


def ransac_flow_cleanup_aot(flow, threshold=1.0, return_gpu=False):
    """Internal AOT RANSAC implementation."""
    is_gpu = isinstance(flow, TaichiGPUBuffer)
    flow_buf = flow if is_gpu else engine.upload(flow, is_vector=True, vector_dim=2)
    if not flow_buf.is_vector or getattr(flow_buf, "vector_dim", None) != 2:
        flow_buf = flow_buf.view_as_vector(True, 2)
    h, w = flow_buf.shape[:2]

    dst = OutputArray(flow_buf.shape, is_vector=True, vector_dim=2)
    mask = engine.allocate((h, w), dtype=np.int32)
    model = engine.allocate((2,), dtype=np.float32)  # [mean_u, mean_v]

    _mod("ransac").run(
        "ransac_flow_cleanup_f32",
        flow=flow_buf,
        inlier_mask=mask,
        model=model,
        output=dst,
        h=h,
        w=w,
        threshold=float(threshold),
        stride_refine=4,  # Default sparse stride
        stride_final=1,
    )  # Full resolution

    del mask, model
    return dst if return_gpu else dst.to_numpy()


def ncc_alignment(image, template, stride=1, return_gpu=False):
    """
    Taichi AOT ZNCC Alignment.
    Returns: (dx, dy, confidence)
    """
    res_map = zncc(
        image, template, stride=stride, return_gpu=False
    )  # Always need peak-finding on CPU for now

    idx = np.unravel_index(np.argmax(res_map), res_map.shape)
    dy, dx = idx[0] * stride, idx[1] * stride
    conf = float(res_map[idx])

    return float(dx), float(dy), conf


def zncc(image, template, stride=1, return_gpu=False):
    """AOT Optimized Spatial ZNCC."""
    is_gpu_img = isinstance(image, TaichiGPUBuffer)
    is_gpu_temp = isinstance(template, TaichiGPUBuffer)
    img_buf = image if is_gpu_img else engine.upload(image)
    temp_buf = template if is_gpu_temp else engine.upload(template)

    h_img, w_img = img_buf.shape[:2]
    h_temp, w_temp = temp_buf.shape[:2]

    s_h = engine.allocate((h_img, w_img))
    sq_h = engine.allocate((h_img, w_img))
    s_2d = engine.allocate((h_img, w_img))
    sq_2d = engine.allocate((h_img, w_img))

    _mod("ncc").run(
        "integral_row_scan", src=img_buf, sum_h=s_h, sq_sum_h=sq_h, h=h_img, w=w_img
    )
    _mod("ncc").run(
        "integral_col_scan",
        sum_h=s_h,
        sq_sum_h=sq_h,
        sum_2d=s_2d,
        sq_sum_2d=sq_2d,
        h=h_img,
        w=w_img,
    )

    del s_h, sq_h

    temp_np = temp_buf.to_numpy() if is_gpu_temp else template
    sum_t = float(np.sum(temp_np))
    n = float(h_temp * w_temp)
    var_t_n = float(max(0.0, np.sum(temp_np**2) - (sum_t**2 / n)))

    res_h, res_w = (h_img - h_temp) // stride + 1, (w_img - w_temp) // stride + 1
    dst = engine.allocate((res_h, res_w))

    _mod("ncc").run(
        "zncc_spatial",
        src=img_buf,
        template=temp_buf,
        sum_2d=s_2d,
        sq_sum_2d=sq_2d,
        dst=dst,
        sum_t=sum_t,
        var_t_n=var_t_n,
        n_float=n,
        stride=stride,
    )

    res = dst if return_gpu else dst.to_numpy()
    del s_2d, sq_2d, dst
    return res


# -------------------------------------------------------------------------
# SIGMA PRESETS (shared with JBF python-side)
# -------------------------------------------------------------------------
_JBF_SIGMA_PRESETS = {
    "high": (0.8, 0.05),
    "medium": (1.5, 0.10),
    "low": (2.5, 0.20),
}


def _jbf_sigma(preset):
    ss, sr = _JBF_SIGMA_PRESETS.get(preset, _JBF_SIGMA_PRESETS["medium"])
    return 1.0 / (2.0 * ss * ss), 1.0 / (2.0 * sr * sr)


def _prepare_guide_aot(guide_raw):
    """Ensure guide is a 2D f32 GPU buffer, normalized [0,1]."""
    is_gpu = isinstance(guide_raw, TaichiGPUBuffer)
    if is_gpu:
        g = guide_raw
        if len(g.shape) == 3:
            # Auto-convert 3ch → gray using common AOT
            g = cvtColor(g, 6)  # BGR2GRAY
        return g, False
    else:
        import numpy as _np

        arr = _np.array(guide_raw, dtype=_np.float32)
        if arr.ndim == 3:
            arr = 0.299 * arr[:, :, 2] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 0]
        if arr.max() > 1.0:
            arr = arr / (255.0 if arr.max() <= 255.0 else 65535.0)
        return engine.upload(arr.astype(_np.float32)), True


def joint_bilateral_filter(src, guide, preset="medium", radius=2, return_gpu=False):
    """
    AOT Joint Bilateral Filter — General post-processor.

    Args:
        src    : (H,W), (H,W,3) vec, or (H,W,2) vec — grayscale/RGB/flow GPU buffer
        guide  : (H,W) or (H,W,3) — guidance image (auto-converted to gray)
        preset : "low" | "medium" | "high"
        radius : 1=3x3 | 2=5x5 (default) | 3=7x7

    Example:
        # Post-process median result with original image as guide
        clean = taichi_aot.joint_bilateral_filter(median_out, original_img, preset="medium")

        # Refine flow field
        smooth_flow = taichi_aot.joint_bilateral_filter(flow_gpu, ref_gray, preset="low")
    """
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    guide_buf, guide_is_temp = _prepare_guide_aot(guide)

    h, w = src_buf.shape[:2]
    inv_2ss2, inv_2sr2 = _jbf_sigma(preset)
    r = radius if radius in (1, 2, 3) else 2

    # Determine src type
    is_vec = getattr(src_buf, "is_vector", False)
    ndim = len(src_buf.shape)

    if ndim == 2 and not is_vec:
        # 1ch scalar
        dst = engine.allocate((h, w))
        _mod("jbf").run(
            f"jbf_1ch_r{r}",
            src=src_buf,
            guide=guide_buf,
            dst=dst,
            h=h,
            w=w,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )
    elif (
        ndim == 3
        and src_buf.shape[2] == 2
        or (is_vec and src_buf.shape[-1] == 2 if hasattr(src_buf, "shape") else False)
    ):
        # flow 2ch
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate(src_buf.shape, is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            f"jbf_flow_r{r}",
            src=src_v,
            guide=guide_buf,
            dst=dst_v,
            h=h,
            w=w,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )
    else:
        # 3ch
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate(src_buf.shape, is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            f"jbf_3ch_r{r}",
            src=src_v,
            guide=guide_buf,
            dst=dst_v,
            h=h,
            w=w,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )

    if guide_is_temp:
        del guide_buf
    return dst if return_gpu else dst.to_numpy()


def joint_bilateral_upsample(src_low, guide_hi, preset="medium", return_gpu=False):
    """
    AOT Joint Bilateral Upsampling (JBLU).
    Upscales src_low to resolution of guide_hi with edge-aware interpolation.

    Args:
        src_low  : (h,w), (h,w,3) vec, or (h,w,2) vec — LOW-RES source
        guide_hi : (H,W) or (H,W,3) — HIGH-RES guide (auto-converted to gray)
        preset   : "low" | "medium" | "high"

    Example:
        # Upsample pyramid flow with full-res image as guide
        flow_full = taichi_aot.joint_bilateral_upsample(flow_low, full_res_img)

        # Upsample low-res mask
        mask_full = taichi_aot.joint_bilateral_upsample(mask_low, full_res_gray)
    """
    is_gpu = isinstance(src_low, TaichiGPUBuffer)
    src_buf = src_low if is_gpu else engine.upload(src_low)
    guide_buf, guide_is_temp = _prepare_guide_aot(guide_hi)

    h_low, w_low = src_buf.shape[:2]
    H, W = guide_buf.shape[:2]
    scale_y = float(H) / float(h_low)
    scale_x = float(W) / float(w_low)
    inv_2ss2, inv_2sr2 = _jbf_sigma(preset)

    is_vec = getattr(src_buf, "is_vector", False)
    ndim = len(src_buf.shape)

    if ndim == 2 and not is_vec:
        # 1ch
        dst = engine.allocate((H, W))
        _mod("jbf").run(
            "jblu_1ch_r2",
            src_low=src_buf,
            guide_hi=guide_buf,
            dst=dst,
            h_low=h_low,
            w_low=w_low,
            H=H,
            W=W,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )
    elif (ndim == 3 and src_buf.shape[2] == 2) or (
        is_vec and ndim == 2 and len(src_buf.shape) == 2
    ):
        # flow 2ch — check by is_vector and shape
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate((H, W, 2), is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            "jblu_flow_r2",
            src_low=src_v,
            guide_hi=guide_buf,
            dst=dst_v,
            h_low=h_low,
            w_low=w_low,
            H=H,
            W=W,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
            scale_y=scale_y,
            scale_x=scale_x,
        )
    else:
        # 3ch
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate((H, W, 3), is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            "jblu_3ch_r2",
            src_low=src_v,
            guide_hi=guide_buf,
            dst=dst_v,
            h_low=h_low,
            w_low=w_low,
            H=H,
            W=W,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )

    if guide_is_temp:
        del guide_buf
    return dst if return_gpu else dst.to_numpy()


# --- Bilateral Grid ---

BILATERAL_GRID_PRESETS = {
    # Tier: (s_s, s_r, sigma_s, sigma_r)
    "light": (32, 32, 1.0, 1.0),
    "medium": (16, 16, 1.0, 1.0),
    "heavy": (8, 8, 2.0, 1.5),
}


def bilateral_grid_filter(src, preset="medium", return_gpu=False):
    """
    AOT Bilateral Grid Filter.
    Edge-preserving smoothing in O(1) time per pixel.
    """
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]

    # Handle multichannel by looping
    is_3ch = len(src_buf.shape) == 3 and src_buf.shape[2] == 3

    s_s, s_r, sigma_s, sigma_r = BILATERAL_GRID_PRESETS.get(
        preset, BILATERAL_GRID_PRESETS["medium"]
    )
    gn, gm, gl = (h + s_s - 1) // s_s + 2, (w + s_s - 1) // s_s + 2, 256 // s_r + 2

    # Allocate grids (pooled) - 3D spatial field of 2D vectors
    grid_a = engine.allocate((gn, gm, gl), is_vector=True, vector_dim=2)
    grid_b = engine.allocate((gn, gm, gl), is_vector=True, vector_dim=2)
    grid_a_v = grid_a.view_as_vector(True, 2)
    grid_b_v = grid_b.view_as_vector(True, 2)

    rs, rr = int(np.ceil(sigma_s * 3.0)), int(np.ceil(sigma_r * 3.0))

    if not is_3ch:
        dst = engine.allocate((h, w))
        # Clear, Splat, Blur X, Y, Z, Slice
        _mod("bilateral_grid").run("bg_clear", grid=grid_a_v, gn=gn, gm=gm, gl=gl)
        _mod("bilateral_grid").run(
            "bg_splat",
            src=src_buf,
            grid=grid_a_v,
            s_s=s_s,
            s_r=s_r,
            h=h,
            w=w,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_blur_x",
            grid=grid_a_v,
            dst_grid=grid_b_v,
            radius=rs,
            sigma=sigma_s,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_blur_y",
            grid=grid_b_v,
            dst_grid=grid_a_v,
            radius=rs,
            sigma=sigma_s,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_blur_z",
            grid=grid_a_v,
            dst_grid=grid_b_v,
            radius=rr,
            sigma=sigma_r,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_slice",
            src=src_buf,
            grid=grid_b_v,
            dst=dst,
            s_s=s_s,
            s_r=s_r,
            h=h,
            w=w,
            gn=gn,
            gm=gm,
            gl=gl,
        )
    else:
        # RGB loop
        dst = engine.allocate((h, w, 3), is_vector=True)
        dst_v = dst.view_as_vector(True)
        src_v = (
            src_buf
            if getattr(src_buf, "is_vector", False)
            else src_buf.view_as_vector(True)
        )

        temp_ch = engine.allocate((h, w))
        temp_out = engine.allocate((h, w))

        for c in range(3):
            # 1. Extract channel
            _mod("common").run("extract_channel_f32", src=src_v, dst=temp_ch, ch=c)

            # 2. Filter
            _mod("bilateral_grid").run("bg_clear", grid=grid_a_v, gn=gn, gm=gm, gl=gl)
            _mod("bilateral_grid").run(
                "bg_splat",
                src=temp_ch,
                grid=grid_a_v,
                s_s=s_s,
                s_r=s_r,
                h=h,
                w=w,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_blur_x",
                grid=grid_a_v,
                dst_grid=grid_b_v,
                radius=rs,
                sigma=sigma_s,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_blur_y",
                grid=grid_b_v,
                dst_grid=grid_a_v,
                radius=rs,
                sigma=sigma_s,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_blur_z",
                grid=grid_a_v,
                dst_grid=grid_b_v,
                radius=rr,
                sigma=sigma_r,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_slice",
                src=temp_ch,
                grid=grid_b_v,
                dst=temp_out,
                s_s=s_s,
                s_r=s_r,
                h=h,
                w=w,
                gn=gn,
                gm=gm,
                gl=gl,
            )

        engine.sync()
        temp_ch.release()
        temp_out.release()
        del temp_ch, temp_out

    engine.sync()
    grid_a.release()
    grid_b.release()
    del grid_a, grid_b
    return dst if return_gpu else dst.to_numpy()


def phase_correlation(ref, comp, use_hanning=True):
    """
    Taichi AOT Phase Correlation for global shift estimation.
    Returns: (dx, dy, response)
    """
    is_gpu = isinstance(ref, TaichiGPUBuffer)
    ref_buf = ref if is_gpu else engine.upload(ref)
    comp_buf = comp if is_gpu else engine.upload(comp)

    h, w = ref_buf.shape[:2]
    # 1. FFT
    f_complex = fft2(ref_buf, use_hanning=use_hanning)
    g_complex = fft2(comp_buf, use_hanning=use_hanning)

    th, tw = f_complex.shape[:2]
    r_complex = OutputArray((th, tw, 2), is_vector=True)

    # 2. Cross-power spectrum: G * conj(F)
    # Graph Arg: src (a), b, dst, conj_b
    _mod("fft").run(
        "fft_complex_mul_f32", src=g_complex, b=f_complex, dst=r_complex, conj_b=1
    )

    # 3. Phase Normalize: R = R / |R|
    _mod("fft").run("fft_phase_normalize_f32", data=r_complex)

    # 4. IFFT
    corr_buf = ifft2(r_complex, target_shape=(h, w))
    corr_np = corr_buf.to_numpy()

    # 5. Peak finding
    idx = np.unravel_index(np.argmax(corr_np), corr_np.shape)
    dy, dx = idx[0], idx[1]
    peak_val = corr_np[idx]

    # Shift wrapping
    if dy > h // 2:
        dy -= h
    if dx > w // 2:
        dx -= w

    del f_complex, g_complex, r_complex, corr_buf
    return float(dx), float(dy), float(peak_val)


def remap(src, map_x, map_y, return_gpu=False):
    """Taichi AOT Remap (OpenCV Parity API)"""
    orig_dtype = None
    if isinstance(src, np.ndarray) and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cast = src.astype(np.float32)
    elif hasattr(src, "dtype") and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cast = src.cast(np.float32)
    else:
        src_cast = src

    src_buf = InputArray(src_cast)
    mx_buf = InputArray(map_x)
    my_buf = InputArray(map_y)

    h_src, w_src = src_buf.shape[:2]
    h_dst, w_dst = mx_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    if is_3d:
        src_v = src_buf if getattr(src_buf, "is_vector", False) else src_buf.view_as_vector(True)
        v_dim = src_v.vector_dim
        dst_shape = (h_dst, w_dst, v_dim)
        is_vec = True
    else:
        src_v = src_buf
        v_dim = 1
        dst_shape = (h_dst, w_dst)
        is_vec = False

    dst_buf = OutputArray(dst_shape, dtype=src_buf.dtype, is_vector=is_vec, vector_dim=v_dim)

    graph_name = "remap_f32_3d" if is_vec else "remap_f32_2d"
    _mod("remap").run(
        graph_name,
        src=src_v,
        map_x=mx_buf,
        map_y=my_buf,
        dst=dst_buf,
        h_src=h_src,
        w_src=w_src,
        h_dst=h_dst,
        w_dst=w_dst,
    )

    if src_cast is not src and hasattr(src_cast, "release"):
        engine.sync()
        src_cast.release()
    elif src_cast is not src and hasattr(src_cast, "destroy"):
        engine.sync()
        src_cast.destroy()

    if not return_gpu:
        res = dst_buf.to_numpy()
    else:
        engine.sync()
        res = dst_buf

    if orig_dtype is not None:
        if return_gpu:
            res_cast = res.cast(orig_dtype)
            res.release()
            res = res_cast
        else:
            if np.issubdtype(orig_dtype, np.integer):
                res = np.clip(res, np.iinfo(orig_dtype).min, np.iinfo(orig_dtype).max)
            res = res.astype(orig_dtype)

    return res


def remap_with_flow(src, flow, full_h, full_w, return_gpu=False, dst=None):
    """
    Fused remap with flow: bilinear interpolate flow on-the-fly + warp src image.
    Eliminates need for map_x, map_y full-res buffers (~91.6 MB VRAM saved).
    """
    # Cast src to float32 on CPU if it is not float32 (matches legacy remap behavior)
    orig_dtype = None
    if isinstance(src, np.ndarray) and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cpu = src.astype(np.float32)
    elif hasattr(src, "dtype") and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cpu = src.cast(np.float32)
    else:
        src_cpu = src
        if hasattr(src, "dtype"):
            orig_dtype = src.dtype
        else:
            orig_dtype = np.float32

    is_gpu_src = isinstance(src_cpu, TaichiGPUBuffer)
    is_gpu_flow = isinstance(flow, TaichiGPUBuffer)
    src_buf = src_cpu if is_gpu_src else engine.upload(src_cpu)
    if is_gpu_flow:
        flow_buf = flow
    else:
        # Bypass engine.upload auto-detect bug for (H, W, 2) flow array by using direct allocation
        flow_buf = engine.allocate(flow.shape, dtype=np.float32, is_vector=False, host_accessible=True)
        from taichi_library.taichi_aot.engine import _LIB, _RUNTIME
        _LIB.write_to_gpu_buffer(_RUNTIME, flow_buf.handle, np.ascontiguousarray(flow, dtype=np.float32).ctypes.data, flow_buf.nbytes)

    h_src, w_src = src_buf.shape[:2]
    h_flow, w_flow = flow_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3
    c_count = src_buf.shape[2] if is_3d else 1

    src_cast = src_buf
    target_dtype = np.float32
    graph_name = "remap_with_flow_f32_3d" if is_3d else "remap_with_flow_f32_2d"

    # Output buffer determination (allocate intermediate float32 buffer)
    if dst is None:
        dst_shape = (full_h, full_w, c_count) if is_3d else (full_h, full_w)
        dst_buf = engine.allocate(dst_shape, dtype=np.float32, is_vector=is_3d)
    else:
        if dst.dtype == np.float32:
            dst_buf = dst
        else:
            dst_buf = engine.allocate(dst.shape, dtype=np.float32, is_vector=is_3d)

    # Input view for 3d vector graphs
    src_v = src_cast
    dst_v = dst_buf
    if is_3d:
        src_v = src_cast if getattr(src_cast, "is_vector", False) else src_cast.view_as_vector(True)
        dst_v = dst_buf if getattr(dst_buf, "is_vector", False) else dst_buf.view_as_vector(True)

    scale_x = float(full_w) / float(w_flow)
    scale_y = float(full_h) / float(h_flow)

    # Run AOT Graph (always float32 for interpolation precision)
    _mod("remap").run(
        graph_name,
        src=src_v,
        flow=flow_buf,
        dst=dst_v,
        h_src=int(h_src),
        w_src=int(w_src),
        h_dst=int(full_h),
        w_dst=int(full_w),
        h_flow=int(h_flow),
        w_flow=int(w_flow),
        scale_x=float(scale_x),
        scale_y=float(scale_y),
    )

    # Sync
    engine.sync()
    
    # Clean up intermediate casts and uploads
    if src_cast is not src_buf:
        src_cast.release()
    if not is_gpu_src:
        src_buf.release()
    if not is_gpu_flow:
        flow_buf.release()

    # Cast back to original dtype or download with CPU fallback
    if return_gpu:
        if dst is not None and dst is not dst_buf:
            from taichi_library.taichi_algorithm.common import copy_field
            copy_field(dst_buf, dst)
            dst_buf.release()
            return dst
        return dst_buf
    else:
        # Download f32 from GPU first, then cast on CPU to avoid Vulkan u16/i16 host-mapping restrictions or .cast failures
        res_f32 = dst_buf.to_numpy()
        dst_buf.release()
        
        if orig_dtype != np.float32:
            if np.issubdtype(orig_dtype, np.integer):
                res_np = np.clip(res_f32, np.iinfo(orig_dtype).min, np.iinfo(orig_dtype).max).astype(orig_dtype)
            else:
                res_np = res_f32.astype(orig_dtype)
        else:
            res_np = res_f32
            
        if dst is not None:
            dst[:] = res_np
            return dst
        return res_np



def smooth_flow_gpu(flow, sigma=1.0, kernel_size=5, dst=None):
    """Gaussian blur a 2-channel flow field (H, W, 2) entirely on GPU.

    Uses the fused smooth_flow_x / smooth_flow_y graphs compiled into remap.tcm.
    Both channels are processed simultaneously in a single kernel launch per pass,
    making this significantly faster than calling gaussian_blur twice on separate channels.

    Args:
        flow:        TaichiGPUBuffer (H, W, 2) — the raw flow field.
        sigma:       Gaussian standard deviation.
        kernel_size: Filter kernel size (must be odd). Auto-computed from sigma if <= 0.
        dst:         Optional pre-allocated TaichiGPUBuffer (H, W, 2) to reuse as output.
                     If None or incompatible, a new buffer is allocated.

    Returns:
        TaichiGPUBuffer (H, W, 2) — smoothed flow. Caller must destroy when done.
    """
    from taichi_library.taichi_algorithm.gaussian import (
        compute_gaussian_weights,
    )

    if kernel_size is None or kernel_size <= 0:
        kernel_size = int(np.ceil(3 * sigma)) * 2 + 1
    radius = kernel_size // 2

    weights_np = compute_gaussian_weights(sigma, radius).astype(np.float32)
    weights_buf = InputArray(weights_np)

    h, w = int(flow.shape[0]), int(flow.shape[1])

    # Intermediate buffer for x-pass output (always new — cannot alias src)
    tmp_buf = engine.allocate((h, w, 2), dtype=np.float32)

    # Output buffer: reuse if compatible
    if dst is not None and dst.shape == (h, w, 2) and dst.dtype == np.float32:
        out_buf = dst
    else:
        out_buf = engine.allocate((h, w, 2), dtype=np.float32)

    _mod("remap").run(
        "smooth_flow_x",
        src=flow, dst=tmp_buf,
        h=h, w=w, weights=weights_buf, radius=radius,
    )
    _mod("remap").run(
        "smooth_flow_y",
        src=tmp_buf, dst=out_buf,
        h=h, w=w, weights=weights_buf, radius=radius,
    )

    engine.sync()
    tmp_buf.release()
    if hasattr(weights_buf, "release"):
        weights_buf.release()
    elif hasattr(weights_buf, "destroy"):
        weights_buf.destroy()
    del weights_buf
    return out_buf


def build_flow_maps(flow_or_dx, flow_or_dy_or_h, full_h_or_w=None, full_w=None,
                    scale_x=None, scale_y=None, map_x_buf=None, map_y_buf=None):
    """Build remap coordinate maps from a flow field — fully on GPU.

    Two calling conventions:
      1. 2-channel flow tensor:
         build_flow_maps(flow_2ch, full_h, full_w, ...)
         where flow_2ch is TaichiGPUBuffer (H_flow, W_flow, 2).

      2. Separate dx/dy tensors (legacy):
         build_flow_maps(dx, dy, full_h, full_w, ...)
         where dx and dy are TaichiGPUBuffer (H_flow, W_flow).

    Args:
        flow_or_dx:         2-channel flow buffer OR dx buffer.
        flow_or_dy_or_h:    full_h (int) if 2ch convention, OR dy buffer if separate.
        full_h_or_w:        full_w (int) if 2ch convention, OR full_h (int) if separate.
        full_w:             full_w (int) only when using separate dx/dy convention.
        scale_x:            Horizontal scale factor. Auto-computed if None.
        scale_y:            Vertical scale factor. Auto-computed if None.
        map_x_buf:          Optional pre-allocated output buffer (full_h, full_w) to reuse.
        map_y_buf:          Optional pre-allocated output buffer (full_h, full_w) to reuse.

    Returns:
        (map_x_buf, map_y_buf): TaichiGPUBuffer (full_h, full_w) each.
    """
    # Detect calling convention
    if isinstance(flow_or_dy_or_h, int):
        # Convention 1: build_flow_maps(flow_2ch, full_h, full_w, ...)
        flow_buf  = InputArray(flow_or_dx)
        _full_h   = int(flow_or_dy_or_h)
        _full_w   = int(full_h_or_w)
        h_flow    = int(flow_buf.shape[0])
        w_flow    = int(flow_buf.shape[1])

        if scale_x is None:
            scale_x = float(_full_w) / float(w_flow)
        if scale_y is None:
            scale_y = float(_full_h) / float(h_flow)

        out_shape = (_full_h, _full_w)
        if map_x_buf is None or map_x_buf.shape != out_shape or map_x_buf.dtype != np.float32:
            map_x_buf = engine.allocate(out_shape, dtype=np.float32)
        if map_y_buf is None or map_y_buf.shape != out_shape or map_y_buf.dtype != np.float32:
            map_y_buf = engine.allocate(out_shape, dtype=np.float32)

        _mod("remap").run(
            "build_flow_maps_from_2ch",
            flow=flow_buf, map_x=map_x_buf, map_y=map_y_buf,
            h_flow=h_flow, w_flow=w_flow,
            h_dst=_full_h, w_dst=_full_w,
            scale_x=float(scale_x), scale_y=float(scale_y),
        )
    else:
        # Convention 2: build_flow_maps(dx, dy, full_h, full_w, ...)
        dx_buf  = InputArray(flow_or_dx)
        dy_buf  = InputArray(flow_or_dy_or_h)
        _full_h = int(full_h_or_w)
        _full_w = int(full_w)
        h_flow  = int(dx_buf.shape[0])
        w_flow  = int(dx_buf.shape[1])

        if scale_x is None:
            scale_x = float(_full_w) / float(w_flow)
        if scale_y is None:
            scale_y = float(_full_h) / float(h_flow)

        out_shape = (_full_h, _full_w)
        if map_x_buf is None or map_x_buf.shape != out_shape or map_x_buf.dtype != np.float32:
            map_x_buf = engine.allocate(out_shape, dtype=np.float32)
        if map_y_buf is None or map_y_buf.shape != out_shape or map_y_buf.dtype != np.float32:
            map_y_buf = engine.allocate(out_shape, dtype=np.float32)

        _mod("remap").run(
            "build_flow_maps",
            dx=dx_buf, dy=dy_buf, map_x=map_x_buf, map_y=map_y_buf,
            h_flow=h_flow, w_flow=w_flow,
            h_dst=_full_h, w_dst=_full_w,
            scale_x=float(scale_x), scale_y=float(scale_y),
        )

    return map_x_buf, map_y_buf


def enhance_grayscale(src, blur, lut, micro_contrast=2.93, clarity=0.0, return_gpu=False, dst=None):
    """Taichi AOT Grayscale Image Enhancement (1D LUT & Micro-Contrast) API"""
    src_buf = InputArray(src)
    blur_buf = InputArray(blur)
    lut_buf = InputArray(lut)

    h, w = src_buf.shape[:2]

    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)

    _mod("remap").run(
        "enhance_grayscale",
        src=src_buf,
        blur=blur_buf,
        lut=lut_buf,
        dst=dst_buf,
        micro_contrast=float(micro_contrast),
        clarity=float(clarity),
        h=h,
        w=w,
    )

    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def hamilton_demosaic(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Taichi AOT Hamilton-Adams Demosaicing & Color Space / Gamma transform API"""
    bayer_buf   = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    
    h, w = bayer_buf.shape[:2]
    
    # Pre-allocate temporary intermediate buffers in VRAM to keep it blazing fast!
    wb_bayer_buf = engine.allocate((h, w), dtype=np.float32)
    green_buf    = engine.allocate((h, w), dtype=np.float32)
    r_diff_buf   = engine.allocate((h, w), dtype=np.float32)
    b_diff_buf   = engine.allocate((h, w), dtype=np.float32)
    r_diff_f_buf = engine.allocate((h, w), dtype=np.float32)
    b_diff_f_buf = engine.allocate((h, w), dtype=np.float32)
    
    # Destination output RGB float32 buffer
    if dst is not None and dst.shape == (h, w, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w, 3), dtype=np.float32)
        
    _mod("hamilton").run(
        "hamilton_demosaic",
        bayer=bayer_buf,
        wb_bayer=wb_bayer_buf,
        green=green_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        r_diff=r_diff_buf,
        b_diff=b_diff_buf,
        r_diff_filtered=r_diff_f_buf,
        b_diff_filtered=b_diff_f_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    # Immediately release intermediate VRAM buffers back to pool
    engine.sync()
    wb_bayer_buf.release()
    green_buf.release()
    r_diff_buf.release()
    b_diff_buf.release()
    r_diff_f_buf.release()
    b_diff_f_buf.release()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()
    
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def hamilton_demosaic_1channel(
    bayer, wb_r, wb_g1, wb_b, wb_g2,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Fast Green-Only Demosaic to Grayscale 1-channel (Fused Single-Pass)."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    
    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)
        
    _mod("hamilton").run(
        "hamilton_demosaic_1channel",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
        
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def hamilton_demosaic_half_res(
    bayer, wb_r, wb_g1, wb_b, wb_g2,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Bypass Demosaicing: Extract Green Sub-Sampling to 1/2 size (half_res) grayscale (Fused Single-Pass)."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    
    if dst is not None and dst.shape == (h // 2, w // 2) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2), dtype=np.float32)
        
    _mod("hamilton").run(
        "hamilton_demosaic_half_res",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def hamilton_demosaic_rgb_half_res(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Bypass Demosaicing: Extract RGB Direct Sub-Sampling to 1/2 size (half_res) RGB (Fused Single-Pass)."""
    bayer_buf = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    h, w = bayer_buf.shape[:2]
    
    if dst is not None and dst.shape == (h // 2, w // 2, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2, 3), dtype=np.float32)
        
    _mod("hamilton").run(
        "hamilton_demosaic_rgb_half_res",
        bayer=bayer_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def hamilton_demosaic_3channel(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Full-Luma Demosaic directly to Grayscale 1-channel."""
    bayer_buf = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    h, w = bayer_buf.shape[:2]
    wb_bayer_buf = engine.allocate((h, w), dtype=np.float32)
    green_buf = engine.allocate((h, w), dtype=np.float32)
    
    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)
        
    _mod("hamilton").run(
        "hamilton_demosaic_3channel",
        bayer=bayer_buf,
        wb_bayer=wb_bayer_buf,
        green=green_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    wb_bayer_buf.release()
    green_buf.release()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()
        
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def arm_demosaic(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Taichi AOT ARM Demosaicing & sRGB / Gamma transform API"""
    bayer_buf   = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    
    h, w = bayer_buf.shape[:2]
    
    # Pre-allocate temporary intermediate buffers in VRAM
    wb_bayer_buf = engine.allocate((h, w), dtype=np.float32)
    green_buf    = engine.allocate((h, w), dtype=np.float32)
    r_diff_buf   = engine.allocate((h, w), dtype=np.float32)
    b_diff_buf   = engine.allocate((h, w), dtype=np.float32)
    r_diff_f_buf = engine.allocate((h, w), dtype=np.float32)
    b_diff_f_buf = engine.allocate((h, w), dtype=np.float32)
    
    # Destination output RGB float32 buffer
    if dst is not None and dst.shape == (h, w, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w, 3), dtype=np.float32)
        
    _mod("arm").run(
        "arm_demosaic",
        bayer=bayer_buf,
        wb_bayer=wb_bayer_buf,
        green=green_buf,
        r_diff=r_diff_buf,
        b_diff=b_diff_buf,
        r_diff_filtered=r_diff_f_buf,
        b_diff_filtered=b_diff_f_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    # Immediately release intermediate VRAM buffers back to pool
    engine.sync()
    wb_bayer_buf.release()
    green_buf.release()
    r_diff_buf.release()
    b_diff_buf.release()
    r_diff_f_buf.release()
    b_diff_f_buf.release()
    
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()
    
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def arm_demosaic_1channel(
    bayer, wb_r, wb_g1, wb_b, wb_g2,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Fast Green-Only ARM Demosaic to Grayscale 1-channel."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    
    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)
        
    _mod("arm").run(
        "arm_demosaic_1channel",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
        
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def arm_demosaic_half_res(
    bayer, wb_r, wb_g1, wb_b, wb_g2,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Bypass Demosaicing: Extract Green Sub-Sampling to 1/2 size (half_res) grayscale (ARM)."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    
    if dst is not None and dst.shape == (h // 2, w // 2) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2), dtype=np.float32)
        
    _mod("arm").run(
        "arm_demosaic_half_res",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def arm_demosaic_rgb_half_res(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Bypass Demosaicing: Extract RGB Direct Sub-Sampling to 1/2 size (half_res) RGB (ARM)."""
    bayer_buf = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    h, w = bayer_buf.shape[:2]
    
    if dst is not None and dst.shape == (h // 2, w // 2, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2, 3), dtype=np.float32)
        
    _mod("arm").run(
        "arm_demosaic_rgb_half_res",
        bayer=bayer_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def pure_arm_demosaic(
    bayer, black_level, white_level, c00, c01, c10, c11,
    return_gpu=False, dst=None
):
    """Taichi AOT Pure ARM Demosaicing (no color space or gamma)"""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    
    if dst is not None and dst.shape == (h, w, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w, 3), dtype=np.float32)
        
    _mod("arm").run(
        "pure_arm_demosaic",
        bayer=bayer_buf,
        dst=dst_buf,
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11)
    )
    
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
        
    return dst_buf if return_gpu else dst_buf.to_numpy()


def rotate_by_flip(img: np.ndarray, flip: int) -> np.ndarray:
    """Rotates a numpy array according to the LibRaw/rawpy sizes.flip value."""
    if flip == 0:
        return img
    elif flip == 1:
        return np.fliplr(img)
    elif flip == 2:
        return np.rot90(img, 2)
    elif flip == 3:
        return np.rot90(img, 2)
    elif flip == 4:
        return np.fliplr(np.rot90(img, 1))
    elif flip == 5:
        return np.rot90(img, 1)
    elif flip == 6:
        return np.rot90(img, 3)
    elif flip == 7:
        return np.fliplr(np.rot90(img, 3))
    return img


def demosaic(
    raw_input,
    wb_r=None, wb_g1=None, wb_b=None, wb_g2=None, cmatrix=None,
    black_level=None, white_level=None, c00=None, c01=None, c10=None, c11=None,
    method="hamilton", return_gpu=False, dst=None, output_bgr_u16=False
):
    """
    Unified, Ultra-Simplified GPU-Accelerated RAW Demosaicing API.
    
    This function acts as the single entry-point for all GPU-accelerated demosaicing algorithms.
    It automatically routes the raw sensor Bayer array to the appropriate pre-compiled AOT shader.
    
    Smart Metadata Auto-Extraction:
    -------------------------------
    To make integration extremely simple and prevent intimidating signatures, you can pass a
    `rawpy` object or a file path string directly as the first argument. All sensor metadata
    (Bayer array, WB gains, color matrix, black/white levels, layout indices) will be extracted
    automatically under the hood!
    
    Usage Examples:
    ---------------
    1. Pass rawpy object directly (Recommended):
       >>> rgb = ta_aot.demosaic(raw, method="hamilton")
       
    2. Pass DNG filepath directly:
       >>> rgb = ta_aot.demosaic("path/to/image.dng", method="hamilton")
       
    3. Pass parameters manually (For advanced JIT/AOT parity checks):
       >>> rgb = ta_aot.demosaic(bayer_np, wb_r, wb_g1, wb_b, wb_g2, cmatrix, ...)
       
    Supported Methods:
    -----------------
    1. 'hamilton' / 'hamilton-adams' / 'ha' / 'ppg':
       - Real Name: Hamilton-Adams Edge-Directed Demosaicing (equivalent to PPG / Patterned Pixel Grouping).
       - Features: High-speed edge-directed green interpolation, color difference gradient restoration,
                   and fused sRGB + Dynamic Algebraic Sigmoid contrast roll-off.
       
    Parameters:
    -----------
    raw_input : rawpy.RawPy, str, or np.ndarray
        Either a loaded rawpy object, a file path to a DNG/RAW image, or a raw Bayer NumPy array.
    """
    bayer = raw_input
    flip = 0
    
    # Check if raw_input is a filepath string or rawpy object
    is_rawpy_obj = hasattr(raw_input, "raw_image")
    is_filepath = isinstance(raw_input, str) and os.path.exists(raw_input)
    
    if is_rawpy_obj or is_filepath:
        import rawpy
        
        def _extract_from_raw(raw):
            b_np = raw.raw_image.astype(np.float32)
            bl = float(raw.black_level_per_channel[0])
            wl = float(raw.white_level)
            
            # --- Dynamic Experiment: Limit white level to 98% to preserve highlight headroom ---
            wl = wl * 0.98
            # ------------------------------------------------------------------------------------
            
            wb_np = np.array(raw.camera_whitebalance, dtype=np.float32)
            if len(wb_np) == 4:
                if wb_np[3] <= 0.01:
                    wb_np[3] = wb_np[1]
                g_gain = (wb_np[1] + wb_np[3]) / 2.0
                wb_np /= g_gain
            else:
                wb_np = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)

            c_00 = int(raw.raw_colors[0, 0])
            c_01 = int(raw.raw_colors[0, 1])
            c_10 = int(raw.raw_colors[1, 0])
            c_11 = int(raw.raw_colors[1, 1])
            cm = raw.color_matrix[:, :3].astype(np.float32)
            return b_np, wb_np[0], wb_np[1], wb_np[2], wb_np[3], cm, bl, wl, c_00, c_01, c_10, c_11
            
        if is_rawpy_obj:
            flip = getattr(raw_input.sizes, "flip", 0)
            bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix, black_level, white_level, c00, c01, c10, c11 = _extract_from_raw(raw_input)
        else:
            with rawpy.imread(raw_input) as raw:
                flip = getattr(raw.sizes, "flip", 0)
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix, black_level, white_level, c00, c01, c10, c11 = _extract_from_raw(raw)
        
        # Store active cmatrix in engine singleton for downstream gamma proxy color space alignment transformations
        engine.active_cmatrix = cmatrix
        engine.active_wb_r = wb_r
        engine.active_wb_g1 = wb_g1
        engine.active_wb_b = wb_b
        engine.active_wb_g2 = wb_g2
        engine.active_black_level = black_level
        engine.active_white_level = white_level
        engine.active_c00 = c00
        engine.active_c01 = c01
        engine.active_c10 = c10
        engine.active_c11 = c11

    method_lower = method.lower().replace("_", "-")
    if method_lower in ("hamilton", "hamilton-adams", "ha", "ppg"):
        if output_bgr_u16:
            # Step 1: Run the demosaic JIT/AOT to produce float32 RGB on GPU
            rgb_f32_gpu = hamilton_demosaic(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=True, dst=None
            )
            h, w = rgb_f32_gpu.shape[:2]
            
            # Step 2: Allocate host-accessible intermediate i32 BGR buffer in VRAM
            bgr_i32_gpu = engine.allocate((h, w, 3), dtype=np.int32, host_accessible=True)
            
            # Step 3: Run the conversion/channel-swapping graph on GPU
            _mod("hamilton").run(
                "rgb_to_bgr_i32",
                src=rgb_f32_gpu,
                dst=bgr_i32_gpu,
                h=int(h),
                w=int(w)
            )
            
            # Step 4: Clean up GPU intermediate float32 buffer immediately
            engine.sync()
            rgb_f32_gpu.release()
            
            # Step 5: Convert and return
            if not return_gpu:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_u16_cpu = bgr_u16_gpu.to_numpy()
                bgr_u16_gpu.release()
                bgr_i32_gpu.release()
                if flip != 0:
                    bgr_u16_cpu = rotate_by_flip(bgr_u16_cpu, flip)
                return bgr_u16_cpu
            else:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_i32_gpu.release()
                return bgr_u16_gpu
        else:
            res = hamilton_demosaic(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=return_gpu, dst=dst
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
    elif method_lower in ("hamilton-1channel", "hamilton-1ch", "ha-1ch"):
        res = hamilton_demosaic_1channel(
            bayer, wb_r, wb_g1, wb_b, wb_g2,
            black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("hamilton-half-res", "hamilton-half", "ha-half-res", "ha-half", "half-res"):
        res = hamilton_demosaic_half_res(
            bayer, wb_r, wb_g1, wb_b, wb_g2,
            black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("hamilton-rgb-half-res", "hamilton-rgb-half", "ha-rgb-half-res", "rgb-half-res"):
        res = hamilton_demosaic_rgb_half_res(
            bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
            black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("hamilton-3channel", "hamilton-3ch", "ha-3ch"):
        res = hamilton_demosaic_3channel(
            bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
            black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("arm", "arm-demosaic", "arm_demosaic"):
        if output_bgr_u16:
            rgb_f32_gpu = arm_demosaic(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=True, dst=None
            )
            h, w = rgb_f32_gpu.shape[:2]
            bgr_i32_gpu = engine.allocate((h, w, 3), dtype=np.int32, host_accessible=True)
            _mod("arm").run(
                "rgb_to_bgr_i32",
                src=rgb_f32_gpu,
                dst=bgr_i32_gpu,
                h=int(h),
                w=int(w)
            )
            engine.sync()
            rgb_f32_gpu.release()
            if not return_gpu:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_u16_cpu = bgr_u16_gpu.to_numpy()
                bgr_u16_gpu.release()
                bgr_i32_gpu.release()
                if flip != 0:
                    bgr_u16_cpu = rotate_by_flip(bgr_u16_cpu, flip)
                return bgr_u16_cpu
            else:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_i32_gpu.release()
                return bgr_u16_gpu
        else:
            res = arm_demosaic(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=return_gpu, dst=dst
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
    elif method_lower in ("arm-1channel", "arm-1ch", "arm_demosaic_1channel"):
        res = arm_demosaic_1channel(
            bayer, wb_r, wb_g1, wb_b, wb_g2,
            black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("arm-half-res", "arm-half", "arm_demosaic_half_res"):
        res = arm_demosaic_half_res(
            bayer, wb_r, wb_g1, wb_b, wb_g2,
            black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("arm-rgb-half-res", "arm-rgb-half", "arm_demosaic_rgb_half_res"):
        res = arm_demosaic_rgb_half_res(
            bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
            black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("pure-arm", "pure-arm-demosaic", "pure_arm_demosaic"):
        res = pure_arm_demosaic(
            bayer, black_level, white_level, c00, c01, c10, c11,
            return_gpu=return_gpu, dst=dst
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    else:
        supported = [
            "'hamilton' (aliases: 'hamilton-adams', 'ha', 'ppg')",
            "'hamilton-1channel' (aliases: 'hamilton-1ch', 'ha-1ch')",
            "'hamilton-half-res' (aliases: 'hamilton-half', 'ha-half-res', 'half-res')",
            "'hamilton-rgb-half-res' (aliases: 'hamilton-rgb-half', 'ha-rgb-half-res', 'rgb-half-res')",
            "'hamilton-3channel' (aliases: 'hamilton-3ch', 'ha-3ch')",
            "'arm' (aliases: 'arm-demosaic', 'arm_demosaic')",
            "'arm-1channel' (aliases: 'arm-1ch')",
            "'arm-half-res' (aliases: 'arm-half')",
            "'arm-rgb-half-res' (aliases: 'arm-rgb-half')",
            "'pure-arm'"
        ]
        raise ValueError(
            f"\n[Taichi AOT] Unsupported demosaicing method: '{method}'.\n"
            f"  SUPPORTED METHODS: {', '.join(supported)}"
        )


def generate_brief_pattern(num_pairs=256, patch_size=31, seed=42):
    """Generate BRIEF descriptor pattern coordinates."""
    np.random.seed(seed)
    sigma = patch_size / 5.0
    x1 = np.random.normal(0, sigma, num_pairs)
    y1 = np.random.normal(0, sigma, num_pairs)
    x2 = np.random.normal(0, sigma, num_pairs)
    y2 = np.random.normal(0, sigma, num_pairs)
    
    radius = patch_size // 2
    x1 = np.clip(np.round(x1), -radius, radius)
    y1 = np.clip(np.round(y1), -radius, radius)
    x2 = np.clip(np.round(x2), -radius, radius)
    y2 = np.clip(np.round(y2), -radius, radius)
    
    pattern = np.stack([x1, y1, x2, y2], axis=1).astype(np.float32)
    return pattern


def ofb(src1, src2, ratio_threshold=0.8, grid_size=32, threshold=0.015, margin=15, max_keypoints=1500):
    """
    Scale-Invariant Multi-Scale O-FAST-BRIEF Feature Matching on GPU.
    Automatically handles super low resolution images (< 240px) using adaptive parameters.
    
    Args:
        src1, src2: Grayscale input images (np.ndarray or TaichiGPUBuffer) [H, W] normalized to [0, 1].
        ratio_threshold: Lowe's ratio test threshold (default 0.8).
        grid_size: ANMS grid size (default 32).
        threshold: FAST score threshold (default 0.015).
        margin: Sensor margin to avoid border keypoints (default 15).
        max_keypoints: Maximum number of keypoints to extract (default 1500).
        
    Returns:
        pts1: Matched points from src1 (N, 2) in (x, y) coordinates.
        pts2: Matched points from src2 (N, 2) in (x, y) coordinates.
        scores: Matching scores / Hamming distances (N,).
    """
    img1_gpu = upload(src1) if not isinstance(src1, TaichiGPUBuffer) else src1
    img2_gpu = upload(src2) if not isinstance(src2, TaichiGPUBuffer) else src2
    
    h_orig, w_orig = img1_gpu.shape[:2]
    min_dim = min(h_orig, w_orig)
    
    # 1. Determine number of scale pyramid levels dynamically
    if min_dim < 240:
        num_levels = 1
    elif min_dim < 512:
        num_levels = 2
    else:
        num_levels = 3
        
    pattern_np = generate_brief_pattern(num_pairs=256, patch_size=31, seed=42)
    pattern_gpu = engine.upload(pattern_np)
    
    kps1_list = []
    kps2_list = []
    desc1_list = []
    
    for level in range(num_levels):
        if level > 0:
            dh, dw = h_orig // (2**level), w_orig // (2**level)
            curr1 = resize(img1_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True)
            curr2 = resize(img2_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True)
        else:
            curr1 = img1_gpu
            curr2 = img2_gpu
            
        h_l, w_l = curr1.shape[:2]
        
        # Adaptive parameters for this scale level
        grid_size_l = max(8, grid_size // (2**level))
        margin_l = max(4, margin // (2**level))
        threshold_l = threshold * (0.8 ** level)
        
        # Apply Median Filter to remove hot pixels
        img1_med = median_filter(curr1, return_gpu=True)
        img2_med = median_filter(curr2, return_gpu=True)
        
        # Apply Gaussian Blur to smooth noise for BRIEF descriptor
        img1_blur = gaussian_blur(curr1, sigma=2.0, return_gpu=True)
        img2_blur = gaussian_blur(curr2, sigma=2.0, return_gpu=True)
        
        # Allocate keypoint and descriptor buffers for this scale
        max_kps_l = max(100, max_keypoints // (2**level))
        
        kps1_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)
        kps2_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)
        
        score_map1 = engine.allocate((h_l, w_l), dtype=np.float32)
        score_map2 = engine.allocate((h_l, w_l), dtype=np.float32)
        
        counter1 = upload(np.zeros(1, dtype=np.int32))
        counter2 = upload(np.zeros(1, dtype=np.int32))
        
        # Detect keypoints
        _mod("ofb").run("detect_keypoints", src=img1_med, score_map=score_map1, keypoints=kps1_gpu, counter=counter1, h=h_l, w=w_l, grid_size=grid_size_l, margin=margin_l, threshold=threshold_l)
        _mod("ofb").run("detect_keypoints", src=img2_med, score_map=score_map2, keypoints=kps2_gpu, counter=counter2, h=h_l, w=w_l, grid_size=grid_size_l, margin=margin_l, threshold=threshold_l)
        
        desc1_gpu = engine.allocate((max_kps_l, 8), dtype=np.int32)
        desc2_gpu = engine.allocate((max_kps_l, 8), dtype=np.int32)
        matches_gpu = engine.allocate((max_kps_l, 2), dtype=np.int32)
        
        # Compute descriptors on GPU (fully async)
        _mod("ofb").run("compute_descriptors", src=img1_blur, kps=kps1_gpu, pattern=pattern_gpu, desc=desc1_gpu, counter=counter1, h=h_l, w=w_l)
        _mod("ofb").run("compute_descriptors", src=img2_blur, kps=kps2_gpu, pattern=pattern_gpu, desc=desc2_gpu, counter=counter2, h=h_l, w=w_l)
        
        # Match descriptors on GPU (fully async)
        _mod("ofb").run("match_descriptors", desc1=desc1_gpu, desc2=desc2_gpu, matches=matches_gpu, counter1=counter1, counter2=counter2, ratio_threshold=ratio_threshold)
        
        results_gpu = engine.allocate((max_kps_l, 6), dtype=np.float32)
        
        # Pack matches on GPU (fully async)
        _mod("ofb").run("pack_matches", kps1=kps1_gpu, kps2=kps2_gpu, matches=matches_gpu, counter1=counter1, counter2=counter2, results=results_gpu)
        
        # Download results (causes exactly one sync step per level)
        results_np = results_gpu.to_numpy()
        
        valid_mask = results_np[:, 5] == 1.0
        if np.any(valid_mask):
            pts1_level = results_np[valid_mask, 0:2]
            pts2_level = results_np[valid_mask, 2:4]
            dists_level = results_np[valid_mask, 4]
            
            scale_factor = float(2**level)
            for idx in range(len(pts1_level)):
                kps1_list.append([pts1_level[idx, 0] * scale_factor, pts1_level[idx, 1] * scale_factor])
                kps2_list.append([pts2_level[idx, 0] * scale_factor, pts2_level[idx, 1] * scale_factor])
                desc1_list.append(dists_level[idx])
            
        # Clean up this scale's temporary buffers
        results_gpu.release()
        desc1_gpu.release()
        desc2_gpu.release()
        matches_gpu.release()
        score_map1.release()
        score_map2.release()
        kps1_gpu.release()
        kps2_gpu.release()
        counter1.release()
        counter2.release()
        img1_med.release()
        img2_med.release()
        img1_blur.release()
        img2_blur.release()
        
        # Release downsampled images if allocated
        if level > 0:
            curr1.release()
            curr2.release()

    pattern_gpu.release()
    
    if len(kps1_list) == 0:
        return None, None, None
        
    return np.array(kps1_list, dtype=np.float32), np.array(kps2_list, dtype=np.float32), np.array(desc1_list, dtype=np.float32)


def get_fed_step_sizes(n=8):
    """Generate cycle of step sizes for Fast Explicit Diffusion (FED)."""
    tau_max = 0.25
    steps = []
    for j in range(n):
        tau = tau_max / (np.cos((2 * j + 1) * np.pi / (4 * n + 2)) ** 2)
        steps.append(float(tau))
    return steps


def akaze(src1, src2, ratio_threshold=0.8, grid_size=32, threshold=0.008, margin=15, max_keypoints=1500, k_contrast=0.02, num_fed_steps=8):
    """
    Scale-Invariant Multi-Scale A-KAZE (Accelerated KAZE) Feature Matching on GPU.
    Uses Non-Linear Scale Space via FED (Fast Explicit Diffusion) for superior keypoint quality
    under extreme noise, low contrast, and medical/microscopic images.
    
    Args:
        src1, src2: Grayscale input images (np.ndarray or TaichiGPUBuffer) [H, W] normalized to [0, 1].
        ratio_threshold: Lowe's ratio test threshold (default 0.8).
        grid_size: ANMS grid size (default 32).
        threshold: Hessian determinant score threshold (default 0.008).
        margin: Sensor margin to avoid border keypoints (default 15).
        max_keypoints: Maximum number of keypoints to extract (default 1500).
        k_contrast: Contrast threshold for non-linear conductivity (default 0.02).
        num_fed_steps: Number of FED steps per pyramid level (default 8).
        
    Returns:
        pts1: Matched points from src1 (N, 2) in (x, y) coordinates.
        pts2: Matched points from src2 (N, 2) in (x, y) coordinates.
        scores: Matching scores / Hamming distances (N,).
    """
    img1_gpu = upload(src1) if not isinstance(src1, TaichiGPUBuffer) else src1
    img2_gpu = upload(src2) if not isinstance(src2, TaichiGPUBuffer) else src2
    
    h_orig, w_orig = img1_gpu.shape[:2]
    min_dim = min(h_orig, w_orig)
    
    # Determine scale levels dynamically
    if min_dim < 240:
        num_levels = 1
    elif min_dim < 512:
        num_levels = 2
    else:
        num_levels = 3
        
    pattern_np = generate_brief_pattern(num_pairs=256, patch_size=31, seed=42)
    pattern_gpu = engine.upload(pattern_np)
    
    kps1_list = []
    kps2_list = []
    desc1_list = []
    
    fed_taus = get_fed_step_sizes(num_fed_steps)
    
    for level in range(num_levels):
        if level > 0:
            dh, dw = h_orig // (2**level), w_orig // (2**level)
            curr1 = resize(img1_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True)
            curr2 = resize(img2_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True)
        else:
            # We must copy to avoid modifying original inputs during diffusion
            curr1 = engine.allocate((h_orig, w_orig), dtype=np.float32)
            curr2 = engine.allocate((h_orig, w_orig), dtype=np.float32)
            copy_field(img1_gpu, curr1)
            copy_field(img2_gpu, curr2)
            
        h_l, w_l = curr1.shape[:2]
        
        # Allocate temporary buffers for Non-Linear Scale Space Diffusion
        temp1 = engine.allocate((h_l, w_l), dtype=np.float32)
        temp2 = engine.allocate((h_l, w_l), dtype=np.float32)
        cond1 = engine.allocate((h_l, w_l), dtype=np.float32)
        cond2 = engine.allocate((h_l, w_l), dtype=np.float32)
        
        # 1. Compute conductivity map at this scale level
        _mod("akaze").run("compute_conductivity_map", src=curr1, conductivity=cond1, h=h_l, w=w_l, k=float(k_contrast))
        _mod("akaze").run("compute_conductivity_map", src=curr2, conductivity=cond2, h=h_l, w=w_l, k=float(k_contrast))
        
        # 2. Run FED explicit diffusion iterations on GPU
        for tau in fed_taus:
            # Step on image 1
            _mod("akaze").run("fed_diffusion_step", src=curr1, dst=temp1, conductivity=cond1, h=h_l, w=w_l, tau=tau)
            curr1, temp1 = temp1, curr1 # zero-cost swap
            
            # Step on image 2
            _mod("akaze").run("fed_diffusion_step", src=curr2, dst=temp2, conductivity=cond2, h=h_l, w=w_l, tau=tau)
            curr2, temp2 = temp2, curr2 # zero-cost swap
            
        # 3. Compute Hessian Determinant Map
        score_map1 = engine.allocate((h_l, w_l), dtype=np.float32)
        score_map2 = engine.allocate((h_l, w_l), dtype=np.float32)
        
        _mod("akaze").run("compute_hessian_determinant", src=curr1, hessian_map=score_map1, h=h_l, w=w_l)
        _mod("akaze").run("compute_hessian_determinant", src=curr2, hessian_map=score_map2, h=h_l, w=w_l)
        
        # Adaptive parameters for this scale level
        grid_size_l = max(8, grid_size // (2**level))
        margin_l = max(4, margin // (2**level))
        threshold_l = threshold * (0.8 ** level)
        
        max_kps_l = max(100, max_keypoints // (2**level))
        
        kps1_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)
        kps2_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)
        
        counter1 = upload(np.zeros(1, dtype=np.int32))
        counter2 = upload(np.zeros(1, dtype=np.int32))
        
        # Detect keypoints (ANMS)
        _mod("akaze").run("detect_keypoints", hessian_map=score_map1, keypoints=kps1_gpu, counter=counter1, h=h_l, w=w_l, grid_size=grid_size_l, threshold=threshold_l)
        _mod("akaze").run("detect_keypoints", hessian_map=score_map2, keypoints=kps2_gpu, counter=counter2, h=h_l, w=w_l, grid_size=grid_size_l, threshold=threshold_l)
        
        desc1_gpu = engine.allocate((max_kps_l, 16), dtype=np.int32)
        desc2_gpu = engine.allocate((max_kps_l, 16), dtype=np.int32)
        matches_gpu = engine.allocate((max_kps_l, 2), dtype=np.int32)
        
        # Compute descriptors on GPU (fully async)
        _mod("akaze").run("compute_descriptors", src=curr1, kps=kps1_gpu, pattern=pattern_gpu, desc=desc1_gpu, counter=counter1, h=h_l, w=w_l)
        _mod("akaze").run("compute_descriptors", src=curr2, kps=kps2_gpu, pattern=pattern_gpu, desc=desc2_gpu, counter=counter2, h=h_l, w=w_l)
        
        # Match descriptors on GPU (fully async)
        _mod("akaze").run("match_descriptors", desc1=desc1_gpu, desc2=desc2_gpu, matches=matches_gpu, counter1=counter1, counter2=counter2, ratio_threshold=ratio_threshold)
        
        results_gpu = engine.allocate((max_kps_l, 6), dtype=np.float32)
        
        # Pack matches on GPU (fully async)
        _mod("akaze").run("pack_matches", kps1=kps1_gpu, kps2=kps2_gpu, matches=matches_gpu, counter1=counter1, counter2=counter2, results=results_gpu)
        
        # Download results (causes exactly one sync step per level)
        results_np = results_gpu.to_numpy()
        
        valid_mask = results_np[:, 5] == 1.0
        if np.any(valid_mask):
            pts1_level = results_np[valid_mask, 0:2]
            pts2_level = results_np[valid_mask, 2:4]
            dists_level = results_np[valid_mask, 4]
            
            scale_factor = float(2**level)
            for idx in range(len(pts1_level)):
                kps1_list.append([pts1_level[idx, 0] * scale_factor, pts1_level[idx, 1] * scale_factor])
                kps2_list.append([pts2_level[idx, 0] * scale_factor, pts2_level[idx, 1] * scale_factor])
                desc1_list.append(dists_level[idx])
                
        # Clean up temporary buffers
        results_gpu.release()
        desc1_gpu.release()
        desc2_gpu.release()
        matches_gpu.release()
        score_map1.release()
        score_map2.release()
        kps1_gpu.release()
        kps2_gpu.release()
        counter1.release()
        counter2.release()
        
        temp1.release()
        temp2.release()
        cond1.release()
        cond2.release()
        curr1.release()
        curr2.release()

    pattern_gpu.release()
    
    if len(kps1_list) == 0:
        return None, None, None
        
    return np.array(kps1_list, dtype=np.float32), np.array(kps2_list, dtype=np.float32), np.array(desc1_list, dtype=np.float32)


def find_homography(
    pts1,
    pts2,
    method: str = "MAGSAC++",
    ransacReprojThreshold: float = 3.0,
    n_hypotheses: int = 1024,
    max_iters: int = 1,
    return_gpu: bool = False
) -> tuple:
    """
    Estimasi matriks Homografi 3x3 menggunakan GPU RANSAC / MAGSAC++.
    API menyerupai cv2.findHomography(pts1, pts2, cv2.RANSAC, ransacReprojThreshold).
    
    Args:
        pts1  (np.ndarray | TaichiGPUBuffer): Array titik sumber, shape (N, 2) float32 [x, y].
        pts2  (np.ndarray | TaichiGPUBuffer): Array titik tujuan, shape (N, 2) float32 [x, y].
        method (str)      : 'RANSAC' atau 'MAGSAC++' (default MAGSAC++).
        ransacReprojThreshold (float): Jarak re-proyeksi maksimum inlier (piksel).
        n_hypotheses (int): Jumlah iterasi RANSAC paralel di GPU (default 1024).
        max_iters (int)   : Jumlah putaran pencarian ulang untuk memperbaiki akurasi.
        return_gpu (bool) : Jika True, mengembalikan mask dalam TaichiGPUBuffer (zero-copy VRAM).
    
    Returns:
        H    (np.ndarray | None): Matriks Homografi 3x3 float64, atau None jika gagal.
        mask (np.ndarray | TaichiGPUBuffer | None): Mask biner inlier shape (N, 1) uint8 atau TaichiGPUBuffer.
    """
    if pts1 is None or pts2 is None:
        return None, None

    # Deteksi input dari GPU Buffer atau NumPy
    is_pts1_gpu = isinstance(pts1, TaichiGPUBuffer)
    is_pts2_gpu = isinstance(pts2, TaichiGPUBuffer)

    n_pts = pts1.shape[0]
    if n_pts < 4:
        return None, None

    # Handle Upload ke GPU jika input berupa numpy array
    pts1_gpu = pts1 if is_pts1_gpu else upload(np.ascontiguousarray(pts1.reshape(-1, 2), dtype=np.float32))
    pts2_gpu = pts2 if is_pts2_gpu else upload(np.ascontiguousarray(pts2.reshape(-1, 2), dtype=np.float32))

    H_cand_gpu     = engine.allocate((n_hypotheses, 9), dtype=np.float32)
    inlier_cnt_gpu = engine.allocate((n_hypotheses,),   dtype=np.int32)

    best_H_flat  = None
    best_inliers = -1

    import time
    seed_base = int(time.time() * 1000) & 0x7FFFFFFF

    for iteration in range(max_iters):
        seed_offset = (seed_base + iteration * 31337) & 0x7FFFFFFF

        # Jalankan 1024 hipotesis RANSAC secara paralel di GPU (dari modul ransac)
        _mod("ransac").run(
            "ransac_homography",
            pts1=pts1_gpu, pts2=pts2_gpu,
            n_pts=n_pts, n_hypotheses=n_hypotheses,
            reproj_threshold=float(ransacReprojThreshold),
            H_candidates=H_cand_gpu, inlier_counts=inlier_cnt_gpu,
            seed_offset=seed_offset
        )

        # Download hanya vektor inlier count kecil (1024 int) — sangat cepat
        inlier_counts_np = inlier_cnt_gpu.to_numpy()
        best_idx         = int(np.argmax(inlier_counts_np))
        best_count       = int(inlier_counts_np[best_idx])

        if best_count > best_inliers:
            best_inliers = best_count
            H_cand_np    = H_cand_gpu.to_numpy()
            best_H_flat  = H_cand_np[best_idx]  # 9-element flat

    H_cand_gpu.release()
    inlier_cnt_gpu.release()

    if best_H_flat is None:
        if not is_pts1_gpu: pts1_gpu.release()
        if not is_pts2_gpu: pts2_gpu.release()
        return None, None

    # Hasilkan mask inlier pada GPU menggunakan matriks RANSAC terbaik
    H_flat_gpu = upload(best_H_flat)
    mask_gpu   = engine.allocate((n_pts,), dtype=np.int32)

    _mod("ransac").run(
        "generate_inlier_mask",
        pts1=pts1_gpu, pts2=pts2_gpu,
        H_best=H_flat_gpu, n_pts=n_pts,
        reproj_threshold=float(ransacReprojThreshold),
        mask_out=mask_gpu
    )

    # ── Least-Squares refinement (Weighted Least Squares) ───────────
    ATA_gpu = engine.allocate((8, 8), dtype=np.float32)
    ATb_gpu = engine.allocate((8,),   dtype=np.float32)

    _mod("ransac").run(
        "refine_homography",
        pts1=pts1_gpu, pts2=pts2_gpu,
        mask=mask_gpu, n_pts=n_pts,
        reproj_threshold=float(ransacReprojThreshold),
        ATA_out=ATA_gpu, ATb_out=ATb_gpu
    )

    ATA_np = ATA_gpu.to_numpy().astype(np.float64)
    ATb_np = ATb_gpu.to_numpy().astype(np.float64)

    ATA_gpu.release()
    ATb_gpu.release()

    H = best_H_flat.reshape(3, 3).astype(np.float64)

    # Selesaikan ATA*h = ATb di CPU
    try:
        h_refined = np.linalg.solve(ATA_np, ATb_np)
        H_refined = np.array([
            [h_refined[0], h_refined[1], h_refined[2]],
            [h_refined[3], h_refined[4], h_refined[5]],
            [h_refined[6], h_refined[7], 1.0],
        ], dtype=np.float64)
        H = H_refined
    except np.linalg.LinAlgError:
        pass  # Gunakan H dari RANSAC jika LS singular

    # Re-generate mask final menggunakan H yang sudah di-refine
    H_flat_refined = H.ravel().astype(np.float32)
    H_flat_gpu2    = upload(H_flat_refined)
    mask_gpu2      = engine.allocate((n_pts,), dtype=np.int32)

    _mod("ransac").run(
        "generate_inlier_mask",
        pts1=pts1_gpu, pts2=pts2_gpu,
        H_best=H_flat_gpu2, n_pts=n_pts,
        reproj_threshold=float(ransacReprojThreshold),
        mask_out=mask_gpu2
    )

    # Bersihkan input GPU Buffer jika kita yang mengalokasikannya secara lokal
    if not is_pts1_gpu: pts1_gpu.release()
    if not is_pts2_gpu: pts2_gpu.release()
    H_flat_gpu.release()
    mask_gpu.release()
    H_flat_gpu2.release()

    if return_gpu:
        return H, mask_gpu2
    else:
        mask_np = mask_gpu2.to_numpy().astype(np.uint8).reshape(-1, 1)
        mask_gpu2.release()
        return H, mask_np


def warp_perspective(src, M, dsize, return_gpu=False, dst=None):
    """
    GPU-accelerated Warp Perspective menggunakan Taichi AOT.
    API menyerupai cv2.warpPerspective(src, M, dsize).
    """
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else upload(src)

    h_src, w_src = src_buf.shape[:2]
    w_dst, h_dst = dsize

    # Hitung inverse matriks di CPU menggunakan NumPy
    M_np = np.asarray(M, dtype=np.float32)
    try:
        M_inv = np.linalg.inv(M_np)
    except np.linalg.LinAlgError:
        M_inv = np.eye(3, dtype=np.float32)

    M_inv_gpu = upload(M_inv)

    is_vec = getattr(src_buf, "is_vector", False)
    is_3d = len(src_buf.shape) == 3 or is_vec
    v_dim = src_buf.vector_dim if is_vec else (src_buf.shape[2] if len(src_buf.shape) == 3 else 1)

    if dst is None:
        if is_3d:
            dst_buf = OutputArray((h_dst, w_dst, v_dim), dtype=src_buf.dtype, is_vector=is_vec, vector_dim=v_dim)
        else:
            dst_buf = OutputArray((h_dst, w_dst), dtype=src_buf.dtype)
    else:
        dst_buf = dst

    src_v = src_buf
    dst_v = dst_buf
    if is_3d:
        if not getattr(src_buf, "is_vector", False):
            src_v = src_buf.view_as_vector(True)
        if not getattr(dst_buf, "is_vector", False):
            dst_v = dst_buf.view_as_vector(True)

    graph = "warp_perspective_f32_3d" if is_3d else "warp_perspective_f32_2d"

    _mod("remap").run(
        graph,
        src=src_v,
        M_inv=M_inv_gpu,
        dst=dst_v,
        h_src=h_src,
        w_src=w_src,
        h_dst=h_dst,
        w_dst=w_dst
    )

    M_inv_gpu.release()
    if not is_gpu:
        src_buf.release()

    return dst_buf if return_gpu else dst_buf.to_numpy()


# ===========================================================================
# AOT Dispatch: Non-Local Means Denoising
# ===========================================================================
def non_local_means(src, h_param=10.0, search_window=7, patch_size=5,
                     return_gpu=False):
    """
    Taichi AOT Non-Local Means Denoising.
    Dispatches to pre-compiled fixed-parameter kernel variants.
    Supports: search_window in {3,5,7}, patch_size in {1,2,3}.
    Auto-cast: uint8/uint16 input is normalized to [0,1] float32,
    processed, then cast back to original dtype.
    """
    is_numpy = isinstance(src, np.ndarray)
    is_3d = len(src.shape) == 3 and src.shape[2] == 3

    # --- Auto-cast: normalize integer types to float32 [0,1] ---
    orig_dtype = src.dtype if isinstance(src, np.ndarray) else np.float32
    if isinstance(src, np.ndarray) and src.dtype == np.uint8:
        src = src.astype(np.float32) / 255.0
    elif isinstance(src, np.ndarray) and src.dtype == np.uint16:
        src = src.astype(np.float32) / 65535.0

    # Round to nearest supported variant
    sr = min(search_window, 7)
    if sr <= 3:
        sr = 3
    elif sr <= 5:
        sr = 5
    else:
        sr = 7

    pr = min(patch_size, 3)
    if pr <= 1:
        pr = 1
    elif pr <= 2:
        pr = 2
    else:
        pr = 3

    h, w = src.shape[:2]

    src_np = np.ascontiguousarray(src, dtype=np.float32)
    h, w = src_np.shape[:2]

    if is_3d:
        # Bypass engine.upload auto-vectorization (it forces is_vector=True for 3ch)
        # The AOT graph was compiled with ndim=3 raw ndarray, not vector.
        from taichi_library.taichi_aot.engine import _LIB, _RUNTIME
        src_buf = engine.allocate((h, w, 3), dtype=np.float32, is_vector=False, host_accessible=True)
        dst_buf = engine.allocate((h, w, 3), dtype=np.float32, is_vector=False)
        _LIB.write_to_gpu_buffer(_RUNTIME, src_buf.handle, src_np.ctypes.data, src_buf.nbytes)
        graph_name = f"nlm_3ch_s{sr}_p{pr}_f32"
    else:
        src_buf = InputArray(src_np)
        dst_buf = OutputArray((h, w), dtype=np.float32)
        graph_name = f"nlm_1ch_s{sr}_p{pr}_f32"

    _mod("nlm").run(
        graph_name,
        src=src_buf,
        dst=dst_buf,
        h=h,
        w=w,
        h_param=float(h_param),
    )

    if return_gpu:
        return dst_buf

    result = dst_buf.to_numpy()

    # --- Auto-cast back to original dtype ---
    if orig_dtype == np.uint8:
        return np.clip(result * 255.0, 0, 255).astype(np.uint8)
    elif orig_dtype == np.uint16:
        return np.clip(result * 65535.0, 0, 65535).astype(np.uint16)
    return result


# ===========================================================================
# AOT Dispatch: Inpainting
# ===========================================================================
def inpaint(src, mask, inpaint_radius=3, flags=0, return_gpu=False):
    """
    Taichi AOT Inpainting.
    Dispatches individual kernels in sequence (distance transform, dilate, fill).
    """
    is_numpy = isinstance(src, np.ndarray)
    is_3d = len(src.shape) == 3 and src.shape[2] == 3

    src_buf, src_is_temp2 = _ensure_upload(src)
    mask_buf = InputArray(mask.astype(np.float32) if isinstance(mask, np.ndarray) else mask)

    h, w = src_buf.shape[:2]
    max_dist = max(h, w) // 2 + 1

    # Allocate intermediate buffers
    dist_buf = OutputArray((h, w), dtype=np.float32)
    dist_tmp = OutputArray((h, w), dtype=np.float32)
    boundary_buf = OutputArray((h, w), dtype=np.float32)
    filled_buf = OutputArray((h, w), dtype=np.float32)

    # Stage 1: Init distance
    _mod("inpaint").run("inpaint_init_distance_f32",
        mask=mask_buf, dist=dist_buf, boundary=boundary_buf, h=h, w=w)

    # Iterative dilation to compute distance map
    for level in range(max_dist):
        _mod("inpaint").run("inpaint_dilate_distance_f32",
            dist_in=dist_buf, dist_out=dist_tmp, h=h, w=w,
            current_level=float(level))
        dist_buf, dist_tmp = dist_tmp, dist_buf

    # Stage 2: Init filled mask
    _mod("inpaint").run("inpaint_init_distance_f32",
        mask=mask_buf, dist=filled_buf, boundary=boundary_buf, h=h, w=w)
    _mod("inpaint").run("inpaint_set_filled_f32",
        mask=mask_buf, filled=filled_buf, h=h, w=w)

    # Stage 3: Iterative inpainting
    if is_3d:
        for level in range(1, max_dist + 1):
            _mod("inpaint").run("inpaint_level_3ch_f32",
                src=src_buf, dist=dist_buf, filled=filled_buf,
                h=h, w=w, target_level=float(level),
                inpaint_radius=float(inpaint_radius))
            _mod("inpaint").run("inpaint_mark_filled_f32",
                dist=dist_buf, filled=filled_buf, h=h, w=w,
                target_level=float(level))
    else:
        for level in range(1, max_dist + 1):
            _mod("inpaint").run("inpaint_level_1ch_f32",
                src=src_buf, dist=dist_buf, filled=filled_buf,
                h=h, w=w, target_level=float(level),
                inpaint_radius=float(inpaint_radius))
            _mod("inpaint").run("inpaint_mark_filled_f32",
                dist=dist_buf, filled=filled_buf, h=h, w=w,
                target_level=float(level))

    return src_buf if return_gpu else src_buf.to_numpy()


# ===========================================================================
# AOT Dispatch: Seamless Clone (Poisson Image Editing)
# ===========================================================================
def seamless_clone(src, dst, mask, center=(0, 0), flags=1,
                    max_iterations=200, return_gpu=False):
    """
    Taichi AOT Seamless Clone.
    Dispatches Jacobi iterations for Poisson blending.
    """
    is_numpy = isinstance(dst, np.ndarray)

    src_buf = InputArray(src)
    dst_buf = InputArray(dst)
    mask_buf = InputArray(mask.astype(np.float32) if isinstance(mask, np.ndarray) else mask)

    src_buf = src_buf.view_as_vector(True) if len(src_buf.shape) == 3 else src_buf
    dst_buf_v = dst_buf.view_as_vector(True) if len(dst_buf.shape) == 3 else dst_buf

    h, w = dst_buf.shape[:2]

    # Output = copy of dst
    out_buf = OutputArray((h, w, 3), dtype=np.float32, is_vector=True, vector_dim=3)
    _mod("seamless_clone").run("seamless_copy_f32",
        s=dst_buf_v, d=out_buf, h=h, w=w)

    # Intermediate buffers
    div_x = OutputArray((h, w), dtype=np.float32)
    div_y = OutputArray((h, w), dtype=np.float32)
    lap_buf = OutputArray((h, w), dtype=np.float32)
    f_in_buf = OutputArray((h, w), dtype=np.float32)
    f_out_buf = OutputArray((h, w), dtype=np.float32)

    num_channels = 3 if flags != 3 else 1  # MONOCHROME_TRANSFER = 3

    for ch in range(num_channels):
        # Compute guidance gradient
        if flags == 1 or flags == 3:  # NORMAL_CLONE or MONOCHROME_TRANSFER
            _mod("seamless_clone").run("seamless_divergence_normal_f32",
                src=src_buf, div_x=div_x, div_y=div_y, h=h, w=w, ch=ch)
        elif flags == 2:  # MIXED_CLONE
            _mod("seamless_clone").run("seamless_divergence_mixed_f32",
                src=src_buf, dst=dst_buf_v, div_x=div_x, div_y=div_y, h=h, w=w, ch=ch)

        # Compute Laplacian
        _mod("seamless_clone").run("seamless_laplacian_f32",
            div_x=div_x, div_y=div_y, lap=lap_buf, h=h, w=w)

        # Init f from destination channel
        _mod("seamless_clone").run("seamless_init_f_channel_f32",
            dst_arr=out_buf, f=f_in_buf, h=h, w=w, c=ch)

        # Jacobi iterations
        for _ in range(max_iterations):
            _mod("seamless_clone").run("seamless_jacobi_step_f32",
                f_in=f_in_buf, f_out=f_out_buf, lap=lap_buf,
                mask=mask_buf, h=h, w=w)
            f_in_buf, f_out_buf = f_out_buf, f_in_buf

        # Composite
        _mod("seamless_clone").run("seamless_composite_f32",
            f=f_in_buf, dst_out=out_buf, mask=mask_buf, h=h, w=w, ch=ch)

    return out_buf if return_gpu else out_buf.to_numpy()


# ===========================================================================
# AOT Dispatch: MTB (Median Threshold Bitmap) Alignment
# ===========================================================================
def align_mtb(ref_img, target_img, max_levels=6, tolerance=4.0/255.0):
    """
    Taichi AOT MTB Alignment.
    Returns: (dx, dy) integer shift.
    Uses pre-compiled histogram, bitmap, and error kernels.
    """
    import cv2

    # Convert to grayscale
    if len(ref_img.shape) == 3:
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    else:
        ref_gray = ref_img.astype(np.float32) / 255.0 if ref_img.dtype != np.float32 else ref_img

    if len(target_img.shape) == 3:
        tgt_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    else:
        tgt_gray = target_img.astype(np.float32) / 255.0 if target_img.dtype != np.float32 else target_img

    # Build image pyramids (CPU-based for AOT simplicity)
    def _build_pyr(img, levels):
        pyr = [img]
        for _ in range(levels - 1):
            img = cv2.pyrDown(img)
            pyr.append(img)
        return pyr

    ref_pyr = _build_pyr(ref_gray, max_levels)
    tgt_pyr = _build_pyr(tgt_gray, max_levels)

    current_dx, current_dy = 0, 0

    for level in reversed(range(len(ref_pyr))):
        ref_level = ref_pyr[level]
        tgt_level = tgt_pyr[level]
        h, w = ref_level.shape

        current_dx *= 2
        current_dy *= 2

        ref_buf = InputArray(ref_level)
        tgt_buf = InputArray(tgt_level)

        # Compute histograms
        ref_hist = OutputArray((256,), dtype=np.int32)
        tgt_hist = OutputArray((256,), dtype=np.int32)
        _mod("mtb").run("mtb_histogram_f32", img=ref_buf, hist=ref_hist)
        _mod("mtb").run("mtb_histogram_f32", img=tgt_buf, hist=tgt_hist)

        # Find medians (CPU)
        def _find_median(hist_np):
            total = h * w
            cum = 0
            for i in range(256):
                cum += int(hist_np[i])
                if cum >= total // 2:
                    return i / 255.0
            return 0.5

        ref_med = _find_median(ref_hist.to_numpy())
        tgt_med = _find_median(tgt_hist.to_numpy())

        # Compute bitmaps and exclusion maps
        ref_bitmap = OutputArray((h, w), dtype=np.int32)
        ref_excl = OutputArray((h, w), dtype=np.int32)
        tgt_bitmap = OutputArray((h, w), dtype=np.int32)
        tgt_excl = OutputArray((h, w), dtype=np.int32)

        _mod("mtb").run("mtb_bitmaps_f32", img=ref_buf, bitmap=ref_bitmap,
            exclusion=ref_excl, median_val=float(ref_med), tolerance=float(tolerance))
        _mod("mtb").run("mtb_bitmaps_f32", img=tgt_buf, bitmap=tgt_bitmap,
            exclusion=tgt_excl, median_val=float(tgt_med), tolerance=float(tolerance))

        # Search 3x3 neighborhood
        best_err = 2**31 - 1
        best_ox, best_oy = 0, 0
        err_buf = OutputArray((1,), dtype=np.int32)

        for oy in [-1, 0, 1]:
            for ox in [-1, 0, 1]:
                test_dx = current_dx + ox
                test_dy = current_dy + oy
                _mod("mtb").run("mtb_error_f32",
                    bitmap1=ref_bitmap, exclusion1=ref_excl,
                    bitmap2=tgt_bitmap, exclusion2=tgt_excl,
                    error_buf=err_buf, dx=test_dx, dy=test_dy)
                err_val = int(err_buf.to_numpy()[0])
                if err_val < best_err:
                    best_err = err_val
                    best_ox, best_oy = ox, oy

        current_dx += best_ox
        current_dy += best_oy

    return current_dx, current_dy


def _ensure_upload(arr):
    """Helper: upload ndarray to InputArray if needed."""
    if isinstance(arr, TaichiGPUBuffer):
        return arr, False
    return InputArray(arr), True


# =========================================================================
# NEW ALGORITHMS — AOT Bridge Wrappers
# =========================================================================

# --- Color Space Conversion Constants ---
COLOR_BGR2HSV = 40
COLOR_HSV2BGR = 54
COLOR_BGR2YCrCb = 36
COLOR_YCrCb2BGR = 38
COLOR_BGR2LAB = 44
COLOR_LAB2BGR = 55


# --- Inpainting Flags ---
INPAINT_TELEA = 0
INPAINT_NS = 1

# --- Seamless Clone Flags ---
NORMAL_CLONE = 1
MIXED_CLONE = 2
MONOCHROME_TRANSFER = 3


def cvtColor_extended(src, code, return_gpu=False):
    """AOT Color Space Conversion (BGR<->HSV, BGR<->YCrCb, BGR<->LAB)."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    # Override auto-detected is_vector for ndim=3 graphs:
    # engine.upload auto-sets is_vector=True for (H,W,3) arrays,
    # but the TCM graph expects plain ndim=3 (not vector field).
    if getattr(src_buf, 'is_vector', False):
        src_buf = src_buf.view_as_vector(False)
    h, w = src_buf.shape[:2]
    # Allocate dst as plain ndarray (is_vector=False) to match ndim=3 graph
    dst = engine.allocate((h, w, 3))

    graph_map = {
        COLOR_BGR2HSV: "bgr2hsv_f32",
        COLOR_HSV2BGR: "hsv2bgr_f32",
        COLOR_BGR2YCrCb: "bgr2ycrcb_f32",
        COLOR_YCrCb2BGR: "ycrcb2bgr_f32",
        COLOR_BGR2LAB: "bgr2lab_f32",
        COLOR_LAB2BGR: "lab2bgr_f32",
    }
    graph_name = graph_map.get(code)
    if graph_name is None:
        raise ValueError(f"Unsupported color conversion code: {code}")

    _mod("color_convert").run(graph_name, src=src_buf, dst=dst, h=h, w=w)
    return dst if return_gpu else dst.to_numpy()


def otsu_threshold_aot(src, thresh_type=0, max_val=255.0, return_gpu=False):
    """AOT Otsu's Thresholding. Returns (threshold_value, binary_image)."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    dst = engine.allocate((h, w))

    # Histogram — zero-initialize to avoid garbage data from buffer pool reuse
    num_bins = 256
    hist = engine.allocate((num_bins,), dtype=np.int32)
    zero_np = np.zeros(num_bins, dtype=np.int32)
    zero_buf = engine.upload(zero_np)
    copy_field(zero_buf, hist)
    zero_buf.destroy()

    _mod("otsu").run("otsu_histogram_f32", src=src_buf, hist=hist, h=h, w=w,
                      max_val=float(max_val), num_bins=num_bins)

    # Find threshold on CPU — use float64 to avoid int32 overflow
    hist_np = hist.to_numpy().astype(np.float64)
    total = float(hist_np.sum())
    if total == 0:
        threshold_val = 0.0
    else:
        mu_T = sum(float(i) * hist_np[i] for i in range(256)) / total
        w0, sum_0, max_sigma, best_t = 0.0, 0.0, -1.0, 0
        for t in range(256):
            w0 += hist_np[t]
            if w0 == 0: continue
            w1 = total - w0
            if w1 == 0: break
            sum_0 += float(t) * hist_np[t]
            mu0 = sum_0 / w0
            mu1 = (mu_T * total - sum_0) / w1
            sigma_B = w0 * w1 * (mu0 - mu1) ** 2
            if sigma_B > max_sigma:
                max_sigma = sigma_B
                best_t = t
        threshold_val = float(best_t)

    # Apply threshold
    _mod("otsu").run("otsu_threshold_f32", src=src_buf, dst=dst,
                      threshold=threshold_val, max_val=float(max_val),
                      thresh_type=thresh_type, h=h, w=w)
    result = dst if return_gpu else dst.to_numpy()
    return threshold_val, result


def clahe_aot(src, clip_limit=2.0, tile_grid_size=(8, 8), return_gpu=False):
    """AOT CLAHE - Contrast Limited Adaptive Histogram Equalization."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    tiles_x, tiles_y = tile_grid_size
    total_tiles = tiles_x * tiles_y
    num_bins = 256
    tile_h = (h + tiles_y - 1) // tiles_y
    tile_w = (w + tiles_x - 1) // tiles_x
    tile_pixels = tile_h * tile_w
    beta = max(int(clip_limit * tile_pixels / num_bins), 1)

    hist = engine.allocate((total_tiles, num_bins), dtype=np.int32)
    lut = engine.allocate((total_tiles, num_bins))
    dst = engine.allocate((h, w))

    # Zero-initialize hist and lut to avoid garbage from buffer pool reuse
    zero_hist = engine.upload(np.zeros((total_tiles, num_bins), dtype=np.int32))
    copy_field(zero_hist, hist)
    zero_hist.destroy()
    zero_lut = engine.upload(np.zeros((total_tiles, num_bins), dtype=np.float32))
    copy_field(zero_lut, lut)
    zero_lut.destroy()

    _mod("clahe").run("clahe_pipeline_f32",
                       src=src_buf, hist=hist, lut=lut, dst=dst,
                       h=h, w=w, tile_h=tile_h, tile_w=tile_w,
                       tiles_x=tiles_x, tiles_y=tiles_y,
                       total_tiles=total_tiles, num_bins=num_bins,
                       clip_limit=beta, tile_pixels=tile_pixels,
                       max_val=255.0)
    return dst if return_gpu else dst.to_numpy()


def canny_aot(src, low_threshold=50.0, high_threshold=150.0, return_gpu=False):
    """AOT Canny Edge Detector."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]

    # Step 0: Gaussian pre-smoothing (matches OpenCV cv2.Canny and JIT implementation)
    blurred_buf = gaussian_blur(src_buf, sigma=1.0, kernel_size=5, return_gpu=True)

    # Internal buffers
    gx = engine.allocate((h, w))
    gy = engine.allocate((h, w))
    mag = engine.allocate((h, w))
    nms = engine.allocate((h, w))
    edges = engine.allocate((h, w))
    dst = engine.allocate((h, w))

    # Step 1: Sobel gradients on pre-smoothed image
    _mod("gradients").run("sobel_f32", src=blurred_buf, dst_dx=gx, dst_dy=gy, h=h, w=w)
    blurred_buf.release()

    # Step 2: Mag + NMS
    _mod("canny").run("canny_mag_nms_f32", gx=gx, gy=gy, mag=mag, nms=nms, h=h, w=w)

    # Step 3: Double threshold
    _mod("canny").run("canny_threshold_f32", nms=nms, edges=edges,
                       low_thresh=low_threshold, high_thresh=high_threshold, h=h, w=w)

    # Step 4: Iterative hysteresis
    for _ in range(h + w):  # max iterations
        zero_np = np.zeros(1, dtype=np.int32)
        changed_buf = engine.upload(zero_np)
        _mod("canny").run("canny_hysteresis_f32", edges=edges, changed=changed_buf, h=h, w=w)
        if changed_buf.to_numpy()[0] == 0:
            changed_buf.release()
            break
        changed_buf.release()

    # Step 5: Finalize
    _mod("canny").run("canny_finalize_f32", edges=edges, dst=dst, h=h, w=w)
    return dst if return_gpu else dst.to_numpy()


def hough_lines_aot(edge_image, rho_resolution=1.0, theta_resolution=1.0,
                     threshold=80, return_gpu=False):
    """AOT Hough Line Transform. Returns list of (rho, theta) pairs."""
    is_gpu = isinstance(edge_image, TaichiGPUBuffer)
    src_buf = edge_image if is_gpu else engine.upload(edge_image)
    h, w = src_buf.shape[:2]

    import math
    num_theta = int(180.0 / theta_resolution)
    diag = int(math.sqrt(h * h + w * w))
    num_rho = int(2 * diag / rho_resolution) + 1
    rho_offset = diag

    acc = engine.allocate((num_rho, num_theta), dtype=np.int32)
    cos_table = engine.allocate((num_theta,))
    sin_table = engine.allocate((num_theta,))
    peaks_buf = engine.allocate((500, 3))  # max 500 peaks
    peak_count = engine.allocate((1,), dtype=np.int32)

    # Fill trig tables
    cos_np = np.array([math.cos(math.radians(t * theta_resolution)) for t in range(num_theta)], dtype=np.float32)
    sin_np = np.array([math.sin(math.radians(t * theta_resolution)) for t in range(num_theta)], dtype=np.float32)
    cos_table_buf = engine.upload(cos_np)
    sin_table_buf = engine.upload(sin_np)

    # Vote
    _mod("hough").run("hough_vote_f32", edges=src_buf, accumulator=acc,
                       cos_table=cos_table_buf, sin_table=sin_table_buf,
                       h=h, w=w, num_theta=num_theta, rho_offset=rho_offset,
                       edge_threshold=128.0)

    # Find peaks
    _mod("hough").run("hough_peaks_f32", accumulator=acc, peaks=peaks_buf,
                       peak_count=peak_count, num_rho=num_rho, num_theta=num_theta,
                       threshold=threshold, nms_radius=10, max_peaks=500)

    peaks_np = peaks_buf.to_numpy()
    count = min(int(peak_count.to_numpy()[0]), 500)  # Clamp to buffer size
    lines = []
    for i in range(count):
        rho = (peaks_np[i, 0] - rho_offset) * rho_resolution
        theta = peaks_np[i, 1] * theta_resolution * math.pi / 180.0
        lines.append((rho, theta))
    return lines


def guided_filter_aot(guide, src, radius=8, epsilon=1e-4, return_gpu=False):
    """AOT Guided Filter (edge-preserving smoothing).
    Uses box_filter module for box averaging and guided_filter module for element-wise ops.
    """
    is_gpu_src = isinstance(src, TaichiGPUBuffer)
    is_gpu_guide = isinstance(guide, TaichiGPUBuffer)
    src_buf = src if is_gpu_src else engine.upload(src)
    guide_buf = guide if is_gpu_guide else engine.upload(guide)
    h, w = src_buf.shape[:2]

    # Box filter helper (separable) — use 1ch generic graph
    ks = 2 * radius + 1
    radius_bf = ks // 2

    def _box_filter_1ch(input_buf):
        """Apply separable box filter on a single-channel buffer using box_filter module."""
        out = engine.allocate((h, w))
        tmp = engine.allocate((h, w))
        _mod("box_filter").run("box_filter_separable_generic_1ch_f32",
                               src=input_buf, tmp=tmp, dst=out, h=h, w=w, radius=radius_bf)
        tmp.destroy()
        return out

    # Step 1: Compute means via box filter
    mean_I = _box_filter_1ch(guide_buf)
    mean_p = _box_filter_1ch(src_buf)

    # Element-wise products
    II = engine.allocate((h, w))
    Ip = engine.allocate((h, w))
    _mod("guided_filter").run("gf_mul_f32", a=guide_buf, b=guide_buf, dst=II, h=h, w=w)
    _mod("guided_filter").run("gf_mul_f32", a=guide_buf, b=src_buf, dst=Ip, h=h, w=w)
    mean_II = _box_filter_1ch(II)
    mean_Ip = _box_filter_1ch(Ip)
    II.destroy()
    Ip.destroy()

    # Step 2: Compute var and cov
    var_I = engine.allocate((h, w))
    cov_Ip = engine.allocate((h, w))
    _mod("guided_filter").run("gf_var_cov_f32",
                               mean_I=mean_I, mean_p=mean_p,
                               mean_II=mean_II, mean_Ip=mean_Ip,
                               var_I=var_I, cov_Ip=cov_Ip, h=h, w=w)

    # Step 3: Compute a, b coefficients
    a = engine.allocate((h, w))
    b = engine.allocate((h, w))
    _mod("guided_filter").run("gf_ab_f32", var_I=var_I, cov_Ip=cov_Ip,
                               mean_I=mean_I, mean_p=mean_p,
                               a=a, b=b, epsilon=float(epsilon), h=h, w=w)

    # Step 4: Average a, b via box filter
    mean_a = _box_filter_1ch(a)
    mean_b = _box_filter_1ch(b)
    a.destroy()
    b.destroy()

    # Step 5: Compute output
    dst = engine.allocate((h, w))
    _mod("guided_filter").run("gf_output_f32", mean_a=mean_a, mean_b=mean_b,
                               I=guide_buf, dst=dst, h=h, w=w)

    # Cleanup
    mean_I.destroy()
    mean_p.destroy()
    mean_II.destroy()
    mean_Ip.destroy()
    var_I.destroy()
    cov_Ip.destroy()
    mean_a.destroy()
    mean_b.destroy()

    return dst if return_gpu else dst.to_numpy()


def non_local_means_aot(src, h_param=10.0, search_window=7, patch_size=5,
                         refinement_strength=1.0, shrinkage_strength=1.0,
                         return_gpu=False):
    """AOT Non-Local Means Denoising (fixed-parameter variants)."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    
    # View as 3D scalar array if uploaded as 2D vector array
    if getattr(src_buf, 'is_vector', False):
        src_buf = src_buf.view_as_vector(False)
        
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    # Select AOT variant based on search_window and patch_size
    sr = search_window
    pr = patch_size
    valid_configs = [(3, 1), (5, 2), (7, 3)]
    # Find closest valid config
    best = min(valid_configs, key=lambda c: abs(c[0] - sr) + abs(c[1] - pr))
    sr, pr = best

    if is_3d:
        dst = engine.allocate((h, w, 3), is_vector=False)
        yuv = engine.allocate((h, w, 3), is_vector=False)
        graph = f"nlm_3ch_s{sr}_p{pr}_f32"
        _mod("nlm").run(graph, src=src_buf, yuv=yuv, dst=dst, h=h, w=w, h_param=float(h_param),
                        refinement_strength=float(refinement_strength),
                        shrinkage_strength=float(shrinkage_strength))
        yuv.destroy()
    else:
        dst = engine.allocate((h, w))
        graph = f"nlm_1ch_s{sr}_p{pr}_f32"
        _mod("nlm").run(graph, src=src_buf, dst=dst, h=h, w=w, h_param=float(h_param),
                        refinement_strength=float(refinement_strength),
                        shrinkage_strength=float(shrinkage_strength))
    return dst if return_gpu else dst.to_numpy()


def inpaint_aot(src, mask, inpaint_radius=3, return_gpu=False):
    """AOT Image Inpainting (iterative diffusion)."""
    is_gpu_src = isinstance(src, TaichiGPUBuffer)
    is_gpu_mask = isinstance(mask, TaichiGPUBuffer)
    src_buf = src if is_gpu_src else engine.upload(src)
    # Override auto-detected is_vector for ndim=3 graphs (3ch inpaint)
    if getattr(src_buf, 'is_vector', False):
        src_buf = src_buf.view_as_vector(False)
    mask_buf = mask if is_gpu_mask else engine.upload(mask)
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    # Working buffers
    dist = engine.allocate((h, w))
    boundary = engine.allocate((h, w))
    filled = engine.allocate((h, w))

    # Step 1: Initialize
    _mod("inpaint").run("inpaint_init_distance_f32", mask=mask_buf, dist=dist,
                         boundary=boundary, h=h, w=w)
    _mod("inpaint").run("inpaint_set_filled_f32", mask=mask_buf, filled=filled, h=h, w=w)

    # Step 2: Iterative dilation + inpainting
    max_level = int(max(h, w))
    for level in range(1, max_level + 1):
        dist2 = engine.allocate((h, w))
        _mod("inpaint").run("inpaint_dilate_distance_f32",
                             dist_in=dist, dist_out=dist2, h=h, w=w,
                             current_level=float(level - 1))
        copy_field(dist2, dist)
        dist2.destroy()

        if is_3d:
            _mod("inpaint").run("inpaint_level_3ch_f32", src=src_buf, dist=dist,
                                 filled=filled, h=h, w=w,
                                 target_level=float(level),
                                 inpaint_radius=float(inpaint_radius))
        else:
            _mod("inpaint").run("inpaint_level_1ch_f32", src=src_buf, dist=dist,
                                 filled=filled, h=h, w=w,
                                 target_level=float(level),
                                 inpaint_radius=float(inpaint_radius))

        _mod("inpaint").run("inpaint_mark_filled_f32", dist=dist, filled=filled,
                             h=h, w=w, target_level=float(level))

    return src_buf if return_gpu else src_buf.to_numpy()


def seamless_clone_aot(src, dst_img, mask, center=(0, 0),
                         flags=NORMAL_CLONE, max_iterations=200, return_gpu=False):
    """AOT Seamless Cloning (Poisson Image Editing)."""
    is_gpu_src = isinstance(src, TaichiGPUBuffer)
    is_gpu_dst = isinstance(dst_img, TaichiGPUBuffer)
    src_buf = src if is_gpu_src else engine.upload(src)
    dst_buf = dst_img if is_gpu_dst else engine.upload(dst_img)
    # Override auto-detected is_vector for ndim=3 graphs
    if getattr(src_buf, 'is_vector', False):
        src_buf = src_buf.view_as_vector(False)
    if getattr(dst_buf, 'is_vector', False):
        dst_buf = dst_buf.view_as_vector(False)
    mask_buf = mask if isinstance(mask, TaichiGPUBuffer) else engine.upload(mask)
    h, w = dst_buf.shape[:2]

    # Copy destination to output (plain ndim=3, not vector)
    result = engine.allocate((h, w, 3))
    _mod("seamless_clone").run("seamless_copy_f32", s=dst_buf, d=result, h=h, w=w)

    # Grayscale source for MONOCHROME_TRANSFER
    if flags == MONOCHROME_TRANSFER:
        src_buf_copy = engine.allocate((h, w, 3))
        _mod("seamless_clone").run("seamless_copy_f32", s=src_buf, d=src_buf_copy, h=h, w=w)
        gray = engine.allocate((h, w))
        _mod("seamless_clone").run("seamless_to_grayscale_f32", s=src_buf_copy, g=gray, h=h, w=w)
        # Create 3ch grayscale source
        src_buf = engine.allocate((h, w, 3))
        for c in range(3):
            _mod("seamless_clone").run("seamless_init_f_channel_f32",
                                       dst_arr=src_buf, f_arr=gray, h=h, w=w, c=c)
        gray.destroy()
        src_buf_copy.destroy()

    # Solve per channel
    for ch in range(3):
        div_x = engine.allocate((h, w))
        div_y = engine.allocate((h, w))
        lap = engine.allocate((h, w))

        # Compute divergence
        if flags == MIXED_CLONE:
            _mod("seamless_clone").run("seamless_divergence_mixed_f32",
                                       src=src_buf, dst=result, div_x=div_x, div_y=div_y,
                                       h=h, w=w, ch=ch)
        else:
            _mod("seamless_clone").run("seamless_divergence_normal_f32",
                                       src=src_buf, div_x=div_x, div_y=div_y,
                                       h=h, w=w, ch=ch)

        # Compute Laplacian of divergence
        _mod("seamless_clone").run("seamless_laplacian_f32",
                                   div_x=div_x, div_y=div_y, lap=lap, h=h, w=w)

        # Initialize f from destination channel
        f_in = engine.allocate((h, w))
        f_out = engine.allocate((h, w))
        _mod("seamless_clone").run("seamless_init_f_channel_f32",
                                   dst_arr=result, f_arr=f_in, h=h, w=w, c=ch)

        # Jacobi iteration
        for _ in range(max_iterations):
            _mod("seamless_clone").run("seamless_jacobi_step_f32",
                                       f_in=f_in, f_out=f_out, lap=lap, mask=mask_buf,
                                       h=h, w=w)
            copy_field(f_out, f_in)

        # Composite
        _mod("seamless_clone").run("seamless_composite_f32",
                                   f=f_in, dst_out=result, mask=mask_buf,
                                   h=h, w=w, ch=ch)

        # Cleanup
        div_x.destroy()
        div_y.destroy()
        lap.destroy()
        f_in.destroy()
        f_out.destroy()

    return result if return_gpu else result.to_numpy()


# ---------------------------------------------------------------------------
# Farneback Optical Flow (AOT)
# ---------------------------------------------------------------------------

def farneback_flow(
    ref_gray,
    comp_gray,
    pyr_scale=0.5,
    num_levels=3,
    win_size=15,
    num_iters=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0,
    flow_init=None,
    return_gpu=False,
):
    """
    AOT Farneback Dense Optical Flow (OpenCV-compatible).

    Computes a dense flow field from ref_gray to comp_gray.

    Parameters
    ----------
    ref_gray  : ndarray (H, W) float32 – reference frame [0, 255].
    comp_gray : ndarray (H, W) float32 – comparison frame [0, 255].
    pyr_scale : float – pyramid scale factor (default 0.5).
    num_levels: int   – number of pyramid levels (default 3).
    win_size  : int   – smoothing window size (default 15).
    num_iters : int   – iterations per pyramid level (default 3).
    poly_n    : int   – polynomial expansion neighborhood (default 5).
    poly_sigma: float – polynomial expansion sigma (default 1.2).
    flags     : int   – reserved.
    flow_init : ndarray (H,W,2) or TaichiGPUBuffer – optional initial flow.
    return_gpu: bool  – if True, return TaichiGPUBuffer; else np.ndarray.

    Returns
    -------
    flow : (H, W, 2) float32 – flow field where flow[:,:,0]=dx, flow[:,:,1]=dy.
    """
    from taichi_library.taichi_algorithm.farneback_flow import (
        prepare_gaussian_constants,
        compute_smoothing_weights,
    )
    from taichi_library.taichi_algorithm.pyramid import build_image_pyramid_gpu

    # Upload images
    ref_buf = InputArray(ref_gray)
    comp_buf = InputArray(comp_gray)
    h_orig, w_orig = ref_buf.shape[:2]

    # Build pyramids
    downscale_factor = 1.0 / pyr_scale
    ref_pyr = build_image_pyramid_gpu(
        ref_buf, n_levels=num_levels, min_size=32,
        downscale_factor=downscale_factor,
    )
    comp_pyr = build_image_pyramid_gpu(
        comp_buf, n_levels=num_levels, min_size=32,
        downscale_factor=downscale_factor,
    )
    actual_levels = len(ref_pyr)

    # Pre-compute constants on CPU, upload to GPU
    g_w, xg_w, xxg_w, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(poly_n, poly_sigma)
    smooth_w, smooth_radius = compute_smoothing_weights(win_size)
    poly_radius = poly_n // 2

    g_gpu = InputArray(g_w)
    xg_gpu = InputArray(xg_w)
    xxg_gpu = InputArray(xxg_w)
    smooth_gpu = InputArray(smooth_w[:smooth_radius + 1])

    mod = _mod("farneback_flow")
    if mod is None:
        raise RuntimeError("farneback_flow TCM not found in aot_tcm/")

    # Coarse-to-fine
    prev_flow = None
    for lvl in range(actual_levels - 1, -1, -1):
        ref_lvl = ref_pyr[lvl]
        comp_lvl = comp_pyr[lvl]
        hl, wl = ref_lvl.shape[0], ref_lvl.shape[1]

        flow_buf = engine.allocate((hl, wl, 2), dtype=np.float32)

        if prev_flow is not None:
            scale_up = float(ref_lvl.shape[0]) / float(prev_flow.shape[0])
            mod.run("farneback_upsample_flow",
                    flow_coarse=prev_flow, flow_fine=flow_buf, scale=float(scale_up))
        else:
            mod.run("farneback_clear_flow", flow=flow_buf)

        # Polynomial expansion for both images
        vert_buf = engine.allocate((hl, wl, 3), dtype=np.float32)
        R0 = engine.allocate((hl, wl, 5), dtype=np.float32)
        R1 = engine.allocate((hl, wl, 5), dtype=np.float32)

        # Polynomial expansion: ref (writes to R0), comp (writes to R1)
        # poly_expansion_f32 graph: src -> vert (vertical) -> poly (horizontal)
        mod.run("poly_expansion_f32",
                src=ref_lvl, vert=vert_buf, poly=R0,
                h=hl, w=wl, g=g_gpu, xg=xg_gpu, xxg=xxg_gpu, poly_radius=poly_radius)
        mod.run("poly_expansion_f32",
                src=comp_lvl, vert=vert_buf, poly=R1,
                h=hl, w=wl, g=g_gpu, xg=xg_gpu, xxg=xxg_gpu, poly_radius=poly_radius)

        vert_buf.destroy()

        # Allocate tensor scratch buffers
        M = engine.allocate((hl, wl, 5), dtype=np.float32)
        M_smooth = engine.allocate((hl, wl, 5), dtype=np.float32)

        # Choose batched multi-iteration graph for efficiency
        iter_args = dict(R0=R0, R1=R1, flow=flow_buf, M=M, M_smooth=M_smooth,
                         h=hl, w=wl, smooth_weights=smooth_gpu,
                         smooth_radius=smooth_radius)

        remaining = num_iters
        while remaining > 0:
            if remaining >= 5:
                batch_key = "farneback_multi_5"
                batch_size = 5
            elif remaining >= 3:
                batch_key = "farneback_multi_3"
                batch_size = 3
            elif remaining >= 2:
                batch_key = "farneback_multi_2"
                batch_size = 2
            else:
                batch_key = "farneback_iteration"
                batch_size = 1
            try:
                mod.run(batch_key, **iter_args)
            except Exception:
                # Fallback to single iteration if batch graph not found
                mod.run("farneback_iteration", **iter_args)
            remaining -= batch_size

        R0.destroy()
        R1.destroy()
        M.destroy()
        M_smooth.destroy()

        if prev_flow is not None and lvl < actual_levels - 1:
            prev_flow.destroy()
        prev_flow = flow_buf

    engine.sync()
    result = prev_flow

    # Cleanup pyramid buffers (except level 0 which shares ref/comp_buf)
    for lvl_buf in ref_pyr[1:]:
        lvl_buf.destroy()
    for lvl_buf in comp_pyr[1:]:
        lvl_buf.destroy()
    for buf in (g_gpu, xg_gpu, xxg_gpu, smooth_gpu):
        try: buf.destroy()
        except Exception: pass

    return result if return_gpu else result.to_numpy()

# ===========================================================================
# AOT Dispatch: BM3D (Hybrid Fast Collaborative Denoising)
# ===========================================================================
def bm3d(src, sigma, block_size=8, search_radius=15,
         max_matches=16, lambda_3d=2.7, cycle_spins=1,
         return_gpu=False):
    """
    Taichi AOT BM3D Denoising (Hybrid Fast Collaborative Denoising).

    Self-contained — no external fallback. Handles edge cases internally.
    Supports: uint8, uint16, float32 | grayscale (H,W), RGB (H,W,3).

    Pipeline per spin:
      1. Zero output + weight_sum buffers
      2. Block matching (brute-force L2 + Top-K)
      3. 2D DCT hard thresholding per group
      4. Weighted overlap-add aggregation
      5. Normalize output
    """
    is_numpy = isinstance(src, np.ndarray)
    orig_dtype = src.dtype if is_numpy else np.float32

    # --- Auto-cast dtype ---
    if is_numpy and src.dtype == np.uint8:
        src = src.astype(np.float32) / 255.0
        sigma = float(sigma) / 255.0
    elif is_numpy and src.dtype == np.uint16:
        src = src.astype(np.float32) / 65535.0
        sigma = float(sigma) / 65535.0
    else:
        sigma = float(sigma)

    # --- Auto-repair: sanitize ---
    if is_numpy and src.dtype in (np.float32, np.float64):
        if np.any(np.isnan(src)) or np.any(np.isinf(src)):
            src = np.nan_to_num(src, nan=0.0, posinf=1.0, neginf=0.0).astype(np.float32)
    if is_numpy:
        src = np.ascontiguousarray(src, dtype=np.float32)
        src = np.clip(src, 0.0, 1.0)

    # --- Validate sigma ---
    if not np.isfinite(sigma) or sigma <= 0:
        if return_gpu:
            return InputArray(src) if is_numpy else src
        return src.copy() if is_numpy else src.to_numpy()

    # --- Handle multi-channel (RGB) ---
    if len(src.shape) == 3 and src.shape[2] == 3:
        h, w = src.shape[:2]
        result_np = np.zeros((h, w, 3), dtype=np.float32)
        for c in range(3):
            ch_np = np.ascontiguousarray(src[:, :, c], dtype=np.float32)
            result_np[:, :, c] = bm3d(
                ch_np, sigma, block_size=block_size,
                search_radius=search_radius, max_matches=max_matches,
                lambda_3d=lambda_3d, cycle_spins=cycle_spins,
                return_gpu=False)
        if orig_dtype == np.uint8:
            return np.clip(result_np * 255.0, 0, 255).astype(np.uint8)
        elif orig_dtype == np.uint16:
            return np.clip(result_np * 65535.0, 0, 65535).astype(np.uint16)
        return result_np

    # --- Single channel processing ---
    H, W = src.shape[:2]
    N = min(block_size, H, W)
    search_radius = min(search_radius, max(1, min(H, W) // 2))
    max_area = (2 * search_radius + 1) ** 2
    K = min(max_matches, max(1, max_area), 32)

    step = N
    ref_positions_list = []
    for ry in range(0, H - N + 1, step):
        for rx in range(0, W - N + 1, step):
            ref_positions_list.append((ry, rx))
    num_refs = len(ref_positions_list)

    if num_refs == 0:
        if return_gpu:
            return InputArray(src) if is_numpy else src
        return src.copy() if is_numpy else src.to_numpy()

    src_np = np.ascontiguousarray(src, dtype=np.float32)
    src_buf = InputArray(src_np)
    ref_pos_np = np.array(ref_positions_list, dtype=np.int32)
    ref_pos_buf = InputArray(ref_pos_np)

    from taichi_library.taichi_algorithm.bm3d import _get_dct_matrix
    T_np = _get_dct_matrix(N)
    T_buf = InputArray(T_np)

    groups_buf = OutputArray((num_refs, K, N, N), dtype=np.float32)
    match_y_buf = OutputArray((num_refs, K), dtype=np.int32)
    match_x_buf = OutputArray((num_refs, K), dtype=np.int32)
    valid_buf = OutputArray((num_refs, K), dtype=np.int32)
    filtered_buf = OutputArray((num_refs, K, N, N), dtype=np.float32)
    weights_buf = OutputArray((num_refs,), dtype=np.float32)
    temp_buf = OutputArray((num_refs, K, N, N), dtype=np.float32)
    output_buf = OutputArray((H, W), dtype=np.float32)
    wsum_buf = OutputArray((H, W), dtype=np.float32)
    final_buf = OutputArray((H, W), dtype=np.float32)

    mod = _mod("bm3d")
    mod.run("bm3d_zero_f32", dst=final_buf, H=H, W=W)

    for spin in range(cycle_spins):
        shift_x = (spin * N // 2) % W if spin > 0 else 0
        shift_y = (spin * N // 2) % H if spin > 0 else 0

        mod.run("bm3d_zero_f32", dst=output_buf, H=H, W=W)
        mod.run("bm3d_zero_f32", dst=wsum_buf, H=H, W=W)

        if shift_x != 0 or shift_y != 0:
            shifted_buf = OutputArray((H, W), dtype=np.float32)
            mod.run("bm3d_shift_f32", src=src_buf, dst=shifted_buf,
                    H=H, W=W, sy=shift_y, sx=shift_x)
            work_buf = shifted_buf
        else:
            work_buf = src_buf

        mod.run("bm3d_block_match_f32",
                src=work_buf, groups=groups_buf,
                match_y=match_y_buf, match_x=match_x_buf,
                valid_mask=valid_buf, ref_positions=ref_pos_buf,
                num_refs=num_refs, K=K, N=N,
                search_r=search_radius, H=H, W=W)

        mod.run("bm3d_dct_filter_f32",
                groups=groups_buf, filtered=filtered_buf,
                group_weights=weights_buf, T_dct=T_buf, temp_buf=temp_buf,
                num_refs=num_refs, K=K, N=N,
                sigma=sigma, lambda_3d=lambda_3d)

        mod.run("bm3d_aggregate_f32",
                filtered=filtered_buf, group_weights=weights_buf,
                match_y=match_y_buf, match_x=match_x_buf, valid_mask=valid_buf,
                output=output_buf, weight_sum=wsum_buf,
                num_refs=num_refs, K=K, N=N, H=H, W=W)

        mod.run("bm3d_normalize_f32",
                output=output_buf, weight_sum=wsum_buf,
                src=work_buf, H=H, W=W)

        if shift_x != 0 or shift_y != 0:
            unshifted_buf = OutputArray((H, W), dtype=np.float32)
            mod.run("bm3d_shift_f32", src=output_buf, dst=unshifted_buf,
                    H=H, W=W, sy=-shift_y, sx=-shift_x)
            mod.run("bm3d_accumulate_f32", dst=final_buf,
                    src=unshifted_buf, H=H, W=W)
            shifted_buf.destroy()
            unshifted_buf.destroy()
        else:
            mod.run("bm3d_accumulate_f32", dst=final_buf,
                    src=output_buf, H=H, W=W)

    if cycle_spins > 1:
        mod.run("bm3d_scale_f32", data=final_buf,
                scale=1.0 / cycle_spins, H=H, W=W)

    for buf in [groups_buf, match_y_buf, match_x_buf, valid_buf,
                filtered_buf, weights_buf, temp_buf, output_buf, wsum_buf]:
        buf.destroy()

    if return_gpu:
        return final_buf

    result = final_buf.to_numpy()
    if orig_dtype == np.uint8:
        return np.clip(result * 255.0, 0, 255).astype(np.uint8)
    elif orig_dtype == np.uint16:
        return np.clip(result * 65535.0, 0, 65535).astype(np.uint16)
    return result
