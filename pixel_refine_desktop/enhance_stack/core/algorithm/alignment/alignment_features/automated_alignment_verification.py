import taichi as ti
import numpy as np
import cv2
import os
import sys
import time

# Setup Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from taichi_library.taichi_aot.engine import AOTEngine
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import taichi_bridge
import taichi_library.taichi_aot as taichi_aot

def calculate_ssim(img1, img2):
    """Menghitung SSIM (Structural Similarity Index) secara manual untuk kontrol yang ketat"""
    C1 = (0.01 * 255)**2
    C2 = (0.03 * 255)**2

    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    kernel = np.ones((11, 11), np.float64) / 121.0

    mu1 = cv2.filter2D(img1, -1, kernel)
    mu2 = cv2.filter2D(img2, -1, kernel)

    mu1_sq = mu1**2
    mu2_sq = mu2**2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.filter2D(img1**2, -1, kernel) - mu1_sq
    sigma2_sq = cv2.filter2D(img2**2, -1, kernel) - mu2_sq
    sigma12 = cv2.filter2D(img1 * img2, -1, kernel) - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    return np.mean(ssim_map)

def calculate_mse(img1, img2):
    """Menghitung Mean Squared Error (Semakin kecil semakin baik)"""
    return np.mean((img1.astype(np.float32) - img2.astype(np.float32))**2)

def run_strict_verification():
    print("="*70)
    print("      STRICT ALIGNMENT VERIFICATION SYSTEM (SSIM + MSE)")
    print("="*70)
    
    engine = AOTEngine()
    tcm_path = os.path.join(project_root, "pixel_refine_desktop", "ui", "data", "aot_assets", "compute_flow_vulkan.tcm")
    mod = engine.load(tcm_path)
    
    img_path = os.path.join(project_root, "test_algorithm", "IMG_20250401_182043_B002.dng")
    if not os.path.exists(img_path):
        print("Warning: Test DNG not found, generating synthetic pattern.")
        img_ref = np.random.rand(1024, 1024, 3).astype(np.float32) * 255.0
        img_ref = img_ref.astype(np.uint8)
    else:
        import rawpy
        print(f"Loading and demosaicing: {img_path}")
        with rawpy.imread(img_path) as raw:
            rgb = raw.postprocess(use_camera_wb=True, half_size=True)
            img_ref = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            h_ref, w_ref = img_ref.shape[:2]
            img_ref = img_ref[(h_ref//2 - 512):(h_ref//2 + 512), (w_ref//2 - 512):(w_ref//2 + 512)].copy()
    
    h, w = img_ref.shape[:2]
    
    shifts = [0, 10, 20, 30, 40, 50]
    results = []
    
    for shift_val in shifts:
        dx_t, dy_t = shift_val, shift_val // 2
        # Use Identity for 0px
        if shift_val == 0:
            img_comp = img_ref.copy()
        else:
            M = np.float32([[1, 0, dx_t], [0, 1, dy_t]])
            img_comp = cv2.warpAffine(img_ref, M, (w, h))
        
        # AOT Alignment
        ref_pyramid = taichi_bridge.prepare_reference_for_alignment(img_ref.astype(np.float32)/255.0, False, 1.0, 1024, 1024)
        comp_pyramid = taichi_bridge.prepare_comparison_for_alignment(img_comp, np.uint8, False, 1.0, 1024, 1024)
        
        f0 = engine.allocate((1024, 1024, 2), dtype=np.float32)
        f1 = engine.allocate((512, 512, 2), dtype=np.float32)
        f2 = engine.allocate((256, 256, 2), dtype=np.float32)
        
        mod.run('align_end_to_end_3layer', 
                ref_l0=ref_pyramid[0], ref_l1=ref_pyramid[1], ref_l2=ref_pyramid[2],
                comp_l0=comp_pyramid[0], comp_l1=comp_pyramid[1], comp_l2=comp_pyramid[2],
                flow_l0=f0, flow_l1=f1, flow_l2=f2,
                tile_h=16, tile_w=16, search_radius=8, scale=2.0, search_dist=2, downscale=2)
        engine.sync()
        
        # Upscale & Warp
        flow_work_np = f0.to_numpy()
        dx_full = taichi_aot.resize(flow_work_np[:,:,0], (w, h), interpolation=taichi_aot.INTER_LINEAR)
        dy_full = taichi_aot.resize(flow_work_np[:,:,1], (w, h), interpolation=taichi_aot.INTER_LINEAR)
        dx_full *= (float(w) / 1024.0)
        dy_full *= (float(h) / 1024.0)
        
        # Debug Flow
        mean_dx, mean_dy = np.mean(dx_full), np.mean(dy_full)
        print(f"DEBUG Shift {dx_t}px: Expected({dx_t}, {dy_t}), Detected({mean_dx:.2f}, {mean_dy:.2f})")
        
        # Step 4: Final Warp
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        # Try both directions to find the right one
        map_x_pos, map_y_pos = x + dx_full, y + dy_full
        warped_res = cv2.remap(img_comp, map_x_pos, map_y_pos, cv2.INTER_LINEAR)
        
        # Strict Metric Calculation (Grayscale SSIM for pure flow accuracy)
        margin = 200 
        crop_ref = cv2.cvtColor(img_ref[margin:-margin, margin:-margin], cv2.COLOR_BGR2GRAY)
        crop_res = cv2.cvtColor(warped_res[margin:-margin, margin:-margin], cv2.COLOR_BGR2GRAY)
        
        ssim_score = calculate_ssim(crop_ref, crop_res) * 100.0
        mse_score = calculate_mse(crop_ref, crop_res)
        
        status = "[PASSED]" if ssim_score >= 90.0 else "[FAILED]"
        
        results.append({
            "shift": f"{dx_t}px",
            "ssim": f"{ssim_score:.4f}%",
            "mse": f"{mse_score:.2f}",
            "status": status
        })
        print(f"Shift {dx_t}px: SSIM={ssim_score:.2f}%, MSE={mse_score:.2f} -> {status}")

    print("\n" + "="*70)
    print(f"{'SHIFT':<10} | {'SSIM (%)':<15} | {'MSE':<10} | {'STATUS':<15}")
    print("-" * 70)
    for res in results:
        print(f"{res['shift']:<10} | {res['ssim']:<15} | {res['mse']:<10} | {res['status']:<15}")
    print("="*70)

if __name__ == "__main__":
    run_strict_verification()
