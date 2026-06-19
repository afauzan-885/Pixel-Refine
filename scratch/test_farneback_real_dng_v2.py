# test_farneback_real_dng_v2.py - GPU Farneback V2 vs OpenCV on Real DNG Images
# Tests optical flow on real burst DNG images with different demosaicing algorithms.
# Compares SSIM and performance between GPU (Taichi) and CPU (OpenCV) Farneback.
# 
# Flow Convention Fix:
# GPU flow = -(cmp - ref) * 0.5 (inverted relative to OpenCV)
# OpenCV flow = (cmp - ref)
# To convert: negate GPU flow to get (cmp - ref) * 0.5

import os
import sys
import time
import ctypes
import numpy as np
import cv2
import rawpy

# Set path to import project modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from taichi_library.taichi_aot.engine import AOTEngine

# =============================================================================
# Constants
# =============================================================================
POLY_N = 5
POLY_SIGMA = 1.2        # Match OpenCV default
WIN_SIZE = 15
WIN_SIGMA = 1.2
NUM_ITERATIONS = 3       # Per pyramid level (matches OpenCV default)
NUM_LEVELS = 4           # Multi-scale pyramid levels
CROP_SIZE = 100          # Center crop for shift estimation
SSIM_MARGIN = 30         # Border crop for SSIM evaluation
MAX_IMAGE_SIZE = 1024    # Maximum image dimension for processing

# =============================================================================
# 1. Helper Functions
# =============================================================================

def calculate_ssim(img1, img2):
    """
    Manual SSIM calculation using OpenCV GaussianBlur.
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
    Needed because engine.upload() auto-detects 3D arrays as vector fields.
    """
    buf = engine.allocate(data.shape, data.dtype, host_accessible=True)
    ptr = buf.map()
    ctypes.memmove(ptr, np.ascontiguousarray(data).ctypes.data, buf.size_bytes)
    buf.unmap()
    return buf


def load_dng_image(path, demosaic_algo='AHD', max_size=MAX_IMAGE_SIZE):
    """
    Load DNG image and demosaic to grayscale.
    demosaic_algo: 'AHD' (Hamilton) or 'LINEAR' (bilinear)
    Returns: float32 grayscale array in [0, 1] with shape (h, w)
    """
    print(f"  Loading DNG: {os.path.basename(path)} with {demosaic_algo} demosaicing...")
    
    with rawpy.imread(path) as raw:
        if demosaic_algo == 'AHD':
            # Hamilton-Adams Directed (AHD) - high quality
            rgb = raw.postprocess(
                demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
                use_camera_wb=True,
                no_auto_bright=True,
                output_bps=16,
                output_color=rawpy.ColorSpace.sRGB,
            )
        elif demosaic_algo == 'LINEAR':
            # Bilinear - fast, lower quality
            rgb = raw.postprocess(
                demosaic_algorithm=rawpy.DemosaicAlgorithm.LINEAR,
                use_camera_wb=True,
                no_auto_bright=True,
                output_bps=16,
                output_color=rawpy.ColorSpace.sRGB,
            )
        else:
            raise ValueError(f"Unknown demosaic algorithm: {demosaic_algo}")
    
    # Convert to float32 [0, 1]
    rgb_f32 = rgb.astype(np.float32) / 65535.0
    
    # Convert to grayscale
    gray = cv2.cvtColor(rgb_f32, cv2.COLOR_RGB2GRAY)
    
    # Resize if too large (maintain aspect ratio)
    h, w = gray.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
        print(f"    Resized from {w}x{h} to {new_w}x{new_h}")
    
    print(f"    Final shape: {gray.shape}, dtype: {gray.dtype}, range: [{gray.min():.3f}, {gray.max():.3f}]")
    return gray


# =============================================================================
# 2. Flow Warping & Shift Estimation
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


def estimate_shift(flow, h, w):
    """
    Estimate mean (dx, dy) from center crop of flow field.
    Returns: (est_dx, est_dy)
    """
    y_s, y_e = h // 2 - CROP_SIZE, h // 2 + CROP_SIZE
    x_s, x_e = w // 2 - CROP_SIZE, w // 2 + CROP_SIZE
    crop = flow[y_s:y_e, x_s:x_e]
    return np.mean(crop[..., 0]), np.mean(crop[..., 1])


