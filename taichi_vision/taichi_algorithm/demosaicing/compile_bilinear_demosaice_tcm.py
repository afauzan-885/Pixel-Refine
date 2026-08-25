import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module

try:
    from taichi_vision.taichi_algorithm.demosaicing.demosaic_aot_builder import (
        register_bilinear_graphs,
    )
    from taichi_vision.taichi_algorithm.demosaicing.demosaic_postprocess import (
        rgb_to_bgr_i32,
    )
except ImportError:
    from demosaic_aot_builder import register_bilinear_graphs
    from demosaic_postprocess import rgb_to_bgr_i32

@ti.func
def _fast_gamma(x: ti.f32) -> ti.f32:
    t = ti.math.sqrt(x)
    return t * (1.30547177 + t * (-0.78947190 + t * (0.79064221 - 0.30664208 * t)))

@ti.func
def _get_gain_fast(ym: ti.i32, xm: ti.i32, g00: ti.f32, g01: ti.f32, g10: ti.f32, g11: ti.f32) -> ti.f32:
    return ti.select(ym == 0, ti.select(xm == 0, g00, g01), ti.select(xm == 0, g10, g11))

@ti.func
def _get_green_gain(nr: ti.i32, nc: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32, wb_g1: ti.f32, wb_g2: ti.f32) -> ti.f32:
    color_idx = 1
    if nr % 2 == 0:
        color_idx = c00 if nc % 2 == 0 else c01
    else:
        color_idx = c10 if nc % 2 == 0 else c11
    return wb_g1 if color_idx == 1 else wb_g2

