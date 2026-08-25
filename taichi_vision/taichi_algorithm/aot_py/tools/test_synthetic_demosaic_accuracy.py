"""Synthetic Demosaic Accuracy & Multi-Backend Performance Benchmark

Generates ground-truth synthetic test patterns (Siemens Star, Color Checker, Zone Plate),
simulates RGGB Bayer sensor mosaic, and evaluates demosaicing algorithms (Hamilton, ARM,
DCB, MLRI) across available backends.

Metrics:
- L1 Loss x 4: 4 * Mean(|Pred - GT|) to amplify color reconstruction error.
- PSNR (dB): Peak Signal-to-Noise Ratio.
- Max Error: Absolute maximum pixel error.
- Latency (ms): Execution time per frame.
"""

import os
import sys
import time
import numpy as np

# Ensure project root is in python path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import taichi_vision.taichi_aot as ta_aot


def generate_siemens_star(size=512, spokes=32):
    """Generate Siemens Star radial pattern (0.0 to 1.0 float32 RGB)."""
    y, x = np.ogrid[:size, :size]
    cy, cx = size / 2.0, size / 2.0
    angle = np.arctan2(y - cy, x - cx)
    radius = np.hypot(y - cy, x - cx)

    pattern = 0.5 + 0.5 * np.cos(spokes * angle)
    pattern = np.where(radius < 4.0, 0.5, pattern)

    rgb = np.zeros((size, size, 3), dtype=np.float32)
    rgb[:, :, 0] = pattern
    rgb[:, :, 1] = np.roll(pattern, shift=10, axis=0)
    rgb[:, :, 2] = 1.0 - pattern
    return np.clip(rgb, 0.0, 1.0).astype(np.float32)


def generate_color_checker(size=512):
    """Generate Macbeth-like 4x6 color patch grid (0.0 to 1.0 float32 RGB)."""
    grid = np.zeros((size, size, 3), dtype=np.float32)
    rows, cols = 4, 6
    ph, pw = size // rows, size // cols

    colors = [
        [0.45, 0.32, 0.24],
        [0.76, 0.57, 0.49],
        [0.38, 0.48, 0.61],
        [0.35, 0.42, 0.28],
        [0.52, 0.49, 0.67],
        [0.38, 0.74, 0.66],
        [0.85, 0.47, 0.18],
        [0.28, 0.35, 0.67],
        [0.76, 0.36, 0.38],
        [0.36, 0.23, 0.41],
        [0.62, 0.74, 0.26],
        [0.87, 0.63, 0.19],
        [0.17, 0.25, 0.56],
        [0.28, 0.58, 0.28],
        [0.69, 0.21, 0.22],
        [0.91, 0.79, 0.16],
        [0.73, 0.34, 0.57],
        [0.18, 0.52, 0.62],
        [0.95, 0.95, 0.95],
        [0.78, 0.78, 0.78],
        [0.62, 0.62, 0.62],
        [0.47, 0.47, 0.47],
        [0.33, 0.33, 0.33],
        [0.13, 0.13, 0.13],
    ]

    idx = 0
    for r in range(rows):
        for c in range(cols):
            color = colors[idx % len(colors)]
            grid[r * ph : (r + 1) * ph, c * pw : (c + 1) * pw, :] = color
            idx += 1
    return grid


def generate_zone_plate(size=512):
    """Generate zone plate concentric frequency sweep."""
    y, x = np.ogrid[:size, :size]
    cy, cx = size / 2.0, size / 2.0
    r2 = (x - cx) ** 2 + (y - cy) ** 2
    pattern = 0.5 + 0.5 * np.cos(0.005 * r2)

    rgb = np.zeros((size, size, 3), dtype=np.float32)
    rgb[:, :, 0] = pattern
    rgb[:, :, 1] = pattern
    rgb[:, :, 2] = pattern
    return rgb.astype(np.float32)


def rgb_to_rggb_bayer(rgb):
    """Simulate RGGB 2D Bayer Mosaic from RGB image."""
    h, w, _ = rgb.shape
    bayer = np.zeros((h, w), dtype=np.float32)

    bayer[0::2, 0::2] = rgb[0::2, 0::2, 0]
    bayer[0::2, 1::2] = rgb[0::2, 1::2, 1]
    bayer[1::2, 0::2] = rgb[1::2, 0::2, 1]
    bayer[1::2, 1::2] = rgb[1::2, 1::2, 2]
    return bayer


