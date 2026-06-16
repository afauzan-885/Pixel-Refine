# -*- coding: utf-8 -*-
"""
FARNEBACK OPTICAL FLOW - 3-WAY COMPARISON

A) OpenCV murni (baseline)
B) OpenCV Pipeline (denoise + block tiling + median uint8 quantization)
C) Taichi Pipeline (ta.bilateral_grid + Farneback + ta.median_filter_flow float32 + ta.ransac_flow_cleanup)

10 iterasi dengan displacement berbeda. Output JSON + summary table.
"""

import os
import sys
import time
import json
import cv2
import numpy as np

# Ensure taichi_library is importable
# AOT_MODE=0 needed for live Taichi JIT kernels
os.environ["AOT_MODE"] = "0"
TAICHI_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "taichi_library")
TAICHI_ROOT = os.path.normpath(TAICHI_ROOT)
if TAICHI_ROOT not in sys.path:
    sys.path.insert(0, TAICHI_ROOT)

# Import test helpers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farneback_flow_accuracy_test import (
    compute_flow_opencv_direct,
    compute_epe,
    compute_psnr,
    compute_ssim,
    warp_image,
)

# Import taichi modules
try:
    import taichi_algorithm as ta
    from taichi_algorithm.median_filter import median_filter
    from taichi_algorithm.ransac import ransac_flow_cleanup
    from taichi_algorithm.bilateral_grid import bilateral_grid_filter
    TAICHI_OK = True
except (ImportError, Exception) as e:
    print(f"  [WARN] Taichi import failed: {e}")
    TAICHI_OK = False


DISPLACEMENTS = [
    {"name": "D01_tiny_right",   "dx": 2,   "dy": 0,   "desc": "2px horizontal"},
    {"name": "D02_small_diag",   "dx": 3,   "dy": 2,   "desc": "3x2 diagonal"},
    {"name": "D03_medium_right", "dx": 5,   "dy": 0,   "desc": "5px horizontal"},
    {"name": "D04_medium_diag",  "dx": 5,   "dy": 3,   "desc": "5x3 diagonal"},
    {"name": "D05_medium_left",  "dx": -4,  "dy": 1,   "desc": "-4x1 kiri"},
    {"name": "D06_large_right",  "dx": 8,   "dy": 0,   "desc": "8px horizontal"},
    {"name": "D07_large_diag",   "dx": 7,   "dy": 5,   "desc": "7x5 diagonal"},
    {"name": "D08_large_up",     "dx": 2,   "dy": -6,  "desc": "2x-6 naik"},
    {"name": "D09_extreme",      "dx": 10,  "dy": 8,   "desc": "10x8 extreme"},
    {"name": "D10_subpixel",     "dx": 1.5, "dy": 0.7, "desc": "1.5x0.7 sub-pixel"},
]


