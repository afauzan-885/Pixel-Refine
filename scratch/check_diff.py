import os
import sys
import numpy as np

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../"))
if project_root not in sys.path:
    sys.path.append(project_root)

dng_path = "test_algorithm/IMG_20260429_230301Z_B015.dng"

import rawpy
with rawpy.imread(dng_path) as raw:
    bayer_np = raw.raw_image.astype(np.float32)
    black_level = float(raw.black_level_per_channel[0])
    white_level = float(raw.white_level)
    
    wb_np = np.array(raw.camera_whitebalance, dtype=np.float32)
    if len(wb_np) == 4:
        if wb_np[3] <= 0.01:
            wb_np[3] = wb_np[1]
        g_gain = (wb_np[1] + wb_np[3]) / 2.0
        wb_np /= g_gain
    else:
        wb_np = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)

    c00 = int(raw.raw_colors[0, 0])
    c01 = int(raw.raw_colors[0, 1])
    c10 = int(raw.raw_colors[1, 0])
    c11 = int(raw.raw_colors[1, 1])
    cmatrix_np = raw.color_matrix[:, :3].astype(np.float32)

# JIT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "0"
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm as ta
jit_res = ta.hamilton_demosaic(
    bayer_np, wb_np[0], wb_np[1], wb_np[2], wb_np[3], cmatrix_np,
    black_level, white_level, c00, c01, c10, c11
)

# AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as ta_aot
aot_res = ta_aot.hamilton_demosaic(
    bayer_np, wb_np[0], wb_np[1], wb_np[2], wb_np[3], cmatrix_np,
    black_level, white_level, c00, c01, c10, c11
)

crop_jit = jit_res[15:-15, 15:-15]
crop_aot = aot_res[15:-15, 15:-15]

diff = np.abs(crop_jit - crop_aot)
print("Max diff:", np.max(diff))
print("MAE:", np.mean(diff))

idx = np.where(diff > 0.01)
print("Num pixels with diff > 0.01:", len(idx[0]))
if len(idx[0]) > 0:
    print("First 10 diff coordinates (cropped space):")
    for i in range(min(10, len(idx[0]))):
        r, c, ch = idx[0][i], idx[1][i], idx[2][i]
        orig_r, orig_c = r + 15, c + 15
        print(f"Cropped: ({r},{c},{ch}), Original: ({orig_r},{orig_c},{ch}), JIT: {crop_jit[r,c,ch]:.6f}, AOT: {crop_aot[r,c,ch]:.6f}, Diff: {diff[r,c,ch]:.6f}")
