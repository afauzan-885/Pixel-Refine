import numpy as np
import cv2
import os
import sys

# Fungsi mocking untuk OpenCV Noise Estimation
def estimate_noise_in_python_local(ref_image_gray_float):
    if ref_image_gray_float is None or ref_image_gray_float.size == 0:
        return 0.015
    lap = cv2.Laplacian(ref_image_gray_float, cv2.CV_32F, ksize=3)
    if lap is None:
        return 0.015
    median_val = np.median(lap)
    mad_value = np.median(np.abs(lap - median_val))
    estimated_sigma = mad_value * 1.4826
    return float(np.clip(estimated_sigma, 0.00001, 0.99999))

def test_noise_parity():
    # Lazy imports inside function to avoid project-level circular imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.taichi_bridge import estimate_noise_gpu
    from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

    print("============================================================")
    print(" NOISE ESTIMATION PARITY TEST: OPENCV VS TAICHI GPU")
    print("============================================================")
    
    # 1. Load Test Image
    test_img_path = "test_algorithm/IMG_20250401_182043_B003.png"
    if not os.path.exists(test_img_path):
        print(f"Warning: {test_img_path} not found. Using synthetic noise.")
        img_np = np.random.normal(0.5, 0.1, (1024, 1024)).astype(np.float32)
        img_gray = np.clip(img_np, 0, 1)
    else:
        img_bgr = cv2.imread(test_img_path)
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

    # 2. Estimate with OpenCV (Python)
    sigma_py = estimate_noise_in_python_local(img_gray)
    
    # 3. Estimate with Taichi (GPU)
    img_gpu = taichi_aot.upload(img_gray)
    sigma_gpu = estimate_noise_gpu(img_gpu)
    
    # 4. Results
    diff = abs(sigma_py - sigma_gpu)
    parity = "PASS" if diff < 0.01 else "CALIBRATION_NEEDED"
    
    print(f"\n[Results]")
    print(f"  OpenCV (CPU): {sigma_py:.6f}")
    print(f"  Taichi (GPU): {sigma_gpu:.6f}")
    print(f"  Difference:   {diff:.6f}")
    print(f"  Status:       [{parity}]")
    
    if parity == "CALIBRATION_NEEDED":
        suggested_multiplier = (sigma_py / (sigma_gpu / 0.85)) 
        print(f"\n  Tip: Try adjusting the multiplier in taichi_bridge.py to ~{suggested_multiplier:.4f}")

if __name__ == "__main__":
    test_noise_parity()
