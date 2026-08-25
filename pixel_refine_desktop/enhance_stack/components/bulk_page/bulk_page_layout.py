import json
import os
import shutil
import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QFileDialog,
    QGraphicsOpacityEffect,
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
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_import_service import (
    BulkDeleteProcess,
    process_and_start_batch_import,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_thumbnail_service import (
    stop_process_thumbnails,
)
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_policy import (
    ThumbnailPolicy,
    thumbnail_creation_enabled,
)

from resources.GenericUILibrary import ScrollContainer, live_update


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

            json_path = os.path.join("database", "align", "batch_parameter.json")
            state = {}
            if os.path.exists(json_path):
                try:
                    all_saved = load_json_state(json_path)
                    state = all_saved.get(str(self.batch_id), {})
                except Exception:
                    state = {}

            self.batch_prepared.emit(self.batch_id, state, valid_paths)
        except Exception as e:
            print(f"[ERROR] BatchPreloaderThread error for batch {self.batch_id}: {e}")
            self.batch_prepared.emit(self.batch_id, {}, [])


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
            vh = self.viewport().height()
            content_h = inner.layout().sizeHint().height()
            inner.setMinimumHeight(max(vh, content_h))


def setup_main_panel(layout_instance, scroll_area_style):
    """Creates the main panel scroll container utilizing GenericUILibrary ScrollContainer."""
    scroll_area = BulkBatchScrollContainer()
    scroll_area.setObjectName("MainBatchScrollArea")

    main_panel = scroll_area.container
    main_panel.setObjectName("BulkMainPanel")

    layout_instance.setContentsMargins(16, 16, 16, 16)
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
from config import CACHE_DIR, SUPPORTED_FORMATS


def load_json_state(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def is_widget_valid(widget):
    """Cek apakah widget masih valid (belum dihapus)."""
    if widget is None:
        return False
    try:
        _ = widget.isVisible()  # akses properti sederhana
        return True
    except RuntimeError:
        return False
    except Exception:
        return False


def safe_hide_widget(widget):
    """Sembunyikan widget jika masih valid, tangani error jika sudah dihapus."""
    if not is_widget_valid(widget):
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

        self.data_changed.connect(self.update_batch_view)

        # Hook scroll listener for lazy loading (Task 4)
        self.limit = 10
        self.load_timer_running = False
        self._thumbnail_batch_queue = []
        self._is_thumbnail_queue_running = False
        self.main_scroll_area.verticalScrollBar().valueChanged.connect(
            self._on_scroll_changed
        )

        self.layout.addWidget(self.main_scroll_area)

    def _on_scroll_changed(self, value):
        scroll_bar = self.main_scroll_area.verticalScrollBar()
        if scroll_bar.maximum() > 0 and value > scroll_bar.maximum() * 0.8:
            db_ids = self.database_manager.get_all_batch_ids()
            if self.limit < len(db_ids):
                self.limit += 10
                self.update_batch_view()

    def _load_next_batch_incrementally(self):
        from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
            is_widget_alive,
        )

        if not self.loading_queue:
            self.load_timer_running = False
            return

        batch_id = self.loading_queue.pop(0)
        skeleton = self.active_skeletons.pop(batch_id, None)

        # Offload DB & JSON state parsing to background worker thread
        preloader = BatchPreloaderThread(self.database_manager, batch_id, parent=self)

        def on_preloaded(b_id, pre_state, valid_paths):
            new_panel = self.setup_combined_panel(
                b_id, preloaded_state=pre_state, preloaded_image_paths=valid_paths
            )

            # Replace skeleton in layout
            if skeleton and is_widget_alive(skeleton):
                idx = self.main_panel_container.indexOf(skeleton)
                if idx != -1:
                    self.main_panel_container.removeWidget(skeleton)
                    skeleton.hide()
                    skeleton.deleteLater()
                    self.main_panel_container.insertWidget(idx, new_panel)
                else:
                    self.main_panel_container.addWidget(new_panel)
            else:
                if self._spacer_item:
                    self.main_panel_container.insertWidget(
                        self.main_panel_container.count() - 1, new_panel
                    )
                else:
                    self.main_panel_container.addWidget(new_panel)

            self._start_fade_in_animation(new_panel)
            self._reorder_visual_batch_numbers()
            self._manage_placeholder_and_spacer()
            if hasattr(self.main_scroll_area, "update_inner_dimensions"):
                self.main_scroll_area.update_inner_dimensions()

            # Schedule next batch preloader asynchronously with 500ms breathing room interval
            QTimer.singleShot(100, self._load_next_batch_incrementally)

        preloader.batch_prepared.connect(on_preloaded)
        preloader.start()
        if not hasattr(self, "_active_preloaders"):
            self._active_preloaders = []
        self._active_preloaders.append(preloader)

    def refresh_after_project_load(self):
        """Discard legacy UI caches and rebuild from the active session DB."""
        self.stop_thumbnail()
        for panel in list(self.active_batch_panels.values()):
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
        self.batch_states.clear()
        self.loading_queue.clear()
        self.limit = 10
        self.update_batch_view()

    def update_batch_view(self):
        """
        Memperbarui tampilan daftar batch secara cerdas dengan lazy loading dan skeleton loader.
        """
        # 1. Dapatkan state dari database dan UI
        db_ids = self.database_manager.get_all_batch_ids()
        if not hasattr(self, "limit"):
            self.limit = 10
        visible_db_ids = db_ids[: self.limit]
        ui_ids = set(self.active_batch_panels.keys())

        # 2. Identifikasi batch yang perlu dihapus dari UI
        # Termasuk batch yang sudah tidak ada di DB (cache stale eviction)
        db_ids_set = set(db_ids)
        ids_to_remove = ui_ids - set(visible_db_ids)
        for batch_id in ids_to_remove:
            panel_to_remove = self.active_batch_panels.pop(batch_id, None)
            if panel_to_remove:
                self.batch_states.pop(batch_id, None)

                # Hapus widget dari layout SECARA LANGSUNG
                self.main_panel_container.removeWidget(panel_to_remove)
                # Sembunyikan widget agar tidak terlihat sesaat sebelum benar-benar dihapus
                panel_to_remove.hide()
                # Jadwalkan penghapusan memori widget
                panel_to_remove.deleteLater()

            # Jika batch sudah tidak ada di DB sama sekali, hapus dari cache juga
            if batch_id not in db_ids_set:
                stale = self._panel_cache.pop(batch_id, None)
                if stale and stale is not panel_to_remove:
                    try:
                        stale.deleteLater()
                    except RuntimeError:
                        pass

        # Remove skeletons that are no longer in visible list
        for bid in list(self.active_skeletons.keys()):
            if bid not in visible_db_ids:
                skel = self.active_skeletons.pop(bid, None)
                if skel:
                    self.main_panel_container.removeWidget(skel)
                    skel.hide()
                    skel.deleteLater()

        # 3. Identifikasi batch yang perlu ditambahkan ke UI
        ids_to_add = [
            bid
            for bid in visible_db_ids
            if bid not in ui_ids and bid not in self.active_skeletons
        ]
        if ids_to_add:
            for bid, panel in list(self.active_batch_panels.items()):
                try:
                    if panel:
                        self.batch_states[bid] = panel.get_current_state()
                except Exception:
                    pass

        for batch_id in ids_to_add:

            # --- CACHE HIT: Reuse panel yang sudah pernah dibuat ---
            cached_panel = self._panel_cache.get(batch_id)
            if cached_panel is not None:
                try:
                    _ = cached_panel.isVisible()  # cek masih hidup
                    # Panel valid: re-insert ke layout dan tampilkan langsung
                    if self._spacer_item:
                        insert_idx = self.main_panel_container.count() - 1
                        self.main_panel_container.insertWidget(insert_idx, cached_panel)
                    else:
                        self.main_panel_container.addWidget(cached_panel)
                    cached_panel.show()
                    self.active_batch_panels[batch_id] = cached_panel
                    self._reorder_visual_batch_numbers()
                    self._manage_placeholder_and_spacer()
                    continue  # langsung ke batch_id berikutnya, tanpa skeleton
                except RuntimeError:
                    # Panel sudah dihancurkan, hapus dari cache
                    self._panel_cache.pop(batch_id, None)

            # --- CACHE MISS: Buat skeleton dulu, lalu load panel asli ---
            skeleton = SkeletonCombinedPanel(self)
            self.active_skeletons[batch_id] = skeleton

            # Tambahkan skeleton ke layout. Jika ada spacer, tambahkan sebelum spacer.
            if self._spacer_item:
                self.main_panel_container.insertWidget(
                    self.main_panel_container.count() - 1, skeleton
                )
            else:
                self.main_panel_container.addWidget(skeleton)

            self.loading_queue.append(batch_id)

        # Trigger incremental loading timer tanpa delay (langsung mulai render)
        if self.loading_queue and not self.load_timer_running:
            self.load_timer_running = True
            QTimer.singleShot(0, self._load_next_batch_incrementally)

        # 4. Atur ulang nomor urut visual untuk semua panel yang ada
        self._reorder_visual_batch_numbers()

        # 5. Kelola tampilan placeholder atau spacer
        self._manage_placeholder_and_spacer()

    def _reorder_visual_batch_numbers(self):
        """Mengatur ulang label nomor urut (Batch #1, Batch #2, dst.) pada semua panel."""
        # Ambil semua widget CombinedPanel yang ada di layout
        panels_in_layout = []
        for i in range(self.main_panel_container.count()):
            widget = self.main_panel_container.itemAt(i).widget()
            # Pastikan itu adalah instance dari CombinedPanel
            if widget and isinstance(widget, CombinedPanel):
                panels_in_layout.append(widget)

        # Update nomor urut berdasarkan posisi mereka di layout
        for index, panel in enumerate(panels_in_layout):
            panel.update_sequential_number(index + 1)

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

        # Enqueue untuk pemuatan thumbnail sekuensial per batch
        self._enqueue_thumbnail_loading(combined_panel)
        return combined_panel

    def _enqueue_thumbnail_loading(self, panel):
        """Tambahkan panel ke dalam antrean pemuatan thumbnail sekuensial."""
        if not thumbnail_creation_enabled(self.thumbnail_policy):
            return

        if not hasattr(self, "_thumbnail_batch_queue"):
            self._thumbnail_batch_queue = []
        if panel not in self._thumbnail_batch_queue:
            self._thumbnail_batch_queue.append(panel)
        self._process_thumbnail_queue()

    def _process_thumbnail_queue(self):
        """Proses antrean thumbnail secara sekuensial per batch (1 batch 100% baru lanjut ke batch berikutnya)."""
        if not thumbnail_creation_enabled(self.thumbnail_policy):
            self._thumbnail_batch_queue.clear()
            self._is_thumbnail_queue_running = False
            return

        if getattr(self, "_is_thumbnail_queue_running", False):
            return
        if not getattr(self, "_thumbnail_batch_queue", None):
            return

        self._is_thumbnail_queue_running = True
        next_panel = self._thumbnail_batch_queue.pop(0)

        from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
            is_widget_alive,
        )

        if is_widget_alive(next_panel):
            next_panel.delay_thumbnails(
                completion_callback=self._on_batch_thumbnail_completed
            )
        else:
            self._on_batch_thumbnail_completed()

    @Slot(bool)
    def _on_thumbnail_policy_changed(self, enabled):
        if enabled:
            return

        self._thumbnail_batch_queue.clear()
        self._is_thumbnail_queue_running = False
        # Cancel workers but keep the visible panels in place.  The regular
        # stop_thumbnail() path also hides/caches panels for mode switching,
        # which is not appropriate for a settings toggle.
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

    def _on_batch_thumbnail_completed(self):
        """Dipanggil ketika satu batch selesai memuat thumbnail 100% atau setelah 6 detik inactivity watchdog."""
        self._is_thumbnail_queue_running = False
        QTimer.singleShot(10, self._process_thumbnail_queue)

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
            self.main_scroll_area.setStyleSheet(
                self._original_scroll_stylesheet
                + " QScrollArea#MainBatchScrollArea { border: 2px dashed #4CAF50; }"
            )
        else:
            event.ignore()
        return True

    def _handle_drag_leave(self, event):
        if self.main_scroll_area.property("acceptingDrop"):
            self.main_scroll_area.setProperty("acceptingDrop", False)
            self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet)
        event.accept()
        return True

    def _handle_drag_move(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
        return True

    def _handle_drop(self, event):
        if self.main_scroll_area.property("acceptingDrop"):
            self.main_scroll_area.setProperty("acceptingDrop", False)
            self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            supported_extensions = {
                ext for fmts in SUPPORTED_FORMATS.values() for ext in fmts
            }
            valid_image_paths = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.isLocalFile()
                and os.path.isfile(url.toLocalFile())
                and os.path.splitext(url.toLocalFile())[1].lower()
                in supported_extensions
            ]
            if valid_image_paths:
                process_and_start_batch_import(self, valid_image_paths)
            return True
        event.ignore()
        return True

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
        # Bagian 1: Mengumpulkan dan memvalidasi panel yang akan diproses (sama seperti sebelumnya)
        active_panels_list = list(self.active_batch_panels.values())
        active_panels = []
        for panel in active_panels_list:
            try:
                if (
                    panel
                    and hasattr(panel, "isWidgetType")
                    and panel.isWidgetType()
                    and (
                        not hasattr(self, "animator")
                        or not hasattr(self.animator, "_active_fade_outs")
                        or panel not in self.animator._active_fade_outs
                    )
                ):
                    active_panels.append(panel)
            except RuntimeError:
                print(f"RuntimeError: Panel {panel} has been deleted.")
            except Exception as e:
                print(f"Unexpected error while filtering panel {panel}: {e}")

        candidate_panels = []
        for panel in active_panels:
            if (
                hasattr(panel, "batch_id")
                and panel.batch_id is not None
                and hasattr(panel, "sequential_batch_number")
            ):
                candidate_panels.append(panel)

        if not candidate_panels:
            self.show_toast_requested.emit(
                language_config.UI_LABEL_BATCH_NO_PROCESS, 4000, False
            )
            return

        # Bagian 2: Validasi akhir terhadap database (sama seperti sebelumnya)
        panels_to_actually_process = []
        for panel_candidate in candidate_panels:
            try:
                batch_id_to_check = str(panel_candidate.batch_id)
                images_in_db_for_panel = self.database_manager.get_images_by_batch(
                    batch_id_to_check
                )
                if images_in_db_for_panel:
                    panels_to_actually_process.append(panel_candidate)
            except Exception as db_val_e:
                print(
                    f"Error validating batch {panel_candidate.batch_id} against DB: {db_val_e}"
                )

        if not panels_to_actually_process:
            self.show_toast_requested.emit(
                language_config.UI_LABEL_BATCH_NO_PROCESS + " (after DB validation).",
                4000,
                False,
            )
            return

        # Bagian 3: Buat dan tampilkan dialog baru
        # Alih-alih melanjutkan pemrosesan di sini, kita panggil dialog.
        # Kita meneruskan 'self' (instance BatchPageLayout) agar dialog dapat mengakses
        # fungsi-fungsi helper seperti _move_single_batch_result dan get_files_in_stack_folder
        # Kita bungkus panel ke dalam class pembantu yang memaparkan properti name dan id (kompatibel dengan batch v2)
        class BatchWrapper:
            def __init__(self, panel):
                self.original_panel = panel
                self.id = panel.batch_id
                self.batch_id = panel.batch_id
                self.sequential_batch_number = getattr(
                    panel, "sequential_batch_number", 1
                )
                self.name = f"Batch {self.sequential_batch_number}"

            def process_all_batch(self, *args, **kwargs):
                return self.original_panel.process_all_batch(*args, **kwargs)

        batches_wrapper = [BatchWrapper(panel) for panel in panels_to_actually_process]
        dialog = BatchProcessDialog(batches_wrapper, self, self)
        dialog.exec_()

    def _move_single_batch_result(self, source_file_path, target_folder):
        """
        Memindahkan file hasil ke folder target, hanya menggunakan nama file asli.
        Jika file dengan nama yang sama sudah ada, tambahkan akhiran "_1", "_2", dst.
        """
        if not source_file_path or not os.path.exists(source_file_path):
            print(language_config.SOURCE_FILE_DOES_NOT_EXIST.format(source_file_path))
            return False

        if not target_folder or not os.path.isdir(target_folder):
            print(language_config.TARGET_FOLDER_INVALID.format(target_folder))
            QMessageBox.critical(
                self,
                language_config.BATCH_SAVE_ERROR_TITLE,
                language_config.TARGET_FOLDER_NOT_ACCESSIBLE.format(target_folder),
            )
            return False

        original_file_name = os.path.basename(source_file_path)
        destination_path = os.path.join(target_folder, original_file_name)

        try:
            # Jika file tujuan sudah ada, cari nama baru yang tersedia.
            if os.path.exists(destination_path):
                base, ext = os.path.splitext(original_file_name)
                counter = 1
                while os.path.exists(destination_path):
                    new_file_name = f"{base}_{counter}{ext}"
                    destination_path = os.path.join(target_folder, new_file_name)
                    counter += 1

            # Pindahkan file setelah nama tujuan yang valid ditemukan
            shutil.move(source_file_path, destination_path)

            print(
                language_config.LOG_MOVE_SUCCESS.format(
                    original_file_name, destination_path
                )
            )
            return True

        except Exception as e:
            error_detail_msg = str(e)
            print(
                language_config.LOG_MOVE_FAILED.format(
                    original_file_name, target_folder, error_detail_msg
                )
            )
            QMessageBox.warning(
                self,
                language_config.MOVE_FILE_ERROR_TITLE,
                language_config.COULD_NOT_SAVE_FILE_FOR_BATCH.format(
                    original_file_name, error=error_detail_msg
                ),
            )
            return False

    def handle_delete_individual_batch(self, batch_id):
        panel_to_delete = self.active_batch_panels.get(batch_id)
        panel_ref = weakref.ref(panel_to_delete) if panel_to_delete else None

        if not panel_to_delete:
            return

        title, message = language_config.BATCH_DELETE_LABEL
        message = message.format(batch_id)
        from resources.GenericUILibrary import modal_confirm

        reply = modal_confirm.question(self, message)

        if reply:
            if batch_id in self.batch_states:
                del self.batch_states[batch_id]

            fade_out(
                animator=self.animator,
                widget=panel_to_delete,
                duration=300,
                on_finished_callback=lambda bid=batch_id, pref=panel_ref: self._individual_delete_post_animation(
                    bid, pref
                ),
            )

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
        from resources.GenericUILibrary import modal_confirm

        reply = modal_confirm.question(self, message)

        if reply:
            self.batch_states.clear()
            panels_to_animate = list(self.active_batch_panels.values())
            panel_refs = [weakref.ref(p) for p in panels_to_animate]

            if not panels_to_animate:
                self._start_bulk_background_delete_process()
                return

            self._bulk_delete_animation_counter = len(panels_to_animate)
            delay_ms = 10

            for index, panel_ref in enumerate(panel_refs):
                QTimer.singleShot(
                    index * delay_ms,
                    lambda pref=panel_ref: self._trigger_single_bulk_fade_out(pref),
                )

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
        if is_widget_valid(panel):
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
        stop_process_thumbnails(self.thumbnail_threads)

        # Clear incremental loading queue
        self.loading_queue.clear()
        self.load_timer_running = False

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
            if is_widget_valid(panel) and hasattr(panel, "retranslate_ui"):
                try:
                    panel.retranslate_ui()
                except Exception as e:
                    print(f"Error retranslating panel: {e}")
        self.update_theme()

    def update_theme(self):
        """Update stylesheets and themes for all child widgets dynamically."""
        for child in self.findChildren(QWidget):
            if hasattr(child, "update_theme") and child != self:
                try:
                    child.update_theme()
                except Exception as e:
                    pass
