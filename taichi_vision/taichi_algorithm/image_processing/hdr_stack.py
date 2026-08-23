"""HDR stack/deghost orchestration built from the existing HDR AOT leaves.

This module deliberately does not add another HDR pyramid implementation.  The
actual fusion is delegated to :func:`aot_api.research_pipeline.hdr_fuse_aot`,
which in turn dispatches the existing ``hdr_*`` graphs.  The family-local code
only owns the parts that are specific to a stack: robust exposure-normalised
motion confidence and the policy for replacing pixels that are likely ghosts.

``backend="aot"`` is the default and is fail-closed: the residual graph and
HDR fusion must be present in the selected target artifact, otherwise the
runtime error is propagated to the caller.  ``backend="numpy"`` is an
explicit host reference path for diagnostics and tests; it is never selected
implicitly by the AOT path.  The AOT residual leaf is qualified on the CPU
x86_64 Windows artifact; percentile/MAD thresholding and smoothing remain
bounded host policy.
"""

from typing import Sequence

import numpy as np

try:  # Taichi is optional for the explicit host/reference path.
    import taichi as ti
except ImportError:  # pragma: no cover - minimal installations
    ti = None

from ..pipeline_common import (
    PipelineReport,
    as_gray_float32,
    finite_fraction,
    timed_stage,
    update_stage_output,
    validate_same_shape,
)


# This policy stage intentionally runs on the host until a qualified residual
# graph exists.  Keep it bounded so an accidental oversized input cannot cause
# an unbounded temporary allocation.
MAX_POLICY_PIXELS = 55_000_000
MAX_SMOOTH_RADIUS = 8
DEFAULT_DEGHOST_WORKING_BYTES = 1_500_000_000


def _estimate_deghost_working_bytes(pixels: int) -> int:
    """Conservatively estimate peak scratch for one residual/confidence map.

    The residual policy materialises the two grayscale inputs, an
    exposure-normalised target, gradient/residual temporaries, the optional
    padded box mean, and the returned confidence plane.  NumPy reductions may
    allocate flattened temporaries as well, so use a fixed conservative
    bytes-per-pixel estimate instead of pretending the operation is in-place.
    This estimate is a guard only; it is not an allocator trace.
    """

    return int(max(0, int(pixels)) * 56 + 16 * 1024)


def _ensure_taichi_cpu() -> None:
    """Initialise or validate the explicit CPU-JIT deghost runtime."""

    if ti is None:
        raise ImportError("Taichi is required for deghost backend='taichi'")
    from taichi.lang import impl

    runtime = impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        ti.init(arch=ti.cpu, offline_cache=False)
        return
    current_arch = getattr(getattr(ti, "cfg", None), "arch", None)
    if current_arch != ti.cpu:
        raise RuntimeError(
            "deghost backend='taichi' requires a CPU JIT runtime; "
            "the current Taichi runtime is already initialised on another arch"
        )


if ti is not None:

    @ti.kernel
    def _deghost_residual_kernel(
        reference: ti.types.ndarray(dtype=ti.f32, ndim=2),
        target: ti.types.ndarray(dtype=ti.f32, ndim=2),
        residual: ti.types.ndarray(dtype=ti.f32, ndim=2),
        scale: ti.f32,
        offset: ti.f32,
        edge_weight: ti.f32,
    ):
        """Fuse exposure-normalised luminance and first-order edge residual."""

        for y, x in ti.ndrange(reference.shape[0], reference.shape[1]):
            ref_value = reference[y, x]
            normalised = ti.min(ti.max(target[y, x] * scale + offset, -4.0), 4.0)
            ref_left = reference[y, x - 1] if x > 0 else ref_value
            target_left = target[y, x - 1] if x > 0 else target[y, x]
            ref_up = reference[y - 1, x] if y > 0 else ref_value
            target_up = target[y - 1, x] if y > 0 else target[y, x]
            normalised_left = ti.min(
                ti.max(target_left * scale + offset, -4.0), 4.0
            )
            normalised_up = ti.min(
                ti.max(target_up * scale + offset, -4.0), 4.0
            )
            luminance = ti.abs(normalised - ref_value)
            gradient = ti.abs((ref_value - ref_left) - (normalised - normalised_left))
            gradient += ti.abs((ref_value - ref_up) - (normalised - normalised_up))
            residual[y, x] = luminance + edge_weight * gradient


