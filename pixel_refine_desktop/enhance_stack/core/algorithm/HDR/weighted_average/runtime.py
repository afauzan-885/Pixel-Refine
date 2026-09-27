"""Target-aware dispatch for the packaged weighted-average HDR TCM."""

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
        assets_root, "hdr_weighted_average", target, allow_legacy=False
    )
    if path is None:
        expected = assets_root / target.artifact_name("hdr_weighted_average")
        raise FileNotFoundError(
            "Weighted HDR TCM is missing for the active target "
            f"{target.target_id}: expected {expected}. Compile it with "
            "pixel_refine_desktop\\enhance_stack\\core\\algorithm\\HDR\\"
            "weighted_average\\compile_weighted_average.py."
        )
    return path


def _run_weight_graph(image, laplacian, scalars):
    from taichi_vision.taichi_aot.engine import InputArray, OutputArray
    from taichi_vision.taichi_aot import get_engine

    engine = get_engine()
    rgb = np.ascontiguousarray(image, dtype=np.float32)
    lap = np.ascontiguousarray(laplacian, dtype=np.float32)
    if rgb.ndim != 3 or rgb.shape[2] != 3 or lap.shape != rgb.shape[:2]:
        raise ValueError("weighted HDR expects matching RGB and grayscale Laplacian")

    owned = []
    try:
        # AOTEngine.upload auto-detects HxWx3 arrays as vectors. The flat
        # scalar contract keeps graph ndim metadata consistent on every target.
        image_buffer = InputArray(rgb.reshape(-1), is_vector=False)
        lap_buffer = InputArray(lap, is_vector=False)
        weight_buffer = OutputArray(rgb.shape[:2], dtype=np.float32, is_vector=False)
        owned.extend((image_buffer, lap_buffer, weight_buffer))
        module = engine.load(str(_asset_path(engine)))
        module.run(
            "hdr_weighted_average_weight_f32",
            img_rgb=image_buffer,
            lap_gray=lap_buffer,
            weight=weight_buffer,
            h=int(rgb.shape[0]),
            w=int(rgb.shape[1]),
            **scalars,
        )
        result = weight_buffer.to_numpy()
        engine.sync()
        return np.ascontiguousarray(result, dtype=np.float32)
    finally:
        try:
            engine.sync()
        finally:
            for buffer in owned:
                try:
                    buffer.destroy()
                except Exception:
                    pass


def compute_weights_aot(
    image,
    laplacian,
    *,
    noise_sigma=0.1,
    noise_power=2.0,
    exposure_sigma=0.2,
    exposure_power=1.0,
    detail_power=1.0,
    saturation_power=1.0,
):
    """Compute exposure, detail, saturation, and SNR weights through TCM."""
    return _run_weight_graph(
        image,
        laplacian,
        {
            "noise_sigma": float(noise_sigma),
            "noise_power": float(noise_power),
            "exposure_sigma": float(exposure_sigma),
            "exposure_power": float(exposure_power),
            "detail_power": float(detail_power),
            "saturation_power": float(saturation_power),
        },
    )


def accumulate_weighted_aot(image, weights, result):
    """Accumulate one weighted RGB frame using the packaged Taichi graph."""
    from taichi_vision.taichi_aot.engine import InputArray
    from taichi_vision.taichi_aot import get_engine

    engine = get_engine()
    rgb = np.ascontiguousarray(image, dtype=np.float32)
    weight = np.ascontiguousarray(weights, dtype=np.float32)
    accumulator = np.ascontiguousarray(result, dtype=np.float32)
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"expected RGB [H, W, 3], got {rgb.shape}")
    if weight.shape != rgb.shape[:2] or accumulator.shape != rgb.shape:
        raise ValueError("weighted HDR image, weight, and accumulator shapes differ")

    owned = []
    try:
        image_buffer = InputArray(rgb.reshape(-1), is_vector=False)
        weight_buffer = InputArray(weight, is_vector=False)
        accumulator_buffer = InputArray(accumulator.reshape(-1), is_vector=False)
        owned.extend((image_buffer, weight_buffer, accumulator_buffer))
        module = engine.load(str(_asset_path(engine)))
        module.run(
            "hdr_weighted_average_accumulate_f32",
            lap_rgb=image_buffer,
            weight=weight_buffer,
            result=accumulator_buffer,
            h=int(rgb.shape[0]),
            w=int(rgb.shape[1]),
        )
        output = accumulator_buffer.to_numpy().reshape(rgb.shape)
        engine.sync()
        return np.ascontiguousarray(output, dtype=np.float32)
    finally:
        try:
            engine.sync()
        finally:
            for buffer in owned:
                try:
                    buffer.destroy()
                except Exception:
                    pass


__all__ = ["accumulate_weighted_aot", "compute_weights_aot"]
