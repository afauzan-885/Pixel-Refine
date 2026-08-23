"""Stable, offline TCM/runtime contract validation.

This module is deliberately independent from the native bridge.  It validates
an optional ``tcm_manifest.json`` envelope inside an existing Taichi ``.tcm``
archive and never creates a Taichi context, loads a DLL, or selects a device.
Archives without the manifest are reported as legacy rather than rejected so
the migration can be introduced without invalidating existing artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import zipfile
from typing import Any, Iterable, Mapping, Optional

TCM_MAGIC = "PIXEL_REFINE_TCM"
TCM_MANIFEST_NAME = "tcm_manifest.json"
TCM_FORMAT_VERSION = 1
RUNTIME_ABI_VERSION = 1

# Feature names are part of the contract.  Unknown names are rejected during
# validation instead of being ignored, which prevents an older runtime from
# accidentally executing a graph requiring a newer capability.
KNOWN_RUNTIME_FEATURES = frozenset(
    {
        "COMPUTE",
        "SSBO",
        "FP16",
        "DYNAMIC_SHARED_MEMORY",
        "SUBGROUP_OP",
        "TENSOR_DESCRIPTOR",
        "CUDA_GRAPH",
        "SPIRV_1_4",
    }
)
_PAYLOAD_KINDS = frozenset({"llvm_ir", "ptx", "spirv", "glsl_es", "native"})
_BACKENDS = frozenset({"cpu", "cuda", "vulkan", "opengl", "gles"})
_ARG_TYPES = frozenset({"scalar", "buffer", "texture", "rw_texture", "matrix"})
_ARG_ACCESS = frozenset({"read", "write", "read_write", "value"})
_MAX_MANIFEST_BYTES = 4 * 1024 * 1024
_MAX_KERNELS = 65536
_MAX_ARGS_PER_KERNEL = 4096
_MAX_PAYLOADS = 65536

_ARCH_ALIASES = {
    "amd64": "x86_64",
    "x86_64": "x86_64",
    "x64": "x86_64",
    "aarch64": "arm64",
    "arm64": "arm64",
    "arm64-v8a": "arm64",
    "armv8": "arm64",
    "x86": "x86",
    "i386": "x86",
    "i686": "x86",
}
_OS_ALIASES = {
    "win32": "windows",
    "windows": "windows",
    "linux": "linux",
    "android": "android",
    "darwin": "macos",
    "macos": "macos",
}
_BACKEND_ALIASES = {
    "cpu": "cpu",
    "x64": "cpu",
    "x86": "cpu",
    "arm": "cpu",
    "arm64": "cpu",
    "vulkan": "vulkan",
    "vk": "vulkan",
    "opengl": "opengl",
    "gl": "opengl",
    "gles": "gles",
    "opengles": "gles",
    "opengl-es": "gles",
    "cuda": "cuda",
}
_VENDORS = {"unknown", "nvidia", "intel", "amd", "qualcomm", "arm", "apple"}


class TcmContractError(ValueError):
    """Raised when a TCM manifest or archive violates the v1 contract."""


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TcmContractError(f"{name} must be an object")
    return value


def _require_string(value: Any, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise TcmContractError(f"{name} must be a non-empty string")
    return value.strip()


def _require_int(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise TcmContractError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _string_list(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Iterable):
        raise TcmContractError(f"{name} must be a list of strings")
    result = tuple(_require_string(item, f"{name}[]").upper() for item in value)
    if len(result) != len(set(result)):
        raise TcmContractError(f"{name} contains duplicate values")
    return result


def _safe_archive_name(value: Any, name: str) -> str:
    path = _require_string(value, name)
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or ".." in parsed.parts or "\\" in path:
        raise TcmContractError(f"{name} must be a relative POSIX archive path")
    if path != parsed.as_posix() or not parsed.parts:
        raise TcmContractError(f"{name} is not a canonical archive path")
    return path


def _canonical_arch(value: Any) -> str:
    raw = str(value or "").strip().lower().replace(" ", "")
    return _ARCH_ALIASES.get(raw, raw or "unknown")


def _canonical_os(value: Any) -> str:
    raw = str(value or "").strip().lower()
    return _OS_ALIASES.get(raw, raw or "unknown")


def _canonical_backend(value: Any, os_name: str) -> str:
    raw = str(value or "").strip().lower()
    backend = _BACKEND_ALIASES.get(raw, raw or "cpu")
    if backend == "opengl" and os_name == "android":
        return "gles"
    return backend


def _canonical_vendor(value: Any) -> str:
    raw = str(value or "unknown").strip().lower()
    if raw in _VENDORS:
        return raw
    if "nvidia" in raw or "geforce" in raw:
        return "nvidia"
    if "intel" in raw:
        return "intel"
    if "amd" in raw or "radeon" in raw:
        return "amd"
    if "qualcomm" in raw or "adreno" in raw:
        return "qualcomm"
    if "arm" in raw or "mali" in raw:
        return "arm"
    if "apple" in raw:
        return "apple"
    return "unknown"


def _normalize_target(value: Any) -> dict[str, Any]:
    target = _require_mapping(value, "target")
    os_name = _canonical_os(_require_string(target.get("os"), "target.os"))
    backend = _canonical_backend(_require_string(target.get("backend"), "target.backend"), os_name)
    arch = _canonical_arch(_require_string(target.get("arch"), "target.arch"))
    vendor = _canonical_vendor(target.get("vendor", "unknown"))
    if backend not in _BACKENDS:
        raise TcmContractError(f"unsupported TCM target backend {backend!r}")
    abi = str(target.get("abi", "") or "").strip()
    variant = str(target.get("variant", "") or "").strip()
    if backend == "cuda" and vendor not in {"unknown", "nvidia"}:
        raise TcmContractError("CUDA TCM targets must use the NVIDIA vendor")
    if backend == "gles" and os_name not in {"android", "linux", "unknown"}:
        raise TcmContractError("GLES TCM targets require Android, Linux, or unknown OS")
    result = {
        "backend": backend,
        "arch": arch,
        "os": os_name,
        "vendor": vendor,
    }
    if abi:
        result["abi"] = abi
    if variant:
        result["variant"] = variant
    for optional in ("api", "api_version", "target_triple", "compute_capability", "isa"):
        if optional in target and target[optional] is not None:
            result[optional] = _require_string(target[optional], f"target.{optional}")
    features = _string_list(target.get("features", ()), "target.features")
    if features:
        result["features"] = list(features)
    return result


def _target_value(target: Any, field: str, default: Any = "unknown") -> Any:
    if isinstance(target, Mapping):
        return target.get(field, default)
    return getattr(target, field, default)


def _normalize_arg(value: Any, kernel_name: str, index: int) -> dict[str, Any]:
    arg = _require_mapping(value, f"kernels[{kernel_name}].args[{index}]")
    arg_type = _require_string(arg.get("type"), f"kernels[{kernel_name}].args[{index}].type").lower()
    if arg_type not in _ARG_TYPES:
        raise TcmContractError(f"unsupported kernel argument type {arg_type!r}")
    result: dict[str, Any] = {
        "name": _require_string(arg.get("name"), f"kernels[{kernel_name}].args[{index}].name"),
        "type": arg_type,
        "dtype": _require_string(arg.get("dtype"), f"kernels[{kernel_name}].args[{index}].dtype").lower(),
        "access": _require_string(arg.get("access", "value"), f"kernels[{kernel_name}].args[{index}].access").lower(),
        "binding": _require_int(arg.get("binding", 0), f"kernels[{kernel_name}].args[{index}].binding"),
    }
    if result["access"] not in _ARG_ACCESS:
        raise TcmContractError(f"unsupported kernel argument access {result['access']!r}")
    if "ndim" in arg:
        result["ndim"] = _require_int(arg["ndim"], f"kernels[{kernel_name}].args[{index}].ndim")
    for field in ("shape", "strides"):
        if field in arg:
            values = arg[field]
            if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Iterable):
                raise TcmContractError(f"kernels[{kernel_name}].args[{index}].{field} must be a list")
            result[field] = [_require_int(item, f"{field}[]") for item in values]
    if "alignment" in arg:
        result["alignment"] = _require_int(arg["alignment"], f"kernels[{kernel_name}].args[{index}].alignment", minimum=1)
    if "resource" in arg:
        result["resource"] = _require_string(arg["resource"], f"kernels[{kernel_name}].args[{index}].resource").lower()
    return result


def validate_manifest(
    manifest: Mapping[str, Any],
    *,
    runtime_abi: int = RUNTIME_ABI_VERSION,
    runtime_features: Iterable[str] = (),
    requested_target: Optional[Any] = None,
) -> dict[str, Any]:
    """Validate a manifest and return a normalized, JSON-safe report."""

    source = _require_mapping(manifest, "manifest")
    if source.get("magic") != TCM_MAGIC:
        raise TcmContractError("manifest.magic is not a Pixel Refine TCM manifest")
    schema_version = _require_int(source.get("schema_version"), "schema_version", minimum=1)
    if schema_version != TCM_FORMAT_VERSION:
        raise TcmContractError(f"unsupported TCM manifest schema {schema_version}; expected {TCM_FORMAT_VERSION}")
    tcm_format = _require_int(source.get("tcm_format_version"), "tcm_format_version", minimum=1)
    if tcm_format != TCM_FORMAT_VERSION:
        raise TcmContractError(f"unsupported TCM format {tcm_format}; expected {TCM_FORMAT_VERSION}")
    compiler_version = _require_string(source.get("compiler_version"), "compiler_version")
    minimum_runtime_abi = _require_int(source.get("minimum_runtime_abi"), "minimum_runtime_abi", minimum=1)
    runtime_abi = _require_int(runtime_abi, "runtime_abi", minimum=1)
    if minimum_runtime_abi > runtime_abi:
        raise TcmContractError(
            f"TCM requires runtime ABI {minimum_runtime_abi}, current runtime is {runtime_abi}"
        )

    required_features = _string_list(
        source.get("required_runtime_features", source.get("required_features", ())),
        "required_runtime_features",
    )
    unknown_features = sorted(set(required_features) - KNOWN_RUNTIME_FEATURES)
    if unknown_features:
        raise TcmContractError(f"unknown required runtime feature(s): {', '.join(unknown_features)}")
    available_features = {str(feature).strip().upper() for feature in runtime_features}
    missing_features = sorted(set(required_features) - available_features)
    if missing_features:
        raise TcmContractError(f"runtime lacks required feature(s): {', '.join(missing_features)}")

    target = _normalize_target(source.get("target"))
    if requested_target is not None:
        requested_os = _canonical_os(_target_value(requested_target, "os"))
        requested = {
            "backend": _canonical_backend(_target_value(requested_target, "backend", "cpu"), requested_os),
            "arch": _canonical_arch(_target_value(requested_target, "arch")),
            "os": requested_os,
            "vendor": _canonical_vendor(_target_value(requested_target, "vendor")),
        }
        for field in ("backend", "arch", "os"):
            if target[field] != requested[field]:
                raise TcmContractError(
                    f"TCM target mismatch for {field}: manifest={target[field]!r}, requested={requested[field]!r}"
                )
        if target["vendor"] != "unknown" and target["vendor"] != requested["vendor"]:
            raise TcmContractError(
                f"TCM target mismatch for vendor: manifest={target['vendor']!r}, requested={requested['vendor']!r}"
            )

    payloads = source.get("payloads", [])
    if isinstance(payloads, (str, bytes, bytearray)) or not isinstance(payloads, Iterable):
        raise TcmContractError("payloads must be a list")
    payload_report: list[dict[str, Any]] = []
    seen_payloads: set[str] = set()
    for index, item in enumerate(payloads):
        payload = _require_mapping(item, f"payloads[{index}]")
        path = _safe_archive_name(payload.get("path"), f"payloads[{index}].path")
        if path in seen_payloads:
            raise TcmContractError(f"duplicate payload path: {path}")
        seen_payloads.add(path)
        kind = _require_string(payload.get("kind"), f"payloads[{index}].kind").lower()
        if kind not in _PAYLOAD_KINDS:
            raise TcmContractError(f"unsupported payload kind {kind!r}")
        report = {"path": path, "kind": kind}
        for field in ("version", "target_profile", "sha256", "size"):
            if field in payload and payload[field] is not None:
                if field == "size":
                    report[field] = _require_int(payload[field], f"payloads[{index}].size")
                else:
                    report[field] = _require_string(payload[field], f"payloads[{index}].{field}")
        if "sha256" in report and (len(report["sha256"]) != 64 or any(char not in "0123456789abcdefABCDEF" for char in report["sha256"])):
            raise TcmContractError(f"payloads[{index}].sha256 must be a SHA-256 hex digest")
        payload_report.append(report)
    if len(payload_report) > _MAX_PAYLOADS:
        raise TcmContractError("manifest contains too many payloads")
    if not payload_report:
        raise TcmContractError("manifest must describe at least one executable payload")

    kernels = source.get("kernels", [])
    if isinstance(kernels, (str, bytes, bytearray)) or not isinstance(kernels, Iterable):
        raise TcmContractError("kernels must be a list")
    kernel_report: list[dict[str, Any]] = []
    seen_kernels: set[str] = set()
    for index, item in enumerate(kernels):
        kernel = _require_mapping(item, f"kernels[{index}]")
        name = _require_string(kernel.get("name"), f"kernels[{index}].name")
        if name in seen_kernels:
            raise TcmContractError(f"duplicate kernel name: {name}")
        seen_kernels.add(name)
        args = kernel.get("args", [])
        if isinstance(args, (str, bytes, bytearray)) or not isinstance(args, Iterable):
            raise TcmContractError(f"kernels[{name}].args must be a list")
        args = list(args)
        if len(args) > _MAX_ARGS_PER_KERNEL:
            raise TcmContractError(f"kernel {name!r} contains too many arguments")
        normalized_args = [_normalize_arg(arg, name, arg_index) for arg_index, arg in enumerate(args)]
        arg_names = [arg["name"] for arg in normalized_args]
        if len(arg_names) != len(set(arg_names)):
            raise TcmContractError(f"kernel {name!r} contains duplicate argument names")
        normalized_kernel: dict[str, Any] = {"name": name, "args": normalized_args}
        for field in ("graph", "entry", "payload"):
            if field in kernel and kernel[field] is not None:
                normalized_kernel[field] = _require_string(kernel[field], f"kernels[{name}].{field}")
        kernel_report.append(normalized_kernel)
    if len(kernel_report) > _MAX_KERNELS:
        raise TcmContractError("manifest contains too many kernels")

    return {
        "magic": TCM_MAGIC,
        "schema_version": schema_version,
        "tcm_format_version": tcm_format,
        "compiler_version": compiler_version,
        "minimum_runtime_abi": minimum_runtime_abi,
        "required_runtime_features": list(required_features),
        "target": target,
        "payloads": payload_report,
        "kernels": kernel_report,
    }


def _read_manifest(archive: zipfile.ZipFile) -> Optional[Mapping[str, Any]]:
    names = archive.namelist()
    if TCM_MANIFEST_NAME not in names:
        return None
    if names.count(TCM_MANIFEST_NAME) != 1:
        raise TcmContractError("TCM archive contains duplicate manifest entries")
    info = archive.getinfo(TCM_MANIFEST_NAME)
    if info.file_size > _MAX_MANIFEST_BYTES:
        raise TcmContractError("TCM manifest exceeds the maximum allowed size")
    try:
        decoded = json.loads(archive.read(TCM_MANIFEST_NAME).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TcmContractError("TCM manifest is not valid UTF-8 JSON") from exc
    return _require_mapping(decoded, "manifest")


def _validate_legacy_payload_target(
    archive: zipfile.ZipFile,
    *,
    requested_target: Optional[Any],
) -> None:
    """Reject an obvious backend/payload mismatch in legacy CUDA archives.

    Legacy Taichi archives have no portable manifest, but their embedded LLVM
    IR still declares a target triple.  A CUDA target containing only host
    ``x86_64`` IR is a stale/mislabelled payload (as opposed to a device
    capability limitation) and must not reach the native loader.  Archives
    without LLVM IR remain compatible because their payload kind cannot be
    inferred here.
    """

    if requested_target is None:
        return
    target_os = _canonical_os(_target_value(requested_target, "os"))
    backend = _canonical_backend(_target_value(requested_target, "backend", "cpu"), target_os)
    if backend not in {"cuda", "cpu"}:
        return
    llvm_entries = [name for name in archive.namelist() if name.lower().endswith((".ll", ".tic"))]
    for name in llvm_entries:
        try:
            text = archive.read(name).decode("utf-8", errors="replace")
        except (KeyError, OSError):
            continue
        triples = re.findall(r'target triple = "([^"]+)"', text)
        if not triples:
            continue
        if backend == "cuda":
            if any("nvptx" not in triple.lower() for triple in triples):
                raise TcmContractError(
                    f"legacy CUDA payload target mismatch in {name}: expected NVPTX LLVM triple"
                )
            continue
        # CPU archives are also target-qualified.  Reject an obvious host
        # relabel (for example Windows/MSVC IR placed under the Linux target)
        # before native loading; textual triples are the only portable signal
        # available for legacy archives without a TCM manifest.
        expected_arch = "aarch64" if _canonical_arch(_target_value(requested_target, "arch")) == "arm64" else "x86_64"
        expected_os = target_os
        for triple in triples:
            normalized = triple.lower()
            if expected_arch not in normalized:
                raise TcmContractError(
                    f"legacy CPU payload target mismatch in {name}: expected {expected_arch} LLVM triple"
                )
            if expected_os == "linux" and ("windows" in normalized or "msvc" in normalized):
                raise TcmContractError(
                    f"legacy CPU payload target mismatch in {name}: expected Linux LLVM triple"
                )
            if expected_os == "windows" and ("linux" in normalized or "gnu" in normalized):
                raise TcmContractError(
                    f"legacy CPU payload target mismatch in {name}: expected Windows LLVM triple"
                )


def validate_tcm(
    path: os.PathLike[str] | str,
    *,
    runtime_abi: int = RUNTIME_ABI_VERSION,
    runtime_features: Iterable[str] = (),
    requested_target: Optional[Any] = None,
) -> dict[str, Any]:
    """Validate one archive without loading native code.

    A legacy archive without ``tcm_manifest.json`` returns ``status='legacy'``
    and a payload inventory.  A manifest-bearing archive returns
    ``status='valid'`` or raises :class:`TcmContractError` with a fail-closed
    reason.
    """

    artifact = Path(path).resolve()
    if artifact.suffix.lower() != ".tcm":
        raise TcmContractError(f"expected a .tcm archive, got {artifact}")
    if not artifact.is_file():
        raise TcmContractError(f"TCM archive does not exist: {artifact}")
    try:
        with zipfile.ZipFile(artifact, "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise TcmContractError("TCM archive contains duplicate entry names")
            manifest = _read_manifest(archive)
            inventory = sorted(names)
            if manifest is None:
                _validate_legacy_payload_target(
                    archive,
                    requested_target=requested_target,
                )
                return {
                    "status": "legacy",
                    "legacy": True,
                    "path": str(artifact),
                    "entries": inventory,
                }
            normalized = validate_manifest(
                manifest,
                runtime_abi=runtime_abi,
                runtime_features=runtime_features,
                requested_target=requested_target,
            )
            for payload in normalized["payloads"]:
                payload_path = payload["path"]
                if payload_path not in names:
                    raise TcmContractError(f"payload entry is missing from archive: {payload_path}")
                info = archive.getinfo(payload_path)
                if "size" in payload and int(payload["size"]) != info.file_size:
                    raise TcmContractError(
                        f"payload size mismatch for {payload_path}: manifest={payload['size']}, archive={info.file_size}"
                    )
                if "sha256" in payload:
                    digest = hashlib.sha256(archive.read(payload_path)).hexdigest()
                    if digest.lower() != payload["sha256"].lower():
                        raise TcmContractError(f"payload checksum mismatch for {payload_path}")
            return {
                "status": "valid",
                "legacy": False,
                "path": str(artifact),
                "entries": inventory,
                "manifest": normalized,
            }
    except zipfile.BadZipFile as exc:
        raise TcmContractError(f"invalid TCM zip archive: {artifact}") from exc


def build_manifest_from_archive(
    path: os.PathLike[str] | str,
    *,
    target: Mapping[str, Any],
    compiler_version: str,
    minimum_runtime_abi: int = RUNTIME_ABI_VERSION,
    required_runtime_features: Iterable[str] = (),
    kernels: Iterable[Mapping[str, Any]] = (),
    payload_versions: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    """Create a v1 manifest from an existing Taichi archive.

    The caller supplies target and kernel contracts because legacy Taichi
    ``graphs.tcb`` is binary and does not expose a portable public schema.
    Payload checksums and sizes are derived from the archive itself.  This is
    a packaging helper only; it does not write or load the artifact.
    """

    artifact = Path(path).resolve()
    if artifact.suffix.lower() != ".tcm" or not artifact.is_file():
        raise TcmContractError(f"TCM archive does not exist: {artifact}")
    versions = dict(payload_versions or {})
    features = tuple(required_runtime_features)
    payloads: list[dict[str, Any]] = []
    suffix_kinds = (
        (".ll", "llvm_ir"),
        (".tic", "llvm_ir"),
        (".ptx", "ptx"),
        (".spv", "spirv"),
        (".glsl", "glsl_es"),
    )
    with zipfile.ZipFile(artifact, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise TcmContractError("TCM archive contains duplicate entry names")
        for name in sorted(names):
            kind = next((candidate for suffix, candidate in suffix_kinds if name.lower().endswith(suffix)), None)
            if kind is None:
                continue
            data = archive.read(name)
            entry: dict[str, Any] = {
                "path": name,
                "kind": kind,
                "version": str(versions.get(kind, "unspecified")),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            payloads.append(entry)
    manifest = {
        "magic": TCM_MAGIC,
        "schema_version": TCM_FORMAT_VERSION,
        "tcm_format_version": TCM_FORMAT_VERSION,
        "compiler_version": _require_string(compiler_version, "compiler_version"),
        "minimum_runtime_abi": minimum_runtime_abi,
        "required_runtime_features": list(features),
        "target": dict(target),
        "payloads": payloads,
        "kernels": [dict(kernel) for kernel in kernels],
    }
    return validate_manifest(
        manifest,
        runtime_abi=max(RUNTIME_ABI_VERSION, int(minimum_runtime_abi)),
        runtime_features=features,
    )


def attach_manifest(path: os.PathLike[str] | str, manifest: Mapping[str, Any]) -> str:
    """Atomically add or replace ``tcm_manifest.json`` in one `.tcm` archive.

    This operation is explicit and opt-in.  Compiler scripts are not changed
    to call it automatically until the manifest schema has passed the target
    packaging matrix.
    """

    artifact = Path(path).resolve()
    if artifact.suffix.lower() != ".tcm" or not artifact.is_file():
        raise TcmContractError(f"TCM archive does not exist: {artifact}")
    normalized = validate_manifest(
        manifest,
        runtime_abi=max(RUNTIME_ABI_VERSION, int(manifest.get("minimum_runtime_abi", 1))),
        runtime_features=manifest.get("required_runtime_features", ()),
    )
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with zipfile.ZipFile(artifact, "r") as source:
        contents = {entry.filename: source.read(entry) for entry in source.infolist() if entry.filename != TCM_MANIFEST_NAME}
    staging: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f"{artifact.stem}.", suffix=".staging.tcm", dir=artifact.parent, delete=False
        ) as handle:
            staging = Path(handle.name)
        with zipfile.ZipFile(staging, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
            for name in sorted((*contents.keys(), TCM_MANIFEST_NAME)):
                entry = zipfile.ZipInfo(name, date_time=(2000, 12, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                target_zip.writestr(entry, encoded if name == TCM_MANIFEST_NAME else contents[name])
        os.replace(staging, artifact)
    finally:
        if staging is not None and staging.exists():
            staging.unlink()
    return str(artifact)


__all__ = [
    "KNOWN_RUNTIME_FEATURES",
    "RUNTIME_ABI_VERSION",
    "TCM_FORMAT_VERSION",
    "TCM_MAGIC",
    "TCM_MANIFEST_NAME",
    "TcmContractError",
    "attach_manifest",
    "build_manifest_from_archive",
    "validate_manifest",
    "validate_tcm",
]
