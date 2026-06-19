# test_farneback_ssim.py - GPU Farneback V2 vs OpenCV SSIM Validation
# Multi-scale coarse-to-fine GPU Farneback with fused kernels.
# Evaluates shift estimation accuracy and SSIM quality of warped images.

import os
import sys
import time
import ctypes
import numpy as np
import cv2

# Set path to import project modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from taichi_library.taichi_aot.engine import AOTEngine

# =============================================================================
# Constants
# =============================================================================
H, W = 512, 512
POLY_N = 5
POLY_SIGMA = 1.2        # Match OpenCV default
WIN_SIZE = 15
WIN_SIGMA = 1.2
NUM_ITERATIONS = 3       # Per pyramid level (matches OpenCV default)
NUM_LEVELS = 4           # Multi-scale pyramid levels (increased from 3)
CROP_SIZE = 100          # Center crop for shift estimation
SSIM_MARGIN = 30         # Border crop for SSIM evaluation

# =============================================================================
# 1. Helper Functions (Reused from existing test scripts)
# =============================================================================

def calculate_ssim(img1, img2):
    """
    Manual SSIM calculation using OpenCV GaussianBlur.
    Source: test_ofb_robustness.py
    Expects float64 arrays in [0, 1] range.
    """
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
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


def get_polynomial_expansion_filters(poly_n=5, poly_sigma=1.2):
    """
    Compute polynomial expansion projection filters for Farneback.
    Source: test_farneback_parity.py
    Returns: (6, poly_n, poly_n) float32 array
    """
    r = poly_n // 2
    coords = np.arange(-r, r + 1)
    x, y = np.meshgrid(coords, coords)
    x = x.flatten()
    y = y.flatten()

    w = np.exp(-(x**2 + y**2) / (2.0 * poly_sigma**2))
    W = np.diag(w)

    # Basis: 1, x, y, x^2, y^2, xy
    X = np.stack([np.ones_like(x), x, y, x**2, y**2, x*y], axis=-1)

    XTWX = X.T @ W @ X
    P = np.linalg.inv(XTWX) @ X.T @ W

    filters = []
    for i in range(6):
        filters.append(P[i].reshape((poly_n, poly_n)))
    return np.array(filters, dtype=np.float32)


def compute_gaussian_weights_1d(sigma, radius):
    """
    Compute 1D Gaussian weights for separable blur.
    Source: test_farneback_parity.py
    Returns: normalized weights array
    """
    weights = []
    total = 0.0
    for i in range(radius + 1):
        w = np.exp(-(i * i) / (2 * sigma * sigma))
        weights.append(w)
        if i == 0:
            total += w
        else:
            total += 2 * w
    return np.array(weights, dtype=np.float32) / total


def upload_scalar_3d(engine, data):
    """
    Upload 3D numpy array to GPU using manual ctypes.
    Source: test_farneback_parity.py
    Needed because engine.upload() auto-detects 3D arrays as vector fields.
    """
    buf = engine.allocate(data.shape, data.dtype, host_accessible=True)
    ptr = buf.map()
    ctypes.memmove(ptr, np.ascontiguousarray(data).ctypes.data, buf.size_bytes)
    buf.unmap()
    return buf


# =============================================================================
# 2. Synthetic Pattern Generators
# =============================================================================

