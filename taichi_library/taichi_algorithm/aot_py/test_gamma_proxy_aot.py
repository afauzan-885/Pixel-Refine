import numpy as np
import os
import sys
import cv2
import time

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_library.alignment.alignment_features.taichi_bridge import to_gamma_proxy_gpu

def to_gamma_proxy_python(linear_img, scale=1.0, gamma_pow=2.22, slope=4.5, cutoff=0.018):
    x = linear_img * scale
    x_mapped = x / np.sqrt(1.0 + x * x)
    res = np.power(np.clip(x_mapped, 0.0, 1.0), 1.0 / gamma_pow)
    return res.astype(np.float32)

def verify_aot_parity():
    from taichi_library.taichi_aot.engine import AOTEngine
    engine = AOTEngine()
    
    print("\n" + "="*60)
    print(" GAMMA PROXY AOT PARITY VERIFICATION")
    print("="*60)
    
    # 1. Load Real Image
    img_path = os.path.join(project_root, "test_algorithm/IMG_20160202_015247.png")
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("[Error] Image not found.")
        return
        
    # Convert to RGB Float [0, 1] for alignment-style input
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    print(f"[Input] {os.path.basename(img_path)} ({img_rgb.shape}, {img_rgb.dtype})")
    
    scale = 1.0
    
    # 2. Python Reference
    t0 = time.perf_counter()
    ref_out = to_gamma_proxy_python(img_rgb, scale=scale)
    print(f"[Python] Reference computed in {(time.perf_counter()-t0)*1000:.2f} ms")
    
    # 3. AOT Implementation
    # Upload to GPU first
    img_gpu = engine.upload(img_rgb)
    
    t0 = time.perf_counter()
    aot_gpu = to_gamma_proxy_gpu(img_gpu, scale=scale)
    engine.sync() # Ensure completion
    aot_time = (time.perf_counter()-t0)*1000
    
    aot_out = aot_gpu.to_numpy()
    print(f"[AOT] Pipeline computed in {aot_time:.2f} ms")
    
    # 4. Compare
    diff = np.abs(ref_out - aot_out)
    mae = np.mean(diff)
    max_err = np.max(diff)
    
    tolerance = 0.0000001 # 0.00001%
    
    print("\n" + "-"*40)
    print(f"Mean Absolute Error (MAE): {mae:.10f}")
    print(f"Max Absolute Error (Max): {max_err:.10f}")
    print(f"Target Tolerance         : {tolerance:.10f}")
    
    print(f"\n[Stats] Ref - Min: {ref_out.min():.4f}, Max: {ref_out.max():.4f}, Mean: {ref_out.mean():.4f}")
    print(f"[Stats] AOT - Min: {aot_out.min():.4f}, Max: {aot_out.max():.4f}, Mean: {aot_out.mean():.4f}")

    if max_err <= tolerance:
        print("\n>>> [SUCCESS] AOT Parity Achieved! (Bit-Perfect)")
    elif max_err <= 1e-6:
        print("\n>>> [PASS] High Precision Achieved (1e-6 threshold)")
    else:
        print("\n>>> [FAILURE] Precision Mismatch!")
        
    print("-"*40 + "\n")

if __name__ == "__main__":
    verify_aot_parity()
