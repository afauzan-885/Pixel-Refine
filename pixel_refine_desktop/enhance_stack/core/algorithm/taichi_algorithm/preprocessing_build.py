"""
Preprocessing Build - Modular Taichi GPU Implementation
=======================================================
Modular GPU-accelerated preprocessing functions matching CPU API.

Functions:
- normalize_image_gpu: Normalize u16/u8/f32 to [0,1] float32
- to_gamma_proxy_gpu: Linear → Gamma conversion (BT.709)
- preprocess_in_python_gpu: Extract green + optional contrast reduction
- preprocess_pipeline_gpu: Unified pipeline with minimal transfers

Usage Examples:
    # Individual functions
    normalized = normalize_image_gpu(image_u16)
    gamma = to_gamma_proxy_gpu(normalized, scale=1.0)
    gray = preprocess_in_python_gpu(gamma, use_sharpen=True)
    
    # Unified pipeline (optimized)
    result = preprocess_pipeline_gpu(
        image_u16,
        normalize=True,
        apply_gamma=True,
        extract_green=True,
    )
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from . import common

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None
    common = None


# ============================================================================
# Normalization Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _normalize_kernel_2d(
        src: ti.types.ndarray(ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: int,
        w: int,
        scale: float,
    ):
        """Normalize grayscale (2D) to RGB (3D) float32."""
        for y, x in ti.ndrange(h, w):
            val = float(src[y, x]) / scale
            dst[y, x, 0] = val
            dst[y, x, 1] = val
            dst[y, x, 2] = val

    @ti.kernel
    def _normalize_kernel_3d(
        src: ti.types.ndarray(ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: int,
        w: int,
        scale: float,
    ):
        """Normalize RGB (3D) to float32."""
        for y, x in ti.ndrange(h, w):
            for c in ti.static(range(3)):
                dst[y, x, c] = float(src[y, x, c]) / scale


def normalize_image_gpu(image, dtype=None, out=None, buffer_provider="pool"):
    """
    GPU version of normalize_image.
    Normalize image to range [0, 1] float32.
    
    Args:
        image: Input array (numpy or taichi), grayscale (2D) or RGB (3D)
        dtype: Original dtype (auto-detected if None)
        out: Optional output buffer (GPU or will be created)
        buffer_provider: Buffer pool provider
    
    Returns:
        ti.ndarray (GPU buffer) with shape (H, W, 3) and dtype float32
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Auto-detect dtype
    if dtype is None:
        dtype = getattr(image, "dtype", np.float32)

    # Determine scale
    if np.issubdtype(dtype, np.integer):
        scale = float(np.iinfo(dtype).max)
    elif np.issubdtype(dtype, np.floating):
        scale = 1.0
    else:
        raise TypeError(f"Unsupported dtype for normalization: {dtype}")

    # Upload to GPU if needed
    src_gpu, src_is_temp = common.ensure_taichi_field(
        image, buffer_provider=buffer_provider
    )

    h, w = src_gpu.shape[:2]
    is_grayscale = len(src_gpu.shape) == 2

    # Create output buffer
    if out is None:
        dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32, buffer_provider)
    else:
        dst_gpu = out

    # Run normalization kernel
    if is_grayscale:
        _normalize_kernel_2d(src_gpu, dst_gpu, h, w, scale)
    else:
        _normalize_kernel_3d(src_gpu, dst_gpu, h, w, scale)

    # Cleanup
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return dst_gpu


