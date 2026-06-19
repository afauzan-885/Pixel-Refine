"""
HFCD/BM3D Comprehensive AOT Test
=================================
Tests accuracy (9 configs) and auto-repair (15 edge cases).

Usage:
  set AOT_MODE=1
  python scratch/test_hfcd_aot_comprehensive.py
"""
import os
import sys
import time
import numpy as np

# MUST be set before imports
os.environ["AOT_MODE"] = "1"

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from skimage.metrics import structural_similarity as ssim


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


def test_accuracy():
    """Test 1: Accuracy across dimensions, dtypes, channels."""
    from taichi_library import taichi_aot

    print("=" * 80)
    print("  ACCURACY TESTS (AOT mode)")
    print("=" * 80)

    configs = [
        # (H, W, dtype, channels, sigma_raw, sigma_desc, ssim_threshold)
        (128, 128, np.float32, 1, 0.05,       "f32 1ch s=0.05",      0.70),
        (128, 128, np.float32, 1, 0.10,       "f32 1ch s=0.10",      0.55),
        (256, 256, np.float32, 1, 0.05,       "f32 1ch s=0.05",      0.70),
        (256, 256, np.float32, 1, 0.10,       "f32 1ch s=0.10",      0.60),
        (256, 256, np.float32, 3, 0.10,       "f32 3ch s=0.10",      0.55),
        (128, 128, np.uint8,   1, 12,         "u8  1ch s=12",        0.70),
        (128, 128, np.uint8,   3, 25,         "u8  3ch s=25",        0.55),
        (256, 256, np.uint16,  1, 2500,       "u16 1ch s=2500",      0.70),
        (256, 256, np.uint16,  3, 6500,       "u16 3ch s=6500",      0.55),
    ]

    results = []
    all_pass = True

    for H, W, dtype, channels, sigma_raw, desc, threshold in configs:
        print(f"\n--- {desc} ({H}x{W}) ---")

        # Generate ground truth
        if channels == 1:
            gt_f32 = generate_synthetic_image(H, W, seed=42)
        else:
            gt_f32 = np.stack([
                generate_synthetic_image(H, W, seed=42 + c)
                for c in range(channels)
            ], axis=-1)

        # Convert to target dtype
        if dtype == np.float32:
            gt = gt_f32.copy()
            sigma = sigma_raw
        elif dtype == np.uint8:
            gt = (gt_f32 * 255).astype(np.uint8)
            sigma = sigma_raw
        elif dtype == np.uint16:
            gt = (gt_f32 * 65535).astype(np.uint16)
            sigma = sigma_raw

        # Add noise (in float domain, then convert back)
        sigma_f32 = sigma_raw / 255.0 if dtype == np.uint8 else \
                    sigma_raw / 65535.0 if dtype == np.uint16 else sigma_raw
        noisy_f32 = add_gaussian_noise(gt_f32, sigma=sigma_f32, seed=123)

        if dtype == np.uint8:
            noisy = (noisy_f32 * 255).astype(np.uint8)
        elif dtype == np.uint16:
            noisy = (noisy_f32 * 65535).astype(np.uint16)
        else:
            noisy = noisy_f32

        # Compute noisy SSIM
        ssim_noisy = ssim(gt_f32, noisy_f32, data_range=1.0,
                          channel_axis=-1 if channels > 1 else None)

        # Run HFCD
        t0 = time.perf_counter()
        denoised = taichi_aot.bm3d(noisy, sigma)
        t_bm3d = time.perf_counter() - t0

        # Convert result back to float32 for comparison
        if dtype == np.uint8:
            denoised_f32 = denoised.astype(np.float32) / 255.0
        elif dtype == np.uint16:
            denoised_f32 = denoised.astype(np.float32) / 65535.0
        else:
            denoised_f32 = denoised

        ssim_denoised = ssim(gt_f32, denoised_f32, data_range=1.0,
                             channel_axis=-1 if channels > 1 else None)
        imp = ssim_denoised - ssim_noisy
        passed = ssim_denoised >= threshold and imp > 0
        marker = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False

        print(f"  Noisy SSIM={ssim_noisy:.4f}  Denoised SSIM={ssim_denoised:.4f} "
              f"({imp:+.4f})  {t_bm3d*1000:.0f}ms  [{marker}]")

        results.append((desc, ssim_noisy, ssim_denoised, imp, threshold, passed))

    return all_pass, results


