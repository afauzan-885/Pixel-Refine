"""Regression tests for safe non-3D cleanup refactors."""

import ast
import importlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESKTOP_ROOT = REPO_ROOT / "pixel_refine_desktop"


def _is_intentional_duplicate_decorator(node: ast.FunctionDef) -> bool:
    decorators = {ast.unparse(decorator) for decorator in node.decorator_list}
    if decorators & {"overload", "Property", "property"}:
        return True
    return any(
        decorator.endswith((".setter", ".getter"))
        for decorator in decorators
    )


def test_non_3d_code_has_no_silent_duplicate_definitions():
    """Ensure removed definitions cannot silently override future changes."""
    duplicate_classes = []
    duplicate_methods = []

    source_files = sorted(
        path
        for path in DESKTOP_ROOT.rglob("*.py")
        if "3d_reconstruction" not in path.parts
        and "__pycache__" not in path.parts
    )

    for path in source_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        classes = {}
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.setdefault(node.name, []).append(node.lineno)
        duplicate_classes.extend(
            (path, name, lines)
            for name, lines in classes.items()
            if len(lines) > 1
        )

        for class_node in ast.walk(tree):
            if not isinstance(class_node, ast.ClassDef):
                continue

            methods = {}
            for method in class_node.body:
                if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if _is_intentional_duplicate_decorator(method):
                    continue
                methods.setdefault(method.name, []).append(method.lineno)

            duplicate_methods.extend(
                (path, class_node.name, name, lines)
                for name, lines in methods.items()
                if len(lines) > 1
            )

    assert not duplicate_classes, duplicate_classes
    assert not duplicate_methods, duplicate_methods


def test_database_manager_keeps_panorama_image_order(tmp_path):
    """The surviving get_images_for_project implementation keeps its contract."""
    module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.core.logic.database_manager"
    )
    database = module.DatabaseManager(str(tmp_path / "regression.db"))

    project_id = database.create_new_panorama_project("Regression Project")
    assert project_id is not None

    image_paths = ["frame-02.png", "frame-01.png", "frame-03.png"]
    assert database.add_images_to_project(project_id, image_paths)
    assert database.get_images_for_project(project_id) == image_paths


def test_lucas_kanade_alias_resolves_configured_backend(monkeypatch):
    """Removing the duplicate delegate method preserves CPU/GPU routing."""
    module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser"
    )

    class ConfigurableAlgorithm:
        def __init__(self, backend):
            self.backend = backend

        def load_config(self, batch_id=None):
            return {"backend": self.backend, "batch_id": batch_id}

    gpu_delegate = object()
    registry = {
        "Lucas Kanade Optical Flow": ConfigurableAlgorithm("cpu"),
        "Lucas Kanade GPU Optical Flow": gpu_delegate,
    }
    monkeypatch.setattr(module, "get_alignment_registry", lambda: registry)

    alias = module.LucasKanadeAliasAlgorithm()
    assert (
        alias._resolve_delegate(batch_id=7)
        is registry["Lucas Kanade Optical Flow"]
    )

    registry["Lucas Kanade Optical Flow"] = ConfigurableAlgorithm("gpu")
    assert alias._resolve_delegate(batch_id=8) is gpu_delegate


def test_public_ui_exports_are_importable_without_eager_cycle():
    """Package exports remain available after switching to lazy imports."""
    components = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.components"
    )
    views = importlib.import_module("pixel_refine_desktop.enhance_stack.views")
    ui = importlib.import_module("pixel_refine_desktop.ui")

    assert components.BatchPageV2Layout.__name__ == "BatchPageV2Layout"
    assert views.EnhanceStackView.__name__ == "EnhanceStackView"
    assert ui.SettingsView.__name__ == "SettingsView"


def test_application_manager_initializes_database_once(tmp_path, monkeypatch):
    """Database schema setup is owned by DatabaseManager construction."""
    module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.core.logic.database_manager"
    )
    app_module = importlib.import_module("pixel_refine_desktop.app_core.app_manager")
    calls = []
    original_create_database = module.DatabaseManager.create_database

    def counted_create_database(self):
        calls.append(self.db_path)
        return original_create_database(self)

    monkeypatch.setattr(
        module.DatabaseManager, "create_database", counted_create_database
    )

    manager = app_module.ApplicationManager(main_window=None)
    manager.initialize_database(str(tmp_path / "single-init.db"))

    assert len(calls) == 1
