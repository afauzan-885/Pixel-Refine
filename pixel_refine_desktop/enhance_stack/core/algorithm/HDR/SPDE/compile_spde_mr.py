"""Compile the canonical SPDE-MR Taichi graphs into desktop AOT assets."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("AOT_MODE", "0")

_PROJECT_ROOT = Path(__file__).resolve().parents[6]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from taichi_vision.taichi_aot.artifact_targets import detect_target
from taichi_vision.taichi_algorithm.spatial_fusion.compile_spde_mr_hdr_tcm import (
    compile_spde_mr_hdr_tcm,
)


def compile_spde_mr(
    *, backend: str, output_path: str | Path | None = None, overwrite: bool = False
) -> str:
    """Compile one backend to ui/data/aot_assets using the canonical kernels."""
    target = detect_target(backend=backend)
    output = (
        Path(output_path).resolve()
        if output_path is not None
        else Path(__file__).resolve().parents[5]
        / "ui"
        / "data"
        / "aot_assets"
        / target.artifact_name("hdr_spde_mr")
    )
    return compile_spde_mr_hdr_tcm(
        backend=backend,
        output_path=output,
        overwrite=overwrite,
    )


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
    compile_spde_mr(
        backend=args.backend,
        output_path=args.output_path,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