def test_auto_repair():
    """Test 2: Auto-repair edge cases (no crash, correct behavior)."""
    from taichi_library import taichi_aot

    print("\n" + "=" * 80)
    print("  AUTO-REPAIR TESTS")
    print("=" * 80)

    cases = []
    all_pass = True

    def check(desc, passed, detail=""):
        nonlocal all_pass
        marker = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{marker}] {desc} {detail}")
        cases.append((desc, passed))

    # 1. Very small image (4x4, smaller than block_size=8)
    try:
        small = np.random.rand(4, 4).astype(np.float32)
        result = taichi_aot.bm3d(small, 0.1)
        check("4x4 image (small)", result.shape == (4, 4),
              f"shape={result.shape}")
    except Exception as e:
        check("4x4 image (small)", False, f"CRASH: {e}")

    # 2. NaN pixels
    try:
        nan_img = generate_synthetic_image(64, 64)
        nan_img[10, 10] = np.nan
        nan_img[20, 20] = np.nan
        result = taichi_aot.bm3d(nan_img, 0.05)
        has_nan = np.any(np.isnan(result))
        check("NaN pixels", not has_nan and result.shape == (64, 64),
              f"has_nan={has_nan}")
    except Exception as e:
        check("NaN pixels", False, f"CRASH: {e}")

    # 3. +Inf pixels
    try:
        inf_img = generate_synthetic_image(64, 64)
        inf_img[10, 10] = np.inf
        result = taichi_aot.bm3d(inf_img, 0.05)
        has_inf = np.any(np.isinf(result))
        check("+Inf pixels", not has_inf and result.shape == (64, 64),
              f"has_inf={has_inf}")
    except Exception as e:
        check("+Inf pixels", False, f"CRASH: {e}")

    # 4. sigma = 0
    try:
        img = generate_synthetic_image(64, 64)
        result = taichi_aot.bm3d(img, 0)
        is_copy = np.allclose(result, img)
        check("sigma=0 (no-op)", is_copy, f"is_copy={is_copy}")
    except Exception as e:
        check("sigma=0 (no-op)", False, f"CRASH: {e}")

    # 5. sigma = -1
    try:
        img = generate_synthetic_image(64, 64)
        result = taichi_aot.bm3d(img, -1)
        is_copy = np.allclose(result, img)
        check("sigma=-1 (no-op)", is_copy, f"is_copy={is_copy}")
    except Exception as e:
        check("sigma=-1 (no-op)", False, f"CRASH: {e}")

    # 6. sigma = NaN
    try:
        img = generate_synthetic_image(64, 64)
        result = taichi_aot.bm3d(img, np.nan)
        is_copy = np.allclose(result, img)
        check("sigma=NaN (no-op)", is_copy, f"is_copy={is_copy}")
    except Exception as e:
        check("sigma=NaN (no-op)", False, f"CRASH: {e}")

    # 7. sigma = Inf
    try:
        img = generate_synthetic_image(64, 64)
        result = taichi_aot.bm3d(img, np.inf)
        is_copy = np.allclose(result, img)
        check("sigma=Inf (no-op)", is_copy, f"is_copy={is_copy}")
    except Exception as e:
        check("sigma=Inf (no-op)", False, f"CRASH: {e}")

    # 8. sigma very large (0.5)
    try:
        img = generate_synthetic_image(64, 64)
        noisy = add_gaussian_noise(img, 0.3)
        result = taichi_aot.bm3d(noisy, 0.5)
        check("sigma=0.5 (large)", result.shape == (64, 64) and not np.any(np.isnan(result)),
              f"shape={result.shape}")
    except Exception as e:
        check("sigma=0.5 (large)", False, f"CRASH: {e}")

    # 9. 1x1000 image (extreme aspect)
    try:
        img = np.random.rand(1, 1000).astype(np.float32)
        result = taichi_aot.bm3d(img, 0.05)
        check("1x1000 (extreme aspect)", result.shape == (1, 1000),
              f"shape={result.shape}")
    except Exception as e:
        check("1x1000 (extreme aspect)", False, f"CRASH: {e}")

    # 10. 1000x1 image (extreme aspect)
    try:
        img = np.random.rand(1000, 1).astype(np.float32)
        result = taichi_aot.bm3d(img, 0.05)
        check("1000x1 (extreme aspect)", result.shape == (1000, 1),
              f"shape={result.shape}")
    except Exception as e:
        check("1000x1 (extreme aspect)", False, f"CRASH: {e}")

    # 11. Non-contiguous numpy array
    try:
        big = np.random.rand(128, 128).astype(np.float32)
        non_contig = big[::2, ::2]  # strided view, non-contiguous
        result = taichi_aot.bm3d(non_contig, 0.05)
        check("Non-contiguous array", result.shape == (64, 64),
              f"shape={result.shape}")
    except Exception as e:
        check("Non-contiguous array", False, f"CRASH: {e}")

    # 12. All-zero image
    try:
        img = np.zeros((64, 64), dtype=np.float32)
        result = taichi_aot.bm3d(img, 0.05)
        check("All-zero image", result.shape == (64, 64) and not np.any(np.isnan(result)),
              f"max_val={np.max(np.abs(result)):.6f}")
    except Exception as e:
        check("All-zero image", False, f"CRASH: {e}")

    # 13. All-one image
    try:
        img = np.ones((64, 64), dtype=np.float32)
        result = taichi_aot.bm3d(img, 0.05)
        check("All-one image", result.shape == (64, 64) and not np.any(np.isnan(result)),
              f"max_val={np.max(np.abs(result)):.6f}")
    except Exception as e:
        check("All-one image", False, f"CRASH: {e}")

    # 14. Single pixel (1x1)
    try:
        img = np.array([[0.5]], dtype=np.float32)
        result = taichi_aot.bm3d(img, 0.05)
        check("1x1 image", result.shape == (1, 1),
              f"val={result[0,0]:.4f}")
    except Exception as e:
        check("1x1 image", False, f"CRASH: {e}")

    # 15. Very large image (2048x2048) - memory test
    try:
        img = generate_synthetic_image(512, 512)  # Use 512 to be safe with VRAM
        noisy = add_gaussian_noise(img, 0.05)
        t0 = time.perf_counter()
        result = taichi_aot.bm3d(noisy, 0.05)
        t_large = time.perf_counter() - t0
        s = ssim(img, result, data_range=1.0)
        check("Large image (512x512)", s > 0.60,
              f"SSIM={s:.4f} {t_large*1000:.0f}ms")
    except Exception as e:
        check("Large image (512x512)", False, f"CRASH: {e}")

    return all_pass, cases


