"""High-level AOT orchestration for the research algorithms.

The compiled graphs in :mod:`taichi_vision.taichi_algorithm.aot_api.research` are small
array-to-array kernels.  This module composes those kernels into the public
algorithms used by the experimental library.  Python owns validation,
variable-length pyramids, sparse Schur solves, voxel grouping, and mesh
extraction; pixel/point-local arithmetic is dispatched through TCM.

That split is intentional.  It gives CPU, CUDA, Vulkan, and desktop OpenGL
the same numerical contract while avoiding backend-specific dynamic memory
and sparse-solver behaviour inside a graph.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .research import (
    hdr_add_aot,
    hdr_add_weighted_laplacian_aot,
    hdr_downsample_aot,
    hdr_normalize_weights_aot,
    hdr_subtract_aot,
    hdr_upsample_aot,
    hdr_weight_aot,
    sfm_bilateral_refine_depth_aot,
    sfm_bundle_normal_equations_aot,
    sfm_cost_aot,
    sfm_knn_distance_aot,
    sfm_normals_pca_aot,
    sfm_apply_point_update_aot,
    sfm_poisson_occupancy_aot,
    sfm_poisson_rasterize_aot,
    sfm_poisson_step_aot,
    sfm_reprojection_errors_aot,
    sfm_sor_filter_aot,
    sfm_sweep_depths_aot,
    sfm_voxel_accumulate_aot,
    sfm_winner_take_all_aot,
    tone_add_aot,
    tone_blend_weight_aot,
    tone_contrast_aot,
    tone_downsample_aot,
    tone_luminance_aot,
    tone_reinhard_aot,
    tone_simulate_exposure_aot,
    tone_srgb_aot,
    tone_subtract_aot,
    tone_upsample_aot,
    tone_weighted_blend_aot,
)


def _f32(value, *, ndim=None):
    array = np.ascontiguousarray(value, dtype=np.float32)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected ndim={ndim}, got shape {array.shape}")
    return array


def _levels_for_shape(h, w, n_levels):
    if n_levels is None:
        return max(2, min(6, int(np.log2(max(2, min(h, w)))) - 3))
    value = int(n_levels)
    if value < 1:
        raise ValueError("n_levels must be at least 1")
    return value


def _laplacian_abs(gray):
    """Reference-compatible 4-neighbour absolute Laplacian on the host."""

    image = _f32(gray, ndim=2)
    padded = np.pad(image, 1, mode="edge")
    lap = (
        padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        - 4.0 * padded[1:-1, 1:-1]
    )
    return np.abs(lap).astype(np.float32)


def _gaussian_pyramid(base, levels, downsample):
    pyramid = [_f32(base)]
    for _ in range(max(0, int(levels) - 1)):
        h, w = pyramid[-1].shape[:2]
        nh, nw = h // 2, w // 2
        if nh < 2 or nw < 2:
            break
        pyramid.append(downsample(pyramid[-1]))
    return pyramid


def _laplacian_pyramid(base, levels, downsample, upsample, subtract):
    gaussian = _gaussian_pyramid(base, levels, downsample)
    laplacian = []
    for level in range(len(gaussian) - 1):
        current = gaussian[level]
        upsampled = upsample(gaussian[level + 1], current.shape)
        laplacian.append(subtract(current, upsampled))
    laplacian.append(gaussian[-1])
    return laplacian


def _reconstruct_laplacian(laplacian, upsample, add):
    result = _f32(laplacian[-1]).copy()
    for level in range(len(laplacian) - 2, -1, -1):
        upsampled = upsample(result, laplacian[level].shape)
        result = add(upsampled, laplacian[level])
    return result


def _prepare_frames(frames):
    if not isinstance(frames, (list, tuple)):
        frames = list(frames)
    if not frames:
        raise ValueError("frames must contain at least one image")
    arrays = [_f32(frame) for frame in frames]
    shape = arrays[0].shape
    if len(shape) not in (2, 3) or (len(shape) == 3 and shape[2] != 3):
        raise ValueError("frames must be HxW grayscale or HxWx3 RGB arrays")
    if any(array.shape != shape for array in arrays):
        raise ValueError("all frames must have identical dimensions")
    return arrays, len(shape) == 2


def _estimate_noise_sigma(gray):
    highpass = _laplacian_abs(gray)
    sigma = float(np.std(highpass))
    return max(sigma, 1e-3)


def hdr_fuse_aot(
    frames,
    noise_sigmas=None,
    noise_power=2.0,
    exposure_sigma=0.2,
    exposure_power=1.0,
    detail_power=1.0,
    saturation_power=1.0,
    n_levels=None,
    return_weights=False,
):
    """Multi-resolution HDR exposure fusion using the research AOT leaves.

    The result matches the JIT algorithm's RGB/grayscale contract.  Pyramid
    scheduling and the small contrast stencil are host operations; every
    weight, resize, level subtraction, accumulation, and reconstruction
    operation is dispatched to the selected AOT backend.
    """

    arrays, is_grayscale = _prepare_frames(frames)
    if len(arrays) == 1:
        result = np.clip(arrays[0], 0.0, 1.0).astype(np.float32)
        return (result, np.ones((1,) + result.shape[:2], np.float32)) if return_weights else result

    h, w = arrays[0].shape[:2]
    levels = _levels_for_shape(h, w, n_levels)
    rgb_frames = [
        np.repeat(frame[..., None], 3, axis=2) if is_grayscale else frame
        for frame in arrays
    ]
    gray_frames = [frame if is_grayscale else (0.299 * frame[..., 0] + 0.587 * frame[..., 1] + 0.114 * frame[..., 2]).astype(np.float32) for frame in arrays]

    if noise_sigmas is None:
        sigmas = [_estimate_noise_sigma(gray) for gray in gray_frames]
    else:
        sigmas = [float(value) for value in noise_sigmas]
        if len(sigmas) != len(arrays):
            raise ValueError("noise_sigmas must contain one value per frame")

    weights = []
    for image, gray, sigma in zip(rgb_frames, gray_frames, sigmas):
        weights.append(
            hdr_weight_aot(
                image,
                _laplacian_abs(gray),
                noise_sigma=sigma,
                noise_power=noise_power,
                exposure_sigma=exposure_sigma,
                exposure_power=exposure_power,
                detail_power=detail_power,
                saturation_power=saturation_power,
            )
        )
    weights = hdr_normalize_weights_aot(np.stack(weights, axis=0))

    weight_pyramids = [
        _gaussian_pyramid(weights[i], levels, hdr_downsample_aot)
        for i in range(len(rgb_frames))
    ]
    frame_pyramids = [
        _laplacian_pyramid(
            image,
            levels,
            hdr_downsample_aot,
            hdr_upsample_aot,
            hdr_subtract_aot,
        )
        for image in rgb_frames
    ]

    actual_levels = len(frame_pyramids[0])
    blended = []
    for level in range(actual_levels):
        accumulator = np.zeros_like(frame_pyramids[0][level], dtype=np.float32)
        for frame_index, pyramid in enumerate(frame_pyramids):
            weight_level = weight_pyramids[frame_index][min(level, len(weight_pyramids[frame_index]) - 1)]
            accumulator = hdr_add_weighted_laplacian_aot(
                pyramid[level], weight_level, result=accumulator
            )
        blended.append(accumulator)

    result_rgb = np.clip(
        _reconstruct_laplacian(blended, hdr_upsample_aot, hdr_add_aot),
        0.0,
        1.0,
    ).astype(np.float32)
    result = result_rgb[..., 0] if is_grayscale else result_rgb
    if return_weights:
        return result, weights
    return result


def hdr_fusion_aot(*args, **kwargs):
    """Alias matching the experimental module name."""

    return hdr_fuse_aot(*args, **kwargs)


def local_tone_map_aot(
    img,
    gain=2.0,
    target_lum=0.5,
    sigma=0.3,
    n_levels=None,
    n_iterations=2,
    apply_gamma=True,
    gamma=2.2,
):
    """Local Laplacian tone mapping composed from native AOT stages."""

    result = _f32(img, ndim=3).copy()
    if result.shape[2] != 3:
        raise ValueError("tone mapping expects an HxWx3 RGB image")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    levels = _levels_for_shape(result.shape[0], result.shape[1], n_levels)

    for _ in range(max(0, int(n_iterations))):
        bright = tone_simulate_exposure_aot(result, gain=gain)
        dark_lum = tone_luminance_aot(result)
        bright_lum = tone_luminance_aot(bright)
        dark_weight = tone_blend_weight_aot(dark_lum, target_lum=target_lum, sigma=sigma)
        bright_weight = tone_blend_weight_aot(bright_lum, target_lum=target_lum, sigma=sigma)

        dark_lap = _laplacian_pyramid(
            result,
            levels,
            tone_downsample_aot,
            tone_upsample_aot,
            tone_subtract_aot,
        )
        bright_lap = _laplacian_pyramid(
            bright,
            levels,
            tone_downsample_aot,
            tone_upsample_aot,
            tone_subtract_aot,
        )
        dark_weights = _gaussian_pyramid(dark_weight, levels, tone_downsample_aot)
        bright_weights = _gaussian_pyramid(bright_weight, levels, tone_downsample_aot)

        blended = []
        for level, (dark_level, bright_level) in enumerate(zip(dark_lap, bright_lap)):
            wd = dark_weights[min(level, len(dark_weights) - 1)]
            wb = bright_weights[min(level, len(bright_weights) - 1)]
            blended.append(tone_weighted_blend_aot(dark_level, bright_level, wd, wb))
        result = np.clip(
            _reconstruct_laplacian(blended, tone_upsample_aot, tone_add_aot),
            0.0,
            1.0,
        ).astype(np.float32)

    if apply_gamma:
        result = tone_srgb_aot(result, gamma=gamma)
    return np.clip(result, 0.0, 1.0).astype(np.float32)


def tone_map_aot(
    img,
    method="local",
    key=0.18,
    lum_white=1.0,
    gain=2.0,
    target_lum=0.5,
    sigma=0.3,
    n_iterations=2,
    apply_gamma=True,
    gamma=2.2,
    contrast=1.0,
    brightness=0.0,
):
    """Unified AOT tone mapping API matching the experimental API."""

    method = str(method).lower()
    if method == "reinhard":
        result = tone_reinhard_aot(img, key=key, lum_white=lum_white)
        if apply_gamma:
            result = tone_srgb_aot(result, gamma=gamma)
    elif method == "local":
        result = local_tone_map_aot(
            img,
            gain=gain,
            target_lum=target_lum,
            sigma=sigma,
            n_iterations=n_iterations,
            apply_gamma=apply_gamma,
            gamma=gamma,
        )
    elif method == "simple":
        result = np.clip(_f32(img, ndim=3), 0.0, 1.0)
        if apply_gamma:
            result = tone_srgb_aot(result, gamma=gamma)
    else:
        raise ValueError("method must be 'local', 'reinhard', or 'simple'")

    if contrast != 1.0 or brightness != 0.0:
        result = tone_contrast_aot(result, contrast=contrast, brightness=brightness)
    return np.clip(result, 0.0, 1.0).astype(np.float32)


def plane_sweep_stereo_aot(
    ref_img,
    target_img,
    K_ref,
    K_target,
    R_rel,
    t_rel,
    depth_min=0.1,
    depth_max=100.0,
    n_depths=64,
    patch_radius=3,
    depth_spacing="linear",
    refine=True,
):
    """Dense plane sweep composed from AOT cost, winner, and refine kernels."""

    ref = _f32(ref_img, ndim=2)
    target = _f32(target_img, ndim=2)
    if ref.shape != target.shape:
        raise ValueError("reference and target images must have matching shape")
    count = int(n_depths)
    if count < 1 or depth_min <= 0 or depth_max < depth_min:
        raise ValueError("invalid depth range or n_depths")
    if str(depth_spacing).lower() == "log":
        depths = np.logspace(np.log10(max(depth_min, 0.01)), np.log10(depth_max), count, dtype=np.float32)
    else:
        depths = np.linspace(depth_min, depth_max, count, dtype=np.float32)
    volume = sfm_sweep_depths_aot(
        ref,
        target,
        _f32(K_ref, ndim=2),
        _f32(K_target, ndim=2),
        _f32(R_rel, ndim=2),
        _f32(t_rel, ndim=1),
        depths,
        patch_radius=patch_radius,
    )
    depth, confidence = sfm_winner_take_all_aot(volume, depths)
    if refine:
        depth = sfm_bilateral_refine_depth_aot(depth, ref, sigma_s=5.0, sigma_r=0.1)
    return depth.astype(np.float32), confidence.astype(np.float32)


def multi_view_plane_sweep_aot(
    ref_img,
    target_images,
    K_ref,
    K_targets,
    R_rels,
    t_rels,
    depth_min=0.1,
    depth_max=100.0,
    n_depths=64,
    patch_radius=3,
    depth_spacing="linear",
    refine=True,
):
    """Aggregate AOT plane-sweep costs over multiple target views."""

    targets = list(target_images)
    if not targets:
        raise ValueError("target_images must not be empty")
    if not (len(targets) == len(K_targets) == len(R_rels) == len(t_rels)):
        raise ValueError("target images and camera relation lists must match")
    ref = _f32(ref_img, ndim=2)
    count = int(n_depths)
    if str(depth_spacing).lower() == "log":
        depths = np.logspace(np.log10(max(depth_min, 0.01)), np.log10(depth_max), count, dtype=np.float32)
    else:
        depths = np.linspace(depth_min, depth_max, count, dtype=np.float32)
    total = None
    for target, K_t, R, t in zip(targets, K_targets, R_rels, t_rels):
        volume = sfm_sweep_depths_aot(
            ref,
            _f32(target, ndim=2),
            _f32(K_ref, ndim=2),
            _f32(K_t, ndim=2),
            _f32(R, ndim=2),
            _f32(t, ndim=1),
            depths,
            patch_radius=patch_radius,
        )
        total = volume if total is None else total + volume
    total /= float(len(targets))
    depth, confidence = sfm_winner_take_all_aot(total, depths)
    if refine:
        depth = sfm_bilateral_refine_depth_aot(depth, ref, sigma_s=5.0, sigma_r=0.1)
    return depth.astype(np.float32), confidence.astype(np.float32)


def _voxel_downsample_aot(points, voxel_size):
    data = _f32(points, ndim=2)
    if len(data) == 0:
        return data.copy()
    if voxel_size <= 0:
        raise ValueError("voxel_size must be positive")
    coords = np.floor(data / float(voxel_size)).astype(np.int64)
    _, inverse, counts = np.unique(coords, axis=0, return_inverse=True, return_counts=True)
    order = np.argsort(inverse, kind="stable")
    sums, _ = sfm_voxel_accumulate_aot(
        data[order], inverse[order].astype(np.int32), max_voxels=len(counts)
    )
    return (sums[: len(counts)] / np.maximum(counts[:, None], 1)).astype(np.float32)


def point_cloud_preprocess_aot(points, voxel_size=0.01, sor_k=20, sor_std=2.0, normal_k=20):
    """SOR, exact voxel grouping, and PCA normals using AOT point kernels."""

    data = _f32(points, ndim=2)
    if data.shape[1] != 3:
        raise ValueError("points must have shape (N, 3)")
    if len(data) == 0:
        return data.copy(), np.empty((0, 3), np.float32), np.empty(0, np.int32)

    k = min(int(sor_k), max(1, len(data) - 1))
    if len(data) < int(sor_k) + 1:
        filtered = data.copy()
        keep_indices = np.arange(len(data), dtype=np.int32)
    else:
        distances, _ = sfm_knn_distance_aot(data, k=k)
        keep_mask = sfm_sor_filter_aot(distances, std_multiplier=sor_std)
        keep_indices = np.flatnonzero(keep_mask > 0).astype(np.int32)
        filtered = data[keep_indices]
    downsampled = _voxel_downsample_aot(filtered, voxel_size)
    if len(downsampled) < 3:
        normals = np.zeros_like(downsampled, dtype=np.float32)
        if len(normals):
            normals[:, 2] = 1.0
        return downsampled, normals, keep_indices
    nk = min(int(normal_k), len(downsampled) - 1)
    _, knn_idx = sfm_knn_distance_aot(downsampled, k=nk)
    normals = sfm_normals_pca_aot(downsampled, knn_idx)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.maximum(norms, 1e-8)
    return downsampled.astype(np.float32), normals.astype(np.float32), keep_indices


def _skew(vector):
    x, y, z = vector
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], dtype=np.float64)


def _exp_rotation(vector):
    vec = np.asarray(vector, dtype=np.float64)
    theta = float(np.linalg.norm(vec))
    if theta < 1e-12:
        return np.eye(3, dtype=np.float64) + _skew(vec)
    axis = vec / theta
    k = _skew(axis)
    return np.eye(3) + np.sin(theta) * k + (1.0 - np.cos(theta)) * (k @ k)


def _camera_rotation(camera):
    axis = np.asarray(camera[:3], dtype=np.float64)
    angle = float(camera[3])
    norm = float(np.linalg.norm(axis))
    if norm < 1e-12 or abs(angle) < 1e-12:
        return np.eye(3, dtype=np.float64)
    return _exp_rotation(axis / norm * angle)


def _matrix_to_axis_angle(rotation, fallback_axis):
    matrix = np.asarray(rotation, dtype=np.float64)
    cosine = np.clip((np.trace(matrix) - 1.0) * 0.5, -1.0, 1.0)
    angle = float(np.arccos(cosine))
    if angle < 1e-8:
        vee = 0.5 * np.array(
            [matrix[2, 1] - matrix[1, 2], matrix[0, 2] - matrix[2, 0], matrix[1, 0] - matrix[0, 1]],
            dtype=np.float64,
        )
        norm = float(np.linalg.norm(vee))
        if norm > 1e-10:
            return vee / norm, norm
        axis = np.asarray(fallback_axis, dtype=np.float64)
        norm = float(np.linalg.norm(axis))
        return (axis / norm if norm > 1e-10 else np.array([0.0, 0.0, 1.0])), 0.0
    sine = np.sin(angle)
    if abs(sine) > 1e-7:
        axis = np.array(
            [matrix[2, 1] - matrix[1, 2], matrix[0, 2] - matrix[2, 0], matrix[1, 0] - matrix[0, 1]],
            dtype=np.float64,
        ) / (2.0 * sine)
    else:
        diagonal = np.maximum(np.diag(matrix) + 1.0, 0.0)
        index = int(np.argmax(diagonal))
        axis = np.zeros(3, dtype=np.float64)
        axis[index] = np.sqrt(diagonal[index]) * 0.5
        other = [(index + 1) % 3, (index + 2) % 3]
        if axis[index] > 1e-8:
            axis[other[0]] = (matrix[other[0], index] + matrix[index, other[0]]) / (4.0 * axis[index])
            axis[other[1]] = (matrix[other[1], index] + matrix[index, other[1]]) / (4.0 * axis[index])
    norm = float(np.linalg.norm(axis))
    return (axis / max(norm, 1e-12)), angle


def _apply_camera_pose_delta(cameras, delta, damping=1.0):
    result = _f32(cameras, ndim=2).copy()
    steps = _f32(delta, ndim=2)
    if result.shape[0] != steps.shape[0] or steps.shape[1] != 6 or result.shape[1] < 7:
        raise ValueError("cameras must be (N, >=7) and delta must be (N, 6)")
    for index in range(len(result)):
        rotation = _exp_rotation(steps[index, :3].astype(np.float64) * float(damping)) @ _camera_rotation(result[index])
        axis, angle = _matrix_to_axis_angle(rotation, result[index, :3])
        result[index, :3] = axis.astype(np.float32)
        result[index, 3] = np.float32(angle)
        result[index, 4:7] += steps[index, 3:6] * np.float32(damping)
    return result


def bundle_adjust_lm_aot(
    cameras,
    points_3d,
    observations,
    observed_2d,
    max_iterations=50,
    lambda_init=1e-3,
    lambda_factor=10.0,
    convergence_thresh=1e-6,
    fx=None,
    fy=None,
    cx=None,
    cy=None,
    optimize_cameras=True,
    fixed_camera_indices=(0,),
    return_history=False,
):
    """Levenberg-Marquardt bundle adjustment with AOT Jacobian stages.

    The normal-equation construction, reprojection, cost, and point update
    run through TCM.  Schur elimination and the compact axis-angle pose
    update are host-side NumPy operations, which keeps the sparse solve
    deterministic across the four desktop backends.
    """

    cams = _f32(cameras, ndim=2).copy()
    points = _f32(points_3d, ndim=2).copy()
    obs = np.ascontiguousarray(observations, dtype=np.int32)
    measured = _f32(observed_2d, ndim=2)
    if cams.shape[1] < 9 or points.shape[1] != 3 or obs.shape[1] != 2 or measured.shape != (len(obs), 2):
        raise ValueError("invalid camera, point, observation, or measurement shapes")
    if len(obs) == 0 or len(cams) == 0 or len(points) == 0:
        return (cams, points, 0.0, 0, []) if return_history else (cams, points, 0.0, 0)
    if np.any(obs < 0) or np.any(obs[:, 0] >= len(cams)) or np.any(obs[:, 1] >= len(points)):
        raise ValueError("observation indices are out of bounds")

    if any(value is not None for value in (fx, fy, cx, cy)):
        if cams.shape[1] < 11:
            expanded = np.zeros((len(cams), 11), dtype=np.float32)
            expanded[:, : cams.shape[1]] = cams
            cams = expanded
        if fx is not None:
            cams[:, 7] = float(fx)
        if fy is not None:
            cams[:, 8] = float(fy)
        if cx is not None:
            cams[:, 9] = float(cx)
        if cy is not None:
            cams[:, 10] = float(cy)

    fixed = {int(index) for index in fixed_camera_indices}
    if any(index < 0 or index >= len(cams) for index in fixed):
        raise ValueError("fixed_camera_indices contains an invalid camera")

    def cost_for(current_cams, current_points):
        errors = sfm_reprojection_errors_aot(current_cams, current_points, obs, measured)
        squared = max(0.0, sfm_cost_aot(errors, n_obs=len(obs)))
        return squared, float(np.sqrt(squared / max(len(obs), 1)))

    lam = float(lambda_init)
    factor = float(lambda_factor)
    if lam <= 0 or factor <= 1:
        raise ValueError("lambda_init must be positive and lambda_factor > 1")
    history = []
    previous_squared = np.inf
    iterations = 0

    for iteration in range(max(0, int(max_iterations))):
        iterations = iteration + 1
        current_squared, current_rmse = cost_for(cams, points)
        history.append(current_rmse)
        if iteration > 0 and abs(previous_squared - current_squared) < float(convergence_thresh):
            break

        normal = sfm_bundle_normal_equations_aot(cams, points, obs, measured)
        cam_h = np.asarray(normal["JtJ_cam"], dtype=np.float64)
        pt_h = np.asarray(normal["JtJ_pt"], dtype=np.float64)
        cross = np.asarray(normal["JtJ_cp"], dtype=np.float64)
        cam_b = np.asarray(normal["Jte_cam"], dtype=np.float64)
        pt_b = np.asarray(normal["Jte_pt"], dtype=np.float64)

        point_inv = np.zeros_like(pt_h)
        for p in range(len(points)):
            diagonal = np.maximum(np.abs(np.diag(pt_h[p])), 1e-8)
            try:
                point_inv[p] = np.linalg.inv(pt_h[p] + lam * np.diag(diagonal))
            except np.linalg.LinAlgError:
                point_inv[p] = np.linalg.pinv(pt_h[p] + lam * np.diag(diagonal), rcond=1e-10)

        schur = cam_h.copy()
        schur_b = cam_b.copy()
        if optimize_cameras:
            for camera_index in range(len(cams)):
                if camera_index in fixed:
                    continue
                for point_index in range(len(points)):
                    block = cross[camera_index, point_index]
                    if np.abs(block).sum() < 1e-14:
                        continue
                    schur[camera_index] -= block @ point_inv[point_index] @ block.T
                    schur_b[camera_index] -= block @ point_inv[point_index] @ pt_b[point_index]
        for camera_index in range(len(cams)):
            diagonal = np.maximum(np.abs(np.diag(schur[camera_index])), 1e-8)
            schur[camera_index] += lam * np.diag(diagonal)

        delta_cam = np.zeros((len(cams), 6), dtype=np.float64)
        if optimize_cameras:
            for camera_index in range(len(cams)):
                if camera_index in fixed:
                    continue
                try:
                    delta_cam[camera_index] = np.linalg.solve(schur[camera_index], schur_b[camera_index])
                except np.linalg.LinAlgError:
                    delta_cam[camera_index] = np.linalg.lstsq(schur[camera_index], schur_b[camera_index], rcond=None)[0]

        delta_points = np.zeros((len(points), 3), dtype=np.float64)
        for point_index in range(len(points)):
            rhs = pt_b[point_index].copy()
            if optimize_cameras:
                for camera_index in range(len(cams)):
                    if np.abs(cross[camera_index, point_index]).sum() >= 1e-14:
                        rhs -= cross[camera_index, point_index].T @ delta_cam[camera_index]
            delta_points[point_index] = point_inv[point_index] @ rhs

        trial_cams = (
            _apply_camera_pose_delta(cams, delta_cam.astype(np.float32))
            if optimize_cameras
            else cams.copy()
        )
        trial_points = sfm_apply_point_update_aot(points, delta_points.astype(np.float32))
        trial_squared, _ = cost_for(trial_cams, trial_points)
        if trial_squared < current_squared:
            cams, points = trial_cams, trial_points
            previous_squared = current_squared
            lam = max(lam / factor, 1e-10)
        else:
            previous_squared = current_squared
            lam = min(lam * factor, 1e12)

    final_squared, final_rmse = cost_for(cams, points)
    if return_history:
        return cams, points, final_rmse, iterations, history
    return cams, points, final_rmse, iterations


def poisson_reconstruct_aot(
    points,
    normals=None,
    grid_resolution=64,
    solver_iterations=50,
    iso_threshold=0.5,
    dilate_radius=2,
    omega=1.5,
):
    """Poisson volume solve through AOT primitives plus host mesh extraction."""

    data = _f32(points, ndim=2)
    if data.shape[1] != 3:
        raise ValueError("points must have shape (N, 3)")
    if len(data) == 0:
        return np.empty((0, 3), np.float32), np.empty((0, 3), np.int32)
    if normals is None:
        k = min(15, len(data) - 1)
        if k < 3:
            nrm = np.zeros_like(data)
            nrm[:, 2] = 1.0
        else:
            _, idx = sfm_knn_distance_aot(data, k=k)
            nrm = sfm_normals_pca_aot(data, idx)
    else:
        nrm = _f32(normals, ndim=2)
        if nrm.shape != data.shape:
            raise ValueError("normals must have the same shape as points")
    nrm = nrm / np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-8)

    resolution = int(grid_resolution)
    if resolution < 2:
        raise ValueError("grid_resolution must be at least 2")
    bbox_min = data.min(axis=0) - 1e-3
    bbox_max = data.max(axis=0) + 1e-3
    extent = bbox_max - bbox_min
    max_extent = float(max(extent.max(), 1e-6))
    voxel_size = max_extent / resolution
    dims = np.ceil(extent / voxel_size).astype(int) + 1
    gx, gy, gz = (max(2, int(value)) for value in dims)
    origin = bbox_min.astype(np.float32)

    mask = sfm_poisson_occupancy_aot(
        data,
        origin,
        voxel_size=voxel_size,
        gx=gx,
        gy=gy,
        gz=gz,
        dilate_radius=int(dilate_radius),
    )
    divergence = sfm_poisson_rasterize_aot(
        data,
        nrm,
        origin,
        voxel_size=voxel_size,
        gx=gx,
        gy=gy,
        gz=gz,
    )
    field = np.zeros_like(divergence, dtype=np.float32)
    for _ in range(max(0, int(solver_iterations))):
        field = sfm_poisson_step_aot(field, divergence, mask, omega=omega)

    from taichi_vision.taichi_algorithm.sfm.poisson_recon import _marching_cubes_numpy

    vertices, faces = _marching_cubes_numpy(
        field.astype(np.float64),
        mask,
        float(voxel_size),
        origin.astype(np.float64),
        float(iso_threshold),
    )
    vertices = np.asarray(vertices, dtype=np.float32)
    faces = np.asarray(faces, dtype=np.int32)
    vertices = vertices.reshape((-1, 3)) if vertices.size else np.empty((0, 3), np.float32)
    faces = faces.reshape((-1, 3)) if faces.size else np.empty((0, 3), np.int32)
    return vertices, faces


__all__ = [
    "hdr_fuse_aot",
    "hdr_fusion_aot",
    "local_tone_map_aot",
    "tone_map_aot",
    "plane_sweep_stereo_aot",
    "multi_view_plane_sweep_aot",
    "point_cloud_preprocess_aot",
    "bundle_adjust_lm_aot",
    "poisson_reconstruct_aot",
]