def _validate_backend(backend: str) -> str:
    value = str(backend).lower()
    if value not in {"aot", "numpy"}:
        raise ValueError("backend must be 'aot' or the explicit host backend 'numpy'")
    return value


def _percentile_scale(reference: np.ndarray, target: np.ndarray) -> tuple[float, float, float, float]:
    """Estimate an exposure-only affine normalisation from robust percentiles."""

    ref_low, ref_high = np.percentile(reference, (5.0, 95.0))
    tgt_low, tgt_high = np.percentile(target, (5.0, 95.0))
    ref_span = max(float(ref_high - ref_low), 1e-6)
    tgt_span = max(float(tgt_high - tgt_low), 1e-6)
    scale = ref_span / tgt_span
    offset = float(ref_low) - scale * float(tgt_low)
    return float(scale), float(offset), float(ref_low), float(ref_high)


def _deghost_residual_taichi(
    reference: np.ndarray,
    target: np.ndarray,
    *,
    scale: float,
    offset: float,
    edge_weight: float,
) -> np.ndarray:
    """Compute the deterministic residual plane with the CPU-JIT kernel."""

    _ensure_taichi_cpu()
    ref = np.ascontiguousarray(reference, dtype=np.float32)
    tgt = np.ascontiguousarray(target, dtype=np.float32)
    residual = np.empty_like(ref, dtype=np.float32)
    _deghost_residual_kernel(
        ref,
        tgt,
        residual,
        np.float32(scale),
        np.float32(offset),
        np.float32(edge_weight),
    )
    try:
        ti.sync()
    except Exception:
        pass
    return np.ascontiguousarray(residual, dtype=np.float32)


def _box_mean(image: np.ndarray, radius: int) -> np.ndarray:
    """Small-memory edge-padded box mean used for motion confidence smoothing."""

    radius = int(radius)
    if radius > MAX_SMOOTH_RADIUS:
        raise ValueError(f"smooth radius is limited to {MAX_SMOOTH_RADIUS} for bounded host policy work")
    if radius <= 0:
        return np.asarray(image, dtype=np.float32).copy()
    data = np.asarray(image, dtype=np.float32)
    padded = np.pad(data, radius, mode="edge")
    result = np.zeros_like(data, dtype=np.float32)
    width = 2 * radius + 1
    # Accumulate in-place to avoid a large integral-image allocation at 50 MP.
    for dy in range(width):
        for dx in range(width):
            result += padded[dy : dy + data.shape[0], dx : dx + data.shape[1]]
    result /= float(width * width)
    return result


