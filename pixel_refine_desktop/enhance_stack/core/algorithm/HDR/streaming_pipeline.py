"""Database-backed HDR processing with bounded, one-frame-at-a-time reads."""

from __future__ import annotations

from dataclasses import dataclass
import math
import os
from pathlib import Path
import sqlite3
from typing import Callable

import numpy as np
from PIL import Image
import tifffile

from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
    PipelineCancelledError,
    PipelineRuntime,
)

from .card_content import (
    CARD_NAME,
    LEGACY_CARD_NAME,
    LEGACY_SPDE_MR_NAME,
    SPDE_MR_NAME,
)
from .hdr_fusion import (
    WeightedHDRFusion,
    estimate_noise_taichi,
    rgb_to_gray,
    srgb_to_linear,
)
from .spde_mr import SPDEMRAlgorithm


_RAW_EXTENSIONS = {
    ".dng", ".cr2", ".cr3", ".nef", ".arw", ".rw2", ".orf", ".raf",
    ".pef", ".srw",
}
_HISTOGRAM_BINS = 256


@dataclass(frozen=True)
class FrameAnalysis:
    path: str
    histogram_score: float
    median_luminance: float
    shape: tuple[int, int, int]
    exposure_time: float | None
    iso: float | None
    f_number: float | None
    camera: str | None

    @property
    def effective_exposure(self) -> float | None:
        if not self.exposure_time or not self.iso or not self.f_number:
            return None
        return self.exposure_time * self.iso / (self.f_number * self.f_number)


def _load_rgb(path: str | os.PathLike) -> np.ndarray:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"HDR input image not found: {path}")
    if path.suffix.lower() in _RAW_EXTENSIONS:
        # Match MF-Denoising's resident RAW path: keep Hamilton's output on
        # the selected Taichi backend, then read back the one frame needed by
        # HDR analysis/fusion. The non-resident return path may enter a
        # different block adapter for full-resolution RAW images.
        from taichi_vision import taichi_aot

        decoded_gpu = taichi_aot.demosaic(
            str(path), method="hamilton", return_gpu=True
        )
        try:
            decoded = np.asarray(decoded_gpu.to_numpy())
        finally:
            decoded_gpu.destroy()
        if decoded.ndim != 3 or decoded.shape[2] != 3:
            raise ValueError(f"Taichi RAW demosaic returned {decoded.shape} for {path}")
        if np.issubdtype(decoded.dtype, np.integer):
            rgb = decoded.astype(np.float32) / float(np.iinfo(decoded.dtype).max)
        else:
            rgb = decoded.astype(np.float32)
            peak = float(np.nanmax(rgb)) if rgb.size else 0.0
            if peak > 1.5:
                rgb /= 65535.0 if peak > 255.0 else 255.0
    else:
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
            load_rgb_linear_image,
        )

        rgb = load_rgb_linear_image(path, is_raw=False)
    rgb = np.ascontiguousarray(rgb, dtype=np.float32)
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"HDR input must decode to RGB [H, W, 3], got {rgb.shape}")
    if not np.isfinite(rgb).all():
        raise ValueError(f"HDR input contains non-finite pixels: {path}")
    return np.clip(rgb, 0.0, 1.0).astype(np.float32, copy=False)


def _numeric(value) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        try:
            numerator, denominator = value
            number = float(numerator) / float(denominator)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            return None
    return number if math.isfinite(number) and number > 0.0 else None


def _read_exposure_metadata(path: str) -> tuple[float | None, float | None, float | None, str | None]:
    exposure_time = iso = f_number = None
    camera_parts = []
    try:
        with Image.open(path) as image:
            exif = image.getexif()
            try:
                exif_ifd = exif.get_ifd(0x8769)
            except Exception:
                exif_ifd = {}
            exposure_time = _numeric(exif_ifd.get(33434, exif.get(33434)))
            f_number = _numeric(exif_ifd.get(33437, exif.get(33437)))
            iso_value = exif_ifd.get(34855, exif.get(34855))
            if isinstance(iso_value, (tuple, list)):
                iso_value = iso_value[0] if iso_value else None
            iso = _numeric(iso_value)
            for tag_id in (271, 272):
                value = exif.get(tag_id)
                if value:
                    camera_parts.append(str(value).strip())
    except Exception:
        pass

    if exposure_time is None or iso is None or f_number is None:
        try:
            import exifread

            with open(path, "rb") as handle:
                tags = exifread.process_file(handle, details=False, strict=True)
            exposure_time = exposure_time or _numeric(tags.get("EXIF ExposureTime"))
            iso = iso or _numeric(
                tags.get("EXIF ISOSpeedRatings")
                or tags.get("EXIF PhotographicSensitivity")
            )
            f_number = f_number or _numeric(tags.get("EXIF FNumber"))
            for key in ("Image Make", "Image Model"):
                value = tags.get(key)
                if value:
                    camera_parts.append(str(value).strip())
        except Exception:
            pass

    camera = " ".join(dict.fromkeys(camera_parts)) or None
    return exposure_time, iso, f_number, camera


