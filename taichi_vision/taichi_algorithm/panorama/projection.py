"""Inverse panorama projections for the family-local reference path.

The existing panorama compositor operates in a planar canvas.  This module
adds the coordinate maps normally used before/after that compositor:
cylindrical, spherical and equirectangular projections.  NumPy remains the
reference implementation; ``backend="taichi"`` runs the same map through a
CPU/GPU-capable JIT kernel.  ``backend="aot"`` reuses the existing
target-qualified ``remap`` graph for the sampling stage while keeping the
small analytic inverse-map construction on the host.  This is deliberately a
composed path: no projection-specific graph is claimed or required.

Coordinates are inverse-mapped and bilinearly sampled.  This avoids holes in
the output and makes the validity mask deterministic, which is useful when a
caller later computes an overlap seam.
"""

from dataclasses import dataclass
import importlib
import os
from typing import Any

import numpy as np

from ..pipeline_common import as_float32_image


MAX_PROJECTION_PIXELS = 55_000_000
DEFAULT_MAX_WORKING_BYTES = 1_500_000_000


_TAICHI_KERNELS: tuple[Any, Any] | None = None


class ProjectionError(ValueError):
    """Raised when a projection cannot be evaluated safely."""


@dataclass(frozen=True)
class ProjectionResult:
    """Projected image and its valid inverse-map mask."""

    image: np.ndarray
    valid: np.ndarray
    projection: str
    backend: str
    focal_length: tuple[float, float]


def _backend_name(backend: str) -> str:
    value = str(backend).lower()
    if value not in {"numpy", "taichi", "aot"}:
        raise ValueError("backend must be 'numpy', 'taichi', or 'aot'")
    return value


def _ensure_taichi_runtime(arch: Any | None = None):
    """Load Taichi and initialise it only when no runtime exists yet.

    This is deliberately local to the experimental JIT backend.  It does not
    touch the AOT engine or its backend selection.  A caller that already
    initialised Taichi keeps that runtime and can pass ``taichi_arch`` only for
    documentation/diagnostics.
    """

    try:
        taichi = importlib.import_module("taichi")
    except ImportError as exc:
        raise ImportError("backend='taichi' requires the taichi package") from exc
    requested = arch
    requested_explicit = requested is not None
    if requested is None:
        configured = os.environ.get("TAICHI_ARCH")
        if configured:
            requested = configured
            requested_explicit = True
        else:
            requested = "cpu"
    if isinstance(requested, str):
        requested_name = requested.lower().strip()
        arch_map = {
            "cpu": taichi.cpu,
            "cuda": taichi.cuda,
            "vulkan": taichi.vulkan,
            "opengl": getattr(taichi, "opengl", None),
            "gpu": taichi.gpu,
        }
        if requested_name not in arch_map or arch_map[requested_name] is None:
            raise ValueError("taichi_arch must be cpu, cuda, vulkan, opengl, or gpu")
        requested = arch_map[requested_name]
    runtime_ready = False
    try:
        runtime_ready = (
            getattr(taichi.lang.impl.get_runtime(), "prog", None) is not None
        )
    except Exception:
        runtime_ready = False
    if runtime_ready:
        current = getattr(getattr(taichi, "cfg", None), "arch", None)
        if requested_explicit and current != requested:
            raise RuntimeError(
                f"backend='taichi' requested arch {requested}, but Taichi is already initialised on {current}"
            )
    else:
        taichi.init(arch=requested, offline_cache=False)
    return taichi