def convert_gpu_flow_to_opencv(gpu_flow):
    """
    Now that the GPU flow convention matches OpenCV exactly,
    we can return the flow directly.
    """
    return gpu_flow



# =============================================================================
# 3. GPU Farneback V2 Runner (Multi-Scale)
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
    h, w = img_ref.shape[:2]
    
    # Upload images
    ref_gpu = engine.upload(img_ref)
    comp_gpu = engine.upload(img_comp)

    # Build pyramids using OpenCV CPU (ensures 100% parity downsampling)
    ref_pyramid_np = [img_ref]
    comp_pyramid_np = [img_comp]
    curr_ref = img_ref
    curr_comp = img_comp
    for _ in range(NUM_LEVELS - 1):
        curr_ref = cv2.pyrDown(curr_ref)
        curr_comp = cv2.pyrDown(curr_comp)
        ref_pyramid_np.append(curr_ref)
        comp_pyramid_np.append(curr_comp)
        
    ref_pyramid = [engine.upload(lvl) for lvl in ref_pyramid_np]
    comp_pyramid = [engine.upload(lvl) for lvl in comp_pyramid_np]

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

    # Per-level configuration: match OpenCV (constant iterations and poly_n=5)
    level_configs = []
    for lvl in range(num_levels):
        level_configs.append({"iterations": NUM_ITERATIONS, "poly_idx": 0})

    # Warmup at coarsest level
    coarsest = num_levels - 1
    cfg = level_configs[coarsest]
    pf_gpu, pf_n = poly_filters_per_level[cfg["poly_idx"]]
    print(f"DEBUG warmup farneback_iteration_v2 at coarsest level:")
    print(f"  ref: {ref_pyramid[coarsest].handle}")
    print(f"  comp: {comp_pyramid[coarsest].handle}")
    print(f"  flow: {flow_bufs[coarsest].handle}")
    print(f"  warped_comp: {warped_bufs[coarsest].handle}")
    print(f"  tensors: {tensor_bufs[coarsest].handle}")
    print(f"  smooth_tensors: {smooth_bufs[coarsest].handle}")
    print(f"  poly_filters: {pf_gpu.handle}")
    print(f"  gaussian_weights: {gaussian_weights_gpu.handle}")
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
            
            print(f"DEBUG running {batch_key} at level {lvl}:")
            print(f"  ref: {ref_pyramid[lvl].handle}")
            print(f"  comp: {comp_pyramid[lvl].handle}")
            print(f"  flow: {flow_bufs[lvl].handle}")
            print(f"  warped_comp: {warped_bufs[lvl].handle}")
            print(f"  tensors: {tensor_bufs[lvl].handle}")
            print(f"  smooth_tensors: {smooth_bufs[lvl].handle}")
            print(f"  poly_filters: {pf_gpu.handle}")
            print(f"  gaussian_weights: {gaussian_weights_gpu.handle}")
            mod.run(batch_key,
                    ref=ref_pyramid[lvl], comp=comp_pyramid[lvl],
                    flow=flow_bufs[lvl], warped_comp=warped_bufs[lvl],
                    tensors=tensor_bufs[lvl], smooth_tensors=smooth_bufs[lvl],
                    poly_filters=pf_gpu, gaussian_weights=gaussian_weights_gpu,
                    win_radius=int(win_radius), poly_n=int(pf_n))
            remaining -= batch_size

        engine.sync()
        lvl_flow = flow_bufs[lvl].to_numpy()
        print(f"  Level {lvl} flow stats: mean={np.mean(lvl_flow, axis=(0,1))}, max={np.max(np.abs(lvl_flow), axis=(0,1))}")

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
# 4. Test Case for Real DNG Images
# =============================================================================

