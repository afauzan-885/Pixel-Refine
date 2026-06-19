"""
NLM AOT Module Test: Taichi AOT vs OpenCV fastNlMeansDenoising
==============================================================
Generates synthetic test images, adds Gaussian noise, denoises with
Taichi NLM AOT module and OpenCV NLM, then compares using SSIM.

Reference:
  Buades, A., Coll, B., Morel, J.M. (2005). "A Non-Local Algorithm for
  Image Denoising." CVPR 2005, pp. 60-65.
  Buades, A., Coll, B., Morel, J.M. (2011). "Non-Local Means Denoising."
  Image Processing On Line (IPOL), 1.

Parameter selection:
  h = k * sigma, where k is calibrated for float32 [0,1] images WITHOUT
  noise variance subtraction (which the IPOL reference implementation uses).
  Calibrated against scikit-image recommendations (0.6-1.15 * sigma).

Usage:
  python scratch/test_nlm_aot_ssim.py
"""
import os
import sys
import time
import numpy as np

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Force AOT mode — this ensures taichi_aot.non_local_means is called
os.environ["AOT_MODE"] = "1"

import cv2
from skimage.metrics import structural_similarity as ssim


def generate_synthetic_image(h=256, w=256, seed=42):
    """Generate a synthetic grayscale image with sharp edges, gradients, and textures."""
    rng = np.random.RandomState(seed)
    img = np.zeros((h, w), dtype=np.float32)

    yy, xx = np.mgrid[0:h, 0:w]

    # 1. Large gradients
    img += 0.3 * np.sin(2 * np.pi * xx / w)
    img += 0.2 * np.cos(2 * np.pi * yy / h)

    # 2. Sharp rectangular features
    img[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4] += 0.4

    # 3. Circles
    cx, cy = w // 3, h // 3
    r = min(h, w) // 6
    img[((xx - cx) ** 2 + (yy - cy) ** 2) < r ** 2] += 0.3

    cx2, cy2 = 2 * w // 3, 2 * h // 3
    r2 = min(h, w) // 8
    img[((xx - cx2) ** 2 + (yy - cy2) ** 2) < r2 ** 2] -= 0.2

    # 4. High-freq texture patch
    texture = 0.1 * np.sin(2 * np.pi * xx / 4) * np.cos(2 * np.pi * yy / 4)
    img[10:60, 10:60] += texture[10:60, 10:60]

    # 5. Small dots / impulses
    for _ in range(50):
        ry, rx = rng.randint(5, h - 5), rng.randint(5, w - 5)
        img[ry - 1 : ry + 2, rx - 1 : rx + 2] += 0.5

    img = np.clip(img, 0, 1)
    return img


def generate_synthetic_rgb(h=256, w=256, seed=42):
    """Generate a synthetic RGB image."""
    r = generate_synthetic_image(h, w, seed)
    g = generate_synthetic_image(h, w, seed + 1)
    b = generate_synthetic_image(h, w, seed + 2)
    return np.stack([r, g, b], axis=-1)


def add_gaussian_noise(img, sigma=0.1, seed=123):
    """Add Gaussian noise to an image."""
    rng = np.random.RandomState(seed)
    noisy = img + rng.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(noisy, 0, 1)


def psnr(ref, test, eps=1e-10):
    mse = np.mean((ref - test) ** 2)
    return 10 * np.log10(1.0 / max(mse, eps))


def optimal_h(noise_sigma, patch_radius):
    """
    Compute optimal h for float32 [0,1] images WITHOUT noise variance subtraction.

    Based on Buades et al. (IPOL 2011): h = k * sigma.

    The IPOL paper's raw k values (0.2-0.4) assume the implementation subtracts
    expected noise variance from patch distances. Since our Taichi kernels do NOT
    perform noise variance subtraction, we use higher k values calibrated to
    scikit-image's recommendations (0.6-1.15 without sigma correction).

    The constant k decreases as patch size increases because:
    - Larger patches average out noise, making distance more discriminative
    - More patch pixels -> lower variance in distance estimate

    Args:
        noise_sigma: Noise standard deviation (same scale as image, e.g. [0,1]).
        patch_radius: Half-size of comparison patch (f).

    Returns:
        Optimal h parameter value for float32 [0,1] images.
    """
    # Calibrated for float32 [0,1] without noise variance subtraction.
    # Target: exp(-sigma^2 / h^2) ~ 0.6 for similar patches.
    k_table = {1: 1.2, 2: 1.0, 3: 0.8}
    k = k_table.get(patch_radius, 0.8)
    return k * noise_sigma


