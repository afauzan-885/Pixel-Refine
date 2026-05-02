import time
import numpy as np
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Standardized Import
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def run_stress_test(iterations=20):
    print(f"=== Taichi AOT Stress Test ({iterations} Iterations) ===")
    
    # 1. Image Data Generation (12MP)
    h_orig, w_orig = 3000, 4000
    print(f"Generating {w_orig}x{h_orig} source image...")
    img = np.random.rand(h_orig, w_orig, 3).astype(np.float32)
    
    # 2. Initialization & Warm-up
    print("\n[Phase 1] Initializing & Warm-up...")
    start_init = time.time()
    # First call triggers DLL loading and TCM parsing
    _ = taichi_aot.resize(img, (1000, 750))
    print(f"Initialization + First Resize: {(time.time()-start_init)*1000:.2f} ms")

    # 3. Pure GPU Processing Test (Zero-Overhead)
    print(f"\n[Phase 2] Running {iterations} iterations of Downscaling (12MP -> 1MP)...")
    print("Mode: Pure GPU (Image stays on VRAM, only compute is measured)")
    
    # Upload to GPU ONCE
    gpu_img = taichi_aot.upload(img)
    
    latencies = []
    for i in range(iterations):
        start = time.time()
        # Resize with return_gpu=True to prevent downloading back to NumPy
        gpu_result = taichi_aot.resize(gpu_img, (1000, 750), return_gpu=True)
        latencies.append((time.time() - start) * 1000)
        
        if (i + 1) % 5 == 0:
            print(f"  Iteration {i+1}/{iterations}...")

    avg_latency = sum(latencies) / iterations
    print(f"\n>>> Average GPU Compute Time: {avg_latency:.2f} ms")
    print(f">>> Max Latency: {max(latencies):.2f} ms")
    print(f">>> Min Latency: {min(latencies):.2f} ms")

    # 4. Sampling Stress Test
    print(f"\n[Phase 3] Running {iterations} iterations of Batch Sampling (100,000 points)...")
    coords = np.random.rand(100000, 2).astype(np.float32) * [w_orig-2, h_orig-2]
    
    sample_latencies = []
    for i in range(iterations):
        start = time.time()
        _ = taichi_aot.sample_at(gpu_img, coords, return_gpu=True)
        sample_latencies.append((time.time() - start) * 1000)

    avg_sample = sum(sample_latencies) / iterations
    print(f"\n>>> Average Sampling Time: {avg_sample:.2f} ms")

    print("\n=== Stress Test Completed ===")

if __name__ == "__main__":
    try:
        run_stress_test(20)
    except Exception as e:
        print(f"\n[Critical Error] {e}")
        import traceback
        traceback.print_exc()
