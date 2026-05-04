import taichi as ti
import numpy as np
import time
import os
import sys
import cv2
import gc

# Path setup
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Force AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot


def print_header(text):
    print("\n" + "=" * 50)
    print(f" {text}")
    print("=" * 50)


def test_comprehensive():
    # Detect Arch
    print_header("Vulkan Device Enumeration")
    try:
        devices = taichi_aot.engine.get_vulkan_devices()
        for i, name in enumerate(devices):
            active = (
                " (ACTIVE)"
                if str(i) == os.environ.get("PIXEL_REFINE_AOT_DEVICE", "0")
                else ""
            )
            print(f"[{i}] {name}{active}")
    except:
        print("Device enumeration failed.")

    img_path = os.path.join(project_root, "test_algorithm", "IMG_20160202_015247.png")
    if not os.path.exists(img_path):
        print(f"Error: Image not found at {img_path}")
        return

    # Load and prepare image (Original Resolution 3000x3000px)
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not load image at {img_path}")
        return

    h_orig, w_orig = img.shape[:2]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    img_color = img.astype(np.float32)

    # For FFT compatibility
    img_fft_ready = cv2.resize(img_gray, (2048, 2048))

    print(f"Loaded Image: {img_path}")
    print(f"Test Resolution: {w_orig}x{h_orig}")

    n_frames = 10
    img_gpu = taichi_aot.engine.upload(img_color)
    img_gray_gpu = taichi_aot.engine.upload(img_gray)

    # 1. Bicubic (Resize)
    print_header(f"1. Bicubic (Resize) ({n_frames} frames)")
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.resize(img_gpu, (512, 512), interpolation=taichi_aot.INTER_CUBIC, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"Bicubic FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 1b. Bilinear (Resize)
    print_header(f"1b. Bilinear (Resize) ({n_frames} frames)")
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.resize(img_gpu, (512, 512), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"Bilinear FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 2. Box Filter (Optimized O(1))
    print_header(f"2. Box Filter (Integral O(1)) ({n_frames} frames)")
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.box_filter(img_gpu, kernel_size=15, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"Box Filter FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 3. Gaussian Blur
    print_header(f"3. Gaussian Blur (Separable) ({n_frames} frames)")
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.gaussian_blur(img_gpu, sigma=1.0, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"Gaussian Blur FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 4. Image Pyramid
    print_header(f"4. Image Pyramid 4 Levels ({n_frames} frames)")
    start = time.perf_counter()
    for _ in range(n_frames):
        p = taichi_aot.image_pyramid(img_gpu, levels=4, return_gpu=True)
        del p
    taichi_aot.engine.sync()
    print(f"Pyramid FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 5. FFT & IFFT
    print_header(f"5. FFT & IFFT (2048x2048) ({n_frames} frames)")
    fft_ready_gpu = taichi_aot.engine.upload(img_fft_ready)
    start = time.perf_counter()
    for _ in range(n_frames):
        complex_gpu = taichi_aot.fft2(fft_ready_gpu)
        res = taichi_aot.ifft2(complex_gpu)
        del complex_gpu, res
    taichi_aot.engine.sync()
    print(f"FFT+IFFT FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 7. Median Filter (3x3)
    print_header(f"7. Median Filter (3x3) ({n_frames} frames)")
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.median_filter(img_gray_gpu, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"Median Filter FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 8. Sobel & Laplacian
    print_header(f"8. Sobel & Laplacian ({n_frames} frames)")
    start = time.perf_counter()
    for _ in range(n_frames):
        dx, dy = taichi_aot.sobel(img_gray_gpu, return_gpu=True)
        lap = taichi_aot.laplacian(img_gray_gpu, return_gpu=True)
        del dx, dy, lap
    taichi_aot.engine.sync()
    print(f"Gradients FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 9. NCC (ZNCC Integral O(1))
    print_header(f"9. NCC (Integral O(1)) ({n_frames} frames)")
    template = img_gray[100:132, 100:132].copy()
    temp_gpu = taichi_aot.engine.upload(template)
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.zncc(img_gray_gpu, temp_gpu, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"NCC FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 10. RANSAC Flow Cleanup
    print_header(f"10. RANSAC Flow Cleanup ({n_frames} frames)")
    flow_mock = np.zeros((128, 128, 2), dtype=np.float32)
    flow_gpu = taichi_aot.engine.upload(flow_mock, is_vec2=True)
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.ransac_flow_cleanup(flow_gpu, threshold=1.0, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"RANSAC FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    # 11. Warping (Guided)
    print_header(f"11. Warping (Guided) ({n_frames} frames)")
    # Warping AOT expects i32 images (16-bit representation)
    img_i32_gpu = taichi_aot.engine.upload(img_color.astype(np.int32))
    
    # Warping AOT (Old Version) expects Scalar 3D flow (H, W, 2)
    flow_warp = np.zeros((h_orig, w_orig, 2), dtype=np.float32)
    flow_warp_gpu = taichi_aot.engine.upload(flow_warp, is_vec2=False) 
    start = time.perf_counter()
    for _ in range(n_frames):
        res = taichi_aot.warp_image(img_i32_gpu, flow_warp_gpu, ref=img_i32_gpu, return_gpu=True)
        del res
    taichi_aot.engine.sync()
    print(f"Warping FPS: {n_frames / (time.perf_counter() - start):.2f}")
    taichi_aot.engine.report_memory()
    gc.collect()

    taichi_aot.engine.report_memory()
    taichi_aot.engine.clear_pool()
    print("\n[Success] Standardized Comprehensive Test Finished!")


if __name__ == "__main__":
    test_comprehensive()
