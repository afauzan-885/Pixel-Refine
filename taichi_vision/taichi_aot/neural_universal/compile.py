"""Compile the universal kernel pool into ``neural_{backend}.tcm``.

Every kernel in :data:`kernels.ALL_KERNELS` is wrapped in a one-node Taichi AOT
graph so the C API can dispatch it by name with ndarray + scalar arguments. The
artifact manifest is asserted to match the pool exactly: a kernel that fails to
register aborts the build instead of producing a silently incomplete pool.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from .errors import ArtifactError
from .kernels import ALL_KERNELS

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = Path("pixel_refine_desktop/ui/data/aot_assets/neural")
BACKEND_SUBDIRS = {"cuda": "nvidia", "vulkan": "vulkan", "opengl": "opengl", "cpu": "cpu"}
GATED_BACKENDS = ("cpu", "cuda", "vulkan")
SPIRV_UNSUPPORTED_I64_KERNELS = frozenset({
    "nu_cast_f32_i64",
    "nu_cast_i64_f32",
    "nu_cast_i64_i32",
    "nu_cast_i32_i64",
    "nu_copy_i64",
    "nu_fill_i64",
    "nu_range_i64",
})
# Backward-compatible registry test/API name; Vulkan uses the SPIR-V subset.
VULKAN_UNSUPPORTED_I64_KERNELS = SPIRV_UNSUPPORTED_I64_KERNELS


def _kernels_for_backend(backend: str):
    """Return kernels supported by the selected Taichi AOT target profile."""
    if backend in {"vulkan", "opengl"}:
        return tuple(
            kernel for kernel in ALL_KERNELS
            if kernel.__name__ not in SPIRV_UNSUPPORTED_I64_KERNELS
        )
    return tuple(ALL_KERNELS)


def _graph_arguments(kernel):
    """Derive ti.graph.Arg list from the kernel's annotated signature."""
    import taichi as ti
    from taichi.types.ndarray_type import NdarrayType

    args = []
    for arg in kernel._primal.arguments:
        annotation = arg.annotation
        if isinstance(annotation, NdarrayType):
            args.append(
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, arg.name, annotation.dtype,
                             ndim=annotation.ndim)
            )
        else:
            args.append(ti.graph.Arg(ti.graph.ArgKind.SCALAR, arg.name, annotation))
    return args


def compile_pool(backend: str, output_path: Path, *, extra_kernels=(),
                fast_math: Optional[bool] = None) -> Path:
    """Compile the default pool and optional isolated candidate kernels.

    ``extra_kernels`` is intended for a separate candidate target path. It does
    not change :data:`ALL_KERNELS` or the default compiler entry point.
    """
    import taichi as ti
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module

    arch_map = {"cpu": ti.cpu, "cuda": ti.cuda, "vulkan": ti.vulkan, "opengl": ti.opengl}
    if backend not in arch_map:
        raise ArtifactError(f"unknown backend {backend!r}")
    arch = arch_map[backend]
    init_kwargs = {"arch": arch, "offline_cache": False}
    if fast_math is not None:
        init_kwargs["fast_math"] = bool(fast_math)
    ti.init(**init_kwargs)

    module = ti.aot.Module(arch)
    backend_kernels = _kernels_for_backend(backend)
    extras = tuple(extra_kernels)
    if extras and backend != "cpu":
        raise ArtifactError("candidate extension kernels are currently CPU-test-only")
    names = [kernel.__name__ for kernel in backend_kernels]
    extra_names = [kernel.__name__ for kernel in extras]
    if len(set(names + extra_names)) != len(names) + len(extra_names):
        raise ArtifactError("candidate pool kernel names must be unique")
    backend_kernels = backend_kernels + extras
    registered: List[str] = []
    for kernel in backend_kernels:
        name = kernel.__name__
        builder = ti.graph.GraphBuilder()
        builder.dispatch(kernel, *_graph_arguments(kernel))
        module.add_graph(name, builder.compile())
        registered.append(name)

    expected = [kernel.__name__ for kernel in backend_kernels]
    missing = sorted(set(expected) - set(registered))
    if missing:
        raise ArtifactError(f"kernels failed to register: {missing}")

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    archive_module(module, output_path)

    _verify_manifest(output_path, expected)
    size_kb = output_path.stat().st_size / 1024
    print(f"[neural_universal] {backend}: {len(registered)} kernels -> "
          f"{output_path} ({size_kb:.1f} KB)")
    return output_path


def _verify_manifest(tcm_path: Path, expected: List[str]) -> None:
    """The artifact must contain exactly the pool kernels, no more, no less."""
    import zipfile

    with zipfile.ZipFile(tcm_path) as archive:
        names = set(archive.namelist())
        content = None
        if "__content__" in names:
            content = archive.read("__content__").decode("utf-8", errors="replace")
    if content is None:
        return  # unpacked CPU directory layout; presence checked by load()
    graphs = {
        line.split(":", 1)[1].strip()
        for line in content.splitlines()
        if line.startswith("cgraph:")
    }
    missing = sorted(set(expected) - graphs)
    extra = sorted(graphs - set(expected))
    if missing or extra:
        raise ArtifactError(
            f"pool manifest mismatch in {tcm_path.name}: missing={missing} extra={extra}"
        )


def compile_backend_worker(backend: str, target: Path) -> None:
    compile_pool(backend, target)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="all",
                        choices=("cpu", "cuda", "vulkan", "opengl", "all"))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--target-path", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.worker:
        if not args.target_path:
            raise SystemExit("--target-path required in worker mode")
        compile_backend_worker(args.backend, Path(args.target_path))
        return 0

    base = Path(args.output_dir)
    if not base.is_absolute():
        base = ROOT / base
    backends = list(GATED_BACKENDS) if args.backend == "all" else [args.backend]
    failures = {}
    for backend in backends:
        target = base / f"neural_{backend}.tcm"
        command = [
            sys.executable,
            "-m",
            "taichi_vision.taichi_aot.neural_universal.compile",
            "--backend", backend,
            "--worker",
            "--target-path", str(target),
        ]
        result = subprocess.run(
            command, cwd=str(ROOT), env=dict(os.environ, AOT_ARCH=backend)
        )
        if result.returncode != 0:
            failures[backend] = result.returncode
    if failures:
        print(f"[neural_universal] failed backends: {failures}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
