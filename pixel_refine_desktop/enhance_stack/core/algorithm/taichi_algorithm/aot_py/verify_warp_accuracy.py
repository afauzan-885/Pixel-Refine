import taichi as ti
import numpy as np
import cv2
import os
import sys
import time

# Path setup
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def verify_accuracy():
    print("\n" + "="*60)
    print(" TAICHI AOT TURBO WARP ACCURACY VERIFICATION (vs OPENCV)")
    print("="*60)

    # 1. Prepare Test Data (1024x1024 16-bit)
    h, w = 1024, 1024
    # Create a gradient pattern + noise for challenging interpolation
    img = np.linspace(0, 65535, h*w).reshape(h, w).astype(np.int32)
    img_3ch = np.stack([img, img//2, img//4], axis=-1).astype(np.int32)
    
    # 2. Create a Smooth Flow (Sine wave displacement)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    flow_u = 10.0 * np.sin(y / 50.0)
    flow_v = 10.0 * np.cos(x / 50.0)
    flow = np.stack([flow_u, flow_v], axis=-1).astype(np.float32)

    # --- TAICHI AOT TURBO EXECUTION ---
    print(f"Running Taichi AOT Turbo Warp (3-Channel)...")
    start_ti = time.perf_counter()
    res_ti_gpu = taichi_aot.warp_image(img_3ch, flow, ref=img_3ch, return_gpu=True)
    res_ti = res_ti_gpu.to_numpy()
    del res_ti_gpu
    ti_time = time.perf_counter() - start_ti
    print(f"Taichi AOT Turbo Time: {ti_time*1000:.2f} ms")

    # --- OPENCV REFERENCE ---
    print(f"Running OpenCV Remap (INTER_CUBIC)...")
    start_cv = time.perf_counter()
    map_x = x + flow_u
    map_y = y + flow_v
    img_cv = img_3ch.astype(np.uint16)
    res_cv = cv2.remap(img_cv, map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
    cv_time = time.perf_counter() - start_cv
    print(f"OpenCV Time: {cv_time*1000:.2f} ms")

    # --- ACCURACY CALCULATION ---
    res_ti_f = res_ti.astype(np.float32)
    res_cv_f = res_cv.astype(np.float32)

    diff = np.abs(res_ti_f - res_cv_f)
    mae = np.mean(diff)
    error_percent = (mae / 65535.0) * 100.0

    print("\n" + "-"*30)
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Error Percentage: {error_percent:.4f}%")
    print("-" * 30)

    if error_percent <= 0.012: # Original (0.0018) + Trade-off (0.01)
        print(f"[PASS] Turbo Accuracy is within limits (< 0.012%)")
    else:
        print(f"[FAIL] Turbo Accuracy error ({error_percent:.4f}%) exceeds limit!")

if __name__ == "__main__":
    verify_accuracy()
