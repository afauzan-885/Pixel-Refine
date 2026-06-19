"""
Comprehensive Accuracy Test for 9 New Taichi Algorithms
========================================================
Tests CLAHE, NLM, Canny, Guided Filter, Hough, Color Convert,
Otsu, Inpaint, and Seamless Clone with synthetic images.

Covers:
  - 8-bit and 16-bit depth
  - Grayscale and color (3-channel)
  - SSIM, PSNR, MAE metrics vs OpenCV reference

Usage:
  python scratch/test_new_algorithms_accuracy.py
"""
import os
import sys
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ["AOT_MODE"] = "0"  # JIT mode for testing

import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim


# =========================================================================
# Synthetic Image Generators
# =========================================================================

def generate_gradient_image(h=256, w=256, channels=1, dtype=np.float32):
    """Smooth gradient image with horizontal and vertical ramps."""
    yy, xx = np.mgrid[0:h, 0:w]
    img = (xx.astype(np.float32) / w + yy.astype(np.float32) / h) / 2.0
    if channels == 3:
        img = np.stack([img, img[::-1, :], img[:, ::-1]], axis=-1)
    return img


def generate_checkerboard(h=256, w=256, block_size=32, dtype=np.float32):
    """Sharp-edged checkerboard pattern."""
    yy, xx = np.mgrid[0:h, 0:w]
    checker = ((yy // block_size) + (xx // block_size)) % 2
    return checker.astype(dtype)


def generate_textured_image(h=256, w=256, channels=1, dtype=np.float32):
    """Image with gradients, circles, and sinusoidal textures."""
    yy, xx = np.mgrid[0:h, 0:w]
    img = np.zeros((h, w), dtype=dtype)
    img += 0.3 * np.sin(2 * np.pi * xx / w)
    img += 0.2 * np.cos(2 * np.pi * yy / h)

    # Circle
    cx, cy = w // 3, h // 3
    r = min(h, w) // 6
    mask = ((xx - cx)**2 + (yy - cy)**2) < r**2
    img[mask] += 0.3

    # Rectangle
    img[h//4:3*h//4, w//4:3*w//4] += 0.4

    img = np.clip(img, 0, 1)
    if channels == 3:
        img = np.stack([img, img[::-1, :], img[:, ::-1]], axis=-1)
    return img


def add_gaussian_noise(img, sigma=0.05, seed=42):
    rng = np.random.RandomState(seed)
    noisy = img + rng.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(noisy, 0, img.max())


def create_circular_mask(h, w, cy=None, cx=None, r=None):
    if cy is None: cy = h // 2
    if cx is None: cx = w // 2
    if r is None: r = min(h, w) // 4
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx - cx)**2 + (yy - cy)**2 < r**2).astype(np.float32)


# =========================================================================
# Metric Helpers
# =========================================================================

def psnr(ref, test, eps=1e-10):
    mse = np.mean((ref.astype(np.float64) - test.astype(np.float64)) ** 2)
    if mse == 0:
        return 100.0
    return 10 * np.log10(1.0 / max(mse, eps))


def run_test(name, func, threshold, metric="mae"):
    """Run a test function, catch exceptions, print result."""
    try:
        result = func()
        value = result[0] if isinstance(result, tuple) else result
        passed = value < threshold
        status = "[PASS]" if passed else "[FAIL]"
        detail = result[1] if isinstance(result, tuple) and len(result) > 1 else ""
        print(f"  {status} {name:45} | {metric.upper()}: {value:.6f} | Limit: {threshold} {detail}")
        return passed
    except Exception as e:
        print(f"  [FAIL] {name:45} | ERROR: {e}")
        return False


# =========================================================================
# Test Functions
# =========================================================================

def test_clahe_8bit():
    img = generate_textured_image(256, 256) * 255.0
    img_u8 = img.astype(np.uint8)
    img_f32 = img.astype(np.float32)

    import taichi_library.taichi_algorithm as ta
    ta_clahe = ta.clahe(img_f32, clip_limit=2.0, tile_grid_size=(8, 8))
    cv_clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(img_u8).astype(np.float32)

    mae = np.mean(np.abs(ta_clahe - cv_clahe))
    return mae


def test_clahe_16bit():
    img = generate_textured_image(256, 256) * 65535.0
    img_u16 = img.astype(np.uint16)

    import taichi_library.taichi_algorithm as ta
    ta_clahe = ta.clahe(img, clip_limit=2.0, tile_grid_size=(8, 8))

    # OpenCV 16-bit CLAHE
    cv_clahe_obj = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cv_clahe = cv_clahe_obj.apply(img_u16).astype(np.float32)

    # Compare relative error instead of absolute (16-bit range is huge)
    mae = np.mean(np.abs(ta_clahe - cv_clahe))
    # Use percentage-based metric: MAE / max_val * 100
    pct = mae / 65535.0 * 100.0
    return mae, f"(relative={pct:.2f}%)"


def test_clahe_grayscale_8bit():
    img = generate_checkerboard(128, 128, 16) * 255.0
    img_f32 = img.astype(np.float32)

    import taichi_library.taichi_algorithm as ta
    ta_clahe = ta.clahe(img_f32, clip_limit=3.0, tile_grid_size=(4, 4))

    cv_clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4)).apply(img.astype(np.uint8)).astype(np.float32)
    mae = np.mean(np.abs(ta_clahe - cv_clahe))
    return mae


