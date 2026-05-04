import os
import sys
import numpy as np
import cv2
import time
import importlib.util

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

def verify_ncc_accuracy():
    print("==================================================")
    print(" NCC Accuracy Verification: Taichi AOT vs OpenCV")
    print("==================================================")

    # 1. Prepare Test Data (Deterministic for debugging)
    np.random.seed(42)
    # Smaller size to isolate issues
    img_size = 256
    img = np.random.rand(img_size, img_size).astype(np.float32)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    
    true_y, true_x = 100, 80
    h_t, w_t = 32, 32
    template = img[true_y:true_y+h_t, true_x:true_x+w_t].copy()
    
    # 2. Run OpenCV (Ground Truth)
    start = time.perf_counter()
    res_cv = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val_cv, max_val_cv, min_loc_cv, max_loc_cv = cv2.minMaxLoc(res_cv)
    cv_x, cv_y = max_loc_cv
    cv_time = (time.perf_counter() - start) * 1000
    print(f"OpenCV: Found at ({cv_y}, {cv_x}), Score: {max_val_cv:.6f}, Time: {cv_time:.2f}ms")

    # 3. Run Taichi AOT (Hierarchical)
    print("\nRunning Taichi AOT...")
    os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
    from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot
    importlib.reload(taichi_aot)
    
    start = time.perf_counter()
    res_aot = taichi_aot.zncc(img, template)
    aot_score, aot_y, aot_x = res_aot[0]
    aot_time = (time.perf_counter() - start) * 1000
    print(f"Taichi AOT: Found at ({aot_y}, {aot_x}), Score: {aot_score:.6f}, Time: {aot_time:.2f}ms")
    
    # 4. Final Comparison
    print("\n--------------------------------------------------")
    print(" FINAL COMPARISON")
    print("--------------------------------------------------")
    print(f"OpenCV: ({cv_y}, {cv_x}) Score: {max_val_cv:.6f}")
    print(f"AOT:    ({aot_y}, {aot_x}) Score: {aot_score:.6f} Error: {np.sqrt((cv_y-aot_y)**2 + (cv_x-aot_x)**2):.4f}px")
    
    aot_err = np.sqrt((cv_y - aot_y)**2 + (cv_x - aot_x)**2)
    if aot_err < 1.0:
        print("\n[SUCCESS] Taichi AOT is accurate!")
    else:
        print("\n[FAILED] Taichi AOT accuracy is outside tolerance.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    verify_ncc_accuracy()
