"""
Average denoising adapter (GPU-Resident & CPU Parity).

Matches SpatialFusion and FusioNet pipeline architecture:
- Routes to GPU-resident pipeline (taichi_aot Vulkan) for zero-copy streaming
- Guarantees 100% RGB output in uint16/uint8 format
- Output saved with AutoEnhance v2 tonemapping via save_image
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ._common_helpers import active_backend, restore_output_dtype
from .raw_metadata import extract_demosaic_parameters, extract_source_dng_metadata


def _apply_baked_orientation(image: np.ndarray, orientation: int) -> np.ndarray:
    """Match the RGB Linear orientation transform for a Bayer mosaic."""
    if orientation == 2:
        return np.fliplr(image)
    if orientation == 3:
        return np.rot90(image, 2)
    if orientation == 4:
        return np.flipud(image)
    if orientation == 5:
        return np.rot90(np.fliplr(image), -1)
    if orientation == 6:
        return np.rot90(image, -1)
    if orientation == 7:
        return np.rot90(np.fliplr(image), 1)
    if orientation == 8:
        return np.rot90(image, 1)
    return image


def _baked_cfa_pattern(frame) -> tuple[int, int, int, int]:
    """Return the output CFA tile after applying TIFF orientation to samples."""
    height, width = frame.shape

    def source_coordinate(row: int, column: int) -> tuple[int, int]:
        orientation = int(frame.orientation)
        if orientation == 2:
            return row, width - 1 - column
        if orientation == 3:
            return height - 1 - row, width - 1 - column
        if orientation == 4:
            return height - 1 - row, column
        if orientation == 5:
            return height - 1 - column, width - 1 - row
        if orientation == 6:
            return height - 1 - column, row
        if orientation == 7:
            return column, row
        if orientation == 8:
            return column, width - 1 - row
        return row, column

    return tuple(
        int(frame.cfa_pattern[frame.phase_index(*source_coordinate(row, column))])
        for row, column in ((0, 0), (0, 1), (1, 0), (1, 1))
    )


@dataclass(frozen=True)
class RawNativeAverageResult:
    """One CFA fusion with one final RGB-linear materialization.

    ``normalized_mosaic`` is the sole sensor-domain result.  ``linear_rgb``
    is demosaiced exactly once from its baked-orientation mosaic; the UI
    preview is only an AutoEnhance view derived from that linear RGB data.
    """

    preview_rgb: np.ndarray
    normalized_mosaic: np.ndarray
    reference_frame: object
    source_paths: tuple[str, ...]
    report: object
    linear_rgb: np.ndarray | None = None
    output_format: str = "RAW Native"

    def _quantized_mosaic(self) -> np.ndarray:
        """Encode normalized CFA values in a derived full-range RAW space.

        The maintained native DNG writer has one BlackLevel/WhiteLevel pair.
        Source cameras may have four distinct CFA calibration pairs, so
        preserving source codes would make the derived DNG ambiguous.  Store
        the already calibrated average with black=0 and white=max-code instead.
        """
        frame = self.reference_frame
        maximum_code = (1 << int(frame.bits_per_sample)) - 1
        output = np.empty(frame.shape, dtype=frame.samples.dtype)
        normalized = np.asarray(self.normalized_mosaic, dtype=np.float32)
        if not np.isfinite(normalized).all():
            raise ValueError(
                "RAW Native fusion produced non-finite sensor samples; "
                "refusing to encode a corrupted derived DNG."
            )
        values = normalized / np.float32(frame.exposure_scale)
        output[...] = np.clip(
            np.rint(values * np.float32(maximum_code)), 0, maximum_code
        ).astype(output.dtype)
        return output

    def baked_oriented_mosaic(self) -> tuple[np.ndarray, tuple[int, int, int, int]]:
        """Bake the source orientation into pixels and the matching CFA tile."""
        mosaic = _apply_baked_orientation(
            self._quantized_mosaic(), int(self.reference_frame.orientation)
        )
        return np.ascontiguousarray(mosaic), _baked_cfa_pattern(self.reference_frame)

    def save_dng(self, path: str | Path) -> str:
        """Persist a derived mosaiced DNG; no RGB preview data is written."""
        from taichi_vision.taichi_algorithm.compression import save_dng_aot

        frame = self.reference_frame
        mosaic, cfa_pattern = self.baked_oriented_mosaic()
        source_path = frame.source_id or (self.source_paths[0] if self.source_paths else "")
        metadata = {
            # Pixels are already oriented, so the derived DNG is always
            # Orientation=1 by construction.  Its CFA tile must be transformed
            # with the same operation or a later demosaic would swap colours.
            "cfa_pattern": cfa_pattern,
            "orientation": 1,
            "black_level": 0,
            "white_level": (1 << int(frame.bits_per_sample)) - 1,
            "rows_per_strip": min(256, int(frame.height)),
        }
        metadata.update(
            extract_source_dng_metadata(
                frame, mosaic.shape, source_path=source_path
            )
        )
        target = Path(path)
        save_dng_aot(
            mosaic,
            target,
            metadata=metadata,
            # The native PackBits writer is not yet reliable for every
            # multi-strip CFA payload.  Uncompressed TIFF/DNG is still
            # lossless and has an exact native read-back contract.
            compression="none",
            bits_per_sample=int(frame.bits_per_sample),
        )
        return str(target)

    def save_linear_tiff(self, path: str | Path) -> str:
        """Persist the one-demosaic RGB-linear result without display tuning."""
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            save_image,
        )

        rgb = self.linear_rgb if self.linear_rgb is not None else self.preview_rgb
        encoded = np.clip(np.asarray(rgb, dtype=np.float32), 0.0, 1.0)
        encoded = np.rint(encoded * 65535.0).astype(np.uint16)
        # Pixels are already baked into their final orientation.  Passing no
        # reference prevents the generic TIFF helper from rotating them again.
        if not save_image(encoded, str(path), reference_image_path=None):
            raise OSError(f"Failed to save RGB Linear TIFF: {path}")
        # Copy the complete source metadata after writing.  The copy happens
        # after pixels are already baked, so the metadata tool must normalize
        # Orientation without triggering another pixel rotation.
        source_path = self.reference_frame.source_id or (
            self.source_paths[0] if self.source_paths else ""
        )
        if source_path:
            try:
                from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                    _copy_output_metadata,
                )

                _copy_output_metadata(source_path, str(path))
            except Exception as exc:
                # Metadata preservation is best-effort for installations that
                # do not ship the optional metadata copier.
                print(f"[Average] TIFF metadata preservation warning: {exc}")
        return str(path)


def _raw_native_block_size(value) -> int:
    if value is not None:
        return max(32, int(value))
    try:
        from config import get_compute_block_settings

        return max(32, int(get_compute_block_settings().get("block_size", 1024)))
    except Exception:
        return 1024


def create_raw_native_average_result(
    normalized_mosaic: np.ndarray,
    reference_frame,
    source_paths,
    *,
    report=None,
    progress_callback=None,
) -> RawNativeAverageResult:
    """Materialize one fused sensor mosaic only after RAW processing ends.

    The display preview is intentionally a separate, final-only product.  It
    may be demosaiced and naturally tone-mapped for the application, while
    ``normalized_mosaic`` remains the untouched, linear sensor result used by
    :meth:`RawNativeAverageResult.save_dng`.
    """
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        analyze_auto_enhance_params,
        apply_auto_enhance_np,
    )

    result = RawNativeAverageResult(
        preview_rgb=np.empty((0, 0, 3), dtype=np.float32),
        normalized_mosaic=np.ascontiguousarray(normalized_mosaic, dtype=np.float32),
        reference_frame=reference_frame,
        source_paths=tuple(source_paths),
        report=report,
    )
    # Orientation is intentionally baked once, after all sensor-native warp
    # and accumulation have completed.
    preview_mosaic, preview_cfa = result.baked_oriented_mosaic()
    if progress_callback:
        progress_callback(88, "Membuat pratinjau RGB dari RAW hasil fusion...")
    try:
        demosaic_params = extract_demosaic_parameters(
            result.source_paths[0], cfa_pattern=preview_cfa
        )
    except Exception:
        # Synthetic/headless callers may not have a readable source file.
        # Real DNG outputs use the camera contract above; this fallback keeps
        # the existing in-memory API usable without inventing metadata.
        demosaic_params = {
            "wb_r": 1.0,
            "wb_g1": 1.0,
            "wb_b": 1.0,
            "wb_g2": 1.0,
            "cmatrix": np.eye(3, dtype=np.float32),
            "black_level": 0.0,
            "white_level": float((1 << int(reference_frame.bits_per_sample)) - 1),
            "c00": int(preview_cfa[0]),
            "c01": int(preview_cfa[1]),
            "c10": int(preview_cfa[2]),
            "c11": int(preview_cfa[3]),
        }
    linear_rgb = taichi_aot.demosaic(
        preview_mosaic.astype(np.float32, copy=False),
        method="hamilton",
        return_gpu=False,
        **demosaic_params,
    )
    # Natural AutoEnhance is display-only.  Do not feed this RGB result back
    # into the RAW Native accumulator or DNG writer: the persisted file must
    # remain a linear, mosaiced sensor-domain fusion.
    linear_rgb = np.ascontiguousarray(linear_rgb, dtype=np.float32)
    preview = apply_auto_enhance_np(
        linear_rgb,
        params=analyze_auto_enhance_params(linear_rgb, mode="natural"),
    )
    if progress_callback:
        progress_callback(92, "Pratinjau RAW native siap.")
    return RawNativeAverageResult(
        preview_rgb=np.ascontiguousarray(preview, dtype=np.float32),
        normalized_mosaic=result.normalized_mosaic,
        reference_frame=reference_frame,
        source_paths=tuple(source_paths),
        report=report,
        linear_rgb=linear_rgb,
    )


def run_raw_native_average(
    image_paths,
    *,
    block_size=None,
    stop_event=None,
    progress_callback=None,
) -> RawNativeAverageResult:
    """Average compatible DNG mosaics before one display-only demosaic."""
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.compression import (
        RawMosaicFrame,
        fuse_dng_frames_blockwise,
        read_dng_aot,
    )

    paths = tuple(str(Path(path)) for path in image_paths)
    if len(paths) < 2:
        raise ValueError("RAW Native Average requires at least two DNG frames")
    if any(Path(path).suffix.lower() != ".dng" for path in paths):
        raise ValueError("RAW Native Average currently supports DNG input only")
    if stop_event is not None and getattr(stop_event, "is_set", lambda: False)():
        raise RuntimeError("RAW Native Average cancelled before fusion")

    containers = tuple(read_dng_aot(path) for path in paths)
    frames = tuple(
        RawMosaicFrame.from_dng(container, source_id=path)
        for container, path in zip(containers, paths)
    )
    reference = frames[0]
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
    for path, frame in zip(paths[1:], frames[1:]):
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
                "RAW Native Average requires matching DNG geometry, CFA phase, "
                f"calibration, and orientation; incompatible frame: {path}"
            )
    if progress_callback:
        progress_callback(5, "Menyiapkan average RAW native...")
    normalized, report = fuse_dng_frames_blockwise(
        containers,
        block_size=_raw_native_block_size(block_size),
        apply_white_balance=False,
        # Use the target-qualified compression_raw graph for the selected
        # Taichi backend.  Missing/stale artifacts are intentionally surfaced
        # by the native dispatcher instead of silently changing computation
        # paths behind the user's selected backend.
        native=True,
    )
    return create_raw_native_average_result(
        normalized,
        reference,
        paths,
        report=report,
        progress_callback=progress_callback,
    )


class AverageDenoisingAlgorithm:
    """Simple average multi-frame denoising adapter."""

    NAME = "Average"
    KIND = "denoising"
    DESCRIPTION = "Average all aligned frames."

    def run(self, ctx, frames=None, batch_plan=None):
        backend = active_backend()
        image_paths = getattr(ctx, "image_paths", None)

        if image_paths and len(image_paths) >= 2:
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.resident_pipeline import (
                run_resident_pipeline,
            )

            is_raw = bool(getattr(ctx, "is_linear_mode", False))
            storage_mode = "direct"
            work_scale = float(
                getattr(ctx, "params", {}).get("work_resolution_scale", 0.50)
            ) if hasattr(ctx, "params") else 0.50

            stop_req = getattr(ctx, "stop_requested", None)
            if stop_req is not None and callable(stop_req) and stop_req():
                return None

            print(
                f"[Average] Routing to GPU-resident pipeline: backend={backend} "
                f"frames={len(image_paths)} storage_mode={storage_mode}"
            )

            alignment_plan = (
                getattr(ctx, "alignment_selection_name", None)
                or getattr(ctx, "params", {}).get("alignment_plan", "No Alignment")
            )
            alignment_config = getattr(ctx, "params", {}).get(
                "alignment_params", {}
            )
            batch_queue = int(
                getattr(ctx, "params", {}).get(
                    "batch_queue", getattr(ctx, "params", {}).get("batch_size", 3)
                )
            )
            params = getattr(ctx, "params", {}) if hasattr(ctx, "params") else {}
            configured_block_size = params.get("accumulation_block_size")
            if configured_block_size is None:
                # The global Performance Settings selection is resolved once
                # at the application boundary and then carried explicitly by
                # the resident request.  RAW Native also keeps the same
                # resolver as a headless fallback.
                configured_block_size = _raw_native_block_size(None)

            result_fp32, _ = run_resident_pipeline(
                image_paths,
                session=None,
                weight_engine="average",
                alignment_plan=alignment_plan,
                alignment_config=alignment_config,
                work_scale=work_scale,
                is_raw=is_raw,
                storage_mode=storage_mode,
                accumulation_mode=getattr(ctx, "params", {}).get(
                    "processing_mode", "auto"
                ),
                accumulation_block_size=configured_block_size,
                batch_queue=batch_queue,
                stop_event=stop_req,
                progress_callback=getattr(ctx, "update_progress", None),
                processing_format=getattr(ctx, "params", {}).get(
                    "processing_format", "RGB Linear"
                ),
            )

            if result_fp32 is None:
                return None

            if isinstance(result_fp32, RawNativeAverageResult):
                ctx.raw_native_result = result_fp32
                result_fp32 = result_fp32.preview_rgb

            ref_dtype = getattr(
                ctx,
                "ref_dtype",
                np.uint16 if (is_raw or hasattr(ctx, "raw_native_result")) else np.uint8,
            )
            result = restore_output_dtype(result_fp32, ref_dtype)
            print(
                f"[Average] finished backend={backend} "
                f"result shape={result.shape} dtype={result.dtype}"
            )
            return result

        # Legacy in-memory / HDF5 fallback
        if frames:
            print(
                f"[AverageDenoisingAlgorithm] start in-memory frames={len(frames)} "
                f"batch_plan={batch_plan}"
            )
            stack = np.stack(
                [frame.astype(np.float32, copy=False) for frame in frames], axis=0
            )
            averaged = np.mean(stack, axis=0)
            ref_dtype = getattr(ctx, "ref_dtype", frames[0].dtype)
            return restore_output_dtype(averaged, ref_dtype)

        return None