def run_real_dng_test(engine, mod, pyramid_mod, ref_path, comp_path, demosaic_algo,
                      poly_filters_per_level, gaussian_weights_gpu):
    """
    Run optical flow test on real DNG images.
    Returns: result dict
    """
    print(f"\n{'='*80}")
    print(f"Testing with {demosaic_algo} demosaicing")
    print(f"Reference: {os.path.basename(ref_path)}")
    print(f"Comparison: {os.path.basename(comp_path)}")
    print(f"{'='*80}")
    
    # Load images
    t_load_start = time.perf_counter()
    img_ref = load_dng_image(ref_path, demosaic_algo)
    img_comp = load_dng_image(comp_path, demosaic_algo)
    t_load_ms = (time.perf_counter() - t_load_start) * 1000.0
    
    h, w = img_ref.shape[:2]
    print(f"Image size: {w}x{h}")
    
    # Convert to uint8 for OpenCV Farneback (requires uint8 input)
    ref_u8 = (np.clip(img_ref, 0, 1) * 255).astype(np.uint8)
    comp_u8 = (np.clip(img_comp, 0, 1) * 255).astype(np.uint8)
    
    # --- OpenCV Farneback (CPU, multi-scale) ---
    print("\nRunning OpenCV Farneback (CPU)...")
    t0 = time.perf_counter()
    cv_flow = cv2.calcOpticalFlowFarneback(
        ref_u8, comp_u8, None,
        pyr_scale=0.5, levels=NUM_LEVELS, winsize=WIN_SIZE,
        iterations=NUM_ITERATIONS, poly_n=POLY_N, poly_sigma=POLY_SIGMA,
        flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN
    )
    cv_time_ms = (time.perf_counter() - t0) * 1000.0
    
    # OpenCV shift estimation
    cv_est_dx, cv_est_dy = estimate_shift(cv_flow, h, w)
    
    # --- GPU Farneback V2 (multi-scale) ---
    print("Running GPU Farneback V2 (Taichi)...")
    gpu_flow_raw, gpu_time_ms = run_gpu_farneback_v2(
        engine, mod, pyramid_mod, img_ref, img_comp,
        poly_filters_per_level, gaussian_weights_gpu
    )
    
    # Convert GPU flow to OpenCV convention
    gpu_flow = convert_gpu_flow_to_opencv(gpu_flow_raw)
    
    # GPU shift estimation
    gpu_est_dx, gpu_est_dy = estimate_shift(gpu_flow, h, w)
    
    # Debug: Print flow statistics
    print(f"\n  DEBUG: GPU flow shape={gpu_flow.shape}")
    print(f"  DEBUG: GPU flow center = [{gpu_flow[h//2, w//2, 0]:.6f}, {gpu_flow[h//2, w//2, 1]:.6f}]")
    print(f"  DEBUG: CV flow center = [{cv_flow[h//2, w//2, 0]:.6f}, {cv_flow[h//2, w//2, 1]:.6f}]")
    print(f"  DEBUG: GPU flow mean = [{np.mean(gpu_flow[..., 0]):.6f}, {np.mean(gpu_flow[..., 1]):.6f}]")
    print(f"  DEBUG: CV flow mean = [{np.mean(cv_flow[..., 0]):.6f}, {np.mean(cv_flow[..., 1]):.6f}]")
    print(f"  DEBUG: GPU/CV ratio = [{np.mean(gpu_flow[..., 0])/np.mean(cv_flow[..., 0]):.4f}, {np.mean(gpu_flow[..., 1])/np.mean(cv_flow[..., 1]):.4f}]")
    
    # --- Warp comparison images for SSIM ---
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
    
    # --- Flow statistics ---
    flow_magnitude_cv = np.sqrt(cv_flow[..., 0]**2 + cv_flow[..., 1]**2)
    flow_magnitude_gpu = np.sqrt(gpu_flow[..., 0]**2 + gpu_flow[..., 1]**2)
    
    result = {
        "demosaic_algo": demosaic_algo,
        "ref_image": os.path.basename(ref_path),
        "comp_image": os.path.basename(comp_path),
        "image_size": f"{w}x{h}",
        "load_time_ms": t_load_ms,
        "cv_time_ms": cv_time_ms,
        "gpu_time_ms": gpu_time_ms,
        "speedup": cv_time_ms / gpu_time_ms if gpu_time_ms > 0 else 0,
        "cv_shift_est": (cv_est_dx, cv_est_dy),
        "gpu_shift_est": (gpu_est_dx, gpu_est_dy),
        "shift_diff": np.sqrt((cv_est_dx - gpu_est_dx)**2 + (cv_est_dy - gpu_est_dy)**2),
        "ssim_ref_cv": ssim_ref_cv,
        "ssim_ref_gpu": ssim_ref_gpu,
        "ssim_cv_gpu": ssim_cv_gpu,
        "cv_flow_mean_mag": np.mean(flow_magnitude_cv),
        "gpu_flow_mean_mag": np.mean(flow_magnitude_gpu),
        "cv_flow_max_mag": np.max(flow_magnitude_cv),
        "gpu_flow_max_mag": np.max(flow_magnitude_gpu),
    }
    
    return result


