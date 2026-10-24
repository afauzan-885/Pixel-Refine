"""Compile maintained Pixel Refine AOT modules for one backend safely.

Every module is compiled in a fresh Python interpreter.  Taichi backend
initialization is process-global and OpenGL contexts are thread-affine, so a
single long-lived compiler process is not reliable across this module suite.
"""

import argparse
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

try:
    from .aot_artifact import normalize_tcm, validate_normalized_tcm
except ImportError:  # Direct script execution.
    from aot_artifact import normalize_tcm, validate_normalized_tcm

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

BUILD_PROVENANCE_SCHEMA = 1
BUILD_REPORT_DIR = ARTIFACT_DIR.parent / ".aot_compile_reports"
WORKER_METRICS_SCHEMA = 1
WORKER_PHASE_BOUNDARIES = {
    "fingerprint_seconds": "build identity calculation start through completion",
    "taichi_import_seconds": "Taichi import start through completion",
    "compiler_module_import_seconds": "time after the Taichi import through compiler module import completion, less the separately timed Taichi import (also includes architecture/package selection)",
    "compiler_call_seconds": "compiler callable entry through return",
    "payload_validation_seconds": "backend payload validation during promotion",
    "normalization_seconds": "archive normalization during promotion",
    "promotion_seconds": "atomic artifact replacement during promotion",
    "manifest_seconds": "TCM manifest attachment and validation, when requested",
    "post_promotion_integrity_seconds": "post-promotion payload and normalized archive validation",
    "inventory_seconds": "artifact inventory calculation",
    "provenance_seconds": "build provenance calculation and sidecar write",
    "worker_total_seconds": "worker entry through final metric serialization",
}
UNKNOWN_WORKER_PHASES = {
    "backend_init_seconds": "compiler API does not expose an isolated backend-init boundary",
    "frontend_lowering_seconds": "compiler API does not expose an isolated lowering boundary",
    "backend_codegen_seconds": "compiler API does not expose an isolated codegen boundary",
    "archive_seconds": "compiler API does not expose archive-production timing",
    "per_graph_compile_seconds": "compiler API does not expose per-graph compile timing",
}
_SOURCE_FINGERPRINT_CACHE: str | None = None
_TOOLCHAIN_FINGERPRINT_CACHE: dict[str, str] = {}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_fingerprint(*, refresh: bool = False) -> str:
    """Hash Python source inputs that can affect maintained AOT artifacts."""
    global _SOURCE_FINGERPRINT_CACHE
    if refresh:
        _SOURCE_FINGERPRINT_CACHE = None
    if _SOURCE_FINGERPRINT_CACHE is not None:
        return _SOURCE_FINGERPRINT_CACHE
    roots = (
        PROJECT_ROOT / "taichi_vision" / "taichi_algorithm",
        PROJECT_ROOT / "taichi_vision" / "taichi_aot",
    )
    files = sorted(
        (path for root in roots for path in root.rglob("*.py")
         if "__pycache__" not in path.parts),
        key=lambda path: path.relative_to(PROJECT_ROOT).as_posix(),
    )
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(PROJECT_ROOT).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(_sha256_file(path)))
    manifest = PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
    digest.update(b"target_manifest.json\0")
    digest.update(bytes.fromhex(_sha256_file(manifest)))
    _SOURCE_FINGERPRINT_CACHE = digest.hexdigest()
    return _SOURCE_FINGERPRINT_CACHE


def _toolchain_fingerprint(python_executable: Path) -> str:
    """Fingerprint the selected interpreter and installed Taichi compiler files."""
    key = str(python_executable.resolve())
    cached = _TOOLCHAIN_FINGERPRINT_CACHE.get(key)
    if cached:
        return cached
    probe = r'''
import hashlib, importlib.metadata, importlib.util, json, sys
from pathlib import Path
try:
    dist = importlib.metadata.distribution("taichi")
    version = dist.version
    spec = importlib.util.find_spec("taichi")
    origin = str(Path(spec.origin).resolve()) if spec and spec.origin else None
    origin_sha256 = None
    if origin and Path(origin).is_file():
        origin_sha256 = hashlib.sha256(Path(origin).read_bytes()).hexdigest()
    imported_files = []
    if spec:
        for location in spec.submodule_search_locations or ():
            package_root = Path(location)
            for path in package_root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".py", ".pyd", ".dll", ".so", ".dylib", ".bc"}:
                    imported_files.append((path.relative_to(package_root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
    files = []
    for item in dist.files or ():
        rel = item.as_posix()
        suffix = Path(rel).suffix.lower()
        if not rel.startswith("taichi/") or suffix not in {".py", ".pyd", ".dll", ".so", ".dylib", ".bc"}:
            continue
        path = Path(dist.locate_file(item))
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            files.append((rel, digest))
    payload = {"version": version, "origin": origin, "origin_sha256": origin_sha256, "imported_files": sorted(imported_files), "files": sorted(files)}
except importlib.metadata.PackageNotFoundError:
    payload = {"version": None, "origin": None, "origin_sha256": None, "imported_files": [], "files": []}
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
'''
    result = subprocess.run(
        [key, "-c", probe], cwd=PROJECT_ROOT, text=True,
        capture_output=True, check=False, timeout=60.0,
    )
    if result.returncode:
        raise RuntimeError("could not identify selected Taichi toolchain: " + result.stderr.strip())
    try:
        dist_identity = json.loads(result.stdout.strip())
    except json.JSONDecodeError as error:
        raise RuntimeError("selected Taichi toolchain identity was not valid JSON") from error
    if not dist_identity.get("version") or not (dist_identity.get("files") or dist_identity.get("imported_files")):
        raise RuntimeError(
            f"selected interpreter has no fingerprintable Taichi distribution: {key}"
        )
    payload = {
        "python": key,
        "python_sha256": _sha256_file(Path(key)),
        "taichi_distribution": dist_identity,
    }
    cached = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    _TOOLCHAIN_FINGERPRINT_CACHE[key] = cached
    return cached


