"""
Compile the Spatial Fusion (Ghost Reduction) AOT module for a backend.

Canonical family-local compiler for ``taichi_vision.taichi_algorithm.spatial_fusion``.
Follows the established per-backend compile convention (see
``compile_gaussian_tcm`` / ``compile_block_matching_tcm``).

Backend resolution is automatic:
  - ``PIXEL_REFINE_AOT_ARCH`` / ``TARGET_BACKEND`` / ``AOT_ARCH`` env markers
    (set by the backend suite worker or engine),
  - otherwise the ACTIVE engine backend from ``engine.py``,
  - or an explicit ``--backend cpu|vulkan|opengl|gles|cuda`` argument.

Usage:
    python compile_spatial_fusion_tcm.py                # engine-controlled backend
    python compile_spatial_fusion_tcm.py --backend cpu  # explicit backend
    python compile_spatial_fusion_tcm.py --backend vulkan --backend cuda
"""

import argparse
import os
import sys

os.environ["AOT_MODE"] = "0"

# Add the project root so ``taichi_vision`` is importable when this script is
# executed directly (the backend suite runs it in a fresh interpreter with the
# root already on sys.path).
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (  # noqa: E402
    _resolve_backend_arch,
    compile_spatial_tcm,
)

_ARCHES = {
    "cpu": "ti.cpu",
    "vulkan": "ti.vulkan",
    "opengl": "ti.opengl",
    "gles": "ti.gles",
    "cuda": "ti.cuda",
}


def compile_spatial_fusion_tcm(arch=None, suffix=None, out_dir=None, save_path=None):
    """Compile the spatial-merging TCM (engine-controlled backend by default).

    ``save_path`` supports the backend-suite ``path`` calling convention.
    """
    return compile_spatial_tcm(
        arch=arch, suffix=suffix, out_dir=out_dir, save_path=save_path
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compile the Spatial Fusion AOT module."
    )
    parser.add_argument(
        "--backend",
        action="append",
        choices=tuple(_ARCHES),
        help="Backend to compile; may be given more than once. "
             "Default: resolved from engine/env (automatic).",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: app assets or PIXEL_REFINE_SPATIAL_TCM_OUTPUT_DIR).",
    )
    args = parser.parse_args()

    if args.backend:
        import taichi as ti

        arch_map = {
            "cpu": ti.cpu,
            "vulkan": ti.vulkan,
            "opengl": ti.opengl,
            "gles": ti.gles,
            "cuda": ti.cuda,
        }
        for backend in args.backend:
            compile_spatial_tcm(
                arch=arch_map[backend], suffix=backend, out_dir=args.out_dir
            )
    else:
        # engine.py / env controlled backend → fully automatic.
        arch, suffix = _resolve_backend_arch()
        compile_spatial_tcm(arch=arch, suffix=suffix, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
