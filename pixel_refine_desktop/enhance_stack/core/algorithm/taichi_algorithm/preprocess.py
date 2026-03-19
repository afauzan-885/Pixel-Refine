"""
Preprocessing - Modular Taichi GPU Implementation
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
    from .taichi_worker import ti_thread, TAICHI_AVAILABLE
    from . import common
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None
    common = None
    ti_thread = lambda f: f  # No-op in case of no Taichi


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


@ti_thread
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


@ti_thread
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
        _gamma_kernel_2d(src_gpu, dst_gpu, h, w, scale, gamma_pow, slope, cutoff)
    else:
        _gamma_kernel_3d(src_gpu, dst_gpu, h, w, scale, gamma_pow, slope, cutoff)

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


@ti_thread
def preprocess_in_python_gpu(
    ref_image_float,
    use_raft=False,
    use_sharpen=False,
    out=None,
    buffer_provider="pool",
    return_numpy=False,
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
        return_numpy: If True, download to numpy array

    Returns:
        ti.ndarray (GPU buffer) grayscale float32 or numpy array
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
            dst_gpu = src_gpu
        else:
            # Need to copy to avoid modifying original
            dst_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32, buffer_provider)
            common.copy_field(src_gpu, dst_gpu)

        if return_numpy:
            result = dst_gpu.to_numpy()
            common.release_temp_buffer(dst_gpu)
            return result
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

    # Return
    if return_numpy:
        result = dst_gpu.to_numpy()
        common.release_temp_buffer(dst_gpu)
        return result
    else:
        return dst_gpu


# ============================================================================
# Fused Kernels for Optimal Performance
# ============================================================================

if TAICHI_AVAILABLE:

    # ========================================================================
    # Tier 3: Full Pipeline (Highest Impact - 75% speedup)
    # ========================================================================

    @ti.func
    def _fused_apply_postprocess(
        val: float,
        scale_norm: float,
        scale_gamma: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
        use_sharpen: int,
    ) -> float:
        """Shared fused post-process math for JIT and AOT kernels."""
        green = val / scale_norm
        green = green * scale_gamma
        if green < cutoff:
            green = green * slope
        else:
            green = 1.099 * tm.pow(green, 1.0 / gamma_pow) - 0.099

        if use_sharpen:
            green = (green - 0.5) * 0.7 + 0.5
        return tm.clamp(green, 0.0, 1.0)

    @ti.kernel
    def _fused_full_pipeline_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3), # Standardize to 3D for AOT
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        src_h: int,
        src_w: int,
        dst_h: int,
        dst_w: int,
        scale_norm: float,
        scale_gamma: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
        use_sharpen: int,
    ):
        """
        Fused kernel: Normalize → Gamma → Extract Green → Resize

        This is the most optimized path for alignment preprocessing.
        Combines all 4 steps into a single GPU kernel.
        """
        for y, x in ti.ndrange(dst_h, dst_w):
            # Step 1: Bilinear sampling coordinates
            u = (x + 0.5) / float(dst_w)
            v = (y + 0.5) / float(dst_h)

            src_x = u * float(src_w) - 0.5
            src_y = v * float(src_h) - 0.5

            x0 = int(ti.floor(src_x))
            y0 = int(ti.floor(src_y))
            fx = src_x - x0
            fy = src_y - y0

            # Clamp indices
            x0 = tm.clamp(x0, 0, src_w - 2)
            y0 = tm.clamp(y0, 0, src_h - 2)
            x1 = x0 + 1
            y1 = y0 + 1

            # Step 2: Sample green channel with bilinear interpolation (3D RGB input)
            v00 = float(src[y0, x0, 1])
            v10 = float(src[y0, x1, 1])
            v01 = float(src[y1, x0, 1])
            v11 = float(src[y1, x1, 1])

            top = v00 * (1.0 - fx) + v10 * fx
            bottom = v01 * (1.0 - fx) + v11 * fx
            green = top * (1.0 - fy) + bottom * fy
            dst[y, x] = _fused_apply_postprocess(
                green,
                scale_norm,
                scale_gamma,
                gamma_pow,
                slope,
                cutoff,
                use_sharpen,
            )

    @ti.kernel
    def _fused_full_pipeline_i32_2d_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        src_h: int,
        src_w: int,
        dst_h: int,
        dst_w: int,
        scale_norm: float,
        scale_gamma: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
        use_sharpen: int,
    ):
        """
        AOT-stable fused pipeline for grayscale i32 input.
        Shared math with _fused_full_pipeline_kernel.
        """
        for y, x in ti.ndrange(dst_h, dst_w):
            u = (x + 0.5) / float(dst_w)
            v = (y + 0.5) / float(dst_h)

            src_x = u * float(src_w) - 0.5
            src_y = v * float(src_h) - 0.5

            x0 = int(ti.floor(src_x))
            y0 = int(ti.floor(src_y))
            fx = src_x - x0
            fy = src_y - y0

            x0 = tm.clamp(x0, 0, src_w - 2)
            y0 = tm.clamp(y0, 0, src_h - 2)
            x1 = x0 + 1
            y1 = y0 + 1

            v00 = float(src[y0, x0])
            v10 = float(src[y0, x1])
            v01 = float(src[y1, x0])
            v11 = float(src[y1, x1])

            top = v00 * (1.0 - fx) + v10 * fx
            bottom = v01 * (1.0 - fx) + v11 * fx
            gray = top * (1.0 - fy) + bottom * fy

            dst[y, x] = _fused_apply_postprocess(
                gray,
                scale_norm,
                scale_gamma,
                gamma_pow,
                slope,
                cutoff,
                use_sharpen,
            )

    @ti.kernel
    def _fused_full_pipeline_i32_3d_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        src_h: int,
        src_w: int,
        dst_h: int,
        dst_w: int,
        scale_norm: float,
        scale_gamma: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
        use_sharpen: int,
    ):
        """
        AOT-stable fused pipeline for RGB i32 input.
        Uses green channel for alignment parity with preprocess_pipeline_gpu(extract_green=True).
        """
        for y, x in ti.ndrange(dst_h, dst_w):
            u = (x + 0.5) / float(dst_w)
            v = (y + 0.5) / float(dst_h)

            src_x = u * float(src_w) - 0.5
            src_y = v * float(src_h) - 0.5

            x0 = int(ti.floor(src_x))
            y0 = int(ti.floor(src_y))
            fx = src_x - x0
            fy = src_y - y0

            x0 = tm.clamp(x0, 0, src_w - 2)
            y0 = tm.clamp(y0, 0, src_h - 2)
            x1 = x0 + 1
            y1 = y0 + 1

            v00 = float(src[y0, x0, 1])
            v10 = float(src[y0, x1, 1])
            v01 = float(src[y1, x0, 1])
            v11 = float(src[y1, x1, 1])

            top = v00 * (1.0 - fx) + v10 * fx
            bottom = v01 * (1.0 - fx) + v11 * fx
            green = top * (1.0 - fy) + bottom * fy

            dst[y, x] = _fused_apply_postprocess(
                green,
                scale_norm,
                scale_gamma,
                gamma_pow,
                slope,
                cutoff,
                use_sharpen,
            )

    @ti_thread
    def fused_full_pipeline(
        image,
        target_size,
        is_linear=False,
        scale=1.0,
        use_sharpen=False,
        gamma_pow=2.22,
        slope=4.5,
        cutoff=0.018,
        dtype=None,
        buffer_provider="pool",
        return_numpy=False,
    ):
        """
        Fused kernel: Normalize → Gamma → Extract Green → Resize

        This is the FASTEST preprocessing path for alignment.
        Combines all 4 steps into a single GPU kernel.

        Args:
            image: Input image (numpy or GPU buffer)
            target_size: (height, width) tuple for output size
            is_linear: If True, apply gamma correction
            scale: Exposure scaling factor (for gamma)
            use_sharpen: Apply 30% contrast reduction
            gamma_pow: Gamma power (default 2.22)
            slope: Linear slope (default 4.5)
            cutoff: Gamma transition point (default 0.018)
            dtype: Original dtype (auto-detected if None)
            buffer_provider: Buffer pool provider
            return_numpy: If True, download to numpy array

        Returns:
            GPU buffer (ti.ndarray) or numpy array if return_numpy=True

        Performance:
            ~75% faster than modular approach (4 kernels → 1 kernel)
        """
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi not available")

        # Auto-detect dtype
        if dtype is None:
            dtype = getattr(image, "dtype", np.float32)

        # Determine normalization scale
        if np.issubdtype(dtype, np.integer):
            scale_norm = float(np.iinfo(dtype).max)
        else:
            scale_norm = 1.0

        # Upload to GPU if needed
        src_gpu, src_is_temp = common.ensure_taichi_field(
            image, buffer_provider=buffer_provider
        )

        src_h, src_w = src_gpu.shape[:2]
        dst_h, dst_w = target_size

        # Create output buffer
        dst_gpu = common.get_temp_buffer((dst_h, dst_w), ti.f32, buffer_provider)

        # Run fused kernel
        scale_gamma = scale if is_linear else 1.0
        
        # Standardize src to 3D for fused kernel compatibility (H, W, 3)
        src_3d = src_gpu
        if len(src_gpu.shape) == 2:
            src_3d = common.get_temp_buffer((src_h, src_w, 3), ti.f32, buffer_provider)
            _normalize_kernel_2d(src_gpu, src_3d, src_h, src_w, 1.0)

        _fused_full_pipeline_kernel(
            src_3d,
            dst_gpu,
            src_h,
            src_w,
            dst_h,
            dst_w,
            scale_norm,
            scale_gamma,
            gamma_pow,
            slope,
            cutoff,
            int(use_sharpen),
        )

        # Cleanup
        if src_3d is not src_gpu:
            common.release_temp_buffer(src_3d)
        if src_is_temp:
            common.release_temp_buffer(src_gpu)

        # Return
        if return_numpy:
            result = dst_gpu.to_numpy()
            common.release_temp_buffer(dst_gpu)
            return result
        else:
            return dst_gpu

    # ========================================================================
    # Tier 2: 3-Step Fusions (60% speedup)
    # ========================================================================

    @ti.kernel
    def _fused_normalize_gamma_green_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: int,
        w: int,
        scale_norm: float,
        scale_gamma: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
        use_sharpen: int,
    ):
        """Fused kernel: Normalize → Gamma → Extract Green"""
        for y, x in ti.ndrange(h, w):
            # Extract green channel
            green = 0.0
            if ti.static(len(src.shape) == 3):
                green = float(src[y, x, 1])
            else:
                green = float(src[y, x])

            # Normalize
            green = green / scale_norm

            # Gamma correction
            green = green * scale_gamma
            if green < cutoff:
                green = green * slope
            else:
                green = 1.099 * tm.pow(green, 1.0 / gamma_pow) - 0.099

            # Sharpen
            if use_sharpen:
                green = (green - 0.5) * 0.7 + 0.5

            dst[y, x] = tm.clamp(green, 0.0, 1.0)

    @ti_thread
    def fused_normalize_gamma_green(
        image,
        is_linear=False,
        scale=1.0,
        use_sharpen=False,
        gamma_pow=2.22,
        slope=4.5,
        cutoff=0.018,
        dtype=None,
        buffer_provider="pool",
        return_numpy=False,
    ):
        """
        Fused kernel: Normalize → Gamma → Extract Green

        Optimized for alignment preprocessing without resize.

        Performance: ~60% faster than modular approach (3 kernels → 1 kernel)
        """
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi not available")

        # Auto-detect dtype
        if dtype is None:
            dtype = getattr(image, "dtype", np.float32)

        # Determine normalization scale
        if np.issubdtype(dtype, np.integer):
            scale_norm = float(np.iinfo(dtype).max)
        else:
            scale_norm = 1.0

        # Upload to GPU if needed
        src_gpu, src_is_temp = common.ensure_taichi_field(
            image, buffer_provider=buffer_provider
        )

        h, w = src_gpu.shape[:2]

        # Create output buffer
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

        # Run fused kernel
        scale_gamma = scale if is_linear else 1.0
        _fused_normalize_gamma_green_kernel(
            src_gpu,
            dst_gpu,
            h,
            w,
            scale_norm,
            scale_gamma,
            gamma_pow,
            slope,
            cutoff,
            int(use_sharpen),
        )

        # Cleanup
        if src_is_temp:
            common.release_temp_buffer(src_gpu)

        # Return
        if return_numpy:
            result = dst_gpu.to_numpy()
            common.release_temp_buffer(dst_gpu)
            return result
        else:
            return dst_gpu

    # ========================================================================
    # Tier 1: 2-Step Fusions (40% speedup)
    # ========================================================================

    @ti.kernel
    def _fused_gamma_and_extract_green_kernel(
        src: ti.types.ndarray(dtype=ti.f32),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: int,
        w: int,
        scale_gamma: float,
        gamma_pow: float,
        slope: float,
        cutoff: float,
        use_sharpen: int,
    ):
        """Fused kernel: Gamma → Extract Green"""
        for y, x in ti.ndrange(h, w):
            # Extract green channel
            green = 0.0
            if ti.static(len(src.shape) == 3):
                green = src[y, x, 1]
            else:
                green = src[y, x]

            # Gamma correction
            green = green * scale_gamma
            if green < cutoff:
                green = green * slope
            else:
                green = 1.099 * tm.pow(green, 1.0 / gamma_pow) - 0.099

            # Sharpen
            if use_sharpen:
                green = (green - 0.5) * 0.7 + 0.5

            dst[y, x] = tm.clamp(green, 0.0, 1.0)

    @ti_thread
    def fused_gamma_and_extract_green(
        image,
        scale=1.0,
        use_sharpen=False,
        gamma_pow=2.22,
        slope=4.5,
        cutoff=0.018,
        buffer_provider="pool",
        return_numpy=False,
    ):
        """
        Fused kernel: Gamma → Extract Green

        For already normalized images.

        Performance: ~40% faster than modular approach (2 kernels → 1 kernel)
        """
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi not available")

        # Upload to GPU if needed
        src_gpu, src_is_temp = common.ensure_taichi_field(
            image, dtype=ti.f32, buffer_provider=buffer_provider
        )

        h, w = src_gpu.shape[:2]

        # Create output buffer
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

        # Run fused kernel
        _fused_gamma_and_extract_green_kernel(
            src_gpu,
            dst_gpu,
            h,
            w,
            scale,
            gamma_pow,
            slope,
            cutoff,
            int(use_sharpen),
        )

        # Cleanup
        if src_is_temp:
            common.release_temp_buffer(src_gpu)

        # Return
        if return_numpy:
            result = dst_gpu.to_numpy()
            common.release_temp_buffer(dst_gpu)
            return result
        else:
            return dst_gpu


# ============================================================================
# Unified Pipeline Function
# ============================================================================


@ti_thread
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
    target_size=None,  # NEW: (height, width) for resize
):
    """
    Smart GPU preprocessing pipeline with automatic optimization.

    Automatically selects the fastest fused kernel based on enabled steps.
    The more steps you enable, the more optimization you get!

    Pipeline: Normalize → Gamma → Extract Green → Resize

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
        target_size: (height, width) for resize, or None

    Returns:
        GPU buffer (ti.ndarray) or numpy array if return_numpy=True

    Performance:
        - 4-step fusion (N+G+E+R): ~75% faster
        - 3-step fusion (N+G+E): ~60% faster
        - 2-step fusion (G+E): ~40% faster
        - Modular fallback: baseline speed
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Determine which steps are enabled
    has_normalize = normalize
    has_gamma = apply_gamma
    has_green = extract_green and not use_raft
    has_resize = target_size is not None

    # ========================================================================
    # Smart Kernel Selection - Route to optimal fused kernel
    # ========================================================================

    # 4-step fusion (FASTEST - 75% speedup)
    if has_normalize and has_gamma and has_green and has_resize:
        return fused_full_pipeline(
            image,
            target_size=target_size,
            is_linear=True,
            scale=scale,
            use_sharpen=use_sharpen,
            gamma_pow=gamma_pow,
            slope=slope,
            cutoff=cutoff,
            dtype=dtype,
            buffer_provider=buffer_provider,
            return_numpy=return_numpy,
        )

    # 3-step fusions (FAST - 60% speedup)
    if has_normalize and has_gamma and has_green:
        return fused_normalize_gamma_green(
            image,
            is_linear=True,
            scale=scale,
            use_sharpen=use_sharpen,
            gamma_pow=gamma_pow,
            slope=slope,
            cutoff=cutoff,
            dtype=dtype,
            buffer_provider=buffer_provider,
            return_numpy=return_numpy,
        )

    # 2-step fusions (FASTER - 40% speedup)
    if has_gamma and has_green:
        return fused_gamma_and_extract_green(
            image,
            scale=scale,
            use_sharpen=use_sharpen,
            gamma_pow=gamma_pow,
            slope=slope,
            cutoff=cutoff,
            buffer_provider=buffer_provider,
            return_numpy=return_numpy,
        )

    # ========================================================================
    # Fallback: Modular approach (for combinations without fused kernels)
    # ========================================================================

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

    # Step 4: Resize (if needed)
    if has_resize:
        from . import bilinear_interpolation

        prev_gpu = current_gpu
        dst_h, dst_w = target_size

        # Use public API which handles kernel selection and threading
        current_gpu = bilinear_interpolation.bilinear_resize(
            prev_gpu, dst_h, dst_w, dst=None
        )
        common.release_temp_buffer(prev_gpu)

    # Return
    if return_numpy:
        result = current_gpu.to_numpy()
        common.release_temp_buffer(current_gpu)
        return result
    else:
        return current_gpu


