import os
import sys
import tempfile
from types import SimpleNamespace
import numpy as np
from PIL import Image

import pytest
from PySide6.QtWidgets import QApplication, QAbstractItemView
from PySide6.QtCore import Qt, QThreadPool, QPoint
from PySide6.QtGui import QColor, QPixmap

from pixel_refine_desktop.enhance_stack.views.single_page_view import SinglePageView
from pixel_refine_desktop.enhance_stack.views.enhance_stack_view import EnhanceStackView
from pixel_refine_desktop.enhance_stack.core.logic.database_manager import DatabaseManager
from pixel_refine_desktop.enhance_stack.core.logic.project_archive import save_project, load_project
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.switchable_parameter_panel import SwitchableParameterPanel
from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import ProcessingThread


@pytest.fixture(scope="session")
def qapp():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_parameter_panel_style_caching(qapp):
    panel = SwitchableParameterPanel()
    panel._update_styles("transparent")
    first_cache = panel._last_style_key
    assert first_cache is not None

    # Re-invoking with identical arguments must hit cache
    panel._update_styles("transparent")
    assert panel._last_style_key == first_cache


def test_batch_mode_grid_cache_switch(qapp):
    with tempfile.TemporaryDirectory(prefix="test_batch_smooth_") as temp_dir:
        db_path = os.path.join(temp_dir, "test.sqlite")
        db_mgr = DatabaseManager(db_path)
        db_mgr.create_database()

        # Create 2 batches with 10 images each
        for b_idx in (1, 2):
            b_id = db_mgr.create_new_batch(f"Batch {b_idx}")
            paths = [os.path.join(temp_dir, f"b{b_idx}_{i}.jpg") for i in range(10)]
            for p in paths:
                if not os.path.exists(p):
                    Image.fromarray((np.random.rand(40, 40, 3) * 255).astype(np.uint8)).save(p)
            db_mgr.batch_process_save_image_path(b_id, paths)

        view = SinglePageView(db_path=db_path)
        view.resize(1000, 700)
        view.show()
        qapp.processEvents()

        right_panel = view.batch_panel
        display_panel = view.workspace_panel.display_panel

        # Select Batch 1
        right_panel.select_batch_sync(1)
        for _ in range(10):
            qapp.processEvents()

        assert display_panel.current_batch_id == 1
        cards_b1 = list(display_panel.all_cards.values())
        assert len(cards_b1) == 10

        # Switch to Batch 2
        right_panel.select_batch_sync(2)
        for _ in range(10):
            qapp.processEvents()

        assert display_panel.current_batch_id == 2
        # Verify Batch 1 was saved into _grid_cache
        assert 1 in display_panel._grid_cache
        cached_b1_imgs, cached_b1_cards = display_panel._grid_cache[1]
        assert len(cached_b1_cards) == 10

        # Switch back to Batch 1 - must restore from cache
        right_panel.select_batch_sync(1)
        for _ in range(5):
            qapp.processEvents()

        assert display_panel.current_batch_id == 1
        assert len(display_panel.all_cards) == 10
        # Check that card instances were reused
        for card in display_panel.all_cards.values():
            assert card in cached_b1_cards


def test_grid_cache_invalidation_on_project_load(qapp):
    with tempfile.TemporaryDirectory(prefix="test_proj_inv_") as temp_dir:
        db_path = os.path.join(temp_dir, "test.sqlite")
        db_mgr = DatabaseManager(db_path)
        db_mgr.create_database()

        b_id = db_mgr.create_new_batch("Batch 1")
        paths = [os.path.join(temp_dir, f"img_{i}.jpg") for i in range(5)]
        for p in paths:
            if not os.path.exists(p):
                Image.fromarray((np.random.rand(40, 40, 3) * 255).astype(np.uint8)).save(p)
        db_mgr.batch_process_save_image_path(b_id, paths)

        view = SinglePageView(db_path=db_path)
        view.show()
        qapp.processEvents()

        display_panel = view.workspace_panel.display_panel
        view.batch_panel.select_batch_sync(1)
        for _ in range(5):
            qapp.processEvents()

        dummy_imgs = [type("Img", (), {"id": i, "path": p})() for i, p in enumerate(paths)]
        display_panel._store_grid_cache(1, dummy_imgs)
        assert len(display_panel._grid_cache) > 0

        # Invalidate all
        display_panel.invalidate_grid_cache(None)
        assert len(display_panel._grid_cache) == 0

        # Let background thumbnail decodes finish before the temporary directory
        # is removed: the cleanup otherwise races with a worker that still holds
        # a source file open (Windows: PermissionError WinError 32).
        QThreadPool.globalInstance().waitForDone(10000)


