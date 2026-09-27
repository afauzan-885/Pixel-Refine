"""Compile target-qualified weighted HDR graphs into the desktop AOT assets."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("AOT_MODE", "0")

_PROJECT_ROOT = Path(__file__).resolve().parents[6]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import taichi as ti

from taichi_vision.taichi_aot.artifact_targets import detect_target
from taichi_vision.taichi_algorithm.image_processing.hdr_weighted import (
    accumulate_weighted_rgb_flat_f32,
    hdr_weight_rgb_flat_f32,
)


def _nd(name: str, dtype, ndim: int):
    return ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype, ndim=ndim)


def _scalar(name: str, dtype):
    return ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, dtype)


def _add_graph(module, name: str, kernel, *args):
    builder = ti.graph.GraphBuilder()
    builder.dispatch(kernel, *args)
    module.add_graph(name, builder.compile())


def _register(module):
    f32, i32 = ti.f32, ti.i32
    _add_graph(
        module,
        "hdr_weighted_average_weight_f32",
        hdr_weight_rgb_flat_f32,
        _nd("img_rgb", f32, 1),
        _nd("lap_gray", f32, 2),
        _nd("weight", f32, 2),
        _scalar("h", i32),
        _scalar("w", i32),
        _scalar("noise_sigma", f32),
        _scalar("noise_power", f32),
        _scalar("exposure_sigma", f32),
        _scalar("exposure_power", f32),
        _scalar("detail_power", f32),
        _scalar("saturation_power", f32),
    )
    _add_graph(
        module,
        "hdr_weighted_average_accumulate_f32",
        accumulate_weighted_rgb_flat_f32,
        _nd("lap_rgb", f32, 1),
        _nd("weight", f32, 2),
        _nd("result", f32, 1),
        _scalar("h", i32),
        _scalar("w", i32),
    )


def compile_weighted_average_tcm(
    *, backend: str, output_path: str | Path | None = None, overwrite: bool = False
) -> str:
    """Compile one explicit backend; refuse to replace an existing TCM by default."""
    target = detect_target(backend=backend)
    output = (
        Path(output_path).resolve()
        if output_path is not None
        else Path(__file__).resolve().parents[5]
        / "ui"
        / "data"
        / "aot_assets"
        / target.artifact_name("hdr_weighted_average")
    )
    if output.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing TCM: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    arch = {
        "cpu": ti.cpu,
        "cuda": ti.cuda,
        "vulkan": ti.vulkan,
        "opengl": ti.opengl,
    }.get(target.backend)
    if arch is None:
        raise ValueError(f"Unsupported desktop AOT backend: {target.backend}")

    ti.init(arch=arch, offline_cache=False)
    try:
        module = ti.aot.Module(arch)
        _register(module)
        module.archive(str(output))
    finally:
        ti.reset()
    print(f"[OK] Compiled backend={target.backend} target={target.target_id}")
    print(f"[OK] Archived {output}")
    return str(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        default="cpu",
        choices=("cpu", "cuda", "vulkan", "opengl"),
        help="Compile one backend target. Defaults to the project CPU baseline.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Optional exact TCM path; defaults to ui/data/aot_assets/<target artifact>.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output artifact when it already exists.",
    )
    args = parser.parse_args()
    compile_weighted_average_tcm(
        backend=args.backend,
        output_path=args.output_path,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
