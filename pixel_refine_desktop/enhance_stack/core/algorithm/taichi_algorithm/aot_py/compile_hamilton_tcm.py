import taichi as ti
import os
import sys

# Setup path to find taichi_algorithm
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Set AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

# --- Define JIT Kernels for Compiler-Time only ---


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
    """Pass 0: Fused Pre-Processing Kernel.
    Performs clamping, normalization, and white balance gain scaling in a single pass.
    """
    for r, c in ti.ndrange(h, w):
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
    """Pass 1: Hamilton-Adams Edge-Directed Green Channel Reconstruction."""
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
    """Pass 2: Red and Blue Reconstruction using Color Difference Interpolation."""
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

        if color_idx == 0:  # Red pixel
            R = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                b_diff = (
                    (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1])
                    + (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1])
                    + (wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                    + (wb_bayer[r + 1, c + 1] - green[r + 1, c + 1])
                ) * 0.25
                B = G + b_diff
            else:
                B = G

        elif color_idx == 2:  # Blue pixel
            B = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                r_diff = (
                    (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1])
                    + (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1])
                    + (wb_bayer[r + 1, c - 1] - green[r - 1, c - 1])
                    + (wb_bayer[r + 1, c + 1] - green[r + 1, c + 1])
                ) * 0.25
                R = G + r_diff
            else:
                R = G

        else:  # Green pixel
            is_red_horizontal = False
            if r_mod == 0:
                other_color = c00 if c_mod == 1 else c01
                is_red_horizontal = other_color == 0
            else:
                other_color = c10 if c_mod == 1 else c11
                is_red_horizontal = other_color == 0

            if is_red_horizontal:  # Red is Horizontal, Blue is Vertical
                if c > 0 and c < w - 1:
                    r_diff = (
                        (wb_bayer[r, c - 1] - green[r, c - 1])
                        + (wb_bayer[r, c + 1] - green[r, c + 1])
                    ) * 0.5
                    R = G + r_diff
                else:
                    R = G

                if r > 0 and r < h - 1:
                    b_diff = (
                        (wb_bayer[r - 1, c] - green[r - 1, c])
                        + (wb_bayer[r + 1, c] - green[r + 1, c])
                    ) * 0.5
                    B = G + b_diff
                else:
                    B = G

            else:  # Blue is Horizontal, Red is Vertical
                if r > 0 and r < h - 1:
                    r_diff = (
                        (wb_bayer[r - 1, c] - green[r - 1, c])
                        + (wb_bayer[r + 1, c] - green[r + 1, c])
                    ) * 0.5
                    R = G + r_diff
                else:
                    R = G

                if c > 0 and c < w - 1:
                    b_diff = (
                        (wb_bayer[r, c - 1] - green[r, c - 1])
                        + (wb_bayer[r, c + 1] - green[r, c + 1])
                    ) * 0.5
                    B = G + b_diff
                else:
                    B = G

        # --- Advanced Highlight Recovery & Desaturation (executed in white-balanced camera space) ---
        # 1. Estimate RAW Bayer values (before white balance)
        R_raw = R / ti.max(0.1, wb_r)
        G_raw = G / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
        B_raw = B / ti.max(0.1, wb_b)

        # 2. Inpainting-based Highlight Reconstruction
        # If any channel is approaching or exceeds the clipping limit, reconstruct using local ratios of HEALTHY unclipped pixels
        clip_limit = 0.80
        healthy_limit = 0.72 # Only use neighbor pixels that are completely healthy (unclipped) to prevent skewing ratios
        
        if R_raw > clip_limit or B_raw > clip_limit or G_raw > clip_limit:
            sum_r_ratio = 0.0
            count_r = 0.0
            sum_b_ratio = 0.0
            count_b = 0.0
            
            # Search 5x5 neighborhood for completely healthy ratios
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < h and nc >= 0 and nc < w:
                        n_color_idx = 1
                        nr_mod = nr % 2
                        nc_mod = nc % 2
                        if nr_mod == 0:
                            n_color_idx = c00 if nc_mod == 0 else c01
                        else:
                            n_color_idx = c10 if nc_mod == 0 else c11
                        
                        n_raw = wb_bayer[nr, nc]
                        n_green = green[nr, nc]
                        
                        if n_color_idx == 0: # Red neighbor
                            n_r_raw = n_raw / ti.max(0.1, wb_r)
                            n_g_raw = n_green / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
                            # Only use completely healthy pixels (no channel is clipped/skewed)
                            if n_r_raw < healthy_limit and n_g_raw < healthy_limit and n_g_raw > 0.01:
                                weight = 1.0 / (1.0 + ti.cast(dr*dr + dc*dc, ti.f32))
                                sum_r_ratio += (n_r_raw / n_g_raw) * weight
                                count_r += weight
                        elif n_color_idx == 2: # Blue neighbor
                            n_b_raw = n_raw / ti.max(0.1, wb_b)
                            n_g_raw = n_green / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
                            # Only use completely healthy pixels
                            if n_b_raw < healthy_limit and n_g_raw < healthy_limit and n_g_raw > 0.01:
                                weight = 1.0 / (1.0 + ti.cast(dr*dr + dc*dc, ti.f32))
                                sum_b_ratio += (n_b_raw / n_g_raw) * weight
                                count_b += weight

            if count_r > 0.0 and R_raw > clip_limit:
                ratio_r = sum_r_ratio / count_r
                R_raw = ti.max(R_raw, G_raw * ratio_r)
            if count_b > 0.0 and B_raw > clip_limit:
                ratio_b = sum_b_ratio / count_b
                B_raw = ti.max(B_raw, G_raw * ratio_b)
            
            # Re-scale back to white-balanced space
            R = R_raw * wb_r
            B = B_raw * wb_b

        # 3. Compute saturation metrics on restored/inpainted channels
        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))

        # 4. Calculate highlight desaturation factor
        # Smoothly blend to neutral white as we approach clipping to prevent magenta/cyan casts
        factor = ti.math.clamp((max_raw - 0.75) / 0.23, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        final_factor = factor

        # 5. Reconstruct and blend in white-balanced space to eliminate magenta artifacts in extreme highlights
        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - final_factor) + L * final_factor
        G = G * (1.0 - final_factor) + L * final_factor
        B = B * (1.0 - final_factor) + L * final_factor

        # 6. Direct camera linear RGB output normalized by maximum white balance gain to prevent highlight clipping
        max_wb = ti.max(wb_r, ti.max(wb_g1, ti.max(wb_b, wb_g2)))
        dst[r, c, 0] = ti.math.clamp(R / max_wb, 0.0, 1.0)
        dst[r, c, 1] = ti.math.clamp(G / max_wb, 0.0, 1.0)
        dst[r, c, 2] = ti.math.clamp(B / max_wb, 0.0, 1.0)


