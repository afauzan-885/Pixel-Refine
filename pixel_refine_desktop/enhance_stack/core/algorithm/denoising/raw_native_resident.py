"""Sensor-native resident processing for derived mosaiced DNG output.

Alignment is estimated from a temporary linear RGB proxy, but every warp and
accumulation operation below works on independent float32 Bayer planes.  The
source orientation stays in sensor coordinates until one final materialization
step in :mod:`Average`.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
import queue
import threading

import numpy as np


class RawNativePipelineNotReadyError(RuntimeError):
    """Raised when an algorithm has no truthful RAW mosaic implementation."""


@dataclass(frozen=True)
class RawNativeAlignmentReport:
    """Small execution record for RAW Native Average alignment."""

    alignment_plan: str
    frames: int
    aligned_supports: int
    identity_supports: int
    domain: str = "sensor_native_cfa_float32"
    block_size: int | None = None
    block_count: int = 1


@dataclass(frozen=True)
class RawNativeSession:
    """Validated burst with lazy support-frame decoding.

    The reference mosaic stays available for final materialization.  Support
    mosaics are decoded from their DNG payload only for a proxy, a full-source
    dense-flow pass, or the exact ROI needed by a homography tile.
    """

    paths: tuple[str, ...]
    containers: tuple[object, ...]
    reference_frame: object

    @classmethod
    def load(cls, image_paths) -> "RawNativeSession":
        from taichi_vision.taichi_algorithm.compression import RawMosaicFrame, read_dng_aot

        paths = tuple(str(Path(path)) for path in image_paths)
        if len(paths) < 2:
            raise ValueError("RAW Native Average requires at least two DNG frames")
        if any(Path(path).suffix.lower() != ".dng" for path in paths):
            raise ValueError("RAW Native processing currently supports DNG input only")
        containers = tuple(read_dng_aot(path) for path in paths)
        reference = RawMosaicFrame.from_dng(containers[0], source_id=paths[0])
        contract = (
            reference.shape,
            reference.bits_per_sample,
            reference.cfa_pattern,
            reference.phase_origin,
            reference.black_level,
            reference.white_level,
            reference.active_area,
            reference.orientation,
            reference.exposure_scale,
        )
        for path, container in zip(paths[1:], containers[1:]):
            # Decode one support frame only while validating its semantic
            # contract; do not retain its HxW sample array for the burst.
            frame = RawMosaicFrame.from_dng(container, source_id=path)
            candidate = (
                frame.shape,
                frame.bits_per_sample,
                frame.cfa_pattern,
                frame.phase_origin,
                frame.black_level,
                frame.white_level,
                frame.active_area,
                frame.orientation,
                frame.exposure_scale,
            )
            if candidate != contract:
                raise ValueError(
                    "RAW Native requires matching sensor geometry, CFA phase, "
                    "calibration, active area, and orientation; incompatible frame: "
                    f"{path}"
                )
        return cls(paths=paths, containers=containers, reference_frame=reference)

    @property
    def reference(self):
        return self.reference_frame

    @property
    def frame_count(self) -> int:
        return len(self.paths)

    def frame(self, index: int):
        """Materialize one source frame; support callers must not retain it."""
        from taichi_vision.taichi_algorithm.compression import RawMosaicFrame

        index = int(index)
        if index == 0:
            return self.reference_frame
        return RawMosaicFrame.from_dng(self.containers[index], source_id=self.paths[index])

    def region(self, index: int, y0: int, y1: int, x0: int, x1: int):
        """Decode a phase-correct source ROI without a full support mosaic."""
        from taichi_vision.taichi_algorithm.compression import RawMosaicFrame

        index = int(index)
        if index == 0:
            return _source_region_frame(self.reference_frame, y0, y1, x0, x1)
        return RawMosaicFrame.from_dng_region(
            self.containers[index], y0, y1, x0, x1, source_id=self.paths[index]
        )

    def normalized(self, index: int) -> np.ndarray:
        frame = self.frame(index)
        return np.ascontiguousarray(
            frame.normalized_headroom(apply_white_balance=False),
            dtype=np.float32,
        )

    def normalized_region(self, index: int, y0: int, y1: int, x0: int, x1: int) -> np.ndarray:
        frame = self.region(index, y0, y1, x0, x1)
        return np.ascontiguousarray(
            frame.normalized_headroom(apply_white_balance=False), dtype=np.float32
        )

    def analysis_proxy(self, index: int, *, work_scale: float = 1.0):
        """Create one temporary RGB proxy in sensor—not display—coordinates."""
        from taichi_vision import taichi_aot

        frame = self.frame(index)
        maximum_code = (1 << int(frame.bits_per_sample)) - 1
        cfa_pattern = tuple(int(value) for value in frame.cfa_pattern)
        raw_proxy = np.clip(
            np.rint(
                frame.normalized_headroom(apply_white_balance=False) * maximum_code
            ),
            0,
            maximum_code,
        ).astype(np.float32)
        # A support frame is only needed for its temporary demosaic proxy.
        # Releasing this local reference now lets its decoded sample array be
        # reclaimed before the RGB proxy/resize path allocates its own buffers.
        if int(index) != 0:
            del frame
        proxy = taichi_aot.demosaic(
            raw_proxy,
            method="hamilton",
            return_gpu=True,
            wb_r=1.0,
            wb_g1=1.0,
            wb_b=1.0,
            wb_g2=1.0,
            cmatrix=np.eye(3, dtype=np.float32),
            black_level=0.0,
            white_level=float(maximum_code),
            c00=cfa_pattern[0],
            c01=cfa_pattern[1],
            c10=cfa_pattern[2],
            c11=cfa_pattern[3],
        )
        scale = min(1.0, max(0.05, float(work_scale)))
        if scale == 1.0:
            return proxy
        height, width = map(int, proxy.shape[:2])
        resized = taichi_aot.resize(
            proxy,
            (max(32, int(width * scale)), max(32, int(height * scale))),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
        _release(proxy)
        return resized


def _release(buffer) -> None:
    if buffer is None:
        return
    for method in ("destroy", "release"):
        callback = getattr(buffer, method, None)
        if callable(callback):
            callback()
            return


def _plane_slice(frame, index: int) -> tuple[slice, slice]:
    plane_row, plane_col = divmod(int(index), 2)
    row = (plane_row - int(frame.phase_origin[0])) & 1
    col = (plane_col - int(frame.phase_origin[1])) & 1
    return slice(row, None, 2), slice(col, None, 2)


def _plane_homography(matrix: np.ndarray, frame, index: int) -> np.ndarray:
    """Conjugate a sensor-pixel homography into one half-resolution CFA plane."""
    row_slice, col_slice = _plane_slice(frame, index)
    origin_x, origin_y = int(col_slice.start), int(row_slice.start)
    plane_to_sensor = np.array(
        [[2.0, 0.0, origin_x], [0.0, 2.0, origin_y], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )
    return np.ascontiguousarray(
        np.linalg.inv(plane_to_sensor) @ np.asarray(matrix, dtype=np.float32) @ plane_to_sensor,
        dtype=np.float32,
    )


def _tile_plane_selector(frame, index: int, y0: int, x0: int, height: int, width: int):
    """Select one CFA plane inside an output tile and its full-plane offset."""
    full_rows, full_columns = _plane_slice(frame, index)
    first_row = (int(full_rows.start) - int(y0)) & 1
    first_column = (int(full_columns.start) - int(x0)) & 1
    rows = slice(first_row, int(height), 2)
    columns = slice(first_column, int(width), 2)
    plane_h = len(range(first_row, int(height), 2))
    plane_w = len(range(first_column, int(width), 2))
    offset_y = (int(y0) + first_row - int(full_rows.start)) // 2
    offset_x = (int(x0) + first_column - int(full_columns.start)) // 2
    return rows, columns, plane_h, plane_w, offset_y, offset_x


def _source_region_frame(frame, y0: int, y1: int, x0: int, x1: int):
    """Create a phase-correct RAW view for a source ROI in sensor coordinates."""
    from taichi_vision.taichi_algorithm.compression import RawMosaicFrame

    metadata = dict(frame.metadata)
    metadata["region_origin"] = (int(y0), int(x0))
    return RawMosaicFrame.from_samples(
        np.ascontiguousarray(frame.samples[y0:y1, x0:x1]),
        bits_per_sample=frame.bits_per_sample,
        cfa_pattern=frame.cfa_pattern,
        phase_origin=(
            (int(frame.phase_origin[0]) + int(y0)) & 1,
            (int(frame.phase_origin[1]) + int(x0)) & 1,
        ),
        black_level=frame.black_level,
        white_level=frame.white_level,
        active_area=(0, 0, int(y1 - y0), int(x1 - x0)),
        white_balance=frame.white_balance,
        exposure_scale=frame.exposure_scale,
        orientation=frame.orientation,
        source_id=frame.source_id,
        source_version=frame.source_version,
        metadata=metadata,
    )


def _homography_source_roi(matrix, y0, y1, x0, x1, shape, *, halo: int = 2):
    """Return the conservative source ROI required by one output tile."""
    height, width = (int(shape[0]), int(shape[1]))
    try:
        inverse = np.linalg.inv(np.asarray(matrix, dtype=np.float32))
    except np.linalg.LinAlgError as exc:
        raise ValueError("RAW Native homography is singular") from exc
    corners = np.asarray(
        ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)),
        dtype=np.float32,
    )
    points = np.c_[corners, np.ones((4, 1), dtype=np.float32)] @ inverse.T
    points = points[:, :2] / np.maximum(points[:, 2:3], 1e-12)
    left = max(0, int(np.floor(np.min(points[:, 0]))) - int(halo))
    top = max(0, int(np.floor(np.min(points[:, 1]))) - int(halo))
    right = min(width, int(np.ceil(np.max(points[:, 0]))) + int(halo) + 1)
    bottom = min(height, int(np.ceil(np.max(points[:, 1]))) + int(halo) + 1)
    if right <= left or bottom <= top:
        raise ValueError("RAW Native homography tile has an empty source ROI")
    return top, bottom, left, right


def _warp_cfa_homography_tile(source_frame, reference_frame, matrix, y0, y1, x0, x1):
    """Warp only one global output tile, preserving its absolute CFA phase."""
    from taichi_vision import taichi_aot

    source = source_frame.normalized_headroom(apply_white_balance=False)
    tile_h, tile_w = int(y1 - y0), int(x1 - x0)
    warped = np.zeros((tile_h, tile_w), dtype=np.float32)
    valid = np.zeros((tile_h, tile_w), dtype=np.float32)
    for index in range(4):
        source_rows, source_columns = _plane_slice(source_frame, index)
        output_rows, output_columns, plane_h, plane_w, out_y, out_x = _tile_plane_selector(
            reference_frame, index, y0, x0, tile_h, tile_w
        )
        if plane_h == 0 or plane_w == 0:
            continue
        source_plane = np.ascontiguousarray(
            source[source_rows, source_columns], dtype=np.float32
        )
        source_origin_y, source_origin_x = source_frame.metadata.get(
            "region_origin", (0, 0)
        )
        source_to_sensor = np.asarray(
            [
                [2.0, 0.0, int(source_columns.start) + int(source_origin_x)],
                [0.0, 2.0, int(source_rows.start) + int(source_origin_y)],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )
        reference_rows, reference_columns = _plane_slice(reference_frame, index)
        reference_plane_to_sensor = np.asarray(
            [[2.0, 0.0, int(reference_columns.start)], [0.0, 2.0, int(reference_rows.start)], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        full_plane = (
            np.linalg.inv(reference_plane_to_sensor)
            @ np.asarray(matrix, dtype=np.float32)
            @ source_to_sensor
        )
        local_output = np.asarray(
            [[1.0, 0.0, -float(out_x)], [0.0, 1.0, -float(out_y)], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        ) @ full_plane
        warped_plane = taichi_aot.warp_perspective(
            source_plane, local_output, (plane_w, plane_h), return_gpu=False
        )
        mask_plane = taichi_aot.warp_perspective(
            np.ones(source_plane.shape, dtype=np.float32),
            local_output,
            (plane_w, plane_h),
            return_gpu=False,
        )
        warped[output_rows, output_columns] = np.asarray(warped_plane, dtype=np.float32)
        valid[output_rows, output_columns] = np.asarray(mask_plane, dtype=np.float32) > 0.999
    return warped, valid


def _warp_cfa_homography(source: np.ndarray, frame, matrix: np.ndarray):
    """Warp R/G1/G2/B independently; never interpolate across CFA colours."""
    from taichi_vision import taichi_aot

    warped = np.zeros_like(source, dtype=np.float32)
    valid = np.zeros_like(source, dtype=np.float32)
    for index in range(4):
        rows, cols = _plane_slice(frame, index)
        plane = np.ascontiguousarray(source[rows, cols], dtype=np.float32)
        height, width = plane.shape
        matrix_plane = _plane_homography(matrix, frame, index)
        warped_plane = taichi_aot.warp_perspective(
            plane, matrix_plane, (width, height), return_gpu=False
        )
        mask_plane = taichi_aot.warp_perspective(
            np.ones((height, width), dtype=np.float32),
            matrix_plane,
            (width, height),
            return_gpu=False,
        )
        warped[rows, cols] = np.asarray(warped_plane, dtype=np.float32)
        valid[rows, cols] = np.asarray(mask_plane, dtype=np.float32) > 0.999
    return warped, valid


def _warp_cfa_flow(source: np.ndarray, frame, flow_work: np.ndarray):
    """Remap Bayer planes with one RGB-proxy flow field in sensor coordinates.

    ``remap_with_flow`` scales a work-grid displacement by output/flow size.
    Supplying each half-resolution plane therefore converts a full-sensor flow
    into the correct half-resolution CFA displacement without cross-colour
    interpolation.  The remaining half-pixel CFA phase is fixed by the common
    session contract and is handled by the plane split itself.
    """
    from taichi_vision import taichi_aot

    flow = np.ascontiguousarray(flow_work, dtype=np.float32)
    if flow.ndim != 3 or flow.shape[2] != 2:
        raise ValueError(f"dense flow must have shape (H, W, 2), got {flow.shape}")
    warped = np.zeros_like(source, dtype=np.float32)
    valid = np.zeros_like(source, dtype=np.float32)
    for index in range(4):
        rows, cols = _plane_slice(frame, index)
        plane = np.ascontiguousarray(source[rows, cols], dtype=np.float32)
        height, width = plane.shape
        warped_plane = taichi_aot.remap_with_flow(
            plane, flow, height, width, return_gpu=False
        )
        mask_plane = taichi_aot.remap_with_flow(
            np.ones((height, width), dtype=np.float32),
            flow, height, width, return_gpu=False
        )
        warped[rows, cols] = np.asarray(warped_plane, dtype=np.float32)
        valid[rows, cols] = np.asarray(mask_plane, dtype=np.float32) > 0.999
    return warped, valid


def _accumulate_cfa_flow_tiles(
    sums: np.ndarray,
    weights: np.ndarray,
    source: np.ndarray,
    frame,
    flow_gpu,
    *,
    block_size: int,
) -> int:
    """Remap one CFA source into global accumulators through output tiles.

    ``flow_gpu`` stays owned by the alignment estimator for the whole support
    frame.  Only the current CFA-plane output tile crosses back to host for
    the numerically established float32 accumulator.  This is deliberately
    separate from RGB Linear's blend graph because its samples must never be
    interpolated across CFA colours.
    """
    from taichi_vision import taichi_aot

    height, width = frame.shape
    sources = []
    masks = []
    try:
        for index in range(4):
            rows, columns = _plane_slice(frame, index)
            plane = np.ascontiguousarray(source[rows, columns], dtype=np.float32)
            sources.append(taichi_aot.upload(plane))
            masks.append(taichi_aot.upload(np.ones(plane.shape, dtype=np.float32)))

        block_count = 0
        for y0 in range(0, height, int(block_size)):
            y1 = min(height, y0 + int(block_size))
            for x0 in range(0, width, int(block_size)):
                x1 = min(width, x0 + int(block_size))
                tile_h, tile_w = y1 - y0, x1 - x0
                sum_tile = sums[y0:y1, x0:x1]
                weight_tile = weights[y0:y1, x0:x1]
                for index in range(4):
                    rows, columns, plane_h, plane_w, out_y, out_x = _tile_plane_selector(
                        frame, index, y0, x0, tile_h, tile_w
                    )
                    if plane_h == 0 or plane_w == 0:
                        continue
                    warped_gpu = valid_gpu = None
                    try:
                        warped_gpu = taichi_aot.remap_with_flow_tile(
                            sources[index],
                            flow_gpu,
                            int(sources[index].shape[0]),
                            int(sources[index].shape[1]),
                            out_y,
                            out_x,
                            plane_h,
                            plane_w,
                        )
                        valid_gpu = taichi_aot.remap_with_flow_tile(
                            masks[index],
                            flow_gpu,
                            int(masks[index].shape[0]),
                            int(masks[index].shape[1]),
                            out_y,
                            out_x,
                            plane_h,
                            plane_w,
                        )
                        warped = np.asarray(warped_gpu.to_numpy(), dtype=np.float32)
                        valid = (
                            np.asarray(valid_gpu.to_numpy(), dtype=np.float32) > 0.999
                        ) & np.isfinite(warped)
                        # ``NaN * 0`` remains NaN.  Accumulate only samples
                        # which are both mapped inside the source and finite.
                        sum_tile[rows, columns] += np.where(valid, warped, 0.0)
                        weight_tile[rows, columns] += valid
                    finally:
                        _release(warped_gpu)
                        _release(valid_gpu)
                block_count += 1
        return block_count
    finally:
        for buffer in sources:
            _release(buffer)
        for buffer in masks:
            _release(buffer)


def _accumulate_weighted_cfa_flow_tiles(
    sums: np.ndarray,
    weights: np.ndarray,
    source: np.ndarray,
    frame,
    flow_gpu,
    weight_rgb: np.ndarray,
    *,
    block_size: int,
) -> int:
    """Accumulate a WeightNet confidence map into matching CFA samples only.

    ``weight_rgb`` is analysis-only model output at sensor resolution.  Its
    R/G/B channels are selected by the source CFA tile (both green planes use
    G), while the source samples remain independent float32 Bayer planes.
    """
    from taichi_vision import taichi_aot

    full_weight = np.asarray(weight_rgb, dtype=np.float32)
    if full_weight.shape != (*frame.shape, 3):
        raise ValueError(
            "FusionNet RAW Native weight map must have shape "
            f"{(*frame.shape, 3)}, got {full_weight.shape}"
        )
    height, width = frame.shape
    sources = []
    masks = []
    try:
        for index in range(4):
            rows, columns = _plane_slice(frame, index)
            plane = np.ascontiguousarray(source[rows, columns], dtype=np.float32)
            sources.append(taichi_aot.upload(plane))
            masks.append(taichi_aot.upload(np.ones(plane.shape, dtype=np.float32)))
        block_count = 0
        for y0 in range(0, height, int(block_size)):
            y1 = min(height, y0 + int(block_size))
            for x0 in range(0, width, int(block_size)):
                x1 = min(width, x0 + int(block_size))
                tile_h, tile_w = y1 - y0, x1 - x0
                sum_tile = sums[y0:y1, x0:x1]
                weight_tile = weights[y0:y1, x0:x1]
                model_tile = full_weight[y0:y1, x0:x1]
                for index in range(4):
                    rows, columns, plane_h, plane_w, out_y, out_x = _tile_plane_selector(
                        frame, index, y0, x0, tile_h, tile_w
                    )
                    if plane_h == 0 or plane_w == 0:
                        continue
                    warped_gpu = valid_gpu = None
                    try:
                        warped_gpu = taichi_aot.remap_with_flow_tile(
                            sources[index], flow_gpu, int(sources[index].shape[0]),
                            int(sources[index].shape[1]), out_y, out_x, plane_h, plane_w,
                        )
                        valid_gpu = taichi_aot.remap_with_flow_tile(
                            masks[index], flow_gpu, int(masks[index].shape[0]),
                            int(masks[index].shape[1]), out_y, out_x, plane_h, plane_w,
                        )
                        warped = np.asarray(warped_gpu.to_numpy(), dtype=np.float32)
                        valid = (
                            np.asarray(valid_gpu.to_numpy(), dtype=np.float32) > 0.999
                        ) & np.isfinite(warped)
                        channel = int(frame.cfa_pattern[index])
                        confidence = np.clip(model_tile[rows, columns, channel], 0.0, 1.0)
                        contribution = np.where(valid, confidence, 0.0)
                        sum_tile[rows, columns] += np.where(valid, warped * confidence, 0.0)
                        weight_tile[rows, columns] += contribution
                    finally:
                        _release(warped_gpu)
                        _release(valid_gpu)
                block_count += 1
        return block_count
    finally:
        for buffer in sources:
            _release(buffer)
        for buffer in masks:
            _release(buffer)


def _accumulate_weighted_cfa_flow_resident(
    source: np.ndarray,
    frame,
    flow_gpu,
    weight_work_gpu,
    sum_gpu,
    weight_gpu,
) -> int:
    """Fuse one support directly into resident CFA sums.

    The four uploads are source Bayer lattices only.  Once uploaded, flow
    sampling, WeightNet channel selection, validity testing, warp, weighted
    accumulation, and normalization ownership remain in Taichi.  In
    particular, this path has no per-tile host download.
    """
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        remap_accumulate_cfa_weighted_taichi,
    )

    source_planes = []
    try:
        for index in range(4):
            rows, columns = _plane_slice(frame, index)
            source_planes.append(
                taichi_aot.upload(
                    np.ascontiguousarray(source[rows, columns], dtype=np.float32)
                )
            )
        remap_accumulate_cfa_weighted_taichi(
            source_planes,
            flow_gpu,
            weight_work_gpu,
            sum_gpu,
            weight_gpu,
            full_shape=frame.shape,
            cfa_pattern=frame.cfa_pattern,
            phase_origin=frame.phase_origin,
        )
        return len(source_planes)
    finally:
        for plane in source_planes:
            _release(plane)


def _analysis_proxy_numpy(session, index: int, *, work_scale: float):
    """Materialize only the aligned-stage RGB proxy at the GPU boundary."""
    from taichi_vision import taichi_aot

    proxy_gpu = session.analysis_proxy(index, work_scale=work_scale)
    try:
        proxy = np.ascontiguousarray(proxy_gpu.to_numpy(), dtype=np.float32)
    finally:
        _release(proxy_gpu)
    return proxy


def _weightnet_analysis_proxy(session, index: int, *, work_scale: float, params=None):
    """Build a disposable AutoEnhance RGB proxy for alignment and WeightNet."""
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        analyze_auto_enhance_params,
        apply_auto_enhance_np,
    )

    proxy = _analysis_proxy_numpy(session, index, work_scale=work_scale)
    if params is None:
        params = analyze_auto_enhance_params(proxy, mode="analysis")
    enhanced = apply_auto_enhance_np(proxy, params=params)
    return np.ascontiguousarray(enhanced, dtype=np.float32), params


def _legacy_weightnet_proxy_gpu(path, *, shape, params=None):
    """Build the commit-50e2e8a WeightNet analysis proxy on GPU.

    This path is intentionally isolated from alignment.  It reuses the
    established RGB resident loader/demosaic contract, then applies the
    analysis AutoEnhance parameters before the caller supplies the already
    estimated alignment flow.
    """
    from taichi_vision import taichi_aot
    from .rgb_linear_resident import load_frame_to_gpu, apply_auto_enhance_on_gpu

    source_gpu = load_frame_to_gpu(path, is_raw=True)
    try:
        target_h, target_w = int(shape[0]), int(shape[1])
        if tuple(int(v) for v in source_gpu.shape[:2]) != (target_h, target_w):
            resized = taichi_aot.resize(
                source_gpu,
                (target_w, target_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
            _release(source_gpu)
            source_gpu = resized
        if params is not None:
            enhanced = apply_auto_enhance_on_gpu(
                source_gpu, params
            )
            if enhanced is not source_gpu:
                _release(source_gpu)
            source_gpu = enhanced
        return source_gpu
    except Exception:
        _release(source_gpu)
        raise


def _run_weightnet_cfa_fusion_serial(
    raw_session: RawNativeSession,
    weightnet_session,
    *,
    alignment_plan: str,
    alignment_config=None,
    work_scale: float = 0.50,
    tile_size: int = 256,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 1.0,
    block_size=None,
    stop_event=None,
    progress_callback=None,
):
    """WeightNet RGB analysis with weighted CFA-float32 sensor fusion."""
    from taichi_vision import taichi_aot
    from .Average import create_raw_native_average_result
    from .fusionet_engine.flownet_inference import AOTOpticalFlowAligner
    from .fusionet_engine.weightnet_inference import infer_single_support_weight_map
    from .resident_alignment import resolve_fusionnet_alignment_plan
    from .rgb_linear_resident import BlockMatchingGPUResidentAligner

    plan = resolve_fusionnet_alignment_plan(alignment_plan)
    reference = raw_session.reference
    ref_analysis, analysis_params = _weightnet_analysis_proxy(
        raw_session, 0, work_scale=work_scale
    )
    ref_gpu = taichi_aot.upload(ref_analysis)
    # CFA FusionNet currently uses one resident dispatch per Bayer plane.
    # Region/block dispatch remains disabled until this fused path has parity
    # and throughput evidence on every backend.
    selected_block = None
    sums_gpu = taichi_aot.upload(raw_session.normalized(0))
    weights_gpu = taichi_aot.upload(
        np.ones(reference.shape, dtype=np.float32)
    )
    aligned_supports = 0
    block_count = 0
    aligner = None
    accumulation_complete = False
    try:
        if plan == "block matching gpu":
            aligner = BlockMatchingGPUResidentAligner(
                ref_gpu, full_shape=reference.shape, alignment_config=alignment_config
            )
        else:
            # compute_flow operates entirely on the RGB proxy. The same flow
            # is then consumed by CFA-plane remapping below.
            aligner = AOTOpticalFlowAligner(
                ref_gpu, work_scale=1.0, full_shape=ref_analysis.shape[:2]
            )
        total = max(1, raw_session.frame_count - 1)
        ref_chw = np.ascontiguousarray(np.transpose(ref_analysis, (2, 0, 1)), dtype=np.float32)
        for index in range(1, raw_session.frame_count):
            if stop_event is not None and (stop_event() if callable(stop_event) else stop_event.is_set()):
                raise RuntimeError("RAW Native FusionNet cancelled")
            supp_analysis, _ = _weightnet_analysis_proxy(
                raw_session, index, work_scale=work_scale, params=analysis_params
            )
            supp_gpu = taichi_aot.upload(supp_analysis)
            flow_gpu = aligned_gpu = weight_work_gpu = None
            try:
                if plan == "block matching gpu":
                    estimate = aligner.estimate_alignment(supp_gpu, stop_event=stop_event)
                    flow_gpu = estimate.flow_gpu
                    estimate.flow_gpu = None
                    aligned_gpu = taichi_aot.remap_with_flow(
                        supp_gpu, flow_gpu, ref_analysis.shape[0], ref_analysis.shape[1], return_gpu=True
                    )
                    estimate.release()
                else:
                    aligned_gpu = aligner.align_frame(
                        supp_gpu, stop_event=stop_event, return_gpu=True, keep_flow=True
                    )
                    flow_gpu = aligner.take_last_flow()
                supp_aligned = np.ascontiguousarray(aligned_gpu.to_numpy(), dtype=np.float32)
                weight_work, _alpha = infer_single_support_weight_map(
                    weightnet_session, ref_chw,
                    np.ascontiguousarray(np.transpose(supp_aligned, (2, 0, 1)), dtype=np.float32),
                    tile_size=tile_size, overlap=overlap, ghost_penalty=ghost_penalty,
                    ghost_cutoff=ghost_cutoff, chroma_sensitivity=chroma_sensitivity,
                    stop_event=stop_event,
                )
                weight_hwc = np.ascontiguousarray(np.transpose(weight_work, (1, 2, 0)), dtype=np.float32)
                weight_work_gpu = taichi_aot.upload(weight_hwc)
                block_count += _accumulate_weighted_cfa_flow_resident(
                    raw_session.normalized(index),
                    reference,
                    flow_gpu,
                    weight_work_gpu,
                    sums_gpu,
                    weights_gpu,
                )
                aligned_supports += 1
            finally:
                _release(weight_work_gpu)
                _release(flow_gpu)
                _release(aligned_gpu)
                _release(supp_gpu)
            if progress_callback:
                progress_callback(
                    5 + int(78 * index / total),
                    f"Fusion RAW native {index}/{total}: alignment dan confidence...",
                )
        accumulation_complete = True
    finally:
        if aligner is not None:
            aligner.close()
        _release(ref_gpu)
        if not accumulation_complete:
            _release(sums_gpu)
            _release(weights_gpu)
    try:
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            normalize_accumulator_cfa_taichi,
        )

        normalize_accumulator_cfa_taichi(sums_gpu, weights_gpu)
        fused_cfa = np.ascontiguousarray(sums_gpu.to_numpy(), dtype=np.float32)
    finally:
        _release(sums_gpu)
        _release(weights_gpu)
    report = RawNativeAlignmentReport(
        alignment_plan=plan, frames=raw_session.frame_count,
        aligned_supports=aligned_supports, identity_supports=0,
        block_size=selected_block, block_count=block_count,
    )
    return create_raw_native_average_result(
        fused_cfa, reference, raw_session.paths,
        report=report, progress_callback=progress_callback,
    )


def _run_weightnet_cfa_fusion(
    raw_session: RawNativeSession,
    weightnet_session,
    **kwargs,
):
    """Run RAW FusionNet through the bounded resident coordinator.

    The ONNX boundary still requires a NumPy work-resolution proxy, but that
    boundary is overlapped with alignment of the next support frame.  Only
    one aligned packet and one weighted packet are retained, matching the
    proven RGB resident contract: ``in_flight=1`` without unbounded VRAM use.
    """
    from taichi_vision import taichi_aot
    from .Average import create_raw_native_average_result
    from .fusionet_engine.flownet_inference import AOTOpticalFlowAligner
    from .fusionet_engine.weightnet_inference import infer_single_support_weight_map
    from .resident_alignment import resolve_fusionnet_alignment_plan
    from .rgb_linear_resident import BlockMatchingGPUResidentAligner
    from taichi_vision.taichi_algorithm.spatial_fusion import normalize_accumulator_cfa_taichi

    alignment_plan = kwargs.get("alignment_plan", "optical_flow")
    alignment_config = kwargs.get("alignment_config")
    work_scale = float(kwargs.get("work_scale", 0.50))
    tile_size = int(kwargs.get("tile_size", 256))
    overlap = float(kwargs.get("overlap", 0.30))
    ghost_penalty = float(kwargs.get("ghost_penalty", 1.0))
    ghost_cutoff = float(kwargs.get("ghost_cutoff", 0.05))
    chroma_sensitivity = float(kwargs.get("chroma_sensitivity", 1.0))
    stop_event = kwargs.get("stop_event")
    progress_callback = kwargs.get("progress_callback")
    plan = resolve_fusionnet_alignment_plan(alignment_plan)
    reference = raw_session.reference
    ref_analysis, analysis_params = _weightnet_analysis_proxy(
        raw_session, 0, work_scale=work_scale
    )
    ref_chw = np.ascontiguousarray(
        np.transpose(ref_analysis, (2, 0, 1)), dtype=np.float32
    )
    ref_gpu = taichi_aot.upload(ref_analysis)
    # Keep alignment on the existing proxy.  WeightNet receives a separate
    # proxy built with the metadata-aware RGB resident loader used by the
    # 50e2e8a pipeline, so this experiment does not alter flow estimation.
    from .rgb_linear_resident import analyze_auto_enhance_on_gpu, apply_auto_enhance_on_gpu
    legacy_ref_base_gpu = _legacy_weightnet_proxy_gpu(
        raw_session.paths[0], shape=ref_analysis.shape[:2]
    )
    try:
        legacy_analysis_params = analyze_auto_enhance_on_gpu(
            legacy_ref_base_gpu, mode="natural"
        )
        legacy_ref_gpu = apply_auto_enhance_on_gpu(
            legacy_ref_base_gpu, legacy_analysis_params
        )
        if legacy_ref_gpu is not legacy_ref_base_gpu:
            _release(legacy_ref_base_gpu)
        legacy_ref_base_gpu = None
        legacy_ref_chw = np.ascontiguousarray(
            np.transpose(legacy_ref_gpu.to_numpy(), (2, 0, 1)), dtype=np.float32
        )
    finally:
        _release(legacy_ref_base_gpu)
        _release(locals().get("legacy_ref_gpu"))
    sums_gpu = taichi_aot.upload(raw_session.normalized(0))
    weights_gpu = taichi_aot.upload(np.ones(reference.shape, dtype=np.float32))
    aligner = None
    state_lock = threading.Lock()
    stop_requested = threading.Event()
    failure = []
    sentinel = object()
    preloaded_queue = queue.Queue(maxsize=3)
    aligned_queue = queue.Queue(maxsize=1)
    weighted_queue = queue.Queue(maxsize=1)
    gpu_lock = threading.Lock()

    def stopped():
        if stop_requested.is_set():
            return True
        if stop_event is None:
            return False
        return bool(stop_event() if callable(stop_event) else stop_event.is_set())

    def fail(exc):
        with state_lock:
            if not failure:
                failure.append(exc)
        stop_requested.set()

    def put_until(q, item):
        while not stopped():
            try:
                q.put(item, timeout=0.05)
                return True
            except queue.Full:
                continue
        return False

    def preloader_worker():
        try:
            for index in range(1, raw_session.frame_count):
                if not put_until(preloaded_queue, index):
                    return
            # The producer owns the input sentinel.  Downstream stages emit
            # their own sentinel after draining their input queue.
            while not stopped():
                try:
                    preloaded_queue.put(sentinel, timeout=0.05)
                    return
                except queue.Full:
                    continue
        except Exception as exc:
            fail(exc)

    def alignment_worker():
        local_aligner = None
        try:
            try:
                taichi_aot.ensure_cuda_context()
            except Exception:
                pass
            with gpu_lock:
                if plan == "block matching gpu":
                    local_aligner = BlockMatchingGPUResidentAligner(
                        ref_gpu, full_shape=reference.shape,
                        alignment_config=alignment_config,
                    )
                else:
                    local_aligner = AOTOpticalFlowAligner(
                        ref_gpu, work_scale=1.0,
                        full_shape=ref_analysis.shape[:2],
                    )
            while not stopped():
                try:
                    index = preloaded_queue.get(timeout=0.05)
                except queue.Empty:
                    continue
                if index is sentinel:
                    break
                # Serialize only the Taichi proxy/readback. The CPU
                # AutoEnhance work remains outside the lock so ONNX and the
                # next GPU alignment can overlap it.
                with gpu_lock:
                    proxy = _analysis_proxy_numpy(
                        raw_session, index, work_scale=work_scale
                    )
                from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
                    apply_auto_enhance_np,
                )
                supp_analysis = np.ascontiguousarray(
                    apply_auto_enhance_np(proxy, params=analysis_params),
                    dtype=np.float32,
                )
                supp_gpu = flow_gpu = aligned_gpu = None
                onnx_aligned_gpu = None
                try:
                    supp_gpu = taichi_aot.upload(supp_analysis)
                    with gpu_lock:
                        if plan == "block matching gpu":
                            estimate = local_aligner.estimate_alignment(
                                supp_gpu, stop_event=stop_event
                            )
                            flow_gpu = estimate.flow_gpu
                            estimate.flow_gpu = None
                            aligned_gpu = taichi_aot.remap_with_flow(
                                supp_gpu, flow_gpu,
                                ref_analysis.shape[0], ref_analysis.shape[1],
                                return_gpu=True,
                            )
                            estimate.release()
                        else:
                            aligned_gpu = local_aligner.align_frame(
                                supp_gpu, stop_event=stop_event,
                                return_gpu=True, keep_flow=True,
                            )
                            flow_gpu = local_aligner.take_last_flow()
                    # Rebuild only the WeightNet input with the legacy
                    # metadata-aware demosaic/preprocessing path. The flow
                    # itself remains the one estimated above.
                    with gpu_lock:
                        legacy_support_gpu = _legacy_weightnet_proxy_gpu(
                            raw_session.paths[index],
                            shape=ref_analysis.shape[:2],
                            params=legacy_analysis_params,
                        )
                        try:
                            onnx_aligned_gpu = taichi_aot.remap_with_flow(
                                legacy_support_gpu, flow_gpu,
                                ref_analysis.shape[0], ref_analysis.shape[1],
                                return_gpu=True,
                            )
                        finally:
                            _release(legacy_support_gpu)
                    _release(aligned_gpu)
                    aligned_gpu = None
                    _release(supp_gpu)
                    supp_gpu = None
                    if not put_until(aligned_queue, (index, flow_gpu, onnx_aligned_gpu)):
                        _release(flow_gpu)
                        _release(onnx_aligned_gpu)
                        break
                    flow_gpu = onnx_aligned_gpu = None
                finally:
                    _release(flow_gpu)
                    _release(aligned_gpu)
                    _release(supp_gpu)
                    _release(onnx_aligned_gpu)
        except Exception as exc:
            fail(exc)
        finally:
            if local_aligner is not None:
                try:
                    local_aligner.close()
                except Exception:
                    pass
            put_until(aligned_queue, sentinel)

    def weight_worker():
        try:
            try:
                taichi_aot.ensure_cuda_context()
            except Exception:
                pass
            while not stopped():
                try:
                    packet = aligned_queue.get(timeout=0.05)
                except queue.Empty:
                    continue
                if packet is sentinel:
                    break
                index, flow_gpu, onnx_aligned_gpu = packet
                weight_gpu = None
                try:
                    # This is the ONNX boundary. It is intentionally outside
                    # gpu_lock so the alignment worker can prepare the next
                    # frame while WeightNet is running.
                    with gpu_lock:
                        supp_aligned = np.ascontiguousarray(
                            onnx_aligned_gpu.to_numpy(), dtype=np.float32
                        )
                    weight_work, _alpha = infer_single_support_weight_map(
                        weightnet_session, legacy_ref_chw,
                        np.ascontiguousarray(
                            np.transpose(supp_aligned, (2, 0, 1)), dtype=np.float32
                        ),
                        tile_size=tile_size, overlap=overlap,
                        ghost_penalty=ghost_penalty,
                        ghost_cutoff=ghost_cutoff,
                        chroma_sensitivity=chroma_sensitivity,
                        stop_event=stop_event,
                    )
                    weight_hwc = np.ascontiguousarray(
                        np.transpose(weight_work, (1, 2, 0)), dtype=np.float32
                    )
                    with gpu_lock:
                        weight_gpu = taichi_aot.upload(weight_hwc)
                    if not put_until(weighted_queue, (index, flow_gpu, weight_gpu)):
                        _release(flow_gpu)
                        _release(weight_gpu)
                        break
                    flow_gpu = weight_gpu = None
                finally:
                    _release(weight_gpu)
                    _release(flow_gpu)
                    _release(onnx_aligned_gpu)
        except Exception as exc:
            fail(exc)
        finally:
            put_until(weighted_queue, sentinel)

    preload_thread = threading.Thread(
        target=preloader_worker, name="RAW_Preloader", daemon=True
    )
    align_thread = threading.Thread(target=alignment_worker, name="RAW_Alignment", daemon=True)
    weight_thread = threading.Thread(target=weight_worker, name="RAW_WeightNet", daemon=True)
    preload_thread.start()
    align_thread.start()
    weight_thread.start()
    aligned_supports = 0
    try:
        total = max(1, raw_session.frame_count - 1)
        while not stopped():
            try:
                packet = weighted_queue.get(timeout=0.05)
            except queue.Empty:
                if not align_thread.is_alive() and not weight_thread.is_alive():
                    break
                continue
            if packet is sentinel:
                break
            index, flow_gpu, weight_gpu = packet
            try:
                source = raw_session.normalized(index)
                with gpu_lock:
                    _accumulate_weighted_cfa_flow_resident(
                        source, reference, flow_gpu, weight_gpu,
                        sums_gpu, weights_gpu,
                    )
                aligned_supports += 1
                if progress_callback:
                    progress_callback(
                        5 + int(78 * index / total),
                        f"Fusion RAW native {index}/{total}: pipeline in-flight=1...",
                    )
            finally:
                _release(weight_gpu)
                _release(flow_gpu)
        align_thread.join(timeout=2.0)
        weight_thread.join(timeout=2.0)
        if failure:
            raise failure[0]
        with gpu_lock:
            normalize_accumulator_cfa_taichi(sums_gpu, weights_gpu)
            fused_cfa = np.ascontiguousarray(sums_gpu.to_numpy(), dtype=np.float32)
    finally:
        stop_requested.set()
        preload_thread.join(timeout=2.0)
        align_thread.join(timeout=2.0)
        weight_thread.join(timeout=2.0)
        _release(ref_gpu)
        _release(sums_gpu)
        _release(weights_gpu)

    report = RawNativeAlignmentReport(
        alignment_plan=str(alignment_plan), frames=raw_session.frame_count,
        aligned_supports=aligned_supports, identity_supports=0,
        block_size=None, block_count=aligned_supports * 4,
    )
    return create_raw_native_average_result(
        fused_cfa, reference, raw_session.paths,
        report=report, progress_callback=progress_callback,
    )


def _run_feature_aligned_average(
    session: RawNativeSession,
    *,
    alignment_plan: str,
    alignment_config=None,
    work_scale: float = 0.50,
    block_size=None,
    stop_event=None,
    progress_callback=None,
):
    """Estimate once, then fuse RAW CFA tiles without full-frame accumulators."""
    from .Average import create_raw_native_average_result
    from .Average import _raw_native_block_size
    from .rgb_linear_resident import FeatureMatchingGPUAligner

    reference = session.reference
    ref_proxy = session.analysis_proxy(0, work_scale=work_scale)
    aligner = None
    aligned_supports = 0
    identity_supports = 0
    estimates = []
    try:
        plan = str(alignment_plan or "").strip().casefold()
        feature = "akaze" if plan == "akaze" else "ofb"
        aligner = FeatureMatchingGPUAligner(
            ref_proxy,
            feature_type=feature,
            work_scale=float(work_scale),
            full_shape=reference.shape,
            feature_config=alignment_config,
        )
        total_supports = max(1, session.frame_count - 1)
        for index in range(1, session.frame_count):
            if stop_event is not None:
                cancelled = stop_event() if callable(stop_event) else stop_event.is_set()
                if cancelled:
                    raise RuntimeError("RAW Native alignment cancelled")
            proxy = session.analysis_proxy(index, work_scale=work_scale)
            try:
                estimate = aligner.estimate_alignment(proxy, stop_event=stop_event)
            finally:
                _release(proxy)
            if estimate is None:
                # Preserve RGB Linear's established feature-match behaviour:
                # failed geometry falls back to the unwarped support, never to
                # an unrelated alignment implementation.
                estimates.append((index, None))
                identity_supports += 1
            else:
                estimates.append((index, estimate.homography))
                aligned_supports += 1
            if progress_callback:
                progress_callback(
                    5 + int(38 * index / total_supports),
                    f"Mengestimasi alignment RAW native {index}/{total_supports}...",
                )
    finally:
        if aligner is not None:
            aligner.close()
        _release(ref_proxy)

    selected_block = _raw_native_block_size(block_size)
    height, width = reference.shape
    normalized = np.empty(reference.shape, dtype=np.float32)
    block_count = 0
    total_blocks = max(1, ((height + selected_block - 1) // selected_block) * ((width + selected_block - 1) // selected_block))
    for y0 in range(0, height, selected_block):
        y1 = min(height, y0 + selected_block)
        for x0 in range(0, width, selected_block):
            x1 = min(width, x0 + selected_block)
            sums = reference.normalized_headroom_region(
                y0, y1, x0, x1, apply_white_balance=False
            )
            weights = np.ones((y1 - y0, x1 - x0), dtype=np.float32)
            for index, matrix in estimates:
                if matrix is None:
                    sums += session.normalized_region(index, y0, y1, x0, x1)
                    weights += 1.0
                    continue
                try:
                    sy0, sy1, sx0, sx1 = _homography_source_roi(
                        matrix, y0, y1, x0, x1, reference.shape
                    )
                except ValueError:
                    # A valid global projective transform can map an outer
                    # output tile entirely outside the support sensor.  That
                    # tile has no support contribution; preserve the
                    # reference rather than aborting the whole RAW burst or
                    # clamping unrelated edge pixels into its CFA planes.
                    continue
                source_region = session.region(index, sy0, sy1, sx0, sx1)
                warped, valid = _warp_cfa_homography_tile(
                    source_region, reference, matrix, y0, y1, x0, x1
                )
                finite_valid = np.asarray(valid, dtype=bool) & np.isfinite(warped)
                # Do not let a projective denominator singularity poison a
                # complete output block through ``NaN * False``.
                sums += np.where(finite_valid, warped, 0.0)
                weights += finite_valid
            normalized[y0:y1, x0:x1] = sums / np.maximum(weights, 1e-6)
            block_count += 1
            if progress_callback:
                progress_callback(
                    43 + int(42 * block_count / total_blocks),
                    f"Menggabungkan RAW native per blok {block_count}/{total_blocks}...",
                )
    report = RawNativeAlignmentReport(
        alignment_plan=str(alignment_plan),
        frames=session.frame_count,
        aligned_supports=aligned_supports,
        identity_supports=identity_supports,
        block_size=selected_block,
        block_count=block_count,
    )
    return create_raw_native_average_result(
        normalized,
        reference,
        session.paths,
        report=report,
        progress_callback=progress_callback,
    )


def _run_dense_flow_aligned_average(
    session: RawNativeSession,
    *,
    alignment_plan: str,
    alignment_config=None,
    work_scale: float = 0.50,
    block_size=None,
    stop_event=None,
    progress_callback=None,
):
    """Reuse dense RGB flow and apply it only to raw float32 CFA planes."""
    from .Average import create_raw_native_average_result
    from .rgb_linear_resident import (
        BlockMatchingGPUResidentAligner,
        TaichiDenseFlowResidentAligner,
    )

    reference = session.reference
    from .Average import _raw_native_block_size

    reference_native = session.normalized(0)
    sums = reference_native.copy()
    weights = np.ones_like(reference_native, dtype=np.float32)
    ref_proxy = session.analysis_proxy(0, work_scale=work_scale)
    aligner = None
    aligned_supports = 0
    selected_block = _raw_native_block_size(block_size)
    block_count = 0
    try:
        plan = str(alignment_plan or "").strip().casefold()
        if "block matching" in plan:
            aligner = BlockMatchingGPUResidentAligner(
                ref_proxy,
                full_shape=reference.shape,
                alignment_config=alignment_config,
            )
        else:
            flow_type = "farneback" if "farneback" in plan else "lucas_kanade"
            aligner = TaichiDenseFlowResidentAligner(
                ref_proxy,
                flow_type=flow_type,
                full_shape=reference.shape,
                alignment_config=alignment_config,
            )
        total_supports = max(1, session.frame_count - 1)
        for index in range(1, session.frame_count):
            proxy = session.analysis_proxy(index, work_scale=work_scale)
            estimate = None
            try:
                estimate = aligner.estimate_alignment(proxy, stop_event=stop_event)
                block_count = _accumulate_cfa_flow_tiles(
                    sums,
                    weights,
                    session.normalized(index),
                    reference,
                    estimate.flow_gpu,
                    block_size=selected_block,
                )
            finally:
                if estimate is not None:
                    estimate.release()
                _release(proxy)
            aligned_supports += 1
            if progress_callback:
                progress_callback(
                    5 + int(78 * index / total_supports),
                    f"Menyelaraskan RAW native {index}/{total_supports}...",
                )
    finally:
        if aligner is not None:
            aligner.close()
        _release(ref_proxy)

    report = RawNativeAlignmentReport(
        alignment_plan=str(alignment_plan),
        frames=session.frame_count,
        aligned_supports=aligned_supports,
        identity_supports=0,
        block_size=selected_block,
        block_count=block_count,
    )
    return create_raw_native_average_result(
        sums / np.maximum(weights, 1e-6),
        reference,
        session.paths,
        report=report,
        progress_callback=progress_callback,
    )


class RawNativeResidentProcessor:
    """Run the shared CFA pipeline and select its final output representation."""

    process_format = "RAW Native"
    _FEATURE_PLANS = {"ofb", "orb", "akaze", "feature matching"}
    _DENSE_FLOW_PLANS = {
        "farneback",
        "farneback optical flow",
        "lucas kanade",
        "lucas kanade optical flow",
        "lucas kanade gpu optical flow",
        "block matching gpu",
        "block matching gpu optical flow",
        "block matching",
    }
    _NO_ALIGNMENT = {"no alignment", "none", "off", ""}

    def __init__(self, output_format: str = "RAW Native"):
        normalized = str(output_format or "RAW Native").strip().casefold()
        if normalized not in {"raw native", "rgb linear"}:
            raise ValueError(f"Unsupported CFA output format: {output_format!r}")
        self.output_format = "RAW Native" if normalized == "raw native" else "RGB Linear"

    def _result_for_output(self, result):
        """Keep one CFA computation while recording its requested final form."""
        return replace(result, output_format=self.output_format)

    def run(self, image_paths, session=None, **kwargs):
        weight_engine = str(kwargs.get("weight_engine", "")).casefold()
        alignment = str(kwargs.get("alignment_plan", "No Alignment")).casefold()
        if weight_engine == "fusionet":
            if session is None:
                raise RawNativePipelineNotReadyError(
                    "RAW Native FusionNet requires an initialized WeightNet ONNX session."
                )
            from .resident_alignment import resolve_fusionnet_alignment_plan

            raw_session = RawNativeSession.load(image_paths)
            result = _run_weightnet_cfa_fusion(
                raw_session,
                session,
                alignment_plan=resolve_fusionnet_alignment_plan(alignment),
                alignment_config=kwargs.get("alignment_config"),
                work_scale=float(kwargs.get("work_scale", 0.50)),
                tile_size=int(kwargs.get("tile_size", 256)),
                overlap=float(kwargs.get("overlap", 0.30)),
                ghost_penalty=float(kwargs.get("ghost_penalty", 1.0)),
                ghost_cutoff=float(kwargs.get("ghost_cutoff", 0.05)),
                chroma_sensitivity=float(kwargs.get("chroma_sensitivity", 1.0)),
                block_size=kwargs.get("accumulation_block_size"),
                stop_event=kwargs.get("stop_event"),
                progress_callback=kwargs.get("progress_callback"),
            )
            return self._result_for_output(result), 1.0
        if weight_engine != "average":
            raise RawNativePipelineNotReadyError(
                "RAW Native supports Average and FusionNet CFA fusion only."
            )
        if alignment in self._NO_ALIGNMENT:
            from .Average import run_raw_native_average

            result = run_raw_native_average(
                image_paths,
                block_size=kwargs.get("accumulation_block_size"),
                stop_event=kwargs.get("stop_event"),
                progress_callback=kwargs.get("progress_callback"),
            )
            return self._result_for_output(result), 1.0
        if alignment in self._DENSE_FLOW_PLANS:
            session = RawNativeSession.load(image_paths)
            result = _run_dense_flow_aligned_average(
                session,
                alignment_plan=alignment,
                alignment_config=kwargs.get("alignment_config"),
                work_scale=float(kwargs.get("work_scale", 0.50)),
                block_size=kwargs.get("accumulation_block_size"),
                stop_event=kwargs.get("stop_event"),
                progress_callback=kwargs.get("progress_callback"),
            )
            return self._result_for_output(result), 1.0
        if alignment not in self._FEATURE_PLANS:
            raise RawNativePipelineNotReadyError(
                "RAW Native alignment supports OFB/ORB, AKAZE, Farneback, "
                "Lucas-Kanade, and Block Matching. Select RGB Linear for RAFT."
            )
        session = RawNativeSession.load(image_paths)
        result = _run_feature_aligned_average(
            session,
            alignment_plan=alignment,
            alignment_config=kwargs.get("alignment_config"),
            work_scale=float(kwargs.get("work_scale", 0.50)),
            block_size=kwargs.get("accumulation_block_size"),
            stop_event=kwargs.get("stop_event"),
            progress_callback=kwargs.get("progress_callback"),
        )
        return self._result_for_output(result), 1.0
