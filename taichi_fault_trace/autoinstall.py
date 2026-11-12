"""Zero-configuration activation for the project venv.

A ``.pth`` file in ``venv/Lib/site-packages`` imports this module at
interpreter startup.  It stays lightweight: only a single-meta-path finder
for ``taichi`` is registered.  The tracer itself (which imports numpy) is
loaded on the first ``import taichi``, so unrelated Python tools in the venv
pay no cost.

Disable with ``TAICHI_FAULT=0``.
"""

from __future__ import annotations

import importlib.util
import os
import sys

_DISABLED = {"0", "off", "false", "no", "none", "disabled"}


def _enabled() -> bool:
    raw = os.environ.get("TAICHI_FAULT")
    if raw is None:
        return True
    return raw.strip().lower() not in _DISABLED


class _BootLoader:
    def __init__(self, loader, finder):
        self._loader = loader
        self._finder = finder

    def __getattr__(self, name):
        return getattr(self._loader, name)

    def create_module(self, spec):
        return self._loader.create_module(spec)

    def exec_module(self, module):
        self._loader.exec_module(module)
        self._finder.deactivate()
        _install_tracer()


class _BootFinder:
    def __init__(self):
        self._busy = False

    def find_spec(self, fullname, path=None, target=None):
        if fullname != "taichi" or self._busy:
            return None
        self._busy = True
        try:
            spec = importlib.util.find_spec(fullname)
        except Exception:
            return None
        finally:
            self._busy = False
        if spec is None or spec.loader is None:
            return None
        try:
            spec.loader = _BootLoader(spec.loader, self)
        except Exception:
            return spec
        return spec

    def deactivate(self) -> None:
        try:
            sys.meta_path.remove(self)
        except ValueError:
            pass

    def invalidate_caches(self):
        return None


def _install_tracer() -> None:
    try:
        import taichi_fault_trace as tracer

        tracer.install()
    except Exception as exc:  # pragma: no cover - never break interpreter boot
        try:
            sys.stderr.write(
                f"[taichi_fault_trace] autoinstall skipped: "
                f"{type(exc).__name__}: {exc}\n"
            )
        except Exception:
            pass


def activate() -> bool:
    """Register the boot finder (or install immediately if taichi is loaded)."""

    if not _enabled():
        return False
    if "taichi" in sys.modules:
        _install_tracer()
        return True
    for finder in sys.meta_path:
        if isinstance(finder, _BootFinder):
            return True
    sys.meta_path.insert(0, _BootFinder())
    return True


if __name__ == "__main__":  # pragma: no cover
    print("taichi_fault_trace autoinstall:", "enabled" if activate() else "disabled")
else:
    activate()
