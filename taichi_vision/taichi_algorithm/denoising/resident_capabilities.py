"""Capability identity for resident WeightNet artifacts.

The same pure function family is used by the compiler (to record what an
artifact requires) and by the loader (to describe the live device), so the
manifest validator can compare them with plain equality.

Scope of this gate (be explicit about what it does NOT prove):
  * It records the artifact's backend, FP32 requirement and the requirement
    that the live device is admitted as ``safe`` by the AOT capability policy
    (``taichi_aot.capabilities.classify_device``).
  * It refuses quarantined devices (e.g. an Intel Vulkan/OpenGL ICD that the
    policy has not admitted) and any backend mismatch.
  * It is NOT a hardware feature probe (SPIR-V extensions, driver limits,
    compute-capability bits). Target/arch/ABI/driver identity is validated
    separately through ``target_identity``.
"""
from __future__ import annotations

CAPABILITY_SCHEMA = 1


def required_capabilities(backend):
    """Requirements a resident artifact compiled for ``backend`` places on a device."""
    return {
        "schema": CAPABILITY_SCHEMA,
        "backend": str(backend).lower(),
        "fp32": True,
        "safe": True,
    }


def capability_identity(backend):
    """Manifest ``device_capabilities`` entry written by the compiler."""
    return {"status": "known", "requirements": required_capabilities(backend)}


def runtime_capabilities(backend, device=""):
    """Describe the live device in the same shape as ``required_capabilities``.

    ``fp32``/``safe`` come from the AOT capability policy for the actual
    device, so an unadmitted device yields ``safe=False`` and fails the
    manifest comparison instead of being silently accepted.
    """
    from taichi_vision.taichi_aot.capabilities import classify_device

    backend = str(backend).lower()
    if backend == "cuda" and not str(device or "").strip():
        device = "nvidia"
    caps = classify_device(device or "unknown", backend)
    return {
        "schema": CAPABILITY_SCHEMA,
        "backend": backend,
        "fp32": bool(caps.fp32),
        "safe": bool(caps.safe),
    }
