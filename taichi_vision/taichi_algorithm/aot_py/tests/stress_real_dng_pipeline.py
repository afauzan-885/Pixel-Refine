"""Real-DNG block pipeline: demosaic, flow, remap, sharpen, fusion, NLM."""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path

import cv2
import numpy as np

from taichi_vision import taichi_aot as aot
from taichi_vision.taichi_algorithm.aot_py.tests.stress_optical_flow_blocks import VramSampler


def timed(stages, name, function):
    with VramSampler() as vram:
        start = time.perf_counter()
        result = function()
        seconds = time.perf_counter() - start
    stages[name] = {
        "seconds": seconds,
        "vram_baseline_mib": vram.baseline_mib,
        "vram_peak_mib": vram.peak_mib,
        "vram_delta_mib": vram.delta_mib,
    }
    return result


def normalize_edge(dx, dy, laplacian):
    magnitude = np.sqrt(dx * dx + dy * dy) + 0.35 * np.abs(laplacian)
    scale = float(np.percentile(magnitude, 99.0))
    return np.clip(magnitude / max(scale, 1e-6), 0.0, 1.0).astype(np.float32)


def sharpen(rgb, edge, amount=0.65):
    blurred = aot.gaussian_blur(rgb, sigma=1.0, kernel_size=5)
    mask = (0.2 + 0.8 * edge)[..., None]
    return np.clip(rgb + amount * mask * (rgb - blurred), 0.0, 1.0).astype(np.float32)