def test_external_import_sync_to_batch_mode(qapp):
    """Verify that if images are added to a batch externally (e.g. Bulk Mode drag & drop),
    Batch Mode immediately reflects the images and does not get stuck on 'This Batch is Empty'.
    """
    with tempfile.TemporaryDirectory(prefix="test_ext_sync_") as temp_dir:
        db_path = os.path.join(temp_dir, "test.sqlite")
        db_mgr = DatabaseManager(db_path)
        db_mgr.create_database()

        # 1. Create Batch 1 (empty)
        b1_id = db_mgr.create_new_batch("Batch 1")

        view = SinglePageView(db_path=db_path)
        view.resize(1000, 700)
        view.show()
        qapp.processEvents()

        # View batch 1 when empty
        view.batch_panel.select_batch_sync(b1_id)
        for _ in range(5):
            qapp.processEvents()
        display_panel = view.workspace_panel.display_panel
        assert display_panel.total_image_count == 0

        # 2. External import (Bulk mode drag-and-drop directly into SQLite)
        paths = [os.path.join(temp_dir, f"ext_img_{i}.jpg") for i in range(12)]
        for p in paths:
            if not os.path.exists(p):
                Image.fromarray((np.random.rand(40, 40, 3) * 255).astype(np.uint8)).save(p)
        db_mgr.batch_process_save_image_path(b1_id, paths)

        # 3. User switches back to Batch 1
        view.batch_panel.select_batch_sync(b1_id)
        for _ in range(10):
            qapp.processEvents()

        # Must have 12 cards rendered and count updated, NOT empty!
        assert display_panel.total_image_count == 12
        assert len(display_panel.all_cards) == 12
        assert display_panel.grid_content_stack.currentWidget() == display_panel.grid_container

        # Ensure NO rogue ImageCard top-level windows were launched!
        from UILibrary import ImageCard
        card_windows = [w for w in qapp.topLevelWidgets() if isinstance(w, ImageCard)]
        assert len(card_windows) == 0

        # Let background thumbnail decodes finish before the temporary directory
        # is removed: the cleanup otherwise races with a worker that still holds
        # a source file open (Windows: PermissionError WinError 32).
        QThreadPool.globalInstance().waitForDone(10000)


