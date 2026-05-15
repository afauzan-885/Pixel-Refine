import taichi as ti
import numpy as np
import cv2
import os
import sys
import time
import imageio

# Setup Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import AOTEngine
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import taichi_bridge
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

def resize_with_aspect(img, max_size=1024):
    h, w = img.shape[:2]
    if w > h:
        new_w = max_size
        new_h = int(h * (max_size / w))
    else:
        new_h = max_size
        new_w = int(w * (max_size / h))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

def test_real_dataset_alignment():
    print("--- Pure AOT Alignment (No RANSAC, No Median) ---")
    engine = AOTEngine()
    
    # Configuration
    dataset_path = r"E:\APP Developer\Pixel Refine\test_algorithm\align_image\Folder Baru"
    output_gif = os.path.join(dataset_path, "alignment_result_pure_1024.gif")
    
    # Load Main Modules
    tcm_path = os.path.join(project_root, "pixel_refine_desktop", "ui", "data", "aot_assets", "compute_flow_vulkan.tcm")
    mod = engine.load(tcm_path)

    # Scan for images
    valid_exts = (".jpg", ".jpeg", ".png")
    img_files = sorted([f for f in os.listdir(dataset_path) if f.lower().endswith(valid_exts)])
    
    if len(img_files) < 2: return

    # Load Reference Image
    ref_path = os.path.join(dataset_path, img_files[0])
    img_ref = cv2.imread(ref_path)
    h_orig, w_orig = img_ref.shape[:2]
    
    # Pre-convert to Gray on CPU and Resize to 1024x1024 for alignment detection
    ref_gray_cpu = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    ref_gray_1024 = cv2.resize(ref_gray_cpu, (1024, 1024), interpolation=cv2.INTER_LINEAR)
    ref_pyramid = taichi_bridge.prepare_pyramid_aot(taichi_aot.upload(ref_gray_1024))
    
    frames_for_gif = []
    frames_for_gif.append(cv2.cvtColor(resize_with_aspect(img_ref, 1024), cv2.COLOR_BGR2RGB))

    # Static Flow Buffers (Using 3D Array shape for kernel compatibility)
    wh, ww = 1024, 1024
    f0 = engine.allocate((wh, ww, 2), dtype=np.float32)
    f1 = engine.allocate((wh//2, ww//2, 2), dtype=np.float32)
    f2 = engine.allocate((wh//4, ww//4, 2), dtype=np.float32)

    for i in range(1, len(img_files)):
        fname = img_files[i]
        print(f"[{i}/{len(img_files)-1}] Processing Frame: {fname}")
        
        img_comp = cv2.imread(os.path.join(dataset_path, fname))
        
        # Pre-convert to Gray on CPU and Resize to 1024x1024
        comp_gray_cpu = cv2.cvtColor(img_comp, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        comp_gray_1024 = cv2.resize(comp_gray_cpu, (1024, 1024), interpolation=cv2.INTER_LINEAR)
        comp_pyramid = taichi_bridge.prepare_pyramid_aot(taichi_aot.upload(comp_gray_1024))
        
        # 1. Direct AOT Run (Hierarchical Alignment)
        mod.run('align_end_to_end_3layer', 
                ref_l0=ref_pyramid[0], ref_l1=ref_pyramid[1], ref_l2=ref_pyramid[2],
                comp_l0=comp_pyramid[0], comp_l1=comp_pyramid[1], comp_l2=comp_pyramid[2],
                flow_l0=f0, flow_l1=f1, flow_l2=f2,
                tile_h=16, tile_w=16, search_radius=12, scale=2.0, search_dist=3, downscale=2)
        engine.sync()
        
        # 2. Extract and Upscale Flow
        flow_np = f0.to_numpy()
        dx_full = cv2.resize(flow_np[:,:,0], (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)
        dy_full = cv2.resize(flow_np[:,:,1], (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)
        
        # Rescale units to full-resolution pixels
        dx_full *= (float(w_orig) / 1024.0)
        dy_full *= (float(h_orig) / 1024.0)
        
        # 3. Warp with OpenCV Remap
        y, x = np.mgrid[0:h_orig, 0:w_orig].astype(np.float32)
        map_x, map_y = x + dx_full, y + dy_full
        warped = cv2.remap(img_comp, map_x, map_y, cv2.INTER_LINEAR)
        
        # 4. GIF Prep
        frames_for_gif.append(cv2.cvtColor(resize_with_aspect(warped, 1024), cv2.COLOR_BGR2RGB))

    # Export
    print(f"Saving Result GIF: {output_gif}...")
    imageio.mimsave(output_gif, frames_for_gif, fps=5, loop=0)
    print("Done! Check the result in 'Folder Baru'.")

if __name__ == "__main__":
    test_real_dataset_alignment()
