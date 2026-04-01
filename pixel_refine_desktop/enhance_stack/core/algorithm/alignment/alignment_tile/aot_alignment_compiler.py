import taichi as ti
import os
import sys
import numpy as np

# Menambah root project ke sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../../../../../"))
sys.path.append(project_root)

# Import Kernels
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.preprocess import (
    _fused_full_pipeline_i32_3d_aot,
    _fused_full_pipeline_i32_2d_aot,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import (
    _downsample_2x_kernel,
    _upsample_flow_kernel,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_flow import (
    _initialize_coarsest_flow_kernel,
    _search_coarse_level_kernel,
    _search_fine_level_kernel,
    _parabolic_subpixel_refinement_kernel,
)


def compile_alignment_aot(target_arch=ti.vulkan, output_dir="aot_assets/alignment"):
    """
    Mengompilasi seluruh pipeline alignment ke dalam modul AOT tunggal.
    Satu modul untuk semua tahap: Preprocess -> Pyramid -> Search -> Upsample.
    """
    ti.init(arch=target_arch)
    print(f"[AOT Compiler] Initializing for {target_arch}")

    # --- 1. PREPROCESS GRAPHS ---
    def build_preprocess_graph(is_rgb=True):
        builder = ti.graph.GraphBuilder()
        # Input: i32 Image
        src_ndim = 3 if is_rgb else 2
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=src_ndim)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)

        # Scalar Params
        src_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "src_h", ti.i32)
        src_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "src_w", ti.i32)
        dst_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dst_h", ti.i32)
        dst_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dst_w", ti.i32)
        scale_norm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_norm", ti.f32)
        apply_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "apply_gamma", ti.i32)
        scale_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_gamma", ti.f32)
        gamma_pow = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gamma_pow", ti.f32)
        slope = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "slope", ti.f32)
        cutoff = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cutoff", ti.f32)
        use_sharpen = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_sharpen", ti.i32)

        kernel = (
            _fused_full_pipeline_i32_3d_aot
            if is_rgb
            else _fused_full_pipeline_i32_2d_aot
        )
        builder.dispatch(
            kernel,
            src,
            dst,
            src_h,
            src_w,
            dst_h,
            dst_w,
            scale_norm,
            apply_gamma,
            scale_gamma,
            gamma_pow,
            slope,
            cutoff,
            use_sharpen,
        )
        return builder.compile()

    graph_preprocess_rgb = build_preprocess_graph(is_rgb=True)
    graph_preprocess_gray = build_preprocess_graph(is_rgb=False)

    # --- 2. PYRAMID GRAPH (2X DOWNSAMPLE) ---
    def build_downsample_graph():
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
        h_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src", ti.i32)
        w_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src", ti.i32)
        h_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst", ti.i32)
        w_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst", ti.i32)
        builder.dispatch(_downsample_2x_kernel, src, dst, h_src, w_src, h_dst, w_dst)
        return builder.compile()

    graph_downsample = build_downsample_graph()

    # --- 3. ALIGNMENT GRAPHS ---

    # Init Flow
    def build_init_flow_graph():
        builder = ti.graph.GraphBuilder()
        flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
        h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
        w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
        init_dx = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "init_dx", ti.f32)
        init_dy = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "init_dy", ti.f32)
        builder.dispatch(_initialize_coarsest_flow_kernel, flow, h, w, init_dx, init_dy)
        return builder.compile()

    graph_init_flow = build_init_flow_graph()

    # Search Coarse (L2)
    def build_search_coarse_graph():
        builder = ti.graph.GraphBuilder()
        ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.f32, ndim=2)
        comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp", ti.f32, ndim=2)
        flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
        prev_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "prev_flow", ti.f32, ndim=3)
        out_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_flow", ti.f32, ndim=3)
        h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
        w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
        tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
        tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)
        dist = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dist", ti.i32)
        prev_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "prev_h", ti.i32)
        prev_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "prev_w", ti.i32)
        downscale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "downscale", ti.i32)

        builder.dispatch(
            _search_coarse_level_kernel,
            ref,
            comp,
            flow,
            prev_flow,
            out_flow,
            h,
            w,
            tile_h,
            tile_w,
            dist,
            prev_h,
            prev_w,
            downscale,
        )
        return builder.compile()

    graph_search_coarse = build_search_coarse_graph()

    # Search Fine (L1, L0)
    def build_search_fine_graph():
        builder = ti.graph.GraphBuilder()
        ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.f32, ndim=2)
        comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp", ti.f32, ndim=2)
        flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
        prev_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "prev_flow", ti.f32, ndim=3)
        out_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_flow", ti.f32, ndim=3)
        h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
        w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
        tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
        tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)
        prev_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "prev_h", ti.i32)
        prev_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "prev_w", ti.i32)
        downscale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "downscale", ti.i32)

        builder.dispatch(
            _search_fine_level_kernel,
            ref,
            comp,
            flow,
            prev_flow,
            out_flow,
            h,
            w,
            tile_h,
            tile_w,
            prev_h,
            prev_w,
            downscale,
        )
        return builder.compile()

    graph_search_fine = build_search_fine_graph()

    # Upsample Flow
    def build_upsample_flow_graph():
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
        h_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src", ti.i32)
        w_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src", ti.i32)
        h_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst", ti.i32)
        w_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst", ti.i32)
        scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)

        builder.dispatch(
            _upsample_flow_kernel, src, dst, h_src, w_src, h_dst, w_dst, scale
        )
        return builder.compile()

    graph_upsample_flow = build_upsample_flow_graph()

    # Subpixel Refine
    def build_subpixel_graph():
        builder = ti.graph.GraphBuilder()
        ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.f32, ndim=2)
        comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp", ti.f32, ndim=2)
        flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
        out_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_flow", ti.f32, ndim=3)
        h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
        w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
        tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
        tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)

        builder.dispatch(
            _parabolic_subpixel_refinement_kernel,
            ref,
            comp,
            flow,
            out_flow,
            h,
            w,
            tile_h,
            tile_w,
        )
        return builder.compile()

    graph_subpixel = build_subpixel_graph()

    # --- 4. EXPORT TO MODULE ---
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    mod = ti.aot.Module(target_arch)
    # Preprocess
    mod.add_graph("preprocess_rgb", graph_preprocess_rgb)
    mod.add_graph("preprocess_gray", graph_preprocess_gray)
    # Pyramid
    mod.add_graph("downsample", graph_downsample)
    # Alignment
    mod.add_graph("init_flow", graph_init_flow)
    mod.add_graph("upsample_flow", graph_upsample_flow)
    mod.add_graph("search_coarse", graph_search_coarse)
    mod.add_graph("search_fine", graph_search_fine)
    mod.add_graph("subpixel_refine", graph_subpixel)

    mod.save(output_dir)
    print(f"[AOT Compiler] Full Alignment Module saved to: {output_dir}")


if __name__ == "__main__":
    # Tentukan output dir: pixel_refine_desktop/ui/data/aot_assets/preprocess
    default_out = os.path.join(
        script_dir, "../../../../../", "ui", "data", "aot_assets", "preprocess"
    )
    default_out = os.path.abspath(default_out)

    compile_alignment_aot(target_arch=ti.cuda, output_dir=default_out)
