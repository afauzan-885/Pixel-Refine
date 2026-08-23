"""LLVM 20 target profiles used by the isolated AOT build matrix.

This module contains policy only.  It does not import :mod:`engine`, create a
GPU context, invoke CMake, or compile anything.  Keeping the target contract
here lets configure/build scripts and offline validators agree on the same
LLVM/ABI/API identity before a bridge or TCM is produced.

The profiles intentionally separate a portable baseline from optional
instruction variants.  A variant is never a promise that the host supports
the instructions; the runtime must select it after CPUID/OSXSAVE (x86) or
``getauxval(AT_HWCAP/HWCAP2)`` (Android ARM64) probing.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Mapping


LLVM20_PROFILE_SCHEMA = 1
LLVM20_MAJOR = 20


@dataclass(frozen=True)
class LLVM20Toolchain:
    """One coherent compiler/runtime tuple.

    ``llvm_major`` is deliberately required in every artifact manifest.  A
    LLVM15 runtime bitcode file, LLVM20 bridge, and LLVM20 TCM are not a safe
    combination even when their filenames look compatible.
    """

    llvm_major: int = LLVM20_MAJOR
    clang_version: str = "20.x"
    lld_version: str = "20.x"
    # Windows isolated builds normally use CMake's MultiThreaded setting;
    # Android/Linux profiles must record their platform CRT explicitly.
    crt: str = "platform-default"
    cuda_toolkit: str = ""
    spirv_tools_version: str = ""

    def __post_init__(self) -> None:
        if int(self.llvm_major) != LLVM20_MAJOR:
            raise ValueError("LLVM20 profiles require llvm_major=20")
        if not str(self.clang_version).strip():
            raise ValueError("clang_version must be recorded")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LLVM20TargetProfile:
    """Cross-backend target contract consumed by build/validation tooling."""

    name: str
    backend: str
    target_triple: str
    os: str
    arch: str
    baseline: str
    vendor: str = ""
    optional_variants: tuple[str, ...] = ()
    features: tuple[str, ...] = ()
    api_floor: str = ""
    shader_profile: str = ""
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# x86-64-v1 is the ABI baseline required for the broadest supported Windows
# CPU range.  SSE4.2/POPCNT (v2), AVX/AVX2, AVX-512, and AVX10 remain optional
# runtime-selected variants; the default artifact must not exclude older
# Core/Phenom-era x86-64 machines.
CPU_X86_64_WINDOWS = LLVM20TargetProfile(
    name="cpu_x86_64_windows_llvm20",
    backend="cpu",
    target_triple="x86_64-pc-windows-msvc",
    os="windows",
    arch="x86_64",
    baseline="x86-64-v1",
    optional_variants=(
        "x86-64-v2",
        "ivybridge-avx",
        "haswell-avx2-fma",
        "skylake-avx512",
        "core-ultra-avx10",
        "znver2-avx2-fma",
        "znver4-avx512",
    ),
    features=("sse2",),
    notes=(
        "Never compile the default bridge with -march=native.",
        "Dispatch variants only after CPUID, OSXSAVE, and XGETBV checks.",
    ),
)


CPU_X86_64_LINUX = LLVM20TargetProfile(
    name="cpu_x86_64_linux_llvm20",
    backend="cpu",
    target_triple="x86_64-unknown-linux-gnu",
    os="linux",
    arch="x86_64",
    baseline="x86-64-v1",
    optional_variants=CPU_X86_64_WINDOWS.optional_variants,
    features=("sse2",),
    notes=(
        "Build on a Linux/glibc worker or with an explicit x86_64-linux cross toolchain.",
        "The default bridge must remain x86-64-v1; dispatch variants require CPUID/OSXSAVE/XGETBV.",
        "A Windows artifact must never be relabeled as this Linux target.",
    ),
)


CPU_ARM64_ANDROID = LLVM20TargetProfile(
    name="cpu_arm64_android_api26_llvm20",
    backend="cpu",
    target_triple="aarch64-linux-android26",
    os="android",
    arch="arm64",
    baseline="armv8-a+simd",
    optional_variants=("armv8.2-a+fp16", "armv8.2-a+dotprod", "sve", "sve2"),
    features=("neon",),
    api_floor="android-26",
    notes=(
        "arm64-v8a is the portable Android ABI; optional features need HWCAP probes.",
        "Do not mix NDK/LLVM14 bitcode with LLVM20 runtime bitcode.",
    ),
)


OPENGL_X86_64_WINDOWS = LLVM20TargetProfile(
    name="opengl_x86_64_windows_compute43",
    backend="opengl",
    target_triple="x86_64-pc-windows-msvc",
    os="windows",
    arch="x86_64",
    vendor="generic",
    baseline="desktop-gl-4.3-compute",
    api_floor="OpenGL-4.3",
    shader_profile="glsl-4.30/spirv-1.3",
    notes=(
        "GL 2.0-4.2 remains a legacy rendering tier, not a current Taichi compute target.",
        "Runtime must query compute shaders, SSBO limits, and extensions.",
    ),
)


GLES_ARM64_ANDROID = LLVM20TargetProfile(
    name="gles_arm64_android_api26_compute31",
    backend="gles",
    target_triple="aarch64-linux-android26",
    os="android",
    arch="arm64",
    vendor="generic",
    baseline="gles-3.1-compute",
    api_floor="OpenGL-ES-3.1",
    shader_profile="glsl-es-3.10/spirv-1.3",
    notes=(
        "Desktop OpenGL and GLES artifacts are never interchangeable.",
        "GLES2/3.0 requires a separate non-compute implementation.",
    ),
)


VULKAN_DESKTOP = LLVM20TargetProfile(
    name="vulkan_x86_64_windows_negotiated",
    backend="vulkan",
    target_triple="x86_64-pc-windows-msvc",
    os="windows",
    arch="x86_64",
    vendor="generic",
    baseline="vulkan-1.0",
    optional_variants=("vulkan-1.1", "vulkan-1.2", "vulkan-1.3", "vulkan-1.4"),
    api_floor="Vulkan-1.0",
    shader_profile="negotiated-spirv",
    notes=(
        "Select the lowest artifact compatible with the loader/device feature set.",
        "There is no released Vulkan 2.0 core target; 1.4 plus extensions is current.",
    ),
)


VULKAN_ANDROID = LLVM20TargetProfile(
    name="vulkan_arm64_android_api26_negotiated",
    backend="vulkan",
    target_triple="aarch64-linux-android26",
    os="android",
    arch="arm64",
    vendor="generic",
    baseline="vulkan-1.0",
    optional_variants=("vulkan-1.1", "vulkan-1.2", "vulkan-1.3", "vulkan-1.4"),
    api_floor="android-26/Vulkan-1.0",
    shader_profile="negotiated-spirv",
    notes=(
        "Android libvulkan is available from API24, while this product profile starts at API26.",
        "Physical-device API/features still override the OS-level floor.",
    ),
)


CUDA_X86_64_WINDOWS_NVIDIA = LLVM20TargetProfile(
    name="cuda_x86_64_windows_nvidia_llvm20",
    backend="cuda",
    target_triple="x86_64-pc-windows-msvc",
    os="windows",
    arch="x86_64",
    vendor="nvidia",
    baseline="sm_50",
    optional_variants=(
        "sm_52",
        "sm_53",
        "sm_60",
        "sm_61",
        "sm_62",
        "sm_70",
        "sm_72",
        "sm_75",
        "sm_80",
        "sm_86",
        "sm_89",
        "sm_90",
        "sm_100",
        "sm_101",
        "sm_103",
        "sm_120",
        "sm_120a",
        "sm_120f",
        "sm_121",
    ),
    features=("nvptx",),
    api_floor="CUDA-12",
    notes=(
        "CUDA toolkit and target SM must be recorded separately from the LLVM bridge.",
        "Do not infer Blackwell support from a generic CUDA artifact filename.",
    ),
)


CUDA_ARM64_LINUX_NVIDIA = LLVM20TargetProfile(
    name="cuda_arm64_linux_nvidia_llvm20",
    backend="cuda",
    target_triple="aarch64-linux-gnu",
    os="linux",
    arch="arm64",
    vendor="nvidia",
    baseline="sm_50",
    optional_variants=CUDA_X86_64_WINDOWS_NVIDIA.optional_variants,
    features=("nvptx", "aarch64-host"),
    api_floor="CUDA-12",
    notes=(
        "Requires an AArch64 Linux host runtime or an explicit CUDA cross-toolchain; "
        "a host x86_64 Taichi build must never be relabeled as this target.",
        "The profile is a contract only: no TCM or native qualification is implied "
        "until every graph and an ARM64 NVIDIA device are validated.",
    ),
)


LLVM20_TARGET_PROFILES: Mapping[str, LLVM20TargetProfile] = {
    profile.name: profile
    for profile in (
        CPU_X86_64_WINDOWS,
        CPU_X86_64_LINUX,
        CPU_ARM64_ANDROID,
        OPENGL_X86_64_WINDOWS,
        GLES_ARM64_ANDROID,
        VULKAN_DESKTOP,
        VULKAN_ANDROID,
        CUDA_X86_64_WINDOWS_NVIDIA,
        CUDA_ARM64_LINUX_NVIDIA,
    )
}


def get_target_profile(name: str) -> LLVM20TargetProfile:
    key = str(name).strip()
    try:
        return LLVM20_TARGET_PROFILES[key]
    except KeyError as exc:
        raise ValueError(f"unknown LLVM20 target profile: {name!r}") from exc


def validate_artifact_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate an LLVM20 artifact manifest without touching the filesystem."""

    if not isinstance(payload, Mapping):
        raise ValueError("LLVM20 artifact manifest must be an object")
    if payload.get("schema_version") != LLVM20_PROFILE_SCHEMA:
        raise ValueError("unsupported LLVM20 artifact manifest schema")
    toolchain = payload.get("toolchain")
    if not isinstance(toolchain, Mapping):
        raise ValueError("LLVM20 artifact manifest requires a toolchain object")
    if int(toolchain.get("llvm_major", -1)) != LLVM20_MAJOR:
        raise ValueError("artifact is not built by LLVM20")
    profile_name = str(payload.get("profile", "")).strip()
    profile = get_target_profile(profile_name)
    backend = str(payload.get("backend", "")).strip().lower()
    if backend != profile.backend:
        raise ValueError("manifest backend does not match its LLVM20 profile")
    triple = str(payload.get("target_triple", "")).strip()
    if triple != profile.target_triple:
        raise ValueError("manifest target triple does not match its LLVM20 profile")
    identity = payload.get("target_identity")
    if not isinstance(identity, Mapping):
        raise ValueError("manifest requires a target_identity object")
    expected_identity = {
        "backend": profile.backend,
        "os": profile.os,
        "arch": profile.arch,
        "vendor": profile.vendor or "generic",
        "target_triple": profile.target_triple,
    }
    for key, expected in expected_identity.items():
        actual = str(identity.get(key, "")).strip().lower()
        if actual != str(expected).strip().lower():
            raise ValueError(f"manifest target_identity.{key} does not match its LLVM20 profile")
    for key in ("clang_version", "lld_version"):
        value = str(toolchain.get(key, "")).strip()
        match = re.match(r"(\d+)", value)
        if match is None or int(match.group(1)) != LLVM20_MAJOR:
            raise ValueError(f"toolchain {key} must identify LLVM20")
    if profile.backend == "cuda":
        cuda_toolkit = str(toolchain.get("cuda_toolkit", "")).strip()
        if not re.match(r"\d+(?:\.\d+)?", cuda_toolkit):
            raise ValueError("CUDA artifacts require an explicit cuda_toolkit version")
    normalized = dict(payload)
    normalized["schema_version"] = LLVM20_PROFILE_SCHEMA
    normalized["backend"] = backend
    normalized["profile"] = profile.name
    normalized["target_triple"] = triple
    normalized["toolchain"] = dict(toolchain)
    normalized["target_identity"] = dict(identity)
    return normalized


def make_artifact_manifest(
    profile: LLVM20TargetProfile,
    *,
    toolchain: LLVM20Toolchain | None = None,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a manifest payload; writing/building remains the caller's job."""

    payload = {
        "schema_version": LLVM20_PROFILE_SCHEMA,
        "backend": profile.backend,
        "profile": profile.name,
        "target_triple": profile.target_triple,
        "target_identity": {
            "backend": profile.backend,
            "os": profile.os,
            "arch": profile.arch,
            "vendor": profile.vendor or "generic",
            "target_triple": profile.target_triple,
        },
        "baseline": profile.baseline,
        "features": list(profile.features),
        "api_floor": profile.api_floor,
        "shader_profile": profile.shader_profile,
        "toolchain": (toolchain or LLVM20Toolchain()).as_dict(),
        "evidence": dict(evidence or {}),
    }
    return validate_artifact_manifest(payload)