# ============================================================================
# Gamma Conversion Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _gamma_kernel_2d(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: int,
        w: int,
        scale: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
    ):
        """Apply gamma curve to grayscale image."""
        for y, x in ti.ndrange(h, w):
            val = tm.clamp(src[y, x] * scale, 0.0, 1.0)
            if val < cutoff:
                dst[y, x] = val * slope
            else:
                dst[y, x] = 1.099 * tm.pow(val, 1.0 / gamma_pow) - 0.099

    @ti.kernel
    def _gamma_kernel_3d(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: int,
        w: int,
        scale: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
    ):
        """Apply gamma curve to RGB image."""
        for y, x in ti.ndrange(h, w):
            for c in ti.static(range(3)):
                val = tm.clamp(src[y, x, c] * scale, 0.0, 1.0)
                if val < cutoff:
                    dst[y, x, c] = val * slope
                else:
                    dst[y, x, c] = 1.099 * tm.pow(val, 1.0 / gamma_pow) - 0.099


def to_gamma_proxy_gpu(
    linear_img,
    scale=1.0,
    gamma_pow=2.22,
    slope=4.5,
    cutoff=0.018,
    out=None,
    buffer_provider="pool",
):
    """
    GPU version of to_gamma_proxy.
    Convert Linear [0,1] to Gamma Proxy [0,1] for alignment.
    
    Args:
        linear_img: Input linear image (GPU buffer or numpy)
        scale: Exposure scaling factor
        gamma_pow: Gamma power (default 2.22 for BT.709)
        slope: Linear slope for dark values
        cutoff: Transition point between linear and gamma
        out: Optional output buffer
        buffer_provider: Buffer pool provider
    
    Returns:
        ti.ndarray (GPU buffer) with gamma-corrected values
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Upload to GPU if needed
    src_gpu, src_is_temp = common.ensure_taichi_field(
        linear_img, dtype=ti.f32, buffer_provider=buffer_provider
    )

    h, w = src_gpu.shape[:2]
    is_grayscale = len(src_gpu.shape) == 2

    # Create output buffer
    if out is None:
        shape = (h, w) if is_grayscale else (h, w, 3)
        dst_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)
    else:
        dst_gpu = out

    # Run gamma kernel
    if is_grayscale:
        _gamma_kernel_2d(
            src_gpu, dst_gpu, h, w, scale, gamma_pow, slope, cutoff
        )
    else:
        _gamma_kernel_3d(
            src_gpu, dst_gpu, h, w, scale, gamma_pow, slope, cutoff
        )

    # Cleanup
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return dst_gpu


# ============================================================================
# Preprocessing (Green Extraction + Sharpen) Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _extract_green_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: int,
        w: int,
        use_sharpen: int,
    ):
        """Extract green channel with optional contrast reduction."""
        for y, x in ti.ndrange(h, w):
            gray = src[y, x, 1]  # Green channel (index 1)

            if use_sharpen:
                # 30% contrast reduction: (pixel - 0.5) * 0.7 + 0.5
                gray = (gray - 0.5) * 0.7 + 0.5

            dst[y, x] = tm.clamp(gray, 0.0, 1.0)

    @ti.kernel
    def _extract_green_kernel_2d(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: int,
        w: int,
        use_sharpen: int,
    ):
        """Process grayscale with optional contrast reduction."""
        for y, x in ti.ndrange(h, w):
            gray = src[y, x]

            if use_sharpen:
                # 30% contrast reduction
                gray = (gray - 0.5) * 0.7 + 0.5

            dst[y, x] = tm.clamp(gray, 0.0, 1.0)


def preprocess_in_python_gpu(
    ref_image_float,
    use_raft=False,
    use_sharpen=False,
    out=None,
    buffer_provider="pool",
):
    """
    GPU version of preprocess_in_python.
    Extract green channel with optional contrast reduction.
    
    Args:
        ref_image_float: Input image (GPU buffer or numpy), float32
        use_raft: If True, return as-is (for RAFT compatibility)
        use_sharpen: If True, apply 30% contrast reduction
        out: Optional output buffer
        buffer_provider: Buffer pool provider
    
    Returns:
        ti.ndarray (GPU buffer) grayscale float32
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Upload to GPU if needed
    src_gpu, src_is_temp = common.ensure_taichi_field(
        ref_image_float, dtype=ti.f32, buffer_provider=buffer_provider
    )

    h, w = src_gpu.shape[:2]
    is_rgb = len(src_gpu.shape) == 3 and src_gpu.shape[2] > 1

    # If use_raft, return as-is
    if use_raft:
        if src_is_temp:
            return src_gpu
        else:
            # Need to copy to avoid modifying original
            dst_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32, buffer_provider)
            common.copy_field(src_gpu, dst_gpu)
            return dst_gpu

    # Create output buffer (grayscale)
    if out is None:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    else:
        dst_gpu = out

    # Extract green or process grayscale
    if is_rgb:
        _extract_green_kernel(src_gpu, dst_gpu, h, w, int(use_sharpen))
    else:
        _extract_green_kernel_2d(src_gpu, dst_gpu, h, w, int(use_sharpen))

    # Cleanup
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return dst_gpu


