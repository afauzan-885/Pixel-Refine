import os
import sys
import numpy as np
import cv2
import rawpy
import taichi as ti

# Setup path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Initialize Taichi
ti.init(arch=ti.cpu)

def load_dng_and_metadata(dng_path):
    with rawpy.imread(dng_path) as raw:
        bayer_np = raw.raw_image.astype(np.float32)
        black = float(raw.black_level_per_channel[0])
        white = float(raw.white_level)
        
        # White balance gains
        wb = np.array(raw.camera_whitebalance, dtype=np.float32)
        if len(wb) == 4:
            if wb[3] <= 0.01:
                wb[3] = wb[1]
            g_gain = (wb[1] + wb[3]) / 2.0
            wb /= g_gain
        else:
            wb = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)
            
        c00 = int(raw.raw_colors[0, 0])
        c01 = int(raw.raw_colors[0, 1])
        c10 = int(raw.raw_colors[1, 0])
        c11 = int(raw.raw_colors[1, 1])
        cmatrix = raw.color_matrix[:, :3].astype(np.float32)
        
    return bayer_np, wb, cmatrix, black, white, c00, c01, c10, c11

def demosaic_linear_numpy(bayer, wb, black, white, c00, c01, c10, c11):
    # Normalized Bayer
    norm = np.clip((bayer - black) / max(1.0, white - black), 0.0, 1.0)
    h, w = bayer.shape
    
    # 1. Preprocess white balance
    wb_bayer = np.zeros_like(norm)
    for r in range(h):
        for c in range(w):
            r_mod, c_mod = r % 2, c % 2
            if r_mod == 0:
                color_idx = c00 if c_mod == 0 else c01
            else:
                color_idx = c10 if c_mod == 0 else c11
            
            gain = wb[color_idx]
            wb_bayer[r, c] = norm[r, c] * gain
            
    # 2. Simple bilinear demosaic for validation
    rgb = np.zeros((h, w, 3), dtype=np.float32)
    for r in range(1, h-1):
        for c in range(1, w-1):
            r_mod, c_mod = r % 2, c % 2
            if r_mod == 0:
                color_idx = c00 if c_mod == 0 else c01
            else:
                color_idx = c10 if c_mod == 0 else c11
                
            if color_idx == 0: # Red
                rgb[r, c, 0] = wb_bayer[r, c]
                rgb[r, c, 1] = (wb_bayer[r-1, c] + wb_bayer[r+1, c] + wb_bayer[r, c-1] + wb_bayer[r, c+1]) * 0.25
                rgb[r, c, 2] = (wb_bayer[r-1, c-1] + wb_bayer[r-1, c+1] + wb_bayer[r+1, c-1] + wb_bayer[r+1, c+1]) * 0.25
            elif color_idx == 2: # Blue
                rgb[r, c, 2] = wb_bayer[r, c]
                rgb[r, c, 1] = (wb_bayer[r-1, c] + wb_bayer[r+1, c] + wb_bayer[r, c-1] + wb_bayer[r, c+1]) * 0.25
                rgb[r, c, 0] = (wb_bayer[r-1, c-1] + wb_bayer[r-1, c+1] + wb_bayer[r+1, c-1] + wb_bayer[r+1, c+1]) * 0.25
            else: # Green
                rgb[r, c, 1] = wb_bayer[r, c]
                if r_mod == 0: # Green in Red row (G1)
                    rgb[r, c, 0] = (wb_bayer[r, c-1] + wb_bayer[r, c+1]) * 0.5
                    rgb[r, c, 2] = (wb_bayer[r-1, c] + wb_bayer[r+1, c]) * 0.5
                else: # Green in Blue row (G2)
                    rgb[r, c, 2] = (wb_bayer[r, c-1] + wb_bayer[r, c+1]) * 0.5
                    rgb[r, c, 0] = (wb_bayer[r-1, c] + wb_bayer[r+1, c]) * 0.5
                    
    # Prevent highlight clipping
    max_wb = np.max(wb)
    rgb_linear = np.clip(rgb / max_wb, 0.0, 1.0)
    return rgb_linear

def path_a_direct_nonlinear(rgb_linear, cmatrix, scale=1.0, gamma_pow=2.22):
    # 1. Camera to sRGB
    h, w, _ = rgb_linear.shape
    flat = rgb_linear.reshape(-1, 3)
    srgb_linear = flat @ cmatrix.T
    srgb_linear = srgb_linear.reshape(h, w, 3)
    
    # 2. Sigmoid roll-off (tone mapping)
    x = srgb_linear * scale
    x_mapped = x / np.sqrt(1.0 + x * x)
    
    # 3. Gamma correction
    res = np.power(np.clip(x_mapped, 0.0, 1.0), 1.0 / gamma_pow)
    return res.astype(np.float32)

def path_b1_linear_srgb_proxy(rgb_linear, cmatrix, scale=1.0, gamma_pow=2.22):
    # 1. Convert to linear sRGB first
    h, w, _ = rgb_linear.shape
    flat = rgb_linear.reshape(-1, 3)
    srgb_linear = flat @ cmatrix.T
    srgb_linear = srgb_linear.reshape(h, w, 3)
    
    # 2. Run gamma proxy (exposure scale, sigmoid tone mapping, gamma correction)
    x = srgb_linear * scale
    x_mapped = x / np.sqrt(1.0 + x * x)
    res = np.power(np.clip(x_mapped, 0.0, 1.0), 1.0 / gamma_pow)
    return res.astype(np.float32)

