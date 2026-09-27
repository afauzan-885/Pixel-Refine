"""Lightweight target-aware TCM module loader shared by API and warm-up."""

from __future__ import annotations

import os
import threading

from .artifact_targets import detect_target, resolve_artifact


class AOTModuleLoader:
    """Resolve and cache logical AOT modules without importing the full API."""

    def __init__(self, engine, *, tcm_dir=None, cache=None):
        self.engine = engine
        self.tcm_dir = os.path.abspath(
            tcm_dir
            if tcm_dir is not None
            else os.path.join(
                os.path.dirname(__file__), "..", "taichi_algorithm", "aot_tcm"
            )
        )
        self.cache = cache if cache is not None else {}
        self._lock = threading.RLock()
        self._target_resolution_cache = {}

    @staticmethod
    def _local_target_has_artifacts(root, target):
        """Detect a usable project-local target without probing staging disks."""
        target_id = str(getattr(target, "target_id", "")).strip()
        if not target_id:
            return False
        candidates = [target_id]
        backend = str(getattr(target, "backend", "")).lower()
        if backend in {"vulkan", "opengl", "gles"}:
            for suffix in ("_intel", "_nvidia", "_amd"):
                generic_id = target_id.removesuffix(suffix)
                if generic_id != target_id:
                    candidates.append(generic_id)

        root = os.path.abspath(str(root))
        for candidate in candidates:
            candidate_dir = os.path.join(root, candidate)
            if os.path.isdir(candidate_dir):
                try:
                    if any(
                        item.is_file() and item.name.lower().endswith(".tcm")
                        for item in os.scandir(candidate_dir)
                    ):
                        return True
                except OSError:
                    pass
            suffix = f"_{candidate}.tcm".lower()
            try:
                if any(
                    item.is_file() and item.name.lower().endswith(suffix)
                    for item in os.scandir(root)
                ):
                    return True
            except OSError:
                pass
        return False

    def _module_is_current_locked(self, name):
        cached = self.cache.get(name)
        if cached is None:
            return None
        if (
            getattr(cached, "module_ptr", None)
            and getattr(cached, "engine_generation", None)
            == getattr(self.engine, "_generation", 0)
        ):
            return cached
        self.cache.pop(name, None)
        return None

    def resolve_target(self):
        target = detect_target(
            backend=getattr(self.engine, "arch", "cpu"),
            device=getattr(self.engine, "gpu_name", ""),
        )
        explicit_root = os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip()
        cache_key = (target.target_id, explicit_root, self.tcm_dir)
        cached = self._target_resolution_cache.get(cache_key)
        if cached is not None:
            return cached

        active_tcm_dir = self.tcm_dir
        if not explicit_root and not self._local_target_has_artifacts(
            active_tcm_dir, target
        ):
            try:
                from taichi_vision.llvm20_runtime_paths import tcm_root as staged_tcm_root

                staged_root = staged_tcm_root(target.target_id)
            except (ImportError, OSError, ValueError):
                staged_root = None
            if staged_root is not None:
                active_tcm_dir = os.path.abspath(str(staged_root))
        resolved = (target, active_tcm_dir)
        self._target_resolution_cache[cache_key] = resolved
        return resolved

    @staticmethod
    def resolve_module_path(name, target, active_tcm_dir):
        path_dir = os.path.join(active_tcm_dir, name)
        if os.path.isdir(path_dir):
            return path_dir

        allow_legacy = (
            os.environ.get("PIXEL_REFINE_AOT_ALLOW_LEGACY_ARTIFACTS", "0") == "1"
            and not target.is_arm
            and not target.is_mobile
        )
        resolved = resolve_artifact(
            active_tcm_dir,
            name,
            target,
            allow_legacy=allow_legacy,
        )
        if resolved is None:
            raise FileNotFoundError(
                f"No AOT artifact for target {target.target_id}: "
                f"algorithm={name!r}, root={active_tcm_dir!r}. "
                "Compile the target-qualified TCM before dispatch."
            )
        return str(resolved)

    def _load_resolved_module_locked(self, name, path):
        cached = self._module_is_current_locked(name)
        if cached is not None:
            return cached
        module = self.engine.load(path)
        self.cache[name] = module
        try:
            setattr(module, "logical_key", str(name))
        except Exception:
            pass
        return module

    def load(self, name):
        with self._lock:
            cached = self._module_is_current_locked(name)
            if cached is not None:
                try:
                    setattr(cached, "logical_key", str(name))
                except Exception:
                    pass
                return cached
            target, active_tcm_dir = self.resolve_target()
            path = self.resolve_module_path(name, target, active_tcm_dir)
            return self._load_resolved_module_locked(name, path)

    def warmup(self, names):
        """Batch-resolve and serially load modules for startup warm-up."""
        unique_names = tuple(dict.fromkeys(names))
        result = {
            "loaded_modules": 0,
            "total_modules": len(unique_names),
            "deferred_modules": [],
        }
        if not unique_names:
            return result

        with self._lock:
            pending = []
            for name in unique_names:
                if self._module_is_current_locked(name) is None:
                    pending.append(name)
                else:
                    result["loaded_modules"] += 1
            if not pending:
                return result

            try:
                target, active_tcm_dir = self.resolve_target()
            except Exception as exc:
                result["deferred_modules"].extend((name, exc) for name in pending)
                return result

            for name in pending:
                try:
                    path = self.resolve_module_path(name, target, active_tcm_dir)
                    self._load_resolved_module_locked(name, path)
                    result["loaded_modules"] += 1
                except Exception as exc:
                    # One optional artifact must not abort the rest of Pack 1.
                    result["deferred_modules"].append((name, exc))
        return result

    def clear(self):
        with self._lock:
            self.cache.clear()
            self._target_resolution_cache.clear()


__all__ = ["AOTModuleLoader"]
