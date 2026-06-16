# -*- coding: utf-8 -*-
"""
FARNEBACK PRODUCTION TEST - After Taichi Integration
Tests FarnebackAlgorithm.calculate_optical_flow() directly
with block tiling ON + Taichi GPU acceleration.
"""
import os, sys, time, json, cv2, numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

os.environ["AOT_MODE"] = "0"

from farneback_flow_accuracy_test import (
    compute_flow_opencv_direct, compute_flow_pipeline,
    compute_epe, compute_psnr, compute_ssim, warp_image,
)

DISPLACEMENTS = [
    {"name": "D01_tiny",     "dx": 2,   "dy": 0},
    {"name": "D02_small",    "dx": 3,   "dy": 2},
    {"name": "D03_med_h",    "dx": 5,   "dy": 0},
    {"name": "D04_med_d",    "dx": 5,   "dy": 3},
    {"name": "D05_left",     "dx": -4,  "dy": 1},
    {"name": "D06_large_h",  "dx": 8,   "dy": 0},
    {"name": "D07_large_d",  "dx": 7,   "dy": 5},
    {"name": "D08_up",       "dx": 2,   "dy": -6},
    {"name": "D09_extreme",  "dx": 10,  "dy": 8},
    {"name": "D10_subpx",    "dx": 1.5, "dy": 0.7},
]


def gen(h, w, dx, dy):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.clip(
        128 + 55*np.sin(2*np.pi*xx/80)*np.cos(2*np.pi*yy/120)
        + 35*np.sin(2*np.pi*xx/40 + yy/60)
        + 25*np.cos(2*np.pi*(xx+yy)/200)
        + 20*np.sin(2*np.pi*xx/30)*np.sin(2*np.pi*yy/50), 0, 255
    ).astype(np.uint8)
    base[150:280, 150:320] += 70
    base[350:420, 100:250] += 50
    flow_gt = np.zeros((h, w, 2), dtype=np.float32)
    flow_gt[:,:,0], flow_gt[:,:,1] = dx, dy
    target = warp_image(base, flow_gt, cv2.INTER_CUBIC)
    target = np.clip(target.astype(np.float32) + np.random.randn(h,w).astype(np.float32)*1.5, 0, 255).astype(np.uint8)
    return base, target, flow_gt


def test_farneback_algo(base, target, config):
    """Call FarnebackAlgorithm.calculate_optical_flow directly."""
    # Import from same directory
    from Farneback_optical_flow import FarnebackAlgorithm
    algo = FarnebackAlgorithm.__new__(FarnebackAlgorithm)
    algo.db_path, algo.hdf5_path = "", ""
    
    gray_base = base if base.ndim == 2 else cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    gray_target = target if target.ndim == 2 else cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    
    t0 = time.perf_counter()
    flow = algo.calculate_optical_flow(
        gray_base.astype(np.float32), gray_target.astype(np.float32),
        config_filename=None, stop_requested=None
    )
    ms = (time.perf_counter() - t0) * 1000
    return flow, ms


def main():
    H, W = 768, 768
    cfg = {"pyr_scale": 0.5, "levels": 3, "winsize": 15,
           "iterations": 3, "poly_n": 5, "poly_sigma": 1.2, "flags": 0}

    # Check taichi
    try:
        from Farneback_optical_flow import TAICHI_AVAILABLE
        taichi = TAICHI_AVAILABLE
    except:
        taichi = False

    print("=" * 90)
    print(f"  FARNEBACK PRODUCTION TEST | {W}x{H} | Taichi: {taichi}")
    print("=" * 90)

    A, B = [], []

    for d in DISPLACEMENTS:
        base, tgt, gt = gen(H, W, d["dx"], d["dy"])

        # A) OpenCV murni
        fa, ta = compute_flow_opencv_direct(base, tgt, cfg)
        wa = warp_image(base, fa)
        ea = compute_epe(fa, gt)
        sa = round(float(compute_ssim(tgt, wa)), 4)

        # B) Production FarnebackAlgorithm (Taichi + block tiling)
        sb, tb, pb = 0, 0, 0
        try:
            fb, tb = test_farneback_algo(base, tgt, cfg)
            if fb is not None:
                wb = warp_image(base, fb)
                sb = round(float(compute_ssim(tgt, wb)), 4)
                pb = round(float(compute_psnr(tgt, wb)), 2)
        except Exception as e:
            print(f"  [ERR] {d['name']}: {e}")

        A.append({"ssim": sa, "time": ta})
        B.append({"ssim": sb, "psnr": pb, "time": tb})

        m = lambda v: "**" if v >= 0.95 else ("* " if v >= 0.90 else ("." if v >= 0.85 else " "))
        print(f"  {d['name']:12s} | A: SSIM={sa:.4f}{m(sa)} {ta:5.0f}ms | "
              f"B: SSIM={sb:.4f}{m(sb)} {tb:5.0f}ms")

    # Summary
    a_ss = [r["ssim"] for r in A]
    b_ss = [r["ssim"] for r in B if r["ssim"] > 0]
    a_t  = [r["time"] for r in A]
    b_t  = [r["time"] for r in B if r["time"] > 0]

    print("\n" + "=" * 90)
    print(f"  A) OpenCV murni     | Avg SSIM={np.mean(a_ss):.4f} | Avg Time={np.mean(a_t):.0f}ms")
    if b_ss:
        print(f"  B) Farneback+Taichi | Avg SSIM={np.mean(b_ss):.4f} | Avg Time={np.mean(b_t):.0f}ms")
    else:
        print(f"  B) Farneback+Taichi | FAILED")
    print("=" * 90)


if __name__ == "__main__":
    main()