def deghost_confidence(
    reference,
    target,
    *,
    threshold: float | None = None,
    smooth_radius: int = 1,
    edge_weight: float = 0.25,
    return_residual: bool = False,
    backend: str = "numpy",
    max_working_bytes: int = DEFAULT_DEGHOST_WORKING_BYTES,
):
    """Return a soft confidence map for one exposure relative to a reference.

    The target is first normalised with robust 5/95-percentile statistics so a
    global exposure difference does not become a false ghost.  A luminance
    residual and a gradient residual are combined, and the threshold defaults
    to ``max(3*MAD, 1e-3)``.  Values near one are consistent; values near zero
    are likely moving/ghost regions.

    ``backend="taichi"`` moves the exposure-normalised luminance/gradient
    residual to an explicit CPU-JIT kernel; ``backend="aot"`` dispatches the
    matching target-qualified residual graph.  Percentile estimation, MAD
    thresholding, and bounded box smoothing remain host policy work.  The
    optional
    ``max_working_bytes`` guard applies before percentile/smoothing temporaries
    are allocated and is useful when this policy is called independently of
    :func:`hdr_stack`.
    """

    backend_name = str(backend).strip().lower()
    if backend_name not in {"numpy", "taichi"}:
        if backend_name != "aot":
            raise ValueError("backend must be 'numpy', 'taichi', or 'aot'")

    ref = as_gray_float32(reference, name="reference")
    tgt = as_gray_float32(target, name="target")
    if ref.shape != tgt.shape:
        raise ValueError(f"reference and target must have the same shape, got {ref.shape} vs {tgt.shape}")
    if int(ref.size) > MAX_POLICY_PIXELS:
        raise ValueError(
            f"deghost policy input has {int(ref.size):,} pixels; maximum is {MAX_POLICY_PIXELS:,}"
        )
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    estimated_working_bytes = _estimate_deghost_working_bytes(int(ref.size))
    if estimated_working_bytes > int(max_working_bytes):
        raise MemoryError(
            f"HDR deghost residual requires about {estimated_working_bytes} bytes of working memory; "
            f"limit is {int(max_working_bytes)}"
        )
    if not np.isfinite(ref).all() or not np.isfinite(tgt).all():
        raise ValueError("reference and target must contain only finite values")
    if int(smooth_radius) < 0 or int(smooth_radius) > MAX_SMOOTH_RADIUS:
        raise ValueError(f"smooth_radius must be between 0 and {MAX_SMOOTH_RADIUS}")
    if not np.isfinite(float(edge_weight)) or float(edge_weight) < 0.0:
        raise ValueError("edge_weight must be finite and non-negative")

    scale, offset, _, _ = _percentile_scale(ref, tgt)
    if backend_name == "taichi":
        residual = _deghost_residual_taichi(
            ref,
            tgt,
            scale=scale,
            offset=offset,
            edge_weight=float(edge_weight),
        )
    elif backend_name == "aot":
        from ..aot_api.research import hdr_deghost_residual_aot

        residual = hdr_deghost_residual_aot(
            ref,
            tgt,
            scale=scale,
            offset=offset,
            edge_weight=float(edge_weight),
        )
    else:
        normalised = np.clip(tgt * scale + offset, -4.0, 4.0)
        residual = np.abs(normalised - ref).astype(np.float32)

        # A first-order gradient residual suppresses low-frequency exposure
        # drift while retaining edges around moving objects.
        gx_ref = np.diff(ref, axis=1, prepend=ref[:, :1])
        gy_ref = np.diff(ref, axis=0, prepend=ref[:1, :])
        gx_tgt = np.diff(normalised, axis=1, prepend=normalised[:, :1])
        gy_tgt = np.diff(normalised, axis=0, prepend=normalised[:1, :])
        gradient_residual = (np.abs(gx_ref - gx_tgt) + np.abs(gy_ref - gy_tgt)).astype(np.float32)
        residual = residual + float(edge_weight) * gradient_residual

    if smooth_radius > 0:
        residual = _box_mean(residual, smooth_radius)
    if threshold is None:
        median = float(np.median(residual))
        mad = float(np.median(np.abs(residual - median)))
        threshold_value = max(3.0 * 1.4826 * mad, 1e-3)
    else:
        threshold_value = float(threshold)
        if not np.isfinite(threshold_value) or threshold_value <= 0.0:
            raise ValueError("threshold must be finite and positive")

    # A soft ramp avoids seams at the confidence boundary and leaves a small
    # floor so a single noisy estimate cannot erase an entire exposure.
    confidence = np.clip(1.0 - residual / threshold_value, 0.05, 1.0).astype(np.float32)
    return (confidence, residual) if return_residual else confidence


