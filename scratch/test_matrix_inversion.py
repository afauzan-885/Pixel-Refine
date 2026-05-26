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
    
    # Get raw colors grid
    c00 = raw.raw_colors[0, 0]
    c01 = raw.raw_colors[0, 1]
    c10 = raw.raw_colors[1, 0]
    c11 = raw.raw_colors[1, 1]
    
    # Color matrix
    cmatrix = raw.color_matrix[:, :3].astype(np.float32)

# Normal bayer
norm_bayer = np.clip((bayer - black) / (white - black), 0.0, 1.0)

# Create white balanced bayer
wb_bayer = np.zeros_like(norm_bayer)
for r in range(h):
    r_mod = r % 2
    for c in range(w):
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
        wb_bayer[r, c] = norm_bayer[r, c] * wb[color_idx]

# Fast crop for color testing
crop_h, crop_w = 400, 400
cy, cx = h // 2, w // 2
crop_wb = wb_bayer[cy:cy+crop_h, cx:cx+crop_w]

# Bilinear demosaic
B_raw = np.zeros_like(crop_wb)
G_raw = np.zeros_like(crop_wb)
R_raw = np.zeros_like(crop_wb)

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
            
        val = crop_wb[r, c]
        if color_idx == 0:
            R_raw[r, c] = val
        elif color_idx == 2:
            B_raw[r, c] = val
        else:
            G_raw[r, c] = val

# Bilinear filters
kernel_cross = np.array([[0, 0.25, 0], [0.25, 1.0, 0.25], [0, 0.25, 0]], dtype=np.float32)
kernel_diag = np.array([[0.25, 0, 0.25], [0, 1.0, 0], [0.25, 0, 0.25]], dtype=np.float32)
kernel_horiz = np.array([[0, 0, 0], [0.5, 1.0, 0.5], [0, 0, 0]], dtype=np.float32)
kernel_vert = np.array([[0, 0.5, 0], [0, 1.0, 0], [0, 0.5, 0]], dtype=np.float32)

G_interp = cv2.filter2D(G_raw, -1, kernel_cross)
R_interp_diag = cv2.filter2D(R_raw, -1, kernel_diag)
R_interp_horiz = cv2.filter2D(R_raw, -1, kernel_horiz)
R_interp_vert = cv2.filter2D(R_raw, -1, kernel_vert)

R_final = np.zeros_like(crop_wb)
for r in range(crop_h):
    global_r = cy + r
    r_mod = global_r % 2
    for c in range(crop_w):
        global_c = cx + c
        c_mod = global_c % 2
        if r_mod == 1 and c_mod == 1: # Red pixel (assuming BGGR grid)
            R_final[r, c] = R_raw[r, c]
        elif r_mod == 0 and c_mod == 0: # Blue pixel
            R_final[r, c] = R_interp_diag[r, c]
        elif r_mod == 0 and c_mod == 1: # Green1
            R_final[r, c] = R_interp_horiz[r, c]
        else: # Green2
            R_final[r, c] = R_interp_vert[r, c]

B_interp_diag = cv2.filter2D(B_raw, -1, kernel_diag)
B_interp_horiz = cv2.filter2D(B_raw, -1, kernel_horiz)
B_interp_vert = cv2.filter2D(B_raw, -1, kernel_vert)

B_final = np.zeros_like(crop_wb)
for r in range(crop_h):
    global_r = cy + r
    r_mod = global_r % 2
    for c in range(crop_w):
        global_c = cx + c
        c_mod = global_c % 2
        if r_mod == 0 and c_mod == 0: # Blue pixel
            B_final[r, c] = B_raw[r, c]
        elif r_mod == 1 and c_mod == 1: # Red pixel
            B_final[r, c] = B_interp_diag[r, c]
        elif r_mod == 0 and c_mod == 1: # Green1
            B_final[r, c] = B_interp_vert[r, c]
        else: # Green2
            B_final[r, c] = B_interp_horiz[r, c]

rgb_sensor = np.stack([R_final, G_interp, B_final], axis=-1)

# We want to try standard transformations:
# Conversion 1: Direct cmatrix (already tested, very green)
# Let's try to see if cmatrix is actually XYZ-to-Camera, so to get Camera-to-sRGB we do:
# M = xyz_to_srgb * cmatrix^-1
try:
    cmatrix_inv = np.linalg.inv(cmatrix)
except:
    print("Could not invert cmatrix!")
    cmatrix_inv = np.eye(3, dtype=np.float32)

xyz_to_srgb = np.array([
    [ 3.2404542, -1.5371385, -0.4985314],
    [-0.9692660,  1.8760108,  0.0415560],
    [ 0.0556434, -0.2040259,  1.0572252]
], dtype=np.float32)

c_to_srgb_1 = np.dot(xyz_to_srgb, cmatrix_inv)

# Let's try another common DNG matrix:
# DNG's ColorMatrix is XYZ_D50 to Camera.
# So Camera to XYZ_D50 = inv(ColorMatrix)
# Then XYZ_D50 to sRGB using D50-to-sRGB (standard chromatic adaptation):
# D50-to-sRGB matrix:
xyz_to_srgb_d50 = np.array([
    [ 3.1338561, -1.6168667, -0.4906146],
    [-0.9787684,  1.9161415,  0.0334540],
    [ 0.0719453, -0.2289914,  1.4052427]
], dtype=np.float32)

c_to_srgb_2 = np.dot(xyz_to_srgb_d50, cmatrix_inv)

# Let's also check if cmatrix is Camera-to-XYZ, in which case we do:
# c_to_srgb_3 = xyz_to_srgb * cmatrix
c_to_srgb_3 = np.dot(xyz_to_srgb, cmatrix)

# Apply and save each to compare
for name, mat in [("direct", cmatrix), ("inv_d65", c_to_srgb_1), ("inv_d50", c_to_srgb_2), ("direct_xyz", c_to_srgb_3)]:
    img_srgb = np.zeros_like(rgb_sensor)
    for i in range(3):
        img_srgb[..., i] = (mat[i, 0] * rgb_sensor[..., 0] +
                            mat[i, 1] * rgb_sensor[..., 1] +
                            mat[i, 2] * rgb_sensor[..., 2])
    img_srgb = np.clip(img_srgb, 0.0, 1.0)
    img_gamma = np.power(img_srgb, 1.0 / 2.22)
    bgr = (img_gamma * 255.0).astype(np.uint8)
    bgr = cv2.cvtColor(bgr, cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"scratch/crop_{name}.png", bgr)
    print(f"Saved scratch/crop_{name}.png")
