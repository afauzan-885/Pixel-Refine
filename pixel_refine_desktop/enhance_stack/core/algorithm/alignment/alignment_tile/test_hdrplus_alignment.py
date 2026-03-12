import numpy as np
import time
import os
import sys

# Use CUDA for final verification
os.environ["TAICHI_ARCH"] = "cuda"

# Add the project root to sys.path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../../../")
)
sys.path.append(project_root)

# Import Taichi but do NOT init it manually
import taichi as ti
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_alignmentHDRplus import (
    compute_alignment_hdrplus,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.taichi_worker import (
    ti_thread,
)


def test_hdrplus_alignment():
    print("Testing HDR+ Alignment Variation (CUDA Mode)...")

    # Create synthetic test data with a larger pattern
    h, w = 512, 512
    ref_data = np.zeros((h, w), dtype=np.float32)
    # Put a large square in it
    ref_data[128:384, 128:384] = 0.5
    # Add some noise for texture
    ref_data += np.random.rand(h, w).astype(np.float32) * 0.1

    # Create shifted image (16 pixels right, 8 pixels down)
    shift_y, shift_x = 8, 16
    comp_data = np.zeros_like(ref_data)
    # Roll handles wrapping which is easier for FFT/PhaseCorrelation
    comp_data = np.roll(ref_data, (shift_y, shift_x), axis=(0, 1))

    print(f"Synthetic Shift: (dx={shift_x}, dy={shift_y})")

    # Run New compute_alignment_hdrplus multiple times for benchmarking
    print("\nSubmitting compute_alignment_hdrplus to worker...")
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import (
        taichi_worker,
    )

    num_runs = 10
    execution_times = []
    
    for i in range(num_runs):
        t_start = time.perf_counter()
        flow_gpu_hdr = compute_alignment_hdrplus(ref_data, comp_data, n_layers=3)
        t_end = time.perf_counter()
        
        exec_time = (t_end - t_start) * 1000
        execution_times.append(exec_time)
        print(f"Run {i+1}/{num_runs} Execution Time: {exec_time:.2f}ms")
        
        # Only download and validate the last run to save time, or do it for the first
        if i == num_runs - 1:
            flow_hdr = taichi_worker.download_taichi_ndarray(flow_gpu_hdr)
            
            # Check a central area to avoid boundary effects from roll
            roi = flow_hdr[100:-100, 100:-100]
            avg_dx_hdr = np.mean(roi[..., 0])
            avg_dy_hdr = np.mean(roi[..., 1])
            
            print(f"\nHDR+ Flow Result -> Avg dx: {avg_dx_hdr:.4f}, avg dy: {avg_dy_hdr:.4f}")
            print(f"Expected Result -> dx: {float(shift_x)}, dy: {float(shift_y)}")
            
            # Validation
            if abs(avg_dx_hdr - shift_x) < 0.5 and abs(avg_dy_hdr - shift_y) < 0.5:
                print("SUCCESS: Alignment is accurate!")
            else:
                print("WARNING: Alignment accuracy is low.")
                
        taichi_worker.release_taichi_ndarray(flow_gpu_hdr)

    # Calculate average ignoring the first run (JIT compilation overhead)
    if num_runs > 1:
        avg_time = sum(execution_times[1:]) / (num_runs - 1)
        print(f"\nAverage Execution Time (excluding first run): {avg_time:.2f}ms")
    else:
        print(f"\nExecution Time: {execution_times[0]:.2f}ms")


if __name__ == "__main__":
    try:
        test_hdrplus_alignment()
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
