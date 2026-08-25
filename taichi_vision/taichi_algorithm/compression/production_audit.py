"""Machine-readable production-readiness audit for native image compression.

This module is intentionally an audit layer, not an encoder.  It does not
turn a structural HEVC/AV1 parser into a pixel encoder and it does not hide
the NumPy host ABI boundary.  The report is designed for CI and release
reviews where a truthful capability matrix is more useful than a single
ambiguous ``supported`` flag.
"""

from __future__ import annotations

import argparse
import ast
import dataclasses
import json
import os
import platform
from pathlib import Path
from typing import Any


_FORBIDDEN_CODEC_IMPORTS = {
    "cv2",
    "PIL",
    "imageio",
    "imagecodecs",
    "zlib",
    "libjpeg",
    "libheif",
    "libavif",
    "libwebp",
    "libpng",
    "x265",
    "aom",
    "avm",
    "rawpy",
    "tifffile",
}
_VALIDATION_ONLY_MODULES = {"benchmark_compression.py", "verify_*.py", "test_*.py"}


def _compression_root() -> Path:
    return Path(__file__).resolve().parent


def _repository_root() -> Path:
    # compression/ -> taichi_algorithm/ -> taichi_vision/ -> repository
    return _compression_root().parents[2]


def _imports_audit() -> dict[str, Any]:
    forbidden: set[tuple[str, str]] = set()
    numpy: set[tuple[str, str]] = set()
    for source in sorted(_compression_root().glob("*.py")):
        if (
            source.name in _VALIDATION_ONLY_MODULES
            or source.name.startswith("verify_")
            or source.name.startswith("test_")
        ):
            continue
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, SyntaxError):
            continue
        modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
        for module in modules:
            root_name = module.split(".", 1)[0]
            item = (source.name, module)
            if root_name in _FORBIDDEN_CODEC_IMPORTS:
                forbidden.add(item)
            if root_name == "numpy":
                numpy.add(item)
    return {
        "codec_backend_imports": [list(item) for item in sorted(forbidden)],
        "numpy_host_abi_imports": [list(item) for item in sorted(numpy)],
        "codec_runtime_clean": not forbidden,
        "strict_no_numpy": not numpy,
        "validation_helpers_excluded": sorted(_VALIDATION_ONLY_MODULES),
    }


def _load_report(module_name: str, function_name: str) -> dict[str, Any]:
    try:
        module = __import__(
            f"taichi_vision.taichi_algorithm.compression.{module_name}",
            fromlist=[function_name],
        )
        value = getattr(module, function_name)()
        return dict(value)
    except Exception as exc:  # pragma: no cover - diagnostic guard
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _tcm_artifacts() -> dict[str, Any]:
    root = _repository_root() / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
    artifacts = []
    if root.exists():
        for path in sorted(root.rglob("compression_image_*.tcm")):
            try:
                size = path.stat().st_size
            except OSError:
                continue
            artifacts.append(
                {
                    "target": str(path.parent.relative_to(root)),
                    "file": path.name,
                    "bytes": int(size),
                    "non_empty": size > 0,
                }
            )
    return {
        "root": str(root),
        "count": len(artifacts),
        "artifacts": artifacts,
        "has_non_empty_artifact": any(item["non_empty"] for item in artifacts),
    }


