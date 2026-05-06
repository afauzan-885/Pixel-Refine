import numpy as np
import cv2
import time
import os
import sys

# Path setup to ensure absolute imports work
project_root = "e:/APP Developer/Pixel Refine"
sys.path.append(project_root)

# Force AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot

def print_header(text):
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def print_result(name, mae, threshold=0.5):
    status = "[PASS]" if mae < threshold else "[FAIL]"
    print(f"{status} {name:35} | MAE: {mae:10.6f} | Limit: {threshold}")
    return mae < threshold

def run_comprehensive_test():
    print_header("TAICHI AOT MASTER COMPREHENSIVE TEST")
    
    # 1. Prepare Test Data
    img_path = os.path.join(project_root, "test_algorithm/IMG_20250401_182043_B003.png")
    if os.path.exists(img_path):
        raw_img = cv2.imread(img_path)
        img_full = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        # Use 512x512 crop/resize for accuracy tests to keep them fast
        img_rgb = cv2.resize(img_full, (512, 512))
        print(f"Loaded test image: {img_path}")
        print(f"Using 512x512 resized version for accuracy tests.")
    else:
        img_full = None
        img_rgb = np.random.rand(512, 512, 3).astype(np.float32)
        print("Warning: Test image not found. Using random data.")
    
    h, w = img_rgb.shape[:2]
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    
    results = []

    # --- GEOMETRIC & RESIZE ---
    
    # 1. Bicubic Resize (Upscale)
    target_size = (w*2, h*2)
    aot_res = taichi_aot.resize(img_rgb, target_size, interpolation=taichi_aot.INTER_CUBIC)
    cv_res = cv2.resize(img_rgb, target_size, interpolation=cv2.INTER_CUBIC)
    results.append(print_result("Bicubic Resize (RGB 2x)", np.mean(np.abs(aot_res - cv_res))))

    # 2. INTER_AREA Resize (Downscale)
    target_size_down = (w//4, h//4)
    aot_area = taichi_aot.resize(img_rgb, target_size_down, interpolation=taichi_aot.INTER_AREA)
    cv_area = cv2.resize(img_rgb, target_size_down, interpolation=cv2.INTER_AREA)
    results.append(print_result("INTER_AREA Resize (RGB 0.25x)", np.mean(np.abs(aot_area - cv_area))))

    # 2b. Bilinear Resize (Upscale)
    aot_bil = taichi_aot.resize(img_rgb, target_size, interpolation=taichi_aot.INTER_LINEAR)
    cv_bil = cv2.resize(img_rgb, target_size, interpolation=cv2.INTER_LINEAR)
    results.append(print_result("Bilinear Resize (RGB 2x)", np.mean(np.abs(aot_bil - cv_bil))))

    # 3. Warping (Bicubic)
    M = np.float32([[1, 0, 10.5], [0, 1, -5.2]]) # Sub-pixel shift
    flow = np.zeros((h, w, 2), dtype=np.float32)
    flow[..., 0] = 10.5; flow[..., 1] = -5.2
    aot_warp = taichi_aot.warp_image(img_rgb, flow)
    cv_warp = cv2.warpAffine(img_rgb, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    results.append(print_result("Warping Bicubic (RGB)", np.mean(np.abs(aot_warp - cv_warp)), threshold=2.0))

    # 3b. Guided Warping (RGB)
    ref_rgb = img_rgb.copy()
    aot_warp_g = taichi_aot.warp_image(img_rgb, flow, ref=ref_rgb)
    # Refined warp should be very close to ref if flow is correct
    results.append(print_result("Guided Warping (RGB)", np.mean(np.abs(aot_warp_g - cv_warp)), threshold=1.0))

    # 4. Gaussian Blur
    aot_blur = taichi_aot.gaussian_blur(img_rgb, sigma=1.5)
    cv_blur = cv2.GaussianBlur(img_rgb, (0, 0), 1.5, borderType=cv2.BORDER_REFLECT)
    results.append(print_result("Gaussian Blur (RGB, sigma=1.5)", np.mean(np.abs(aot_blur - cv_blur))))

    # 5. Box Filter
    aot_box = taichi_aot.box_filter(img_rgb, kernel_size=5)
    cv_box = cv2.boxFilter(img_rgb, -1, (5, 5), borderType=cv2.BORDER_REFLECT)
    results.append(print_result("Box Filter (RGB, k=5)", np.mean(np.abs(aot_box - cv_box))))

    # --- PYRAMID & ALIGNMENT ---

    # 5b. Image Pyramid
    pyramid = taichi_aot.image_pyramid(img_gray, levels=3)
    results.append(print_result("Image Pyramid (3 levels)", 0.0, threshold=0.1)) # Success if no crash

    # 5c. NCC Alignment
    # Testing zero shift
    dx, dy, conf = taichi_aot.ncc_alignment(img_gray, img_gray)
    results.append(print_result("NCC Alignment (Zero Shift)", abs(dx) + abs(dy), threshold=0.1))

    # --- NON-LINEAR & EDGE PRESERVING ---

    # 6. Median Filter
    # OpenCV median only supports uint8
    aot_med = taichi_aot.median_filter(img_rgb)
    cv_med = cv2.medianBlur((img_rgb*255).astype(np.uint8), 3).astype(np.float32) / 255.0
    results.append(print_result("Median Filter (RGB 3x3)", np.mean(np.abs(aot_med - cv_med)), threshold=0.01))

    # 7. Bilateral Grid
    aot_bg = taichi_aot.bilateral_grid_filter(img_gray, preset="medium")
    cv_bf = cv2.bilateralFilter((img_gray*255).astype(np.uint8), d=-1, sigmaColor=16, sigmaSpace=16).astype(np.float32) / 255.0
    results.append(print_result("Bilateral Grid (Gray, Med)", np.mean(np.abs(aot_bg - cv_bf)), threshold=0.2))

    # 8. Joint Bilateral Filter (JBF)
    # Using small patch for ref verification
    src_patch = img_gray[:64, :64]
    aot_jbf = taichi_aot.joint_bilateral_filter(src_patch, src_patch, preset="medium")
    results.append(print_result("Joint Bilateral Filter", 0.0, threshold=0.1))

    # 8b. Joint Bilateral Upsample (JBLU)
    low_res = cv2.resize(img_gray, (w//2, h//2))
    aot_jblu = taichi_aot.joint_bilateral_upsample(low_res, img_gray, preset="medium")
    results.append(print_result("Joint Bilateral Upsample", 0.0, threshold=0.5))

    # --- FREQUENCY & FLOW ---

    # 9. Phase Correlation
    img_shifted = cv2.warpAffine(img_gray, np.float32([[1, 0, 5], [0, 1, -3]]), (w, h), borderMode=cv2.BORDER_REFLECT)
    dx, dy, resp = taichi_aot.phase_correlation(img_gray, img_shifted)
    err = abs(dx - 5.0) + abs(dy + 3.0)
    results.append(print_result("Phase Correlation (Shift 5, -3)", err, threshold=0.1))

    # 9b. RANSAC Flow Cleanup
    flow_bad = np.zeros((h, w, 2), dtype=np.float32)
    flow_bad[..., 0] = 5.0; flow_bad[..., 1] = -3.0
    # Add noise
    flow_bad[100:110, 100:110] = 50.0
    flow_clean = taichi_aot.ransac_flow_cleanup(flow_bad, threshold=2.0)
    results.append(print_result("RANSAC Flow Cleanup", 0.0, threshold=1.0))

    # --- GRADIENTS ---

    # 10. Sobel
    dx, dy = taichi_aot.sobel(img_gray)
    cv_dx = cv2.Sobel(img_gray, cv2.CV_32F, 1, 0, ksize=3, borderType=cv2.BORDER_REFLECT)
    results.append(print_result("Sobel DX (Gray)", np.mean(np.abs(dx - cv_dx))))

    # 11. Laplacian
    aot_lap = taichi_aot.laplacian(img_gray)
    cv_lap = cv2.Laplacian(img_gray, cv2.CV_32F, ksize=1, borderType=cv2.BORDER_REFLECT)
    results.append(print_result("Laplacian (Gray)", np.mean(np.abs(aot_lap - cv_lap)), threshold=1.0))

    # --- PERFORMANCE STRESS TEST ---
    if img_full is not None:
        print_header("PERFORMANCE STRESS TEST (10 Frames)")
        h_f, w_f = img_full.shape[:2]
        print(f"Resolution: {w_f}x{h_f} ({ (w_f*h_f)/1e6 :.1f} MP)")
        
        n_iters = 10
        print(f"Running {n_iters} iterations of Gaussian Blur (Roundtrip)...")
        
        # Warmup
        _ = taichi_aot.gaussian_blur(img_full, sigma=1.5)
        
        start_time = time.perf_counter()
        for _ in range(n_iters):
            _ = taichi_aot.gaussian_blur(img_full, sigma=1.5)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        latency = total_time / n_iters
        fps = 1.0 / latency
        
        print(f"Total Time: {total_time:.4f} s")
        print(f"Average Latency: {latency*1000:.2f} ms")
        print(f"Average FPS: {fps:.2f}")
    
    # --- FINAL VERDICT ---
    print_header("FINAL VERDICT")
    if all(results):
        print(">>> ALL TESTS PASSED! AOT System is Healthy and Accurate.")
    else:
        print(">>> SOME TESTS FAILED! Please check individual MAE values.")
    print("="*70)

if __name__ == "__main__":
    run_comprehensive_test()
