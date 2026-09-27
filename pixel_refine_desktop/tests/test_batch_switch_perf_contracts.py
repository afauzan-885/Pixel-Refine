"""Contract tests for the batch-workflow performance and RAM invariants.

These guard the optimizations that are easy to regress silently:

* ``BatchPageController.get_batch`` must never serve a stale cached model
  (batches can be written out-of-band, e.g. by Bulk Mode).
* ``GridManager`` must reuse a single populate timer instead of creating one per
  switch.
* The playback frame cache must stay inside its byte budget while keeping the
  active batch intact.
* The thumbnail L1 RAM cache must be bounded.
* The thumbnail disk cache must shed leftovers from the old naming scheme.
"""

import os

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QWidget


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _tiny_solid_pixmap(width=64, height=64):
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(100, 120, 140))
    return QPixmap.fromImage(image)


def _pixmap_bytes(pixmap):
    depth = int(pixmap.depth() or 32)
    return int(pixmap.width()) * int(pixmap.height()) * max(1, depth // 8)


def test_get_batch_reflects_out_of_band_writes(qapp, tmp_path):
    """A batch modified by another connection must be visible on the next read."""
    import numpy as np
    from PIL import Image

    from pixel_refine_desktop.enhance_stack.controllers.batch_page_controller import (
        BatchPageController,
    )
    from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
        DatabaseManager,
    )

    db_path = str(tmp_path / "batch_switch.sqlite")
    db_mgr = DatabaseManager(db_path)
    db_mgr.create_database()
    batch_id = db_mgr.create_new_batch("Batch 1")

    controller = BatchPageController(db_path)
    assert controller.get_batch(batch_id) is not None

    # Out-of-band writer: Bulk Mode writes the same database directly.
    paths = [str(tmp_path / f"img_{i}.jpg") for i in range(3)]
    for path in paths:
        Image.fromarray(
            (np.random.rand(16, 16, 3) * 255).astype(np.uint8)
        ).save(path)
    db_mgr.batch_process_save_image_path(batch_id, paths)

    refreshed = controller.get_batch(batch_id)
    assert refreshed is not None
    assert len(refreshed.images) == 3

    controller.deleteLater()
    qapp.processEvents()


def test_grid_populate_timer_is_reused(qapp):
    """Switching batches must not accumulate one populate QTimer per switch."""
    from pixel_refine_desktop.enhance_stack.core.logic.grid_manager import GridManager

    class FakeContainer:
        def set_batch_update(self, active):
            self.batch_update = active

    class FakeLogic:
        thumbnail_policy = None

    class FakePanel(QWidget):
        def __init__(self):
            super().__init__()
            self.logic = FakeLogic()
            self.grid_container = FakeContainer()
            self.all_cards = {}
            self.current_batch_id = None

    panel = FakePanel()
    manager = GridManager(panel)

    first_timer = manager.populate_timer
    timer_count = len(panel.findChildren(QTimer))

    for _ in range(5):
        manager.populate_grid_incremental([])

    assert manager.populate_timer is first_timer
    assert len(panel.findChildren(QTimer)) == timer_count

    panel.deleteLater()
    qapp.processEvents()


def test_playback_cache_respects_byte_budget(qapp):
    """Non-active batches are dropped once the frame budget is exceeded."""
    from collections import OrderedDict

    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.display_panel import (
        DisplayPanel,
    )

    pixmap = _tiny_solid_pixmap()
    frame_bytes = _pixmap_bytes(pixmap)

    class DummyDisplayPanel:
        def __init__(self):
            self.current_batch_id = 1
            self._batch_playback_cache = OrderedDict()
            self._batch_playback_cache_limit = 10
            self._playback_cache_max_bytes = frame_bytes * 3

        _store_playback_frame = DisplayPanel._store_playback_frame

    panel = DummyDisplayPanel()

    for batch in range(1, 5):
        panel.current_batch_id = batch
        for frame in range(2):
            panel._store_playback_frame(str(batch), f"p{frame}.jpg", pixmap)

    # The batch being viewed keeps every frame it stored.
    assert len(panel._batch_playback_cache["4"]) == 2
    # Older batches were dropped so the total stays inside the budget.
    total_bytes = sum(
        len(frames) * frame_bytes for frames in panel._batch_playback_cache.values()
    )
    assert total_bytes <= panel._playback_cache_max_bytes
    assert len(panel._batch_playback_cache) < 4


