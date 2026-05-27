import os
import cv2
import numpy as np
import taichi as ti
import math

# Initialize Taichi on GPU
ti.init(arch=ti.gpu)

print("=== Taichi GPU Image Enhancement Calibration Tool ===")
print("Adjust the sliders to calibrate the parameters.")
print("Press 'S' to save parameters and the side-by-side comparison.")
print("Press 'Q' or 'ESC' to exit.")

# 1. Load test image
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(project_root, "test_algorithm/IMG_20250401_182043_B003.png")

if not os.path.exists(img_path):
    # Fallback to standard check path
    img_path = "../test_algorithm/IMG_20250401_182043_B003.png"

if os.path.exists(img_path):
    raw_img = cv2.imread(img_path)
    # Resize to 800px width for visual clarity and comfortable UI size
    h_orig, w_orig = raw_img.shape[:2]
    w_target = 800
    h_target = int(h_orig * (w_target / w_orig))
    raw_resized = cv2.resize(raw_img, (w_target, h_target))
    # Convert to grayscale and normalize to float32 [0, 1]
    img_gray = cv2.cvtColor(raw_resized, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    print(f"Loaded test image: {img_path} (Resized to {w_target}x{h_target})")
else:
    # Generate synthetic textured test pattern if image is missing
    w_target, h_target = 800, 800
    grid_y, grid_x = np.mgrid[0:h_target, 0:w_target]
    img_gray = (0.5 + 0.3 * np.sin(grid_x / 10.0) * np.cos(grid_y / 10.0)).astype(np.float32)
    img_gray += 0.1 * np.random.randn(h_target, w_target).astype(np.float32)
    img_gray = np.clip(img_gray, 0.0, 1.0)
    print("Warning: Standard test image not found. Using synthetic pattern.")

h, w = img_gray.shape

# 2. Allocate Taichi ndarrays on GPU VRAM
src_gpu      = ti.ndarray(dtype=ti.f32, shape=(h, w))
tmp_gpu      = ti.ndarray(dtype=ti.f32, shape=(h, w))  # for separable blur pass
blur_gpu     = ti.ndarray(dtype=ti.f32, shape=(h, w))
lut_gpu      = ti.ndarray(dtype=ti.f32, shape=(256,))
dst_gpu      = ti.ndarray(dtype=ti.f32, shape=(h, w))
weights_gpu  = ti.ndarray(dtype=ti.f32, shape=(32,))

# Upload source image to GPU
src_gpu.from_numpy(img_gray)

# 3. Define GPU-accelerated Taichi Kernels (JIT Compilation)

@ti.kernel
def gaussian_blur_x_kernel(
    src: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    weights: ti.types.ndarray(),
    radius: ti.i32
):
    for r, c in ti.ndrange(h, w):
        val = 0.0
        weight_sum = 0.0
        for i in range(-radius, radius + 1):
            sample_c = c + i
            # Reflect boundary condition
            if sample_c < 0:
                sample_c = -sample_c
            elif sample_c >= w:
                sample_c = 2 * w - 2 - sample_c
            
            weight = weights[i + radius]
            val += src[r, sample_c] * weight
            weight_sum += weight
        dst[r, c] = val / weight_sum

@ti.kernel
def gaussian_blur_y_kernel(
    src: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    weights: ti.types.ndarray(),
    radius: ti.i32
):
    for r, c in ti.ndrange(h, w):
        val = 0.0
        weight_sum = 0.0
        for i in range(-radius, radius + 1):
            sample_r = r + i
            # Reflect boundary condition
            if sample_r < 0:
                sample_r = -sample_r
            elif sample_r >= h:
                sample_r = 2 * h - 2 - sample_r
            
            weight = weights[i + radius]
            val += src[sample_r, c] * weight
            weight_sum += weight
        dst[r, c] = val / weight_sum

@ti.kernel
def enhance_grayscale_kernel(
    src: ti.types.ndarray(),
    blur: ti.types.ndarray(),
    lut: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    micro_contrast: ti.f32,
    clarity: ti.f32,
    h: ti.i32,
    w: ti.i32
):
    for r, c in ti.ndrange(h, w):
        val = src[r, c]
        b_val = blur[r, c]
        
        # 1. Contrast-Aware Halo-Free Detail Shaping (Soft limiter)
        diff = val - b_val
        shaped_diff = diff / (1.0 + ti.abs(diff) * 5.0)  # 5.0 halo suppression coefficient
        
        # 2. Midtone-targeted local contrast (Clarity bell curve: peaks at 0.5, zero at 0 and 1)
        midtone_mask = 16.0 * val * val * (1.0 - val) * (1.0 - val)
        
        # Combine Micro-contrast (high frequencies) and Clarity (midtones local contrast)
        enhanced = val + shaped_diff * micro_contrast + shaped_diff * clarity * midtone_mask
        
        # 3. Global contrast enhancement (1D LUT lookup)
        lut_idx = ti.cast(ti.math.clamp(enhanced * 255.0, 0.0, 255.0), ti.i32)
        dst[r, c] = lut[lut_idx]

# Helper to compute Gaussian weights
def get_gaussian_weights(sigma, radius):
    size = 2 * radius + 1
    weights = np.zeros(size, dtype=np.float32)
    two_sigma_sq = 2.0 * sigma * sigma
    const = 1.0 / (np.sqrt(2.0 * np.pi) * sigma)
    
    for i in range(size):
        x = i - radius
        weights[i] = const * np.exp(-(x * x) / two_sigma_sq)
        
    return weights / np.sum(weights)

# 4. Callback logic for interactive GUI parameters
def run_enhancement(params):
    # Unpack parameters
    micro_c    = params["micro_c"]
    clarity    = params["clarity"]
    sigma      = params["sigma"]
    contrast   = params["contrast"]
    brightness = params["brightness"]
    gamma      = params["gamma"]
    
    # A. Generate 1D LUT Curve on CPU
    lut_np = np.zeros(256, dtype=np.float32)
    for i in range(256):
        val = (i / 255.0) ** gamma * contrast + brightness
        lut_np[i] = np.clip(val, 0.0, 1.0)
    
    # Upload LUT to GPU
    lut_gpu.from_numpy(lut_np)
    
    # B. Compute Gaussian weights and upload to GPU
    radius = int(np.ceil(3.0 * sigma))
    radius = max(1, min(15, radius))  # cap radius to 15 for safety
    weights_np = get_gaussian_weights(sigma, radius)
    weights_padded = np.zeros(32, dtype=np.float32)
    weights_padded[:len(weights_np)] = weights_np
    weights_gpu.from_numpy(weights_padded)
    
    # C. Execute separable Gaussian blur on GPU
    gaussian_blur_x_kernel(src_gpu, tmp_gpu, h, w, weights_gpu, radius)
    gaussian_blur_y_kernel(tmp_gpu, blur_gpu, h, w, weights_gpu, radius)
    
    # D. Execute fused contrast & detail enhancement kernel on GPU
    enhance_grayscale_kernel(src_gpu, blur_gpu, lut_gpu, dst_gpu, micro_c, clarity, h, w)
    
    # E. Download result from VRAM to CPU for visualization
    res_img = dst_gpu.to_numpy()
    return res_img

# 5. Setup OpenCV Window & GUI Trackbars
win_name = "Taichi GPU Image Enhancement Calibration"
has_display = True

# Detect if we can create a window
try:
    cv2.namedWindow(win_name, cv2.WINDOW_AUTOSIZE)
    # Test highgui window presence
    cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE)
