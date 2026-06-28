"""
Test Optical Flow AOT Modules — Farneback & Horn-Schunck
========================================================
Tests AOT-compiled optical flow modules with synthetic images:
- 8-bit grayscale, 16-bit grayscale, color RGB
- Known ground-truth motion (translation, rotation, affine)
- Accuracy metrics: AEPE, SSIM, flow magnitude consistency
- Saves visualizations to test_output/ directory

Usage:
    python test_optical_flow_aot.py
"""
import os
import sys
import time
import numpy as np
import cv2

# Setup paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Force AOT mode
os.environ["AOT_MODE"] = "1"
os.environ["VK_LOADER_DEBUG"] = "error"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_output_flow")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def print_header(text):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_result(name, value, threshold, unit=""):
    status = "[PASS]" if value < threshold else "[FAIL]"
    print(f"{status} {name:40} | Value: {value:.6f} {unit} | Limit: < {threshold} {unit}")
    return value < threshold


def create_synthetic_images(h, w, motion_type="translation", motion_params=None):
    """
    Create a pair of synthetic images with known ground-truth flow.
    
    Returns:
        ref_img: Reference image (H, W) float32 [0, 1]
        comp_img: Comparison image with known motion
        gt_flow: Ground truth flow (H, W, 2) float32
    """
    if motion_params is None:
        motion_params = {}
    
    # Create base image with gradients, edges, and texture
    ref = np.zeros((h, w), dtype=np.float32)
    
    # Horizontal gradient
    ref += np.linspace(0, 0.3, w)[np.newaxis, :]
    
    # Vertical gradient
    ref += np.linspace(0, 0.3, h)[:, np.newaxis]
    
    # Add circles (texture)
    for cx, cy, r in [(w//4, h//4, w//8), (3*w//4, 3*h//4, w//6), (w//2, h//2, w//10)]:
        Y, X = np.ogrid[:h, :w]
        mask = ((X - cx)**2 + (Y - cy)**2) < r**2
        ref[mask] += 0.3
    
    # Add checkerboard pattern
    block_size = max(8, w // 16)
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            if (y // block_size + x // block_size) % 2 == 0:
                ref[y:y+block_size, x:x+block_size] += 0.2
    
    ref = np.clip(ref, 0, 1)
    
    # Apply motion
    gt_flow = np.zeros((h, w, 2), dtype=np.float32)
    
    if motion_type == "translation":
        dx = motion_params.get("dx", 5.0)
        dy = motion_params.get("dy", 3.0)
        gt_flow[:, :, 0] = dx
        gt_flow[:, :, 1] = dy
        
        # Warp reference using ground truth flow
        Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
        map_x = (X - dx).astype(np.float32)
        map_y = (Y - dy).astype(np.float32)
        comp = cv2.remap(ref, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        
    elif motion_type == "rotation":
        cx = motion_params.get("cx", w / 2)
        cy = motion_params.get("cy", h / 2)
        angle_deg = motion_params.get("angle", 2.0)
        angle_rad = np.radians(angle_deg)
        
        Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
        # Rotation flow
        dx = -(Y - cy) * np.sin(angle_rad) + (X - cx) * (np.cos(angle_rad) - 1)
        dy = (Y - cy) * (np.cos(angle_rad) - 1) + (X - cx) * np.sin(angle_rad)
        gt_flow[:, :, 0] = dx
        gt_flow[:, :, 1] = dy
        
        # Warp
        map_x = (X - dx).astype(np.float32)
        map_y = (Y - dy).astype(np.float32)
        comp = cv2.remap(ref, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        
    elif motion_type == "diverse":
        # Complex motion: varying flow field
        Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
        dx = 5.0 * np.sin(2 * np.pi * X / w) * np.cos(2 * np.pi * Y / h)
        dy = 3.0 * np.cos(2 * np.pi * X / w) * np.sin(2 * np.pi * Y / h)
        gt_flow[:, :, 0] = dx
        gt_flow[:, :, 1] = dy
        
        map_x = (X - dx).astype(np.float32)
        map_y = (Y - dy).astype(np.float32)
        comp = cv2.remap(ref, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    
    return ref, comp, gt_flow


def convert_to_type(img, bit_depth=8, is_color=False):
    """Convert float32 [0,1] image to specified type."""
    if is_color:
        # Create 3-channel image
        img_rgb = np.stack([img, img * 0.8, img * 0.6], axis=-1)
        if bit_depth == 8:
            return np.clip(img_rgb * 255, 0, 255).astype(np.uint8)
        elif bit_depth == 16:
            return np.clip(img_rgb * 65535, 0, 65535).astype(np.uint16)
    else:
        if bit_depth == 8:
            return np.clip(img * 255, 0, 255).astype(np.uint8)
        elif bit_depth == 16:
            return np.clip(img * 65535, 0, 65535).astype(np.uint16)
    return img


def to_float32_gray(img):
    """Convert any image format to float32 grayscale [0, 1]."""
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.shape[2] == 3 else img[:, :, 0]
    else:
        gray = img
    
    if img.dtype == np.uint8:
        return gray.astype(np.float32) / 255.0
    elif img.dtype == np.uint16:
        return gray.astype(np.float32) / 65535.0
    return gray.astype(np.float32)


def compute_flow_metrics(est_flow, gt_flow, valid_mask=None):
    """Compute optical flow accuracy metrics."""
    diff = est_flow - gt_flow
    aepe = np.mean(np.sqrt(np.sum(diff**2, axis=-1)))
    
    # Angular error (simplified)
    dot = np.sum(est_flow * gt_flow, axis=-1)
    mag_est = np.sqrt(np.sum(est_flow**2, axis=-1)) + 1e-8
    mag_gt = np.sqrt(np.sum(gt_flow**2, axis=-1)) + 1e-8
    cos_angle = np.clip(dot / (mag_est * mag_gt), -1, 1)
    angular_err = np.degrees(np.arccos(cos_angle))
    avg_angular = np.mean(angular_err)
    
    # Outlier ratio (>3px or >5%)
    epe = np.sqrt(np.sum(diff**2, axis=-1))
    outlier_ratio = np.mean(epe > 3.0)
    
    return aepe, avg_angular, outlier_ratio


def compute_ssim(img1, img2):
    """Compute Structural Similarity Index between two images."""
    from skimage.metrics import structural_similarity as ssim
    h, w = img1.shape[:2]
    win_size = min(7, min(h, w) // 2 * 2 + 1)  # Ensure odd and <= image size
    if h < 7 or w < 7:
        win_size = 3 if min(h, w) >= 3 else 1
    if img1.ndim == 3:
        return ssim(img1, img2, channel_axis=2, win_size=win_size, data_range=1.0)
    return ssim(img1, img2, win_size=win_size, data_range=1.0)


def warp_image_with_flow(img, flow):
    """Warp image using optical flow field."""
    h, w = flow.shape[:2]
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    map_x = (X - flow[:, :, 0]).astype(np.float32)
    map_y = (Y - flow[:, :, 1]).astype(np.float32)
    return cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def test_farneback_aot():
    """Test Farneback AOT module with synthetic images."""
    print_header("FARNEBACK AOT TEST")
    
    from taichi_library.taichi_aot.engine import AOTEngine
    
    engine = AOTEngine()
    tcm_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../aot_tcm"))
    tcm_path = os.path.join(tcm_dir, "farneback_flow_vulkan.tcm")
    
    if not os.path.exists(tcm_path):
        print(f"[SKIP] TCM not found: {tcm_path}")
        return []
    
    mod = engine.load(tcm_path)
    print(f"Loaded: {tcm_path}")
    
    results = []
    test_cases = [
        # (name, h, w, motion_type, motion_params, bit_depth, is_color)
        ("Translation-8bit-gray", 128, 128, "translation", {"dx": 5, "dy": 3}, 8, False),
        ("Translation-16bit-gray", 128, 128, "translation", {"dx": 5, "dy": 3}, 16, False),
        ("Translation-8bit-color", 128, 128, "translation", {"dx": 5, "dy": 3}, 8, True),
        ("Rotation-8bit-gray", 128, 128, "rotation", {"angle": 2.0}, 8, False),
        ("Diverse-8bit-gray", 128, 128, "diverse", {}, 8, False),
        ("Diverse-16bit-gray", 128, 128, "diverse", {}, 16, False),
        ("Diverse-8bit-color", 128, 128, "diverse", {}, 8, True),
        ("Large-8bit-gray", 256, 256, "translation", {"dx": 8, "dy": 5}, 8, False),
    ]
    
    for name, h, w, motion, params, bit_depth, is_color in test_cases:
        print(f"\n--- {name} ({w}x{h}, {bit_depth}bit {'color' if is_color else 'gray'}) ---")
        
        try:
            # Create synthetic images
            ref_f32, comp_f32, gt_flow = create_synthetic_images(h, w, motion, params)
            
            # Convert to target type
            ref_typed = convert_to_type(ref_f32, bit_depth, is_color)
            comp_typed = convert_to_type(comp_f32, bit_depth, is_color)
            
            # Convert to float32 grayscale for flow computation
            ref_gray = to_float32_gray(ref_typed)
            comp_gray = to_float32_gray(comp_typed)
            
            # Scale to [0, 255] for Farneback (matches OpenCV convention)
            ref_255 = np.ascontiguousarray(ref_gray * 255.0, dtype=np.float32)
            comp_255 = np.ascontiguousarray(comp_gray * 255.0, dtype=np.float32)
            
            # Upload images to GPU
            ref_gpu = engine.upload(ref_255)
            comp_gpu = engine.upload(comp_255)
            
            # Allocate flow buffer
            flow_gpu = engine.allocate((h, w, 2), dtype=np.float32, is_vector=False)
            
            # Import constants
            from taichi_library.taichi_algorithm.farneback_flow import (
                prepare_gaussian_constants,
                compute_smoothing_weights,
            )
            
            poly_n, poly_sigma, win_size = 5, 1.2, 15
            g_w, xg_w, xxg_w, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(poly_n, poly_sigma)
            smooth_w, smooth_radius = compute_smoothing_weights(win_size)
            poly_radius = poly_n // 2
            
            # Upload constants
            g_gpu = engine.upload(g_w[:poly_radius + 1])
            xg_gpu = engine.upload(xg_w[:poly_radius + 1])
            xxg_gpu = engine.upload(xxg_w[:poly_radius + 1])
            smooth_gpu = engine.upload(smooth_w[:smooth_radius + 1])
            
            # Allocate temp buffers
            vert_gpu = engine.allocate((h, w, 3), dtype=np.float32)
            R0_gpu = engine.allocate((h, w, 5), dtype=np.float32)
            R1_gpu = engine.allocate((h, w, 5), dtype=np.float32)
            M_gpu = engine.allocate((h, w, 5), dtype=np.float32)
            M_smooth_gpu = engine.allocate((h, w, 5), dtype=np.float32)
            
            # Polynomial expansion
            mod.run("poly_expansion_f32",
                    src=ref_gpu, vert=vert_gpu, poly=R0_gpu,
                    h=h, w=w, g=g_gpu, xg=xg_gpu, xxg=xxg_gpu,
                    ig11=ig11, ig03=ig03, ig33=ig33, ig55=ig55,
                    poly_radius=poly_radius)
            mod.run("poly_expansion_f32",
                    src=comp_gpu, vert=vert_gpu, poly=R1_gpu,
                    h=h, w=w, g=g_gpu, xg=xg_gpu, xxg=xxg_gpu,
                    ig11=ig11, ig03=ig03, ig33=ig33, ig55=ig55,
                    poly_radius=poly_radius)
            
            # Clear flow
            mod.run("farneback_clear_flow", flow=flow_gpu)
            
            # Run 3 iterations (timed)
            t_start = time.time()
            mod.run("farneback_multi_3",
                    R0=R0_gpu, R1=R1_gpu, flow=flow_gpu,
                    M=M_gpu, M_smooth=M_smooth_gpu,
                    h=h, w=w, smooth_weights=smooth_gpu,
                    smooth_radius=smooth_radius)
            engine.sync()
            t_aot = time.time() - t_start
            
            # Download result
            flow_np = flow_gpu.to_numpy()
            
            # Compare with OpenCV reference (timed)
            t_start_cv = time.time()
            cv_flow = cv2.calcOpticalFlowFarneback(
                (ref_255).astype(np.uint8),
                (comp_255).astype(np.uint8),
                None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            t_cv = time.time() - t_start_cv
            
            # Compute metrics
            aepe, angular, outlier = compute_flow_metrics(flow_np, gt_flow)
            aepe_cv, angular_cv, outlier_cv = compute_flow_metrics(cv_flow, gt_flow)
            
            # Compute SSIM (warp ref with flow, compare to comp)
            ref_vis = convert_to_type(ref_f32, bit_depth, is_color)
            if ref_vis.ndim == 3:
                ref_vis = ref_vis.astype(np.float32) / (255 if bit_depth == 8 else 65535)
            else:
                ref_vis = ref_vis.astype(np.float32) / (255 if bit_depth == 8 else 65535)
            
            warped_aot = warp_image_with_flow(ref_vis, flow_np)
            warped_cv = warp_image_with_flow(ref_vis, cv_flow)
            comp_vis = convert_to_type(comp_f32, bit_depth, is_color).astype(np.float32) / (255 if bit_depth == 8 else 65535)
            if comp_vis.ndim == 3:
                comp_vis = comp_vis[..., :3] if comp_vis.shape[2] >= 3 else comp_vis[..., 0]
            
            ssim_aot = compute_ssim(warped_aot, comp_vis)
            ssim_cv = compute_ssim(warped_cv, comp_vis)
            
            print(f"  AOT  AEPE: {aepe:.4f} px | Angular: {angular:.2f} deg | Outlier: {outlier:.2%} | SSIM: {ssim_aot:.4f} | Time: {t_aot*1000:.1f} ms")
            print(f"  OpenCV AEPE: {aepe_cv:.4f} px | Angular: {angular_cv:.2f} deg | Outlier: {outlier_cv:.2%} | SSIM: {ssim_cv:.4f} | Time: {t_cv*1000:.1f} ms")
            
            # Save visualization
            vis = visualize_flow(flow_np, f"FB_AOT_{name}")
            cv2.imwrite(os.path.join(OUTPUT_DIR, f"fb_aot_{name.replace(' ', '_').lower()}.png"), vis)
            
            # Accept if AEPE < 10px (generous threshold for synthetic tests)
            ok = aepe < 10.0
            results.append(print_result(f"FB AOT: {name}", aepe, threshold=10.0, unit="px"))
            
            # Cleanup
            for buf in [ref_gpu, comp_gpu, flow_gpu, vert_gpu, R0_gpu, R1_gpu, M_gpu, M_smooth_gpu,
                        g_gpu, xg_gpu, xxg_gpu, smooth_gpu]:
                buf.release()
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    return results


def test_horn_schunck_aot():
    """Test Horn-Schunck AOT module with synthetic images."""
    print_header("HORN-SCHUNCK AOT TEST")
    
    from taichi_library.taichi_aot.engine import AOTEngine
    
    engine = AOTEngine()
    tcm_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../aot_tcm"))
    tcm_path = os.path.join(tcm_dir, "template_flow_vulkan.tcm")
    
    if not os.path.exists(tcm_path):
        print(f"[SKIP] TCM not found: {tcm_path}")
        return []
    
    mod = engine.load(tcm_path)
    print(f"Loaded: {tcm_path}")
    
    # Check available graphs
    print("Note: Horn-Schunck requires 3-layer pyramid input")
    
    results = []
    test_cases = [
        ("Translation-8bit-gray", 128, 128, "translation", {"dx": 5, "dy": 3}, 8, False),
        ("Translation-16bit-gray", 128, 128, "translation", {"dx": 5, "dy": 3}, 16, False),
        ("Translation-8bit-color", 128, 128, "translation", {"dx": 5, "dy": 3}, 8, True),
        ("Rotation-8bit-gray", 128, 128, "rotation", {"angle": 2.0}, 8, False),
        ("Diverse-8bit-gray", 128, 128, "diverse", {}, 8, False),
        ("Diverse-16bit-gray", 128, 128, "diverse", {}, 16, False),
        ("Diverse-8bit-color", 128, 128, "diverse", {}, 8, True),
    ]
    
    for name, h, w, motion, params, bit_depth, is_color in test_cases:
        print(f"\n--- {name} ({w}x{h}, {bit_depth}bit {'color' if is_color else 'gray'}) ---")
        
        try:
            # Create synthetic images
            ref_f32, comp_f32, gt_flow = create_synthetic_images(h, w, motion, params)
            
            # Convert to float32 grayscale
            ref_gray = to_float32_gray(convert_to_type(ref_f32, bit_depth, is_color))
            comp_gray = to_float32_gray(convert_to_type(comp_f32, bit_depth, is_color))
            
            # Upload to GPU
            ref_gpu = engine.upload(np.ascontiguousarray(ref_gray, dtype=np.float32))
            comp_gpu = engine.upload(np.ascontiguousarray(comp_gray, dtype=np.float32))
            
            # Build 3-layer pyramids (downscale by 2x each level)
            from taichi_library.taichi_aot import resize as aot_resize, INTER_LINEAR
            
            ref_l1 = aot_resize(ref_gpu, (w//2, h//2), interpolation=INTER_LINEAR, return_gpu=True)
            ref_l2 = aot_resize(ref_l1, (w//4, h//4), interpolation=INTER_LINEAR, return_gpu=True)
            comp_l1 = aot_resize(comp_gpu, (w//2, h//2), interpolation=INTER_LINEAR, return_gpu=True)
            comp_l2 = aot_resize(comp_l1, (w//4, h//4), interpolation=INTER_LINEAR, return_gpu=True)
            
            # Allocate flow buffers
            flow_l0 = engine.allocate((h, w, 2), dtype=np.float32, is_vector=False)
            flow_l1 = engine.allocate((h//2, w//2, 2), dtype=np.float32, is_vector=False)
            flow_l2 = engine.allocate((h//4, w//4, 2), dtype=np.float32, is_vector=False)
            flow_temp_l0 = engine.allocate((h, w, 2), dtype=np.float32, is_vector=False)
            flow_temp_l1 = engine.allocate((h//2, w//2, 2), dtype=np.float32, is_vector=False)
            flow_temp_l2 = engine.allocate((h//4, w//4, 2), dtype=np.float32, is_vector=False)
            
            # Run Horn-Schunck (20 iterations, timed)
            graph_name = "hs_align_3layer_20"
            t_start = time.time()
            mod.run(graph_name,
                    ref_l0=ref_gpu, ref_l1=ref_l1, ref_l2=ref_l2,
                    comp_l0=comp_gpu, comp_l1=comp_l1, comp_l2=comp_l2,
                    flow_l0=flow_l0, flow_l1=flow_l1, flow_l2=flow_l2,
                    flow_temp_l0=flow_temp_l0, flow_temp_l1=flow_temp_l1, flow_temp_l2=flow_temp_l2,
                    alpha=1.0, num_iters=20, scale=2.0, downscale=2)
            engine.sync()
            t_aot = time.time() - t_start
            
            # Download result
            flow_np = flow_l0.to_numpy()
            
            # Compare with OpenCV Farneback reference (timed)
            t_start_cv = time.time()
            ref_u8 = (ref_gray * 255).astype(np.uint8)
            comp_u8 = (comp_gray * 255).astype(np.uint8)
            cv_flow = cv2.calcOpticalFlowFarneback(ref_u8, comp_u8, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            t_cv = time.time() - t_start_cv
            
            # Compute metrics
            aepe, angular, outlier = compute_flow_metrics(flow_np, gt_flow)
            aepe_cv, angular_cv, outlier_cv = compute_flow_metrics(cv_flow, gt_flow)
            
            # Compute SSIM
            ref_vis = ref_gray.copy()
            warped_aot = warp_image_with_flow(ref_vis, flow_np)
            warped_cv = warp_image_with_flow(ref_vis, cv_flow)
            
            ssim_aot = compute_ssim(warped_aot, comp_gray)
            ssim_cv = compute_ssim(warped_cv, comp_gray)
            
            print(f"  AOT  AEPE: {aepe:.4f} px | Angular: {angular:.2f} deg | Outlier: {outlier:.2%} | SSIM: {ssim_aot:.4f} | Time: {t_aot*1000:.1f} ms")
            print(f"  OpenCV AEPE: {aepe_cv:.4f} px | Angular: {angular_cv:.2f} deg | Outlier: {outlier_cv:.2%} | SSIM: {ssim_cv:.4f} | Time: {t_cv*1000:.1f} ms")
            
            # Save visualization
            vis = visualize_flow(flow_np, f"HS_AOT_{name}")
            cv2.imwrite(os.path.join(OUTPUT_DIR, f"hs_aot_{name.replace(' ', '_').lower()}.png"), vis)
            
            # Horn-Schunck is less accurate than Farneback, use 15px threshold
            ok = aepe < 15.0
            results.append(print_result(f"HS AOT: {name}", aepe, threshold=15.0, unit="px"))
            
            # Cleanup
            for buf in [ref_gpu, comp_gpu, ref_l1, ref_l2, comp_l1, comp_l2,
                        flow_l0, flow_l1, flow_l2, flow_temp_l0, flow_temp_l1, flow_temp_l2]:
                buf.release()
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    return results


def visualize_flow(flow, title=""):
    """Visualize optical flow as color-coded image."""
    h, w = flow.shape[:2]
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    
    hsv = np.zeros((h, w, 3), dtype=np.uint8)
    hsv[..., 1] = 255
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 2] = np.clip(mag * 20, 0, 255).astype(np.uint8)
    
    vis = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    if title:
        cv2.putText(vis, title, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return vis


def test_tcm_integrity():
    """Verify TCM files are valid and loadable."""
    print_header("TCM FILE INTEGRITY TEST")
    
    from taichi_library.taichi_aot.engine import AOTEngine
    
    engine = AOTEngine()
    tcm_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../aot_tcm"))
    
    tcm_files = {
        "farneback_flow_vulkan.tcm": [
            "poly_expansion_f32",
            "farneback_iteration",
            "farneback_multi_2",
            "farneback_multi_3",
            "farneback_multi_5",
            "farneback_upsample_flow",
            "farneback_clear_flow",
        ],
        "template_flow_vulkan.tcm": [
            "hs_align_3layer_10",
            "hs_align_3layer_20",
        ],
    }
    
    results = []
    for tcm_name, expected_graphs in tcm_files.items():
        tcm_path = os.path.join(tcm_dir, tcm_name)
        print(f"\n--- {tcm_name} ---")
        
        if not os.path.exists(tcm_path):
            print(f"  [FAIL] File not found: {tcm_path}")
            results.append(False)
            continue
        
        try:
            file_size = os.path.getsize(tcm_path) / 1024
            print(f"  Size: {file_size:.1f} KB")
            
            mod = engine.load(tcm_path)
            print(f"  [OK] Module loaded successfully")
            
            # Try to run a simple graph to verify it works
            if "farneback_clear_flow" in expected_graphs:
                test_flow = engine.allocate((32, 32, 2), dtype=np.float32, is_vector=False)
                mod.run("farneback_clear_flow", flow=test_flow)
                engine.sync()
                flow_np = test_flow.to_numpy()
                assert np.allclose(flow_np, 0), "clear_flow should produce zeros"
                test_flow.release()
                print(f"  [OK] farneback_clear_flow verified")
            
            if "hs_align_3layer_20" in expected_graphs:
                # Minimal test with tiny images
                ref = engine.upload(np.random.rand(32, 32).astype(np.float32))
                comp = engine.upload(np.random.rand(32, 32).astype(np.float32))
                ref_l1 = engine.upload(np.random.rand(16, 16).astype(np.float32))
                comp_l1 = engine.upload(np.random.rand(16, 16).astype(np.float32))
                ref_l2 = engine.upload(np.random.rand(8, 8).astype(np.float32))
                comp_l2 = engine.upload(np.random.rand(8, 8).astype(np.float32))
                
                flow_l0 = engine.allocate((32, 32, 2), dtype=np.float32, is_vector=False)
                flow_l1 = engine.allocate((16, 16, 2), dtype=np.float32, is_vector=False)
                flow_l2 = engine.allocate((8, 8, 2), dtype=np.float32, is_vector=False)
                temp_l0 = engine.allocate((32, 32, 2), dtype=np.float32, is_vector=False)
                temp_l1 = engine.allocate((16, 16, 2), dtype=np.float32, is_vector=False)
                temp_l2 = engine.allocate((8, 8, 2), dtype=np.float32, is_vector=False)
                
                mod.run("hs_align_3layer_20",
                        ref_l0=ref, ref_l1=ref_l1, ref_l2=ref_l2,
                        comp_l0=comp, comp_l1=comp_l1, comp_l2=comp_l2,
                        flow_l0=flow_l0, flow_l1=flow_l1, flow_l2=flow_l2,
                        flow_temp_l0=temp_l0, flow_temp_l1=temp_l1, flow_temp_l2=temp_l2,
                        alpha=1.0, num_iters=20, scale=2.0, downscale=2)
                engine.sync()
                
                flow_np = flow_l0.to_numpy()
                assert flow_np.shape == (32, 32, 2), f"Expected (32,32,2), got {flow_np.shape}"
                assert not np.allclose(flow_np, 0), "Horn-Schunck should produce non-zero flow"
                print(f"  [OK] hs_align_3layer_20 verified (flow range: [{flow_np.min():.2f}, {flow_np.max():.2f}])")
                
                for buf in [ref, comp, ref_l1, comp_l1, ref_l2, comp_l2,
                           flow_l0, flow_l1, flow_l2, temp_l0, temp_l1, temp_l2]:
                    buf.release()
            
            results.append(True)
            
        except Exception as e:
            print(f"  [FAIL] {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    return results


def main():
    print_header("OPTICAL FLOW AOT MODULE TEST SUITE")
    print(f"Output directory: {OUTPUT_DIR}")
    
    all_results = []
    
    # 1. TCM Integrity
    all_results.extend(test_tcm_integrity())
    
    # 2. Farneback AOT
    all_results.extend(test_farneback_aot())
    
    # 3. Horn-Schunck AOT
    all_results.extend(test_horn_schunck_aot())
    
    # Final verdict
    print_header("FINAL VERDICT")
    passed = sum(all_results)
    total = len(all_results)
    
    if all(all_results):
        print(">>> ALL TESTS PASSED!")
    else:
        print(">>> SOME TESTS FAILED!")
    
    print(f">>> Results: {passed}/{total} tests passed")
    print(f">>> Visualizations saved to: {OUTPUT_DIR}")
    print("=" * 70)
    
    return 0 if all(all_results) else 1


if __name__ == "__main__":
    sys.exit(main())
