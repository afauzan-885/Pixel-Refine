import os
import sys
import numpy as np

# Path resolution to find the bridge
file_dir = os.path.dirname(os.path.abspath(__file__))

# Import the Generic AOT Engine and Buffer Pool
from .engine import AOTEngine, TaichiGPUBuffer

# Initialize the Singleton Engine
engine = AOTEngine()

# Preload TCM Modules (Handles architecture suffixes automatically)
_tcm_dir = os.path.abspath(os.path.join(file_dir, "../taichi_algorithm/aot_tcm"))

_bicubic_module = engine.load(os.path.join(_tcm_dir, "bicubic.tcm"))
_pyramid_module = engine.load(os.path.join(_tcm_dir, "pyramid.tcm"))
_box_filter_module = engine.load(os.path.join(_tcm_dir, "box_filter.tcm"))
_gaussian_module = engine.load(os.path.join(_tcm_dir, "gaussian.tcm"))
_fft_module = engine.load(os.path.join(_tcm_dir, "fft.tcm"))
_warp_module = engine.load(os.path.join(_tcm_dir, "warp.tcm"))
_gradients_module = engine.load(os.path.join(_tcm_dir, "gradients.tcm"))
_median_module = engine.load(os.path.join(_tcm_dir, "median_filter.tcm"))
_ncc_module = engine.load(os.path.join(_tcm_dir, "ncc.tcm"))
_ransac_module = engine.load(os.path.join(_tcm_dir, "ransac.tcm"))

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

def resize(src, dsize, interpolation=INTER_CUBIC, return_gpu=False):
    """Taichi AOT Resize (OpenCV Parity API)"""
    target_w, target_h = dsize
    if interpolation == INTER_CUBIC:
        is_gpu_input = isinstance(src, TaichiGPUBuffer)
        src_buf = src if is_gpu_input else engine.upload(src)
        # Bicubic expects Scalar 3D
        if src_buf.is_vec2: src_buf = src_buf.view_as_vector(False)
        
        is_3d = len(src_buf.shape) == 3
        graph_name = "bicubic_resize_f32_3d" if is_3d else "bicubic_resize_f32_2d"
        h_src, w_src = src_buf.shape[0], src_buf.shape[1]
        dst_shape = (target_h, target_w, src_buf.shape[2]) if is_3d else (target_h, target_w)
        dst_buf = engine.allocate(dst_shape)
        _bicubic_module.run(graph_name, src=src_buf, dst=dst_buf, h_src=h_src, w_src=w_src, h_dst=target_h, w_dst=target_w)
        return dst_buf if return_gpu else dst_buf.to_numpy()
    else:
        raise NotImplementedError("Only INTER_CUBIC is supported in AOT currently.")

def bicubic_interpolation(src, target_w, target_h, return_gpu=False):
    """Alias for resize(interpolation=INTER_CUBIC)"""
    return resize(src, (target_w, target_h), interpolation=INTER_CUBIC, return_gpu=return_gpu)

def box_filter(src, kernel_size=3, return_gpu=False):
    """AOT Implementation of Box Filter (Scalar 3D Optimized)"""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    h, w = src.shape[:2]
    radius = kernel_size // 2
    is_3d = len(src.shape) == 3
    
    src_buf = src if is_gpu else engine.upload(src)
    if src_buf.is_vec2: src_buf = src_buf.view_as_vector(False)
    
    dst_buf = engine.allocate(src_buf.shape)
    
    if kernel_size == 3:
        graph = "box_filter_fused_3x3_3ch_f32" if is_3d else "box_filter_3x3_f32"
        _box_filter_module.run(graph, src=src_buf, dst=dst_buf, h=h, w=w)
    else:
        tmp_buf = engine.allocate(src_buf.shape)
        graph = "box_filter_separable_generic_3ch_f32" if is_3d else "box_filter_separable_generic_f32"
        _box_filter_module.run(graph, src=src_buf, tmp=tmp_buf, dst=dst_buf, h=h, w=w, radius=radius)
    
    return dst_buf if return_gpu else dst_buf.to_numpy()

