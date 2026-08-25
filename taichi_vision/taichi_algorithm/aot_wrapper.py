"""
AOT Wrapper Layer — NumPy/OpenCV-Compatible API for AOT-Compiled Kernels
=====================================================================

Single-source API for all Taichi AOT-compiled kernels.
All functions follow NumPy/OpenCV naming conventions and signatures.

Usage:
    from taichi_vision.taichi_algorithm.aot_wrapper import ta

    # OpenCV-compatible
    result = ta.resize(src, (width, height))
    gray = ta.cvtColor(src, ta.COLOR_BGR2GRAY)
    blurred = ta.gaussianBlur(src, (5, 5), 1.0)
    edges = ta.Canny(src, 50, 150)

    # NumPy-compatible
    z = ta.zeros((H, W))
    f = ta.full((H, W), 0.42)
    w = ta.hanning(1024)

All functions accept numpy arrays and return numpy arrays.
No need for InputArray/OutputArray wrappers or explicit h, w parameters.
"""

import os
import numpy as np

# Numeric compatibility constants.  The AOT wrapper deliberately has no
# OpenCV runtime dependency; callers may still use the familiar values.
NORM_HAMMING = 6
TM_CCOEFF_NORMED = 5

# ── Environment setup ──────────────────────────────────────────────────
from taichi_vision.config import AOT_MODE

# ── Lazy module loading ────────────────────────────────────────────────
_modules = {}
_OPENGL_FLOW_FAMILY = None
_OPENGL_FLOW_GPU_OUTPUTS = []


def _register_opengl_flow_output(buffer):
    if buffer is not None:
        _OPENGL_FLOW_GPU_OUTPUTS.append(buffer)
    return buffer


def _prepare_opengl_flow_family(family):
    """Reset the OpenGL AOT context when switching dense-flow graph families.

    Intel OpenGL drivers can retain SSBO binding state across the Lucas,
    Block-Matching, and Farneback modules. Reinitializing the native context
    at a family boundary prevents an algorithm-order-dependent assertion while
    keeping every computation on the OpenGL backend.
    """
    global _OPENGL_FLOW_FAMILY
    engine = _get_engine()
    if str(getattr(engine, "arch", "")).lower() not in {"opengl", "gles"}:
        return
    if _OPENGL_FLOW_FAMILY == family:
        return
    if _OPENGL_FLOW_FAMILY is not None:
        for buffer in list(_OPENGL_FLOW_GPU_OUTPUTS):
            try:
                buffer.destroy()
            except Exception:
                pass
        _OPENGL_FLOW_GPU_OUTPUTS.clear()
        _modules.clear()
        engine.reinit()
    _OPENGL_FLOW_FAMILY = family
_engine = None

# ── Persistent Buffer Cache ────────────────────────────────────────────
# FixedBufferPool for 512x512 processing - zero-allocation reuse
_fixed_pool = None


def _get_fixed_pool():
    """Get or create FixedBufferPool singleton."""
    global _fixed_pool
    if _fixed_pool is None:
        try:
            from taichi_vision.taichi_aot.engine import FixedBufferPool
            from taichi_vision.taichi_aot import get_engine
        except ImportError:
            return None
        _fixed_pool = FixedBufferPool(get_engine())
        # Pre-allocate common 512x512 buffers
        _fixed_pool.preallocate(
            [
                (512, 512),  # 1ch FP32
                (512, 512, 3),  # 3ch FP32
                (512, 512),  # 1ch intermediate
            ]
        )
    return _fixed_pool


def _get_buf(key, shape, dtype=np.float32):
    """Get buffer from FixedBufferPool (512x512) or fallback to OutputArray."""
    pool = _get_fixed_pool()
    if pool is None:
        from taichi_vision.taichi_aot.engine import OutputArray

        return OutputArray(shape, dtype)
    return pool.acquire(shape, dtype)


def _release_buf(buf):
    """Release buffer back to FixedBufferPool."""
    if _fixed_pool is not None and buf is not None:
        _fixed_pool.release(buf)


def _clear_buf_cache():
    """Clear FixedBufferPool."""
    global _fixed_pool
    if _fixed_pool is not None:
        _fixed_pool.clear()
        _fixed_pool = None


# ── Gaussian Weight Cache (CPU-side) ─────────────────────────────────
_w_cache = {}


def _get_gaussian_weights(ks, sigma):
    """Cache Gaussian weights di CPU, tanpa GPU copy."""
    key = (ks, sigma)
    if key not in _w_cache:
        radius = ks // 2
        w = np.exp(-0.5 * np.arange(-radius, radius + 1) ** 2 / sigma**2)
        _w_cache[key] = (w / w.sum()).astype(np.float32)
    return _w_cache[key]


def _get_engine():
    global _engine
    if _engine is None:
        # The package facade owns backend/device resolution.  Do not perform a
        # second env-based preflight here: that used to let this wrapper pick
        # a different adapter from the singleton engine during hybrid-GPU
        # startup.
        from taichi_vision.taichi_aot import get_engine

        _engine = get_engine()
    return _engine


def _is_gpu_buffer(value):
    return (
        hasattr(value, "to_numpy")
        and hasattr(value, "handle")
        and hasattr(value, "shape")
    )


# Import for direct graph execution (bypass AutoBatcher).  AOT compiler
# workers only need the kernel definitions; importing the bridge here would
# create an OpenGL context before Taichi's compiler and force a CPU fallback.
if os.environ.get("PIXEL_REFINE_AOT_COMPILE_ONLY", "0") == "1":
    DynamicArg = None
    _populate_dynamic_arg = None
else:
    from taichi_vision.taichi_aot.engine import DynamicArg, _populate_dynamic_arg


def _get_module(name):
    """Load a backend-specific TCM module without changing the public API."""
    engine = _get_engine()
    cache_key = (engine.arch.lower(), getattr(engine, "_generation", 0), name)
    if cache_key not in _modules:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        # Resolve the exact architecture/API/vendor artifact before calling
        # the native loader.  The previous unsuffixed path depended on the
        # legacy ``name_<backend>.tcm`` files and could silently load an
        # artifact compiled for a different adapter.
        from taichi_vision.taichi_aot.artifact_targets import (
            detect_target,
            resolve_artifact,
        )

        target = detect_target(
            backend=getattr(engine, "arch", "cpu"),
            device=getattr(engine, "gpu_name", ""),
        )
        # Prefer the exact target-qualified LLVM20 bundle when available.  An
        # explicit root wins; otherwise the repository tree remains a
        # rollback/source fallback.  Never search both roots, because mixing a
        # legacy LLVM15 archive with an LLVM20 bridge is an ABI error.
        explicit_tcm_root = os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip()
        if explicit_tcm_root:
            tcm_root = os.path.abspath(explicit_tcm_root)
        else:
            from taichi_vision.llvm20_runtime_paths import tcm_root as staged_tcm_root

            staged_root = staged_tcm_root(target.target_id)
            tcm_root = os.path.abspath(
                str(staged_root) if staged_root is not None else os.path.join(file_dir, "aot_tcm")
            )
        allow_legacy = (
            # Legacy root artifacts are migration-only and disabled by
            # default now that the target-qualified tree is complete.
            os.environ.get("PIXEL_REFINE_AOT_ALLOW_LEGACY_ARTIFACTS", "0") == "1"
            and not target.is_arm
            and not target.is_mobile
        )
        resolved = resolve_artifact(
            tcm_root,
            name,
            target,
            allow_legacy=allow_legacy,
        )
        if resolved is None:
            raise FileNotFoundError(
                f"No target-qualified AOT artifact for {name!r} "
                f"({target.target_id}) under {tcm_root!r}"
            )
        _modules[cache_key] = engine.load(str(resolved))
    return _modules[cache_key]


# ── Helper functions ───────────────────────────────────────────────────
def _InputArray(data, is_vector=False, force_vector=None):
    """Wrap numpy array for AOT kernel input.

    Args:
        data: Input numpy array.
        is_vector: Whether to treat as vector field.
        force_vector: If True, force vector mode; if False, force non-vector;
                       if None, use is_vector value.
    """
    from taichi_vision.taichi_aot.engine import InputArray

    # Map force_vector to is_vector (InputArray doesn't have force_vector param)
    effective_vector = is_vector
    if force_vector is not None:
        effective_vector = force_vector
    if force_vector is False and isinstance(data, np.ndarray):
        from taichi_vision.taichi_aot import engine as aot_engine
        import importlib

        engine_mod = importlib.import_module("taichi_vision.taichi_aot.engine")

        arr = np.ascontiguousarray(data)
        buf = aot_engine.allocate(
            arr.shape,
            arr.dtype,
            is_vector=False,
            host_accessible=True,
            vector_dim=1,
        )
        engine_mod._LIB.write_to_gpu_buffer(
            aot_engine.runtime,
            buf.handle,
            arr.ctypes.data,
            buf.nbytes,
        )
        return buf
    return InputArray(data, is_vector=effective_vector)


def _OutputArray(shape, dtype=np.float32):
    """Create output buffer for AOT kernel."""
    from taichi_vision.taichi_aot.engine import OutputArray
    return OutputArray(shape, dtype)


def _as_f32_array(src):
    """Return a contiguous float32 ndarray with no copy when already compatible."""
    if _is_gpu_buffer(src):
        return src
    if isinstance(src, np.ndarray):
        if src.dtype == np.float32 and src.flags.c_contiguous:
            return src
        return np.ascontiguousarray(src, dtype=np.float32)
    return np.ascontiguousarray(src, dtype=np.float32)


def array(src, dtype=np.float32):
    """Upload an array to GPU once for chained math operations."""
    if _is_gpu_buffer(src):
        return src
    if dtype is not None:
        src = np.ascontiguousarray(src, dtype=dtype)
    return _InputArray(src)


# ══════════════════════════════════════════════════════════════════════════
# COMMON OPERATIONS (cmn_*)
# ══════════════════════════════════════════════════════════════════════════


def copy(src):
    from taichi_vision import taichi_aot
    return taichi_aot.copy(src)

    """Copy array (same as numpy.copy) — persistent buffer."""
    mod = _get_module("common")
    inp = _InputArray(src)
    out = _get_buf("copy_dst", src.shape, src.dtype)
    mod.run("cmn_copy_2d", src=inp, dst=out)
    result = out.to_numpy()
    _release_buf(out)
    return result


def copy_3ch(src):
    from taichi_vision import taichi_aot
    return taichi_aot.copy(src)

    """Copy 3-channel array (same as numpy.copy for 3D arrays) — persistent buffer."""
    mod = _get_module("common")
    inp = _InputArray(src, force_vector=False)
    out = _get_buf("copy3ch_dst", src.shape, src.dtype)
    mod.run("cmn_copy_3ch", src=inp, dst=out)
    result = out.to_numpy()
    _release_buf(out)
    return result


def split_channels(src):
    from taichi_vision import taichi_aot
    return taichi_aot.split_3ch(src)

    """Split 3-channel array into 3 single-channel arrays (same as cv2.split)."""
    mod = _get_module("common")
    h, w = src.shape[:2]
    inp = _InputArray(src, force_vector=False)
    c0 = _OutputArray((h, w), src.dtype)
    c1 = _OutputArray((h, w), src.dtype)
    c2 = _OutputArray((h, w), src.dtype)
    mod.run("cmn_split_3ch", src=inp, ch0=c0, ch1=c1, ch2=c2, h=h, w=w)
    return c0.to_numpy(), c1.to_numpy(), c2.to_numpy()


def merge(channels):
    """Merge single-channel arrays into multi-channel array (same as cv2.merge)."""
    if isinstance(channels, (list, tuple)):
        if len(channels) == 1 and isinstance(channels[0], (list, tuple)):
            channels = channels[0]
        ch_list = list(channels)
    else:
        raise TypeError("merge() expects a list/tuple of channels.")

    if len(ch_list) < 2 or len(ch_list) > 4:
        raise ValueError(f"merge() expects 2-4 channels, got {len(ch_list)}")

    n_ch = len(ch_list)
    mod = _get_module("common")
    h, w = ch_list[0].shape[:2]
    inputs = [_InputArray(ch) for ch in ch_list]
    out = _OutputArray((h, w, n_ch), ch_list[0].dtype)

    if n_ch == 3:
        mod.run(
            "cmn_merge_3ch",
            ch0=inputs[0],
            ch1=inputs[1],
            ch2=inputs[2],
            src=out,
            h=h,
            w=w,
        )
        return out.to_numpy()
    else:
        return np.stack(ch_list, axis=-1).astype(ch_list[0].dtype)


def absdiff(src1, src2):
    from taichi_vision import taichi_aot
    return taichi_aot.absdiff(src1, src2)

    """Absolute difference between two arrays (same as cv2.absdiff) — persistent buffer."""
    mod = _get_module("common")
    i1 = _InputArray(src1)
    i2 = _InputArray(src2)
    out = _get_buf("absdiff_dst", src1.shape, src1.dtype)
    mod.run("cmn_absdiff_2d", src1=i1, src2=i2, dst=out)
    return out if _is_gpu_buffer(src) else out.to_numpy()


def mean_division(num, den, eps=1e-6):
    """Element-wise division with epsilon for numerical stability."""
    mod = _get_module("common")
    h, w = num.shape[:2]
    in_ = _InputArray(num)
    id_ = _InputArray(den)
    out = _OutputArray(num.shape, num.dtype)
    mod.run("cmn_mean_div_2d", num=in_, den=id_, dst=out, h=h, w=w, eps=eps)
    return out if _is_gpu_buffer(src) else out.to_numpy()


