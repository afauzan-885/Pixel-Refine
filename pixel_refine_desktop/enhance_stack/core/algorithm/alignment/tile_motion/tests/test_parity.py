import os
import sys
import numpy as np
import cv2

# Setup PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# We will run both JIT and AOT in the same script by using sub-processes or by importing
# and modifying os.environ dynamically. But since Taichi JIT and AOT use different imports,
# we can just run JIT, save results, then run AOT, save results, and compare.

def run_jit():
    os.environ["AOT_MODE"] = "0"
    import taichi as ti
    ti.init(arch=ti.vulkan, offline_cache=False)
    
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_block_correlation import compute_block_correlation
    
    # Synthetic inputs
    np.random.seed(42)
    ref = np.random.rand(192, 256).astype(np.float32)
    # Shift comp by dx=3.5, dy=-2.2
    M = np.float32([[1, 0, 3.5], [0, 1, -2.2]])
    comp = cv2.warpAffine(ref, M, (256, 192), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    
    grid_flow = compute_block_correlation(ref, comp, tile_h=16, tile_w=16, n_layers=2)
    flow_np = grid_flow.to_numpy()
    print("JIT flow median:", np.median(flow_np[..., 0]), np.median(flow_np[..., 1]))
    np.save("jit_flow.npy", flow_np)
    ti.reset()

def run_aot():
    os.environ["AOT_MODE"] = "1"
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_block_correlation import compute_block_correlation
    
    # Synthetic inputs
    np.random.seed(42)
    ref = np.random.rand(192, 256).astype(np.float32)
    # Shift comp by dx=3.5, dy=-2.2
    M = np.float32([[1, 0, 3.5], [0, 1, -2.2]])
    comp = cv2.warpAffine(ref, M, (256, 192), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    
    ref_gpu = taichi_aot.upload(ref)
    comp_gpu = taichi_aot.upload(comp)
    
    grid_flow = compute_block_correlation(ref_gpu, comp_gpu, tile_h=16, tile_w=16, n_layers=2)
    flow_np = grid_flow.to_numpy()
    print("AOT flow median:", np.median(flow_np[..., 0]), np.median(flow_np[..., 1]))
    np.save("aot_flow.npy", flow_np)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "aot":
        run_aot()
    else:
        run_jit()
