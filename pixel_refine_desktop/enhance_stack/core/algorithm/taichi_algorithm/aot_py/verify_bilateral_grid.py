import numpy as np
import cv2
import os
import sys

# Path setup
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def verify_bilateral_grid():
    print("="*60)
    print(" TAICHI AOT BILATERAL GRID VERIFICATION ")
    print("="*60)
    
    # Load test image
    img_path = os.path.join(project_root, "test_data/ref_00.png")
    if not os.path.exists(img_path):
        # Create dummy if not exists
        img = (np.random.rand(512, 512, 3) * 255).astype(np.uint8)
    else:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (512, 512))

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Grayscale Verification (Medium)
    print("Running Bilateral Grid (Gray, Medium)...")
    # Bilateral Grid approximation: s_s=16, s_r=16, sigma_s=1.0, sigma_r=1.0
    # In OpenCV, sigmaSpace and sigmaColor are roughly s_s * sigma_s and s_r * sigma_r
    aot_res = taichi_aot.bilateral_grid_filter(img_gray.astype(np.float32), preset="medium")
    
    # OpenCV reference (Exact Bilateral)
    # sigmaColor=16, sigmaSpace=16
    cv_res = cv2.bilateralFilter(img_gray, d=-1, sigmaColor=16, sigmaSpace=16)
    
    mae = np.mean(np.abs(aot_res - cv_res.astype(np.float32)))
    status = "PASS" if mae < 10.0 else "FAIL" # Higher tolerance for approximation
    print(f"[{status}] Gray Medium | MAE: {mae:.4f} | Limit: 10.0")

    # 2. RGB Verification (Light)
    print("Running Bilateral Grid (RGB, Light)...")
    aot_res_rgb = taichi_aot.bilateral_grid_filter(img.astype(np.float32), preset="light")
    
    # OpenCV reference for RGB
    cv_res_rgb = cv2.bilateralFilter(img, d=-1, sigmaColor=32, sigmaSpace=32)
    
    mae_rgb = np.mean(np.abs(aot_res_rgb - cv_res_rgb.astype(np.float32)))
    status_rgb = "PASS" if mae_rgb < 15.0 else "FAIL"
    print(f"[{status_rgb}] RGB Light   | MAE: {mae_rgb:.4f} | Limit: 15.0")

    # 3. Performance Check
    import time
    start = time.time()
    for _ in range(10):
        taichi_aot.bilateral_grid_filter(img.astype(np.float32), preset="medium")
    end = time.time()
    print(f"Average Time (512x512 RGB): {(end-start)/10*1000:.2f} ms")

    print("="*60)

if __name__ == "__main__":
    verify_bilateral_grid()
