import os
import sys
import time
import cv2
import numpy as np
import taichi as ti

# 1. Initialize Taichi JIT on GPU
ti.init(arch=ti.gpu)

print("=== Taichi GPU Hamilton-Adams Demosaicing (Dynamic Color Correction) ===")

# 2. Path to the DNG test file
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dng_path = os.path.join(project_root, "test_algorithm/IMG_20260429_230301Z_B015.dng")

if not os.path.exists(dng_path):
    print(f"Error: DNG file not found at {dng_path}")
    sys.exit(1)

# 3. Load DNG file and extract RAW Bayer matrix & Metadata using rawpy
try:
    import rawpy
except ImportError:
    print("Error: 'rawpy' is not installed in the active python environment.")
    print("Please install it using: pip install rawpy")
    sys.exit(1)

print(f"Loading RAW DNG file: {os.path.basename(dng_path)} ...")
start_load = time.perf_counter()

with rawpy.imread(dng_path) as raw:
    # Get raw Bayer 2D grid
    bayer_np = raw.raw_image.astype(np.float32)
    h_orig, w_orig = bayer_np.shape

    # Extract metadata
    black_level = float(raw.black_level_per_channel[0])
    white_level = float(raw.white_level)

    # White Balance Gains (Camera native)
    # raw.camera_whitebalance maps to [R_gain, G1_gain, B_gain, G2_gain]
    wb_np = np.array(raw.camera_whitebalance, dtype=np.float32)

    # CRITICAL WB FIX: If G2_gain is 0.0, half of the Green pixels will be black!
    # Set G2_gain to G1_gain if G2 is zero or invalid.
    if len(wb_np) == 4:
        if wb_np[3] <= 0.01:
            print(
                f"  [WB Fix] G2_gain was {wb_np[3]}, replacing it with G1_gain ({wb_np[1]})"
            )
            wb_np[3] = wb_np[1]

        # Normalize so Green has gain 1.0 (average G1 and G2)
        g_gain = (wb_np[1] + wb_np[3]) / 2.0
        wb_np /= g_gain
    else:
        wb_np = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)

    # Dynamic Bayer Pattern Detection from raw_colors 2x2 grid
    # 0 = Red, 1 = Green, 2 = Blue, 3 = Green
    c00 = int(raw.raw_colors[0, 0])
    c01 = int(raw.raw_colors[0, 1])
    c10 = int(raw.raw_colors[1, 0])
    c11 = int(raw.raw_colors[1, 1])

    # Map pattern for display
    color_names = {0: "R", 1: "G", 2: "B", 3: "G"}
    detected_pattern = (
        f"{color_names[c00]}{color_names[c01]}{color_names[c10]}{color_names[c11]}"
    )

    # Color Matrix (Camera to sRGB standard) from DNG metadata
    color_matrix_np = raw.color_matrix[:, :3].astype(np.float32)

    print(f"  RAW Resolution: {w_orig}x{h_orig} ({ (w_orig*h_orig)/1e6 :.2f} MP)")
    print(
        f"  Detected Bayer Pattern: {detected_pattern} (Grid: {c00},{c01},{c10},{c11})"
    )
    print(f"  Black Level: {black_level} | White Level: {white_level}")
    print(
        f"  WB Gains (Normalized): R={wb_np[0]:.3f}, G1={wb_np[1]:.3f}, B={wb_np[2]:.3f}, G2={wb_np[3]:.3f}"
    )

print(f"DNG loaded successfully in {(time.perf_counter() - start_load)*1000:.2f} ms")

# 4. Allocate GPU VRAM Taichi Fields
bayer_gpu = ti.ndarray(dtype=ti.f32, shape=(h_orig, w_orig))
green_gpu = ti.ndarray(
    dtype=ti.f32, shape=(h_orig, w_orig)
)  # temporary channel for step 1
dst_rgb_gpu = ti.ndarray(dtype=ti.f32, shape=(h_orig, w_orig, 3))  # output RGB

wb_gpu = ti.ndarray(dtype=ti.f32, shape=(4,))
cmatrix_gpu = ti.ndarray(dtype=ti.f32, shape=(3, 3))

# Upload initial matrices to GPU
bayer_gpu.from_numpy(bayer_np)
wb_gpu.from_numpy(wb_np)
cmatrix_gpu.from_numpy(color_matrix_np)

# 5. Define GPU Hamilton-Adams Demosaicing Kernels in Taichi JIT


