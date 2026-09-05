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


def test_database_manager_keeps_batch_image_order(tmp_path):
    """The surviving batch implementation keeps its contract."""
    module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.core.logic.database_manager"
    )
    database = module.DatabaseManager(str(tmp_path / "regression.db"))

    batch_id = database.create_new_batch("Regression Batch")
    assert batch_id is not None

    image_paths = ["frame-02.png", "frame-01.png", "frame-03.png"]
    assert database.batch_process_save_image_path(batch_id, image_paths)
    assert database.get_images_by_batch(batch_id) == image_paths


def test_lucas_kanade_registry_contains_cpu_and_gpu():
    """Registry provides both CPU and GPU variants of Lucas Kanade."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
        get_alignment_registry,
    )

    registry = get_alignment_registry()
    assert "Lucas Kanade Optical Flow" in registry
    assert "Lucas Kanade GPU Optical Flow" in registry


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


def test_burst_preload_worker_and_playback_cache_contract():
    """Verify BurstPreloadWorker exists, has abort, and DisplayPanel defines playback_cache."""
    dp_module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.components.batch_page_v2.display_panel"
    )
    assert hasattr(dp_module, "BurstPreloadWorker")
    worker_cls = getattr(dp_module, "BurstPreloadWorker")
    assert hasattr(worker_cls, "abort")
    assert hasattr(worker_cls, "frame_cached")
    assert hasattr(worker_cls, "preload_progress")
    assert hasattr(worker_cls, "preload_finished")

    worker = worker_cls(["dummy1.jpg", "dummy2.jpg"], max_workers=4)
    assert worker.max_workers == 4
    assert hasattr(worker, "_decode_frame")

    # Verify helper display_image_in_zoomable accepts callback
    idh_module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.core.logic.image_display_helper"
    )
    import inspect
    sig = inspect.signature(idh_module.display_image_in_zoomable)
    assert "callback" in sig.parameters
    assert "half_res" in sig.parameters


def test_thumbnail_processor_async_flush_contract():
    """Verify ThumbnailBatchProcessor has non-blocking stop_all with async_flush."""
    tp_module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor"
    )
    assert hasattr(tp_module, "_AsyncThumbnailFlushRunnable")
    import inspect
    sig = inspect.signature(tp_module.ThumbnailBatchProcessor.stop_all)
    assert "async_flush" in sig.parameters


def test_playback_zoom_preservation_and_inplace_swap():
    """Verify _update_preview_pixmap reuses QGraphicsPixmapItem and does not wipe out zoom."""
    from PySide6.QtWidgets import QApplication, QGraphicsScene
    from PySide6.QtGui import QPixmap, QImage, QColor
    import sys

    app = QApplication.instance() or QApplication(sys.argv)

    dp_module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.components.batch_page_v2.display_panel"
    )
    DisplayPanel = getattr(dp_module, "DisplayPanel")
    assert hasattr(DisplayPanel, "_update_preview_pixmap")

    scene = QGraphicsScene()
    from pixel_refine_desktop.enhance_stack.core.logic.Zoomable_Handler import Zoomable
    zoomable = Zoomable(scene)

    img1 = QImage(100, 100, QImage.Format.Format_RGB888)
    img1.fill(QColor(255, 0, 0))
    pm1 = QPixmap.fromImage(img1)

    img2 = QImage(100, 100, QImage.Format.Format_RGB888)
    img2.fill(QColor(0, 255, 0))
    pm2 = QPixmap.fromImage(img2)

    class DummyPanel:
        def __init__(self):
            self.preview_scene = scene
            self.zoomable_preview = zoomable
            self._preview_pixmap_item = None
        _update_preview_pixmap = DisplayPanel._update_preview_pixmap

    panel = DummyPanel()
    panel._update_preview_pixmap(pm1)
    assert panel._preview_pixmap_item is not None
    assert panel._preview_pixmap_item in scene.items()
    first_item = panel._preview_pixmap_item

    zoomable.scale(2.5, 2.5)
    zoomable._zoom_level = 3
    saved_transform = zoomable.transform()

    panel._update_preview_pixmap(pm2)

    assert panel._preview_pixmap_item is first_item
    assert zoomable.transform() == saved_transform
    assert zoomable._zoom_level == 3


def test_fifo_batch_playback_cache():
    """Verify FIFO 15-batch RAM caching preserves frames across batch switches and evicts oldest when exceeding 15."""
    from collections import OrderedDict
    from PySide6.QtGui import QPixmap, QImage, QColor

    dp_module = importlib.import_module(
        "pixel_refine_desktop.enhance_stack.components.batch_page_v2.display_panel"
    )
    DisplayPanel = getattr(dp_module, "DisplayPanel")

    img = QImage(64, 64, QImage.Format.Format_RGB888)
    img.fill(QColor(100, 150, 200))
    pm = QPixmap.fromImage(img)

    class DummyDisplayPanel:
        def __init__(self):
            self.current_batch_id = 1
            self._batch_playback_cache = OrderedDict()
            self._batch_playback_cache_limit = 15
        playback_cache = DisplayPanel.playback_cache
        _store_playback_frame = DisplayPanel._store_playback_frame

    panel = DummyDisplayPanel()

    for b in range(1, 16):
        panel.current_batch_id = b
        panel._store_playback_frame(str(b), f"path_{b}.jpg", pm)

    assert len(panel._batch_playback_cache) == 15
    assert "1" in panel._batch_playback_cache
    assert "15" in panel._batch_playback_cache

    assert f"path_1.jpg" in panel._batch_playback_cache["1"]

    panel.current_batch_id = 16
    panel._store_playback_frame("16", "path_16.jpg", pm)

    assert len(panel._batch_playback_cache) == 15
    assert "1" not in panel._batch_playback_cache
    assert "2" in panel._batch_playback_cache
    assert "16" in panel._batch_playback_cache


def test_aot_silent_warmup_contract():
    """Verify that silent AOT warmup worker and exports conform to contract."""
    import os
    from pixel_refine_desktop.app_core.aot_warmup import (
        start_silent_aot_warmup,
        stop_silent_aot_warmup,
        AOTSilentWarmupWorker,
        TIER_1_MODULES,
        TIER_2_MODULES,
        _resolve_tcm_directory,
    )
    from pixel_refine_desktop.app_core import (
        start_silent_aot_warmup as exported_start,
        stop_silent_aot_warmup as exported_stop,
    )

    assert callable(start_silent_aot_warmup)
    assert callable(stop_silent_aot_warmup)
    assert exported_start is start_silent_aot_warmup
    assert exported_stop is stop_silent_aot_warmup

    # Ensure Tier 1 contains core preview/demosaic modules
    assert "bilinear_demosaice" in TIER_1_MODULES
    assert "hamilton" in TIER_1_MODULES
    assert "common" in TIER_1_MODULES

    # Ensure Tier 2 contains alignment and enhancement modules
    assert "auto_enhance" in TIER_2_MODULES
    assert "spatial_fusion" in TIER_2_MODULES

    # Ensure TCM directory resolves to an actual directory
    tcm_dir = _resolve_tcm_directory()
    assert os.path.isdir(tcm_dir)

    # Worker instantiation and stop request test
    worker = AOTSilentWarmupWorker()
    assert worker.isRunning() is False
    worker.request_stop()
    assert worker._stop_requested is True


def test_non_contiguous_array_conversion_contract():
    """Verify that non-contiguous arrays convert cleanly to QPixmap without memoryview error."""
    import numpy as np
    from pixel_refine_desktop.enhance_stack.core.logic.image_display_helper import (
        ImageLoaderThread,
    )

    loader = ImageLoaderThread("dummy.jpg")
    # Slicing with step creates a non-contiguous buffer
    non_contiguous = np.zeros((100, 100, 3), dtype=np.uint8)[::2, ::2, :]
    assert not non_contiguous.flags.c_contiguous

    pixmap = loader._array_to_pixmap(non_contiguous)
    assert pixmap is not None
    assert not pixmap.isNull()
    assert pixmap.width() == 50
    assert pixmap.height() == 50
