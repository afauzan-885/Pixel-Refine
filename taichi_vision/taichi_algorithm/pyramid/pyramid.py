"""Image Pyramid - Taichi GPU"""

import numpy as np
import os

import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass

MIN_PYRAMID_SIZE = 32

if TAICHI_AVAILABLE:
    class _AotKernelProvider:
        """Helper to switch between JIT and AOT kernels."""
        _kernels = {}

        @classmethod
        def get(cls, name, fallback):
            return cls._kernels.get(name, fallback)

        @classmethod
        def register(cls, name, kernel):
            cls._kernels[name] = kernel


    @ti.kernel
    def _downsample_2x_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    ):
        """Standard 2x downsampling (Gaussian filter). AOT-compatible.
        Uses REFLECT_101 boundary to match OpenCV pyrDown.
        """
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        # Gaussian weights [1, 4, 6, 4, 1] / 16
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        total_weight = 256.0  # (1+4+6+4+1)^2

        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = r * 2
            x_src = c * 2

            val = 0.0
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    # Use REFLECT_101 boundary to match OpenCV pyrDown
                    sy = common.reflect_idx(y_src + j, h_src)
                    sx = common.reflect_idx(x_src + i, w_src)
                    val += src[sy, sx] * weights[j + 2] * weights[i + 2]

            dst[r, c] = val / total_weight

    @ti.kernel
    def _downsample_2x_kernel_3ch(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Standard 2x downsampling (Gaussian filter) for 3-channel color images.
        Uses REFLECT_101 boundary to match OpenCV pyrDown.
        """
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        total_weight = 256.0

        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = r * 2
            x_src = c * 2

            val = tm.vec3(0.0)
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    # Use REFLECT_101 boundary to match OpenCV pyrDown
                    sy = common.reflect_idx(y_src + j, h_src)
                    sx = common.reflect_idx(x_src + i, w_src)
                    w = weights[j + 2] * weights[i + 2]
                    val += tm.vec3(src[sy, sx, 0], src[sy, sx, 1], src[sy, sx, 2]) * w

            res = val / total_weight
            dst[r, c, 0] = res[0]
            dst[r, c, 1] = res[1]
            dst[r, c, 2] = res[2]

    @ti.kernel
    def _downsample_2x_offset_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        offset_y: int, offset_x: int,
    ):
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            sy0, sx0 = (r + offset_y) * 2, (c + offset_x) * 2
            val = 0.0
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    sy = common.reflect_idx(sy0 + j, src.shape[0])
                    sx = common.reflect_idx(sx0 + i, src.shape[1])
                    val += src[sy, sx] * weights[j + 2] * weights[i + 2]
            dst[r, c] = val / 256.0

    @ti.kernel
    def _downsample_2x_offset_kernel_3ch(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        offset_y: int, offset_x: int,
    ):
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        for r, c, ch in ti.ndrange(dst.shape[0], dst.shape[1], 3):
            sy0, sx0 = (r + offset_y) * 2, (c + offset_x) * 2
            val = 0.0
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    sy = common.reflect_idx(sy0 + j, src.shape[0])
                    sx = common.reflect_idx(sx0 + i, src.shape[1])
                    val += src[sy, sx, ch] * weights[j + 2] * weights[i + 2]
            dst[r, c, ch] = val / 256.0

    @ti.kernel
    def _upsample_flow_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        scale: ti.f32,
    ):
        """Bicubic upsampling for flow fields. AOT-compatible."""
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        for r, c in ti.ndrange(h_dst, w_dst):
            # Coordinates in source domain
            v = float(c) * (float(w_src) / float(w_dst))
            u = float(r) * (float(h_src) / float(h_dst))

            # Sample each channel using bicubic interpolation from common.py
            val0 = common.bicubic_at_channel(src, v, u, h_src, w_src, 0)
            val1 = common.bicubic_at_channel(src, v, u, h_src, w_src, 1)

            dst[r, c, 0] = val0 * scale
            dst[r, c, 1] = val1 * scale





@ti_thread
def build_image_pyramid(
    image: np.ndarray, n_levels: int = 4, min_size: int = MIN_PYRAMID_SIZE
) -> list:
    """CPU interface: Build image pyramid and return list of NumPy arrays."""
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return [lvl.to_numpy() for lvl in taichi_aot.image_pyramid(image, levels=n_levels, return_gpu=True)]

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Upload once using common
    image_gpu, _ = common.ensure_taichi_field(image, dtype=ti.f32)

    # Build on GPU
    pyramid_gpu = build_image_pyramid_gpu(image_gpu, n_levels, min_size)

    # Download all (for backward compatibility)
    return [level.to_numpy() for level in pyramid_gpu]


@ti_thread
def build_image_pyramid_gpu(
    image_gpu,
    n_levels: int = 4,
    min_size: int = MIN_PYRAMID_SIZE,
    downscale_factor: float = 2.0,
    buffer_provider="pool",
) -> list:
    """
    GPU native interface: Build image pyramid with dynamic downsampling.

    Args:
        image_gpu: Source image ti.ndarray.
        n_levels: Total number of levels (including full res).
        min_size: Minimum width or height to stop downsampling.
        downscale_factor: Scale factor between levels (e.g., 2, 4, 1.5).
            - Powers of 2: Uses high-quality cascaded 5x5 Gaussian downsampling.
            - Others: Uses Bilinear interpolation.
        buffer_provider: "pool" or "new".
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        # ``taichi_aot.image_pyramid`` exposes the deepest level for its
        # single-output API.  Optical-flow callers need every resident level,
        # so dispatch the same native pyramid TCM graph while retaining L0,
        # L1, ... as owned GPU buffers.
        from taichi_vision.taichi_aot import get_engine
        from taichi_vision.taichi_algorithm.aot_api import (
            aot_graph_available,
            _resolve_pyramid_graph_module,
            _run_auto_graph_sequence,
        )

        engine = get_engine()
        pyramid = [image_gpu]
        is_3d = len(image_gpu.shape) == 3
        graph = "downsample_2x_3ch_f32" if is_3d else "downsample_2x_f32"
        pyramid_module, module_key = _resolve_pyramid_graph_module(graph)
        vector_dim = int(image_gpu.shape[2]) if is_3d else 1
        dispatches = []

        for _ in range(max(0, int(n_levels) - 1)):
            prev = pyramid[-1]
            h_prev, w_prev = prev.shape[:2]
            h_next, w_next = h_prev // 2, w_prev // 2
            if h_next < min_size or w_next < min_size:
                break

            dst_shape = (
                (h_next, w_next, vector_dim) if is_3d else (h_next, w_next)
            )
            dst = engine.allocate(
                dst_shape,
                dtype=prev.dtype,
                is_vector=is_3d,
                vector_dim=vector_dim,
            )
            prev_view = (
                prev.view_as_vector(False)
                if is_3d and getattr(prev, "is_vector", False)
                else prev
            )
            dst_view = (
                dst.view_as_vector(False)
                if is_3d and getattr(dst, "is_vector", False)
                else dst
            )
            dispatches.append((prev_view, dst_view))
            pyramid.append(dst)

        if dispatches:
            # OFB contains fixed-length native chain graphs for the common
            # 3- and 4-level pyramids.  Submit the whole chain directly when
            # available; unlike the generic recorder this creates no
            # per-call graph and preserves the exact dispatch ordering.
            chain_graph = None
            # CUDA benefits materially from a precompiled chain because the
            # driver launch/recorder overhead is visible on small pyramid
            # levels.  Vulkan/OpenGL/CPU measurements show that their direct
            # dispatch path is already cheaper than a multi-argument chain,
            # so keep those backends on the normal per-level submission.
            use_chain = str(getattr(engine, "arch", "")).lower() == "cuda"
            if use_chain and module_key == "ofb" and len(dispatches) in (2, 3):
                suffix = "3ch_f32" if is_3d else "f32"
                candidate = f"pyramid_chain_{len(dispatches)}_{suffix}"
                if aot_graph_available("ofb", candidate):
                    chain_graph = candidate

            if chain_graph is not None:
                chain_kwargs = {"src": dispatches[0][0]}
                for level_index in range(1, len(dispatches)):
                    intermediate = dispatches[level_index - 1][1]
                    # The chain graph exposes separate producer/consumer
                    # arguments for each intermediate to avoid compile-time
                    # shape unification.  Both names intentionally bind to
                    # the same resident buffer.
                    chain_kwargs[f"level_{level_index}_out"] = intermediate
                    chain_kwargs[f"level_{level_index}_in"] = intermediate
                chain_kwargs["dst"] = dispatches[-1][1]
                pyramid_module.run(chain_graph, **chain_kwargs)
                return pyramid

            def _dispatch_pyramid_levels():
                for src_view, dst in dispatches:
                    pyramid_module.run(graph, src=src_view, dst=dst)

            if module_key == "ofb" and not use_chain:
                for src_view, dst in dispatches:
                    pyramid_module.run(graph, src=src_view, dst=dst)
                return pyramid

            # All graphs live in the same bundle when available.  The
            # automatic recorder keeps the ordered sequence device-resident,
            # reducing Python/bridge launches while retaining a direct
            # same-backend fallback when the driver or memory governor rejects
            # recording.  ``shape_policy=transform`` is required because each
            # level intentionally changes dimensions.
            _run_auto_graph_sequence(
                (graph,) * len(dispatches),
                tuple(int(value) for value in image_gpu.shape),
                _dispatch_pyramid_levels,
                operation="ofb_pyramid" if module_key == "ofb" else "image_pyramid",
                source=f"{module_key}_pyramid_levels",
                resident_multiplier=2,
                reads=("pyramid_input",),
                writes=("pyramid_levels",),
                metadata={
                    "sequence_kind": "deterministic_local_prefix",
                    "hazard_policy": "ordered",
                    "shape_policy": "transform",
                    "allow_shape_change": True,
                },
                module_keys=(module_key,) * len(dispatches),
                retain_buffers=tuple(pyramid),
            )

        return pyramid

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    pyramid = [image_gpu]

    # Check if downscale_factor is a power of 2
    is_power_of_2 = False
    steps_per_level = 0
    if downscale_factor > 0:
        log2_val = np.log2(downscale_factor)
        if np.isclose(log2_val, np.round(log2_val)):
            is_power_of_2 = True
            steps_per_level = int(np.round(log2_val))

    for _ in range(n_levels - 1):
        prev = pyramid[-1]
        h_src_prev, w_src_prev = prev.shape

        # Calculate target size
        h_dst_curr = int(np.round(h_src_prev / downscale_factor))
        w_dst_curr = int(np.round(w_src_prev / downscale_factor))

        if h_dst_curr < min_size or w_dst_curr < min_size:
            break

        if is_power_of_2 and steps_per_level > 0:
            # High-quality Gaussian cascaded downsampling
            current_lvl_input = prev
            h_s_curr, w_s_curr = h_src_prev, w_src_prev
            for step in range(steps_per_level):
                h_d_step, w_d_step = h_s_curr // 2, w_s_curr // 2

                # Should not reach here if h_dst/w_dst check above is correct,
                # but adding safety for internal steps
                if h_d_step < 1 or w_d_step < 1:
                    break

                dst = common.get_temp_buffer(
                    (h_d_step, w_d_step), ti.f32, buffer_provider
                )
                _AotKernelProvider.get("_downsample_2x_kernel", _downsample_2x_kernel)(
                    current_lvl_input, dst
                )

                if step < steps_per_level - 1:
                    if current_lvl_input is not prev:
                        common.release_temp_buffer(current_lvl_input)
                    current_lvl_input = dst
                    h_s_curr, w_s_curr = h_d_step, w_d_step
                else:
                    pyramid.append(dst)
                    if current_lvl_input is not prev:
                        common.release_temp_buffer(current_lvl_input)
        else:
            # Fallback to Bilinear Resize for arbitrary scales
            from ..interpolation.bilinear_interpolation import bilinear_resize

            dst = bilinear_resize(
                prev, h_dst_curr, w_dst_curr, buffer_provider=buffer_provider
            )
            pyramid.append(dst)

    return pyramid


@ti_thread
def build_image_pyramid_gpu_4x(
    image_gpu,
    n_levels: int = 4,
    min_size: int = MIN_PYRAMID_SIZE,
    buffer_provider="pool",
) -> list:
    """
    Backward compatibility wrapper for 4x downsampling pyramid.
    """
    return build_image_pyramid_gpu(
        image_gpu,
        n_levels,
        min_size,
        downscale_factor=4,
        buffer_provider=buffer_provider,
    )


@ti_thread
def upsample_flow(
    flow: np.ndarray,
    target_h: int,
    target_w: int,
    scale: float = 2.0,
    buffer_provider="pool",
) -> np.ndarray:
    """CPU interface: Upsample flow using NumPy input/output."""
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision.taichi_aot import get_engine
        engine = get_engine()
        src_gpu = engine.upload(flow)
        dst_gpu = engine.allocate((target_h, target_w, 2), dtype=np.float32)
        upsample_flow_gpu(src_gpu, dst_gpu, scale)
        res = dst_gpu.to_numpy()
        src_gpu.destroy()
        dst_gpu.destroy()
        return res

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    src_gpu, src_is_temp = common.ensure_taichi_field(
        flow, dtype=ti.f32, buffer_provider=buffer_provider
    )
    dst_gpu = common.get_temp_buffer((target_h, target_w, 2), ti.f32, buffer_provider)
    upsample_flow_gpu(src_gpu, dst_gpu, scale)

    res = dst_gpu.to_numpy()

    if src_is_temp:
        common.release_temp_buffer(src_gpu)
    common.release_temp_buffer(dst_gpu)

    return res


@ti_thread
def upsample_flow_gpu(
    src_gpu,
    dst_gpu,
    scale: float | tuple[float, float] = 2.0,
):
    """GPU native interface: Upsample flow from one ti.ndarray to another."""
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        pyramid_mod = taichi_aot._mod("pyramid")
        if isinstance(scale, (tuple, list)):
            sx = scale[0]
        else:
            sx = scale
        pyramid_mod.run("upsample_flow_f32", src=src_gpu, dst=dst_gpu, scale=float(sx))
        return

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h_src, w_src = src_gpu.shape[:2]
    h_dst, w_dst = dst_gpu.shape[:2]

    if isinstance(scale, (tuple, list)):
        sx, sy = scale
    else:
        sx, sy = scale, scale

    _upsample_flow_kernel(
        src_gpu, dst_gpu,
        float(sx),
    )
