"""
test_farneback_parity.py — Farneback Optical Flow Parity Test vs OpenCV
========================================================================
Tests the GPU Taichi JIT implementation against cv2.calcOpticalFlowFarneback.

Tests:
  A. Synthetic translation (known ground-truth displacement)
  B. Multiple displacement pairs
  C. Polynomial expansion unit test (separable vs OpenCV)

Usage:
    set AOT_MODE=0
    python test_farneback_parity.py
"""

import os, sys, time
import numpy as np
import cv2

os.environ["AOT_MODE"] = "0"

# Ensure project root is on sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Force Taichi init for JIT mode
import taichi as ti
ti.init(arch=ti.vulkan, offline_cache=True)

from taichi_library.taichi_algorithm.farneback_flow import (
    farneback_flow,
    prepare_gaussian_constants,
)


# =============================================================================
# Helpers
# =============================================================================

def calculate_ssim(img1, img2):
    """Manual SSIM using OpenCV GaussianBlur. Expects float64 [0,255] or [0,1]."""
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    # Normalize to [0,1] if needed
    if img1.max() > 1.0:
        img1 = img1 / 255.0
        img2 = img2 / 255.0
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2
    mu1 = cv2.GaussianBlur(img1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(img2, (11, 11), 1.5)
    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = cv2.GaussianBlur(img1 ** 2, (11, 11), 1.5) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(img2 ** 2, (11, 11), 1.5) - mu2_sq
    sigma12 = cv2.GaussianBlur(img1 * img2, (11, 11), 1.5) - mu1_mu2
    num = (2 * mu1_mu2 + C1) * (2 * sigma12 + C2)
    den = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
    return np.mean(num / den)


def make_textured_image(h, w, seed=42):
    """Generate a textured grayscale image in [0, 255] float32.
    Uses multi-frequency sinusoidal patterns + noise for rich texture."""
    np.random.seed(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # Multi-frequency sinusoidal pattern (rich texture for optical flow)
    pattern = (
        np.sin(xx * 0.05) * np.cos(yy * 0.04) * 80.0
        + np.sin(xx * 0.12 + yy * 0.08) * 40.0
        + np.sin(xx * 0.25 - yy * 0.15) * 20.0
        + np.cos(xx * 0.03 + yy * 0.06) * 60.0
    )
    # Add Gaussian noise for micro-texture
    noise = np.random.randn(h, w).astype(np.float32) * 15.0
    img = pattern + noise + 128.0  # center around 128
    # Clip to [0, 255]
    img = np.clip(img, 0.0, 255.0).astype(np.float32)
    return img


def compute_epe(flow1, flow2):
    """End-Point Error: mean Euclidean distance between flow vectors."""
    diff = flow1 - flow2
    return np.mean(np.sqrt(diff[:, :, 0] ** 2 + diff[:, :, 1] ** 2))


# =============================================================================
# Test A: Synthetic Translation
# =============================================================================

def test_synthetic_translation():
    print("=" * 70)
    print("TEST A: Synthetic Translation")
    print("=" * 70)

    H, W = 512, 512
    ref = make_textured_image(H, W)

    displacements = [
        (2.0, 0.0),
        (3.0, 2.0),
        (5.0, 0.0),
        (5.0, 3.0),
        (-4.0, 1.0),
        (8.0, 0.0),
        (7.0, 5.0),
        (2.0, -6.0),
        (1.5, 0.7),
    ]

    all_passed = True
    for dx, dy in displacements:
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        comp = cv2.warpAffine(ref, M, (W, H), borderMode=cv2.BORDER_REFLECT_101)

        # OpenCV reference
        t0 = time.time()
        flow_cv = cv2.calcOpticalFlowFarneback(
            ref, comp, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2,
            flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN,
        )
        cv_time = (time.time() - t0) * 1000

        # Our GPU implementation
        t0 = time.time()
        flow_gpu = farneback_flow(
            ref, comp,
            pyr_scale=0.5, num_levels=3, win_size=15,
            num_iters=3, poly_n=5, poly_sigma=1.2,
        )
        gpu_time = (time.time() - t0) * 1000

        # Evaluate
        epe = compute_epe(flow_gpu, flow_cv)

        # Center-crop shift estimation
        margin = 50
        crop_cv = flow_cv[margin:H - margin, margin:W - margin]
        crop_gpu = flow_gpu[margin:H - margin, margin:W - margin]

        mean_dx_cv = np.mean(crop_cv[:, :, 0])
        mean_dy_cv = np.mean(crop_cv[:, :, 1])
        mean_dx_gpu = np.mean(crop_gpu[:, :, 0])
        mean_dy_gpu = np.mean(crop_gpu[:, :, 1])

        # Check that flow values match expected displacement
        err_dx = abs(mean_dx_gpu - dx)
        err_dy = abs(mean_dy_gpu - dy)

        # Warp ref using GPU flow and compute SSIM
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        map_x = xs + flow_gpu[:, :, 0]
        map_y = ys + flow_gpu[:, :, 1]
        warped_gpu = cv2.remap(comp, map_x, map_y,
                               cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        ssim_gpu = calculate_ssim(ref, warped_gpu)

        # Pass if: EPE < 2.0 AND flow error < 1.5 px from expected displacement
        passed = epe < 2.0 and err_dx < 1.5 and err_dy < 1.5
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False

        print(f"  d=({dx:+.1f}, {dy:+.1f})  "
              f"GPU=({mean_dx_gpu:.2f}, {mean_dy_gpu:.2f})  "
              f"CV=({mean_dx_cv:.2f}, {mean_dy_cv:.2f})  "
              f"EPE={epe:.3f}  SSIM={ssim_gpu:.4f}  "
              f"CV={cv_time:.0f}ms  GPU={gpu_time:.0f}ms  [{status}]")

    print(f"\n  Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return all_passed


# =============================================================================
# Test B: Polynomial Expansion Unit Test
# =============================================================================

def test_poly_expansion():
    print("\n" + "=" * 70)
    print("TEST B: Polynomial Expansion Unit Test")
    print("=" * 70)

    # Create a gradient image in [0, 255] range
    H, W = 64, 64
    img = np.zeros((H, W), dtype=np.float32)
    for y in range(H):
        for x in range(W):
            img[y, x] = float(x * 2.0 + y * 1.5)  # values in [0, ~224]

    # Compute poly expansion constants
    g, xg, xxg, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(5, 1.2)
    poly_radius = 2

    # CPU reference: compute poly expansion manually for center pixel
    cx, cy = W // 2, H // 2
    n = poly_radius

    # Build 6x6 weighted least-squares
    coords = np.arange(-n, n + 1)
    xx, yy = np.meshgrid(coords, coords)
    xx_flat = xx.flatten()
    yy_flat = yy.flatten()

    w = np.exp(-(xx_flat ** 2 + yy_flat ** 2) / (2.0 * 1.2 ** 2))
    W_mat = np.diag(w)
    X = np.stack([np.ones_like(xx_flat), xx_flat, yy_flat,
                  xx_flat ** 2, yy_flat ** 2, xx_flat * yy_flat], axis=-1)
    P = np.linalg.inv(X.T @ W_mat @ X) @ X.T @ W_mat

    # Extract pixel values
    vals = []
    for dy in range(-n, n + 1):
        for dx in range(-n, n + 1):
            ny = max(0, min(cy + dy, H - 1))
            nx = max(0, min(cx + dx, W - 1))
            vals.append(img[ny, nx])
    vals = np.array(vals)
    coeffs = P @ vals  # [c, b_x, b_y, A_xx, A_yy, A_xy]

    print(f"  CPU reference coefficients at ({cy},{cx}):")
    print(f"    c    = {coeffs[0]:.6f}")
    print(f"    b_x  = {coeffs[1]:.6f}")
    print(f"    b_y  = {coeffs[2]:.6f}")
    print(f"    A_xx = {coeffs[3]:.6f}")
    print(f"    A_yy = {coeffs[4]:.6f}")
    print(f"    A_xy = {coeffs[5]:.6f}")

    # GPU poly expansion
    img_gpu = ti.ndarray(dtype=ti.f32, shape=(H, W))
    img_gpu.from_numpy(img)

    vert_gpu = ti.ndarray(dtype=ti.f32, shape=(H, W, 3))
    poly_gpu = ti.ndarray(dtype=ti.f32, shape=(H, W, 5))

    g_gpu = ti.ndarray(dtype=ti.f32, shape=(poly_radius + 1,))
    g_gpu.from_numpy(g)
    xg_gpu = ti.ndarray(dtype=ti.f32, shape=(poly_radius + 1,))
    xg_gpu.from_numpy(xg)
    xxg_gpu = ti.ndarray(dtype=ti.f32, shape=(poly_radius + 1,))
    xxg_gpu.from_numpy(xxg)

    from taichi_library.taichi_algorithm.farneback_flow import (
        _poly_exp_vertical_kernel,
        _poly_exp_horizontal_kernel,
    )

    _poly_exp_vertical_kernel(img_gpu, vert_gpu, H, W, g_gpu, xg_gpu, xxg_gpu, poly_radius)
    _poly_exp_horizontal_kernel(vert_gpu, poly_gpu, H, W, g_gpu, xg_gpu, xxg_gpu,
                                 ig11, ig03, ig33, ig55, poly_radius)
    ti.sync()

    poly_np = poly_gpu.to_numpy()
    # Output layout: [b_y, b_x, A_yy, A_xx, A_xy]
    gpu_by = poly_np[cy, cx, 0]
    gpu_bx = poly_np[cy, cx, 1]
    gpu_Ayy = poly_np[cy, cx, 2]
    gpu_Axx = poly_np[cy, cx, 3]
    gpu_Axy = poly_np[cy, cx, 4]

    print(f"\n  GPU separable coefficients at ({cy},{cx}):")
    print(f"    b_y  = {gpu_by:.6f}  (ref: {coeffs[2]:.6f})")
    print(f"    b_x  = {gpu_bx:.6f}  (ref: {coeffs[1]:.6f})")
    print(f"    A_yy = {gpu_Ayy:.6f}  (ref: {coeffs[4]:.6f})")
    print(f"    A_xx = {gpu_Axx:.6f}  (ref: {coeffs[3]:.6f})")
    print(f"    A_xy = {gpu_Axy:.6f}  (ref: {coeffs[5]:.6f})")

    # Check accuracy
    err_by = abs(gpu_by - coeffs[2])
    err_bx = abs(gpu_bx - coeffs[1])
    err_Ayy = abs(gpu_Ayy - coeffs[4])
    err_Axx = abs(gpu_Axx - coeffs[3])
    err_Axy = abs(gpu_Axy - coeffs[5])

    max_err = max(err_by, err_bx, err_Ayy, err_Axx, err_Axy)
    print(f"\n  Max absolute error: {max_err:.6e}")

    # Note: boundary handling differs (GPU uses clamp, CPU reference uses clamp too)
    # For center pixels away from borders, errors should be tiny
    passed = max_err < 1e-3
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    return passed


# =============================================================================
# Test C: Constants Validation
# =============================================================================

def test_constants():
    print("\n" + "=" * 70)
    print("TEST C: Constants Validation (prepare_gaussian_constants)")
    print("=" * 70)

    g, xg, xxg, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(5, 1.2)

    print(f"  g   = {g}")
    print(f"  xg  = {xg}")
    print(f"  xxg = {xxg}")
    print(f"  ig11 = {ig11:.8f}")
    print(f"  ig03 = {ig03:.8f}")
    print(f"  ig33 = {ig33:.8f}")
    print(f"  ig55 = {ig55:.8f}")

    # Basic sanity checks
    assert g[0] > 0, "g[0] should be positive (center weight)"
    assert np.all(np.diff(g) < 0), "g should be monotonically decreasing"
    assert ig11 > 0, "ig11 should be positive"
    assert ig33 > 0, "ig33 should be positive"
    assert ig55 > 0, "ig55 should be positive"

    print("  All sanity checks passed.")
    return True


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("Farneback Optical Flow Parity Test")
    print("=" * 70)

    results = {}

    results["Constants"] = test_constants()
    results["Poly Expansion"] = test_poly_expansion()
    results["Synthetic Translation"] = test_synthetic_translation()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, passed in results.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")

    all_ok = all(results.values())
    print(f"\n  Overall: {'ALL TESTS PASSED' if all_ok else 'SOME TESTS FAILED'}")
    sys.exit(0 if all_ok else 1)
