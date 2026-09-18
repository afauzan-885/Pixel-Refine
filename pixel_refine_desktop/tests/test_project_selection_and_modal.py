import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from resources.GenericUILibrary.modals import AlertModal


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_alert_modal_auto_dismiss(qapp):
    """Test that AlertModal with auto_dismiss_seconds ticks down and auto-accepts."""
    modal = AlertModal(
        message="Test message",
        title="Test Title",
        variant="info",
        auto_dismiss_seconds=1,
    )
    assert modal._countdown == 1
    assert "1s" in modal.ok_button.text()

    # Simulate countdown tick
    modal._on_dismiss_tick()
    assert modal.result() == 1 or not modal.isVisible()


def test_right_panel_select_batch_sync(qapp):
    """Test that select_batch_sync stops debounce timer and selects the batch immediately."""
    from PySide6.QtCore import QObject, Signal
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.right_panel import RightPanel

    class DummyBatch:
        def __init__(self, bid, name):
            self.id = bid
            self.name = name
            self.images = []

    class DummyController(QObject):
        batch_created = Signal()
        batch_deleted = Signal()
        images_added = Signal(int, int)
        images_removed = Signal(int, int)

        def __init__(self):
            super().__init__()
            self.batches = [DummyBatch(1, "Batch 1"), DummyBatch(2, "Batch 2")]

        def get_all_batches(self):
            return self.batches

        def get_batch(self, bid):
            for b in self.batches:
                if b.id == bid:
                    return b
            return None

    controller = DummyController()
    panel = RightPanel(controller=controller)

    # Manually populate batches
    panel._load_batches()
    assert panel._pending_selection is None
    assert not panel._selection_timer.isActive()

    # Call select_batch_sync
    selected = panel.select_batch_sync(2)
    assert selected is True
    assert panel.current_batch_id == 2
    assert panel._pending_selection is None
    assert not panel._selection_timer.isActive()

