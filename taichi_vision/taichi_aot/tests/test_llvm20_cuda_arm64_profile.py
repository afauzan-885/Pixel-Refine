import pytest

from taichi_vision.taichi_aot.llvm20_profiles import (
    CUDA_ARM64_LINUX_NVIDIA,
    LLVM20Toolchain,
    get_target_profile,
    make_artifact_manifest,
)


def test_cuda_arm64_linux_profile_is_explicit_and_not_x86_relabel():
    profile = get_target_profile("cuda_arm64_linux_nvidia_llvm20")
    assert profile is CUDA_ARM64_LINUX_NVIDIA
    assert profile.target_triple == "aarch64-linux-gnu"
    assert profile.os == "linux"
    assert profile.arch == "arm64"
    assert profile.vendor == "nvidia"
    assert "aarch64-host" in profile.features


def test_cuda_arm64_manifest_requires_explicit_llvm20_cuda_toolchain():
    manifest = make_artifact_manifest(
        CUDA_ARM64_LINUX_NVIDIA,
        toolchain=LLVM20Toolchain(
            clang_version="20.1.5",
            lld_version="20.1.5",
            cuda_toolkit="12.8",
        ),
    )
    assert manifest["target_identity"]["arch"] == "arm64"
    assert manifest["target_identity"]["target_triple"] == "aarch64-linux-gnu"


def test_unknown_cuda_arm64_profile_is_rejected():
    with pytest.raises(ValueError):
        get_target_profile("cuda_arm64_linux_nvidia")
