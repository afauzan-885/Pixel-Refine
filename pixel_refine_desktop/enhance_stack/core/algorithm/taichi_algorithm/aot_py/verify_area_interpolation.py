import numpy as np
import cv2
import os
import sys

# Path setup
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def verify_area_interpolation():
    print("="*60)
    print(" TAICHI AOT INTER_AREA VERIFICATION ")
    print("="*60)
    
    # Load test image
    img_path = os.path.join(project_root, "test_data/ref_00.png")
    if not os.path.exists(img_path):
        img = (np.random.rand(512, 512, 3) * 255).astype(np.uint8)
    else:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (512, 512))

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Grayscale Downscaling (4x)
    print("Test 1: Grayscale 4x Downscaling (512x512 -> 128x128)...")
    target_size = (128, 128)
    aot_res = taichi_aot.resize(img_gray.astype(np.float32), target_size, interpolation=taichi_aot.INTER_AREA)
    cv_res = cv2.resize(img_gray, target_size, interpolation=cv2.INTER_AREA)
    
    mae = np.mean(np.abs(aot_res - cv_res.astype(np.float32)))
    status = "PASS" if mae < 0.5 else "FAIL"
    print(f"[{status}] Gray 4x | MAE: {mae:.6f} | Limit: 0.5")

    # 2. RGB Downscaling (Fractional 1.5x)
    print("Test 2: RGB 1.5x Downscaling (512x512 -> 341x341)...")
    target_size_frac = (341, 341)
    aot_res_rgb = taichi_aot.resize(img.astype(np.float32), target_size_frac, interpolation=taichi_aot.INTER_AREA)
    cv_res_rgb = cv2.resize(img, target_size_frac, interpolation=cv2.INTER_AREA)
    
    mae_rgb = np.mean(np.abs(aot_res_rgb - cv_res_rgb.astype(np.float32)))
    status_rgb = "PASS" if mae_rgb < 0.5 else "FAIL"
    print(f"[{status_rgb}] RGB 1.5x | MAE: {mae_rgb:.6f} | Limit: 0.5")

    # 3. Performance Check
    import time
    start = time.time()
    for _ in range(20):
        taichi_aot.resize(img.astype(np.float32), (128, 128), interpolation=taichi_aot.INTER_AREA)
    end = time.time()
    print(f"Average Time (512x512 -> 128x128 RGB): {(end-start)/20*1000:.2f} ms")

    print("="*60)

if __name__ == "__main__":
    verify_area_interpolation()
