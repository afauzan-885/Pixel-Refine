import numpy as np
import cv2
import os
import sys

# Path setup
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def verify_phase_correlation():
    print("="*60)
    print(" TAICHI AOT PHASE CORRELATION VERIFICATION ")
    print("="*60)
    
    # Load test image
    img_path = os.path.join(project_root, "test_data/ref_00.png")
    if not os.path.exists(img_path):
        img = (np.random.rand(512, 512) * 255).astype(np.uint8)
    else:
        img = cv2.imread(img_path, 0)
        img = cv2.resize(img, (512, 512))

    # Apply shift: dx=10, dy=-5
    dx_true, dy_true = 10, -5
    M = np.float32([[1, 0, dx_true], [0, 1, dy_true]])
    img_shifted = cv2.warpAffine(img, M, (512, 512), borderMode=cv2.BORDER_REFLECT)

    # 1. Test with Hanning (Recommended)
    print("Running Phase Correlation (with Hanning)...")
    dx, dy, response = taichi_aot.phase_correlation(img.astype(np.float32), img_shifted.astype(np.float32), use_hanning=True)
    
    # Note: Shift direction might be reversed depending on convention
    # Formula: Cross-power spectrum R = (G * F*) / |F * G*|
    # If G is shifted version of F (G = F translated), peak at shift.
    
    err_x = abs(dx - dx_true)
    err_y = abs(dy - dy_true)
    
    status = "PASS" if (err_x < 0.5 and err_y < 0.5) else "FAIL"
    print(f"[{status}] Shift found: ({dx:.2f}, {dy:.2f}) | True: ({dx_true}, {dy_true}) | Response: {response:.4f}")

    # 2. Test without Hanning
    print("Running Phase Correlation (without Hanning)...")
    dx2, dy2, response2 = taichi_aot.phase_correlation(img.astype(np.float32), img_shifted.astype(np.float32), use_hanning=False)
    err_x2 = abs(dx2 - dx_true)
    err_y2 = abs(dy2 - dy_true)
    status2 = "PASS" if (err_x2 < 0.5 and err_y2 < 0.5) else "FAIL"
    print(f"[{status2}] Shift found: ({dx2:.2f}, {dy2:.2f}) | True: ({dx_true}, {dy_true}) | Response: {response2:.4f}")

    print("="*60)

if __name__ == "__main__":
    verify_phase_correlation()
