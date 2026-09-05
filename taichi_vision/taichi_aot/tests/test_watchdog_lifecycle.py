"""Regression tests for the AOT watchdog startup/lifecycle boundary."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
ENGINE_MODULE = "taichi_vision.taichi_aot.engine"


def _run_probe(extra_env: dict[str, str], source: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "AUTO_DESTROY": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONPATH": str(ROOT),
            **extra_env,
        }
    )
    return subprocess.run(
        [sys.executable, "-u", "-c", source],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )


def test_watchdog_does_not_reclaim_before_first_engine() -> None:
    result = _run_probe(
        {"HEARTBEAT_TIMEOUT": "0"},
        f"""
import importlib, threading, time
engine = importlib.import_module({ENGINE_MODULE!r})
engine._WATCHDOG_INTERVAL_S = 0.01
threading.Thread(target=engine._watchdog_run, daemon=True).start()
time.sleep(0.08)
print('instances=' + str(len(engine.AOTEngine._instances)))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "instances=0" in result.stdout
    assert "No GPU activity" not in result.stderr
    assert "reclamation" not in result.stderr.lower()


def test_legacy_watchdog_disable_aliases_are_honoured() -> None:
    for variable in ("DISABLE_AOT_WATCHDOG", "PIXEL_REFINE_DISABLE_AOT_WATCHDOG"):
        result = _run_probe(
            {variable: "1"},
            f"""
import importlib
engine = importlib.import_module({ENGINE_MODULE!r})
print('enabled=' + str(engine._AUTO_DESTROY_ENABLED))
""",
        )
        assert result.returncode == 0, result.stderr
        assert "enabled=False" in result.stdout


