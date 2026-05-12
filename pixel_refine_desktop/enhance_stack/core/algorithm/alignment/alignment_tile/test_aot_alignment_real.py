import taichi as ti
import numpy as np
import cv2
import os
import sys
import time

# Setup Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot import AOTEngine

def run_test_case(engine, module, img_path, shift_y, shift_x, case_name):
    # 1. Load Image using Native Engine (Direct to VRAM)
    # Note: engine.imread likely returns uint8 or uint16. 
    # Our TCM expects f32 (normalized). We might need to cast.
    ref_gpu_raw = engine.imread(img_path)
    
    # 2. Basic Metadata
    h, w = ref_gpu_raw.shape[0], ref_gpu_raw.shape[1]
    
    # Since we can't easily warp in VRAM without a kernel, 
    # let's download, shift, and re-upload for this test
    ref_img = ref_gpu_raw.to_numpy().astype(np.float32)
    if ref_img.ndim == 3: ref_img = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    ref_img /= (255.0 if ref_img.max() <= 255.0 else 65535.0)
    
    h_tile, w_tile = (h // 16) * 16, (w // 16) * 16
    ref_img = ref_img[:h_tile, :w_tile]
    
    # Create shifted comp
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    comp_img = cv2.warpAffine(ref_img, M, (w_tile, h_tile), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    
    # Prepare Pyramids
    ref_l1 = cv2.resize(ref_img, (w_tile//2, h_tile//2), interpolation=cv2.INTER_AREA)
    ref_l2 = cv2.resize(ref_img, (w_tile//4, h_tile//4), interpolation=cv2.INTER_AREA)
    comp_l1 = cv2.resize(comp_img, (w_tile//2, h_tile//2), interpolation=cv2.INTER_AREA)
    comp_l2 = cv2.resize(comp_img, (w_tile//4, h_tile//4), interpolation=cv2.INTER_AREA)
    
    # Upload all to GPU
    buffers = {
        'ref_l0': engine.upload(ref_img),
        'ref_l1': engine.upload(ref_l1),
        'ref_l2': engine.upload(ref_l2),
        'comp_l0': engine.upload(comp_img),
        'comp_l1': engine.upload(comp_l1),
        'comp_l2': engine.upload(comp_l2),
        'flow_l0': engine.allocate((h_tile, w_tile, 2), dtype=np.float32, is_vector=False),
        'flow_l1': engine.allocate((h_tile//2, w_tile//2, 2), dtype=np.float32, is_vector=False),
        'flow_l2': engine.allocate((h_tile//4, w_tile//4, 2), dtype=np.float32, is_vector=False),
        'tile_h': 16,
        'tile_w': 16,
        'search_radius': 8,
        'scale': 2.0,
        'search_dist': 2,
        'downscale': 2
    }
    
    # 4. Run AOT Graph
    # Run once to warm up (should be fast in AOT, but let's be sure)
    module.run('align_end_to_end_3layer', **buffers)
    engine.sync()
    
    start_time = time.perf_counter()
    module.run('align_end_to_end_3layer', **buffers)
    engine.sync()
    end_time = time.perf_counter()
    
    # 5. Analyze
    final_flow = buffers['flow_l0'].to_numpy()
    center_y, center_x = h_tile // 2, w_tile // 2
    samples = final_flow[h_tile//4:3*h_tile//4:50, w_tile//4:3*w_tile//4:50]
    detected = np.median(samples.reshape(-1, 2), axis=0)
    
    err_x, err_y = abs(shift_x - detected[0]), abs(shift_y - detected[1])
    
    print(f"\n[Case: {case_name}]")
    print(f"  Target:   DX={shift_x:6.2f}, DY={shift_y:6.2f}")
    print(f"  Detected: DX={detected[0]:6.2f}, DY={detected[1]:6.2f}")
    print(f"  Error:    X={err_x:7.4f}, Y={err_y:7.4f}")
    print(f"  GPU Time: {(end_time - start_time)*1000:.2f} ms")
    
    return err_x < 0.5 and err_y < 0.5

def main():
    img_path = os.path.join(project_root, "test_algorithm", "IMG_20160202_015247.png")
    if not os.path.exists(img_path): return

    engine = AOTEngine()
    tcm_path = os.path.join(project_root, "pixel_refine_desktop", "ui", "data", "aot_assets", "compute_flow_vulkan.tcm")
    module = engine.load(tcm_path)

    test_cases = [
        (1.2, -0.8, "Little Shift"),
        (6.0, 4.0, "Normal Shift"),
        (15.0, -12.0, "Large Shift")
    ]

    for sy, sx, name in test_cases:
        run_test_case(engine, module, img_path, sy, sx, name)

if __name__ == "__main__":
    main()