# ============================================================================
# CPU Fallback for non-Taichi environments (Optimized with NumPy/OpenCV)
# ============================================================================
if not TAICHI_AVAILABLE:
    import cv2

    def normalize_image_gpu(image, dtype=None, out=None, buffer_provider="pool"):
        """
        CPU fallback: Normalize image to [0, 1] float32.

        This is optimized using NumPy vectorization.
        """
        # Auto-detect dtype
        if dtype is None:
            dtype = image.dtype

        # Determine scale
        if np.issubdtype(dtype, np.integer):
            scale = float(np.iinfo(dtype).max)
        else:
            scale = 1.0

        # Normalize
        normalized = image.astype(np.float32) / scale

        # Ensure 3 channels
        if normalized.ndim == 2:
            normalized = np.stack([normalized] * 3, axis=-1)

        return normalized

    def to_gamma_proxy_gpu(
        image,
        scale=1.0,
        gamma_pow=2.22,
        slope=4.5,
        cutoff=0.018,
        buffer_provider="pool",
    ):
        """
        CPU fallback: Apply gamma correction (BT.709).

        Optimized using NumPy vectorization.
        """
        result = image.copy()
        result = result * scale

        # BT.709 gamma curve (vectorized)
        mask_linear = result < cutoff
        result[mask_linear] = result[mask_linear] * slope
        result[~mask_linear] = (
            1.099 * np.power(result[~mask_linear], 1.0 / gamma_pow) - 0.099
        )

        return np.clip(result, 0.0, 1.0)

    def preprocess_in_python_gpu(
        image,
        use_raft=False,
        use_sharpen=False,
        buffer_provider="pool",
        return_numpy=False,
    ):
        """
        CPU fallback: Extract green channel and apply sharpening.

        Optimized using NumPy indexing.
        """
        # Extract green channel
        if image.ndim == 3:
            green = image[:, :, 1].copy()
        else:
            green = image.copy()

        # Apply contrast reduction (sharpen)
        if use_sharpen:
            green = (green - 0.5) * 0.7 + 0.5

        return np.clip(green, 0.0, 1.0)

    def fused_full_pipeline(
        image,
        target_size,
        is_linear=False,
        scale=1.0,
        use_sharpen=False,
        gamma_pow=2.22,
        slope=4.5,
        cutoff=0.018,
        dtype=None,
        buffer_provider="pool",
        return_numpy=True,
    ):
        """
        CPU fallback: Full pipeline (Normalize → Gamma → Green → Resize).

        Optimized using NumPy + OpenCV resize.
        """
        # Auto-detect dtype
        if dtype is None:
            dtype = image.dtype

        # Determine scale
        if np.issubdtype(dtype, np.integer):
            scale_norm = float(np.iinfo(dtype).max)
        else:
            scale_norm = 1.0

        # Extract green channel and normalize
        if image.ndim == 3:
            green = image[:, :, 1].astype(np.float32) / scale_norm
        else:
            green = image.astype(np.float32) / scale_norm

        # Apply gamma if linear
        if is_linear:
            green = green * scale
            mask_linear = green < cutoff
            green[mask_linear] = green[mask_linear] * slope
            green[~mask_linear] = (
                1.099 * np.power(green[~mask_linear], 1.0 / gamma_pow) - 0.099
            )

        # Apply sharpening
        if use_sharpen:
            green = (green - 0.5) * 0.7 + 0.5

        green = np.clip(green, 0.0, 1.0)

        # Resize using OpenCV (optimized)
        dst_h, dst_w = target_size
        result = cv2.resize(green, (dst_w, dst_h), interpolation=cv2.INTER_LINEAR)

        return result

    def fused_normalize_gamma_green(
        image,
        is_linear=False,
        scale=1.0,
        use_sharpen=False,
        gamma_pow=2.22,
        slope=4.5,
        cutoff=0.018,
        dtype=None,
        buffer_provider="pool",
        return_numpy=True,
    ):
        """
        CPU fallback: Normalize → Gamma → Green.

        Optimized using NumPy vectorization.
        """
        # Auto-detect dtype
        if dtype is None:
            dtype = image.dtype

        # Determine scale
        if np.issubdtype(dtype, np.integer):
            scale_norm = float(np.iinfo(dtype).max)
        else:
            scale_norm = 1.0

        # Extract green and normalize
        if image.ndim == 3:
            green = image[:, :, 1].astype(np.float32) / scale_norm
        else:
            green = image.astype(np.float32) / scale_norm

        # Apply gamma if linear
        if is_linear:
            green = green * scale
            mask_linear = green < cutoff
            green[mask_linear] = green[mask_linear] * slope
            green[~mask_linear] = (
                1.099 * np.power(green[~mask_linear], 1.0 / gamma_pow) - 0.099
            )

        # Apply sharpening
        if use_sharpen:
            green = (green - 0.5) * 0.7 + 0.5

        return np.clip(green, 0.0, 1.0)

    def fused_gamma_and_extract_green(
        image,
        scale=1.0,
        use_sharpen=False,
        gamma_pow=2.22,
        slope=4.5,
        cutoff=0.018,
        buffer_provider="pool",
        return_numpy=True,
    ):
        """
        CPU fallback: Gamma → Green.

        Optimized using NumPy vectorization.
        """
        # Extract green
        if image.ndim == 3:
            green = image[:, :, 1].copy()
        else:
            green = image.copy()

        # Apply gamma
        green = green * scale
        mask_linear = green < cutoff
        green[mask_linear] = green[mask_linear] * slope
        green[~mask_linear] = (
            1.099 * np.power(green[~mask_linear], 1.0 / gamma_pow) - 0.099
        )

        # Apply sharpening
        if use_sharpen:
            green = (green - 0.5) * 0.7 + 0.5

        return np.clip(green, 0.0, 1.0)

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
        return_numpy=True,
        target_size=None,
    ):
        """
        CPU fallback: Smart preprocessing pipeline.

        Automatically routes to optimized CPU implementations.
        """
        # Determine which steps are enabled
        has_normalize = normalize
        has_gamma = apply_gamma
        has_green = extract_green and not use_raft
        has_resize = target_size is not None

        # Route to optimized CPU functions
        # 4-step fusion
        if has_normalize and has_gamma and has_green and has_resize:
            return fused_full_pipeline(
                image,
                target_size,
                is_linear=True,
                scale=scale,
                use_sharpen=use_sharpen,
                gamma_pow=gamma_pow,
                slope=slope,
                cutoff=cutoff,
                dtype=dtype,
            )

        # 3-step fusion
        if has_normalize and has_gamma and has_green:
            return fused_normalize_gamma_green(
                image,
                is_linear=True,
                scale=scale,
                use_sharpen=use_sharpen,
                gamma_pow=gamma_pow,
                slope=slope,
                cutoff=cutoff,
                dtype=dtype,
            )

        # 2-step fusion
        if has_gamma and has_green:
            return fused_gamma_and_extract_green(
                image,
                scale=scale,
                use_sharpen=use_sharpen,
                gamma_pow=gamma_pow,
                slope=slope,
                cutoff=cutoff,
            )

        # Fallback: Modular approach
        current = image

        # Step 1: Normalize
        if normalize:
            current = normalize_image_gpu(current, dtype=dtype)

        # Step 2: Gamma
        if apply_gamma:
            current = to_gamma_proxy_gpu(
                current,
                scale=scale,
                gamma_pow=gamma_pow,
                slope=slope,
                cutoff=cutoff,
            )

        # Step 3: Extract green
        if extract_green or use_sharpen:
            current = preprocess_in_python_gpu(
                current,
                use_raft=use_raft,
                use_sharpen=use_sharpen,
            )

        # Step 4: Resize
        if has_resize:
            dst_h, dst_w = target_size
            current = cv2.resize(
                current, (dst_w, dst_h), interpolation=cv2.INTER_LINEAR
            )

        return current
