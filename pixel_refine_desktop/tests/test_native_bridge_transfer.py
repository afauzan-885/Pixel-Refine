"""Native bridge transfer contract (run in an isolated subprocess).

The bridge owns a process-global native runtime. Initialising and destroying it
inside the test process clobbers the runtime other suites use, so every check
here runs in a fresh interpreter. The third argument of allocate_gpu_buffer is
a host-accessible FLAG (1/0); passing 0 creates a VRAM-only buffer whose direct
read returns zeros without raising, which is the trap these tests pin.
"""

import os
import subprocess
import sys
import textwrap

import pytest

import taichi as ti

pytestmark = pytest.mark.skipif(
    not ti._TESTS_HAVE_VULKAN, reason="no Vulkan device on this host"
)

SCRIPT = textwrap.dedent(
    """
    import numpy as np
    import taichi as ti

    engine = ti.native_bridge.init_engine("vulkan", 0)
    host = ti.native_bridge.allocate_buffer(engine, 4096, host_accessible=True)
    source = np.full(1024, 2.5, dtype=np.float32)
    ti.native_bridge.write_buffer(engine, host, source)
    direct = np.zeros(1024, dtype=np.float32)
    ti.native_bridge.read_buffer(engine, host, direct)
    ti.native_bridge.sync(engine)
    print("HOST_ROUNDTRIP", bool(np.array_equal(direct, source)))
    ti.native_bridge.free_buffer(engine, host)

    device = ti.native_bridge.allocate_buffer(engine, 4096, host_accessible=False)
    staging = ti.native_bridge.allocate_buffer(engine, 4096, host_accessible=True)
    ramp = np.arange(1024, dtype=np.float32)
    ti.native_bridge.write_buffer(engine, device, ramp, staging=staging)
    staged = np.zeros(1024, np.float32)
    ti.native_bridge.read_buffer(engine, device, staged, staging=staging)
    print("STAGED_ROUNDTRIP", bool(np.array_equal(staged, ramp)))
    print("STAGED_EDGES", float(staged[0]), float(staged[-1]))

    blind = np.zeros(1024, np.float32)
    ti.native_bridge.read_buffer(engine, device, blind)
    print("VRAM_DIRECT_READ_IS_ZERO", bool(blind.max() == 0.0))
    print("LAST_ERROR", repr(ti.native_bridge.last_error(engine)))
    ti.native_bridge.free_buffer(engine, staging)
    ti.native_bridge.free_buffer(engine, device)
    ti.native_bridge.destroy_engine(engine)
    """
)


@pytest.fixture(scope="module")
def probe():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = dict(os.environ)
    env["PYTHONPATH"] = repo_root
    completed = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        capture_output=True,
        text=True,
        cwd=repo_root,
        env=env,
        timeout=420,
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    values = {}
    for line in completed.stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[0].isupper():
            values[parts[0]] = parts[1]
    return values


def test_host_accessible_roundtrip(probe):
    assert probe["HOST_ROUNDTRIP"] == "True"


def test_vram_buffer_roundtrip_through_staging(probe):
    assert probe["STAGED_ROUNDTRIP"] == "True"
    assert probe["STAGED_EDGES"] == "0.0 1023.0"


def test_direct_read_of_vram_buffer_is_silently_zero(probe):
    assert probe["VRAM_DIRECT_READ_IS_ZERO"] == "True"


def test_no_engine_error_after_transfers(probe):
    assert probe["LAST_ERROR"] == "''"
