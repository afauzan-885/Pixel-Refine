"""Compile the research-stage HDR, SfM, and Camera2 AOT modules.

The high-level algorithms in ``taichi_algorithm`` deliberately remain Python
orchestrators.  This file packages their portable, array-to-array hot paths
into target-qualified TCM modules so the same implementation can be used by
CPU, CUDA, Vulkan, and desktop OpenGL backends.

The compiler reuses existing Taichi kernels wherever their signatures are
portable.  A small number of f32 adapters are defined here for kernels whose
original JIT API uses untyped camera buffers, u8 input, f64 work arrays, or a
scalar kernel return value.  Those adapters preserve the algorithm while
keeping the cross-backend artifact contract uniform.
"""

import os
from pathlib import Path
from typing import Callable

os.environ.setdefault("AOT_MODE", "0")

import taichi as ti

from taichi_vision.taichi_algorithm.image_processing import hdr_fusion as _hdr
from taichi_vision.taichi_algorithm.image_processing import hdr_stack as _hdr_stack
from taichi_vision.taichi_algorithm.image_processing import hdr_response as _hdr_response
from taichi_vision.taichi_algorithm.image_processing import tone_mapping as _tone
from taichi_vision.taichi_algorithm.sfm import bundle_adjustment as _ba
from taichi_vision.taichi_algorithm.sfm import cheirality_check as _cheir
from taichi_vision.taichi_algorithm.sfm import feature_matching as _match
from taichi_vision.taichi_algorithm.sfm import five_point_solver as _five
from taichi_vision.taichi_algorithm.sfm import plane_sweep as _stereo
from taichi_vision.taichi_algorithm.sfm import mvs_regularization as _mvs
from taichi_vision.taichi_algorithm.sfm import point_cloud as _cloud
from taichi_vision.taichi_algorithm.sfm import poisson_recon as _poisson
from taichi_vision.taichi_algorithm.sfm import registration as _registration
from taichi_vision.taichi_algorithm.sfm import triangulation as _tri
from taichi_vision.taichi_algorithm.panorama import seam as _seam


def _nd(name: str, dtype, ndim: int):
    return ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype, ndim=ndim)


def _scalar(name: str, dtype):
    return ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, dtype)


def _add_graph(module, name: str, kernel, *args) -> None:
    builder = ti.graph.GraphBuilder()
    builder.dispatch(kernel, *args)
    module.add_graph(name, builder.compile())


