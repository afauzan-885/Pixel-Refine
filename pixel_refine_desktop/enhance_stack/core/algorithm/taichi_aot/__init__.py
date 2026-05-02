import os
import sys
import numpy as np

# Path resolution to find the bridge
file_dir = os.path.dirname(os.path.abspath(__file__))

# Import the new Generic AOT Engine
from .engine import AOTEngine, TaichiGPUBuffer

# Initialize the Singleton Engine
engine = AOTEngine()

# Preload TCM Modules
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
INTER_CUBIC = 2  # Standard Bicubic
INTER_AREA = 3
INTER_LANCZOS4 = 4

# --- Type Aliases ---
GPUBuffer = TaichiGPUBuffer


def upload(arr: np.ndarray) -> TaichiGPUBuffer:
    """Upload a NumPy array to GPU VRAM."""
    return engine.upload(arr)


def resize(src, dsize, interpolation=INTER_CUBIC, return_gpu=False):
    """
    Taichi AOT Resize (OpenCV Parity API)

    Args:
        src: input image (np.ndarray or taichi_aot.GPUBuffer)
        dsize: tuple (width, height)
        interpolation: interpolation method (e.g., taichi_aot.INTER_CUBIC)
        return_gpu: if True, returns a GPUBuffer instead of np.ndarray

    Returns:
        Resized image (np.ndarray or GPUBuffer)
    """
    target_w, target_h = dsize

    if interpolation == INTER_CUBIC:
        is_gpu_input = isinstance(src, TaichiGPUBuffer)
        src_buf = src if is_gpu_input else engine.upload(src)

        # Determine 2D or 3D
        is_3d = len(src_buf.shape) == 3
        graph_name = "bicubic_resize_f32_3d" if is_3d else "bicubic_resize_f32_2d"

        # Determine shapes
        h_src, w_src = src_buf.shape[0], src_buf.shape[1]
        h_dst, w_dst = target_h, target_w

        dst_shape = (h_dst, w_dst, 3) if is_3d else (h_dst, w_dst)
        dst_buf = engine.allocate(dst_shape)

        # Execute via Generic AOT Engine
        _bicubic_module.run(
            graph_name,
            src=src_buf,
            dst=dst_buf,
            h_src=h_src,
            w_src=w_src,
            h_dst=h_dst,
            w_dst=w_dst,
        )

        return dst_buf if return_gpu else dst_buf.to_numpy()

    elif interpolation == INTER_LINEAR:
        # Placeholder for future expansion
        raise NotImplementedError("Bilinear AOT is coming soon!")
    else:
        raise ValueError(
            f"Interpolation mode {interpolation} is not supported in Taichi AOT yet."
        )


def sample_at(src, coords, return_gpu=False):
    """
    Sample image at fractional coordinates (Bicubic).
    Format parity with original library.

    Args:
        src: input image (np.ndarray or GPUBuffer)
        coords: coordinates to sample.
               Can be single [x, y] or array of shape (N, 2).
        return_gpu: if True, returns a GPUBuffer
    """
    coords = np.array(coords, dtype=np.float32)
    single_point = False

    if len(coords.shape) == 1:
        single_point = True
        coords = coords.reshape(1, 2)

    is_gpu_input = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu_input else engine.upload(src)

    # Upload coords
    coords_buf = engine.upload(coords)

    n_samples = coords.shape[0]
    is_3d = len(src_buf.shape) == 3
    graph_name = "bicubic_sample_f32_3d" if is_3d else "bicubic_sample_f32_2d"

    h_src, w_src = src_buf.shape[0], src_buf.shape[1]

    # Allocate results
    res_shape = (n_samples, 3) if is_3d else (n_samples,)
    res_buf = engine.allocate(res_shape)

    # Execute via Generic AOT Engine
    _bicubic_module.run(
        graph_name,
        src=src_buf,
        coords=coords_buf,
        results=res_buf,
        n_samples=n_samples,
        h_src=h_src,
        w_src=w_src,
    )

    if return_gpu:
        return res_buf
    else:
        out_np = res_buf.to_numpy()
        return out_np[0] if single_point else out_np


