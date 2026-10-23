"""Analysis, AutoEnhance, and WeightNet input preparation helpers.

Resolves analysis configuration, builds the work-resolution analysis proxy,
estimates reference noise, and prepares WeightNet reference/support tensors.
Stage-boundary helpers are reached through the resident facade so the
monkeypatched entry points keep working.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine

from .facade import api as _facade

ANALYSIS_AUTO_ENHANCE_MODE = "natural"

__all__ = [
    "ANALYSIS_AUTO_ENHANCE_MODE",
    "_resolve_apap_fit_grid_size",
    "_select_ransac_inlier_correspondences",
    "_resolve_spatial_analysis_config",
    "_resolve_reference_analysis_params",
    "_resolve_engine_analysis_params",
    "_resolve_weightnet_input_channels",
    "analyze_auto_enhance_on_gpu",
    "apply_auto_enhance_on_gpu",
    "prepare_analysis_proxy_gpu",
    "resolve_noise_adaptive_penalty",
    "prepare_reference_analysis_and_noise",
    "apply_clahe_16bit_reference",
    "apply_precomputed_transfer_map",
    "prepare_weightnet_reference_input",
    "prepare_weightnet_support_input",
]


def _resolve_apap_fit_grid_size(config):
    """Choose a local-model grid independently from the fixed 33x33 warp grid."""
    settings = config or {}
    preset = str(settings.get("mode", "fast")).strip().lower()
    default_size = {"fast": 13, "balance": 17, "high": 25}.get(preset, 17)
    return max(4, min(33, int(settings.get("apap_fit_grid_size", default_size))))


def _select_ransac_inlier_correspondences(source, target, inlier_mask):
    """Apply one RANSAC mask while preserving the selected rows' input order."""
    src = np.ascontiguousarray(source)
    dst = np.ascontiguousarray(target)
    if src.ndim != 2 or src.shape[1:] != (2,) or dst.shape != src.shape:
        raise ValueError(
            f"RANSAC correspondences must be matching Nx2 arrays, got {src.shape} and {dst.shape}"
        )
    if inlier_mask is None:
        selected = np.ones((len(src),), dtype=bool)
    else:
        if isinstance(inlier_mask, TaichiGPUBuffer):
            get_engine().sync()
            mask_values = inlier_mask.to_numpy()
        else:
            mask_values = np.asarray(inlier_mask)
        mask_values = np.asarray(mask_values).reshape(-1)
        if len(mask_values) != len(src):
            raise ValueError(
                f"RANSAC inlier mask has {len(mask_values)} rows for {len(src)} correspondences"
            )
        selected = mask_values.astype(bool, copy=False)
    if int(selected.sum()) < 4:
        raise RuntimeError(
            f"RANSAC selected only {int(selected.sum())} APAP correspondences; at least four are required"
        )
    return (
        np.ascontiguousarray(src[selected]),
        np.ascontiguousarray(dst[selected]),
    )


def _resolve_spatial_analysis_config(
    config, *, tile_size, overlap, work_shape, noise_score, is_raw
):
    """Resolve one identical spatial-weight policy for RGB and CFA carriers."""
    from taichi_vision.taichi_algorithm.spatial_fusion import auto_motion_sensitivity

    cfg = config or {}
    tile = max(
        8, min(int(cfg.get("similarity_spatial_tile_size", tile_size)), min(work_shape))
    )
    ratio = float(cfg.get("similarity_spatial_overlap_percent", overlap))
    base_motion = float(
        cfg.get("similarity_spatial_motion_sensitivity",
                cfg.get("motion_sensitivity", cfg.get("motion_sensivity", 150.0)))
    )
    offset = float(
        cfg.get("similarity_spatial_noise_mad_offset_factor",
                cfg.get("noise_offset_factor",
                        cfg.get("noise_mad_offset_factor", cfg.get("noise_offset", 0.15))))
    )
    explicit_sigma = cfg.get("similarity_spatial_noise_sigma", cfg.get("noise_sigma"))
    if explicit_sigma is not None and float(explicit_sigma) > 0:
        sigma, mode = float(explicit_sigma), "explicit_ui"
    elif noise_score is not None:
        sigma, mode = (
            float(np.clip(noise_score, 1e-4, 0.99999)),
            "linear_reference_score",
        )
    else:
        sigma, mode = 0.025, "fallback"
    motion = auto_motion_sensitivity(is_raw=is_raw, base=base_motion, noise_sigma=sigma)
    return tile, ratio, motion, offset, sigma, mode


