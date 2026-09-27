"""Taichi kernels for the patch-policy stage of SPDE-MR HDR fusion."""

import taichi as ti


@ti.kernel
def _score_patch_grid_f32(
    reference_gray: ti.types.ndarray(ti.f32, ndim=2),
    frame_gray: ti.types.ndarray(ti.f32, ndim=2),
    patch_quality: ti.types.ndarray(ti.f32, ndim=2),
    patch_stable: ti.types.ndarray(ti.i32, ndim=2),
    patch_rows: ti.i32,
    patch_cols: ti.i32,
    patch_size: ti.i32,
    stride: ti.i32,
    exposure_center: ti.f32,
    exposure_sigma: ti.f32,
    structure_threshold: ti.f32,
):
    """Compute local E×C×S quality and reference correlation per patch."""
    area = ti.cast(patch_size * patch_size, ti.f32)
    for patch_y, patch_x in ti.ndrange(patch_rows, patch_cols):
        y0 = patch_y * stride
        x0 = patch_x * stride
        reference_sum = 0.0
        frame_sum = 0.0
        reference_square_sum = 0.0
        frame_square_sum = 0.0
        cross_sum = 0.0

        for dy, dx in ti.ndrange(patch_size, patch_size):
            ref_value = reference_gray[y0 + dy, x0 + dx]
            frame_value = frame_gray[y0 + dy, x0 + dx]
            reference_sum += ref_value
            frame_sum += frame_value
            reference_square_sum += ref_value * ref_value
            frame_square_sum += frame_value * frame_value
            cross_sum += ref_value * frame_value

        reference_mean = reference_sum / area
        frame_mean = frame_sum / area
        reference_variance = ti.max(
            reference_square_sum / area - reference_mean * reference_mean, 0.0
        )
        frame_variance = ti.max(
            frame_square_sum / area - frame_mean * frame_mean, 0.0
        )
        covariance = cross_sum / area - reference_mean * frame_mean
        correlation = covariance / ti.sqrt(
            ti.max(reference_variance * frame_variance, 1e-12)
        )
        correlation = ti.max(-1.0, ti.min(correlation, 1.0))
        if reference_variance <= 1e-8 and frame_variance <= 1e-8:
            correlation = 1.0

        exposure_delta = (frame_mean - exposure_center) / exposure_sigma
        exposure = ti.exp(-0.5 * exposure_delta * exposure_delta)
        contrast = ti.sqrt(frame_variance)
        structure = ti.max(correlation, 0.0)
        patch_quality[patch_y, patch_x] = exposure * contrast * structure
        patch_stable[patch_y, patch_x] = ti.cast(
            correlation >= structure_threshold, ti.i32
        )


@ti.kernel
def _expand_patch_maps_f32(
    patch_quality: ti.types.ndarray(ti.f32, ndim=2),
    patch_stable: ti.types.ndarray(ti.i32, ndim=2),
    valid_mask: ti.types.ndarray(ti.i32, ndim=2),
    quality: ti.types.ndarray(ti.f32, ndim=2),
    stable: ti.types.ndarray(ti.i32, ndim=2),
    policy_weight: ti.types.ndarray(ti.f32, ndim=2),
    height: ti.i32,
    width: ti.i32,
    patch_rows: ti.i32,
    patch_cols: ti.i32,
):
    """Expand patch maps using OpenCV-compatible linear/nearest coordinates."""
    for y, x in ti.ndrange(height, width):
        source_y = (ti.cast(y, ti.f32) + 0.5) * patch_rows / height - 0.5
        source_x = (ti.cast(x, ti.f32) + 0.5) * patch_cols / width - 0.5
        source_y = ti.min(ti.max(source_y, 0.0), ti.cast(patch_rows - 1, ti.f32))
        source_x = ti.min(ti.max(source_x, 0.0), ti.cast(patch_cols - 1, ti.f32))
        y0 = ti.cast(ti.floor(source_y), ti.i32)
        x0 = ti.cast(ti.floor(source_x), ti.i32)
        y1 = ti.min(y0 + 1, patch_rows - 1)
        x1 = ti.min(x0 + 1, patch_cols - 1)
        wy = source_y - ti.cast(y0, ti.f32)
        wx = source_x - ti.cast(x0, ti.f32)

        top = patch_quality[y0, x0] * (1.0 - wx) + patch_quality[y0, x1] * wx
        bottom = patch_quality[y1, x0] * (1.0 - wx) + patch_quality[y1, x1] * wx
        interpolated = top * (1.0 - wy) + bottom * wy

        nearest_y = ti.min((y * patch_rows) // height, patch_rows - 1)
        nearest_x = ti.min((x * patch_cols) // width, patch_cols - 1)
        is_valid = valid_mask[y, x] != 0
        is_stable = patch_stable[nearest_y, nearest_x] != 0 and is_valid
        quality[y, x] = interpolated if is_valid else 0.0
        stable[y, x] = ti.cast(is_stable, ti.i32)
        policy_weight[y, x] = interpolated if is_stable else 0.0


__all__ = ["_score_patch_grid_f32", "_expand_patch_maps_f32"]
