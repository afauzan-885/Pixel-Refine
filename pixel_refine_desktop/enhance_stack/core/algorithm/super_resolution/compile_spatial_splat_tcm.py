"""Compile the production ``robust_splat`` graph for one Taichi backend.

Examples (run from the project venv):
    python compile_spatial_splat_tcm.py vulkan
    python compile_spatial_splat_tcm.py cuda
    python compile_spatial_splat_tcm.py opengl

Compilation is intentionally one backend per process because Taichi owns a
single active runtime context.  The resulting TCM is only considered usable
after the corresponding native-device parity test passes.
"""

from __future__ import annotations

import os
import sys


os.environ.setdefault("AOT_MODE", "0")

import taichi as ti

from taichi_vision.taichi_algorithm.aot_py.aot_artifact import normalize_tcm

try:
    from . import splat_sr
except ImportError:  # direct script invocation from this directory
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "splat_sr_compile", os.path.join(os.path.dirname(__file__), "splat_sr.py")
    )
    splat_sr = importlib.util.module_from_spec(_spec)
    assert _spec.loader is not None
    _spec.loader.exec_module(splat_sr)


_ARCHES = {
    "vulkan": ti.vulkan,
    "opengl": ti.opengl,
    "cuda": ti.cuda,
    "cpu": ti.cpu,
}


def compile_spatial_splat(backend: str, output_dir: str | None = None) -> str:
    name = str(backend).strip().lower()
    if name not in _ARCHES:
        raise ValueError(f"unsupported backend {backend!r}; choose {sorted(_ARCHES)}")
    output_dir = output_dir or os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../ui/data/aot_assets")
    )
    os.makedirs(output_dir, exist_ok=True)
    try:
        ti.init(arch=_ARCHES[name], offline_cache=False)
        module = ti.aot.Module(_ARCHES[name])
        splat_sr._build_splat_graph(module, include_vector=False)
        out_path = os.path.join(output_dir, f"spatial_splat_{name}.tcm")
        # ``Module.archive`` is the ABI-compatible path used by the existing
        # production TCM builders.  Packing ``module.save`` ourselves can add
        # auxiliary metadata that older native bridges reject at load time.
        module.archive(out_path)
        normalize_tcm(out_path)
        print(f"[AOT] compiled backend={name} artifact={out_path}")
        return out_path
    finally:
        try:
            ti.reset()
        finally:
            pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python compile_spatial_splat_tcm.py <vulkan|cuda|opengl|cpu>")
    compile_spatial_splat(sys.argv[1])
