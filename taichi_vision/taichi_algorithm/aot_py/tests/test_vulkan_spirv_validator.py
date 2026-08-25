"""Tests for graphics SPIR-V target-environment inference."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py" / "validate_vulkan_spirv.py"
SPEC = importlib.util.spec_from_file_location("spirv_validator", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_opengl_and_gles_profiles_use_spirv13():
    assert MODULE.default_target_env(Path("opengl_arm64_linux")) == "spv1.3"
    assert MODULE.default_target_env(Path("gles_arm64_android")) == "spv1.3"


def test_vulkan_profile_uses_vulkan11():
    assert MODULE.default_target_env(Path("vulkan_arm64_android")) == "vulkan1.1"


def test_unknown_profile_remains_conservative_vulkan11():
    assert MODULE.default_target_env(Path("custom_target")) == "vulkan1.1"


def test_collect_accepts_case_insensitive_spirv_suffix():
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        archive_path = root / "upper_case.tcm"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("graphs.json", "{}")
            archive.writestr("shader.SPV", b"spv")
        items = MODULE._collect(root)
        assert [(archive, name) for archive, name, _ in items] == [
            ("upper_case.tcm", "shader.SPV")
        ]