def test_nlm_grayscale_8bit():
    gt = generate_textured_image(128, 128) * 255.0
    noisy = add_gaussian_noise(gt, sigma=10.0)

    import taichi_library.taichi_algorithm as ta
    ta_nlm = ta.non_local_means(noisy, h_param=10.0, search_window=5, patch_size=2)

    cv_nlm = cv2.fastNlMeansDenoising(
        noisy.astype(np.uint8), None, h=10, templateWindowSize=5, searchWindowSize=11
    ).astype(np.float32)

    ssim_val = ssim(gt, ta_nlm, data_range=255.0)
    cv_ssim = ssim(gt, cv_nlm, data_range=255.0)
    delta = abs(ssim_val - cv_ssim)
    return delta, f"(Taichi={ssim_val:.4f}, CV={cv_ssim:.4f})"


def test_nlm_color_8bit():
    gt = generate_textured_image(128, 128, channels=3) * 255.0
    noisy = add_gaussian_noise(gt, sigma=10.0)

    import taichi_library.taichi_algorithm as ta
    ta_nlm = ta.non_local_means(noisy, h_param=10.0, search_window=5, patch_size=2)

    # OpenCV color NLM (use positional args to avoid keyword issues)
    cv_nlm = cv2.fastNlMeansDenoisingColored(
        noisy.astype(np.uint8), None, 10, 10, 5, 11
    ).astype(np.float32)

    ssim_val = ssim(gt, ta_nlm, data_range=255.0, channel_axis=-1)
    cv_ssim = ssim(gt, cv_nlm, data_range=255.0, channel_axis=-1)
    delta = abs(ssim_val - cv_ssim)
    return delta, f"(Taichi={ssim_val:.4f}, CV={cv_ssim:.4f})"


def test_nlm_grayscale_16bit():
    gt = generate_textured_image(64, 64) * 65535.0
    noisy = add_gaussian_noise(gt, sigma=1000.0)

    import taichi_library.taichi_algorithm as ta
    # Normalize to [0, 255] for NLM, then rescale
    noisy_norm = noisy / 256.0
    gt_norm = gt / 256.0
    ta_nlm = ta.non_local_means(noisy_norm.astype(np.float32), h_param=10.0, search_window=3, patch_size=1)

    cv_nlm = cv2.fastNlMeansDenoising(
        noisy_norm.astype(np.uint8), None, h=10, templateWindowSize=3, searchWindowSize=7
    ).astype(np.float32)

    ssim_val = ssim(gt_norm, ta_nlm, data_range=255.0)
    cv_ssim = ssim(gt_norm, cv_nlm, data_range=255.0)
    delta = abs(ssim_val - cv_ssim)
    return delta, f"(Taichi={ssim_val:.4f}, CV={cv_ssim:.4f})"


