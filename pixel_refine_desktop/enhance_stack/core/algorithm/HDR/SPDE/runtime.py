"""Target-aware dispatch for the packaged SPDE-MR HDR TCM."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def _asset_path(engine) -> Path:
    from taichi_vision.taichi_aot.artifact_targets import detect_target, resolve_artifact

    target = detect_target(
        backend=str(engine.arch),
        device=str(getattr(engine, "gpu_name", "") or ""),
    )
    assets_root = Path(__file__).resolve().parents[5] / "ui" / "data" / "aot_assets"
    path = resolve_artifact(
        assets_root, "hdr_spde_mr", target, allow_legacy=False
    )
    if path is None:
        expected = assets_root / target.artifact_name("hdr_spde_mr")
        raise FileNotFoundError(
            "SPDE-MR TCM is missing for the active target "
            f"{target.target_id}: expected {expected}. Compile it with "
            "pixel_refine_desktop\\enhance_stack\\core\\algorithm\\HDR\\"
            "SPDE\\compile_spde_mr.py."
        )
    return path


def score_patch_maps_aot(
    reference_gray,
    frame_gray,
    *,
    valid_mask=None,
    patch_size=8,
    stride=4,
    exposure_center=0.5,
    exposure_sigma=0.2,
    structure_threshold=0.8,
):
    """Run both SPDE-MR graphs from the active target's packaged TCM."""
    from taichi_vision.taichi_aot.engine import InputArray, OutputArray
    from taichi_vision.taichi_aot import get_engine

    reference = np.ascontiguousarray(reference_gray, dtype=np.float32)
    frame = np.ascontiguousarray(frame_gray, dtype=np.float32)
    if reference.ndim != 2 or frame.shape != reference.shape:
        raise ValueError("SPDE-MR grayscale inputs must have matching HxW dimensions")
    height, width = reference.shape
    if patch_size != 8 or stride != 4:
        raise ValueError("the initial SPDE-MR contract uses 8x8 patches at stride 4")
    if height < patch_size or width < patch_size:
        raise ValueError("SPDE-MR needs frames at least 8x8 pixels")
    if not np.isfinite(float(exposure_center)):
        raise ValueError("exposure_center must be finite")
    if not np.isfinite(float(exposure_sigma)) or float(exposure_sigma) <= 0.0:
        raise ValueError("exposure_sigma must be finite and greater than zero")
    if not np.isfinite(float(structure_threshold)):
        raise ValueError("structure_threshold must be finite")

    valid = (
        np.ones((height, width), dtype=np.int32)
        if valid_mask is None
        else np.ascontiguousarray(valid_mask, dtype=np.int32)
    )
    if valid.shape != (height, width):
        raise ValueError("alignment validity mask must match the grayscale inputs")

    patch_rows = (height - patch_size) // stride + 1
    patch_cols = (width - patch_size) // stride + 1
    engine = get_engine()
    owned = []
    try:
        reference_buffer = InputArray(reference, is_vector=False)
        frame_buffer = InputArray(frame, is_vector=False)
        valid_buffer = InputArray(valid, is_vector=False)
        patch_quality_buffer = OutputArray(
            (patch_rows, patch_cols), dtype=np.float32, is_vector=False
        )
        patch_stable_buffer = OutputArray(
            (patch_rows, patch_cols), dtype=np.int32, is_vector=False
        )
        quality_buffer = OutputArray(
            (height, width), dtype=np.float32, is_vector=False
        )
        stable_buffer = OutputArray(
            (height, width), dtype=np.int32, is_vector=False
        )
        policy_weight_buffer = OutputArray(
            (height, width), dtype=np.float32, is_vector=False
        )
        owned.extend(
            (
                reference_buffer,
                frame_buffer,
                valid_buffer,
                patch_quality_buffer,
                patch_stable_buffer,
                quality_buffer,
                stable_buffer,
                policy_weight_buffer,
            )
        )

        module = engine.load(str(_asset_path(engine)))
        module.run(
            "hdr_spde_mr_patch_score_f32",
            reference_gray=reference_buffer,
            frame_gray=frame_buffer,
            patch_quality=patch_quality_buffer,
            patch_stable=patch_stable_buffer,
            patch_rows=int(patch_rows),
            patch_cols=int(patch_cols),
            patch_size=int(patch_size),
            stride=int(stride),
            exposure_center=float(exposure_center),
            exposure_sigma=float(exposure_sigma),
            structure_threshold=float(structure_threshold),
        )
        module.run(
            "hdr_spde_mr_patch_expand_f32",
            patch_quality=patch_quality_buffer,
            patch_stable=patch_stable_buffer,
            valid_mask=valid_buffer,
            quality=quality_buffer,
            stable=stable_buffer,
            policy_weight=policy_weight_buffer,
            height=int(height),
            width=int(width),
            patch_rows=int(patch_rows),
            patch_cols=int(patch_cols),
        )

        quality = quality_buffer.to_numpy()
        stable = stable_buffer.to_numpy().astype(bool, copy=False)
        policy_weight = policy_weight_buffer.to_numpy()
        engine.sync()
        return (
            np.ascontiguousarray(quality, dtype=np.float32),
            np.ascontiguousarray(stable, dtype=bool),
            np.ascontiguousarray(policy_weight, dtype=np.float32),
        )
    finally:
        try:
            engine.sync()
        finally:
            for buffer in owned:
                try:
                    buffer.destroy()
                except Exception:
                    pass


__all__ = ["score_patch_maps_aot"]