def test_nlm_aot():
    """Run the AOT NLM test across multiple configurations."""
    from taichi_library import taichi_aot

    print("=" * 80)
    print("  NLM AOT Module Test: Taichi AOT vs OpenCV")
    print("  Reference: Buades, Coll, Morel -- CVPR 2005 / IPOL 2011")
    print("=" * 80)

    # ------- GRAYSCALE TESTS -------
    # h_param computed via optimal_h(noise_sigma, patch_radius)
    # AOT supports fixed variants: search_window in {3,5,7}, patch_size in {1,2,3}
    gray_configs = [
        (128, 128, 0.05, optimal_h(0.05, 1), 3, 1, "Gray 128x128 s=0.05 R=3 f=1"),
        (128, 128, 0.10, optimal_h(0.10, 2), 5, 2, "Gray 128x128 s=0.10 R=5 f=2"),
        (256, 256, 0.05, optimal_h(0.05, 2), 5, 2, "Gray 256x256 s=0.05 R=5 f=2"),
        (256, 256, 0.10, optimal_h(0.10, 3), 7, 3, "Gray 256x256 s=0.10 R=7 f=3"),
        (256, 256, 0.15, optimal_h(0.15, 3), 7, 3, "Gray 256x256 s=0.15 R=7 f=3"),
        (512, 512, 0.10, optimal_h(0.10, 3), 7, 3, "Gray 512x512 s=0.10 R=7 f=3"),
    ]

    # ------- RGB TESTS -------
    rgb_configs = [
        (128, 128, 0.08, optimal_h(0.08, 2), 5, 2, "RGB 128x128 s=0.08 R=5 f=2"),
        (256, 256, 0.10, optimal_h(0.10, 3), 7, 3, "RGB 256x256 s=0.10 R=7 f=3"),
    ]

    results = []

    # --- Gray tests ---
    print("\n>>> GRAYSCALE TESTS")
    for h, w, noise_sigma, h_param, search_w, patch_s, label in gray_configs:
        print(f"\n--- {label}  (h={h_param:.4f}) ---")
        gt = generate_synthetic_image(h, w, seed=42)
        noisy = add_gaussian_noise(gt, sigma=noise_sigma, seed=123)

        ssim_noisy = ssim(gt, noisy, data_range=1.0)
        psnr_noisy = psnr(gt, noisy)
        print(f"  Noisy SSIM vs GT : {ssim_noisy:.4f}  PSNR={psnr_noisy:.2f}dB")

        # OpenCV reference -- h is on uint8 [0,255] scale
        h_cv = max(1, int(round(h_param * 255)))
        noisy_uint8 = (noisy * 255).astype(np.uint8)
        t0 = time.perf_counter()
        cv_result = cv2.fastNlMeansDenoising(
            noisy_uint8, None,
            h=h_cv,
            templateWindowSize=2 * patch_s + 1,
            searchWindowSize=2 * search_w + 1,
        )
        t_cv = time.perf_counter() - t0
        cv_float = cv_result.astype(np.float32) / 255.0

        # Taichi AOT
        t0 = time.perf_counter()
        ta_result = taichi_aot.non_local_means(
            noisy.astype(np.float32),
            h_param=h_param,
            search_window=search_w,
            patch_size=patch_s,
            return_gpu=False,
        )
        t_ta = time.perf_counter() - t0
        if hasattr(ta_result, "to_numpy"):
            ta_result = ta_result.to_numpy()
        ta_result = np.clip(ta_result.astype(np.float32), 0, 1)

        ssim_cv = ssim(gt, cv_float, data_range=1.0)
        ssim_ta = ssim(gt, ta_result, data_range=1.0)
        psnr_cv = psnr(gt, cv_float)
        psnr_ta = psnr(gt, ta_result)
        pixel_diff = np.mean(np.abs(cv_float - ta_result))

        # Improvement over noisy input
        ssim_imp_cv = ssim_cv - ssim_noisy
        ssim_imp_ta = ssim_ta - ssim_noisy
        psnr_imp_cv = psnr_cv - psnr_noisy
        psnr_imp_ta = psnr_ta - psnr_noisy

        print(f"  OpenCV NLM : SSIM={ssim_cv:.4f} (+{ssim_imp_cv:.4f})  "
              f"PSNR={psnr_cv:.2f}dB (+{psnr_imp_cv:.2f})  {t_cv*1000:.1f}ms")
        print(f"  Taichi AOT : SSIM={ssim_ta:.4f} (+{ssim_imp_ta:.4f})  "
              f"PSNR={psnr_ta:.2f}dB (+{psnr_imp_ta:.2f})  {t_ta*1000:.1f}ms")
        print(f"  L1 Pixel Diff  : {pixel_diff:.6f}")

        results.append(dict(
            label=label, channel="gray",
            ssim_noisy=ssim_noisy, psnr_noisy=psnr_noisy,
            ssim_cv=ssim_cv, ssim_ta=ssim_ta,
            ssim_imp_cv=ssim_imp_cv, ssim_imp_ta=ssim_imp_ta,
            psnr_cv=psnr_cv, psnr_ta=psnr_ta,
            psnr_imp_cv=psnr_imp_cv, psnr_imp_ta=psnr_imp_ta,
            time_cv_ms=t_cv * 1000, time_ta_ms=t_ta * 1000,
            pixel_diff=pixel_diff,
        ))

    # --- RGB tests ---
    print("\n>>> RGB TESTS")
    for h, w, noise_sigma, h_param, search_w, patch_s, label in rgb_configs:
        print(f"\n--- {label}  (h={h_param:.4f}) ---")
        gt = generate_synthetic_rgb(h, w, seed=42)
        noisy = add_gaussian_noise(gt, sigma=noise_sigma, seed=123)

        ssim_noisy = ssim(gt, noisy, data_range=1.0, channel_axis=-1)
        psnr_noisy = psnr(gt, noisy)
        print(f"  Noisy SSIM vs GT : {ssim_noisy:.4f}  PSNR={psnr_noisy:.2f}dB")

        # OpenCV reference (fastNlMeansDenoisingColored for RGB)
        h_cv = max(1, int(round(h_param * 255)))
        noisy_uint8 = np.clip(noisy * 255, 0, 255).astype(np.uint8)
        t0 = time.perf_counter()
        cv_result = cv2.fastNlMeansDenoisingColored(
            noisy_uint8, None,
            h_cv, h_cv,
            2 * patch_s + 1,
            2 * search_w + 1,
        )
        t_cv = time.perf_counter() - t0
        cv_float = cv_result.astype(np.float32) / 255.0

        # Taichi AOT
        t0 = time.perf_counter()
        ta_result = taichi_aot.non_local_means(
            noisy.astype(np.float32),
            h_param=h_param,
            search_window=search_w,
            patch_size=patch_s,
            return_gpu=False,
        )
        t_ta = time.perf_counter() - t0
        if hasattr(ta_result, "to_numpy"):
            ta_result = ta_result.to_numpy()
        ta_result = np.clip(ta_result.astype(np.float32), 0, 1)

        ssim_cv = ssim(gt, cv_float, data_range=1.0, channel_axis=-1)
        ssim_ta = ssim(gt, ta_result, data_range=1.0, channel_axis=-1)
        psnr_cv = psnr(gt, cv_float)
        psnr_ta = psnr(gt, ta_result)
        pixel_diff = np.mean(np.abs(cv_float - ta_result))

        # Improvement over noisy input
        ssim_imp_cv = ssim_cv - ssim_noisy
        ssim_imp_ta = ssim_ta - ssim_noisy
        psnr_imp_cv = psnr_cv - psnr_noisy
        psnr_imp_ta = psnr_ta - psnr_noisy

        print(f"  OpenCV NLM : SSIM={ssim_cv:.4f} (+{ssim_imp_cv:.4f})  "
              f"PSNR={psnr_cv:.2f}dB (+{psnr_imp_cv:.2f})  {t_cv*1000:.1f}ms")
        print(f"  Taichi AOT : SSIM={ssim_ta:.4f} (+{ssim_imp_ta:.4f})  "
              f"PSNR={psnr_ta:.2f}dB (+{psnr_imp_ta:.2f})  {t_ta*1000:.1f}ms")
        print(f"  L1 Pixel Diff  : {pixel_diff:.6f}")

        results.append(dict(
            label=label, channel="rgb",
            ssim_noisy=ssim_noisy, psnr_noisy=psnr_noisy,
            ssim_cv=ssim_cv, ssim_ta=ssim_ta,
            ssim_imp_cv=ssim_imp_cv, ssim_imp_ta=ssim_imp_ta,
            psnr_cv=psnr_cv, psnr_ta=psnr_ta,
            psnr_imp_cv=psnr_imp_cv, psnr_imp_ta=psnr_imp_ta,
            time_cv_ms=t_cv * 1000, time_ta_ms=t_ta * 1000,
            pixel_diff=pixel_diff,
        ))

    # --- Summary ---
    print("\n" + "=" * 120)
    print("  SUMMARY -- NLM AOT vs OpenCV  (h = k*sigma, calibrated for float32)")
    print("=" * 120)
    header = (f"{'Config':<32} {'Ch':>4} "
              f"{'SSIM_n':>7} {'SSIM_CV':>8} {'SSIM_TA':>8} {'dSSIM':>7} "
              f"{'iCV':>6} {'iTA':>6} "
              f"{'PSNR_CV':>8} {'PSNR_TA':>8} "
              f"{'Time_CV':>9} {'Time_TA':>9} {'L1':>9}")
    print(header)
    print("-" * 120)

    all_pass = True
    for r in results:
        delta = r["ssim_ta"] - r["ssim_cv"]
        # Pass if: SSIM delta < 0.05, L1 < 0.10, AND denoising improves over noisy
        ok = (abs(delta) < 0.05
              and r["pixel_diff"] < 0.10
              and r["ssim_imp_ta"] > 0)
        marker = " PASS" if ok else " FAIL"
        if not ok:
            all_pass = False
        ch = "G" if r["channel"] == "gray" else "RGB"
        print(f"{r['label']:<32} {ch:>4} "
              f"{r['ssim_noisy']:>7.4f} {r['ssim_cv']:>8.4f} {r['ssim_ta']:>8.4f} "
              f"{delta:>+7.4f} "
              f"{r['ssim_imp_cv']:>+6.4f} {r['ssim_imp_ta']:>+6.4f} "
              f"{r['psnr_cv']:>7.2f}dB {r['psnr_ta']:>7.2f}dB "
              f"{r['time_cv_ms']:>7.1f}ms {r['time_ta_ms']:>7.1f}ms "
              f"{r['pixel_diff']:>8.6f}{marker}")

    print("-" * 120)
    print(f"\n  RESULT: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
    print("\n  Pass criteria:")
    print("    1. SSIM delta (Taichi - OpenCV) < 0.05")
    print("    2. L1 pixel diff < 0.10")
    print("    3. SSIM improvement > 0 (denoised better than noisy)")
    print("\n  Note: OpenCV uses cv2.fastNlMeansDenoising (uint8) while Taichi AOT")
    print("  operates on float32 -- algorithmic differences are expected.")
    print("  h_param = k * sigma, calibrated for float32 [0,1] (no noise var subtraction).")

    return all_pass


if __name__ == "__main__":
    success = test_nlm_aot()
    sys.exit(0 if success else 1)
