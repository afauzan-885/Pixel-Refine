import os
import sys
import numpy as np

# Path resolution to find the bridge
file_dir = os.path.dirname(os.path.abspath(__file__))

# Import the Generic AOT Engine and Buffer Pool
from .engine import AOTEngine, TaichiGPUBuffer

# Initialize the Singleton Engine
engine = AOTEngine()

# Preload TCM Modules
_tcm_dir = os.path.abspath(os.path.join(file_dir, "../taichi_algorithm/aot_tcm"))

def load_tcm(name):
    return engine.load(os.path.join(_tcm_dir, f"{name}.tcm"))

_bicubic_module = load_tcm("bicubic")
_pyramid_module = load_tcm("pyramid")
_box_filter_module = load_tcm("box_filter")
_gaussian_module = load_tcm("gaussian")
_fft_module = load_tcm("fft")
_warp_module = load_tcm("warp")
_gradients_module = load_tcm("gradients")
_median_module = load_tcm("median_filter")
_ncc_module = load_tcm("ncc")
_ransac_module = load_tcm("ransac")
_common_module = load_tcm("common")

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
    if src.dtype == np.float32: 
        graph = "copy_f32_2d"
    elif is_3ch:
        graph = "copy_vec3_2d"
    
    src_v, dst_v = src, dst
    if is_3ch:
        if not getattr(src, 'is_vec3', False): src_v = src.view_as_vector(True)
        if not getattr(dst, 'is_vec3', False): dst_v = dst.view_as_vector(True)
        
    _common_module.run(graph, src=src_v, dst=dst_v)

def extract_channel(src, ch):
    """AOT Optimized channel extraction."""
    h, w = src.shape[0], src.shape[1]
    dst = engine.allocate((h, w), dtype=np.int32)
    src_v = src
    if len(src.shape) == 3 and not getattr(src, 'is_vec3', False):
        src_v = src.view_as_vector(True)
    _common_module.run("extract_channel_i32", src=src_v, dst=dst, ch=int(ch))
    return dst

def split_3ch(src):
    """Fused 3-channel split."""
    h, w = src.shape[0], src.shape[1]
    c0 = engine.allocate((h, w), dtype=np.int32)
    c1 = engine.allocate((h, w), dtype=np.int32)
    c2 = engine.allocate((h, w), dtype=np.int32)
    src_v = src
    if not getattr(src, 'is_vec3', False): src_v = src.view_as_vector(True)
    _common_module.run("split_3ch_i32", src=src_v, c0=c0, c1=c1, c2=c2)
    return [c0, c1, c2]

def merge_3ch(c0, c1, c2):
    """Fused 3-channel merge."""
    h, w = c0.shape[0], c0.shape[1]
    dst = engine.allocate((h, w, 3), dtype=np.int32, is_vector=True)
    _common_module.run("merge_3ch_i32", c0=c0, c1=c1, c2=c2, dst=dst)
    return dst

def rgb2gray(src):
    """AOT Optimized RGB to Gray conversion."""
    h, w = src.shape[0], src.shape[1]
    dst = engine.allocate((h, w), dtype=np.int32)
    src_v = src
    if len(src.shape) == 3 and not getattr(src, 'is_vec3', False):
        src_v = src.view_as_vector(True)
    _common_module.run("rgb2gray_i32", src=src_v, dst=dst)
    return dst

def absdiff(src1, src2):
    """AOT Optimized absolute difference."""
    dst = engine.allocate(src1.shape, dtype=src1.dtype)
    _common_module.run("absdiff_i32_2d", src=src1, src2=src2, dst=dst)
    return dst

# -------------------------------------------------------------------------
# Algorithm APIs
# -------------------------------------------------------------------------