@ti.func
def get_wb_val(
    bayer: ti.template(),
    r,
    c,
    black,
    white,
    c00,
    c01,
    c10,
    c11,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
):
    val = ti.math.clamp((bayer[r, c] - black) / (white - black), 0.0, 1.0)
    color_idx = 1
    r_mod = r % 2
    c_mod = c % 2
    if r_mod == 0:
        if c_mod == 0:
            color_idx = c00
        else:
            color_idx = c01
    else:
        if c_mod == 0:
            color_idx = c10
        else:
            color_idx = c11

    gain = 1.0
    if color_idx == 0:
        gain = wb_r
    elif color_idx == 1:
        gain = wb_g1
    elif color_idx == 2:
        gain = wb_b
    else:
        gain = wb_g2
    return val * gain


@ti.kernel
def ha_green_interpolation_kernel(
    bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    black: ti.f32,
    white: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 1: Hamilton-Adams Edge-Directed Green Channel Reconstruction.

    Uses high-order second-derivative gradients of Red/Blue to guide Green interpolation.
    """
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            if c_mod == 0:
                color_idx = c00
            else:
                color_idx = c01
        else:
            if c_mod == 0:
                color_idx = c10
            else:
                color_idx = c11

        is_green = (color_idx == 1) or (color_idx == 3)

        if is_green:
            green[r, c] = get_wb_val(
                bayer, r, c, black, white, c00, c01, c10, c11, wb_r, wb_g1, wb_b, wb_g2
            )
        else:
            # We are at a Red or Blue pixel, interpolate Green
            if r > 1 and r < h - 2 and c > 1 and c < w - 2:
                # Adjacent Green neighbors
                g_left = get_wb_val(
                    bayer,
                    r,
                    c - 1,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )
                g_right = get_wb_val(
                    bayer,
                    r,
                    c + 1,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )
                g_up = get_wb_val(
                    bayer,
                    r - 1,
                    c,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )
                g_down = get_wb_val(
                    bayer,
                    r + 1,
                    c,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )

                # Active center channel (Red or Blue)
                c_center = get_wb_val(
                    bayer,
                    r,
                    c,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )
                c_left2 = get_wb_val(
                    bayer,
                    r,
                    c - 2,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )
                c_right2 = get_wb_val(
                    bayer,
                    r,
                    c + 2,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )
                c_up2 = get_wb_val(
                    bayer,
                    r - 2,
                    c,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )
                c_down2 = get_wb_val(
                    bayer,
                    r + 2,
                    c,
                    black,
                    white,
                    c00,
                    c01,
                    c10,
                    c11,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                )

                # Hamilton-Adams horizontal and vertical gradients
                dh = ti.abs(g_left - g_right) + ti.abs(
                    2.0 * c_center - c_left2 - c_right2
                )
                dv = ti.abs(g_up - g_down) + ti.abs(2.0 * c_center - c_up2 - c_down2)

                if dh < dv:
                    # Horizontal Edge: Interpolate Horizontally
                    green[r, c] = (g_left + g_right) * 0.5 + (
                        2.0 * c_center - c_left2 - c_right2
                    ) * 0.25
                elif dh > dv:
                    # Vertical Edge: Interpolate Vertically
                    green[r, c] = (g_up + g_down) * 0.5 + (
                        2.0 * c_center - c_up2 - c_down2
                    ) * 0.25
                else:
                    # Flat / Diagonal: Average both directions
                    green[r, c] = (g_left + g_right + g_up + g_down) * 0.25 + (
                        4.0 * c_center - c_left2 - c_right2 - c_up2 - c_down2
                    ) * 0.125
            else:
                # Simple fallback bilinear green interpolation at borders
                g_val = 0.0
                g_count = 0.0
                for dr, dc in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < h and nc >= 0 and nc < w:
                        g_val += get_wb_val(
                            bayer,
                            nr,
                            nc,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        g_count += 1.0
                green[r, c] = g_val / g_count


@ti.kernel
def ha_red_blue_interpolation_kernel(
    bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    black: ti.f32,
    white: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 2: Red and Blue Reconstruction using Color Difference Interpolation (R-G / B-G).

    Interpolates Red and Blue color differences based on the fully reconstructed Green channel,
    preventing color bleeding and zippering.
    """
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            if c_mod == 0:
                color_idx = c00
            else:
                color_idx = c01
        else:
            if c_mod == 0:
                color_idx = c10
            else:
                color_idx = c11

        R, G, B = 0.0, 0.0, 0.0

        # Green is already perfectly populated at all coordinates
        G = green[r, c]

        if color_idx == 0:  # Red pixel
            # White Balance correction on the raw value
            R = get_wb_val(
                bayer, r, c, black, white, c00, c01, c10, c11, wb_r, wb_g1, wb_b, wb_g2
            )
            # Interpolate Blue using color difference (B - G) at diagonals
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                b_diff = (
                    (
                        get_wb_val(
                            bayer,
                            r - 1,
                            c - 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r - 1, c - 1]
                    )
                    + (
                        get_wb_val(
                            bayer,
                            r - 1,
                            c + 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r - 1, c + 1]
                    )
                    + (
                        get_wb_val(
                            bayer,
                            r + 1,
                            c - 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r + 1, c - 1]
                    )
                    + (
                        get_wb_val(
                            bayer,
                            r + 1,
                            c + 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r + 1, c + 1]
                    )
                ) * 0.25
                B = G + b_diff
            else:
                B = G

        elif color_idx == 2:  # Blue pixel
            # White Balance correction on the raw value
            B = get_wb_val(
                bayer, r, c, black, white, c00, c01, c10, c11, wb_r, wb_g1, wb_b, wb_g2
            )
            # Interpolate Red using color difference (R - G) at diagonals
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                r_diff = (
                    (
                        get_wb_val(
                            bayer,
                            r - 1,
                            c - 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r - 1, c - 1]
                    )
                    + (
                        get_wb_val(
                            bayer,
                            r - 1,
                            c + 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r - 1, c + 1]
                    )
                    + (
                        get_wb_val(
                            bayer,
                            r + 1,
                            c - 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r + 1, c - 1]
                    )
                    + (
                        get_wb_val(
                            bayer,
                            r + 1,
                            c + 1,
                            black,
                            white,
                            c00,
                            c01,
                            c10,
                            c11,
                            wb_r,
                            wb_g1,
                            wb_b,
                            wb_g2,
                        )
                        - green[r + 1, c + 1]
                    )
                ) * 0.25
                R = G + r_diff
            else:
                R = G

        else:  # Green pixel (G1 or G2)
            # Determine if left neighbor is Red or Blue to check row type
            cl = c - 1
            if cl < 0:
                cl = 1

            left_color = 1
            if r_mod == 0:
                if cl % 2 == 0:
                    left_color = c00
                else:
                    left_color = c01
            else:
                if cl % 2 == 0:
                    left_color = c10
                else:
                    left_color = c11

            if left_color == 0:  # Left is Red, so Red is Horizontal, Blue is Vertical
                # Red (Horizontal difference R-G)
                if c > 0 and c < w - 1:
                    r_diff = (
                        (
                            get_wb_val(
                                bayer,
                                r,
                                c - 1,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r, c - 1]
                        )
                        + (
                            get_wb_val(
                                bayer,
                                r,
                                c + 1,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r, c + 1]
                        )
                    ) * 0.5
                    R = G + r_diff
                else:
                    R = G

                # Blue (Vertical difference B-G)
                if r > 0 and r < h - 1:
                    b_diff = (
                        (
                            get_wb_val(
                                bayer,
                                r - 1,
                                c,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r - 1, c]
                        )
                        + (
                            get_wb_val(
                                bayer,
                                r + 1,
                                c,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r + 1, c]
                        )
                    ) * 0.5
                    B = G + b_diff
                else:
                    B = G

            else:  # Left is Blue, so Blue is Horizontal, Red is Vertical
                # Red (Vertical difference R-G)
                if r > 0 and r < h - 1:
                    r_diff = (
                        (
                            get_wb_val(
                                bayer,
                                r - 1,
                                c,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r - 1, c]
                        )
                        + (
                            get_wb_val(
                                bayer,
                                r + 1,
                                c,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r + 1, c]
                        )
                    ) * 0.5
                    R = G + r_diff
                else:
                    R = G

                # Blue (Horizontal difference B-G)
                if c > 0 and c < w - 1:
                    b_diff = (
                        (
                            get_wb_val(
                                bayer,
                                r,
                                c - 1,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r, c - 1]
                        )
                        + (
                            get_wb_val(
                                bayer,
                                r,
                                c + 1,
                                black,
                                white,
                                c00,
                                c01,
                                c10,
                                c11,
                                wb_r,
                                wb_g1,
                                wb_b,
                                wb_g2,
                            )
                            - green[r, c + 1]
                        )
                    ) * 0.5
                    B = G + b_diff
                else:
                    B = G

        # Apply Camera-to-sRGB matrix transform (3x3 matrix multiply)
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        # Tone curve / Gamma correction (Power of 1 / 2.22)
        dst[r, c, 0] = ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 1] = ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 2] = ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)