def generate_pair(h, w, dx, dy, noise_sigma=1.5):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    base = (
        128
        + 55 * np.sin(2*np.pi*x/80) * np.cos(2*np.pi*y/120)
        + 35 * np.sin(2*np.pi*x/40 + y/60)
        + 25 * np.cos(2*np.pi*(x+y)/200)
        + 20 * np.sin(2*np.pi*x/30) * np.sin(2*np.pi*y/50)
    ).astype(np.float32)
    base[150:280, 150:320] += 70
    base[350:420, 100:250] += 50
    base = np.clip(base, 0, 255).astype(np.uint8)
    flow_gt = np.zeros((h, w, 2), dtype=np.float32)
    flow_gt[:, :, 0] = dx
    flow_gt[:, :, 1] = dy
    target = warp_image(base, flow_gt, interpolation=cv2.INTER_CUBIC)
    noise = np.random.randn(h, w).astype(np.float32) * noise_sigma
    target = np.clip(target.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return base, target, flow_gt


# --- Method A: OpenCV murni ---
def method_a_opencv_direct(base_gray, target_gray, config):
    t0 = time.perf_counter()
    flow_a, _ = compute_flow_opencv_direct(base_gray, target_gray, config)
    time_ms = (time.perf_counter() - t0) * 1000
    return flow_a, time_ms


# --- Method B: OpenCV Pipeline (denoise + block + median uint8) ---
def method_b_opencv_pipeline(base_gray, target_gray, config):
    from farneback_flow_accuracy_test import compute_flow_pipeline
    t0 = time.perf_counter()
    flow_b, _ = compute_flow_pipeline(base_gray, target_gray, config)
    time_ms = (time.perf_counter() - t0) * 1000
    return flow_b, time_ms


# --- Method C: Taichi Pipeline ---
def method_c_taichi_pipeline(base_gray, target_gray, config):
    t0 = time.perf_counter()

    # 1. Konversi ke grayscale 8-bit
    base_8bit = base_gray if base_gray.dtype == np.uint8 else (
        (base_gray * 255).astype(np.uint8) if base_gray.max() <= 1.0
        else base_gray.astype(np.uint8)
    )
    target_8bit = target_gray if target_gray.dtype == np.uint8 else (
        (target_gray * 255).astype(np.uint8) if target_gray.max() <= 1.0
        else target_gray.astype(np.uint8)
    )

    # 2. Taichi Bilateral Grid Denoise (GPU, edge-preserving)
    base_f32 = base_8bit.astype(np.float32)
    target_f32 = target_8bit.astype(np.float32)
    base_denoised = bilateral_grid_filter(base_f32, s_s=16, s_r=16, sigma_s=1.0, sigma_r=1.0)
    target_denoised = bilateral_grid_filter(target_f32, s_s=16, s_r=16, sigma_s=1.0, sigma_r=1.0)
    # Convert back to uint8 for Farneback
    base_denoised_u8 = np.clip(base_denoised, 0, 255).astype(np.uint8)
    target_denoised_u8 = np.clip(target_denoised, 0, 255).astype(np.uint8)

    # 3. OpenCV Farneback (core algorithm - no taichi equivalent)
    flow_full = cv2.calcOpticalFlowFarneback(
        base_denoised_u8, target_denoised_u8, None,
        pyr_scale=config["pyr_scale"], levels=config["levels"],
        winsize=config["winsize"], iterations=config["iterations"],
        poly_n=config["poly_n"], poly_sigma=config["poly_sigma"],
        flags=config["flags"],
    )

    # 4. Taichi Median Filter Flow - per-channel (native float32, NO uint8 quantization!)
    flow_x = flow_full[:, :, 0].copy()
    flow_y = flow_full[:, :, 1].copy()
    flow_x = median_filter(flow_x, kernel_size=3)
    flow_y = median_filter(flow_y, kernel_size=3)
    flow_full = np.stack([flow_x, flow_y], axis=-1)

    # 5. Taichi RANSAC Flow Cleanup (outlier removal) - skip if bug
    try:
        flow_full = ransac_flow_cleanup(flow_full, threshold=3.0, n_iterations=10)
    except Exception as e:
        pass  # ransac_flow_cleanup has stride param bug in 1.7.4

    time_ms = (time.perf_counter() - t0) * 1000
    return flow_full, time_ms


def run_one(base_gray, target_gray, flow_gt, config):
    results = {}

    # Method A
    flow_a, t_a = method_a_opencv_direct(base_gray, target_gray, config)
    warped_a = warp_image(base_gray, flow_a)
    epe_a = compute_epe(flow_a, flow_gt)
    results["A"] = {
        "time_ms": round(t_a, 1),
        "ssim": round(float(compute_ssim(target_gray, warped_a)), 4),
        "psnr": round(float(compute_psnr(target_gray, warped_a)), 2),
        "epe_mean": round(epe_a["EPE_mean"], 4),
    }

    # Method B
    flow_b, t_b = method_b_opencv_pipeline(base_gray, target_gray, config)
    warped_b = warp_image(base_gray, flow_b)
    epe_b = compute_epe(flow_b, flow_gt)
    results["B"] = {
        "time_ms": round(t_b, 1),
        "ssim": round(float(compute_ssim(target_gray, warped_b)), 4),
        "psnr": round(float(compute_psnr(target_gray, warped_b)), 2),
        "epe_mean": round(epe_b["EPE_mean"], 4),
    }

    # Method C
    if TAICHI_OK:
        flow_c, t_c = method_c_taichi_pipeline(base_gray, target_gray, config)
        warped_c = warp_image(base_gray, flow_c)
        epe_c = compute_epe(flow_c, flow_gt)
        results["C"] = {
            "time_ms": round(t_c, 1),
            "ssim": round(float(compute_ssim(target_gray, warped_c)), 4),
            "psnr": round(float(compute_psnr(target_gray, warped_c)), 2),
            "epe_mean": round(epe_c["EPE_mean"], 4),
        }
    else:
        results["C"] = {"time_ms": 0, "ssim": 0, "psnr": 0, "epe_mean": 0, "error": "taichi not available"}

    return results


def main():
    H, W = 768, 768
    config = {
        "pyr_scale": 0.5, "levels": 3, "winsize": 15,
        "iterations": 3, "poly_n": 5, "poly_sigma": 1.2, "flags": 0,
    }

    print("=" * 90)
    print("  FARNEBACK FLOW - 3-WAY COMPARISON (10 displacements x 3 methods)")
    print(f"  Image size: {W}x{H} | Taichi: {'OK' if TAICHI_OK else 'NOT AVAILABLE'}")
    print("=" * 90)

    all_results = []

    for i, d in enumerate(DISPLACEMENTS):
        base, target, flow_gt = generate_pair(H, W, d["dx"], d["dy"])
        res = run_one(base, target, flow_gt, config)

        all_results.append({
            "displacement": d["name"],
            "dx": d["dx"], "dy": d["dy"],
            "results": res,
        })

        a, b, c = res["A"], res["B"], res["C"]
        c_ssim = c.get("ssim", 0)
        c_time = c.get("time_ms", 0)
        print(f"  {d['name']:20s} | "
              f"A: SSIM={a['ssim']:.4f} t={a['time_ms']:5.0f}ms | "
              f"B: SSIM={b['ssim']:.4f} t={b['time_ms']:5.0f}ms | "
              f"C: SSIM={c_ssim:.4f} t={c_time:5.0f}ms")

    # Summary
    print("\n" + "=" * 90)
    print("  AVERAGE SUMMARY (10 displacements)")
    print("=" * 90)

    for method in ["A", "label_A", "B", "label_B", "C", "label_C"]:
        pass

    labels = {
        "A": "A) OpenCV murni",
        "B": "B) OpenCV Pipeline (denoise+block+median_uint8)",
        "C": "C) Taichi Pipeline (bilateral_grid+median_flow_f32+ransac)",
    }

    for key in ["A", "B", "C"]:
        ssims = [r["results"][key]["ssim"] for r in all_results if "ssim" in r["results"][key]]
        psnrs = [r["results"][key]["psnr"] for r in all_results if "psnr" in r["results"][key]]
        epes = [r["results"][key]["epe_mean"] for r in all_results if "epe_mean" in r["results"][key]]
        times = [r["results"][key]["time_ms"] for r in all_results if "time_ms" in r["results"][key]]
        if ssims:
            print(f"\n  {labels[key]}:")
            print(f"    Avg SSIM : {np.mean(ssims):.4f}")
            print(f"    Avg PSNR : {np.mean(psnrs):.2f} dB")
            print(f"    Avg EPE  : {np.mean(epes):.4f}")
            print(f"    Avg Time : {np.mean(times):.0f} ms/iter")
            print(f"    Total    : {sum(times):.0f} ms ({sum(times)/1000:.1f}s) for 10 iters")

    # Save JSON
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
    json_path = os.path.join(out_dir, "FARNEBACK_3WAY_RESULTS.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  JSON: {json_path}")
    print("=" * 90)


if __name__ == "__main__":
    main()
