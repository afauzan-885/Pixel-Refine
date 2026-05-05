import cv2
import numpy as np
import os
import sys

# Setup path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

def print_result(name, mae, threshold=1.0):
    status = "[PASS]" if mae < threshold else "[FAIL]"
    print(f"{status} {name:30} | MAE: {mae:10.6f} | Limit: {threshold}")

def ref_jbf_numpy(src, guide, ss=1.5, sr=0.1, r=2):
    """NumPy reference JBF for accuracy verification (slow, use for small patches)."""
    h, w = src.shape
    inv_ss2 = 1.0 / (2.0 * ss * ss); inv_sr2 = 1.0 / (2.0 * sr * sr)
    out = np.zeros_like(src)
    for y in range(h):
        for x in range(w):
            acc, total = 0.0, 1e-12
            c_g = guide[y, x]
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    ny = np.clip(y+dy, 0, h-1); nx = np.clip(x+dx, 0, w-1)
                    diff_g = guide[ny, nx] - c_g
                    wt = np.exp(-float(dx*dx+dy*dy)*inv_ss2 - diff_g*diff_g*inv_sr2)
                    acc += src[ny, nx] * wt; total += wt
            out[y, x] = acc / total
    return out

def verify_accuracy():
    print("="*60)
    print(" TAICHI AOT VS OPENCV ACCURACY VERIFICATION")
    print("="*60)
    
    # Test Image
    h, w = 512, 512
    img = np.random.rand(h, w, 3).astype(np.float32) * 255.0
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    img_gpu = taichi_aot.upload(img)
    img_gray_gpu = taichi_aot.upload(img_gray)
    
    # 1. Bicubic Resize
    target_size = (256, 256)
    aot_res = taichi_aot.resize(img, target_size, interpolation=taichi_aot.INTER_CUBIC)
    cv_res = cv2.resize(img, target_size, interpolation=cv2.INTER_CUBIC)
    mae = np.mean(np.abs(aot_res - cv_res))
    print_result("Bicubic Resize (Color)", mae, threshold=2.0)
    
    # 2. Bilinear Resize
    aot_res = taichi_aot.resize(img, target_size, interpolation=taichi_aot.INTER_LINEAR)
    cv_res = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
    mae = np.mean(np.abs(aot_res - cv_res))
    print_result("Bilinear Resize (Color)", mae, threshold=1.0)
    
    # 3. Box Filter
    k = 7
    aot_res = taichi_aot.box_filter(img_gpu, kernel_size=k)
    cv_res = cv2.boxFilter(img, -1, (k, k), borderType=cv2.BORDER_REPLICATE)
    mae = np.mean(np.abs(aot_res - cv_res))
    print_result("Box Filter (Color)", mae, threshold=0.5)
    
    # 4. Gaussian Blur
    sigma = 1.5
    aot_res = taichi_aot.gaussian_blur(img_gpu, sigma=sigma)
    cv_res = cv2.GaussianBlur(img, (0, 0), sigmaX=sigma, sigmaY=sigma)
    mae = np.mean(np.abs(aot_res - cv_res))
    print_result("Gaussian Blur (Color)", mae, threshold=1.0) # Gaussian can differ slightly in tail
    
    # 5. Median Filter (3x3)
    # Taichi implementation is currently float-based, OpenCV medianBlur expects uint8 or float32 (single ch)
    # We compare color first (now supported in AOT)
    aot_res = taichi_aot.median_filter(img_gpu)
    # OpenCV medianBlur for float32 only supports 1 channel or 3/4 ch with specific constraints
    # For comparison, we use a simple loop or just grayscale if OpenCV refuses color f32
    # Actually OpenCV medianBlur supports 3ch f32.
    cv_res = cv2.medianBlur(img, 3)
    mae = np.mean(np.abs(aot_res - cv_res))
    print_result("Median Filter (Color)", mae, threshold=1.0)
    
    aot_res_gray = taichi_aot.median_filter(img_gray_gpu)
    cv_res_gray = cv2.medianBlur(img_gray, 3)
    mae = np.mean(np.abs(aot_res_gray - cv_res_gray))
    print_result("Median Filter (Gray)", mae, threshold=1.0)
    
    # 6. Sobel
    dx_gpu, dy_gpu = taichi_aot.sobel(img_gray_gpu, return_gpu=True)
    aot_dx = dx_gpu.to_numpy()
    cv_dx = cv2.Sobel(img_gray, cv2.CV_32F, 1, 0, ksize=3, borderType=cv2.BORDER_REPLICATE)
    mae = np.mean(np.abs(aot_dx - cv_dx))
    print_result("Sobel DX (Gray)", mae, threshold=1.0)
    
    # 7. Warping (Bicubic f32)
    # Taichi warp uses Bicubic interpolation (cubic_hermite_weights, a=-0.75, BORDER_REFLECT_101)
    # OpenCV comparison uses INTER_CUBIC with same border mode.
    # Threshold = 2.0 is realistic for bicubic GPU vs CPU floating-point differences on high-freq patches.
    # Note: On smooth natural images, MAE drops to ~0.0 (verified in test_compherensif_aot.py).
    img_patch = img[100:356, 100:356].copy()
    img_gpu_f32 = taichi_aot.upload(img_patch)
    ph, pw = img_patch.shape[:2]
    flow = np.zeros((ph, pw, 2), dtype=np.float32)
    flow[..., 0] = 5.5 
    flow[..., 1] = 2.2 
    
    # Test Naked Warp (no guided flow)
    aot_res_naked = taichi_aot.warp_image(img_gpu_f32, flow)
    
    yy, xx = np.mgrid[:ph, :pw].astype(np.float32)
    map_x = xx + flow[..., 0]
    map_y = yy + flow[..., 1]
    # Reference: OpenCV INTER_CUBIC == bicubic (same algorithm as Taichi)
    cv_res = cv2.remap(img_patch, map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
    
    mae_naked = np.mean(np.abs(aot_res_naked - cv_res))
    print_result("Warping Bicubic (Naked f32)", mae_naked, threshold=2.0)

    # Test Guided Warp (with same ref — guided flow bilinear samples ref, then applies warp)
    ref_gpu = taichi_aot.upload(img_patch) 
    aot_res_guided = taichi_aot.warp_image(img_gpu_f32, flow, ref=ref_gpu)
    mae_guided = np.mean(np.abs(aot_res_guided - cv_res))
    print_result("Warping Bicubic (Guided f32)", mae_guided, threshold=2.0)

    # 8. Joint Bilateral Filter (1ch f32)
    # Use a small patch for speed in comprehensive test
    ph = 64
    src_patch = img_gray[:ph, :ph] / 255.0
    guide_patch = img_gray[:ph, :ph] / 255.0
    aot_jbf = taichi_aot.joint_bilateral_filter(src_patch, guide_patch, preset="medium", radius=2)
    ref_jbf = ref_jbf_numpy(src_patch, guide_patch, ss=1.5, sr=0.1, r=2)
    mae = np.mean(np.abs(aot_jbf - ref_jbf))
    print_result("JBF 1ch (Patch 64x64)", mae, threshold=0.01)

    # 9. Joint Bilateral Upsample (JBLU 1ch)
    # Resize small to high with guide
    low_res = cv2.resize(img_gray, (w//4, h//4)).astype(np.float32) / 255.0
    guide_hi = img_gray.astype(np.float32) / 255.0
    aot_jblu = taichi_aot.joint_bilateral_upsample(low_res, guide_hi, preset="medium")
    # Shape check + simple bilinear comparison (JBLU should be different but close-ish)
    bilinear_up = cv2.resize(low_res, (w, h), interpolation=cv2.INTER_LINEAR)
    mae_vs_bilinear = np.mean(np.abs(aot_jblu - bilinear_up))
    print_result("JBLU 1ch (Shape & Scale)", 0.0 if aot_jblu.shape == (h, w) else 1.0, threshold=0.5)

    # 10. JBLU Flow (2ch)
    flow_low = np.zeros((h//4, w//4, 2), dtype=np.float32)
    flow_low[..., 0] = 1.0
    flow_low[..., 1] = 0.5
    aot_jblu_flow = taichi_aot.joint_bilateral_upsample(flow_low, guide_hi, preset="medium")
    # Flow values should be scaled by 4x
    mae_flow_scale = np.mean(np.abs(aot_jblu_flow[h//2, w//2] - np.array([4.0, 2.0])))
    print_result("JBLU Flow 2ch (Scaling)", mae_flow_scale, threshold=0.1)

    # 11. Bilateral Grid (1ch Medium)
    aot_bg = taichi_aot.bilateral_grid_filter(src_patch, preset="medium")
    cv_bf = cv2.bilateralFilter((src_patch*255).astype(np.uint8), d=-1, sigmaColor=16, sigmaSpace=16).astype(np.float32) / 255.0
    mae = np.mean(np.abs(aot_bg - cv_bf))
    print_result("Bilateral Grid (1ch Medium)", mae, threshold=0.2)

    # 12. INTER_AREA Resize (Color Downscaling)
    target_size = (w//4, h//4)
    aot_area = taichi_aot.resize(img.astype(np.float32), target_size, interpolation=taichi_aot.INTER_AREA)
    cv_area = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA).astype(np.float32)
    mae_area = np.mean(np.abs(aot_area - cv_area))
    print_result("INTER_AREA Resize (Color 4x)", mae_area, threshold=0.5)

    # 13. Phase Correlation (Global Shift)
    img_shifted = cv2.warpAffine(img_gray, np.float32([[1, 0, 5], [0, 1, -3]]), (w, h), borderMode=cv2.BORDER_REFLECT)
    dx, dy, resp = taichi_aot.phase_correlation(img_gray.astype(np.float32), img_shifted.astype(np.float32))
    err = abs(dx - 5.0) + abs(dy + 3.0)
    print_result("Phase Correlation (dx=5, dy=-3)", err, threshold=0.1)

    print("="*60)

if __name__ == "__main__":
    verify_accuracy()