# ============================================================================
# Unified Pipeline Function
# ============================================================================


def preprocess_pipeline_gpu(
    image,
    normalize=True,
    apply_gamma=False,
    extract_green=True,
    use_sharpen=False,
    use_raft=False,
    scale=1.0,
    gamma_pow=2.22,
    slope=4.5,
    cutoff=0.018,
    dtype=None,
    buffer_provider="pool",
    return_numpy=False,
):
    """
    Unified GPU preprocessing pipeline with minimal CPU-GPU transfers.
    
    Pipeline: Normalize → Gamma → Extract Green → Sharpen
    
    Args:
        image: Input image (numpy or GPU buffer)
        normalize: Apply normalization (u16/u8 → f32 [0,1])
        apply_gamma: Apply gamma correction (linear → gamma)
        extract_green: Extract green channel (RGB → grayscale)
        use_sharpen: Apply contrast reduction (30%)
        use_raft: Return as-is for RAFT (skips green extraction)
        scale: Exposure scaling factor
        gamma_pow: Gamma power
        slope: Linear slope
        cutoff: Gamma transition point
        dtype: Original dtype (auto-detected if None)
        buffer_provider: Buffer pool provider
        return_numpy: If True, download to numpy array
    
    Returns:
        GPU buffer (ti.ndarray) or numpy array if return_numpy=True
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    current_gpu = None

    # Step 1: Normalize
    if normalize:
        current_gpu = normalize_image_gpu(
            image, dtype=dtype, buffer_provider=buffer_provider
        )
    else:
        current_gpu, _ = common.ensure_taichi_field(
            image, dtype=ti.f32, buffer_provider=buffer_provider
        )

    # Step 2: Gamma
    if apply_gamma:
        prev_gpu = current_gpu
        current_gpu = to_gamma_proxy_gpu(
            prev_gpu,
            scale=scale,
            gamma_pow=gamma_pow,
            slope=slope,
            cutoff=cutoff,
            buffer_provider=buffer_provider,
        )
        common.release_temp_buffer(prev_gpu)

    # Step 3: Extract Green / Preprocess
    if extract_green or use_sharpen:
        prev_gpu = current_gpu
        current_gpu = preprocess_in_python_gpu(
            prev_gpu,
            use_raft=use_raft,
            use_sharpen=use_sharpen,
            buffer_provider=buffer_provider,
        )
        if prev_gpu != current_gpu:
            common.release_temp_buffer(prev_gpu)

    # Return
    if return_numpy:
        result = current_gpu.to_numpy()
        common.release_temp_buffer(current_gpu)
        return result
    else:
        return current_gpu


# ============================================================================
# Fallback for non-Taichi environments
# ============================================================================

else:

    def normalize_image_gpu(*args, **kwargs):
        raise ImportError("Taichi not available")

    def to_gamma_proxy_gpu(*args, **kwargs):
        raise ImportError("Taichi not available")

    def preprocess_in_python_gpu(*args, **kwargs):
        raise ImportError("Taichi not available")

    def preprocess_pipeline_gpu(*args, **kwargs):
        raise ImportError("Taichi not available")
