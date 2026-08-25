"""Compile target-qualified batch Lucas--Kanade TCM archives."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import sys

os.environ.setdefault("AOT_MODE", "0")
os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", "cpu")

import taichi as ti

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
from taichi_vision.taichi_algorithm.optical_flow import lucas_kanade_batch as batch


ARCHES = {
    "cpu": ti.cpu,
    "vulkan": ti.vulkan,
    "opengl": ti.opengl,
    "cuda": ti.cuda,
}


def _target_id(backend: str) -> str:
    machine = platform.machine().lower()
    arch = "arm64" if machine in {"arm64", "aarch64"} else "x86_64"
    os_name = "windows" if sys.platform.startswith("win") else sys.platform
    if backend == "cpu":
        return f"cpu_{arch}_{os_name}"
    vendor = os.environ.get("PIXEL_REFINE_TARGET_VENDOR", "unknown").lower()
    if "nvidia" in vendor or "geforce" in vendor:
        vendor = "nvidia"
    elif "intel" in vendor:
        vendor = "intel"
    elif vendor not in {"amd", "qualcomm", "arm", "apple"}:
        vendor = "unknown"
    suffix = f"_{vendor}" if vendor != "unknown" else ""
    return f"{backend}_{arch}_{os_name}{suffix}"


def compile_lucas_kanade_batch(
    backend=None,
    output=None,
    *,
    arch=None,
    save_path=None,
):
    backend = str(
        backend or os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan")
    ).lower()
    if backend not in ARCHES:
        raise ValueError(f"unsupported backend: {backend}")
    target_arch = arch or ARCHES[backend]
    target_id = _target_id(backend)
    output = save_path or output
    if output is None:
        output = (
            ROOT
            / "taichi_vision"
            / "taichi_algorithm"
            / "aot_tcm"
            / target_id
            / f"lucas_kanade_batch_{target_id}.tcm"
        )
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f">>> Compiling batch Lucas--Kanade graphs for {target_id}")
    ti.init(arch=target_arch, offline_cache=False)
    module = ti.aot.Module(target_arch)

    prev = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "prev", ti.f32, ndim=3)
    next_image = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "next", ti.f32, ndim=3
    )
    init_flow = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "init_flow", ti.f32, ndim=4
    )
    grid_flow = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "grid_flow", ti.f32, ndim=4
    )
    grid_meta = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "grid_meta", ti.f32, ndim=4
    )
    flow_out = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "flow_out", ti.f32, ndim=4
    )
    grid_step = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_step", ti.i32)
    border_margin = ti.graph.Arg(
        ti.graph.ArgKind.SCALAR, "border_margin", ti.i32
    )
    win_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "win_radius", ti.i32)
    iterations = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "iterations", ti.i32)
    epsilon = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "epsilon", ti.f32)
    overlap = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "overlap", ti.f32)
    scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)

    src_batch = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3
    )
    dst_batch = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3
    )
    graph = ti.graph.GraphBuilder()
    graph.dispatch(batch._batch_downsample_2x_kernel, src_batch, dst_batch)
    module.add_graph("flow_lk_batch_downsample_2x_f32", graph.compile())

    upsample_src = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=4
    )
    upsample_dst = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=4
    )
    graph = ti.graph.GraphBuilder()
    graph.dispatch(
        batch._batch_upsample_flow_kernel, upsample_src, upsample_dst, scale
    )
    module.add_graph("flow_lk_batch_upsample_f32", graph.compile())

    graph = ti.graph.GraphBuilder()
    flow_batch = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=4
    )
    graph.dispatch(batch._batch_zero_flow_kernel, flow_batch)
    module.add_graph("flow_lk_batch_zero", graph.compile())

    graph = ti.graph.GraphBuilder()
    graph.dispatch(
        batch._batch_grid_track_kernel,
        prev,
        next_image,
        init_flow,
        grid_flow,
        grid_meta,
        grid_step,
        border_margin,
        win_radius,
        iterations,
        epsilon,
    )
    module.add_graph("flow_lk_batch_grid_track", graph.compile())

    graph = ti.graph.GraphBuilder()
    graph.dispatch(
        batch._batch_dense_interpolate_kernel,
        grid_flow,
        flow_out,
        grid_step,
        border_margin,
        overlap,
    )
    module.add_graph("flow_lk_batch_dense_interpolate", graph.compile())

    graph = ti.graph.GraphBuilder()
    scatter_flow = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "flow_batch", ti.f32, ndim=4
    )
    scatter_out = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "flow_out", ti.f32, ndim=3
    )
    scatter_offsets = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "offsets", ti.i32, ndim=2
    )
    graph.dispatch(
        batch._batch_scatter_core_kernel,
        scatter_flow,
        scatter_out,
        scatter_offsets,
    )
    module.add_graph("flow_lk_batch_scatter_core", graph.compile())

    archive_module(module, output)
    ti.reset()
    print(f"  -> {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", action="append", choices=tuple(ARCHES))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    for backend_name in args.backend or ["vulkan"]:
        compile_lucas_kanade_batch(
            backend_name,
            args.output if len(args.backend or []) == 1 else None,
        )
