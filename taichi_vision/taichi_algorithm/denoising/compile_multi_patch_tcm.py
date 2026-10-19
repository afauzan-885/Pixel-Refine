"""Compile the target-qualified FusionNet multi-patch search TCM."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ["AOT_MODE"] = "0"

import taichi as ti

from .multi_patch_kernels import (
    multi_patch_compose_dense_flow_kernel,
    multi_patch_topk_kernel,
)


def compile_multi_patch_tcm(arch, output_path):
    """Compile only the requested backend and write to an explicit path."""
    ti.init(arch=arch, offline_cache=False)
    actual_arch = getattr(ti.lang.impl.current_cfg(), "arch", None)
    if actual_arch is not None and int(actual_arch) != int(arch):
        raise RuntimeError(
            f"Taichi fell back to {actual_arch} while compiling {arch}; refusing to package a mismatched TCM"
        )

    module = ti.aot.Module(arch)
    src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reference", ti.f32, ndim=3)
    candidate = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "candidate", ti.f32, ndim=3)
    offsets = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "offsets", ti.i32, ndim=2)
    indices = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "indices", ti.i32, ndim=3)
    i32 = ti.graph.ArgKind.SCALAR
    height = ti.graph.Arg(i32, "height", ti.i32)
    width = ti.graph.Arg(i32, "width", ti.i32)
    channels = ti.graph.Arg(i32, "channels", ti.i32)
    candidate_count = ti.graph.Arg(i32, "candidate_count", ti.i32)
    neighbor_count = ti.graph.Arg(i32, "neighbor_count", ti.i32)
    cell_size = ti.graph.Arg(i32, "cell_size", ti.i32)
    graph = ti.graph.GraphBuilder()
    graph.dispatch(
        multi_patch_topk_kernel,
        src,
        candidate,
        offsets,
        indices,
        height,
        width,
        channels,
        candidate_count,
        neighbor_count,
        cell_size,
    )
    module.add_graph("deno_multi_patch_topk_f32_v1", graph.compile())

    rank_indices = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "rank_indices", ti.i32, ndim=2)
    base_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "base_flow", ti.f32, ndim=3)
    output_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output_flow", ti.f32, ndim=3)
    index_height = ti.graph.Arg(i32, "index_height", ti.i32)
    index_width = ti.graph.Arg(i32, "index_width", ti.i32)
    flow_height = ti.graph.Arg(i32, "flow_height", ti.i32)
    flow_width = ti.graph.Arg(i32, "flow_width", ti.i32)
    full_height = ti.graph.Arg(i32, "full_height", ti.i32)
    full_width = ti.graph.Arg(i32, "full_width", ti.i32)
    flow_candidate_count = ti.graph.Arg(i32, "candidate_count", ti.i32)
    flow_graph = ti.graph.GraphBuilder()
    flow_graph.dispatch(
        multi_patch_compose_dense_flow_kernel,
        rank_indices,
        offsets,
        base_flow,
        output_flow,
        index_height,
        index_width,
        flow_height,
        flow_width,
        full_height,
        full_width,
        flow_candidate_count,
    )
    module.add_graph("deno_multi_patch_compose_dense_flow_f32_v1", flow_graph.compile())

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module

    archive_module(module, output_path)
    ti.reset()
    return str(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("cpu", "cuda", "vulkan", "opengl", "gles"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    arch = {
        "cpu": ti.cpu,
        "cuda": ti.cuda,
        "vulkan": ti.vulkan,
        "opengl": ti.opengl,
        "gles": ti.gles,
    }[args.backend]
    print(compile_multi_patch_tcm(arch, args.output))


if __name__ == "__main__":
    main()