def flow_visualization(flow):
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    scale = max(float(np.percentile(magnitude, 99.0)), 1e-6)
    hsv = np.empty((*flow.shape[:2], 3), dtype=np.uint8)
    hsv[..., 0] = np.mod(angle * 90.0 / np.pi, 180).astype(np.uint8)
    hsv[..., 1] = 255
    hsv[..., 2] = np.clip(magnitude / scale * 255.0, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def as_bgr8(rgb):
    return cv2.cvtColor(np.clip(rgb * 255.0, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)


def preview(image, width=1200):
    if image.shape[1] <= width:
        return image
    height = int(round(image.shape[0] * width / image.shape[1]))
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    stages = {}
    aot.set_block_mode(
        enabled=True,
        size=args.block_size,
        threshold_bytes=0,
        cache_entries=args.cache_entries,
        cache_bytes=args.cache_mib * 1024 ** 2 if args.cache_mib else None,
        adaptive_memory=True,
        device_cache_enabled=False,
    )
    aot.engine.clear_block_cache()
    cache_before = aot.get_block_cache_stats()

    ref = timed(stages, "demosaic_reference", lambda: aot.demosaic(str(args.reference), method="hamilton"))
    comp = timed(stages, "demosaic_comparison", lambda: aot.demosaic(str(args.comparison), method="hamilton"))
    if ref.shape != comp.shape:
        raise RuntimeError(f"demosaic shapes differ: {ref.shape} versus {comp.shape}")

    ref_gray = timed(stages, "gray_reference", lambda: aot.rgb2gray(ref))
    comp_gray = timed(stages, "gray_comparison", lambda: aot.rgb2gray(comp))
    flow = timed(
        stages,
        "farneback_flow",
        lambda: aot.farneback_flow(
            np.ascontiguousarray(ref_gray * 255.0),
            np.ascontiguousarray(comp_gray * 255.0),
            num_levels=3, num_iters=3,
            win_size=15, poly_n=5, poly_sigma=1.2,
        ),
    )
    flow = timed(stages, "smooth_flow", lambda: aot.smooth_flow_gpu(flow, sigma=1.0, kernel_size=5))
    aligned = timed(
        stages, "remap_comparison",
        lambda: aot.remap_with_flow(comp, flow, ref.shape[0], ref.shape[1]),
    )
    aligned_gray = timed(stages, "gray_aligned", lambda: aot.rgb2gray(aligned))

    ref_dx, ref_dy = timed(stages, "sobel_reference", lambda: aot.sobel(ref_gray))
    ref_lap = timed(stages, "laplacian_reference", lambda: aot.laplacian(ref_gray))
    aligned_dx, aligned_dy = timed(stages, "sobel_aligned", lambda: aot.sobel(aligned_gray))
    aligned_lap = timed(stages, "laplacian_aligned", lambda: aot.laplacian(aligned_gray))
    ref_edge = normalize_edge(ref_dx, ref_dy, ref_lap)
    aligned_edge = normalize_edge(aligned_dx, aligned_dy, aligned_lap)
    del ref_dx, ref_dy, ref_lap, aligned_dx, aligned_dy, aligned_lap

    ref_sharp = timed(stages, "sharpen_reference", lambda: sharpen(ref, ref_edge))
    aligned_sharp = timed(stages, "sharpen_aligned", lambda: sharpen(aligned, aligned_edge))
    consistency = np.exp(-np.abs(ref_gray - aligned_gray) / 0.08).astype(np.float32)
    ref_weight = 1.0 + ref_edge
    aligned_weight = consistency * (1.0 + aligned_edge)
    weight_sum = np.maximum(ref_weight + aligned_weight, 1e-6)
    fused = timed(
        stages,
        "edge_weighted_fusion",
        lambda: np.ascontiguousarray(
            (ref_sharp * ref_weight[..., None] + aligned_sharp * aligned_weight[..., None])
            / weight_sum[..., None],
            dtype=np.float32,
        ),
    )
    final = timed(
        stages,
        "non_local_means",
        lambda: aot.non_local_means(
            fused, h_param=0.08, search_window=3, patch_size=1,
            refinement_strength=1.0, shrinkage_strength=1.0,
        ),
    )
    warm_final = timed(
        stages,
        "non_local_means_warm",
        lambda: aot.non_local_means(
            fused, h_param=0.08, search_window=3, patch_size=1,
            refinement_strength=1.0, shrinkage_strength=1.0,
        ),
    )

    margin = 96
    core = (slice(margin, -margin), slice(margin, -margin))
    before_error = np.abs(ref_gray[core] - comp_gray[core])
    after_error = np.abs(ref_gray[core] - aligned_gray[core])
    flow_mag = np.sqrt(np.sum(flow * flow, axis=2))
    metrics = {
        "shape": list(ref.shape),
        "alignment_mae_before": float(np.mean(before_error)),
        "alignment_mae_after": float(np.mean(after_error)),
        "alignment_improvement_pct": float(
            (np.mean(before_error) - np.mean(after_error)) / max(np.mean(before_error), 1e-8) * 100.0
        ),
        "flow_median_px": float(np.median(flow_mag[core])),
        "flow_p95_px": float(np.percentile(flow_mag[core], 95)),
        "flow_p99_px": float(np.percentile(flow_mag[core], 99)),
        "consistency_mean": float(np.mean(consistency[core])),
        "finite": bool(all(np.isfinite(value).all() for value in (flow, aligned, fused, final))),
        "final_range": [float(np.min(final)), float(np.max(final))],
        "nlm_warm_identical": bool(np.array_equal(final, warm_final)),
    }

    flow_bgr = flow_visualization(flow)
    ref_bgr = as_bgr8(ref)
    aligned_bgr = as_bgr8(aligned)
    fused_bgr = as_bgr8(fused)
    final_bgr = as_bgr8(final)
    edge_bgr = cv2.cvtColor((ref_edge * 255.0).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    panels = [preview(value) for value in (ref_bgr, aligned_bgr, flow_bgr, edge_bgr, fused_bgr, final_bgr)]
    sheet = np.vstack((np.hstack(panels[:3]), np.hstack(panels[3:])))
    cv2.imwrite(str(args.output / "real_dng_pipeline_contact_sheet.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 94])
    cv2.imwrite(str(args.output / "real_dng_final_nlm_16bit.png"), cv2.cvtColor(
        np.clip(final * 65535.0, 0, 65535).astype(np.uint16), cv2.COLOR_RGB2BGR
    ))
    cv2.imwrite(str(args.output / "real_dng_flow.jpg"), preview(flow_bgr), [cv2.IMWRITE_JPEG_QUALITY, 94])

    report = {
        "reference": str(args.reference),
        "comparison": str(args.comparison),
        "block_size": args.block_size,
        "stages": stages,
        "metrics": metrics,
        "memory": aot.get_memory_status(force=True),
        "cache_before": cache_before,
        "cache_after": aot.get_block_cache_stats(),
    }
    (args.output / "real_dng_pipeline_report.json").write_text(
        json.dumps(report, indent=2), encoding="ascii"
    )
    print(json.dumps(report, indent=2))
    del ref, comp, aligned, fused, final, warm_final
    gc.collect()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("comparison", type=Path)
    parser.add_argument("--output", type=Path, default=Path("test_algorithm/block_visualization/real_dng_pipeline"))
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--cache-entries", type=int, default=512)
    parser.add_argument("--cache-mib", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