# =============================================================================
# 5. Output Formatting
# =============================================================================

def print_results_table(results):
    """Print formatted ASCII table and summary statistics."""
    
    header = (
        f"| {'Demosaic':<8} | {'CV Time':>8} | {'GPU Time':>9} | {'Speedup':>7} | "
        f"{'CV Shift Est':<18} | {'GPU Shift Est':<18} | {'Shift Diff':>10} | "
        f"{'SSIM(ref,cv)':>12} | {'SSIM(ref,gpu)':>13} | {'SSIM(cv,gpu)':>12} |"
    )
    sep = "-" * len(header)
    
    print("\n" + sep)
    print(header)
    print(sep)
    
    for r in results:
        cv_dx, cv_dy = r["cv_shift_est"]
        gpu_dx, gpu_dy = r["gpu_shift_est"]
        
        cv_est_str = f"({cv_dx:+.4f}, {cv_dy:+.4f})"
        gpu_est_str = f"({gpu_dx:+.4f}, {gpu_dy:+.4f})"
        
        print(
            f"| {r['demosaic_algo']:<8} | {r['cv_time_ms']:>7.1f}ms | {r['gpu_time_ms']:>8.1f}ms | "
            f"{r['speedup']:>6.2f}x | {cv_est_str:<18} | {gpu_est_str:<18} | "
            f"{r['shift_diff']:>9.4f} | {r['ssim_ref_cv']:>11.4f} | {r['ssim_ref_gpu']:>12.4f} | "
            f"{r['ssim_cv_gpu']:>11.4f} |"
        )
    
    print(sep)
    
    # --- Summary Statistics ---
    print("\nSUMMARY")
    print("-" * 60)
    
    for r in results:
        print(f"\n{r['demosaic_algo']} Demosaicing:")
        print(f"  Image: {r['ref_image']} vs {r['comp_image']} ({r['image_size']})")
        print(f"  Load Time: {r['load_time_ms']:.1f} ms")
        print(f"  CV Time: {r['cv_time_ms']:.1f} ms")
        print(f"  GPU Time: {r['gpu_time_ms']:.1f} ms")
        print(f"  Speedup: {r['speedup']:.2f}x")
        print(f"  CV Shift Est: ({r['cv_shift_est'][0]:+.4f}, {r['cv_shift_est'][1]:+.4f})")
        print(f"  GPU Shift Est: ({r['gpu_shift_est'][0]:+.4f}, {r['gpu_shift_est'][1]:+.4f})")
        print(f"  Shift Difference: {r['shift_diff']:.4f} px")
        print(f"  SSIM(ref vs cv): {r['ssim_ref_cv']:.4f}")
        print(f"  SSIM(ref vs gpu): {r['ssim_ref_gpu']:.4f}")
        print(f"  SSIM(cv vs gpu): {r['ssim_cv_gpu']:.4f}")
        print(f"  CV Flow Magnitude (mean/max): {r['cv_flow_mean_mag']:.2f} / {r['cv_flow_max_mag']:.2f} px")
        print(f"  GPU Flow Magnitude (mean/max): {r['gpu_flow_mean_mag']:.2f} / {r['gpu_flow_max_mag']:.2f} px")
    
    # --- PASS/FAIL Evaluation ---
    print("\nPASS/FAIL EVALUATION")
    print("-" * 60)
    
    for r in results:
        print(f"\n{r['demosaic_algo']} Demosaicing:")
        
        # SSIM thresholds
        ssim_ref_gpu_pass = r['ssim_ref_gpu'] > 0.90
        ssim_cv_gpu_pass = r['ssim_cv_gpu'] > 0.95
        
        # Performance threshold (5x speedup target)
        speedup_pass = r['speedup'] >= 5.0
        
        # Shift consistency (GPU and CV should agree within 1px)
        shift_consistent = r['shift_diff'] < 1.0
        
        print(f"  SSIM(ref vs gpu) > 0.90:  {'PASS' if ssim_ref_gpu_pass else 'FAIL'} ({r['ssim_ref_gpu']:.4f})")
        print(f"  SSIM(cv vs gpu) > 0.95:   {'PASS' if ssim_cv_gpu_pass else 'FAIL'} ({r['ssim_cv_gpu']:.4f})")
        print(f"  Performance (5x target):  {'PASS' if speedup_pass else 'FAIL'} ({r['speedup']:.2f}x)")
        print(f"  Shift Consistency < 1px:  {'PASS' if shift_consistent else 'FAIL'} ({r['shift_diff']:.4f} px)")
    
    print("\n" + "=" * 60)