def _resolve_reference_analysis_params(
    reference,
    *,
    enabled,
    supplied=None,
    needs_analysis=True,
    mode=ANALYSIS_AUTO_ENHANCE_MODE,
):
    """Analyze a reference once so its stage-specific RGB parameters are reused."""
    override = os.environ.get("PIXEL_REFINE_ANALYSIS_ENHANCE")
    if override is not None:
        enabled = override.strip().lower() not in ("0", "false", "off", "no")
    if not enabled or not needs_analysis:
        return None
    normalized_mode = str(mode).strip().lower()
    if normalized_mode not in {"analysis", "natural"}:
        raise ValueError(f"Unsupported AutoEnhance mode: {mode!r}")
    return supplied or _facade().analyze_auto_enhance_on_gpu(
        reference, mode=normalized_mode
    )


def _resolve_engine_analysis_params(
    reference,
    *,
    weight_engine,
    enabled,
    supplied=None,
    needs_analysis=True,
    mode=ANALYSIS_AUTO_ENHANCE_MODE,
):
    """Resolve the reference-driven transform for a requested pipeline stage."""
    # When mode is explicitly given as "natural" for spatial_weight scoring (not alignment),
    # SpatialFusion weight input remains linear.
    if (
        str(weight_engine).strip().lower() == "spatial_fusion"
        and str(mode).strip().lower() == "natural"
        and ANALYSIS_AUTO_ENHANCE_MODE != "natural"
    ):
        return None
    return _facade()._resolve_reference_analysis_params(
        reference,
        enabled=enabled,
        supplied=supplied,
        needs_analysis=needs_analysis,
        mode=mode,
    )


def _resolve_weightnet_input_channels(session, requested: Optional[int]) -> int:
    requested_channels = None if requested is None else int(requested)
    if requested_channels not in (None, 1):
        raise ValueError(f"FusionNet baseline requires 1 input channel, got {requested_channels}")
    active_session = getattr(session, "encoder_session", session)
    try:
        shape = active_session.get_inputs()[0].shape
        model_channels = shape[1] if len(shape) >= 2 else None
        if isinstance(model_channels, int) and model_channels != 1:
            raise ValueError(
                "FusionNet baseline requires a 1-channel ONNX model, "
                f"got model input channels={model_channels}"
            )
    except AttributeError:
        pass
    return requested_channels or 1

def analyze_auto_enhance_on_gpu(
    ref_gpu: TaichiGPUBuffer, mode: str = "natural"
) -> dict:
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        analyze_auto_enhance_params_gpu,
    )

    return analyze_auto_enhance_params_gpu(ref_gpu, mode=mode)


def apply_auto_enhance_on_gpu(
    src_gpu: TaichiGPUBuffer,
    params: dict,
    dst: Optional[TaichiGPUBuffer] = None,
) -> TaichiGPUBuffer:
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        apply_auto_enhance_gpu,
    )

    return _facade()._track_gpu_result(
        apply_auto_enhance_gpu(src_gpu, params, dst=dst, return_gpu=True)
    )