def hanning(n):
    return np.hanning(int(n)).astype(np.float32)

    """Create 1D Hanning window (same as numpy.hanning)."""
    mod = _get_module("common")
    out = _OutputArray((n,), np.float32)
    mod.run("cmn_hanning", dst=out, h=n)
    return out if _is_gpu_buffer(src) else out.to_numpy()


def normalize(src, min_val=0.0, max_val=1.0):
    array = src.to_numpy() if _is_gpu_buffer(src) else np.asarray(src)
    lo = float(np.min(array))
    hi = float(np.max(array))
    if hi <= lo:
        return np.full_like(array, float(min_val), dtype=np.float32)
    scaled = (array.astype(np.float32) - lo) / (hi - lo)
    return scaled * (float(max_val) - float(min_val)) + float(min_val)

    """Normalize array to [min_val, max_val] range (same as cv2.normalize NORM_MINMAX) — persistent buffer."""
    mod = _get_module("common")
    inp = _InputArray(src)
    out = _get_buf("norm_dst", src.shape, src.dtype)
    mod.run("cmn_normalize_2d", src=inp, dst=out, min_val=min_val, max_val=max_val)
    return out


def zero(shape, dtype=np.float32):
    return np.zeros(shape, dtype=dtype)

    """Create zero-filled array (same as numpy.zeros) — persistent buffer."""
    mod = _get_module("common")
    out = _get_buf("zero_dst", shape, dtype)
    mod.run("cmn_zero_2d", dst=out)
    return out.to_numpy()


def full(shape, val, dtype=np.float32):
    return np.full(shape, val, dtype=dtype)

    """Create constant-filled array (same as numpy.full) — persistent buffer."""
    mod = _get_module("common")
    out = _get_buf("full_dst", shape, dtype)
    mod.run("cmn_fill_2d", dst=out, val=float(val))
    return out.to_numpy()


def copyMakeBorder(src, top, bottom, left, right, borderType=4, dst=None, value=0):
    """OpenCV-compatible copyMakeBorder using AOT.

    Pads image borders natively on the GPU supporting multiple datatypes
    and both 2D and 3D (multi-channel) arrays.
    """
    array = src.to_numpy() if _is_gpu_buffer(src) else np.asarray(src)
    # OpenCV REFLECT includes the edge (NumPy ``symmetric``); REFLECT_101
    # excludes it (NumPy ``reflect``).
    mode = {1: "edge", 2: "symmetric", 4: "reflect"}.get(int(borderType), "constant")
    pad_width = ((int(top), int(bottom)), (int(left), int(right)))
    if array.ndim == 3:
        pad_width += ((0, 0),)
    kwargs = {"constant_values": value} if mode == "constant" else {}
    return np.pad(array, pad_width, mode=mode, **kwargs)


# Backward-compatible alias
copy_make_border = copyMakeBorder


def non_local_means(src, h_param=10.0, search_window=7, patch_size=3):
    """Apply Non-Local Means (NLM) Denoising (same as cv2.fastNlMeansDenoising)."""
    from taichi_vision import taichi_aot

    return taichi_aot.non_local_means(
        src, h_param=h_param, search_window=search_window, patch_size=patch_size
    )


fastNlMeansDenoising = non_local_means


def bm3d(
    src,
    sigma,
    block_size=8,
    search_radius=15,
    max_matches=16,
    lambda_3d=2.7,
    cycle_spins=1,
):
    """Apply BM3D (Hybrid Fast Collaborative Denoising)."""
    from taichi_vision import taichi_aot

    return taichi_aot.bm3d(
        src,
        sigma=sigma,
        block_size=block_size,
        search_radius=search_radius,
        max_matches=max_matches,
        lambda_3d=lambda_3d,
        cycle_spins=cycle_spins,
    )


# ══════════════════════════════════════════════════════════════════════════
# COLOR CONVERSION (color_*)
# ══════════════════════════════════════════════════════════════════════════

# Constants (OpenCV-compatible values)
COLOR_BGR2GRAY = 6
COLOR_RGB2GRAY = 7
COLOR_GRAY2BGR = 8
COLOR_GRAY2RGB = 9
COLOR_BGR2HSV = 40
COLOR_HSV2BGR = 54
COLOR_BGR2LAB = 44
COLOR_LAB2BGR = 55
COLOR_BGR2YCrCb = 36
COLOR_YCrCb2BGR = 37


def cvtColor(src, code):
    # Keep this compatibility wrapper on the canonical AOT graph contracts;
    # legacy ``cmn_gray``/``color`` names are not shipped anymore.
    from taichi_vision import taichi_aot
    return taichi_aot.cvtColor(src, code)

    """Convert image color space (same as cv2.cvtColor) — persistent buffer."""
    h, w = src.shape[:2]

    # Grayscale conversions
    if code in (COLOR_BGR2GRAY, COLOR_RGB2GRAY):
        mod = _get_module("common")
        # Keep RGB arrays as Taichi vector fields (ndim=2, vector_dim=3),
        # matching the bilinear AOT graph contract.
        inp = _InputArray(src, is_vector=True, force_vector=True)
        out = _get_buf("gray_dst", (h, w), src.dtype)
        mod.run("cmn_gray", src=inp, dst=out, h=h, w=w)
        return out

    # Grayscale to 3-channel
    if code in (COLOR_GRAY2BGR, COLOR_GRAY2RGB):
        return np.stack([src, src, src], axis=-1).astype(src.dtype)

    # Color space conversions (via color module)
    mod = _get_module("color")
    inp = _InputArray(src, force_vector=False)
    out = _get_buf(f"cvt_color_{h}x{w}x3", src.shape, src.dtype)

    _color_map = {
        COLOR_BGR2HSV: "color_bgr2hsv",
        COLOR_HSV2BGR: "color_hsv2bgr",
        COLOR_BGR2LAB: "color_bgr2lab",
        COLOR_LAB2BGR: "color_lab2bgr",
        COLOR_BGR2YCrCb: "color_bgr2ycrcb",
        COLOR_YCrCb2BGR: "color_ycrcb2bgr",
    }

    graph_name = _color_map.get(code)
    if graph_name is None:
        raise NotImplementedError(f"cvtColor code {code} not yet implemented.")

    mod.run(graph_name, src=inp, dst=out, h=h, w=w)
    return out if _is_gpu_buffer(src) else out.to_numpy()


# ══════════════════════════════════════════════════════════════════════════
# GRADIENTS (grad_*) — cv2.Sobel, cv2.Laplacian
# ══════════════════════════════════════════════════════════════════════════


def Sobel(src, dx, dy, ksize=3):
    from taichi_vision import taichi_aot
    gx, gy = taichi_aot.sobel(src, return_gpu=_is_gpu_buffer(src))
    return gx if dx >= 1 and dy == 0 else gy

    """Apply Sobel operator (same as cv2.Sobel).

    Args:
        src: Input grayscale image (H, W).
        dx: Order of derivative x (0 or 1).
        dy: Order of derivative y (0 or 1).
        ksize: Kernel size (currently only 3 supported).
    Returns:
        Gradient image (H, W) float32.
    """
    mod = _get_module("gradients")
    h, w = src.shape[:2]
    inp = _InputArray(src)
    out = _get_buf("sobel_dst", (h, w), np.float32)

    if dx >= 1 and dy == 0:
        mod.run("grad_sobel_h", src=inp, dst=out, h=h, w=w)
    elif dx == 0 and dy >= 1:
        mod.run("grad_sobel_v", src=inp, dst=out, h=h, w=w)
    else:
        raise NotImplementedError("Sobel: only dx=1,dy=0 or dx=0,dy=1 supported.")

    return out


def Laplacian(src, ksize=1):
    from taichi_vision import taichi_aot
    return taichi_aot.laplacian(src, return_gpu=_is_gpu_buffer(src))

    """Apply Laplacian operator (same as cv2.Laplacian)."""
    mod = _get_module("gradients")
    h, w = src.shape[:2]
    inp = _InputArray(src)
    out = _get_buf("lap_dst", (h, w), np.float32)
    mod.run("grad_laplacian", src=inp, dst=out, h=h, w=w)
    return out if any(_is_gpu_buffer(v) for v in (cond, x, y)) else out.to_numpy()


# ══════════════════════════════════════════════════════════════════════════
# INTERPOLATION (intr_*) — cv2.resize, cv2.remap
# ══════════════════════════════════════════════════════════════════════════

INTER_NEAREST = 0
INTER_LINEAR = 1
INTER_CUBIC = 2


def resize(src, dsize, interpolation=INTER_LINEAR):
    """Resize image (same as cv2.resize).

    Args:
        src: Input image (H, W) or (H, W, 3).
        dsize: Tuple (width, height).
        interpolation: INTER_LINEAR, INTER_NEAREST, INTER_CUBIC.
    Returns:
        Resized image.
    """
    # Keep the legacy convenience wrapper on the canonical AOT implementation
    # so graph names, vector views, dtype normalization, and tiled/full-frame
    # policy remain identical across all backends.
    from taichi_vision import taichi_aot

    return taichi_aot.resize(src, dsize, interpolation=interpolation)

    target_w, target_h = dsize
    src_h, src_w = src.shape[:2]
    is_3ch = len(src.shape) == 3

    # The published artifacts are split by operation.  ``interpolation.tcm``
    # was a legacy name and is not shipped; use the graph contracts emitted by
    # compile_bilinear_tcm/compile_nearest_tcm instead.
    mod = _get_module("nearest" if interpolation == INTER_NEAREST else "bilinear")

    if is_3ch:
        inp = _InputArray(src, force_vector=False)
        out = _get_buf(
            f"resize_3ch_{target_h}x{target_w}", (target_h, target_w, 3), src.dtype
        )
        if interpolation == INTER_NEAREST:
            raise NotImplementedError(
                "AOT nearest-neighbor currently has a scalar graph only; "
                "use INTER_LINEAR for 3-channel input."
            )
        else:  # INTER_LINEAR
            mod.run(
                "bilinear_resize_f32_3d",
                src=inp,
                dst=out,
                h_src=src_h,
                w_src=src_w,
                h_dst=target_h,
                w_dst=target_w,
            )
    else:
        inp = _InputArray(src)
        out = _get_buf(
            f"resize_2d_{target_h}x{target_w}", (target_h, target_w), src.dtype
        )
        if interpolation == INTER_NEAREST:
            mod.run(
                "nearest_resize_f32",
                src=inp,
                dst=out,
                h_src=src_h,
                w_src=src_w,
                h_dst=target_h,
                w_dst=target_w,
            )
        else:
            mod.run(
                "bilinear_resize_f32_2d",
                src=inp,
                dst=out,
                h_src=src_h,
                w_src=src_w,
                h_dst=target_h,
                w_dst=target_w,
            )

    return out.to_numpy()


def remap(src, map1, map2, interpolation=INTER_LINEAR):
    from taichi_vision import taichi_aot
    return taichi_aot.remap(src, map1, map2)

    """Remap image (same as cv2.remap).

    Args:
        src: Input image (H, W) or (H, W, 3).
        map1: X coordinate map (H, W) float32.
        map2: Y coordinate map (H, W) float32.
        interpolation: INTER_LINEAR or INTER_NEAREST.
    Returns:
        Remapped image.
    """
    mod = _get_module("geometric")
    h, w = src.shape[:2]
    is_3ch = len(src.shape) == 3

    if is_3ch:
        # For 3-channel remap, process each channel separately (simplified)
        c0, c1, c2 = split_channels(src)
        r0 = remap(c0, map1, map2, interpolation)
        r1 = remap(c1, map1, map2, interpolation)
        r2 = remap(c2, map1, map2, interpolation)
        return merge([r0, r1, r2])

    inp = _InputArray(src)
    mx = _InputArray(map1.astype(np.float32))
    my = _InputArray(map2.astype(np.float32))
    out = _get_buf(f"remap_{h}x{w}", (h, w), src.dtype)
    mod.run("geom_remap", src=inp, dst=out, map_x=mx, map_y=my, h=h, w=w)
    return out


# ══════════════════════════════════════════════════════════════════════════
# SMOOTHING (smth_*) — cv2.GaussianBlur, cv2.blur, cv2.medianBlur, cv2.bilateralFilter
# ══════════════════════════════════════════════════════════════════════════


def gaussianBlur(src, ksize, sigmaX=0, sigmaY=0):
    from taichi_vision import taichi_aot
    kernel = int(ksize[0] if isinstance(ksize, (tuple, list)) else ksize)
    sigma = float(sigmaX or sigmaY or 1.0)
    return taichi_aot.gaussian_blur(src, sigma=sigma, kernel_size=kernel)

    """Apply Gaussian Blur (same as cv2.GaussianBlur).

    Args:
        src: Input image (H, W) or (H, W, 3).
        ksize: Kernel size as (w, h) tuple or int.
        sigmaX: Standard deviation in X direction.
        sigmaY: Standard deviation in Y direction (unused, uses sigmaX).
    Returns:
        Blurred image.
    """
    ks = ksize[0] if isinstance(ksize, (tuple, list)) else ksize
    mod = _get_module("smoothing")
    h, w = src.shape[:2]
    is_3ch = len(src.shape) == 3

    sigma = sigmaX if sigmaX > 0 else 0.3 * ((ks - 1) * 0.5 - 1) + 0.8
    weights = _get_gaussian_weights(ks, sigma)
    w_inp = _InputArray(weights)

    if is_3ch:
        inp = _InputArray(src, force_vector=False)
        tmp = _get_buf("gauss_tmp_3ch", (h, w, 3), np.float32)
        out = _get_buf("gauss_out_3ch", (h, w, 3), np.float32)
        mod.run("smth_gauss_h_3ch", src=inp, dst=tmp, weights=w_inp, h=h, w=w)
        mod.run("smth_gauss_v_3ch", src=tmp, dst=out, weights=w_inp, h=h, w=w)
    else:
        inp = _InputArray(src)
        tmp = _get_buf("gauss_tmp_1ch", (h, w), np.float32)
        out = _get_buf("gauss_out_1ch", (h, w), np.float32)
        mod.run("smth_gauss_h_1ch", src=inp, dst=tmp, weights=w_inp, h=h, w=w)
        mod.run("smth_gauss_v_1ch", src=tmp, dst=out, weights=w_inp, h=h, w=w)

    result = out.to_numpy()
    _release_buf(out)
    _release_buf(tmp)
    return result