def _codec_matrix() -> dict[str, dict[str, Any]]:
    hevc = _load_report("hevc_aot", "hevc_capability_report")
    hevc_general = _load_report(
        "hevc_general_aot", "hevc_general_capability_report"
    )
    # Use the HEIF facade for every packaged profile.  Calling the underlying
    # HEVC modules directly used to make the audit silently report a missing
    # capability for the 10-bit profile (its public report lives in
    # ``hevc_ipcm10_aot`` but the HEIF wrapper is the canonical container
    # surface).  Keeping this matrix at the facade also verifies that the
    # profile is actually exposed through the format API being audited.
    hevc_vcl = _load_report("heif_aot", "heic_vcl_capability_report")
    hevc_ipcm = _load_report("heif_aot", "heic_ipcm_capability_report")
    hevc_ipcm10 = _load_report("heif_aot", "heic_ipcm10_capability_report")
    hevc_neutral = _load_report("heif_aot", "heic_neutral_capability_report")
    hevc_flat = _load_report("heif_aot", "heic_flat_capability_report")
    hevc_flat10 = _load_report("heif_aot", "heic_flat10_capability_report")
    hevc_stripes = _load_report("heif_aot", "heic_ctu_stripes_capability_report")
    av1 = _load_report("av1_intra_aot", "av1_intra_capability_report")
    av1_entropy = _load_report(
        "av1_entropy_aot", "av1_entropy_capability_report"
    )
    av1_cdf = _load_report("av1_cdf_aot", "av1_cdf_capability_report")
    dng_source = _repository_root() / "test_algorithm" / "IMG_test.dng"
    try:
        from . import dng_aot as dng_module
        from .dng_aot import dng_capability_report

        if dng_source.exists():
            value = dng_capability_report(dng_source)
            dng = (
                dataclasses.asdict(value)
                if dataclasses.is_dataclass(value)
                else dict(value)
            )
        else:
            dng = {"available": False, "error": "IMG_test.dng not found"}
        dng["bytes_api"] = bool(
            hasattr(dng_module, "encode_dng_bytes")
            and hasattr(dng_module, "decode_dng_bytes")
        )
    except Exception as exc:  # pragma: no cover - diagnostic guard
        dng = {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "jpeg": {
            "status": "development_qualification",
            "general_pixel_encoder": True,
            "gpu_numeric_stages": True,
            "gpu_full_codec": False,
            "subsampling": ["444", "422", "420"],
            "optimized_huffman": True,
            "restart_markers": True,
            "production_blockers": [
                "12MP target is not met",
                "strict NumPy-free native ABI is not complete",
                "GLES runtime qualification is pending",
            ],
        },
        "heif_heic": {
            "status": "development_bounded_profile",
            "general_pixel_encoder": bool(hevc.get("pixel_to_slice_encoder", False)),
            "gpu_numeric_stages": False,
            "gpu_full_codec": False,
            "parameter_sets": bool(hevc.get("parameter_sets", False)),
            "fixed_validated_vcl_profile": bool(hevc_vcl.get("vcl_encoder", False)),
            "lossless_ipcm_profile": bool(hevc_ipcm.get("lossless_ipcm", False)),
            "ipcm_variable_subsampling": bool(
                hevc_ipcm.get("variable_subsampling", False)
            ),
            "ipcm_chroma_formats": tuple(hevc_ipcm.get("chroma_formats", ())),
            "ipcm_external_decoder_validated": bool(
                hevc_ipcm.get("external_decoder_validated_payload", False)
            ),
            "lossless_ipcm10_profile": bool(hevc_ipcm10.get("lossless_ipcm", False)),
            "ipcm10_external_decoder_validated": bool(
                hevc_ipcm10.get("external_decoder_validated_payload", False)
            ),
            "compressed_neutral_profile": bool(
                hevc_neutral.get("compressed_intra_profile", False)
            ),
            "neutral_external_decoder_validated": bool(
                hevc_neutral.get("external_decoder_validated_payload", False)
            ),
            "constant_plane_dc_profile": bool(
                hevc_flat.get(
                    "cabac_residual_syntax",
                    hevc_flat.get("transform_coefficients", False),
                )
            ),
            "constant_plane_external_decoder_validated": bool(
                hevc_flat.get("external_decoder_validated_payload", False)
            ),
            "multi_row_ctu_constant_blocks": bool(
                hevc_flat.get("multi_row_ctu_constant_blocks", False)
            ),
            "pixel_derived_residual_profile": bool(
                hevc_general.get("pixel_derived_residual_profile", False)
            ),
        "pixel_derived_residual_scope": hevc_general.get(
            "pixel_derived_residual_scope", ""
        ),
            "compressed_main10_profile": bool(
                hevc_flat10.get("compressed_intra_profile", False)
            ),
            "compressed_main10_external_decoder_validated": bool(
                hevc_flat10.get("external_decoder_validated_payload", False)
            ),
            "compressed_chroma_formats": tuple(
                hevc_flat.get("chroma_formats", ())
            ),
            "horizontal_ctu_stripe_profile": bool(
                hevc_stripes.get("horizontal_ctu_stripes", False)
            ),
            "horizontal_ctu_stripe_external_decoder_validated": bool(
                hevc_stripes.get("external_decoder_validated_payload", False)
            ),
            "production_blockers": [
                "general arbitrary-pixel HEVC residual AC/transform path is not enabled",
            "validated compressed profiles are constant-inside-CTU blocks with matching top/left references only",
                "multi-row nonconstant pictures, arbitrary pixels inside a CTU, RDO, and nonzero QP remain unsupported",
                "4:2:2 compressed residual path remains unqualified",
            ],
        },
        "avif": {
            "status": "development_bounded_profile",
            "general_pixel_encoder": False,
            "gpu_numeric_stages": True,
            "gpu_full_codec": False,
            "native_q15_entropy_primitive": bool(
                av1_entropy.get("q15_range_coder", False)
            ),
            "native_entropy_symbol_coding": bool(
                av1_entropy.get("cdf_symbol_coding", False)
            ),
            "native_default_cdf_subset": bool(av1_cdf.get("fail_closed", False))
            and bool(av1_cdf.get("tables")),
            "native_default_cdf_scope": av1_cdf.get("profile", ""),
            "native_dc_predictor_graph": True,
            "native_dc_predictor_targets": (
                "cpu_x86_64_windows",
                "vulkan_x86_64_windows_nvidia",
            ),
            "fixed_validated_profile": bool(av1.get("native_runtime", False))
            and not bool(av1.get("general_encoder", True)),
            "production_blockers": [
                "general AV1 partition/prediction/transform/range coding is not enabled",
                "qualified native profile is limited to constant 16x16 8-bit 4:2:0",
                "10-bit, alpha, arbitrary dimensions, and multi-tile are pending",
            ],
        },
        "png": {
            "status": "development_qualification",
            "general_pixel_encoder": True,
            "gpu_numeric_stages": True,
            "gpu_full_codec": False,
            "lossless": True,
            "production_blockers": [
                "full-format corpus, metadata, and device matrix are pending",
                "strict NumPy-free host ABI is not complete",
            ],
        },
        "webp": {
            "status": "development_qualification",
            "general_pixel_encoder": True,
            "gpu_numeric_stages": True,
            "gpu_full_codec": False,
            "lossless": True,
            "production_blockers": [
                "full decoder corpus and device matrix are pending",
                "strict NumPy-free host ABI is not complete",
            ],
        },
        "dng": {
            "status": "strong_limited_profile",
            "general_pixel_encoder": False,
            "gpu_numeric_stages": True,
            "gpu_full_codec": False,
            "capability": dng,
            "production_blockers": [
                "multiple IFD/SubIFD, BigTIFF, preview, and broad compressed-DNG coverage are pending",
            ],
        },
    }


