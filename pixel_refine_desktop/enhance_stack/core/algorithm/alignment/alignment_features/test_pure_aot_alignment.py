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

def test_pure_aot_direct():
    print("--- Verifikasi DIRECT Taichi AOT (Pure VRAM) ---")
    engine = AOTEngine()
    
    # Path TCM
    aot_dir = os.path.join(project_root, "taichi_vision", "taichi_algorithm", "aot_tcm")
    io_mod = engine.load(os.path.join(aot_dir, "common_vulkan.tcm"))
    res_mod = engine.load(os.path.join(aot_dir, "interpolation_vulkan.tcm"))
    flow_mod = engine.load(os.path.join(aot_dir, "optical_flow_vulkan.tcm"))
    warp_mod = engine.load(os.path.join(aot_dir, "geometric_vulkan.tcm"))
    
    # 1. Load & Upload
    img_path = os.path.join(project_root, "test_algorithm", "IMG_20160202_015247.png")
    img_np = cv2.imread(img_path)
    h, w = img_np.shape[:2]
    
    DX_T, DY_T = 20.0, 10.0
    M = np.float32([[1, 0, DX_T], [0, 1, DY_T]])
    img_shift_np = cv2.warpAffine(img_np, M, (w, h))
    
    # Upload sebagai i32 (AOT standard for RGB)
    ref_u8_gpu = engine.upload(img_np).cast(np.int32)
    comp_u8_gpu = engine.upload(img_shift_np).cast(np.int32)
    
    # 2. Preprocessing (100% VRAM)
    print("Step 1: Preprocessing in VRAM...")
    # RGB -> Gray f32
    ref_gray_f32 = engine.allocate((h, w), dtype=np.float32)
    comp_gray_f32 = engine.allocate((h, w), dtype=np.float32)
    
    # Note: image_io kernels expect vector view for RGB
    io_mod.run("rgb2gray_i32_to_f32", src=ref_u8_gpu.view_as_vector(True), dst=ref_gray_f32, scale=1.0/255.0)
    io_mod.run("rgb2gray_i32_to_f32", src=comp_u8_gpu.view_as_vector(True), dst=comp_gray_f32, scale=1.0/255.0)
    
    # Resize to 1024x1024 work res
    wh, ww = 1024, 1024
    ref_work = engine.allocate((wh, ww), dtype=np.float32)
    comp_work = engine.allocate((wh, ww), dtype=np.float32)
    
    res_mod.run("bilinear_resize_f32_2d", src=ref_gray_f32, dst=ref_work, h_src=h, w_src=w, h_dst=wh, w_dst=ww)
    res_mod.run("bilinear_resize_f32_2d", src=comp_gray_f32, dst=comp_work, h_src=h, w_src=w, h_dst=wh, w_dst=ww)
    
    # 3. Pyramid (GPU)
    ref_l1 = engine.allocate((wh//2, ww//2), dtype=np.float32)
    ref_l2 = engine.allocate((wh//4, ww//4), dtype=np.float32)
    comp_l1 = engine.allocate((wh//2, ww//2), dtype=np.float32)
    comp_l2 = engine.allocate((wh//4, ww//4), dtype=np.float32)
    
    res_mod.run("bilinear_resize_f32_2d", src=ref_work, dst=ref_l1, h_src=wh, w_src=ww, h_dst=wh//2, w_dst=ww//2)
    res_mod.run("bilinear_resize_f32_2d", src=ref_l1, dst=ref_l2, h_src=wh//2, w_src=ww//2, h_dst=wh//4, w_dst=ww//4)
    res_mod.run("bilinear_resize_f32_2d", src=comp_work, dst=comp_l1, h_src=wh, w_src=ww, h_dst=wh//2, w_dst=ww//2)
    res_mod.run("bilinear_resize_f32_2d", src=comp_l1, dst=comp_l2, h_src=wh//2, w_src=ww//2, h_dst=wh//4, w_dst=ww//4)
    
    # 4. Alignment
    print("Step 2: Alignment OBG...")
    f0 = engine.allocate((wh, ww, 2), dtype=np.float32)
    f1 = engine.allocate((wh//2, ww//2, 2), dtype=np.float32)
    f2 = engine.allocate((wh//4, ww//4, 2), dtype=np.float32)
    
    flow_mod.run('align_end_to_end_3layer', 
                 ref_l0=ref_work, ref_l1=ref_l1, ref_l2=ref_l2,
                 comp_l0=comp_work, comp_l1=comp_l1, comp_l2=comp_l2,
                 flow_l0=f0, flow_l1=f1, flow_l2=f2,
                 tile_h=16, tile_w=16, max_search_radius=8, scale=2.0, search_dist=2, downscale=2)
    engine.sync()
    
    # 5. Full Res Scaling (Manual Magnitude in NumPy for simplicity, but resize in GPU)
    print("Step 3: Scaling Flow...")
    flow_full_gpu = engine.allocate((h, w, 2), dtype=np.float32)
    res_mod.run("bilinear_resize_f32_3d", src=f0.view_as_vector(True), dst=flow_full_gpu.view_as_vector(True), 
                h_src=wh, w_src=ww, h_dst=h, w_dst=w)
    
    # Magnitude scaling
    flow_np = flow_full_gpu.to_numpy()
    flow_np[:,:,0] *= (w / ww)
    flow_np[:,:,1] *= (h / wh)
    flow_final_gpu = engine.upload(-flow_np) # Invert to align back
    
    # 6. Warping
    print("Step 4: Warping (Pure VRAM)...")
    warped_u8_gpu = engine.allocate((h, w, 3), dtype=np.int32, is_vector=True, vector_dim=3)
    warp_mod.run("warp_naked_i32_3ch", src=comp_u8_gpu.view_as_vector(True), flow=flow_final_gpu, dst=warped_u8_gpu)
    
    # 7. View
    res_np = warped_u8_gpu.to_numpy().astype(np.uint8)
    
    s = 0.4
    vw, vh = int(w*s), int(h*s)
    ref_v = cv2.resize(img_np, (vw, vh))
    res_v = cv2.resize(res_np, (vw, vh))
    
    print("\nVisualisasi 40% (Pure VRAM Pipeline):")
    while True:
        cv2.imshow("PURE VRAM VERIFY", ref_v)
        if cv2.waitKey(400) == 27: break
        cv2.imshow("PURE VRAM VERIFY", res_v)
        if cv2.waitKey(400) == 27: break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_pure_aot_direct()
