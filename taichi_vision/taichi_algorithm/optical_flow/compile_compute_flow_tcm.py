"""Canonical compiler entry point for the resident three-level flow graph.

The kernels remain shared with the maintained alignment implementation.  This
entry point owns only AOT graph registration and artifact staging, so the
backend suite can compile ``compute_flow`` into the same target-qualified
directory as the rest of Taichi Vision.
"""

from __future__ import annotations

import taichi as ti

from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_flow import (
    block_search_kernel,
    search_coarse_level_kernel,
    search_fine_level_kernel,
    upsample_flow_bicubic_kernel,
)


def compile_compute_flow_tcm(
    arch=ti.vulkan,
    save_path: str = "compute_flow.tcm",
) -> str:
    """Compile the resident three-layer coarse-to-fine flow graph."""

    ti.init(arch=arch, offline_cache=False)
    try:
        module = ti.aot.Module(arch)

        image_args = [
            ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype=ti.f32, ndim=2)
            for name in (
                "ref_l0",
                "ref_l1",
                "ref_l2",
                "comp_l0",
                "comp_l1",
                "comp_l2",
            )
        ]
        flow_args = [
            ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype=ti.f32, ndim=3)
            for name in ("flow_l0", "flow_l1", "flow_l2")
        ]
        max_search_radius = ti.graph.Arg(
            ti.graph.ArgKind.SCALAR, "max_search_radius", dtype=ti.i32
        )
        tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", dtype=ti.i32)
        tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", dtype=ti.i32)
        scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.f32)
        search_dist = ti.graph.Arg(
            ti.graph.ArgKind.SCALAR, "search_dist", dtype=ti.i32
        )
        downscale = ti.graph.Arg(
            ti.graph.ArgKind.SCALAR, "downscale", dtype=ti.i32
        )

        ref_l0, ref_l1, ref_l2, comp_l0, comp_l1, comp_l2 = image_args
        flow_l0, flow_l1, flow_l2 = flow_args
        builder = ti.graph.GraphBuilder()
        builder.dispatch(
            block_search_kernel,
            ref_l2,
            comp_l2,
            flow_l2,
            tile_h,
            tile_w,
            max_search_radius,
        )
        builder.dispatch(upsample_flow_bicubic_kernel, flow_l2, flow_l1, scale)
        builder.dispatch(
            search_coarse_level_kernel,
            ref_l1,
            comp_l1,
            flow_l1,
            flow_l2,
            flow_l1,
            tile_h,
            tile_w,
            search_dist,
            downscale,
        )
        builder.dispatch(upsample_flow_bicubic_kernel, flow_l1, flow_l0, scale)
        builder.dispatch(
            search_fine_level_kernel,
            ref_l0,
            comp_l0,
            flow_l0,
            flow_l1,
            flow_l0,
            tile_h,
            tile_w,
            downscale,
        )
        module.add_graph("align_end_to_end_3layer", builder.compile())

        # V2 keeps every coarse-to-fine source immutable while the next
        # level is being produced.  The original graph bound ``flow_l1`` and
        # ``flow_l0`` as both input and output of a tile-parallel kernel;
        # neighbouring tiles could then observe a partially written flow.
        # Extra arguments are internal to the resident aligner, so the
        # historical graph and public API remain available as a fallback.
        flow_l1_seed = ti.graph.Arg(
            ti.graph.ArgKind.NDARRAY, "flow_l1_seed", dtype=ti.f32, ndim=3
        )
        flow_l0_seed = ti.graph.Arg(
            ti.graph.ArgKind.NDARRAY, "flow_l0_seed", dtype=ti.f32, ndim=3
        )
        flow_l0_raw = ti.graph.Arg(
            ti.graph.ArgKind.NDARRAY, "flow_l0_raw", dtype=ti.f32, ndim=3
        )
        builder_v2 = ti.graph.GraphBuilder()
        builder_v2.dispatch(
            block_search_kernel,
            ref_l2,
            comp_l2,
            flow_l2,
            tile_h,
            tile_w,
            max_search_radius,
        )
        builder_v2.dispatch(
            upsample_flow_bicubic_kernel, flow_l2, flow_l1_seed, scale
        )
        builder_v2.dispatch(
            search_coarse_level_kernel,
            ref_l1,
            comp_l1,
            flow_l1_seed,
            flow_l2,
            flow_l1,
            tile_h,
            tile_w,
            search_dist,
            downscale,
        )
        builder_v2.dispatch(
            upsample_flow_bicubic_kernel, flow_l1, flow_l0_seed, scale
        )
        builder_v2.dispatch(
            search_fine_level_kernel,
            ref_l0,
            comp_l0,
            flow_l0_seed,
            flow_l1,
            flow_l0_raw,
            tile_h,
            tile_w,
            downscale,
        )
        module.add_graph("align_end_to_end_3layer_v2", builder_v2.compile())
        archive_module(module, save_path)
        return str(save_path)
    finally:
        ti.reset()


__all__ = ["compile_compute_flow_tcm"]