def build_image_pyramid(image, n_levels=4, min_size=32, return_gpu=False):
    """
    AOT Implementation of Image Pyramid.
    Uses cascaded 2x downsampling for maximum quality.

    Args:
        image: np.ndarray or TaichiGPUBuffer (shape H, W)
        n_levels: Total levels including original.
        return_gpu: If True, returns a list of TaichiGPUBuffer.
    """
    is_gpu_input = isinstance(image, TaichiGPUBuffer)
    current_buf = image if is_gpu_input else engine.upload(image)

    pyramid = [current_buf]

    for i in range(n_levels - 1):
        prev = pyramid[-1]
        h_src, w_src = prev.shape[0], prev.shape[1]

        # Next level size
        h_dst, w_dst = h_src // 2, w_src // 2

        if h_dst < min_size or w_dst < min_size:
            break

        # Allocate destination
        is_3d = len(prev.shape) == 3
        if is_3d:
            c = prev.shape[2]
            dst_buf = engine.allocate((h_dst, w_dst, c))
            _pyramid_module.run("downsample_2x_3ch_f32", src=prev, dst=dst_buf)
        else:
            dst_buf = engine.allocate((h_dst, w_dst))
            _pyramid_module.run("downsample_2x_f32", src=prev, dst=dst_buf)

        pyramid.append(dst_buf)

    if return_gpu:
        return pyramid
    else:
        return [level.to_numpy() for level in pyramid]


def box_filter(src, kernel_size=3, return_gpu=False):
    """
    AOT Implementation of Box Filter (mean blur).
    """
    is_gpu_input = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu_input else engine.upload(src)

    h_src, w_src = src_buf.shape[0], src_buf.shape[1]
    radius = kernel_size // 2

    # 2D, 3D, or Flow Box Filter based on shape
    is_3d = len(src_buf.shape) == 3
    if is_3d:
        c_count = src_buf.shape[2]
        dst_buf = engine.allocate((h_src, w_src, c_count))
        if c_count == 2:
            graph_name = "box_filter_flow_f32"
            _box_filter_module.run(
                graph_name, src=src_buf, dst=dst_buf, h=h_src, w=w_src, radius=radius
            )
        else:
            graph_name = "box_filter_3d_f32"
            _box_filter_module.run(
                graph_name,
                src=src_buf,
                dst=dst_buf,
                h=h_src,
                w=w_src,
                radius=radius,
                c=c_count,
            )
    else:
        dst_buf = engine.allocate((h_src, w_src))
        graph_name = "box_filter_2d_f32"
        _box_filter_module.run(
            graph_name, src=src_buf, dst=dst_buf, h=h_src, w=w_src, radius=radius
        )

    if return_gpu:
        return dst_buf
    else:
        return dst_buf.to_numpy()


def gaussian_blur(src, sigma=1.0, kernel_size=None, return_gpu=False):
    """
    AOT Implementation of Gaussian Blur (Separable 1D + 1D).
    """
    is_gpu_input = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu_input else engine.upload(src)

    if sigma <= 0 and kernel_size is not None:
        sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8
        if sigma <= 0:
            sigma = 1.0

    if kernel_size is None or kernel_size <= 0:
        radius = int(np.ceil(3 * sigma))
        kernel_size = 2 * radius + 1
    else:
        radius = kernel_size // 2

    if radius < 1:
        return src_buf if return_gpu else src_buf.to_numpy()

    h_src, w_src = src_buf.shape[0], src_buf.shape[1]
    is_3d = len(src_buf.shape) == 3

    # Needs intermediate buffer for separable convolution
    shape = src_buf.shape
    temp_buf = engine.allocate(shape)
    dst_buf = engine.allocate(shape)

    # Compute weights
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian import (
        compute_gaussian_weights,
    )

    weights_np = compute_gaussian_weights(sigma, radius).astype(np.float32)
    weights_buf = engine.upload(weights_np)

    if not is_3d or src_buf.shape[2] == 1:
        _gaussian_module.run(
            "gaussian_blur_x_1ch_f32",
            src=src_buf,
            dst=temp_buf,
            h=h_src,
            w=w_src,
            weights=weights_buf,
            radius=radius,
        )
        _gaussian_module.run(
            "gaussian_blur_y_1ch_f32",
            src=temp_buf,
            dst=dst_buf,
            h=h_src,
            w=w_src,
            weights=weights_buf,
            radius=radius,
        )
    else:
        _gaussian_module.run(
            "gaussian_blur_x_3ch_f32",
            src=src_buf,
            dst=temp_buf,
            h=h_src,
            w=w_src,
            weights=weights_buf,
            radius=radius,
        )
        _gaussian_module.run(
            "gaussian_blur_y_3ch_f32",
            src=temp_buf,
            dst=dst_buf,
            h=h_src,
            w=w_src,
            weights=weights_buf,
            radius=radius,
        )

    if return_gpu:
        return dst_buf
    else:
        return dst_buf.to_numpy()