def gaussian_blur(src, sigma=1.0, kernel_size=None, return_gpu=False):
    """AOT Implementation of Gaussian Blur (Separable Scalar 3D)"""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    # Gaussian expects Scalar 3D
    if src_buf.is_vec2: src_buf = src_buf.view_as_vector(False)
    
    if kernel_size is None or kernel_size <= 0:
        kernel_size = int(np.ceil(3 * sigma)) * 2 + 1
    radius = kernel_size // 2
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3
    
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian import compute_gaussian_weights
    weights_np = compute_gaussian_weights(sigma, radius).astype(np.float32)
    weights_buf = engine.upload(weights_np)
    
    tmp_buf = engine.allocate(src_buf.shape)
    dst_buf = engine.allocate(src_buf.shape)
    
    suffix = "3ch_f32" if is_3d else "1ch_f32"
    _gaussian_module.run(f"gaussian_blur_x_{suffix}", src=src_buf, dst=tmp_buf, h=h, w=w, weights=weights_buf, radius=radius)
    _gaussian_module.run(f"gaussian_blur_y_{suffix}", src=tmp_buf, dst=dst_buf, h=h, w=w, weights=weights_buf, radius=radius)
    
    return dst_buf if return_gpu else dst_buf.to_numpy()

def image_pyramid(src, levels=4, return_gpu=False):
    """AOT Implementation of Image Pyramid (Downsampling)"""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    if src_buf.is_vec2: src_buf = src_buf.view_as_vector(False) # Pyramid uses Scalar 3D
    is_3d = len(src_buf.shape) == 3
    
    curr_buf = src_buf
    graph = "downsample_2x_3ch_f32" if is_3d else "downsample_2x_f32"
    
    for _ in range(levels):
        h, w = curr_buf.shape[0], curr_buf.shape[1]
        next_h, next_w = h // 2, w // 2
        if next_h < 1 or next_w < 1: break
        
        dst_shape = (next_h, next_w, src_buf.shape[2]) if is_3d else (next_h, next_w)
        dst_buf = engine.allocate(dst_shape)
        _pyramid_module.run(graph, src=curr_buf, dst=dst_buf)
        curr_buf = dst_buf
        
    return curr_buf if return_gpu else curr_buf.to_numpy()

def median_filter(src, kernel_size=3, return_gpu=False):
    """AOT Implementation of Median Filter (Fixed 3x3 currently)"""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    h, w = src.shape[:2]
    is_flow = (len(src.shape) == 3 and src.shape[2] == 2)
    
    src_buf = src if is_gpu else engine.upload(src, is_vector=is_flow)
    if is_flow and not src_buf.is_vec2:
        src_buf = src_buf.view_as_vector(True)
        
    dst_buf = engine.allocate(src_buf.shape, is_vector=is_flow)
    graph = "median_flow_3x3_f32" if is_flow else "median_3x3_f32"
    _median_module.run(graph, src=src_buf, dst=dst_buf, h=h, w=w)
    return dst_buf if return_gpu else dst_buf.to_numpy()

def _fft_1d_gpu(complex_buf, h, w, is_inverse, is_col):
    """Helper to run multi-pass 1D FFT on GPU."""
    n = h if is_col else w
    bits = (n - 1).bit_length()

    temp_buf = engine.allocate((h, w, 2), is_vector=True) # FFT uses vec2
    _fft_module.run("fft_bit_reverse_f32", src=complex_buf, dst=temp_buf, bits=bits, is_col=1 if is_col else 0)
    
    # Swap pointers
    complex_buf.handle, temp_buf.handle = temp_buf.handle, complex_buf.handle

    for stage in range(1, bits + 1):
        stage_len = 1 << stage
        _fft_module.run("fft_stage_f32", data=complex_buf, n=n, stage_len=stage_len, 
                        is_inverse=1 if is_inverse else 0, is_col=1 if is_col else 0)

    if is_inverse:
        _fft_module.run("fft_normalize_f32", data=complex_buf, scale=1.0 / n)

