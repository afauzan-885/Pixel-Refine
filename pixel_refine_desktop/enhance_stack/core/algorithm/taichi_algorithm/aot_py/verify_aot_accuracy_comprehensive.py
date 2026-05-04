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
    img_u8 = img.astype(np.uint8)
    aot_res = taichi_aot.median_filter(img_gpu)
    # OpenCV medianBlur for float32 only supports 1 channel or 3/4 ch with specific constraints
    # We compare grayscale for simplicity in verification
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
    
    # 7. Warping (Naked i32)
    # Note: AOT Warping expects i32 images for now in our current tcm.
    img_i32 = img.astype(np.int32)
    img_i32_gpu = taichi_aot.upload(img_i32)
    flow = np.zeros((h, w, 2), dtype=np.float32)
    flow[..., 0] = 5.5 # Shift 5.5 pixels right
    flow[..., 1] = 2.2 # Shift 2.2 pixels down
    
    aot_res = taichi_aot.warp_image(img_i32_gpu, flow)
    
    # OpenCV remap for comparison
    # In Taichi: dest[y, x] = src[y + flow_y, x + flow_x]
    # In OpenCV: dest[y, x] = src[map_y[y,x], map_x[y,x]]
    # So map_x = x + flow_x, map_y = y + flow_y
    yy, xx = np.mgrid[:h, :w].astype(np.float32)
    map_x = xx + flow[..., 0]
    map_y = yy + flow[..., 1]
    cv_res = cv2.remap(img_i32.astype(np.float32), map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.int32)
    
    mae = np.mean(np.abs(aot_res - cv_res))
    print_result("Warping (Naked i32)", mae, threshold=2.0)

    print("="*60)

if __name__ == "__main__":
    verify_accuracy()
