"""Adversarial demosaic accuracy and runtime benchmark against RawPy.

The generated scenes target failure modes that are difficult for Bayer
demosaicing: high-contrast slanted edges, near-Nyquist repeated detail, and
distant foliage-like microstructure.  Each RGB scene is mosaiced as RGGB and
also written as a standards-based synthetic DNG so LibRaw/RawPy sees exactly
the same sensor samples as Taichi Vision.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import cv2
import numpy as np
import rawpy
import tifffile


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _downsample(canvas: np.ndarray, size: int) -> np.ndarray:
    return cv2.resize(canvas, (size, size), interpolation=cv2.INTER_AREA).astype(
        np.float32
    )


def make_contrast_edges(size: int = 256) -> np.ndarray:
    scale = 4
    n = size * scale
    image = np.full((n, n, 3), 0.025, dtype=np.float32)
    cv2.rectangle(image, (n // 11, n // 10), (n * 5 // 11, n * 9 // 10), (0.92,) * 3, -1)
    polygon = np.array(
        [[n * 5 // 10, n // 12], [n * 19 // 20, n * 4 // 10], [n * 6 // 10, n * 19 // 20]],
        dtype=np.int32,
    )
    cv2.fillConvexPoly(image, polygon, (0.04, 0.04, 0.04))
    cv2.line(image, (n // 20, n * 17 // 20), (n * 19 // 20, n // 5), (0.98,) * 3, 3 * scale)
    cv2.line(image, (n // 15, n // 3), (n * 14 // 15, n // 3 + 9 * scale), (0.01,) * 3, scale)
    return np.clip(_downsample(image, size), 0.0, 1.0)


def make_color_edges(size: int = 256) -> np.ndarray:
    scale = 4
    n = size * scale
    image = np.full((n, n, 3), (0.015, 0.02, 0.025), dtype=np.float32)
    cv2.rectangle(image, (n // 14, n // 12), (n * 7 // 15, n * 11 // 13), (0.92, 0.025, 0.02), -1)
    cv2.circle(image, (n * 7 // 10, n * 3 // 10), n // 5, (0.025, 0.88, 0.035), -1, cv2.LINE_AA)
    polygon = np.array(
        [[n * 11 // 20, n * 19 // 20], [n * 19 // 20, n * 9 // 20], [n * 19 // 20, n * 19 // 20]],
        dtype=np.int32,
    )
    cv2.fillConvexPoly(image, polygon, (0.02, 0.035, 0.94))
    cv2.line(image, (n // 20, n * 18 // 20), (n * 19 // 20, n // 15), (0.96, 0.96, 0.05), 2 * scale)
    return np.clip(_downsample(image, size), 0.0, 1.0)


def make_repeating_detail(size: int = 256) -> np.ndarray:
    y, x = np.indices((size, size), dtype=np.float32)
    sweep = 0.5 + 0.46 * np.sin(2.0 * np.pi * (0.035 * x + 0.00072 * x * x))
    diagonal = 0.5 + 0.46 * np.sign(np.sin(2.0 * np.pi * (x + 1.71 * y) / 5.5))
    checker = (((x.astype(np.int32) // 2) + (y.astype(np.int32) // 2)) & 1).astype(np.float32)
    mono = np.where(y < size / 3, sweep, np.where(y < 2 * size / 3, diagonal, 0.04 + 0.92 * checker))
    return np.repeat(mono[:, :, None], 3, axis=2).astype(np.float32)


def make_micro_foliage(size: int = 256, seed: int = 885) -> np.ndarray:
    scale = 4
    n = size * scale
    rng = np.random.default_rng(seed)
    image = np.empty((n, n, 3), dtype=np.float32)
    image[:] = (0.32, 0.48, 0.68)
    for _ in range(135):
        x0 = int(rng.integers(0, n))
        y0 = int(rng.integers(n // 7, n))
        length = int(rng.integers(20, 150))
        angle = float(rng.uniform(-1.45, 1.45))
        x1 = int(x0 + np.cos(angle) * length)
        y1 = int(y0 - abs(np.sin(angle)) * length)
        shade = float(rng.uniform(0.015, 0.12))
        cv2.line(image, (x0, y0), (x1, y1), (shade * 0.8, shade * 0.65, shade * 0.35), int(rng.integers(1, 4)))
    for _ in range(1850):
        center = (int(rng.integers(0, n)), int(rng.integers(n // 9, n)))
        axes = (int(rng.integers(2, 11)), int(rng.integers(1, 6)))
        angle = float(rng.uniform(0.0, 180.0))
        level = float(rng.uniform(0.08, 0.62))
        color = (level * rng.uniform(0.18, 0.48), level, level * rng.uniform(0.12, 0.36))
        cv2.ellipse(image, center, axes, angle, 0.0, 360.0, color, -1, cv2.LINE_AA)
    return np.clip(_downsample(image, size), 0.0, 1.0)


def rgb_to_rggb(rgb: np.ndarray) -> np.ndarray:
    bayer = np.empty(rgb.shape[:2], dtype=np.float32)
    bayer[0::2, 0::2] = rgb[0::2, 0::2, 0]
    bayer[0::2, 1::2] = rgb[0::2, 1::2, 1]
    bayer[1::2, 0::2] = rgb[1::2, 0::2, 1]
    bayer[1::2, 1::2] = rgb[1::2, 1::2, 2]
    return bayer


def write_synthetic_dng(path: Path, bayer: np.ndarray) -> None:
    raw = np.round(np.clip(bayer, 0.0, 1.0) * 65535.0).astype(np.uint16)
    height, width = raw.shape
    tags = [
        (50706, "B", 4, (1, 4, 0, 0), False),
        (50707, "B", 4, (1, 1, 0, 0), False),
        (50708, "s", 0, "PixelRefine Synthetic", False),
        (33421, "H", 2, (2, 2), False),
        (33422, "B", 4, (0, 1, 1, 2), False),
        (50710, "B", 3, (0, 1, 2), False),
        (50711, "H", 1, 1, False),
        (50713, "H", 2, (2, 2), False),
        (50714, "H", 4, (0, 0, 0, 0), False),
        (50717, "I", 1, 65535, False),
        (50718, "2I", 2, ((1, 1), (1, 1)), False),
        (50719, "I", 2, (0, 0), False),
        (50720, "I", 2, (width, height), False),
        (50721, "2i", 9, ((1, 1), (0, 1), (0, 1), (0, 1), (1, 1), (0, 1), (0, 1), (0, 1), (1, 1)), False),
        (50728, "2I", 3, ((1, 1), (1, 1), (1, 1)), False),
        (50778, "H", 1, 21, False),
    ]
    tifffile.imwrite(path, raw, photometric=32803, metadata=None, extratags=tags)


def rawpy_ahd(path: Path) -> np.ndarray:
    with rawpy.imread(str(path)) as raw:
        output = raw.postprocess(
            demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
            use_camera_wb=False,
            use_auto_wb=False,
            user_wb=[1.0, 1.0, 1.0, 1.0],
            output_color=rawpy.ColorSpace.raw,
            no_auto_bright=True,
            gamma=(1.0, 1.0),
            output_bps=16,
            adjust_maximum_thr=0.0,
        )
    return output.astype(np.float32) / 65535.0


def output_transfer(rgb: np.ndarray, method: str) -> np.ndarray:
    """Mirror the public graph's non-linear post-reconstruction transfer."""
    rgb = np.asarray(rgb, dtype=np.float32)
    maximum = np.max(rgb, axis=2)
    minimum = np.min(rgb, axis=2)
    if method == "arm":
        factor = np.clip((maximum - 0.45) / 0.35, 0.0, 1.0)
        ratio = minimum / np.maximum(maximum, 1e-5)
        neutrality = np.clip((0.82 - ratio) / 0.52, 0.0, 1.0)
    else:
        factor = np.clip((maximum - 0.55) / 0.43, 0.0, 1.0)
        ratio = minimum / np.maximum(maximum, 1e-5)
        neutrality = np.clip((ratio - 0.40) / 0.45, 0.0, 1.0)
    factor = factor * factor * (3.0 - 2.0 * factor)
    neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)
    blend = (factor * neutrality)[:, :, None]
    peak = maximum[:, :, None]
    recovered = rgb * (1.0 - blend) + peak * blend
    return recovered / np.sqrt(1.0 + recovered * recovered)