def _taichi_projection_kernels(taichi):
    """Create and cache 2D/3D JIT kernels after Taichi is importable."""

    global _TAICHI_KERNELS
    if _TAICHI_KERNELS is not None:
        return _TAICHI_KERNELS

    @taichi.kernel
    def project_2d(
        src: taichi.types.ndarray(dtype=taichi.f32, ndim=2),
        dst: taichi.types.ndarray(dtype=taichi.f32, ndim=2),
        valid: taichi.types.ndarray(dtype=taichi.i32, ndim=2),
        h_src: taichi.i32,
        w_src: taichi.i32,
        h_dst: taichi.i32,
        w_dst: taichi.i32,
        fx: taichi.f32,
        fy: taichi.f32,
        yaw: taichi.f32,
        pitch: taichi.f32,
        projection_mode: taichi.i32,
    ):
        for r, c in taichi.ndrange(h_dst, w_dst):
            cx_src = (float(w_src) - 1.0) * 0.5
            cy_src = (float(h_src) - 1.0) * 0.5
            cx_dst = (float(w_dst) - 1.0) * 0.5
            cy_dst = (float(h_dst) - 1.0) * 0.5
            longitude = 0.0
            latitude = 0.0
            vertical = 0.0
            if projection_mode == 0:  # cylindrical
                longitude = (float(c) - cx_dst) / fx + yaw
                vertical = (float(r) - cy_dst) / fy + pitch
            elif projection_mode == 1:  # spherical
                longitude = (float(c) - cx_dst) / fx + yaw
                latitude = -(float(r) - cy_dst) / fy + pitch
            else:  # equirectangular
                longitude = ((float(c) + 0.5) / float(w_dst) - 0.5) * (
                    2.0 * taichi.math.pi
                ) + yaw
                latitude = (
                    0.5 - (float(r) + 0.5) / float(h_dst)
                ) * taichi.math.pi + pitch
            cosine = taichi.cos(longitude)
            good = taichi.abs(cosine) > 1.0e-8
            src_x = 0.0
            src_y = 0.0
            if good:
                src_x = fx * taichi.tan(longitude) + cx_src
                if projection_mode == 0:
                    src_y = fy * (vertical / cosine) + cy_src
                else:
                    good = good & (taichi.abs(latitude) < 0.5 * taichi.math.pi - 1.0e-6)
                    if good:
                        src_y = fy * (taichi.tan(latitude) / cosine) + cy_src
            good = good & (src_x >= 0.0) & (src_x <= float(w_src - 1))
            good = good & (src_y >= 0.0) & (src_y <= float(h_src - 1))
            x0 = int(taichi.floor(src_x))
            y0 = int(taichi.floor(src_y))
            x0c = taichi.min(taichi.max(x0, 0), w_src - 1)
            y0c = taichi.min(taichi.max(y0, 0), h_src - 1)
            x1c = taichi.min(x0c + 1, w_src - 1)
            y1c = taichi.min(y0c + 1, h_src - 1)
            wx = src_x - float(x0)
            wy = src_y - float(y0)
            value = (
                src[y0c, x0c] * (1.0 - wx) * (1.0 - wy)
                + src[y0c, x1c] * wx * (1.0 - wy)
                + src[y1c, x0c] * (1.0 - wx) * wy
                + src[y1c, x1c] * wx * wy
            )
            dst[r, c] = value if good else 0.0
            valid[r, c] = 1 if good else 0

    @taichi.kernel
    def project_3d(
        src: taichi.types.ndarray(dtype=taichi.f32, ndim=3),
        dst: taichi.types.ndarray(dtype=taichi.f32, ndim=3),
        valid: taichi.types.ndarray(dtype=taichi.i32, ndim=2),
        h_src: taichi.i32,
        w_src: taichi.i32,
        h_dst: taichi.i32,
        w_dst: taichi.i32,
        fx: taichi.f32,
        fy: taichi.f32,
        yaw: taichi.f32,
        pitch: taichi.f32,
        projection_mode: taichi.i32,
    ):
        for r, c, channel in taichi.ndrange(h_dst, w_dst, dst.shape[2]):
            cx_src = (float(w_src) - 1.0) * 0.5
            cy_src = (float(h_src) - 1.0) * 0.5
            cx_dst = (float(w_dst) - 1.0) * 0.5
            cy_dst = (float(h_dst) - 1.0) * 0.5
            longitude = 0.0
            latitude = 0.0
            vertical = 0.0
            if projection_mode == 0:
                longitude = (float(c) - cx_dst) / fx + yaw
                vertical = (float(r) - cy_dst) / fy + pitch
            elif projection_mode == 1:
                longitude = (float(c) - cx_dst) / fx + yaw
                latitude = -(float(r) - cy_dst) / fy + pitch
            else:
                longitude = ((float(c) + 0.5) / float(w_dst) - 0.5) * (
                    2.0 * taichi.math.pi
                ) + yaw
                latitude = (
                    0.5 - (float(r) + 0.5) / float(h_dst)
                ) * taichi.math.pi + pitch
            cosine = taichi.cos(longitude)
            good = taichi.abs(cosine) > 1.0e-8
            src_x = 0.0
            src_y = 0.0
            if good:
                src_x = fx * taichi.tan(longitude) + cx_src
                if projection_mode == 0:
                    src_y = fy * (vertical / cosine) + cy_src
                else:
                    good = good & (taichi.abs(latitude) < 0.5 * taichi.math.pi - 1.0e-6)
                    if good:
                        src_y = fy * (taichi.tan(latitude) / cosine) + cy_src
            good = good & (src_x >= 0.0) & (src_x <= float(w_src - 1))
            good = good & (src_y >= 0.0) & (src_y <= float(h_src - 1))
            x0 = int(taichi.floor(src_x))
            y0 = int(taichi.floor(src_y))
            x0c = taichi.min(taichi.max(x0, 0), w_src - 1)
            y0c = taichi.min(taichi.max(y0, 0), h_src - 1)
            x1c = taichi.min(x0c + 1, w_src - 1)
            y1c = taichi.min(y0c + 1, h_src - 1)
            wx = src_x - float(x0)
            wy = src_y - float(y0)
            value = (
                src[y0c, x0c, channel] * (1.0 - wx) * (1.0 - wy)
                + src[y0c, x1c, channel] * wx * (1.0 - wy)
                + src[y1c, x0c, channel] * (1.0 - wx) * wy
                + src[y1c, x1c, channel] * wx * wy
            )
            dst[r, c, channel] = value if good else 0.0
            valid[r, c] = 1 if good else 0

    _TAICHI_KERNELS = (project_2d, project_3d)
    return _TAICHI_KERNELS


