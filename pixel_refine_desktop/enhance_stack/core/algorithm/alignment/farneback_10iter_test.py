# -*- coding: utf-8 -*-
"""
FARNEBACK OPTICAL FLOW - 10 ITERATIONS + ACCURACY TUNING TO 0.95 SSIM

10 pasang citra sintetis dengan displacement berbeda-beda.
Beberapa strategi tuning untuk mendorong SSIM mendekati 0.95.
"""

import os
import sys
import time
import json
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farneback_flow_accuracy_test import (
    compute_flow_opencv_direct,
    compute_flow_pipeline,
    compute_epe,
    compute_psnr,
    compute_ssim,
    warp_image,
    flow_to_color,
)


# ---------------------------------------------------------------------------
# 10 displacement configurations
# ---------------------------------------------------------------------------
DISPLACEMENTS = [
    {"name": "D01_tiny_right",    "dx": 2,  "dy": 0,  "desc": "2px horizontal kanan"},
    {"name": "D02_small_diag",    "dx": 3,  "dy": 2,  "desc": "3x2 diagonal kecil"},
    {"name": "D03_medium_right",  "dx": 5,  "dy": 0,  "desc": "5px horizontal"},
    {"name": "D04_medium_diag",   "dx": 5,  "dy": 3,  "desc": "5x3 diagonal (standar)"},
    {"name": "D05_medium_left",   "dx": -4, "dy": 1,  "desc": "-4x1 kiri + turun"},
    {"name": "D06_large_right",   "dx": 8,  "dy": 0,  "desc": "8px horizontal besar"},
    {"name": "D07_large_diag",    "dx": 7,  "dy": 5,  "desc": "7x5 diagonal besar"},
    {"name": "D08_large_up",      "dx": 2,  "dy": -6, "desc": "2x-6 naik"},
    {"name": "D09_extreme_diag",  "dx": 10, "dy": 8,  "desc": "10x8 extreme"},
    {"name": "D10_subpixel",      "dx": 1.5,"dy": 0.7,"desc": "1.5x0.7 sub-pixel"},
]


def generate_pair(h, w, dx, dy, noise_sigma=1.5):
    """Generate base+target dengan displacement diketahui."""
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


# ---------------------------------------------------------------------------
# Tuning configs — progression toward SSIM 0.95
# ---------------------------------------------------------------------------
TUNING_CONFIGS = [
    {
        "name": "Config_A_Default",
        "desc": "Default seperti production (baseline)",
        "config": {
            "pyr_scale": 0.5, "levels": 3, "winsize": 15,
            "iterations": 3, "poly_n": 5, "poly_sigma": 1.2, "flags": 0,
            "cpu_num_blocks_x": 1, "cpu_num_blocks_y": 1,
            "cpu_overlap_ratio": 0.0, "flow_smoothing_kernel": 5,
        }
    },
    {
        "name": "Config_B_MoreLevels",
        "desc": "Lebih banyak pyramid levels untuk menangkap motion besar",
        "config": {
            "pyr_scale": 0.5, "levels": 5, "winsize": 15,
            "iterations": 3, "poly_n": 5, "poly_sigma": 1.2, "flags": 0,
            "cpu_num_blocks_x": 1, "cpu_num_blocks_y": 1,
            "cpu_overlap_ratio": 0.0, "flow_smoothing_kernel": 5,
        }
    },
    {
        "name": "Config_C_MoreIter",
        "desc": "Lebih banyak iterasi refinement per level",
        "config": {
            "pyr_scale": 0.5, "levels": 4, "winsize": 19,
            "iterations": 5, "poly_n": 5, "poly_sigma": 1.2, "flags": 0,
            "cpu_num_blocks_x": 1, "cpu_num_blocks_y": 1,
            "cpu_overlap_ratio": 0.0, "flow_smoothing_kernel": 5,
        }
    },
    {
        "name": "Config_D_LargePoly",
        "desc": "Poly_n besar + poly_sigma besar untuk akurasi tinggi",
        "config": {
            "pyr_scale": 0.5, "levels": 5, "winsize": 21,
            "iterations": 5, "poly_n": 7, "poly_sigma": 1.5, "flags": 0,
            "cpu_num_blocks_x": 1, "cpu_num_blocks_y": 1,
            "cpu_overlap_ratio": 0.0, "flow_smoothing_kernel": 5,
        }
    },
    {
        "name": "Config_E_MaxAccuracy",
        "desc": "Maximum: levels=6, winsize=25, iter=7, poly_n=9",
        "config": {
            "pyr_scale": 0.5, "levels": 6, "winsize": 25,
            "iterations": 7, "poly_n": 9, "poly_sigma": 1.8, "flags": 0,
            "cpu_num_blocks_x": 1, "cpu_num_blocks_y": 1,
            "cpu_overlap_ratio": 0.0, "flow_smoothing_kernel": 5,
        }
    },
    {
        "name": "Config_F_BestCombo",
        "desc": "Sweet spot: levels=5, winsize=21, iter=5, poly_n=7, pyr_scale=0.4",
        "config": {
            "pyr_scale": 0.4, "levels": 5, "winsize": 21,
            "iterations": 5, "poly_n": 7, "poly_sigma": 1.5, "flags": 0,
            "cpu_num_blocks_x": 1, "cpu_num_blocks_y": 1,
            "cpu_overlap_ratio": 0.0, "flow_smoothing_kernel": 3,
        }
    },
]


