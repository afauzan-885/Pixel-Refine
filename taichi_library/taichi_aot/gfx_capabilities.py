"""Negotiated OpenGL/GLES/Vulkan capability policy.

This is a pure policy layer.  Probes supply version, extensions, limits, and
feature bits; this module decides which artifact tier is safe.  It deliberately
does not equate a legacy rendering API with Taichi's compute-capable path.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Mapping


# Keep probe spellings interchangeable while exposing one stable policy name.
# Vulkan probes commonly report ``storage_buffer`` or
# ``shader_storage_buffer`` whereas the TCM ABI calls the feature ``SSBO``.
_FEATURE_ALIASES = {
    "compute": "compute",
    "compute_shader": "compute",
    "compute_queue": "compute",
    "ssbo": "ssbo",
    "storage_buffer": "ssbo",
    "shader_storage_buffer": "ssbo",
    "shader_storage_buffer_object": "ssbo",
}

# The policy intentionally has explicit upper bounds as well as minimums.
# Probing a future/unknown API version must not silently qualify an artifact
# built and validated only against today's ABI contract.
_OPENGL_MAX_API = (4, 6)
_GLES_MAX_API = (3, 2)
_VULKAN_MIN_API = (1, 0)
_VULKAN_MAX_API = (1, 4)
_SPIRV_MIN_VERSION = (1, 0)
_SPIRV_MAX_VERSION = (1, 6)


@dataclass(frozen=True)
class GfxDecision:
    backend: str
    status: str
    profile: str
    reason: str
    api_version: tuple[int, int]
    spirv_version: tuple[int, int] = (0, 0)

    @property
    def usable(self) -> bool:
        return self.status in {"native_candidate", "software_candidate"}


def parse_version(value: object) -> tuple[int, int]:
    if isinstance(value, (tuple, list)) and len(value) >= 2:
        return int(value[0]), int(value[1])
    text = str(value or "").strip().lower()
    # Driver probes use several equivalent spellings, e.g. ``1.3.280``,
    # ``VK_API_VERSION_1_3`` and ``OpenGL ES 3.2``.  Extract exactly the
    # major/minor pair while ignoring patch/build fields.  Requiring two
    # numeric components keeps an incomplete value fail-closed.
    match = re.search(r"(?<!\d)(\d+)[._-](\d+)(?!\d)", text)
    if match is None:
        raise ValueError(f"invalid graphics API version: {value!r}")
    return int(match.group(1)), int(match.group(2))


def _feature_set(features: Iterable[str] | Mapping[str, object]) -> frozenset[str]:
    def canonical(value: object) -> str:
        raw = str(value).strip().lower().replace("-", "_").replace(" ", "_")
        return _FEATURE_ALIASES.get(raw, raw)

    if isinstance(features, Mapping):
        return frozenset(
            canonical(key) for key, enabled in features.items() if bool(enabled)
        )
    return frozenset(canonical(feature) for feature in features)


def classify_desktop_opengl(
    version: object,
    extensions: Iterable[str] | Mapping[str, object] = (),
    *,
    compute_shader: bool | None = None,
    ssbo: bool | None = None,
) -> GfxDecision:
    api = parse_version(version)
    ext = _feature_set(extensions)
    if api < (2, 0) or api > _OPENGL_MAX_API:
        return GfxDecision(
            "opengl",
            "unsupported",
            "desktop-gl-unknown",
            f"desktop OpenGL API {api} is outside the qualified 2.0-{_OPENGL_MAX_API[0]}.{_OPENGL_MAX_API[1]} range",
            api,
        )
    has_compute = bool(compute_shader) if compute_shader is not None else (
        api >= (4, 3) or "gl_arb_compute_shader" in ext
    )
    has_ssbo = bool(ssbo) if ssbo is not None else (
        api >= (4, 3)
        or "gl_shader_storage_buffer_object" in ext
        or "gl_arb_shader_storage_buffer_object" in ext
        or "gl_ext_shader_storage_buffer_object" in ext
    )
    if api < (4, 3):
        return GfxDecision("opengl", "legacy_render", "desktop-gl-legacy", "compute shaders are unavailable below OpenGL 4.3", api)
    if not (has_compute and has_ssbo):
        return GfxDecision("opengl", "unsupported", "desktop-gl-4.3", "missing compute shader or SSBO capability", api)
    return GfxDecision("opengl", "native_candidate", "desktop-gl-4.3", "compute shader and SSBO capability detected", api, (1, 3))


def classify_gles(
    version: object,
    extensions: Iterable[str] | Mapping[str, object] = (),
    *,
    compute_shader: bool | None = None,
    ssbo: bool | None = None,
) -> GfxDecision:
    api = parse_version(version)
    ext = _feature_set(extensions)
    if api < (2, 0) or api > _GLES_MAX_API:
        return GfxDecision(
            "gles",
            "unsupported",
            "gles-unknown",
            f"OpenGLES API {api} is outside the qualified 2.0-{_GLES_MAX_API[0]}.{_GLES_MAX_API[1]} range",
            api,
        )
    has_compute = bool(compute_shader) if compute_shader is not None else api >= (3, 1)
    has_ssbo = bool(ssbo) if ssbo is not None else api >= (3, 1)
    if api < (3, 1):
        return GfxDecision("gles", "legacy_render", "gles-legacy", "compute shaders are unavailable below GLES 3.1", api)
    if not (has_compute and has_ssbo):
        return GfxDecision("gles", "unsupported", "gles-3.1", "missing compute shader or SSBO capability", api)
    return GfxDecision("gles", "native_candidate", "gles-3.1", "compute shader and SSBO capability detected", api, (1, 3))


def minimum_vulkan_for_spirv(spirv: object) -> tuple[int, int]:
    version = parse_version(spirv)
    if version >= (1, 6):
        return (1, 3)
    if version >= (1, 5):
        return (1, 2)
    if version >= (1, 3):
        return (1, 1)
    return (1, 0)


def classify_vulkan(
    device_version: object,
    *,
    features: Iterable[str] | Mapping[str, object] | None = None,
    required_spirv: object = "1.3",
    required_features: Iterable[str] = ("compute", "ssbo"),
    software: bool = False,
) -> GfxDecision:
    """Classify a Vulkan device for the graphics TCM profile.

    The default feature floor mirrors the TCM runtime contract: a compute
    queue and storage-buffer support are both required.  Diagnostic callers
    that intentionally validate a narrower capability can pass an explicit
    ``required_features`` tuple; doing so does not promote any native runtime
    evidence or alter backend dispatch.
    """
    api = parse_version(device_version)
    spirv = parse_version(required_spirv)
    if api < _VULKAN_MIN_API or api > _VULKAN_MAX_API:
        return GfxDecision(
            "vulkan",
            "unsupported",
            "vulkan-unknown",
            f"Vulkan API {api} is outside the qualified {_VULKAN_MIN_API[0]}.{_VULKAN_MIN_API[1]}-{_VULKAN_MAX_API[0]}.{_VULKAN_MAX_API[1]} range",
            api,
            spirv,
        )
    if spirv < _SPIRV_MIN_VERSION or spirv > _SPIRV_MAX_VERSION:
        return GfxDecision(
            "vulkan",
            "unsupported",
            f"vulkan-{api[0]}.{api[1]}",
            f"SPIR-V version {spirv} is outside the qualified {_SPIRV_MIN_VERSION[0]}.{_SPIRV_MIN_VERSION[1]}-{_SPIRV_MAX_VERSION[0]}.{_SPIRV_MAX_VERSION[1]} range",
            api,
            spirv,
        )
    minimum = minimum_vulkan_for_spirv(spirv)
    if api < minimum:
        return GfxDecision("vulkan", "unsupported", f"vulkan-{minimum[0]}.{minimum[1]}", f"device API {api} cannot consume SPIR-V {spirv}", api, spirv)
    if features is None:
        return GfxDecision("vulkan", "unknown", f"vulkan-{api[0]}.{api[1]}", "physical-device feature probe is required", api, spirv)
    feature_set = _feature_set(features)
    required = tuple(dict.fromkeys(_feature_set(required_features)))
    missing = tuple(feature for feature in required if feature not in feature_set)
    if missing:
        labels = ", ".join(missing)
        return GfxDecision(
            "vulkan",
            "unsupported",
            f"vulkan-{api[0]}.{api[1]}",
            f"required Vulkan feature(s) missing: {labels}",
            api,
            spirv,
        )
    profile = f"vulkan-{min(api, (1, 4))[0]}.{min(api, (1, 4))[1]}"
    status = "software_candidate" if software else "native_candidate"
    return GfxDecision("vulkan", status, profile, "device API and SPIR-V profile are compatible", api, spirv)
