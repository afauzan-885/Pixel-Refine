import os
import rawpy
import cv2
import numpy as np

dng_path = "test_algorithm/IMG_20260429_230301Z_B015.dng"
with rawpy.imread(dng_path) as raw:
    bayer = raw.raw_image.astype(np.float32)
    h, w = bayer.shape
    black = float(raw.black_level_per_channel[0])
    white = float(raw.white_level)
    wb = np.array(raw.camera_whitebalance, dtype=np.float32)
    
    # WB fix
    if len(wb) == 4 and wb[3] <= 0.01:
        wb[3] = wb[1]
    
    # Normalize WB so green average is 1.0
    g_gain = (wb[1] + wb[3]) / 2.0
    wb /= g_gain
    
    # Get color matrix
    cmatrix = raw.color_matrix[:, :3].astype(np.float32)
    
    # Get raw colors grid
    c00 = raw.raw_colors[0, 0]
    c01 = raw.raw_colors[0, 1]
    c10 = raw.raw_colors[1, 0]
    c11 = raw.raw_colors[1, 1]

# Normal bayer
norm_bayer = np.clip((bayer - black) / (white - black), 0.0, 1.0)

# Create white balanced bayer (vectorized!)
wb_bayer = np.zeros_like(norm_bayer)
wb_bayer[0::2, 0::2] = norm_bayer[0::2, 0::2] * wb[c00]
wb_bayer[0::2, 1::2] = norm_bayer[0::2, 1::2] * wb[c01]
wb_bayer[1::2, 0::2] = norm_bayer[1::2, 0::2] * wb[c10]
wb_bayer[1::2, 1::2] = norm_bayer[1::2, 1::2] * wb[c11]

# Crop a 800x800 area from center for fast testing
crop_h, crop_w = 800, 800
cy, cx = (h - crop_h) // 2, (w - crop_w) // 2
# Make sure crop is aligned to 2x2 grid
cy = cy - (cy % 2)
cx = cx - (cx % 2)

crop_bayer = wb_bayer[cy:cy+crop_h, cx:cx+crop_w]

print("Running Hamilton-Adams Demosaic on CPU for cropped region...")
green = np.zeros_like(crop_bayer)
rgb = np.zeros((crop_h, crop_w, 3), dtype=np.float32)

# Pass 1: Green Reconstruction
for r in range(crop_h):
    global_r = cy + r
    r_mod = global_r % 2
    for c in range(crop_w):
        global_c = cx + c
        c_mod = global_c % 2
        
        color_idx = c00 if c_mod == 0 else c01 if r_mod == 0 else c10 if c_mod == 0 else c11
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
            
        is_green = (color_idx == 1) or (color_idx == 3)
        
        if is_green:
            green[r, c] = crop_bayer[r, c]
        else:
            if r > 1 and r < crop_h - 2 and c > 1 and c < crop_w - 2:
                g_left  = crop_bayer[r, c-1]
                g_right = crop_bayer[r, c+1]
                g_up    = crop_bayer[r-1, c]
                g_down  = crop_bayer[r+1, c]
                
                c_center = crop_bayer[r, c]
                c_left2  = crop_bayer[r, c-2]
                c_right2 = crop_bayer[r, c+2]
                c_up2    = crop_bayer[r-2, c]
                c_down2  = crop_bayer[r+2, c]
                
                dh = abs(g_left - g_right) + abs(2.0 * c_center - c_left2 - c_right2)
                dv = abs(g_up - g_down)    + abs(2.0 * c_center - c_up2 - c_down2)
                
                if dh < dv:
                    green[r, c] = (g_left + g_right) * 0.5 + (2.0 * c_center - c_left2 - c_right2) * 0.25
                elif dh > dv:
                    green[r, c] = (g_up + g_down) * 0.5 + (2.0 * c_center - c_up2 - c_down2) * 0.25
                else:
                    green[r, c] = (g_left + g_right + g_up + g_down) * 0.25 + (4.0 * c_center - c_left2 - c_right2 - c_up2 - c_down2) * 0.125
            else:
                # Border fallback
                g_val = 0.0
                g_count = 0.0
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < crop_h and nc >= 0 and nc < crop_w:
                        g_val += crop_bayer[nr, nc]
                        g_count += 1.0
                green[r, c] = g_val / g_count