def _histogram_analysis(rgb: np.ndarray) -> tuple[float, float]:
    gray = rgb_to_gray(rgb)
    counts, edges = np.histogram(
        gray, bins=_HISTOGRAM_BINS, range=(0.0, 1.0)
    )
    total = max(1, int(counts.sum()))
    probabilities = counts.astype(np.float64) / total
    centers = (edges[:-1] + edges[1:]) * 0.5
    exposure_suitability = float(
        np.sum(
            probabilities
            * np.exp(-0.5 * ((centers - 0.5) / 0.22) ** 2)
        )
    )
    usable_fraction = float(probabilities[3:-3].sum())
    score = float(np.clip(0.7 * exposure_suitability + 0.3 * usable_fraction, 0.0, 1.0))
    median_index = int(np.searchsorted(np.cumsum(counts), total * 0.5, side="left"))
    median = float(centers[min(median_index, len(centers) - 1)])
    return score, median


def _analyze_inputs(
    paths: list[str],
    *,
    progress_callback: Callable | None,
    stop_callback: Callable | None,
) -> list[FrameAnalysis]:
    analyses = []
    count = len(paths)
    for index, path in enumerate(paths):
        if stop_callback is not None and stop_callback():
            raise PipelineCancelledError("HDR histogram analysis cancelled")
        frame = _load_rgb(path)
        score, median = _histogram_analysis(frame)
        exposure_time, iso, f_number, camera = _read_exposure_metadata(path)
        analyses.append(
            FrameAnalysis(
                path=os.fspath(path),
                histogram_score=score,
                median_luminance=median,
                shape=tuple(frame.shape),
                exposure_time=exposure_time,
                iso=iso,
                f_number=f_number,
                camera=camera,
            )
        )
        del frame
        if progress_callback is not None:
            progress_callback(
                5 + int(15 * (index + 1) / max(count, 1)),
                f"Menganalisis histogram HDR {index + 1}/{count}",
            )
    return analyses


def _select_reference(analyses: list[FrameAnalysis], user_reference: str) -> tuple[int, bool]:
    by_path = {analysis.path: index for index, analysis in enumerate(analyses)}
    user_index = by_path.get(os.fspath(user_reference), 0)
    best_index = max(
        range(len(analyses)),
        key=lambda index: analyses[index].histogram_score,
    )
    selected_score = analyses[user_index].histogram_score
    best_score = analyses[best_index].histogram_score
    selected_is_poor = (
        best_index != user_index
        and selected_score < best_score * 0.8
        and best_score - selected_score > 0.12
    )
    return (best_index if selected_is_poor else user_index), selected_is_poor


def _metadata_gate(analyses: list[FrameAnalysis]) -> tuple[bool, str, list[float]]:
    effective = [analysis.effective_exposure for analysis in analyses]
    if any(value is None for value in effective):
        return False, "EXIF exposure, ISO, or aperture metadata is missing", []
    numeric_exposures = [float(value) for value in effective]
    cameras = {analysis.camera for analysis in analyses if analysis.camera}
    if len(cameras) > 1:
        return False, "input frames report different camera make/model values", []

    log_exposure = np.log2(np.asarray(numeric_exposures, dtype=np.float64))
    if len(analyses) > 1 and float(np.ptp(log_exposure)) >= 0.5:
        brightness = np.asarray(
            [analysis.median_luminance for analysis in analyses], dtype=np.float64
        )
        if np.unique(brightness).size < 2:
            return (
                False,
                "frame histograms cannot confirm the varying EXIF exposure order",
                [],
            )
        exposure_rank = np.argsort(np.argsort(log_exposure)).astype(np.float64)
        brightness_rank = np.argsort(np.argsort(brightness)).astype(np.float64)
        rank_correlation = float(np.corrcoef(exposure_rank, brightness_rank)[0, 1])
        if not math.isfinite(rank_correlation) or rank_correlation < 0.15:
            return (
                False,
                "EXIF exposure ordering conflicts with the observed frame histograms",
                [],
            )
    reference_exposure = numeric_exposures[0]
    return True, "complete EXIF exposure data passed consistency checks", numeric_exposures


def _alignment_validity(shape: tuple[int, int], dx: int, dy: int) -> np.ndarray:
    height, width = shape
    mask = np.zeros((height, width), dtype=bool)
    x0, x1 = max(0, -dx), min(width, width - dx)
    y0, y1 = max(0, -dy), min(height, height - dy)
    if x1 > x0 and y1 > y0:
        mask[y0:y1, x0:x1] = True
    return mask


