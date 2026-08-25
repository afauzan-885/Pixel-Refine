"""Contract tests for the isolated LLVM20 x86_64 Linux profile."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "taichi_vision" / "taichi_aot" / "llvm20_profiles.py"
SPEC = importlib.util.spec_from_file_location("pixel_refine_llvm20_profiles_linux_test", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_cpu_linux_profile_matches_manifest_target_identity():
    profile = MODULE.get_target_profile("cpu_x86_64_linux_llvm20")
    assert profile.backend == "cpu"
    assert profile.target_triple == "x86_64-unknown-linux-gnu"
    assert profile.os == "linux"
    assert profile.arch == "x86_64"
    assert profile.baseline == "x86-64-v1"
    assert "sse2" in profile.features


def test_cpu_linux_profile_does_not_reuse_windows_triple():
    profile = MODULE.get_target_profile("cpu_x86_64_linux_llvm20")
    assert profile.target_triple != MODULE.CPU_X86_64_WINDOWS.target_triple
    assert any("Linux/glibc" in note for note in profile.notes)

