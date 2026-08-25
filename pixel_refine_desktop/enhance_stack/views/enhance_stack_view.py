"""
Enhanced Stack Page View (MVC Refactored).
Main container for single and batch page views with controller integration.
Subclass of WorkspaceView from workplace framework.
"""

from PySide6.QtCore import QThread, QTimer, Signal, QObject, Slot, Qt
from PySide6.QtGui import QKeySequence, QShortcut, QIcon, QPixmap
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget, QMenu, QProgressDialog, QLabel
from resources.GenericUILibrary import Button, Modal
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.core.logic.project_archive import (
    load_project,
    recent_projects,
    session_has_data,
    session_state_token,
    save_project,
)
import os
import config
from pixel_refine_desktop.workplace.workspace_view import WorkspaceView
from .single_page_view import SinglePageView
from .batch_page_view import BatchPageView


class _ProjectSaveWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, path, database_path, active_batch_id=None):
        super().__init__()
        self.path = path
        self.database_path = database_path
        self.active_batch_id = active_batch_id

    @Slot()
    def run(self):
        try:
            self.finished.emit(
                save_project(
                    self.path,
                    self.database_path,
                    active_batch_id=self.active_batch_id,
                    page="enhance_stack",
                )
            )
        except Exception as exc:
            self.failed.emit(str(exc))