def _compile_one(arch, save_path: str, register: Callable) -> str:
    output = Path(save_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    ti.init(arch=arch, offline_cache=False)
    try:
        module = ti.aot.Module(arch)
        register(module)
        module.archive(str(output))
    finally:
        ti.reset()
    print(f"[OK] Archived {output}")
    return str(output)


# ---------------------------------------------------------------------------
# HDR fusion and tone mapping
# ---------------------------------------------------------------------------


@ti.kernel
def _hdr_weight_f32_portable(
    img_rgb: ti.types.ndarray(ti.f32, ndim=3),
    lap_gray: ti.types.ndarray(ti.f32, ndim=2),
    weight: ti.types.ndarray(ti.f32, ndim=2),
    h: ti.i32,
    w: ti.i32,
    noise_sigma: ti.f32,
    noise_power: ti.f32,
    exposure_sigma: ti.f32,
    exposure_power: ti.f32,
    detail_power: ti.f32,
    saturation_power: ti.f32,
):
    """Portable spelling of the HDR weight formula.

    The source kernel is mathematically portable, but its graph ABI is
    rejected by the runtime on some CPU builds even though the module
    archives successfully.  Keeping the same f32 formula in a local adapter
    gives the public AOT contract a stable ndarray signature.
    """
    for y, x in ti.ndrange(h, w):
        r_val = img_rgb[y, x, 0]
        g_val = img_rgb[y, x, 1]
        b_val = img_rgb[y, x, 2]
        luma = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
        snr = luma / ti.max(noise_sigma, 1e-6)
        w_noise = ti.pow(snr / (snr + 0.5), noise_power)
        denom = 2.0 * exposure_sigma * exposure_sigma
        w_exp_r = ti.exp(-ti.pow(r_val - 0.5, 2) / denom)
        w_exp_g = ti.exp(-ti.pow(g_val - 0.5, 2) / denom)
        w_exp_b = ti.exp(-ti.pow(b_val - 0.5, 2) / denom)
        w_exposure = ti.pow(w_exp_r * w_exp_g * w_exp_b, exposure_power / 3.0)
        contrast = ti.abs(lap_gray[y, x])
        w_contrast = ti.pow(contrast + 1e-6, detail_power)
        mean_rgb = (r_val + g_val + b_val) / 3.0
        sat = ti.sqrt(
            (r_val - mean_rgb) ** 2
            + (g_val - mean_rgb) ** 2
            + (b_val - mean_rgb) ** 2
        ) / 3.0
        w_sat = ti.pow(sat + 1e-6, saturation_power)
        weight[y, x] = w_noise * w_exposure * w_contrast * w_sat


def _register_hdr(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(
        module,
        "hdr_weight_f32",
        _hdr_weight_f32_portable,
        _nd("img_rgb", f32, 3),
        _nd("lap_gray", f32, 2),
        _nd("weight", f32, 2),
        _scalar("h", i32),
        _scalar("w", i32),
        _scalar("noise_sigma", f32),
        _scalar("noise_power", f32),
        _scalar("exposure_sigma", f32),
        _scalar("exposure_power", f32),
        _scalar("detail_power", f32),
        _scalar("saturation_power", f32),
    )
    _add_graph(
        module,
        "hdr_normalize_weights_f32",
        _hdr._normalize_weights_kernel,
        _nd("weights", f32, 3),
        _scalar("h", i32),
        _scalar("w", i32),
        _scalar("n_frames", i32),
    )
    _add_graph(module, "hdr_downsample_3ch_f32", _hdr._downsample_2x_3ch_kernel, _nd("src", f32, 3), _nd("dst", f32, 3))
    _add_graph(module, "hdr_downsample_1ch_f32", _hdr._downsample_2x_1ch_kernel, _nd("src", f32, 2), _nd("dst", f32, 2))
    _add_graph(module, "hdr_upsample_3ch_f32", _hdr._upsample_2x_3ch_kernel, _nd("src", f32, 3), _nd("dst", f32, 3))
    _add_graph(module, "hdr_upsample_1ch_f32", _hdr._upsample_2x_1ch_kernel, _nd("src", f32, 2), _nd("dst", f32, 2))
    _add_graph(module, "hdr_subtract_3ch_f32", _hdr._subtract_kernel, _nd("img", f32, 3), _nd("upsampled", f32, 3), _nd("lap", f32, 3))
    _add_graph(module, "hdr_add_weighted_laplacian_f32", _hdr._add_weighted_laplacian_kernel, _nd("lap", f32, 3), _nd("weight", f32, 2), _nd("result", f32, 3))
    _add_graph(module, "hdr_add_3ch_f32", _hdr._add_3ch_kernel, _nd("dst", f32, 3), _nd("src", f32, 3))
    # The high-level deghost policy still owns percentile/MAD thresholding and
    # bounded smoothing on the host.  This graph packages its deterministic
    # exposure-normalised luminance/edge residual so AOT callers do not need
    # to reimplement the residual kernel or silently fall back to NumPy.
    _add_graph(
        module,
        "hdr_deghost_residual_f32",
        _hdr_stack._deghost_residual_kernel,
        _nd("reference", f32, 2),
        _nd("target", f32, 2),
        _nd("residual", f32, 2),
        _scalar("scale", f32),
        _scalar("offset", f32),
        _scalar("edge_weight", f32),
    )
    # Response calibration consumes the same deterministic unit-range
    # quantiser as the JIT/reference implementation.  Keep QR/SVD and
    # Robertson reductions host-side, but make this bounded per-sample leaf
    # available through the target-qualified HDR artifact.
    _add_graph(
        module,
        "hdr_response_quantise_f32",
        _hdr_response._response_quantise_kernel,
        _nd("values", f32, 1),
        _nd("quantised", i32, 1),
        _scalar("levels", i32),
    )
    _add_graph(
        module,
        "hdr_merge_linear_f32",
        _hdr_response._merge_linear_kernel,
        _nd("stack", f32, 4),
        _nd("times", f32, 1),
        _nd("output", f32, 3),
        _scalar("h", i32),
        _scalar("w", i32),
        _scalar("channels", i32),
        _scalar("frame_count", i32),
        _scalar("levels", i32),
    )
    _add_graph(
        module,
        "hdr_merge_log_f32",
        _hdr_response._merge_log_kernel,
        _nd("stack", f32, 4),
        _nd("times", f32, 1),
        _nd("curve", f32, 2),
        _nd("output", f32, 3),
        _scalar("h", i32),
        _scalar("w", i32),
        _scalar("channels", i32),
        _scalar("frame_count", i32),
        _scalar("levels", i32),
    )


def compile_hdr_aot(arch=ti.cpu, save_path="hdr.tcm") -> str:
    return _compile_one(arch, save_path, _register_hdr)


def _register_tone_mapping(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "tone_luminance_f32", _tone._compute_luminance_kernel, _nd("img", f32, 3), _nd("lum", f32, 2), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "tone_reinhard_f32", _tone._reinhard_global_kernel, _nd("img", f32, 3), _nd("lum", f32, 2), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("key", f32), _scalar("lum_white", f32), _scalar("epsilon", f32))
    _add_graph(module, "tone_srgb_f32", _tone._srgb_gamma_kernel, _nd("img", f32, 3), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("gamma", f32))
    _add_graph(module, "tone_srgb_simple_f32", _tone._srgb_gamma_simple_kernel, _nd("img", f32, 3), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("gamma", f32))
    _add_graph(module, "tone_simulate_exposure_f32", _tone._simulate_exposure_kernel, _nd("img", f32, 3), _nd("bright", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("gain", f32))
    _add_graph(module, "tone_blend_weight_f32", _tone._compute_blend_weight_kernel, _nd("lum", f32, 2), _nd("weight", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("target_lum", f32), _scalar("sigma", f32))
    _add_graph(module, "tone_weighted_blend_f32", _tone._weighted_blend_kernel, _nd("img_dark", f32, 3), _nd("img_bright", f32, 3), _nd("w_dark", f32, 2), _nd("w_bright", f32, 2), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "tone_contrast_f32", _tone._contrast_adjust_kernel, _nd("img", f32, 3), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("contrast", f32), _scalar("brightness", f32))
    _add_graph(module, "tone_downsample_3ch_f32", _tone._downsample_2x_3ch_kernel, _nd("src", f32, 3), _nd("dst", f32, 3))
    _add_graph(module, "tone_downsample_1ch_f32", _tone._downsample_2x_1ch_kernel, _nd("src", f32, 2), _nd("dst", f32, 2))
    _add_graph(module, "tone_upsample_3ch_f32", _tone._upsample_2x_3ch_kernel, _nd("src", f32, 3), _nd("dst", f32, 3))
    _add_graph(module, "tone_upsample_1ch_f32", _tone._upsample_2x_1ch_kernel, _nd("src", f32, 2), _nd("dst", f32, 2))
    _add_graph(module, "tone_subtract_3ch_f32", _tone._subtract_3ch_kernel, _nd("img", f32, 3), _nd("upsampled", f32, 3), _nd("lap", f32, 3))
    _add_graph(module, "tone_add_3ch_f32", _tone._add_3ch_kernel, _nd("dst", f32, 3), _nd("src", f32, 3))


def compile_tone_mapping_aot(arch=ti.cpu, save_path="tone_mapping.tcm") -> str:
    return _compile_one(arch, save_path, _register_tone_mapping)


# ---------------------------------------------------------------------------
# Camera2 leaf kernels.  Camera buffers arrive as f32 [0,255] in the AOT
# contract; the Python CameraPipeline can convert byte buffers once at the
# boundary.  This avoids backend-dependent u8 shader support.
# ---------------------------------------------------------------------------


@ti.kernel
def _yuv420_3plane_f32(
    y_plane: ti.types.ndarray(ti.f32, ndim=1),
    u_plane: ti.types.ndarray(ti.f32, ndim=1),
    v_plane: ti.types.ndarray(ti.f32, ndim=1),
    dst: ti.types.ndarray(ti.f32, ndim=3),
    h: ti.i32,
    w: ti.i32,
    y_row_stride: ti.i32,
    y_pixel_stride: ti.i32,
    u_row_stride: ti.i32,
    u_pixel_stride: ti.i32,
    v_row_stride: ti.i32,
    v_pixel_stride: ti.i32,
):
    for py, px in ti.ndrange(h, w):
        yv = y_plane[py * y_row_stride + px * y_pixel_stride] - 16.0
        cx = px // 2
        cy = py // 2
        uv = u_plane[cy * u_row_stride + cx * u_pixel_stride] - 128.0
        vv = v_plane[cy * v_row_stride + cx * v_pixel_stride] - 128.0
        r = 1.164 * yv + 1.596 * vv
        g = 1.164 * yv - 0.813 * vv - 0.391 * uv
        b = 1.164 * yv + 2.018 * uv
        dst[py, px, 0] = ti.max(0.0, ti.min(1.0, r / 255.0))
        dst[py, px, 1] = ti.max(0.0, ti.min(1.0, g / 255.0))
        dst[py, px, 2] = ti.max(0.0, ti.min(1.0, b / 255.0))


@ti.kernel
def _nv21_f32(
    y_plane: ti.types.ndarray(ti.f32, ndim=1),
    vu: ti.types.ndarray(ti.f32, ndim=1),
    dst: ti.types.ndarray(ti.f32, ndim=3),
    h: ti.i32,
    w: ti.i32,
):
    for py, px in ti.ndrange(h, w):
        yv = y_plane[py * w + px] - 16.0
        idx = (py // 2) * w + (px // 2) * 2
        vv = vu[idx] - 128.0
        uv = vu[idx + 1] - 128.0
        dst[py, px, 0] = ti.max(0.0, ti.min(1.0, (1.164 * yv + 1.596 * vv) / 255.0))
        dst[py, px, 1] = ti.max(0.0, ti.min(1.0, (1.164 * yv - 0.813 * vv - 0.391 * uv) / 255.0))
        dst[py, px, 2] = ti.max(0.0, ti.min(1.0, (1.164 * yv + 2.018 * uv) / 255.0))


@ti.kernel
def _yuv420_3plane_bilinear_f32(
    y_plane: ti.types.ndarray(ti.f32, ndim=1),
    u_plane: ti.types.ndarray(ti.f32, ndim=1),
    v_plane: ti.types.ndarray(ti.f32, ndim=1),
    dst: ti.types.ndarray(ti.f32, ndim=3),
    h: ti.i32,
    w: ti.i32,
    y_row_stride: ti.i32,
    y_pixel_stride: ti.i32,
    u_row_stride: ti.i32,
    u_pixel_stride: ti.i32,
    v_row_stride: ti.i32,
    v_pixel_stride: ti.i32,
):
    """Typed f32 version of the Camera2 bilinear-chroma path."""
    ch_h = h // 2
    ch_w = w // 2
    for py, px in ti.ndrange(h, w):
        yv = y_plane[py * y_row_stride + px * y_pixel_stride] - 16.0
        cx_f = (ti.cast(px, ti.f32) + 0.5) / 2.0 - 0.5
        cy_f = (ti.cast(py, ti.f32) + 0.5) / 2.0 - 0.5
        cx0 = ti.cast(ti.floor(cx_f), ti.i32)
        cy0 = ti.cast(ti.floor(cy_f), ti.i32)
        cx1 = cx0 + 1
        cy1 = cy0 + 1
        cx0c = ti.max(0, ti.min(ch_w - 1, cx0))
        cy0c = ti.max(0, ti.min(ch_h - 1, cy0))
        cx1c = ti.max(0, ti.min(ch_w - 1, cx1))
        cy1c = ti.max(0, ti.min(ch_h - 1, cy1))
        fx = cx_f - ti.cast(cx0, ti.f32)
        fy = cy_f - ti.cast(cy0, ti.f32)

        u00 = u_plane[cy0c * u_row_stride + cx0c * u_pixel_stride]
        u10 = u_plane[cy0c * u_row_stride + cx1c * u_pixel_stride]
        u01 = u_plane[cy1c * u_row_stride + cx0c * u_pixel_stride]
        u11 = u_plane[cy1c * u_row_stride + cx1c * u_pixel_stride]
        uv = (
            u00 * (1.0 - fx) * (1.0 - fy)
            + u10 * fx * (1.0 - fy)
            + u01 * (1.0 - fx) * fy
            + u11 * fx * fy
            - 128.0
        )
        v00 = v_plane[cy0c * v_row_stride + cx0c * v_pixel_stride]
        v10 = v_plane[cy0c * v_row_stride + cx1c * v_pixel_stride]
        v01 = v_plane[cy1c * v_row_stride + cx0c * v_pixel_stride]
        v11 = v_plane[cy1c * v_row_stride + cx1c * v_pixel_stride]
        vv = (
            v00 * (1.0 - fx) * (1.0 - fy)
            + v10 * fx * (1.0 - fy)
            + v01 * (1.0 - fx) * fy
            + v11 * fx * fy
            - 128.0
        )
        r = 1.164 * yv + 1.596 * vv
        g = 1.164 * yv - 0.813 * vv - 0.391 * uv
        b = 1.164 * yv + 2.018 * uv
        dst[py, px, 0] = ti.max(0.0, ti.min(1.0, r / 255.0))
        dst[py, px, 1] = ti.max(0.0, ti.min(1.0, g / 255.0))
        dst[py, px, 2] = ti.max(0.0, ti.min(1.0, b / 255.0))


@ti.kernel
def _nv12_f32(
    y_plane: ti.types.ndarray(ti.f32, ndim=1),
    uv: ti.types.ndarray(ti.f32, ndim=1),
    dst: ti.types.ndarray(ti.f32, ndim=3),
    h: ti.i32,
    w: ti.i32,
):
    for py, px in ti.ndrange(h, w):
        yv = y_plane[py * w + px] - 16.0
        idx = (py // 2) * w + (px // 2) * 2
        uvv = uv[idx] - 128.0
        vv = uv[idx + 1] - 128.0
        dst[py, px, 0] = ti.max(0.0, ti.min(1.0, (1.164 * yv + 1.596 * vv) / 255.0))
        dst[py, px, 1] = ti.max(0.0, ti.min(1.0, (1.164 * yv - 0.813 * vv - 0.391 * uvv) / 255.0))
        dst[py, px, 2] = ti.max(0.0, ti.min(1.0, (1.164 * yv + 2.018 * uvv) / 255.0))


@ti.kernel
def _y_to_gray_f32(
    y_plane: ti.types.ndarray(ti.f32, ndim=1),
    dst: ti.types.ndarray(ti.f32, ndim=2),
    h: ti.i32,
    w: ti.i32,
    row_stride: ti.i32,
    pixel_stride: ti.i32,
):
    for py, px in ti.ndrange(h, w):
        dst[py, px] = y_plane[py * row_stride + px * pixel_stride] / 255.0


@ti.kernel
def _camera_unsharp_f32(
    src: ti.types.ndarray(ti.f32, ndim=3),
    blurred: ti.types.ndarray(ti.f32, ndim=3),
    dst: ti.types.ndarray(ti.f32, ndim=3),
    amount: ti.f32,
    h: ti.i32,
    w: ti.i32,
):
    for y, x, c in ti.ndrange(h, w, 3):
        dst[y, x, c] = ti.max(0.0, ti.min(1.0, src[y, x, c] + amount * (src[y, x, c] - blurred[y, x, c])))


def _register_camera(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "camera_yuv420_f32", _yuv420_3plane_f32, _nd("y_plane", f32, 1), _nd("u_plane", f32, 1), _nd("v_plane", f32, 1), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("y_row_stride", i32), _scalar("y_pixel_stride", i32), _scalar("u_row_stride", i32), _scalar("u_pixel_stride", i32), _scalar("v_row_stride", i32), _scalar("v_pixel_stride", i32))
    _add_graph(module, "camera_yuv420_bilinear_f32", _yuv420_3plane_bilinear_f32, _nd("y_plane", f32, 1), _nd("u_plane", f32, 1), _nd("v_plane", f32, 1), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("y_row_stride", i32), _scalar("y_pixel_stride", i32), _scalar("u_row_stride", i32), _scalar("u_pixel_stride", i32), _scalar("v_row_stride", i32), _scalar("v_pixel_stride", i32))
    _add_graph(module, "camera_nv21_f32", _nv21_f32, _nd("y_plane", f32, 1), _nd("vu", f32, 1), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "camera_nv12_f32", _nv12_f32, _nd("y_plane", f32, 1), _nd("uv", f32, 1), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "camera_y_to_gray_f32", _y_to_gray_f32, _nd("y_plane", f32, 1), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("row_stride", i32), _scalar("pixel_stride", i32))
    _add_graph(module, "camera_unsharp_f32", _camera_unsharp_f32, _nd("src", f32, 3), _nd("blurred", f32, 3), _nd("dst", f32, 3), _scalar("amount", f32), _scalar("h", i32), _scalar("w", i32))


def compile_camera_aot(arch=ti.cpu, save_path="camera.tcm") -> str:
    return _compile_one(arch, save_path, _register_camera)


# ---------------------------------------------------------------------------
# SfM: descriptor matching.  The f32 L2 path is portable.  The existing
# AKAZE/OFB modules remain the preferred binary-descriptor path and are already
# compiled independently in the active suite.
# ---------------------------------------------------------------------------


@ti.kernel
def _knn_select_f32(
    dist_matrix: ti.types.ndarray(ti.f32, ndim=2),
    best_idx: ti.types.ndarray(ti.i32, ndim=2),
    best_dist: ti.types.ndarray(ti.f32, ndim=2),
    n1: ti.i32,
    n2: ti.i32,
    k: ti.i32,
):
    """Portable insertion-sort KNN selection.

    The source implementation used a three-argument descending ``range``.
    AOT backends accept the equivalent explicit while loop consistently.
    """
    for i in range(n1):
        for ki in range(k):
            best_idx[i, ki] = -1
            best_dist[i, ki] = 1e30
        for j in range(n2):
            value = dist_matrix[i, j]
            for ki in range(k):
                if value < best_dist[i, ki]:
                    kk = k - 1
                    while kk > ki:
                        best_dist[i, kk] = best_dist[i, kk - 1]
                        best_idx[i, kk] = best_idx[i, kk - 1]
                        kk -= 1
                    best_dist[i, ki] = value
                    best_idx[i, ki] = j
                    break


def _register_sfm_matching(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "sfm_l2_distance_f32", _match.compute_l2_distance_kernel, _nd("desc1", f32, 2), _nd("desc2", f32, 2), _nd("dist_out", f32, 2), _scalar("n1", i32), _scalar("n2", i32), _scalar("d", i32))
    _add_graph(module, "sfm_knn_f32", _knn_select_f32, _nd("dist_matrix", f32, 2), _nd("best_idx", i32, 2), _nd("best_dist", f32, 2), _scalar("n1", i32), _scalar("n2", i32), _scalar("k", i32))
    _add_graph(module, "sfm_ratio_filter_f32", _match.ratio_test_filter_kernel, _nd("best_dist", f32, 2), _nd("match_out", i32, 2), _nd("match_dist_out", f32, 1), _nd("best_idx", i32, 2), _scalar("n1", i32), _scalar("ratio_threshold", f32))


def compile_sfm_matching_aot(arch=ti.cpu, save_path="sfm_matching.tcm") -> str:
    return _compile_one(arch, save_path, _register_sfm_matching)


# ---------------------------------------------------------------------------
# SfM geometry: 5-point system, cheirality, and adaptive triangulation.
# ---------------------------------------------------------------------------


def _register_sfm_geometry(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "sfm_build_5pt_system_f32", _five.build_5pt_system_kernel, _nd("pts1", f32, 2), _nd("pts2", f32, 2), _nd("indices", i32, 1), _nd("ATA_out", f32, 2))
    _add_graph(module, "sfm_batch_build_5pt_system_f32", _five.batch_build_5pt_system_kernel, _nd("pts1", f32, 2), _nd("pts2", f32, 2), _nd("indices_batch", i32, 2), _scalar("n_batch", i32), _nd("ATA_batch", f32, 3))
    _add_graph(module, "sfm_cheirality_minimal_f32", _cheir.preemptive_cheirality_kernel, _nd("E_arr", f32, 1), _nd("K1", f32, 2), _nd("K2", f32, 2), _nd("pts1", f32, 2), _nd("pts2", f32, 2), _nd("sample_indices", i32, 1), _scalar("n_samples", i32), _nd("result_out", i32, 1))
    _add_graph(module, "sfm_cheirality_full_f32", _cheir.full_cheirality_kernel, _nd("R_arr", f32, 1), _nd("t_arr", f32, 1), _nd("pts1", f32, 2), _nd("pts2", f32, 2), _scalar("n_pts", i32), _nd("depth_out", f32, 2), _nd("inlier_mask", i32, 1))
    _add_graph(module, "sfm_triangulate_adaptive_f32", _tri.triangulate_adaptive_kernel, _nd("pts1", f32, 2), _nd("pts2", f32, 2), _nd("P1", f32, 2), _nd("P2", f32, 2), _nd("C1", f32, 1), _nd("C2", f32, 1), _scalar("n_pts", i32), _scalar("parallax_threshold", f32), _nd("points_3d_out", f32, 2), _nd("method_used_out", i32, 1))


def compile_sfm_geometry_aot(arch=ti.cpu, save_path="sfm_geometry.tcm") -> str:
    return _compile_one(arch, save_path, _register_sfm_geometry)


# ---------------------------------------------------------------------------
# SfM plane sweep / stereo.
# ---------------------------------------------------------------------------


@ti.kernel
def _warp_ncc_f32(
    ref_img: ti.types.ndarray(ti.f32, ndim=2),
    target_img: ti.types.ndarray(ti.f32, ndim=2),
    H_inv: ti.types.ndarray(ti.f32, ndim=2),
    depth: ti.f32,
    n_hypotheses: ti.i32,
    h: ti.i32,
    w: ti.i32,
    patch_radius: ti.i32,
    cost_out: ti.types.ndarray(ti.f32, ndim=2),
):
    # ``depth`` and ``n_hypotheses`` are retained in the ABI for parity with
    # the source kernel; H_inv already contains the selected hypothesis.
    for yi, xi in ti.ndrange(h, w):
        fx = H_inv[0, 0] * xi + H_inv[0, 1] * yi + H_inv[0, 2]
        fy = H_inv[1, 0] * xi + H_inv[1, 1] * yi + H_inv[1, 2]
        fw = H_inv[2, 0] * xi + H_inv[2, 1] * yi + H_inv[2, 2]
        if ti.abs(fw) < 1e-10:
            cost_out[yi, xi] = 1.0
            continue
        sx = fx / fw
        sy = fy / fw
        sum_ref = ti.f32(0.0)
        sum_target = ti.f32(0.0)
        sum_ref2 = ti.f32(0.0)
        sum_target2 = ti.f32(0.0)
        sum_cross = ti.f32(0.0)
        count = ti.f32(0.0)
        for dy in range(-patch_radius, patch_radius + 1):
            for dx in range(-patch_radius, patch_radius + 1):
                ry = yi + dy
                rx = xi + dx
                if ry >= 0 and ry < h and rx >= 0 and rx < w:
                    ty = sy + dy
                    tx = sx + dx
                    tye = ti.cast(ty, ti.i32)
                    txe = ti.cast(tx, ti.i32)
                    if tye >= 0 and tye < h - 1 and txe >= 0 and txe < w - 1:
                        wy = ty - ti.cast(tye, ti.f32)
                        wx = tx - ti.cast(txe, ti.f32)
                        v00 = target_img[tye, txe]
                        v01 = target_img[tye, txe + 1]
                        v10 = target_img[tye + 1, txe]
                        v11 = target_img[tye + 1, txe + 1]
                        target_val = ((1.0 - wy) * (1.0 - wx) * v00 + (1.0 - wy) * wx * v01 + wy * (1.0 - wx) * v10 + wy * wx * v11)
                        ref_val = ref_img[ry, rx]
                        sum_ref += ref_val
                        sum_target += target_val
                        sum_ref2 += ref_val * ref_val
                        sum_target2 += target_val * target_val
                        sum_cross += ref_val * target_val
                        count += 1.0
        if count > 1.0:
            mean_ref = sum_ref / count
            mean_target = sum_target / count
            var_ref = sum_ref2 / count - mean_ref * mean_ref
            var_target = sum_target2 / count - mean_target * mean_target
            std_ref = ti.sqrt(ti.max(var_ref, 1e-10))
            std_target = ti.sqrt(ti.max(var_target, 1e-10))
            ncc_val = (sum_cross / count - mean_ref * mean_target) / (std_ref * std_target)
            cost_out[yi, xi] = 1.0 - ti.max(0.0, ncc_val)
        else:
            cost_out[yi, xi] = 1.0


def _register_sfm_stereo(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "sfm_sweep_depths_f32", _stereo.sweep_all_depths_kernel, _nd("ref_img", f32, 2), _nd("target_img", f32, 2), _nd("K_ref", f32, 2), _nd("K_target", f32, 2), _nd("R_rel", f32, 2), _nd("t_rel", f32, 1), _nd("depth_hypotheses", f32, 1), _scalar("n_depths", i32), _scalar("h", i32), _scalar("w", i32), _scalar("patch_radius", i32), _nd("cost_volume", f32, 3))
    _add_graph(module, "sfm_warp_ncc_f32", _warp_ncc_f32, _nd("ref_img", f32, 2), _nd("target_img", f32, 2), _nd("H_inv", f32, 2), _scalar("depth", f32), _scalar("n_hypotheses", i32), _scalar("h", i32), _scalar("w", i32), _scalar("patch_radius", i32), _nd("cost_out", f32, 2))
    _add_graph(module, "sfm_winner_take_all_f32", _stereo.winner_take_all_kernel, _nd("cost_volume", f32, 3), _nd("depth_hypotheses", f32, 1), _scalar("n_depths", i32), _scalar("h", i32), _scalar("w", i32), _nd("depth_out", f32, 2), _nd("confidence_out", f32, 2))
    _add_graph(module, "sfm_bilateral_refine_depth_f32", _stereo.bilateral_refine_depth_kernel, _nd("depth_in", f32, 2), _nd("guide_img", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("sigma_s", f32), _scalar("sigma_r", f32), _nd("depth_out", f32, 2))
    # SGM and PatchMatch are scan-order regularisers over an existing plane-
    # sweep volume.  Reuse the maintained Taichi kernels rather than creating
    # compiler-only copies; the public orchestrator still controls direction
    # and iteration sequencing on the host.  These graph leaves are explicit
    # and target-qualified, so an older artifact without them fails closed at
    # the API boundary instead of silently using a CPU implementation.
    _add_graph(
        module,
        "sfm_sgm_path_f32",
        _mvs._sgm_path_kernel,
        _nd("cost", f32, 3),
        _nd("path", f32, 3),
        _scalar("dy", i32),
        _scalar("dx", i32),
        _scalar("p1", f32),
        _scalar("p2", f32),
    )
    _add_graph(
        module,
        "sfm_patchmatch_iteration_f32",
        _mvs._patchmatch_iteration_kernel,
        _nd("cost", f32, 3),
        _nd("labels", i32, 2),
        _scalar("iteration", i32),
        _scalar("random_seed", i32),
    )


def compile_sfm_stereo_aot(arch=ti.cpu, save_path="sfm_stereo.tcm") -> str:
    return _compile_one(arch, save_path, _register_sfm_stereo)


# ---------------------------------------------------------------------------
# SfM point cloud.  The f32 accumulator is a portable equivalent of the JIT
# f64/i64 implementation; host-side sorting/unique remains in point_cloud.py.
# ---------------------------------------------------------------------------


@ti.kernel
def _accumulate_voxel_sums_f32(
    points: ti.types.ndarray(ti.f32, ndim=2),
    sorted_voxel_idx: ti.types.ndarray(ti.i32, ndim=1),
    voxel_sum: ti.types.ndarray(ti.f32, ndim=2),
    voxel_count: ti.types.ndarray(ti.i32, ndim=1),
    n: ti.i32,
    max_voxels: ti.i32,
):
    for i in range(n):
        slot = ti.abs(sorted_voxel_idx[i]) % max_voxels
        ti.atomic_add(voxel_sum[slot, 0], points[i, 0])
        ti.atomic_add(voxel_sum[slot, 1], points[i, 1])
        ti.atomic_add(voxel_sum[slot, 2], points[i, 2])
        ti.atomic_add(voxel_count[slot], 1)


def _register_sfm_point_cloud(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "sfm_knn_distance_f32", _cloud.compute_knn_distance_kernel, _nd("points", f32, 2), _nd("dist_out", f32, 2), _nd("idx_out", i32, 2), _scalar("n", i32), _scalar("k", i32))
    _add_graph(module, "sfm_sor_filter_f32", _cloud.sor_filter_kernel, _nd("knn_dist", f32, 2), _nd("keep_mask", i32, 1), _scalar("n", i32), _scalar("k", i32), _scalar("std_multiplier", f32))
    _add_graph(module, "sfm_radius_outlier_f32", _cloud.radius_outlier_kernel, _nd("points", f32, 2), _nd("keep_mask", i32, 1), _scalar("n", i32), _scalar("radius", f32), _scalar("min_neighbors", i32))
    _add_graph(module, "sfm_voxel_hash_f32", _cloud.voxel_hash_kernel, _nd("points", f32, 2), _nd("voxel_indices", i32, 1), _scalar("n", i32), _scalar("voxel_size", f32))
    _add_graph(module, "sfm_voxel_accumulate_f32", _accumulate_voxel_sums_f32, _nd("points", f32, 2), _nd("sorted_voxel_idx", i32, 1), _nd("voxel_sum", f32, 2), _nd("voxel_count", i32, 1), _scalar("n", i32), _scalar("max_voxels", i32))
    _add_graph(module, "sfm_normals_pca_f32", _cloud.compute_normals_pca_kernel, _nd("points", f32, 2), _nd("knn_idx", i32, 2), _nd("normals_out", f32, 2), _scalar("n", i32), _scalar("k", i32))


def compile_sfm_point_cloud_aot(arch=ti.cpu, save_path="sfm_point_cloud.tcm") -> str:
    return _compile_one(arch, save_path, _register_sfm_point_cloud)


# ---------------------------------------------------------------------------
# SfM bundle adjustment.  Normal-equation construction is reused from the
# source module.  The update and cost stages use f32 buffers so all four
# desktop backends share the same graph ABI.
# ---------------------------------------------------------------------------


@ti.kernel
def _apply_point_update_f32(
    points_3d: ti.types.ndarray(ti.f32, ndim=2),
    delta_pts: ti.types.ndarray(ti.f32, ndim=2),
    n_pts: ti.i32,
    damping: ti.f32,
):
    for i in range(n_pts):
        for j in ti.static(range(3)):
            points_3d[i, j] += delta_pts[i, j] * damping


@ti.kernel
def _apply_camera_update_f32(
    cameras: ti.types.ndarray(ti.f32, ndim=2),
    delta_cam: ti.types.ndarray(ti.f32, ndim=2),
    n_cam: ti.i32,
    damping: ti.f32,
):
    for i in range(n_cam):
        for j in ti.static(range(7)):
            cameras[i, j] += delta_cam[i, j] * damping


@ti.kernel
def _compute_cost_f32(
    errors: ti.types.ndarray(ti.f32, ndim=1),
    n_obs: ti.i32,
    cost_out: ti.types.ndarray(ti.f32, ndim=1),
):
    total = ti.f32(0.0)
    for i in range(n_obs * 2):
        total += errors[i] * errors[i]
    cost_out[0] = total


def _register_sfm_bundle(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "sfm_reprojection_errors_f32", _ba.compute_reprojection_errors_kernel, _nd("cameras", f32, 2), _nd("points_3d", f32, 2), _nd("observations", i32, 2), _nd("observed_2d", f32, 2), _nd("errors_out", f32, 1), _scalar("n_obs", i32))
    _add_graph(module, "sfm_build_normal_equations_f32", _ba.build_jtj_jte_kernel, _nd("cameras", f32, 2), _nd("points_3d", f32, 2), _nd("observations", i32, 2), _nd("observed_2d", f32, 2), _nd("JtJ_cam", f32, 3), _nd("JtJ_pt", f32, 3), _nd("JtJ_cp", f32, 4), _nd("Jte_cam", f32, 2), _nd("Jte_pt", f32, 2), _scalar("n_obs", i32), _scalar("n_cam", i32), _scalar("n_pts", i32))
    _add_graph(module, "sfm_apply_point_update_f32", _apply_point_update_f32, _nd("points_3d", f32, 2), _nd("delta_pts", f32, 2), _scalar("n_pts", i32), _scalar("damping", f32))
    _add_graph(module, "sfm_apply_camera_update_f32", _apply_camera_update_f32, _nd("cameras", f32, 2), _nd("delta_cam", f32, 2), _scalar("n_cam", i32), _scalar("damping", f32))
    _add_graph(module, "sfm_cost_f32", _compute_cost_f32, _nd("errors", f32, 1), _scalar("n_obs", i32), _nd("cost_out", f32, 1))


def compile_sfm_bundle_aot(arch=ti.cpu, save_path="sfm_bundle.tcm") -> str:
    return _compile_one(arch, save_path, _register_sfm_bundle)


# ---------------------------------------------------------------------------
# SfM point-cloud Poisson reconstruction primitives.
# ---------------------------------------------------------------------------


def _register_sfm_poisson(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "sfm_rasterize_divergence_f32", _poisson.rasterize_divergence_kernel, _nd("points", f32, 2), _nd("normals", f32, 2), _nd("div_field", f32, 3), _scalar("n_pts", i32), _nd("grid_origin", f32, 1), _scalar("voxel_size", f32), _scalar("gx", i32), _scalar("gy", i32), _scalar("gz", i32))
    _add_graph(module, "sfm_occupancy_mask_f32", _poisson.build_occupancy_mask_kernel, _nd("points", f32, 2), _nd("mask", i32, 3), _scalar("n_pts", i32), _nd("grid_origin", f32, 1), _scalar("voxel_size", f32), _scalar("gx", i32), _scalar("gy", i32), _scalar("gz", i32), _scalar("dilate_radius", i32))
    _add_graph(module, "sfm_poisson_step_f32", _poisson.gauss_seidel_step_kernel, _nd("field", f32, 3), _nd("div_field", f32, 3), _nd("mask", i32, 3), _scalar("gx", i32), _scalar("gy", i32), _scalar("gz", i32), _scalar("omega", f32))


def compile_sfm_poisson_aot(arch=ti.cpu, save_path="sfm_poisson.tcm") -> str:
    return _compile_one(arch, save_path, _register_sfm_poisson)


# ---------------------------------------------------------------------------
# SfM registration.  Reuse the bounded point-to-plane ICP and TSDF kernels
# from ``sfm.registration`` rather than maintaining compiler-only copies.
# The host orchestrators retain the global 6x6 solve and frame sequencing;
# these graphs package only their independent accumulator/integration leaves.
# ---------------------------------------------------------------------------


def _register_sfm_registration(module) -> None:
    f32, i32 = ti.f32, ti.i32
    _add_graph(
        module,
        "sfm_icp_accumulate_f32",
        _registration._icp_accumulate_kernel,
        _nd("source", f32, 2),
        _nd("target", f32, 2),
        _nd("normals", f32, 2),
        _nd("rotation", f32, 2),
        _nd("translation", f32, 1),
        _scalar("max_distance_sq", f32),
        _nd("jtj", f32, 2),
        _nd("jtr", f32, 1),
        _nd("residuals", f32, 1),
        _nd("correspondences", i32, 1),
    )
    _add_graph(
        module,
        "sfm_tsdf_integrate_f32",
        _registration._tsdf_integrate_kernel,
        _nd("depth", f32, 2),
        _nd("intrinsics", f32, 2),
        _nd("rotation", f32, 2),
        _nd("translation", f32, 1),
        _nd("origin", f32, 1),
        _scalar("voxel_size", f32),
        _scalar("truncation", f32),
        _scalar("max_weight", i32),
        _nd("tsdf", f32, 3),
        _nd("weights", i32, 3),
    )


def compile_sfm_registration_aot(arch=ti.cpu, save_path="sfm_registration.tcm") -> str:
    """Archive the existing registration leaves for one target backend."""

    return _compile_one(arch, save_path, _register_sfm_registration)


# ---------------------------------------------------------------------------
# Panorama seam leaves
# ---------------------------------------------------------------------------


def _register_panorama(module) -> None:
    """Register the finite unary-map leaf used by exact graph-cut seams.

    The residual graph and push-relabel control flow intentionally remain in
    ``panorama.seam`` on the host. Reusing the maintained kernel here keeps
    the AOT path semantically identical to the Taichi-JIT path without trying
    to encode a dynamic adjacency graph in a static image graph.
    """

    f32 = ti.f32
    _add_graph(
        module,
        "panorama_graph_cut_unary_f32",
        _seam._graph_cut_unary_kernel,
        _nd("left_gray", f32, 2),
        _nd("right_gray", f32, 2),
        _nd("unary_left", f32, 2),
        _nd("unary_right", f32, 2),
        _nd("color_difference", f32, 2),
        _scalar("gradient_weight", f32),
        _scalar("color_weight", f32),
    )


def compile_panorama_aot(arch=ti.cpu, save_path="panorama.tcm") -> str:
    """Archive the exact graph-cut unary leaf for one target backend."""

    return _compile_one(arch, save_path, _register_panorama)


__all__ = [
    "compile_hdr_aot",
    "compile_tone_mapping_aot",
    "compile_camera_aot",
    "compile_sfm_matching_aot",
    "compile_sfm_geometry_aot",
    "compile_sfm_stereo_aot",
    "compile_sfm_point_cloud_aot",
    "compile_sfm_bundle_aot",
    "compile_sfm_poisson_aot",
    "compile_sfm_registration_aot",
    "compile_panorama_aot",
]