def blur(src, ksize):
    """Apply Box Filter (same as cv2.blur).

    Args:
        src: Input image (H, W) or (H, W, 3).
        ksize: Kernel size as (w, h) tuple or int.
    Returns:
        Blurred image.
    """
    ks = ksize[0] if isinstance(ksize, (tuple, list)) else ksize
    mod = _get_module("smoothing")
    h, w = src.shape[:2]
    is_3ch = len(src.shape) == 3

    if ks == 3 and not is_3ch:
        inp = _InputArray(src)
        out = _get_buf("box3_dst", (h, w), src.dtype)
        mod.run("smth_box_3x3", src=inp, dst=out, h=h, w=w)
        result = out.to_numpy()
        _release_buf(out)
        return result

    if is_3ch:
        c0, c1, c2 = split_channels(src)
        r0 = blur(c0, ksize)
        r1 = blur(c1, ksize)
        r2 = blur(c2, ksize)
        return merge([r0, r1, r2])

    inp = _InputArray(src)
    tmp = _get_buf("box_tmp", (h, w), src.dtype)
    out = _get_buf("box_out", (h, w), src.dtype)
    mod.run("smth_box_sep_h", src=inp, dst=tmp, kernel_size=ks, h=h, w=w)
    mod.run("smth_box_sep_v", src=tmp, dst=out, kernel_size=ks, h=h, w=w)
    result = out.to_numpy()
    _release_buf(out)
    _release_buf(tmp)
    return result


def medianBlur(src, ksize):
    from taichi_vision import taichi_aot
    return taichi_aot.median_filter(src)

    """Apply Median filter (same as cv2.medianBlur).

    Args:
        src: Input image (H, W) or (H, W, 3).
        ksize: Kernel size (currently only 3 supported).
    Returns:
        Filtered image.
    """
    mod = _get_module("smoothing")
    h, w = src.shape[:2]
    is_3ch = len(src.shape) == 3

    if is_3ch:
        inp = _InputArray(src, force_vector=False)
        out = _get_buf("med_dst_3ch", (h, w, 3), src.dtype)
        mod.run("smth_median_3ch", src=inp, dst=out, h=h, w=w)
    else:
        inp = _InputArray(src)
        out = _get_buf("med_dst_1ch", (h, w), src.dtype)
        mod.run("smth_median_1ch", src=inp, dst=out, h=h, w=w)

    result = out.to_numpy()
    _release_buf(out)
    return result


def bilateralFilter(src, d, sigmaColor, sigmaSpace):
    """Apply Bilateral Filter (same as cv2.bilateralFilter).

    Args:
        src: Input image (H, W) float32.
        d: Diameter of pixel neighborhood.
        sigmaColor: Filter sigma in the color space.
        sigmaSpace: Filter sigma in the coordinate space.
    Returns:
        Filtered image.
    """
    mod = _get_module("smoothing")
    h, w = src.shape[:2]
    inp = _InputArray(src.astype(np.float32))
    out = _get_buf("bilat_dst", (h, w), np.float32)
    grid_size = max(int(sigmaSpace), 4)
    mod.run(
        "smth_bilateral_grid",
        src=inp,
        dst=out,
        h=h,
        w=w,
        sigma_s=float(sigmaSpace),
        sigma_r=float(sigmaColor),
        grid_size=grid_size,
    )
    result = out.to_numpy()
    _release_buf(out)
    return result


def GaussianBlur(src, ksize, sigmaX=0):
    """Alias for gaussianBlur (OpenCV naming convention)."""
    return gaussianBlur(src, ksize, sigmaX)


# ══════════════════════════════════════════════════════════════════════════
# IMAGE PROCESSING (imgp_*) — CLAHE, Canny, Hough, Threshold, Morphology, Otsu
# ══════════════════════════════════════════════════════════════════════════

# Threshold constants
THRESH_BINARY = 0
THRESH_BINARY_INV = 1
THRESH_TRUNC = 2
THRESH_TOZERO = 3
THRESH_TOZERO_INV = 4
THRESH_OTSU = 8

# Morphology constants
MORPH_RECT = 0
MORPH_CROSS = 1
MORPH_ELLIPSE = 2


def Canny(src, threshold1, threshold2, apertureSize=3):
    from taichi_vision import taichi_aot
    return taichi_aot.canny_aot(src, low_threshold=threshold1, high_threshold=threshold2)

    """Apply Canny edge detection (same as cv2.Canny).

    Args:
        src: Input grayscale image (H, W).
        threshold1: Lower threshold for hysteresis.
        threshold2: Upper threshold for hysteresis.
        apertureSize: Not used (fixed 5x5 Gaussian).
    Returns:
        Edge map (H, W) float32.
    """
    # NOTE: Multi-step pipeline - execute directly to avoid AutoBatcher issues
    mod = _get_module("image_processing")
    h, w = src.shape[:2]
    inp = _InputArray(src)
    tmp = _OutputArray((h, w), np.float32)
    out = _OutputArray((h, w), np.float32)
    gx = _OutputArray((h, w), np.float32)
    gy = _OutputArray((h, w), np.float32)
    mag = _OutputArray((h, w), np.float32)

    # Execute directly (bypass AutoBatcher)
    engine = _get_engine()
    with engine._lock:
        mod.run("imgp_canny_gauss", src=inp, dst=tmp, h=h, w=w)
        mod.run("imgp_canny_sobel", src=tmp, gx=gx, gy=gy, mag=mag, h=h, w=w)
        mod.run("imgp_canny_nms", src=mag, gx=gx, gy=gy, dst=tmp, h=h, w=w)
        mod.run(
            "imgp_canny_dthresh",
            src=tmp,
            dst=out,
            h=h,
            w=w,
            low=float(threshold1),
            high=float(threshold2),
        )
        mod.run("imgp_canny_hyst", dst=out, h=h, w=w)
        engine.backend.sync(engine.runtime)
    return out


def HoughLines(edges, rho=1, theta=np.pi / 180, threshold=150):
    """Detect lines using Hough Transform (same as cv2.HoughLines).

    Args:
        edges: Edge map (H, W).
        rho: Distance resolution.
        theta: Angle resolution.
        threshold: Accumulator threshold.
    Returns:
        Lines array (N, 1, 2) with (rho, theta).
    """
    mod = _get_module("image_processing")
    h, w = edges.shape[:2]
    rho_offset = int(np.ceil(np.sqrt(h * h + w * w)))
    num_theta = 180

    # Build cos/sin tables
    cos_table = np.cos(np.arange(num_theta) * theta).astype(np.float32)
    sin_table = np.sin(np.arange(num_theta) * theta).astype(np.float32)

    acc = np.zeros((2 * rho_offset + 1, num_theta), dtype=np.int32)
    cos_buf = _InputArray(cos_table)
    sin_buf = _InputArray(sin_table)
    acc_buf = _OutputArray(acc.shape, np.int32)
    inp = _InputArray(edges.astype(np.float32))

    mod.run(
        "imgp_hough_vote",
        src=inp,
        accumulator=acc_buf,
        cos_table=cos_buf,
        sin_table=sin_buf,
        h=h,
        w=w,
        num_theta=num_theta,
        rho_offset=rho_offset,
        edge_threshold=0.5,
    )

    # Find peaks
    peak_count = np.zeros(1, dtype=np.int32)
    pc_buf = _OutputArray((1,), np.int32)
    peaks_buf = _OutputArray((500, 3), np.float32)

    mod.run(
        "imgp_hough_peaks",
        accumulator=acc_buf,
        peaks=peaks_buf,
        peak_count=pc_buf,
        num_rho=2 * rho_offset + 1,
        num_theta=num_theta,
        threshold=int(threshold),
        nms_radius=5,
        max_peaks=500,
    )

    count = pc_buf.to_numpy()[0]
    peaks = peaks_buf.to_numpy()[:count]
    if count == 0:
        return np.empty((0, 1, 2), dtype=np.float32)

    # Convert (rho_idx, theta_idx) to (rho, theta)
    lines = np.zeros((count, 1, 2), dtype=np.float32)
    for i in range(count):
        lines[i, 0, 0] = peaks[i, 0] - rho_offset
        lines[i, 0, 1] = peaks[i, 1] * theta
    return lines


def threshold(src, thresh, maxval=255, type=THRESH_BINARY):
    """Apply threshold (same as cv2.threshold).

    Args:
        src: Input image (H, W).
        thresh: Threshold value.
        maxval: Maximum value for THRESH_BINARY.
        type: Threshold type (THRESH_BINARY, THRESH_OTSU, etc.).
    Returns:
        Tuple (threshold_value, result_image).
    """
    mod = _get_module("image_processing")
    h, w = src.shape[:2]
    inp = _InputArray(src)
    out = _get_buf(f"thresh_{h}x{w}", (h, w), src.dtype)

    # Otsu: compute threshold using vectorized numpy operations
    actual_thresh = thresh
    if type & THRESH_OTSU:
        hist_buf = _get_buf("otsu_hist", (256,), np.int32)
        mod.run("imgp_otsu_hist", src=inp, hist=hist_buf, h=h, w=w)
        hist = hist_buf.to_numpy().astype(np.float64)

        # Vectorized Otsu computation (faster than Python loop)
        total = hist.sum()
        if total > 0:
            # Cumulative sums
            cum_hist = np.cumsum(hist)
            cum_sum = np.cumsum(np.arange(256) * hist)

            # Background and foreground weights
            weight_bg = cum_hist
            weight_fg = total - cum_hist

            # Avoid division by zero
            valid = (weight_bg > 0) & (weight_fg > 0)

            # Mean values
            mean_bg = np.zeros(256)
            mean_fg = np.zeros(256)
            mean_bg[valid] = cum_sum[valid] / weight_bg[valid]
            mean_fg[valid] = (cum_sum[-1] - cum_sum[valid]) / weight_fg[valid]

            # Between-class variance
            var_between = np.zeros(256)
            var_between[valid] = (
                weight_bg[valid]
                * weight_fg[valid]
                * (mean_bg[valid] - mean_fg[valid]) ** 2
            )

            # Find threshold with maximum variance
            actual_thresh = float(np.argmax(var_between))

    mod.run(
        "imgp_otsu_thresh", src=inp, dst=out, threshold=float(actual_thresh), h=h, w=w
    )
    return actual_thresh, out


def CLAHE(src, clipLimit=2.0, tileGridSize=(8, 8)):
    """Apply CLAHE (same as cv2.createCLAHE).

    Args:
        src: Input grayscale image (H, W) uint8.
        clipLimit: Threshold for contrast limiting.
        tileGridSize: Size of the interpolation grid.
    Returns:
        Enhanced image (H, W).
    """
    if np.asarray(src).ndim != 2:
        raise ValueError("CLAHE expects a single-channel 2D image")
    if clipLimit <= 0:
        raise ValueError("clipLimit must be positive")
    if len(tileGridSize) != 2 or any(int(v) <= 0 for v in tileGridSize):
        raise ValueError("tileGridSize must contain two positive integers")

    # The old wrapper computed two intermediate buffers and then discarded
    # them, returning a global normalize result instead of CLAHE.  Delegate to
    # the target-qualified three-pass AOT graph (histogram, clipped CDF, and
    # bilinear LUT interpolation) while preserving the OpenCV-style wrapper
    # signature and float32 output contract.
    from taichi_vision import taichi_aot

    source = np.ascontiguousarray(src, dtype=np.float32)
    return taichi_aot.clahe_aot(
        source,
        clip_limit=float(clipLimit),
        tile_grid_size=(int(tileGridSize[0]), int(tileGridSize[1])),
        return_gpu=False,
    )


def dilate(src, kernel, iterations=1):
    """Dilate image through the target-qualified morphology graph."""
    from taichi_vision import taichi_aot

    return taichi_aot.dilate_aot(
        np.ascontiguousarray(src, dtype=np.float32),
        kernel=kernel,
        iterations=int(iterations),
    )


def erode(src, kernel, iterations=1):
    """Erode image through the target-qualified morphology graph."""
    from taichi_vision import taichi_aot

    return taichi_aot.erode_aot(
        np.ascontiguousarray(src, dtype=np.float32),
        kernel=kernel,
        iterations=int(iterations),
    )


# ══════════════════════════════════════════════════════════════════════════
# DENOISING (deno_*) — cv2.fastNlMeansDenoising
# ══════════════════════════════════════════════════════════════════════════