def metric_bundle(reference: np.ndarray, candidate: np.ndarray, *, achromatic: bool) -> dict:
    border = 8
    reference = reference[border:-border, border:-border]
    candidate = candidate[border:-border, border:-border]
    error = np.abs(candidate - reference)
    luma = np.dot(reference, np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))
    gx = cv2.Sobel(luma, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(luma, cv2.CV_32F, 0, 1, ksize=3)
    edge = cv2.dilate((np.hypot(gx, gy) > 0.06).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    mse = float(np.mean((candidate - reference) ** 2))
    result = {
        "mae": float(np.mean(error)),
        "psnr_db": float(10.0 * np.log10(1.0 / max(mse, 1e-12))),
        "p99_abs": float(np.quantile(error, 0.99)),
        "false_pixel_rate": float(np.mean(np.max(error, axis=2) > 0.08)),
        "edge_mae": float(np.mean(error[edge])) if np.any(edge) else 0.0,
    }
    if achromatic:
        chroma = np.max(candidate, axis=2) - np.min(candidate, axis=2)
        result["false_chroma_mean"] = float(np.mean(chroma))
        result["false_chroma_p99"] = float(np.quantile(chroma, 0.99))
        result["edge_false_chroma"] = float(np.mean(chroma[edge])) if np.any(edge) else 0.0
    return result


def cfa_gain_probe(taichi_aot, method: str) -> dict:
    """Detect G1/G2 orientation regressions for all four Bayer layouts."""
    patterns = {
        "RGGB": (0, 1, 3, 2),
        "GRBG": (1, 0, 2, 3),
        "GBRG": (3, 2, 0, 1),
        "BGGR": (2, 3, 1, 0),
    }
    gains = np.array([1.8, 1.0, 1.5, 1.17], dtype=np.float32)
    effective_gains = gains / np.max(gains) if method == "dcb" else gains
    level = np.float32(0.2)
    expected = output_transfer(
        np.full((1, 1, 3), level, dtype=np.float32), method
    )[0, 0]
    function = getattr(taichi_aot, method)
    report = {}
    for name, cfa in patterns.items():
        bayer = np.empty((64, 80), dtype=np.float32)
        for row in range(2):
            for col in range(2):
                bayer[row::2, col::2] = level / effective_gains[cfa[row * 2 + col]]
        output = function(
            bayer,
            float(gains[0]),
            float(gains[1]),
            float(gains[2]),
            float(gains[3]),
            np.eye(3, dtype=np.float32),
            0.0,
            1.0,
            *cfa,
        )[8:-8, 8:-8]
        report[name] = {
            "max_abs": float(np.max(np.abs(output - expected[None, None, :]))),
        }
    return report


def run_algorithm(
    taichi_aot,
    method: str,
    bayer: np.ndarray,
    runs: int,
    resident_input: bool,
) -> tuple[np.ndarray, dict]:
    """Run one full-frame AOT graph and report dispatch/readback timings."""
    function = getattr(taichi_aot, method)
    input_bayer = taichi_aot.upload(bayer) if resident_input else bayer
    args = (
        input_bayer,
        1.0,
        1.0,
        1.0,
        1.0,
        np.eye(3, dtype=np.float32),
        0.0,
        1.0,
        0,
        1,
        3,
        2,
    )
    dispatch_ms = []
    end_to_end_ms = []
    output = None
    try:
        warm = function(*args, return_gpu=True)
        if hasattr(warm, "release"):
            warm.release()
        for _ in range(max(1, runs)):
            started = time.perf_counter()
            candidate = function(*args, return_gpu=True)
            dispatched = time.perf_counter()
            output = (
                candidate.to_numpy()
                if hasattr(candidate, "to_numpy")
                else np.asarray(candidate)
            )
            finished = time.perf_counter()
            dispatch_ms.append((dispatched - started) * 1000.0)
            end_to_end_ms.append((finished - started) * 1000.0)
            if hasattr(candidate, "release"):
                candidate.release()
    finally:
        if resident_input and hasattr(input_bayer, "release"):
            input_bayer.release()
    return np.asarray(output), {
        "dispatch_median_ms": float(np.median(dispatch_ms)),
        "end_to_end_median_ms": float(np.median(end_to_end_ms)),
        "dispatch_runs_ms": dispatch_ms,
        "end_to_end_runs_ms": end_to_end_ms,
    }


def summarize(report: dict) -> dict:
    summary = {}
    for method in report["methods"]:
        entries = [scene["methods"][method] for scene in report["scenes"].values()]
        summary[method] = {
            "mean_mae": float(np.mean([entry["taichi"]["mae"] for entry in entries])),
            "rawpy_mean_mae": float(
                np.mean([entry["rawpy_ahd"]["mae"] for entry in entries])
            ),
            "mean_false_pixel_rate": float(
                np.mean([entry["taichi"]["false_pixel_rate"] for entry in entries])
            ),
            "rawpy_mean_false_pixel_rate": float(
                np.mean([entry["rawpy_ahd"]["false_pixel_rate"] for entry in entries])
            ),
            "dispatch_median_ms": float(
                np.median([entry["timing"]["dispatch_median_ms"] for entry in entries])
            ),
            "end_to_end_median_ms": float(
                np.median([entry["timing"]["end_to_end_median_ms"] for entry in entries])
            ),
        }
    summary["rawpy_ahd"] = {
        "end_to_end_median_ms": float(
            np.median(
                [scene["rawpy_ahd_ms"] for scene in report["scenes"].values()]
            )
        )
    }
    return summary


def run_benchmark(
    backend: str,
    size: int,
    methods: list[str],
    runs: int,
    selected_scenes: list[str],
    probe_cfa: bool,
    resident_input: bool,
) -> dict:
    os.environ["PIXEL_REFINE_AOT_ARCH"] = backend
    os.environ["AOT_ARCH"] = backend
    os.environ.setdefault("AOT_MODE", "1")
    from taichi_vision import taichi_aot

    all_scenes = {
        "contrast_edges": (make_contrast_edges(size), True),
        "color_edges": (make_color_edges(size), False),
        "repeating_detail": (make_repeating_detail(size), True),
        "micro_foliage": (make_micro_foliage(size), False),
    }
    scenes = {name: all_scenes[name] for name in selected_scenes}
    report = {
        "backend": backend,
        "size": size,
        "cfa_gain_probe": (
            {method: cfa_gain_probe(taichi_aot, method) for method in methods}
            if probe_cfa
            else {}
        ),
        "methods": methods,
        "input_mode": "resident" if resident_input else "host",
        "scenes": {},
    }
    with tempfile.TemporaryDirectory(prefix="pixel-refine-demosaic-") as directory:
        root = Path(directory)
        for name, (ground_truth, achromatic) in scenes.items():
            bayer = rgb_to_rggb(ground_truth)
            dng_path = root / f"{name}.dng"
            write_synthetic_dng(dng_path, bayer)
            rawpy_started = time.perf_counter()
            rawpy_rgb = rawpy_ahd(dng_path)
            rawpy_ms = (time.perf_counter() - rawpy_started) * 1000.0
            scene_report = {"rawpy_ahd_ms": rawpy_ms, "methods": {}}
            for method in methods:
                output, timing = run_algorithm(
                    taichi_aot, method, bayer, runs, resident_input
                )
                target = output_transfer(ground_truth, method)
                scene_report["methods"][method] = {
                    "taichi": metric_bundle(target, output, achromatic=achromatic),
                    "rawpy_ahd": metric_bundle(
                        target,
                        output_transfer(rawpy_rgb, method),
                        achromatic=achromatic,
                    ),
                    "timing": timing,
                }
            report["scenes"][name] = scene_report
    report["summary"] = summarize(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--methods", default="hamilton,arm,dcb,mlri_admm")
    parser.add_argument(
        "--scenes",
        default="contrast_edges,color_edges,repeating_detail,micro_foliage",
    )
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--skip-cfa-probe", action="store_true")
    parser.add_argument("--resident-input", action="store_true")
    args = parser.parse_args()
    methods = [item.strip() for item in args.methods.split(",") if item.strip()]
    unknown = sorted(set(methods) - {"hamilton", "arm", "dcb", "mlri_admm"})
    if unknown:
        parser.error(f"unsupported methods: {', '.join(unknown)}")
    scenes = [item.strip() for item in args.scenes.split(",") if item.strip()]
    valid_scenes = {
        "contrast_edges", "color_edges", "repeating_detail", "micro_foliage"
    }
    unknown_scenes = sorted(set(scenes) - valid_scenes)
    if unknown_scenes:
        parser.error(f"unsupported scenes: {', '.join(unknown_scenes)}")
    report = run_benchmark(
        args.backend,
        args.size,
        methods,
        max(1, args.runs),
        scenes,
        not args.skip_cfa_probe,
        args.resident_input,
    )
    console_report = (
        {
            "backend": report["backend"],
            "size": report["size"],
            "scenes": scenes,
            "input_mode": report["input_mode"],
            "cfa_gain_probe": report["cfa_gain_probe"],
            "summary": report["summary"],
        }
        if args.summary_only
        else report
    )
    payload = json.dumps(console_report, indent=2, sort_keys=True)
    print(payload)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