def run_production_audit() -> dict[str, Any]:
    """Return a release-review report without running the expensive verifier."""

    imports = _imports_audit()
    codecs = _codec_matrix()
    compression_root = _compression_root()
    native_buffer_path = {
        "numpy_free_public_facade": (
            _repository_root() / "taichi_vision" / "native_compression.py"
        ).is_file(),
        "numpy_free_dng_facade": (
            _repository_root() / "taichi_vision" / "native_dng.py"
        ).is_file(),
        "direct_c_abi_runner": (compression_root / "native_dispatch.py").is_file(),
        "native_yuv_preparation": (compression_root / "native_video_prep.py").is_file(),
        "standalone_numpy_free_verifier": (compression_root / "verify_native_bridge.py").is_file(),
        "canonical_public_dispatch_replaced": False,
        "qualification_scope": "CPU, NVIDIA Vulkan, CUDA, and NVIDIA OpenGL JPEG/Y/Cb/Cr plus bounded HEVC DC/AC graphs",
    }
    blockers = []
    if not imports["codec_runtime_clean"]:
        blockers.append("forbidden codec backend import detected")
    if not imports["strict_no_numpy"]:
        blockers.append("strict NumPy-free native ABI is not complete")
    for name, report in codecs.items():
        if report.get("status", "").startswith("development"):
            blockers.append(f"{name} remains development/qualification")
    if not all(bool(report.get("gpu_full_codec", False)) for report in codecs.values()):
        blockers.append(
            "no codec family currently has a qualified full GPU-resident codec path"
        )
    return {
        "schema": "compression-production-audit-v1",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "backend": os.environ.get("AOT_ARCH", "default"),
        "aot_mode": os.environ.get("AOT_MODE", "1"),
        "runtime_dependencies": imports,
        "native_buffer_path": native_buffer_path,
        "tcm_artifacts": _tcm_artifacts(),
        "codecs": codecs,
        "gpu_full_codec_ready": all(
            bool(report.get("gpu_full_codec", False)) for report in codecs.values()
        ),
        "production_ready": False,
        "release_blockers": blockers,
        "interpretation": (
            "A codec is production-ready only after its capability report is general, "
            "its external decode/parity matrix passes, and its target-specific TCM/ABI "
            "benchmark gates pass."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run_production_audit(), indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