except Exception:
    has_display = False
    print("\n[Warning] No active display screen or GUI context detected. Running in Headless Simulation Mode...")

# Default baseline parameters
current_params = {
    "micro_c": 1.5,
    "clarity": 1.2,
    "sigma": 1.5,
    "contrast": 1.0,
    "brightness": 0.0,
    "gamma": 1.0
}

def on_trackbar_change(*_):
    pass

if has_display:
    # Create Trackbars with integer mapping
    # Micro-Contrast: 0 - 500 (maps to 0.0 - 5.0)
    cv2.createTrackbar("Micro-Contrast", win_name, int(current_params["micro_c"] * 100), 500, on_trackbar_change)
    # Clarity: 0 - 400 (maps to 0.0 - 4.0)
    cv2.createTrackbar("Clarity (Clarity)", win_name, int(current_params["clarity"] * 100), 400, on_trackbar_change)
    # Sigma: 5 - 50 (maps to 0.5 - 5.0)
    cv2.createTrackbar("Sigma (Detail Scale)", win_name, int(current_params["sigma"] * 10), 50, on_trackbar_change)
    # Contrast: 50 - 300 (maps to 0.5 - 3.0)
    cv2.createTrackbar("Global Contrast", win_name, int(current_params["contrast"] * 100), 300, on_trackbar_change)
    # Brightness: 0 - 100 (maps to -0.5 - 0.5)
    cv2.createTrackbar("Brightness Offset", win_name, int((current_params["brightness"] + 0.5) * 100), 100, on_trackbar_change)
    # Gamma: 20 - 300 (maps to 0.2 - 3.0)
    cv2.createTrackbar("Gamma Curve", win_name, int(current_params["gamma"] * 100), 300, on_trackbar_change)