def resize(src, dsize, interpolation=INTER_CUBIC, return_gpu=False):
    """Taichi AOT Resize (OpenCV Parity API)"""
    target_w, target_h = dsize
    if interpolation == INTER_CUBIC:
        is_gpu_input = isinstance(src, TaichiGPUBuffer)
        src_buf = src if is_gpu_input else engine.upload(src)
        if getattr(src_buf, 'is_vec3', False): src_buf = src_buf.view_as_vector(False)
        
        is_3d = len(src_buf.shape) == 3
        graph_name = "bicubic_resize_f32_3d" if is_3d else "bicubic_resize_f32_2d"
        h_src, w_src = src_buf.shape[0], src_buf.shape[1]
        dst_shape = (target_h, target_w, src_buf.shape[2]) if is_3d else (target_h, target_w)
        dst_buf = engine.allocate(dst_shape)
        _bicubic_module.run(graph_name, src=src_buf, dst=dst_buf, h_src=h_src, w_src=w_src, h_dst=target_h, w_dst=target_w)
        return dst_buf if return_gpu else dst_buf.to_numpy()
    else:
        raise NotImplementedError("Only INTER_CUBIC is supported in AOT currently.")

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
    _ncc_module.run("integral_row_scan", src=img_buf, sum_h=s_h, sq_sum_h=sq_h, h=h_img, w=w_img)
    _ncc_module.run("integral_col_scan", sum_h=s_h, sq_sum_h=sq_h, sum_2d=s_2d, sq_sum_2d=sq_2d, h=h_img, w=w_img)
    del s_h, sq_h
    temp_np = temp_buf.to_numpy() if is_gpu_temp else template
    sum_t = float(np.sum(temp_np))
    n = float(h_temp * w_temp)
    var_t_n = float(max(0.0, np.sum(temp_np**2) - (sum_t**2 / n)))
    res_h, res_w = (h_img - h_temp) // stride + 1, (w_img - w_temp) // stride + 1
    dst = engine.allocate((res_h, res_w))
    _ncc_module.run("zncc_spatial", src=img_buf, template=temp_buf, sum_2d=s_2d, sq_sum_2d=sq_2d,
                    dst=dst, sum_t=sum_t, var_t_n=var_t_n, n_float=n, stride=stride)
    res = dst if return_gpu else dst.to_numpy()
    del s_2d, sq_2d, dst
    return res

def warp_image(image, flow, ref=None, return_gpu=False):
    """Ultra-Extreme AOT Warping Pipeline."""
    is_gpu_src = isinstance(image, TaichiGPUBuffer)
    is_gpu_flow = isinstance(flow, TaichiGPUBuffer)
    is_gpu_ref = isinstance(ref, TaichiGPUBuffer)
    src_buf = image if is_gpu_src else engine.upload(image, is_vector=True)
    flow_buf = flow if is_gpu_flow else engine.upload(flow, is_vector=True)
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3
    dst_buf = engine.allocate(src_buf.shape, dtype=np.int32, is_vector=is_3d)
    if ref is not None:
        ref_buf = ref if is_gpu_ref else engine.upload(ref, is_vector=is_3d)
        if is_3d:
            ref_g = engine.allocate((h, w), dtype=np.int32)
            ref_buf_v = ref_buf.view_as_vector(False) if ref_buf.is_vec3 else ref_buf
            _warp_module.run("extract_green_i32", src=ref_buf_v, dst=ref_g)
            ref_arg = ref_g
        else:
            ref_arg = ref_buf
        graph = "warp_guided_i32_3ch" if is_3d else "warp_guided_i32_1ch"
        _warp_module.run(graph, src=src_buf, flow=flow_buf, dst=dst_buf, ref=ref_arg)
        if is_3d: del ref_g
    else:
        graph = "warp_naked_i32_3ch" if is_3d else "warp_naked_i32_1ch"
        _warp_module.run(graph, src=src_buf, flow=flow_buf, dst=dst_buf)
    res = dst_buf if return_gpu else dst_buf.to_numpy()
    if not is_gpu_src: del src_buf
    if not is_gpu_flow: del flow_buf
    return res

def median_filter(src, return_gpu=False):
    """AOT Median Filter 3x3."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    dst_buf = engine.allocate(src_buf.shape)
    _median_module.run("median_3x3", src=src_buf, dst=dst_buf)
    return dst_buf if return_gpu else dst_buf.to_numpy()
