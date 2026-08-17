"""Compile target-qualified VSAC fundamental-matrix leaves.

The flow/homography RANSAC archive predates the fundamental kernels and is
kept independent because its vector-field ABI is intentionally different.
This compiler packages the existing kernels from :mod:`ransac` without
duplicating their numerical implementation.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("AOT_MODE", "0")

import taichi as ti

from .ransac import (
    generate_fundamental_inlier_mask_kernel,
    ransac_fundamental_kernel,
    vsac_classify_independent_kernel,
)


def _nd(name: str, dtype, ndim: int):
    return ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype, ndim=ndim)


def _scalar(name: str, dtype):
    return ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, dtype)


def _add_graph(module, name: str, kernel, *args):
    builder = ti.graph.GraphBuilder()
    builder.dispatch(kernel, *args)
    module.add_graph(name, builder.compile())


def compile_vsac_tcm(arch=ti.cpu, save_path="vsac_fundamental_cpu.tcm") -> str:
    """Compile the three VSAC leaves into one isolated AOT archive."""

    output = Path(save_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    ti.init(arch=arch, offline_cache=False)
    try:
        module = ti.aot.Module(arch)
        f32, i32 = ti.f32, ti.i32
        _add_graph(
            module,
            "ransac_fundamental",
            ransac_fundamental_kernel,
            _nd("pts1", f32, 2),
            _nd("pts2", f32, 2),
            _scalar("n_pts", i32),
            _scalar("n_hypotheses", i32),
            _scalar("threshold", f32),
            _nd("F_candidates", f32, 2),
            _nd("scores", i32, 1),
            _scalar("seed_offset", i32),
        )
        _add_graph(
            module,
            "generate_fundamental_inlier_mask",
            generate_fundamental_inlier_mask_kernel,
            _nd("pts1", f32, 2),
            _nd("pts2", f32, 2),
            _nd("F_best", f32, 1),
            _scalar("n_pts", i32),
            _scalar("threshold", f32),
            _nd("mask_out", i32, 1),
        )
        _add_graph(
            module,
            "vsac_classify_independent",
            vsac_classify_independent_kernel,
            _nd("pts1", f32, 2),
            _nd("pts2", f32, 2),
            _nd("F_arr", f32, 1),
            _scalar("n_pts", i32),
            _scalar("threshold", f32),
            _scalar("epipole_thresh", f32),
            _nd("indep_count_out", i32, 1),
        )
        module.archive(str(output))
    finally:
        ti.reset()
    return str(output)


__all__ = ["compile_vsac_tcm"]