def fft2(src):
    """
    AOT Implementation of 2D Fast Fourier Transform.
    Automatically pads to next power of two if needed.
    """
    is_gpu_input = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu_input else engine.upload(src)

    h, w = src_buf.shape[:2]

    # Power of two
    target_h = 1 << (h - 1).bit_length()
    target_w = 1 << (w - 1).bit_length()

    # Allocate Complex Buffer (vec2)
    # The AOT engine expects a 2D array of vec2, so we pass shape=(target_h, target_w) and is_vec2=True
    complex_buf = engine.allocate((target_h, target_w), is_vec2=True)

    # Real to Complex
    _fft_module.run("fft_real_to_complex_f32", src=src_buf, dst=complex_buf, h=h, w=w)

    # FFT 1D (Row)
    _fft_1d_gpu(complex_buf, target_h, target_w, is_inverse=False, is_col=False)
    # FFT 1D (Col)
    _fft_1d_gpu(complex_buf, target_h, target_w, is_inverse=False, is_col=True)

    return complex_buf


def ifft2(complex_buf, target_shape=None):
    """
    AOT Implementation of Inverse 2D Fast Fourier Transform.
    Returns a real field.
    """
    h, w = complex_buf.shape[:2]

    # IFFT 1D (Col)
    _fft_1d_gpu(complex_buf, h, w, is_inverse=True, is_col=True)
    # IFFT 1D (Row)
    _fft_1d_gpu(complex_buf, h, w, is_inverse=True, is_col=False)

    out_h, out_w = target_shape if target_shape else (h, w)
    res_buf = engine.allocate((out_h, out_w))

    _fft_module.run(
        "fft_complex_to_real_f32", src=complex_buf, dst=res_buf, h=out_h, w=out_w
    )
    return res_buf


def _fft_1d_gpu(complex_buf, h, w, is_inverse, is_col):
    n = h if is_col else w
    bits = (n - 1).bit_length()

    # Bit Reversal
    temp_buf = engine.allocate((h, w), is_vec2=True)
    _fft_module.run(
        "fft_bit_reverse_f32",
        src=complex_buf,
        dst=temp_buf,
        bits=bits,
        is_col=1 if is_col else 0,
    )

    # Copy back (Wait, AOT doesn't have a direct copy graph, but we can reuse the engine logic or swap buffers!)
    # Actually, Taichi graphs don't easily let you swap pointers in Python to emulate copy unless we use the GPU pointer.
    # To keep it simple, we just swap the python wrapper properties or we run a small copy!
    # Wait, in C-API, we can't swap easily if it expects complex_buf to be the input.
    # But wait! I can just reassign the handle inside the Python object!
    # SWAP pointers!
    complex_buf.handle, temp_buf.handle = temp_buf.handle, complex_buf.handle
    # Now complex_buf points to the bit-reversed data!

    # Butterfly Stages
    for stage in range(1, bits + 1):
        stage_len = 1 << stage
        _fft_module.run(
            "fft_stage_f32",
            data=complex_buf,
            n=n,
            stage_len=stage_len,
            is_inverse=1 if is_inverse else 0,
            is_col=1 if is_col else 0,
        )

    if is_inverse:
        _fft_module.run("fft_normalize_f32", data=complex_buf, scale=1.0 / n)


