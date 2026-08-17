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
from taichi_library.backend_config import (
    is_android_runtime,
    requested_backend as _requested_backend,
)


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
    vendor = (
        "intel"
        if "intel" in name
        else "nvidia" if ("nvidia" in name or "geforce" in name) else "unknown"
    )
    backend = backend.lower()
    if backend == "vulkan" and vendor == "intel":
        try:
            from taichi_library.vulkan_probe import intel_vulkan_is_validated

            validated = intel_vulkan_is_validated(int(os.environ.get("AOT_DEVICE", 0)))
        except Exception:
            validated = False
        if validated:
            return BackendCapabilities(
                backend,
                vendor,
                device,
                driver,
                safe=True,
                reason="Intel Vulkan lifecycle, parity, and pipeline manifest validated",
            )
        return BackendCapabilities(
            backend,
            vendor,
            device,
            driver,
            safe=False,
            reason="Intel Vulkan AOT is quarantined after ABI/pipeline failures",
        )
    if backend == "opengl":
        return BackendCapabilities(
            backend,
            vendor,
            device,
            driver,
            safe=True,
            reason="OpenGL artifact/load smoke tests validated",
        )
    if backend == "gles":
        # GLES artifacts and the ARM64 bridge are statically validated, but a
        # real Android GLES context is required before automatic dispatch can
        # call this target.  Keep it visible to diagnostics without allowing a
        # desktop process to treat a cross-compiled mobile target as ready.
        return BackendCapabilities(
            backend,
            vendor,
            device,
            driver,
            safe=False,
            reason="GLES TCM/bridge static gates passed; Android device execution is pending",
        )
    return BackendCapabilities(backend, vendor, device, driver)


def requested_backend():
    return _requested_backend()[0]


def backend_candidates(device: str = "unknown"):
    """Return deterministic preference order for automatic dispatch."""
    name = (device or "").lower()
    if is_android_runtime():
        # Android's desktop-OpenGL spelling is not a valid artifact identity;
        # the resolver canonicalizes it to GLES. Keep the mobile preference
        # list explicit so auto mode never attempts a desktop OpenGL bridge.
        return ["vulkan", "gles", "cpu"]
    if "intel" in name:
        try:
            from taichi_library.vulkan_probe import intel_vulkan_is_validated

            if intel_vulkan_is_validated(int(os.environ.get("AOT_DEVICE", 0))):
                return ["vulkan", "opengl", "cpu"]
        except Exception:
            pass
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
    if os.environ.get("AOT_GL_PROBE") == "1":
        return True
    if operation not in {"guided", "inpaint", "seamless", "median"}:
        return False
    cache = getattr(opengl_native_probe, "_cache", None)
    if cache is None:
        cache = opengl_native_probe._cache = {}
    cache_key = (operation, _requested_backend()[0], os.environ.get("AOT_DEVICE", "0"))
    if cache_key in cache:
        return cache[cache_key]
    snippets = {
        "guided": "from taichi_library.taichi_aot import guided_filter_aot; guided_filter_aot(a,a,radius=1,epsilon=1e-3)",
        "inpaint": "from taichi_library.taichi_aot import inpaint; inpaint(a,m,inpaint_radius=1)",
        "seamless": "from taichi_library.taichi_aot import seamless_clone_aot; seamless_clone_aot(a,a,m,center=(4,4),max_iterations=2)",
        "median": "from taichi_library.taichi_aot import median_filter, engine; b=engine.upload(a); median_filter(b); engine.sync(); b.destroy()",
    }
    shape_init = (
        "a=np.ones((8,8,3), np.float32); m=np.ones((8,8), np.float32); "
        if operation == "seamless"
        else "a=np.ones((8,8), np.float32); m=np.ones((8,8), np.float32); "
    )
    if operation == "median":
        shape_init = "a=np.ones((8,8,3), np.float32); m=np.ones((8,8), np.float32); "
    code = (
        "import os, numpy as np; os.environ['AOT_GL_PROBE']='1'; "
        "os.environ['AOT_NATIVE_%s']='1'; " % operation.upper()
        + shape_init
        + snippets[operation]
    )
    try:
        probe_timeout = 30.0 if operation == "seamless" else timeout
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            timeout=probe_timeout,
            env=os.environ.copy(),
        )
        ok = result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        ok = False
    cache[cache_key] = ok
    return ok
