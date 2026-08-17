"""Panorama and global-to-local alignment orchestration.

This family module deliberately contains orchestration only.  Feature
matching, RANSAC, homography, and remap kernels remain in their existing
families and are reused when an AOT backend is available.  A deterministic
NumPy path is retained as the correctness/reference route for tests and for
systems where a target-qualified artifact is not installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Callable, Sequence

import numpy as np

from ..pipeline_common import (
    PipelineReport,
    as_float32_image,
    as_gray_float32,
    timed_stage,
)
from ..alignment.apap import APAPWarp, fit_apap
from ..alignment.quality import (
    TransformEstimationError,
    TransformQuality,
    choose_best_transform,
    evaluate_transform,
    project_points,
    validate_correspondences,
)
from ..alignment.tps import TPSQuality, TPSWarp, fit_tps_checked
from .seam import graph_cut_maxflow


class PanoramaError(RuntimeError):
    """Raised when panorama inputs or a required alignment gate fail."""


@dataclass
class AlignmentResult:
    """Global transform plus optional local refinement and diagnostics."""

    transform: np.ndarray
    inlier_mask: np.ndarray
    source_points: np.ndarray
    target_points: np.ndarray
    quality: TransformQuality
    model: str
    tps: TPSWarp | None = None
    tps_quality: TPSQuality | None = None
    apap: APAPWarp | None = None
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "transform": np.asarray(self.transform).tolist(),
            "model": self.model,
            "quality": self.quality.as_dict(),
            "inliers": int(np.asarray(self.inlier_mask).sum()),
            "tps_quality": (
                None if self.tps_quality is None else self.tps_quality.as_dict()
            ),
            "warnings": list(self.warnings),
        }


def _phase_translation_numpy(
    reference: np.ndarray, moving: np.ndarray
) -> tuple[float, float, float]:
    """Small FFT reference fallback for translation-only image pairs."""

    ref = np.asarray(reference, dtype=np.float64)
    mov = np.asarray(moving, dtype=np.float64)
    if ref.shape != mov.shape or ref.ndim != 2:
        raise ValueError("phase translation requires equal-size grayscale images")
    ref = ref - float(np.mean(ref))
    mov = mov - float(np.mean(mov))
    spectrum = np.fft.fft2(ref) * np.conj(np.fft.fft2(mov))
    magnitude = np.abs(spectrum)
    spectrum /= np.maximum(magnitude, 1.0e-12)
    correlation = np.fft.ifft2(spectrum).real
    peak = np.unravel_index(int(np.argmax(correlation)), correlation.shape)
    dy, dx = float(peak[0]), float(peak[1])
    h, w = ref.shape
    if dy > h / 2.0:
        dy -= h
    if dx > w / 2.0:
        dx -= w
    response = float(correlation[peak])
    return dx, dy, response


def _translation_alignment_score(
    reference: np.ndarray,
    moving: np.ndarray,
    dx: float,
    dy: float,
) -> float:
    """Score an integer moving-to-reference translation on its valid overlap.

    Existing AOT phase-correlation builds expose a peak response with a
    backend-dependent scale.  Comparing that raw number to the NumPy FFT
    response can therefore select a wrong shift.  This bounded overlap score
    puts both candidates on the same normalized cross-correlation scale.
    """

    ref = np.asarray(reference, dtype=np.float32)
    mov = np.asarray(moving, dtype=np.float32)
    shift_x, shift_y = int(round(float(dx))), int(round(float(dy)))
    height, width = ref.shape
    x0, x1 = max(0, shift_x), min(width, width + shift_x)
    y0, y1 = max(0, shift_y), min(height, height + shift_y)
    if x1 <= x0 or y1 <= y0:
        return -1.0
    lhs = ref[y0:y1, x0:x1]
    rhs = mov[y0 - shift_y : y1 - shift_y, x0 - shift_x : x1 - shift_x]
    # Keep the validation cheap for very large frames; the phase candidate is
    # still computed by the maintained AOT/FFT leaf, while this oracle only
    # adjudicates suspicious backend response conventions.
    stride = max(1, int(np.ceil(np.sqrt(lhs.size / 1_000_000.0))))
    lhs = lhs[::stride, ::stride].astype(np.float64, copy=False)
    rhs = rhs[::stride, ::stride].astype(np.float64, copy=False)
    lhs -= float(lhs.mean())
    rhs -= float(rhs.mean())
    denominator = float(np.linalg.norm(lhs) * np.linalg.norm(rhs))
    if denominator <= 1.0e-12:
        return -float(np.mean((lhs - rhs) ** 2))
    return float(np.sum(lhs * rhs) / denominator)


# The phase-correlation TCMs expose a backend-specific peak response.  A very
# small response is not a usable alignment candidate even when the returned
# displacement is finite; accepting it can create a plausible-looking but
# wrong panorama.  Keep this gate deliberately conservative and use the
# normalized overlap score below for the final candidate comparison.
_MIN_PHASE_RESPONSE = 5.0e-2


def _default_feature_matches(
    reference: np.ndarray,
    moving: np.ndarray,
    *,
    feature: str = "ofb",
    strict: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None] | None:
    """Use the existing AOT OFB/AKAZE facade when a qualified artifact exists."""

    if str(feature).lower() in {"none", "phase", "translation", "fft"}:
        return None
    # Import lazily: importing the panorama package must remain safe in a
    # compiler worker and must not eagerly initialise the AOT engine.
    try:
        from .. import aot_api
    except Exception as exc:
        if strict:
            raise NotImplementedError(
                "AOT panorama feature matching could not import the qualified facade"
            ) from exc
        return None
    # The maintained OFB/AKAZE facades document a normalized [0, 1] input
    # range, while panorama callers often provide uint8-like float planes.
    # Normalise only the matcher view; coordinates and the caller's image data
    # remain untouched.
    match_reference = np.asarray(reference, dtype=np.float32)
    match_moving = np.asarray(moving, dtype=np.float32)
    scale = max(
        float(np.max(np.abs(match_reference))), float(np.max(np.abs(match_moving))), 1.0
    )
    if scale > 1.0:
        match_reference = match_reference / scale
        match_moving = match_moving / scale
    candidates = [str(feature).lower()] if feature else []
    candidates.extend(name for name in ("ofb", "akaze") if name not in candidates)
    last_error = None
    for name in candidates:
        matcher = getattr(aot_api, name, None)
        if matcher is None:
            continue
        try:
            result = matcher(match_reference, match_moving)
        except Exception as exc:
            # An unavailable artifact is a normal fallback condition here;
            # callers still get deterministic phase/translation alignment.
            last_error = exc
            if strict:
                raise NotImplementedError(
                    f"AOT panorama feature matcher {name!r} is unavailable for the active target"
                ) from exc
            continue
        if not isinstance(result, tuple) or len(result) < 2:
            continue
        src, dst = result[0], result[1]
        if src is None or dst is None:
            continue
        try:
            src, dst = validate_correspondences(src, dst, min_points=3)
        except (ValueError, TransformEstimationError):
            if strict:
                raise NotImplementedError(
                    f"AOT panorama feature matcher {name!r} returned an invalid correspondence set"
                )
            continue
        scores = None if len(result) < 3 or result[2] is None else np.asarray(result[2])
        return src, dst, scores
    if strict:
        detail = f": {last_error}" if last_error is not None else ""
        raise NotImplementedError(
            "No qualified AOT OFB/AKAZE feature matcher produced valid correspondences"
            + detail
        )
    return None


def align_pair(
    reference: np.ndarray,
    moving: np.ndarray,
    *,
    matches: (
        tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray] | None
    ) = None,
    matcher: Callable[[np.ndarray, np.ndarray], object] | None = None,
    feature: str = "ofb",
    model: str = "auto",
    reprojection_threshold: float = 3.0,
    ransac_iterations: int = 512,
    refine: str | None = None,
    tps_regularization: float = 1.0e-3,
    tps_max_displacement: float | None = None,
    seed: int = 0,
    backend: str = "auto",
) -> AlignmentResult:
    """Estimate ``moving -> reference`` with a fail-closed quality gate.

    ``matches`` is the preferred production input because it permits the
    application to keep keypoint buffers resident.  The tuple convention is
    ``(reference_points, moving_points[, scores])`` and the returned matrix
    maps moving coordinates into reference coordinates.  When omitted, the
    existing OFB/AKAZE AOT matcher is attempted, then a phase-correlation
    translation fallback is used for texture-poor or artifact-free systems.
    """

    backend_name = str(backend).strip().lower()
    if backend_name not in {"auto", "numpy", "aot"}:
        raise ValueError("backend must be one of 'auto', 'numpy', or 'aot'")
    ref = as_gray_float32(reference, name="reference")
    mov = as_gray_float32(moving, name="moving")
    if ref.shape != mov.shape:
        raise ValueError(
            f"reference and moving images must have equal shape: {ref.shape} vs {mov.shape}"
        )

    correspondence = matches
    if correspondence is None and matcher is not None:
        correspondence = matcher(ref, mov)
    if correspondence is None and backend_name != "numpy":
        correspondence = _default_feature_matches(
            ref,
            mov,
            feature=feature,
            strict=backend_name == "aot",
        )

    warnings: list[str] = []
    if correspondence is not None:
        # Existing OFB/AKAZE facades return points in input order
        # (reference, moving).  Invert that ordering for the moving->reference
        # transform contract used by panorama composition.
        dst = np.asarray(correspondence[0], dtype=np.float64)
        src = np.asarray(correspondence[1], dtype=np.float64)
        src, dst = validate_correspondences(src, dst, min_points=3)
        if str(model).lower() == "auto":
            models = ("translation", "affine", "homography")
        else:
            models = (str(model),)
        try:
            transform, mask, quality = choose_best_transform(
                src,
                dst,
                models=models,
                reprojection_threshold=float(reprojection_threshold),
                iterations=int(ransac_iterations),
                seed=int(seed),
                quality_kwargs={
                    "min_inliers": (
                        3 if str(model).lower() in {"translation", "affine"} else 4
                    )
                },
            )
        except (ValueError, TransformEstimationError, np.linalg.LinAlgError) as exc:
            warnings.append(f"feature transform rejected: {exc}")
            transform = np.eye(3, dtype=np.float64)
            mask = np.zeros(len(src), dtype=bool)
            quality = evaluate_transform(
                src,
                dst,
                transform,
                model="affine",
                inlier_mask=mask,
                min_inliers=3,
            )
        model_name = quality.model
    else:
        # Existing Taichi phase-correlation is preferred; NumPy FFT is only a
        # backend-free reference fallback when no qualified artifact exists.
        dx = dy = response = 0.0
        try:
            if backend_name == "numpy":
                dx, dy, response = _phase_translation_numpy(ref, mov)
                raise StopIteration
            from ..alignment.phase_correlation import phase_correlation

            # The maintained phase-correlation facade reports reference ->
            # moving displacement.  The panorama transform is moving ->
            # reference, hence the sign inversion here.
            phase_dx, phase_dy, phase_response = phase_correlation(ref, mov)
            aot_dx, aot_dy = -float(phase_dx), -float(phase_dy)
            # ``backend='aot'`` is strict: NumPy may adjudicate a native
            # candidate's finite/quality metrics, but it must never replace a
            # rejected native displacement.  The historical ``auto`` path
            # may still compare against the reference FFT and select it.
            if backend_name == "aot":
                if not np.isfinite((aot_dx, aot_dy, phase_response)).all():
                    raise NotImplementedError(
                        "AOT panorama phase correlation returned non-finite output"
                    )
                if float(phase_response) < _MIN_PHASE_RESPONSE:
                    raise NotImplementedError(
                        "AOT panorama phase correlation response is below the quality gate"
                    )
                dx, dy, response = aot_dx, aot_dy, float(phase_response)
            else:
                numpy_dx, numpy_dy, numpy_response = _phase_translation_numpy(ref, mov)
                aot_score = _translation_alignment_score(ref, mov, aot_dx, aot_dy)
                numpy_score = _translation_alignment_score(ref, mov, numpy_dx, numpy_dy)
                if (
                    float(phase_response) < _MIN_PHASE_RESPONSE
                    or numpy_score > aot_score + 1.0e-5
                ):
                    dx, dy, response = (
                        float(numpy_dx),
                        float(numpy_dy),
                        float(numpy_response),
                    )
                    warnings.append(
                        "AOT phase candidate rejected by quality gate "
                        f"(response={float(phase_response):.4f}, "
                        f"overlap={aot_score:.4f} vs {numpy_score:.4f})"
                    )
                else:
                    dx, dy, response = aot_dx, aot_dy, float(phase_response)
        except StopIteration:
            pass
        except Exception as exc:
            if backend_name == "aot":
                raise NotImplementedError(
                    "AOT panorama phase-correlation is unavailable for the active target"
                ) from exc
            dx, dy, response = _phase_translation_numpy(ref, mov)
        transform = np.eye(3, dtype=np.float64)
        # The phase cross-power convention estimates moving -> reference here.
        transform[0, 2] = float(dx)
        transform[1, 2] = float(dy)
        height, width = ref.shape
        source_grid = np.array(
            [
                [0.0, 0.0],
                [width - 1.0, 0.0],
                [width - 1.0, height - 1.0],
                [0.0, height - 1.0],
            ],
            dtype=np.float64,
        )
        target_grid = source_grid + np.array([dx, dy], dtype=np.float64)
        src, dst = source_grid, target_grid
        mask = np.ones(len(src), dtype=bool)
        quality = evaluate_transform(
            src,
            dst,
            transform,
            model="translation",
            inlier_mask=mask,
            reprojection_threshold=max(float(reprojection_threshold), 1.0),
            min_inliers=3,
            min_inlier_ratio=0.5,
        )
        model_name = "translation"
        warnings.append(
            f"feature matches unavailable; phase response={float(response):.4f}"
        )

    tps = None
    tps_quality = None
    apap = None
    if refine:
        inlier_source = src[mask]
        inlier_target = dst[mask]
        if str(refine).lower() == "tps" and len(inlier_source) >= 3 and quality.valid:
            try:
                h, w = ref.shape
                tps, tps_quality = fit_tps_checked(
                    inlier_source,
                    inlier_target,
                    regularization=tps_regularization,
                    source_bounds=(0.0, 0.0, float(w - 1), float(h - 1)),
                    max_displacement=tps_max_displacement,
                )
                if not tps_quality.valid:
                    warnings.append(f"TPS refinement rejected: {tps_quality.reason}")
                    tps = None
            except (ValueError, TransformEstimationError, np.linalg.LinAlgError) as exc:
                warnings.append(f"TPS refinement unavailable: {exc}")
        elif (
            str(refine).lower() == "apap" and len(inlier_source) >= 4 and quality.valid
        ):
            try:
                apap = fit_apap(
                    inlier_source, inlier_target, global_homography=transform
                )
            except (ValueError, TransformEstimationError, np.linalg.LinAlgError) as exc:
                warnings.append(f"APAP refinement unavailable: {exc}")
        elif str(refine).lower() not in {"tps", "apap"}:
            raise ValueError("refine must be None, 'tps', or 'apap'")

    return AlignmentResult(
        transform=np.asarray(transform, dtype=np.float64),
        inlier_mask=np.asarray(mask, dtype=bool),
        source_points=np.asarray(src, dtype=np.float64),
        target_points=np.asarray(dst, dtype=np.float64),
        quality=quality,
        model=model_name,
        tps=tps,
        tps_quality=tps_quality,
        apap=apap,
        warnings=warnings,
    )


def _warp_numpy(
    image: np.ndarray, transform: np.ndarray, dsize: tuple[int, int]
) -> tuple[np.ndarray, np.ndarray]:
    """Inverse-map bilinear warp used when the AOT remap artifact is absent."""

    src = as_float32_image(image, name="image")
    width, height = int(dsize[0]), int(dsize[1])
    if width < 1 or height < 1:
        raise ValueError("dsize must contain positive dimensions")
    try:
        inverse = np.linalg.inv(np.asarray(transform, dtype=np.float64))
    except np.linalg.LinAlgError as exc:
        raise PanoramaError("warp transform is singular") from exc
    yy, xx = np.indices((height, width), dtype=np.float64)
    homogeneous = np.stack((xx.ravel(), yy.ravel(), np.ones(xx.size)), axis=1)
    mapped = homogeneous @ inverse.T
    denom = mapped[:, 2]
    good = np.abs(denom) > 1.0e-12
    sx = np.full(mapped.shape[0], -1.0, dtype=np.float64)
    sy = np.full(mapped.shape[0], -1.0, dtype=np.float64)
    sx[good] = mapped[good, 0] / denom[good]
    sy[good] = mapped[good, 1] / denom[good]
    h, w = src.shape[:2]
    valid = good & (sx >= 0.0) & (sx <= w - 1.0) & (sy >= 0.0) & (sy <= h - 1.0)
    x0 = np.clip(np.floor(sx).astype(np.int64), 0, max(w - 1, 0))
    y0 = np.clip(np.floor(sy).astype(np.int64), 0, max(h - 1, 0))
    x1 = np.clip(x0 + 1, 0, max(w - 1, 0))
    y1 = np.clip(y0 + 1, 0, max(h - 1, 0))
    wx = (sx - np.floor(sx)).astype(np.float32)
    wy = (sy - np.floor(sy)).astype(np.float32)
    if src.ndim == 2:
        values = (
            src[y0, x0] * (1.0 - wx) * (1.0 - wy)
            + src[y0, x1] * wx * (1.0 - wy)
            + src[y1, x0] * (1.0 - wx) * wy
            + src[y1, x1] * wx * wy
        )
        output = values.reshape(height, width).astype(np.float32)
        output[~valid.reshape(height, width)] = 0.0
    else:
        values = (
            src[y0, x0] * ((1.0 - wx) * (1.0 - wy))[:, None]
            + src[y0, x1] * (wx * (1.0 - wy))[:, None]
            + src[y1, x0] * ((1.0 - wx) * wy)[:, None]
            + src[y1, x1] * (wx * wy)[:, None]
        )
        output = values.reshape(height, width, src.shape[2]).astype(np.float32)
        output[~valid.reshape(height, width)] = 0.0
    return output, valid.reshape(height, width)


def _sample_source_coordinates(
    image: np.ndarray,
    source_x: np.ndarray,
    source_y: np.ndarray,
    valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Bilinearly sample a source image at an already-computed map."""

    src = as_float32_image(image, name="image")
    h, w = src.shape[:2]
    valid = np.asarray(valid, dtype=bool)
    x = np.asarray(source_x, dtype=np.float64)
    y = np.asarray(source_y, dtype=np.float64)
    finite = np.isfinite(x) & np.isfinite(y)
    valid = valid & finite & (x >= 0.0) & (x <= w - 1.0) & (y >= 0.0) & (y <= h - 1.0)
    safe_x = np.where(finite, x, 0.0)
    safe_y = np.where(finite, y, 0.0)
    x0 = np.clip(np.floor(safe_x).astype(np.int64), 0, max(w - 1, 0))
    y0 = np.clip(np.floor(safe_y).astype(np.int64), 0, max(h - 1, 0))
    x1 = np.clip(x0 + 1, 0, max(w - 1, 0))
    y1 = np.clip(y0 + 1, 0, max(h - 1, 0))
    wx = (safe_x - np.floor(safe_x)).astype(np.float32)
    wy = (safe_y - np.floor(safe_y)).astype(np.float32)
    if src.ndim == 2:
        values = (
            src[y0, x0] * (1.0 - wx) * (1.0 - wy)
            + src[y0, x1] * wx * (1.0 - wy)
            + src[y1, x0] * (1.0 - wx) * wy
            + src[y1, x1] * wx * wy
        )
        output = values.astype(np.float32)
        output[~valid] = 0.0
    else:
        values = (
            src[y0, x0] * ((1.0 - wx) * (1.0 - wy))[..., None]
            + src[y0, x1] * (wx * (1.0 - wy))[..., None]
            + src[y1, x0] * ((1.0 - wx) * wy)[..., None]
            + src[y1, x1] * (wx * wy)[..., None]
        )
        output = values.astype(np.float32)
        output[~valid] = 0.0
    return output, valid


