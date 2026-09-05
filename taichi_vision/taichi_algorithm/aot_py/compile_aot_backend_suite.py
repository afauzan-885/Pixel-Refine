"""Compile maintained Pixel Refine AOT modules for one backend safely.

Every module is compiled in a fresh Python interpreter.  Taichi backend
initialization is process-global and OpenGL contexts are thread-affine, so a
single long-lived compiler process is not reliable across this module suite.
"""

import argparse
import importlib
import importlib.util
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

try:
    from .target_registry import TARGET_BACKENDS, target_entry_for_id
except ImportError:  # Direct script execution.
    from target_registry import TARGET_BACKENDS, target_entry_for_id


PROJECT_ROOT = Path(__file__).resolve().parents[3]
# Keep production artifacts immutable while a toolchain migration is staged.
# The default remains the historical repository directory for compatibility;
# LLVM20 builds can point this suite at an isolated D: drive root.
_artifact_override = os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT")
ARTIFACT_DIR = (
    Path(_artifact_override).expanduser().resolve()
    if _artifact_override
    else PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
)
PACKAGE = "taichi_vision.taichi_algorithm.aot_py"
# Family-local compiler modules live next to the algorithm source.  Keep the
# short names in JOBS for readability and resolve them through this map so the
# orchestration contract remains stable while the source tree is colocated.
COLOCATED_COMPILER_PACKAGES = {
    # Shared cross-family compilers live beside the algorithm package.  The
    # aot_py modules remain compatibility shims for older direct commands.
    "compile_cast_tcm": "taichi_vision.taichi_algorithm",
    "compile_common_tcm": "taichi_vision.taichi_algorithm",
    "compile_research_tcm": "taichi_vision.taichi_algorithm",
    "compile_akaze_tcm": "taichi_vision.taichi_algorithm.feature_matching",
    "compile_ofb_tcm": "taichi_vision.taichi_algorithm.feature_matching",
    "compile_auto_enhance_tcm": "taichi_vision.taichi_algorithm.enhancement",
    "compile_estimate_noise_tcm": "taichi_vision.taichi_algorithm.enhancement",
    "compile_area_tcm": "taichi_vision.taichi_algorithm.interpolation",
    "compile_bicubic_tcm": "taichi_vision.taichi_algorithm.interpolation",
    "compile_bilinear_tcm": "taichi_vision.taichi_algorithm.interpolation",
    "compile_bilinear_batch_tcm": "taichi_vision.taichi_algorithm.interpolation",
    "compile_nearest_tcm": "taichi_vision.taichi_algorithm.interpolation",
    "compile_remap_tcm": "taichi_vision.taichi_algorithm.interpolation",
    "compile_arm_tcm": "taichi_vision.taichi_algorithm.demosaicing",
    "compile_bilinear_demosaice_tcm": "taichi_vision.taichi_algorithm.demosaicing",
    "compile_dcb_tcm": "taichi_vision.taichi_algorithm.demosaicing",
    "compile_hamilton_tcm": "taichi_vision.taichi_algorithm.demosaicing",
    "compile_highlight_recovery_tcm": "taichi_vision.taichi_algorithm.demosaicing",
    "compile_mlri_admm_tcm": "taichi_vision.taichi_algorithm.demosaicing",
    "compile_bilateral_grid_tcm": "taichi_vision.taichi_algorithm.smoothing",
    "compile_box_filter_tcm": "taichi_vision.taichi_algorithm.smoothing",
    "compile_gaussian_tcm": "taichi_vision.taichi_algorithm.smoothing",
    "compile_jbf_tcm": "taichi_vision.taichi_algorithm.smoothing",
    "compile_median_tcm": "taichi_vision.taichi_algorithm.smoothing",
    "compile_bm3d_tcm": "taichi_vision.taichi_algorithm.denoising",
    "compile_nlm_tcm": "taichi_vision.taichi_algorithm.denoising",
    "compile_block_matching_tcm": "taichi_vision.taichi_algorithm.optical_flow",
    "compile_farneback_tcm": "taichi_vision.taichi_algorithm.optical_flow",
    "compile_horn_schunck_tcm": "taichi_vision.taichi_algorithm.optical_flow",
    "compile_lucas_kanade_tcm": "taichi_vision.taichi_algorithm.optical_flow",
    "compile_lucas_kanade_batch_tcm": "taichi_vision.taichi_algorithm.optical_flow",
    "compile_compute_flow_tcm": "taichi_vision.taichi_algorithm.optical_flow",
    "compile_fft_tcm": "taichi_vision.taichi_algorithm.pyramid",
    "compile_pyramid_tcm": "taichi_vision.taichi_algorithm.pyramid",
    "compile_gradients_tcm": "taichi_vision.taichi_algorithm.math_ops",
    "compile_math_ops": "taichi_vision.taichi_algorithm.math_ops",
    "compile_mtb_tcm": "taichi_vision.taichi_algorithm.alignment",
    "compile_ncc_tcm": "taichi_vision.taichi_algorithm.alignment",
    "compile_phase_corr_tcm": "taichi_vision.taichi_algorithm.alignment",
    "compile_ransac_tcm": "taichi_vision.taichi_algorithm.alignment",
    "compile_normalize_image_tcm": "taichi_vision.taichi_algorithm.alignment",
    "compile_analysis_suite_tcm": "taichi_vision.taichi_algorithm.image_processing",
    "compile_extended_tcm": "taichi_vision.taichi_algorithm.image_processing",
    "compile_inpaint_tcm": "taichi_vision.taichi_algorithm.image_processing",
    "compile_seamless_clone_tcm": "taichi_vision.taichi_algorithm.image_processing",
    "compile_compression_image_tcm": "taichi_vision.taichi_algorithm.compression",
    "compile_raw_pipeline_tcm": "taichi_vision.taichi_algorithm.compression",
    "compile_spatial_fusion_tcm": "taichi_vision.taichi_algorithm.spatial_fusion",
}
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
    "auto_enhance": (
        "compile_auto_enhance_tcm",
        "compile_auto_enhance",
        "path",
        (),
    ),
    "area": ("compile_area_tcm", "compile_area_aot", "path", ()),
    "arm": ("compile_arm_tcm", "compile_arm_tcm", "path", ()),
    "bicubic": ("compile_bicubic_tcm", "compile_bicubic_aot", "path", ()),
    "bilateral_grid": ("compile_bilateral_grid_tcm", "compile_bg_aot", "path", ()),
    "bilinear": ("compile_bilinear_tcm", "compile_bilinear_tcm", "path", ()),
    "bilinear_batch": (
        "compile_bilinear_batch_tcm",
        "compile_bilinear_batch",
        "path",
        (),
    ),
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
    "dcb": ("compile_dcb_tcm", "compile_dcb_tcm", "path", ()),
    "farneback_flow": (
        "compile_farneback_tcm",
        "compile_farneback_flow",
        "out_dir",
        (),
    ),
    "fft": ("compile_fft_tcm", "compile_fft_aot", "path", ()),
    "gaussian": ("compile_gaussian_tcm", "compile_gaussian_tcm", "path", ()),
    "gradients": ("compile_gradients_tcm", "compile_gradients_aot", "path", ()),
    "hamilton": ("compile_hamilton_tcm", "compile_hamilton_tcm", "path", ()),
    "highlight_recovery": (
        "compile_highlight_recovery_tcm",
        "compile_highlight_recovery_tcm",
        "path",
        (),
    ),
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
    "lucas_kanade_batch": (
        "compile_lucas_kanade_batch_tcm",
        "compile_lucas_kanade_batch",
        "path",
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
    "spatial_fusion": (
        "compile_spatial_fusion_tcm",
        "compile_spatial_fusion_tcm",
        "path",
        (),
    ),
    # Research-stage native modules.  The public Camera2/SfM APIs remain
    # Python orchestrators; these artifacts contain their portable hot paths.
    "hdr": ("compile_research_tcm", "compile_hdr_aot", "path", ()),
    "tone_mapping": (
        "compile_research_tcm",
        "compile_tone_mapping_aot",
        "path",
        (),
    ),
    "camera": ("compile_research_tcm", "compile_camera_aot", "path", ()),
    "sfm_matching": (
        "compile_research_tcm",
        "compile_sfm_matching_aot",
        "path",
        (),
    ),
    "sfm_geometry": (
        "compile_research_tcm",
        "compile_sfm_geometry_aot",
        "path",
        (),
    ),
    "sfm_stereo": (
        "compile_research_tcm",
        "compile_sfm_stereo_aot",
        "path",
        (),
    ),
    "sfm_point_cloud": (
        "compile_research_tcm",
        "compile_sfm_point_cloud_aot",
        "path",
        (),
    ),
    "sfm_bundle": (
        "compile_research_tcm",
        "compile_sfm_bundle_aot",
        "path",
        (),
    ),
    "sfm_poisson": (
        "compile_research_tcm",
        "compile_sfm_poisson_aot",
        "path",
        (),
    ),
    "sfm_registration": (
        "compile_research_tcm",
        "compile_sfm_registration_aot",
        "path",
        (),
    ),
    "panorama": (
        "compile_research_tcm",
        "compile_panorama_aot",
        "path",
        (),
    ),
    # Keep the image families independently compilable.  The former
    # image_core/image_heavy/image_guidance aggregate jobs compiled a large
    # monolithic module and were prone to backend timeouts; the production
    # registry below intentionally names each artifact separately.
    "morphology": ("compile_extended_tcm", "compile_morphology_aot", "path", ()),
    "histogram": ("compile_extended_tcm", "compile_histogram_aot", "path", ()),
    "ssim": ("compile_extended_tcm", "compile_ssim_aot", "path", ()),
    "warp_affine": ("compile_extended_tcm", "compile_warp_affine_aot", "path", ()),
    "filter2d": ("compile_extended_tcm", "compile_filter2d_aot", "path", ()),
    "copy_make_border": ("compile_extended_tcm", "compile_border_aot", "path", ()),
    "normalize": ("compile_extended_tcm", "compile_normalize_aot", "path", ()),
    "normalize_image": (
        "compile_normalize_image_tcm",
        "compile_normalize_image_tcm",
        "path",
        (),
    ),
    "threshold": ("compile_extended_tcm", "compile_threshold_aot", "path", ()),
    "gaussian_window": (
        "compile_extended_tcm",
        "compile_gaussian_window_aot",
        "path",
        (),
    ),
    "joint_bilateral_guidance": (
        "compile_extended_tcm",
        "compile_guidance_aot",
        "path",
        (),
    ),
    "enhance_image": ("compile_extended_tcm", "compile_enhance_aot", "path", ()),
    "estimate_noise": (
        "compile_estimate_noise_tcm",
        "compile_estimate_noise",
        "path",
        (),
    ),
    "compression_image": (
        "compile_compression_image_tcm",
        "compile_compression_aot",
        "path",
        (),
    ),
    "compute_flow": (
        "compile_compute_flow_tcm",
        "compile_compute_flow_tcm",
        "path",
        (),
    ),
    # Pre-demosaic RAW/DNG transport and fusion graphs.  The compiler uses an
    # explicit i32 sample transport so 8--16 bit sensor values remain lossless
    # on graphics targets whose native u16 ABI is not qualified yet.
    "compression_raw": (
        "compile_raw_pipeline_tcm",
        "compile_raw_pipeline_aot",
        "path",
        (),
    ),
    # Analysis-suite graphs use a shared source compiler but remain separate
    # archives so a histogram/CLAHE/Canny failure cannot invalidate unrelated
    # image kernels.  Registering them here removes the last parallel build
    # path and lets the target-qualified runner handle all public TCM jobs.
    "color_convert": (
        "compile_analysis_suite_tcm",
        "compile_color_convert",
        "path",
        (),
    ),
    "otsu": ("compile_analysis_suite_tcm", "compile_otsu", "path", ()),
    "clahe": ("compile_analysis_suite_tcm", "compile_clahe", "path", ()),
    "canny": ("compile_analysis_suite_tcm", "compile_canny", "path", ()),
    "hough": ("compile_analysis_suite_tcm", "compile_hough", "path", ()),
    "guided_filter": (
        "compile_analysis_suite_tcm",
        "compile_guided_filter",
        "path",
        (),
    ),
}


