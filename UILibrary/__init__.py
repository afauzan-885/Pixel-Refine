"""Canonical import alias for the PySide6 GenericUILibrary backend.

Applications can use ``import UILibrary as ui`` on both supported backends.
The installed checkout supplies the implementation selected by
``UILIBRARY_BACKEND``; this checkout binds that name to GenericUILibrary.
"""

from __future__ import annotations

import importlib
import os
import sys

_backend = os.environ.get("UILIBRARY_BACKEND", "pyside6").strip().lower()
if _backend not in {"pyside6", "flet"}:
    raise ValueError("UILIBRARY_BACKEND must be 'pyside6' or 'flet'")
if _backend != "pyside6":
    raise RuntimeError(
        "This checkout provides the PySide6 UILibrary backend; install/select "
        "the Flet UILibrary package when UILIBRARY_BACKEND=flet."
    )

_implementation = importlib.import_module("resources.GenericUILibrary")
_module_names = (
    "buttons", "forms", "containers", "cards", "list_group", "image_grid",
    "empty_state", "skeleton", "modals", "overlays", "grids", "tables",
    "tabs", "collapse", "navbar", "progress_bars", "comparison",
    "horizontal_scroll", "dot_indicator", "bottom_action_bar", "ui_component",
    "store", "mixins", "live_update", "theme", "config_panel",
    "selector_panel", "viewer_panel", "workspace_layout", "style_spec",
)
for _name in _module_names:
    _module = importlib.import_module(f"resources.GenericUILibrary.{_name}")
    sys.modules[f"{__name__}.{_name}"] = _module
    # GenericUILibrary exports ``live_update`` as a package-level decorator.
    # Keep that callable instead of shadowing it with the same-named submodule.
    if _name != "live_update":
        setattr(_implementation, _name, _module)

_implementation.BACKEND = "pyside6"
sys.modules[__name__] = _implementation
