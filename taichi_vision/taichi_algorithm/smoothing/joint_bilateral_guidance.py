"""
Joint Bilateral Filter & JBLU - Taichi GPU Implementation
==========================================================
General-purpose edge-preserving filter + guided upsampler.

Modes:
  1. joint_bilateral_filter()   - Post-processor for any image/flow/scalar
  2. joint_bilateral_upsample() - JBLU for upscaling low-res maps with hi-res guide
"""

import numpy as np

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
except ImportError:
    pass

# --- Sigma Presets ---
SIGMA_PRESETS = {
    "high":   (0.8,  0.05),   # Highest detail preservation (gentle smoothing)
    "medium": (1.5,  0.10),   # Balanced
    "low":    (2.5,  0.20),   # Lowest detail preservation (aggressive smoothing)
}

def _get_sigma_args(preset="medium"):
    ss, sr = SIGMA_PRESETS.get(preset, SIGMA_PRESETS["medium"])
    return 1.0 / (2.0 * ss * ss), 1.0 / (2.0 * sr * sr)

if TAICHI_AVAILABLE:

    # =========================================================================
    # JBF KERNELS - General Post-Processor
    # =========================================================================
    # Guide is always grayscale f32 normalized [0, 1].
    # Window variants: r=1 (3x3), r=2 (5x5), r=3 (7x7)

    @ti.kernel
    def _jbf_1ch_r1(src: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w, acc = 1e-12, 0.0
            c_g = guide[y, x]
            for dy in ti.static(range(-1, 2)):
                for dx in ti.static(range(-1, 2)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    @ti.kernel
    def _jbf_1ch_r2(src: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w, acc = 1e-12, 0.0
            c_g = guide[y, x]
            for dy in ti.static(range(-2, 3)):
                for dx in ti.static(range(-2, 3)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    @ti.kernel
    def _jbf_1ch_r3(src: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w, acc = 1e-12, 0.0
            c_g = guide[y, x]
            for dy in ti.static(range(-3, 4)):
                for dx in ti.static(range(-3, 4)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    # --- 3ch (RGB) ---
    @ti.kernel
    def _jbf_3ch_r1(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                    guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                    h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12; acc = tm.vec3(0.0); c_g = guide[y, x]
            for dy in ti.static(range(-1, 2)):
                for dx in ti.static(range(-1, 2)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    @ti.kernel
    def _jbf_3ch_r2(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                    guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                    h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12; acc = tm.vec3(0.0); c_g = guide[y, x]
            for dy in ti.static(range(-2, 3)):
                for dx in ti.static(range(-2, 3)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    @ti.kernel
    def _jbf_3ch_r3(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                    guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                    h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12; acc = tm.vec3(0.0); c_g = guide[y, x]
            for dy in ti.static(range(-3, 4)):
                for dx in ti.static(range(-3, 4)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    # --- Flow (2ch) ---
    @ti.kernel
    def _jbf_flow_r1(src: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                     guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                     dst: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                     h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12; acc = tm.vec2(0.0); c_g = guide[y, x]
            for dy in ti.static(range(-1, 2)):
                for dx in ti.static(range(-1, 2)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    @ti.kernel
    def _jbf_flow_r2(src: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                     guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                     dst: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                     h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12; acc = tm.vec2(0.0); c_g = guide[y, x]
            for dy in ti.static(range(-2, 3)):
                for dx in ti.static(range(-2, 3)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    @ti.kernel
    def _jbf_flow_r3(src: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                     guide: ti.types.ndarray(dtype=ti.f32, ndim=2),
                     dst: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                     h: int, w: int, inv_2ss2: float, inv_2sr2: float):
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12; acc = tm.vec2(0.0); c_g = guide[y, x]
            for dy in ti.static(range(-3, 4)):
                for dx in ti.static(range(-3, 4)):
                    ny = tm.clamp(y+dy, 0, h-1); nx = tm.clamp(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src[ny, nx] * wt; total_w += wt
            dst[y, x] = acc / total_w

    # =========================================================================
    # JBLU KERNELS - Joint Bilateral Upsampling
    # =========================================================================
    # src_low is small, guide_hi is full resolution.
    # For each HIGH-RES pixel, gather weighted LOW-RES neighbors.
    # Range weight is based on guide_hi color difference.

    @ti.kernel
    def _jblu_1ch_r2(src_low: ti.types.ndarray(dtype=ti.f32, ndim=2),
                     guide_hi: ti.types.ndarray(dtype=ti.f32, ndim=2),
                     dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
                     h_low: int, w_low: int, H: int, W: int,
                     inv_2ss2: float, inv_2sr2: float):
        for Y, X in ti.ndrange(H, W):
            iy = int(ti.floor(float(Y) * float(h_low) / float(H)))
            ix = int(ti.floor(float(X) * float(w_low) / float(W)))
            c_g = guide_hi[Y, X]
            total_w, acc = 1e-12, 0.0
            for dy in ti.static(range(-2, 3)):
                for dx in ti.static(range(-2, 3)):
                    ny = tm.clamp(iy+dy, 0, h_low-1); nx = tm.clamp(ix+dx, 0, w_low-1)
                    ny_hi = tm.clamp(int(float(ny)*float(H)/float(h_low)+0.5), 0, H-1)
                    nx_hi = tm.clamp(int(float(nx)*float(W)/float(w_low)+0.5), 0, W-1)
                    diff_g = guide_hi[ny_hi, nx_hi] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src_low[ny, nx] * wt; total_w += wt
            dst[Y, X] = acc / total_w

    @ti.kernel
    def _jblu_flow_r2(src_low: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                      guide_hi: ti.types.ndarray(dtype=ti.f32, ndim=2),
                      dst: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
                      h_low: int, w_low: int, H: int, W: int,
                      inv_2ss2: float, inv_2sr2: float,
                      scale_y: float, scale_x: float):
        for Y, X in ti.ndrange(H, W):
            iy = int(ti.floor(float(Y) * float(h_low) / float(H)))
            ix = int(ti.floor(float(X) * float(w_low) / float(W)))
            c_g = guide_hi[Y, X]
            total_w = 1e-12; acc = tm.vec2(0.0)
            for dy in ti.static(range(-2, 3)):
                for dx in ti.static(range(-2, 3)):
                    ny = tm.clamp(iy+dy, 0, h_low-1); nx = tm.clamp(ix+dx, 0, w_low-1)
                    ny_hi = tm.clamp(int(float(ny)*float(H)/float(h_low)+0.5), 0, H-1)
                    nx_hi = tm.clamp(int(float(nx)*float(W)/float(w_low)+0.5), 0, W-1)
                    diff_g = guide_hi[ny_hi, nx_hi] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src_low[ny, nx] * wt; total_w += wt
            result = acc / total_w
            dst[Y, X] = tm.vec2(result[0] * scale_x, result[1] * scale_y)

    @ti.kernel
    def _jblu_3ch_r2(src_low: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                     guide_hi: ti.types.ndarray(dtype=ti.f32, ndim=2),
                     dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
                     h_low: int, w_low: int, H: int, W: int,
                     inv_2ss2: float, inv_2sr2: float):
        for Y, X in ti.ndrange(H, W):
            iy = int(ti.floor(float(Y) * float(h_low) / float(H)))
            ix = int(ti.floor(float(X) * float(w_low) / float(W)))
            c_g = guide_hi[Y, X]
            total_w = 1e-12; acc = tm.vec3(0.0)
            for dy in ti.static(range(-2, 3)):
                for dx in ti.static(range(-2, 3)):
                    ny = tm.clamp(iy+dy, 0, h_low-1); nx = tm.clamp(ix+dx, 0, w_low-1)
                    ny_hi = tm.clamp(int(float(ny)*float(H)/float(h_low)+0.5), 0, H-1)
                    nx_hi = tm.clamp(int(float(nx)*float(W)/float(w_low)+0.5), 0, W-1)
                    diff_g = guide_hi[ny_hi, nx_hi] - c_g
                    wt = ti.exp(-float(dx*dx+dy*dy)*inv_2ss2 - diff_g*diff_g*inv_2sr2)
                    acc += src_low[ny, nx] * wt; total_w += wt
            dst[Y, X] = acc / total_w

    # =========================================================================
    # HELPER: Prepare guide (ensure grayscale f32 normalized 0-1)
    # =========================================================================
    def _prepare_guide(guide_input, buffer_provider="pool"):
        """
        Converts any guide input to a grayscale f32 [0,1] buffer.
        - (H,W) f32: pass through (assumed already normalized)
        - (H,W) u8/u16/i32: convert and normalize
        - (H,W,3) any: convert BGR→gray then normalize
        """
        is_taichi = hasattr(guide_input, 'to_numpy')

        if is_taichi:
            sh = guide_input.shape
            if len(sh) == 2:
                # Already 2D — normalize if not f32
                if guide_input.dtype == np.float32:
                    return guide_input, False  # ready to use
                else:
                    np_data = guide_input.to_numpy().astype(np.float32)
                    np_data /= 255.0 if guide_input.dtype == np.uint8 else 65535.0
                    buf = common.get_temp_buffer(sh, ti.f32, buffer_provider)
                    buf.from_numpy(np_data)
                    return buf, True
            else:
                # 3ch taichi → cvt color
                np_data = guide_input.to_numpy().astype(np.float32)
                gray = 0.299*np_data[:,:,2] + 0.587*np_data[:,:,1] + 0.114*np_data[:,:,0]
                gray /= 255.0 if np_data.max() > 1.0 else 1.0
                buf = common.get_temp_buffer(np_data.shape[:2], ti.f32, buffer_provider)
                buf.from_numpy(gray.astype(np.float32))
                return buf, True
        else:
            # NumPy path
            if guide_input.ndim == 3:
                gray = (0.299*guide_input[:,:,2] + 0.587*guide_input[:,:,1]
                        + 0.114*guide_input[:,:,0]).astype(np.float32)
            else:
                gray = guide_input.astype(np.float32)

            if gray.max() > 1.0:
                gray = gray / 255.0 if gray.max() <= 255.0 else gray / 65535.0

            buf = common.get_temp_buffer(gray.shape, ti.f32, buffer_provider)
            buf.from_numpy(np.ascontiguousarray(gray))
            return buf, True

    # =========================================================================
    # PUBLIC API
    # =========================================================================
    _JBF_1CH_KERNELS  = {1: _jbf_1ch_r1,  2: _jbf_1ch_r2,  3: _jbf_1ch_r3}
    _JBF_3CH_KERNELS  = {1: _jbf_3ch_r1,  2: _jbf_3ch_r2,  3: _jbf_3ch_r3}
    _JBF_FLOW_KERNELS = {1: _jbf_flow_r1, 2: _jbf_flow_r2, 3: _jbf_flow_r3}

def joint_bilateral_filter(src, guide, preset="medium", radius=2, buffer_provider="pool"):
    """
    General-purpose Joint Bilateral Filter.
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.joint_bilateral_filter(src, guide, preset=preset, radius=radius, return_gpu=hasattr(src, "to_numpy"))

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = not hasattr(src, 'to_numpy')
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    guide_gpu, guide_is_temp = _prepare_guide(guide, buffer_provider)

    h, w = src_gpu.shape[:2]
    ndim = len(src_gpu.shape)
    inv_2ss2, inv_2sr2 = _get_sigma_args(preset)

    r = radius if radius in (1, 2, 3) else 2

    if ndim == 2:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        _JBF_1CH_KERNELS[r](src_gpu, guide_gpu, dst_gpu, h, w, inv_2ss2, inv_2sr2)
    elif src_gpu.shape[2] == 3:
        dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32, buffer_provider)
        _JBF_3CH_KERNELS[r](src_gpu, guide_gpu, dst_gpu, h, w, inv_2ss2, inv_2sr2)
    else:  # flow (2ch)
        dst_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)
        _JBF_FLOW_KERNELS[r](src_gpu, guide_gpu, dst_gpu, h, w, inv_2ss2, inv_2sr2)

    if guide_is_temp: common.release_temp_buffer(guide_gpu)
    if src_is_temp:   common.release_temp_buffer(src_gpu)

    if is_numpy:
        res = dst_gpu.to_numpy()
        common.release_temp_buffer(dst_gpu)
        return res
    return dst_gpu

def joint_bilateral_upsample(src_low, guide_hi, preset="medium", buffer_provider="pool"):
    """
    Joint Bilateral Upsampling (JBLU).
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.joint_bilateral_upsample(src_low, guide_hi, preset=preset, return_gpu=hasattr(src_low, "to_numpy"))

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = not hasattr(src_low, 'to_numpy')
    src_gpu, src_is_temp = common.ensure_taichi_field(src_low, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    guide_gpu, guide_is_temp = _prepare_guide(guide_hi, buffer_provider)

    h_low, w_low = src_gpu.shape[:2]
    H, W = guide_gpu.shape[:2]
    scale_y = float(H) / float(h_low)
    scale_x = float(W) / float(w_low)
    ndim = len(src_gpu.shape)
    inv_2ss2, inv_2sr2 = _get_sigma_args(preset)

    if ndim == 2:
        dst_gpu = common.get_temp_buffer((H, W), ti.f32, buffer_provider)
        _jblu_1ch_r2(src_gpu, guide_gpu, dst_gpu,
                     h_low, w_low, H, W, inv_2ss2, inv_2sr2)
    elif src_gpu.shape[2] == 3:
        dst_gpu = common.get_temp_buffer((H, W, 3), ti.f32, buffer_provider)
        _jblu_3ch_r2(src_gpu, guide_gpu, dst_gpu,
                     h_low, w_low, H, W, inv_2ss2, inv_2sr2)
    else:  # flow (2ch)
        dst_gpu = common.get_temp_buffer((H, W, 2), ti.f32, buffer_provider)
        _jblu_flow_r2(src_gpu, guide_gpu, dst_gpu,
                      h_low, w_low, H, W, inv_2ss2, inv_2sr2,
                      scale_y, scale_x)

    if guide_is_temp: common.release_temp_buffer(guide_gpu)
    if src_is_temp:   common.release_temp_buffer(src_gpu)

    if is_numpy:
        res = dst_gpu.to_numpy()
        common.release_temp_buffer(dst_gpu)
        return res
    return dst_gpu