@ti.kernel
def _bilinear_demosaice_fused_kernel(
    bayer: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
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
    linear: ti.i32,
):
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    gain_c00 = wb_r if c00==0 else (wb_g1 if c00==1 else (wb_b if c00==2 else wb_g2))
    gain_c01 = wb_r if c01==0 else (wb_g1 if c01==1 else (wb_b if c01==2 else wb_g2))
    gain_c10 = wb_r if c10==0 else (wb_g1 if c10==1 else (wb_b if c10==2 else wb_g2))
    gain_c11 = wb_r if c11==0 else (wb_g1 if c11==1 else (wb_b if c11==2 else wb_g2))

    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        
        # Center color index
        color_idx = 1
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
            
        r_up = ti.max(0, r - 1)
        r_down = ti.min(h - 1, r + 1)
        c_left = ti.max(0, c - 1)
        c_right = ti.min(w - 1, c + 1)
        
        up_mod = 0 if r == 0 else (1 - r_mod)
        down_mod = (h - 1) % 2 if r == h - 1 else (1 - r_mod)
        left_mod = 0 if c == 0 else (1 - c_mod)
        right_mod = (w - 1) % 2 if c == w - 1 else (1 - c_mod)
        
        # 1. Read center and cardinal raw values, clamp, and apply WB
        v11 = ti.math.clamp((bayer[r, c] - black) * inv_range, 0.0, 1.0)
        v01 = ti.math.clamp((bayer[r_up, c] - black) * inv_range, 0.0, 1.0)
        v21 = ti.math.clamp((bayer[r_down, c] - black) * inv_range, 0.0, 1.0)
        v10 = ti.math.clamp((bayer[r, c_left] - black) * inv_range, 0.0, 1.0)
        v12 = ti.math.clamp((bayer[r, c_right] - black) * inv_range, 0.0, 1.0)

        w11 = v11 * _get_gain_fast(r_mod, c_mod, gain_c00, gain_c01, gain_c10, gain_c11)
        w01 = v01 * _get_gain_fast(up_mod, c_mod, gain_c00, gain_c01, gain_c10, gain_c11)
        w21 = v21 * _get_gain_fast(down_mod, c_mod, gain_c00, gain_c01, gain_c10, gain_c11)
        w10 = v10 * _get_gain_fast(r_mod, left_mod, gain_c00, gain_c01, gain_c10, gain_c11)
        w12 = v12 * _get_gain_fast(r_mod, right_mod, gain_c00, gain_c01, gain_c10, gain_c11)

        R, G, B = 0.0, 0.0, 0.0

        if color_idx == 0:  # Red center
            # Read diagonal raw values
            v00 = ti.math.clamp((bayer[r_up, c_left] - black) * inv_range, 0.0, 1.0)
            v02 = ti.math.clamp((bayer[r_up, c_right] - black) * inv_range, 0.0, 1.0)
            v20 = ti.math.clamp((bayer[r_down, c_left] - black) * inv_range, 0.0, 1.0)
            v22 = ti.math.clamp((bayer[r_down, c_right] - black) * inv_range, 0.0, 1.0)
            
            w00 = v00 * _get_gain_fast(up_mod, left_mod, gain_c00, gain_c01, gain_c10, gain_c11)
            w02 = v02 * _get_gain_fast(up_mod, right_mod, gain_c00, gain_c01, gain_c10, gain_c11)
            w20 = v20 * _get_gain_fast(down_mod, left_mod, gain_c00, gain_c01, gain_c10, gain_c11)
            w22 = v22 * _get_gain_fast(down_mod, right_mod, gain_c00, gain_c01, gain_c10, gain_c11)

            R = w11
            G = (w01 + w10 + w12 + w21) * 0.25
            B = (w00 + w02 + w20 + w22) * 0.25

        elif color_idx == 2:  # Blue center
            # Read diagonal raw values
            v00 = ti.math.clamp((bayer[r_up, c_left] - black) * inv_range, 0.0, 1.0)
            v02 = ti.math.clamp((bayer[r_up, c_right] - black) * inv_range, 0.0, 1.0)
            v20 = ti.math.clamp((bayer[r_down, c_left] - black) * inv_range, 0.0, 1.0)
            v22 = ti.math.clamp((bayer[r_down, c_right] - black) * inv_range, 0.0, 1.0)
            
            w00 = v00 * _get_gain_fast(up_mod, left_mod, gain_c00, gain_c01, gain_c10, gain_c11)
            w02 = v02 * _get_gain_fast(up_mod, right_mod, gain_c00, gain_c01, gain_c10, gain_c11)
            w20 = v20 * _get_gain_fast(down_mod, left_mod, gain_c00, gain_c01, gain_c10, gain_c11)
            w22 = v22 * _get_gain_fast(down_mod, right_mod, gain_c00, gain_c01, gain_c10, gain_c11)

            B = w11
            G = (w01 + w10 + w12 + w21) * 0.25
            R = (w00 + w02 + w20 + w22) * 0.25

        else:  # Green center
            G = w11
            # Check if horizontal neighbors are Red (0)
            horiz_idx = c00 if r_mod == 0 else c10
            if left_mod != 0:
                horiz_idx = c01 if r_mod == 0 else c11
            
            if horiz_idx == 0:
                R = (w10 + w12) * 0.5
                B = (w01 + w21) * 0.5
            else:
                B = (w10 + w12) * 0.5
                R = (w01 + w21) * 0.5

        # sRGB Conversion Matrix multiplication
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        if linear == 1:
            # Linear RGB (WB + color matrix, no gamma) for natural tonemapping.
            dst[r, c, 0] = ti.math.clamp(sR, 0.0, 1.0)
            dst[r, c, 1] = ti.math.clamp(sG, 0.0, 1.0)
            dst[r, c, 2] = ti.math.clamp(sB, 0.0, 1.0)
        else:
            # Fast Gamma polynomial roll-off & clamp
            dst[r, c, 0] = _fast_gamma(ti.math.clamp(sR, 0.0, 1.0))
            dst[r, c, 1] = _fast_gamma(ti.math.clamp(sG, 0.0, 1.0))
            dst[r, c, 2] = _fast_gamma(ti.math.clamp(sB, 0.0, 1.0))

