import numpy as np
import taichi as ti
import os
import cv2

os.environ["PIXEL_REFINE_BACKEND"] = "PRODUCTION"

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.alignment_tile_taichi import (
    AlignmentTileTaichiAOT,
    AlignmentTileTaichiJIT,
)

def test_warp():
    # Setup data
    h, w = 512, 512
    work_h, work_w = 128, 128
    
    # Ref image
    np.random.seed(42)
    ref = np.random.randint(0, 65535, (h, w, 3), dtype=np.uint16)
    
    # Comp image (shifted slightly)
    comp = np.roll(ref, shift=5, axis=0) # Shift down 5 pixels
    
    aot = AlignmentTileTaichiAOT()
    jit = AlignmentTileTaichiJIT()
    
    # Reference
    aot.set_reference(ref, work_h, work_w, is_linear=True)
    jit.set_reference(ref, work_h, work_w, is_linear=True)
    
    # Warp AOT
    print("Computing AOT Warp...")
    aot_res = aot.compute_alignment_and_warp(comp, tile_h=128, tile_w=128, n_layers=3, is_linear=True, search_dist=4)
    if aot_res is None:
        print("AOT Warp failed!")
        return
        
    # Warp JIT
    print("Computing JIT Warp...")
    jit_res = jit.compute_alignment_and_warp(comp, tile_h=128, tile_w=128, n_layers=3, is_linear=True, search_dist=4)
    if jit_res is None:
        print("JIT Warp failed!")
        return
    
    diff = np.abs(aot_res.astype(np.float32) - jit_res.astype(np.float32))
    print(f"Max Warp Error: {np.max(diff)}")
    print(f"Mean Warp Error: {np.mean(diff)}")

if __name__ == "__main__":
    test_warp()