# 6. Execute GPU Demosaicing Pipeline
print("\nExecuting Hamilton-Adams Demosaicing on GPU VRAM...")

# Warmup to compile JIT kernels
ha_green_interpolation_kernel(
    bayer_gpu,
    green_gpu,
    float(wb_np[0]),
    float(wb_np[1]),
    float(wb_np[2]),
    float(wb_np[3]),
    black_level,
    white_level,
    h_orig,
    w_orig,
    c00,
    c01,
    c10,
    c11,
)
ha_red_blue_interpolation_kernel(
    bayer_gpu,
    green_gpu,
    float(wb_np[0]),
    float(wb_np[1]),
    float(wb_np[2]),
    float(wb_np[3]),
    cmatrix_gpu,
    dst_rgb_gpu,
    black_level,
    white_level,
    h_orig,
    w_orig,
    c00,
    c01,
    c10,
    c11,
)
ti.sync()

# Benchmark loop
print(f"\nRunning 30-Frame GPU Stress Test (FPS & Throughput)...")
start_bench = time.perf_counter()
n_iters = 10
for i in range(n_iters):
    t0 = time.perf_counter()
    ha_green_interpolation_kernel(
        bayer_gpu,
        green_gpu,
        float(wb_np[0]),
        float(wb_np[1]),
        float(wb_np[2]),
        float(wb_np[3]),
        black_level,
        white_level,
        h_orig,
        w_orig,
        c00,
        c01,
        c10,
        c11,
    )
    ha_red_blue_interpolation_kernel(
        bayer_gpu,
        green_gpu,
        float(wb_np[0]),
        float(wb_np[1]),
        float(wb_np[2]),
        float(wb_np[3]),
        cmatrix_gpu,
        dst_rgb_gpu,
        black_level,
        white_level,
        h_orig,
        w_orig,
        c00,
        c01,
        c10,
        c11,
    )
    ti.sync()
    t1 = time.perf_counter()
    print(f"  Frame {i+1:02d}/{n_iters} processed in {(t1-t0)*1000:.2f} ms")

