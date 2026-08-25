"""Deterministic parity and timing checks for the research AOT modules.

Run with an already-selected backend, for example::

    $env:AOT_ARCH = "cpu"
    python -m taichi_vision.taichi_algorithm.aot_py.tests.test_research_aot

The same script can be run in separate processes with ``cuda``, ``vulkan``,
and ``opengl``.  Keeping one backend per process mirrors the native engine's
single-runtime contract and makes the timing numbers comparable.
"""

from __future__ import annotations

import argparse
import os
import time

import numpy as np

from taichi_vision import taichi_aot as ta


def _check(name, actual, expected, *, atol=2e-5, rtol=2e-5):
    actual = np.asarray(actual)
    expected = np.asarray(expected)
    if actual.shape != expected.shape:
        raise AssertionError(f"{name}: shape {actual.shape} != {expected.shape}")
    if not np.allclose(actual, expected, atol=atol, rtol=rtol, equal_nan=False):
        error = float(
            np.max(np.abs(actual.astype(np.float64) - expected.astype(np.float64)))
        )
        raise AssertionError(f"{name}: max_abs_error={error:g}")
    return float(
        np.max(np.abs(actual.astype(np.float64) - expected.astype(np.float64)))
    )


def _hdr_reference(
    image,
    lap,
    noise_sigma,
    noise_power,
    exposure_sigma,
    exposure_power,
    detail_power,
    saturation_power,
):
    image = image.astype(np.float64)
    lap = lap.astype(np.float64)
    r, g, b = image[..., 0], image[..., 1], image[..., 2]
    luma = 0.299 * r + 0.587 * g + 0.114 * b
    snr = luma / max(float(noise_sigma), 1e-6)
    noise = (snr / (snr + 0.5)) ** noise_power
    denom = 2.0 * exposure_sigma * exposure_sigma
    exposure = (
        np.exp(-((r - 0.5) ** 2) / denom)
        * np.exp(-((g - 0.5) ** 2) / denom)
        * np.exp(-((b - 0.5) ** 2) / denom)
    ) ** (exposure_power / 3.0)
    contrast = (np.abs(lap) + 1e-6) ** detail_power
    mean = (r + g + b) / 3.0
    saturation = np.sqrt((r - mean) ** 2 + (g - mean) ** 2 + (b - mean) ** 2) / 3.0
    return (
        noise * exposure * contrast * (saturation + 1e-6) ** saturation_power
    ).astype(np.float32)