def warp_image(src, flow, ref=None, return_gpu=False):
    """
    AOT Implementation of Image Warping.
    Supports both 1-channel and 3-channel input images.
    Input image and reference image must be int32 (0-65535 range).
    """
    is_gpu_src = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu_src else engine.upload(src)

    is_gpu_flow = isinstance(flow, TaichiGPUBuffer)
    flow_buf = flow if is_gpu_flow else engine.upload(flow, is_vec2=True)

    # Determine channels
    is_3d = len(src_buf.shape) == 3
    if is_3d:
        h, w = src_buf.shape[:2]
        c = src_buf.shape[2]
        dst_buf = engine.allocate((h, w, c), dtype=np.int32)
    else:
        h, w = src_buf.shape[:2]
        dst_buf = engine.allocate((h, w), dtype=np.int32)

    if ref is not None:
        is_gpu_ref = isinstance(ref, TaichiGPUBuffer)
        ref_buf = ref if is_gpu_ref else engine.upload(ref)
        if is_3d:
            _warp_module.run(
                "warp_guided_i32_3ch",
                src=src_buf,
                flow=flow_buf,
                dst=dst_buf,
                ref=ref_buf,
            )
        else:
            _warp_module.run(
                "warp_guided_i32_1ch",
                src=src_buf,
                flow=flow_buf,
                dst=dst_buf,
                ref=ref_buf,
            )
    else:
        if is_3d:
            _warp_module.run(
                "warp_naked_i32_3ch", src=src_buf, flow=flow_buf, dst=dst_buf
            )
        else:
            _warp_module.run(
                "warp_naked_i32_1ch", src=src_buf, flow=flow_buf, dst=dst_buf
            )

    if return_gpu:
        return dst_buf
    return dst_buf.to_numpy()


def sobel(src, return_gpu=False):
    """
    AOT Implementation of Sobel Edge Detection.
    Returns dx, dy GPU buffers or numpy arrays.
    """
    is_gpu_input = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu_input else engine.upload(src)

    h, w = src_buf.shape[:2]
    dx_buf = engine.allocate((h, w))
    dy_buf = engine.allocate((h, w))

    _gradients_module.run(
        "sobel_f32", src=src_buf, dst_dx=dx_buf, dst_dy=dy_buf, h=h, w=w
    )

    if return_gpu:
        return dx_buf, dy_buf
    return dx_buf.to_numpy(), dy_buf.to_numpy()


def laplacian(src, return_gpu=False):
    """
    AOT Implementation of Laplacian Edge Detection.
    """
    is_gpu_input = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu_input else engine.upload(src)

    h, w = src_buf.shape[:2]
    dst_buf = engine.allocate((h, w))

    _gradients_module.run("laplacian_f32", src=src_buf, dst=dst_buf, h=h, w=w)

    if return_gpu:
        return dst_buf
    return dst_buf.to_numpy()