end_bench = time.perf_counter()
total_time = end_bench - start_bench
bench_time = total_time / n_iters * 1000
fps = n_iters / total_time
print(f"\n[GPU Speed Benchmark Results]")
print(f"  Total Time for {n_iters} frames: {total_time*1000:.2f} ms")
print(f"  Average Speed per frame: {bench_time:.2f} ms")
print(f"  Demosaicing Throughput: {fps:.2f} FPS!")

# 7. Download result to CPU
print("Downloading demosaiced image to RAM...")
res_rgb = dst_rgb_gpu.to_numpy()

# Convert RGB float [0, 1] to BGR uint8 for OpenCV rendering
res_bgr = (res_rgb * 255.0).astype(np.uint8)
res_bgr = cv2.cvtColor(res_bgr, cv2.COLOR_RGB2BGR)

# 8. Render in 4K resolution!
# 4K UHD dimensions: 3840x2160.
h_dst, w_dst = 2160, 3840
print(f"Resizing final rendering to 4K UHD resolution ({w_dst}x{h_dst})...")
res_4k = cv2.resize(res_bgr, (w_dst, h_dst), interpolation=cv2.INTER_CUBIC)

# Save result as a proof of quality
out_tiff = os.path.join(project_root, "scratch/calibrated_demosaic_4k.tif")
cv2.imwrite(out_tiff, res_bgr)
print(f"[Saved] Full resolution TIFF saved to: {out_tiff}")

# Show image in OpenCV
win_name = "Taichi GPU Hamilton-Adams Demosaicing - 4K Rendering"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win_name, 1280, 720)  # resizable preview window
cv2.imshow(win_name, res_4k)

print("\nPress any key in the OpenCV Window to close.")
cv2.waitKey(0)
cv2.destroyAllWindows()
print("Demosaicing script completed cleanly.")
