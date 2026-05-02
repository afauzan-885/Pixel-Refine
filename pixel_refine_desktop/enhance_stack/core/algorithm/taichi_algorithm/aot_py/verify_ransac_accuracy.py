import taichi as ti
import numpy as np
import time
import os
import sys
import cv2

# Path setup
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Force AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def verify_ransac():
    print("=" * 50)
    print(" RANSAC ACCURACY VERIFICATION (Taichi vs OpenCV/Ground Truth)")
    print("=" * 50)

    # 1. Prepare Synthetic Data (128x128 Flow)
    h, w = 128, 128
    true_dx, true_dy = 2.5, -1.8
    
    # Base translation
    flow = np.zeros((h, w, 2), dtype=np.float32)
    flow[:, :, 0] = true_dx
    flow[:, :, 1] = true_dy
    
    # Add Gaussian Noise
    flow += np.random.randn(h, w, 2).astype(np.float32) * 0.1
    
    # Add Outliers (20% of pixels are random garbage)
    outlier_mask = np.random.rand(h, w) < 0.2
    flow[outlier_mask] = np.random.uniform(-10, 10, (np.sum(outlier_mask), 2))

    print(f"Flow Size: {h}x{h}")
    print(f"Ground Truth Translation: ({true_dx}, {true_dy})")
    print(f"Outlier Ratio: 20%")

    # 2. Taichi RANSAC
    start_t = time.perf_counter()
    cleaned_gpu, model_taichi = taichi_aot.ransac_flow_cleanup(
        flow, threshold=1.0, n_iterations=10, return_model=True
    )
    t_taichi = (time.perf_counter() - start_t) * 1000
    
    # 3. OpenCV Reference (Using Median of non-outliers for parity)
    # Actually, let's use OpenCV findAffine2D on point grid
    y, x = np.mgrid[0:h, 0:w]
    pts1 = np.stack([x, y], axis=-1).reshape(-1, 2).astype(np.float32)
    pts2 = pts1 + flow.reshape(-1, 2)
    
    start_cv = time.perf_counter()
    affine_mat, inliers = cv2.estimateAffinePartial2D(pts1, pts2, method=cv2.RANSAC, ransacReprojThreshold=1.0)
    t_cv = (time.perf_counter() - start_cv) * 1000
    
    cv_dx = affine_mat[0, 2]
    cv_dy = affine_mat[1, 2]

    # 4. Compare
    print(f"\nTaichi Time: {t_taichi:.2f} ms")
    print(f"OpenCV Time: {t_cv:.2f} ms")
    print("-" * 30)
    print(f"Taichi Vector: ({model_taichi[0]:.4f}, {model_taichi[1]:.4f})")
    print(f"OpenCV Vector: ({cv_dx:.4f}, {cv_dy:.4f})")
    
    err_taichi = np.sqrt((model_taichi[0] - true_dx)**2 + (model_taichi[1] - true_dy)**2)
    err_opencv = np.sqrt((cv_dx - true_dx)**2 + (cv_dy - true_dy)**2)
    
    print(f"Taichi L2 Error: {err_taichi:.6f}")
    print(f"OpenCV L2 Error: {err_opencv:.6f}")
    
    diff = np.sqrt((model_taichi[0] - cv_dx)**2 + (model_taichi[1] - cv_dy)**2)
    print(f"Taichi vs OpenCV Deviation: {diff:.6f}")

    if diff < 0.1:
        print("\n[PASSED] RANSAC Accuracy is within parity with OpenCV!")
    else:
        print("\n[WARNING] RANSAC Accuracy deviates significantly from OpenCV.")

if __name__ == "__main__":
    verify_ransac()