def _prepare_deghosted_frames(
    frames: Sequence[np.ndarray],
    reference_index: int,
    threshold: float | None,
    smooth_radius: int,
    deghost_backend: str,
    max_working_bytes: int,
):
    reference = frames[reference_index]
    cleaned: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    for index, frame in enumerate(frames):
        if index == reference_index:
            mask = np.ones(frame.shape[:2], dtype=np.float32)
        else:
            mask = deghost_confidence(
                reference,
                frame,
                threshold=threshold,
                smooth_radius=smooth_radius,
                backend=deghost_backend,
                max_working_bytes=max_working_bytes,
            )
        if frame.ndim == 2:
            cleaned_frame = mask * frame + (1.0 - mask) * reference
        else:
            cleaned_frame = mask[..., None] * frame + (1.0 - mask[..., None]) * reference
        cleaned.append(np.ascontiguousarray(cleaned_frame, dtype=np.float32))
        masks.append(mask)
    return cleaned, np.stack(masks, axis=0).astype(np.float32)


def _numpy_fuse(frames: Sequence[np.ndarray], masks: np.ndarray) -> np.ndarray:
    """Explicit host reference fusion; AOT callers never enter this branch."""

    arrays = [np.asarray(frame, dtype=np.float32) for frame in frames]
    # Exposure fusion reference: confidence-weighted mean.  The AOT path uses
    # the existing noise/exposure/detail Laplacian fusion implementation.
    weights = np.asarray(masks, dtype=np.float32)
    denominator = np.maximum(weights.sum(axis=0), 1e-6)
    if arrays[0].ndim == 2:
        numerator = sum(weight * frame for weight, frame in zip(weights, arrays))
    else:
        numerator = sum(weight[..., None] * frame for weight, frame in zip(weights, arrays))
    return np.clip(numerator / (denominator if arrays[0].ndim == 2 else denominator[..., None]), 0.0, 1.0).astype(np.float32)