def _write_tiff_atomic(path: Path, image: np.ndarray, *, radiance=False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.stem}.partial{path.suffix}")
    if radiance:
        payload = np.ascontiguousarray(image, dtype=np.float32)
    else:
        payload = np.rint(np.clip(image, 0.0, 1.0) * 65535.0).astype(np.uint16)
    try:
        tifffile.imwrite(
            temp_path,
            payload,
            photometric="rgb",
            metadata={"axes": "YXS"},
        )
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def run_hdr_pipeline(
    paths: list[str],
    *,
    user_reference: str,
    algorithm_name: str,
    output_directory: str | os.PathLike,
    progress_callback: Callable | None = None,
    stop_callback: Callable | None = None,
) -> dict:
    if not paths:
        raise ValueError("HDR batch has no input images")
    analyses = _analyze_inputs(
        paths,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
    )
    selected_index, reference_fallback = _select_reference(analyses, user_reference)
    selected = analyses[selected_index]
    reference_rgb = _load_rgb(selected.path)
    if min(reference_rgb.shape[:2]) < 8:
        raise ValueError("HDR frames must be at least 8x8 pixels")
    if any(analysis.shape != selected.shape for analysis in analyses):
        raise ValueError("HDR input images must share the reference image dimensions")

    metadata_is_reliable, metadata_reason, effective_exposures = _metadata_gate(analyses)
    radiance_enabled = metadata_is_reliable
    algorithm_key = str(algorithm_name).strip()
    is_spde_mr = algorithm_key in {
        SPDE_MR_NAME,
        LEGACY_SPDE_MR_NAME,
        "SPDE-MR",
        "SPDE MR",
    }
    if algorithm_key not in {CARD_NAME, LEGACY_CARD_NAME, "Weighted HDR (Streaming)"} and not is_spde_mr:
        raise ValueError(f"Unknown HDR algorithm: {algorithm_name}")

    from taichi_vision.taichi_algorithm.aot_api import align_mtb, warp_affine_aot

    progress = progress_callback
    if progress is not None:
        if reference_fallback:
            progress(
                20,
                "Referensi pilihan pengguna kurang baik menurut histogram; "
                f"memakai {Path(selected.path).name}",
            )
        else:
            progress(20, f"Referensi HDR: {Path(selected.path).name}")
        if not metadata_is_reliable:
            progress(20, f"Radiance HDR dilewati: {metadata_reason}; menyimpan LDR fusion")

    if is_spde_mr:
        fusion = SPDEMRAlgorithm().create_fusion(
            reference_rgb, radiance_enabled=radiance_enabled
        )
        add_frame = fusion.add_spde_frame
    else:
        fusion = WeightedHDRFusion(
            reference_rgb.shape, radiance_enabled=radiance_enabled
        )
        add_frame = fusion.add_frame

    ordered_paths = [analysis.path for analysis in analyses]
    support_paths = [path for path in ordered_paths if path != selected.path]
    selected_exposure = (
        effective_exposures[selected_index] if radiance_enabled else None
    )

    with PipelineRuntime(
        prefetch_depth=0,
        stop_event=stop_callback,
        progress_callback=progress_callback,
    ) as runtime:
        session = runtime.ensure_session()

        def add_aligned_frame(rgb, *, valid_mask=None, is_reference=False, index=0):
            gray = rgb_to_gray(rgb)
            sigma = estimate_noise_taichi(gray, session)
            radiance_rgb = None
            if radiance_enabled:
                source_exposure = effective_exposures[index]
                scale = selected_exposure / source_exposure
                radiance_rgb = srgb_to_linear(rgb) * np.float32(scale)
            if is_spde_mr:
                fusion.add_spde_frame(
                    rgb,
                    noise_sigma=sigma,
                    valid_mask=valid_mask,
                    radiance_rgb=radiance_rgb,
                    is_reference=is_reference,
                )
            else:
                fusion.add_frame(
                    rgb,
                    noise_sigma=sigma,
                    valid_mask=valid_mask,
                    radiance_rgb=radiance_rgb,
                )

        # User/reference frame is always the first candidate and anchors MTB.
        add_aligned_frame(reference_rgb, is_reference=True, index=selected_index)

        path_to_index = {analysis.path: i for i, analysis in enumerate(analyses)}

        def load_support(index):
            return _load_rgb(support_paths[index])

        for processed, (support_index, support_rgb) in enumerate(
            runtime.iter_supports(
                range(len(support_paths)),
                load_support,
                raise_on_cancel=True,
            ),
            start=1,
        ):
            if stop_callback is not None and stop_callback():
                raise PipelineCancelledError("HDR fusion cancelled")
            if support_rgb.shape != reference_rgb.shape:
                raise ValueError(
                    f"HDR frame shape changed during processing: {support_paths[support_index]}"
                )
            dx, dy = align_mtb(
                np.ascontiguousarray(reference_rgb * 255.0, dtype=np.float32),
                np.ascontiguousarray(support_rgb * 255.0, dtype=np.float32),
            )
            height, width = reference_rgb.shape[:2]
            aligned = warp_affine_aot(
                support_rgb,
                np.asarray([[1.0, 0.0, -dx], [0.0, 1.0, -dy]], dtype=np.float32),
                (width, height),
            )
            valid = _alignment_validity((height, width), int(dx), int(dy))
            source_index = path_to_index[support_paths[support_index]]
            add_aligned_frame(
                aligned,
                valid_mask=valid,
                index=source_index,
            )
            del support_rgb, aligned, valid
            if progress is not None:
                progress(
                    20 + int(70 * processed / max(len(support_paths), 1)),
                    f"HDR MTB alignment dan fusion {processed}/{len(support_paths)}",
                )

        ldr, radiance = fusion.finalize(reference_rgb)

    output_directory = Path(output_directory)
    output_name = Path(selected.path).stem
    safe_name = "".join(
        char if char.isalnum() or char in "-_" else "_" for char in output_name
    ).strip("._") or "hdr_reference"
    algorithm_suffix = "spde_mr" if is_spde_mr else "weighted_hdr"
    ldr_path = output_directory / f"{safe_name}_{algorithm_suffix}_ldr.tif"
    if progress is not None:
        progress(94, "Menyimpan hasil HDR LDR")
    _write_tiff_atomic(ldr_path, ldr)

    radiance_path = None
    if radiance is not None:
        radiance_path = output_directory / f"{safe_name}_{algorithm_suffix}_radiance.tif"
        _write_tiff_atomic(radiance_path, radiance, radiance=True)
    if progress is not None:
        progress(100, f"HDR selesai: {ldr_path.name}")

    return {
        "algorithm": SPDE_MR_NAME if is_spde_mr else CARD_NAME,
        "frame_count": len(analyses),
        "reference_path": selected.path,
        "reference_fallback": reference_fallback,
        "ldr_path": os.fspath(ldr_path),
        "radiance_path": os.fspath(radiance_path) if radiance_path else None,
        "radiance_reason": metadata_reason,
    }


