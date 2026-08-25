"""Dependency-free backend naming and configuration primitives.

This module deliberately lives at the ``taichi_vision`` root so compiler
workers and settings code can normalize a backend without importing
``taichi_vision.taichi_aot`` (whose package initializer creates a native
runtime).  The AOT package re-exports the same symbols for public callers.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from typing import Mapping, Optional


CANONICAL_BACKENDS = ("cpu", "cuda", "vulkan", "opengl", "gles")
GPU_BACKENDS = frozenset(("cuda", "vulkan", "opengl", "gles"))

_ALIASES = {
    "host": "cpu",
    "x86": "cpu",
    "x86_64": "cpu",
    "cpu_x86_64": "cpu",
    "cpu_windows": "cpu",
    "cpu_x86_64_windows": "cpu",
    "cuda_native": "cuda",
    "cuda_x86_64": "cuda",
    "cuda_x86_64_windows": "cuda",
    "cuda_x86_64_windows_nvidia": "cuda",
    "vk": "vulkan",
    "vulkan_desktop": "vulkan",
    "vulkan_x86_64": "vulkan",
    "vulkan_x86_64_windows": "vulkan",
    "gl": "opengl",
    "egl": "opengl",
    "gles": "gles",
    "opengl_es": "gles",
    "opengl_es3": "gles",
    "opengl_es_2": "gles",
    "opengl_es_3": "gles",
    "gles2": "gles",
    "gles3": "gles",
    "opengl_desktop": "opengl",
    "opengl_x86_64": "opengl",
    "opengl_x86_64_windows": "opengl",
    "gpu": "auto",
    "automatic": "auto",
    "default": "auto",
}


def _token(value) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def normalize_backend(value, *, allow_auto: bool = True, strict: bool = False) -> str:
    """Return one canonical backend name or ``auto`` for an unset value."""

    token = _ALIASES.get(_token(value), _token(value))
    if token in CANONICAL_BACKENDS:
        return token
    if token in ("", "auto") and allow_auto:
        return "auto"
    if strict:
        allowed = ", ".join(CANONICAL_BACKENDS)
        raise ValueError(f"Unsupported backend {value!r}; choose one of: {allowed}")
    return "auto" if allow_auto else "cpu"


def is_android_runtime(environ: Optional[Mapping[str, str]] = None) -> bool:
    """Return whether the current process is running inside Android.

    Android Python distributions do not consistently report a distinct
    ``sys.platform`` value, so use the standard runtime environment markers.
    Keeping this helper dependency-free lets the loader canonicalize an old
    ``opengl`` setting to the target-qualified ``gles`` backend before a
    bridge or artifact is selected.
    """

    env = os.environ if environ is None else environ
    return bool(
        env.get("ANDROID_ROOT")
        or env.get("ANDROID_DATA")
        or "ANDROID_ARGUMENT" in env
    )


def normalize_vendor(value) -> str:
    """Normalize a device/vendor label for matching and persisted settings."""

    token = _token(value)
    if any(part in token for part in ("nvidia", "geforce", "quadro", "rtx", "gtx")):
        return "nvidia"
    if any(part in token for part in ("intel", "uhd", "iris", "arc")):
        return "intel"
    if any(part in token for part in ("amd", "radeon", "advanced_micro_devices")):
        return "amd"
    if token in ("cpu", "host", "universal") or token.startswith("cpu_"):
        return "cpu"
    return "unknown"


def parse_device_id(value, default: Optional[int] = None) -> Optional[int]:
    """Parse a non-negative device ordinal without raising on stale config."""

    if value in (None, ""):
        return default
    try:
        ordinal = int(str(value).strip(), 0)
    except (TypeError, ValueError):
        return default
    return ordinal if ordinal >= 0 else default


def requested_backend(
    prefer=None,
    *,
    arch=None,
    environ: Optional[Mapping[str, str]] = None,
) -> tuple[str, bool, str]:
    """Resolve the requested backend without probing hardware."""

    env = os.environ if environ is None else environ
    candidates = (
        (arch, "argument"),
        (env.get("PIXEL_REFINE_AOT_ARCH"), "PIXEL_REFINE_AOT_ARCH"),
        (prefer, "argument_preference"),
        (env.get("PIXEL_REFINE_BACKEND"), "PIXEL_REFINE_BACKEND"),
        # ``AOT_ARCH`` is the long-standing environment knob used by the
        # standalone test harnesses and older callers.  Keep it as a legacy
        # alias so an explicit CPU/CUDA/Vulkan request cannot be overwritten
        # by automatic hardware selection during module import.
        (env.get("AOT_ARCH"), "AOT_ARCH"),
    )
    for value, source in candidates:
        if value is None:
            continue
        token = normalize_backend(value, allow_auto=True, strict=True)
        if token != "auto":
            return token, True, source
    return "auto", False, "auto"


@dataclass(frozen=True)
class BackendConfig:
    """Resolved backend/device contract passed into the native engine."""

    backend: str = "cpu"
    device_id: int = 0
    vendor: str = "unknown"
    device_name: str = ""
    explicit: bool = False
    source: str = "auto"
    strict: bool = False

    def __post_init__(self):
        object.__setattr__(self, "backend", normalize_backend(self.backend, allow_auto=False, strict=True))
        object.__setattr__(self, "device_id", parse_device_id(self.device_id, 0) or 0)
        object.__setattr__(self, "vendor", normalize_vendor(self.vendor))

    @property
    def is_gpu(self) -> bool:
        return self.backend in GPU_BACKENDS

    @property
    def target_family(self) -> str:
        if self.backend == "cpu":
            return "cpu_x86_64_windows"
        if self.backend == "cuda":
            return "cuda_x86_64_windows_nvidia"
        if self.backend == "vulkan":
            return "vulkan_desktop"
        if self.backend == "gles":
            return "gles_mobile"
        return "opengl_desktop"

    def with_device(self, *, device_id=None, vendor=None, device_name=None):
        return replace(
            self,
            device_id=self.device_id if device_id is None else device_id,
            vendor=self.vendor if vendor is None else vendor,
            device_name=self.device_name if device_name is None else device_name,
        )

    def as_dict(self) -> dict:
        return {
            "backend": self.backend,
            "device_id": self.device_id,
            "vendor": self.vendor,
            "device_name": self.device_name,
            "explicit": self.explicit,
            "source": self.source,
            "strict": self.strict,
            "is_gpu": self.is_gpu,
            "target_family": self.target_family,
        }


def backend_env(config: BackendConfig) -> dict[str, str]:
    """Return canonical environment keys for a child process/compiler."""

    values = {
        "PIXEL_REFINE_AOT_ARCH": config.backend,
        "PIXEL_REFINE_AOT_DEVICE": str(config.device_id),
    }
    if config.backend == "cuda":
        values["PIXEL_REFINE_CUDA_DEVICE"] = str(config.device_id)
    return values


__all__ = [
    "BackendConfig",
    "CANONICAL_BACKENDS",
    "GPU_BACKENDS",
    "backend_env",
    "is_android_runtime",
    "normalize_backend",
    "normalize_vendor",
    "parse_device_id",
    "requested_backend",
]