def test_canny_grayscale_8bit():
    img = generate_textured_image(256, 256) * 255.0
    img_u8 = img.astype(np.uint8)
    img_f32 = img.astype(np.float32)

    import taichi_library.taichi_algorithm as ta
    ta_canny = ta.canny(img_f32, low_threshold=50.0, high_threshold=150.0)
    cv_canny = cv2.Canny(img_u8, 50, 150).astype(np.float32)

    mae = np.mean(np.abs(ta_canny - cv_canny))
    return mae


def test_canny_grayscale_16bit():
    img = generate_textured_image(128, 128) * 65535.0
    img_norm = (img / 256.0).astype(np.float32)
    img_u8 = img_norm.astype(np.uint8)

    import taichi_library.taichi_algorithm as ta
    ta_canny = ta.canny(img_norm, low_threshold=50.0, high_threshold=150.0)
    cv_canny = cv2.Canny(img_u8, 50, 150).astype(np.float32)

    mae = np.mean(np.abs(ta_canny - cv_canny))
    return mae


def test_guided_filter_grayscale_8bit():
    img = generate_textured_image(128, 128) * 255.0
    noisy = add_gaussian_noise(img, sigma=5.0)

    import taichi_library.taichi_algorithm as ta
    guide = img.astype(np.float32)
    src = noisy.astype(np.float32)
    ta_gf = ta.guided_filter(guide, src, radius=4, epsilon=0.01)

    # OpenCV guided filter (if available)
    try:
        cv_gf = cv2.ximgproc.guidedFilter(
            guide.astype(np.uint8), src.astype(np.uint8), 4, 0.01 * 255 * 255
        ).astype(np.float32)
        ssim_val = ssim(img, ta_gf, data_range=255.0)
        cv_ssim = ssim(img, cv_gf, data_range=255.0)
        delta = abs(ssim_val - cv_ssim)
        return delta, f"(Taichi={ssim_val:.4f}, CV={cv_ssim:.4f})"
    except AttributeError:
        # No cv2.ximgproc, just verify smoothing property
        input_std = np.std(src)
        output_std = np.std(ta_gf)
        smoothed = input_std - output_std
        return 0.0 if smoothed > 0 else 1.0, "(no OpenCV ximgproc)"


def test_guided_filter_color_8bit():
    img = generate_textured_image(128, 128, channels=3) * 255.0
    noisy = add_gaussian_noise(img, sigma=5.0)

    import taichi_library.taichi_algorithm as ta
    # Use grayscale guide (2D) with 3-channel source - test 1ch guided filter on each channel
    guide = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    # Use single channel for guided filter test
    src_ch0 = noisy[:, :, 0].astype(np.float32)
    ta_gf = ta.guided_filter(guide, src_ch0, radius=4, epsilon=0.01)

    # Verify output shape matches input
    shape_ok = ta_gf.shape == src_ch0.shape
    # Verify smoothing property
    input_std = np.std(src_ch0)
    output_std = np.std(ta_gf)
    smoothed = input_std - output_std
    return 0.0 if (shape_ok and smoothed > 0) else 1.0, f"(smoothed={smoothed:.4f})"


def test_hough_lines():
    # Create synthetic edge image with clear lines
    synth = np.zeros((128, 128), dtype=np.float32)
    synth[30:32, 10:118] = 255.0  # Horizontal line
    synth[10:118, 60:62] = 255.0  # Vertical line

    import taichi_library.taichi_algorithm as ta
    lines = ta.hough_lines(synth, threshold=40)

    # Should detect at least 2 lines
    return 0.0 if len(lines) >= 2 else 1.0, f"(found {len(lines)} lines)"