def sparse_to_dense_warp(
    image: np.ndarray,
    source_map: np.ndarray,
    *,
    valid_mask: np.ndarray | None = None,
    backend: str = "numpy",
    use_flow: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Sample an image from a dense map evaluated from sparse alignment.

    ``source_map[..., 0:2]`` contains source ``(x, y)`` coordinates for each
    output pixel.  A caller can obtain this map by evaluating an existing TPS
    or APAP warp on the output grid after the global OFB/AKAZE + RANSAC gate.
    The family does not fit a second model here; it only owns the safe dense
    sampling boundary.  ``backend="aot"`` reuses the qualified ``remap`` TCM
    (or ``remap_with_flow`` when ``use_flow=True``), while ``numpy`` is the
    deterministic oracle.  Explicit AOT failures are reported instead of
    silently changing backend.
    """

    src = as_float32_image(image, name="image")
    maps = np.ascontiguousarray(source_map, dtype=np.float64)
    if maps.ndim != 3 or maps.shape[2] != 2:
        raise ValueError("source_map must have shape (H, W, 2)")
    height, width = maps.shape[:2]
    if height < 1 or width < 1:
        raise ValueError("source_map must have positive spatial dimensions")
    selected = str(backend).strip().lower()
    if selected not in {"numpy", "aot"}:
        raise ValueError("backend must be 'numpy' or 'aot'")
    if selected == "aot" and src.ndim == 3 and int(src.shape[2]) != 3:
        raise NotImplementedError(
            "sparse-to-dense AOT warp supports HxW or HxWx3 input; "
            "use backend='numpy' or convert the channel layout explicitly"
        )
    if valid_mask is None:
        valid = np.ones((height, width), dtype=bool)
    else:
        valid = np.asarray(valid_mask, dtype=bool)
        if valid.shape != (height, width):
            raise ValueError(
                "valid_mask shape must match source_map spatial dimensions"
            )
    x = maps[..., 0]
    y = maps[..., 1]
    finite = np.isfinite(x) & np.isfinite(y)
    h_src, w_src = src.shape[:2]
    valid = (
        valid
        & finite
        & (x >= 0.0)
        & (x <= w_src - 1.0)
        & (y >= 0.0)
        & (y <= h_src - 1.0)
    )
    safe_x = np.where(valid, x, 0.0).astype(np.float32, copy=False)
    safe_y = np.where(valid, y, 0.0).astype(np.float32, copy=False)
    if selected == "numpy":
        output, output_valid = _sample_source_coordinates(
            src,
            safe_x.reshape(-1),
            safe_y.reshape(-1),
            valid.reshape(-1),
        )
        return output.reshape(
            (height, width) + (() if src.ndim == 2 else (src.shape[2],))
        ), output_valid.reshape(height, width)

    try:
        from .. import aot_api

        if use_flow:
            yy, xx = np.indices((height, width), dtype=np.float32)
            flow = np.stack((safe_x - xx, safe_y - yy), axis=2).astype(
                np.float32, copy=False
            )
            output = aot_api.remap_with_flow(src, flow, height, width, return_gpu=False)
        else:
            output = aot_api.remap(src, safe_x, safe_y, return_gpu=False)
    except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
        raise NotImplementedError(
            "sparse-to-dense AOT warp requires target-qualified remap artifacts; "
            "use backend='numpy' explicitly"
        ) from exc
    output = np.ascontiguousarray(output, dtype=np.float32)
    output[~valid] = 0.0
    return output, valid


def _local_source_map(
    image: np.ndarray,
    canvas_to_previous: np.ndarray,
    inverse_local: Callable[[np.ndarray], np.ndarray],
    dsize: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Build a dense source map for a TPS/APAP refinement."""

    width, height = int(dsize[0]), int(dsize[1])
    yy, xx = np.indices((height, width), dtype=np.float64)
    homogeneous = np.stack((xx.ravel(), yy.ravel(), np.ones(xx.size)), axis=1)
    mapped = homogeneous @ np.asarray(canvas_to_previous, dtype=np.float64).T
    denom = mapped[:, 2]
    good = np.abs(denom) > 1.0e-12
    previous = np.full((len(mapped), 2), np.nan, dtype=np.float64)
    previous[good] = mapped[good, :2] / denom[good, None]
    finite = np.isfinite(previous).all(axis=1)
    source = np.full_like(previous, np.nan)
    if np.any(finite):
        source[finite] = np.asarray(inverse_local(previous[finite]), dtype=np.float64)
    valid_mask = finite & np.isfinite(source).all(axis=1)
    source_map = source.reshape(height, width, 2)
    return source_map, valid_mask.reshape(height, width)


def _warp_local_numpy(
    image: np.ndarray,
    canvas_to_previous: np.ndarray,
    inverse_local: Callable[[np.ndarray], np.ndarray],
    dsize: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Inverse-map a TPS/APAP refinement followed by a global canvas map."""

    source_map, valid_mask = _local_source_map(
        image, canvas_to_previous, inverse_local, dsize
    )
    height, width = source_map.shape[:2]
    warped, valid_mask = _sample_source_coordinates(
        image,
        source_map[..., 0].reshape(-1),
        source_map[..., 1].reshape(-1),
        valid_mask.reshape(-1),
    )
    if warped.ndim == 1:
        warped = warped.reshape(height, width)
    else:
        warped = warped.reshape(height, width, warped.shape[-1])
    return warped, valid_mask.reshape(height, width)


def _warp_with_existing_aot(
    image: np.ndarray,
    transform: np.ndarray,
    dsize: tuple[int, int],
    *,
    strict: bool = False,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Try the maintained AOT warp facade; return ``None`` on unavailable target."""

    if not strict and os.environ.get("PANORAMA_USE_AOT", "0") != "1":
        return None
    try:
        from .. import aot_api

        result = aot_api.warp_perspective(image, transform, dsize, return_gpu=False)
        warped, valid = _warp_numpy(
            np.ones_like(image, dtype=np.float32), transform, dsize
        )
        # ``valid`` above is only a geometric mask; preserve the AOT result
        # for valid pixels and clear clamped samples outside the source.
        result = np.ascontiguousarray(result, dtype=np.float32)
        result[~valid] = 0.0
        return result, valid
    except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
        if strict:
            raise NotImplementedError(
                "panorama AOT warp requires target-qualified warp_perspective/remap artifacts; "
                "use backend='numpy' explicitly"
            ) from exc
        return None


def _warp_local_aot(
    image: np.ndarray,
    canvas_to_previous: np.ndarray,
    inverse_local: Callable[[np.ndarray], np.ndarray],
    dsize: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Dispatch a TPS/APAP dense map through the existing AOT remap leaf."""

    source_map, valid_mask = _local_source_map(
        image, canvas_to_previous, inverse_local, dsize
    )
    height, width = source_map.shape[:2]
    return sparse_to_dense_warp(
        image,
        source_map,
        valid_mask=valid_mask,
        backend="aot",
    )


def _feather_weight(
    valid: np.ndarray, transform: np.ndarray, source_shape: tuple[int, ...]
) -> np.ndarray:
    """Distance-to-border feather weight in the source image domain."""

    h, w = source_shape[:2]
    yy, xx = np.indices(valid.shape, dtype=np.float64)
    homogeneous = np.stack((xx.ravel(), yy.ravel(), np.ones(xx.size)), axis=1)
    try:
        inverse = np.linalg.inv(np.asarray(transform, dtype=np.float64))
        mapped = homogeneous @ inverse.T
        denom = mapped[:, 2]
        good = np.abs(denom) > 1.0e-12
        sx = np.full(len(mapped), -1.0)
        sy = np.full(len(mapped), -1.0)
        sx[good] = mapped[good, 0] / denom[good]
        sy[good] = mapped[good, 1] / denom[good]
    except np.linalg.LinAlgError:
        return np.zeros(valid.shape, dtype=np.float32)
    distance = np.minimum.reduce((sx, sy, (w - 1.0) - sx, (h - 1.0) - sy))
    distance = distance.reshape(valid.shape)
    return np.where(valid, np.clip(distance + 1.0, 1.0, None), 0.0).astype(np.float32)


def stitch_panorama(
    images: Sequence[np.ndarray],
    *,
    transforms: Sequence[np.ndarray] | None = None,
    matcher: Callable[[np.ndarray, np.ndarray], object] | None = None,
    feature: str = "ofb",
    model: str = "auto",
    refine: str | None = None,
    blend: str = "feather",
    reprojection_threshold: float = 3.0,
    max_pixels: int = 80_000_000,
    max_working_bytes: int = 1_500_000_000,
    backend: str = "auto",
    seam_backend: str = "numpy",
    seam_smoothness: float = 0.25,
    seam_max_working_bytes: int = 1_500_000_000,
    return_report: bool = False,
) -> np.ndarray | tuple[np.ndarray, PipelineReport]:
    """Align and blend a planar panorama stack.

    ``transforms[i]`` maps image ``i`` into the first-image canvas.  When no
    transforms are provided, pairwise global alignment is estimated using the
    existing matcher and composed left-to-right.  APAP/TPS are optional local
    refinements and are only used after the global quality gate passes.
    ``backend="auto"`` preserves the historical environment-gated AOT attempt
    for global perspective warps and uses the NumPy reference for local fields.
    ``blend="graph_cut"`` composes frames sequentially with the bounded exact
    binary seam solver and is capped by that solver's four-million-pixel
    contract.  ``seam_backend="aot"`` uses the target-qualified static unary
    map leaf and the same deterministic host residual solver; missing target
    artifacts fail closed.
    ``backend="numpy"`` forces the reference path.  ``backend="aot"``
    requires target-qualified ``warp_perspective``/``remap`` artifacts
    (including dense TPS/APAP map sampling) and fails closed when unavailable.
    """

    if not images:
        raise ValueError("images must contain at least one frame")
    arrays = [
        as_float32_image(image, name=f"images[{i}]") for i, image in enumerate(images)
    ]
    reference_shape = arrays[0].shape
    if any(array.shape != reference_shape for array in arrays[1:]):
        raise ValueError("all panorama images must have the same shape")
    blend_name = str(blend).lower()
    if blend_name not in {"feather", "average", "graph_cut"}:
        raise ValueError("blend must be 'feather', 'average', or 'graph_cut'")
    if blend_name == "graph_cut":
        seam_name = str(seam_backend).strip().lower()
        if seam_name not in {"numpy", "taichi", "aot"}:
            raise ValueError(
                "seam_backend must be 'numpy', 'taichi', or 'aot' for graph_cut blending"
            )
        if int(seam_max_working_bytes) <= 0:
            raise ValueError("seam_max_working_bytes must be positive")
        if not np.isfinite(float(seam_smoothness)) or float(seam_smoothness) < 0.0:
            raise ValueError("seam_smoothness must be finite and non-negative")
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    backend_name = str(backend).strip().lower()
    if backend_name not in {"auto", "numpy", "aot"}:
        raise ValueError("backend must be one of 'auto', 'numpy', or 'aot'")
    # ``warp_perspective``/``remap`` AOT leaves expose only scalar and vec3
    # image graphs.  Explicit AOT must reject unsupported channel layouts
    # before dispatch; ``auto`` remains allowed to use its documented NumPy
    # local/reference path when the native leaf cannot represent the input.
    if backend_name == "aot" and arrays[0].ndim == 3 and int(arrays[0].shape[2]) != 3:
        raise NotImplementedError(
            "panorama AOT stitching supports HxW or HxWx3 input; "
            "use backend='numpy' or convert the channel layout explicitly"
        )
    # Preserve the historical report value for auto callers while making
    # explicit requests auditable in reports and downstream diagnostics.
    report_backend = (
        "aot-or-numpy" if backend_name == "auto" else f"panorama-{backend_name}"
    )
    report = PipelineReport(pipeline="panorama", backend=report_backend)
    homographies: list[np.ndarray] = []
    alignments: list[AlignmentResult] = []
    # For image ``i`` an optional entry stores the previous-image index and an
    # inverse TPS/APAP map ``previous -> image[i]``.  Keeping
    # this separate from the global matrices lets the AOT warp remain a valid
    # fast path whenever no local field was requested.
    local_inverse_fields: list[
        tuple[int, Callable[[np.ndarray], np.ndarray]] | None
    ] = []
    if transforms is not None:
        if len(transforms) != len(arrays):
            raise ValueError("transforms length must match images")
        homographies = [np.asarray(matrix, dtype=np.float64) for matrix in transforms]
        if any(
            matrix.shape != (3, 3) or not np.isfinite(matrix).all()
            for matrix in homographies
        ):
            raise ValueError("every panorama transform must be a finite 3x3 matrix")
    else:
        homographies = [np.eye(3, dtype=np.float64)]
        local_inverse_fields = [None]
        for index in range(1, len(arrays)):
            with timed_stage(report, f"align_{index}"):
                alignment = align_pair(
                    arrays[index - 1],
                    arrays[index],
                    matcher=matcher,
                    feature=feature,
                    model=model,
                    refine=refine,
                    reprojection_threshold=reprojection_threshold,
                    seed=index,
                    backend=backend_name,
                )
            alignments.append(alignment)
            if not alignment.quality.valid:
                raise PanoramaError(
                    f"pair {index - 1}->{index} failed quality gate: {alignment.quality.reason}"
                )
            homographies.append(homographies[-1] @ alignment.transform)
            local_field = None
            if alignment.tps is not None:
                try:
                    previous_h, previous_w = arrays[index - 1].shape[:2]
                    inverse_tps, inverse_quality = fit_tps_checked(
                        alignment.target_points[alignment.inlier_mask],
                        alignment.source_points[alignment.inlier_mask],
                        regularization=alignment.tps.regularization,
                        source_bounds=(
                            0.0,
                            0.0,
                            float(previous_w - 1),
                            float(previous_h - 1),
                        ),
                    )
                    if inverse_quality.valid:
                        local_field = (index - 1, inverse_tps.map_points)
                    else:
                        alignment.warnings.append(
                            f"inverse TPS rejected: {inverse_quality.reason}"
                        )
                except (
                    ValueError,
                    TransformEstimationError,
                    np.linalg.LinAlgError,
                ) as exc:
                    alignment.warnings.append(f"inverse TPS unavailable: {exc}")
            elif alignment.apap is not None:
                try:
                    inverse_apap = fit_apap(
                        alignment.target_points[alignment.inlier_mask],
                        alignment.source_points[alignment.inlier_mask],
                        global_homography=np.linalg.inv(alignment.transform),
                    )
                    local_field = (index - 1, inverse_apap.map_points)
                except (
                    ValueError,
                    TransformEstimationError,
                    np.linalg.LinAlgError,
                ) as exc:
                    alignment.warnings.append(f"inverse APAP unavailable: {exc}")
            local_inverse_fields.append(local_field)
    if transforms is not None:
        local_inverse_fields = [None for _ in arrays]

    h, w = reference_shape[:2]
    corners = np.array(
        [[0.0, 0.0], [w - 1.0, 0.0], [w - 1.0, h - 1.0], [0.0, h - 1.0]],
        dtype=np.float64,
    )
    projected_corners = [project_points(corners, matrix) for matrix in homographies]
    if any(not np.isfinite(points).all() for points in projected_corners):
        raise PanoramaError("one or more transforms project non-finite canvas corners")
    all_points = np.concatenate(projected_corners, axis=0)
    minimum = np.floor(np.min(all_points, axis=0))
    maximum = np.ceil(np.max(all_points, axis=0))
    offset = np.array([-minimum[0], -minimum[1]], dtype=np.float64)
    canvas_w = int(maximum[0] - minimum[0] + 1.0)
    canvas_h = int(maximum[1] - minimum[1] + 1.0)
    if canvas_h < 1 or canvas_w < 1 or canvas_h * canvas_w > int(max_pixels):
        raise PanoramaError(
            f"panorama canvas {canvas_w}x{canvas_h} exceeds max_pixels={int(max_pixels)}"
        )
    channels = None if arrays[0].ndim == 2 else arrays[0].shape[2]
    # The current family-local compositor keeps an accumulator, weight map,
    # and output resident.  Refuse a request whose conservative estimate would
    # exceed the caller's memory budget; a future streamed/multiband path can
    # opt into a larger budget without changing the alignment contract.
    channel_count = 1 if channels is None else int(channels)
    estimated_working_bytes = int(canvas_h * canvas_w) * (
        channel_count * np.dtype(np.float64).itemsize
        + np.dtype(np.float64).itemsize
        + channel_count * np.dtype(np.float32).itemsize
    )
    if blend_name == "graph_cut":
        # Sequential graph-cut composition keeps a float32 canvas and a
        # validity mask in addition to the normal warp workspace.
        estimated_working_bytes += int(canvas_h * canvas_w) * (channel_count * 4 + 1)
    if estimated_working_bytes > int(max_working_bytes):
        raise MemoryError(
            f"panorama compositor requires about {estimated_working_bytes} bytes, "
            f"limit is {int(max_working_bytes)}"
        )
    offset_matrix = np.array(
        [[1.0, 0.0, offset[0]], [0.0, 1.0, offset[1]], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    canvas_transforms = [offset_matrix @ matrix for matrix in homographies]

    accum_shape = (
        (canvas_h, canvas_w) if channels is None else (canvas_h, canvas_w, channels)
    )
    accumulator = np.zeros(accum_shape, dtype=np.float64)
    weight_sum = np.zeros((canvas_h, canvas_w), dtype=np.float64)
    seam_canvas = (
        np.zeros(accum_shape, dtype=np.float32) if blend_name == "graph_cut" else None
    )
    seam_valid = (
        np.zeros((canvas_h, canvas_w), dtype=bool)
        if blend_name == "graph_cut"
        else None
    )
    for index, (array, matrix) in enumerate(zip(arrays, canvas_transforms)):
        with timed_stage(report, f"warp_{index}"):
            local_field = (
                local_inverse_fields[index]
                if index < len(local_inverse_fields)
                else None
            )
            if local_field is not None:
                previous_index, inverse_local = local_field
                previous_inverse = np.linalg.inv(canvas_transforms[previous_index])
                if backend_name == "aot":
                    warped, valid = _warp_local_aot(
                        array,
                        previous_inverse,
                        inverse_local,
                        (canvas_w, canvas_h),
                    )
                else:
                    # ``auto`` retains the established local NumPy path;
                    # ``numpy`` explicitly requests the same oracle.
                    warped, valid = _warp_local_numpy(
                        array,
                        previous_inverse,
                        inverse_local,
                        (canvas_w, canvas_h),
                    )
            else:
                if backend_name == "aot":
                    warped_info = _warp_with_existing_aot(
                        array,
                        matrix,
                        (canvas_w, canvas_h),
                        strict=True,
                    )
                elif backend_name == "numpy":
                    warped_info = None
                else:
                    warped_info = _warp_with_existing_aot(
                        array, matrix, (canvas_w, canvas_h)
                    )
                if warped_info is None:
                    warped, valid = _warp_numpy(array, matrix, (canvas_w, canvas_h))
                else:
                    warped, valid = warped_info
            if blend_name == "graph_cut":
                assert seam_canvas is not None and seam_valid is not None
                warped_array = np.ascontiguousarray(warped, dtype=np.float32)
                if index == 0:
                    seam_canvas[valid] = warped_array[valid]
                    seam_valid[...] = valid
                else:
                    overlap = seam_valid & valid
                    labels = graph_cut_maxflow(
                        seam_canvas,
                        warped_array,
                        overlap_mask=overlap,
                        smoothness=float(seam_smoothness),
                        backend=seam_backend,
                        max_pixels=min(int(max_pixels), 4_000_000),
                        max_working_bytes=int(seam_max_working_bytes),
                    )
                    choose_right = labels & valid
                    incoming_only = valid & ~seam_valid
                    if channels is None:
                        seam_canvas[choose_right] = warped_array[choose_right]
                        seam_canvas[incoming_only] = warped_array[incoming_only]
                    else:
                        seam_canvas[choose_right, :] = warped_array[choose_right, :]
                        seam_canvas[incoming_only, :] = warped_array[incoming_only, :]
                    seam_valid |= valid
            else:
                weights = (
                    _feather_weight(valid, matrix, array.shape)
                    if blend_name == "feather"
                    else valid.astype(np.float32)
                )
                accumulator += np.asarray(warped, dtype=np.float64) * (
                    weights if channels is None else weights[..., None]
                )
                weight_sum += weights
    if blend_name == "graph_cut":
        assert seam_canvas is not None and seam_valid is not None
        output = np.ascontiguousarray(seam_canvas, dtype=np.float32)
        valid_output = seam_valid
    else:
        output = np.zeros(accum_shape, dtype=np.float32)
        valid_output = weight_sum > 1.0e-12
        if channels is None:
            output[valid_output] = (
                accumulator[valid_output] / weight_sum[valid_output]
            ).astype(np.float32)
        else:
            output[valid_output] = (
                accumulator[valid_output] / weight_sum[valid_output, None]
            ).astype(np.float32)
    report.metrics.update(
        {
            "image_count": float(len(arrays)),
            "canvas_width": float(canvas_w),
            "canvas_height": float(canvas_h),
            "canvas_pixels": float(canvas_w * canvas_h),
            "coverage_fraction": float(valid_output.mean()),
            "estimated_working_bytes": float(estimated_working_bytes),
        }
    )
    # Keep useful alignment information in warnings/metadata without making
    # PipelineReport depend on a custom non-serialisable object.
    for index, alignment in enumerate(alignments, start=1):
        report.warnings.extend(
            f"pair_{index}: {warning}" for warning in alignment.warnings
        )
    return (output, report) if return_report else output


__all__ = [
    "PanoramaError",
    "AlignmentResult",
    "align_pair",
    "sparse_to_dense_warp",
    "stitch_panorama",
]
