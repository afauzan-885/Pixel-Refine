"""Portable Taichi kernels for the pre-demosaic RAW contract.

The public RAW model keeps sensor samples in their native integer container.
Graphics backends do not have a validated ``u16`` ABI in this repository, so
the AOT transport deliberately uses ``i32`` for samples and performs the
black/white normalization once inside the selected backend.  No demosaic or
implicit RGB interpolation is performed here.
"""

import taichi as ti


@ti.kernel
def raw_normalize_headroom_i32(
    src: ti.types.ndarray(dtype=ti.i32, ndim=2),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    black_level: ti.types.ndarray(dtype=ti.f32, ndim=1),
    white_level: ti.types.ndarray(dtype=ti.f32, ndim=1),
    white_balance: ti.types.ndarray(dtype=ti.f32, ndim=1),
    phase_y: ti.i32,
    phase_x: ti.i32,
    origin_y: ti.i32,
    origin_x: ti.i32,
    apply_white_balance: ti.i32,
    exposure_scale: ti.f32,
):
    """Normalize an absolute sensor-domain tile without upper clamping."""

    for y, x in dst:
        plane = (((y + origin_y + phase_y) & 1) * 2) + ((x + origin_x + phase_x) & 1)
        denominator = ti.max(white_level[plane] - black_level[plane], 1e-12)
        value = (ti.cast(src[y, x], ti.f32) - black_level[plane]) / denominator
        value = ti.max(value, 0.0)
        if apply_white_balance != 0:
            value *= white_balance[plane]
        dst[y, x] = value * exposure_scale


@ti.kernel
def raw_weight_map_f32(
    reference: ti.types.ndarray(dtype=ti.f32, ndim=2),
    current: ti.types.ndarray(dtype=ti.f32, ndim=2),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    noise_floor: ti.f32,
    sensitivity: ti.f32,
):
    """Build a finite residual weight map in normalized RAW space."""

    for y, x in dst:
        residual = ti.abs(current[y, x] - reference[y, x]) - ti.max(noise_floor, 0.0)
        residual = ti.max(residual, 0.0)
        scale = ti.max(sensitivity, 1e-6)
        dst[y, x] = 1.0 / (1.0 + residual * scale)


@ti.kernel
def raw_fuse_pair_f32(
    reference: ti.types.ndarray(dtype=ti.f32, ndim=2),
    current: ti.types.ndarray(dtype=ti.f32, ndim=2),
    local_weight: ti.types.ndarray(dtype=ti.f32, ndim=2),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    reference_weight: ti.f32,
    current_weight: ti.f32,
):
    """Fuse two already aligned normalized RAW tiles deterministically."""

    for y, x in dst:
        rw = ti.max(reference_weight, 0.0)
        cw = ti.max(current_weight, 0.0) * ti.max(local_weight[y, x], 0.0)
        denominator = rw + cw
        dst[y, x] = ti.select(
            denominator > 1e-12,
            (reference[y, x] * rw + current[y, x] * cw) / denominator,
            0.0,
        )


@ti.kernel
def raw_fuse_accumulate_f32(
    accum: ti.types.ndarray(dtype=ti.f32, ndim=2),
    denominator: ti.types.ndarray(dtype=ti.f32, ndim=2),
    current: ti.types.ndarray(dtype=ti.f32, ndim=2),
    local_weight: ti.types.ndarray(dtype=ti.f32, ndim=2),
    dst_accum: ti.types.ndarray(dtype=ti.f32, ndim=2),
    dst_denominator: ti.types.ndarray(dtype=ti.f32, ndim=2),
    current_weight: ti.f32,
):
    """Append one normalized frame to a deterministic weighted accumulator."""

    for y, x in dst_accum:
        weight = ti.max(current_weight, 0.0) * ti.max(local_weight[y, x], 0.0)
        dst_accum[y, x] = accum[y, x] + current[y, x] * weight
        dst_denominator[y, x] = denominator[y, x] + weight


__all__ = [
    "raw_normalize_headroom_i32",
    "raw_weight_map_f32",
    "raw_fuse_pair_f32",
    "raw_fuse_accumulate_f32",
]
