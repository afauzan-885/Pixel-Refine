"""Canonical compiler entry point for the image normalization graphs."""

from __future__ import annotations

import taichi as ti

from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.tile_motion.image_utils_aot.normalize_image_kernels import (
    normalize_f32_to_vec3_kernel,
    normalize_vec3_f32_to_vec3_f32_kernel,
)


def compile_normalize_image_tcm(
    arch=ti.vulkan,
    save_path: str = "normalize_image.tcm",
) -> str:
    """Compile both scalar and vec3 normalization graphs."""

    ti.init(arch=arch, offline_cache=False)
    try:
        module = ti.aot.Module(arch)
        inv_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_scale", ti.f32)
        src_f32 = ti.graph.Arg(
            ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2
        )
        src_vec3 = ti.graph.Arg(
            ti.graph.ArgKind.NDARRAY,
            "src_vec3",
            ti.types.vector(3, ti.f32),
            ndim=2,
        )
        dst_vec3 = ti.graph.Arg(
            ti.graph.ArgKind.NDARRAY,
            "dst",
            ti.types.vector(3, ti.f32),
            ndim=2,
        )

        scalar_graph = ti.graph.GraphBuilder()
        scalar_graph.dispatch(
            normalize_f32_to_vec3_kernel, src_f32, dst_vec3, inv_scale
        )
        module.add_graph("normalize_f32_to_vec3", scalar_graph.compile())

        vector_graph = ti.graph.GraphBuilder()
        vector_graph.dispatch(
            normalize_vec3_f32_to_vec3_f32_kernel,
            src_vec3,
            dst_vec3,
            inv_scale,
        )
        module.add_graph(
            "normalize_vec3_f32_to_vec3_f32", vector_graph.compile()
        )
        archive_module(module, save_path)
        return str(save_path)
    finally:
        ti.reset()


__all__ = ["compile_normalize_image_tcm"]
