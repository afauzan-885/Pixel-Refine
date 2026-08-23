"""Bounded UV texture-atlas rasterisation for reconstructed meshes.

The reconstruction family already produces triangle meshes, but did not expose
the final texture-space rasterisation step.  This module keeps the operation
small and explicit: callers provide per-vertex UVs, triangle indices, and an
image in texture space; the result is a deterministic atlas with a validity
mask.  ``backend="taichi"`` executes the same bounded rasteriser as a Taichi
JIT kernel on the caller's already-initialised Taichi runtime.  ``backend="aot"``
composes the host barycentric map with the existing target-qualified ``remap``
sampling leaf.  Neither path silently initialises a different device or falls
back to NumPy.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np


MAX_ATLAS_PIXELS = 16_000_000
DEFAULT_MAX_WORKING_BYTES = 1_500_000_000

try:  # Importing Taichi is cheap; initialisation remains the caller's policy.
    import taichi as ti
except Exception:  # pragma: no cover - exercised only on Taichi-less installs
    ti = None


@dataclass(frozen=True)
class TextureAtlasResult:
    """Rasterised atlas and the pixels covered by at least one triangle."""

    atlas: np.ndarray
    valid: np.ndarray
    backend: str


def _validate_inputs(
    uv_vertices: Any,
    faces: Any,
    texture: Any,
    atlas_shape: tuple[int, int],
    *,
    max_pixels: int,
    max_working_bytes: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, tuple[int, int]]:
    uv = np.ascontiguousarray(uv_vertices, dtype=np.float32)
    tri = np.ascontiguousarray(faces, dtype=np.int32)
    image = np.ascontiguousarray(texture, dtype=np.float32)
    if uv.ndim != 2 or uv.shape[1] != 2 or len(uv) == 0:
        raise ValueError("uv_vertices must have non-empty shape (N, 2)")
    if tri.ndim != 2 or tri.shape[1] != 3 or len(tri) == 0:
        raise ValueError("faces must have non-empty shape (M, 3)")
    if np.any(tri < 0) or np.any(tri >= len(uv)):
        raise ValueError("faces contain an out-of-range vertex index")
    if image.ndim not in (2, 3) or (image.ndim == 3 and image.shape[2] not in (1, 3, 4)):
        raise ValueError("texture must be HxW or HxWx(1|3|4)")
    if not np.isfinite(uv).all() or not np.isfinite(image).all():
        raise ValueError("uv_vertices and texture must contain only finite values")
    if len(atlas_shape) != 2:
        raise ValueError("atlas_shape must be (height, width)")
    height, width = (int(atlas_shape[0]), int(atlas_shape[1]))
    if height < 1 or width < 1:
        raise ValueError("atlas_shape dimensions must be positive")
    pixels = height * width
    if pixels > int(max_pixels):
        raise ValueError(f"atlas has {pixels:,} pixels; maximum is {int(max_pixels):,}")
    channels = 1 if image.ndim == 2 else int(image.shape[2])
    estimate = pixels * (channels * 4 + 1 + 4) + int(len(tri)) * 3 * 4
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    if estimate > int(max_working_bytes):
        raise MemoryError(f"texture atlas requires about {estimate} bytes, limit is {int(max_working_bytes)}")
    if np.min(image) < 0.0 or np.max(image) > 1.0:
        raise ValueError("texture values must be normalised to [0, 1]")
    return uv, tri, image, (height, width)


def _sample_numpy(image: np.ndarray, u: float, v: float) -> np.ndarray | float:
    """Bilinear sample using conventional UV coordinates (v=0 is bottom)."""

    h, w = image.shape[:2]
    x = float(np.clip(u, 0.0, 1.0)) * max(w - 1, 0)
    y = (1.0 - float(np.clip(v, 0.0, 1.0))) * max(h - 1, 0)
    x0, y0 = int(np.floor(x)), int(np.floor(y))
    x1, y1 = min(x0 + 1, w - 1), min(y0 + 1, h - 1)
    wx, wy = x - x0, y - y0
    if image.ndim == 2:
        return float(
            image[y0, x0] * (1.0 - wx) * (1.0 - wy)
            + image[y0, x1] * wx * (1.0 - wy)
            + image[y1, x0] * (1.0 - wx) * wy
            + image[y1, x1] * wx * wy
        )
    return (
        image[y0, x0] * ((1.0 - wx) * (1.0 - wy))
        + image[y0, x1] * (wx * (1.0 - wy))
        + image[y1, x0] * ((1.0 - wx) * wy)
        + image[y1, x1] * (wx * wy)
    )


def _build_uv_coordinate_maps(
    uv: np.ndarray,
    faces: np.ndarray,
    shape: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rasterise barycentric UV coordinates without sampling the source.

    This is the geometry half of :func:`_raster_numpy`.  It lets the AOT path
    reuse the existing target-qualified ``remap`` graph for bilinear sampling
    while retaining the same deterministic first-hit triangle policy and
    validity mask on the host.
    """

    height, width = shape
    map_u = np.zeros((height, width), dtype=np.float32)
    map_v = np.zeros((height, width), dtype=np.float32)
    valid = np.zeros((height, width), dtype=bool)
    for face in faces:
        p0, p1, p2 = uv[face[0]], uv[face[1]], uv[face[2]]
        min_x = max(0, int(np.floor(min(p0[0], p1[0], p2[0]) * (width - 1))))
        max_x = min(width - 1, int(np.ceil(max(p0[0], p1[0], p2[0]) * (width - 1))))
        min_y = max(0, int(np.floor((1.0 - max(p0[1], p1[1], p2[1])) * (height - 1))))
        max_y = min(height - 1, int(np.ceil((1.0 - min(p0[1], p1[1], p2[1])) * (height - 1))))
        if min_x > max_x or min_y > max_y:
            continue
        denominator = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if abs(float(denominator)) < 1.0e-12:
            continue
        for row in range(min_y, max_y + 1):
            v = 1.0 - float(row) / max(height - 1, 1)
            for col in range(min_x, max_x + 1):
                if valid[row, col]:
                    continue
                u = float(col) / max(width - 1, 1)
                w0 = ((p1[1] - p2[1]) * (u - p2[0]) + (p2[0] - p1[0]) * (v - p2[1])) / denominator
                w1 = ((p2[1] - p0[1]) * (u - p2[0]) + (p0[0] - p2[0]) * (v - p2[1])) / denominator
                w2 = 1.0 - w0 - w1
                if min(w0, w1, w2) < -1.0e-6:
                    continue
                map_u[row, col] = np.float32(w0 * p0[0] + w1 * p1[0] + w2 * p2[0])
                map_v[row, col] = np.float32(w0 * p0[1] + w1 * p1[1] + w2 * p2[1])
                valid[row, col] = True
    return map_u, map_v, valid


