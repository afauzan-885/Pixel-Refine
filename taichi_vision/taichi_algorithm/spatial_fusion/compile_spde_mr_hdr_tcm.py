"""Compile target-qualified AOT graphs for SPDE-MR HDR patch scoring."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("AOT_MODE", "0")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import taichi as ti

from taichi_vision.taichi_aot.artifact_targets import detect_target
from taichi_vision.taichi_algorithm.spatial_fusion.spde_mr_hdr import (
    _expand_patch_maps_f32,
    _score_patch_grid_f32,
)


def _nd(name: str, dtype, ndim: int):
    return ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype, ndim=ndim)


def _scalar(name: str, dtype):
    return ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, dtype)


def _add_graph(module, name, kernel, *args):
    builder = ti.graph.GraphBuilder()
    builder.dispatch(kernel, *args)
    module.add_graph(name, builder.compile())


def _register(module):
    f32, i32 = ti.f32, ti.i32
    _add_graph(
        module,
        "hdr_spde_mr_patch_score_f32",
        _score_patch_grid_f32,
        _nd("reference_gray", f32, 2),
        _nd("frame_gray", f32, 2),
        _nd("patch_quality", f32, 2),
        _nd("patch_stable", i32, 2),
        _scalar("patch_rows", i32),
        _scalar("patch_cols", i32),
        _scalar("patch_size", i32),
        _scalar("stride", i32),
        _scalar("exposure_center", f32),
        _scalar("exposure_sigma", f32),
        _scalar("structure_threshold", f32),
    )
    _add_graph(
        module,
        "hdr_spde_mr_patch_expand_f32",
        _expand_patch_maps_f32,
        _nd("patch_quality", f32, 2),
        _nd("patch_stable", i32, 2),
        _nd("valid_mask", i32, 2),
        _nd("quality", f32, 2),
        _nd("stable", i32, 2),
        _nd("policy_weight", f32, 2),
        _scalar("height", i32),
        _scalar("width", i32),
        _scalar("patch_rows", i32),
        _scalar("patch_cols", i32),
    )


def compile_spde_mr_hdr_tcm(
    *, backend: str, output_path: str | Path, overwrite: bool = False
) -> str:
    """Compile one explicit target; replace an artifact only when requested."""
    target = detect_target(backend=backend)
    output = Path(output_path).resolve()
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
        help="One target only; defaults to the project CPU baseline.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Target-qualified TCM directory (defaults to aot_tcm/<target>).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace this module's existing target artifact explicitly.",
    )
    args = parser.parse_args()
    target = detect_target(backend=args.backend)
    output_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir
        else Path(__file__).resolve().parents[1] / "aot_tcm" / target.target_id
    )
    output_path = output_dir / target.artifact_name("hdr_spde_mr")
    compile_spde_mr_hdr_tcm(
        backend=args.backend,
        output_path=output_path,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
