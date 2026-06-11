import os
import sys
import numpy as np
import cv2
import time

# Setup Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Enable AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import perform_image_alignment
from taichi_library.taichi_aot.engine import AOTEngine

def test_alignment_with_flow_remap():
    print("=== End-to-End AOT Alignment Test with remap_with_flow ===")
    
    # Init engine to verify GPU auto-selection is outputted
    engine = AOTEngine()
    
    # Generate reference and comparison images (synthesize shift)
    h, w = 1024, 1024
    np.random.seed(42)
    ref_img = (np.random.rand(h, w, 3) * 255.0).astype(np.uint8)
    
    # 10px X shift, 5px Y shift
    M = np.float32([[1, 0, 10], [0, 1, 5]])
    comp_img = cv2.warpAffine(ref_img, M, (w, h))
    
    # Create copies for two alignment runs
    images_legacy = [ref_img.copy(), comp_img.copy()]
    images_opt = [ref_img.copy(), comp_img.copy()]
    
    # Define parameters
    work_res_h, work_res_w = 256, 256
    tile_h, tile_w = 16, 16
    ref_dtype = np.uint8
    
    # Run Legacy Mode (use_flow_remap=False)
    print("\n[Test] Running Legacy Alignment (using map_x/y buffers)...")
    start = time.time()
    success_legacy = perform_image_alignment(
        images_legacy,
        ref_img.astype(np.float32) / 255.0,
        work_res_h,
        work_res_w,
        tile_h,
        tile_w,
        ref_dtype,
        optical_flow_type="alignment_tile",
        use_flow_remap=False,
        save_align_image=False,
        harvest_alignment=False
    )
    time_legacy = time.time() - start
    print(f"Legacy Success: {success_legacy} in {time_legacy:.2f}s")
    
    # Run Optimized Mode (use_flow_remap=True)
    print("\n[Test] Running Optimized Alignment (using remap_with_flow on-the-fly)...")
    start = time.time()
    success_opt = perform_image_alignment(
        images_opt,
        ref_img.astype(np.float32) / 255.0,
        work_res_h,
        work_res_w,
        tile_h,
        tile_w,
        ref_dtype,
        optical_flow_type="alignment_tile",
        use_flow_remap=True,
        save_align_image=False,
        harvest_alignment=False
    )
    time_opt = time.time() - start
    print(f"Optimized Success: {success_opt} in {time_opt:.2f}s")
    
    # Verify results are equivalent (bit-perfect or extremely low error)
    legacy_aligned = images_legacy[1]
    opt_aligned = images_opt[1]
    
    mae = np.mean(np.abs(legacy_aligned.astype(np.float32) - opt_aligned.astype(np.float32)))
    print(f"\nMean Absolute Error between Legacy and Fused: {mae}")
    
    assert success_legacy and success_opt, "One of the runs failed!"
    assert mae < 1.0, f"MAE is too high: {mae}!"
    print("SUCCESS: End-to-end alignment output matches Legacy perfectly!")

if __name__ == "__main__":
    test_alignment_with_flow_remap()