def _artifact_path(name: str, backend: str) -> Path:
    return ARTIFACT_DIR / f"{name}_{backend}.tcm"


def _target_artifact_path(name: str, target_id: str) -> Path:
    directory = ARTIFACT_DIR / target_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{name}_{target_id}.tcm"


def _load_tcm_contract():
    """Load contract helpers without importing the public AOT package."""

    contract_path = PROJECT_ROOT / "taichi_vision" / "taichi_aot" / "tcm_contract.py"
    spec = importlib.util.spec_from_file_location("pixel_refine_tcm_contract_build", contract_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load TCM contract helper: {contract_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _attach_manifest_to_target_artifacts(
    artifacts: list[Path], target_id: str, compiler_version: str
) -> None:
    """Attach ABI metadata only when the caller explicitly requests it."""

    if not target_id:
        raise RuntimeError("TCM manifest packaging requires an exact --target profile")
    contract = _load_tcm_contract()
    target = target_entry_for_id(target_id)
    backend = str(target.get("backend", "cpu"))
    required_features = ("COMPUTE", "SSBO") if backend in {"vulkan", "opengl", "gles"} else ()
    for artifact in artifacts:
        if not artifact.is_file():
            raise RuntimeError(f"cannot attach TCM manifest; artifact is missing: {artifact}")
        manifest = contract.build_manifest_from_archive(
            artifact,
            target=target,
            compiler_version=compiler_version,
            required_runtime_features=required_features,
        )
        contract.attach_manifest(artifact, manifest)
        report = contract.validate_tcm(
            artifact,
            runtime_features=required_features,
            requested_target=target,
        )
        if report.get("status") != "valid":
            raise RuntimeError(f"TCM manifest validation did not produce a valid result: {artifact}")
        print(f"[TCM ABI] manifest attached: {artifact.name}")


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
        llvm_text = ""
        if backend == "cuda":
            llvm_members = [name for name in names if name.endswith(".ll")]
            llvm_text = "\n".join(
                archive.read(name).decode("utf-8", errors="replace")
                for name in llvm_members
            ).lower()
    is_gfx = "graphs.json" in names and any(name.endswith(".spv") for name in names)
    # Taichi 1.7.4 serializes both CPU and CUDA AOT graphs as LLVM/TBC
    # archives (CUDA device code is lowered by the CUDA runtime later), while
    # Vulkan/OpenGL/GLES archives carry SPIR-V and ``graphs.json``.  Keep the
    # distinction explicit so a CUDA archive cannot be mistaken for a graphics
    # artifact, but do not reject valid CUDA TCMs merely because they do not
    # contain SPIR-V.
    is_llvm_tcb = "graphs.tcb" in names and any(name.endswith(".ll") for name in names)
    if backend in {"cpu", "cuda"} and not is_llvm_tcb:
        raise RuntimeError(f"{path.name} is not a {backend} LLVM/TBC AOT artifact")
    if backend == "cuda" and "nvptx64" not in llvm_text:
        raise RuntimeError(
            f"{path.name} has no NVPTX device LLVM triple; refusing CUDA promotion"
        )
    if backend in {"vulkan", "opengl", "gles"} and not is_gfx:
        raise RuntimeError(f"{path.name} is not a {backend} GFX AOT artifact")


def _run_worker(backend: str, name: str, target_id: str | None = None) -> None:
    module_name, function_name, convention, aliases = JOBS[name]
    # OpenGL compilation normally stays context-free so a missing ICD cannot
    # silently turn a graphics archive into CPU LLVM.  A native ICD context is
    # an explicit opt-in for the staged Windows profile; the worker still
    # validates the resulting payload before promotion.
    if backend == "opengl" and os.environ.get("PIXEL_REFINE_AOT_NATIVE_CONTEXT") == "1":
        from taichi_vision import taichi_aot as _native_context  # noqa: F401
    import taichi as ti

    # Compile each target with its actual Taichi architecture.  The worker uses
    # the rebuilt wheel, whose GLFW path can create the hidden native context.
    # GLES is a distinct Taichi architecture.  It must not be compiled as
    # desktop OpenGL and then relabeled for Android: the context/GLSL profile
    # and driver capability contract are different even though both archives
    # carry SPIR-V payloads.
    arch = {
        "cpu": ti.cpu,
        "vulkan": ti.vulkan,
        "opengl": ti.opengl,
        "gles": ti.gles,
        "cuda": ti.cuda,
    }[backend]
    module_package = COLOCATED_COMPILER_PACKAGES.get(module_name, PACKAGE)
    module = importlib.import_module(f"{module_package}.{module_name}")
    compiler = getattr(module, function_name)
    target = (
        _target_artifact_path(name, target_id)
        if target_id
        else _artifact_path(name, backend)
    )
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    if convention == "path":
        # Never let a backend fallback overwrite a previously valid artifact.
        # Compile into a staging path and promote only after validating the
        # archive payload (CPU LLVM vs GFX SPIR-V).
        staging = target.with_name(target.stem + ".staging.tcm")
        if staging.exists():
            staging.unlink()
        try:
            compiler(arch=arch, save_path=str(staging))
            _require_backend_artifact(staging, backend)
            normalize_tcm(staging)
            os.replace(staging, target)
        finally:
            # A failed/fallback compiler must not leave a misleading partial
            # archive in the isolated bundle.  Promotion above is atomic, so
            # this only removes an unpromoted temporary artifact.
            if staging.exists():
                staging.unlink()
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
                target_path = (
                    _target_artifact_path(candidate, target_id)
                    if target_id
                    else _artifact_path(candidate, backend)
                )
                # out_dir compilers emit the historical ``*_cuda.tcm`` (or
                # ``*_vulkan.tcm``) name. Accept that producer name, then
                # promote it to the target-qualified path. Older code only
                # looked for the final name inside staging and incorrectly
                # rejected otherwise valid CUDA flow artifacts.
                candidates = (
                    staging_dir / target_path.name,
                    staging_dir / f"{candidate}_{backend}.tcm",
                    staging_dir / f"{candidate}.tcm",
                )
                staged = next((item for item in candidates if item.is_file()), None)
                if staged is None:
                    raise RuntimeError(
                        "compiler did not create staging artifact: "
                        + ", ".join(item.name for item in candidates)
                    )
                _require_backend_artifact(staged, backend)
                normalize_tcm(staged)
                os.replace(staged, target_path)
        finally:
            shutil.rmtree(staging_dir, ignore_errors=True)
    elif convention == "environment":
        os.environ["AOT_ARCH"] = backend
        compiler()
        if target_id:
            # Environment-style producers save beside the suite by design.
            # Move the validated legacy name into the exact target directory
            # before the common postcondition check below.
            legacy = _artifact_path(name, backend)
            target = _target_artifact_path(name, target_id)
            if legacy.is_file() and legacy.resolve() != target.resolve():
                _require_backend_artifact(legacy, backend)
                normalize_tcm(legacy)
                os.replace(legacy, target)
    else:  # pragma: no cover - registry invariant
        raise RuntimeError(f"unknown convention {convention!r}")

    expected = (name, *aliases)
    missing = [
        candidate
        for candidate in expected
        if not (
            _target_artifact_path(candidate, target_id)
            if target_id
            else _artifact_path(candidate, backend)
        ).is_file()
    ]
    if missing:
        raise RuntimeError(f"compiler did not create: {', '.join(missing)}")
    for candidate in expected:
        artifact = (
            _target_artifact_path(candidate, target_id)
            if target_id
            else _artifact_path(candidate, backend)
        )
        _require_backend_artifact(artifact, backend)
        normalize_tcm(artifact)


def _run_subprocess(
    backend: str, name: str, target_id: str | None = None, timeout: float = 900.0
) -> tuple[bool, str]:
    env = os.environ.copy()
    native_context = backend == "opengl" and os.environ.get("PIXEL_REFINE_AOT_NATIVE_CONTEXT") == "1"
    env.update(
        {
            "AOT_ARCH": backend,
            # Device 0 (Intel UHD) may not expose shaderFloat64; use the
            # configured Vulkan device for capability-sensitive AOT builds.
            "AOT_DEVICE": os.environ.get("AOT_DEVICE", "1"),
            "AUTO_DESTROY": "0",
            "AOT_MODE": "0",
            # Keep the AOT bridge out of compiler workers.  It can claim an
            # OpenGL context before Taichi initializes its compiler and cause
            # the requested graphics artifact to silently become CPU AOT.
            "AOT_COMPILE_ONLY": "0" if native_context else "1",
            # The maintained algorithm wrapper checks the project-specific
            # spelling.  Set both markers so every colocated compiler follows
            # the same no-bridge-before-Taichi contract.
            "PIXEL_REFINE_AOT_COMPILE_ONLY": "0" if native_context else "1",
        }
    )
    if target_id:
        env.update(
            {
                "TARGET_BACKEND": backend,
                "TARGET_VARIANT": target_id,
            }
        )
    existing_pythonpath = env.get("PYTHONPATH", "")
    # Use the interpreter's installed custom wheel.  Prepending the historical
    # build/pr-vk-python tree silently selected an older Taichi binary and made
    # OpenGL appear unsupported despite the rebuilt wheel having a context.
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(PROJECT_ROOT), existing_pythonpath) if part
    )
    # Allow an isolated LLVM20 Python profile to drive workers.  The default
    # remains the current interpreter for backwards compatibility, while
    # graphics/CUDA builds can opt into their matching TI_WITH_* extension
    # without mutating the venv or accidentally compiling with the legacy
    # LLVM15 wheel.
    worker_python = os.environ.get("PIXEL_REFINE_AOT_PYTHON", "").strip()
    python_executable = Path(worker_python) if worker_python else Path(sys.executable)
    if not python_executable.is_file():
        return False, f"configured worker interpreter does not exist: {python_executable}"
    try:
        result = subprocess.run(
            [
                str(python_executable),
                str(Path(__file__).resolve()),
                "--backend",
                backend,
                "--worker",
                name,
            ]
            + (["--target", target_id] if target_id else []),
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


def _retarget_cpu_arm64(target_id: str, force: bool = False) -> None:
    """Build a CPU ARM64 profile without invoking ``ti.arm64`` on x64.

    Taichi 1.7.4 reports ``Arch.arm64`` but silently falls back to x64 on a
    Windows host.  Calling the normal worker for an ARM target would
    therefore create a mislabeled artifact.  The dedicated retargeter
    validates each textual LLVM kernel with the AArch64 frontend and the
    runtime builder selects the matching Android/Linux triple.
    """

    retargeter = Path(__file__).with_name("retarget_cpu_tcm_arm64.py")
    runtime_builder = Path(__file__).with_name("build_arm64_runtime.py")
    if not retargeter.is_file() or not runtime_builder.is_file():
        raise RuntimeError("ARM64 cross-target helpers are missing")
    if force:
        retarget = subprocess.run(
            [sys.executable, str(retargeter), "--target", target_id],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=1800.0,
        )
        if retarget.returncode:
            raise RuntimeError(retarget.stdout + retarget.stderr)
    runtime_path = ARTIFACT_DIR / target_id / f"runtime_{target_id[len('cpu_'):]}.bc"
    if force or not runtime_path.is_file():
        runtime = subprocess.run(
            [sys.executable, str(runtime_builder), "--target", target_id],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=300.0,
        )
        if runtime.returncode:
            raise RuntimeError(runtime.stdout + runtime.stderr)


def _promote_vulkan_arm64_android() -> None:
    """Synchronize the architecture-neutral Vulkan archives for Android.

    Vulkan TCMs contain SPIR-V rather than host machine code, so the validated
    desktop set can be reused by ARM64 Android.  Keep the promotion behind the
    explicit target profile and its SPIR-V validator; this prevents a generic
    or malformed archive from being mislabeled as an Android artifact.
    """

    promoter = Path(__file__).with_name("promote_vulkan_spirv_arm64.py")
    source = ARTIFACT_DIR / "vulkan_x86_64_windows"
    output = ARTIFACT_DIR / "vulkan_arm64_android"
    if not promoter.is_file():
        raise RuntimeError("Vulkan ARM64 promotion helper is missing")
    if not source.is_dir() or not any(source.glob("*.tcm")):
        raise RuntimeError(
            "vulkan_x86_64_windows must be compiled before promoting ARM64 Vulkan artifacts"
        )
    result = subprocess.run(
        [
            sys.executable,
            str(promoter),
            "--source",
            str(source),
            "--output",
            str(output),
            "--overwrite",
            "--target-env",
            "vulkan1.1",
            "--workers",
            str(min(8, max(1, os.cpu_count() or 1))),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=900.0,
    )
    if result.returncode:
        raise RuntimeError((result.stdout + result.stderr).strip())
    print((result.stdout + result.stderr).strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend", choices=("cpu", "vulkan", "opengl", "gles", "cuda")
    )
    parser.add_argument(
        "--target",
        choices=tuple(sorted(TARGET_BACKENDS)),
        help="exact architecture/OS/vendor artifact profile",
    )
    parser.add_argument("--only", help="comma-separated artifact names")
    parser.add_argument(
        "--force", action="store_true", help="recompile existing artifacts"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("AOT_COMPILE_TIMEOUT", "900")),
        help="per-artifact worker timeout in seconds",
    )
    parser.add_argument(
        "--with-tcm-manifest",
        action="store_true",
        help="opt-in: attach and validate a TCM ABI v1 manifest after compilation",
    )
    parser.add_argument(
        "--tcm-compiler-version",
        default=os.environ.get("PIXEL_REFINE_TCM_COMPILER_VERSION", "taichi-1.7.4-custom"),
        help="compiler identity recorded in an opt-in TCM manifest",
    )
    parser.add_argument("--worker", choices=tuple(sorted(JOBS)), help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.target:
        target_backend = TARGET_BACKENDS[args.target]
        if args.backend and args.backend != target_backend:
            parser.error(f"target {args.target} requires --backend {target_backend}")
        args.backend = target_backend
    if not args.backend:
        parser.error("--backend or --target is required")
    if args.with_tcm_manifest and not args.target:
        parser.error("--with-tcm-manifest requires an exact --target profile")

    # CPU/CUDA archives contain host-architecture code.  Never label an x86
    # compile as another OS/architecture merely because a filename was
    # requested. Cross-target builds must use an explicit toolchain helper;
    # ``ti.cpu`` on Windows produces a Windows LLVM triple.
    cross_cpu_allowed = os.environ.get("ALLOW_CROSS_CPU_AOT") == "1"
    if args.target == "cpu_x86_64_linux" and os.name == "nt":
        # The normal Taichi CPU worker always lowers against the host triple.
        # ALLOW_CROSS_CPU_AOT used to bypass this gate, but no worker in this
        # script actually configures a Linux sysroot/compiler.  Continuing
        # would therefore put Windows LLVM/CRT code in a Linux-qualified
        # directory.  Keep the target fail-closed until a dedicated,
        # target-aware cross worker is implemented.
        if cross_cpu_allowed:
            parser.error(
                "cpu_x86_64_linux cross build is not implemented by this worker; "
                "use a Linux/glibc worker (or a dedicated target-aware helper)"
            )
        parser.error(
            "cpu_x86_64_linux requires a Linux worker or a dedicated target-aware cross-compiler helper"
        )
    if (
        args.target == "cpu_x86_64_windows"
        and os.name != "nt"
        and not cross_cpu_allowed
    ):
        parser.error(
            "cpu_x86_64_windows requires a Windows worker or an explicit cross-compiler profile"
        )
    # CPU/CUDA archives contain host-architecture code.  Never label an x86
    # compile as ARM merely because a filename was requested.
    if args.target and args.target.startswith("cuda_arm64"):
        host = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
        # Unlike the CPU ARM retargeter, this suite has no CUDA ARM64
        # cross-compiler path.  ``ALLOW_CROSS_CPU_AOT`` must not bypass this
        # gate: the normal Taichi CUDA worker would emit host-x86 payloads
        # into a CUDA ARM directory, creating a mislabeled artifact.
        if host not in {"arm64", "aarch64"}:
            parser.error(
                "CUDA ARM64 AOT requires an ARM64 worker; this worker has no CUDA ARM64 cross-compiler"
            )

    if args.worker:
        _run_worker(args.backend, args.worker, args.target)
        if args.with_tcm_manifest:
            module_name, function_name, convention, aliases = JOBS[args.worker]
            expected = (args.worker, *aliases)
            artifacts = [
                _target_artifact_path(candidate, args.target)
                for candidate in expected
            ]
            _attach_manifest_to_target_artifacts(
                artifacts, args.target, args.tcm_compiler_version
            )
        return

    requested = tuple(args.only.split(",")) if args.only else tuple(sorted(JOBS))
    unknown = sorted(set(requested) - set(JOBS))
    if unknown:
        parser.error(f"unknown artifact(s): {', '.join(unknown)}")

    # Never let a host-x64 Taichi worker emit x64 IR into an ARM directory.
    # The dedicated path is intentionally handled before the normal worker
    # loop and is safe to rerun because each archive is atomically promoted.
    if args.target and args.target.startswith("cpu_arm64"):
        target_dir = ARTIFACT_DIR / args.target
        requested_paths = [
            target_dir / f"{name}_{args.target}.tcm" for name in requested
        ]
        needs_generation = args.force or any(
            not path.is_file() for path in requested_paths
        )
        _retarget_cpu_arm64(args.target, force=needs_generation)
        missing = [str(path.name) for path in requested_paths if not path.is_file()]
        if missing:
            raise RuntimeError(
                "ARM64 retargeter did not produce requested archives: "
                + ", ".join(missing)
            )
        if args.with_tcm_manifest:
            _attach_manifest_to_target_artifacts(
                requested_paths, args.target, args.tcm_compiler_version
            )
        for name in requested:
            print(f"[PASS] {name} ({args.target} cross-target)")
        return

    # Vulkan graphics archives are SPIR-V and therefore architecture-neutral,
    # but they must pass the portability validator before receiving the Android
    # target identity.  Do this automatically so a rebuild cannot leave the
    # ARM profile with a stale partial inventory.
    if args.target == "vulkan_arm64_android":
        _promote_vulkan_arm64_android()
        target_dir = ARTIFACT_DIR / args.target
        missing = [
            str(target_dir / f"{name}_{args.target}.tcm")
            for name in requested
            if not (target_dir / f"{name}_{args.target}.tcm").is_file()
        ]
        if missing:
            raise RuntimeError(
                "Vulkan ARM64 promotion did not produce requested archives: "
                + ", ".join(missing)
            )
        if args.with_tcm_manifest:
            _attach_manifest_to_target_artifacts(
                [
                    target_dir / f"{name}_{args.target}.tcm"
                    for name in requested
                ],
                args.target,
                args.tcm_compiler_version,
            )
        for name in requested:
            print(f"[PASS] {name} (vulkan_arm64_android SPIR-V promotion)")
        return

    outcomes: list[tuple[str, str]] = []
    for name in requested:
        artifact = (
            _target_artifact_path(name, args.target)
            if args.target
            else _artifact_path(name, args.backend)
        )
        if artifact.is_file() and not args.force:
            outcomes.append((name, "SKIP existing"))
            continue
        ok, output = _run_subprocess(
            args.backend, name, args.target, timeout=args.timeout
        )
        outcomes.append((name, "PASS" if ok else f"FAIL\n{output}"))

    for name, outcome in outcomes:
        print(f"[{outcome.splitlines()[0]}] {name}")
    failures = [
        f"{name}: {outcome}" for name, outcome in outcomes if outcome.startswith("FAIL")
    ]
    if failures:
        raise RuntimeError("AOT backend compilation failed:\n" + "\n".join(failures))
    if args.with_tcm_manifest:
        artifacts = [
            _target_artifact_path(candidate, args.target)
            for name in requested
            for candidate in (name, *JOBS[name][3])
        ]
        _attach_manifest_to_target_artifacts(
            artifacts, args.target, args.tcm_compiler_version
        )


if __name__ == "__main__":
    main()
