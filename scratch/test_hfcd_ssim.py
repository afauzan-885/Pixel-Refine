"""
HFCD (Hybrid Fast Collaborative Denoising) SSIM Test
=====================================================
Tests the HFCD denoising algorithm against NLM and OpenCV baselines
using synthetic images with Gaussian noise.

Uses JIT mode (AOT_MODE=0) since HFCD doesn't have compiled TCM yet.

Reference:
  Dabov et al. (2007) IEEE TIP — BM3D
  Sanders & Larkin (2021) arXiv:2103.10765 — G-BM3D

Usage:
  set AOT_MODE=0
  python scratch/test_hfcd_ssim.py
"""
import os
import sys
import time
import numpy as np

# MUST set AOT_MODE=0 BEFORE any taichi imports
os.environ["AOT_MODE"] = "0"

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import cv2
from skimage.metrics import structural_similarity as ssim

# Import directly from modules (JIT path)
from taichi_library.taichi_algorithm.bm3d import hfcd_denoise
from taichi_library.taichi_algorithm.nlm import non_local_means


def generate_synthetic_image(h=256, w=256, seed=42):
    """Generate a synthetic grayscale image with edges, gradients, textures."""
    rng = np.random.RandomState(seed)
    img = np.zeros((h, w), dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w]

    img += 0.3 * np.sin(2 * np.pi * xx / w)
    img += 0.2 * np.cos(2 * np.pi * yy / h)
    img[h // 4:3 * h // 4, w // 4:3 * w // 4] += 0.4

    cx, cy = w // 3, h // 3
    r = min(h, w) // 6
    img[((xx - cx)**2 + (yy - cy)**2) < r**2] += 0.3

    cx2, cy2 = 2 * w // 3, 2 * h // 3
    r2 = min(h, w) // 8
    img[((xx - cx2)**2 + (yy - cy2)**2) < r2**2] -= 0.2

    texture = 0.1 * np.sin(2 * np.pi * xx / 4) * np.cos(2 * np.pi * yy / 4)
    img[10:60, 10:60] += texture[10:60, 10:60]

    for _ in range(50):
        ry, rx = rng.randint(5, h - 5), rng.randint(5, w - 5)
        img[ry - 1:ry + 2, rx - 1:rx + 2] += 0.5

    return np.clip(img, 0, 1)


def add_gaussian_noise(img, sigma=0.1, seed=123):
    """Add Gaussian noise."""
    rng = np.random.RandomState(seed)
    noisy = img + rng.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(noisy, 0, 1)


def psnr(ref, test, eps=1e-10):
    mse = np.mean((ref - test)**2)
    return 10 * np.log10(1.0 / max(mse, eps))


def test_hfcd():
    """Run HFCD vs NLM vs OpenCV comparison."""
    print("=" * 80)
    print("  HFCD vs NLM vs OpenCV -- Synthetic SSIM Test (JIT mode)")
    print("  Reference: Dabov et al. (2007), Sanders & Larkin (2021)")
    print("=" * 80)

    # Test configurations: (H, W, sigma, label)
    configs = [
        (128, 128, 0.05, "128x128 s=0.05"),
        (128, 128, 0.10, "128x128 s=0.10"),
        (256, 256, 0.05, "256x256 s=0.05"),
        (256, 256, 0.10, "256x256 s=0.10"),
    ]

    results = []

    for h, w, sigma, label in configs:
        print(f"\n--- {label} ---")
        gt = generate_synthetic_image(h, w, seed=42)
        noisy = add_gaussian_noise(gt, sigma=sigma, seed=123)

        ssim_noisy = ssim(gt, noisy, data_range=1.0)
        psnr_noisy = psnr(gt, noisy)
        print(f"  Noisy: SSIM={ssim_noisy:.4f}  PSNR={psnr_noisy:.2f}dB")

        # --- HFCD (JIT) ---
        t0 = time.perf_counter()
        hfcd_result = hfcd_denoise(
            noisy.copy(), sigma,
            block_size=8, search_radius=15,
            max_matches=16, lambda_3d=2.7,
            cycle_spins=1
        )
        t_hfcd = time.perf_counter() - t0
        if hasattr(hfcd_result, "to_numpy"):
            hfcd_result = hfcd_result.to_numpy()
        hfcd_result = np.clip(hfcd_result.astype(np.float32), 0, 1)

        ssim_hfcd = ssim(gt, hfcd_result, data_range=1.0)
        psnr_hfcd = psnr(gt, hfcd_result)
        imp_ssim_hfcd = ssim_hfcd - ssim_noisy
        imp_psnr_hfcd = psnr_hfcd - psnr_noisy

        print(f"  HFCD:    SSIM={ssim_hfcd:.4f} ({imp_ssim_hfcd:+.4f})  "
              f"PSNR={psnr_hfcd:.2f}dB ({imp_psnr_hfcd:+.2f})  "
              f"{t_hfcd*1000:.1f}ms")

        # --- NLM (JIT) ---
        k_nlm = {1: 1.2, 2: 1.0, 3: 0.8}
        h_nlm = k_nlm[3] * sigma

        t0 = time.perf_counter()
        nlm_result = non_local_means(
            noisy.astype(np.float32),
            h_param=h_nlm,
            search_window=7,
            patch_size=3,
        )
        t_nlm = time.perf_counter() - t0
        if hasattr(nlm_result, "to_numpy"):
            nlm_result = nlm_result.to_numpy()
        nlm_result = np.clip(nlm_result.astype(np.float32), 0, 1)

        ssim_nlm = ssim(gt, nlm_result, data_range=1.0)
        psnr_nlm = psnr(gt, nlm_result)
        imp_ssim_nlm = ssim_nlm - ssim_noisy
        imp_psnr_nlm = psnr_nlm - psnr_noisy

        print(f"  NLM:     SSIM={ssim_nlm:.4f} ({imp_ssim_nlm:+.4f})  "
              f"PSNR={psnr_nlm:.2f}dB ({imp_psnr_nlm:+.2f})  "
              f"{t_nlm*1000:.1f}ms")

        # --- OpenCV NLM baseline ---
        h_cv = max(1, int(round(h_nlm * 255)))
        noisy_uint8 = (noisy * 255).astype(np.uint8)
        t0 = time.perf_counter()
        cv_result = cv2.fastNlMeansDenoising(
            noisy_uint8, None, h=h_cv,
            templateWindowSize=7, searchWindowSize=15
        )
        t_cv = time.perf_counter() - t0
        cv_float = cv_result.astype(np.float32) / 255.0

        ssim_cv = ssim(gt, cv_float, data_range=1.0)
        psnr_cv = psnr(gt, cv_float)

        print(f"  OpenCV:  SSIM={ssim_cv:.4f}  PSNR={psnr_cv:.2f}dB  {t_cv*1000:.1f}ms")

        results.append(dict(
            label=label, sigma=sigma,
            ssim_noisy=ssim_noisy, psnr_noisy=psnr_noisy,
            ssim_hfcd=ssim_hfcd, psnr_hfcd=psnr_hfcd,
            imp_ssim_hfcd=imp_ssim_hfcd, imp_psnr_hfcd=imp_psnr_hfcd,
            ssim_nlm=ssim_nlm, psnr_nlm=psnr_nlm,
            imp_ssim_nlm=imp_ssim_nlm, imp_psnr_nlm=imp_psnr_nlm,
            ssim_cv=ssim_cv, psnr_cv=psnr_cv,
            time_hfcd=t_hfcd * 1000, time_nlm=t_nlm * 1000, time_cv=t_cv * 1000,
        ))

    # --- Summary ---
    print("\n" + "=" * 115)
    print("  SUMMARY -- HFCD vs NLM vs OpenCV  (JIT mode)")
    print("=" * 115)
    hdr = (f"{'Config':<20} {'S_n':>6} "
           f"{'S_HFCD':>7} {'iS':>6} {'P_HFCD':>7} "
           f"{'S_NLM':>7} {'iS':>6} {'P_NLM':>7} "
           f"{'S_CV':>7} {'P_CV':>7} "
           f"{'tHFCD':>8} {'tNLM':>8} {'tCV':>8}")
    print(hdr)
    print("-" * 115)

    all_pass = True
    for r in results:
        ok = (r["imp_ssim_hfcd"] > 0
              and r["ssim_hfcd"] >= r["ssim_nlm"] - 0.03)
        marker = " PASS" if ok else " FAIL"
        if not ok:
            all_pass = False

        print(f"{r['label']:<20} {r['ssim_noisy']:>6.4f} "
              f"{r['ssim_hfcd']:>7.4f} {r['imp_ssim_hfcd']:>+6.4f} {r['psnr_hfcd']:>6.2f}dB "
              f"{r['ssim_nlm']:>7.4f} {r['imp_ssim_nlm']:>+6.4f} {r['psnr_nlm']:>6.2f}dB "
              f"{r['ssim_cv']:>7.4f} {r['psnr_cv']:>6.2f}dB "
              f"{r['time_hfcd']:>7.1f}ms {r['time_nlm']:>7.1f}ms {r['time_cv']:>7.1f}ms"
              f"{marker}")

    print("-" * 115)
    print(f"\n  RESULT: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
    print("\n  Pass criteria:")
    print("    1. HFCD SSIM improvement > 0 (better than noisy)")
    print("    2. HFCD SSIM >= NLM SSIM - 0.03 (competitive with NLM)")
    print("\n  Note: Running in JIT mode (AOT_MODE=0). AOT compilation planned.")

    return all_pass


if __name__ == "__main__":
    success = test_hfcd()
    sys.exit(0 if success else 1)
