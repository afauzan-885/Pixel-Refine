import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QCheckBox,
    QWidget,
    QMessageBox,
    QGridLayout,
    QSpinBox,
    QComboBox,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication

# Generic UI Library
from resources.GenericUILibrary import (
    DataTable,
    Button,
    ModalDialog,
    ProgressBar,
    get_store,
)
from resources.styles.stylesheet import (
    CHECKBOX_SWITCH_STYLE,
    PROGRESS_BAR,
    stylesheet_global_page,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.core.logic.batch_parameter_manager import (
    get_batch_algorithm_summary,
)
from pixel_refine_desktop.enhance_stack.core.logic.batch_processor import (
    BatchProcessingThread,
)


class MassAlgorithmEditDialog(QDialog):
    algorithms_updated = Signal()
class MassAlgorithmEditDialog(QDialog):
    algorithms_updated = Signal()

    def __init__(self, batches, parent=None):
        super().__init__(parent)
        self.batches = batches
        # Create mapping: index -> batch_id for range selection
        self.seq_to_batch_id = {i + 1: batch.id for i, batch in enumerate(self.batches)}
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import get_backend_arch
        _alignment_choices = [
            language_config.UI_NO_CHANGE,
            "ORB",
            "AKAZE",
            "Light Glue",
            "Farneback",
            "Lucas Kanade",
            "Block Matching GPU",
            "RAFT",
            "No Alignment",
        ]
        backend_arch = get_backend_arch()
        if backend_arch == "opengl":
            _alignment_choices = [
                c for c in _alignment_choices
                if c not in ("RAFT",)
            ]
        elif backend_arch == "cpu":
            _alignment_choices = [
                c for c in _alignment_choices if c not in ("RAFT",)
            ]

        self.algorithms = {
            "alignment": _alignment_choices,
            "super_resolution": [language_config.UI_NO_CHANGE, "No Super Resolution"],
            "denoising": [
                language_config.UI_NO_CHANGE,
                "Average",
                "Median",
                "Similarity",
                "Similarity Fusion",
                "No Denoising",
            ],
        }

    def populate_table(self):
        self.table_widget.clear_rows()
        self.table_widget.setRowCount(len(self.batches))

        for i, batch in enumerate(self.batches):
            # --- Kolom 0: Checkbox ---
            checkbox_widget = QWidget()
            chk_layout = QHBoxLayout(checkbox_widget)
            chk_box = QCheckBox()
            chk_box.setStyleSheet(CHECKBOX_SWITCH_STYLE)
            chk_box.setChecked(True)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table_widget.setCellWidget(i, 0, checkbox_widget)

            # --- Kolom 1: Project Name ---
            project_name_text = f"{batch.name} (ID: {batch.id})"
            item_name = QTableWidgetItem(project_name_text)
            item_name.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table_widget.setItem(i, 1, item_name)

            # --- Kolom 2: Status ---
            item_status = QTableWidgetItem(language_config.BATCH_QUEUE)
            item_status.setFlags(
                Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
            )
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(i, 2, item_status)

            # --- Kolom 3: Details ---
            algo_summary = self._get_algorithm_summary(batch.id)
            details_label = QLabel(algo_summary)
            details_label.setWordWrap(True)

            if algo_summary == language_config.UI_ALGORITHM_NOT_SET:
                details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                details_label.setAlignment(
                    Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
                )

            cell_widget = QWidget()
            cell_layout = QVBoxLayout(cell_widget)
            cell_layout.addWidget(details_label)
            cell_layout.setContentsMargins(5, 5, 5, 5)
            self.table_widget.setCellWidget(i, 3, cell_widget)

        self.table_widget.resize_columns_to_content(target_cols=[0])
        self.table_widget.resizeRowsToContents()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # DataTable handles some resizing, but we can force update if needed
        pass

    def on_batch_finished(self, row, success, result_message):
        status = "Success" if success else "Failed"
        color = self.COLOR_SUCCESS if success else self.COLOR_FAILED

        item = self.table_widget.item(row, 2)
        if item:
            item.setText(status)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self._update_details_cell(row, result_message)
        self.table_widget.set_row_color(row, color)

        self.table_widget.resizeRowsToContents()
        self.processed_count += 1

        num_total = len(self.panels_to_process_with_rows)
        overall_percent = (
            int((self.processed_count / num_total) * 100) if num_total > 0 else 0
        )
        self.progress_bar.setValue(overall_percent)
        self.progress_bar.setFormat(f"{overall_percent}%")

    def open_mass_edit_dialog(self):
        """Membuka dialog dan menghubungkan sinyalnya untuk update real-time."""
        if not self.batches:
            QMessageBox.information(
                self, "Info", language_config.UI_BATCH_NOT_CONFIGURE
            )
            return

        edit_dialog = MassAlgorithmEditDialog(self.batches, self)
        edit_dialog.algorithms_updated.connect(self.refresh_details_column)
        edit_dialog.exec()

    def refresh_details_column(self):
        """Mengupdate kolom 'Details' untuk semua baris."""
        for i in range(self.table_widget.rowCount()):
            # Safe check
            if i < len(self.batches):
                batch = self.batches[i]
                algo_summary = self._get_algorithm_summary(batch.id)
                self._update_details_cell(i, algo_summary)

        self.table_widget.resizeRowsToContents()

    def on_progress_update_from_thread(
        self, row, status, details, percent_in_batch, current_num, total_num
    ):
        """Update status baris yang sedang diproses."""
        item = self.table_widget.item(row, 2)
        if item:
            item.setText(status)

        self._update_details_cell(row, details)

        num_total_batches = len(self.panels_to_process_with_rows)
        overall_percent = (
            int(
                (
                    (self.processed_count + (percent_in_batch / 100.0))
                    / num_total_batches
                )
                * 100
            )
            if num_total_batches > 0
            else 0
        )
        self.progress_bar.setValue(overall_percent)
        self.progress_bar.setFormat(
            language_config.UI_LABEL_BATCH_PROGRESS.format(current_num, total_num)
        )
        self.table_widget.resizeRowToContents(row)

    def _update_details_cell(self, row, text):
        """Helper function untuk update teks di sel Details."""
        widget = self.table_widget.get_cell_widget(row, 3)
        if widget:
            label = widget.findChild(QLabel)
            if label:
                if text == language_config.UI_ALGORITHM_NOT_SET:
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    label.setAlignment(
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
                    )
                label.setText(text)

    def start_processing(self):
        self._was_cancelled = False
        target_folder = self.folder_path_edit.text()
        if not target_folder:
            QMessageBox.warning(self, "Warning", language_config.UI_FOLDER_PATH_NOT_SET)
            return

        self.panels_to_process_with_rows = []
        for i in range(self.table_widget.rowCount()):
            # Access checkbox from widget
            chk_widget = self.table_widget.get_cell_widget(i, 0)
            if chk_widget:
                checkbox = chk_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    if i < len(self.batches):
                        self.panels_to_process_with_rows.append((self.batches[i], i))

        if not self.panels_to_process_with_rows:
            QMessageBox.information(
                self, "Info", language_config.UI_LABEL_BATCH_NO_PROCESS
            )
            return

        # Prepare UI
        for batch, row in self.panels_to_process_with_rows:
            item = self.table_widget.item(row, 2)
            if item:
                item.setText(language_config.BATCH_QUEUE)

            algo_summary = self._get_algorithm_summary(batch.id)
            self._update_details_cell(row, algo_summary)
            self.table_widget.set_row_color(row, QColor(Qt.GlobalColor.transparent))

        self.start_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.edit_algo_button.setEnabled(False)
        self.close_button.setText(language_config.BATCH_CANCELED_PROCESS)
        try:
            self.close_button.clicked.disconnect()
        except Exception:
            pass  # Ignore if not connected
        self.close_button.clicked.connect(self.cancel_processing)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Starting...")
        self.processed_count = 0

        # Start Processing Thread from Logic Layer
        self.processing_thread = BatchProcessingThread(
            self.panels_to_process_with_rows, self.batch_page_layout, target_folder
        )

        # Connect batch context switching signal to handle in main thread
        self.processing_thread.batch_context_switch_requested.connect(
            self._handle_batch_context_switch
        )

        # Connect algorithm execution signal to run in main thread (avoid nested threads)
        self.processing_thread.execute_algorithm_requested.connect(
            self._handle_algorithm_execution
        )

        # Connect completion signal so worker thread knows when to continue
        self.processing_thread.algorithm_execution_completed.connect(
            lambda: setattr(self.processing_thread, "_algorithm_completed", True)
        )

        self.processing_thread.progress_update.connect(
            self.on_progress_update_from_thread
        )
        self.processing_thread.batch_finished.connect(self.on_batch_finished)
        self.processing_thread.processing_complete.connect(self.on_processing_complete)
        self.processing_thread.start()

    def cancel_processing(self):
        """Menampilkan dialog konfirmasi dan membatalkan proses."""
        if hasattr(self, "processing_thread") and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self,
                language_config.BATCH_CANCELED_PROCESS,
                language_config.BATCH_CANCELED_CONFIRMATION,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._was_cancelled = True

                # Stop the current algorithm processor if running
                if (
                    hasattr(self, "_current_algorithm_processor")
                    and self._current_algorithm_processor
                ):
                    self._current_algorithm_processor.stop()
                    self._current_algorithm_processor.wait(1000)  # Wait up to 1 second

                self.processing_thread.stop()
                self.processing_thread.wait()
                self.reset_dialog_state()
                QMessageBox.information(
                    self,
                    language_config.BATCH_CANCELED_INFO,
                    language_config.BATCH_CANCELED_BY_USER,
                )

    def reset_dialog_state(self):
        self.start_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.edit_algo_button.setEnabled(True)
        self.close_button.setText("Close")
        try:
            self.close_button.clicked.disconnect()
        except:
            pass
        self.close_button.clicked.connect(self.close)

        for i in range(self.table_widget.rowCount()):
            status_item = self.table_widget.item(i, 2)
            if not status_item:
                continue

            if status_item.text() == "Processing":
                status_item.setText(language_config.BATCH_CANCELED_INFO)
                self._update_details_cell(i, "")
                self.table_widget.set_row_color(i, self.COLOR_CANCELLED)

            elif status_item.text() == "Pending" and self._was_cancelled:
                status_item.setText(language_config.BATCH_CANCELED_INFO)
                self._update_details_cell(i, "")
                self.table_widget.set_row_color(i, self.COLOR_CANCELLED)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, language_config.SELECT_OUTPUT_FOLDER_TITLE
        )
        if folder:
            self.folder_path_edit.setText(folder)

    def on_processing_complete(self, failed_batches_summary):
        if not self._was_cancelled:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat(language_config.BATCH_SUCCESS_HEADER)
            QMessageBox.information(
                self,
                language_config.BATCH_SUCCESS_HEADER,
                language_config.BATCH_SUCCESS,
            )

        if failed_batches_summary:
            print("Failed batches:", failed_batches_summary)

        self.reset_dialog_state()

    def _handle_batch_context_switch(self, batch_id):
        """
        Handle batch context switching in the main thread.
        Called via signal from worker thread to avoid thread safety issues.
        """
        if (
            hasattr(self.batch_page_layout, "controller")
            and self.batch_page_layout.controller
        ):
            self.batch_page_layout.controller.handle_batch_selected(batch_id)

    def _handle_algorithm_execution(self, batch_id):
        """
        Execute algorithm processing in the main thread using AlgorithmProcessorThread.
        Called via signal from worker thread to avoid nested thread deadlock.

        CRITICAL: This runs in main thread, so algorithms can spawn their own
        worker threads (ThreadWorker, ImageProcessingMultiThreading) safely.

        NON-BLOCKING: Uses signal-based completion to keep UI responsive.

        Uses AlgorithmProcessorThread with:
        - batch_id: The specific batch to process
        - single_process=False: Use batch mode (reads images from batch_process_image table)
        """
        from pixel_refine_desktop.enhance_stack.core.logic.algorithm_processor import (
            AlgorithmProcessorThread,
        )
        from pixel_refine_desktop.enhance_stack.core.logic.batch_parameter_manager import (
            get_batch_algorithm_settings,
        )

        try:
            # Get algorithm settings for this specific batch
            settings = get_batch_algorithm_settings(batch_id)

            # Check if any algorithm is active
            has_active_algo = any(
                settings.get(key)
                not in [
                    None,
                    "None",
                    "No Alignment",
                    "No Super Resolution",
                    "No Denoising",
                ]
                for key in ["alignment", "super_resolution", "denoising"]
            )

            if not has_active_algo:
                print(f"[INFO] No active algorithms for batch_id: {batch_id}")
                # Signal completion even if no algorithms to run
                self.processing_thread.algorithm_execution_completed.emit()
                return

            # Create processor thread with correct batch settings
            # single_process=False means it will read images from batch_process_image table
            self._current_algorithm_processor = AlgorithmProcessorThread(
                batch_id=batch_id,
                settings=settings,
                parent=self.batch_page_layout,
                single_process=False,  # CRITICAL: False for batch mode!
            )

            # Connect finished signal to emit completion to BatchProcessingThread
            # This allows non-blocking execution while keeping UI responsive
            def on_algorithm_finished():
                # Clean up processor reference
                self._current_algorithm_processor = None
                # Signal completion to worker thread
                self.processing_thread.algorithm_execution_completed.emit()

            def on_algorithm_error(error_msg):
                print(f"[ERROR] Algorithm error: {error_msg}")
                # Clean up processor reference
                self._current_algorithm_processor = None
                # Still signal completion so batch processing can continue
                self.processing_thread.algorithm_execution_completed.emit()

            # Connect progress signal to update real-time progress
            def on_algorithm_progress(percent, message):
                self._on_algorithm_progress_update(batch_id, percent, message)

            self._current_algorithm_processor.progress_update.connect(
                on_algorithm_progress
            )
            self._current_algorithm_processor.finished_processing.connect(
                on_algorithm_finished
            )
            self._current_algorithm_processor.error_occurred.connect(on_algorithm_error)

            # Start thread NON-BLOCKING - no .wait()!
            # UI remains responsive while algorithm runs in background
            self._current_algorithm_processor.start()

        except Exception as e:
            error_msg = f"Error processing batch {batch_id}: {e}"
            print(f"[ERROR] {error_msg}")
            # Clean up processor reference
            if hasattr(self, "_current_algorithm_processor"):
                self._current_algorithm_processor = None
            # Always signal completion, even if there was an error
            self.processing_thread.algorithm_execution_completed.emit()

    def _on_algorithm_progress_update(self, batch_id, percent, message):
        """
        Handle real-time progress updates from AlgorithmProcessorThread.
        Updates both the table row for this batch and the overall progress bar.
        """
        # Find the row for this batch_id
        current_row = None
        current_batch_index = 0

        for i, (batch, row) in enumerate(self.panels_to_process_with_rows):
            if batch.id == batch_id:
                current_row = row
                current_batch_index = i
                break

        if current_row is None:
            return

        # Update status in table
        item = self.table_widget.item(current_row, 2)
        if item:
            item.setText("Processing")

        # Update details cell with progress message
        if message:
            self._update_details_cell(current_row, message)

        # Calculate overall progress
        # Overall = (completed batches + current batch progress) / total batches
        num_total_batches = len(self.panels_to_process_with_rows)
        if num_total_batches > 0:
            overall_percent = int(
                ((self.processed_count + (percent / 100.0)) / num_total_batches) * 100
            )
            self.progress_bar.setValue(overall_percent)
            self.progress_bar.setFormat(
                language_config.UI_LABEL_BATCH_PROGRESS.format(
                    current_batch_index + 1, num_total_batches
                )
            )

        # Resize row to fit content
        self.table_widget.resizeRowToContents(current_row)


from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import (
    BatchProcessDialog,
)
