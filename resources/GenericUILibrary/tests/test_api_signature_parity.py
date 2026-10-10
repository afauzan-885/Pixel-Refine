"""Check the PySide6 public API against the shared source contract."""

from __future__ import annotations

import ast
import importlib
import inspect
import json
from pathlib import Path

import UILibrary

GOLDEN = json.loads(
    (Path(__file__).parent / "golden_signatures.json").read_text(encoding="utf-8")
)
ALIASED = {"AnimatedTabContainer": "TabContainer"}
OMITTED = {"FeatureCardSelect"}
QT_ONLY = {
    "showEvent", "hideEvent", "paintEvent", "resizeEvent", "mousePressEvent",
    "mouseMoveEvent", "mouseReleaseEvent", "mouseDoubleClickEvent", "enterEvent",
    "leaveEvent", "wheelEvent", "keyPressEvent", "keyReleaseEvent", "eventFilter",
    "sizeHint", "minimumSizeHint", "event", "show", "hide", "close", "open",
    "deleteLater", "update", "repaint", "blockSignals", "setProperty", "property",
    "findChild", "findChildren", "installEventFilter", "setStyleSheet", "setObjectName",
    "objectName", "setFixedSize", "setFixedWidth", "setFixedHeight", "setSizePolicy",
    "setCursor", "setAccessibleName", "setAttribute", "setFocus", "clearFocus",
    "setMaximumWidth", "setMinimumWidth", "setContentsMargins", "setFont", "setPalette",
    "move", "lower", "adjustSize", "updateGeometry", "boundingRect", "setGeometry",
    "setSizePolicyFlags", "exec", "accept", "reject", "isVisible", "to_qml",
    "heightForWidth", "minimumHeightForWidth", "minimumWidthForHeight",
}


def _signature(callable_obj):
    params = list(inspect.signature(callable_obj).parameters.values())
    if params and params[0].name in {"self", "cls"}:
        params = params[1:]
    return [
        {
            "name": p.name,
            "kind": {
                inspect.Parameter.POSITIONAL_ONLY: "posonly",
                inspect.Parameter.POSITIONAL_OR_KEYWORD: "positional_or_keyword",
                inspect.Parameter.VAR_POSITIONAL: "var_positional",
                inspect.Parameter.KEYWORD_ONLY: "keyword_only",
                inspect.Parameter.VAR_KEYWORD: "var_keyword",
            }[p.kind],
            "default": None if p.default is inspect.Parameter.empty else p.default,
        }
        for p in params
    ]


def _matches(actual, expected):
    got = _signature(actual)
    wanted = expected["parameters"]
    if [(p["name"], p["kind"]) for p in got] != [
        (p["name"], p["kind"]) for p in wanted
    ]:
        return False
    for parameter, source in zip(got, wanted):
        raw = source["default"]
        try:
            default = ast.literal_eval(raw) if raw is not None else None
        except (SyntaxError, ValueError):
            continue  # Native Qt defaults are toolkit-specific.
        if parameter["default"] != default:
            return False
    return True


def test_pyside_public_signatures_match_shared_contract():
    gaps = []
    for module_name, module_spec in GOLDEN["modules"].items():
        module = importlib.import_module(f"UILibrary.{module_name}")
        for class_name, spec in module_spec["classes"].items():
            target = getattr(module, ALIASED.get(class_name, class_name), None)
            if target is None:
                if class_name not in OMITTED:
                    gaps.append(f"{module_name}.{class_name}: class missing")
                continue
            if spec["init"] and not _matches(target.__init__, spec["init"]):
                gaps.append(f"{module_name}.{class_name}.__init__: signature differs")
            for name, expected in spec["methods"].items():
                if name in QT_ONLY:
                    continue
                method = inspect.getattr_static(target, name, None)
                if isinstance(method, property):
                    method = method.fget
                if method is None:
                    gaps.append(f"{module_name}.{class_name}.{name}: method missing")
                elif not _matches(method, expected):
                    gaps.append(f"{module_name}.{class_name}.{name}: signature differs")
            for name in spec["signals"]:
                if not hasattr(target, name):
                    gaps.append(f"{module_name}.{class_name}.{name}: signal missing")
        for name, expected in module_spec["functions"].items():
            function = getattr(module, name, None)
            if function is None:
                gaps.append(f"{module_name}.{name}: function missing")
            elif not _matches(function, expected):
                gaps.append(f"{module_name}.{name}: signature differs")
    for name, expected in GOLDEN["root_functions"].items():
        function = getattr(UILibrary, name, None)
        if function is None:
            gaps.append(f"root.{name}: function missing")
        elif not _matches(function, expected):
            gaps.append(f"root.{name}: signature differs")
    assert gaps == [], "API contract gaps:\n" + "\n".join(gaps)


def test_composite_classes_remain_module_only():
    for module_name, class_name in (
        ("config_panel", "ConfigPanel"),
        ("selector_panel", "SelectorPanel"),
        ("viewer_panel", "ViewerPanel"),
        ("workspace_layout", "WorkspaceLayout"),
    ):
        assert hasattr(getattr(UILibrary, module_name), class_name)
        assert class_name not in UILibrary.__all__
        assert not hasattr(UILibrary, class_name)
