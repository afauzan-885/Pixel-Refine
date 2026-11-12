"""Module loading parity: legacy engine vs the migrated bridge client.

Loading runs in a fresh interpreter per side because both paths bind a
process-global native runtime; doing it in-process would clobber the runtime
other suites rely on. Note the artifact cache must be disabled: a stale
quarantine entry from an earlier failed attempt short-circuits loading before
the native runtime is ever asked.
"""
import taichi.aot_engine as _ti_rt

import os
import subprocess
import sys
import textwrap

import pytest

import taichi as ti

pytestmark = pytest.mark.skipif(
    not ti._TESTS_HAVE_VULKAN, reason="no Vulkan device on this host"
)

ARTIFACT = os.path.join(
    "taichi_vision",
    "taichi_algorithm",
    "aot_tcm",
    "vulkan_x86_64_windows",
    "box_filter_vulkan_x86_64_windows.tcm",
)

LEGACY_SCRIPT = textwrap.dedent(
    """
    import os
    os.environ["PIXEL_REFINE_AOT_DISABLE_CACHE"] = "1"
    from taichi_vision import algorithm as tv

    engine = _ti_rt.get_engine()
    try:
        engine.load(os.environ["AOT_TEST_ARTIFACT"])
        print("LEGACY_LOAD True")
    except Exception as exc:
        print("LEGACY_LOAD False", str(exc).replace(chr(10), " ")[:200])
    """
)

CLIENT_SCRIPT = textwrap.dedent(
    """
    import os
    os.environ["PIXEL_REFINE_AOT_DISABLE_CACHE"] = "1"
    import taichi as ti

    handle = ti.native_bridge.init_engine("vulkan", 0)
    try:
        module = ti.native_bridge.load_module(
            handle, os.environ["AOT_TEST_ARTIFACT"], arch="vulkan"
        )
        ti.native_bridge.destroy_module(module)
        print("CLIENT_LOAD True")
    except Exception as exc:
        print("CLIENT_LOAD False", str(exc).replace(chr(10), " ")[:200])
    finally:
        ti.native_bridge.destroy_engine(handle)
    """
)


def _run(script):
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = dict(os.environ)
    env["PYTHONPATH"] = repo_root
    env["AOT_TEST_ARTIFACT"] = ARTIFACT
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=repo_root,
        env=env,
        timeout=420,
    )
    assert completed.returncode == 0, completed.stderr[-1500:]
    for line in completed.stdout.splitlines():
        if line.startswith(("LEGACY_LOAD", "CLIENT_LOAD")):
            return line
    raise AssertionError(f"no verdict in output: {completed.stdout[-800:]}")


def test_module_load_parity():
    legacy = _run(LEGACY_SCRIPT)
    client = _run(CLIENT_SCRIPT)
    legacy_ok = legacy.split()[1] == "True"
    client_ok = client.split()[1] == "True"
    assert legacy_ok, f"legacy baseline failed, so parity cannot be claimed: {legacy}"
    assert client_ok, f"migrated client failed while legacy succeeded: {client}"


def test_stale_quarantine_blocks_loading():
    """Documents why a cached quarantine must not be mistaken for a real failure."""
    assert ARTIFACT.endswith(".tcm")
    assert os.path.exists(ARTIFACT)