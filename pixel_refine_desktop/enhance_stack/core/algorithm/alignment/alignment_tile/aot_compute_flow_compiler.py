import taichi as ti
import os
import sys

# Ambil lokasi folder skrip saat ini (alignment_tile)
file_dir = os.path.dirname(os.path.abspath(__file__))

# Melompat ke atas hingga mencapai folder di luar 'pixel_refine_desktop'
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))

if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_flow import (
    process_single_layer,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import (
    _downsample_2x_kernel,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ncc import (
    _compute_global_zncc_surface,
    _reduce_min_2d_kernel,
)


def aot_compute_flow_compiler():
    arch = ti.vulkan
    print("\n>>> Compiling COMPUTE FLOW AOT for: VULKAN (GRID-BROADCAST UNIFIED)")
    ti.init(arch=arch, offline_cache=False)
    mod = ti.aot.Module(arch)

    # Inisialisasi Graph Builder
    g = ti.graph.GraphBuilder()

    # =========================================================
    # 1. DEKLARASI ARGUMEN
    # =========================================================

    # Piramida L0, L1, L2 (Ref & Comp)
    refs = [
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"ref_l{i}", ti.f32, ndim=2)
        for i in range(3)
    ]
    comps = [
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"comp_l{i}", ti.f32, ndim=2)
        for i in range(3)
    ]

    # Piramida Flow (2 Buffers per Layer - Shared Buffering)
    # 1. flow_l: Buffer Output / Working Flow
    flows = [
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"flow_l{i}", ti.f32, ndim=3)
        for i in range(3)
    ]
    # 2. flow_tmp_l: Buffer untuk Anchor Points (Grid-Broadcast)
    flow_tmps = [
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"flow_tmp_l{i}", ti.f32, ndim=3)
        for i in range(3)
    ]

    # Intermediate buffers untuk downsampling
    tmp_refs = [
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"tmp_ref_l{i}", ti.f32, ndim=2)
        for i in range(1, 4)
    ]
    tmp_comps = [
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"tmp_comp_l{i}", ti.f32, ndim=2)
        for i in range(1, 4)
    ]

    # ZNCC Buffers
    z_surf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zncc_surf", ti.f32, ndim=2)
    z_res = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zncc_res", ti.f32, ndim=1)

    # Konfigurasi
    tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
    tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)
    search_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "search_radius", ti.i32)
    coarse_dist = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "coarse_dist", ti.i32)
    scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    ds_fac = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ds_fac", ti.i32)
    zncc_shift = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "zncc_shift", ti.i32)
    step_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "step_y", ti.i32)
    step_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "step_x", ti.i32)

    # =========================================================
    # 2. MEREKAM GRAPH EKSEKUSI
    # =========================================================

    # FASE A: DOWNSAMPLING PIRAMIDA (L0 -> L1 -> L2)
    # L0 -> L1
    g.dispatch(_downsample_2x_kernel, refs[0], tmp_refs[0])
    g.dispatch(_downsample_2x_kernel, tmp_refs[0], refs[1])
    g.dispatch(_downsample_2x_kernel, comps[0], tmp_comps[0])
    g.dispatch(_downsample_2x_kernel, tmp_comps[0], comps[1])

    # L1 -> L2
    g.dispatch(_downsample_2x_kernel, refs[1], tmp_refs[1])
    g.dispatch(_downsample_2x_kernel, tmp_refs[1], refs[2])
    g.dispatch(_downsample_2x_kernel, comps[1], tmp_comps[1])
    g.dispatch(_downsample_2x_kernel, tmp_comps[1], comps[2])

    # FASE B: GLOBAL ZNCC UNTUK L2
    g.dispatch(_compute_global_zncc_surface, refs[2], comps[2], z_surf, zncc_shift)
    g.dispatch(_reduce_min_2d_kernel, z_surf, z_res)

    # FASE C: MEREKAM PROCESS SINGLE LAYER (L2, L1, L0)
    for i in range(2, -1, -1):
        # Input flow untuk level i adalah output dari level i+1
        prev_flow = flows[i + 1] if i < 2 else None

        process_single_layer(
            ref_layer_gpu=refs[i],
            comp_layer_gpu=comps[i],
            previous_flow_gpu=prev_flow,
            layer_index=i,
            total_layers=3,
            tile_h=tile_h,
            tile_w=tile_w,
            search_dist=coarse_dist,
            downscale_factor=ds_fac,
            g=g,
            # Shared Buffering Mapping:
            flow_out_arg=flows[i],
            flow_tmp_arg=flow_tmps[i],
            z_res_arg=z_res,
            search_radius_arg=search_radius,
            zncc_shift_arg=zncc_shift,
            scale_arg=scale,
            step_y_arg=step_y,
            step_x_arg=step_x,
        )

    # Compile
    mod.add_graph("align_end_to_end_3layer", g.compile())

    # Simpan
    output_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../ui/data/aot_assets")
    )
    os.makedirs(output_dir, exist_ok=True)
    archive_path = os.path.join(output_dir, "compute_flow_vulkan.tcm")

    mod.archive(archive_path)
    print(f"Successfully compiled and archived to: {archive_path}")
    ti.reset()


if __name__ == "__main__":
    aot_compute_flow_compiler()