def _get_batch_paths(db_path: str, batch_id: int, single_process: bool) -> list[str]:
    if not db_path:
        raise ValueError("HDR processing requires the session database path")
    with sqlite3.connect(db_path) as connection:
        rows = []
        try:
            rows = connection.execute(
                """
                SELECT images.path, batch_process_image.is_reference_batch
                FROM batch_process_image
                JOIN images ON images.id = batch_process_image.image_id_batch
                WHERE batch_process_image.batch_id = ?
                ORDER BY batch_process_image.is_reference_batch DESC, images.path ASC
                """,
                (int(batch_id),),
            ).fetchall()
        except sqlite3.Error:
            rows = []
        if not rows and single_process:
            try:
                rows = connection.execute(
                    """
                    SELECT images.path, single_process_image.is_reference
                    FROM single_process_image
                    JOIN images ON images.id = single_process_image.image_id_single
                    ORDER BY single_process_image.is_reference DESC, images.path ASC
                    """
                ).fetchall()
            except sqlite3.Error:
                rows = []
    paths = [os.fspath(path) for path, _ in rows if path and os.path.isfile(path)]
    if not paths:
        raise ValueError(f"No readable images found for HDR batch {batch_id}")
    return paths


def run_hdr_batch(
    *,
    parent=None,
    single_process=False,
    batch_id=1,
    algorithm_name=CARD_NAME,
    progress_callback=None,
    stop_callback=None,
    db_path=None,
) -> dict:
    if not db_path:
        db_path = os.environ.get("PIXEL_REFINE_SESSION_DB")
    batch_id = int(batch_id or 1)
    paths = _get_batch_paths(db_path, batch_id, bool(single_process))
    # The DB query orders the user's marked reference first. Keep that choice;
    # the preflight histogram can replace it only if it is clearly poor.
    user_reference = paths[0]
    output_directory = Path(db_path).parent / "stack"
    result = run_hdr_pipeline(
        paths,
        user_reference=user_reference,
        algorithm_name=algorithm_name,
        output_directory=output_directory,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
    )
    print(
        f"[HDR] {result['algorithm']} fused {result['frame_count']} frames; "
        f"reference={Path(result['reference_path']).name}; "
        f"ldr={result['ldr_path']}; radiance={result['radiance_path']}"
    )
    return result


__all__ = [
    "FrameAnalysis",
    "run_hdr_batch",
    "run_hdr_pipeline",
]