def _project_taichi(
    src: np.ndarray,
    output_shape: tuple[int, int],
    focal: tuple[float, float],
    projection_name: str,
    yaw: float,
    pitch: float,
    *,
    taichi_arch: Any | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    taichi = _ensure_taichi_runtime(taichi_arch)
    kernels = _taichi_projection_kernels(taichi)
    oh, ow = output_shape
    output = np.empty(
        (oh, ow) if src.ndim == 2 else (oh, ow, src.shape[2]), dtype=np.float32
    )
    valid = np.zeros((oh, ow), dtype=np.int32)
    mode = {"cylindrical": 0, "spherical": 1, "equirectangular": 2}[projection_name]
    fx, fy = focal
    if src.ndim == 2:
        kernels[0](
            src,
            output,
            valid,
            src.shape[0],
            src.shape[1],
            oh,
            ow,
            fx,
            fy,
            yaw,
            pitch,
            mode,
        )
    else:
        kernels[1](
            src,
            output,
            valid,
            src.shape[0],
            src.shape[1],
            oh,
            ow,
            fx,
            fy,
            yaw,
            pitch,
            mode,
        )
    taichi.sync()
    return output, valid.astype(bool)


def _project_aot(
    src: np.ndarray,
    output_shape: tuple[int, int],
    projection_name: str,
    focal: tuple[float, float],
    yaw: float,
    pitch: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Compose the host projection map with the qualified AOT remap leaf.

    The analytic map is generated by the same reference helper used by the
    NumPy path.  Only bilinear sampling is dispatched to the existing
    ``remap`` TCM, so this function does not imply that a projection-specific
    graph exists.  Invalid/NaN map entries are replaced by a safe coordinate
    before dispatch and masked back to zero afterwards; otherwise a remap
    kernel is allowed to clamp an invalid coordinate to the image edge.
    """

    source_x, source_y, valid = _inverse_map(
        projection_name,
        src.shape,
        output_shape,
        focal,
        float(yaw),
        float(pitch),
    )
    finite = np.isfinite(source_x) & np.isfinite(source_y)
    valid = np.asarray(valid, dtype=bool) & finite
    safe_x = np.where(valid, source_x, 0.0).astype(np.float32, copy=False)
    safe_y = np.where(valid, source_y, 0.0).astype(np.float32, copy=False)
    try:
        from .. import aot_api

        sampled = aot_api.remap(
            np.ascontiguousarray(src, dtype=np.float32),
            np.ascontiguousarray(safe_x),
            np.ascontiguousarray(safe_y),
            return_gpu=False,
        )
    except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
        raise NotImplementedError(
            "panorama AOT projection requires the target-qualified 'remap' artifact; "
            "use backend='numpy' or backend='taichi' explicitly"
        ) from exc
    sampled = np.ascontiguousarray(sampled, dtype=np.float32)
    sampled[~valid] = 0.0
    return sampled, valid


def _budget(shape: tuple[int, ...], *, max_pixels: int, max_working_bytes: int) -> None:
    if len(shape) < 2:
        raise ProjectionError("image shape must have at least two dimensions")
    pixels = int(shape[0]) * int(shape[1])
    if pixels < 1 or pixels > int(max_pixels):
        raise ProjectionError(
            f"projection output has {pixels:,} pixels; maximum is {int(max_pixels):,}"
        )
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    channels = 1 if len(shape) == 2 else int(shape[2])
    # Coordinate maps (x/y), valid mask, sampled image and output.  This is a
    # conservative estimate and deliberately rejects before allocating maps.
    estimate = pixels * (8 + 8 + 1 + 4 * channels + 4 * channels)
    if estimate > int(max_working_bytes):
        raise MemoryError(
            f"projection requires about {estimate} bytes, limit is {int(max_working_bytes)}"
        )


def _focal_pair(
    source_shape: tuple[int, ...],
    output_shape: tuple[int, int],
    focal_length: float | tuple[float, float] | None,
) -> tuple[tuple[float, float], tuple[float, float]]:
    sh, sw = int(source_shape[0]), int(source_shape[1])
    oh, ow = int(output_shape[0]), int(output_shape[1])
    if focal_length is None:
        # A 90-degree horizontal field of view is a stable reference default.
        fx = max(float(sw) * 0.5, 1.0)
        fy = max(float(sh) * 0.5, 1.0)
    elif np.isscalar(focal_length):
        fx = fy = float(focal_length)
    else:
        if len(focal_length) != 2:
            raise ValueError("focal_length must be a scalar or (fx, fy)")
        fx, fy = float(focal_length[0]), float(focal_length[1])
    if not np.isfinite(fx) or not np.isfinite(fy) or fx <= 0.0 or fy <= 0.0:
        raise ValueError("focal_length values must be finite and positive")
    return (fx, fy), (max((ow - 1) * 0.5, 0.0), max((oh - 1) * 0.5, 0.0))


def _sample_bilinear(
    image: np.ndarray,
    source_x: np.ndarray,
    source_y: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Bilinearly sample image at maps; invalid samples become zero."""

    src = np.asarray(image, dtype=np.float32)
    h, w = src.shape[:2]
    finite = np.isfinite(source_x) & np.isfinite(source_y)
    valid = np.asarray(valid, dtype=bool) & finite
    safe_x = np.where(finite, source_x, 0.0)
    safe_y = np.where(finite, source_y, 0.0)
    x0 = np.clip(np.floor(safe_x).astype(np.int64), 0, max(w - 1, 0))
    y0 = np.clip(np.floor(safe_y).astype(np.int64), 0, max(h - 1, 0))
    x1 = np.clip(x0 + 1, 0, max(w - 1, 0))
    y1 = np.clip(y0 + 1, 0, max(h - 1, 0))
    wx = (safe_x - np.floor(safe_x)).astype(np.float32)
    wy = (safe_y - np.floor(safe_y)).astype(np.float32)
    if src.ndim == 2:
        out = (
            src[y0, x0] * (1.0 - wx) * (1.0 - wy)
            + src[y0, x1] * wx * (1.0 - wy)
            + src[y1, x0] * (1.0 - wx) * wy
            + src[y1, x1] * wx * wy
        ).astype(np.float32)
        out[~valid] = 0.0
        return out
    out = (
        src[y0, x0] * ((1.0 - wx) * (1.0 - wy))[..., None]
        + src[y0, x1] * (wx * (1.0 - wy))[..., None]
        + src[y1, x0] * ((1.0 - wx) * wy)[..., None]
        + src[y1, x1] * (wx * wy)[..., None]
    ).astype(np.float32)
    out[~valid] = 0.0
    return out


def _normalise_output_shape(
    image: np.ndarray, output_shape: tuple[int, int] | None, projection: str
) -> tuple[int, int]:
    if output_shape is None:
        h, w = image.shape[:2]
        if projection == "equirectangular":
            return int(h), max(2 * int(h), 1)
        return int(h), int(w)
    if len(output_shape) != 2:
        raise ValueError("output_shape must be (height, width)")
    h, w = int(output_shape[0]), int(output_shape[1])
    if h < 1 or w < 1:
        raise ValueError("output_shape dimensions must be positive")
    return h, w


def _inverse_map(
    projection: str,
    source_shape: tuple[int, ...],
    output_shape: tuple[int, int],
    focal_length: tuple[float, float],
    yaw: float,
    pitch: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build source x/y coordinates for an output grid."""

    sh, sw = int(source_shape[0]), int(source_shape[1])
    oh, ow = output_shape
    fx, fy = focal_length
    cx_src, cy_src = (sw - 1) * 0.5, (sh - 1) * 0.5
    cx_out, cy_out = (ow - 1) * 0.5, (oh - 1) * 0.5
    yy, xx = np.indices((oh, ow), dtype=np.float64)
    if projection == "cylindrical":
        theta = (xx - cx_out) / fx + float(yaw)
        vertical = (yy - cy_out) / fy + float(pitch)
        cosine = np.cos(theta)
        safe_cosine = np.where(np.abs(cosine) > 1.0e-8, cosine, np.nan)
        source_x = fx * np.tan(theta) + cx_src
        source_y = fy * (vertical / safe_cosine) + cy_src
        valid = np.isfinite(source_x) & np.isfinite(source_y)
    elif projection in {"spherical", "equirectangular"}:
        # Longitude/latitude are represented directly on the output grid.
        if projection == "equirectangular":
            longitude = ((xx + 0.5) / float(ow) - 0.5) * (2.0 * np.pi) + float(yaw)
            latitude = (0.5 - (yy + 0.5) / float(oh)) * np.pi + float(pitch)
        else:
            longitude = (xx - cx_out) / fx + float(yaw)
            latitude = -(yy - cy_out) / fy + float(pitch)
        cosine = np.cos(longitude)
        safe_cosine = np.where(np.abs(cosine) > 1.0e-8, cosine, np.nan)
        source_x = fx * np.tan(longitude) + cx_src
        source_y = fy * (np.tan(latitude) / safe_cosine) + cy_src
        valid = (
            np.isfinite(source_x)
            & np.isfinite(source_y)
            & (np.abs(latitude) < (0.5 * np.pi - 1.0e-6))
        )
    else:
        raise ValueError(
            "projection must be 'cylindrical', 'spherical', or 'equirectangular'"
        )
    valid &= (source_x >= 0.0) & (source_x <= sw - 1.0)
    valid &= (source_y >= 0.0) & (source_y <= sh - 1.0)
    return source_x, source_y, valid


def project_image(
    image: Any,
    *,
    projection: str = "cylindrical",
    focal_length: float | tuple[float, float] | None = None,
    output_shape: tuple[int, int] | None = None,
    yaw: float = 0.0,
    pitch: float = 0.0,
    backend: str = "numpy",
    taichi_arch: Any | None = None,
    max_pixels: int = MAX_PROJECTION_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
    return_result: bool = False,
) -> np.ndarray | ProjectionResult:
    """Project an image to a cylindrical, spherical or equirectangular map.

    ``backend="numpy"`` is an explicit host reference path.  ``backend="taichi"``
    runs the same inverse map with a JIT kernel (CPU by default, or the caller's
    selected ``taichi_arch``).  ``backend="aot"`` composes the host inverse map
    with the existing target-qualified ``remap`` graph; it does not claim a
    projection-specific AOT graph.  The optional
    :class:`ProjectionResult` exposes the geometric mask needed by
    overlap/exposure/seam stages.
    """

    backend_name = _backend_name(backend)
    src = as_float32_image(image, name="image")
    # The maintained remap AOT graph has a scalar 2-D variant and a fixed
    # vec3 variant.  Do not let a 3-D singleton/RGBA image reach the native
    # dispatcher, where it would fail with a low-level field-dimension error.
    # NumPy and explicit Taichi JIT retain their broader channel handling.
    if backend_name == "aot" and src.ndim == 3 and int(src.shape[2]) != 3:
        raise NotImplementedError(
            "panorama AOT projection supports HxW or HxWx3 input; "
            "use backend='numpy'/'taichi' or convert the channel layout explicitly"
        )
    projection_name = str(projection).lower()
    out_shape = _normalise_output_shape(src, output_shape, projection_name)
    _budget(
        out_shape + (() if src.ndim == 2 else (src.shape[2],)),
        max_pixels=int(max_pixels),
        max_working_bytes=int(max_working_bytes),
    )
    if not np.isfinite(src).all():
        raise ValueError("image must contain only finite values")
    if not np.isfinite(float(yaw)) or not np.isfinite(float(pitch)):
        raise ValueError("yaw and pitch must be finite")
    focal, _ = _focal_pair(src.shape, out_shape, focal_length)
    if backend_name == "taichi":
        output, valid = _project_taichi(
            src,
            out_shape,
            focal,
            projection_name,
            float(yaw),
            float(pitch),
            taichi_arch=taichi_arch,
        )
    elif backend_name == "aot":
        output, valid = _project_aot(
            src,
            out_shape,
            projection_name,
            focal,
            float(yaw),
            float(pitch),
        )
    else:
        source_x, source_y, valid = _inverse_map(
            projection_name,
            src.shape,
            out_shape,
            focal,
            float(yaw),
            float(pitch),
        )
        output = _sample_bilinear(src, source_x, source_y, valid)
    output = np.ascontiguousarray(output, dtype=np.float32)
    result = ProjectionResult(
        output,
        np.ascontiguousarray(valid, dtype=bool),
        projection_name,
        backend_name,
        focal,
    )
    return result if return_result else output


def cylindrical_projection(image: Any, **kwargs: Any) -> np.ndarray | ProjectionResult:
    """Convenience wrapper for :func:`project_image` with cylindrical mode."""

    kwargs["projection"] = "cylindrical"
    return project_image(image, **kwargs)


def spherical_projection(image: Any, **kwargs: Any) -> np.ndarray | ProjectionResult:
    """Convenience wrapper for :func:`project_image` with spherical mode."""

    kwargs["projection"] = "spherical"
    return project_image(image, **kwargs)


def equirectangular_projection(
    image: Any, **kwargs: Any
) -> np.ndarray | ProjectionResult:
    """Convenience wrapper for :func:`project_image` with equirectangular mode."""

    kwargs["projection"] = "equirectangular"
    return project_image(image, **kwargs)


__all__ = [
    "ProjectionError",
    "ProjectionResult",
    "project_image",
    "cylindrical_projection",
    "spherical_projection",
    "equirectangular_projection",
]