def prepare_analysis_proxy_gpu(
    source_gpu: TaichiGPUBuffer,
    *,
    work_shape: tuple[int, int],
    analysis_params: Optional[dict] = None,
    in_place: bool = False,
    source_is_disposable: bool = False,
    dst: Optional[TaichiGPUBuffer] = None,
) -> TaichiGPUBuffer:
    """Create the canonical work-resolution RGB analysis proxy.

    This helper is deliberately shared by RGB and RAW Native.  By default it
    never modifies or destroys ``source_gpu``: callers retain ownership of the
    source carrier and release the returned temporary when finished.

    ``in_place`` opts into writing the tone-mapped result back into
    ``source_gpu`` or ``dst``. The enhance kernel is per-pixel with an explicit
    destination, so when the caller already owns a throwaway carrier (RAW
    Native analysis proxies) or supplies a persistent ``dst`` scratch buffer,
    the second full-resolution buffer is pure waste.
    """

    from taichi_vision import taichi_aot

    taichi_aot = _facade()._managed_api(taichi_aot)

    work_h, work_w = (max(1, int(work_shape[0])), max(1, int(work_shape[1])))
    if tuple(int(value) for value in source_gpu.shape[:2]) != (work_h, work_w):
        proxy = taichi_aot.resize(
            source_gpu,
            (work_w, work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
            dst=dst,
        )
    else:
        if dst is not None and dst is not source_gpu:
            from taichi_vision.taichi_algorithm.common import copy_field
            copy_field(source_gpu, dst)
            proxy = dst
        else:
            proxy = source_gpu
            if (
                in_place
                and analysis_params is not None
                and not source_is_disposable
            ):
                # Keep the full-resolution linear carrier untouched when the
                # requested analysis geometry happens to match its dimensions.
                # A same-size resize does extra filtering work; an exact device
                # copy is sufficient to create the disposable in-place proxy.
                proxy = taichi_aot.copy(source_gpu, return_gpu=True)
    if analysis_params is None:
        return proxy
    enhanced = apply_auto_enhance_on_gpu(
        proxy, analysis_params, dst=proxy if in_place else None
    )
    if enhanced is not proxy and proxy is not source_gpu and proxy is not dst:
        _facade()._destroy_work_item(proxy)
    return enhanced


def resolve_noise_adaptive_penalty(
    analysis_proxy_gpu: TaichiGPUBuffer,
    *,
    ghost_penalty: float,
    ghost_penalty_min: Optional[float] = None,
) -> tuple[Optional[float], float]:
    """Estimate reference noise once and derive the shared ghost penalty."""

    score: Optional[float] = None
    try:
        from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
            estimate_noise,
        )

        score, _ = estimate_noise(analysis_proxy_gpu, session=_facade()._buffer_session())
        score = float(score)
    except Exception as exc:
        print(f"[GPU Pipeline] Noise estimation note: {exc}")

    if score is None:
        return None, float(ghost_penalty)

    maximum = float(ghost_penalty)
    minimum = float(
        ghost_penalty_min
        if ghost_penalty_min is not None
        else min(maximum, 0.65)
    )
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    if score <= 0.50:
        active = maximum
    elif score < 0.90:
        t = (score - 0.50) / 0.40
        factor = 0.5 * (1.0 + np.cos(np.pi * t))
        active = float(minimum + (maximum - minimum) * factor)
    else:
        active = minimum
    print(
        f"[GPU Pipeline] Noise-Adaptive Ghost Penalty: score={score:.4f} "
        f"-> penalty={active:.2f} (range=[{minimum:.2f}, {maximum:.2f}])"
    )
    return score, float(active)


def prepare_reference_analysis_and_noise(
    source_gpu: TaichiGPUBuffer,
    *,
    work_shape: tuple[int, int],
    analysis_params: Optional[dict],
    ghost_penalty: float,
    ghost_penalty_min: Optional[float] = None,
    in_place: bool = False,
    source_is_disposable: bool = False,
    noise_source_gpu: Optional[TaichiGPUBuffer] = None,
    noise_analysis_params: Optional[dict] = None,
) -> tuple[TaichiGPUBuffer, Optional[float], float]:
    """Prepare the reference analysis proxy, then estimate its noise once.

    Keep RGB Linear and RAW Native on the same ordering: work-resolution
    analysis proxy -> reference AutoEnhance -> noise estimate by default.
    FusionNet may provide an independent reference and AutoEnhance parameter
    set for noise estimation while its natural-mode WeightNet proxy remains
    separate from the alignment proxy. SpatialFusion can use an independent
    linear source for noise and weight scoring.
    """

    # If the same linear source is needed for noise estimation, do not let an
    # in-place AutoEnhance consume/mutate it, even when the caller considers
    # that proxy disposable.
    preserve_noise_source = noise_source_gpu is source_gpu
    analysis_gpu = _facade().prepare_analysis_proxy_gpu(
        source_gpu,
        work_shape=work_shape,
        analysis_params=analysis_params,
        in_place=in_place,
        source_is_disposable=(source_is_disposable and not preserve_noise_source),
    )
    noise_gpu = analysis_gpu
    owns_noise_gpu = False
    can_reuse_analysis_for_noise = (
        noise_source_gpu is source_gpu
        and noise_analysis_params == analysis_params
    )
    if noise_source_gpu is not None and not can_reuse_analysis_for_noise:
        noise_gpu = _facade().prepare_analysis_proxy_gpu(
            noise_source_gpu,
            work_shape=work_shape,
            analysis_params=noise_analysis_params,
        )
        owns_noise_gpu = noise_gpu is not noise_source_gpu and noise_gpu is not analysis_gpu
    try:
        score, active_penalty = _facade().resolve_noise_adaptive_penalty(
            noise_gpu,
            ghost_penalty=ghost_penalty,
            ghost_penalty_min=ghost_penalty_min,
        )
    finally:
        if owns_noise_gpu:
            _facade()._destroy_work_item(noise_gpu)
    if score is not None:
        source = (
            "autoenhanced_analysis"
            if noise_source_gpu is not None and noise_analysis_params is not None
            else "linear_unenhanced"
            if noise_source_gpu is not None
            else (
            "autoenhanced_natural"
            if analysis_params is not None
            else "linear_proxy_enhance_disabled"
            )
        )
        print(
            "[GPU Pipeline] Reference noise estimate (Taichi Vision): "
            f"score={score:.6f} source={source} "
            f"shape={tuple(int(v) for v in analysis_gpu.shape[:2])}"
        )
    return analysis_gpu, score, active_penalty


