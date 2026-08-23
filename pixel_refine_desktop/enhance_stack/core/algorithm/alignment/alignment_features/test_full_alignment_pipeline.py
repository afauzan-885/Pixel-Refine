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

from taichi_vision.taichi_aot.engine import AOTEngine
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import taichi_bridge
from taichi_vision import taichi_aot

def put_text(img, text):
    res = img.copy()
    cv2.putText(res, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 4, cv2.LINE_AA)
    return res

def test_stress_hybrid_pipeline():
    print("--- Stress Test: 5 Frame (10px - 50px) Hybrid AOT ---")
    engine = AOTEngine()
    
    img_path = os.path.join(project_root, "test_algorithm", "IMG_20160202_015247.png")
    img_raw = cv2.imread(img_path)
    h_orig, w_orig = img_raw.shape[:2]
    
    # 1. Zoom (Crop tengah untuk menghindari border hitam saat digeser 50px)
    pad = 100
    img = img_raw[pad:-pad, pad:-pad].copy()
    h, w = img.shape[:2]
    print(f"Working with zoomed image: {w}x{h}")
    
    # Load AOT Modules
    tcm_path = os.path.join(project_root, "taichi_vision", "taichi_algorithm", "aot_tcm", "optical_flow_vulkan.tcm")
    mod = engine.load(tcm_path)
    
    # Pergeseran 5 tahap
    shifts = [(10, 5), (20, 10), (30, 15), (40, 20), (50, 25)]
    
    for i, (dx_t, dy_t) in enumerate(shifts):
        print(f"\nProcessing Frame {i+1}: Shift ({dx_t}, {dy_t})")
        
        # Buat gambar bergeser
        M = np.float32([[1, 0, dx_t], [0, 1, dy_t]])
        img_shifted = cv2.warpAffine(img, M, (w, h))
        
        # A. Detection (1024x1024)
        ref_pyramid = taichi_bridge.prepare_reference_for_alignment(img.astype(np.float32)/255.0, False, 1.0, 1024, 1024)
        comp_pyramid = taichi_bridge.prepare_comparison_for_alignment(img_shifted, np.uint8, False, 1.0, 1024, 1024)
        
        f0 = engine.allocate((1024, 1024, 2), dtype=np.float32)
        f1 = engine.allocate((512, 512, 2), dtype=np.float32)
        f2 = engine.allocate((256, 256, 2), dtype=np.float32)
        
        mod.run('align_end_to_end_3layer', 
                ref_l0=ref_pyramid[0], ref_l1=ref_pyramid[1], ref_l2=ref_pyramid[2],
                comp_l0=comp_pyramid[0], comp_l1=comp_pyramid[1], comp_l2=comp_pyramid[2],
                flow_l0=f0, flow_l1=f1, flow_l2=f2,
                tile_h=16, tile_w=16, search_radius=8, scale=2.0, search_dist=2, downscale=2)
        engine.sync()
        
        # B. Upscale Flow (AOT Resize)
        flow_work_np = f0.to_numpy()
        dx_full = taichi_aot.resize(flow_work_np[:,:,0], (w, h), interpolation=taichi_aot.INTER_LINEAR)
        dy_full = taichi_aot.resize(flow_work_np[:,:,1], (w, h), interpolation=taichi_aot.INTER_LINEAR)
        
        dx_full *= (float(w) / 1024.0)
        dy_full *= (float(h) / 1024.0)
        
        # C. Warp (OpenCV Remap)
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        map_x, map_y = x + dx_full, y + dy_full
        warped_cv = cv2.remap(img_shifted, map_x, map_y, cv2.INTER_LINEAR)
        
        # D. Display Result
        s = 0.4
        vw, vh = int(w*s), int(h*s)
        ref_v = cv2.resize(put_text(img, f"REF Frame {i+1}"), (vw, vh))
        res_v = cv2.resize(put_text(warped_cv, f"ALIGNED (Shift {dx_t}px)"), (vw, vh))
        
        print(f"Displaying Frame {i+1}. Tekan tombol apa saja untuk lanjut ke frame berikutnya.")
        while True:
            cv2.imshow("STRESS TEST HYBRID", ref_v)
            if cv2.waitKey(400) != -1: break
            cv2.imshow("STRESS TEST HYBRID", res_v)
            if cv2.waitKey(400) != -1: break
            
    cv2.destroyAllWindows()
    print("\nStress Test Selesai.")

if __name__ == "__main__":
    test_stress_hybrid_pipeline()