def _build_identity(
    name: str, backend: str, target_id: str | None, compiler_version: str,
    python_executable: Path, with_manifest: bool, output_name: str | None = None,
) -> dict[str, object]:
    if name not in JOBS:
        raise ValueError(f"unknown AOT job for build identity: {name}")
    target = target_entry_for_id(target_id) if target_id else {
        "backend": backend, "arch": platform.machine().lower(),
        "os": platform.system().lower(), "vendor": "unknown",
    }
    module_name, function_name, convention, aliases = JOBS[name]
    identity: dict[str, object] = {
        "schema": BUILD_PROVENANCE_SCHEMA,
        "source_sha256": _source_fingerprint(),
        "toolchain_sha256": _toolchain_fingerprint(python_executable),
        "target_manifest_sha256": _sha256_file(
            PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
        ),
        "target": target,
        "backend": backend,
        "job": name,
        "output_artifact": output_name or name,
        "output_roster": [name, *aliases],
        "compiler_module": module_name,
        "compiler_callable": function_name,
        "convention": convention,
        "aliases": list(aliases),
        "compiler_identity": compiler_version,
        "with_tcm_manifest": bool(with_manifest),
        "build_environment": {
            key: os.environ.get(key, "")
            for key in (
                "PIXEL_REFINE_ANDROID_API", "PIXEL_REFINE_AOT_NATIVE_CONTEXT",
                "TI_OFFLINE_CACHE", "LLVM_CONFIG", "CC", "CXX",
            )
            if os.environ.get(key) is not None
        },
        "aot_device": os.environ.get("AOT_DEVICE", "1"),
        "worker_pythonpath": os.pathsep.join(
            part for part in (
                str(PROJECT_ROOT), os.environ.get("PYTHONPATH", "")
            ) if part
        ),
    }
    if target_id and target_id.startswith("cpu_arm64"):
        ndk_bin = PROJECT_ROOT / "test_algorithm" / "android_ndk_extract" / "android-ndk-r25c" / "toolchains" / "llvm" / "prebuilt" / "windows-x86_64" / "bin"
        api = os.environ.get("PIXEL_REFINE_ANDROID_API", "26")
        tool = ndk_bin / (
            f"aarch64-linux-android{api}-clang.cmd"
            if target_id == "cpu_arm64_android" else "clang.exe"
        )
        runtime_source = PROJECT_ROOT / "test_algorithm" / "taichi_upstream" / "stable-v1.7.4-development" / "taichi" / "runtime" / "llvm" / "runtime_module" / "runtime.cpp"
        identity["arm64_toolchain"] = {
            "tool": str(tool),
            "tool_sha256": _sha256_file(tool) if tool.is_file() else None,
            "runtime_source": str(runtime_source),
            "runtime_source_sha256": _sha256_file(runtime_source) if runtime_source.is_file() else None,
            "api_level": api if target_id == "cpu_arm64_android" else None,
        }
    if target_id == "vulkan_arm64_android":
        spirv_opt = shutil.which("spirv-opt")
        source_artifact = _target_artifact_path(output_name or name, "vulkan_x86_64_windows")
        source_provenance = _provenance_path(source_artifact)
        source_record = None
        if source_provenance.is_file():
            try:
                source_record = json.loads(source_provenance.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                source_record = None
        identity["spirv_opt"] = {
            "path": spirv_opt,
            "sha256": _sha256_file(Path(spirv_opt)) if spirv_opt else None,
        }
        identity["promotion_source"] = {
            "path": str(source_artifact),
            "artifact_sha256": _sha256_file(source_artifact) if source_artifact.is_file() else None,
            "build_fingerprint": source_record.get("build_fingerprint") if isinstance(source_record, dict) else None,
        }
    graph_signature_inputs = {
        key: identity[key]
        for key in (
            "source_sha256", "toolchain_sha256", "target_manifest_sha256",
            "target", "backend", "job", "compiler_module",
            "compiler_callable", "compiler_identity", "build_environment",
            "aot_device", "worker_pythonpath",
        )
    }
    identity["graph_build_signature"] = hashlib.sha256(
        json.dumps(graph_signature_inputs, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return identity


def _selected_worker_python() -> Path:
    configured = os.environ.get("PIXEL_REFINE_AOT_PYTHON", "").strip()
    return Path(configured).resolve() if configured else Path(sys.executable).resolve()


def _build_fingerprint(identity: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _provenance_path(artifact: Path) -> Path:
    return artifact.with_name(artifact.name + ".build.json")


def _write_build_provenance(artifact: Path, identity: dict[str, object]) -> None:
    """Atomically record exactly which verified inputs produced this artifact."""
    if not artifact.is_file():
        raise RuntimeError(f"cannot record build provenance for missing artifact: {artifact}")
    payload = {
        "schema": BUILD_PROVENANCE_SCHEMA,
        "build_fingerprint": _build_fingerprint(identity),
        "build_identity": identity,
        "artifact_sha256": _sha256_file(artifact),
        "artifact_size": artifact.stat().st_size,
    }
    encoded = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    destination = _provenance_path(artifact)
    staging = destination.with_name(destination.name + ".staging")
    try:
        staging.write_text(encoded, encoding="utf-8")
        os.replace(staging, destination)
    finally:
        if staging.exists():
            staging.unlink()


def _verified_build(artifact: Path, identity: dict[str, object]) -> tuple[bool, str]:
    """Only reuse an artifact with matching build inputs and payload digest."""
    provenance = _provenance_path(artifact)
    if not artifact.is_file():
        return False, "artifact_missing"
    if not provenance.is_file():
        return False, "provenance_missing"
    target = identity.get("target")
    if isinstance(target, dict) and target.get("backend") == "cpu" and target.get("arch") == "arm64":
        # The external ARM helper consumes an NDK sysroot/header closure that
        # is not yet enumerated by its source contract. Never claim a cache hit
        # while that toolchain input set remains incomplete.
        return False, "arm64_external_toolchain_closure_unverified"
    try:
        payload = json.loads(provenance.read_text(encoding="utf-8"))
        if payload.get("schema") != BUILD_PROVENANCE_SCHEMA:
            return False, "provenance_schema_mismatch"
        if payload.get("build_fingerprint") != _build_fingerprint(identity):
            return False, "build_inputs_mismatch"
        if payload.get("artifact_size") != artifact.stat().st_size:
            return False, "artifact_size_mismatch"
        if payload.get("artifact_sha256") != _sha256_file(artifact):
            return False, "artifact_hash_mismatch"
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False, "provenance_invalid"
    return True, "fingerprint_and_payload_match"


def _verified_job_build(
    outputs: list[tuple[str, Path, dict[str, object]]],
) -> tuple[bool, str]:
    """Accept a job cache hit only when every primary/alias output is verified."""
    if not outputs:
        return False, "job_has_no_expected_outputs"
    expected_roster = [output_name for output_name, _, _ in outputs]
    expected_signature = outputs[0][2].get("graph_build_signature")
    if not expected_signature:
        return False, "graph_build_signature_missing"
    seen_names: set[str] = set()
    for output_name, artifact, identity in outputs:
        if output_name in seen_names:
            return False, f"duplicate_expected_output:{output_name}"
        seen_names.add(output_name)
        if identity.get("output_artifact") != output_name:
            return False, f"identity_output_mismatch:{output_name}"
        if identity.get("output_roster") != expected_roster:
            return False, f"identity_roster_mismatch:{output_name}"
        if identity.get("graph_build_signature") != expected_signature:
            return False, f"graph_build_signature_mismatch:{output_name}"
        valid, reason = _verified_build(artifact, identity)
        if not valid:
            return False, f"{output_name}:{reason}"
    return True, "all_outputs_verified"


def _require_complete_job_outputs(
    job: str, outputs: list[tuple[str, Path, dict[str, object]]],
    *, context: str,
) -> list[tuple[str, Path, dict[str, object]]]:
    """Fail closed unless a producer's complete primary/alias set is verified."""
    if job not in JOBS:
        raise RuntimeError(f"{context} has unknown producer job: {job}")
    expected = (job, *JOBS[job][3])
    actual = tuple(output_name for output_name, _, _ in outputs)
    if actual != expected:
        raise RuntimeError(
            f"incomplete {context} roster for {job}: expected {expected}, found {actual}"
        )
    valid, reason = _verified_job_build(outputs)
    if not valid:
        raise RuntimeError(f"invalid {context} roster for {job}: {reason}")
    return outputs


def _artifact_inventory(path: Path) -> dict[str, object]:
    """Collect static archive/graph counts without loading Taichi or a backend."""
    import zipfile

    result: dict[str, object] = {
        "artifact_bytes": path.stat().st_size,
        "archive_entries": None,
        "uncompressed_bytes": None,
        "llvm_payload_count": None,
        "spirv_payload_count": None,
        "graph_count": None,
        "dispatch_node_count": None,
        "kernel_count": None,
        "inventory_status": "unavailable",
    }
    try:
        with zipfile.ZipFile(path, "r") as archive:
            entries = archive.infolist()
            result["archive_entries"] = len(entries)
            result["uncompressed_bytes"] = sum(item.file_size for item in entries)
            result["llvm_payload_count"] = sum(item.filename.lower().endswith((".ll", ".tic")) for item in entries)
            result["spirv_payload_count"] = sum(item.filename.lower().endswith(".spv") for item in entries)
            graphs = archive.read("graphs.json")
            decoded = json.loads(graphs.decode("utf-8"))
            if not isinstance(decoded, list):
                raise ValueError("graphs.json root is not a list")
            dispatches = [
                dispatch
                for graph in decoded
                for dispatch in graph.get("value", {}).get("dispatches", [])
            ]
            kernel_names = {
                str(dispatch[key])
                for dispatch in dispatches
                for key in ("kernel_name", "kernel", "func_name")
                if isinstance(dispatch.get(key), str)
            }
            result.update({
                "graph_count": len(decoded),
                "dispatch_node_count": len(dispatches),
                "kernel_count": len(kernel_names) if kernel_names else None,
                "inventory_status": "graphics_graphs_json",
            })
    except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError):
        # Legacy LLVM/TBC graph metadata is binary; counts remain explicitly
        # unknown instead of being reported as zero.
        pass
    return result


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


def _run_worker(
    backend: str, name: str, target_id: str | None = None,
    compiler_version: str = "taichi-1.7.4-custom", with_manifest: bool = False,
) -> None:
    worker_started = time.perf_counter()
    phases: dict[str, float] = {}
    phase_started = time.perf_counter()
    module_name, function_name, convention, aliases = JOBS[name]
    python_executable = Path(sys.executable)
    fingerprint_started = time.perf_counter()
    identity = _build_identity(
        name, backend, target_id, compiler_version, python_executable, with_manifest
    )
    expected_source = os.environ.get("PIXEL_REFINE_AOT_EXPECTED_SOURCE_SHA256")
    if expected_source and identity["source_sha256"] != expected_source:
        raise RuntimeError("AOT source inputs changed before worker startup; refusing mixed-source build")
    phases["fingerprint_seconds"] = time.perf_counter() - fingerprint_started
    phase_started = time.perf_counter()
    # OpenGL compilation normally stays context-free so a missing ICD cannot
    # silently turn a graphics archive into CPU LLVM.  A native ICD context is
    # an explicit opt-in for the staged Windows profile; the worker still
    # validates the resulting payload before promotion.
    if backend == "opengl" and os.environ.get("PIXEL_REFINE_AOT_NATIVE_CONTEXT") == "1":
        from taichi_vision import taichi_aot as _native_context  # noqa: F401
    import taichi as ti
    phases["taichi_import_seconds"] = time.perf_counter() - phase_started

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
    phases["compiler_module_import_seconds"] = time.perf_counter() - phase_started - phases["taichi_import_seconds"]
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
            compile_started = time.perf_counter()
            compiler(arch=arch, save_path=str(staging))
            phases["compiler_call_seconds"] = time.perf_counter() - compile_started
            validation_started = time.perf_counter()
            _require_backend_artifact(staging, backend)
            phases["payload_validation_seconds"] = time.perf_counter() - validation_started
            normalize_started = time.perf_counter()
            normalize_tcm(staging)
            phases["normalization_seconds"] = time.perf_counter() - normalize_started
            promotion_started = time.perf_counter()
            os.replace(staging, target)
            phases["promotion_seconds"] = time.perf_counter() - promotion_started
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
            compile_started = time.perf_counter()
            compiler(arch=arch, out_dir=str(staging_dir))
            phases["compiler_call_seconds"] = time.perf_counter() - compile_started
            validation_seconds = normalization_seconds = promotion_seconds = 0.0
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
                phase_mark = time.perf_counter()
                _require_backend_artifact(staged, backend)
                validation_seconds += time.perf_counter() - phase_mark
                phase_mark = time.perf_counter()
                normalize_tcm(staged)
                normalization_seconds += time.perf_counter() - phase_mark
                phase_mark = time.perf_counter()
                os.replace(staged, target_path)
                promotion_seconds += time.perf_counter() - phase_mark
            phases["payload_validation_seconds"] = validation_seconds
            phases["normalization_seconds"] = normalization_seconds
            phases["promotion_seconds"] = promotion_seconds
        finally:
            shutil.rmtree(staging_dir, ignore_errors=True)
    elif convention == "environment":
        os.environ["AOT_ARCH"] = backend
        compile_started = time.perf_counter()
        compiler()
        phases["compiler_call_seconds"] = time.perf_counter() - compile_started
        if target_id:
            # Environment-style producers save beside the suite by design.
            # Move the validated legacy name into the exact target directory
            # before the common postcondition check below.
            legacy = _artifact_path(name, backend)
            target = _target_artifact_path(name, target_id)
            if legacy.is_file() and legacy.resolve() != target.resolve():
                validation_started = time.perf_counter()
                _require_backend_artifact(legacy, backend)
                phases["payload_validation_seconds"] = time.perf_counter() - validation_started
                normalize_started = time.perf_counter()
                normalize_tcm(legacy)
                phases["normalization_seconds"] = time.perf_counter() - normalize_started
                promotion_started = time.perf_counter()
                os.replace(legacy, target)
                phases["promotion_seconds"] = time.perf_counter() - promotion_started
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
    if _source_fingerprint(refresh=True) != identity["source_sha256"]:
        raise RuntimeError("AOT source inputs changed during the worker; refusing provenance stamp")
    if with_manifest:
        manifest_started = time.perf_counter()
        _attach_manifest_to_target_artifacts(
            [_target_artifact_path(candidate, target_id) for candidate in expected],
            target_id or "",
            compiler_version,
        )
        phases["manifest_seconds"] = time.perf_counter() - manifest_started
    post_validation_seconds = 0.0
    inventory_seconds = 0.0
    provenance_seconds = 0.0
    inventory: dict[str, object] = {}
    phases.update({
        # These occur inside compiler-family code. They remain null until the
        # compiler APIs expose them without wrapping or changing lifecycle.
        "backend_init_seconds": None,
        "frontend_lowering_seconds": None,
        "backend_codegen_seconds": None,
        "archive_seconds": None,
        "per_graph_compile_seconds": None,
    })
    for candidate in expected:
        artifact = (
            _target_artifact_path(candidate, target_id)
            if target_id
            else _artifact_path(candidate, backend)
        )
        phase_mark = time.perf_counter()
        _require_backend_artifact(artifact, backend)
        validate_normalized_tcm(artifact)
        post_validation_seconds += time.perf_counter() - phase_mark
        phase_mark = time.perf_counter()
        inventory[candidate] = _artifact_inventory(artifact)
        inventory_seconds += time.perf_counter() - phase_mark
        phase_mark = time.perf_counter()
        artifact_identity = _build_identity(
            name, backend, target_id, compiler_version, python_executable,
            with_manifest, output_name=candidate,
        )
        _write_build_provenance(artifact, artifact_identity)
        provenance_seconds += time.perf_counter() - phase_mark
    phases["post_promotion_integrity_seconds"] = post_validation_seconds
    phases["inventory_seconds"] = inventory_seconds
    phases["provenance_seconds"] = provenance_seconds
    phases["worker_total_seconds"] = time.perf_counter() - worker_started
    for phase_name in WORKER_PHASE_BOUNDARIES:
        phases.setdefault(phase_name, None)
    print("AOT_METRICS_JSON=" + json.dumps({
        "schema_version": WORKER_METRICS_SCHEMA,
        "phase_unit": "seconds",
        "phase_boundaries": WORKER_PHASE_BOUNDARIES,
        "unknown_phase_reasons": UNKNOWN_WORKER_PHASES,
        "job": name,
        "backend": backend,
        "target": target_id,
        "phases": phases,
        "artifacts": inventory,
    }, sort_keys=True, separators=(",", ":")))


def _partial_timeout_output(error: subprocess.TimeoutExpired) -> str:
    """Preserve worker output captured before its timeout.

    ``TimeoutExpired`` may expose bytes even when ``text=True`` was passed to
    ``subprocess.run``. Decode defensively so a timed-out AOT compile still
    reports its last phase markers and native/compiler diagnostics.
    """
    sections = []
    for label, value in (("stdout", error.stdout), ("stderr", error.stderr)):
        if value is None:
            continue
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        value = value.strip()
        if value:
            sections.append(f"partial {label}:\n{value}")
    return "\n".join(sections)


def _worker_metrics(output: str) -> dict[str, object] | None:
    marker = "AOT_METRICS_JSON="
    for line in output.splitlines():
        if line.startswith(marker):
            try:
                decoded = json.loads(line[len(marker):])
            except json.JSONDecodeError:
                return None
            if not isinstance(decoded, dict):
                return None
            if decoded.get("schema_version") != WORKER_METRICS_SCHEMA:
                return None
            if decoded.get("phase_unit") != "seconds":
                return None
            if decoded.get("phase_boundaries") != WORKER_PHASE_BOUNDARIES:
                return None
            if decoded.get("unknown_phase_reasons") != UNKNOWN_WORKER_PHASES:
                return None
            phases = decoded.get("phases")
            if not isinstance(phases, dict):
                return None
            expected_phase_names = set(WORKER_PHASE_BOUNDARIES) | set(
                UNKNOWN_WORKER_PHASES
            )
            if set(phases) != expected_phase_names:
                return None
            # Unknown compiler-internal timings must remain explicitly null;
            # accepting a numeric value here would turn a caller-supplied
            # estimate into an observed measurement in the report.
            if any(name not in phases or phases[name] is not None for name in UNKNOWN_WORKER_PHASES):
                return None
            required_phases = (
                "fingerprint_seconds",
                "taichi_import_seconds",
                "compiler_module_import_seconds",
                "compiler_call_seconds",
                "post_promotion_integrity_seconds",
                "inventory_seconds",
                "provenance_seconds",
                "worker_total_seconds",
            )
            if any(phases.get(name) is None for name in required_phases):
                return None
            for name, value in phases.items():
                if name in UNKNOWN_WORKER_PHASES or value is None:
                    continue
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return None
                if not math.isfinite(value) or value < 0:
                    return None
            artifacts = decoded.get("artifacts")
            if not isinstance(artifacts, dict):
                return None
            return decoded
    return None


def _write_compile_report(report: dict[str, object]) -> Path:
    BUILD_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    destination = BUILD_REPORT_DIR / f"compile-{time.time_ns()}.json"
    staging = destination.with_name(destination.name + ".staging")
    try:
        staging.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        os.replace(staging, destination)
    finally:
        if staging.exists():
            staging.unlink()
    return destination


def _run_subprocess(
    backend: str, name: str, target_id: str | None = None, timeout: float = 900.0,
    compiler_version: str = "taichi-1.7.4-custom", with_manifest: bool = False,
    expected_source_sha256: str | None = None,
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
    if expected_source_sha256:
        env["PIXEL_REFINE_AOT_EXPECTED_SOURCE_SHA256"] = expected_source_sha256
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
                "--tcm-compiler-version",
                compiler_version,
            ]
            + (["--target", target_id] if target_id else [])
            + (["--with-tcm-manifest"] if with_manifest else []),
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            env=env,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        message = f"worker timed out after {error.timeout}s"
        partial_output = _partial_timeout_output(error)
        if partial_output:
            message = f"{message}\n{partial_output}"
        return False, message
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
        _run_worker(
            args.backend, args.worker, args.target,
            args.tcm_compiler_version, args.with_tcm_manifest,
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
        target_dir.mkdir(parents=True, exist_ok=True)
        job_outputs: dict[str, list[tuple[str, Path, dict[str, object]]]] = {}
        decisions: dict[str, tuple[bool, str]] = {}
        for name in requested:
            outputs = (name, *JOBS[name][3])
            job_outputs[name] = [
                (
                    output_name,
                    target_dir / f"{output_name}_{args.target}.tcm",
                    _build_identity(
                        name, args.backend, args.target, args.tcm_compiler_version,
                        Path(sys.executable).resolve(), args.with_tcm_manifest,
                        output_name=output_name,
                    ),
                )
                for output_name in outputs
            ]
            decisions[name] = _verified_job_build(job_outputs[name])
        requested_paths = [
            artifact
            for outputs in job_outputs.values()
            for _, artifact, _ in outputs
        ]
        needs_generation = args.force or any(not valid for valid, _ in decisions.values())
        _retarget_cpu_arm64(args.target, force=needs_generation)
        if needs_generation and _source_fingerprint(refresh=True) != next(iter(job_outputs.values()))[0][2]["source_sha256"]:
            raise RuntimeError("AOT source inputs changed during ARM64 retarget; refusing provenance stamp")
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
        for outputs in job_outputs.values():
            for _, artifact, identity in outputs:
                _require_backend_artifact(artifact, "cpu")
                validate_normalized_tcm(artifact)
                _write_build_provenance(artifact, identity)
        for name in requested:
            decision = decisions[name][1]
            outcome = "PASS" if needs_generation else "SKIP verified"
            print(f"[{outcome}] {name} ({args.target}; {decision})")
        return

    # Vulkan graphics archives are SPIR-V and therefore architecture-neutral,
    # but they must pass the portability validator before receiving the Android
    # target identity.  Do this automatically so a rebuild cannot leave the
    # ARM profile with a stale partial inventory.
    if args.target == "vulkan_arm64_android":
        source_target = "vulkan_x86_64_windows"
        source_dir = ARTIFACT_DIR / source_target
        producer_for_output = {
            output: job
            for job, (_, _, _, aliases) in JOBS.items()
            for output in (job, *aliases)
        }
        source_artifacts = sorted(source_dir.glob("*.tcm")) if source_dir.is_dir() else []
        if not source_artifacts:
            raise RuntimeError("cannot promote Vulkan Android artifacts: desktop source set is empty")
        source_records_by_job: dict[str, dict[str, tuple[str, Path, dict[str, object]]]] = {}
        for source_artifact in source_artifacts:
            suffix = f"_{source_target}.tcm"
            if not source_artifact.name.endswith(suffix):
                raise RuntimeError(f"unexpected desktop Vulkan artifact name: {source_artifact.name}")
            output_name = source_artifact.name[:-len(suffix)]
            producer = producer_for_output.get(output_name)
            if producer is None:
                raise RuntimeError(
                    f"desktop Vulkan artifact has no registered compiler job: {source_artifact.name}"
                )
            producer_records = source_records_by_job.setdefault(producer, {})
            if output_name in producer_records:
                raise RuntimeError(f"duplicate Vulkan source output for {producer}: {output_name}")
            source_identity = _build_identity(
                producer, "vulkan", source_target, args.tcm_compiler_version,
                Path(sys.executable).resolve(), args.with_tcm_manifest,
                output_name=output_name,
            )
            producer_records[output_name] = (output_name, source_artifact, source_identity)

        # Validate the complete producer roster before the promoter can replace
        # any Android destination. This includes requested jobs that have no
        # source files at all and unrequested jobs whose partial files would
        # otherwise be copied by the promoter's directory-wide glob.
        source_outputs_by_job: dict[str, list[tuple[str, Path, dict[str, object]]]] = {}
        producer_jobs = tuple(dict.fromkeys((*requested, *sorted(source_records_by_job))))
        for producer in producer_jobs:
            records = source_records_by_job.get(producer, {})
            expected_names = (producer, *JOBS[producer][3])
            complete_records = [
                records.get(output_name)
                or (
                    output_name,
                    source_dir / f"{output_name}_{source_target}.tcm",
                    _build_identity(
                        producer, "vulkan", source_target, args.tcm_compiler_version,
                        Path(sys.executable).resolve(), args.with_tcm_manifest,
                        output_name=output_name,
                    ),
                )
                for output_name in expected_names
            ]
            try:
                _require_complete_job_outputs(
                    producer, complete_records, context="Vulkan desktop source"
                )
            except RuntimeError as error:
                raise RuntimeError(
                    f"cannot promote Vulkan producer {producer}: {error}"
                ) from error
            for output_name, source_artifact, _ in complete_records:
                _require_backend_artifact(source_artifact, "vulkan")
                validate_normalized_tcm(source_artifact)
            source_outputs_by_job[producer] = complete_records

        promotion_outputs = [
            record
            for producer in sorted(source_outputs_by_job)
            for record in source_outputs_by_job[producer]
        ]
        target_dir = ARTIFACT_DIR / args.target
        expected_destination_names = {
            f"{output_name}_{args.target}.tcm"
            for output_name, _, _ in promotion_outputs
        }
        existing_destination_names = {
            path.name for path in target_dir.glob("*.tcm")
        } if target_dir.is_dir() else set()
        unexpected_destination_names = sorted(
            existing_destination_names - expected_destination_names
        )
        if unexpected_destination_names:
            raise RuntimeError(
                "Vulkan Android destination contains outputs not present in the "
                "verified desktop source roster; preserving them and refusing "
                "promotion: " + ", ".join(unexpected_destination_names)
            )

        _promote_vulkan_arm64_android()
        missing = [
            f"{output_name}_{args.target}.tcm"
            for output_name, _, _ in promotion_outputs
            if not (target_dir / f"{output_name}_{args.target}.tcm").is_file()
        ]
        if missing:
            raise RuntimeError(
                "Vulkan ARM64 promotion did not produce the complete verified roster: "
                + ", ".join(missing)
            )
        for output_name, source_artifact, _ in promotion_outputs:
            destination = target_dir / f"{output_name}_{args.target}.tcm"
            _require_backend_artifact(destination, "vulkan")
            validate_normalized_tcm(destination)
            if _sha256_file(source_artifact) != _sha256_file(destination):
                raise RuntimeError(
                    f"Vulkan promotion payload changed during copy: {destination.name}"
                )
        if args.with_tcm_manifest:
            _attach_manifest_to_target_artifacts(
                [target_dir / f"{output_name}_{args.target}.tcm" for output_name, _, _ in promotion_outputs],
                args.target,
                args.tcm_compiler_version,
            )
        target_outputs_by_job: dict[str, list[tuple[str, Path, dict[str, object]]]] = {}
        for producer, source_outputs in source_outputs_by_job.items():
            target_outputs = []
            for output_name, _, _ in source_outputs:
                target_artifact = target_dir / f"{output_name}_{args.target}.tcm"
                target_identity = _build_identity(
                    producer, "vulkan", args.target, args.tcm_compiler_version,
                    Path(sys.executable).resolve(), args.with_tcm_manifest,
                    output_name=output_name,
                )
                _require_backend_artifact(target_artifact, "vulkan")
                validate_normalized_tcm(target_artifact)
                _write_build_provenance(target_artifact, target_identity)
                target_outputs.append((output_name, target_artifact, target_identity))
            target_outputs_by_job[producer] = target_outputs
        for producer, outputs in target_outputs_by_job.items():
            _require_complete_job_outputs(
                producer, outputs, context="Vulkan Android destination"
            )
        for name in requested:
            print(f"[PASS] {name} (vulkan_arm64_android SPIR-V promotion)")
        return

    outcomes: list[tuple[str, str]] = []
    report_jobs: list[dict[str, object]] = []
    run_started = time.perf_counter()
    worker_python = _selected_worker_python()
    for name in requested:
        preflight_started = time.perf_counter()
        expected_outputs = (name, *JOBS[name][3])
        output_records = [
            (
                output_name,
                _target_artifact_path(output_name, args.target)
                if args.target else _artifact_path(output_name, args.backend),
                _build_identity(
                    name, args.backend, args.target, args.tcm_compiler_version,
                    worker_python, args.with_tcm_manifest,
                    output_name=output_name,
                ),
            )
            for output_name in expected_outputs
        ]
        preflight_seconds = time.perf_counter() - preflight_started
        verified, cache_reason = _verified_job_build(output_records)
        if verified and not args.force:
            outcomes.append((name, "SKIP verified"))
            report_jobs.append({
                "job": name, "status": "cache_hit", "cache_reason": cache_reason,
                "compiler_identity": args.tcm_compiler_version,
                "build_fingerprints": {
                    output_name: _build_fingerprint(identity)
                    for output_name, _, identity in output_records
                },
                "preflight_seconds": preflight_seconds,
                "artifacts": {
                    artifact.name: _artifact_inventory(artifact)
                    for _, artifact, _ in output_records
                },
            })
            continue
        worker_started = time.perf_counter()
        ok, output = _run_subprocess(
            args.backend, name, args.target, timeout=args.timeout,
            compiler_version=args.tcm_compiler_version,
            with_manifest=args.with_tcm_manifest,
            expected_source_sha256=str(output_records[0][2]["source_sha256"]),
        )
        worker_seconds = time.perf_counter() - worker_started
        outcomes.append((name, "PASS" if ok else f"FAIL\n{output}"))
        report_jobs.append({
            "job": name, "status": "compiled" if ok else "failed",
            "cache_reason": "forced" if args.force and verified else cache_reason,
            "compiler_identity": args.tcm_compiler_version,
            "build_fingerprints": {
                output_name: _build_fingerprint(identity)
                for output_name, _, identity in output_records
            },
            "preflight_seconds": preflight_seconds,
            "worker_wall_seconds": worker_seconds,
            "worker_metrics": _worker_metrics(output),
            "output_tail": output[-4000:],
        })

    for name, outcome in outcomes:
        print(f"[{outcome.splitlines()[0]}] {name}")
    failures = [
        f"{name}: {outcome}" for name, outcome in outcomes if outcome.startswith("FAIL")
    ]
    if failures:
        report_path = _write_compile_report({
            "schema": 1, "backend": args.backend, "target": args.target,
            "jobs": report_jobs, "run_total_seconds": time.perf_counter() - run_started,
        })
        print(f"[AOT METRICS] {report_path}")
        raise RuntimeError("AOT backend compilation failed:\n" + "\n".join(failures))
    report_path = _write_compile_report({
        "schema": 1, "backend": args.backend, "target": args.target,
        "jobs": report_jobs, "run_total_seconds": time.perf_counter() - run_started,
    })
    print(f"[AOT METRICS] {report_path}")


if __name__ == "__main__":
    main()