@ti.kernel
def _pure_bilinear_demosaice_kernel(
    bayer: ti.types.ndarray(),
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
    inv_range = 1.0 / ti.max(1.0, white - black)
    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        
        # Center color index
        color_idx = 1
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11
            
        r_up = ti.max(0, r - 1)
        r_down = ti.min(h - 1, r + 1)
        c_left = ti.max(0, c - 1)
        c_right = ti.min(w - 1, c + 1)
        
        v11 = ti.math.clamp((bayer[r, c] - black) * inv_range, 0.0, 1.0)
        v01 = ti.math.clamp((bayer[r_up, c] - black) * inv_range, 0.0, 1.0)
        v21 = ti.math.clamp((bayer[r_down, c] - black) * inv_range, 0.0, 1.0)
        v10 = ti.math.clamp((bayer[r, c_left] - black) * inv_range, 0.0, 1.0)
        v12 = ti.math.clamp((bayer[r, c_right] - black) * inv_range, 0.0, 1.0)
        
        R, G, B = 0.0, 0.0, 0.0
        
        if color_idx == 0:  # Red center
            v00 = ti.math.clamp((bayer[r_up, c_left] - black) * inv_range, 0.0, 1.0)
            v02 = ti.math.clamp((bayer[r_up, c_right] - black) * inv_range, 0.0, 1.0)
            v20 = ti.math.clamp((bayer[r_down, c_left] - black) * inv_range, 0.0, 1.0)
            v22 = ti.math.clamp((bayer[r_down, c_right] - black) * inv_range, 0.0, 1.0)
            
            R = v11
            G = (v01 + v10 + v12 + v21) * 0.25
            B = (v00 + v02 + v20 + v22) * 0.25
        elif color_idx == 2:  # Blue center
            v00 = ti.math.clamp((bayer[r_up, c_left] - black) * inv_range, 0.0, 1.0)
            v02 = ti.math.clamp((bayer[r_up, c_right] - black) * inv_range, 0.0, 1.0)
            v20 = ti.math.clamp((bayer[r_down, c_left] - black) * inv_range, 0.0, 1.0)
            v22 = ti.math.clamp((bayer[r_down, c_right] - black) * inv_range, 0.0, 1.0)
            
            B = v11
            G = (v01 + v10 + v12 + v21) * 0.25
            R = (v00 + v02 + v20 + v22) * 0.25
        else:  # Green center
            G = v11
            horiz_idx = c00 if r_mod == 0 else c10
            if (c_left % 2) != 0:
                horiz_idx = c01 if r_mod == 0 else c11
                
            if horiz_idx == 0:
                R = (v10 + v12) * 0.5
                B = (v01 + v21) * 0.5
            else:
                B = (v10 + v12) * 0.5
                R = (v01 + v21) * 0.5
                
        dst[r, c, 0] = R
        dst[r, c, 1] = G
        dst[r, c, 2] = B

@ti.kernel
def _bilinear_green_to_grayscale_1channel_fused_kernel(
    bayer: ti.types.ndarray(),
    dst: ti.types.ndarray(),
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
    inv_range = 1.0 / ti.max(1.0, white - black)
    
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
            raw_val = ti.math.clamp((bayer[r, c] - black) * inv_range, 0.0, 1.0)
            gain = wb_g1 if color_idx == 1 else wb_g2
            dst[r, c] = raw_val * gain
        else:
            c_left = ti.max(0, c - 1)
            c_right = ti.min(w - 1, c + 1)
            r_up = ti.max(0, r - 1)
            r_down = ti.min(h - 1, r + 1)
            
            raw_l = ti.math.clamp((bayer[r, c_left] - black) * inv_range, 0.0, 1.0)
            raw_r = ti.math.clamp((bayer[r, c_right] - black) * inv_range, 0.0, 1.0)
            raw_u = ti.math.clamp((bayer[r_up, c] - black) * inv_range, 0.0, 1.0)
            raw_d = ti.math.clamp((bayer[r_down, c] - black) * inv_range, 0.0, 1.0)
            
            gain_l = _get_green_gain(r, c_left, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_r = _get_green_gain(r, c_right, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_u = _get_green_gain(r_up, c, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_d = _get_green_gain(r_down, c, c00, c01, c10, c11, wb_g1, wb_g2)
            
            dst[r, c] = (raw_l * gain_l + raw_r * gain_r + raw_u * gain_u + raw_d * gain_d) * 0.25

@ti.kernel
def _bilinear_green_half_res_fused_kernel(
    bayer: ti.types.ndarray(),
    dst: ti.types.ndarray(),
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
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    for r, c in ti.ndrange(h // 2, w // 2):
        r_orig = r * 2
        c_orig = c * 2
        
        g_val = 0.0
        g_count = 0.0
        
        for dr, dc in ti.static([(0, 0), (0, 1), (1, 0), (1, 1)]):
            nr, nc = r_orig + dr, c_orig + dc
            
            color_idx = 1
            nr_mod = nr % 2
            nc_mod = nc % 2
            if nr_mod == 0:
                color_idx = c00 if nc_mod == 0 else c01
            else:
                color_idx = c10 if nc_mod == 0 else c11
                
            is_green = (color_idx == 1) or (color_idx == 3)
            if is_green:
                raw_val = ti.math.clamp((bayer[nr, nc] - black) * inv_range, 0.0, 1.0)
                gain = wb_g1 if color_idx == 1 else wb_g2
                g_val += raw_val * gain
                g_count += 1.0
                
        if g_count > 0.0:
            dst[r, c] = g_val / g_count
        else:
            dst[r, c] = ti.math.clamp((bayer[r_orig, c_orig] - black) * inv_range, 0.0, 1.0)

@ti.kernel
def _bilinear_rgb_half_res_fused_kernel(
    bayer: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
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
    linear: ti.i32,
):
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    for r, c in ti.ndrange(h // 2, w // 2):
        r_orig = r * 2
        c_orig = c * 2
        
        val_00 = ti.math.clamp((bayer[r_orig, c_orig] - black) * inv_range, 0.0, 1.0)
        val_01 = ti.math.clamp((bayer[r_orig, c_orig + 1] - black) * inv_range, 0.0, 1.0)
        val_10 = ti.math.clamp((bayer[r_orig + 1, c_orig] - black) * inv_range, 0.0, 1.0)
        val_11 = ti.math.clamp((bayer[r_orig + 1, c_orig + 1] - black) * inv_range, 0.0, 1.0)
        
        R, G1, B, G2 = 0.0, 0.0, 0.0, 0.0
        
        if c00 == 0: R = val_00
        elif c00 == 1: G1 = val_00
        elif c00 == 2: B = val_00
        else: G2 = val_00
        
        if c01 == 0: R = val_01
        elif c01 == 1: G1 = val_01
        elif c01 == 2: B = val_01
        else: G2 = val_01
        
        if c10 == 0: R = val_10
        elif c10 == 1: G1 = val_10
        elif c10 == 2: B = val_10
        else: G2 = val_10
        
        if c11 == 0: R = val_11
        elif c11 == 1: G1 = val_11
        elif c11 == 2: B = val_11
        else: G2 = val_11
        
        G_raw = (G1 + G2) * 0.5
        min_raw = ti.min(R, ti.min(G_raw, B))
        max_raw = ti.max(R, ti.max(G_raw, B))
        
        factor = ti.math.clamp((max_raw - 0.55) / 0.43, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        ratio = min_raw / ti.max(1e-5, max_raw)
        neutrality = ti.math.clamp((ratio - 0.40) / 0.45, 0.0, 1.0)
        neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)

        final_factor = factor * neutrality

        R = R * wb_r
        G = (G1 * wb_g1 + G2 * wb_g2) * 0.5
        B = B * wb_b

        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - final_factor) + L * final_factor
        G = G * (1.0 - final_factor) + L * final_factor
        B = B * (1.0 - final_factor) + L * final_factor
        
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        if linear == 1:
            # Linear RGB (WB + color matrix, no gamma) for natural tonemapping.
            dst[r, c, 0] = ti.math.clamp(sR, 0.0, 1.0)
            dst[r, c, 1] = ti.math.clamp(sG, 0.0, 1.0)
            dst[r, c, 2] = ti.math.clamp(sB, 0.0, 1.0)
        else:
            sR = sR / ti.math.sqrt(1.0 + sR * sR)
            sG = sG / ti.math.sqrt(1.0 + sG * sG)
            sB = sB / ti.math.sqrt(1.0 + sB * sB)

            dst[r, c, 0] = _fast_gamma(ti.math.clamp(sR, 0.0, 1.0))
            dst[r, c, 1] = _fast_gamma(ti.math.clamp(sG, 0.0, 1.0))
            dst[r, c, 2] = _fast_gamma(ti.math.clamp(sB, 0.0, 1.0))

def compile_bilinear_demosaice_tcm(
    arch=ti.cuda,
    save_path="bilinear_demosaice_cuda.tcm",
):
    print(f"\n>>> Compiling Bilinear Demosaice AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    register_bilinear_graphs(
        module,
        kernels={
            "fast": _bilinear_demosaice_fused_kernel,
            "pure": _pure_bilinear_demosaice_kernel,
            "gray1ch": _bilinear_green_to_grayscale_1channel_fused_kernel,
            "half_res": _bilinear_green_half_res_fused_kernel,
            "rgb_half_res": _bilinear_rgb_half_res_fused_kernel,
            "rgb_to_bgr_i32": rgb_to_bgr_i32,
        },
    )

    archive_module(module, save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()


if __name__ == "__main__":
    # Default: desktop CUDA target-qualified artifact (matches engine loader).
    compile_bilinear_demosaice_tcm(arch=ti.cuda)
