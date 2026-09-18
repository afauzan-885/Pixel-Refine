import os
import sys
import tempfile
import numpy as np
from PIL import Image

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from pixel_refine_desktop.enhance_stack.views.single_page_view import SinglePageView
from pixel_refine_desktop.enhance_stack.core.logic.database_manager import DatabaseManager
from pixel_refine_desktop.enhance_stack.core.logic.project_archive import save_project, load_project
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.switchable_parameter_panel import SwitchableParameterPanel


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
        from resources.GenericUILibrary import ImageCard
        card_windows = [w for w in qapp.topLevelWidgets() if isinstance(w, ImageCard)]
        assert len(card_windows) == 0
