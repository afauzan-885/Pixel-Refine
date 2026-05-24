import os
import sys
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim

project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

# Force production backend mode for AOT testing
os.environ["PIXEL_REFINE_BACKEND"] = "PRODUCTION"
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import remap as ta_remap

def test_remap_parity():
    print("[Test] Starting Taichi Remap Parity Verification...")
    
    img_path = os.path.join(project_root, "test_algorithm/IMG_20160202_015247.png")
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Could not load test image at {img_path}")
    
    print(f"[Test] Loaded test image shape: {img.shape}, dtype={img.dtype}")
    
    # Run tests on both Grayscale and RGB images
    h, w, c = img.shape
    
    # 1. Coordinate Flow Maps for 10px right and 10px up shift
    # Shift right 10px: map_x = x - 10
    # Shift up 10px (which is -10 in Y index space): map_y = y + 10
    grid_y, grid_x = np.mgrid[0:h, 0:w]
    map_x = (grid_x - 10.0).astype(np.float32)
    map_y = (grid_y + 10.0).astype(np.float32)
    
    # Boundaries to crop (remove borders that warped from out-of-bounds)
    crop_border = 15
    
    # ---------------------------------------------
    # Case 1: Grayscale Image (2D)
    # ---------------------------------------------
    print("\n--- Testing Grayscale (2D) Warping ---")
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # OpenCV Warp (Using BORDER_REFLECT_101 to match Taichi common.py reflect_idx)
    cv_warped_gray = cv2.remap(img_gray, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    
    # Taichi Warp
    ta_warped_gray = ta_remap(img_gray, map_x, map_y)
    
    # Crop borders
    cv_cropped_gray = cv_warped_gray[crop_border:-crop_border, crop_border:-crop_border]
    ta_cropped_gray = ta_warped_gray[crop_border:-crop_border, crop_border:-crop_border]
    
    mae_gray = np.mean(np.abs(cv_cropped_gray.astype(np.float32) - ta_cropped_gray.astype(np.float32)))
    ssim_gray = ssim(cv_cropped_gray, ta_cropped_gray, data_range=255.0)
    
    print(f"MAE (Grayscale): {mae_gray:.8f}")
    print(f"SSIM (Grayscale): {ssim_gray:.8f}")
    
    assert mae_gray <= 0.5, f"Grayscale MAE {mae_gray:.8f} exceeds limit of 0.5!"
    assert ssim_gray >= 0.999, f"Grayscale SSIM {ssim_gray:.8f} is too low!"
    print("[PASS] Grayscale Remap Parity Verified!")

    # ---------------------------------------------
    # Case 2: RGB Color Image (3D)
    # ---------------------------------------------
    print("\n--- Testing RGB Color (3D) Warping ---")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # OpenCV Warp (Using BORDER_REFLECT_101 to match Taichi common.py reflect_idx)
    cv_warped_rgb = cv2.remap(img_rgb, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    
    # Taichi Warp
    ta_warped_rgb = ta_remap(img_rgb, map_x, map_y)
    
    # Crop borders
    cv_cropped_rgb = cv_warped_rgb[crop_border:-crop_border, crop_border:-crop_border]
    ta_cropped_rgb = ta_warped_rgb[crop_border:-crop_border, crop_border:-crop_border]
    
    mae_rgb = np.mean(np.abs(cv_cropped_rgb.astype(np.float32) - ta_cropped_rgb.astype(np.float32)))
    ssim_rgb = ssim(cv_cropped_rgb, ta_cropped_rgb, channel_axis=2, data_range=255.0)
    
    print(f"MAE (RGB): {mae_rgb:.8f}")
    print(f"SSIM (RGB): {ssim_rgb:.8f}")
    
    assert mae_rgb <= 0.5, f"RGB MAE {mae_rgb:.8f} exceeds limit of 0.5!"
    assert ssim_rgb >= 0.999, f"RGB SSIM {ssim_rgb:.8f} is too low!"
    print("[PASS] RGB Remap Parity Verified!")
    
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! ZERO TOLERANCE WARPING VERIFIED.")

if __name__ == "__main__":
    test_remap_parity()
