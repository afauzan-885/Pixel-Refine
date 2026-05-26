import os
import time
import rawpy

dng_path = "test_algorithm/IMG_20260429_230301Z_B015.dng"
if not os.path.exists(dng_path):
    print("DNG file not found!")
    exit(1)

n_iters = 10

print("Benchmarking rawpy CPU demosaicing (AHD/default)...")

with rawpy.imread(dng_path) as raw:
    # Warmup
    rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True)
    
    # Benchmark loop
    start_time = time.perf_counter()
    for i in range(n_iters):
        t0 = time.perf_counter()
        rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True)
        t1 = time.perf_counter()
        print(f"  Frame {i+1:02d}/{n_iters} processed in {(t1-t0)*1000:.2f} ms")
        
    end_time = time.perf_counter()

total_time = end_time - start_time
avg_time = (total_time / n_iters) * 1000
fps = n_iters / total_time

print(f"\n[Rawpy CPU Benchmark Results]")
print(f"  Total Time for {n_iters} frames: {total_time*1000:.2f} ms")
print(f"  Average Speed per frame: {avg_time:.2f} ms")
print(f"  Throughput: {fps:.2f} FPS!")