def hdr_stack(
    frames,
    *,
    reference_index: int = 0,
    deghost: bool = True,
    deghost_backend: str = "numpy",
    threshold: float | None = None,
    smooth_radius: int = 1,
    noise_sigmas=None,
    noise_power: float = 2.0,
    exposure_sigma: float = 0.2,
    exposure_power: float = 1.0,
    detail_power: float = 1.0,
    saturation_power: float = 1.0,
    n_levels: int | None = None,
    backend: str = "aot",
    max_working_bytes: int = 1_500_000_000,
    return_masks: bool = False,
    return_report: bool = False,
):
    """Fuse an aligned exposure stack with optional soft deghosting.

    ``backend="aot"`` dispatches the existing HDR research graphs and raises
    if the selected target cannot load them.  ``backend="numpy"`` is an
    explicit reference/diagnostic mode.  Input exposures are expected to be
    linear, same-shaped float images in the public ``[0, 1]`` range.  The
    optional ``deghost_backend`` controls only the residual policy: ``numpy``
    is the compatibility default, ``taichi`` uses the explicit CPU-JIT kernel,
    and ``aot`` uses its matching target-qualified residual leaf; percentile,
    MAD, and smoothing remain host policy in both accelerated modes.
    """

    backend_name = _validate_backend(backend)
    deghost_backend_name = str(deghost_backend).strip().lower()
    if deghost_backend_name not in {"numpy", "taichi", "aot"}:
        raise ValueError("deghost_backend must be 'numpy', 'taichi', or 'aot'")
    if isinstance(frames, np.ndarray):
        # Accept the common stack representation (N,H,W)/(N,H,W,C) while
        # retaining the existing list-of-frames API.
        frames = [frames] if frames.ndim <= 2 else list(frames)
    arrays = validate_same_shape(frames, name="frames")
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    if int(arrays[0].shape[0] * arrays[0].shape[1]) > MAX_POLICY_PIXELS:
        raise ValueError(
            f"HDR stack policy input exceeds the bounded {MAX_POLICY_PIXELS:,}-pixel limit"
        )
    if any(array.ndim == 3 and array.shape[2] not in (1, 3) for array in arrays):
        raise ValueError("HDR frames must be grayscale, RGB, or single-channel images")
    if not all(np.isfinite(array).all() for array in arrays):
        raise ValueError("HDR frames must contain only finite values")
    if not 0 <= int(reference_index) < len(arrays):
        raise ValueError("reference_index is out of range")
    reference_index = int(reference_index)

    # Deghosting holds several float32 planes per frame (normalised image,
    # residual, gradient residual, confidence) and the research HDR graph
    # owns a multi-level pyramid.  Refuse a request whose conservative peak
    # estimate exceeds the caller's budget before allocating those temporaries.
    pixels = int(arrays[0].shape[0]) * int(arrays[0].shape[1])
    channels = 1 if arrays[0].ndim == 2 else int(arrays[0].shape[2])
    per_frame = pixels * (4 * channels + 8)  # input/prepared plus confidence/residual
    pyramid = pixels * channels * 4 * 3  # source, weight, and Laplacian scratch
    estimated_working_bytes = int(len(arrays) * per_frame + pyramid)
    if estimated_working_bytes > int(max_working_bytes):
        raise MemoryError(
            f"HDR stack requires about {estimated_working_bytes} bytes of working memory; "
            f"limit is {int(max_working_bytes)}"
        )

    report = PipelineReport(pipeline="hdr_stack", backend=backend_name)
    if arrays[0].shape[0] * arrays[0].shape[1] > 16_000_000:
        report.add_warning(
            "deghost confidence is host orchestration; 16+ MP runtime/pressure must be benchmarked on the target"
        )
    if backend_name == "aot" and deghost and deghost_backend_name == "numpy":
        report.add_warning(
            "AOT HDR fusion is composed with the explicit NumPy deghost policy; "
            "set deghost_backend='aot' for the target-qualified residual leaf "
            "or 'taichi' for the explicit CPU-JIT residual"
        )
    if backend_name == "aot" and deghost and deghost_backend_name == "aot":
        report.add_warning(
            "AOT HDR fusion uses the target-qualified deghost residual graph; "
            "percentile/MAD thresholding and bounded smoothing remain host policy"
        )
    if backend_name == "numpy":
        report.add_warning("explicit host reference backend; no AOT graph was dispatched")

    if deghost:
        with timed_stage(report, "deghost_confidence"):
            prepared, masks = _prepare_deghosted_frames(
                arrays,
                reference_index,
                threshold,
                smooth_radius,
                deghost_backend_name,
                int(max_working_bytes),
            )
        update_stage_output(report, len(report.stages) - 1, masks)
    else:
        prepared = arrays
        masks = np.ones((len(arrays),) + arrays[0].shape[:2], dtype=np.float32)

    if backend_name == "numpy":
        with timed_stage(report, "fuse"):
            result = _numpy_fuse(prepared, masks)
        update_stage_output(report, len(report.stages) - 1, result)
    else:
        # Import lazily so explicit host diagnostics do not initialise the AOT
        # engine.  No exception is caught here: an unavailable artifact is an
        # actionable backend error, never a silent CPU substitution.
        from ..aot_api.research_pipeline import hdr_fuse_aot

        with timed_stage(report, "fuse"):
            result = hdr_fuse_aot(
                prepared,
                noise_sigmas=noise_sigmas,
                noise_power=noise_power,
                exposure_sigma=exposure_sigma,
                exposure_power=exposure_power,
                detail_power=detail_power,
                saturation_power=saturation_power,
                n_levels=n_levels,
            )
        update_stage_output(report, len(report.stages) - 1, result)

    result = np.ascontiguousarray(np.clip(result, 0.0, 1.0), dtype=np.float32)
    report.metrics["finite_fraction"] = finite_fraction(result)
    report.metrics["mean_confidence"] = float(np.mean(masks))
    report.metrics["estimated_working_bytes"] = float(estimated_working_bytes)
    report.metrics["deghost_backend_taichi"] = 1.0 if deghost_backend_name == "taichi" else 0.0
    report.metrics["deghost_backend_aot"] = 1.0 if deghost_backend_name == "aot" else 0.0
    if return_report and return_masks:
        return result, masks, report
    if return_report:
        return result, report
    if return_masks:
        return result, masks
    return result


__all__ = ["deghost_confidence", "hdr_stack"]