def fft2(src):
    """AOT Implementation of 2D FFT (Actual Butterfly)."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    
    complex_buf = engine.allocate((h, w, 2), is_vector=True)
    _fft_module.run("fft_real_to_complex_f32", src=src_buf, dst=complex_buf, h=h, w=w)
    _fft_1d_gpu(complex_buf, h, w, is_inverse=False, is_col=False)
    _fft_1d_gpu(complex_buf, h, w, is_inverse=False, is_col=True)
    return complex_buf

def ifft2(complex_buf):
    """AOT Implementation of 2D IFFT (Actual Butterfly)."""
    h, w = complex_buf.shape[:2]
    _fft_1d_gpu(complex_buf, h, w, is_inverse=True, is_col=True)
    _fft_1d_gpu(complex_buf, h, w, is_inverse=True, is_col=False)
    dst_buf = engine.allocate((h, w))
    _fft_module.run("fft_complex_to_real_f32", src=complex_buf, dst=dst_buf, h=h, w=w)
    return dst_buf

def sobel(src, return_gpu=False):
    """AOT Implementation of Sobel Edge Detection."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    dx_buf = engine.allocate((h, w))
    dy_buf = engine.allocate((h, w))
    _gradients_module.run("sobel_f32", src=src_buf, dst_dx=dx_buf, dst_dy=dy_buf, h=h, w=w)
    if return_gpu: return dx_buf, dy_buf
    return dx_buf.to_numpy(), dy_buf.to_numpy()

def laplacian(src, return_gpu=False):
    """AOT Implementation of Laplacian Edge Detection."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    dst_buf = engine.allocate((h, w))
    _gradients_module.run("laplacian_f32", src=src_buf, dst=dst_buf, h=h, w=w)
    return dst_buf if return_gpu else dst_buf.to_numpy()

def zncc(image, template, stride=1, return_gpu=False, stats_t=None):
    """Hybrid O(1) Stats + Spatial Correlation ZNCC (AOT)."""
    is_gpu_img = isinstance(image, TaichiGPUBuffer)
    is_gpu_temp = isinstance(template, TaichiGPUBuffer)
    img_buf = image if is_gpu_img else engine.upload(image)
    temp_buf = template if is_gpu_temp else engine.upload(template)
    h_img, w_img = img_buf.shape[:2]
    h_temp, w_temp = temp_buf.shape[:2]
    
    # Template stats
    sum_t, var_t_n = 0.0, 0.0
    n_pixels = float(h_temp * w_temp)
    if stats_t is not None:
        sum_t, var_t_n = stats_t
    else:
        temp_np = template if not is_gpu_temp else template.to_numpy()
        sum_t = float(np.sum(temp_np))
        var_t_n = float(max(0.0, np.sum(temp_np**2) - (sum_t**2 / n_pixels)))

    sum_h = engine.allocate((h_img, w_img))
    sq_sum_h = engine.allocate((h_img, w_img))
    sum_2d = engine.allocate((h_img, w_img))
    sq_sum_2d = engine.allocate((h_img, w_img))
    corr = engine.allocate((h_img, w_img))
    dst_h, dst_w = (h_img + stride - 1) // stride, (w_img + stride - 1) // stride
    dst_buf = engine.allocate((dst_h, dst_w))
    
    _ncc_module.run("zncc_map_f32", image=img_buf, template=temp_buf,
                    sum_h=sum_h, sq_sum_h=sq_sum_h, sum_2d=sum_2d, sq_sum_2d=sq_sum_2d,
                    corr=corr, dst=dst_buf, h_img=h_img, w_img=w_img, h_temp=h_temp, w_temp=w_temp,
                    sum_t=sum_t, var_t_n=var_t_n, n_pixels=n_pixels, stride=stride)
    
    return dst_buf if return_gpu else dst_buf.to_numpy()

def ransac_flow_cleanup(flow, threshold=3.0, n_iterations=5, return_gpu=False, return_model=False):
    """AOT Implementation of RANSAC Flow Cleanup"""
    is_gpu = isinstance(flow, TaichiGPUBuffer)
    flow_buf = flow if is_gpu else engine.upload(flow, is_vector=True) # Flow is vec2
    if not flow_buf.is_vec2: flow_buf = flow_buf.view_as_vector(True)
    
    h, w = flow_buf.shape[:2]
    mask_buf = engine.allocate((h, w), dtype=np.int32)
    model_buf = engine.allocate((2,))
    output_buf = engine.allocate((h, w), is_vector=True)
    
    _ransac_module.run("ransac_flow_cleanup_f32", flow=flow_buf, inlier_mask=mask_buf, model=model_buf, 
                       threshold=threshold, output=output_buf, h=h, w=w, stride_refine=4, stride_final=1)
    
    model_np = model_buf.to_numpy() if return_model else None
    if return_gpu:
        return (output_buf, model_np) if return_model else output_buf
    res = output_buf.to_numpy()
    return (res, model_np) if return_model else res
