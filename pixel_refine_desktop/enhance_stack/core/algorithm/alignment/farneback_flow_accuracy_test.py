# -*- coding: utf-8 -*-
"""
FARNEBACK OPTICAL FLOW - ACCURACY COMPARISON STANDALONE

Membandingkan 2 pendekatan:
  A) OpenCV murni  - cv2.calcOpticalFlowFarneback langsung
  B) Pipeline lengkap: denoise -> block tiling -> median smoothing

Metrik:
  - EPE  (Endpoint Error) - jika ground truth tersedia
  - PSNR / SSIM antara 2 warped image hasil pipeline A vs B
  - Flow difference antara A dan B
  - Max flow magnitude
  - Waktu komputasi (ms)

Cara pakai:
  python farneback_flow_accuracy_test.py --base <img1> --target <img2>
  python farneback_flow_accuracy_test.py --base <img1> --target <img2> --gt <flow_gt.npy>
  python farneback_flow_accuracy_test.py --demo

Requirements: opencv-python, numpy
  (scikit-image optional - untuk SSIM akurat)
"""

import argparse
import os
import sys
import time

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

def compute_epe(flow_pred, flow_gt):
    """Endpoint Error (EPE) - hanya valid jika ground truth tersedia."""
    diff = flow_pred.astype(np.float64) - flow_gt.astype(np.float64)
    epe_map = np.sqrt(np.sum(diff ** 2, axis=-1))
    return {
        "EPE_mean": float(np.mean(epe_map)),
        "EPE_median": float(np.median(epe_map)),
        "EPE_max": float(np.max(epe_map)),
        "EPE_map": epe_map.astype(np.float32),
    }


def compute_psnr(img_a, img_b):
    """Peak Signal-to-Noise Ratio antara 2 citra."""
    a = img_a.astype(np.float64)
    b = img_b.astype(np.float64)
    mse = np.mean((a - b) ** 2)
    if mse == 0:
        return float("inf")
    return float(10.0 * np.log10(255.0 ** 2 / mse))


def compute_ssim(img_a, img_b):
    """Structural Similarity Index.
    Gunakan scikit-image jika ada, fallback ke correlation.
    """
    try:
        from skimage.metrics import structural_similarity as ssim_func
        if img_a.ndim == 3:
            a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
            b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)
        else:
            a, b = img_a, img_b
        return float(ssim_func(a, b, data_range=255))
    except ImportError:
        a = img_a.astype(np.float64).ravel()
        b = img_b.astype(np.float64).ravel()
        a = (a - a.mean()) / (a.std() + 1e-8)
        b = (b - b.mean()) / (b.std() + 1e-8)
        return float(np.mean(a * b))


# ---------------------------------------------------------------------------
# Flow helpers
# ---------------------------------------------------------------------------