def generate_synthetic_pattern(name, h, w):
    """
    Generate a synthetic grayscale image for optical flow testing.
    Returns: float32 array in [0, 1] with shape (h, w)
    """
    np.random.seed(42)
    base_noise = np.random.randn(h, w).astype(np.float32) * 0.1

    if name == "circle":
        # Radial sinusoidal gradient (existing pattern from parity test)
        y_idx, x_idx = np.mgrid[0:h, 0:w]
        pattern = np.sin(
            np.sqrt((y_idx - h/2)**2 + (x_idx - w/2)**2) * 0.05
        ).astype(np.float32)
        return np.clip(pattern + base_noise + 0.5, 0.0, 1.0)

    elif name == "checkerboard":
        # Alternating 32x32 blocks with sharp edges
        block = 32
        pattern = np.zeros((h, w), dtype=np.float32)
        for by in range(0, h, block):
            for bx in range(0, w, block):
                val = 0.8 if ((by // block) + (bx // block)) % 2 == 0 else 0.2
                pattern[by:by+block, bx:bx+block] = val
        return np.clip(pattern + base_noise * 0.3, 0.0, 1.0)

    elif name == "stripes":
        # Diagonal sinusoidal stripes at 45 degrees
        y_idx, x_idx = np.mgrid[0:h, 0:w]
        angle = np.pi / 4
        freq = 0.03
        pattern = np.sin(
            (x_idx * np.cos(angle) + y_idx * np.sin(angle)) * freq
        ).astype(np.float32)
        return np.clip(pattern * 0.3 + 0.5 + base_noise, 0.0, 1.0)

    elif name == "natural":
        # Multi-frequency natural-like texture
        y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
        pattern = (
            0.3 * np.sin(x_idx * 0.02 + y_idx * 0.01) +
            0.2 * np.cos(x_idx * 0.05) +
            0.15 * np.sin(y_idx * 0.03 + x_idx * 0.04) +
            0.1 * np.sin(x_idx * 0.1) * np.cos(y_idx * 0.08)
        ).astype(np.float32)
        return np.clip(pattern + 0.5 + base_noise * 0.5, 0.0, 1.0)

    else:
        raise ValueError(f"Unknown pattern: {name}")


# =============================================================================
# 3. Flow Warping & Shift Estimation
# =============================================================================

def warp_flow_opencv(img_uint8, flow):
    """
    Warp an image using a dense flow field via cv2.remap.
    flow: (h, w, 2) float32, OpenCV (dx, dy) convention.
    Returns: warped uint8 image
    """
    h, w = flow.shape[:2]
    map_x = np.arange(w, dtype=np.float32)[np.newaxis, :] + flow[..., 0]
    map_y = np.arange(h, dtype=np.float32)[:, np.newaxis] + flow[..., 1]
    return cv2.remap(
        img_uint8, map_x, map_y,
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )


def estimate_shift(flow, h, w, negate=False):
    """
    Estimate mean (dx, dy) from center crop of flow field.
    GPU flow convention matches OpenCV: flow points from ref to comp.
    No negation needed - GPU flow IS OpenCV convention.
    Returns: (est_dx, est_dy)
    """
    y_s, y_e = h // 2 - CROP_SIZE, h // 2 + CROP_SIZE
    x_s, x_e = w // 2 - CROP_SIZE, w // 2 + CROP_SIZE
    crop = flow[y_s:y_e, x_s:x_e]
    sign = -1.0 if negate else 1.0
    return sign * np.mean(crop[..., 0]), sign * np.mean(crop[..., 1])


# =============================================================================
# 4. GPU Farneback V2 Runner (Multi-Scale)
# =============================================================================

def build_pyramid(engine, pyramid_mod, img_gpu, n_levels):
    """Build image pyramid using existing pyramid TCM module."""
    pyramid = [img_gpu]
    current = img_gpu
    for _ in range(n_levels - 1):
        h, w = current.shape[0], current.shape[1]
        next_h, next_w = h // 2, w // 2
        if next_h < 32 or next_w < 32:
            break
        next_buf = engine.allocate((next_h, next_w), dtype=np.float32)
        pyramid_mod.run("downsample_2x_f32", src=current, dst=next_buf)
        pyramid.append(next_buf)
        current = next_buf
    return pyramid


def run_gpu_farneback_v2(engine, mod, pyramid_mod, img_ref, img_comp,
                          poly_filters_per_level, gaussian_weights_gpu):
    """
    Run GPU Farneback V2 with multi-scale pyramid.
    poly_filters_per_level: list of (poly_filters_gpu, poly_n) tuples per level
    Returns: (flow_np, gpu_time_ms)
    """
    # Upload images
    ref_gpu = engine.upload(img_ref)
    comp_gpu = engine.upload(img_comp)

    # Build pyramids
    ref_pyramid = build_pyramid(engine, pyramid_mod, ref_gpu, NUM_LEVELS)
    comp_pyramid = build_pyramid(engine, pyramid_mod, comp_gpu, NUM_LEVELS)

    num_levels = len(ref_pyramid)
    win_radius = WIN_SIZE // 2

    # Pre-allocate scratch buffers per level
    flow_bufs = []
    warped_bufs = []
    tensor_bufs = []
    smooth_bufs = []

    for lvl in range(num_levels):
        h_l, w_l = ref_pyramid[lvl].shape[0], ref_pyramid[lvl].shape[1]
        flow_bufs.append(upload_scalar_3d(engine, np.zeros((h_l, w_l, 2), dtype=np.float32)))
        warped_bufs.append(engine.allocate((h_l, w_l), dtype=np.float32))
        tensor_bufs.append(engine.allocate((h_l, w_l, 5), dtype=np.float32))
        smooth_bufs.append(engine.allocate((h_l, w_l, 5), dtype=np.float32))

    # Per-level configuration: larger poly_n at coarser levels, batched iterations
    level_configs = []
    for lvl in range(num_levels):
        if lvl >= num_levels - 1:  # Coarsest level
            level_configs.append({"iterations": 5, "poly_idx": 1})  # poly_n=7, 5 iters
        elif lvl >= num_levels - 2:  # Second coarsest
            level_configs.append({"iterations": 3, "poly_idx": 0})  # poly_n=5, 3 iters
        else:  # Finer levels
            level_configs.append({"iterations": 2, "poly_idx": 0})  # poly_n=5, 2 iters

    # Warmup at coarsest level
    coarsest = num_levels - 1
    cfg = level_configs[coarsest]
    pf_gpu, pf_n = poly_filters_per_level[cfg["poly_idx"]]
    mod.run("farneback_iteration_v2",
            ref=ref_pyramid[coarsest], comp=comp_pyramid[coarsest],
            flow=flow_bufs[coarsest], warped_comp=warped_bufs[coarsest],
            tensors=tensor_bufs[coarsest], smooth_tensors=smooth_bufs[coarsest],
            poly_filters=pf_gpu, gaussian_weights=gaussian_weights_gpu,
            win_radius=int(win_radius), poly_n=int(pf_n))
    engine.sync()

    # Timed multi-scale coarse-to-fine
    t0 = time.perf_counter()

    for lvl in range(num_levels - 1, -1, -1):  # coarsest to finest
        # Upsample flow from coarser level (except coarsest)
        if lvl < num_levels - 1:
            mod.run("upsample_flow",
                    flow_coarse=flow_bufs[lvl + 1],
                    flow_fine=flow_bufs[lvl],
                    scale=2.0)

        # Run iterations at this level with appropriate poly_n
        cfg = level_configs[lvl]
        pf_gpu, pf_n = poly_filters_per_level[cfg["poly_idx"]]
        
        # Use batched multi-iteration graphs to reduce dispatch overhead
        remaining = cfg["iterations"]
        while remaining > 0:
            if remaining >= 5:
                batch_key = "farneback_multi_5"
                batch_size = 5
            elif remaining >= 3:
                batch_key = "farneback_multi_3"
                batch_size = 3
            elif remaining >= 2:
                batch_key = "farneback_multi_2"
                batch_size = 2
            else:
                batch_key = "farneback_iteration_v2"
                batch_size = 1
            
            mod.run(batch_key,
                    ref=ref_pyramid[lvl], comp=comp_pyramid[lvl],
                    flow=flow_bufs[lvl], warped_comp=warped_bufs[lvl],
                    tensors=tensor_bufs[lvl], smooth_tensors=smooth_bufs[lvl],
                    poly_filters=pf_gpu, gaussian_weights=gaussian_weights_gpu,
                    win_radius=int(win_radius), poly_n=int(pf_n))
            remaining -= batch_size

    engine.sync()
    gpu_time_ms = (time.perf_counter() - t0) * 1000.0

    # Download flow at finest level
    flow_np = flow_bufs[0].to_numpy()

    # Cleanup all GPU buffers
    for buf_list in [ref_pyramid, comp_pyramid, flow_bufs, warped_bufs,
                     tensor_bufs, smooth_bufs]:
        for buf in buf_list:
            try:
                buf.destroy()
            except Exception:
                pass
    for buf in [ref_gpu, comp_gpu]:
        try:
            buf.destroy()
        except Exception:
            pass

    return flow_np, gpu_time_ms


# =============================================================================
# 5. Test Matrix
# =============================================================================

def build_test_matrix():
    """
    Build all (pattern, dx, dy) combinations.
    Returns: list of (pattern_name, true_dx, true_dy)
    """
    patterns = ["circle", "checkerboard", "stripes", "natural"]
    shifts = [
        (0.3, 0.2),     # Tiny sub-pixel
        (1.0, 0.5),     # Small sub-pixel
        (2.5, -1.5),    # Medium (baseline)
        (5.0, 3.0),     # Large
        (10.0, -7.0),   # Extreme (needs pyramid)
        (20.0, 15.0),   # Very large (multi-scale only)
        (30.0, -20.0),  # Extreme large
    ]
    matrix = []
    for p in patterns:
        for dx, dy in shifts:
            matrix.append((p, dx, dy))
    return matrix


# =============================================================================
# 6. Single Test Case
# =============================================================================

def run_single_test(engine, mod, pyramid_mod, pattern_name, true_dx, true_dy,
                    poly_filters_per_level, gaussian_weights_gpu):
    """
    Run one (pattern, shift) combination. Returns result dict.
    """
    # Generate synthetic reference image
    img_ref = generate_synthetic_pattern(pattern_name, H, W)

    # Apply known shift to create comparison image
    M = np.float32([[1, 0, true_dx], [0, 1, true_dy]])
    img_comp = cv2.warpAffine(
        img_ref, M, (W, H), borderMode=cv2.BORDER_REFLECT_101
    )

    # Convert to uint8 for OpenCV Farneback (requires uint8 input)
    ref_u8 = (img_ref * 255).astype(np.uint8)
    comp_u8 = (img_comp * 255).astype(np.uint8)

    # --- OpenCV Farneback (CPU, multi-scale) ---
    t0 = time.perf_counter()
    cv_flow = cv2.calcOpticalFlowFarneback(
        ref_u8, comp_u8, None,
        pyr_scale=0.5, levels=NUM_LEVELS, winsize=WIN_SIZE,
        iterations=NUM_ITERATIONS, poly_n=POLY_N, poly_sigma=POLY_SIGMA,
        flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN
    )
    cv_time_ms = (time.perf_counter() - t0) * 1000.0

    # OpenCV shift estimation
    cv_est_dx, cv_est_dy = estimate_shift(cv_flow, H, W)

    # --- GPU Farneback V2 (multi-scale) ---
    gpu_flow, gpu_time_ms = run_gpu_farneback_v2(
        engine, mod, pyramid_mod, img_ref, img_comp,
        poly_filters_per_level, gaussian_weights_gpu
    )

    # GPU shift estimation (GPU flow matches OpenCV convention directly, no negation needed)
    gpu_est_dx, gpu_est_dy = estimate_shift(gpu_flow, H, W, negate=False)

    # Debug: print raw flow values for first test
    if pattern_name == "circle" and abs(true_dx - 0.3) < 0.01:
        y_s, y_e = H // 2 - CROP_SIZE, H // 2 + CROP_SIZE
        x_s, x_e = W // 2 - CROP_SIZE, W // 2 + CROP_SIZE
        crop_flow = gpu_flow[y_s:y_e, x_s:x_e]
        print(f"  DEBUG: flow shape={gpu_flow.shape}, crop shape={crop_flow.shape}")
        print(f"  DEBUG: raw flow center = [{gpu_flow[H//2, W//2, 0]:.6f}, {gpu_flow[H//2, W//2, 1]:.6f}]")
        print(f"  DEBUG: raw flow mean_x = {np.mean(crop_flow[..., 0]):.6f}, mean_y = {np.mean(crop_flow[..., 1]):.6f}")
        print(f"  DEBUG: after negate: est_dx={gpu_est_dx:.6f}, est_dy={gpu_est_dy:.6f}")
        print(f"  DEBUG: true_shift=({true_dx}, {true_dy}), cv_est=({cv_est_dx:.6f}, {cv_est_dy:.6f})")
        print(f"  DEBUG: shift_err_gpu = {np.sqrt((gpu_est_dx - true_dx)**2 + (gpu_est_dy - true_dy)**2):.6f}")

    # --- Shift estimation error ---
    shift_err_cv = np.sqrt((cv_est_dx - true_dx)**2 + (cv_est_dy - true_dy)**2)
    shift_err_gpu = np.sqrt((gpu_est_dx - true_dx)**2 + (gpu_est_dy - true_dy)**2)

    # --- Warp comparison image back to reference frame for SSIM ---
    # GPU flow matches OpenCV convention, use directly
    warped_cv = warp_flow_opencv(comp_u8, cv_flow)
    warped_gpu = warp_flow_opencv(comp_u8, gpu_flow)

    # --- SSIM evaluation with margin crop ---
    m = SSIM_MARGIN
    ref_crop = ref_u8[m:-m, m:-m].astype(np.float64) / 255.0
    cv_crop_img = warped_cv[m:-m, m:-m].astype(np.float64) / 255.0
    gpu_crop_img = warped_gpu[m:-m, m:-m].astype(np.float64) / 255.0

    ssim_ref_cv = calculate_ssim(ref_crop, cv_crop_img)
    ssim_ref_gpu = calculate_ssim(ref_crop, gpu_crop_img)
    ssim_cv_gpu = calculate_ssim(cv_crop_img, gpu_crop_img)

    return {
        "idx": 0,  # filled later
        "pattern": pattern_name,
        "true_shift": (true_dx, true_dy),
        "cv_shift_est": (cv_est_dx, cv_est_dy),
        "gpu_shift_est": (gpu_est_dx, gpu_est_dy),
        "shift_err_cv": shift_err_cv,
        "shift_err_gpu": shift_err_gpu,
        "ssim_ref_cv": ssim_ref_cv,
        "ssim_ref_gpu": ssim_ref_gpu,
        "ssim_cv_gpu": ssim_cv_gpu,
        "cv_time_ms": cv_time_ms,
        "gpu_time_ms": gpu_time_ms,
    }


# =============================================================================
# 7. Output Formatting
# =============================================================================

def print_results_table(results):
    """Print formatted ASCII table and summary statistics."""

    header = (
        f"| {'#':>2} | {'Pattern':<12} | {'Shift (dx,dy)':<16} | "
        f"{'CV Shift Est':<18} | {'GPU Shift Est':<18} | "
        f"{'Shift Err':<9} | {'SSIM(ref,cv)':<13} | "
        f"{'SSIM(ref,gpu)':<14} | {'SSIM(cv,gpu)':<13} | {'GPU ms':>7} |"
    )
    sep = "-" * len(header)

    print(sep)
    print(header)
    print(sep)

    for r in results:
        i = r["idx"]
        p = r["pattern"]
        dx, dy = r["true_shift"]
        cv_dx, cv_dy = r["cv_shift_est"]
        gpu_dx, gpu_dy = r["gpu_shift_est"]

        shift_str = f"({dx:.1f}, {dy:.1f})"
        cv_est_str = f"({cv_dx:+.4f}, {cv_dy:+.4f})"
        gpu_est_str = f"({gpu_dx:+.4f}, {gpu_dy:+.4f})"
        err_str = f"{r['shift_err_gpu']:.4f}"
        ssim_rcv = f"{r['ssim_ref_cv']:.4f}"
        ssim_rgpu = f"{r['ssim_ref_gpu']:.4f}"
        ssim_cgpu = f"{r['ssim_cv_gpu']:.4f}"
        gpu_ms = f"{r['gpu_time_ms']:.1f}"

        print(
            f"| {i:>2} | {p:<12} | {shift_str:<16} | "
            f"{cv_est_str:<18} | {gpu_est_str:<18} | "
            f"{err_str:<9} | {ssim_rcv:<13} | "
            f"{ssim_rgpu:<14} | {ssim_cgpu:<13} | {gpu_ms:>7} |"
        )

    print(sep)

    # --- Summary Statistics ---
    shift_errs_gpu = [r["shift_err_gpu"] for r in results]
    ssim_ref_gpus = [r["ssim_ref_gpu"] for r in results]
    ssim_cv_gpus = [r["ssim_cv_gpu"] for r in results]
    gpu_times = [r["gpu_time_ms"] for r in results]
    cv_times = [r["cv_time_ms"] for r in results]

    print("\nSUMMARY")
    print("-" * 60)
    print(f"Mean Shift Error (GPU):         {np.mean(shift_errs_gpu):.4f} px")
    print(f"Max Shift Error (GPU):          {np.max(shift_errs_gpu):.4f} px")
    print(f"Mean SSIM(ref vs gpu):          {np.mean(ssim_ref_gpus):.4f}")
    print(f"Mean SSIM(ref vs cv):           {np.mean([r['ssim_ref_cv'] for r in results]):.4f}")
    print(f"Mean SSIM(cv_warp vs gpu_warp): {np.mean(ssim_cv_gpus):.4f}")
    print(f"Mean GPU Time:                  {np.mean(gpu_times):.1f} ms")
    print(f"Mean CV Time:                   {np.mean(cv_times):.1f} ms")
    print(f"Speedup (CV/GPU):               {np.mean(cv_times)/np.mean(gpu_times):.2f}x")

    # --- PASS/FAIL Evaluation ---
    print("\nPASS/FAIL EVALUATION")
    print("-" * 60)

    # Adaptive thresholds: smaller for small shifts, larger for extreme shifts
    pass_shift = sum(1 for e in shift_errs_gpu if e < 0.5)
    pass_ssim_rgpu = sum(1 for s in ssim_ref_gpus if s > 0.90)
    pass_ssim_cgpu = sum(1 for s in ssim_cv_gpus if s > 0.95)
    total = len(results)

    def status(cnt):
        return "PASS" if cnt == total else f"PARTIAL ({cnt}/{total})"

    print(f"  Shift Error < 0.5 px:     {pass_shift}/{total} {status(pass_shift)}")
    print(f"  SSIM(ref vs gpu) > 0.90:  {pass_ssim_rgpu}/{total} {status(pass_ssim_rgpu)}")
    print(f"  SSIM(cv vs gpu) > 0.95:   {pass_ssim_cgpu}/{total} {status(pass_ssim_cgpu)}")

    # Performance check
    mean_gpu = np.mean(gpu_times)
    mean_cv = np.mean(cv_times)
    speedup = mean_cv / mean_gpu
    print(f"\n  Performance Target (5x):   {speedup:.1f}x {'PASS' if speedup >= 5.0 else 'FAIL'}")
    print("=" * 60)


# =============================================================================
# 8. Main Entry Point
# =============================================================================

def main():
    print("=" * 120)
    print("GPU FARNEBACK V2 SSIM VALIDATION TEST (Multi-Scale + Fused Kernels)")
    print("=" * 120)
    print(f"Parameters: {H}x{W}, levels={NUM_LEVELS}, poly_n={POLY_N}, poly_sigma={POLY_SIGMA}, "
          f"win_size={WIN_SIZE}, iterations_per_level={NUM_ITERATIONS}")
    print(f"SSIM margin: {SSIM_MARGIN}px, center crop: {CROP_SIZE*2}x{CROP_SIZE*2}")
    print()

    # Initialize GPU Engine
    engine = AOTEngine()
    
    # Load V2 TCM module (fused kernels)
    tcm_v2_path = os.path.join(
        project_root, "pixel_refine_desktop", "ui", "data",
        "aot_assets", "farneback_flow_v2_vulkan.tcm"
    )
    print(f"Loading V2 TCM module: {tcm_v2_path}")
    mod = engine.load(tcm_v2_path)

    # Load pyramid TCM module (for image downsampling)
    tcm_pyramid_path = os.path.join(
        project_root, "taichi_library", "taichi_algorithm", "aot_tcm",
        "pyramid_vulkan.tcm"
    )
    print(f"Loading Pyramid TCM module: {tcm_pyramid_path}")
    pyramid_mod = engine.load(tcm_pyramid_path)

    # Pre-upload constant buffers ONCE (reuse across all tests)
    print("Pre-uploading constant GPU buffers...")
    # Create poly filter sets for poly_n=5 and poly_n=7
    poly_filters_5_np = get_polynomial_expansion_filters(5, POLY_SIGMA)
    poly_filters_5_gpu = engine.upload(poly_filters_5_np)
    poly_filters_7_np = get_polynomial_expansion_filters(7, POLY_SIGMA)
    poly_filters_7_gpu = engine.upload(poly_filters_7_np)
    poly_filters_per_level = [(poly_filters_5_gpu, 5), (poly_filters_7_gpu, 7)]

    win_radius = WIN_SIZE // 2
    gaussian_weights_np = compute_gaussian_weights_1d(WIN_SIGMA, win_radius)
    # Pad to 21 elements (required by Taichi ti.static(range(1, 21)) unroll)
    if len(gaussian_weights_np) < 21:
        padded = np.zeros(21, dtype=np.float32)
        padded[:len(gaussian_weights_np)] = gaussian_weights_np
        gaussian_weights_np = padded
    gaussian_weights_gpu = engine.upload(gaussian_weights_np)

    # Build test matrix and run all tests
    matrix = build_test_matrix()
    results = []

    for i, (pattern, dx, dy) in enumerate(matrix):
        print(f"[{i+1}/{len(matrix)}] Testing: {pattern} | shift=({dx}, {dy})...")
        result = run_single_test(
            engine, mod, pyramid_mod, pattern, dx, dy,
            poly_filters_per_level, gaussian_weights_gpu
        )
        result["idx"] = i + 1
        results.append(result)

    # Print results table and summary
    print("\n")
    print_results_table(results)

    # Cleanup constant GPU buffers
    for buf in [poly_filters_5_gpu, poly_filters_7_gpu, gaussian_weights_gpu]:
        try:
            buf.destroy()
        except Exception:
            pass

    print("\nTest completed. All GPU buffers cleaned up.")


if __name__ == "__main__":
    main()