@ti.kernel
def _rgb_to_bgr_i32_kernel(
    src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    dst: ti.types.ndarray(dtype=ti.i32, ndim=3),
    h: ti.i32,
    w: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        val_r = ti.math.clamp(src[r, c, 0] * 65535.0 + 0.5, 0.0, 65535.0)
        val_g = ti.math.clamp(src[r, c, 1] * 65535.0 + 0.5, 0.0, 65535.0)
        val_b = ti.math.clamp(src[r, c, 2] * 65535.0 + 0.5, 0.0, 65535.0)

        dst[r, c, 0] = ti.cast(ti.round(val_b), ti.i32)
        dst[r, c, 1] = ti.cast(ti.round(val_g), ti.i32)
        dst[r, c, 2] = ti.cast(ti.round(val_r), ti.i32)


def compile_hamilton_tcm(arch=ti.vulkan, save_path="hamilton_vulkan.tcm"):
    print(f"\n>>> Compiling Hamilton Demosaicing AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # 1. Define graph builder
    g_hamilton = ti.graph.GraphBuilder()

    # Inputs and Outputs
    bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bayer", ti.f32, ndim=2)
    wb_bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "wb_bayer", ti.f32, ndim=2)
    green_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "green", ti.f32, ndim=2)
    cmatrix_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cmatrix", ti.f32, ndim=2)
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

    # Scalars
    wb_r_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_r", ti.f32)
    wb_g1_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_g1", ti.f32)
    wb_b_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_b", ti.f32)
    wb_g2_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_g2", ti.f32)
    black_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "black", ti.f32)
    white_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "white", ti.f32)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)

    c00_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c00", ti.i32)
    c01_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c01", ti.i32)
    c10_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c10", ti.i32)
    c11_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c11", ti.i32)

    # Dispatch Pass 0: Pre-process
    g_hamilton.dispatch(
        _preprocess_bayer_kernel,
        bayer_arg,
        wb_bayer_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        black_arg,
        white_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )

    # Dispatch Pass 1: Green Reconstruction
    g_hamilton.dispatch(
        _ha_green_interpolation_kernel_opt,
        wb_bayer_arg,
        green_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )

    # Dispatch Pass 2: Red/Blue Reconstruction & Color/Gamma Transform
    g_hamilton.dispatch(
        _ha_red_blue_interpolation_kernel_opt,
        wb_bayer_arg,
        green_arg,
        cmatrix_arg,
        dst_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )

    # Add compiled graph to module
    module.add_graph("hamilton_demosaic", g_hamilton.compile())

    # Define RGB to BGR i32 graph builder
    g_conv = ti.graph.GraphBuilder()
    src_conv_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_conv_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=3)
    h_conv_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_conv_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    g_conv.dispatch(
        _rgb_to_bgr_i32_kernel, src_conv_arg, dst_conv_arg, h_conv_arg, w_conv_arg
    )
    module.add_graph("rgb_to_bgr_i32", g_conv.compile())

    # Archive the module
    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(script_dir, "../aot_tcm"))
    os.makedirs(assets_dir, exist_ok=True)

    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]

    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"hamilton_{suffix}.tcm"))
        try:
            compile_hamilton_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
            compile_hamilton_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
