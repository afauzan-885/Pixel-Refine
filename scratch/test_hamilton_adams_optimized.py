import os
import sys
import time
import cv2
import numpy as np
import taichi as ti

# Setup path to find pixel_refine_desktop
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(file_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

print(
    "=== Taichi GPU Hamilton-Adams Demosaicing: Optimized JIT vs C++ AOT Stress Test ==="
)

# 2. Path to the DNG test file
dng_path = os.path.join(project_root, "test_algorithm/IMG_20260429_230301Z_B015.dng")
if not os.path.exists(dng_path):
    print(f"Error: DNG file not found at {dng_path}")
    sys.exit(1)

# 3. Load DNG file and extract RAW Bayer matrix & Metadata using rawpy
import rawpy

print(f"Loading RAW DNG file: {os.path.basename(dng_path)} ...")
with rawpy.imread(dng_path) as raw:
    bayer_np = raw.raw_image.astype(np.float32)
    h_orig, w_orig = bayer_np.shape

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
    color_matrix_np = raw.color_matrix[:, :3].astype(np.float32)

print(f"Loaded RAW Bayer matrix: {w_orig}x{h_orig} ({ (w_orig*h_orig)/1e6 :.2f} MP)")

# =========================================================================
# BENCHMARK 1: Local JIT Fallback Mode (Warmup + 100 Frames)
# =========================================================================
print("\n--- [Benchmark 1] Running JIT Fallback Mode ---")
ti.init(
    arch=ti.vulkan,
    offline_cache=True,
    offline_cache_file_path="E:/APP Developer/Pixel Refine/taichi_cache",
)


# Define JIT kernels locally for testing
@ti.kernel
def _preprocess_bayer_kernel(
    bayer: ti.types.ndarray(),
    wb_bayer: ti.types.ndarray(),
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
    for r, c in ti.ndrange(h, w):
        # Utilizes 100% Dynamic Range of the Sensor RAW image
        val = ti.math.clamp(
            (bayer[r, c] - black) / ti.max(1.0, white - black), 0.0, 1.0
        )
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
        gain = 1.0
        if color_idx == 0:
            gain = wb_r
        elif color_idx == 1:
            gain = wb_g1
        elif color_idx == 2:
            gain = wb_b
        else:
            gain = wb_g2
        wb_bayer[r, c] = val * gain


@ti.kernel
def _ha_green_interpolation_kernel_opt(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
        is_green = (color_idx == 1) or (color_idx == 3)
        if is_green:
            green[r, c] = wb_bayer[r, c]
        else:
            if r > 1 and r < h - 2 and c > 1 and c < w - 2:
                g_left = wb_bayer[r, c - 1]
                g_right = wb_bayer[r, c + 1]
                g_up = wb_bayer[r - 1, c]
                g_down = wb_bayer[r + 1, c]
                c_center = wb_bayer[r, c]
                c_left2 = wb_bayer[r, c - 2]
                c_right2 = wb_bayer[r, c + 2]
                c_up2 = wb_bayer[r - 2, c]
                c_down2 = wb_bayer[r + 2, c]
                dh = ti.abs(g_left - g_right) + ti.abs(
                    2.0 * c_center - c_left2 - c_right2
                )
                dv = ti.abs(g_up - g_down) + ti.abs(2.0 * c_center - c_up2 - c_down2)
                if dh < dv:
                    green[r, c] = (g_left + g_right) * 0.5 + (
                        2.0 * c_center - c_left2 - c_right2
                    ) * 0.25
                elif dh > dv:
                    green[r, c] = (g_up + g_down) * 0.5 + (
                        2.0 * c_center - c_up2 - c_down2
                    ) * 0.25
                else:
                    green[r, c] = (g_left + g_right + g_up + g_down) * 0.25 + (
                        4.0 * c_center - c_left2 - c_right2 - c_up2 - c_down2
                    ) * 0.125
            else:
                g_val = 0.0
                g_count = 0.0
                for dr, dc in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < h and nc >= 0 and nc < w:
                        g_val += wb_bayer[nr, nc]
                        g_count += 1.0
                green[r, c] = g_val / g_count


@ti.kernel
def _ha_red_blue_interpolation_kernel_opt(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
        R, G, B = 0.0, 0.0, 0.0
        G = green[r, c]
        if color_idx == 0:
            R = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                B = (
                    G
                    + (
                        (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1])
                        + (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1])
                        + (wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                        + (wb_bayer[r + 1, c + 1] - green[r + 1, c + 1])
                    )
                    * 0.25
                )
            else:
                B = G
        elif color_idx == 2:
            B = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                R = (
                    G
                    + (
                        (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1])
                        + (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1])
                        + (wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                        + (wb_bayer[r + 1, c + 1] - green[r + 1, c + 1])
                    )
                    * 0.25
                )
            else:
                R = G
        else:
            is_red_horizontal = False
            if r_mod == 0:
                is_red_horizontal = c00 == 0 if c_mod == 1 else c01 == 0
            else:
                is_red_horizontal = c10 == 0 if c_mod == 1 else c11 == 0

            if is_red_horizontal:
                R = (
                    G
                    + (
                        (wb_bayer[r, c - 1] - green[r, c - 1])
                        + (wb_bayer[r, c + 1] - green[r, c + 1])
                    )
                    * 0.5
                    if c > 0 and c < w - 1
                    else G
                )
                B = (
                    G
                    + (
                        (wb_bayer[r - 1, c] - green[r - 1, c])
                        + (wb_bayer[r + 1, c] - green[r + 1, c])
                    )
                    * 0.5
                    if r > 0 and r < h - 1
                    else G
                )
            else:
                R = (
                    G
                    + (
                        (wb_bayer[r - 1, c] - green[r - 1, c])
                        + (wb_bayer[r + 1, c] - green[r + 1, c])
                    )
                    * 0.5
                    if r > 0 and r < h - 1
                    else G
                )
                B = (
                    G
                    + (
                        (wb_bayer[r, c - 1] - green[r, c - 1])
                        + (wb_bayer[r, c + 1] - green[r, c + 1])
                    )
                    * 0.5
                    if c > 0 and c < w - 1
                    else G
                )
        # --- Advanced Highlight Recovery & Desaturation (executed in white-balanced camera space) ---
        R_raw = R / ti.max(0.1, wb_r)
        G_raw = G / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
        B_raw = B / ti.max(0.1, wb_b)

        # 2. Compute saturation metrics
        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        min_raw = ti.min(R_raw, ti.min(G_raw, B_raw))

        # 3. Calculate highlight desaturation factor with wide, smooth transitions (Smoothstep)
        factor = ti.math.clamp((max_raw - 0.55) / 0.43, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        # Calculate color neutrality weight with a wide, soft smoothstep
        ratio = min_raw / ti.max(1e-5, max_raw)
        neutrality = ti.math.clamp((ratio - 0.40) / 0.45, 0.0, 1.0)
        neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)

        final_factor = factor * neutrality

        # 4. Reconstruct and blend in white-balanced space
        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - final_factor) + L * final_factor
        G = G * (1.0 - final_factor) + L * final_factor
        B = B * (1.0 - final_factor) + L * final_factor

        # 5. Apply Camera-to-sRGB matrix transform
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        # 6. Apply Dynamic Algebraic Sigmoid Highlight Roll-off to preserve gradients and color fidelity
        sR = sR / ti.math.sqrt(1.0 + sR * sR)
        sG = sG / ti.math.sqrt(1.0 + sG * sG)
        sB = sB / ti.math.sqrt(1.0 + sB * sB)

        # Tone curve / Gamma correction
        dst[r, c, 0] = ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 1] = ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 2] = ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)


