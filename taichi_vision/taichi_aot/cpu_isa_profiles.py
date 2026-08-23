"""Portable CPU ISA profiles and fail-closed runtime variant selection.

The module is intentionally free of CPUID calls and native imports.  A small
platform bridge can pass the feature bits it observed, which keeps policy
testable on machines that do not have every Intel/AMD/ARM generation.  The
default artifact is always the baseline; optimized variants are selected only
when both hardware and operating-system state are confirmed.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable, Mapping


@dataclass(frozen=True)
class CpuIsaVariant:
    name: str
    arch: str
    march: str
    required_features: frozenset[str] = frozenset()
    required_os_features: frozenset[str] = frozenset()
    score: int = 0
    vendor: str = ""


X86_VARIANTS: tuple[CpuIsaVariant, ...] = (
    # x86-64-v1 is the portable baseline.  Never infer v2 from an empty or
    # malformed feature probe; the optimized profiles below require explicit
    # hardware and OS evidence.
    CpuIsaVariant("x86-64-v1", "x86_64", "x86-64", frozenset(), score=0),
    CpuIsaVariant("x86-64-v2", "x86_64", "x86-64-v2", frozenset({"sse4.2", "popcnt"}), score=20),
    # AVX is not safe to execute from the CPUID bit alone: Windows/Linux may
    # advertise AVX in hardware while the OS has not enabled XMM/YMM state
    # management.  Keep this gate identical to the AVX2 profile so a runtime
    # dispatcher can never select an AVX artifact that would fault on first
    # use.
    CpuIsaVariant(
        "ivybridge-avx",
        "x86_64",
        "ivybridge",
        frozenset({"avx"}),
        frozenset({"xsave", "osxsave", "xcr0.ymm"}),
        score=30,
        vendor="intel",
    ),
    CpuIsaVariant(
        "haswell-avx2-fma",
        "x86_64",
        "haswell",
        frozenset({"avx2", "fma", "f16c"}),
        frozenset({"xsave", "osxsave", "xcr0.ymm"}),
        40,
        "intel",
    ),
    CpuIsaVariant(
        "skylake-avx512",
        "x86_64",
        "skylake-avx512",
        frozenset({"avx512f", "avx512bw", "avx512vl"}),
        frozenset({"xsave", "osxsave", "xcr0.zmm"}),
        50,
        "intel",
    ),
    CpuIsaVariant(
        "core-ultra-avx10",
        "x86_64",
        "arrowlake",
        frozenset({"avx10.2"}),
        frozenset({"xsave", "osxsave", "xcr0.zmm"}),
        60,
        "intel",
    ),
    CpuIsaVariant("znver2-avx2-fma", "x86_64", "znver2", frozenset({"avx2", "fma", "f16c"}), score=40, vendor="amd"),
    CpuIsaVariant("znver4-avx512", "x86_64", "znver4", frozenset({"avx512f", "avx512bw", "avx512vl"}), score=50, vendor="amd"),
)


ARM64_VARIANTS: tuple[CpuIsaVariant, ...] = (
    # AArch64 requires Advanced SIMD (NEON) architecturally, so this is the
    # portable ARM baseline even when a platform HWCAP probe is unavailable.
    CpuIsaVariant("armv8-a+simd", "arm64", "armv8-a", frozenset(), score=0),
    CpuIsaVariant("armv8.2-a+fp16", "arm64", "armv8.2-a", frozenset({"fp16", "neon"}), score=30),
    CpuIsaVariant("armv8.2-a+dotprod", "arm64", "armv8.2-a", frozenset({"dotprod", "neon"}), score=40),
    CpuIsaVariant("sve", "arm64", "armv8.2-a", frozenset({"sve", "neon"}), score=50),
    CpuIsaVariant("sve2", "arm64", "armv9-a", frozenset({"sve2", "sve", "neon"}), score=60),
)


_FEATURE_ALIASES = {
    "asimd": "neon",
    "hwcap_asimd": "neon",
    "hwcap_asimd_hp": "fp16",
    "asimdhp": "fp16",
    "fphp": "fp16",
    "asimddp": "dotprod",
    "dotprod": "dotprod",
    # Toolchain and OS probes differ in punctuation for these architectural
    # flags.  Keep one canonical spelling for variant contracts.
    "avx10_2": "avx10.2",
    "avx10_1": "avx10.1",
    "xcr0_ymm": "xcr0.ymm",
    "xcr0_zmm": "xcr0.zmm",
    "avx512_f": "avx512f",
    "avx512_bw": "avx512bw",
    "avx512_vl": "avx512vl",
}


def _normalized(values: Iterable[str]) -> frozenset[str]:
    """Normalize feature tokens without treating malformed input as enabled.

    Linux HWCAP readers commonly expose ``asimd|fphp|dotprod`` strings or a
    mapping whose values are textual booleans.  Splitting strings here and
    canonicalizing ARM aliases lets the policy consume either form while
    remaining conservative for unknown tokens.
    """

    tokens: list[str] = []
    for value in values:
        if isinstance(value, str):
            tokens.extend(part for part in re.split(r"[|,;\s]+", value) if part)
        else:
            token = str(value).strip()
            if token:
                tokens.append(token)
    normalized = set()
    for token in tokens:
        key = token.strip().lower().replace("-", "_")
        key = _FEATURE_ALIASES.get(key, key)
        if key.startswith("hwcap_"):
            key = key.removeprefix("hwcap_")
            key = _FEATURE_ALIASES.get(key, key)
        normalized.add(key)
    return frozenset(normalized)


def _probe_enabled(value: object) -> bool:
    """Return true only for an unambiguous enabled probe value."""

    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        # A malformed numeric probe must never enable an optimized ISA.
        # NaN compares unequal to zero, and infinity is not a valid feature
        # bit either; both therefore fail closed instead of selecting AVX/FP16.
        return math.isfinite(float(value)) and value != 0
    if isinstance(value, str):
        return value.strip().lower() in {
            "1", "true", "yes", "on", "enabled", "present", "supported"
        }
    return False


def variants_for_arch(arch: str) -> tuple[CpuIsaVariant, ...]:
    normalized = str(arch).strip().lower().replace("-", "_")
    if normalized in {"x86_64", "amd64", "x64"}:
        return X86_VARIANTS
    if normalized in {"arm64", "aarch64", "arm64_v8a"}:
        return ARM64_VARIANTS
    raise ValueError(f"unsupported CPU architecture: {arch!r}")


def select_cpu_variant(
    arch: str,
    hardware_features: Iterable[str] | Mapping[str, object],
    os_features: Iterable[str] | Mapping[str, object] = (),
    *,
    vendor: str = "",
) -> CpuIsaVariant:
    """Select the highest safe variant, always retaining a baseline fallback."""

    def feature_set(values: Iterable[str] | Mapping[str, object]) -> frozenset[str]:
        if isinstance(values, Mapping):
            return _normalized(key for key, enabled in values.items() if _probe_enabled(enabled))
        if isinstance(values, str):
            return _normalized((values,))
        return _normalized(values)

    hardware = feature_set(hardware_features)
    operating_system = feature_set(os_features)
    normalized_vendor = str(vendor).strip().lower()
    normalized_vendor = {
        "genuineintel": "intel",
        "intel corporation": "intel",
        "authenticamd": "amd",
        "advanced micro devices": "amd",
    }.get(normalized_vendor, normalized_vendor)
    candidates = []
    for variant in variants_for_arch(arch):
        # A feature-only probe cannot distinguish Intel AVX2 from AMD AVX2.
        # Keep vendor-specific variants disabled until the caller supplies the
        # vendor identity, preventing a wrong microarchitecture tuning choice.
        if variant.vendor and variant.vendor != normalized_vendor:
            continue
        if not variant.required_features.issubset(hardware):
            continue
        if not variant.required_os_features.issubset(operating_system):
            continue
        candidates.append(variant)
    if not candidates:
        # The baseline is still returned even if a broken probe omitted its
        # expected flags; it is the only artifact safe to load by default.
        return variants_for_arch(arch)[0]
    return max(candidates, key=lambda variant: variant.score)


def manifest_for_variant(variant: CpuIsaVariant) -> dict[str, object]:
    return {
        "name": variant.name,
        "arch": variant.arch,
        "march": variant.march,
        "required_features": sorted(variant.required_features),
        "required_os_features": sorted(variant.required_os_features),
        "dispatch": "runtime-probe",
    }
