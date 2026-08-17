"""Canonical target and artifact identity helpers.

The AOT runtime is used on more than one CPU architecture and GPU API.  A
backend name alone (for example ``vulkan``) is therefore not a sufficient
artifact identity: the native bridge, ABI, operating system and sometimes the
GPU vendor also matter.  This module keeps that identity in one place without
changing the existing public algorithm API.

The resolver is deliberately conservative.  It prefers an explicitly named
target artifact and only falls back to the historical ``<name>_<backend>.tcm``
layout when the caller opts into legacy compatibility.  That prevents an ARM
process from accidentally loading an x86 artifact while allowing the current
desktop tree to keep working during the migration.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import os
import platform as _platform
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Mapping, Optional


_ARCH_ALIASES = {
    "amd64": "x86_64",
    "x86_64": "x86_64",
    "x64": "x86_64",
    "i386": "x86",
    "i686": "x86",
    "x86": "x86",
    "aarch64": "arm64",
    "arm64": "arm64",
    "arm64-v8a": "arm64",
    "armv8": "arm64",
    "armv7l": "armv7",
    "armv7": "armv7",
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


def canonical_arch(value: Optional[str]) -> str:
    """Return the stable architecture name used in artifact filenames."""

    raw = str(value or "").strip().lower().replace(" ", "")
    return _ARCH_ALIASES.get(raw, raw or "unknown")


def canonical_os(value: Optional[str]) -> str:
    raw = str(value or "").strip().lower()
    return _OS_ALIASES.get(raw, raw or "unknown")


def canonical_backend(value: Optional[str], *, os_name: Optional[str] = None) -> str:
    raw = str(value or "").strip().lower()
    backend = _BACKEND_ALIASES.get(raw, raw or "cpu")
    # Android's desktop OpenGL name is misleading.  Keep an explicit GLES
    # artifact identity so desktop GL and mobile GLES cannot be mixed.
    if backend == "opengl" and canonical_os(os_name) == "android":
        return "gles"
    return backend


def canonical_vendor(value: Optional[str]) -> str:
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


def _is_android() -> bool:
    return bool(
        os.environ.get("ANDROID_ROOT")
        or os.environ.get("ANDROID_DATA")
        or "ANDROID_ARGUMENT" in os.environ
    )


@dataclass(frozen=True)
class TargetSpec:
    """Immutable identity of one native AOT target."""

    backend: str = "cpu"
    arch: str = "x86_64"
    os: str = "unknown"
    vendor: str = "unknown"
    abi: str = ""
    driver: str = "unknown"
    variant: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "arch", canonical_arch(self.arch))
        object.__setattr__(self, "os", canonical_os(self.os))
        object.__setattr__(
            self, "backend", canonical_backend(self.backend, os_name=self.os)
        )
        object.__setattr__(self, "vendor", canonical_vendor(self.vendor))
        if self.backend == "cuda" and self.vendor not in {"unknown", "nvidia"}:
            raise ValueError("CUDA artifacts require an NVIDIA vendor")
        if self.backend == "gles" and self.os not in {"android", "linux", "unknown"}:
            raise ValueError("GLES artifacts are only valid on mobile/Linux targets")

    @property
    def target_id(self) -> str:
        parts = [self.backend, self.arch]
        if self.os != "unknown":
            parts.append(self.os)
        if self.vendor != "unknown" and self.backend in {
            "cuda",
            "vulkan",
            "gles",
            "opengl",
        }:
            parts.append(self.vendor)
        if self.variant:
            parts.append(self.variant)
        return "_".join(parts)

    @property
    def is_arm(self) -> bool:
        return self.arch in {"arm64", "armv7"}

    @property
    def is_mobile(self) -> bool:
        return self.os == "android" or self.abi in {"arm64-v8a", "armeabi-v7a"}

    def artifact_name(self, algorithm: str, extension: str = "tcm") -> str:
        stem = str(algorithm).strip().replace(" ", "_")
        if not stem:
            raise ValueError("algorithm name must be non-empty")
        return f"{stem}_{self.target_id}.{extension.lstrip('.') }"

    def bridge_name(self, stem: str = "taichi_aot_engine") -> str:
        suffix = (
            ".dll"
            if self.os == "windows"
            else ".dylib" if self.os == "macos" else ".so"
        )
        return f"{stem}_{self.target_id}{suffix}"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self) | {"target_id": self.target_id}


def detect_target(
    *,
    backend: Optional[str] = None,
    device: Optional[str] = None,
    driver: Optional[str] = None,
) -> TargetSpec:
    """Detect a host target, with environment overrides for CI/cross-builds."""

    env_os = os.environ.get("TARGET_OS")
    env_arch = os.environ.get("TARGET_ARCH")
    env_backend = os.environ.get("TARGET_BACKEND")
    env_vendor = os.environ.get("TARGET_VENDOR")
    env_abi = os.environ.get("TARGET_ABI", "")
    env_variant = os.environ.get("TARGET_VARIANT", "")

    os_name = canonical_os(env_os or ("android" if _is_android() else sys.platform))
    arch = canonical_arch(env_arch or _platform.machine())
    selected_backend = canonical_backend(
        backend or env_backend or "cpu", os_name=os_name
    )
    vendor = canonical_vendor(device or env_vendor)
    if selected_backend == "cpu":
        vendor = "unknown"
    elif selected_backend == "cuda" and vendor == "unknown":
        # CUDA is intentionally NVIDIA-only in the target registry. The
        # native bridge may not expose a device name until after init, so do
        # not resolve a valid CUDA artifact as the vendor-less desktop ID.
        vendor = "nvidia"
    abi = env_abi or ("arm64-v8a" if arch == "arm64" and os_name == "android" else "")
    return TargetSpec(
        backend=selected_backend,
        arch=arch,
        os=os_name,
        vendor=vendor,
        abi=abi,
        driver=driver or os.environ.get("TARGET_DRIVER", "unknown"),
        variant=env_variant,
    )


def resolve_artifact(
    root: os.PathLike[str] | str,
    algorithm: str,
    target: TargetSpec,
    *,
    allow_legacy: bool = True,
) -> Optional[Path]:
    """Resolve an exact target artifact without silently mixing architectures."""

    base = Path(root)
    exact_candidates = [
        base / target.target_id / target.artifact_name(algorithm),
        base / target.artifact_name(algorithm),
    ]
    # Vulkan/OpenGL/GLES graph binaries are vendor-neutral (the driver
    # selects the device at runtime).  A runtime may still detect a vendor
    # suffix (e.g. ``vulkan_x86_64_windows_intel``) while the build only
    # produced the canonical desktop profile.  Prefer a vendor-qualified
    # artifact when present, then safely try that same ABI/API without the
    # vendor suffix.  CUDA deliberately does not use this fallback because
    # its toolchain and device ABI are NVIDIA-specific.
    if target.vendor != "unknown" and target.backend in {"vulkan", "opengl", "gles"}:
        generic = TargetSpec(
            backend=target.backend,
            arch=target.arch,
            os=target.os,
            vendor="unknown",
            abi=target.abi,
            driver=target.driver,
            variant=target.variant,
        )
        exact_candidates.extend(
            [
                base / generic.target_id / generic.artifact_name(algorithm),
                base / generic.artifact_name(algorithm),
            ]
        )
    for candidate in exact_candidates:
        if candidate.is_file() and _artifact_matches_target(candidate, target):
            return candidate
    # ARM/mobile targets must never fall back to the historical unqualified
    # filename: those archives were generated for the desktop ABI and a
    # caller passing ``allow_legacy=True`` must not be able to mix them by
    # accident.  Desktop migration callers retain the explicit opt-in.
    if allow_legacy and not target.is_arm and not target.is_mobile:
        legacy = base / f"{algorithm}_{target.backend}.tcm"
        if legacy.is_file() and _artifact_matches_target(legacy, target):
            return legacy
    return None


def _artifact_matches_target(path: Path, target: TargetSpec) -> bool:
    """Reject a target-qualified archive emitted for another ABI/OS.

    Graphics TCMs carry SPIR-V and are architecture-neutral, so payload kind
    is sufficient there. CPU/CUDA TCMs contain LLVM text whose target triple
    is authoritative; checking it prevents a host-Windows archive from being
    silently loaded by a Linux process merely because it was placed in the
    Linux target directory.
    """
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = set(archive.namelist())
            if target.backend in {"vulkan", "opengl", "gles"}:
                has_spv = "graphs.json" in names and any(
                    name.endswith(".spv") for name in names
                )
                has_llvm = "graphs.tcb" in names or any(
                    name.endswith(".ll") or name.endswith(".tic") for name in names
                )
                if has_spv or has_llvm:
                    return True
            llvm_files = [name for name in names if name.endswith(".ll")]
            if "graphs.tcb" not in names or not llvm_files:
                return False
            sample = archive.read(llvm_files[0]).decode("utf-8", errors="replace")
            triples = re.findall(r'target triple = "([^"]+)"', sample)
            if not triples:
                return False
            triple = triples[0].lower()
            if target.backend == "cuda":
                return "nvptx64" in triple
            if target.arch == "x86_64":
                arch_ok = "x86_64" in triple or "amd64" in triple
            elif target.arch == "arm64":
                arch_ok = "aarch64" in triple or "arm64" in triple
            else:
                arch_ok = target.arch in triple
            if not arch_ok:
                return False
            if target.os == "windows":
                return "windows" in triple or "win32" in triple
            if target.os == "linux":
                return "linux" in triple and "android" not in triple
            if target.os == "android":
                return "android" in triple
            return True
    except (OSError, zipfile.BadZipFile, KeyError):
        return False


def load_target_manifest(path: os.PathLike[str] | str) -> Mapping[str, Any]:
    """Load and minimally validate the repository artifact contract."""

    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("unsupported AOT target manifest schema")
    return payload
