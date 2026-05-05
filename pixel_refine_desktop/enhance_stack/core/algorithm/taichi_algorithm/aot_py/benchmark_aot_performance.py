import numpy as np
import time
import os
import sys

# Path setup
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def run_benchmark():
    print("="*70)
    print(" TAICHI AOT PERFORMANCE BENCHMARK (12MP -> 48MP) ")
    print("="*70)
    
    # 12MP (4000x3000)
    h, w = 3000, 4000
    print(f"Input Resolution: {w}x{h} (12.0 MP)")
    
    # Create test data
    img_1ch = np.random.rand(h, w).astype(np.float32)
    img_3ch = np.random.rand(h, w, 3).astype(np.float32)
    
    # Warmup
    print("Warming up GPU...")
    taichi_aot.resize(img_1ch, (w//4, h//4), interpolation=taichi_aot.INTER_AREA)
    
    def measure(name, func, *args, **kwargs):
        iters = 10
        # Measure Full Roundtrip (NumPy in -> NumPy out)
        start = time.perf_counter()
        for _ in range(iters):
            res = func(*args, **kwargs)
        end = time.perf_counter()
        avg_full = (end - start) / iters
        
        print(f" - Running GPU measure for {name}...")
        # Measure GPU Only
        src_gpu = None
        res_gpu = None
        avg_gpu = 0.0
        
        try:
            # Determine if we should use vector based on how the bridge handles it
            is_3ch = (len(args[0].shape) == 3 and args[0].shape[2] == 3)
            is_flow = (len(args[0].shape) == 3 and args[0].shape[2] == 2)
            
            # Simple heuristic for pre-uploading
            if "Median" not in name and "Bilateral Grid" not in name:
                is_vec_upload = is_flow or is_3ch
                src_gpu = taichi_aot.upload(args[0], is_vector=is_vec_upload)
                new_args = list(args)
                new_args[0] = src_gpu
                kwargs['return_gpu'] = True
                
                start_gpu = time.perf_counter()
                for _ in range(iters):
                    res_gpu = func(*new_args, **kwargs)
                end_gpu = time.perf_counter()
                avg_gpu = (end_gpu - start_gpu) / iters
            else:
                # For complex ones, just measure full roundtrip and estimate
                avg_gpu = 0.0 # Will mark as N/A
        except Exception as e:
            avg_gpu = -1.0
        
        fps = 1.0 / avg_full
        gpu_str = f"{avg_gpu*1000:7.2f}ms" if avg_gpu > 0 else "   N/A   "
        print(f"{name:35} | GPU: {gpu_str} | Full: {avg_full*1000:7.2f}ms | FPS: {fps:5.1f}")
        
        # Cleanup
        del src_gpu, res_gpu

    # --- BENCHMARK SUITE ---
    
    # 1. Resize (Upscaling 2x)
    target_size = (w*2, h*2) # 8000x6000 (48MP)
    measure("Bicubic Resize (12MP->48MP RGB)", taichi_aot.resize, img_3ch, target_size, interpolation=taichi_aot.INTER_CUBIC)
    measure("Bilinear Resize (12MP->48MP RGB)", taichi_aot.resize, img_3ch, target_size, interpolation=taichi_aot.INTER_LINEAR)
    
    # 2. Filters (12MP)
    measure("Gaussian Blur (12MP RGB, s=1.5)", taichi_aot.gaussian_blur, img_3ch, sigma=1.5)
    measure("Box Filter (12MP RGB, k=5)", taichi_aot.box_filter, img_3ch, kernel_size=5)
    measure("Median Filter (12MP RGB, 3x3)", taichi_aot.median_filter, img_3ch)
    
    # 3. Edge Preserving (12MP)
    # Testing RGB Bilateral Grid (Heavy)
    measure("Bilateral Grid (12MP RGB, Heavy)", taichi_aot.bilateral_grid_filter, img_3ch, preset="heavy")
    measure("Joint Bilateral (12MP Gray, Med)", taichi_aot.joint_bilateral_filter, img_1ch, img_1ch, preset="medium")
    
    # 4. Alignment / Warp
    flow = np.zeros((h, w, 2), dtype=np.float32)
    measure("Warping (12MP RGB)", taichi_aot.warp_image, img_3ch, flow)
    
    # 5. Phase Correlation (2048x2048)
    img_2k = np.random.rand(2048, 2048).astype(np.float32)
    # Wrap in a lambda to handle the return values and avoid measure() complexity
    start = time.perf_counter()
    for _ in range(10):
        taichi_aot.phase_correlation(img_2k, img_2k)
    end = time.perf_counter()
    print(f"{'Phase Correlation (2048x2048 Gray)':35} | Full: {(end-start)/10*1000:7.2f}ms | FPS: {10/(end-start):5.1f}")

    print("="*70)

if __name__ == "__main__":
    try:
        run_benchmark()
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