class EnhanceStackView(WorkspaceView):
    """
    Main view for enhance stack feature (MVC Architecture).
    Subclass of WorkspaceView - implementasi spesifik enhance_stack.
    """

    page_changed = Signal(int)  # Forward global navigation

    def __init__(self, db_path: str, parent=None):
        # WorkspaceView.__init__ akan memanggil _create_pages() dan _connect_page_signals()
        self.batch_page_view = None
        self._batch_placeholder = None
        self._batch_signals_connected = False
        self._current_project_path = None
        self._project_baseline_token = None
        self._save_thread = None
        self._save_worker = None
        self._save_dialog = None
        super().__init__(db_path, parent)
        self._save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self._save_shortcut.activated.connect(self._save_project)
        QTimer.singleShot(750, self.preload_batch_page)

    def setup_ui(self):
        """Add a compact project text control without changing page geometry."""
        super().setup_ui()

    def _active_display_panel(self):
        page = self.stacked_widget.currentWidget()
        candidates = [
            getattr(page, "workspace_panel", None),
            getattr(getattr(page, "batch_layout", None), "workspace_panel", None),
        ]
        for candidate in candidates:
            panel = getattr(candidate, "display_panel", None)
            if panel is not None:
                return panel
        return None

    def _populate_project_menu(self):
        self.project_menu.clear()
        save_action = self.project_menu.addAction(
            getattr(language_config, "PROJECT_SAVE", "Save Project")
        )
        save_action.triggered.connect(self._save_project)
        save_as_action = self.project_menu.addAction(
            getattr(language_config, "PROJECT_SAVE_AS", "Save Project As...")
        )
        save_as_action.triggered.connect(self._save_project_as)
        open_action = self.project_menu.addAction(
            getattr(language_config, "PROJECT_OPEN", "Open Project...")
        )
        open_action.triggered.connect(self._open_project)
        recent_menu = self.project_menu.addMenu(
            getattr(language_config, "PROJECT_RECENT", "Recent Projects")
        )
        paths = recent_projects()
        if paths:
            for path in paths:
                action = recent_menu.addAction(os.path.basename(path))
                action.setToolTip(path)
                action.triggered.connect(
                    lambda checked=False, value=path: self._open_project(value)
                )
        else:
            empty = recent_menu.addAction("(None)")
            empty.setEnabled(False)
        self.project_menu.addSeparator()
        about_action = self.project_menu.addAction(
            getattr(language_config, "PROJECT_ABOUT", "About Pixel Refine")
        )
        about_action.triggered.connect(self._show_about_project)

    def _save_project(self, blocking=False):
        if self._save_thread is not None and self._save_thread.isRunning():
            return False
        if self._current_project_path:
            try:
                if blocking:
                    self._write_project(self._current_project_path)
                    return True
                return self._start_background_save(self._current_project_path)
            except Exception as exc:
                QMessageBox.critical(self, "Project Error", str(exc))
                return False
        return self._save_project_as(blocking=blocking)

    def _save_project_as(self, blocking=False):
        path, _ = QFileDialog.getSaveFileName(
            self,
            getattr(language_config, "PROJECT_SAVE_AS", "Save Project As..."),
            "pixel project.prf",
            "Pixel Refine Project (*.prf)",
        )
        if path:
            try:
                if blocking:
                    self._write_project(path)
                    return True
                return self._start_background_save(path)
            except Exception as exc:
                QMessageBox.critical(self, "Project Error", str(exc))
        return False

    def _start_background_save(self, path):
        self._save_dialog = QProgressDialog("Saving project...", None, 0, 0, self)
        self._save_dialog.setWindowTitle("Save Project")
        self._save_dialog.setCancelButton(None)
        self._save_dialog.setMinimumDuration(0)
        self._save_dialog.setAutoClose(False)
        self._save_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._save_dialog.show()

        self._save_thread = QThread(self)
        panel = self._active_display_panel()
        active_batch_id = getattr(panel, "current_batch_id", None)
        self._save_worker = _ProjectSaveWorker(path, self.db_path, active_batch_id)
        self._save_worker.moveToThread(self._save_thread)
        self._save_thread.started.connect(self._save_worker.run)
        self._save_worker.finished.connect(self._on_background_save_finished)
        self._save_worker.failed.connect(self._on_background_save_failed)
        self._save_worker.finished.connect(self._save_thread.quit)
        self._save_worker.failed.connect(self._save_thread.quit)
        self._save_worker.finished.connect(self._save_worker.deleteLater)
        self._save_worker.failed.connect(self._save_worker.deleteLater)
        self._save_thread.finished.connect(self._save_thread.deleteLater)
        self._save_thread.start()
        return True

    def _finish_save_dialog(self):
        if self._save_dialog is not None:
            self._save_dialog.close()
            self._save_dialog.deleteLater()
            self._save_dialog = None

    @Slot(object)
    def _on_background_save_finished(self, manifest):
        self._current_project_path = manifest["path"]
        self._project_baseline_token = session_state_token(self.db_path)
        self._finish_save_dialog()
        self._save_thread = None
        self._save_worker = None

    @Slot(str)
    def _on_background_save_failed(self, message):
        self._finish_save_dialog()
        self._save_thread = None
        self._save_worker = None
        QMessageBox.critical(self, "Project Error", message)

    def _write_project(self, path):
        panel = self._active_display_panel()
        manifest = save_project(
            path,
            self.db_path,
            active_batch_id=getattr(panel, "current_batch_id", None),
            page="enhance_stack",
        )
        self._current_project_path = manifest["path"]
        self._project_baseline_token = session_state_token(self.db_path)

    def _open_project(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self,
                getattr(language_config, "PROJECT_OPEN", "Open Project..."),
                "",
                "Pixel Refine Project (*.prf)",
            )
        if not path:
            return
        try:
            result = load_project(path, self.db_path, replace=True)
            self._current_project_path = result["path"]
            panel = self._active_display_panel()
            right_panel = getattr(panel, "right_panel", None) if panel else None
            if right_panel:
                refresh = getattr(right_panel, "refresh_after_project_load", None)
                if refresh:
                    refresh()
                else:
                    right_panel._load_batches()
            if self.batch_page_view is not None:
                legacy_refresh = getattr(
                    self.batch_page_view.batch_layout,
                    "refresh_after_project_load",
                    None,
                )
                if legacy_refresh:
                    legacy_refresh()
            active_id = result.get("active_batch_id")
            restored = False
            if active_id is not None and right_panel:
                # Use the normal selection route so the right-panel state,
                # parameter store, header, and preview stay synchronized.
                right_panel.list_group.blockSignals(True)
                try:
                    restored = right_panel.list_group.select_item_by_value(active_id)
                finally:
                    right_panel.list_group.blockSignals(False)
                if restored:
                    right_panel.selection_handler.handle_selection([active_id])
            if not restored and active_id is not None and panel and panel.controller:
                # Defensive fallback for legacy/custom panels without a list group.
                batch = panel.controller.get_batch(active_id)
                if batch:
                    panel.load_batch(
                        active_id, [image.path for image in batch.images], batch.name
                    )
                    restored = True
            if not restored and panel:
                if right_panel and hasattr(right_panel, "list_group"):
                    if hasattr(right_panel.list_group, "clear_selection"):
                        right_panel.list_group.clear_selection()
                    else:
                        right_panel.list_group.clearSelection()
                panel.clear_display()
            # Selection restoration can normalize persisted settings; capture
            # the clean baseline only after that synchronization is complete.
            self._project_baseline_token = session_state_token(self.db_path)
            self._show_project_loaded_modal(result)
        except Exception as exc:
            QMessageBox.critical(self, "Project Error", str(exc))
            return False
        return True

    def _show_project_loaded_modal(self, result):
        """Show the standard GenericUILibrary success modal after project load."""
        project_name = os.path.basename(self._current_project_path or "project.prf")
        batch_map = result.get("batch_id_map", {}) if isinstance(result, dict) else {}
        batch_count = len(batch_map) if isinstance(batch_map, dict) else 0

        modal = Modal(
            title="",
            size="small",
            parent=self,
        )

        # Gunakan title-bar sebagai satu-satunya header agar tidak ada judul
        # besar yang terduplikasi di dalam isi modal.
        modal.header.hide()
        modal.setWindowTitle(f"Berhasil memuat {project_name}")

        # Padatkan layout khusus modal informasi ini agar tidak menyisakan
        # ruang vertikal kosong yang berlebihan.
        modal.body.layout.setContentsMargins(15, 5, 15, 5)
        modal.footer.layout().setContentsMargins(15, 4, 15, 7)

        message = QLabel(f"Berhasil memuat {batch_count} batch")
        message.setWordWrap(True)
        message_font = message.font()
        base_point_size = message_font.pointSizeF()
        if base_point_size <= 0:
            base_point_size = 10.0
        message_font.setPointSizeF(base_point_size + 2.0)
        message.setFont(message_font)
        modal.set_body(message)
        modal.add_footer_button("OK", variant="primary")
        modal.fit_to_content(max_width=420, max_height=180)
        modal.exec()

    def project_has_unsaved_changes(self) -> bool:
        """Return whether the current session differs from its saved baseline."""
        if self._project_baseline_token is None:
            return session_has_data(self.db_path)
        return session_state_token(self.db_path) != self._project_baseline_token

    def _show_about_project(self):
        self._show_about_with_logo(
            self,
            getattr(language_config, "PROJECT_ABOUT", "About Pixel Refine"),
            f"Pixel Refine\nVersion {getattr(config, 'APP_VERSION', 'unknown')}\n\n"
            "Created by: afauzan-885 / Pixel Refine Team\n"
            "Development period: 2024–2026",
        )

    def retranslate_ui(self):
        # Project actions are hosted by the active page's hamburger control.
        return None

    def _show_about_with_logo(self, parent, title, message):
        """Show About using the canonical Pixel Refine logo asset."""
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(title)
        logo_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "resources", "assets", "images", "Logo_Pixel_Refine.png",
            )
        )
        if os.path.isfile(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                dialog.setIconPixmap(
                    pixmap.scaled(
                        72, 72,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                dialog.setWindowIcon(QIcon(logo_path))
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()

    def _create_pages(self):
        """Buat halaman-halaman enhance_stack dan tambahkan ke stacked_widget."""
        # Create single page view (hybrid MVC)
        self.single_page_view = SinglePageView(self.db_path, self)
        self.stacked_widget.addWidget(self.single_page_view)

        # Bulk/legacy batch page is heavier than the default page, so startup
        # only reserves its stack slot and loads it after the window is usable.
        self._batch_placeholder = QWidget(self)
        self.stacked_widget.addWidget(self._batch_placeholder)

    def _set_initial_page(self):
        """Set halaman awal ke single page view."""
        self.stacked_widget.setCurrentWidget(self.single_page_view)

    def _connect_page_signals(self):
        """Connect page signals and toast notifications."""
        # Connect Navigation
        self.single_page_view.page_changed.connect(self.page_changed)
        # Connect Bulk Mode toggles between V2 (SinglePageView) and V1 (BatchPageView)
        if (
            hasattr(self.single_page_view, "workspace_panel")
            and self.single_page_view.workspace_panel
        ):
            dp = self.single_page_view.workspace_panel.display_panel
            if hasattr(dp, "bulk_mode_btn"):
                dp.bulk_mode_btn.clicked.connect(self._on_v2_bulk_clicked)

        self._connect_batch_page_signals()

    def preload_batch_page(self):
        """Warm up the legacy bulk page after the main window becomes usable."""
        self._ensure_batch_page()

    def _ensure_batch_page(self):
        """Create the legacy bulk page once and replace the reserved placeholder."""
        if self.batch_page_view is not None:
            return self.batch_page_view

        self.batch_page_view = BatchPageView(self.db_path, self)
        placeholder_index = self.stacked_widget.indexOf(self._batch_placeholder)
        if placeholder_index >= 0:
            self.stacked_widget.insertWidget(placeholder_index, self.batch_page_view)
            self.stacked_widget.removeWidget(self._batch_placeholder)
            self._batch_placeholder.deleteLater()
            self._batch_placeholder = None
        else:
            self.stacked_widget.addWidget(self.batch_page_view)

        self._connect_batch_page_signals()
        return self.batch_page_view

    def _connect_batch_page_signals(self):
        if self._batch_signals_connected or self.batch_page_view is None:
            return

        self.batch_page_view.page_changed.connect(self.page_changed)
        self.batch_page_view.bulk_mode_toggled.connect(self._on_legacy_bulk_toggled)
        if hasattr(self.batch_page_view, "batch_layout"):
            if hasattr(self.batch_page_view.batch_layout, "show_toast_requested"):
                self.batch_page_view.batch_layout.show_toast_requested.connect(
                    self._handle_legacy_toast
                )
        self._batch_signals_connected = True

    def _on_v2_bulk_clicked(self):
        if (
            hasattr(self.single_page_view, "workspace_panel")
            and self.single_page_view.workspace_panel
        ):
            dp = self.single_page_view.workspace_panel.display_panel
            dp.is_bulk_mode = not dp.is_bulk_mode
            dp.set_mode_button_state(dp.is_bulk_mode)
            self._on_v2_bulk_toggled(dp.is_bulk_mode)

    def _on_v2_bulk_toggled(self, checked):
        if checked:
            batch_page = self._ensure_batch_page()
            # Direct switch avoids QPainter conflicts while the thumbnail/grid
            # pages are still repainting.
            self.animator.stop_all()
            self.stacked_widget.setCurrentWidget(batch_page)
            # Synchronize batches: refresh V1
            if hasattr(batch_page, "batch_layout"):
                batch_page.batch_layout.data_changed.emit()

    def _on_legacy_bulk_toggled(self, checked):
        if not checked:
            self.animator.stop_all()
            self.stacked_widget.setCurrentWidget(self.single_page_view)

            # Defer/stop V1 thumbnail generation and reset lazy load limit immediately (Task 4)
            if self.batch_page_view is not None and hasattr(
                self.batch_page_view, "batch_layout"
            ):
                self.batch_page_view.batch_layout.stop_thumbnail()
                self.batch_page_view.batch_layout.limit = 10

            # Synchronize batches: refresh V2
            if (
                hasattr(self.single_page_view, "batch_panel")
                and self.single_page_view.batch_panel
            ):
                self.single_page_view.batch_panel._load_batches()
            # Synchronize switch on V2 header
            if (
                hasattr(self.single_page_view, "workspace_panel")
                and self.single_page_view.workspace_panel
            ):
                dp = self.single_page_view.workspace_panel.display_panel
                dp.is_bulk_mode = False
                dp.set_mode_button_state(False)

        # Single page buttons
        # self.top_bar.single_page_import_button.clicked.connect(
        #     self.single_page_view.handle_import_button
        # )
        # self.top_bar.single_page_delete_button.clicked.connect(
        #     self.single_page_view.handle_delete_button
        # )

        # Batch page buttons
        # self.top_bar.batch_page_import_button.clicked.connect(
        #     self.batch_page_view.handle_batch_import_button
        # )
        # self.top_bar.batch_page_delete_button.clicked.connect(
        #     self.batch_page_view.handle_delete_all_batches

        # Single page buttons
        # self.top_bar.single_page_import_button.clicked.connect(
        #     self.single_page_view.handle_import_button
        # )
        # self.top_bar.single_page_delete_button.clicked.connect(
        #     self.single_page_view.handle_delete_button
        # )

        # Batch page buttons
        # self.top_bar.batch_page_import_button.clicked.connect(
        #     self.batch_page_view.handle_batch_import_button
        # )
        # self.top_bar.batch_page_delete_button.clicked.connect(
        #     self.batch_page_view.handle_delete_all_batches
        # )

    def _handle_legacy_toast(self, message, duration_or_category, is_progress):
        """Handle legacy toast notifications from BatchPageLayout V1."""
        if is_progress:
            category = (
                duration_or_category
                if isinstance(duration_or_category, str)
                else "legacy_batch_progress"
            )
            self.toast_manager.show_progress(message, category=category)
        else:
            duration = (
                duration_or_category if isinstance(duration_or_category, int) else 3000
            )
            try:
                self.toast_manager.hide_progress()
            except Exception:
                pass
            self.toast_manager.show_message(message, duration=duration)