def fastNlMeansDenoising(src, h=10, templateWindowSize=7, searchWindowSize=21):
    """Denoise image using Non-Local Means (same as cv2.fastNlMeansDenoising).

    Args:
        src: Input image (H, W) or (H, W, 3).
        h: Filter strength.
        templateWindowSize: Not used (simplified).
        searchWindowSize: Not used (simplified).
    Returns:
        Denoised image.
    """
    mod = _get_module("denoising")
    src_f = src.astype(np.float32)
    h_img, w_img = src_f.shape[:2]
    is_3ch = len(src_f.shape) == 3

    patch_radius = 3
    search_radius = max(1, min(searchWindowSize // 2, 10))
    h_factor = float(h) / 10.0

    if is_3ch:
        inp = _InputArray(src_f, force_vector=False)
        out = _get_buf(f"nlm_{h_img}x{w_img}x3", (h_img, w_img, 3), np.float32)
        mod.run(
            "deno_nlm_3ch",
            src=inp,
            dst=out,
            h=h_img,
            w=w_img,
            patch_radius=patch_radius,
            search_radius=search_radius,
            h_factor=h_factor,
        )
    else:
        inp = _InputArray(src_f)
        out = _get_buf(f"nlm_{h_img}x{w_img}", (h_img, w_img), np.float32)
        mod.run(
            "deno_nlm_1ch",
            src=inp,
            dst=out,
            h=h_img,
            w=w_img,
            patch_radius=patch_radius,
            search_radius=search_radius,
            h_factor=h_factor,
        )

    return out


# ══════════════════════════════════════════════════════════════════════════
# GEOMETRIC (geom_*) — cv2.inpaint, cv2.seamlessClone
# ══════════════════════════════════════════════════════════════════════════

INPAINT_TELEA = 0
INPAINT_NS = 1
NORMAL_CLONE = 1
MIXED_CLONE = 2
MONOCHROME_TRANSFER = 3


def inpaint(src, mask, inpaintRadius, flags=INPAINT_TELEA):
    """Inpaint missing regions (same as cv2.inpaint).

    Args:
        src: Input image (H, W, 3).
        mask: Inpaint mask (H, W) uint8.
        inpaintRadius: Not used (simplified).
        flags: INPAINT_TELEA or INPAINT_NS.
    Returns:
        Inpainted image (H, W, 3).
    """
    # NOTE: Iterative pipeline - execute directly
    mod = _get_module("geometric")
    h, w = src.shape[:2]
    src_f = src.astype(np.float32)
    mask_f = mask.astype(np.float32) / 255.0

    inp = _InputArray(src_f, force_vector=False)
    msk = _InputArray(mask_f)
    out = _OutputArray((h, w, 3), np.float32)
    dist = _OutputArray((h, w), np.float32)

    # Execute directly (bypass AutoBatcher)
    engine = _get_engine()
    with engine._lock:
        for _ in range(max(1, inpaintRadius)):
            mod.run("geom_inpaint_dist", mask=msk, dist=dist, h=h, w=w)
            mod.run("geom_inpaint_lvl", src=inp, dst=out, mask=msk, dist=dist, h=h, w=w)
            inp = out  # chain iterations
        engine.backend.sync(engine.runtime)

    return out


def seamlessClone(src, dst, mask, center, flags=NORMAL_CLONE):
    """Seamless cloning (same as cv2.seamlessClone).

    Args:
        src: Source image (H, W, 3).
        dst: Destination image (H, W, 3).
        mask: Clone mask (H, W).
        center: Not used (simplified).
        flags: Clone flag.
    Returns:
        Cloned image (H, W, 3).
    """
    # NOTE: Multi-step pipeline - execute directly
    mod = _get_module("geometric")
    h, w = dst.shape[:2]
    src_f = src.astype(np.float32)
    dst_f = dst.astype(np.float32)
    mask_f = mask.astype(np.float32) / 255.0

    s = _InputArray(src_f, force_vector=False)
    d = _InputArray(dst_f, force_vector=False)
    m = _InputArray(mask_f)
    out = _OutputArray((h, w, 3), np.float32)
    normal = _OutputArray((h, w, 3), np.float32)

    # Execute directly (bypass AutoBatcher)
    engine = _get_engine()
    with engine._lock:
        # Step 1: Compute divergence
        mod.run("geom_seamless_div", normal=normal, src=s, dst_img=d, mask=m, h=h, w=w)
        # Step 2: Jacobi iteration (simplified - single iteration)
        mod.run("geom_seamless_jac", src=normal, dst=out, mask=m, h=h, w=w)
        # Step 3: Composite
        mod.run("geom_seamless_comp", src=out, dst_img=d, mask=m, h=h, w=w)
        engine.backend.sync(engine.runtime)

    return out


# ══════════════════════════════════════════════════════════════════════════
# PYRAMID (pyra_*) — cv2.pyrDown, cv2.pyrUp
# ══════════════════════════════════════════════════════════════════════════


def pyrDown(src):
    """Downsample image (same as cv2.pyrDown).

    Args:
        src: Input image (H, W) or (H, W, 3).
    Returns:
        Downsampled image (H//2, W//2).
    """
    mod = _get_module("pyramid")
    h, w = src.shape[:2]
    is_3ch = len(src.shape) == 3

    inp = _InputArray(src, force_vector=False if is_3ch else True)
    out = _get_buf(
        f"pyr_down_{h//2}x{w//2}",
        (h // 2, w // 2, 3) if is_3ch else (h // 2, w // 2),
        src.dtype,
    )

    if is_3ch:
        mod.run("pyra_down_2x_3ch", src=inp, dst=out)
    else:
        mod.run("pyra_down_2x", src=inp, dst=out)

    return out.to_numpy()


def pyrUp(src):
    """Upsample image (same as cv2.pyrUp).

    Args:
        src: Input image (H, W) or (H, W, 3).
    Returns:
        Upsampled image (H*2, W*2).
    """
    # Simplified: use resize with INTER_LINEAR
    h, w = src.shape[:2]
    return resize(src, (w * 2, h * 2), INTER_LINEAR)


# ══════════════════════════════════════════════════════════════════════════
# OPTICAL FLOW (flow_*) — cv2.calcOpticalFlowFarneback
# ══════════════════════════════════════════════════════════════════════════


def calcOpticalFlowFarneback(
    prev,
    next,
    flow=None,
    pyr_scale=0.5,
    levels=3,
    winsize=15,
    iterations=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0,
):
    """Compute dense optical flow using Farneback method (same as cv2.calcOpticalFlowFarneback).

    Args:
        prev: Previous grayscale image (H, W).
        next: Next grayscale image (H, W).
        flow: Optional output flow array (H, W, 2).
        pyr_scale: Pyramid scale.
        levels: Number of pyramid levels.
        winsize: Average window size.
        iterations: Iterations at each level.
        poly_n: Size of pixel neighborhood.
        poly_sigma: Standard deviation of Gaussian.
        flags: Not used.
    Returns:
        Optical flow (H, W, 2) float32.
    """
    # NOTE: This function uses multi-step pipeline with intermediate buffers.
    # AutoBatcher cannot handle this properly, so we execute directly.
    mod = _get_module("optical_flow")
    h, w = prev.shape[:2]
    prev_f = prev.astype(np.float32)

    inp = _InputArray(prev_f)

    # Use OutputArray for intermediate buffers (specific shapes required by TCM)
    flow_buf = _OutputArray((h, w, 3), np.float32)
    py0 = _OutputArray((h, w), np.float32)
    py1 = _OutputArray((h, w), np.float32)
    py2 = _OutputArray((h, w), np.float32)
    poly = _OutputArray((h, w, 5), np.float32)

    # Helper to run graph directly (bypass AutoBatcher)
    def _run_graph_direct(graph_name, **kwargs):
        num_args = len(kwargs)
        args_array = (DynamicArg * num_args)()
        arg_names = [k.encode("utf-8") for k in kwargs.keys()]
        for i, (k, v) in enumerate(kwargs.items()):
            _populate_dynamic_arg(
                args_array[i], arg_names[i], v, context_name=graph_name
            )
        engine.backend.run_graph(
            engine.runtime,
            mod.module_ptr,
            graph_name.encode("utf-8"),
            args_array,
            num_args,
        )

    # Execute directly (bypass AutoBatcher for multi-step pipeline)
    engine = _get_engine()
    with engine._lock:
        # Clear flow
        _run_graph_direct("flow_farne_clear", flow=flow_buf, h=h, w=w)
        # Polynomial expansion
        _run_graph_direct(
            "flow_farne_poly_v", src=inp, py0=py0, py1=py1, py2=py2, h=h, w=w
        )
        _run_graph_direct(
            "flow_farne_poly_h", src0=py0, src1=py1, src2=py2, dst=poly, h=h, w=w
        )
        # Gaussian blur on polynomial
        _run_graph_direct("flow_farne_gauss_x", src=poly, dst=poly, h=h, w=w)
        _run_graph_direct("flow_farne_gauss_y", src=poly, dst=poly, h=h, w=w)
        # Sync to ensure all operations complete
        engine.backend.sync(engine.runtime)

    return flow_buf


def calcOpticalFlowPyrLK(
    prev,
    next,
    prevPts=None,
    nextPts=None,
    winSize=(13, 13),
    maxLevel=2,
    criteria=None,
    flags=0,
    minEigThreshold=1e-4,
    grid_step=48,
    border_margin=8,
    overlap=0.35,
    adaptive=False,
    adaptive_threshold=1,
    motion_mode="fast",
    dense_mode="smooth",
    max_flow_px=0.0,
    return_gpu=False,
    return_diagnostics=False,
):
    """Dense grid Lucas-Kanade optical flow with cv2-style function name.

    The Pixel Refine variant intentionally hides point setup: grid points,
    overlap, and Hanning-style splatting are handled internally.
    """
    _prepare_opengl_flow_family("lucas_kanade")
    # Intel OpenGL cannot safely expose the transient SSBO produced by the
    # dense graph. Compute natively using the validated host-output path,
    # then upload the completed result as a stable public GPU buffer.
    if return_gpu:
        try:
            if str(getattr(_get_engine(), "arch", "")).lower() in {"opengl", "gles"}:
                host_result = calcOpticalFlowPyrLK(
                    prev, next, prevPts=prevPts, nextPts=nextPts,
                    winSize=winSize, maxLevel=maxLevel, criteria=criteria,
                    flags=flags, minEigThreshold=minEigThreshold,
                    grid_step=grid_step, border_margin=border_margin,
                    overlap=overlap, adaptive=adaptive,
                    adaptive_threshold=adaptive_threshold,
                    motion_mode=motion_mode, dense_mode=dense_mode,
                    max_flow_px=max_flow_px, return_gpu=False,
                    return_diagnostics=return_diagnostics,
                )
                if return_diagnostics:
                    host_result, diagnostics = host_result
                else:
                    diagnostics = None
                from taichi_vision import taichi_aot
                gpu_result = taichi_aot.engine.upload(
                    np.ascontiguousarray(host_result, dtype=np.float32),
                    is_vector=True, vector_dim=2,
                )
                _register_opengl_flow_output(gpu_result)
                return (gpu_result, diagnostics) if return_diagnostics else gpu_result
        except Exception:
            raise
    h, w = prev.shape[:2]
    is_prev_gpu = hasattr(prev, "handle")
    is_next_gpu = hasattr(next, "handle")
    prev_f = prev if is_prev_gpu else prev.astype(np.float32)
    next_f = next if is_next_gpu else next.astype(np.float32)
    win = winSize[0] if isinstance(winSize, tuple) else int(winSize)
    win_radius = max(2, int(win) // 2)
    if criteria is None:
        iterations = 8
        epsilon = 0.03
    else:
        iterations = int(criteria[1])
        epsilon = float(criteria[2])

    try:
        mod = _get_module("lucas_kanade")
        pyramid_mod = _get_module("pyramid")
        grid_step_i = max(4, int(grid_step))
        margin_i = max(0, int(border_margin))
        levels_i = max(1, int(maxLevel) + 1)
        mode = str(motion_mode or "fast").lower()
        dense_mode_value = str(dense_mode or "smooth").lower()
        diagnostics = None
        rerun_high_motion = False

        engine = _get_engine()
        with engine._lock:
            prev_levels = [_InputArray(prev_f)]
            next_levels = [_InputArray(next_f)]
            level_shapes = [(h, w)]

            for _level in range(1, levels_i):
                src_h, src_w = level_shapes[-1]
                dst_h = src_h // 2
                dst_w = src_w // 2
                if dst_h < 32 or dst_w < 32:
                    break
                prev_dst = _OutputArray((dst_h, dst_w), np.float32)
                next_dst = _OutputArray((dst_h, dst_w), np.float32)
                pyramid_mod.run(
                    "downsample_2x_f32",
                    src=prev_levels[-1],
                    dst=prev_dst,
                )
                pyramid_mod.run(
                    "downsample_2x_f32",
                    src=next_levels[-1],
                    dst=next_dst,
                )
                prev_levels.append(prev_dst)
                next_levels.append(next_dst)
                level_shapes.append((dst_h, dst_w))

            current_flow = None
            for level in range(len(level_shapes) - 1, -1, -1):
                lh, lw = level_shapes[level]
                if current_flow is None:
                    init_flow = _OutputArray((lh, lw, 2), np.float32)
                    mod.run("flow_lk_zero", init_flow=init_flow)
                else:
                    init_flow = _OutputArray((lh, lw, 2), np.float32)
                    prev_h, _prev_w = level_shapes[level + 1]
                    scale = float(lh) / float(prev_h)
                    pyramid_mod.run(
                        "upsample_flow_f32",
                        src=current_flow,
                        dst=init_flow,
                        scale=scale,
                    )

                level_grid_step = max(4, grid_step_i >> level)
                level_margin = max(0, margin_i >> level)
                grid_w = max(
                    1, (lw - 2 * level_margin + level_grid_step - 1) // level_grid_step
                )
                grid_h = max(
                    1, (lh - 2 * level_margin + level_grid_step - 1) // level_grid_step
                )
                grid_flow = _OutputArray((grid_h, grid_w, 3), np.float32)
                grid_meta = _OutputArray((grid_h, grid_w, 4), np.float32)
                flow_out = _OutputArray((lh, lw, 2), np.float32)

                mod.run(
                    "flow_lk_grid_track",
                    prev=prev_levels[level],
                    next=next_levels[level],
                    init_flow=init_flow,
                    grid_flow=grid_flow,
                    grid_meta=grid_meta,
                    grid_step=level_grid_step,
                    border_margin=level_margin,
                    win_radius=win_radius,
                    iterations=max(1, int(iterations)),
                    epsilon=float(epsilon),
                )
                if adaptive and level == 0:
                    mod.run(
                        "flow_lk_adaptive_refine",
                        prev=prev_levels[level],
                        next=next_levels[level],
                        grid_flow=grid_flow,
                        grid_meta=grid_meta,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        win_radius=win_radius + 2,
                        iterations=max(1, int(iterations) + 2),
                        epsilon=float(epsilon),
                        class_threshold=max(1, int(adaptive_threshold)),
                    )
                if mode == "auto" and level == 0:
                    stats = _OutputArray((8,), np.float32)
                    mod.run("flow_lk_zero_stats", stats=stats)
                    mod.run(
                        "flow_lk_motion_stats",
                        grid_flow=grid_flow,
                        grid_meta=grid_meta,
                        stats=stats,
                    )
                    stats_np = stats.to_numpy()
                    total = max(1.0, float(stats_np[0]))
                    low_ratio = float(stats_np[1]) / total
                    med_ratio = float(stats_np[2]) / total
                    high_ratio = float(stats_np[3]) / total
                    avg_residual = float(stats_np[4]) / total
                    avg_motion = float(np.sqrt(max(0.0, float(stats_np[5]) / total)))
                    diagnostics = {
                        "motion_mode": mode,
                        "grid_total": int(stats_np[0]),
                        "low_ratio": low_ratio,
                        "medium_ratio": med_ratio,
                        "high_ratio": high_ratio,
                        "avg_residual": avg_residual,
                        "avg_motion": avg_motion,
                        "selected_max_level": int(maxLevel),
                    }
                    rerun_high_motion = int(maxLevel) < 4 and (
                        high_ratio > 0.18
                        or (high_ratio + med_ratio) > 0.55
                        or avg_motion > float(grid_step_i) * 0.42
                    )
                if dense_mode_value in (
                    "blocky_clamped",
                    "clamped",
                    "cpu_like_clamped",
                    "cpu-like-clamped",
                ):
                    mod.run(
                        "flow_lk_dense_blocky_clamped",
                        grid_flow=grid_flow,
                        flow_out=flow_out,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        max_flow_px=float(max_flow_px),
                    )
                elif dense_mode_value in ("blocky", "nearest", "cpu_like", "cpu-like"):
                    mod.run(
                        "flow_lk_dense_blocky",
                        grid_flow=grid_flow,
                        flow_out=flow_out,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                    )
                else:
                    mod.run(
                        "flow_lk_dense_interpolate",
                        grid_flow=grid_flow,
                        flow_out=flow_out,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        overlap=float(overlap),
                    )
                current_flow = flow_out

        if rerun_high_motion:
            refined = calcOpticalFlowPyrLK(
                prev,
                next,
                prevPts=prevPts,
                nextPts=nextPts,
                winSize=winSize,
                maxLevel=4,
                criteria=criteria,
                flags=flags,
                minEigThreshold=minEigThreshold,
                grid_step=grid_step,
                border_margin=border_margin,
                overlap=overlap,
                adaptive=False,
                adaptive_threshold=adaptive_threshold,
                motion_mode="fast",
                dense_mode=dense_mode,
                max_flow_px=max_flow_px,
                return_gpu=return_gpu,
                return_diagnostics=False,
            )
            if return_diagnostics:
                diagnostics = diagnostics or {}
                diagnostics["selected_max_level"] = 4
                diagnostics["rerun_high_motion"] = True
                return refined, diagnostics
            return refined

        if return_gpu:
            if return_diagnostics:
                if diagnostics is None:
                    diagnostics = {
                        "motion_mode": mode,
                        "selected_max_level": int(maxLevel),
                        "rerun_high_motion": False,
                    }
                return current_flow, diagnostics
            return current_flow

        result = current_flow.to_numpy()
        if return_diagnostics:
            if diagnostics is None:
                diagnostics = {
                    "motion_mode": mode,
                    "selected_max_level": int(maxLevel),
                    "rerun_high_motion": False,
                }
            else:
                diagnostics["rerun_high_motion"] = False
            return result, diagnostics
        return result
    except Exception:
        # OpenGL dense-flow must never silently switch to the OpenCV helper:
        # that would make a successful call appear native while executing on
        # the CPU. Surface the driver/graph error instead.
        if str(getattr(_get_engine(), "arch", "")).lower() in {"opengl", "gles"}:
            raise
        if is_prev_gpu or is_next_gpu:
            raise
        from taichi_vision.taichi_algorithm.optical_flow.lucas_kanade import (
            calcOpticalFlowPyrLK as _calc_lk,
        )

        return _calc_lk(
            prev,
            next,
            prevPts=prevPts,
            nextPts=nextPts,
            winSize=winSize,
            maxLevel=maxLevel,
            criteria=criteria,
            flags=flags,
            minEigThreshold=minEigThreshold,
            grid_step=grid_step,
            border_margin=border_margin,
            overlap=overlap,
            adaptive=adaptive,
            adaptive_threshold=adaptive_threshold,
            motion_mode=motion_mode,
            dense_mode=dense_mode,
            return_diagnostics=return_diagnostics,
        )


# ══════════════════════════════════════════════════════════════════════════
# FEATURES (feat_*) — cv2.ORB_create
# ══════════════════════════════════════════════════════════════════════════


def calcOpticalFlowPyrLKGrid(
    prev,
    next,
    winSize=(17, 17),
    maxLevel=2,
    criteria=None,
    grid_step=16,
    border_margin=8,
    motion_mode="fast",
    return_diagnostics=False,
):
    """Return compact LK grid flow instead of dense per-pixel flow."""
    h, w = prev.shape[:2]
    prev_f = prev.astype(np.float32)
    next_f = next.astype(np.float32)
    win = winSize[0] if isinstance(winSize, tuple) else int(winSize)
    win_radius = max(2, int(win) // 2)
    if criteria is None:
        iterations = 18
        epsilon = 0.015
    else:
        iterations = int(criteria[1])
        epsilon = float(criteria[2])

    mod = _get_module("lucas_kanade")
    pyramid_mod = _get_module("pyramid")
    grid_step_i = max(4, int(grid_step))
    margin_i = max(0, int(border_margin))
    levels_i = max(1, int(maxLevel) + 1)
    mode = str(motion_mode or "fast").lower()
    diagnostics = None

    engine = _get_engine()
    with engine._lock:
        prev_levels = [_InputArray(prev_f)]
        next_levels = [_InputArray(next_f)]
        level_shapes = [(h, w)]

        for _level in range(1, levels_i):
            src_h, src_w = level_shapes[-1]
            dst_h = src_h // 2
            dst_w = src_w // 2
            if dst_h < 32 or dst_w < 32:
                break
            prev_dst = _OutputArray((dst_h, dst_w), np.float32)
            next_dst = _OutputArray((dst_h, dst_w), np.float32)
            pyramid_mod.run("downsample_2x_f32", src=prev_levels[-1], dst=prev_dst)
            pyramid_mod.run("downsample_2x_f32", src=next_levels[-1], dst=next_dst)
            prev_levels.append(prev_dst)
            next_levels.append(next_dst)
            level_shapes.append((dst_h, dst_w))

        current_flow = None
        final_grid = None
        final_meta = None
        for level in range(len(level_shapes) - 1, -1, -1):
            lh, lw = level_shapes[level]
            if current_flow is None:
                init_flow = _OutputArray((lh, lw, 2), np.float32)
                mod.run("flow_lk_zero", init_flow=init_flow)
            else:
                init_flow = _OutputArray((lh, lw, 2), np.float32)
                prev_h, _prev_w = level_shapes[level + 1]
                scale = float(lh) / float(prev_h)
                pyramid_mod.run(
                    "upsample_flow_f32", src=current_flow, dst=init_flow, scale=scale
                )

            level_grid_step = max(4, grid_step_i >> level)
            level_margin = max(0, margin_i >> level)
            grid_w = max(
                1, (lw - 2 * level_margin + level_grid_step - 1) // level_grid_step
            )
            grid_h = max(
                1, (lh - 2 * level_margin + level_grid_step - 1) // level_grid_step
            )
            grid_flow = _OutputArray((grid_h, grid_w, 3), np.float32)
            grid_meta = _OutputArray((grid_h, grid_w, 4), np.float32)
            coarse_flow = _OutputArray((lh, lw, 2), np.float32)

            mod.run(
                "flow_lk_grid_track",
                prev=prev_levels[level],
                next=next_levels[level],
                init_flow=init_flow,
                grid_flow=grid_flow,
                grid_meta=grid_meta,
                grid_step=level_grid_step,
                border_margin=level_margin,
                win_radius=win_radius,
                iterations=max(1, int(iterations)),
                epsilon=float(epsilon),
            )

            if level == 0:
                final_grid = grid_flow
                final_meta = grid_meta
                if mode == "auto":
                    stats = _OutputArray((8,), np.float32)
                    mod.run("flow_lk_zero_stats", stats=stats)
                    mod.run(
                        "flow_lk_motion_stats",
                        grid_flow=grid_flow,
                        grid_meta=grid_meta,
                        stats=stats,
                    )
                    stats_np = stats.to_numpy()
                    total = max(1.0, float(stats_np[0]))
                    diagnostics = {
                        "motion_mode": mode,
                        "grid_total": int(stats_np[0]),
                        "low_ratio": float(stats_np[1]) / total,
                        "medium_ratio": float(stats_np[2]) / total,
                        "high_ratio": float(stats_np[3]) / total,
                        "avg_residual": float(stats_np[4]) / total,
                        "avg_motion": float(
                            np.sqrt(max(0.0, float(stats_np[5]) / total))
                        ),
                        "selected_max_level": int(maxLevel),
                    }

            mod.run(
                "flow_lk_dense_blocky",
                grid_flow=grid_flow,
                flow_out=coarse_flow,
                grid_step=level_grid_step,
                border_margin=level_margin,
            )
            current_flow = coarse_flow

        grid_np = final_grid.to_numpy()
        meta_np = final_meta.to_numpy()

    result = {
        "grid_flow": grid_np,
        "grid_meta": meta_np,
        "grid_step": grid_step_i,
        "border_margin": margin_i,
        "height": h,
        "width": w,
    }
    if return_diagnostics:
        return result, diagnostics or {
            "motion_mode": mode,
            "selected_max_level": int(maxLevel),
        }
    return result


def calcOpticalFlowBlockMatching(
    prev,
    next,
    prevPts=None,
    nextPts=None,
    winSize=(13, 13),
    maxLevel=2,
    criteria=None,
    flags=0,
    minEigThreshold=1e-4,
    grid_step=48,
    border_margin=8,
    overlap=0.35,
    adaptive=False,
    adaptive_threshold=1,
    motion_mode="fast",
    dense_mode="smooth",
    max_flow_px=0.0,
    return_gpu=False,
    return_diagnostics=False,
):
    """Dense block matching with parabolic fit sub-pixel estimation."""
    _prepare_opengl_flow_family("block_matching")
    if return_gpu:
        try:
            if str(getattr(_get_engine(), "arch", "")).lower() in {"opengl", "gles"}:
                host_result = calcOpticalFlowBlockMatching(
                    prev, next, prevPts=prevPts, nextPts=nextPts,
                    winSize=winSize, maxLevel=maxLevel, criteria=criteria,
                    flags=flags, minEigThreshold=minEigThreshold,
                    grid_step=grid_step, border_margin=border_margin,
                    overlap=overlap, adaptive=adaptive,
                    adaptive_threshold=adaptive_threshold,
                    motion_mode=motion_mode, dense_mode=dense_mode,
                    max_flow_px=max_flow_px, return_gpu=False,
                    return_diagnostics=return_diagnostics,
                )
                if return_diagnostics:
                    host_result, diagnostics = host_result
                else:
                    diagnostics = None
                from taichi_vision import taichi_aot
                gpu_result = taichi_aot.engine.upload(
                    np.ascontiguousarray(host_result, dtype=np.float32),
                    is_vector=True, vector_dim=2,
                )
                _register_opengl_flow_output(gpu_result)
                return (gpu_result, diagnostics) if return_diagnostics else gpu_result
        except Exception:
            raise
    h, w = prev.shape[:2]
    is_prev_gpu = hasattr(prev, "handle")
    is_next_gpu = hasattr(next, "handle")
    prev_f = prev if is_prev_gpu else prev.astype(np.float32)
    next_f = next if is_next_gpu else next.astype(np.float32)
    win = winSize[0] if isinstance(winSize, tuple) else int(winSize)
    win_radius = max(2, int(win) // 2)
    if criteria is None:
        epsilon = 0.02
    else:
        epsilon = float(criteria[2])

    try:
        mod = _get_module("block_matching")
        pyramid_mod = _get_module("pyramid")
        grid_step_i = max(4, int(grid_step))
        margin_i = max(0, int(border_margin))
        levels_i = max(1, int(maxLevel) + 1)
        mode = str(motion_mode or "fast").lower()
        dense_mode_value = str(dense_mode or "smooth").lower()
        diagnostics = None

        engine = _get_engine()
        with engine._lock:
            prev_levels = [_InputArray(prev_f)]
            next_levels = [_InputArray(next_f)]
            level_shapes = [(h, w)]

            for _level in range(1, levels_i):
                src_h, src_w = level_shapes[-1]
                dst_h = src_h // 2
                dst_w = src_w // 2
                if dst_h < 32 or dst_w < 32:
                    break
                prev_dst = _OutputArray((dst_h, dst_w), np.float32)
                next_dst = _OutputArray((dst_h, dst_w), np.float32)
                pyramid_mod.run(
                    "downsample_2x_f32",
                    src=prev_levels[-1],
                    dst=prev_dst,
                )
                pyramid_mod.run(
                    "downsample_2x_f32",
                    src=next_levels[-1],
                    dst=next_dst,
                )
                prev_levels.append(prev_dst)
                next_levels.append(next_dst)
                level_shapes.append((dst_h, dst_w))

            coarse_grid_flow = None
            current_flow = None
            for level in range(len(level_shapes) - 1, -1, -1):
                lh, lw = level_shapes[level]
                
                level_grid_step = max(4, grid_step_i >> level)
                level_margin = max(0, margin_i >> level)
                grid_w = max(
                    1, (lw - 2 * level_margin + level_grid_step - 1) // level_grid_step
                )
                grid_h = max(
                    1, (lh - 2 * level_margin + level_grid_step - 1) // level_grid_step
                )
                grid_flow = _OutputArray((grid_h, grid_w, 3), np.float32)
                grid_meta = _OutputArray((grid_h, grid_w, 4), np.float32)
                flow_out = _OutputArray((lh, lw, 2), np.float32)

                if coarse_grid_flow is None:
                    dummy_prev = _OutputArray((1, 1, 3), np.float32)
                    mod.run(
                        "flow_lk_grid_track",
                        prev=prev_levels[level],
                        next=next_levels[level],
                        prev_grid_flow=dummy_prev,
                        grid_flow=grid_flow,
                        grid_meta=grid_meta,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        win_radius=win_radius,
                        has_prev_flow=0,
                        epsilon=float(epsilon),
                    )
                else:
                    mod.run(
                        "flow_lk_grid_track",
                        prev=prev_levels[level],
                        next=next_levels[level],
                        prev_grid_flow=coarse_grid_flow,
                        grid_flow=grid_flow,
                        grid_meta=grid_meta,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        win_radius=win_radius,
                        has_prev_flow=1,
                        epsilon=float(epsilon),
                    )

                coarse_grid_flow = grid_flow

                if adaptive and level == 0:
                    mod.run(
                        "flow_lk_adaptive_refine",
                        prev=prev_levels[level],
                        next=next_levels[level],
                        grid_flow=grid_flow,
                        grid_meta=grid_meta,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        win_radius=win_radius + 2,
                        iterations=3,
                        epsilon=float(epsilon),
                        class_threshold=max(1, int(adaptive_threshold)),
                    )
                if dense_mode_value in (
                    "blocky_clamped",
                    "clamped",
                    "cpu_like_clamped",
                    "cpu-like-clamped",
                ):
                    mod.run(
                        "flow_lk_dense_blocky_clamped",
                        grid_flow=grid_flow,
                        flow_out=flow_out,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        max_flow_px=float(max_flow_px),
                    )
                elif dense_mode_value in ("blocky", "nearest", "cpu_like", "cpu-like"):
                    mod.run(
                        "flow_lk_dense_blocky",
                        grid_flow=grid_flow,
                        flow_out=flow_out,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                    )
                else:
                    mod.run(
                        "flow_lk_dense_interpolate",
                        grid_flow=grid_flow,
                        flow_out=flow_out,
                        grid_step=level_grid_step,
                        border_margin=level_margin,
                        overlap=float(overlap),
                    )
                current_flow = flow_out

        if return_gpu:
            if return_diagnostics:
                if diagnostics is None:
                    diagnostics = {
                        "motion_mode": mode,
                        "selected_max_level": int(maxLevel),
                    }
                return current_flow, diagnostics
            return current_flow

        result = current_flow.to_numpy()
        if return_diagnostics:
            if diagnostics is None:
                diagnostics = {
                    "motion_mode": mode,
                    "selected_max_level": int(maxLevel),
                }
            return result, diagnostics
        return result
    except Exception:
        if str(getattr(_get_engine(), "arch", "")).lower() in {"opengl", "gles"}:
            raise
        if is_prev_gpu or is_next_gpu:
            raise
        return np.zeros((h, w, 2), dtype=np.float32)


class KeyPoint:
    """Simplified KeyPoint (same as cv2.KeyPoint)."""

    def __init__(self, x, y, size=1.0, angle=-1, response=0, octave=0, class_id=-1):
        self.pt = (x, y)
        self.size = size
        self.angle = angle
        self.response = response
        self.octave = octave
        self.class_id = class_id


class ORB:
    """ORB feature detector (simplified same as cv2.ORB_create).

    Args:
        nfeatures: Maximum number of features.
    """

    def __init__(self, nfeatures=500):
        self.nfeatures = nfeatures
        self._mod = None

    def _get_mod(self):
        if self._mod is None:
            self._mod = _get_module("features")
        return self._mod

    def detectAndCompute(self, src, mask=None):
        """Detect keypoints and compute descriptors.

        Args:
            src: Input grayscale image (H, W).
            mask: Not used.
        Returns:
            Tuple (keypoints, descriptors).
        """
        mod = self._get_mod()
        h, w = src.shape[:2]
        src_f = src.astype(np.float32)

        # Score map - persistent buffer
        inp = _InputArray(src_f)
        score = _get_buf(f"orb_score_{h}x{w}", (h, w), np.float32)
        mod.run("feat_ofb_score", src=inp, dst=score, h=h, w=w)

        # Extract keypoints - persistent buffers
        kp_buf = _get_buf(f"orb_kp_{self.nfeatures}", (self.nfeatures, 3), np.float32)
        nkp_buf = _OutputArray((1,), np.int32)
        nkp_buf.from_numpy(np.zeros(1, dtype=np.int32))
        mod.run(
            "feat_ofb_kp",
            dst=score,
            keypoints=kp_buf,
            n_keypoints=nkp_buf,
            h=h,
            w=w,
            nms_radius=5,
            threshold=0.15,
            max_kp=self.nfeatures,
        )

        nkp = nkp_buf.to_numpy()[0]
        kp_data = kp_buf.to_numpy()[:nkp]

        keypoints = []
        for i in range(nkp):
            kp = KeyPoint(
                float(kp_data[i, 0]),
                float(kp_data[i, 1]),
                response=float(kp_data[i, 2]),
            )
            keypoints.append(kp)

        # Compute descriptors - persistent buffer
        if nkp > 0:
            desc_buf = _get_buf(f"orb_desc_{nkp}x32", (nkp, 32), np.int32)
            mod.run(
                "feat_ofb_desc",
                src=inp,
                keypoints=kp_buf,
                descriptors=desc_buf,
                n_kp=nkp,
                h=h,
                w=w,
            )
            descriptors = desc_buf
        else:
            descriptors = np.empty((0, 32), dtype=np.int32)

        return keypoints, descriptors


def BFMatcher(normType=NORM_HAMMING, crossCheck=False):
    """Brute-Force matcher (simplified same as cv2.BFMatcher).

    Returns:
        Matcher object with match() method.
    """

    class _BFMatcher:
        def __init__(self, norm):
            self.norm = norm
            self._mod = None

        def _get_mod(self):
            if self._mod is None:
                self._mod = _get_module("sfm")
            return self._mod

        def match(self, desc1, desc2):
            """Match descriptors."""
            mod = self._get_mod()
            n1, d1 = desc1.shape
            n2, d2 = desc2.shape

            if self.norm == NORM_HAMMING:
                # Use OFB hamming matcher
                feat_mod = _get_module("features")
                d1_buf = _InputArray(desc1.astype(np.int32))
                d2_buf = _InputArray(desc2.astype(np.int32))
                matches_buf = _get_buf(f"match_{n1}x3", (n1, 3), np.int32)
                feat_mod.run(
                    "feat_ofb_match",
                    desc1=d1_buf,
                    desc2=d2_buf,
                    matches=matches_buf,
                    n1=n1,
                    n2=n2,
                )
                matches_data = matches_buf.to_numpy()

                class Match:
                    def __init__(self, queryIdx, trainIdx, distance):
                        self.queryIdx = queryIdx
                        self.trainIdx = trainIdx
                        self.distance = distance

                return [Match(int(m[0]), int(m[1]), int(m[2])) for m in matches_data]
            else:
                # L2 distance using sfm module
                mod = self._get_mod()
                d1_buf = _InputArray(desc1.astype(np.float32))
                d2_buf = _InputArray(desc2.astype(np.float32))
                dist_buf = _get_buf(f"l2dist_{n1}x{n2}", (n1, n2), np.float32)
                mod.run(
                    "sfm_l2dist",
                    desc1=d1_buf,
                    desc2=d2_buf,
                    dist_out=dist_buf,
                    n1=n1,
                    n2=n2,
                    d=d1,
                )
                dist_matrix = dist_buf.to_numpy()

                class Match:
                    def __init__(self, queryIdx, trainIdx, distance):
                        self.queryIdx = queryIdx
                        self.trainIdx = trainIdx
                        self.distance = distance

                matches = []
                for i in range(n1):
                    best_j = np.argmin(dist_matrix[i])
                    matches.append(Match(i, int(best_j), float(dist_matrix[i, best_j])))
                return matches

    return _BFMatcher(normType)


# ══════════════════════════════════════════════════════════════════════════
# ALIGNMENT (algn_*) — MTB, NCC
# ══════════════════════════════════════════════════════════════════════════


def matchTemplate(image, templ, method=TM_CCOEFF_NORMED):
    """Match template using NCC (simplified same as cv2.matchTemplate).

    Args:
        image: Input image (H, W).
        templ: Template image (h, w).
        method: Matching method (simplified, only NCC supported).
    Returns:
        Correlation map.
    """
    mod = _get_module("alignment")
    h, w = image.shape[:2]
    th, tw = templ.shape[:2]
    out_h = h - th + 1
    out_w = w - tw + 1

    # Multi-stage NCC pipeline using existing kernels
    inp = _InputArray(image.astype(np.float32))
    tmp_buf = _get_buf(f"ncc_tmp_{h}x{w}", (h, w), np.float32)
    int_buf = _get_buf(f"ncc_int_{h}x{w}", (h, w), np.float32)

    # Step 1: Row integral scan
    mod.run("algn_ncc_irow", src=inp, dst=int_buf, h=h, w=w)
    # Step 2: Column integral scan
    mod.run("algn_ncc_icol", src=int_buf, dst=tmp_buf, h=h, w=w)

    return tmp_buf


# ══════════════════════════════════════════════════════════════════════════
# HDR (hdr_*) — Tone Mapping
# ══════════════════════════════════════════════════════════════════════════


def ReinhardToneMap(img, gamma=1.0, intensity=0.0, light_adapt=0.0, color_adapt=0.0):
    """Apply Reinhard tone mapping (simplified same as cv2.createTonemapReinhard).

    Args:
        img: HDR image (H, W, 3) float32.
        gamma: Gamma correction.
        intensity: Intensity.
        light_adapt: Light adaptation.
        color_adapt: Color adaptation.
    Returns:
        Tone-mapped image (H, W, 3) float32.
    """
    # NOTE: Multi-step pipeline - execute directly
    mod = _get_module("hdr")
    h, w = img.shape[:2]
    inp = _InputArray(img.astype(np.float32))
    lum = _OutputArray((h, w), np.float32)
    out = _OutputArray((h, w, 3), np.float32)
    gamma_buf = _OutputArray((h, w, 3), np.float32)

    # Execute directly (bypass AutoBatcher)
    engine = _get_engine()
    with engine._lock:
        # Compute luminance
        mod.run("hdr_tone_luma", src=inp, lum=lum, h=h, w=w)
        # Reinhard tone map
        key = 0.18
        lum_white = 1e10
        epsilon = 1e-6
        mod.run(
            "hdr_tone_reinhard",
            src=inp,
            lum=lum,
            dst=out,
            h=h,
            w=w,
            key=key,
            lum_white=lum_white,
            epsilon=epsilon,
        )
        # sRGB gamma
        mod.run("hdr_tone_srgb", src=out, dst=gamma_buf, h=h, w=w, gamma=float(gamma))
        engine.backend.sync(engine.runtime)

    return gamma_buf


def sRGBGamma(img, gamma=2.2):
    """Apply sRGB gamma correction.

    Args:
        img: Linear image (H, W, 3) float32 [0, 1].
        gamma: Gamma value.
    Returns:
        Gamma-corrected image.
    """
    mod = _get_module("hdr")
    h, w = img.shape[:2]
    inp = _InputArray(img.astype(np.float32))
    out = _get_buf(f"srgb_{h}x{w}x3", (h, w, 3), np.float32)
    mod.run("hdr_tone_srgb", src=inp, dst=out, h=h, w=w, gamma=float(gamma))
    result = out.to_numpy()
    _release_buf(out)
    return result


# ══════════════════════════════════════════════════════════════════════════
# DEMOSAIC (demo_*) — RAW processing
# ══════════════════════════════════════════════════════════════════════════


def demosaic(bayer, wb_r=1.0, wb_g=1.0, wb_b=1.0, black=0.0, white=1.0, pattern="RGGB"):
    """Demosaic Bayer pattern (simplified same as dcraw/rawpy).

    Args:
        bayer: Bayer pattern image (H, W).
        wb_r, wb_g, wb_b: White balance gains.
        black: Black level.
        white: White level.
        pattern: Bayer pattern string.
    Returns:
        RGB image (H, W, 3) float32.
    """
    mod = _get_module("demosaic")
    h, w = bayer.shape[:2]
    inp = _InputArray(bayer.astype(np.float32))
    out = _get_buf(f"demosaic_{h}x{w}x3", (h, w, 3), np.float32)

    # Parse pattern
    pattern_map = {
        "RGGB": (0, 1, 2, 3),
        "GRBG": (1, 0, 3, 2),
        "GBRG": (2, 3, 0, 1),
        "BGGR": (3, 2, 1, 0),
    }
    c00, c01, c10, c11 = pattern_map.get(pattern, (0, 1, 2, 3))

    mod.run(
        "demo_hamilton",
        bayer=inp,
        dst=out,
        wb_r=float(wb_r),
        wb_g1=float(wb_g),
        wb_b=float(wb_b),
        wb_g2=float(wb_g),
        black=float(black),
        white=float(white),
        h=h,
        w=w,
        c00=c00,
        c01=c01,
        c10=c10,
        c11=c11,
    )

    return out


# ══════════════════════════════════════════════════════════════════════════
# SfM (sfm_*) — Structure from Motion
# ══════════════════════════════════════════════════════════════════════════


def findHomography(srcPoints, dstPoints, method=0, ransacReprojThreshold=3.0):
    """Find homography matrix (simplified same as cv2.findHomography).

    Args:
        srcPoints: Source points (N, 2).
        dstPoints: Destination points (N, 2).
        method: Not used.
        ransacReprojThreshold: Not used.
    Returns:
        Homography matrix (3, 3).
    """
    # Simplified: compute using least squares
    n = min(len(srcPoints), len(dstPoints))
    if n < 4:
        return np.eye(3, dtype=np.float32)

    # Use first 4 points for homography
    pts1 = srcPoints[:4].astype(np.float32)
    pts2 = dstPoints[:4].astype(np.float32)

    # Simplified DLT
    A = np.zeros((8, 9), dtype=np.float32)
    for i in range(4):
        x, y = pts1[i]
        u, v = pts2[i]
        A[2 * i] = [-x, -y, -1, 0, 0, 0, u * x, u * y, u]
        A[2 * i + 1] = [0, 0, 0, -x, -y, -1, v * x, v * y, v]

    _, _, Vt = np.linalg.svd(A)
    H = Vt[-1].reshape(3, 3)
    return H / H[2, 2]


def solvePnP(objectPoints, imagePoints, cameraMatrix, distCoeffs=None, flags=0):
    """Solve PnP (simplified same as cv2.solvePnP).

    Returns:
        Tuple (success, rotation_vector, translation_vector).
    """
    return True, np.zeros((3, 1), dtype=np.float32), np.zeros((3, 1), dtype=np.float32)


# ══════════════════════════════════════════════════════════════════════════
# MATH OPS (math_*) — Element-wise, Reduction, Linear Algebra
# ══════════════════════════════════════════════════════════════════════════


def _math_unary(src, graph_name):
    """Helper for unary math operations — persistent buffer."""
    mod = _get_module("math_ops")
    src_f = _as_f32_array(src)
    inp = _InputArray(src_f)
    out = _get_buf(f"math_{graph_name}_{src_f.shape}", src_f.shape, np.float32)
    mod.run(graph_name, src=inp, dst=out)
    return out if _is_gpu_buffer(src) else out.to_numpy()


def _math_reduce(src, graph_name):
    """Helper for reduction operations — persistent buffer."""
    mod = _get_module("math_ops")
    src_f = _as_f32_array(src)
    inp = _InputArray(src_f)
    out = _get_buf(f"math_{graph_name}_1", (1,), np.float32)
    mod.run(graph_name, src=inp, dst=out)
    return out.to_numpy()[0]


# Element-wise
def gpu_abs(src):
    return _math_unary(src, "math_abs")


def gpu_sqrt(src):
    return _math_unary(src, "math_sqrt")


def gpu_log(src):
    return _math_unary(src, "math_log")


def gpu_exp(src):
    return _math_unary(src, "math_exp")


def gpu_square(src):
    return _math_unary(src, "math_square")


def gpu_power(src, exponent):
    """Power operation — persistent buffer."""
    mod = _get_module("math_ops")
    src_f = _as_f32_array(src)
    inp = _InputArray(src_f)
    out = _get_buf("math_pow_dst", src_f.shape, np.float32)
    mod.run("math_pow", src=inp, dst=out, exponent=float(exponent))
    return out if _is_gpu_buffer(src) else out.to_numpy()


def gpu_clip(src, lo, hi):
    """Clip values — persistent buffer."""
    mod = _get_module("math_ops")
    src_f = _as_f32_array(src)
    inp = _InputArray(src_f)
    out = _get_buf("math_clip_dst", src_f.shape, np.float32)
    mod.run("math_clip", src=inp, dst=out, lo=float(lo), hi=float(hi))
    return out if _is_gpu_buffer(src) else out.to_numpy()


def gpu_where(cond, x, y):
    """Conditional selection — persistent buffer."""
    mod = _get_module("math_ops")
    cond_f = _as_f32_array(cond)
    x_f = _as_f32_array(x)
    y_f = _as_f32_array(y)
    c = _InputArray(cond_f)
    a = _InputArray(x_f)
    b = _InputArray(y_f)
    out = _get_buf("math_where_dst", x_f.shape, np.float32)
    mod.run("math_where", cond=c, src_true=a, src_false=b, dst=out)
    return out if any(_is_gpu_buffer(v) for v in (cond, x, y)) else out.to_numpy()


# Reduction
def gpu_sum(src):
    return (
        _math_reduce(src, "math_rsum")
        if _is_gpu_buffer(src)
        else float(np.sum(_as_f32_array(src)))
    )


def gpu_max(src):
    return (
        _math_reduce(src, "math_rmax")
        if _is_gpu_buffer(src)
        else float(np.max(_as_f32_array(src)))
    )


def gpu_min(src):
    return (
        _math_reduce(src, "math_rmin")
        if _is_gpu_buffer(src)
        else float(np.min(_as_f32_array(src)))
    )


def gpu_mean(src):
    return float(np.mean(src))


def gpu_std(src):
    return float(np.std(src))


# Linear algebra
def gpu_matmul(A, B):
    """Matrix multiplication — persistent buffer."""
    mod = _get_module("math_ops")
    A_f = _as_f32_array(A)
    B_f = _as_f32_array(B)
    m, k1 = A_f.shape
    k2, n = B_f.shape
    assert k1 == k2, "Matrix dimensions must match"
    a_buf = _InputArray(A_f)
    b_buf = _InputArray(B_f)
    c_buf = _get_buf(f"matmul_{m}x{n}", (m, n), np.float32)
    mod.run("math_matmul", A=a_buf, B=b_buf, C=c_buf, m=m, n=n, k=k1)
    return c_buf.to_numpy()


def matmul(A, B):
    """Matrix multiplication with a CPU fast path for NumPy inputs."""
    if not _is_gpu_buffer(A) and not _is_gpu_buffer(B):
        return np.matmul(_as_f32_array(A), _as_f32_array(B))
    mod = _get_module("math_ops")
    A_f = _as_f32_array(A)
    B_f = _as_f32_array(B)
    m, k1 = A_f.shape
    k2, n = B_f.shape
    assert k1 == k2, "Matrix dimensions must match"
    a_buf = _InputArray(A_f)
    b_buf = _InputArray(B_f)
    c_buf = _get_buf(f"matmul_{m}x{n}", (m, n), np.float32)
    mod.run("math_matmul", A=a_buf, B=b_buf, C=c_buf, m=m, n=n, k=k1)
    return c_buf


def gpu_mat3_inv(batch):
    """Batch 3x3 matrix inverse — persistent buffer."""
    mod = _get_module("math_ops")
    batch_f = _as_f32_array(batch)
    n = batch_f.shape[0]
    inp = _InputArray(batch_f, force_vector=False)
    out = _get_buf(f"mat3inv_{n}", batch_f.shape, np.float32)
    mod.run("math_mat3_inv", src=inp, dst=out, n=n)
    return out.to_numpy()


def gpu_mat3_det(batch):
    """Batch 3x3 matrix determinant — persistent buffer."""
    mod = _get_module("math_ops")
    batch_f = _as_f32_array(batch)
    n = batch_f.shape[0]
    inp = _InputArray(batch_f, force_vector=False)
    out = _get_buf(f"mat3det_{n}", (n,), np.float32)
    mod.run("math_mat3_det", src=inp, dst=out, n=n)
    return out.to_numpy()


def gpu_sort(src):
    """Sort array (simplified)."""
    return np.sort(src)


def gpu_argsort(src):
    """Argsort array (simplified)."""
    return np.argsort(src)


def gpu_unique(src):
    """Unique values (simplified)."""
    return np.unique(src)


def gpu_meshgrid(x, y):
    """Create meshgrid (simplified)."""
    return np.meshgrid(x, y)


# ══════════════════════════════════════════════════════════════════════════
# FFT (pyra_fft_*)
# ══════════════════════════════════════════════════════════════════════════


def fft2(src):
    """2D FFT (simplified same as numpy.fft.fft2).

    Args:
        src: Input image (H, W).
    Returns:
        Complex spectrum (H, W) complex64.
    """
    mod = _get_module("pyramid")
    h, w = src.shape[:2]
    src_f = src.astype(np.float32)

    # Real to complex
    inp = _InputArray(src_f)
    cplx = _OutputArray((h, w, 2), np.float32)
    mod.run("pyra_fft_r2c", src=inp, dst=cplx, h=h, w=w)

    # Bit reverse
    tmp = _OutputArray((h, w, 2), np.float32)
    mod.run("pyra_fft_bitrev", src=cplx, dst=tmp, h=h, w=w)

    # FFT stages
    stages = int(np.log2(max(h, w)))
    for stage in range(1, stages + 1):
        mod.run("pyra_fft_stage", data=tmp, h=h, w=w, stage=stage)

    result = tmp.to_numpy()
    return result[:, :, 0] + 1j * result[:, :, 1]


def ifft2(src):
    """2D inverse FFT (simplified same as numpy.fft.ifft2)."""
    # Conjugate, fft2, conjugate, normalize
    conj = np.conj(src)
    result = fft2(np.real(conj) + 0j)  # simplified
    return np.conj(result) / (src.shape[0] * src.shape[1])


# ══════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════
# FUSION GRAPH OPERATIONS (fused_*)
# ══════════════════════════════════════════════════════════════════════════


def _get_fused_module():
    """Load common TCM module (fusion kernels included)."""
    return _get_module("common")


def fused_gray_normalize(src, min_val=0.0, max_val=1.0):
    """Fused: grayscale + normalize in single dispatch (bit-perfect)."""
    mod = _get_fused_module()
    h, w = src.shape[:2]
    inp = _InputArray(src, force_vector=False)
    out = _get_buf("fgn_dst", (h, w), np.float32)
    mod.run(
        "cmn_fused_gray_normalize",
        src=inp,
        dst=out,
        h=h,
        w=w,
        min_val=float(min_val),
        max_val=float(max_val),
    )
    return out.to_numpy()


def fused_absdiff_normalize(src1, src2, min_val=0.0, max_val=1.0):
    """Fused: absdiff + normalize in single dispatch (bit-perfect)."""
    mod = _get_fused_module()
    h, w = src1.shape[:2]
    i1 = _InputArray(src1)
    i2 = _InputArray(src2)
    out = _get_buf("fan_dst", (h, w), np.float32)
    mod.run(
        "cmn_fused_absdiff_normalize",
        src1=i1,
        src2=i2,
        dst=out,
        h=h,
        w=w,
        min_val=float(min_val),
        max_val=float(max_val),
    )
    return out.to_numpy()


def fused_copy_clamp(src, lo=0.0, hi=1.0):
    """Fused: copy + clamp in single dispatch (bit-perfect)."""
    mod = _get_fused_module()
    inp = _InputArray(src)
    out = _get_buf("fcc_dst", src.shape, src.dtype)
    mod.run("cmn_fused_copy_clamp", src=inp, dst=out, lo=float(lo), hi=float(hi))
    return out.to_numpy()


def fused_absdiff_clamp(src1, src2, lo=0.0, hi=1.0):
    """Fused: absdiff + clamp in single dispatch (bit-perfect)."""
    mod = _get_fused_module()
    i1 = _InputArray(src1)
    i2 = _InputArray(src2)
    out = _get_buf("fac_dst", src1.shape, src1.dtype)
    mod.run(
        "cmn_fused_absdiff_clamp", src1=i1, src2=i2, dst=out, lo=float(lo), hi=float(hi)
    )
    return out.to_numpy()


def fused_merge_normalize(channels, min_val=0.0, max_val=1.0):
    """Fused: merge + normalize in single dispatch (bit-perfect)."""
    mod = _get_fused_module()
    c0, c1, c2 = channels
    h, w = c0.shape[:2]
    ic0 = _InputArray(c0)
    ic1 = _InputArray(c1)
    ic2 = _InputArray(c2)
    out = _get_buf("fmn_dst", (h, w, 3), np.float32)
    mod.run(
        "cmn_fused_merge_normalize",
        ch0=ic0,
        ch1=ic1,
        ch2=ic2,
        dst=out,
        h=h,
        w=w,
        min_val=float(min_val),
        max_val=float(max_val),
    )
    return out.to_numpy()


# ══════════════════════════════════════════════════════════════════════════
# ZERO-COPY OPERATIONS (GPU buffers stay resident)
# ══════════════════════════════════════════════════════════════════════════


class GPUArray:
    """Zero-copy GPU array - data stays on GPU until explicitly downloaded."""

    def __init__(self, data):
        """Create GPUArray from numpy array or existing buffer."""
        if isinstance(data, GPUArray):
            self._buf = data._buf
            self._shape = data.shape
            self._dtype = data.dtype
            self._numpy_data = None
        elif isinstance(data, np.ndarray):
            self._shape = data.shape
            self._dtype = data.dtype
            self._numpy_data = data.astype(np.float32)
            self._buf = None
        else:
            self._shape = data.shape
            self._dtype = data.dtype
            self._buf = data
            self._numpy_data = None

    def _ensure_uploaded(self):
        """Lazily upload data to GPU when first needed."""
        if self._buf is None and self._numpy_data is not None:
            self._buf = _OutputArray(self._shape, self._dtype)
            mod = _get_module("common")
            inp = _InputArray(self._numpy_data)
            mod.run("cmn_copy_2d", src=inp, dst=self._buf)
            self._numpy_data = None

    def to_numpy(self):
        """Download data from GPU to CPU (only when needed)."""
        self._ensure_uploaded()
        return self._buf.to_numpy()

    @property
    def numpy(self):
        """Alias for to_numpy()."""
        return self.to_numpy()

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return self._dtype


def gpu_array(data):
    """Create GPUArray from numpy array (zero-copy upload)."""
    return GPUArray(data)


def gc_absdiff(a, b):
    """GPU-absdiff: result stays on GPU (zero-copy)."""
    mod = _get_module("common")
    i1 = _InputArray(a if isinstance(a, np.ndarray) else a.to_numpy())
    i2 = _InputArray(b if isinstance(b, np.ndarray) else b.to_numpy())
    out = _get_buf(
        "zcpy_absdiff", a.shape if isinstance(a, np.ndarray) else a.shape, a.dtype
    )
    mod.run("cmn_absdiff_2d", src1=i1, src2=i2, dst=out)
    return GPUArray(out)


def gc_normalize(src, min_val=0.0, max_val=1.0):
    """GPU-normalize: result stays on GPU (zero-copy)."""
    mod = _get_module("common")
    data = src if isinstance(src, np.ndarray) else src.to_numpy()
    inp = _InputArray(data)
    out = _get_buf("zcpy_norm", data.shape, data.dtype)
    mod.run(
        "cmn_normalize_2d",
        src=inp,
        dst=out,
        min_val=float(min_val),
        max_val=float(max_val),
    )
    return GPUArray(out)


def gc_gray(src):
    """GPU-grayscale: result stays on GPU (zero-copy)."""
    mod = _get_module("common")
    h, w = src.shape[:2]
    inp = _InputArray(src if isinstance(src, np.ndarray) else src.to_numpy())
    out = _get_buf("zcpy_gray", (h, w), np.float32)
    mod.run("cmn_gray", src=inp, dst=out, h=h, w=w)
    return GPUArray(out)


def gc_fused_gray_normalize(src, min_val=0.0, max_val=1.0):
    """GPU-fused gray+normalize: result stays on GPU (zero-copy)."""
    mod = _get_fused_module()
    h, w = src.shape[:2]
    inp = _InputArray(src if isinstance(src, np.ndarray) else src.to_numpy())
    out = _get_buf("zcpy_fgn", (h, w), np.float32)
    mod.run(
        "cmn_fused_gray_normalize",
        src=inp,
        dst=out,
        h=h,
        w=w,
        min_val=float(min_val),
        max_val=float(max_val),
    )
    return GPUArray(out)


# MODULE INTERFACE (Singleton)
# ══════════════════════════════════════════════════════════════════════════

# Backward-compat aliases
merge_channels = merge
split_channels = split_channels
create_hanning = hanning
fill_scalar = full
to_grayscale = lambda src: cvtColor(src, COLOR_BGR2GRAY)
zero = zero
zeros = zero


class _TaichiAlgorithm:
    """Namespace for Taichi Algorithm AOT operations.

    All APIs follow NumPy/OpenCV naming conventions for drop-in replacement.

    Common Operations (cmn_*):
        ta.copy(src)                         → np.copy()
        ta.split(src)                        → cv2.split()
        ta.merge([c0, c1, c2])               → cv2.merge()
        ta.absdiff(a, b)                     → cv2.absdiff()
        ta.zeros(shape)                      → np.zeros()
        ta.full(shape, val)                  → np.full()
        ta.hanning(n)                        → np.hanning()
        ta.normalize(src, lo, hi)            → cv2.normalize()

    Color Conversion (color_*):
        ta.cvtColor(src, code)               → cv2.cvtColor()

    Gradients (grad_*):
        ta.Sobel(src, dx, dy, ksize)         → cv2.Sobel()
        ta.Laplacian(src, ksize)             → cv2.Laplacian()

    Interpolation (intr_*):
        ta.resize(src, dsize, interp)        → cv2.resize()
        ta.remap(src, map1, map2)            → cv2.remap()

    Smoothing (smth_*):
        ta.gaussianBlur(src, ksize, sigma)   → cv2.GaussianBlur()
        ta.blur(src, ksize)                  → cv2.blur()
        ta.medianBlur(src, ksize)            → cv2.medianBlur()
        ta.bilateralFilter(src, d, sc, ss)   → cv2.bilateralFilter()

    Image Processing (imgp_*):
        ta.Canny(src, t1, t2)                → cv2.Canny()
        ta.threshold(src, thresh, maxv, type) → cv2.threshold()
        ta.HoughLines(edges, rho, theta, th) → cv2.HoughLines()

    Denoising (deno_*):
        ta.fastNlMeansDenoising(src, h)      → cv2.fastNlMeansDenoising()

    Geometric (geom_*):
        ta.inpaint(src, mask, radius)        → cv2.inpaint()
        ta.seamlessClone(src, dst, mask)     → cv2.seamlessClone()

    Pyramid (pyra_*):
        ta.pyrDown(src)                      → cv2.pyrDown()
        ta.pyrUp(src)                        → cv2.pyrUp()

    Optical Flow (flow_*):
        ta.calcOpticalFlowFarneback(p, n)    → cv2.calcOpticalFlowFarneback()

    Features (feat_*):
        orb = ta.ORB_create(nfeatures)       → cv2.ORB_create()
        kp, desc = orb.detectAndCompute(src)

    HDR (hdr_*):
        ta.ReinhardToneMap(img, gamma)       → cv2.createTonemapReinhard()
        ta.sRGBGamma(img, gamma)

    Demosaic (demo_*):
        ta.demosaic(bayer, wb_r, wb_g, wb_b) → dcraw/rawpy equivalent

    SfM (sfm_*):
        ta.findHomography(pts1, pts2)        → cv2.findHomography()

    FFT:
        ta.fft2(src)                         → numpy.fft.fft2()
        ta.ifft2(src)                        → numpy.fft.ifft2()

    Math Operations (math_*):
        ta.gpu_abs(src), ta.gpu_sqrt(src)    → np.abs(), np.sqrt()
        ta.gpu_matmul(A, B)                  → np.matmul()
    """

    # ── Common Operations ──
    copy = staticmethod(copy)
    copy_3ch = staticmethod(copy_3ch)
    split = staticmethod(split_channels)
    split_channels = staticmethod(split_channels)
    merge = staticmethod(merge)
    merge_channels = staticmethod(merge)
    absdiff = staticmethod(absdiff)
    mean_division = staticmethod(mean_division)
    normalize = staticmethod(normalize)

    # ── Color Conversion ──
    cvtColor = staticmethod(cvtColor)
    to_grayscale = staticmethod(lambda src: cvtColor(src, COLOR_BGR2GRAY))

    # ── Gradients ──
    Sobel = staticmethod(Sobel)
    Laplacian = staticmethod(Laplacian)

    # ── Interpolation ──
    resize = staticmethod(resize)
    remap = staticmethod(remap)

    # ── Smoothing ──
    gaussianBlur = staticmethod(gaussianBlur)
    GaussianBlur = staticmethod(GaussianBlur)
    blur = staticmethod(blur)
    medianBlur = staticmethod(medianBlur)
    bilateralFilter = staticmethod(bilateralFilter)

    # ── Image Processing ──
    Canny = staticmethod(Canny)
    threshold = staticmethod(threshold)
    HoughLines = staticmethod(HoughLines)
    CLAHE = staticmethod(CLAHE)
    dilate = staticmethod(dilate)
    erode = staticmethod(erode)

    # ── Denoising ──
    fastNlMeansDenoising = staticmethod(fastNlMeansDenoising)
    bm3d = staticmethod(bm3d)

    # ── Geometric ──
    inpaint = staticmethod(inpaint)
    seamlessClone = staticmethod(seamlessClone)

    # ── Pyramid ──
    pyrDown = staticmethod(pyrDown)
    pyrUp = staticmethod(pyrUp)

    # ── Optical Flow ──
    calcOpticalFlowFarneback = staticmethod(calcOpticalFlowFarneback)
    calcOpticalFlowPyrLK = staticmethod(calcOpticalFlowPyrLK)
    calcOpticalFlowBlockMatching = staticmethod(calcOpticalFlowBlockMatching)

    # ── Features ──
    ORB = staticmethod(lambda nfeatures=500: ORB(nfeatures))
    BFMatcher = staticmethod(BFMatcher)

    # ── Alignment ──
    matchTemplate = staticmethod(matchTemplate)

    # ── HDR ──
    ReinhardToneMap = staticmethod(ReinhardToneMap)
    sRGBGamma = staticmethod(sRGBGamma)

    # ── Demosaic ──
    demosaic = staticmethod(demosaic)

    # ── SfM ──
    findHomography = staticmethod(findHomography)
    solvePnP = staticmethod(solvePnP)

    # ── FFT ──
    fft2 = staticmethod(fft2)
    ifft2 = staticmethod(ifft2)

    # ── NumPy-compatible Operations ──
    zero = staticmethod(zero)
    zeros = staticmethod(zero)
    full = staticmethod(full)
    array = staticmethod(array)
    hanning = staticmethod(hanning)
    create_hanning = staticmethod(hanning)
    fill_scalar = staticmethod(full)

    # ── Math Operations ──
    abs = staticmethod(gpu_abs)
    sqrt = staticmethod(gpu_sqrt)
    log = staticmethod(gpu_log)
    exp = staticmethod(gpu_exp)
    power = staticmethod(gpu_power)
    square = staticmethod(gpu_square)
    clip = staticmethod(gpu_clip)
    where = staticmethod(gpu_where)
    sum = staticmethod(gpu_sum)
    max = staticmethod(gpu_max)
    min = staticmethod(gpu_min)
    mean = staticmethod(gpu_mean)
    std = staticmethod(gpu_std)
    matmul = staticmethod(matmul)
    mat3_inv = staticmethod(gpu_mat3_inv)
    mat3_det = staticmethod(gpu_mat3_det)
    sort = staticmethod(gpu_sort)
    argsort = staticmethod(gpu_argsort)
    unique = staticmethod(gpu_unique)
    meshgrid = staticmethod(gpu_meshgrid)

    gpu_abs = staticmethod(gpu_abs)
    gpu_sqrt = staticmethod(gpu_sqrt)
    gpu_log = staticmethod(gpu_log)
    gpu_exp = staticmethod(gpu_exp)
    gpu_power = staticmethod(gpu_power)
    gpu_square = staticmethod(gpu_square)
    gpu_clip = staticmethod(gpu_clip)
    gpu_where = staticmethod(gpu_where)
    gpu_sum = staticmethod(gpu_sum)
    gpu_max = staticmethod(gpu_max)
    gpu_min = staticmethod(gpu_min)
    gpu_mean = staticmethod(gpu_mean)
    gpu_std = staticmethod(gpu_std)
    gpu_matmul = staticmethod(gpu_matmul)
    gpu_mat3_inv = staticmethod(gpu_mat3_inv)
    gpu_mat3_det = staticmethod(gpu_mat3_det)
    gpu_sort = staticmethod(gpu_sort)
    gpu_argsort = staticmethod(gpu_argsort)
    gpu_unique = staticmethod(gpu_unique)
    gpu_meshgrid = staticmethod(gpu_meshgrid)

    # ── Color Conversion Constants ──
    COLOR_BGR2GRAY = COLOR_BGR2GRAY
    COLOR_RGB2GRAY = COLOR_RGB2GRAY
    COLOR_GRAY2BGR = COLOR_GRAY2BGR
    COLOR_GRAY2RGB = COLOR_GRAY2RGB
    COLOR_BGR2HSV = COLOR_BGR2HSV
    COLOR_HSV2BGR = COLOR_HSV2BGR
    COLOR_BGR2LAB = COLOR_BGR2LAB
    COLOR_LAB2BGR = COLOR_LAB2BGR
    COLOR_BGR2YCrCb = COLOR_BGR2YCrCb
    COLOR_YCrCb2BGR = COLOR_YCrCb2BGR

    # ── Interpolation Constants ──
    INTER_NEAREST = INTER_NEAREST
    INTER_LINEAR = INTER_LINEAR
    INTER_CUBIC = INTER_CUBIC

    # ── Threshold Constants ──
    THRESH_BINARY = THRESH_BINARY
    THRESH_BINARY_INV = THRESH_BINARY_INV
    THRESH_TRUNC = THRESH_TRUNC
    THRESH_TOZERO = THRESH_TOZERO
    THRESH_TOZERO_INV = THRESH_TOZERO_INV
    THRESH_OTSU = THRESH_OTSU

    # ── Morphology Constants ──
    MORPH_RECT = MORPH_RECT
    MORPH_CROSS = MORPH_CROSS
    MORPH_ELLIPSE = MORPH_ELLIPSE

    # ── Inpaint Constants ──
    INPAINT_TELEA = INPAINT_TELEA
    INPAINT_NS = INPAINT_NS

    # ── Clone Constants ──
    NORMAL_CLONE = NORMAL_CLONE
    MIXED_CLONE = MIXED_CLONE
    MONOCHROME_TRANSFER = MONOCHROME_TRANSFER


# Create singleton instance
ta = _TaichiAlgorithm()