def test_native_stderr_can_be_preserved_for_diagnostics() -> None:
    result = _run_probe(
        {"AOT_PRESERVE_NATIVE_STDERR": "1"},
        f"""
import importlib
engine = importlib.import_module({ENGINE_MODULE!r})
print('suppressed=' + str(engine._suppress_native_stderr(True).enabled))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "suppressed=False" in result.stdout


def test_watchdog_source_has_no_background_python_gc() -> None:
    result = _run_probe(
        {"AUTO_DESTROY": "0"},
        f"""
import importlib, inspect
import ast
engine = importlib.import_module({ENGINE_MODULE!r})
source = inspect.getsource(engine._watchdog_run)
tree = ast.parse(source)
calls = [node for node in ast.walk(tree)
         if isinstance(node, ast.Call)
         and isinstance(node.func, ast.Attribute)
         and node.func.attr == 'collect']
print('has_gc=' + str(bool(calls)))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "has_gc=False" in result.stdout


def test_startup_warmup_uses_intel_vulkan_compatibility_policy() -> None:
    result = _run_probe(
        {
            "AOT_ARCH": "vulkan",
            "PIXEL_REFINE_AOT_ARCH": "vulkan",
            "TARGET_VENDOR": "intel",
            "PIXEL_REFINE_TARGET_VENDOR": "intel",
        },
        """
from pixel_refine_desktop.app_core.aot_warmup import _startup_warmup_allowed
print('allowed=' + str(_startup_warmup_allowed()))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "allowed=True" in result.stdout


def test_startup_warmup_accepts_qualified_intel_vulkan_in_strict_mode() -> None:
    result = _run_probe(
        {
            "AOT_ARCH": "vulkan",
            "AOT_DEVICE": "4",
            "TARGET_VENDOR": "intel",
            "PIXEL_REFINE_GFX_COMPAT_MODE": "0",
        },
        """
import taichi_vision.vulkan_probe as probe
probe.intel_vulkan_is_validated = lambda device_id=None: True
from pixel_refine_desktop.app_core.aot_warmup import _startup_warmup_allowed
print('allowed=' + str(_startup_warmup_allowed()))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "allowed=True" in result.stdout


def test_startup_warmup_defers_thread_affine_intel_opengl() -> None:
    result = _run_probe(
        {
            "AOT_ARCH": "opengl",
            "PIXEL_REFINE_AOT_ARCH": "opengl",
            "TARGET_VENDOR": "intel",
            "PIXEL_REFINE_TARGET_VENDOR": "intel",
        },
        """
from pixel_refine_desktop.app_core.aot_warmup import _startup_warmup_allowed
print('allowed=' + str(_startup_warmup_allowed()))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "allowed=False" in result.stdout


def test_startup_warmup_remains_allowed_for_nvidia_opengl() -> None:
    result = _run_probe(
        {
            "AOT_ARCH": "opengl",
            "PIXEL_REFINE_AOT_ARCH": "opengl",
            "TARGET_VENDOR": "nvidia",
            "PIXEL_REFINE_TARGET_VENDOR": "nvidia",
        },
        """
from pixel_refine_desktop.app_core.aot_warmup import _startup_warmup_allowed
print('allowed=' + str(_startup_warmup_allowed()))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "allowed=True" in result.stdout


def test_native_intel_vulkan_guard_rejects_unqualified_device() -> None:
    result = _run_probe(
        {
            "AOT_ARCH": "vulkan",
            "AOT_DEVICE": "4",
            "TARGET_VENDOR": "intel",
            "PIXEL_REFINE_TARGET_VENDOR": "intel",
            "AOT_SKIP_DOZEN": "1",
            "PIXEL_REFINE_GFX_COMPAT_MODE": "0",
            "PIXEL_REFINE_INTEL_VULKAN_STATE": str(ROOT / ".codex_test_intel_vk_state"),
        },
        f"""
import importlib
import os
engine = importlib.import_module({ENGINE_MODULE!r})
record = {{
    'ordinal': 4, 'name': 'Intel(R) UHD Graphics 620',
    'vendor': 'intel', 'translation': False, 'native': True,
    'vendor_id': 32902, 'device_id': 16032,
    'driver_id': 'DRIVER_ID_INTEL_PROPRIETARY_WINDOWS',
}}
engine.scan_vulkan_device_records = lambda: [record]
engine.get_vulkan_device_name = lambda ordinal: record['name']
engine._intel_vulkan_allowed = lambda ordinal: False
engine._schedule_intel_vulkan_qualification = lambda ordinal: None
try:
    engine.resolve_backend_config(arch='vulkan', device_id=4, strict=True)
except RuntimeError as exc:
    print('guarded=' + str(exc))
else:
    raise AssertionError('native Intel Vulkan was not guarded')
""",
    )
    assert result.returncode == 0, result.stderr
    assert "guarded=Native Intel Vulkan is quarantined" in result.stdout


def test_native_intel_vulkan_compatibility_mode_admits_device() -> None:
    result = _run_probe(
        {
            "AOT_ARCH": "vulkan",
            "AOT_DEVICE": "4",
            "TARGET_VENDOR": "intel",
            "PIXEL_REFINE_TARGET_VENDOR": "intel",
            "AOT_SKIP_DOZEN": "1",
            "PIXEL_REFINE_GFX_COMPAT_MODE": "1",
        },
        f"""
import importlib
engine = importlib.import_module({ENGINE_MODULE!r})
record = {{
    'ordinal': 4, 'name': 'Intel(R) UHD Graphics 620',
    'vendor': 'intel', 'translation': False, 'native': True,
    'vendor_id': 32902, 'device_id': 16032,
    'driver_id': 'DRIVER_ID_INTEL_PROPRIETARY_WINDOWS',
}}
engine.scan_vulkan_device_records = lambda: [record]
engine.get_vulkan_device_name = lambda ordinal: record['name']
engine._intel_vulkan_allowed = lambda ordinal: False
engine._schedule_intel_vulkan_qualification = lambda ordinal: None
config = engine.resolve_backend_config(arch='vulkan', device_id=4, strict=True)
print('admitted=' + config.backend + ':' + config.vendor)
""",
    )
    assert result.returncode == 0, result.stderr
    assert "admitted=vulkan:intel" in result.stdout


def test_stale_vulkan_ordinal_is_reselected_by_vendor() -> None:
    result = _run_probe(
        {
            "AOT_ARCH": "vulkan",
            "AOT_DEVICE": "1",
            "TARGET_VENDOR": "nvidia",
            "PIXEL_REFINE_TARGET_VENDOR": "nvidia",
            "AOT_SKIP_DOZEN": "1",
        },
        f"""
import importlib
engine = importlib.import_module({ENGINE_MODULE!r})
names = {{
    0: 'Intel(R) UHD Graphics 620',
    1: 'Microsoft Direct3D12 (Intel(R) UHD Graphics 620)',
    2: 'NVIDIA GeForce MX150',
}}
engine.get_vulkan_device_name = lambda ordinal: names[int(ordinal)]
engine._read_cached_device_id = lambda: None
engine._scan_native_vulkan_device = lambda preferred_vendor='unknown': (
    2 if preferred_vendor == 'nvidia' else 0
)
engine.scan_vulkan_device_records = lambda: []
config = engine.resolve_backend_config(arch='vulkan', device_id=1, strict=True)
print('selected=' + str(config.device_id) + ':' + config.vendor)
""",
    )
    assert result.returncode == 0, result.stderr
    assert "selected=2:nvidia" in result.stdout


@pytest.mark.parametrize(
    ("mode", "backend", "vendor", "expected"),
    [
        ("auto", "vulkan", "intel", True),
        ("auto", "opengl", "nvidia", False),
        ("1", "vulkan", "nvidia", True),
        ("0", "opengl", "intel", False),
        ("1", "cpu", "intel", False),
    ],
)
def test_graphics_compatibility_policy(mode, backend, vendor, expected) -> None:
    result = _run_probe(
        {"PIXEL_REFINE_GFX_COMPAT_MODE": mode},
        f"""
from taichi_vision.graphics_compatibility import graphics_compatibility_enabled
print('enabled=' + str(graphics_compatibility_enabled({backend!r}, {vendor!r})))
""",
    )
    assert result.returncode == 0, result.stderr
    assert f"enabled={expected}" in result.stdout


def test_interactive_hardware_test_timeout_is_bounded() -> None:
    result = _run_probe(
        {"PIXEL_REFINE_HARDWARE_TEST_TIMEOUT_S": "3"},
        """
from pixel_refine_desktop.ui.views.settings.General.GeneralSetting import _hardware_test_timeout_seconds
print('fast=' + str(_hardware_test_timeout_seconds('fast')))
print('deep=' + str(_hardware_test_timeout_seconds('deep')))
""",
    )
    assert result.returncode == 0, result.stderr
    assert "fast=10.0" in result.stdout
    assert "deep=10.0" in result.stdout
