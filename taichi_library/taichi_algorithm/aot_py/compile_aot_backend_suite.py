"""Compile maintained Pixel Refine AOT modules for one backend safely.

Every module is compiled in a fresh Python interpreter.  Taichi backend
initialization is process-global and OpenGL contexts are thread-affine, so a
single long-lived compiler process is not reliable across this module suite.
"""

import argparse
import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

try:
    from .aot_artifact import normalize_tcm
except ImportError:  # Direct script execution.
    from aot_artifact import normalize_tcm


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = PROJECT_ROOT / "taichi_library" / "taichi_algorithm" / "aot_tcm"
PACKAGE = "taichi_library.taichi_algorithm.aot_py"
FORK_PYTHON = (
    PROJECT_ROOT
    / "test_algorithm"
    / "taichi_upstream"
    / "stable-v1.7.4-development"
    / "build"
    / "pr-vk-python"
)

# artifact: (compiler module, callable, calling convention, generated aliases)
JOBS = {
    "akaze": ("compile_akaze_tcm", "compile_akaze_tcm", "path", ()),
    "area": ("compile_area_tcm", "compile_area_aot", "path", ()),
    "arm": ("compile_arm_tcm", "compile_arm_tcm", "path", ()),
    "bicubic": ("compile_bicubic_tcm", "compile_bicubic_aot", "path", ()),
    "bilateral_grid": ("compile_bilateral_grid_tcm", "compile_bg_aot", "path", ()),
    "bilinear": ("compile_bilinear_tcm", "compile_bilinear_tcm", "path", ()),
    "bilinear_demosaice": (
        "compile_bilinear_demosaice_tcm",
        "compile_bilinear_demosaice_tcm",
        "path",
        (),
    ),
    "block_matching": (
        "compile_block_matching_tcm",
        "compile_block_matching_flow",
        "out_dir",
        ("lucas_kanade_bm",),
    ),
    "bm3d": ("compile_bm3d_tcm", "compile_bm3d_aot", "path", ()),
    "box_filter": ("compile_box_filter_tcm", "compile_box_filter_aot", "path", ()),
    "common": ("compile_common_tcm", "compile_common_aot", "path", ()),
    "farneback_flow": (
        "compile_farneback_tcm",
        "compile_farneback_flow",
        "out_dir",
        (),
    ),
    "fft": ("compile_fft_tcm", "compile_fft_aot", "path", ()),
    "gaussian": ("compile_gaussian_tcm", "compile_gaussian_tcm", "environment", ()),
    "gradients": ("compile_gradients_tcm", "compile_gradients_aot", "path", ()),
    "hamilton": ("compile_hamilton_tcm", "compile_hamilton_tcm", "path", ()),
    "horn_schunck": (
        "compile_horn_schunck_tcm",
        "compile_horn_schunck_flow",
        "out_dir",
        ("template_flow",),
    ),
    "inpaint": ("compile_inpaint_tcm", "compile_inpaint_aot", "path", ()),
    "jbf": ("compile_jbf_tcm", "compile_jbf_aot", "path", ()),
    "lucas_kanade": (
        "compile_lucas_kanade_tcm",
        "compile_lucas_kanade_flow",
        "out_dir",
        (),
    ),
    "math_ops": ("compile_math_ops", "compile_math_ops", "out_dir", ()),
    "median_filter": ("compile_median_tcm", "compile_median_aot", "path", ()),
    "mlri_admm": ("compile_mlri_admm_tcm", "compile_mlri_admm_tcm", "path", ()),
    "mtb": ("compile_mtb_tcm", "compile_mtb_aot", "path", ()),
    "ncc": ("compile_ncc_tcm", "compile_ncc_aot", "path", ()),
    "nearest": ("compile_nearest_tcm", "compile_nearest_resize", "path", ()),
    "nlm": ("compile_nlm_tcm", "compile_nlm_aot", "path", ()),
    "ofb": ("compile_ofb_tcm", "compile_ofb_tcm", "path", ()),
    "phase_corr": ("compile_phase_corr_tcm", "compile_phase_normalize", "path", ()),
    "pyramid": ("compile_pyramid_tcm", "compile_pyramid_aot", "path", ()),
    "ransac": ("compile_ransac_tcm", "compile_ransac_tcm", "path", ()),
    "remap": ("compile_remap_tcm", "compile_remap_tcm", "path", ()),
    "seamless_clone": (
        "compile_seamless_clone_tcm",
        "compile_seamless_clone_aot",
        "path",
        (),
    ),
}


def _artifact_path(name: str, backend: str) -> Path:
    return ARTIFACT_DIR / f"{name}_{backend}.tcm"


def _require_backend_artifact(path: Path, backend: str) -> None:
    """Reject an artifact emitted by a different Taichi runtime/backend.

    CPU AOT contains LLVM bitcode and the legacy graph metadata.  GFX AOT
    contains SPIR-V and JSON graph metadata.  Without this check a compiler
    accidentally imported from site-packages can silently overwrite an
    OpenGL/Vulkan artifact with a CPU one.
    """
    import zipfile

    with zipfile.ZipFile(path, "r") as archive:
        names = set(archive.namelist())
    is_gfx = "graphs.json" in names and any(name.endswith(".spv") for name in names)
    is_cpu = "graphs.tcb" in names and any(name.endswith(".ll") for name in names)
    if backend == "cpu" and not is_cpu:
        raise RuntimeError(f"{path.name} is not a CPU AOT artifact")
    if backend in {"vulkan", "opengl"} and not is_gfx:
        raise RuntimeError(f"{path.name} is not a {backend} GFX AOT artifact")


