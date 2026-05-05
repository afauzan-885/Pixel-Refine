import numpy as np
import os
import sys
import time

# Path setup
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Force AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def numpy_ransac_cleanup(flow, threshold=1.0, iterations=5):
    h, w = flow.shape[:2]
    u = flow[:,:,0]
    v = flow[:,:,1]
    
    # Initial model: Mean
    model_u = np.mean(u)
    model_v = np.mean(v)
    
    for _ in range(iterations):
        # Find inliers
        err_sq = (u - model_u)**2 + (v - model_v)**2
        inliers = err_sq < (threshold * threshold)
        
        if np.any(inliers):
            model_u = np.mean(u[inliers])
            model_v = np.mean(v[inliers])
        else:
            break
            
    # Final result
    err_sq = (u - model_u)**2 + (v - model_v)**2
    inliers = err_sq < (threshold * threshold)
    
    res = flow.copy()
    res[~inliers, 0] = model_u
    res[~inliers, 1] = model_v
    return res

def test_ransac_precision():
    print("=== RANSAC PRECISION VERIFICATION (TAICHI AOT vs NUMPY) ===")
    
    h, w = 512, 512
    # Create synthetic flow: Global motion (2, 3) + 20% Outliers (random)
    flow = np.zeros((h, w, 2), dtype=np.float32)
    flow[:, :, 0] = 2.0
    flow[:, :, 1] = 3.0
    
    # Add noise
    flow += np.random.normal(0, 0.1, (h, w, 2)).astype(np.float32)
    
    # Add outliers
    mask = np.random.random((h, w)) < 0.2
    flow[mask] = np.random.uniform(-10, 10, (np.sum(mask), 2)).astype(np.float32)
    
    threshold = 1.0
    
    # Taichi AOT (Warm up)
    flow_gpu = taichi_aot.engine.upload(flow, is_vector=True)
    taichi_aot.ransac_flow_cleanup(flow_gpu, threshold=threshold)
    
    # Taichi AOT (Timed)
    start = time.perf_counter()
    taichi_res = taichi_aot.ransac_flow_cleanup(flow_gpu, threshold=threshold)
    ti_time = time.perf_counter() - start
    
    # NumPy (Ideal Reference)
    start = time.perf_counter()
    numpy_res = numpy_ransac_cleanup(flow, threshold=threshold, iterations=5)
    np_time = time.perf_counter() - start
    
    mae = np.mean(np.abs(taichi_res - numpy_res))
    print(f"RANSAC MAE: {mae:.10f}")
    print(f"Taichi Time (Warm): {ti_time*1000:.2f}ms")
    print(f"NumPy Time: {np_time*1000:.2f}ms")
    
    # Check Model Parity (Sample one pixel that was an outlier)
    # If the model is same, the replaced values should be same.
    outlier_idx = np.where(mask.flatten())[0][0]
    ti_model = taichi_res.reshape(-1, 2)[outlier_idx]
    np_model = numpy_res.reshape(-1, 2)[outlier_idx]
    
    print(f"Taichi Model: {ti_model}")
    print(f"NumPy Model:  {np_model}")
    
    if mae < 0.0002: # Adjusted threshold for stride=4
        print("[PASS] RANSAC Parity is excellent!")
    else:
        print("[FAIL] RANSAC Parity exceeds threshold.")
        
    # Check model parity
    # Note: Taichi uses stride=4 for refinement in my bridge, so it might be slightly different
    # Let's check if they are close.
    
    taichi_aot.engine.clear_pool()

if __name__ == "__main__":
    test_ransac_precision()
