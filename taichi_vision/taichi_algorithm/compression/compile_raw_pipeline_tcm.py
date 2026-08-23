"""Compile the portable pre-demosaic RAW AOT graphs.

The graphs intentionally use an ``i32`` sample transport.  This is lossless
for the supported 8--16 bit sensor containers and avoids assuming native
``u16`` storage on graphics drivers that have not passed the dtype ABI gate.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import taichi as ti

try:
    from .raw_kernels import (
        raw_fuse_accumulate_f32,
        raw_fuse_pair_f32,
        raw_normalize_headroom_i32,
        raw_weight_map_f32,
    )
except ImportError:  # direct ``python compile_raw_pipeline_tcm.py`` support
    # Loading through the package would construct the global AOT engine before
    # the compiler selects its target.  Keep a direct compiler invocation
    # side-effect free and avoid importing ``taichi_algorithm.__init__``.
    import importlib.util

    _kernel_path = Path(__file__).resolve().with_name("raw_kernels.py")
    _spec = importlib.util.spec_from_file_location(
        "pixel_refine_raw_kernels", _kernel_path
    )
    if _spec is None or _spec.loader is None:
        raise ImportError(f"cannot load RAW kernels from {_kernel_path}")
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    raw_fuse_pair_f32 = _module.raw_fuse_pair_f32
    raw_fuse_accumulate_f32 = _module.raw_fuse_accumulate_f32
    raw_normalize_headroom_i32 = _module.raw_normalize_headroom_i32
    raw_weight_map_f32 = _module.raw_weight_map_f32


_TARGET_ARCH = {
    "cpu": ti.cpu,
    "vulkan": ti.vulkan,
    "opengl": ti.opengl,
    "gles": ti.gles,
    "cuda": ti.cuda,
}


def _target_id(arch) -> str:
    explicit = os.environ.get("TARGET_VARIANT", "").strip()
    if explicit:
        return explicit
    backend = next(
        (name for name, value in _TARGET_ARCH.items() if value == arch), "cpu"
    )
    defaults = {
        "cpu": "cpu_x86_64_windows" if os.name == "nt" else "cpu_x86_64_linux",
        "vulkan": "vulkan_x86_64_windows" if os.name == "nt" else "vulkan_x86_64_linux",
        "opengl": "opengl_x86_64_windows" if os.name == "nt" else "opengl_x86_64_linux",
        "gles": "gles_arm64_android" if os.name == "nt" else "gles_arm64_linux",
        "cuda": (
            "cuda_x86_64_windows_nvidia"
            if os.name == "nt"
            else "cuda_arm64_linux_nvidia"
        ),
    }
    return defaults[backend]


def compile_raw_pipeline(arch=ti.cpu, output: str | None = None) -> str:
    target_id = _target_id(arch)
    # Target-suite launchers commonly provide only the qualified variant.
    # Never emit a Vulkan/OpenGL/CUDA-named archive from a CPU compiler.
    target_backend = target_id.split("_", 1)[0].lower()
    requested_backend = next(
        (name for name, value in _TARGET_ARCH.items() if value == arch), "cpu"
    )
    if requested_backend == "cpu" and target_backend != "cpu":
        arch = _TARGET_ARCH.get(target_backend, arch)
    if output is None:
        output = (
            Path(__file__).resolve().parents[1]
            / "aot_tcm"
            / target_id
            / f"compression_raw_{target_id}.tcm"
        )
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ti.init(arch=arch, offline_cache=False)
    actual_arch = ti.lang.impl.current_cfg().arch
    if actual_arch != arch:
        ti.reset()
        raise RuntimeError(
            f"requested {arch}, but Taichi initialized {actual_arch}; "
            "refusing a mislabeled RAW TCM"
        )

    module = ti.aot.Module(arch)

    src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    black = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "black_level", ti.f32, ndim=1)
    white = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "white_level", ti.f32, ndim=1)
    wb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "white_balance", ti.f32, ndim=1)
    phase_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "phase_y", ti.i32)
    phase_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "phase_x", ti.i32)
    origin_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "origin_y", ti.i32)
    origin_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "origin_x", ti.i32)
    apply_wb = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "apply_white_balance", ti.i32)
    exposure = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "exposure_scale", ti.f32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        raw_normalize_headroom_i32,
        src,
        dst,
        black,
        white,
        wb,
        phase_y,
        phase_x,
        origin_y,
        origin_x,
        apply_wb,
        exposure,
    )
    module.add_graph("compression_raw_normalize_headroom_i32", builder.compile())

    reference = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reference", ti.f32, ndim=2)
    current = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current", ti.f32, ndim=2)
    local_weight = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "local_weight", ti.f32, ndim=2
    )
    noise_floor = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "noise_floor", ti.f32)
    sensitivity = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sensitivity", ti.f32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        raw_weight_map_f32, reference, current, dst, noise_floor, sensitivity
    )
    module.add_graph("compression_raw_weight_map_f32", builder.compile())

    reference_weight = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "reference_weight", ti.f32)
    current_weight = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "current_weight", ti.f32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        raw_fuse_pair_f32,
        reference,
        current,
        local_weight,
        dst,
        reference_weight,
        current_weight,
    )
    module.add_graph("compression_raw_fuse_pair_f32", builder.compile())

    accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "accum", ti.f32, ndim=2)
    denominator = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "denominator", ti.f32, ndim=2)
    dst_accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_accum", ti.f32, ndim=2)
    dst_denominator = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "dst_denominator", ti.f32, ndim=2
    )
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        raw_fuse_accumulate_f32,
        accum,
        denominator,
        current,
        local_weight,
        dst_accum,
        dst_denominator,
        current_weight,
    )
    module.add_graph("compression_raw_fuse_accumulate_f32", builder.compile())

    module.archive(str(output_path))
    ti.reset()
    print(f"compiled {output_path}")
    return str(output_path)


def compile_raw_pipeline_aot(arch=ti.cpu, save_path: str | None = None) -> str:
    return compile_raw_pipeline(arch=arch, output=save_path)


if __name__ == "__main__":
    compile_raw_pipeline()