def median_filter(src, return_gpu=False):
    """AOT Implementation of 3x3 Median Filter."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]

    is_flow = (len(src_buf.shape) == 3 and src_buf.shape[2] == 2) or getattr(
        src_buf, "is_vec2", False
    )
    if is_flow:
        # Re-upload with is_vec2=True if it was a plain numpy array
        if not is_gpu:
            src_buf = engine.upload(src, is_vec2=True)
        dst_buf = engine.allocate((h, w), is_vec2=True)
        _median_module.run("median_flow_3x3_f32", src=src_buf, dst=dst_buf, h=h, w=w)
    else:
        dst_buf = engine.allocate((h, w))
        _median_module.run("median_3x3_f32", src=src_buf, dst=dst_buf, h=h, w=w)

    if return_gpu:
        return dst_buf
    return dst_buf.to_numpy()


def zncc(image, template, stride=1, return_gpu=False, stats_t=None):
    """Hybrid O(1) Stats + Spatial Correlation ZNCC (AOT) with Stride support."""
    is_gpu_img = isinstance(image, TaichiGPUBuffer)
    is_gpu_temp = isinstance(template, TaichiGPUBuffer)
    
    img_buf = image if is_gpu_img else engine.upload(image)
    temp_buf = template if is_gpu_temp else engine.upload(template)
    
    h_img, w_img = img_buf.shape[:2]
    h_temp, w_temp = temp_buf.shape[:2]
    
    # 1. Get template stats (Avoid sync if possible)
    sum_t, var_t_n, n_pixels = 0.0, 0.0, float(h_temp * w_temp)
    if stats_t is not None:
        sum_t, var_t_n = stats_t
    else:
        temp_np = template if not is_gpu_temp else template.to_numpy()
        sum_t = float(np.sum(temp_np))
        sum_sq_t = float(np.sum(temp_np**2))
        var_t_n = float(max(0.0, sum_sq_t - (sum_t**2 / n_pixels)))

    # Output dimensions based on stride
    res_h = (h_img - h_temp) // stride + 1
    res_w = (w_img - w_temp) // stride + 1
    
    # 2. Allocate buffers (Pooled)
    dst_buf = engine.allocate((res_h, res_w))
    corr_buf = engine.allocate((res_h, res_w))
    sum_h = engine.allocate((h_img, w_img))
    sq_sum_h = engine.allocate((h_img, w_img))
    sum_2d = engine.allocate((h_img, w_img))
    sq_sum_2d = engine.allocate((h_img, w_img))

    # 3. Run the hybrid 4-pass graph
    _ncc_module.run(
        "zncc_map_f32",
        image=img_buf,
        template=temp_buf,
        sum_h=sum_h,
        sq_sum_h=sq_sum_h,
        sum_2d=sum_2d,
        sq_sum_2d=sq_sum_2d,
        corr=corr_buf,
        dst=dst_buf,
        h_img=h_img,
        w_img=w_img,
        h_temp=h_temp,
        w_temp=w_temp,
        sum_t=sum_t,
        var_t_n=var_t_n,
        n_pixels=n_pixels,
        stride=int(stride)
    )

    if return_gpu:
        return dst_buf
    
    return dst_buf.to_numpy()


def ransac(data, threshold=3.0, n_iterations=5, model_type="translation", return_gpu=False, return_model=False):
    """
    Unified RANSAC API for Taichi AOT.
    Currently supports: 'translation' for flow fields.
    """
    if model_type != "translation":
        raise NotImplementedError(f"Model {model_type} not implemented yet in AOT.")

    # Auto-detect input: Flow field (H, W, 2)
    h, w = data.shape[:2]
    
    # Allocate necessary temporary buffers in VRAM
    mask_buf = engine.allocate((h, w), dtype=np.int32)
    model_buf = engine.allocate((2,))
    output_buf = engine.allocate((h, w), is_vec2=True)

    # Dispatch the Fused Graph (Zero PCIe sync during iterations!)
    _ransac_module.run(
        "ransac_flow_cleanup_f32",
        flow=data,
        inlier_mask=mask_buf,
        model=model_buf,
        threshold=threshold,
        output=output_buf,
        h=h,
        w=w,
        stride_refine=4,
        stride_final=1
    )

    model_np = None
    if return_model:
        model_np = model_buf.to_numpy()

    # Clean up intermediate buffers
    # (In a real scenario, we'd use get_temp_buffer to avoid re-allocating)
    
    if return_gpu:
        if return_model:
            return output_buf, model_np
        return output_buf
    
    res = output_buf.to_numpy()
    if return_model:
        return res, model_np
    return res


def ransac_flow_cleanup(flow, threshold=3.0, n_iterations=5, return_gpu=False, return_model=False):
    """Legacy wrapper for RANSAC Flow Cleanup, now using the fused GPU graph."""
    is_gpu = isinstance(flow, TaichiGPUBuffer)
    flow_buf = flow if is_gpu else engine.upload(flow, is_vec2=True)
    
    return ransac(
        data=flow_buf,
        threshold=threshold,
        n_iterations=n_iterations,
        model_type="translation",
        return_gpu=return_gpu,
        return_model=return_model
    )


print(
    f"[TaichiAOT] Generic API initialized (Arch: {engine._active_arch.upper()}, Modules: Bicubic, Pyramid, Box Filter, Gaussian, FFT, Warp, Gradients, Median, NCC, RANSAC)."
)