# Allocate reference fields
bayer_gpu = ti.ndarray(dtype=ti.f32, shape=(h_orig, w_orig))
wb_bayer_gpu = ti.ndarray(dtype=ti.f32, shape=(h_orig, w_orig))
green_gpu = ti.ndarray(dtype=ti.f32, shape=(h_orig, w_orig))
cmatrix_gpu = ti.ndarray(dtype=ti.f32, shape=(3, 3))
dst_rgb_gpu = ti.ndarray(dtype=ti.f32, shape=(h_orig, w_orig, 3))

bayer_gpu.from_numpy(bayer_np)
cmatrix_gpu.from_numpy(color_matrix_np)


def run_jit_pass():
    _preprocess_bayer_kernel(
        bayer_gpu,
        wb_bayer_gpu,
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
    _ha_green_interpolation_kernel_opt(
        wb_bayer_gpu, green_gpu, h_orig, w_orig, c00, c01, c10, c11
    )
    _ha_red_blue_interpolation_kernel_opt(
        wb_bayer_gpu,
        green_gpu,
        cmatrix_gpu,
        dst_rgb_gpu,
        float(wb_np[0]),
        float(wb_np[1]),
        float(wb_np[2]),
        float(wb_np[3]),
        h_orig,
        w_orig,
        c00,
        c01,
        c10,
        c11,
    )


# Warmup JIT
run_jit_pass()
ti.sync()

print("Running 100-Frame JIT Stress Test...")
start_jit = time.perf_counter()
n_iters = 100
for i in range(n_iters):
    t0 = time.perf_counter()
    run_jit_pass()
    ti.sync()
    t1 = time.perf_counter()
    if (i + 1) % 20 == 0 or i == 0:
        print(f"  Frame {i+1:03d}/{n_iters} processed in {(t1-t0)*1000:.2f} ms")
end_jit = time.perf_counter()
total_jit_time = end_jit - start_jit
jit_latency = total_jit_time / n_iters * 1000
jit_fps = n_iters / total_jit_time

print(f"-> JIT Average Latency: {jit_latency:.2f} ms per frame ({jit_fps:.2f} FPS)")

# =========================================================================
# BENCHMARK 2: C++ AOT Graph Mode (Warmup + 100 Frames)
# =========================================================================
print("\n--- [Benchmark 2] Running C++ AOT Graph Mode ---")
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as ta_aot
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot import engine

# Pre-upload/allocate VRAM buffers for AOT to run at raw C++ speed
bayer_aot_gpu = engine.upload(bayer_np)
cmatrix_aot_gpu = engine.upload(color_matrix_np)
dst_aot_gpu = engine.allocate((h_orig, w_orig, 3), dtype=np.float32)

# Pre-allocate intermediate buffers once (Zero-Allocation Loop!)
wb_bayer_aot_gpu = engine.allocate((h_orig, w_orig), dtype=np.float32)
green_aot_gpu = engine.allocate((h_orig, w_orig), dtype=np.float32)

# Get the compiled graph module
hamilton_mod = ta_aot._mod("hamilton")


def run_aot_pass():
    hamilton_mod.run(
        "hamilton_demosaic",
        bayer=bayer_aot_gpu,
        wb_bayer=wb_bayer_aot_gpu,
        green=green_aot_gpu,
        cmatrix=cmatrix_aot_gpu,
        dst=dst_aot_gpu,
        wb_r=float(wb_np[0]),
        wb_g1=float(wb_np[1]),
        wb_b=float(wb_np[2]),
        wb_g2=float(wb_np[3]),
        black=float(black_level),
        white=float(white_level),
        h=int(h_orig),
        w=int(w_orig),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )


# Warmup AOT
run_aot_pass()
engine.sync()

print("Running 100-Frame C++ AOT Stress Test (Zero-Copy VRAM, Zero-Allocation)...")
start_aot = time.perf_counter()
for i in range(n_iters):
    t0 = time.perf_counter()
    run_aot_pass()
    engine.sync()
    t1 = time.perf_counter()
    if (i + 1) % 20 == 0 or i == 0:
        print(f"  Frame {i+1:03d}/{n_iters} processed in {(t1-t0)*1000:.2f} ms")
end_aot = time.perf_counter()
total_aot_time = end_aot - start_aot
aot_latency = total_aot_time / n_iters * 1000
aot_fps = n_iters / total_aot_time

print(f"-> C++ AOT Average Latency: {aot_latency:.2f} ms per frame ({aot_fps:.2f} FPS)")

# =========================================================================
# PERFORMANCE METRICS COMPARISON
# =========================================================================
print("\n" + "=" * 60)
print("             FINAL BENCHMARK COMPARISON REPORT")
print("=" * 60)
print(f"{'Execution Mode':<25} | {'Latency (ms)':<15} | {'Throughput (FPS)':<10}")
print("-" * 60)
print(f"{'Local Reference JIT':<25} | {jit_latency:<15.2f} | {jit_fps:<10.2f}")
print(f"{'C++ AOT Graph (Vulkan)':<25} | {aot_latency:<15.2f} | {aot_fps:<10.2f}")
print("-" * 60)

speedup = jit_latency / aot_latency
improvement = (jit_latency - aot_latency) / jit_latency * 100
print(f">>> C++ AOT is {speedup:.2f}x faster than local JIT!")
print(
    f">>> Latency reduction: {jit_latency - aot_latency:.2f} ms per frame ({improvement:.1f}% faster)"
)
print("=" * 60)

# Clean up GPU memory
bayer_aot_gpu.destroy()
cmatrix_aot_gpu.destroy()
dst_aot_gpu.destroy()
wb_bayer_aot_gpu.destroy()
green_aot_gpu.destroy()

# Download and save final rendering preview for diagnostic
print("\nDownloading AOT final render for visual confirmation...")
final_rgb = ta_aot.hamilton_demosaic(
    bayer_np,
    wb_np[0],
    wb_np[1],
    wb_np[2],
    wb_np[3],
    color_matrix_np,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
)
final_bgr = (final_rgb * 255.0).astype(np.uint8)
final_bgr = cv2.cvtColor(final_bgr, cv2.COLOR_RGB2BGR)

# Resize to 4K UHD and save
h_dst, w_dst = 2160, 3840
print(f"Resizing final render to 4K UHD resolution ({w_dst}x{h_dst})...")
res_4k = cv2.resize(final_bgr, (w_dst, h_dst), interpolation=cv2.INTER_CUBIC)

out_tiff = os.path.join(project_root, "scratch/calibrated_demosaic_4k.tif")
cv2.imwrite(out_tiff, final_bgr)
print(f"[SUCCESS] Calibrated 4K TIFF saved to: {out_tiff}")