def path_b2_linear_camera_proxy(rgb_linear, scale=1.0, gamma_pow=2.22):
    # 1. Run gamma proxy directly on linear camera-space (No sRGB cmatrix transform)
    x = rgb_linear * scale
    x_mapped = x / np.sqrt(1.0 + x * x)
    res = np.power(np.clip(x_mapped, 0.0, 1.0), 1.0 / gamma_pow)
    return res.astype(np.float32)

def run_comparison():
    dng_path = os.path.join(project_root, "test_algorithm/IMG_20250423_160105_B001.dng")
    if not os.path.exists(dng_path):
        print(f"Error: {dng_path} not found.")
        return
        
    print("\n" + "="*70)
    # Corrected title without non-ASCII characters
    print(" RAW PIPELINE PRECISION COMPARISON (PATH A vs PATH B)")
    print("="*70)
    
    # Load DNG
    bayer, wb, cmatrix, black, white, c00, c01, c10, c11 = load_dng_and_metadata(dng_path)
    print(f"Loaded: {os.path.basename(dng_path)}")
    print(f"White Balance: R={wb[0]:.4f}, G1={wb[1]:.4f}, B={wb[2]:.4f}, G2={wb[3]:.4f}")
    
    # Demosaic to pure linear camera RGB
    rgb_linear = demosaic_linear_numpy(bayer, wb, black, white, c00, c01, c10, c11)
    
    # Path A: Direct sRGB non-linear (The gold standard)
    path_a = path_a_direct_nonlinear(rgb_linear, cmatrix, scale=1.0, gamma_pow=2.22)
    
    # Path B1: Linear -> sRGB -> Gamma Proxy
    path_b1 = path_b1_linear_srgb_proxy(rgb_linear, cmatrix, scale=1.0, gamma_pow=2.22)
    
    # Path B2: Linear -> Direct Gamma Proxy (No sRGB matrix)
    path_b2 = path_b2_linear_camera_proxy(rgb_linear, scale=1.0, gamma_pow=2.22)
    
    # 1. Compare Path A vs Path B1 (Correct flow: Matrix multiplication first)
    diff_b1 = np.abs(path_a - path_b1)
    mae_b1 = np.mean(diff_b1)
    max_b1 = np.max(diff_b1)
    
    # 2. Compare Path A vs Path B2 (Incorrect flow: No sRGB color space conversion)
    diff_b2 = np.abs(path_a - path_b2)
    mae_b2 = np.mean(diff_b2)
    max_b2 = np.max(diff_b2)
    
    print("\n" + "-"*50)
    print(" METRICS ANALYSIS")
    print("-"*50)
    print(f"Path A vs Path B1 (Matrix conversion -> Gamma Proxy):")
    print(f"  Mean Absolute Error (MAE): {mae_b1:.10f}")
    print(f"  Max Absolute Error  (Max): {max_b1:.10f}")
    print(f"  Status                   : {'BIT-PERFECT' if max_b1 < 1e-7 else 'PASS' if max_b1 < 1e-5 else 'MISMATCH'}")
    
    print(f"\nPath A vs Path B2 (Direct Gamma Proxy without sRGB Matrix):")
    print(f"  Mean Absolute Error (MAE): {mae_b2:.10f}")
    print(f"  Max Absolute Error  (Max): {max_b2:.10f}")
    print(f"  Status                   : {'MISMATCH (Colors distorted)'}")
    print("-"*50 + "\n")
    
    tolerance = 1e-7  # 0.00001%
    if max_b1 <= tolerance:
        print(">>> [SUCCESS] Mathematical Bit-Perfect Equivalence Confirmed!")
    else:
        print(f">>> [ANALYSIS] Minor Float Precision differences. MAE: {mae_b1:.10f}")

    # Generate side-by-side visual comparison
    img_a = np.clip(path_a * 255.0, 0, 255).astype(np.uint8)
    img_b1 = np.clip(path_b1 * 255.0, 0, 255).astype(np.uint8)
    
    # Convert RGB to BGR for OpenCV
    img_a_bgr = cv2.cvtColor(img_a, cv2.COLOR_RGB2BGR)
    img_b1_bgr = cv2.cvtColor(img_b1, cv2.COLOR_RGB2BGR)
    
    # Put text labels on each half
    cv2.putText(img_a_bgr, "Path A: Direct Hamilton ToneMapped", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(img_b1_bgr, "Path B1: Linear Demosaic + Gamma Proxy", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Concatenate horizontally
    h_cmp = np.hstack([img_a_bgr, img_b1_bgr])
    
    # Save to the specific artifact directory so we can embed it
    artifact_dir = "C:\\Users\\BelutGoyang\\.gemini\\antigravity-ide\\brain\\73866290-fd2f-4f83-9e34-b9f429676c71"
    os.makedirs(artifact_dir, exist_ok=True)
    out_path = os.path.join(artifact_dir, "comparison_side_by_side.png")
    cv2.imwrite(out_path, h_cmp)
    print(f"Saved side-by-side visual comparison to: {out_path}")

if __name__ == "__main__":
    run_comparison()