def test_preview_actions_follow_active_display_page(qapp, monkeypatch):
    with tempfile.TemporaryDirectory(prefix="test_preview_navigation_") as temp_dir:
        db_path = os.path.join(temp_dir, "preview.sqlite")
        database = DatabaseManager(db_path)
        database.create_database()
        batch_id = database.create_new_batch("Preview")
        image_path = os.path.join(temp_dir, "input.jpg")
        Image.fromarray(np.zeros((24, 24, 3), dtype=np.uint8)).save(image_path)
        database.batch_process_save_image_path(batch_id, [image_path])

        view = SinglePageView(db_path=db_path)
        view.show()
        view.batch_panel.select_batch_sync(batch_id)
        qapp.processEvents()
        display_panel = view.workspace_panel.display_panel
        display_panel.logic.current_images = [SimpleNamespace(path=image_path)]
        display_panel._scan_current_results = lambda: [{"path": "result.tif"}]

        display_panel._comparison_request_id = 7
        display_panel._show_comparison_loading(7, 45)
        assert display_panel.comparison_loading_label.text() == "Loading [45%]"
        assert not display_panel.comparison_loading_label.isHidden()
        display_panel._hide_comparison_loading(7)
        assert not display_panel.comparison_loading_label.isVisible()

        compact_controls_width = display_panel.playback_container.sizeHint().width()
        display_panel._on_burst_preload_progress(1, 4)
        qapp.processEvents()
        assert display_panel.play_btn.text() == "25%"
        assert display_panel.play_btn.width() == 56
        assert display_panel.playback_container.sizeHint().width() > compact_controls_width
        display_panel._on_burst_preload_progress(4, 4)
        qapp.processEvents()
        assert display_panel.play_btn.text() == "▶"
        assert display_panel.play_btn.width() == 36
        assert display_panel.playback_container.sizeHint().width() == compact_controls_width

        display_panel.check_result_availability([{"path": "result.tif"}])
        assert not display_panel.preview_process_btn.isHidden()

        display_panel.show_preview()
        display_panel.check_result_availability([{"path": "result.tif"}])
        assert display_panel.preview_process_btn.isHidden()
        assert not display_panel.back_btn.isHidden()

        display_panel.show_grid()
        qapp.processEvents()
        assert not display_panel.preview_process_btn.isHidden()
        assert display_panel.back_btn.isHidden()

        batch_list = view.batch_panel.list_group._list_widget
        batch_item = batch_list.item(0)
        assert batch_list.itemWidget(batch_item) is None
        assert batch_list.editTriggers() == QAbstractItemView.EditTrigger.NoEditTriggers
        assert not (batch_item.flags() & Qt.ItemFlag.ItemIsEditable)
        right_panel = view.batch_panel
        right_panel._batch_status_timer.stop()
        right_panel._batch_queue_states[str(batch_id)] = "running"
        cancel_rect = right_panel._batch_cancel_rect(batch_item)
        row_preview = QPixmap(batch_list.viewport().size())
        batch_list.viewport().render(row_preview)
        assert right_panel._batch_item_at(cancel_rect.center()) is batch_item
        assert right_panel._batch_item_at(
            cancel_rect.center() - QPoint(26, 0)
        ) is None

        row_rect = batch_list.visualItemRect(batch_item)
        delegate = batch_list.itemDelegate()
        assert cancel_rect.width() == 20
        assert cancel_rect.height() == 20
        action_left = row_rect.right() - delegate.ACTION_WIDTH + 1
        cancel_visual_rect = delegate.cancel_button_rect(row_rect)
        status_rect = delegate.status_marker_rect(row_rect)
        assert cancel_visual_rect.top() > row_rect.top()
        assert cancel_visual_rect.top() == row_rect.center().y() - delegate.CANCEL_BUTTON_SIZE // 2 - 2
        assert status_rect.width() == delegate.STATUS_MARKER_WIDTH
        assert status_rect.height() == delegate.STATUS_MARKER_HEIGHT
        assert status_rect.width() > status_rect.height()
        assert status_rect.left() - action_left == 4
        assert status_rect.left() > action_left
        assert status_rect.right() < row_rect.right()
        assert row_rect.right() - status_rect.right() == 4
        assert status_rect.bottom() < row_rect.bottom()
        assert row_preview.toImage().pixelColor(action_left + 2, row_rect.top() + 2) == QColor(
            "#FFFFFF"
        )
        for state, color in (
            ("running", "#3B82F6"),
            ("queued", "#EAB308"),
            ("completed", "#22C55E"),
        ):
            right_panel._batch_queue_states[str(batch_id)] = state
            qapp.processEvents()
            row_preview.fill(Qt.GlobalColor.transparent)
            batch_list.viewport().render(row_preview)
            assert row_preview.toImage().pixelColor(status_rect.center()) == QColor(color)

        cancelled_batch_ids = []
        right_panel._active_process_dialog = SimpleNamespace(
            processing_thread=SimpleNamespace(isRunning=lambda: True),
            cancel_batch_by_id=cancelled_batch_ids.append,
        )
        right_panel._cancel_batch_job(batch_id)
        assert cancelled_batch_ids == [batch_id]
        right_panel._active_process_dialog = None
        right_panel._batch_queue_states.clear()

        from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
            BackendWorkerManager,
        )

        worker_state = SimpleNamespace(is_task_active=lambda: True)
        monkeypatch.setattr(BackendWorkerManager, "instance", lambda: worker_state)
        display_panel._sync_settings_enabled()
        settings_button = display_panel.sidebar.side_buttons[1]
        assert not settings_button.isEnabled()
        display_panel._handle_sidebar_navigation(1)
        assert not display_panel.settings_overlay.isVisible()

        worker_state.is_task_active = lambda: False
        display_panel._sync_settings_enabled()
        assert settings_button.isEnabled()


