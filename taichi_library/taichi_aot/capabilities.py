"""Backend capability policy for automatic AOT dispatch.

The registry deliberately describes *validated* capabilities, not optimistic
hardware marketing claims.  Runtime probes can refine these values later and
the dispatcher can quarantine a backend without changing public APIs.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import os
import json
import subprocess
import sys
import tempfile


@dataclass(frozen=True)
class BackendCapabilities:
    backend: str
    vendor: str = "unknown"
    device: str = "unknown"
    driver: str = "unknown"
    safe: bool = True
    fp32: bool = True
    u8_native: bool = False
    u16_native: bool = False
    reason: str = ""

    def as_dict(self):
        return asdict(self)


def classify_device(device: str, backend: str, driver: str = "unknown"):
    name = (device or "unknown").lower()
    vendor = "intel" if "intel" in name else "nvidia" if ("nvidia" in name or "geforce" in name) else "unknown"
    backend = backend.lower()
    if backend == "vulkan" and vendor == "intel":
        return BackendCapabilities(backend, vendor, device, driver, safe=False,
                                   reason="Intel Vulkan AOT is quarantined after ABI/pipeline failures")
    if backend == "opengl":
        return BackendCapabilities(backend, vendor, device, driver, safe=True,
                                   reason="OpenGL artifact/load smoke tests validated")
    return BackendCapabilities(backend, vendor, device, driver)


def requested_backend():
    return (os.environ.get("PIXEL_REFINE_AOT_ARCH") or
            os.environ.get("PIXEL_REFINE_BACKEND") or "auto").lower()


def backend_candidates(device: str = "unknown"):
    """Return deterministic preference order for automatic dispatch."""
    name = (device or "").lower()
    if "intel" in name:
        return ["opengl", "cpu"]
    if "nvidia" in name or "geforce" in name:
        return ["vulkan", "opengl", "cpu"]
    if "amd" in name or "radeon" in name:
        return ["vulkan", "opengl", "cpu"]
    return ["opengl", "vulkan", "cpu"]


def opengl_native_probe(operation: str, timeout: float = 8.0) -> bool:
    """Return whether a risky OpenGL operation survives on this driver.

    The probe is deliberately executed in a child process: several Intel
    drivers abort inside ``glBindBufferBase`` rather than raising a Python
    exception.  A failed probe therefore cannot corrupt the caller. Results
    are cached per Python/driver environment for the lifetime of the process.
    """
    if os.environ.get("PIXEL_REFINE_AOT_GL_PROBE") == "1":
        return True
    if operation not in {"guided", "inpaint", "seamless", "median"}:
        return False
    cache = getattr(opengl_native_probe, "_cache", None)
    if cache is None:
        cache = opengl_native_probe._cache = {}
    cache_key = (operation, os.environ.get("PIXEL_REFINE_AOT_ARCH", "opengl"),
                 os.environ.get("PIXEL_REFINE_AOT_DEVICE", "0"))
    if cache_key in cache:
        return cache[cache_key]
    snippets = {
        "guided": "from taichi_library.taichi_aot import guided_filter_aot; guided_filter_aot(a,a,radius=1,epsilon=1e-3)",
        "inpaint": "from taichi_library.taichi_aot import inpaint; inpaint(a,m,inpaint_radius=1)",
        "seamless": "from taichi_library.taichi_aot import seamless_clone_aot; seamless_clone_aot(a,a,m,center=(4,4),max_iterations=2)",
        "median": "from taichi_library.taichi_aot import median_filter, engine; b=engine.upload(a); median_filter(b); engine.sync(); b.destroy()",
    }
    shape_init = ("a=np.ones((8,8,3), np.float32); m=np.ones((8,8), np.float32); "
                  if operation == "seamless" else
                  "a=np.ones((8,8), np.float32); m=np.ones((8,8), np.float32); ")
    if operation == "median":
        shape_init = "a=np.ones((8,8,3), np.float32); m=np.ones((8,8), np.float32); "
    code = ("import os, numpy as np; os.environ['PIXEL_REFINE_AOT_GL_PROBE']='1'; "
            "os.environ['PIXEL_REFINE_AOT_NATIVE_%s']='1'; " % operation.upper() +
            shape_init + snippets[operation])
    try:
        probe_timeout = 30.0 if operation == "seamless" else timeout
        result = subprocess.run([sys.executable, "-c", code], capture_output=True,
                                timeout=probe_timeout, env=os.environ.copy())
        ok = result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        ok = False
    cache[cache_key] = ok
    return ok