def flow_to_color(flow):
    """Konversi optical flow field ke citra berwarna untuk visualisasi."""
    hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 1] = 255
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def warp_image(image, flow, interpolation=cv2.INTER_LINEAR):
    """Warp gambar menggunakan optical flow field."""
    h, w = flow.shape[:2]
    grid_y, grid_x = np.mgrid[0:h, 0:w].astype(np.float32)
    map_x = grid_x + flow[:, :, 0]
    map_y = grid_y + flow[:, :, 1]
    return cv2.remap(image, map_x, map_y, interpolation=interpolation,
                     borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------------------
# Method A: OpenCV Farneback murni
# ---------------------------------------------------------------------------

def compute_flow_opencv_direct(base_gray, target_gray, config):
    """OpenCV Farneback murni - tanpa denoise, block tiling, atau smoothing."""
    t0 = time.perf_counter()
    flow = cv2.calcOpticalFlowFarneback(
        base_gray, target_gray, None,
        pyr_scale=config["pyr_scale"],
        levels=config["levels"],
        winsize=config["winsize"],
        iterations=config["iterations"],
        poly_n=config["poly_n"],
        poly_sigma=config["poly_sigma"],
        flags=config["flags"],
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return flow, elapsed_ms


# ---------------------------------------------------------------------------
# Method B: Pipeline lengkap (mirip FarnebackAlgorithm)
# ---------------------------------------------------------------------------

def estimate_noise_level(gray_8bit):
    """Estimasi noise level menggunakan median absolute deviation (MAD).
    Mirip dengan estimate_noise_variance di global_feature.py.
    """
    h, w = gray_8bit.shape
    # Ambil patch kecil 3x3 di beberapa lokasi acak
    block_size = 3
    patches = []
    for yy in range(0, h - block_size, block_size):
        for xx in range(0, w - block_size, block_size):
            patch = gray_8bit[yy:yy+block_size, xx:xx+block_size].astype(np.float64)
            # Laplacian variance sebagai estimasi noise
            lap = cv2.Laplacian(patch, cv2.CV_64F)
            patches.append(np.var(lap))
            if len(patches) > 5000:
                break
        if len(patches) > 5000:
            break
    # noise variance ~= median of laplacian variance / (sigma^2 of laplacian kernel)
    # Empirically: scale factor ~ 1/6.0 for 3x3 Laplacian
    noise_var = np.median(patches) / 6.0
    return float(np.sqrt(max(noise_var, 0.0)))


def compute_flow_pipeline(base_gray, target_gray, config):
    """
    Pipeline lengkap mirip FarnebackAlgorithm:
      1. Konversi ke grayscale 8-bit
      2. Denoise dengan bilateral filter adaptif
      3. Block tiling dengan overlap
      4. Median smoothing
    """
    t0 = time.perf_counter()

    # --- 1. Pastikan grayscale 8-bit ---
    base_8bit = base_gray if base_gray.dtype == np.uint8 else (
        (base_gray * 255).astype(np.uint8) if base_gray.max() <= 1.0
        else base_gray.astype(np.uint8)
    )
    target_8bit = target_gray if target_gray.dtype == np.uint8 else (
        (target_gray * 255).astype(np.uint8) if target_gray.max() <= 1.0
        else target_gray.astype(np.uint8)
    )

    # --- 2. Denoise adaptif ---
    def adaptive_denoise(img):
        noise_level = estimate_noise_level(img)
        min_noise_threshold = 200.0
        max_noise_threshold = 700.0
        if noise_level > min_noise_threshold:
            # Map noise -> bilateral params (same logic as project)
            ratio = min(1.0, (noise_level - min_noise_threshold) /
                        (max_noise_threshold - min_noise_threshold))
            d = int(5 + ratio * (9 - 5))
            sigma_color = 20 + ratio * (75 - 20)
            sigma_space = 20 + ratio * (75 - 20)
            if d % 2 == 0:
                d += 1
            return cv2.bilateralFilter(img, d, sigma_color, sigma_space)
        return img.copy()

    base_denoised = adaptive_denoise(base_8bit)
    target_denoised = adaptive_denoise(target_8bit)

    # --- 3. Block tiling dengan overlap ---
    h, w = base_denoised.shape
    num_blocks_x = config.get("cpu_num_blocks_x", 10)
    num_blocks_y = config.get("cpu_num_blocks_y", 8)
    overlap_ratio = config.get("cpu_overlap_ratio", 0.3)

    block_w = w // num_blocks_x
    block_h = h // num_blocks_y
    if block_w == 0 or block_h == 0:
        num_blocks_x, num_blocks_y = 1, 1
        block_w, block_h = w, h

    flow_full = np.zeros((h, w, 2), dtype=np.float32)

    for bi in range(num_blocks_x):
        for bj in range(num_blocks_y):
            x = bi * block_w
            y = bj * block_h
            bw = block_w if bi < num_blocks_x - 1 else w - x
            bh = block_h if bj < num_blocks_y - 1 else h - y

            ov_x = int(bw * overlap_ratio)
            ov_y = int(bh * overlap_ratio)
            x0 = max(0, x - ov_x)
            y0 = max(0, y - ov_y)
            x1 = min(w, x + bw + ov_x)
            y1 = min(h, y + bh + ov_y)

            roi_base = base_denoised[y0:y1, x0:x1]
            roi_target = target_denoised[y0:y1, x0:x1]

            if roi_base.size == 0 or roi_target.size == 0:
                continue

            flow_roi = cv2.calcOpticalFlowFarneback(
                roi_base, roi_target, None,
                pyr_scale=config["pyr_scale"],
                levels=config["levels"],
                winsize=config["winsize"],
                iterations=config["iterations"],
                poly_n=config["poly_n"],
                poly_sigma=config["poly_sigma"],
                flags=config["flags"],
            )

            ox = x - x0
            oy = y - y0
            bh_v = min(bh, flow_roi.shape[0] - oy)
            bw_v = min(bw, flow_roi.shape[1] - ox)
            if bh_v > 0 and bw_v > 0:
                flow_full[y:y + bh_v, x:x + bw_v] = flow_roi[oy:oy + bh_v, ox:ox + bw_v]

    # --- 4. Median smoothing (reverted - Gaussian blur merusak flow) ---
    # medianBlur efektif untuk outlier rejection di flow field.
    # Scale flow ke uint8, apply blur, lalu scale back.
    kernel_size = config.get("flow_smoothing_kernel", 5)
    if kernel_size % 2 == 0:
        kernel_size += 1
    flow_max = max(np.abs(flow_full).max(), 1e-6)
    flow_scaled = cv2.normalize(flow_full, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    fx, fy = cv2.split(flow_scaled)
    fx = cv2.medianBlur(fx, kernel_size)
    fy = cv2.medianBlur(fy, kernel_size)
    flow_smoothed = cv2.merge([fx, fy]).astype(np.float32)
    flow_full = flow_smoothed * (flow_max / 255.0)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return flow_full, elapsed_ms


# ---------------------------------------------------------------------------
# Synthetic demo - generate 2 images with known displacement
# ---------------------------------------------------------------------------

def generate_synthetic_pair(height=512, width=512, shift_x=5, shift_y=3,
                           noise_sigma=2.0):
    """Membuat sepasang citra sintetis dengan pergeseran terkontrol.
    Menghasilkan:
      - base_gray    : citra dasar (uint8)
      - target_gray  : citra yang digeser + noise (uint8)
      - flow_gt      : ground truth flow field (h, w, 2)
    """
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    base = (
        128
        + 60 * np.sin(2 * np.pi * x / 80) * np.cos(2 * np.pi * y / 120)
        + 40 * np.sin(2 * np.pi * x / 40 + y / 60)
        + 30 * np.cos(2 * np.pi * (x + y) / 200)
    ).astype(np.float32)
    # Tambah rectangle
    base[200:300, 200:350] += 80
    base = np.clip(base, 0, 255).astype(np.uint8)

    # Ground truth flow: konstan (shift_x, shift_y)
    flow_gt = np.zeros((height, width, 2), dtype=np.float32)
    flow_gt[:, :, 0] = shift_x
    flow_gt[:, :, 1] = shift_y

    # Warping manual untuk target
    target = warp_image(base, flow_gt, interpolation=cv2.INTER_CUBIC)

    # Tambah noise
    noise = np.random.randn(height, width).astype(np.float32) * noise_sigma
    target = np.clip(target.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return base, target, flow_gt


# ---------------------------------------------------------------------------
# Main comparison
# ---------------------------------------------------------------------------

def run_comparison(base_gray, target_gray, flow_gt=None, config=None,
                   output_dir="flow_test_output"):
    """Menjalankan perbandingan dan mencetak laporan metrik."""

    if config is None:
        config = {
            "pyr_scale": 0.5, "levels": 3, "winsize": 15,
            "iterations": 3, "poly_n": 5, "poly_sigma": 1.2, "flags": 0,
        }

    os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # A) OpenCV murni
    # ------------------------------------------------------------------
    print("=" * 70)
    print("  A) OpenCV calcOpticalFlowFarneback (murni)")
    print("=" * 70)
    flow_a, time_a_ms = compute_flow_opencv_direct(base_gray, target_gray, config)
    warped_a = warp_image(base_gray, flow_a)
    mag_a = np.sqrt(np.sum(flow_a ** 2, axis=-1))
    print(f"  Waktu komputasi : {time_a_ms:.1f} ms")
    print(f"  Flow shape      : {flow_a.shape}")
    print(f"  Flow dtype      : {flow_a.dtype}")
    print(f"  Flow min/max X  : [{flow_a[:,:,0].min():.3f}, {flow_a[:,:,0].max():.3f}]")
    print(f"  Flow min/max Y  : [{flow_a[:,:,1].min():.3f}, {flow_a[:,:,1].max():.3f}]")
    print(f"  Magnitude mean  : {mag_a.mean():.4f}")
    print(f"  Magnitude max   : {mag_a.max():.4f}")

    epe_a = None
    if flow_gt is not None:
        epe_a = compute_epe(flow_a, flow_gt)
        print(f"  EPE mean        : {epe_a['EPE_mean']:.4f}")
        print(f"  EPE median      : {epe_a['EPE_median']:.4f}")
        print(f"  EPE max         : {epe_a['EPE_max']:.4f}")

    # ------------------------------------------------------------------
    # B) Pipeline lengkap (denoise -> block tiling -> smoothing)
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("  B) Pipeline (denoise -> block tiling -> median smoothing)")
    print("=" * 70)

    flow_b, time_b_ms = compute_flow_pipeline(base_gray, target_gray, config)
    warped_b = warp_image(base_gray, flow_b)
    mag_b = np.sqrt(np.sum(flow_b ** 2, axis=-1))

    print(f"  Waktu komputasi : {time_b_ms:.1f} ms")
    print(f"  Flow shape      : {flow_b.shape}")
    print(f"  Flow dtype      : {flow_b.dtype}")
    print(f"  Flow min/max X  : [{flow_b[:,:,0].min():.3f}, {flow_b[:,:,0].max():.3f}]")
    print(f"  Flow min/max Y  : [{flow_b[:,:,1].min():.3f}, {flow_b[:,:,1].max():.3f}]")
    print(f"  Magnitude mean  : {mag_b.mean():.4f}")
    print(f"  Magnitude max   : {mag_b.max():.4f}")

    epe_b = None
    if flow_gt is not None:
        epe_b = compute_epe(flow_b, flow_gt)
        print(f"  EPE mean        : {epe_b['EPE_mean']:.4f}")
        print(f"  EPE median      : {epe_b['EPE_median']:.4f}")
        print(f"  EPE max         : {epe_b['EPE_max']:.4f}")

    # ------------------------------------------------------------------
    # C) Perbandingan A vs B
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("  PERBANDINGAN: A (murni) vs B (pipeline)")
    print("=" * 70)

    # Speed comparison
    speedup = time_b_ms / max(time_a_ms, 0.001)
    print(f"  Waktu A (ms)    : {time_a_ms:.1f}")
    print(f"  Waktu B (ms)    : {time_b_ms:.1f}")
    print(f"  Rasio B/A       : {speedup:.2f}x")

    # Flow diff
    flow_diff = flow_a - flow_b
    flow_diff_mag = np.sqrt(np.sum(flow_diff ** 2, axis=-1))
    print(f"  Flow diff mean  : {flow_diff_mag.mean():.4f}")
    print(f"  Flow diff max   : {flow_diff_mag.max():.4f}")
    print(f"  Flow diff std   : {flow_diff_mag.std():.4f}")

    # Warped image comparison (A vs B)
    if warped_a.shape == warped_b.shape:
        psnr_ab = compute_psnr(warped_a, warped_b)
        ssim_ab = compute_ssim(warped_a, warped_b)
        print(f"  PSNR (A vs B)   : {psnr_ab:.2f} dB")
        print(f"  SSIM (A vs B)   : {ssim_ab:.4f}")
    else:
        print(f"  [SKIP] warped shape mismatch: {warped_a.shape} vs {warped_b.shape}")

    # Target vs warped
    if base_gray.shape == warped_a.shape:
        psnr_target_vs_a = compute_psnr(target_gray, warped_a)
        psnr_target_vs_b = compute_psnr(target_gray, warped_b)
        ssim_target_vs_a = compute_ssim(target_gray, warped_a)
        ssim_target_vs_b = compute_ssim(target_gray, warped_b)
        print()
        print(f"  Target vs Warped_A PSNR : {psnr_target_vs_a:.2f} dB")
        print(f"  Target vs Warped_B PSNR : {psnr_target_vs_b:.2f} dB")
        print(f"  Target vs Warped_A SSIM : {ssim_target_vs_a:.4f}")
        print(f"  Target vs Warped_B SSIM : {ssim_target_vs_b:.4f}")

    # Ground truth comparison
    if flow_gt is not None and epe_a is not None and epe_b is not None:
        print()
        print(f"  EPE A vs GT (mean) : {epe_a['EPE_mean']:.4f}")
        print(f"  EPE B vs GT (mean) : {epe_b['EPE_mean']:.4f}")
        improvement = (1 - epe_b['EPE_mean'] / max(epe_a['EPE_mean'], 1e-8)) * 100
        print(f"  Pipeline improvement: {improvement:+.2f}%")

    # ------------------------------------------------------------------
    # Simpan visualisasi
    # ------------------------------------------------------------------
    print()
    print(f"  Menyimpan visualisasi ke: {output_dir}/")

    # Flow color maps
    cv2.imwrite(os.path.join(output_dir, "flow_a_opencv_direct.png"), flow_to_color(flow_a))
    cv2.imwrite(os.path.join(output_dir, "flow_b_pipeline.png"), flow_to_color(flow_b))

    # Diff map
    diff_vis = cv2.normalize(flow_diff_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    diff_color = cv2.applyColorMap(diff_vis, cv2.COLORMAP_JET)
    cv2.imwrite(os.path.join(output_dir, "flow_diff_A_vs_B.png"), diff_color)

    if flow_gt is not None:
        cv2.imwrite(os.path.join(output_dir, "flow_gt.png"), flow_to_color(flow_gt))
        if epe_a is not None:
            epe_vis = cv2.normalize(epe_a['EPE_map'], None, 0, 255,
                                   cv2.NORM_MINMAX).astype(np.uint8)
            cv2.imwrite(os.path.join(output_dir, "epe_map_A.png"),
                       cv2.applyColorMap(epe_vis, cv2.COLORMAP_JET))
        if epe_b is not None:
            epe_vis_b = cv2.normalize(epe_b['EPE_map'], None, 0, 255,
                                      cv2.NORM_MINMAX).astype(np.uint8)
            cv2.imwrite(os.path.join(output_dir, "epe_map_B.png"),
                       cv2.applyColorMap(epe_vis_b, cv2.COLORMAP_JET))

    # Warped images
    cv2.imwrite(os.path.join(output_dir, "warped_A_opencv_direct.png"), warped_a)
    cv2.imwrite(os.path.join(output_dir, "warped_B_pipeline.png"), warped_b)

    # Base & Target reference
    cv2.imwrite(os.path.join(output_dir, "base_gray.png"), base_gray)
    cv2.imwrite(os.path.join(output_dir, "target_gray.png"), target_gray)

    print("  [DONE] Selesai!")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Farneback Optical Flow - Accuracy Comparison (OpenCV murni vs Pipeline)"
    )
    parser.add_argument("--base", type=str, help="Path ke gambar base (reference)")
    parser.add_argument("--target", type=str, help="Path ke gambar target")
    parser.add_argument("--gt", type=str, default=None,
                        help="Path ke ground truth flow (.npy), shape (H,W,2) float32")
    parser.add_argument("--demo", action="store_true",
                        help="Gunakan citra sintetis untuk demo")
    parser.add_argument("--output", type=str, default="flow_test_output",
                        help="Direktori output visualisasi")

    # Farneback parameters (override defaults)
    parser.add_argument("--pyr-scale", type=float, default=0.5)
    parser.add_argument("--levels", type=int, default=3)
    parser.add_argument("--winsize", type=int, default=15)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--poly-n", type=int, default=5)
    parser.add_argument("--poly-sigma", type=float, default=1.2)

    # Pipeline parameters
    parser.add_argument("--blocks-x", type=int, default=10,
                        help="Jumlah blok horizontal untuk block tiling")
    parser.add_argument("--blocks-y", type=int, default=8,
                        help="Jumlah blok vertikal untuk block tiling")
    parser.add_argument("--overlap", type=float, default=0.3,
                        help="Overlap ratio antar blok (0.0 - 0.9)")
    parser.add_argument("--smooth-kernel", type=int, default=5,
                        help="Kernel size untuk median smoothing (ganjil)")

    args = parser.parse_args()

    config = {
        "pyr_scale": args.pyr_scale,
        "levels": args.levels,
        "winsize": args.winsize,
        "iterations": args.iterations,
        "poly_n": args.poly_n,
        "poly_sigma": args.poly_sigma,
        "flags": 0,
        # Pipeline-specific
        "cpu_num_blocks_x": args.blocks_x,
        "cpu_num_blocks_y": args.blocks_y,
        "cpu_overlap_ratio": args.overlap,
        "flow_smoothing_kernel": args.smooth_kernel,
    }

    print()
    print("=" * 70)
    print("   FARNEBACK OPTICAL FLOW - ACCURACY TEST")
    print("=" * 70)
    print()
    print(f"  Config: pyr_scale={config['pyr_scale']}, levels={config['levels']}, "
          f"winsize={config['winsize']}, iter={config['iterations']}, "
          f"poly_n={config['poly_n']}, poly_sigma={config['poly_sigma']}")
    print(f"  Pipeline: blocks={config['cpu_num_blocks_x']}x{config['cpu_num_blocks_y']}, "
          f"overlap={config['cpu_overlap_ratio']}, smooth_kernel={config['flow_smoothing_kernel']}")
    print()

    if args.demo:
        print("  [DEMO MODE] Membuat citra sintetis (512x512, shift_x=5, shift_y=3, noise=2.0)")
        base_gray, target_gray, flow_gt = generate_synthetic_pair(
            height=512, width=512, shift_x=5, shift_y=3, noise_sigma=2.0
        )
    elif args.base and args.target:
        if not os.path.exists(args.base):
            print(f"  [ERROR] File tidak ditemukan: {args.base}")
            sys.exit(1)
        if not os.path.exists(args.target):
            print(f"  [ERROR] File tidak ditemukan: {args.target}")
            sys.exit(1)

        base_bgr = cv2.imread(args.base, cv2.IMREAD_COLOR)
        target_bgr = cv2.imread(args.target, cv2.IMREAD_COLOR)
        if base_bgr is None:
            print(f"  [ERROR] Gagal membaca: {args.base}")
            sys.exit(1)
        if target_bgr is None:
            print(f"  [ERROR] Gagal membaca: {args.target}")
            sys.exit(1)

        base_gray = cv2.cvtColor(base_bgr, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2GRAY)

        # Resize target ke base jika berbeda
        if base_gray.shape != target_gray.shape:
            print(f"  [INFO] Resize target {target_gray.shape} -> {base_gray.shape}")
            target_gray = cv2.resize(target_gray, (base_gray.shape[1], base_gray.shape[0]))

        flow_gt = None
        if args.gt:
            flow_gt = np.load(args.gt)
            print(f"  [GT] Loaded ground truth flow: {flow_gt.shape}")

    else:
        print("  [ERROR] Tentukan --base & --target atau --demo")
        parser.print_help()
        sys.exit(1)

    print(f"  Image size : {base_gray.shape[1]}x{base_gray.shape[0]}")
    print(f"  Image dtype: {base_gray.dtype}")
    print()

    run_comparison(base_gray, target_gray, flow_gt=flow_gt,
                   config=config, output_dir=args.output)


if __name__ == "__main__":
    main()