# Main interactive loop
try:
    if has_display:
        while True:
            # Retrieve trackbar values
            mc_val     = cv2.getTrackbarPos("Micro-Contrast", win_name) / 100.0
            clarity_val = cv2.getTrackbarPos("Clarity (Clarity)", win_name) / 100.0
            sig_val    = cv2.getTrackbarPos("Sigma (Detail Scale)", win_name) / 10.0
            sig_val    = max(0.5, sig_val)  # prevent sigma = 0
            cont_val   = cv2.getTrackbarPos("Global Contrast", win_name) / 100.0
            bright_val = (cv2.getTrackbarPos("Brightness Offset", win_name) / 100.0) - 0.5
            gam_val    = cv2.getTrackbarPos("Gamma Curve", win_name) / 100.0
            gam_val    = max(0.1, gam_val)  # prevent gamma = 0
            
            # Pack active parameters
            current_params = {
                "micro_c": mc_val,
                "clarity": clarity_val,
                "sigma": sig_val,
                "contrast": cont_val,
                "brightness": bright_val,
                "gamma": gam_val
            }
            
            # Run enhancement on GPU
            enhanced_float = run_enhancement(current_params)
            
            # Convert back to uint8 for rendering
            src_u8 = (img_gray * 255.0).astype(np.uint8)
            enhanced_u8 = (enhanced_float * 255.0).astype(np.uint8)
            
            # Create a side-by-side comparison image
            comparison = np.hstack((src_u8, enhanced_u8))
            
            # Draw status overlay
            overlay = comparison.copy()
            cv2.putText(overlay, "ORIGINAL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,), 2)
            cv2.putText(overlay, "ENHANCED (Taichi GPU)", (w + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,), 2)
            
            text_status = f"Micro-C: {mc_val:.2f} | Clarity: {clarity_val:.2f} | Sigma: {sig_val:.1f} | Contrast: {cont_val:.2f} | Bright: {bright_val:.2f} | Gamma: {gam_val:.2f}"
            cv2.putText(overlay, text_status, (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,), 1)
            
            # Show image
            cv2.imshow(win_name, overlay)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q') or key == 27:  # Q or ESC to exit
                break
            elif key == ord('s'):  # S to save results
                # Save final values
                save_path_img = os.path.join(project_root, "scratch/enhanced_comparison.png")
                cv2.imwrite(save_path_img, comparison)
                
                save_path_txt = os.path.join(project_root, "scratch/enhancement_params.txt")
                with open(save_path_txt, "w") as f:
                    f.write(f"=== CALIBRATED PARAMETERS ===\n")
                    f.write(f"Micro-Contrast (mc): {mc_val:.4f}\n")
                    f.write(f"Clarity (clarity): {clarity_val:.4f}\n")
                    f.write(f"Sigma (sigma): {sig_val:.4f}\n")
                    f.write(f"Global Contrast (contrast): {cont_val:.4f}\n")
                    f.write(f"Brightness (brightness): {bright_val:.4f}\n")
                    f.write(f"Gamma (gamma): {gam_val:.4f}\n")
                
                print(f"\n[Saved] Parameters saved successfully to: {save_path_txt}")
                print(f"[Saved] Comparison image saved to: {save_path_img}")
    else:
        # Headless simulation mode
        mc_val     = current_params["micro_c"]
        clarity_val = current_params["clarity"]
        sig_val    = current_params["sigma"]
        cont_val   = current_params["contrast"]
        bright_val = current_params["brightness"]
        gam_val    = current_params["gamma"]
        
        print(f"[Sim] Starting baseline GPU calculation...")
        enhanced_float = run_enhancement(current_params)
        
        src_u8 = (img_gray * 255.0).astype(np.uint8)
        enhanced_u8 = (enhanced_float * 255.0).astype(np.uint8)
        comparison = np.hstack((src_u8, enhanced_u8))
        
        # Save comparison outputs
        save_path_img = os.path.join(project_root, "scratch/enhanced_comparison.png")
        cv2.imwrite(save_path_img, comparison)
        
        save_path_txt = os.path.join(project_root, "scratch/enhancement_params.txt")
        with open(save_path_txt, "w") as f:
            f.write(f"=== CALIBRATED PARAMETERS (HEADLESS) ===\n")
            f.write(f"Micro-Contrast (mc): {mc_val:.4f}\n")
            f.write(f"Clarity (clarity): {clarity_val:.4f}\n")
            f.write(f"Sigma (sigma): {sig_val:.4f}\n")
            f.write(f"Global Contrast (contrast): {cont_val:.4f}\n")
            f.write(f"Brightness (brightness): {bright_val:.4f}\n")
            f.write(f"Gamma (gamma): {gam_val:.4f}\n")
            
        print(f"[Saved] Headless simulation completed successfully!")
        print(f"[Saved] Output saved to: {save_path_txt}")
        print(f"[Saved] Visual saved to: {save_path_img}")
            
finally:
    if has_display:
        cv2.destroyAllWindows()
    print("Interactive Calibration Terminated Cleanly.")
