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
from typing import Any, Mapping
from taichi_vision.backend_config import (
    is_android_runtime,
    requested_backend as _requested_backend,
)
from taichi_vision.cuda_arch_matrix import (
    bridge_target_status,
    load_bridge_manifest,
    profile_for,
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


def _device_metadata(device: Any) -> tuple[Mapping[str, Any], str, str]:
    """Normalize string or probe metadata without changing public selectors.

    Hardware probes commonly return a mapping with a generic device ``name``
    and a separate ``vendor`` field.  Keeping the normalization in one place
    prevents backend candidate selection from crashing on mappings or losing
    an explicit vendor declaration.
    """

    metadata: Mapping[str, Any] = device if isinstance(device, Mapping) else {}
    raw_name = metadata.get("name") or metadata.get("device_name") or device
    device_name = str(raw_name or "unknown")
    vendor_hint = str(
        metadata.get("vendor")
        or metadata.get("vendor_name")
        or metadata.get("manufacturer")
        or ""
    ).lower()
    searchable = f"{vendor_hint} {device_name.lower()}"
    vendor = (
        "intel"
        if "intel" in searchable
        else "nvidia"
        if ("nvidia" in searchable or "geforce" in searchable)
        else "amd"
        if ("amd" in searchable or "radeon" in searchable)
        else "unknown"
    )
    return metadata, device_name, vendor


def classify_device(device: Any, backend: str, driver: str = "unknown"):
    metadata, device_name, vendor = _device_metadata(device)
    name = device_name.lower()
    backend = backend.lower()
    if backend == "cuda":
        if vendor != "nvidia":
            return BackendCapabilities(
                backend,
                vendor,
                device_name,
                driver,
                safe=False,
                reason="CUDA requires an NVIDIA device",
            )
        raw_cc = metadata.get("compute_capability")
        if raw_cc not in (None, ""):
            try:
                profile = profile_for(raw_cc)
            except (TypeError, ValueError):
                return BackendCapabilities(
                    backend,
                    vendor,
                    device_name,
                    driver,
                    safe=False,
                    reason=f"Unknown CUDA compute capability: {raw_cc}",
                )
            bridge_manifest = load_bridge_manifest()
            manifest_status = bridge_target_status(raw_cc, bridge_manifest)
            if profile.compute_capability == 50 and manifest_status not in {
                "runtime_candidate",
                "native",
            }:
                return BackendCapabilities(
                    backend,
                    vendor,
                    device_name,
                    driver,
                    safe=False,
                    reason=(
                        "CUDA CC 5.0 Maxwell needs a regenerated TCM graph "
                        "lowering manifest; the generic runtime alone cannot "
                        "prove that legacy PTX dynamic-alloca paths are gone"
                    ),
                )
            if not profile.current_taichi_codegen_candidate:
                if manifest_status in {"runtime_candidate", "native"}:
                    qualification = (
                        "native-qualified"
                        if manifest_status == "native"
                        else "compile/runtime candidate"
                    )
                    return BackendCapabilities(
                        backend,
                        vendor,
                        device_name,
                        driver,
                        safe=True,
                        reason=(
                            f"CUDA CC {profile.compute_capability / 10:.1f} "
                            f"({profile.architecture}) is listed by the matching "
                            f"bridge manifest as {qualification}; native performance "
                            "still requires a strict device run"
                        ),
                    )
                return BackendCapabilities(
                    backend,
                    vendor,
                    device_name,
                    driver,
                    safe=False,
                    reason=(
                        f"CUDA CC {profile.compute_capability / 10:.1f} ({profile.architecture}) "
                        "is outside the current LLVM20 TCM-lowering candidate set; "
                        "complete the target graph sweep and rebuild a coherent bridge "
                        "before enabling it"
                    ),
                )
            if profile.architecture == "Maxwell":
                qualification = (
                    "native-qualified"
                    if manifest_status == "native"
                    else "compile-capable but runtime-unverified"
                )
                return BackendCapabilities(
                    backend,
                    vendor,
                    device_name,
                    driver,
                    safe=True,
                    reason=(
                        f"CUDA CC {profile.compute_capability / 10:.1f} Maxwell "
                        f"is {qualification}; strict device testing required"
                    ),
                )
        return BackendCapabilities(
            backend,
            vendor,
            device_name,
            driver,
            safe=True,
            reason="NVIDIA CUDA selected; compute capability will be validated by the native runtime",
        )
    if backend == "vulkan" and vendor == "intel":
        try:
            from taichi_vision.vulkan_probe import intel_vulkan_is_validated

            validated = intel_vulkan_is_validated(int(os.environ.get("AOT_DEVICE", 0)))
        except Exception:
            validated = False
        if validated:
            return BackendCapabilities(
                backend,
                vendor,
                device_name,
                driver,
                safe=True,
                reason="Intel Vulkan lifecycle, parity, and pipeline manifest validated",
            )
        return BackendCapabilities(
            backend,
            vendor,
            device_name,
            driver,
            safe=False,
            reason="Intel Vulkan AOT is quarantined after ABI/pipeline failures",
        )
    if backend == "opengl":
        return BackendCapabilities(
            backend,
            vendor,
            device_name,
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
            device_name,
            driver,
            safe=False,
            reason="GLES TCM/bridge static gates passed; Android device execution is pending",
        )
    return BackendCapabilities(backend, vendor, device_name, driver)


def requested_backend():
    return _requested_backend()[0]


def backend_candidates(device: Any = "unknown"):
    """Return deterministic preference order for automatic dispatch."""
    _, device_name, vendor = _device_metadata(device)
    auto_fallback = (
        os.environ.get("PIXEL_REFINE_AOT_AUTO_FALLBACK", "0") == "1"
    )
    if is_android_runtime():
        # Android's desktop-OpenGL spelling is not a valid artifact identity;
        # the resolver canonicalizes it to GLES. Keep the mobile preference
        # list explicit so auto mode never attempts a desktop OpenGL bridge.
        return ["vulkan", "gles", "cpu"]
    if vendor == "intel":
        try:
            from taichi_vision.vulkan_probe import intel_vulkan_is_validated

            if intel_vulkan_is_validated(int(os.environ.get("AOT_DEVICE", 0))):
                return ["vulkan", "opengl", "cpu"]
        except Exception:
            pass
        return ["opengl", "cpu"]
    # Auto-fallback order requested by the user: CUDA -> Vulkan -> OpenGL -> CPU.
    if vendor == "nvidia":
        return ["cuda", "vulkan", "opengl", "cpu"] if auto_fallback else ["vulkan", "opengl", "cpu"]
    if vendor == "amd":
        # CUDA is NVIDIA-only; never advertise it for an AMD device even when
        # the optional automatic-fallback switch is enabled.
        return ["vulkan", "opengl", "cpu"]
    return ["vulkan", "opengl", "cpu"] if auto_fallback else ["opengl", "vulkan", "cpu"]


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
        "guided": "from taichi_vision.taichi_aot import guided_filter_aot; guided_filter_aot(a,a,radius=1,epsilon=1e-3)",
        "inpaint": "from taichi_vision.taichi_aot import inpaint; inpaint(a,m,inpaint_radius=1)",
        "seamless": "from taichi_vision.taichi_aot import seamless_clone_aot; seamless_clone_aot(a,a,m,center=(4,4),max_iterations=2)",
        "median": "from taichi_vision.taichi_aot import median_filter, engine; b=engine.upload(a); median_filter(b); engine.sync(); b.destroy()",
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