def run_one_test(base_gray, target_gray, flow_gt, config):
    """Jalankan 1 test, kembalikan dict hasil + timing."""
    # Method A
    t0 = time.perf_counter()
    flow_a, _ = compute_flow_opencv_direct(base_gray, target_gray, config)
    time_a = (time.perf_counter() - t0) * 1000

    warped_a = warp_image(base_gray, flow_a)

    # Method B (pipeline)
    t0 = time.perf_counter()
    flow_b, _ = compute_flow_pipeline(base_gray, target_gray, config)
    time_b = (time.perf_counter() - t0) * 1000

    warped_b = warp_image(base_gray, flow_b)

    epe_a = compute_epe(flow_a, flow_gt)
    epe_b = compute_epe(flow_b, flow_gt)

    return {
        "time_a_ms": round(time_a, 1),
        "time_b_ms": round(time_b, 1),
        "ssim_target_vs_a": round(float(compute_ssim(target_gray, warped_a)), 4),
        "ssim_target_vs_b": round(float(compute_ssim(target_gray, warped_b)), 4),
        "psnr_target_vs_a": round(float(compute_psnr(target_gray, warped_a)), 2),
        "psnr_target_vs_b": round(float(compute_psnr(target_gray, warped_b)), 2),
        "epe_a_mean": round(epe_a["EPE_mean"], 4),
        "epe_b_mean": round(epe_b["EPE_mean"], 4),
    }