def _raster_numpy(uv: np.ndarray, faces: np.ndarray, image: np.ndarray, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    height, width = shape
    channels = 1 if image.ndim == 2 else int(image.shape[2])
    atlas = np.zeros((height, width) if channels == 1 else (height, width, channels), dtype=np.float32)
    valid = np.zeros((height, width), dtype=bool)
    # Faces are visited in source order.  This deterministic first-hit rule is
    # also used by the Taichi kernel for overlapping UV islands.
    for face in faces:
        p0, p1, p2 = uv[face[0]], uv[face[1]], uv[face[2]]
        min_x = max(0, int(np.floor(min(p0[0], p1[0], p2[0]) * (width - 1))))
        max_x = min(width - 1, int(np.ceil(max(p0[0], p1[0], p2[0]) * (width - 1))))
        min_y = max(0, int(np.floor((1.0 - max(p0[1], p1[1], p2[1])) * (height - 1))))
        max_y = min(height - 1, int(np.ceil((1.0 - min(p0[1], p1[1], p2[1])) * (height - 1))))
        if min_x > max_x or min_y > max_y:
            continue
        denominator = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if abs(float(denominator)) < 1.0e-12:
            continue
        for row in range(min_y, max_y + 1):
            v = 1.0 - float(row) / max(height - 1, 1)
            for col in range(min_x, max_x + 1):
                if valid[row, col]:
                    continue
                u = float(col) / max(width - 1, 1)
                w0 = ((p1[1] - p2[1]) * (u - p2[0]) + (p2[0] - p1[0]) * (v - p2[1])) / denominator
                w1 = ((p2[1] - p0[1]) * (u - p2[0]) + (p0[0] - p2[0]) * (v - p2[1])) / denominator
                w2 = 1.0 - w0 - w1
                if min(w0, w1, w2) < -1.0e-6:
                    continue
                sample_u = w0 * p0[0] + w1 * p1[0] + w2 * p2[0]
                sample_v = w0 * p0[1] + w1 * p1[1] + w2 * p2[1]
                value = _sample_numpy(image, sample_u, sample_v)
                if channels == 1:
                    atlas[row, col] = value
                else:
                    atlas[row, col, :] = value
                valid[row, col] = True
    return atlas, valid


if ti is not None:

    @ti.kernel
    def _raster_gray_kernel(
        uv: ti.types.ndarray(dtype=ti.f32, ndim=2),
        faces: ti.types.ndarray(dtype=ti.i32, ndim=2),
        texture: ti.types.ndarray(dtype=ti.f32, ndim=2),
        atlas: ti.types.ndarray(dtype=ti.f32, ndim=2),
        valid: ti.types.ndarray(dtype=ti.i32, ndim=2),
        n_faces: int,
        atlas_h: int,
        atlas_w: int,
        texture_h: int,
        texture_w: int,
    ):
        for row, col in ti.ndrange(atlas_h, atlas_w):
            atlas[row, col] = 0.0
            valid[row, col] = 0
            u = ti.cast(col, ti.f32) / ti.cast(ti.max(atlas_w - 1, 1), ti.f32)
            v = 1.0 - ti.cast(row, ti.f32) / ti.cast(ti.max(atlas_h - 1, 1), ti.f32)
            for face_index in range(n_faces):
                if valid[row, col] != 0:
                    continue
                i0, i1, i2 = faces[face_index, 0], faces[face_index, 1], faces[face_index, 2]
                p0x, p0y = uv[i0, 0], uv[i0, 1]
                p1x, p1y = uv[i1, 0], uv[i1, 1]
                p2x, p2y = uv[i2, 0], uv[i2, 1]
                denominator = (p1y - p2y) * (p0x - p2x) + (p2x - p1x) * (p0y - p2y)
                if ti.abs(denominator) < 1.0e-8:
                    continue
                w0 = ((p1y - p2y) * (u - p2x) + (p2x - p1x) * (v - p2y)) / denominator
                w1 = ((p2y - p0y) * (u - p2x) + (p0x - p2x) * (v - p2y)) / denominator
                w2 = 1.0 - w0 - w1
                if w0 < -1.0e-5 or w1 < -1.0e-5 or w2 < -1.0e-5:
                    continue
                sample_u = ti.min(ti.max(w0 * p0x + w1 * p1x + w2 * p2x, 0.0), 1.0)
                sample_v = ti.min(ti.max(w0 * p0y + w1 * p1y + w2 * p2y, 0.0), 1.0)
                tx = sample_u * ti.cast(ti.max(texture_w - 1, 0), ti.f32)
                ty = (1.0 - sample_v) * ti.cast(ti.max(texture_h - 1, 0), ti.f32)
                x0, y0 = ti.cast(ti.floor(tx), ti.i32), ti.cast(ti.floor(ty), ti.i32)
                x0 = ti.min(ti.max(x0, 0), texture_w - 1)
                y0 = ti.min(ti.max(y0, 0), texture_h - 1)
                x1, y1 = ti.min(x0 + 1, texture_w - 1), ti.min(y0 + 1, texture_h - 1)
                wx, wy = tx - ti.cast(x0, ti.f32), ty - ti.cast(y0, ti.f32)
                atlas[row, col] = (texture[y0, x0] * (1.0 - wx) * (1.0 - wy)
                    + texture[y0, x1] * wx * (1.0 - wy)
                    + texture[y1, x0] * (1.0 - wx) * wy
                    + texture[y1, x1] * wx * wy)
                valid[row, col] = 1

    @ti.kernel
    def _raster_rgb_kernel(
        uv: ti.types.ndarray(dtype=ti.f32, ndim=2),
        faces: ti.types.ndarray(dtype=ti.i32, ndim=2),
        texture: ti.types.ndarray(dtype=ti.f32, ndim=3),
        atlas: ti.types.ndarray(dtype=ti.f32, ndim=3),
        valid: ti.types.ndarray(dtype=ti.i32, ndim=2),
        n_faces: int,
        atlas_h: int,
        atlas_w: int,
        texture_h: int,
        texture_w: int,
        channels: int,
    ):
        for row, col in ti.ndrange(atlas_h, atlas_w):
            valid[row, col] = 0
            for channel in range(channels):
                atlas[row, col, channel] = 0.0
            u = ti.cast(col, ti.f32) / ti.cast(ti.max(atlas_w - 1, 1), ti.f32)
            v = 1.0 - ti.cast(row, ti.f32) / ti.cast(ti.max(atlas_h - 1, 1), ti.f32)
            for face_index in range(n_faces):
                if valid[row, col] != 0:
                    continue
                i0, i1, i2 = faces[face_index, 0], faces[face_index, 1], faces[face_index, 2]
                p0x, p0y = uv[i0, 0], uv[i0, 1]
                p1x, p1y = uv[i1, 0], uv[i1, 1]
                p2x, p2y = uv[i2, 0], uv[i2, 1]
                denominator = (p1y - p2y) * (p0x - p2x) + (p2x - p1x) * (p0y - p2y)
                if ti.abs(denominator) < 1.0e-8:
                    continue
                w0 = ((p1y - p2y) * (u - p2x) + (p2x - p1x) * (v - p2y)) / denominator
                w1 = ((p2y - p0y) * (u - p2x) + (p0x - p2x) * (v - p2y)) / denominator
                w2 = 1.0 - w0 - w1
                if w0 < -1.0e-5 or w1 < -1.0e-5 or w2 < -1.0e-5:
                    continue
                sample_u = ti.min(ti.max(w0 * p0x + w1 * p1x + w2 * p2x, 0.0), 1.0)
                sample_v = ti.min(ti.max(w0 * p0y + w1 * p1y + w2 * p2y, 0.0), 1.0)
                tx = sample_u * ti.cast(ti.max(texture_w - 1, 0), ti.f32)
                ty = (1.0 - sample_v) * ti.cast(ti.max(texture_h - 1, 0), ti.f32)
                x0, y0 = ti.cast(ti.floor(tx), ti.i32), ti.cast(ti.floor(ty), ti.i32)
                x0 = ti.min(ti.max(x0, 0), texture_w - 1)
                y0 = ti.min(ti.max(y0, 0), texture_h - 1)
                x1, y1 = ti.min(x0 + 1, texture_w - 1), ti.min(y0 + 1, texture_h - 1)
                wx, wy = tx - ti.cast(x0, ti.f32), ty - ti.cast(y0, ti.f32)
                for channel in range(channels):
                    atlas[row, col, channel] = (texture[y0, x0, channel] * (1.0 - wx) * (1.0 - wy)
                        + texture[y0, x1, channel] * wx * (1.0 - wy)
                        + texture[y1, x0, channel] * (1.0 - wx) * wy
                        + texture[y1, x1, channel] * wx * wy)
                valid[row, col] = 1


def rasterize_texture_atlas(
    uv_vertices: Any,
    faces: Any,
    texture: Any,
    atlas_shape: tuple[int, int],
    *,
    backend: str = "numpy",
    max_pixels: int = MAX_ATLAS_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
    return_result: bool = False,
) -> np.ndarray | TextureAtlasResult:
    """Rasterise a texture image through a triangle UV atlas.

    ``backend="taichi"`` requires the caller to initialise Taichi first
    (e.g. ``ti.init(arch=ti.cpu)``) and uses no host fallback.  ``backend``
    ``"aot"`` composes the host barycentric coordinate-map stage with the
    existing target-qualified ``remap`` sampling graph.  It is therefore an
    explicit hybrid path; the geometry stage is not advertised as a new
    native atlas graph.
    """

    name = str(backend).lower()
    if name not in {"numpy", "taichi", "aot"}:
        raise ValueError("backend must be 'numpy', 'taichi', or 'aot'")
    uv, tri, image, shape = _validate_inputs(
        uv_vertices,
        faces,
        texture,
        atlas_shape,
        max_pixels=int(max_pixels),
        max_working_bytes=int(max_working_bytes),
    )
    if name == "numpy":
        atlas, valid = _raster_numpy(uv, tri, image, shape)
    elif name == "taichi":
        if ti is None:
            raise ImportError("backend='taichi' requires the taichi package")
        try:
            runtime = ti.lang.impl.get_runtime()
            if getattr(runtime, "prog", None) is None:
                raise RuntimeError("backend='taichi' requires ti.init(...) before rasterize_texture_atlas")
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError("unable to verify the active Taichi runtime") from exc
        valid_i = np.zeros(shape, dtype=np.int32)
        if image.ndim == 2:
            atlas = np.zeros(shape, dtype=np.float32)
            _raster_gray_kernel(uv, tri, image, atlas, valid_i, len(tri), shape[0], shape[1], image.shape[0], image.shape[1])
        else:
            channels = int(image.shape[2])
            atlas = np.zeros((shape[0], shape[1], channels), dtype=np.float32)
            _raster_rgb_kernel(uv, tri, image, atlas, valid_i, len(tri), shape[0], shape[1], image.shape[0], image.shape[1], channels)
        valid = valid_i.astype(bool)
    else:
        channels = 1 if image.ndim == 2 else int(image.shape[2])
        # ``remap`` has scalar HxW and fixed vec3 HxWx3 graphs.  A singleton
        # third axis is not the scalar graph and must not be sent to the vec3
        # ABI as if it were a valid grayscale texture.
        if image.ndim == 3 and channels != 3:
            raise NotImplementedError(
                "backend='aot' UV atlas composition supports grayscale/RGB remap; "
                "H x W x 1/RGBA require an explicit squeeze/split or a "
                "target-qualified graph"
            )
        map_u, map_v, valid = _build_uv_coordinate_maps(uv, tri, shape)
        map_x = np.ascontiguousarray(map_u * np.float32(max(image.shape[1] - 1, 0)), dtype=np.float32)
        map_y = np.ascontiguousarray((1.0 - map_v) * np.float32(max(image.shape[0] - 1, 0)), dtype=np.float32)
        try:
            from ..aot_api import remap

            atlas = remap(image, map_x, map_y)
        except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
            raise NotImplementedError(
                "UV atlas AOT composition requires the target-qualified remap artifact"
            ) from exc
        atlas = np.ascontiguousarray(atlas, dtype=np.float32)
        if atlas.shape[:2] != shape:
            raise RuntimeError(f"AOT remap returned unexpected atlas shape {atlas.shape}")
        atlas[~valid] = 0.0
    atlas = np.ascontiguousarray(atlas, dtype=np.float32)
    result = TextureAtlasResult(atlas=atlas, valid=np.ascontiguousarray(valid, dtype=bool), backend=name)
    return result if return_result else atlas


__all__ = ["TextureAtlasResult", "rasterize_texture_atlas"]
