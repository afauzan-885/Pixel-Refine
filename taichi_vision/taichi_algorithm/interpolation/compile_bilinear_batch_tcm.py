"""Compile the source-resident batched bilinear offset graphs.

This is a separate module so existing ``bilinear_*.tcm`` artifacts remain
loadable while the batch graph is validated backend by backend.  The public
resize API loads it opportunistically and keeps the established offset path
as a fallback when an artifact is not available.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import sys

os.environ.setdefault("AOT_MODE", "0")
# The compiler should not initialize the developer's selected graphics bridge
# merely by importing the source package.  Taichi's compiler target is chosen
# explicitly by ``--backend`` below.
os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", "cpu")

import taichi as ti

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
from taichi_vision.taichi_algorithm.interpolation import bilinear_interpolation as bilinear


ARCHES = {
    "cpu": ti.cpu,
    "vulkan": ti.vulkan,
    "opengl": ti.opengl,
    "cuda": ti.cuda,
}


def _target_id(backend):
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


def compile_bilinear_batch(backend=None, output=None, *, arch=None, save_path=None):
    """Compile the batched graph archive.

    ``compile_aot_backend_suite`` invokes colocated compilers with the common
    ``(arch=..., save_path=...)`` contract.  The explicit ``backend``/``output``
    arguments remain supported for direct command-line use and for developers
    compiling one target interactively.
    """
    backend = str(backend or os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan")).lower()
    if backend not in ARCHES:
        raise ValueError(f"unsupported backend: {backend}")
    target_arch = arch or ARCHES[backend]
    target_id = _target_id(backend)
    if save_path is not None:
        output = save_path
    if output is None:
        output = (
            ROOT
            / "taichi_vision"
            / "taichi_algorithm"
            / "aot_tcm"
            / target_id
            / f"bilinear_batch_{target_id}.tcm"
        )
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f">>> Compiling bilinear batch graphs for {target_id}")
    ti.init(arch=target_arch, offline_cache=False)
    module = ti.aot.Module(target_arch)

    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    offsets = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "offsets", ti.i32, ndim=2)
    h_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src", ti.i32)
    w_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src", ti.i32)
    h_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst", ti.i32)
    w_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst", ti.i32)

    graph = ti.graph.GraphBuilder()
    graph.dispatch(
        bilinear._bilinear_resize_batch_offset_kernel,
        src_2d,
        dst_2d,
        offsets,
        h_src,
        w_src,
        h_dst,
        w_dst,
    )
    module.add_graph("bilinear_resize_batch_offset_f32_2d", graph.compile())

    src_3d = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY,
        "src",
        ti.types.vector(3, ti.f32),
        ndim=2,
    )
    dst_3d = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY,
        "dst",
        ti.types.vector(3, ti.f32),
        ndim=3,
    )
    graph_vec = ti.graph.GraphBuilder()
    graph_vec.dispatch(
        bilinear._bilinear_resize_batch_offset_kernel_vec3,
        src_3d,
        dst_3d,
        offsets,
        h_src,
        w_src,
        h_dst,
        w_dst,
    )
    module.add_graph("bilinear_resize_batch_offset_f32_3d", graph_vec.compile())

    archive_module(module, output)
    ti.reset()
    print(f"  -> {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", action="append", choices=tuple(ARCHES), default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    for backend in args.backend or ["vulkan"]:
        compile_bilinear_batch(
            backend,
            args.output if len(args.backend or []) == 1 else None,
        )
