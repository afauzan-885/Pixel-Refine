import numpy as np
import time
import os
import sys
import cv2

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import preprocess

def benchmark_preprocess_aot():
    print("\n--- PREPROCESS BENCHMARK (10 Iterations) ---")
    
    # 1. Load Real Image
    img_path = os.path.join(project_root, "test_algorithm/IMG_20160202_015247.png")
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("[Error] Failed to load image.")
        return
        
    print(f"[Input] Image: {os.path.basename(img_path)} ({img.shape}, {img.dtype})")
    target_size = (3000, 3000) # Kita uji resolusi penuh agar beban terasa
    
    # --- WARM UP (1 Iteration) ---
    print("\nWarming up engine and loading module...")
    preprocess.preprocess_pipeline_gpu(img, target_size=target_size)
    print("Warm-up complete.")

    # --- BENCHMARK (10 Iterations) ---
    print(f"\nRunning 10 iterations at {target_size} resolution...")
    times = []
    
    for i in range(10):
        t0 = time.perf_counter()
        
        # Eksekusi pipeline lengkap (Upload -> Dispatch -> Download)
        res_gpu = preprocess.preprocess_pipeline_gpu(
            img, 
            target_size=target_size,
            apply_gamma=True,
            scale=1.0
        )
        # Kita hilangkan to_numpy untuk melihat kecepatan murni GPU (Pipelining)
        # _ = res_gpu.to_numpy() 
        
        ms = (time.perf_counter() - t0) * 1000
        times.append(ms)
        print(f" Iteration {i+1:02d}: {ms:.2f} ms")
    
    avg_time = np.mean(times)
    min_time = np.min(times)
    fps = 1000.0 / avg_time
    
    print(f"\n[Final Statistics]")
    print(f"Average Time : {avg_time:.2f} ms")
    print(f"Minimum Time : {min_time:.2f} ms")
    print(f"Throughput   : {fps:.2f} FPS")
    print("-" * 40)

if __name__ == "__main__":
    benchmark_preprocess_aot()