def test_queued_batch_cancel_does_not_dispatch_worker(qapp):
    batch = SimpleNamespace(id=42, name="Batch 42")
    thread = ProcessingThread([(batch, 0)], batch_page_layout=object(), target_folder=".")
    finished = []
    completed = []
    thread.batch_finished.connect(lambda *args: finished.append(args))
    thread.processing_complete.connect(lambda result: completed.append(result))

    thread.cancel_batch(batch.id)
    thread.run()

    assert finished == [(0, False, "Cancelled before processing")]
    assert completed == [[]]


def test_bulk_return_reloads_imported_images_in_batch_page(qapp):
    with tempfile.TemporaryDirectory(prefix="test_bulk_return_refresh_") as temp_dir:
        db_path = os.path.join(temp_dir, "session.sqlite")
        database = DatabaseManager(db_path)
        database.create_database()
        batch_id = database.create_new_batch("Imported in Bulk")

        single_page = SinglePageView(db_path=db_path)
        single_page.resize(1000, 700)
        single_page.show()
        qapp.processEvents()
        single_page.batch_panel.select_batch_sync(batch_id)
        qapp.processEvents()
        display_panel = single_page.workspace_panel.display_panel
        assert display_panel.total_image_count == 0

        image_paths = [os.path.join(temp_dir, f"bulk_{i}.jpg") for i in range(3)]
        for image_path in image_paths:
            Image.fromarray(np.full((40, 40, 3), 90, dtype=np.uint8)).save(image_path)
        # Bulk V1 import writes to the shared database before returning to V2.
        database.batch_process_save_image_path(batch_id, image_paths)

        legacy_batch_layout = SimpleNamespace(
            stop_thumbnail=lambda: None,
            limit=10,
        )
        stacked_widget = SimpleNamespace(_current=SimpleNamespace())
        stacked_widget.currentWidget = lambda: stacked_widget._current
        stacked_widget.setCurrentWidget = lambda widget: setattr(
            stacked_widget, "_current", widget
        )
        orchestrator = SimpleNamespace(
            stacked_widget=stacked_widget,
            animator=SimpleNamespace(stop_all=lambda: None),
            single_page_view=single_page,
            batch_page_view=SimpleNamespace(batch_layout=legacy_batch_layout),
            _active_display_panel=lambda: display_panel,
        )
        orchestrator._refresh_batch_after_legacy_switch = lambda: (
            EnhanceStackView._refresh_batch_after_legacy_switch(orchestrator)
        )

        EnhanceStackView._on_legacy_bulk_toggled(orchestrator, False)
        assert stacked_widget.currentWidget() is single_page
        assert display_panel.total_image_count == 0

        for _ in range(20):
            qapp.processEvents()

        QThreadPool.globalInstance().waitForDone(10000)
        for _ in range(5):
            qapp.processEvents()

        assert display_panel.current_batch_id == batch_id
        assert display_panel.total_image_count == len(image_paths)
        assert len(display_panel.all_cards) == len(image_paths)
        assert all(card.has_thumbnail() for card in display_panel.all_cards.values())
