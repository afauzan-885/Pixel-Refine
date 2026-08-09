"""Runtime API for the portable research AOT modules.

The high-level Camera2/SfM/HDR code remains responsible for validation,
feature policy, pyramid construction, and host-side sparse operations.  This
module exposes the array-to-array kernels as small composable building
blocks.  Every function accepts NumPy arrays, while ``ResearchAOTModule``
also provides a low-level path for callers that already own AOT buffers.

The public contract is deliberately f32/i32 on all desktop backends.  This
keeps the same graph names and buffer metadata valid for CPU, CUDA, Vulkan,
and desktop OpenGL.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from taichi_library.taichi_aot.engine import (
    InputArray,
    OutputArray,
    TaichiGPUBuffer,
    TaichiPlaceholder,
)
from . import _mod


_BUFFER_TYPES = (TaichiGPUBuffer, TaichiPlaceholder)


def _is_buffer(value) -> bool:
    return isinstance(value, _BUFFER_TYPES)


def _as_f32(value, *, ndim=None) -> np.ndarray:
    array = np.ascontiguousarray(value, dtype=np.float32)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected an array with ndim={ndim}, got {array.shape}")
    return array


def _as_i32(value, *, ndim=None) -> np.ndarray:
    array = np.ascontiguousarray(value, dtype=np.int32)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected an array with ndim={ndim}, got {array.shape}")
    return array


def _plain_ndarray(buffer):
    """View an auto-detected RGB/flow buffer as a scalar ndarray.

    ``engine.upload`` intentionally detects HxWx3 arrays as vector fields for
    the established image API.  The research graphs use explicit plain
    ndarray dimensions, so the non-owning view is required at this boundary.
    """

    if getattr(buffer, "is_vector", False):
        return buffer.view_as_vector(False)
    return buffer


def _destroy_owned(buffers):
    seen = set()
    for buffer in buffers:
        if buffer is None or id(buffer) in seen:
            continue
        seen.add(id(buffer))
        buffer.destroy()


def _make_input(value, owned):
    if _is_buffer(value):
        return value
    buffer = InputArray(np.ascontiguousarray(value))
    owned.append(buffer)
    return buffer


def _make_output(spec, owned):
    if _is_buffer(spec):
        return spec
    if isinstance(spec, np.ndarray):
        buffer = InputArray(np.ascontiguousarray(spec))
        owned.append(buffer)
        return buffer
    if isinstance(spec, tuple) and len(spec) == 2:
        shape, dtype = spec
        buffer = OutputArray(shape, dtype=dtype, is_vector=False)
        owned.append(buffer)
        return buffer
    raise TypeError(
        "output specification must be an AOT buffer, ndarray, or (shape, dtype)"
    )


def _dispatch(
    module_name: str,
    graph_name: str,
    *,
    inputs: Mapping[str, object],
    outputs: Mapping[str, object] | None = None,
    scalars: Mapping[str, object] | None = None,
    plain_ndarray: bool = True,
    return_gpu: bool = False,
):
    """Dispatch one graph and manage temporary host-created buffers.

    ``outputs`` may contain preallocated AOT buffers, initialised NumPy
    arrays (useful for atomic/compacted output kernels), or ``(shape, dtype)``
    specifications.  A single output is returned directly; multiple outputs
    are returned as a dictionary keyed by graph argument name.
    """

    owned_inputs = []
    owned_outputs = []
    arguments = {}
    try:
        for name, value in inputs.items():
            buffer = _make_input(value, owned_inputs)
            arguments[name] = (
                _plain_ndarray(buffer)
                if plain_ndarray and getattr(buffer, "ndim", 0) >= 3
                else buffer
            )

        output_buffers = {}
        for name, spec in (outputs or {}).items():
            buffer = _make_output(spec, owned_outputs)
            output_buffers[name] = buffer
            arguments[name] = (
                _plain_ndarray(buffer)
                if plain_ndarray and getattr(buffer, "ndim", 0) >= 3
                else buffer
            )

        if scalars:
            arguments.update(scalars)
        _mod(module_name).run(graph_name, **arguments)

        if return_gpu:
            _destroy_owned(owned_inputs)
            if len(output_buffers) == 1:
                return next(iter(output_buffers.values()))
            return output_buffers

        result = {name: buffer.to_numpy() for name, buffer in output_buffers.items()}
        _destroy_owned(owned_inputs + owned_outputs)
        if len(result) == 1:
            return next(iter(result.values()))
        return result
    except Exception:
        _destroy_owned(owned_inputs + owned_outputs)
        raise


def _dispatch_inplace(
    module_name: str,
    graph_name: str,
    *,
    arrays: Mapping[str, object],
    scalars: Mapping[str, object] | None = None,
    plain_ndarray: bool = True,
):
    owned = []
    arguments = {}
    buffers = {}
    try:
        for name, value in arrays.items():
            buffer = _make_input(value, owned)
            buffers[name] = buffer
            arguments[name] = (
                _plain_ndarray(buffer)
                if plain_ndarray and getattr(buffer, "ndim", 0) >= 3
                else buffer
            )
        if scalars:
            arguments.update(scalars)
        _mod(module_name).run(graph_name, **arguments)
        result = {name: buffer.to_numpy() for name, buffer in buffers.items()}
        _destroy_owned(owned)
        if len(result) == 1:
            return next(iter(result.values()))
        return result
    except Exception:
        _destroy_owned(owned)
        raise


class ResearchAOTModule:
    """Composable low-level handle for one research TCM module."""

    def __init__(self, name: str):
        if name not in RESEARCH_AOT_GRAPHS:
            raise ValueError(f"unknown research AOT module: {name!r}")
        self.name = name

    @property
    def graphs(self):
        return tuple(RESEARCH_AOT_GRAPHS[self.name])

    def run(
        self,
        graph: str,
        *,
        inputs: Mapping[str, object],
        outputs: Mapping[str, object] | None = None,
        scalars: Mapping[str, object] | None = None,
        return_gpu: bool = False,
    ):
        if graph not in self.graphs:
            raise ValueError(f"graph {graph!r} is not registered in module {self.name!r}")
        return _dispatch(
            self.name,
            graph,
            inputs=inputs,
            outputs=outputs,
            scalars=scalars,
            return_gpu=return_gpu,
        )


def research_aot_module(name: str) -> ResearchAOTModule:
    """Return a lazy module handle; the TCM is loaded on first dispatch."""

    return ResearchAOTModule(name)


# ---------------------------------------------------------------------------
# HDR and tone mapping
# ---------------------------------------------------------------------------


def hdr_weight_aot(
    img_rgb,
    lap_gray,
    *,
    noise_sigma=0.1,
    noise_power=2.0,
    exposure_sigma=0.2,
    exposure_power=1.0,
    detail_power=1.0,
    saturation_power=1.0,
    return_gpu=False,
):
    image = _as_f32(img_rgb, ndim=3)
    lap = _as_f32(lap_gray, ndim=2)
    if image.shape[:2] != lap.shape:
        raise ValueError("img_rgb and lap_gray must have matching HxW dimensions")
    h, w = image.shape[:2]
    return _dispatch(
        "hdr",
        "hdr_weight_f32",
        inputs={"img_rgb": image, "lap_gray": lap},
        outputs={"weight": ((h, w), np.float32)},
        scalars={
            "h": int(h),
            "w": int(w),
            "noise_sigma": float(noise_sigma),
            "noise_power": float(noise_power),
            "exposure_sigma": float(exposure_sigma),
            "exposure_power": float(exposure_power),
            "detail_power": float(detail_power),
            "saturation_power": float(saturation_power),
        },
        return_gpu=return_gpu,
    )


def hdr_normalize_weights_aot(weights):
    data = _as_f32(weights, ndim=3).copy()
    n_frames, h, w = data.shape
    if n_frames <= 0:
        raise ValueError("weights must contain at least one frame")
    return _dispatch_inplace(
        "hdr",
        "hdr_normalize_weights_f32",
        arrays={"weights": data},
        scalars={"h": int(h), "w": int(w), "n_frames": int(n_frames)},
    )


def tone_luminance_aot(img):
    image = _as_f32(img, ndim=3)
    h, w = image.shape[:2]
    return _dispatch(
        "tone_mapping",
        "tone_luminance_f32",
        inputs={"img": image},
        outputs={"lum": ((h, w), np.float32)},
        scalars={"h": int(h), "w": int(w)},
    )


def tone_reinhard_aot(img, *, key=0.18, lum_white=1.0, epsilon=1e-6, return_gpu=False):
    image = _as_f32(img, ndim=3)
    h, w = image.shape[:2]
    lum = tone_luminance_aot(image)
    return _dispatch(
        "tone_mapping",
        "tone_reinhard_f32",
        inputs={"img": image, "lum": lum},
        outputs={"dst": ((h, w, 3), np.float32)},
        scalars={
            "h": int(h),
            "w": int(w),
            "key": float(key),
            "lum_white": float(lum_white),
            "epsilon": float(epsilon),
        },
        return_gpu=return_gpu,
    )


def tone_srgb_aot(img, *, gamma=2.2, use_srgb_curve=True, return_gpu=False):
    image = _as_f32(img, ndim=3)
    h, w = image.shape[:2]
    graph = "tone_srgb_f32" if use_srgb_curve else "tone_srgb_simple_f32"
    return _dispatch(
        "tone_mapping",
        graph,
        inputs={"img": image},
        outputs={"dst": ((h, w, 3), np.float32)},
        scalars={"h": int(h), "w": int(w), "gamma": float(gamma)},
        return_gpu=return_gpu,
    )


def tone_simulate_exposure_aot(img, *, gain=2.0, return_gpu=False):
    image = _as_f32(img, ndim=3)
    h, w = image.shape[:2]
    return _dispatch(
        "tone_mapping",
        "tone_simulate_exposure_f32",
        inputs={"img": image},
        outputs={"bright": ((h, w, 3), np.float32)},
        scalars={"h": int(h), "w": int(w), "gain": float(gain)},
        return_gpu=return_gpu,
    )


def tone_blend_weight_aot(lum, *, target_lum=0.5, sigma=0.3):
    data = _as_f32(lum, ndim=2)
    h, w = data.shape
    return _dispatch(
        "tone_mapping",
        "tone_blend_weight_f32",
        inputs={"lum": data},
        outputs={"weight": ((h, w), np.float32)},
        scalars={
            "h": int(h),
            "w": int(w),
            "target_lum": float(target_lum),
            "sigma": float(sigma),
        },
    )


def tone_weighted_blend_aot(img_dark, img_bright, w_dark, w_bright, *, return_gpu=False):
    dark = _as_f32(img_dark, ndim=3)
    bright = _as_f32(img_bright, ndim=3)
    wd = _as_f32(w_dark, ndim=2)
    wb = _as_f32(w_bright, ndim=2)
    if dark.shape != bright.shape or dark.shape[:2] != wd.shape or wd.shape != wb.shape:
        raise ValueError("tone blend inputs must have matching image/weight dimensions")
    h, w = dark.shape[:2]
    return _dispatch(
        "tone_mapping",
        "tone_weighted_blend_f32",
        inputs={"img_dark": dark, "img_bright": bright, "w_dark": wd, "w_bright": wb},
        outputs={"dst": ((h, w, 3), np.float32)},
        scalars={"h": int(h), "w": int(w)},
        return_gpu=return_gpu,
    )


def tone_contrast_aot(img, *, contrast=1.0, brightness=0.0, return_gpu=False):
    image = _as_f32(img, ndim=3)
    h, w = image.shape[:2]
    return _dispatch(
        "tone_mapping",
        "tone_contrast_f32",
        inputs={"img": image},
        outputs={"dst": ((h, w, 3), np.float32)},
        scalars={
            "h": int(h),
            "w": int(w),
            "contrast": float(contrast),
            "brightness": float(brightness),
        },
        return_gpu=return_gpu,
    )


# ---------------------------------------------------------------------------
# Pyramid leaf adapters
# ---------------------------------------------------------------------------


def _pyramid_downsample_aot(module_name, src):
    data = _as_f32(src)
    if data.ndim not in (2, 3):
        raise ValueError("pyramid input must be a 2D or 3D array")
    h, w = data.shape[:2]
    dst_shape = (h // 2, w // 2) + (() if data.ndim == 2 else (data.shape[2],))
    if dst_shape[0] < 1 or dst_shape[1] < 1:
        raise ValueError("pyramid input is too small to downsample")
    prefix = "tone" if module_name == "tone_mapping" else module_name
    graph = f"{prefix}_downsample_{'1ch' if data.ndim == 2 else '3ch'}_f32"
    return _dispatch(
        module_name,
        graph,
        inputs={"src": data},
        outputs={"dst": (dst_shape, np.float32)},
    )


def _pyramid_upsample_aot(module_name, src, output_shape):
    data = _as_f32(src)
    target_shape = tuple(int(v) for v in output_shape)
    if data.ndim not in (2, 3) or len(target_shape) != data.ndim:
        raise ValueError("source and target pyramid dimensions must match")
    if data.ndim == 3 and target_shape[2] != data.shape[2]:
        raise ValueError("pyramid channel count cannot change during upsampling")
    prefix = "tone" if module_name == "tone_mapping" else module_name
    graph = f"{prefix}_upsample_{'1ch' if data.ndim == 2 else '3ch'}_f32"
    return _dispatch(
        module_name,
        graph,
        inputs={"src": data},
        outputs={"dst": (target_shape, np.float32)},
    )


def _pyramid_subtract_aot(module_name, image, upsampled):
    img = _as_f32(image, ndim=3)
    up = _as_f32(upsampled, ndim=3)
    if img.shape != up.shape:
        raise ValueError("image and upsampled pyramid levels must match")
    return _dispatch(
        module_name,
        f"{'tone' if module_name == 'tone_mapping' else module_name}_subtract_3ch_f32",
        inputs={"img": img, "upsampled": up},
        outputs={"lap": (img.shape, np.float32)},
    )


def _pyramid_add_aot(module_name, dst, src):
    destination = _as_f32(dst, ndim=3).copy()
    source = _as_f32(src, ndim=3)
    if destination.shape != source.shape:
        raise ValueError("pyramid levels to add must match")
    return _dispatch_inplace(
        module_name,
        f"{'tone' if module_name == 'tone_mapping' else module_name}_add_3ch_f32",
        arrays={"dst": destination, "src": source},
    )["dst"]


def _pyramid_weighted_add_aot(module_name, lap, weight, result=None):
    level = _as_f32(lap, ndim=3)
    weights = _as_f32(weight, ndim=2)
    if level.shape[:2] != weights.shape:
        raise ValueError("pyramid level and weight dimensions must match")
    accumulator = (
        np.zeros_like(level, dtype=np.float32)
        if result is None
        else _as_f32(result, ndim=3).copy()
    )
    if accumulator.shape != level.shape:
        raise ValueError("weighted pyramid accumulator shape must match level")
    return _dispatch(
        module_name,
        f"{module_name}_add_weighted_laplacian_f32",
        inputs={"lap": level, "weight": weights},
        outputs={"result": accumulator},
    )


def hdr_downsample_aot(src):
    """Run one native HDR Gaussian-pyramid downsample."""

    return _pyramid_downsample_aot("hdr", src)


def hdr_upsample_aot(src, output_shape):
    """Run one native HDR Laplacian reconstruction upsample."""

    return _pyramid_upsample_aot("hdr", src, output_shape)


def hdr_subtract_aot(image, upsampled):
    return _pyramid_subtract_aot("hdr", image, upsampled)


def hdr_add_weighted_laplacian_aot(lap, weight, result=None):
    return _pyramid_weighted_add_aot("hdr", lap, weight, result=result)


def hdr_add_aot(dst, src):
    return _pyramid_add_aot("hdr", dst, src)


def tone_downsample_aot(src):
    """Run one native tone-mapping Gaussian-pyramid downsample."""

    return _pyramid_downsample_aot("tone_mapping", src)


def tone_upsample_aot(src, output_shape):
    return _pyramid_upsample_aot("tone_mapping", src, output_shape)


def tone_subtract_aot(image, upsampled):
    return _pyramid_subtract_aot("tone_mapping", image, upsampled)


def tone_add_aot(dst, src):
    return _pyramid_add_aot("tone_mapping", dst, src)


# ---------------------------------------------------------------------------
# Camera2 leaf kernels
# ---------------------------------------------------------------------------


def camera_yuv420_aot(
    y_plane,
    u_plane,
    v_plane,
    height,
    width,
    *,
    y_row_stride=None,
    y_pixel_stride=1,
    u_row_stride=None,
    u_pixel_stride=1,
    v_row_stride=None,
    v_pixel_stride=1,
    bilinear_chroma=True,
    return_gpu=False,
):
    h, w = int(height), int(width)
    y = _as_f32(y_plane).ravel()
    u = _as_f32(u_plane).ravel()
    v = _as_f32(v_plane).ravel()
    yr = w if y_row_stride is None else int(y_row_stride)
    ur = w // 2 if u_row_stride is None else int(u_row_stride)
    vr = w // 2 if v_row_stride is None else int(v_row_stride)
    return _dispatch(
        "camera",
        "camera_yuv420_bilinear_f32" if bilinear_chroma else "camera_yuv420_f32",
        inputs={"y_plane": y, "u_plane": u, "v_plane": v},
        outputs={"dst": ((h, w, 3), np.float32)},
        scalars={
            "h": h,
            "w": w,
            "y_row_stride": yr,
            "y_pixel_stride": int(y_pixel_stride),
            "u_row_stride": ur,
            "u_pixel_stride": int(u_pixel_stride),
            "v_row_stride": vr,
            "v_pixel_stride": int(v_pixel_stride),
        },
        return_gpu=return_gpu,
    )


def _semi_planar_aot(data, height, width, graph, *, return_gpu=False):
    h, w = int(height), int(width)
    raw = _as_f32(data).ravel()
    y_size = h * w
    if raw.size < y_size + (h // 2) * w:
        raise ValueError("semi-planar input is shorter than H*W*1.5 elements")
    return _dispatch(
        "camera",
        graph,
        inputs={"y_plane": raw[:y_size], "vu" if graph.endswith("nv21_f32") else "uv": raw[y_size:]},
        outputs={"dst": ((h, w, 3), np.float32)},
        scalars={"h": h, "w": w},
        return_gpu=return_gpu,
    )


def camera_nv21_aot(data, height, width, *, return_gpu=False):
    return _semi_planar_aot(data, height, width, "camera_nv21_f32", return_gpu=return_gpu)


def camera_nv12_aot(data, height, width, *, return_gpu=False):
    return _semi_planar_aot(data, height, width, "camera_nv12_f32", return_gpu=return_gpu)


def camera_y_to_gray_aot(
    y_plane,
    height,
    width,
    *,
    row_stride=None,
    pixel_stride=1,
):
    h, w = int(height), int(width)
    y = _as_f32(y_plane).ravel()
    return _dispatch(
        "camera",
        "camera_y_to_gray_f32",
        inputs={"y_plane": y},
        outputs={"dst": ((h, w), np.float32)},
        scalars={
            "h": h,
            "w": w,
            "row_stride": w if row_stride is None else int(row_stride),
            "pixel_stride": int(pixel_stride),
        },
    )


def camera_unsharp_aot(src, blurred, *, amount=0.5, return_gpu=False):
    image = _as_f32(src, ndim=3)
    blur = _as_f32(blurred, ndim=3)
    if image.shape != blur.shape:
        raise ValueError("src and blurred must have identical shape")
    h, w = image.shape[:2]
    return _dispatch(
        "camera",
        "camera_unsharp_f32",
        inputs={"src": image, "blurred": blur},
        outputs={"dst": ((h, w, 3), np.float32)},
        scalars={"amount": float(amount), "h": int(h), "w": int(w)},
        return_gpu=return_gpu,
    )


# ---------------------------------------------------------------------------
# SfM matching and geometry
# ---------------------------------------------------------------------------


def sfm_l2_distance_aot(desc1, desc2):
    first = _as_f32(desc1, ndim=2)
    second = _as_f32(desc2, ndim=2)
    if first.shape[1] != second.shape[1]:
        raise ValueError("descriptor dimensions must match")
    n1, d = first.shape
    n2 = second.shape[0]
    return _dispatch(
        "sfm_matching",
        "sfm_l2_distance_f32",
        inputs={"desc1": first, "desc2": second},
        outputs={"dist_out": ((n1, n2), np.float32)},
        scalars={"n1": int(n1), "n2": int(n2), "d": int(d)},
    )


def sfm_knn_aot(dist_matrix, *, k=2):
    distances = _as_f32(dist_matrix, ndim=2)
    n1, n2 = distances.shape
    k = int(k)
    if k < 1 or k > n2:
        raise ValueError("k must satisfy 1 <= k <= number of train descriptors")
    result = _dispatch(
        "sfm_matching",
        "sfm_knn_f32",
        inputs={"dist_matrix": distances},
        outputs={
            "best_idx": ((n1, k), np.int32),
            "best_dist": ((n1, k), np.float32),
        },
        scalars={"n1": int(n1), "n2": int(n2), "k": k},
    )
    return result["best_idx"], result["best_dist"]


def sfm_match_l2_aot(desc1, desc2, *, k=2, ratio_threshold=0.75, cross_check=False):
    """Complete f32 brute-force matching built from three AOT stages."""
    first = _as_f32(desc1, ndim=2)
    second = _as_f32(desc2, ndim=2)
    if first.shape[1] != second.shape[1]:
        raise ValueError("descriptor dimensions must match")
    if first.shape[0] == 0 or second.shape[0] == 0:
        return np.empty((0, 2), np.int32), np.empty((0,), np.float32)

    dist12 = sfm_l2_distance_aot(first, second)
    idx12, d12 = sfm_knn_aot(dist12, k=1 if cross_check or int(k) == 1 else int(k))
    if cross_check:
        dist21 = sfm_l2_distance_aot(second, first)
        idx21, _ = sfm_knn_aot(dist21, k=1)
        train = idx12[:, 0]
        valid = (train >= 0) & (idx21[train, 0] == np.arange(first.shape[0]))
        matches = np.column_stack(
            [np.arange(first.shape[0], dtype=np.int32)[valid], train[valid]]
        )
        return matches.astype(np.int32), d12[:, 0][valid].astype(np.float32)

    k = int(k)
    if k == 1 or k > 2:
        rows = np.repeat(np.arange(first.shape[0], dtype=np.int32), k)
        cols = idx12.reshape(-1)
        dists = d12.reshape(-1)
        valid = cols >= 0
        return np.column_stack([rows[valid], cols[valid]]).astype(np.int32), dists[valid]

    # The source compaction kernel has no portable scalar return channel.
    # Initialise the tail with sentinels, then derive the accepted count.
    compact = _dispatch(
        "sfm_matching",
        "sfm_ratio_filter_f32",
        inputs={"best_dist": d12, "best_idx": idx12},
        outputs={
            "match_out": np.full((first.shape[0], 2), -1, dtype=np.int32),
            "match_dist_out": np.full(first.shape[0], -1.0, dtype=np.float32),
        },
        scalars={"n1": int(first.shape[0]), "ratio_threshold": float(ratio_threshold)},
    )
    valid = compact["match_dist_out"] >= 0.0
    return compact["match_out"][valid].astype(np.int32), compact["match_dist_out"][valid]


def _normalize_points(points, K):
    data = _as_f32(points, ndim=2)
    if data.shape[1] != 2 or K is None:
        return data
    K64 = np.asarray(K, dtype=np.float64)
    homog = np.concatenate([data.astype(np.float64), np.ones((len(data), 1))], axis=1)
    normalized = (np.linalg.inv(K64) @ homog.T).T
    return np.ascontiguousarray(normalized[:, :2], dtype=np.float32)


def sfm_build_5pt_system_aot(pts1, pts2, indices):
    first = _as_f32(pts1, ndim=2)
    second = _as_f32(pts2, ndim=2)
    idx = _as_i32(indices, ndim=1)
    if first.shape != second.shape or first.shape[1] != 2:
        raise ValueError("pts1 and pts2 must both have shape (N, 2)")
    return _dispatch(
        "sfm_geometry",
        "sfm_build_5pt_system_f32",
        inputs={"pts1": first, "pts2": second, "indices": idx},
        outputs={"ATA_out": ((9, 9), np.float32)},
    )


def sfm_batch_build_5pt_system_aot(pts1, pts2, indices_batch):
    first = _as_f32(pts1, ndim=2)
    second = _as_f32(pts2, ndim=2)
    batch = _as_i32(indices_batch, ndim=2)
    n_batch = batch.shape[0]
    return _dispatch(
        "sfm_geometry",
        "sfm_batch_build_5pt_system_f32",
        inputs={"pts1": first, "pts2": second, "indices_batch": batch},
        outputs={"ATA_batch": ((n_batch, 9, 9), np.float32)},
        scalars={"n_batch": int(n_batch)},
    )


def sfm_cheirality_minimal_aot(E, K1, K2, pts1_sample, pts2_sample, sample_indices=None):
    first = _normalize_points(pts1_sample, K1)
    second = _normalize_points(pts2_sample, K2)
    n = len(first)
    idx = np.arange(n, dtype=np.int32) if sample_indices is None else _as_i32(sample_indices, ndim=1)
    if len(second) != n or len(idx) > n:
        raise ValueError("cheirality sample arrays have incompatible lengths")
    result = _dispatch(
        "sfm_geometry",
        "sfm_cheirality_minimal_f32",
        inputs={
            "E_arr": _as_f32(E, ndim=2).reshape(-1),
            "K1": _as_f32(K1, ndim=2),
            "K2": _as_f32(K2, ndim=2),
            "pts1": first,
            "pts2": second,
            "sample_indices": idx,
        },
        outputs={"result_out": ((3,), np.int32)},
        scalars={"n_samples": int(len(idx))},
    )
    return result


def sfm_cheirality_full_aot(R, t, K1, K2, pts1, pts2):
    first = _normalize_points(pts1, K1)
    second = _normalize_points(pts2, K2)
    if first.shape != second.shape or first.shape[1] != 2:
        raise ValueError("cheirality point arrays must both have shape (N, 2)")
    n = first.shape[0]
    result = _dispatch(
        "sfm_geometry",
        "sfm_cheirality_full_f32",
        inputs={
            "R_arr": _as_f32(R, ndim=2).reshape(-1),
            "t_arr": _as_f32(t, ndim=1),
            "pts1": first,
            "pts2": second,
        },
        outputs={
            "depth_out": ((n, 2), np.float32),
            "inlier_mask": ((n,), np.int32),
        },
        scalars={"n_pts": int(n)},
    )
    return result["depth_out"], result["inlier_mask"], int(result["inlier_mask"].sum())


def sfm_triangulate_adaptive_aot(
    pts1,
    pts2,
    P1,
    P2,
    C1,
    C2,
    *,
    parallax_threshold=4.0,
    K1=None,
    K2=None,
):
    first = _normalize_points(pts1, K1)
    second = _normalize_points(pts2, K2)
    if first.shape != second.shape:
        raise ValueError("triangulation point arrays must have matching shape")
    n = first.shape[0]
    result = _dispatch(
        "sfm_geometry",
        "sfm_triangulate_adaptive_f32",
        inputs={
            "pts1": first,
            "pts2": second,
            "P1": _as_f32(P1, ndim=2),
            "P2": _as_f32(P2, ndim=2),
            "C1": _as_f32(C1, ndim=1),
            "C2": _as_f32(C2, ndim=1),
        },
        outputs={
            "points_3d_out": ((n, 3), np.float32),
            "method_used_out": ((n,), np.int32),
        },
        scalars={"n_pts": int(n), "parallax_threshold": float(parallax_threshold)},
    )
    return result["points_3d_out"], result["method_used_out"]


# ---------------------------------------------------------------------------
# SfM stereo, point cloud, bundle adjustment, and Poisson primitives
# ---------------------------------------------------------------------------


def sfm_warp_ncc_aot(ref_img, target_img, H_inv, *, depth=1.0, n_hypotheses=1, patch_radius=2):
    ref = _as_f32(ref_img, ndim=2)
    target = _as_f32(target_img, ndim=2)
    if ref.shape != target.shape:
        raise ValueError("reference and target images must have matching shape")
    h, w = ref.shape
    return _dispatch(
        "sfm_stereo",
        "sfm_warp_ncc_f32",
        inputs={"ref_img": ref, "target_img": target, "H_inv": _as_f32(H_inv, ndim=2)},
        outputs={"cost_out": ((h, w), np.float32)},
        scalars={
            "depth": float(depth),
            "n_hypotheses": int(n_hypotheses),
            "h": int(h),
            "w": int(w),
            "patch_radius": int(patch_radius),
        },
    )


def sfm_sweep_depths_aot(
    ref_img,
    target_img,
    K_ref,
    K_target,
    R_rel,
    t_rel,
    depth_hypotheses,
    *,
    patch_radius=2,
):
    ref = _as_f32(ref_img, ndim=2)
    target = _as_f32(target_img, ndim=2)
    h, w = ref.shape
    depths = _as_f32(depth_hypotheses, ndim=1)
    return _dispatch(
        "sfm_stereo",
        "sfm_sweep_depths_f32",
        inputs={
            "ref_img": ref,
            "target_img": target,
            "K_ref": _as_f32(K_ref, ndim=2),
            "K_target": _as_f32(K_target, ndim=2),
            "R_rel": _as_f32(R_rel, ndim=2),
            "t_rel": _as_f32(t_rel, ndim=1),
            "depth_hypotheses": depths,
        },
        outputs={"cost_volume": ((len(depths), h, w), np.float32)},
        scalars={
            "n_depths": int(len(depths)),
            "h": int(h),
            "w": int(w),
            "patch_radius": int(patch_radius),
        },
    )


def sfm_winner_take_all_aot(cost_volume, depth_hypotheses):
    volume = _as_f32(cost_volume, ndim=3)
    depths = _as_f32(depth_hypotheses, ndim=1)
    n_depths, h, w = volume.shape
    if len(depths) != n_depths:
        raise ValueError("depth hypothesis count must match cost volume")
    result = _dispatch(
        "sfm_stereo",
        "sfm_winner_take_all_f32",
        inputs={"cost_volume": volume, "depth_hypotheses": depths},
        outputs={
            "depth_out": ((h, w), np.float32),
            "confidence_out": ((h, w), np.float32),
        },
        scalars={"n_depths": int(n_depths), "h": int(h), "w": int(w)},
    )
    return result["depth_out"], result["confidence_out"]


def sfm_bilateral_refine_depth_aot(depth_in, guide_img, *, sigma_s=2.0, sigma_r=0.1):
    depth = _as_f32(depth_in, ndim=2)
    guide = _as_f32(guide_img, ndim=2)
    if depth.shape != guide.shape:
        raise ValueError("depth and guide image must have matching shape")
    h, w = depth.shape
    return _dispatch(
        "sfm_stereo",
        "sfm_bilateral_refine_depth_f32",
        inputs={"depth_in": depth, "guide_img": guide},
        outputs={"depth_out": ((h, w), np.float32)},
        scalars={"h": int(h), "w": int(w), "sigma_s": float(sigma_s), "sigma_r": float(sigma_r)},
    )


def sfm_knn_distance_aot(points, *, k=20):
    data = _as_f32(points, ndim=2)
    if data.shape[1] != 3:
        raise ValueError("points must have shape (N, 3)")
    n, k = len(data), int(k)
    if n == 0:
        return np.empty((0, k), np.float32), np.empty((0, k), np.int32)
    if k < 1 or k >= n:
        raise ValueError("k must satisfy 1 <= k < N")
    result = _dispatch(
        "sfm_point_cloud",
        "sfm_knn_distance_f32",
        inputs={"points": data},
        outputs={
            "dist_out": ((n, k), np.float32),
            "idx_out": ((n, k), np.int32),
        },
        scalars={"n": n, "k": k},
    )
    return result["dist_out"], result["idx_out"]


def sfm_sor_filter_aot(knn_dist, *, std_multiplier=2.0):
    distances = _as_f32(knn_dist, ndim=2)
    n, k = distances.shape
    return _dispatch(
        "sfm_point_cloud",
        "sfm_sor_filter_f32",
        inputs={"knn_dist": distances},
        outputs={"keep_mask": ((n,), np.int32)},
        scalars={"n": n, "k": k, "std_multiplier": float(std_multiplier)},
    )


def sfm_radius_filter_aot(points, *, radius=0.1, min_neighbors=5):
    data = _as_f32(points, ndim=2)
    n = len(data)
    return _dispatch(
        "sfm_point_cloud",
        "sfm_radius_outlier_f32",
        inputs={"points": data},
        outputs={"keep_mask": ((n,), np.int32)},
        scalars={"n": n, "radius": float(radius), "min_neighbors": int(min_neighbors)},
    )


def sfm_voxel_hash_aot(points, *, voxel_size=0.01):
    data = _as_f32(points, ndim=2)
    n = len(data)
    return _dispatch(
        "sfm_point_cloud",
        "sfm_voxel_hash_f32",
        inputs={"points": data},
        outputs={"voxel_indices": ((n,), np.int32)},
        scalars={"n": n, "voxel_size": float(voxel_size)},
    )


def sfm_voxel_accumulate_aot(points, sorted_voxel_idx, *, max_voxels):
    data = _as_f32(points, ndim=2)
    indices = _as_i32(sorted_voxel_idx, ndim=1)
    if len(data) != len(indices):
        raise ValueError("points and sorted_voxel_idx must have equal length")
    max_voxels = int(max_voxels)
    if max_voxels <= 0:
        raise ValueError("max_voxels must be positive")
    result = _dispatch(
        "sfm_point_cloud",
        "sfm_voxel_accumulate_f32",
        inputs={"points": data, "sorted_voxel_idx": indices},
        outputs={
            "voxel_sum": (np.zeros((max_voxels, 3), np.float32)),
            "voxel_count": (np.zeros((max_voxels,), np.int32)),
        },
        scalars={"n": len(data), "max_voxels": max_voxels},
    )
    return result["voxel_sum"], result["voxel_count"]


def sfm_normals_pca_aot(points, knn_idx):
    data = _as_f32(points, ndim=2)
    indices = _as_i32(knn_idx, ndim=2)
    n, k = indices.shape
    if data.shape[0] != n or data.shape[1] != 3:
        raise ValueError("points and knn_idx have incompatible shapes")
    return _dispatch(
        "sfm_point_cloud",
        "sfm_normals_pca_f32",
        inputs={"points": data, "knn_idx": indices},
        outputs={"normals_out": ((n, 3), np.float32)},
        scalars={"n": n, "k": k},
    )


def sfm_reprojection_errors_aot(cameras, points_3d, observations, observed_2d):
    cams = _as_f32(cameras, ndim=2)
    points = _as_f32(points_3d, ndim=2)
    obs = _as_i32(observations, ndim=2)
    observed = _as_f32(observed_2d, ndim=2)
    n_obs = len(obs)
    return _dispatch(
        "sfm_bundle",
        "sfm_reprojection_errors_f32",
        inputs={"cameras": cams, "points_3d": points, "observations": obs, "observed_2d": observed},
        outputs={"errors_out": ((n_obs * 2,), np.float32)},
        scalars={"n_obs": n_obs},
    )


def sfm_bundle_normal_equations_aot(cameras, points_3d, observations, observed_2d):
    cams = _as_f32(cameras, ndim=2)
    points = _as_f32(points_3d, ndim=2)
    obs = _as_i32(observations, ndim=2)
    observed = _as_f32(observed_2d, ndim=2)
    n_cam, n_pts, n_obs = len(cams), len(points), len(obs)
    result = _dispatch(
        "sfm_bundle",
        "sfm_build_normal_equations_f32",
        inputs={"cameras": cams, "points_3d": points, "observations": obs, "observed_2d": observed},
        outputs={
            "JtJ_cam": np.zeros((n_cam, 6, 6), np.float32),
            "JtJ_pt": np.zeros((n_pts, 3, 3), np.float32),
            "JtJ_cp": np.zeros((n_cam, n_pts, 6, 3), np.float32),
            "Jte_cam": np.zeros((n_cam, 6), np.float32),
            "Jte_pt": np.zeros((n_pts, 3), np.float32),
        },
        scalars={"n_obs": n_obs, "n_cam": n_cam, "n_pts": n_pts},
    )
    return result


def sfm_apply_point_update_aot(points_3d, delta_pts, *, damping=1.0):
    points = _as_f32(points_3d, ndim=2).copy()
    delta = _as_f32(delta_pts, ndim=2)
    if points.shape != delta.shape or points.shape[1] != 3:
        raise ValueError("points_3d and delta_pts must have shape (N, 3)")
    return _dispatch_inplace(
        "sfm_bundle",
        "sfm_apply_point_update_f32",
        arrays={"points_3d": points, "delta_pts": delta},
        scalars={"n_pts": len(points), "damping": float(damping)},
    )["points_3d"]


def sfm_apply_camera_update_aot(cameras, delta_cam, *, damping=1.0):
    cams = _as_f32(cameras, ndim=2).copy()
    delta = _as_f32(delta_cam, ndim=2)
    if delta.shape[1] < 7 or delta.shape[0] != cams.shape[0]:
        raise ValueError("delta_cam must have shape (n_camera, >=7)")
    return _dispatch_inplace(
        "sfm_bundle",
        "sfm_apply_camera_update_f32",
        arrays={"cameras": cams, "delta_cam": delta},
        scalars={"n_cam": len(cams), "damping": float(damping)},
    )["cameras"]


def sfm_cost_aot(errors, *, n_obs=None):
    data = _as_f32(errors, ndim=1)
    if n_obs is None:
        if len(data) % 2:
            raise ValueError("errors length must be even")
        n_obs = len(data) // 2
    return float(
        _dispatch(
            "sfm_bundle",
            "sfm_cost_f32",
            inputs={"errors": data},
            outputs={"cost_out": ((1,), np.float32)},
            scalars={"n_obs": int(n_obs)},
        )[0]
    )


def sfm_poisson_rasterize_aot(points, normals, grid_origin, *, voxel_size, gx, gy, gz):
    pts = _as_f32(points, ndim=2)
    nrm = _as_f32(normals, ndim=2)
    # The native kernel accumulates with atomic_add.  Supplying an explicit
    # zero buffer is required on GPU backends because an output allocation is
    # not guaranteed to be cleared before the first atomic update.
    div_field = np.zeros((int(gx), int(gy), int(gz)), dtype=np.float32)
    return _dispatch(
        "sfm_poisson",
        "sfm_rasterize_divergence_f32",
        inputs={"points": pts, "normals": nrm, "grid_origin": _as_f32(grid_origin, ndim=1)},
        outputs={"div_field": div_field},
        scalars={
            "n_pts": len(pts),
            "voxel_size": float(voxel_size),
            "gx": int(gx),
            "gy": int(gy),
            "gz": int(gz),
        },
    )


def sfm_poisson_occupancy_aot(points, grid_origin, *, voxel_size, gx, gy, gz, dilate_radius=1):
    pts = _as_f32(points, ndim=2)
    mask = np.zeros((int(gx), int(gy), int(gz)), dtype=np.int32)
    return _dispatch(
        "sfm_poisson",
        "sfm_occupancy_mask_f32",
        inputs={"points": pts, "grid_origin": _as_f32(grid_origin, ndim=1)},
        outputs={"mask": mask},
        scalars={
            "n_pts": len(pts),
            "voxel_size": float(voxel_size),
            "gx": int(gx),
            "gy": int(gy),
            "gz": int(gz),
            "dilate_radius": int(dilate_radius),
        },
    )


def sfm_poisson_step_aot(field, div_field, mask, *, omega=1.0):
    current = _as_f32(field, ndim=3).copy()
    divergence = _as_f32(div_field, ndim=3)
    occupancy = _as_i32(mask, ndim=3)
    if current.shape != divergence.shape or current.shape != occupancy.shape:
        raise ValueError("field, div_field, and mask must have matching shape")
    gx, gy, gz = current.shape
    return _dispatch_inplace(
        "sfm_poisson",
        "sfm_poisson_step_f32",
        arrays={"field": current, "div_field": divergence, "mask": occupancy},
        scalars={"gx": gx, "gy": gy, "gz": gz, "omega": float(omega)},
    )["field"]


RESEARCH_AOT_GRAPHS = {
    "hdr": (
        "hdr_weight_f32",
        "hdr_normalize_weights_f32",
        "hdr_downsample_3ch_f32",
        "hdr_downsample_1ch_f32",
        "hdr_upsample_3ch_f32",
        "hdr_upsample_1ch_f32",
        "hdr_subtract_3ch_f32",
        "hdr_add_weighted_laplacian_f32",
        "hdr_add_3ch_f32",
    ),
    "tone_mapping": (
        "tone_luminance_f32",
        "tone_reinhard_f32",
        "tone_srgb_f32",
        "tone_srgb_simple_f32",
        "tone_simulate_exposure_f32",
        "tone_blend_weight_f32",
        "tone_weighted_blend_f32",
        "tone_contrast_f32",
        "tone_downsample_3ch_f32",
        "tone_downsample_1ch_f32",
        "tone_upsample_3ch_f32",
        "tone_upsample_1ch_f32",
        "tone_subtract_3ch_f32",
        "tone_add_3ch_f32",
    ),
    "camera": (
        "camera_yuv420_f32",
        "camera_yuv420_bilinear_f32",
        "camera_nv21_f32",
        "camera_nv12_f32",
        "camera_y_to_gray_f32",
        "camera_unsharp_f32",
    ),
    "sfm_matching": (
        "sfm_l2_distance_f32",
        "sfm_knn_f32",
        "sfm_ratio_filter_f32",
    ),
    "sfm_geometry": (
        "sfm_build_5pt_system_f32",
        "sfm_batch_build_5pt_system_f32",
        "sfm_cheirality_minimal_f32",
        "sfm_cheirality_full_f32",
        "sfm_triangulate_adaptive_f32",
    ),
    "sfm_stereo": (
        "sfm_sweep_depths_f32",
        "sfm_warp_ncc_f32",
        "sfm_winner_take_all_f32",
        "sfm_bilateral_refine_depth_f32",
    ),
    "sfm_point_cloud": (
        "sfm_knn_distance_f32",
        "sfm_sor_filter_f32",
        "sfm_radius_outlier_f32",
        "sfm_voxel_hash_f32",
        "sfm_voxel_accumulate_f32",
        "sfm_normals_pca_f32",
    ),
    "sfm_bundle": (
        "sfm_reprojection_errors_f32",
        "sfm_build_normal_equations_f32",
        "sfm_apply_point_update_f32",
        "sfm_apply_camera_update_f32",
        "sfm_cost_f32",
    ),
    "sfm_poisson": (
        "sfm_rasterize_divergence_f32",
        "sfm_occupancy_mask_f32",
        "sfm_poisson_step_f32",
    ),
}


__all__ = [
    "ResearchAOTModule",
    "research_aot_module",
    "RESEARCH_AOT_GRAPHS",
    "hdr_weight_aot",
    "hdr_normalize_weights_aot",
    "tone_luminance_aot",
    "tone_reinhard_aot",
    "tone_srgb_aot",
    "tone_simulate_exposure_aot",
    "tone_blend_weight_aot",
    "tone_weighted_blend_aot",
    "tone_contrast_aot",
    "hdr_downsample_aot",
    "hdr_upsample_aot",
    "hdr_subtract_aot",
    "hdr_add_weighted_laplacian_aot",
    "hdr_add_aot",
    "tone_downsample_aot",
    "tone_upsample_aot",
    "tone_subtract_aot",
    "tone_add_aot",
    "camera_yuv420_aot",
    "camera_nv21_aot",
    "camera_nv12_aot",
    "camera_y_to_gray_aot",
    "camera_unsharp_aot",
    "sfm_l2_distance_aot",
    "sfm_knn_aot",
    "sfm_match_l2_aot",
    "sfm_build_5pt_system_aot",
    "sfm_batch_build_5pt_system_aot",
    "sfm_cheirality_minimal_aot",
    "sfm_cheirality_full_aot",
    "sfm_triangulate_adaptive_aot",
    "sfm_warp_ncc_aot",
    "sfm_sweep_depths_aot",
    "sfm_winner_take_all_aot",
    "sfm_bilateral_refine_depth_aot",
    "sfm_knn_distance_aot",
    "sfm_sor_filter_aot",
    "sfm_radius_filter_aot",
    "sfm_voxel_hash_aot",
    "sfm_voxel_accumulate_aot",
    "sfm_normals_pca_aot",
    "sfm_reprojection_errors_aot",
    "sfm_bundle_normal_equations_aot",
    "sfm_apply_point_update_aot",
    "sfm_apply_camera_update_aot",
    "sfm_cost_aot",
    "sfm_poisson_rasterize_aot",
    "sfm_poisson_occupancy_aot",
    "sfm_poisson_step_aot",
]