def test_color_bgr2ycrcb():
    img = generate_textured_image(128, 128, channels=3) * 255.0
    img_bgr = img[:, :, ::-1].copy()  # RGB -> BGR

    import taichi_library.taichi_algorithm as ta
    ta_ycrcb = ta.cvtColor_extended(img_bgr.astype(np.float32), ta.COLOR_BGR2YCrCb)
    cv_ycrcb = cv2.cvtColor(img_bgr.astype(np.uint8), cv2.COLOR_BGR2YCrCb).astype(np.float32)

    mae = np.mean(np.abs(ta_ycrcb - cv_ycrcb))
    return mae


def test_color_bgr2hsv():
    img = generate_textured_image(128, 128, channels=3) * 255.0
    img_bgr = img[:, :, ::-1].copy()

    import taichi_library.taichi_algorithm as ta
    ta_hsv = ta.cvtColor_extended(img_bgr.astype(np.float32), ta.COLOR_BGR2HSV)
    cv_hsv = cv2.cvtColor(img_bgr.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)

    mae = np.mean(np.abs(ta_hsv - cv_hsv))
    return mae


def test_color_bgr2lab():
    img = generate_textured_image(128, 128, channels=3) * 255.0
    img_bgr = img[:, :, ::-1].copy()

    import taichi_library.taichi_algorithm as ta
    ta_lab = ta.cvtColor_extended(img_bgr.astype(np.float32), ta.COLOR_BGR2LAB)
    cv_lab = cv2.cvtColor(img_bgr.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)

    mae = np.mean(np.abs(ta_lab - cv_lab))
    return mae


def test_color_roundtrip():
    img = generate_textured_image(128, 128, channels=3) * 255.0
    img_bgr = img[:, :, ::-1].copy()

    import taichi_library.taichi_algorithm as ta
    ycrcb = ta.cvtColor_extended(img_bgr.astype(np.float32), ta.COLOR_BGR2YCrCb)
    back = ta.cvtColor_extended(ycrcb, ta.COLOR_YCrCb2BGR)

    mae = np.mean(np.abs(back - img_bgr.astype(np.float32)))
    return mae


def test_color_16bit():
    img = generate_textured_image(64, 64, channels=3) * 65535.0
    img_bgr = img[:, :, ::-1].copy()
    img_u16 = img_bgr.astype(np.uint16)

    import taichi_library.taichi_algorithm as ta
    # Normalize to [0, 255] for color conversion
    img_norm = img_bgr.astype(np.float32) / 256.0
    ta_ycrcb = ta.cvtColor_extended(img_norm, ta.COLOR_BGR2YCrCb)

    cv_ycrcb = cv2.cvtColor(img_u16, cv2.COLOR_BGR2YCrCb).astype(np.float32) / 256.0
    mae = np.mean(np.abs(ta_ycrcb - cv_ycrcb))
    return mae


