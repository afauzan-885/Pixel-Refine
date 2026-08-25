from __future__ import annotations

from taichi_vision.taichi_aot.cpu_isa_profiles import select_cpu_variant


def test_malformed_string_flags_do_not_enable_x86_optimized_variant():
    selected = select_cpu_variant(
        "x86_64",
        {"avx2": "false", "fma": "0", "f16c": "no", "sse4.2": "unknown"},
        {"xsave": "off", "osxsave": "false"},
        vendor="GenuineIntel",
    )
    assert selected.name == "x86-64-v1"


def test_hardware_and_os_features_must_both_be_confirmed():
    selected = select_cpu_variant(
        "x86_64",
        {"avx2": True, "fma": True, "f16c": True},
        {"xsave": True, "osxsave": True, "xcr0.ymm": False},
        vendor="GenuineIntel",
    )
    assert selected.name == "x86-64-v1"


def test_avx_variant_requires_os_ymm_state_support():
    selected = select_cpu_variant(
        "x86_64",
        {"avx": True},
        {"xsave": True, "osxsave": True},
        vendor="GenuineIntel",
    )
    assert selected.name == "x86-64-v1"

    selected = select_cpu_variant(
        "x86_64",
        {"avx": True},
        {"xsave": True, "osxsave": True, "xcr0.ymm": True},
        vendor="GenuineIntel",
    )
    assert selected.name == "ivybridge-avx"


def test_arm_hwcap_aliases_are_normalized_and_split():
    selected = select_cpu_variant(
        "aarch64",
        "HWCAP_ASIMD|HWCAP_ASIMD_HP|HWCAP_ASIMDDP",
    )
    assert selected.name == "armv8.2-a+dotprod"


def test_arm_empty_probe_stays_on_portable_neon_baseline():
    selected = select_cpu_variant("arm64", {}, {}, vendor="Qualcomm")
    assert selected.name == "armv8-a+simd"


def test_x86_probe_punctuation_is_normalized_for_core_ultra_variant():
    selected = select_cpu_variant(
        "amd64",
        {"AVX10_2": True},
        {"xsave": True, "osxsave": True, "XCR0_ZMM": True},
        vendor="Intel Corporation",
    )
    assert selected.name == "core-ultra-avx10"


def test_non_finite_numeric_flags_do_not_enable_optimized_variant():
    selected = select_cpu_variant(
        "x86_64",
        {"avx2": float("nan"), "fma": float("inf"), "f16c": -float("inf")},
        {"xsave": True, "osxsave": True, "xcr0.ymm": True},
        vendor="GenuineIntel",
    )
    assert selected.name == "x86-64-v1"