def evaluate_demosaic(pattern_name, gt_rgb, method, backend_name):
    """Run demosaic evaluation for a specific algorithm and pattern."""
    bayer = rgb_to_rggb_bayer(gt_rgb)
    cmatrix = np.eye(3, dtype=np.float32)

    try:
        # Warmup run
        pred = ta_aot.demosaic(
            bayer,
            wb_r=1.0,
            wb_g1=1.0,
            wb_b=1.0,
            wb_g2=1.0,
            cmatrix=cmatrix,
            black_level=0.0,
            white_level=1.0,
            c00=0,
            c01=1,
            c10=1,
            c11=2,
            method=method,
            return_gpu=False,
        )
    except Exception as e:
        return {
            "method": method,
            "pattern": pattern_name,
            "backend": backend_name,
            "error": str(e),
            "status": "FAILED",
        }

    # Benchmark runs (5 iterations)
    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        pred = ta_aot.demosaic(
            bayer,
            wb_r=1.0,
            wb_g1=1.0,
            wb_b=1.0,
            wb_g2=1.0,
            cmatrix=cmatrix,
            black_level=0.0,
            white_level=1.0,
            c00=0,
            c01=1,
            c10=1,
            c11=2,
            method=method,
            return_gpu=False,
        )
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)

    avg_ms = np.mean(times)

    if pred.shape != gt_rgb.shape:
        return {
            "method": method,
            "pattern": pattern_name,
            "backend": backend_name,
            "error": f"Shape mismatch: {pred.shape} vs {gt_rgb.shape}",
            "status": "FAILED",
        }

    border = 8
    p_crop = pred[border:-border, border:-border]
    g_crop = gt_rgb[border:-border, border:-border]

    abs_diff = np.abs(p_crop - g_crop)
    l1_loss_x4 = 4.0 * np.mean(abs_diff)

    mse = np.mean((p_crop - g_crop) ** 2)
    psnr = 20.0 * np.log10(1.0 / np.sqrt(mse + 1e-10))
    max_err = np.max(abs_diff)

    return {
        "method": method,
        "pattern": pattern_name,
        "backend": backend_name,
        "l1_loss_x4": l1_loss_x4,
        "psnr_db": psnr,
        "max_err": max_err,
        "latency_ms": avg_ms,
        "status": "SUCCESS",
    }


def main():
    print("=" * 90)
    print("  PIXEL REFINE: SYNTHETIC DEMOSAIC ACCURACY & MULTI-BACKEND BENCHMARK")
    print("=" * 90)

    patterns = {
        "Siemens Star": generate_siemens_star(512),
        "Color Checker": generate_color_checker(512),
        "Zone Plate": generate_zone_plate(512),
    }

    algorithms = ["hamilton", "arm", "dcb", "mlri"]
    backends_to_test = ["cpu", "vulkan", "cuda", "opengl"]

    results = []

    for backend in backends_to_test:
        os.environ["AOT_ARCH"] = backend
        print(f"\n---> Testing Backend Environment: [{backend.upper()}] <---")

        for pat_name, gt_rgb in patterns.items():
            for alg in algorithms:
                res = evaluate_demosaic(pat_name, gt_rgb, alg, backend)
                results.append(res)
                if res["status"] == "SUCCESS":
                    print(
                        f"  [{backend.upper():<6}] {res['method']:<10} | Pattern: {res['pattern']:<14} | "
                        f"L1_Loss_x4: {res['l1_loss_x4']:.4f} | PSNR: {res['psnr_db']:.2f} dB | "
                        f"MaxErr: {res['max_err']:.3f} | Time: {res['latency_ms']:.2f} ms"
                    )
                else:
                    print(
                        f"  [{backend.upper():<6}] {res['method']:<10} | Pattern: {res['pattern']:<14} | "
                        f"Status: FAILED ({res['error']})"
                    )

    print("\n" + "=" * 90)
    print("  SUMMARY TABLE: DEMOSAIC ACCURACY (L1 Loss x 4)")
    print("=" * 90)
    print(
        f"{'Backend':<8} | {'Algorithm':<10} | {'Siemens Star L1x4':<18} | {'Color Checker L1x4':<18} | {'Zone Plate L1x4':<18}"
    )
    print("-" * 90)

    for backend in backends_to_test:
        for alg in algorithms:
            s_star = next(
                (
                    r
                    for r in results
                    if r["backend"] == backend
                    and r["method"] == alg
                    and r["pattern"] == "Siemens Star"
                ),
                None,
            )
            c_check = next(
                (
                    r
                    for r in results
                    if r["backend"] == backend
                    and r["method"] == alg
                    and r["pattern"] == "Color Checker"
                ),
                None,
            )
            z_plate = next(
                (
                    r
                    for r in results
                    if r["backend"] == backend
                    and r["method"] == alg
                    and r["pattern"] == "Zone Plate"
                ),
                None,
            )

            s_str = (
                f"{s_star['l1_loss_x4']:.4f}"
                if s_star and s_star["status"] == "SUCCESS"
                else "N/A"
            )
            c_str = (
                f"{c_check['l1_loss_x4']:.4f}"
                if c_check and c_check["status"] == "SUCCESS"
                else "N/A"
            )
            z_str = (
                f"{z_plate['l1_loss_x4']:.4f}"
                if z_plate and z_plate["status"] == "SUCCESS"
                else "N/A"
            )

            print(
                f"{backend.upper():<8} | {alg:<10} | {s_str:<18} | {c_str:<18} | {z_str:<18}"
            )


if __name__ == "__main__":
    main()