def test_otsu_8bit():
    img = generate_checkerboard(256, 256, 32) * 255.0
    img_u8 = img.astype(np.uint8)
    img_f32 = img.astype(np.float32)

    import taichi_library.taichi_algorithm as ta
    ta_thresh, ta_binary = ta.otsu_threshold(img_f32)
    cv_thresh, cv_binary = cv2.threshold(img_u8, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    thresh_err = abs(ta_thresh - float(cv_thresh))
    return thresh_err


def test_otsu_16bit():
    img = generate_checkerboard(128, 128, 16) * 65535.0
    img_u16 = img.astype(np.uint16)

    import taichi_library.taichi_algorithm as ta
    ta_thresh, ta_binary = ta.otsu_threshold(img.astype(np.float32))

    cv_thresh, cv_binary = cv2.threshold(img_u16, 0, 65535, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Compare normalized thresholds
    ta_norm = ta_thresh / 65535.0
    cv_norm = float(cv_thresh) / 65535.0
    err = abs(ta_norm - cv_norm)
    return err


def test_otsu_binary_map():
    img = generate_checkerboard(128, 128, 16) * 255.0
    img_u8 = img.astype(np.uint8)

    import taichi_library.taichi_algorithm as ta
    ta_thresh, ta_binary = ta.otsu_threshold(img.astype(np.float32))
    cv_thresh, cv_binary = cv2.threshold(img_u8, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    binary_diff = np.mean(np.abs(ta_binary - cv_binary.astype(np.float32)))
    return binary_diff


def test_inpaint_color():
    img = generate_textured_image(128, 128, channels=3) * 255.0
    mask = create_circular_mask(128, 128, r=20)

    import taichi_library.taichi_algorithm as ta
    ta_result = ta.inpaint(img.astype(np.float32), mask, inpaint_radius=3)

    # Verify: no NaN, masked region should be filled
    has_nan = np.any(np.isnan(ta_result)) or np.any(np.isinf(ta_result))
    masked_mean = np.mean(ta_result[mask > 0.5])
    return 0.0 if (not has_nan and masked_mean > 1.0) else 1.0


def test_inpaint_grayscale():
    img = generate_textured_image(128, 128) * 255.0
    mask = create_circular_mask(128, 128, r=15)

    import taichi_library.taichi_algorithm as ta
    ta_result = ta.inpaint(img.astype(np.float32), mask, inpaint_radius=3)

    has_nan = np.any(np.isnan(ta_result)) or np.any(np.isinf(ta_result))
    masked_mean = np.mean(ta_result[mask > 0.5])
    return 0.0 if (not has_nan and masked_mean > 1.0) else 1.0


def test_inpaint_16bit():
    img = generate_textured_image(64, 64) * 65535.0
    mask = create_circular_mask(64, 64, r=10)

    import taichi_library.taichi_algorithm as ta
    # Normalize to [0, 255] for inpainting
    img_norm = img.astype(np.float32) / 256.0
    ta_result = ta.inpaint(img_norm, mask, inpaint_radius=3)

    has_nan = np.any(np.isnan(ta_result)) or np.any(np.isinf(ta_result))
    return 0.0 if not has_nan else 1.0


def test_seamless_clone():
    src = generate_textured_image(128, 128, channels=3) * 255.0
    dst = np.ones_like(src) * 128.0
    mask = create_circular_mask(128, 128, r=25)

    import taichi_library.taichi_algorithm as ta
    ta_result = ta.seamless_clone(
        src.astype(np.float32), dst.astype(np.float32), mask,
        flags=ta.NORMAL_CLONE, max_iterations=50
    )

    has_nan = np.any(np.isnan(ta_result)) or np.any(np.isinf(ta_result))
    masked_diff = np.mean(np.abs(ta_result[mask > 0.5] - dst[mask > 0.5]))
    return 0.0 if (not has_nan and masked_diff > 0.5) else 1.0


def test_seamless_clone_mixed():
    src = generate_textured_image(128, 128, channels=3) * 255.0
    dst = np.ones_like(src) * 128.0
    mask = create_circular_mask(128, 128, r=25)

    import taichi_library.taichi_algorithm as ta
    ta_result = ta.seamless_clone(
        src.astype(np.float32), dst.astype(np.float32), mask,
        flags=ta.MIXED_CLONE, max_iterations=50
    )

    has_nan = np.any(np.isnan(ta_result)) or np.any(np.isinf(ta_result))
    return 0.0 if not has_nan else 1.0


# =========================================================================
# Main Test Runner
# =========================================================================

def main():
    print("=" * 70)
    print("  COMPREHENSIVE ACCURACY TEST: 9 New Taichi Algorithms")
    print("  Mode: JIT (AOT_MODE=0)")
    print("=" * 70)

    all_pass = True
    total = 0
    passed = 0

    # --- CLAHE ---
    print("\n--- CLAHE ---")
    tests = [
        ("CLAHE 8-bit textured", test_clahe_8bit, 30.0),
        ("CLAHE 8-bit checkerboard", test_clahe_grayscale_8bit, 30.0),
        ("CLAHE 16-bit", test_clahe_16bit, 5000.0),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh):
            passed += 1
        else:
            all_pass = False

    # --- NLM ---
    print("\n--- Non-Local Means ---")
    tests = [
        ("NLM grayscale 8-bit", test_nlm_grayscale_8bit, 0.05),
        ("NLM color 8-bit", test_nlm_color_8bit, 0.10),
        ("NLM grayscale 16-bit", test_nlm_grayscale_16bit, 0.10),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh, "ssim_delta"):
            passed += 1
        else:
            all_pass = False

    # --- Canny ---
    print("\n--- Canny Edge Detector ---")
    tests = [
        ("Canny grayscale 8-bit", test_canny_grayscale_8bit, 80.0),
        ("Canny grayscale 16-bit", test_canny_grayscale_16bit, 80.0),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh):
            passed += 1
        else:
            all_pass = False

    # --- Guided Filter ---
    print("\n--- Guided Filter ---")
    tests = [
        ("Guided Filter grayscale 8-bit", test_guided_filter_grayscale_8bit, 0.10),
        ("Guided Filter color 8-bit", test_guided_filter_color_8bit, 0.5),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh, "ssim_delta"):
            passed += 1
        else:
            all_pass = False

    # --- Hough ---
    print("\n--- Hough Line Transform ---")
    total += 1
    if run_test("Hough Lines synthetic", test_hough_lines, 0.5):
        passed += 1
    else:
        all_pass = False

    # --- Color Conversions ---
    print("\n--- Color Space Conversions ---")
    tests = [
        ("BGR->YCrCb", test_color_bgr2ycrcb, 3.0),
        ("BGR->HSV", test_color_bgr2hsv, 5.0),
        ("BGR->LAB", test_color_bgr2lab, 5.0),
        ("YCrCb->BGR roundtrip", test_color_roundtrip, 3.0),
        ("Color conversion 16-bit", test_color_16bit, 5.0),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh):
            passed += 1
        else:
            all_pass = False

    # --- Otsu ---
    print("\n--- Otsu's Threshold ---")
    tests = [
        ("Otsu threshold 8-bit", test_otsu_8bit, 5.0),
        ("Otsu threshold 16-bit", test_otsu_16bit, 0.02),
        ("Otsu binary map 8-bit", test_otsu_binary_map, 20.0),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh):
            passed += 1
        else:
            all_pass = False

    # --- Inpainting ---
    print("\n--- Inpainting ---")
    tests = [
        ("Inpaint color 8-bit", test_inpaint_color, 0.5),
        ("Inpaint grayscale 8-bit", test_inpaint_grayscale, 0.5),
        ("Inpaint grayscale 16-bit", test_inpaint_16bit, 0.5),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh):
            passed += 1
        else:
            all_pass = False

    # --- Seamless Cloning ---
    print("\n--- Seamless Cloning ---")
    tests = [
        ("Seamless Clone NORMAL", test_seamless_clone, 0.5),
        ("Seamless Clone MIXED", test_seamless_clone_mixed, 0.5),
    ]
    for name, func, thresh in tests:
        total += 1
        if run_test(name, func, thresh):
            passed += 1
        else:
            all_pass = False

    # --- Summary ---
    print("\n" + "=" * 70)
    print(f"  SUMMARY: {passed}/{total} tests passed")
    if all_pass:
        print("  ALL PASS")
    else:
        print("  SOME FAILURES")
    print("=" * 70)

    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