def apply_clahe_16bit_reference(
    rgb_chw: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
    backend: str = "auto",
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Compatibility alias: CLAHE was removed from FusionNet preprocessing.

    Preserve the historical callable and tuple contract for external callers;
    return the supplied CHW analysis tensor with no transfer map.
    """
    img = np.ascontiguousarray(rgb_chw, dtype=np.float32)
    if img.ndim != 3 or img.shape[0] not in (1, 3):
        raise ValueError(f"WeightNet reference must be CHW with 1 or 3 channels, got {img.shape}")
    return img, None


def apply_precomputed_transfer_map(
    rgb_chw: np.ndarray,
    transfer_map: np.ndarray,
) -> np.ndarray:
    """Compatibility helper for callers supplying an explicit transfer map."""
    img = np.asarray(rgb_chw)
    if img.dtype != np.float32 or not img.flags.c_contiguous:
        img = np.ascontiguousarray(img, dtype=np.float32)
    np.multiply(img, transfer_map[None, :, :], out=img)
    np.clip(img, 0.0, 1.0, out=img)
    return img


def prepare_weightnet_reference_input(
    analysis_gpu: TaichiGPUBuffer,
    *,
    work_shape: tuple[int, int],
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
    session=None,
) -> tuple[np.ndarray, Optional[np.ndarray]]:
    """Build the WeightNet reference tensor directly from the analysis proxy."""

    if getattr(session, "runtime", None) == "taichi_aot":
        return session.prepare_reference(analysis_gpu)
    from taichi_vision import taichi_aot

    taichi_aot = _facade()._managed_api(taichi_aot)

    work_h, work_w = (int(work_shape[0]), int(work_shape[1]))
    if tuple(int(value) for value in analysis_gpu.shape[:2]) != (work_h, work_w):
        work_gpu = taichi_aot.resize(
            analysis_gpu,
            (work_w, work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
    else:
        work_gpu = analysis_gpu
    try:
        reference_array = work_gpu.to_numpy()
        if reference_array.ndim == 2:
            reference_chw = np.ascontiguousarray(reference_array[None, ...], dtype=np.float32)
        else:
            reference_chw = np.ascontiguousarray(
                np.transpose(reference_array, (2, 0, 1)), dtype=np.float32
            )
    finally:
        if work_gpu is not analysis_gpu:
            _facade()._destroy_work_item(work_gpu)
    return reference_chw, None


def prepare_weightnet_support_input(
    aligned_analysis_gpu: TaichiGPUBuffer,
    transfer_map: Optional[np.ndarray] = None,
    workspace=None,
) -> np.ndarray:
    """Build one canonical CHW support tensor for the ONNX bridge.

    ``workspace`` is an internal reusable host readback pair.  The default
    path remains allocation-compatible for external callers, while resident
    pipelines can reuse the HWC readback and CHW bridge arrays per worker.
    """

    if getattr(transfer_map, "runtime", None) == "taichi_aot":
        return transfer_map.prepare(aligned_analysis_gpu)
    if workspace is not None:
        return workspace.read(aligned_analysis_gpu, transfer_map=transfer_map)

    support_chw = np.ascontiguousarray(
        np.transpose(aligned_analysis_gpu.to_numpy(), (2, 0, 1)),
        dtype=np.float32,
    )
    if transfer_map is not None:
        support_chw = apply_precomputed_transfer_map(support_chw, transfer_map)
    return support_chw