# Pass 2: Red / Blue Reconstruction and sRGB matrix
for r in range(crop_h):
    global_r = cy + r
    r_mod = global_r % 2
    for c in range(crop_w):
        global_c = cx + c
        c_mod = global_c % 2
        
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
            
        R, G, B = 0.0, 0.0, 0.0
        G = green[r, c]
        
        if color_idx == 0: # Red pixel
            R = crop_bayer[r, c]
            if r > 0 and r < crop_h - 1 and c > 0 and c < crop_w - 1:
                b_diff = (
                    (crop_bayer[r-1, c-1] - green[r-1, c-1]) +
                    (crop_bayer[r-1, c+1] - green[r-1, c+1]) +
                    (crop_bayer[r+1, c-1] - green[r+1, c-1]) +
                    (crop_bayer[r+1, c+1] - green[r+1, c+1])
                ) * 0.25
                B = G + b_diff
            else:
                B = G
        elif color_idx == 2: # Blue pixel
            B = crop_bayer[r, c]
            if r > 0 and r < crop_h - 1 and c > 0 and c < crop_w - 1:
                r_diff = (
                    (crop_bayer[r-1, c-1] - green[r-1, c-1]) +
                    (crop_bayer[r-1, c+1] - green[r-1, c+1]) +
                    (crop_bayer[r+1, c-1] - green[r+1, c-1]) +
                    (crop_bayer[r+1, c+1] - green[r+1, c+1])
                ) * 0.25
                R = G + r_diff
            else:
                R = G
        else: # Green pixel
            cl = c - 1
            if cl < 0:
                cl = 1
            left_c_mod = (cx + cl) % 2
            left_r_mod = r_mod
            if left_r_mod == 0:
                left_color = c00 if left_c_mod == 0 else c01
            else:
                left_color = c10 if left_c_mod == 0 else c11
                
            if left_color == 0: # Left is Red, so Red is Horizontal, Blue is Vertical
                if c > 0 and c < crop_w - 1:
                    r_diff = ((crop_bayer[r, c-1] - green[r, c-1]) + (crop_bayer[r, c+1] - green[r, c+1])) * 0.5
                    R = G + r_diff
                else:
                    R = G
                if r > 0 and r < crop_h - 1:
                    b_diff = ((crop_bayer[r-1, c] - green[r-1, c]) + (crop_bayer[r+1, c] - green[r+1, c])) * 0.5
                    B = G + b_diff
                else:
                    B = G
            else: # Left is Blue, so Blue is Horizontal, Red is Vertical
                if r > 0 and r < crop_h - 1:
                    r_diff = ((crop_bayer[r-1, c] - green[r-1, c]) + (crop_bayer[r+1, c] - green[r+1, c])) * 0.5
                    R = G + r_diff
                else:
                    R = G
                if c > 0 and c < crop_w - 1:
                    b_diff = ((crop_bayer[r, c-1] - green[r, c-1]) + (crop_bayer[r, c+1] - green[r, c+1])) * 0.5
                    B = G + b_diff
                else:
                    B = G
                    
        # Apply camera-to-sRGB matrix
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B
        
        rgb[r, c, 0] = np.clip(sR, 0.0, 1.0)
        rgb[r, c, 1] = np.clip(sG, 0.0, 1.0)
        rgb[r, c, 2] = np.clip(sB, 0.0, 1.0)

# Gamma correction
rgb_gamma = np.power(rgb, 1.0 / 2.22)
bgr_out = (rgb_gamma * 255.0).astype(np.uint8)
bgr_out = cv2.cvtColor(bgr_out, cv2.COLOR_RGB2BGR)

out_path = "scratch/bilinear_test_cpu.png"
cv2.imwrite(out_path, bgr_out)
print(f"Saved crop test image to {out_path}")