def main():
    H, W = 768, 768
    print("=" * 75)
    print("  FARNEBACK FLOW - 10 ITERATIONS x 6 CONFIGS = 60 TEST RUNS")
    print(f"  Image size: {W}x{H}")
    print("=" * 75)

    all_results = []

    for cfg_idx, cfg_info in enumerate(TUNING_CONFIGS):
        print(f"\n{'='*75}")
        print(f"  CONFIG {cfg_idx+1}/{len(TUNING_CONFIGS)}: {cfg_info['name']}")
        print(f"  {cfg_info['desc']}")
        c = cfg_info["config"]
        print(f"  levels={c['levels']}, winsize={c['winsize']}, iter={c['iterations']}, "
              f"poly_n={c['poly_n']}, poly_sigma={c['poly_sigma']}, "
              f"pyr_scale={c['pyr_scale']}")
        print(f"{'='*75}")

        config_results = []
        total_time_a = 0
        total_time_b = 0

        for d in DISPLACEMENTS:
            base, target, flow_gt = generate_pair(H, W, d["dx"], d["dy"])
            res = run_one_test(base, target, flow_gt, cfg_info["config"])
            res["displacement"] = d["name"]
            res["dx"] = d["dx"]
            res["dy"] = d["dy"]
            res["config_name"] = cfg_info["name"]
            config_results.append(res)
            total_time_a += res["time_a_ms"]
            total_time_b += res["time_b_ms"]

            status = "OK" if res["ssim_target_vs_b"] >= 0.90 else "  "
            status2 = "**" if res["ssim_target_vs_b"] >= 0.95 else status
            print(f"  {d['name']:25s} | dx={d['dx']:5.1f} dy={d['dy']:5.1f} | "
                  f"SSIM_B={res['ssim_target_vs_b']:.4f} | "
                  f"PSNR_B={res['psnr_target_vs_b']:5.1f} | "
                  f"tA={res['time_a_ms']:6.0f}ms tB={res['time_b_ms']:6.0f}ms | "
                  f"{status2}")

        # Summary per config
        avg_ssim_a = np.mean([r["ssim_target_vs_a"] for r in config_results])
        avg_ssim_b = np.mean([r["ssim_target_vs_b"] for r in config_results])
        avg_psnr_b = np.mean([r["psnr_target_vs_b"] for r in config_results])
        avg_epe_b = np.mean([r["epe_b_mean"] for r in config_results])
        avg_time_a = total_time_a / len(config_results)
        avg_time_b = total_time_b / len(config_results)

        print(f"\n  --- SUMMARY {cfg_info['name']} ---")
        print(f"  Avg SSIM Target vs A (murni) : {avg_ssim_a:.4f}")
        print(f"  Avg SSIM Target vs B (pipe)  : {avg_ssim_b:.4f} {'*** TARGET 0.95 ***' if avg_ssim_b >= 0.95 else '(target: 0.95)'}")
        print(f"  Avg PSNR Target vs B         : {avg_psnr_b:.2f} dB")
        print(f"  Avg EPE B vs GT              : {avg_epe_b:.4f}")
        print(f"  Avg Time A                   : {avg_time_a:.0f} ms")
        print(f"  Avg Time B                   : {avg_time_b:.0f} ms")
        print(f"  Total 10 iters A             : {total_time_a:.0f} ms ({total_time_a/1000:.1f}s)")
        print(f"  Total 10 iters B             : {total_time_b:.0f} ms ({total_time_b/1000:.1f}s)")

        all_results.append({
            "config_name": cfg_info["name"],
            "config_desc": cfg_info["desc"],
            "config_params": cfg_info["config"],
            "avg_ssim_a": round(float(avg_ssim_a), 4),
            "avg_ssim_b": round(float(avg_ssim_b), 4),
            "avg_psnr_b": round(float(avg_psnr_b), 2),
            "avg_epe_b": round(float(avg_epe_b), 4),
            "avg_time_a_ms": round(float(avg_time_a), 1),
            "avg_time_b_ms": round(float(avg_time_b), 1),
            "total_time_a_ms": round(float(total_time_a), 1),
            "total_time_b_ms": round(float(total_time_b), 1),
            "per_displacement": config_results,
        })

    # ===================================================================
    # FINAL COMPARISON TABLE
    # ===================================================================
    print("\n" + "=" * 75)
    print("  FINAL COMPARISON - ALL CONFIGS (avg of 10 displacements)")
    print("=" * 75)
    print(f"  {'Config':<25s} | Avg SSIM_B | Avg PSNR_B | Avg EPE_B | Avg Time_B | Hit 0.95?")
    print(f"  {'-'*25}-+-{'-'*10}-+-{'-'*10}-+-{'-'*9}-+-{'-'*10}-+-{'-'*10}")
    for r in all_results:
        hit = "YES" if r["avg_ssim_b"] >= 0.95 else ("~OK" if r["avg_ssim_b"] >= 0.93 else "NO")
        print(f"  {r['config_name']:<25s} | {r['avg_ssim_b']:.4f}   | {r['avg_psnr_b']:.2f} dB  | {r['avg_epe_b']:.4f}   | {r['avg_time_b_ms']:7.0f}ms | {hit}")

    # Find best
    best = max(all_results, key=lambda r: r["avg_ssim_b"])
    fastest = min(all_results, key=lambda r: r["avg_time_b_ms"])
    best_ssim_95 = [r for r in all_results if r["avg_ssim_b"] >= 0.95]

    print()
    print(f"  Best SSIM     : {best['config_name']} ({best['avg_ssim_b']:.4f})")
    print(f"  Fastest       : {fastest['config_name']} ({fastest['avg_time_b_ms']:.0f} ms/iter)")
    if best_ssim_95:
        best_of_95 = min(best_ssim_95, key=lambda r: r["avg_time_b_ms"])
        print(f"  Best >= 0.95  : {best_of_95['config_name']} (SSIM={best_of_95['avg_ssim_b']:.4f}, time={best_of_95['avg_time_b_ms']:.0f}ms)")
    else:
        print(f"  Best >= 0.95  : BELUM TERCAPAI (terbaik: {best['avg_ssim_b']:.4f})")

    # Save JSON
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
    json_path = os.path.join(out_dir, "FARNEBACK_10ITER_RESULTS.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  JSON: {json_path}")
    print("=" * 75)


if __name__ == "__main__":
    main()
