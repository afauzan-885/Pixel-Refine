import os
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
from .engine import INTER_CUBIC, INTER_LINEAR, INTER_NEAREST, INTER_AREA
from .engine import COLOR_BGR2GRAY, COLOR_RGB2GRAY, COLOR_GRAY2BGR

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
    if name not in _module_cache:
        path_dir = os.path.join(_tcm_dir, name)
        if os.path.isdir(path_dir):
            _module_cache[name] = engine.load(path_dir)
        else:
            path_file = os.path.join(_tcm_dir, f"{name}.tcm")
            try:
                _module_cache[name] = engine.load(path_file)
            except Exception:
                _module_cache[name] = None
    return _module_cache[name]


def load_tcm(name):
    """Public helper for external callers (backward compat). Uses lazy cache."""
    return _mod(name)


def unload_all_modules():
    """Release all cached TCM modules. Call after heavy processing to free VRAM."""
    _module_cache.clear()
    engine.modules.clear()

# --- OpenCV-style Constants ---
INTER_NEAREST = 0
INTER_LINEAR = 1
INTER_CUBIC = 2
INTER_AREA = 3
INTER_LANCZOS4 = 4

# --- Core API ---


def upload(arr: np.ndarray, is_vector=False) -> TaichiGPUBuffer:
    """Upload a NumPy array to GPU VRAM."""
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


def rgb2gray(src):
    """AOT Optimized RGB to Gray conversion."""
    h, w = src.shape[0], src.shape[1]
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


def resize(src, dsize, interpolation=INTER_CUBIC, return_gpu=False):
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

    if is_3d:
        dst_shape = (target_h, target_w, v_dim)
    else:
        dst_shape = (target_h, target_w)

    dst_buf = OutputArray(
        dst_shape, dtype=src_buf.dtype, is_vector=is_vec, vector_dim=v_dim
    )

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

    return dst_buf if return_gpu else dst_buf.to_numpy()


def box_filter(src, kernel_size=3, return_gpu=False):
    """AOT Implementation of Box Filter."""
    src_buf = InputArray(src)
    h, w = src_buf.shape[:2]
    radius = kernel_size // 2
    is_3d = len(src_buf.shape) == 3

    dst_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_3d)
    is_vec = getattr(src_buf, "is_vector", False)

    if kernel_size == 3:
        target = (
            "box_filter_fused_3x3_vec3_f32"
            if is_vec
            else "box_filter_fused_3x3_3ch_f32"
        )
        _mod("box_filter").run(target, src=src_buf, dst=dst_buf, h=h, w=w)
    else:
        tmp_buf = engine.allocate(src_buf.shape, dtype=src_buf.dtype, is_vector=is_vec)
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

    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian import (
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

    del tmp_buf, weights_buf
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

            # 3. Insert back
            _mod("common").run("insert_channel_f32", src=temp_out, dst=dst_v, ch=c)

        del temp_ch, temp_out

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

    if src_cast is not src and hasattr(src_cast, "destroy"):
        src_cast.destroy()

    res = dst_buf if return_gpu else dst_buf.to_numpy()

    if orig_dtype is not None:
        if return_gpu:
            res_cast = res.cast(orig_dtype)
            res.destroy()
            res = res_cast
        else:
            if np.issubdtype(orig_dtype, np.integer):
                res = np.clip(res, np.iinfo(orig_dtype).min, np.iinfo(orig_dtype).max)
            res = res.astype(orig_dtype)

    return res


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
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian import (
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

    tmp_buf.destroy()
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

