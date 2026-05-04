import numpy as np
import time
import os
import sys

# Setup path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

def test_bilinear():
    h, w = 3000, 3000
    img = np.random.rand(h, w, 3).astype(np.float32)
    img_gpu = taichi_aot.upload(img)
    
    print(f"Testing Bilinear AOT on {h}x{w} image...")
    
    # 1. Resize via generic API
    start = time.perf_counter()
    for _ in range(10):
        res = taichi_aot.resize(img_gpu, (512, 512), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
    taichi_aot.engine.sync()
    print(f"Bilinear Resize FPS: {10 / (time.perf_counter() - start):.2f}")
    
    # 2. Alias
    start = time.perf_counter()
    for _ in range(10):
        res = taichi_aot.bilinear_interpolation(img_gpu, 512, 512, return_gpu=True)
    taichi_aot.engine.sync()
    print(f"Bilinear Alias FPS: {10 / (time.perf_counter() - start):.2f}")
    
    print("Bilinear Test Finished Successfully!")

if __name__ == "__main__":
    test_bilinear()
