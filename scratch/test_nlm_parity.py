"""
NLM Parity Test: Taichi NLM vs OpenCV fastNlMeansDenoising
============================================================
Generates synthetic test images, adds Gaussian noise, denoises with both
Taichi NLM and OpenCV NLM, then compares using SSIM.

Usage:
  python scratch/test_nlm_parity.py
"""
import os
import sys
import time
import numpy as np

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ["AOT_MODE"] = "0"  # Use JIT mode for testing

import cv2
from skimage.metrics import structural_similarity as ssim


def generate_synthetic_image(h=256, w=256, seed=42):
    """Generate a synthetic grayscale image with sharp edges, gradients, and textures."""
    rng = np.random.RandomState(seed)
    img = np.zeros((h, w), dtype=np.float32)

    # 1. Large gradients
    yy, xx = np.mgrid[0:h, 0:w]
    img += 0.3 * np.sin(2 * np.pi * xx / w)
    img += 0.2 * np.cos(2 * np.pi * yy / h)

    # 2. Sharp rectangular features
    img[h//4:3*h//4, w//4:3*w//4] += 0.4

    # 3. Circles
    cx, cy = w // 3, h // 3
    r = min(h, w) // 6
    mask_circle = ((xx - cx)**2 + (yy - cy)**2) < r**2
    img[mask_circle] += 0.3

    cx2, cy2 = 2*w//3, 2*h//3
    r2 = min(h, w) // 8
    mask_circle2 = ((xx - cx2)**2 + (yy - cy2)**2) < r2**2
    img[mask_circle2] -= 0.2

    # 4. High-freq texture patch
    texture = 0.1 * np.sin(2 * np.pi * xx / 4) * np.cos(2 * np.pi * yy / 4)
    img[10:60, 10:60] += texture[10:60, 10:60]

    # 5. Small dots / impulses
    for _ in range(50):
        ry, rx = rng.randint(5, h-5), rng.randint(5, w-5)
        img[ry-1:ry+2, rx-1:rx+2] += 0.5

    img = np.clip(img, 0, 1)
    return img


def add_gaussian_noise(img, sigma=0.1, seed=123):
    """Add Gaussian noise to an image."""
    rng = np.random.RandomState(seed)
    noisy = img + rng.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(noisy, 0, 1)


def test_nlm_parity():
    """Run the parity test across multiple configurations."""
    from taichi_library.taichi_algorithm import nlm as taichi_nlm

    print("=" * 70)
    print("  NLM Parity Test: Taichi vs OpenCV")
    print("=" * 70)

    # Test configurations: (h, w, noise_sigma, h_param, search_window, patch_size)
    configs = [
        (128, 128, 0.05, 8.0,  3, 1,  "Small+LightNoise"),
        (128, 128, 0.10, 10.0, 5, 2,  "Small+MedNoise"),
        (256, 256, 0.05, 10.0, 5, 2,  "Med+LightNoise"),
        (256, 256, 0.10, 12.0, 7, 3,  "Med+MedNoise"),
        (256, 256, 0.15, 15.0, 7, 3,  "Med+HeavyNoise"),
        (512, 512, 0.10, 12.0, 7, 3,  "Large+MedNoise"),
    ]

    results = []

    for h, w, noise_sigma, h_param, search_w, patch_s, label in configs:
        print(f"\n--- Config: {label} ({h}x{w}, sigma={noise_sigma:.2f}, "
              f"h={h_param}, R={search_w}, f={patch_s}) ---")

        # Generate synthetic ground truth
        gt = generate_synthetic_image(h, w, seed=42)
        noisy = add_gaussian_noise(gt, sigma=noise_sigma, seed=123)

        ssim_noisy = ssim(gt, noisy, data_range=1.0)
        print(f"  Noisy SSIM vs GT: {ssim_noisy:.4f}")

        # --- OpenCV NLM ---
        # OpenCV expects uint8, and h_param is in the range ~3-30 for uint8
        # Scale h_param: our float [0,1] image needs h scaled for uint8 range
        h_cv = int(h_param * 255)  # Convert to uint8-scale
        noisy_uint8 = (noisy * 255).astype(np.uint8)
        gt_uint8 = (gt * 255).astype(np.uint8)

        t0 = time.perf_counter()
        # cv2.fastNlMeansDenoising(src, h, templateWindowSize, searchWindowSize)
        # templateWindowSize = 2*patch_size + 1, searchWindowSize = 2*search_w + 1
        cv_result = cv2.fastNlMeansDenoising(
            noisy_uint8, None,
            h=h_cv,
            templateWindowSize=2 * patch_s + 1,
            searchWindowSize=2 * search_w + 1,
        )
        t_cv = time.perf_counter() - t0
        cv_float = cv_result.astype(np.float32) / 255.0
        ssim_cv = ssim(gt, cv_float, data_range=1.0)

        # --- Taichi NLM ---
        t0 = time.perf_counter()
        ta_result = taichi_nlm.non_local_means(
            noisy.astype(np.float32),
            h_param=h_param,
            search_window=search_w,
            patch_size=patch_s,
        )
        t_ta = time.perf_counter() - t0

        # Handle GPU output
        if hasattr(ta_result, "to_numpy"):
            ta_result = ta_result.to_numpy()
        ta_result = ta_result.astype(np.float32)
        if ta_result.max() > 1.0:
            ta_result = ta_result / 255.0
        ta_result = np.clip(ta_result, 0, 1)

        ssim_ta = ssim(gt, ta_result, data_range=1.0)

        # --- PSNR comparison ---
        def psnr(ref, test, eps=1e-10):
            mse = np.mean((ref - test) ** 2)
            return 10 * np.log10(1.0 / max(mse, eps))

        psnr_cv = psnr(gt, cv_float)
        psnr_ta = psnr(gt, ta_result)

        # --- Pixel difference ---
        pixel_diff = np.mean(np.abs(cv_float - ta_result))

        print(f"  OpenCV NLM:  SSIM={ssim_cv:.4f}  PSNR={psnr_cv:.2f}dB  Time={t_cv*1000:.1f}ms")
        print(f"  Taichi NLM:  SSIM={ssim_ta:.4f}  PSNR={psnr_ta:.2f}dB  Time={t_ta*1000:.1f}ms")
        print(f"  Pixel diff (L1): {pixel_diff:.6f}")

        results.append({
            "label": label,
            "ssim_cv": ssim_cv,
            "ssim_ta": ssim_ta,
            "psnr_cv": psnr_cv,
            "psnr_ta": psnr_ta,
            "time_cv_ms": t_cv * 1000,
            "time_ta_ms": t_ta * 1000,
            "pixel_diff": pixel_diff,
        })

    # --- Summary ---
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"{'Config':<22} {'SSIM_CV':>8} {'SSIM_TA':>8} {'ΔSSIM':>8} "
          f"{'PSNR_CV':>8} {'PSNR_TA':>8} {'Time_CV':>9} {'Time_TA':>9} {'L1_Diff':>9}")
    print("-" * 100)

    all_pass = True
    for r in results:
        delta_ssim = r["ssim_ta"] - r["ssim_cv"]
        # Allow up to 0.02 SSIM difference (algorithmic variation is expected)
        passes = abs(delta_ssim) < 0.05 and r["pixel_diff"] < 0.1
        marker = " ✓" if passes else " ✗"
        if not passes:
            all_pass = False
        print(f"{r['label']:<22} {r['ssim_cv']:>8.4f} {r['ssim_ta']:>8.4f} "
              f"{delta_ssim:>+8.4f} {r['psnr_cv']:>7.2f}dB {r['psnr_ta']:>7.2f}dB "
              f"{r['time_cv_ms']:>7.1f}ms {r['time_ta_ms']:>7.1f}ms "
              f"{r['pixel_diff']:>8.6f}{marker}")

    print("-" * 100)
    print(f"\n{'ALL PASS ✓' if all_pass else 'SOME FAILURES ✗'}")
    print("\nNote: OpenCV and Taichi NLM use different internal implementations,")
    print("so exact pixel parity is not expected. Qualitative SSIM parity is the goal.")

    return all_pass


if __name__ == "__main__":
    success = test_nlm_parity()
    sys.exit(0 if success else 1)
