"""Side-effect-free resolution of the isolated LLVM20 runtime payload.

The resolver keeps the public Taichi API unchanged while making the pruned
LLVM20 release payload the preferred Windows runtime once it exists.  An
explicit ``PIXEL_REFINE_RUNTIME_ROOT`` always wins.  If no explicit root is
supplied, the developer-machine release is selected when it contains the
expected bundle layout, with the development staging root as a transitional
fallback; otherwise callers retain their historical repository fallback.

No Taichi or GPU module is imported here.  This module is safe to use from
packagers, compiler workers, and the runtime bridge loader.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


LLVM20_STAGING_ROOT = Path(r"D:\development_build\taichi_runtime_llvm20")
LLVM20_RELEASE_ROOT = LLVM20_STAGING_ROOT / "release"
PROJECT_ROOT = Path(__file__).resolve().parent
PROJECT_TCM_ROOT = PROJECT_ROOT / "taichi_algorithm" / "aot_tcm"
PROJECT_BRIDGE_ROOT = PROJECT_ROOT / "taichi_algorithm" / "aot_py" / "aot_dll"


def _project_backend_dir(target_id: str) -> Optional[Path]:
    """Return the project-local bridge directory for a desktop target."""

    backend = str(target_id or "").split("_", 1)[0].lower()
    if backend not in {"cpu", "cuda", "vulkan", "opengl"}:
        return None
    candidate = PROJECT_BRIDGE_ROOT / backend
    bridge_name = "taichi_aot_engine.dll"
    return candidate if candidate.is_dir() and (candidate / bridge_name).is_file() else None


def runtime_root() -> Optional[Path]:
    """Return the active LLVM20 staging root, if a valid one is available."""

    explicit = os.environ.get("PIXEL_REFINE_RUNTIME_ROOT", "").strip()
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if not candidate.is_dir():
            raise RuntimeError(
                "PIXEL_REFINE_RUNTIME_ROOT does not exist or is not a directory: "
                f"{candidate}"
            )
        # An explicit path is authoritative, but it must still be a runtime
        # root.  Accepting any existing directory here lets a stale build or
        # source checkout silently fall through to legacy bridge/TCM search in
        # callers.  The bundle directory is the smallest invariant shared by
        # both the pruned release payload and the development staging tree.
        if not (candidate / "bundles").is_dir():
            raise RuntimeError(
                "PIXEL_REFINE_RUNTIME_ROOT is not a qualified LLVM20 runtime "
                f"root (missing bundles directory): {candidate}"
            )
        return candidate

    # Auto-discovery is intentionally limited to the known developer staging
    # root.  Prefer the pruned release payload so normal application launches
    # do not accidentally bind to compiler/development artifacts.  Keep the
    # parent staging tree as a compatibility fallback while the release is
    # being assembled or when a developer explicitly needs its extra files.
    if LLVM20_RELEASE_ROOT.is_dir() and (LLVM20_RELEASE_ROOT / "bundles").is_dir():
        return LLVM20_RELEASE_ROOT
    if LLVM20_STAGING_ROOT.is_dir() and (LLVM20_STAGING_ROOT / "bundles").is_dir():
        return LLVM20_STAGING_ROOT
    return None


def bundle_root(target_id: str) -> Optional[Path]:
    """Resolve one target-qualified runtime bundle without cross-target search."""

    # Prefer the checked-in project bridge when it exists.  TCM resolution is
    # intentionally separate below, allowing a staged migration where the
    # project DLL is current but a GPU TCM still comes from the release bundle.
    project_bridge = _project_backend_dir(target_id)
    if project_bridge is not None:
        return project_bridge

    root = runtime_root()
    if root is None:
        return None
    safe_target = str(target_id or "").strip()
    if not safe_target or Path(safe_target).name != safe_target:
        raise ValueError(f"unsafe runtime target id: {target_id!r}")
    candidates = [root / "bundles" / safe_target, root / safe_target]
    # Desktop OpenGL/Vulkan bundles are vendor-neutral at the artifact level;
    # the physical ICD/device is negotiated at runtime.  Allow their
    # target-qualified vendor probe to resolve to the generic desktop bundle,
    # but never apply this alias to CUDA (whose vendor ABI is NVIDIA-specific).
    if safe_target.startswith(("opengl_", "vulkan_")):
        for suffix in ("_nvidia", "_intel"):
            base = safe_target.removesuffix(suffix)
            if base != safe_target:
                candidates.extend((root / "bundles" / base, root / base))
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def tcm_root(target_id: str) -> Optional[Path]:
    """Resolve the exact TCM root for a target-qualified bundle."""

    project_target = PROJECT_TCM_ROOT / str(target_id or "")
    if project_target.is_dir() and any(project_target.glob("*.tcm")):
        return project_target

    root = runtime_root()
    if root is None:
        return None
    safe_target = str(target_id or "").strip()
    candidates = [root / "bundles" / safe_target, root / safe_target]
    if safe_target.startswith(("opengl_", "vulkan_")):
        for suffix in ("_nvidia", "_intel"):
            base = safe_target.removesuffix(suffix)
            if base != safe_target:
                candidates.extend((root / "bundles" / base, root / base))
    for bundle in candidates:
        nested = bundle / "tcm" / bundle.name
        if nested.is_dir():
            return nested
        direct = bundle / "tcm"
        if direct.is_dir():
            return direct
    return None


__all__ = [
    "LLVM20_STAGING_ROOT",
    "LLVM20_RELEASE_ROOT",
    "runtime_root",
    "bundle_root",
    "tcm_root",
]