def _run_worker(backend: str, name: str) -> None:
    module_name, function_name, convention, aliases = JOBS[name]
    import taichi as ti

    # Compile each target with its actual Taichi architecture.  The worker uses
    # the rebuilt wheel, whose GLFW path can create the hidden native context.
    arch = {"cpu": ti.cpu, "vulkan": ti.vulkan, "opengl": ti.opengl}[backend]
    module = importlib.import_module(f"{PACKAGE}.{module_name}")
    compiler = getattr(module, function_name)
    target = _artifact_path(name, backend)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    if convention == "path":
        # Never let a backend fallback overwrite a previously valid artifact.
        # Compile into a staging path and promote only after validating the
        # archive payload (CPU LLVM vs GFX SPIR-V).
        staging = target.with_name(target.stem + ".staging.tcm")
        if staging.exists():
            staging.unlink()
        compiler(arch=arch, save_path=str(staging))
        _require_backend_artifact(staging, backend)
        normalize_tcm(staging)
        os.replace(staging, target)
    elif convention == "out_dir":
        # Some compilers emit several artifacts (including aliases). Compile
        # into an isolated directory first so an OpenGL->CPU fallback can
        # never overwrite a previously validated production archive.
        staging_dir = Path(
            tempfile.mkdtemp(prefix=f".aot-{backend}-{name}-", dir=ARTIFACT_DIR)
        )
        try:
            compiler(arch=arch, out_dir=str(staging_dir))
            for candidate in (name, *aliases):
                staged = _artifact_path(candidate, backend)
                # out_dir compilers write relative to the supplied directory.
                staged = staging_dir / staged.name
                if not staged.is_file():
                    raise RuntimeError(f"compiler did not create staging artifact: {staged.name}")
                _require_backend_artifact(staged, backend)
                normalize_tcm(staged)
                os.replace(staged, _artifact_path(candidate, backend))
        finally:
            shutil.rmtree(staging_dir, ignore_errors=True)
    elif convention == "environment":
        os.environ["PIXEL_REFINE_AOT_ARCH"] = backend
        compiler()
    else:  # pragma: no cover - registry invariant
        raise RuntimeError(f"unknown convention {convention!r}")

    expected = (name, *aliases)
    missing = [candidate for candidate in expected if not _artifact_path(candidate, backend).is_file()]
    if missing:
        raise RuntimeError(f"compiler did not create: {', '.join(missing)}")
    for candidate in expected:
        artifact = _artifact_path(candidate, backend)
        _require_backend_artifact(artifact, backend)
        normalize_tcm(artifact)


def _run_subprocess(backend: str, name: str, timeout: float = 900.0) -> tuple[bool, str]:
    env = os.environ.copy()
    env.update(
        {
            "PIXEL_REFINE_AOT_ARCH": backend,
            # Device 0 (Intel UHD) may not expose shaderFloat64; use the
            # configured Vulkan device for capability-sensitive AOT builds.
            "PIXEL_REFINE_AOT_DEVICE": os.environ.get("PIXEL_REFINE_AOT_DEVICE", "1"),
            "PIXEL_REFINE_AUTO_DESTROY": "0",
            "AOT_MODE": "0",
            # Keep the AOT bridge out of compiler workers.  It can claim an
            # OpenGL context before Taichi initializes its compiler and cause
            # the requested graphics artifact to silently become CPU AOT.
            "PIXEL_REFINE_AOT_COMPILE_ONLY": "1",
        }
    )
    existing_pythonpath = env.get("PYTHONPATH", "")
    # Use the interpreter's installed custom wheel.  Prepending the historical
    # build/pr-vk-python tree silently selected an older Taichi binary and made
    # OpenGL appear unsupported despite the rebuilt wheel having a context.
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(PROJECT_ROOT), existing_pythonpath) if part
    )
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--backend", backend, "--worker", name],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            env=env,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        return False, f"worker timed out after {error.timeout}s"
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("cpu", "vulkan", "opengl"), required=True)
    parser.add_argument("--only", help="comma-separated artifact names")
    parser.add_argument("--force", action="store_true", help="recompile existing artifacts")
    parser.add_argument(
        "--timeout", type=float,
        default=float(os.environ.get("PIXEL_REFINE_AOT_COMPILE_TIMEOUT", "900")),
        help="per-artifact worker timeout in seconds",
    )
    parser.add_argument("--worker", choices=tuple(sorted(JOBS)), help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker:
        _run_worker(args.backend, args.worker)
        return

    requested = tuple(args.only.split(",")) if args.only else tuple(sorted(JOBS))
    unknown = sorted(set(requested) - set(JOBS))
    if unknown:
        parser.error(f"unknown artifact(s): {', '.join(unknown)}")

    outcomes: list[tuple[str, str]] = []
    for name in requested:
        artifact = _artifact_path(name, args.backend)
        if artifact.is_file() and not args.force:
            outcomes.append((name, "SKIP existing"))
            continue
        ok, output = _run_subprocess(args.backend, name, timeout=args.timeout)
        outcomes.append((name, "PASS" if ok else f"FAIL\n{output}"))

    for name, outcome in outcomes:
        print(f"[{outcome.splitlines()[0]}] {name}")
    failures = [f"{name}: {outcome}" for name, outcome in outcomes if outcome.startswith("FAIL")]
    if failures:
        raise RuntimeError("AOT backend compilation failed:\n" + "\n".join(failures))


if __name__ == "__main__":
    main()