def test_thumbnail_ram_cache_is_bounded(qapp):
    """The L1 thumbnail cache must evict instead of growing without limit."""
    from PySide6.QtCore import QThreadPool

    from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
        ThumbnailBatchProcessor,
    )

    # ThumbnailBatchProcessor resizes the *global* thread pool, so restore it:
    # otherwise later test modules decode with more workers than they expect and
    # their temporary-directory cleanup races with in-flight decodes.
    pool = QThreadPool.globalInstance()
    previous_max = pool.maxThreadCount()
    try:
        processor = ThumbnailBatchProcessor()
        processor.RAM_CACHE_MAX_ITEMS = 5

        image = QImage(16, 16, QImage.Format.Format_RGB32)
        image.fill(QColor(10, 20, 30))

        for index in range(20):
            processor._ram_cache_put(f"p{index}.jpg", image)

        assert len(processor.ram_cache) <= 5
        assert processor._ram_cache_bytes == sum(
            int(value.sizeInBytes()) for value in processor.ram_cache.values()
        )

        # Most recent entries survive; the oldest were evicted.
        assert processor._ram_cache_get("p19.jpg") is not None
        assert processor._ram_cache_get("p0.jpg") is None
    finally:
        pool.setMaxThreadCount(previous_max)


def test_worker_ready_requires_handshake():
    """A live but still-loading worker must not be reported as ready.

    Reporting it as ready dispatched a task into a worker that could not answer
    yet, and the parent then waited for the result with no progress and no
    timeout - the "app looks hung and never processes anything" report.
    """
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
        BackendWorkerManager,
    )

    manager = BackendWorkerManager()

    class FakeProc:
        pid = 4321

        @staticmethod
        def poll():
            return None  # process is alive, but no ready handshake yet

    manager._proc = FakeProc()
    manager._ready_event.clear()

    assert manager.ensure_worker_ready(timeout=0.2) is False

    # The handshake is the only thing that makes it usable.
    manager._ready_event.set()
    assert manager.ensure_worker_ready(timeout=0.2) is True

    # Leave no fake process behind for the manager's atexit shutdown.
    manager._proc = None
    manager._ready_event.clear()


def test_dispatch_retries_once_after_worker_vanished(qapp):
    """A worker that disappears before the write must not fail the user's batch.

    This is the "task arrives while the worker is asleep" race: the ready
    handshake can succeed and the process vanish before the command is written.
    """
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
        BackendWorkerManager,
    )

    manager = BackendWorkerManager()
    manager._active_backend_config = {"arch": "cpu", "device_id": "0", "vendor": ""}
    manager._ready_event.set()

    class FakeProc:
        pid = 4242

        @staticmethod
        def poll():
            return None

    manager._proc = FakeProc()

    calls = {"write": 0, "respawn": 0}

    def fake_write(_payload):
        calls["write"] += 1
        if calls["write"] == 1:
            return "Worker died before task dispatch."
        manager._current_task_result = {"success": True, "type": "finished"}
        manager._current_task_event.set()
        return None

    def fake_spawn(*_args, **_kwargs):
        calls["respawn"] += 1
        manager._proc = FakeProc()
        manager._ready_event.set()
        return True

    manager._write_task = fake_write
    manager._spawn_worker_locked = fake_spawn

    result = manager.dispatch_task({"batch_id": 1, "db_path": "x", "settings": {}})

    assert result.get("success") is True
    assert calls["write"] == 2, "task must be retried exactly once"
    assert calls["respawn"] == 1, "a fresh worker must be started for the retry"

    manager._proc = None
    manager._ready_event.clear()


def test_dispatch_watchdog_restarts_wedged_worker(qapp):
    """A worker that never answers must be restarted, not waited on forever."""
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
        BackendWorkerManager,
    )

    manager = BackendWorkerManager()
    manager._active_backend_config = {"arch": "cpu", "device_id": "0", "vendor": ""}
    manager._ready_event.set()
    manager.TASK_WATCHDOG_TIMEOUT_S = 0.3  # instance override for the test

    class FakeProc:
        pid = 77

        @staticmethod
        def poll():
            return None

    manager._proc = FakeProc()
    manager._write_task = lambda _payload: None  # accepted, never answered
    manager._worker_cpu_seconds = lambda: 0.0  # silent and burning no CPU
    manager._spawn_worker_locked = lambda *_a, **_k: True

    result = manager.dispatch_task({"batch_id": 1, "db_path": "x", "settings": {}})

    assert result.get("success") is False
    assert "merespons" in (result.get("error") or "")

    manager._proc = None
    manager._ready_event.clear()


def test_thumbnail_prune_removes_legacy_names(tmp_path):
    """Only SHA-1 named thumbnails are current; leftovers must be pruned."""
    from pixel_refine_desktop.enhance_stack.models.data_access.thumbnail_repository import (
        ThumbnailRepository,
    )

    cache_dir = tmp_path / "thumbnails"
    repo = ThumbnailRepository(cache_dir=str(cache_dir))

    hashed = cache_dir / (("a" * 40) + ".jpg")
    hashed.write_bytes(b"thumbnail")
    legacy = cache_dir / "img_b1_0.jpg.jpg"
    legacy.write_bytes(b"thumbnail")
    other = cache_dir / "notes.txt"
    other.write_bytes(b"notes")

    removed = repo.prune_cache()

    assert removed == 2
    assert hashed.exists()
    assert not legacy.exists()
    assert not other.exists()
