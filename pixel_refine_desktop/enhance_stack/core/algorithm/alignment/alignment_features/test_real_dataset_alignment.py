import numpy as np
import cv2
import os
import sys
import time
import imageio
import rawpy

# Setup Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from taichi_library.taichi_aot.engine import AOTEngine
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import taichi_bridge
from taichi_library import taichi_aot

def load_image(path):
    """Load DNG or common image format. Returns float32 RGB numpy array."""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.dng':
        with rawpy.imread(path) as raw:
            rgb = raw.postprocess(
                output_bps=8,
                use_camera_wb=True,
                no_auto_bright=True,
                output_color=rawpy.ColorSpace.sRGB,
            )
        return rgb.astype(np.float32) / 255.0
    else:
        bgr = cv2.imread(path)
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

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
    
    # Configuration — use two specific DNG burst frames
    dataset_path = r"E:\APP Developer\Pixel Refine\test_algorithm"
    output_gif = os.path.join(dataset_path, "alignment_result_compute_flow_1024.gif")

    # Load Main Modules
    tcm_path = os.path.join(project_root, "taichi_library", "taichi_algorithm", "aot_tcm", "optical_flow_vulkan.tcm")
    mod = engine.load(tcm_path)

    # Use the two specific burst frames
    img_files = [
        "IMG_20260606_073156Z.dng",
        "IMG_20260606_073157Z.dng",
    ]

    for f in img_files:
        if not os.path.exists(os.path.join(dataset_path, f)):
            print(f"[ERROR] File not found: {f}")
            return
    # Load Reference Image using rawpy
    ref_path = os.path.join(dataset_path, img_files[0])
    print(f"[REF] Loading: {img_files[0]}")
    img_ref_rgb = load_image(ref_path)
    h_orig, w_orig = img_ref_rgb.shape[:2]
    print(f"[REF] Resolution: {w_orig}x{h_orig}")
    
    # Calculate aspect-ratio preserving dimensions with max_dim=1024 (divisible by 16)
    if w_orig > h_orig:
        w_work = 1024
        h_work = int(round(h_orig * (1024.0 / w_orig)))
    else:
        h_work = 1024
        w_work = int(round(w_orig * (1024.0 / h_orig)))
    w_work = (w_work // 16) * 16
    h_work = (h_work // 16) * 16
    print(f"[WORK] Work resolution: {w_work}x{h_work}")
    
    # Grayscale + Resize to work resolution using Taichi AOT
    ref_gpu = taichi_aot.upload(img_ref_rgb, force_8bit=False)
    ref_gray_gpu = taichi_aot.rgb2gray(ref_gpu)
    
    # 1024x1024 for Phase Correlation (no FFT padding)
    ref_gray_pc_gpu = taichi_aot.resize(ref_gray_gpu, (1024, 1024), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
    # Aspect-preserving work resolution for Compute Flow
    ref_gray_work_gpu = taichi_aot.resize(ref_gray_gpu, (w_work, h_work), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
    
    # Synchronize GPU to ensure all resize kernels have finished reading ref_gray_gpu
    engine.sync()
    
    ref_gpu.release()
    ref_gray_gpu.release()
    
    # Note: prepare_pyramid_aot returns l0=image_gpu as alias — do NOT release ref_gray_work_gpu
    ref_pyramid = taichi_bridge.prepare_pyramid_aot(ref_gray_work_gpu)

    frames_for_gif = []
    frames_for_gif.append((resize_with_aspect(img_ref_rgb, 512) * 255).astype(np.uint8))

    # Static Flow Buffers
    f0 = engine.allocate((h_work, w_work, 2), dtype=np.float32)
    f1 = engine.allocate((h_work//2, w_work//2, 2), dtype=np.float32)
    f2 = engine.allocate((h_work//4, w_work//4, 2), dtype=np.float32)

    for i in range(1, len(img_files)):
        fname = img_files[i]
        print(f"\n[{i}/{len(img_files)-1}] Processing Frame: {fname}")
        
        img_comp_rgb = load_image(os.path.join(dataset_path, fname))
        
        # 1. Grayscale + Resize comp using Taichi AOT
        comp_gpu = taichi_aot.upload(img_comp_rgb, force_8bit=False)
        comp_gray_gpu = taichi_aot.rgb2gray(comp_gpu)
        comp_gray_pc_gpu = taichi_aot.resize(comp_gray_gpu, (1024, 1024), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        # Synchronize GPU to ensure resize kernel has completed writing to comp_gray_pc_gpu
        engine.sync()

        comp_gpu.release()
        comp_gray_gpu.release()

        # Free VRAM before FFT
        engine.buffer_pool.clear()
        import gc
        gc.collect()

        # Run Phase Correlation on the square 1024x1024 resolution
        pc_dx, pc_dy, peak = taichi_aot.phase_correlation(ref_gray_pc_gpu, comp_gray_pc_gpu, use_hanning=True)
        print(f"  Phase Correlation (1024x1024 space): dx={pc_dx:.2f}, dy={pc_dy:.2f}, peak={peak:.3f}")
        comp_gray_pc_gpu.release()

        # Scale PC shift to full-res (PC used 1024x1024 square mapping)
        pc_dx_full = pc_dx * (float(w_orig) / 1024.0)
        pc_dy_full = pc_dy * (float(h_orig) / 1024.0)
        print(f"  Phase Correlation (full space): dx={pc_dx_full:.1f}px, dy={pc_dy_full:.1f}px")

        # Pre-warp comp_rgb at full-res (using Taichi warp_perspective translation matrix)
        H_translation = np.array([
            [1.0, 0.0, pc_dx_full],
            [0.0, 1.0, pc_dy_full],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        comp_pre_warped_rgb = taichi_aot.warp_perspective(img_comp_rgb, H_translation, return_gpu=False)

        # Grayscale + Resize pre-warped comp to work resolution using Taichi AOT
        comp_pw_gpu = taichi_aot.upload(comp_pre_warped_rgb, force_8bit=False)
        comp_pw_gray_gpu = taichi_aot.rgb2gray(comp_pw_gpu)
        comp_pw_gray_work_gpu = taichi_aot.resize(comp_pw_gray_gpu, (w_work, h_work), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        
        # Synchronize GPU to ensure resize kernel has completed writing to comp_pw_gray_work_gpu
        engine.sync()
        
        comp_pw_gpu.release()
        comp_pw_gray_gpu.release()

        comp_pyramid = taichi_bridge.prepare_pyramid_aot(comp_pw_gray_work_gpu)

        # 2. Run compute_flow on the pre-warped comp image
        t0 = time.perf_counter()
        mod.run('align_end_to_end_3layer', 
                ref_l0=ref_pyramid[0], ref_l1=ref_pyramid[1], ref_l2=ref_pyramid[2],
                comp_l0=comp_pyramid[0], comp_l1=comp_pyramid[1], comp_l2=comp_pyramid[2],
                flow_l0=f0, flow_l1=f1, flow_l2=f2,
                tile_h=16, tile_w=16, max_search_radius=12, scale=2.0, search_dist=3, downscale=2)
        engine.sync()
        t1 = time.perf_counter()
        print(f"  compute_flow @ {w_work}x{h_work}: {(t1-t0)*1000:.1f}ms")
        
        # 3. Extract and Upscale Flow to full resolution
        flow_np = f0.to_numpy()
        dx_local_work = flow_np[:, :, 0]
        dy_local_work = flow_np[:, :, 1]
        
        scale_x = float(w_orig) / float(w_work)
        scale_y = float(h_orig) / float(h_work)
        
        # Report detected global shift (median of flow field)
        median_dx = float(np.median(dx_local_work))
        median_dy = float(np.median(dy_local_work))
        print(f"  Local residual shift (work space): dx={median_dx:.2f}, dy={median_dy:.2f}")
        print(f"  Total detected shift: dx={pc_dx_full + median_dx*scale_x:.1f}px, dy={pc_dy_full + median_dy*scale_y:.1f}px")

        # Rescale flow units to full-resolution pixel space
        dx_local_full_unit = dx_local_work * scale_x
        dy_local_full_unit = dy_local_work * scale_y

        # Upscale flow map to full resolution
        dx_local_full = cv2.resize(dx_local_full_unit, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)
        dy_local_full = cv2.resize(dy_local_full_unit, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)
        
        # Total flow field is the sum of local flow and global translation
        dx_total = dx_local_full + pc_dx_full
        dy_total = dy_local_full + pc_dy_full

        # 4. Warp with taichi_aot remap (build pure translation map from flow field)
        y_grid, x_grid = np.mgrid[0:h_orig, 0:w_orig].astype(np.float32)
        map_x = x_grid + dx_total
        map_y = y_grid + dy_total
        warped_rgb = cv2.remap(
            img_comp_rgb, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
        )
        
        # Calculate SSIM
        from skimage.metrics import structural_similarity as ssim
        ssim_before = ssim(img_ref_rgb, img_comp_rgb, data_range=1.0, channel_axis=2)
        ssim_after = ssim(img_ref_rgb, warped_rgb, data_range=1.0, channel_axis=2)
        print(f"  SSIM Before: {ssim_before:.6f}")
        print(f"  SSIM After: {ssim_after:.6f}")
        
        # 4. GIF Prep
        frames_for_gif.append((resize_with_aspect(warped_rgb, 512) * 255).astype(np.uint8))
        print(f"  Frame {i} aligned OK.")

        # Cleanup comp pyramid buffers (l0, l1, l2)
        for buf in comp_pyramid:
            try:
                buf.release()
            except Exception:
                pass

    # Cleanup ref buffers
    ref_gray_pc_gpu.release()
    for buf in ref_pyramid:
        try:
            buf.release()
        except Exception:
            pass

    # Export
    print(f"\nSaving Result GIF: {output_gif}...")
    imageio.mimsave(output_gif, frames_for_gif, fps=3, loop=0)
    print(f"Done! Saved to: {output_gif}")

if __name__ == "__main__":
    test_real_dataset_alignment()