# =============================================================================
# 6. Main Entry Point
# =============================================================================

def main():
    print("=" * 120)
    print("GPU FARNEBACK V2 REAL DNG IMAGE TEST (Flow Convention Fixed)")
    print("=" * 120)
    print(f"Parameters: poly_n={POLY_N}, poly_sigma={POLY_SIGMA}, win_size={WIN_SIZE}, "
          f"levels={NUM_LEVELS}, iterations_per_level={NUM_ITERATIONS}")
    print(f"SSIM margin: {SSIM_MARGIN}px, center crop: {CROP_SIZE*2}x{CROP_SIZE*2}")
    print(f"Max image size: {MAX_IMAGE_SIZE}px")
    print(f"Flow convention: GPU flow = -(cmp - ref) * 0.5, negated to match OpenCV")
    print()
    
    # DNG image paths
    test_algorithm_dir = os.path.join(project_root, "test_algorithm")
    ref_path = os.path.join(test_algorithm_dir, "IMG_20260606_073156Z.dng")
    comp_path = os.path.join(test_algorithm_dir, "IMG_20260606_073157Z.dng")
    
    # Verify files exist
    if not os.path.exists(ref_path):
        print(f"ERROR: Reference image not found: {ref_path}")
        return
    if not os.path.exists(comp_path):
        print(f"ERROR: Comparison image not found: {comp_path}")
        return
    
    # Initialize GPU Engine
    print("Initializing GPU engine...")
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
    
    # Run tests with different demosaicing algorithms
    results = []
    
    # Test 1: Hamilton (AHD) demosaicing
    print("\n" + "="*80)
    print("TEST 1: Hamilton (AHD) Demosaicing")
    print("="*80)
    result_ahd = run_real_dng_test(
        engine, mod, pyramid_mod, ref_path, comp_path, 'AHD',
        poly_filters_per_level, gaussian_weights_gpu
    )
    results.append(result_ahd)
    
    # Test 2: Bilinear (LINEAR) demosaicing
    print("\n" + "="*80)
    print("TEST 2: Bilinear (LINEAR) Demosaicing")
    print("="*80)
    result_linear = run_real_dng_test(
        engine, mod, pyramid_mod, ref_path, comp_path, 'LINEAR',
        poly_filters_per_level, gaussian_weights_gpu
    )
    results.append(result_linear)
    
    # Print results table and summary
    print_results_table(results)
    
    # Cleanup constant GPU buffers
    for buf in [poly_filters_5_gpu, poly_filters_7_gpu, gaussian_weights_gpu]:
        try:
            buf.destroy()
        except Exception:
            pass
    
    print("\nTest completed. All GPU buffers cleaned up.")
    
    # Save results to file
    results_file = os.path.join(test_algorithm_dir, "farneback_real_dng_results_v2.txt")
    with open(results_file, 'w') as f:
        f.write("GPU Farneback V2 Real DNG Image Test Results (Flow Convention Fixed)\n")
        f.write("=" * 60 + "\n\n")
        for r in results:
            f.write(f"{r['demosaic_algo']} Demosaicing:\n")
            f.write(f"  Image: {r['ref_image']} vs {r['comp_image']} ({r['image_size']})\n")
            f.write(f"  Load Time: {r['load_time_ms']:.1f} ms\n")
            f.write(f"  CV Time: {r['cv_time_ms']:.1f} ms\n")
            f.write(f"  GPU Time: {r['gpu_time_ms']:.1f} ms\n")
            f.write(f"  Speedup: {r['speedup']:.2f}x\n")
            f.write(f"  SSIM(ref vs cv): {r['ssim_ref_cv']:.4f}\n")
            f.write(f"  SSIM(ref vs gpu): {r['ssim_ref_gpu']:.4f}\n")
            f.write(f"  SSIM(cv vs gpu): {r['ssim_cv_gpu']:.4f}\n")
            f.write(f"  Shift Difference: {r['shift_diff']:.4f} px\n\n")
    
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()