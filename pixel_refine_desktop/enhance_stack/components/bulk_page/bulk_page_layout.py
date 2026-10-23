import json
import os
import shutil
import sqlite3
import time
from types import SimpleNamespace
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QMessageBox,
    QFileDialog,
    QGraphicsOpacityEffect,
    QFrame,
    QMenu,
)
from PySide6.QtCore import (
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    QEvent,
    QTimer,
    Slot,
    QThread,
    Qt,
    QFileSystemWatcher,
)
import weakref
import tempfile
from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import (
    BatchProcessDialog,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.widgets.bulk_combined_panel import (
    CombinedPanel,
    SkeletonCombinedPanel,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.widgets.bulk_batch_list_view import (
    BulkBatchListModel, BulkBatchDelegate, BulkBatchListView,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_import_service import (
    BulkDeleteProcess,
    process_and_start_batch_import,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_drop_processor import (
    BulkDropProcessor,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_thumbnail_service import (
    stop_process_thumbnails,
    ThumbnailScheduler,
)
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_policy import (
    ThumbnailPolicy,
    thumbnail_creation_enabled,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_result_service import (
    move_result,
)

from UILibrary import ScrollContainer, live_update


def _move_file_with_verified_copy_fallback(source_path, destination_path):
    """Move a result, falling back to a verified copy if Windows blocks rename."""
    return move_result(source_path, destination_path)


class BatchPreloaderThread(QThread):
    """
    Background worker thread yang melakukan query DB, parsing JSON parameter,
    dan verifikasi path gambar secara terpisah dari main UI thread.
    """

    batch_prepared = Signal(
        object, dict, list
    )  # (batch_id, state_dict, valid_image_paths)

    def __init__(self, database_manager, batch_id, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.batch_id = batch_id

    def run(self):
        try:
            raw_paths = (
                self.database_manager.get_images_by_batch(self.batch_id)
                if self.batch_id is not None
                else []
            )
            valid_paths = [p for p in raw_paths if os.path.exists(p)]

            json_path = getattr(self, "json_path", os.path.join("database", "align", "batch_parameter.json"))
            state = {}
            if os.path.exists(json_path):
                try:
                    all_saved = load_json_state(json_path)
                    state = all_saved.get(str(self.batch_id), {})
                except Exception:
                    state = {}

            if not self.isInterruptionRequested():
                self.batch_prepared.emit(self.batch_id, state, valid_paths)
        except Exception as e:
            print(f"[ERROR] BatchPreloaderThread error for batch {self.batch_id}: {e}")
            if not self.isInterruptionRequested():
                self.batch_prepared.emit(self.batch_id, {}, [])


class BulkSnapshotThread(QThread):
    """Read all batch metadata off the GUI thread; no QWidget work is done here."""
    prepared = Signal(int, object)

    def __init__(self, database_manager, json_path, generation, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.json_path = json_path
        self.generation = generation

    def run(self):
        records = []
        try:
            states = load_json_state(self.json_path)
            for batch_id in self.database_manager.get_all_batch_ids():
                if self.isInterruptionRequested():
                    return
                paths = self.database_manager.get_images_by_batch(batch_id)
                records.append({
                    "id": batch_id,
                    "paths": [path for path in paths if os.path.exists(path)],
                    "state": dict(states.get(str(batch_id), {}) or {}),
                    "thumbnails": {},
                })
        except Exception as error:
            print(f"[BulkSnapshotThread] Snapshot failed: {error}")
        if not self.isInterruptionRequested():
            self.prepared.emit(self.generation, records)


class BulkBatchScrollContainer(ScrollContainer):
    """
    Scrollable container extending ScrollContainer from GenericUILibrary.
    Handles viewport resizing and smooth content expanding for Batch Mode.
    """

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_inner_dimensions()

    def update_inner_dimensions(self):
        inner = self.container
        if inner and inner.layout():
            inner.layout().invalidate()
            inner.layout().activate()
            vh = self.viewport().height()
            content_h = inner.layout().sizeHint().height()
            inner.setMinimumHeight(max(vh, content_h))


def setup_main_panel(layout_instance, scroll_area_style):
    """Creates the main panel scroll container utilizing GenericUILibrary ScrollContainer."""
    scroll_area = BulkBatchScrollContainer()
    scroll_area.setObjectName("MainBatchScrollArea")

    main_panel = scroll_area.container
    main_panel.setObjectName("BulkMainPanel")

    layout_instance.setContentsMargins(5, 5, 8, 16)
    layout_instance.setSpacing(25)
    layout_instance.setAlignment(Qt.AlignmentFlag.AlignTop)

    # Replace default layout with layout_instance
    old_layout = main_panel.layout()
    if old_layout:
        QWidget().setLayout(old_layout)
    main_panel.setLayout(layout_instance)

    scroll_area.setStyleSheet(scroll_area_style)
    return scroll_area


from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
    DatabaseManager,
)
from resources.animations.animation_manager import (
    StackedWidgetAnimator,
)
from resources.animations.fade import fade_out
from resources.styles import stylesheet
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.core.logic.batch_parameter_manager import load_json_state
from pixel_refine_desktop.enhance_stack.core.logic.process_manager import is_widget_alive
from config import CACHE_DIR, SUPPORTED_FORMATS

def safe_hide_widget(widget):
    """Sembunyikan widget jika masih valid, tangani error jika sudah dihapus."""
    if not is_widget_alive(widget):
        return
    try:
        widget.hide()
    except Exception:
        pass


@live_update
class BulkPageLayout(QWidget):
    data_changed = Signal()
    show_toast_requested = Signal(str, object, bool)
    parameters_changed = Signal(dict)

    def __init__(self, db_path=None):
        super().__init__()
        self.thumbnail_policy = ThumbnailPolicy(self)
        self.thumbnail_policy.changed.connect(self._on_thumbnail_policy_changed)
        self.thumbnail_threads = []
        self.thumbnail_placeholders = weakref.WeakValueDictionary()
        self.active_skeletons = {}
        self.loading_queue = []
        session_path = db_path or os.environ.get("PIXEL_REFINE_SESSION_DB")
        if not session_path:
            session_path = os.path.join(
                tempfile.gettempdir(), f"pixel_refine_session_{os.getpid()}.sqlite"
            )
        self.database_manager = DatabaseManager(session_path)
        self.json_path = os.path.join("database", "align", "batch_parameter.json")
        self.param_watcher = QFileSystemWatcher(self)
        self.param_watcher.fileChanged.connect(self._on_parameters_file_changed)

        # Pastikan direktori ada sebelum memonitor file
        json_dir = os.path.dirname(self.json_path)
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        # Jika file belum ada, buat file kosong agar bisa di-watch
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w") as f:
                json.dump({}, f)

        self.param_watcher.addPath(self.json_path)

        self.animator = StackedWidgetAnimator(self)
        self._active_fade_in_animations = {}
        self._running_delete_threads = []
        self._bulk_delete_animation_counter = 0
        self.active_batch_panels = weakref.WeakValueDictionary()
        self.batch_states = {}
        self._total_pending_imports = 0
        self._total_processed_imports = 0
        self._active_import_threads = []
        # Cache panel by batch_id for instant mode switching
        # Uses regular dict (strong ref) so panels survive hide/show cycles
        self._panel_cache: dict = {}

        # Cache for os.path.exists per batch_id to avoid re-stat on every
        # update_batch_view. Value is (timestamp_seconds, list_of_exists_flags).
        self._file_exists_cache: dict = {}
        self._file_exists_cache_ttl_seconds: int = 30

        # Active drop validation threads; keep refs so they aren't GC'd.
        self._active_drop_processors: list = []

        # Drop indicator overlay (created lazily on first drag-enter).
        self._drop_overlay: QFrame = None

        # Coalesce reorder requests onto a single event-loop tick.
        self._reorder_pending: bool = False

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)
        self.main_panel_container = QVBoxLayout()
        self._spacer_item = None
        self._placeholder_widget = None
        self._placeholder_wrapper = None

        self.main_scroll_area = setup_main_panel(
            self.main_panel_container, stylesheet.SCROLL_AREA
        )
        self.main_scroll_area.setObjectName("MainBatchScrollArea")
        self.main_scroll_area.setAcceptDrops(True)
        self.main_scroll_area.installEventFilter(self)
        self._original_scroll_stylesheet = self.main_scroll_area.styleSheet()

        self.batch_model = BulkBatchListModel(self)
        self.batch_delegate = BulkBatchDelegate(self)
        self.batch_list_view = BulkBatchListView(self.main_scroll_area.container)
        self.batch_list_view.setModel(self.batch_model)
        self.batch_list_view.setItemDelegate(self.batch_delegate)
        self.batch_delegate.action.connect(self._handle_virtual_row_action)
        self.batch_list_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.main_panel_container.addWidget(self.batch_list_view)
        self._snapshot_thread = None

        self.data_changed.connect(self.update_batch_view)

        # Hook scroll listener for lazy loading (Task 4)
        self.limit = 10
        self.load_timer_running = False
        self.MAX_CONCURRENT_BATCH_LOADERS = 2
        self.thumbnail_scheduler = ThumbnailScheduler(self)
        self._batch_ids = []
        self._batch_positions = {}
        self._view_generation = 0
        self._view_active = True
        self._is_scroll_idle = True
        self._wanted_batch_ids = set()
        self._prepared_batch_data = {}
        self._manifest_dirty = set()
        self._active_preloaders = []
        self._panel_materialization_queue = {}
        self._materialize_timer = QTimer(self)
        self._materialize_timer.setSingleShot(True)
        self._materialize_timer.timeout.connect(self._load_next_batch_incrementally)
        self._panel_build_timer = QTimer(self)
        self._panel_build_timer.setSingleShot(True)
        self._panel_build_timer.timeout.connect(self._materialize_next_batch_panel)
        self._viewport_timer = QTimer(self)
        self._viewport_timer.setSingleShot(True)
        self._viewport_timer.timeout.connect(self._refresh_visible_thumbnails)
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.timeout.connect(self._extend_batch_view)
        self._scroll_idle_timer = QTimer(self)
        self._scroll_idle_timer.setSingleShot(True)
        self._scroll_idle_timer.timeout.connect(self._on_scroll_idle)
        self._thumbnail_batch_queue = []
        self._active_thumbnail_batches = []
        self.main_scroll_area.verticalScrollBar().valueChanged.connect(
            self._on_scroll_changed
        )

        self.layout.addWidget(self.main_scroll_area)
        QTimer.singleShot(0, self.update_batch_view)

    def _on_scroll_changed(self, value):
        if not self._scroll_timer.isActive():
            self._scroll_timer.start(16)
        self._is_scroll_idle = False
        self._scroll_idle_timer.start(120)
        self._panel_build_timer.stop()
        # Hindari membuat QWidget ketika scrollbar masih bergerak. Pembuatan
        # panel cukup berat dan dijadwalkan setelah scroll berhenti sejenak.

    def _on_scroll_idle(self):
        self._is_scroll_idle = True
        self._viewport_timer.start(0)

    def _extend_batch_view(self):
        bar = self.main_scroll_area.verticalScrollBar()
        if bar.maximum() > 0 and bar.value() > bar.maximum() * 0.8 and self.limit < len(self._batch_ids):
            self.limit = min(self.limit + 10, len(self._batch_ids))
            self._render_batch_view()

    def showEvent(self, event):
        super().showEvent(event)
        self._view_active = True
        self._is_scroll_idle = True
        self._viewport_timer.start(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_viewport_timer"):
            self._is_scroll_idle = True
            if hasattr(self, "batch_list_view"):
                self.batch_list_view.update_content_height(
                    len(self.batch_model.records), self.main_scroll_area.viewport().height()
                )
            self._viewport_timer.start(0)

    def _load_next_batch_incrementally(self):
        if not self._view_active or not self.loading_queue:
            self.load_timer_running = False
            return
        if len(self._active_preloaders) >= 2:
            return
        batch_id = self.loading_queue.pop(0)
        if batch_id not in self._wanted_batch_ids or (
            batch_id not in self.active_skeletons and batch_id not in self._manifest_dirty
        ):
            self._materialize_timer.start(8)
            return
        prepared = self._prepared_batch_data.get(batch_id)
        if prepared is not None:
            panel = self.active_batch_panels.get(batch_id)
            if panel is not None:
                panel.refresh_image_paths(prepared[1])
                self._manifest_dirty.discard(batch_id)
                self._viewport_timer.start(0)
            else:
                self._queue_panel_materialization(batch_id, *prepared)
            self._materialize_timer.start(8)
            return
        preloader = BatchPreloaderThread(self.database_manager, batch_id, parent=self)
        preloader.json_path = self.json_path
        preloader.view_generation = self._view_generation
        preloader.batch_prepared.connect(self._on_batch_prepared)
        preloader.finished.connect(self._on_preloader_finished)
        self._active_preloaders.append(preloader)
        preloader.start(QThread.Priority.LowPriority)
        self._materialize_timer.start(8)

    @Slot(object, dict, list)
    def _on_batch_prepared(self, batch_id, state, paths):
        preloader = self.sender()
        if preloader.view_generation != self._view_generation or batch_id not in self._batch_positions:
            return
        self._prepared_batch_data[batch_id] = (state, paths)
        if self._view_active and batch_id in self._wanted_batch_ids:
            panel = self.active_batch_panels.get(batch_id)
            if panel is not None:
                panel.refresh_image_paths(paths)
                self._manifest_dirty.discard(batch_id)
                self._viewport_timer.start(0)
            else:
                self._queue_panel_materialization(batch_id, state, paths)

    def _queue_panel_materialization(self, batch_id, state, paths):
        if batch_id not in self.active_skeletons:
            return
        self._panel_materialization_queue[batch_id] = (state, paths)
        if self._is_scroll_idle and not self._panel_build_timer.isActive():
            self._panel_build_timer.start(0)

    @Slot()
    def _materialize_next_batch_panel(self):
        if (
            not self._view_active
            or not self._is_scroll_idle
            or not self._panel_materialization_queue
        ):
            return

        for batch_id in list(self._panel_materialization_queue):
            if batch_id not in self.active_skeletons:
                self._panel_materialization_queue.pop(batch_id, None)
                continue
            if batch_id not in self._wanted_batch_ids:
                continue

            state, paths = self._panel_materialization_queue.pop(batch_id)
            self._materialize_batch(batch_id, state, paths)
            # Yield to paint/input/scroll events between comparatively expensive
            # panel constructors while keeping visible rows moving forward.
            if self._panel_materialization_queue:
                self._panel_build_timer.start(24)
            return

    @Slot()
    def _on_preloader_finished(self):
        preloader = self.sender()
        if preloader in self._active_preloaders:
            self._active_preloaders.remove(preloader)
        preloader.deleteLater()
        if self._view_active:
            self._viewport_timer.start(0)

    def _materialize_batch(self, batch_id, state, paths):
        skeleton = self.active_skeletons.pop(batch_id, None)
        if skeleton is None:
            return
        panel = self.setup_combined_panel(
            batch_id, preloaded_state=self.batch_states.get(batch_id, state),
            preloaded_image_paths=paths,
        )
        index = self.main_panel_container.indexOf(skeleton)
        self.main_panel_container.removeWidget(skeleton)
        skeleton.hide()
        skeleton.deleteLater()
        self.main_panel_container.insertWidget(max(0, index), panel)
        panel.update_sequential_number(self._batch_positions.get(batch_id, 0) + 1)
        self.main_panel_container.invalidate()
        self.main_panel_container.activate()
        self.main_scroll_area.update_inner_dimensions()
        self._viewport_timer.start(0)

    def refresh_after_project_load(self):
        """Discard legacy UI caches and rebuild from the active session DB."""
        self.stop_thumbnail()
        for panel in list(self._panel_cache.values()):
            try:
                self.main_panel_container.removeWidget(panel)
                panel.deleteLater()
            except RuntimeError:
                pass
        for skeleton in list(self.active_skeletons.values()):
            try:
                self.main_panel_container.removeWidget(skeleton)
                skeleton.deleteLater()
            except RuntimeError:
                pass
        self.active_batch_panels.clear()
        self.active_skeletons.clear()
        self._panel_cache.clear()
        self._prepared_batch_data.clear()
        self._panel_materialization_queue.clear()
        self._manifest_dirty.clear()
        self.batch_states.clear()
        self.loading_queue.clear()
        self.limit = 10
        self.update_batch_view()

    def update_batch_view(self):
        """Prepare all batch rows in a worker, then publish one model snapshot."""
        self._view_active = True
        self._view_generation += 1
        generation = self._view_generation
        if self._snapshot_thread is not None and self._snapshot_thread.isRunning():
            self._snapshot_thread.requestInterruption()
        worker = BulkSnapshotThread(self.database_manager, self.json_path, generation, self)
        worker.prepared.connect(self._on_bulk_snapshot_ready)
        worker.finished.connect(lambda w=worker: self._on_bulk_snapshot_finished(w))
        self._snapshot_thread = worker
        worker.start(QThread.Priority.LowPriority)

    @Slot(int, object)
    def _on_bulk_snapshot_ready(self, generation, records):
        if generation != self._view_generation:
            return
        self._batch_ids = [record["id"] for record in records]
        self._batch_positions = {batch_id: index for index, batch_id in enumerate(self._batch_ids)}
        self.batch_model.replace_records(records)
        for record in records:
            self.batch_states[record["id"]] = record["state"]
        self.batch_list_view.update_content_height(len(records), self.main_scroll_area.viewport().height())
        self.batch_list_view.setVisible(bool(records))
        if not records:
            if self._placeholder_wrapper is None:
                self._placeholder_wrapper, self._placeholder_widget = self._create_viewport_centered_placeholder()
                self.main_panel_container.addWidget(self._placeholder_wrapper)
        elif self._placeholder_wrapper is not None:
            self.main_panel_container.removeWidget(self._placeholder_wrapper)
            self._placeholder_wrapper.deleteLater()
            self._placeholder_wrapper = self._placeholder_widget = None
        self.main_panel_container.invalidate()
        self.main_panel_container.activate()
        self.main_scroll_area.update_inner_dimensions()
        self._viewport_timer.start(0)

    def _on_bulk_snapshot_finished(self, worker):
        if self._snapshot_thread is worker:
            self._snapshot_thread = None
        worker.deleteLater()

    def _render_batch_view(self):
        # The model owns all rows; QListView paints only the visible viewport.
        self.batch_list_view.update_content_height(len(self.batch_model.records), self.main_scroll_area.viewport().height())
        self.batch_list_view.viewport().update()
        self.main_panel_container.invalidate()
        self.main_panel_container.activate()
        self.main_scroll_area.update_inner_dimensions()

    def _reorder_visual_batch_numbers(self):
        for batch_id, panel in self.active_batch_panels.items():
            number = self._batch_positions.get(batch_id, 0) + 1
            if panel.sequential_batch_number != number:
                panel.update_sequential_number(number)
        for batch_id, skeleton in self.active_skeletons.items():
            skeleton.batch_label.setText(f"Batch {self._batch_positions.get(batch_id, 0) + 1}")

    def _manage_placeholder_and_spacer(self):
        """Menampilkan placeholder jika tidak ada batch, atau spacer jika ada batch."""
        has_batches = (
            len(self.active_batch_panels) > 0 or len(self.active_skeletons) > 0
        )

        # Jika ada batch
        if has_batches:
            # Sembunyikan dan hapus placeholder wrapper jika ada
            if self._placeholder_wrapper:
                try:
                    self.main_panel_container.removeWidget(self._placeholder_wrapper)
                    self._placeholder_wrapper.hide()
                    self._placeholder_wrapper.deleteLater()
                except RuntimeError:
                    pass
                self._placeholder_wrapper = None
                self._placeholder_widget = None

            # Pastikan spacer ada di bagian bawah
            if not self._spacer_item:
                self._spacer_item = QSpacerItem(
                    20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
                )
                self.main_panel_container.addSpacerItem(self._spacer_item)

        else:
            # Hapus spacer jika ada
            if self._spacer_item:
                self.main_panel_container.removeItem(self._spacer_item)
                self._spacer_item = None

            # Tampilkan placeholder jika belum ada
            if not self._placeholder_wrapper:
                self._placeholder_wrapper, self._placeholder_widget = (
                    self._create_viewport_centered_placeholder()
                )
                self.main_panel_container.addWidget(self._placeholder_wrapper)

    def _create_viewport_centered_placeholder(self):
        """Membuat placeholder yang selalu di tengah viewport scroll area."""
        try:
            format_keys = SUPPORTED_FORMATS.keys()
            supported_formats_text = ", ".join(sorted(list(format_keys)))
        except Exception:
            supported_formats_text = "jpg, png, tiff"

        html_text = f"""
        <p align="center">
            {language_config.PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES}<br><br>
            <span style="color:#666;">{language_config.SUPPORTED_IMAGE_EXTENSION}:</span><br>
            {supported_formats_text}
        </p>
        """
        placeholder_label = QLabel()
        placeholder_label.setTextFormat(Qt.TextFormat.RichText)
        placeholder_label.setText(html_text)
        placeholder_label.setWordWrap(True)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(stylesheet.PLACEHOLDER_LABEL_STYLE)
        placeholder_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )

        # Wrapper yang mengisi seluruh layout dan memusatkan label
        wrapper = QWidget()
        wrapper.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        v_layout = QVBoxLayout(wrapper)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addStretch(1)
        v_layout.addWidget(placeholder_label, 0, Qt.AlignmentFlag.AlignHCenter)
        v_layout.addStretch(1)
        return wrapper, placeholder_label

    def _start_fade_in_animation(self, panel_to_animate):
        if (
            panel_to_animate in self._active_fade_in_animations
            and self._active_fade_in_animations[panel_to_animate].state()
            == QPropertyAnimation.State.Running
        ):
            self._active_fade_in_animations[panel_to_animate].stop()
            if panel_to_animate.graphicsEffect():
                panel_to_animate.setGraphicsEffect(None)

        opacity_effect = QGraphicsOpacityEffect(panel_to_animate)
        panel_to_animate.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.0)

        duration = 350
        curve = QEasingCurve.Type.InOutQuad

        anim = QPropertyAnimation(opacity_effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(curve)

        anim.finished.connect(
            lambda effect=opacity_effect, widget=panel_to_animate: self._on_fade_in_finished(
                effect, widget
            )
        )

        self._active_fade_in_animations[panel_to_animate] = anim
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _on_fade_in_finished(self, effect: QGraphicsOpacityEffect, widget: QWidget):
        if widget:
            if widget.graphicsEffect() == effect:
                widget.setGraphicsEffect(None)
        if widget in self._active_fade_in_animations:
            del self._active_fade_in_animations[widget]

    @Slot(str)
    def _on_parameters_file_changed(self, path):
        all_new_states = {}
        try:
            all_new_states = load_json_state(path)
        except json.JSONDecodeError:
            QTimer.singleShot(100, lambda p=path: self._on_parameters_file_changed(p))
            return

        if all_new_states:
            for batch_id in self._batch_ids:
                if str(batch_id) in all_new_states:
                    self.batch_states[batch_id] = all_new_states[str(batch_id)]
                    record = self.batch_model.record_for_id(batch_id)
                    if record is not None:
                        record["state"] = dict(all_new_states[str(batch_id)] or {})
            if self.batch_model.rowCount():
                self.batch_model.dataChanged.emit(
                    self.batch_model.index(0, 0),
                    self.batch_model.index(self.batch_model.rowCount() - 1, 0),
                    [BulkBatchListModel.RecordRole],
                )
            for batch_id, (_, paths) in list(self._prepared_batch_data.items()):
                self._prepared_batch_data[batch_id] = (all_new_states.get(str(batch_id), {}), paths)
            self.parameters_changed.emit(all_new_states)

        self.param_watcher.removePath(path)
        QTimer.singleShot(100, lambda p=path: self.param_watcher.addPath(p))

    def setup_combined_panel(
        self, batch_id=None, preloaded_state=None, preloaded_image_paths=None
    ):
        initial_state = (
            preloaded_state
            if preloaded_state is not None
            else self.batch_states.get(batch_id, {})
        )
        combined_panel = CombinedPanel(
            database_manager=self.database_manager,
            batch_id=batch_id,
            parent=self,
            thumbnail_threads=self.thumbnail_threads,
            thumbnail_placeholders=self.thumbnail_placeholders,
            initial_state=initial_state,
            preloaded_image_paths=preloaded_image_paths,
        )
        self.active_batch_panels[batch_id] = combined_panel
        # Simpan ke cache untuk instant restore pada re-entry mode bulk
        self._panel_cache[batch_id] = combined_panel
        self.parameters_changed.connect(combined_panel.refresh_ui_from_broadcast)

        combined_panel.set_waiting_state()
        self._enqueue_thumbnail_loading(combined_panel)
        return combined_panel

    def _enqueue_thumbnail_loading(self, panel):
        if thumbnail_creation_enabled(self.thumbnail_policy):
            self._viewport_timer.start(0)

    def _refresh_visible_thumbnails(self):
        if not self._view_active:
            return
        bar = self.main_scroll_area.verticalScrollBar()
        if not thumbnail_creation_enabled(self.thumbnail_policy):
            return
        row_pitch = BulkBatchDelegate.HEIGHT + BulkBatchDelegate.ROW_GAP
        row_offset = 0
        first = max(0, (bar.value() - row_offset) // row_pitch - 1)
        last = min(
            len(self.batch_model.records),
            (bar.value() + self.main_scroll_area.viewport().height() - row_offset) // row_pitch + 2,
        )
        visible_records = self.batch_model.records[first:last]
        needed_paths = {
            path for record in visible_records
            for path in record["paths"]
            if path not in record["thumbnails"]
        }
        self.thumbnail_scheduler.cancel_except(self, needed_paths)
        for record in visible_records:
            record.setdefault("thumbnail_loading", set())
            requested = False
            for path in record["paths"]:
                if path not in record["thumbnails"]:
                    record["thumbnail_loading"].add(path)
                    requested = True
                    self.thumbnail_scheduler.request(
                        self, path,
                        lambda image, image_path, row=record: self._on_virtual_thumbnail_ready(row, image_path, image),
                    )
            if requested:
                self.batch_list_view.refresh_thumbnail_record(record)

    def _on_virtual_thumbnail_ready(self, record, path, image):
        record.setdefault("thumbnail_loading", set()).discard(path)
        if image is not None and not image.isNull() and record in self.batch_model.records:
            record["thumbnails"][path] = image
            self.batch_list_view.refresh_thumbnail_record(record)
            self.batch_list_view.viewport().update()
        elif record in self.batch_model.records:
            self.batch_list_view.refresh_thumbnail_record(record)
            self.batch_list_view.viewport().update()

    def _trim_panel_cache(self, top, bottom):
        return

    def _handle_virtual_row_action(self, action, batch_id, value):
        record = self.batch_model.record_for_id(batch_id)
        if record is None:
            return
        if action == "add":
            from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_import_service import handle_add_image_to_batch
            handle_add_image_to_batch(self, self.database_manager, self.thumbnail_threads, batch_id, None)
        elif action == "delete":
            self.handle_delete_individual_batch(batch_id)
        elif action == "toggle":
            keys = ("checkbox_align_images", "checkbox_denoising", "checkbox_super_resolution")
            key = keys[int(value)]
            state = record["state"]
            state[key] = not bool(state.get(key, False))
            if state[key] and key == "checkbox_denoising":
                state["checkbox_super_resolution"] = False
            elif state[key] and key == "checkbox_super_resolution":
                state["checkbox_denoising"] = False
            self._save_virtual_batch_state(batch_id, state)
            self.batch_list_view.viewport().update()
        elif action == "choose":
            category = str(value)
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import get_algorithm_options
            menu = QMenu(self)
            for name, _ in get_algorithm_options(category):
                menu.addAction(str(name))
            selected = menu.exec(self.batch_list_view.mapToGlobal(self.batch_list_view.viewport().mapFromGlobal(self.cursor().pos())))
            if selected is not None:
                key = {"alignment": "alignment_algo", "denoising": "denoising_algo",
                       "super_resolution": "super_resolution_algo"}[category]
                record["state"][key] = selected.text()
                self._save_virtual_batch_state(batch_id, record["state"])
                self.batch_list_view.viewport().update()
        elif action == "preview":
            panel = self.setup_combined_panel(batch_id, record["state"], record["paths"])
            panel.update_sequential_number(self._batch_positions.get(batch_id, 0) + 1)
            panel.process_and_preview()

    def _save_virtual_batch_state(self, batch_id, state):
        try:
            all_states = load_json_state(self.json_path)
            all_states[str(batch_id)] = dict(state)
            with open(self.json_path, "w", encoding="utf-8") as stream:
                json.dump(all_states, stream, indent=4)
            self.batch_states[batch_id] = dict(state)
        except Exception as error:
            print(f"[BulkPageLayout] Could not save settings for batch {batch_id}: {error}")

    def _trim_panel_cache(self, top, bottom):
        return

    def _process_thumbnail_queue(self):
        """Schedule nearby batches through the shared bounded thumbnail queue."""
        if not thumbnail_creation_enabled(self.thumbnail_policy):
            self._thumbnail_batch_queue.clear()
            if hasattr(self, "_active_thumbnail_batches"):
                self._active_thumbnail_batches.clear()
            return

        if not hasattr(self, "_active_thumbnail_batches"):
            self._active_thumbnail_batches = []
        if not getattr(self, "_thumbnail_batch_queue", None):
            return

        from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
            is_widget_alive,
        )

        while (
            len(self._active_thumbnail_batches) < self.MAX_CONCURRENT_BATCH_LOADERS
            and self._thumbnail_batch_queue
        ):
            next_panel = self._thumbnail_batch_queue.pop(0)
            if not is_widget_alive(next_panel):
                continue

            self._active_thumbnail_batches.append(next_panel)
            next_panel.delay_thumbnails(
                completion_callback=lambda p=next_panel: self._on_batch_thumbnail_completed(p)
            )

    @Slot(bool)
    def _on_thumbnail_policy_changed(self, enabled):
        if enabled:
            self._viewport_timer.start(0)
            return

        self._thumbnail_batch_queue.clear()
        if hasattr(self, "_active_thumbnail_batches"):
            self._active_thumbnail_batches.clear()
        self.thumbnail_scheduler.cancel_all()
        stop_process_thumbnails(self.thumbnail_threads)

        panels = list(self.active_batch_panels.values()) + list(
            self._panel_cache.values()
        )
        seen = set()
        for panel in panels:
            if panel is None or id(panel) in seen:
                continue
            seen.add(id(panel))
            try:
                panel.disable_thumbnail_loading()
            except Exception:
                pass

    def _on_batch_thumbnail_completed(self, panel=None):
        """Dipanggil ketika satu batch selesai memuat thumbnail 100% atau setelah 6 detik inactivity watchdog."""
        if hasattr(self, "_active_thumbnail_batches") and panel in self._active_thumbnail_batches:
            self._active_thumbnail_batches.remove(panel)
        if self._view_active:
            self._viewport_timer.start(0)

    # --- Event Handling ---
    def eventFilter(self, source, event: QEvent):
        if source == self.main_scroll_area:
            return self._handle_scroll_area_events(event)
        return super().eventFilter(source, event)

    def _handle_scroll_area_events(self, event: QEvent):
        if event.type() == QEvent.Type.DragEnter:
            return self._handle_drag_enter(event)
        elif event.type() == QEvent.Type.DragLeave:
            return self._handle_drag_leave(event)
        elif event.type() == QEvent.Type.DragMove:
            return self._handle_drag_move(event)
        elif event.type() == QEvent.Type.Drop:
            return self._handle_drop(event)
        return False

    def _ensure_drop_overlay(self):
        """Create the drop indicator overlay on first use (lazy)."""
        if self._drop_overlay is not None:
            return self._drop_overlay
        overlay = QFrame(self.main_scroll_area)
        overlay.setObjectName("BulkDropOverlay")
        overlay.setStyleSheet(
            "#BulkDropOverlay {"
            "  background-color: rgba(76, 175, 80, 30);"
            "  border: 2px dashed #4CAF50;"
            "  border-radius: 6px;"
            "}"
        )
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        overlay.hide()
        self._drop_overlay = overlay
        return overlay

    def _show_drop_overlay(self):
        overlay = self._ensure_drop_overlay()
        viewport = self.main_scroll_area.viewport()
        overlay.setGeometry(viewport.rect())
        overlay.raise_()
        overlay.show()

    def _hide_drop_overlay(self):
        if self._drop_overlay is not None:
            self._drop_overlay.hide()

    def _handle_drag_enter(self, event):
        should_accept = False
        if event.mimeData().hasUrls():
            supported_extensions = {
                ext for fmts in SUPPORTED_FORMATS.values() for ext in fmts
            }
            has_image = any(
                url.isLocalFile()
                and os.path.splitext(url.toLocalFile())[1].lower()
                in supported_extensions
                for url in event.mimeData().urls()
            )
            if has_image:
                should_accept = True

        if should_accept:
            event.acceptProposedAction()
            self.main_scroll_area.setProperty("acceptingDrop", True)
            self._show_drop_overlay()
        else:
            event.ignore()
        return True

    def _handle_drag_leave(self, event):
        if self.main_scroll_area.property("acceptingDrop"):
            self.main_scroll_area.setProperty("acceptingDrop", False)
            self._hide_drop_overlay()
        event.accept()
        return True

    def _handle_drag_move(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
        return True

    def _handle_drop(self, event):
        # Reset the visual cue immediately so the user gets feedback within
        # a single frame, regardless of how long validation takes.
        if self.main_scroll_area.property("acceptingDrop"):
            self.main_scroll_area.setProperty("acceptingDrop", False)
            self._hide_drop_overlay()

        if not event.mimeData().hasUrls():
            event.ignore()
            return True

        event.acceptProposedAction()

        # Cheap, extension-only filter. Existence + DB work happens on the
        # worker thread to keep the drop event non-blocking.
        supported_extensions = {
            ext for fmts in SUPPORTED_FORMATS.values() for ext in fmts
        }
        candidate_paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
            and os.path.splitext(url.toLocalFile())[1].lower()
            in supported_extensions
        ]

        if not candidate_paths:
            return True

        # Invalidate the file-exists cache for every batch because new
        # paths may now exist on disk; the cache will refill lazily.
        self._file_exists_cache.clear()

        processor = BulkDropProcessor(candidate_paths, parent=self)
        processor.prepared.connect(self._on_drop_prepared)
        processor.finished.connect(
            lambda p=processor: self._on_drop_processor_finished(p)
        )
        if hasattr(processor, "failed"):
            processor.failed.connect(self._on_drop_failed)
        self._active_drop_processors.append(processor)
        processor.start()
        return True

    def _on_drop_prepared(self, valid_image_paths):
        if valid_image_paths:
            process_and_start_batch_import(self, valid_image_paths)

    def _on_drop_failed(self, message):
        print(f"[BulkPageLayout] Drop validation failed: {message}")

    def _on_drop_processor_finished(self, processor):
        try:
            self._active_drop_processors.remove(processor)
        except ValueError:
            pass
        processor.deleteLater()

    def _schedule_reorder(self):
        """Coalesce reorder requests onto a single event-loop tick."""
        if self._reorder_pending:
            return
        self._reorder_pending = True
        QTimer.singleShot(0, self._run_scheduled_reorder)

    def _run_scheduled_reorder(self):
        self._reorder_pending = False
        self._reorder_visual_batch_numbers()

    def invalidate_file_exists_cache(self, batch_id=None):
        """Drop cached existence flags for one batch (or all)."""
        if batch_id is None:
            self._file_exists_cache.clear()
        else:
            self._file_exists_cache.pop(batch_id, None)

    def get_cached_file_exists(self, batch_id, raw_paths, now_fn=None):
        """Return cached existence flags for *raw_paths* or None on miss.

        On miss, callers fall back to the existing os.path.exists loop and
        may call :meth:`set_cached_file_exists` to populate the cache.
        """
        if not raw_paths:
            return [True]  # empty batch is trivially "all present"
        entry = self._file_exists_cache.get(batch_id)
        if entry is None:
            return None
        ts, flags = entry
        import time as _time
        now = now_fn if now_fn is not None else _time.monotonic
        if now() - ts > self._file_exists_cache_ttl_seconds:
            return None
        if len(flags) != len(raw_paths):
            return None
        return flags

    def set_cached_file_exists(self, batch_id, flags):
        import time as _time
        self._file_exists_cache[batch_id] = (_time.monotonic(), list(flags))

    # --- Batch Processing ---
    def get_files_in_stack_folder(self):
        """Mengembalikan daftar path lengkap file di folder 'database/stack'."""
        folder_path = "database/stack"
        if not os.path.isdir(folder_path):
            return []
        try:
            return [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
            ]
        except Exception as e:
            return []

    def process_all_batches(self):
        """
        Mengumpulkan batch yang valid dan menampilkan dialog konfirmasi pemrosesan.
        """
        # Processing uses the DB index, independent of which panels are mounted.
        batch_ids = self.database_manager.get_all_batch_ids()
        if not batch_ids:
            self.show_toast_requested.emit(
                language_config.UI_LABEL_BATCH_NO_PROCESS, 4000, False
            )
            return

        batches_wrapper = []
        for number, batch_id in enumerate(batch_ids, 1):
            panel = self._panel_cache.get(batch_id)
            target = panel if panel is not None else SimpleNamespace(
                batch_id=batch_id, database_manager=self.database_manager,
                selected_algorithms={},
            )
            batches_wrapper.append(SimpleNamespace(
                original_panel=target, id=batch_id, batch_id=batch_id,
                sequential_batch_number=number, name=f"Batch {number}",
            ))
        dialog = BatchProcessDialog(batches_wrapper, self, self)
        dialog.exec()

    def _move_single_batch_result(self, source_file_path, target_folder):
        """
        Move an exact result name without inventing numbered batch copies.
        Worker callers receive the full error rather than opening a GUI dialog.
        """
        self._last_result_export_detail = ""
        if not source_file_path or not os.path.exists(source_file_path):
            print(language_config.SOURCE_FILE_DOES_NOT_EXIST.format(source_file_path))
            return False

        if not target_folder or not os.path.isdir(target_folder):
            self._last_result_export_detail = f"Target folder is not accessible: {target_folder}"
            print(self._last_result_export_detail)
            return False

        original_file_name = os.path.basename(source_file_path)
        destination_path = os.path.join(target_folder, original_file_name)

        try:
            # Pindahkan file; jika Windows menolak rename karena file masih
            # dipegang pembaca, simpan salinan terverifikasi terlebih dahulu.
            move_ok, move_detail = _move_file_with_verified_copy_fallback(
                source_file_path, destination_path
            )
            self._last_result_export_detail = move_detail
            if not move_ok:
                raise OSError(move_detail)

            print(
                language_config.LOG_MOVE_SUCCESS.format(
                    original_file_name, destination_path
                )
            )
            if move_detail != "moved":
                print(f"[Bulk Save] {move_detail}")
            return True

        except Exception as e:
            error_detail_msg = str(e)
            self._last_result_export_detail = error_detail_msg
            print(
                language_config.LOG_MOVE_FAILED.format(
                    original_file_name, target_folder, error_detail_msg
                )
            )
            return False

    def handle_delete_individual_batch(self, batch_id):
        if self.batch_model.record_for_id(batch_id) is None and batch_id not in self._batch_ids:
            return

        title, message = language_config.BATCH_DELETE_LABEL
        message = message.format(batch_id)
        from UILibrary import modal_confirm

        reply = modal_confirm.question(self, message)

        if reply:
            self.batch_states.pop(batch_id, None)
            self._start_background_delete_process(batch_id)

    def handle_delete_all_batches(self):
        title = language_config.TITLE_BATCH_ALL_DELETE_BUTTON
        conn = None
        batch_defined_count = 0
        try:
            db_path = self.database_manager.db_path
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("SELECT COUNT(*) FROM batch_process")
            batch_defined_count = cursor.fetchone()[0]
        except Exception as e:
            QMessageBox.critical(
                self, "Database Error", f"Failed to check batch status: {e}"
            )
            return
        finally:
            if conn:
                conn.close()

        if batch_defined_count == 0:
            QMessageBox.information(
                self,
                title,
                language_config.NO_DATA_BATCH_ALL_DELETE_BUTTON,
                QMessageBox.StandardButton.Ok,
            )
            return

        message = language_config.CONFIRM_BATCH_ALL_DELETE_BUTTON.format(
            batch_defined_count
        )
        from UILibrary import modal_confirm

        reply = modal_confirm.question(self, message)

        if reply:
            self.batch_states.clear()
            self._start_bulk_background_delete_process()

    def _start_bulk_background_delete_process(self):
        """Memulai proses penghapusan semua batch di background."""
        # Hapus seluruh cache panel karena semua batch akan dihapus
        for bid, panel in list(self._panel_cache.items()):
            try:
                panel.deleteLater()
            except RuntimeError:
                pass
        self._panel_cache.clear()
        deleter = BulkDeleteProcess(
            self.database_manager, None, CACHE_DIR, self.thumbnail_threads
        )
        deleter.batch_deleted.connect(self.data_changed.emit)
        deleter.delete_all_batch()

    def _trigger_single_bulk_fade_out(self, panel_ref):
        """Memulai fade out untuk satu panel dalam proses bulk delete."""
        panel = panel_ref() if panel_ref else None
        if is_widget_alive(panel):
            fade_out(
                animator=self.animator,
                widget=panel,
                duration=300,
                on_finished_callback=lambda pref=panel_ref: self._bulk_delete_post_single_animation(
                    pref
                ),
            )
        else:
            # Widget sudah tidak valid, langsung cek animasi selesai
            self._check_bulk_delete_animations_finished()

    def _check_bulk_delete_animations_finished(self):
        """Dipanggil setiap kali satu animasi fade-out selesai saat delete all."""
        self._bulk_delete_animation_counter -= 1
        if self._bulk_delete_animation_counter <= 0:
            self._start_bulk_background_delete_process()

    def _bulk_delete_post_single_animation(self, panel_ref):
        panel = panel_ref() if panel_ref else None
        safe_hide_widget(panel)
        # Hapus panel dari cache jika ada
        if panel is not None:
            for bid, cached in list(self._panel_cache.items()):
                if cached is panel:
                    self._panel_cache.pop(bid, None)
                    break
        self._check_bulk_delete_animations_finished()

    def _individual_delete_post_animation(self, batch_id, panel_ref):
        """Callback setelah animasi fade-out individual selesai."""
        panel = panel_ref() if panel_ref else None
        safe_hide_widget(panel)
        # Hapus dari cache agar tidak di-restore saat re-entry
        stale = self._panel_cache.pop(batch_id, None)
        if stale and stale is not panel:
            try:
                stale.deleteLater()
            except RuntimeError:
                pass
        self._start_background_delete_process(batch_id)

    def _start_background_delete_process(self, batch_id):
        """Memulai proses penghapusan di background thread."""
        deleter_thread = BulkDeleteProcess(
            self.database_manager, batch_id, CACHE_DIR, self.thumbnail_threads
        )
        self._running_delete_threads.append(deleter_thread)

        # Hubungkan sinyal SEBELUM memulai thread
        deleter_thread.batch_deleted.connect(self.data_changed.emit)

        # --- HUBUNGKAN FINISHED UNTUK CLEANUP ---
        deleter_thread.finished.connect(
            lambda thread=deleter_thread: self._on_delete_thread_finished(thread)
        )
        deleter_thread.start()

    def _on_delete_thread_finished(self, thread_instance):
        """Dipanggil saat thread delete selesai untuk menghapusnya dari list."""
        try:
            self._running_delete_threads.remove(thread_instance)
        except ValueError:
            pass

    # --- Batch Import ---
    def handle_batch_import_button(self):
        """Membuka dialog file dan memulai proses impor batch."""

        filter_parts = []
        all_supported_extensions = []

        for ext_list in SUPPORTED_FORMATS.values():
            all_supported_extensions.extend([f"*{ext}" for ext in ext_list])
        all_filter_str = f"All Supported Images ({' '.join(sorted(list(set(all_supported_extensions))))})"
        filter_parts.append(all_filter_str)

        for format_key, extensions in SUPPORTED_FORMATS.items():
            formatted_extensions = " ".join([f"*{ext}" for ext in extensions])
            description = f"{format_key.upper()} Files"
            filter_parts.append(f"{description} ({formatted_extensions})")

        filter_parts.append("All Files (*)")

        file_dialog_filter = ";;".join(filter_parts)

        image_paths, _ = QFileDialog.getOpenFileNames(
            self,
            language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH,  # Judul dialog
            "",
            file_dialog_filter,
        )

        if image_paths:
            process_and_start_batch_import(self, image_paths)

    # --- Helper Methods ---
    def stop_thumbnail(self):
        """Menghentikan semua thread thumbnail dan menyimpan panel ke cache untuk instant restore.

        Panel TIDAK dihancurkan — disimpan ke _panel_cache berdasarkan batch_id.
        Saat user kembali ke bulk mode, update_batch_view() akan langsung menampilkan
        panel dari cache tanpa skeleton/delay (instant mode switching).
        """
        self._view_active = False
        self._view_generation += 1
        self._materialize_timer.stop()
        self._panel_build_timer.stop()
        self._viewport_timer.stop()
        self._scroll_timer.stop()
        self._scroll_idle_timer.stop()
        self.thumbnail_scheduler.cancel_all()
        if self._snapshot_thread is not None and self._snapshot_thread.isRunning():
            self._snapshot_thread.requestInterruption()
        for preloader in self._active_preloaders:
            preloader.requestInterruption()
        for panel in list(self.active_batch_panels.values()):
            panel.pause_thumbnail_loading()
        stop_process_thumbnails(self.thumbnail_threads)

        # Clear incremental loading and thumbnail batch queues
        self.loading_queue.clear()
        self.load_timer_running = False
        if hasattr(self, "_thumbnail_batch_queue"):
            self._thumbnail_batch_queue.clear()
        self._panel_materialization_queue.clear()
        if hasattr(self, "_active_thumbnail_batches"):
            self._active_thumbnail_batches.clear()

        # Safely remove active skeletons from layout (skeleton tidak di-cache)
        from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
            is_widget_alive,
        )

        for bid, skel in list(self.active_skeletons.items()):
            if skel and is_widget_alive(skel):
                try:
                    self.main_panel_container.removeWidget(skel)
                    skel.hide()
                    skel.deleteLater()
                except RuntimeError:
                    pass
        self.active_skeletons.clear()

        # Simpan panel ke cache SEBELUM lepas dari layout
        # Panel disembunyikan (bukan dihancurkan) → siap di-reuse saat kembali
        for bid, panel in list(self.active_batch_panels.items()):
            if is_widget_alive(panel):
                try:
                    self.main_panel_container.removeWidget(panel)
                    panel.hide()
                    # Simpan ke cache (kuat/strong ref) agar tidak di-GC
                    self._panel_cache[bid] = panel
                except RuntimeError:
                    # Panel sudah rusak, jangan cache
                    self._panel_cache.pop(bid, None)
            else:
                self._panel_cache.pop(bid, None)
        self.active_batch_panels = weakref.WeakValueDictionary()

        # Bersihkan panel cache untuk batch yang sudah tidak ada di DB
        try:
            db_ids = set(self.database_manager.get_all_batch_ids())
            for stale_id in list(self._panel_cache.keys()):
                if stale_id not in db_ids:
                    stale_panel = self._panel_cache.pop(stale_id, None)
                    if stale_panel and is_widget_alive(stale_panel):
                        try:
                            stale_panel.deleteLater()
                        except RuntimeError:
                            pass
        except Exception:
            pass  # DB query optional — tidak gagalkan operasi utama

        # Reset placeholder sehingga dibuat ulang jika tidak ada batch
        if self._placeholder_wrapper:
            try:
                self.main_panel_container.removeWidget(self._placeholder_wrapper)
                self._placeholder_wrapper.hide()
                self._placeholder_wrapper.deleteLater()
            except RuntimeError:
                pass
            self._placeholder_wrapper = None
            self._placeholder_widget = None

        # Lepas spacer bawah agar layout bersih
        if self._spacer_item:
            self.main_panel_container.removeItem(self._spacer_item)
            self._spacer_item = None

    # --- Aggregated Progress ---
    @Slot()
    def _handle_item_imported(self):
        """Dipanggil setiap kali satu item berhasil diimpor oleh thread manapun."""
        self._total_processed_imports += 1
        self._update_aggregated_progress_toast()  # Update tampilan progres

    @Slot(QThread)
    def _handle_thread_finished(self, thread_instance):
        """Dipanggil saat thread impor selesai."""
        if thread_instance in self._active_import_threads:
            self._active_import_threads.remove(thread_instance)
        else:
            print("Warning: Finished thread not found in active list.")

        if not self._active_import_threads:
            # Reset state agregat
            self._total_pending_imports = 0
            self._total_processed_imports = 0

            # Emit sinyal data changed untuk refresh UI
            self.data_changed.emit()

    def _update_aggregated_progress_toast(self):
        """Disembunyikan agar tidak muncul toast di kanan bawah saat impor."""
        pass

    @Slot(int, int)
    def _update_import_progress_toast(self, progress_percent, items_left):
        """Disembunyikan agar tidak muncul toast di kanan bawah saat impor."""
        pass

    @Slot(str)
    def on_batch_import_error(self, item_path, error_message):
        self._total_pending_imports -= 1
        if self._total_pending_imports < 0:
            self._total_pending_imports = 0
        self._update_aggregated_progress_toast()
        QMessageBox.warning(
            self,
            "Batch Import Error",
            f"Failed import '{os.path.basename(item_path)}':\n{error_message}",
        )

    @Slot(int)
    def _on_batch_import_complete(self, total_items_processed):
        """Dipanggil saat thread impor batch selesai."""
        completion_msg = language_config.ON_IMPORT_COMPLETE_STATUS
        self.show_toast_requested.emit(completion_msg, 3000, False)

        self.data_changed.emit()

    def retranslate_ui(self):
        """Translate bulk page layout and refresh visual themes."""
        for panel in self.active_batch_panels.values():
            if is_widget_alive(panel) and hasattr(panel, "retranslate_ui"):
                try:
                    panel.retranslate_ui()
                except Exception as e:
                    print(f"Error retranslating panel: {e}")
        if hasattr(self, "batch_list_view"):
            self.batch_list_view.viewport().update()
        self.update_theme()

    def update_theme(self):
        """Update stylesheets and themes for all child widgets dynamically."""
        for child in self.findChildren(QWidget):
            if hasattr(child, "update_theme") and child != self:
                try:
                    child.update_theme()
                except Exception as e:
                    pass
        if hasattr(self, "batch_list_view"):
            self.batch_delegate.refresh_button_styles()
            self.batch_list_view.viewport().update()
