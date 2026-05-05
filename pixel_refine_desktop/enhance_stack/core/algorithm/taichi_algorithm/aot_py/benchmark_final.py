import numpy as np
import time
import os
import sys

# Path setup
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def run_bench():
    print("="*60)
    print(" FINAL PERFORMANCE BENCHMARK (12MP) ")
    print("="*60)
    
    h, w = 3000, 4000
    img_3ch = np.random.rand(h, w, 3).astype(np.float32)
    img_gray = np.random.rand(h, w).astype(np.float32)
    
    # 1. Bicubic Upscale (12MP -> 48MP)
    print("Testing Bicubic 2x Upscale...")
    start = time.perf_counter()
    for _ in range(10):
        taichi_aot.resize(img_3ch, (w*2, h*2), interpolation=taichi_aot.INTER_CUBIC)
    end = time.perf_counter()
    print(f"Bicubic 12MP->48MP | Avg Time: {(end-start)/10*1000:7.2f}ms | FPS: {10/(end-start):5.1f}")
    
    # 2. Gaussian Blur (12MP)
    print("Testing Gaussian Blur...")
    start = time.perf_counter()
    for _ in range(10):
        taichi_aot.gaussian_blur(img_3ch, sigma=1.5)
    end = time.perf_counter()
    print(f"Gaussian 12MP       | Avg Time: {(end-start)/10*1000:7.2f}ms | FPS: {10/(end-start):5.1f}")

    # 3. Bilateral Grid (12MP Gray Medium)
    print("Testing Bilateral Grid...")
    start = time.perf_counter()
    for _ in range(10):
        taichi_aot.bilateral_grid_filter(img_gray, preset="medium")
    end = time.perf_counter()
    print(f"Bilateral Grid 12MP | Avg Time: {(end-start)/10*1000:7.2f}ms | FPS: {10/(end-start):5.1f}")

    # 4. Phase Correlation (2048x2048)
    print("Testing Phase Correlation...")
    img_2k = np.random.rand(2048, 2048).astype(np.float32)
    start = time.perf_counter()
    for _ in range(10):
        taichi_aot.phase_correlation(img_2k, img_2k)
    end = time.perf_counter()
    print(f"Phase Correlate 2K  | Avg Time: {(end-start)/10*1000:7.2f}ms | FPS: {10/(end-start):5.1f}")

    print("="*60)

if __name__ == "__main__":
    run_bench()