if __name__ == "__main__":
    print("HFCD/BM3D Comprehensive AOT Test")
    print(f"AOT_MODE={os.environ.get('AOT_MODE', 'unknown')}")
    print()

    acc_pass, acc_results = test_accuracy()
    repair_pass, repair_cases = test_auto_repair()

    # Summary
    print("\n" + "=" * 80)
    print("  FINAL SUMMARY")
    print("=" * 80)

    print(f"\n  Accuracy: {sum(1 for r in acc_results if r[5])}/{len(acc_results)} PASS")
    for desc, ssim_n, ssim_d, imp, thr, ok in acc_results:
        m = "PASS" if ok else "FAIL"
        print(f"    [{m}] {desc}: noisy={ssim_n:.4f} denoised={ssim_d:.4f} "
              f"(+{imp:.4f}) threshold={thr}")

    print(f"\n  Auto-Repair: {sum(1 for c in repair_cases if c[1])}/{len(repair_cases)} PASS")
    for desc, ok in repair_cases:
        m = "PASS" if ok else "FAIL"
        print(f"    [{m}] {desc}")

    overall = acc_pass and repair_pass
    print(f"\n  OVERALL: {'ALL PASS' if overall else 'SOME FAILURES'}")

    sys.exit(0 if overall else 1)