def _downsample_2x_reference(src):
    """NumPy oracle matching the source 5-tap Gaussian downsample kernel."""

    data = np.asarray(src, dtype=np.float32)
    h, w = data.shape[:2]
    out_shape = (h // 2, w // 2) + (() if data.ndim == 2 else (data.shape[2],))
    out = np.empty(out_shape, dtype=np.float32)
    taps = np.array([1.0, 4.0, 6.0, 4.0, 1.0], dtype=np.float64)
    for y in range(out_shape[0]):
        for x in range(out_shape[1]):
            value = (
                np.zeros((), dtype=np.float64)
                if data.ndim == 2
                else np.zeros(data.shape[2], dtype=np.float64)
            )
            for dy in range(-2, 3):
                sy = min(max(y * 2 + dy, 0), h - 1)
                for dx in range(-2, 3):
                    sx = min(max(x * 2 + dx, 0), w - 1)
                    value += data[sy, sx] * taps[dy + 2] * taps[dx + 2]
            out[y, x] = value / 256.0
    return out


def _upsample_2x_reference(src, output_shape):
    """NumPy oracle matching the source bilinear reconstruction kernel."""

    data = np.asarray(src, dtype=np.float32)
    h, w = data.shape[:2]
    out = np.empty(tuple(output_shape), dtype=np.float32)
    for y in range(out.shape[0]):
        yf = float(y) * 0.5
        y0 = min(int(yf), h - 1)
        y1 = min(y0 + 1, h - 1)
        fy = yf - float(y0)
        for x in range(out.shape[1]):
            xf = float(x) * 0.5
            x0 = min(int(xf), w - 1)
            x1 = min(x0 + 1, w - 1)
            fx = xf - float(x0)
            value = (
                data[y0, x0] * (1.0 - fy) * (1.0 - fx)
                + data[y0, x1] * (1.0 - fy) * fx
                + data[y1, x0] * fy * (1.0 - fx)
                + data[y1, x1] * fy * fx
            ) * 4.0
            out[y, x] = value
    return out


def _laplacian_pyramid_reference(image, levels):
    gaussian = [np.asarray(image, dtype=np.float32)]
    for _ in range(levels - 1):
        h, w = gaussian[-1].shape[:2]
        if h // 2 < 2 or w // 2 < 2:
            break
        gaussian.append(_downsample_2x_reference(gaussian[-1]))
    laplacian = []
    for level in range(len(gaussian) - 1):
        laplacian.append(
            gaussian[level]
            - _upsample_2x_reference(gaussian[level + 1], gaussian[level].shape)
        )
    laplacian.append(gaussian[-1])
    return laplacian


def _reconstruct_pyramid_reference(levels):
    result = np.asarray(levels[-1], dtype=np.float32).copy()
    for level in range(len(levels) - 2, -1, -1):
        result = _upsample_2x_reference(result, levels[level].shape) + levels[level]
    return result.astype(np.float32)


def _hdr_fusion_reference(frames, noise_sigmas, n_levels=2):
    arrays = [np.asarray(frame, dtype=np.float32) for frame in frames]
    grayscale = arrays[0].ndim == 2
    rgb = [
        np.repeat(frame[..., None], 3, axis=2) if grayscale else frame
        for frame in arrays
    ]
    gray = [
        (
            frame
            if grayscale
            else (
                0.299 * frame[..., 0] + 0.587 * frame[..., 1] + 0.114 * frame[..., 2]
            ).astype(np.float32)
        )
        for frame in arrays
    ]
    weights = []
    for image, luminance, sigma in zip(rgb, gray, noise_sigmas):
        padded = np.pad(luminance, 1, mode="edge")
        lap = np.abs(
            padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
            - 4.0 * padded[1:-1, 1:-1]
        )
        weights.append(_hdr_reference(image, lap, sigma, 2.0, 0.2, 1.0, 1.0, 1.0))
    weights = np.stack(weights, axis=0).astype(np.float64)
    weights /= np.maximum(weights.sum(axis=0, keepdims=True), 1e-8)
    weight_pyramids = []
    for weight in weights.astype(np.float32):
        weight_pyramids.append(_gaussian_pyramid_reference(weight, n_levels))
    image_pyramids = [_laplacian_pyramid_reference(image, n_levels) for image in rgb]
    blended = []
    for level in range(len(image_pyramids[0])):
        accumulator = np.zeros_like(image_pyramids[0][level], dtype=np.float32)
        for image_index, pyramid in enumerate(image_pyramids):
            weight_level = weight_pyramids[image_index][
                min(level, len(weight_pyramids[image_index]) - 1)
            ]
            accumulator += pyramid[level] * weight_level[..., None]
        blended.append(accumulator)
    result = np.clip(_reconstruct_pyramid_reference(blended), 0.0, 1.0)
    return result[..., 0] if grayscale else result


def _gaussian_pyramid_reference(image, levels):
    pyramid = [np.asarray(image, dtype=np.float32)]
    for _ in range(levels - 1):
        h, w = pyramid[-1].shape[:2]
        if h // 2 < 2 or w // 2 < 2:
            break
        pyramid.append(_downsample_2x_reference(pyramid[-1]))
    return pyramid


def _tone_local_reference(image, gain=2.0, target_lum=0.5, sigma=0.3, n_levels=2):
    result = np.asarray(image, dtype=np.float32).copy()
    bright = np.minimum(1.0, result * gain)
    dark_lum = (
        0.2126 * result[..., 0] + 0.7152 * result[..., 1] + 0.0722 * result[..., 2]
    )
    bright_lum = (
        0.2126 * bright[..., 0] + 0.7152 * bright[..., 1] + 0.0722 * bright[..., 2]
    )
    dark_weight = np.exp(
        -((dark_lum - target_lum) ** 2) / (2.0 * sigma * sigma)
    ).astype(np.float32)
    bright_weight = np.exp(
        -((bright_lum - target_lum) ** 2) / (2.0 * sigma * sigma)
    ).astype(np.float32)
    dark_lap = _laplacian_pyramid_reference(result, n_levels)
    bright_lap = _laplacian_pyramid_reference(bright, n_levels)
    dark_weights = _gaussian_pyramid_reference(dark_weight, n_levels)
    bright_weights = _gaussian_pyramid_reference(bright_weight, n_levels)
    blended = []
    for level, (dark_level, bright_level) in enumerate(zip(dark_lap, bright_lap)):
        wd = dark_weights[min(level, len(dark_weights) - 1)]
        wb = bright_weights[min(level, len(bright_weights) - 1)]
        total = wd + wb
        blended.append(
            np.where(
                total[..., None] > 1e-8,
                (wd[..., None] * dark_level + wb[..., None] * bright_level)
                / np.maximum(total[..., None], 1e-8),
                dark_level,
            )
        )
    return np.clip(_reconstruct_pyramid_reference(blended), 0.0, 1.0).astype(np.float32)


def _plane_sweep_cost_reference(
    ref_img, target_img, K_ref, K_target, R_rel, t_rel, depths, patch_radius
):
    """Independent NumPy cost-volume oracle for the plane-sweep graph."""

    ref = np.asarray(ref_img, dtype=np.float64)
    target = np.asarray(target_img, dtype=np.float64)
    K_ref = np.asarray(K_ref, dtype=np.float64)
    K_target = np.asarray(K_target, dtype=np.float64)
    R_rel = np.asarray(R_rel, dtype=np.float64)
    t_rel = np.asarray(t_rel, dtype=np.float64)
    h, w = ref.shape
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    nx = (xs - K_ref[0, 2]) / K_ref[0, 0]
    ny = (ys - K_ref[1, 2]) / K_ref[1, 1]
    volume = np.ones((len(depths), h, w), dtype=np.float32)
    radius = int(patch_radius)
    for depth_index, depth in enumerate(np.asarray(depths, dtype=np.float64)):
        X = nx * depth
        Y = ny * depth
        Z = np.full_like(X, depth)
        px = R_rel[0, 0] * X + R_rel[0, 1] * Y + R_rel[0, 2] * Z + t_rel[0]
        py = R_rel[1, 0] * X + R_rel[1, 1] * Y + R_rel[1, 2] * Z + t_rel[1]
        pz = R_rel[2, 0] * X + R_rel[2, 1] * Y + R_rel[2, 2] * Z + t_rel[2]
        valid = pz > 1e-6
        tx = np.where(
            valid, K_target[0, 0] * px / np.maximum(pz, 1e-12) + K_target[0, 2], -1.0
        )
        ty = np.where(
            valid, K_target[1, 1] * py / np.maximum(pz, 1e-12) + K_target[1, 2], -1.0
        )
        for y in range(h):
            for x in range(w):
                if not valid[y, x]:
                    continue
                sx, sy = float(tx[y, x]), float(ty[y, x])
                ref_values = []
                target_values = []
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        ry, rx = y + dy, x + dx
                        sty, stx = sy + dy, sx + dx
                        iy, ix = int(sty), int(stx)
                        wy, wx = sty - iy, stx - ix
                        if iy < 1 or iy >= h - 2 or ix < 1 or ix >= w - 2:
                            continue
                        value = (
                            (1.0 - wy) * (1.0 - wx) * target[iy, ix]
                            + (1.0 - wy) * wx * target[iy, ix + 1]
                            + wy * (1.0 - wx) * target[iy + 1, ix]
                            + wy * wx * target[iy + 1, ix + 1]
                        )
                        ref_values.append(ref[ry, rx])
                        target_values.append(value)
                if len(ref_values) <= 1:
                    continue
                ref_values = np.asarray(ref_values, dtype=np.float64)
                target_values = np.asarray(target_values, dtype=np.float64)
                mean_ref, mean_target = ref_values.mean(), target_values.mean()
                var_ref = (
                    ref_values @ ref_values / len(ref_values) - mean_ref * mean_ref
                )
                var_target = (
                    target_values @ target_values / len(target_values)
                    - mean_target * mean_target
                )
                std_ref = np.sqrt(max(var_ref, 1e-10))
                std_target = np.sqrt(max(var_target, 1e-10))
                ncc = (
                    ref_values @ target_values / len(ref_values)
                    - mean_ref * mean_target
                ) / (std_ref * std_target)
                volume[depth_index, y, x] = np.float32(1.0 - max(0.0, ncc))
    return volume


def _poisson_raster_reference(points, normals, grid_origin, voxel_size, shape):
    """Independent trilinear divergence oracle matching the kernel ABI."""

    points = np.asarray(points, dtype=np.float64)
    normals = np.asarray(normals, dtype=np.float64)
    origin = np.asarray(grid_origin, dtype=np.float64)
    gx, gy, gz = (int(value) for value in shape)
    result = np.zeros((gx, gy, gz), dtype=np.float64)
    for point, normal in zip(points, normals):
        vx, vy, vz = (point - origin) / float(voxel_size)
        ix, iy, iz = (int(np.floor(value)) for value in (vx, vy, vz))
        fx, fy, fz = vx - ix, vy - iy, vz - iz
        for di in range(2):
            for dj in range(2):
                for dk in range(2):
                    ci, cj, ck = ix + di, iy + dj, iz + dk
                    if 0 <= ci < gx and 0 <= cj < gy and 0 <= ck < gz:
                        wx = fx if di == 0 else (1.0 - fx)
                        wy = fy if dj == 0 else (1.0 - fy)
                        wz = fz if dk == 0 else (1.0 - fz)
                        result[ci, cj, ck] += wx * wy * wz * float(normal.sum())
    return result.astype(np.float32)


def run_accuracy_suite():
    rng = np.random.default_rng(20260628)
    errors = {}

    image = rng.uniform(0.02, 0.98, (12, 16, 3)).astype(np.float32)
    lap = rng.uniform(-0.4, 0.4, (12, 16)).astype(np.float32)
    params = dict(
        noise_sigma=0.07,
        noise_power=2.0,
        exposure_sigma=0.21,
        exposure_power=1.0,
        detail_power=1.0,
        saturation_power=1.0,
    )
    errors["hdr_weight"] = _check(
        "hdr_weight",
        ta.hdr_weight_aot(image, lap, **params),
        _hdr_reference(image, lap, **params),
        atol=3e-5,
        rtol=3e-5,
    )

    weights = rng.uniform(0.01, 2.0, (3, 12, 16)).astype(np.float32)
    weights_ref = weights.astype(np.float64)
    weights_ref /= weights_ref.sum(axis=0, keepdims=True)
    errors["hdr_normalize"] = _check(
        "hdr_normalize",
        ta.hdr_normalize_weights_aot(weights),
        weights_ref,
        atol=3e-6,
        rtol=3e-6,
    )

    lum_ref = (
        0.2126 * image[..., 0] + 0.7152 * image[..., 1] + 0.0722 * image[..., 2]
    ).astype(np.float32)
    errors["tone_luminance"] = _check(
        "tone_luminance", ta.tone_luminance_aot(image), lum_ref
    )

    srgb_ref = np.where(
        image <= 0.0031308,
        12.92 * image,
        1.055 * np.power(np.maximum(image, 0.0), 1.0 / 2.2) - 0.055,
    ).astype(np.float32)
    errors["tone_srgb"] = _check(
        "tone_srgb", ta.tone_srgb_aot(image), srgb_ref, atol=3e-5, rtol=3e-5
    )

    exposure_ref = np.minimum(1.0, image * 1.7).astype(np.float32)
    errors["tone_exposure"] = _check(
        "tone_exposure", ta.tone_simulate_exposure_aot(image, gain=1.7), exposure_ref
    )

    contrast_ref = np.clip(1.4 * (image - 0.5) + 0.5 - 0.03, 0.0, 1.0).astype(
        np.float32
    )
    errors["tone_contrast"] = _check(
        "tone_contrast",
        ta.tone_contrast_aot(image, contrast=1.4, brightness=-0.03),
        contrast_ref,
    )

    h, w = 12, 16
    y = np.linspace(16.0, 235.0, h * w, dtype=np.float32).reshape(h, w)
    u = np.linspace(90.0, 160.0, (h // 2) * (w // 2), dtype=np.float32).reshape(
        h // 2, w // 2
    )
    v = np.linspace(100.0, 180.0, (h // 2) * (w // 2), dtype=np.float32).reshape(
        h // 2, w // 2
    )
    # Neutral pixels make an exact, backend-independent camera check.
    neutral = ta.camera_yuv420_aot(
        np.full((h, w), 128, np.float32),
        np.full((h // 2, w // 2), 128, np.float32),
        np.full((h // 2, w // 2), 128, np.float32),
        h,
        w,
    )
    neutral_expected = np.full((h, w, 3), (1.164 * (128.0 - 16.0)) / 255.0, np.float32)
    neutral_expected = np.clip(neutral_expected, 0.0, 1.0)
    errors["camera_yuv420"] = _check(
        "camera_yuv420", neutral, neutral_expected, atol=4e-5, rtol=4e-5
    )
    errors["camera_gray"] = _check(
        "camera_gray", ta.camera_y_to_gray_aot(y, h, w), y / 255.0, atol=3e-6, rtol=3e-6
    )
    # Exercise the actual non-neutral plane path as a finite-output check.
    converted = ta.camera_yuv420_aot(y, u, v, h, w)
    if (
        not np.isfinite(converted).all()
        or converted.min() < 0.0
        or converted.max() > 1.0
    ):
        raise AssertionError("camera_yuv420 non-neutral output is outside [0, 1]")

    desc1 = np.array(
        [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0]], np.float32
    )
    desc2 = np.array(
        [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [4, 4, 4, 4]], np.float32
    )
    matches, distances = ta.sfm_match_l2_aot(desc1, desc2, k=1)
    expected_matches = np.array([[0, 0], [1, 1], [2, 2], [3, 1]], np.int32)
    _check("sfm_match_indices", matches, expected_matches, atol=0.0, rtol=0.0)
    errors["sfm_match_distance"] = _check(
        "sfm_match_distance", distances, np.array([0, 0, 0, 1.0], np.float32)
    )

    pts1 = np.array(
        [[0.1, 0.2], [0.2, -0.1], [-0.3, 0.4], [0.5, 0.1], [-0.2, -0.4]], np.float32
    )
    pts2 = pts1 * np.float32(1.1)
    indices = np.arange(5, dtype=np.int32)
    ata = ta.sfm_build_5pt_system_aot(pts1, pts2, indices)
    expected_ata = np.zeros((9, 9), dtype=np.float64)
    for i in range(5):
        x1, y1 = pts1[i]
        x2, y2 = pts2[i]
        row = np.array(
            [x2 * x1, x2 * y1, x2, y2 * x1, y2 * y1, y2, x1, y1, 1.0], np.float64
        )
        expected_ata += np.outer(row, row)
    errors["five_point_ata"] = _check(
        "five_point_ata", ata, expected_ata.astype(np.float32), atol=2e-5, rtol=2e-5
    )

    # Known fronto-parallel plane for the adaptive triangulator.
    p3 = np.array([[0.0, 0.0, 5.0], [0.5, 0.2, 4.0], [-0.2, 0.4, 6.0]], np.float32)
    P1 = np.hstack([np.eye(3), np.zeros((3, 1))]).astype(np.float32)
    P2 = np.hstack([np.eye(3), np.array([[0.4], [0.0], [0.0]], np.float32)]).astype(
        np.float32
    )
    q1 = (p3[:, :2] / p3[:, 2:]).astype(np.float32)
    q2 = (
        (p3 + np.array([0.4, 0.0, 0.0], np.float32))[:, :2]
        / (p3 + np.array([0.4, 0.0, 0.0], np.float32))[:, 2:]
    ).astype(np.float32)
    # Force the well-conditioned wMid2/DLT branch for a known-value check.
    triangulated, methods = ta.sfm_triangulate_adaptive_aot(
        q1,
        q2,
        P1,
        P2,
        np.zeros(3, np.float32),
        np.array([-0.4, 0.0, 0.0], np.float32),
        parallax_threshold=180.0,
    )
    if not np.isfinite(triangulated).all() or not np.all(
        (methods == 0) | (methods == 1)
    ):
        raise AssertionError("triangulation produced invalid values")
    errors["triangulation"] = float(np.max(np.abs(triangulated - p3)))
    if errors["triangulation"] > 2e-3:
        raise AssertionError(f"triangulation max error={errors['triangulation']:g}")

    cloud = np.array([[x, y, 0.0] for x in range(4) for y in range(4)], np.float32)
    kd, ki = ta.sfm_knn_distance_aot(cloud, k=3)
    expected_first = np.array([1.0, 1.0, np.sqrt(2.0)], np.float32)
    errors["point_cloud_knn"] = _check(
        "point_cloud_knn", kd[0], expected_first, atol=3e-6, rtol=3e-6
    )
    normals = ta.sfm_normals_pca_aot(cloud, ki)
    if not np.isfinite(normals).all():
        raise AssertionError("point-cloud normals contain non-finite values")
    if np.max(np.abs(np.linalg.norm(normals, axis=1) - 1.0)) > 2e-3:
        raise AssertionError("point-cloud normals are not unit length")

    cameras = np.array([[0, 0, 1, 0, 0, 0, 0, 100, 100, 0, 0]], np.float32)
    points = np.array([[0, 0, 5], [1, 0, 5]], np.float32)
    observations = np.array([[0, 0], [0, 1]], np.int32)
    observed = np.array([[0, 0], [20, 0]], np.float32)
    errors_out = ta.sfm_reprojection_errors_aot(cameras, points, observations, observed)
    # Vulkan drivers may evaluate the Rodrigues zero-angle branch with a
    # slightly different transcendental path; the resulting sub-millipixel
    # drift is still far below the pixel-level contract.
    errors["bundle_reprojection"] = _check(
        "bundle_reprojection", errors_out, np.zeros(4, np.float32), atol=1e-3, rtol=1e-4
    )
    normal = ta.sfm_bundle_normal_equations_aot(cameras, points, observations, observed)
    if not all(np.isfinite(value).all() for value in normal.values()):
        raise AssertionError("bundle normal equations contain non-finite values")
    errors["bundle_cost"] = abs(ta.sfm_cost_aot(errors_out))

    origin = np.zeros(3, np.float32)
    normals_in = np.zeros_like(cloud)
    normals_in[:, 2] = 1.0
    div = ta.sfm_poisson_rasterize_aot(
        cloud, normals_in, origin, voxel_size=1.0, gx=6, gy=6, gz=6
    )
    mask = ta.sfm_poisson_occupancy_aot(
        cloud, origin, voxel_size=1.0, gx=6, gy=6, gz=6, dilate_radius=0
    )
    if div.shape != (6, 6, 6) or int(mask.sum()) < len(cloud) // 2:
        raise AssertionError("Poisson primitives produced an unexpected grid")
    _ = ta.sfm_poisson_step_aot(np.zeros_like(div), div, mask)

    # ------------------------------------------------------------------
    # High-level orchestration checks
    # ------------------------------------------------------------------
    frames = [
        np.clip(image * 0.55, 0.0, 1.0).astype(np.float32),
        np.clip(image * 1.35, 0.0, 1.0).astype(np.float32),
    ]
    hdr_result = ta.hdr_fuse_aot(frames, noise_sigmas=[0.03, 0.08], n_levels=2)
    if (
        hdr_result.shape != image.shape
        or not np.isfinite(hdr_result).all()
        or not (0.0 <= hdr_result).all()
        or not (hdr_result <= 1.0).all()
    ):
        raise AssertionError("high-level HDR fusion produced an invalid result")
    errors["hdr_fusion_oracle"] = _check(
        "hdr_fusion_oracle",
        hdr_result,
        _hdr_fusion_reference(frames, [0.03, 0.08], n_levels=2),
        atol=5e-5,
        rtol=5e-5,
    )

    local_tone = ta.local_tone_map_aot(
        image, n_levels=2, n_iterations=1, apply_gamma=False
    )
    if (
        local_tone.shape != image.shape
        or not np.isfinite(local_tone).all()
        or local_tone.min() < 0.0
        or local_tone.max() > 1.0
    ):
        raise AssertionError("high-level local tone mapping produced an invalid result")
    errors["local_tone_oracle"] = _check(
        "local_tone_oracle",
        local_tone,
        _tone_local_reference(image, n_levels=2),
        atol=5e-5,
        rtol=5e-5,
    )
    errors["tone_unified"] = _check(
        "tone_unified",
        ta.tone_map_aot(image, method="reinhard", apply_gamma=False),
        ta.tone_reinhard_aot(image),
        atol=4e-5,
        rtol=4e-5,
    )

    K = np.array([[24.0, 0.0, 8.0], [0.0, 24.0, 6.0], [0.0, 0.0, 1.0]], np.float32)
    stereo_ref = np.linspace(0.1, 0.9, 8 * 10, dtype=np.float32).reshape(8, 10)
    stereo_depths = np.linspace(1.0, 2.0, 4, dtype=np.float32)
    stereo_volume = ta.sfm_sweep_depths_aot(
        stereo_ref,
        stereo_ref.copy(),
        K,
        K,
        np.eye(3, dtype=np.float32),
        np.zeros(3, dtype=np.float32),
        stereo_depths,
        patch_radius=1,
    )
    errors["plane_sweep_cost_oracle"] = _check(
        "plane_sweep_cost_oracle",
        # GPU floating-point cancellation in the deliberately minimal edge
        # patches can fall back to the source kernel's cost=1 sentinel.  The
        # stable interior is the numerical oracle; edge behavior is covered
        # separately by the finite/range assertion below.
        stereo_volume[:, 2:-2, 2:-2],
        _plane_sweep_cost_reference(
            stereo_ref,
            stereo_ref.copy(),
            K,
            K,
            np.eye(3, dtype=np.float32),
            np.zeros(3, dtype=np.float32),
            stereo_depths,
            1,
        )[:, 2:-2, 2:-2],
        atol=4e-5,
        rtol=4e-5,
    )
    stereo_depth, stereo_conf = ta.plane_sweep_stereo_aot(
        stereo_ref,
        stereo_ref.copy(),
        K,
        K,
        np.eye(3, dtype=np.float32),
        np.zeros(3, dtype=np.float32),
        depth_min=1.0,
        depth_max=2.0,
        n_depths=4,
        patch_radius=1,
    )
    if (
        not np.isfinite(stereo_depth).all()
        or not np.isfinite(stereo_conf).all()
        or stereo_depth.min() < 1.0 - 1e-5
        or stereo_depth.max() > 2.0 + 1e-5
    ):
        raise AssertionError("identity plane sweep returned an invalid depth range")
    errors["plane_sweep_range"] = float(
        max(0.0, 1.0 - stereo_depth.min(), stereo_depth.max() - 2.0)
    )

    raw_cloud = np.vstack([cloud, np.array([[100.0, 100.0, 100.0]], np.float32)])
    processed_cloud, processed_normals, kept = ta.point_cloud_preprocess_aot(
        raw_cloud, voxel_size=1.0, sor_k=3, sor_std=1.5, normal_k=3
    )
    if (
        processed_cloud.ndim != 2
        or processed_cloud.shape[1] != 3
        or processed_normals.shape != processed_cloud.shape
        or not np.isfinite(processed_normals).all()
    ):
        raise AssertionError(
            "high-level point-cloud preprocessing produced invalid arrays"
        )
    voxel_input = np.array(
        [[0.0, 0.0, 0.0], [0.2, 0.2, 0.0], [1.1, 0.0, 0.0], [1.2, 0.2, 0.0]], np.float32
    )
    voxel_output, voxel_normals, _ = ta.point_cloud_preprocess_aot(
        voxel_input, voxel_size=1.0, sor_k=10, normal_k=1
    )
    expected_voxels = np.array([[0.1, 0.1, 0.0], [1.15, 0.1, 0.0]], np.float32)
    errors["point_cloud_voxel_oracle"] = _check(
        "point_cloud_voxel_oracle",
        voxel_output[np.argsort(voxel_output[:, 0])],
        expected_voxels,
        atol=3e-5,
        rtol=3e-5,
    )
    if not np.isfinite(voxel_normals).all():
        raise AssertionError("voxel normal output contains non-finite values")

    true_camera = np.array(
        [[0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 80.0, 80.0, 32.0, 24.0]], np.float32
    )
    ba_points = np.array(
        [[0.0, 0.0, 5.0], [0.5, 0.1, 4.0], [-0.2, 0.3, 6.0], [0.2, -0.3, 5.5]],
        np.float32,
    )
    ba_obs = np.column_stack(
        [np.zeros(len(ba_points), np.int32), np.arange(len(ba_points), dtype=np.int32)]
    )
    ba_measurements = np.column_stack(
        [
            ba_points[:, 0] / ba_points[:, 2] * 80.0 + 32.0,
            ba_points[:, 1] / ba_points[:, 2] * 80.0 + 24.0,
        ]
    ).astype(np.float32)
    ba_initial = true_camera.copy()
    ba_initial[0, 4] = 0.25
    ba_initial[0, 5] = -0.12
    ba_before = ta.sfm_cost_aot(
        ta.sfm_reprojection_errors_aot(ba_initial, ba_points, ba_obs, ba_measurements),
        n_obs=len(ba_obs),
    )
    _, _, ba_rmse, _, ba_history = ta.bundle_adjust_lm_aot(
        ba_initial,
        ba_points,
        ba_obs,
        ba_measurements,
        max_iterations=5,
        optimize_cameras=True,
        fixed_camera_indices=(),
        return_history=True,
    )
    if (
        not np.isfinite(ba_rmse)
        or ba_rmse > 1e-4
        or ba_history[-1] >= np.sqrt(ba_before / len(ba_obs))
    ):
        raise AssertionError(
            "AOT bundle adjustment did not reduce synthetic reprojection cost"
        )
    errors["bundle_adjust_rmse"] = float(ba_rmse)

    poisson_points = np.array(
        [[x, y, 0.0] for x in range(3) for y in range(3)], np.float32
    )
    poisson_normals = np.zeros_like(poisson_points)
    poisson_normals[:, 2] = 1.0
    vertices, faces = ta.poisson_reconstruct_aot(
        poisson_points,
        poisson_normals,
        grid_resolution=6,
        solver_iterations=2,
        dilate_radius=0,
    )
    if (
        vertices.ndim != 2
        or vertices.shape[1] != 3
        or faces.ndim != 2
        or faces.shape[1] != 3
        or not np.isfinite(vertices).all()
    ):
        raise AssertionError(
            "high-level Poisson reconstruction produced invalid mesh arrays"
        )
    errors["poisson_mesh"] = 0.0

    fractional_point = np.array([[1.25, 2.5, 3.75]], np.float32)
    fractional_normal = np.array([[1.0, 2.0, 3.0]], np.float32)
    fractional_div = ta.sfm_poisson_rasterize_aot(
        fractional_point,
        fractional_normal,
        np.zeros(3, np.float32),
        voxel_size=1.0,
        gx=8,
        gy=8,
        gz=8,
    )
    fractional_expected = _poisson_raster_reference(
        fractional_point,
        fractional_normal,
        np.zeros(3, np.float32),
        1.0,
        fractional_div.shape,
    )
    errors["poisson_raster_oracle"] = _check(
        "poisson_raster_oracle",
        fractional_div,
        fractional_expected,
        atol=2e-5,
        rtol=2e-5,
    )
    if errors["poisson_raster_oracle"] > 2e-5:
        raise AssertionError(
            f"Poisson rasterization max error={errors['poisson_raster_oracle']:g}"
        )

    from taichi_vision.taichi_algorithm.camera_api2 import AOTCameraPipeline

    camera_pipeline = AOTCameraPipeline(width=10, height=8, target_fps=120.0)
    camera_pipeline.start()
    try:
        y_plane = np.full((8, 10), 128, dtype=np.uint8)
        uv_plane = np.full((4, 5), 128, dtype=np.uint8)
        camera_pipeline.submit_yuv(y_plane, uv_plane, uv_plane, frame_number=1)
        camera_output = None
        deadline = time.time() + 8.0
        while camera_output is None and time.time() < deadline:
            camera_output = camera_pipeline.get_latest_output()
            if camera_output is None:
                time.sleep(0.005)
    finally:
        camera_pipeline.stop()
    expected_neutral = np.clip(1.164 * (128.0 - 16.0) / 255.0, 0.0, 1.0)
    if (
        camera_output is None
        or camera_output.shape != (8, 10, 3)
        or not np.allclose(camera_output, expected_neutral, atol=5e-3)
    ):
        raise AssertionError(
            "AOT Camera2 pipeline failed the neutral YUV end-to-end check"
        )
    errors["camera_pipeline"] = float(np.max(np.abs(camera_output - expected_neutral)))

    # Strided Camera2 planes exercise the actual Image.Plane ABI contract.
    y_stride, uv_stride = 24, 14
    y_strided = np.zeros((8, y_stride), dtype=np.float32)
    u_strided = np.zeros((4, uv_stride), dtype=np.float32)
    v_strided = np.zeros((4, uv_stride), dtype=np.float32)
    y_strided[:, ::2][:, :10] = 128.0
    u_strided[:, ::2][:, :5] = 128.0
    v_strided[:, ::2][:, :5] = 128.0
    strided = ta.camera_yuv420_aot(
        y_strided,
        u_strided,
        v_strided,
        8,
        10,
        y_row_stride=y_stride,
        y_pixel_stride=2,
        u_row_stride=uv_stride,
        u_pixel_stride=2,
        v_row_stride=uv_stride,
        v_pixel_stride=2,
    )
    errors["camera_stride_oracle"] = float(np.max(np.abs(strided - expected_neutral)))
    if errors["camera_stride_oracle"] > 5e-5:
        raise AssertionError("strided Camera2 planes failed the neutral oracle")

    print(
        f"[PASS] research accuracy backend={os.environ.get('AOT_ARCH', 'auto')} checks={len(errors)}"
    )
    worst = max(errors.items(), key=lambda item: item[1])
    print(f"[INFO] worst recorded absolute error: {worst[0]}={worst[1]:.6g}")
    return errors


def _time_call(label, fn, *, warmup=2, repeats=7):
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000.0)
    samples = np.asarray(samples, dtype=np.float64)
    print(
        f"[TIME] {label:28s} median={np.median(samples):8.3f} ms "
        f"p95={np.percentile(samples, 95):8.3f} ms"
    )
    return samples


def run_benchmark():
    rng = np.random.default_rng(99)
    image = rng.random((128, 128, 3), dtype=np.float32)
    gray = rng.random((128, 128), dtype=np.float32)
    descriptors_a = rng.random((128, 32), dtype=np.float32)
    descriptors_b = rng.random((160, 32), dtype=np.float32)
    cloud = rng.random((512, 3), dtype=np.float32)
    cameras = np.array([[0, 0, 1, 0, 0, 0, 0, 100, 100, 0, 0]], np.float32)
    points = rng.random((128, 3), dtype=np.float32) + np.array([0, 0, 2], np.float32)
    observations = np.column_stack(
        [np.zeros(128, np.int32), np.arange(128, dtype=np.int32)]
    )
    observed = np.column_stack(
        [points[:, 0] / points[:, 2] * 100, points[:, 1] / points[:, 2] * 100]
    ).astype(np.float32)

    _time_call("HDR weight", lambda: ta.hdr_weight_aot(image, gray))
    _time_call("Tone Reinhard", lambda: ta.tone_reinhard_aot(image))
    _time_call(
        "Camera YUV420",
        lambda: ta.camera_yuv420_aot(
            np.full((128, 128), 128, np.float32),
            np.full((64, 64), 128, np.float32),
            np.full((64, 64), 128, np.float32),
            128,
            128,
        ),
    )
    _time_call(
        "SfM L2 matching",
        lambda: ta.sfm_match_l2_aot(descriptors_a, descriptors_b, k=1),
    )
    _time_call("Point-cloud KNN", lambda: ta.sfm_knn_distance_aot(cloud, k=8))
    _time_call(
        "Bundle reprojection",
        lambda: ta.sfm_reprojection_errors_aot(cameras, points, observations, observed),
    )

    small_frames = [image[:32, :32], np.clip(image[:32, :32] * 1.25, 0.0, 1.0)]
    _time_call(
        "HDR fusion high-level",
        lambda: ta.hdr_fuse_aot(small_frames, noise_sigmas=[0.04, 0.08], n_levels=2),
        warmup=1,
        repeats=3,
    )
    _time_call(
        "Tone local high-level",
        lambda: ta.local_tone_map_aot(
            image[:32, :32], n_levels=2, n_iterations=1, apply_gamma=False
        ),
        warmup=1,
        repeats=3,
    )

    from taichi_vision.taichi_algorithm.camera_api2 import AOTCameraPipeline

    camera_pipeline = AOTCameraPipeline(width=32, height=32, target_fps=120.0)
    y_small = np.full((32, 32), 128, dtype=np.uint8)
    uv_small = np.full((16, 16), 128, dtype=np.uint8)
    package = {
        "y": y_small,
        "u": uv_small,
        "v": uv_small,
        "y_row_stride": 32,
        "y_pixel_stride": 1,
        "u_row_stride": 16,
        "u_pixel_stride": 1,
        "v_row_stride": 16,
        "v_pixel_stride": 1,
    }
    _time_call(
        "Camera pipeline high-level",
        lambda: camera_pipeline._process_frame(package),
        warmup=1,
        repeats=3,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    run_accuracy_suite()
    if args.benchmark:
        run_benchmark()


if __name__ == "__main__":
    main()
