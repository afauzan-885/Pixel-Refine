import json
import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QFileDialog,
    QCheckBox,
    QWidget,
    QMessageBox,
    QGridLayout,
    QSpinBox,
    QComboBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QGuiApplication
from resources.styles.stylesheet import (
    CHECKBOX_SWITCH_STYLE,
    PROGRESS_BAR,
    stylesheet_global_page,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config

def load_json_state(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default


def save_json_state(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


class MassAlgorithmEditDialog(QDialog):
    algorithms_updated = Signal()

    def __init__(self, panels, parent=None):
        super().__init__(parent)
        self.panels = panels
        self.seq_to_batch_id = {
            p.sequential_batch_number: p.batch_id for p in self.panels
        }
        self.algorithms = {
            "alignment": [
                language_config.UI_NO_CHANGE,
                "ORB",
                "AKAZE",
                "Light Glue",
                "Farneback",
                "Lucas Kanade",
                "Block Matching GPU",
                "RAFT",
                "No Alignment",
            ],
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
        self.json_path = os.path.join("database", "align", "batch_parameter.json")
        self.setWindowTitle(language_config.UI_ALGORITHM_EDIT_HEADER)

        screen = QGuiApplication.primaryScreen()
        if screen:
            available_rect = screen.availableGeometry()
            screen_width = available_rect.width()
            screen_height = available_rect.height()

            dialog_width = int(screen_width * 0.15)
            dialog_height = int(screen_height * 0.25)

            dialog_width = max(dialog_width, 150)
            dialog_height = max(dialog_height, 250)
            self.resize(dialog_width, dialog_height)
        else:
            self.setMinimumSize(150, 250)

        self.initUI()
        self.setStyleSheet(stylesheet_global_page())

    def initUI(self):
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        range_layout = QHBoxLayout()
        from_label = QLabel("From:")
        self.from_spinbox = QSpinBox()
        to_label = QLabel("To:")
        self.to_spinbox = QSpinBox()
        range_layout.addWidget(from_label)
        range_layout.addWidget(self.from_spinbox)
        range_layout.addSpacing(20)
        range_layout.addWidget(to_label)
        range_layout.addWidget(self.to_spinbox)
        range_layout.addStretch()
        grid_layout.addLayout(range_layout, 1, 0, 1, 2)
        if self.seq_to_batch_id:
            min_seq, max_seq = min(self.seq_to_batch_id.keys()), max(
                self.seq_to_batch_id.keys()
            )
            self.from_spinbox.setRange(min_seq, max_seq)
            self.to_spinbox.setRange(min_seq, max_seq)
            self.from_spinbox.setValue(min_seq)
            self.to_spinbox.setValue(max_seq)
        
        self.align_checkbox = QCheckBox("Alignment:")
        self.align_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
        self.align_combo = QComboBox()
        self.align_combo.addItems(self.algorithms["alignment"])
        grid_layout.addWidget(self.align_checkbox, 2, 0)
        grid_layout.addWidget(self.align_combo, 2, 1)

        self.sr_checkbox = QCheckBox("Super Resolution:")
        self.sr_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
        self.sr_combo = QComboBox()
        self.sr_combo.addItems(self.algorithms["super_resolution"])
        grid_layout.addWidget(self.sr_checkbox, 3, 0)
        grid_layout.addWidget(self.sr_combo, 3, 1)

        self.denoise_checkbox = QCheckBox("Denoising:")
        self.denoise_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
        self.denoise_combo = QComboBox()
        self.denoise_combo.addItems(self.algorithms["denoising"])
        grid_layout.addWidget(self.denoise_checkbox, 4, 0)
        grid_layout.addWidget(self.denoise_combo, 4, 1)

        layout.addLayout(grid_layout)

        btn_box = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        cancel_btn = QPushButton("Cancel")
        btn_box.addStretch()
        btn_box.addWidget(apply_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

        apply_btn.clicked.connect(self.apply_changes)
        cancel_btn.clicked.connect(self.reject)

    def apply_changes(self):
        start_seq = self.from_spinbox.value()
        end_seq = self.to_spinbox.value()

        if start_seq > end_seq:
            QMessageBox.warning(self, "Warning", "Start batch number must be <= end batch number.")
            return

        all_params = load_json_state(self.json_path)

        for seq, batch_id in self.seq_to_batch_id.items():
            if start_seq <= seq <= end_seq:
                batch_params = all_params.get(str(batch_id), {})

                if self.align_checkbox.isChecked():
                    align_val = self.align_combo.currentText()
                    if align_val != language_config.UI_NO_CHANGE:
                        batch_params["checkbox_align_images"] = (align_val != "No Alignment")
                        batch_params["alignment_algo"] = align_val

                if self.sr_checkbox.isChecked():
                    sr_val = self.sr_combo.currentText()
                    if sr_val != language_config.UI_NO_CHANGE:
                        batch_params["checkbox_super_resolution"] = (sr_val != "No Super Resolution")
                        batch_params["super_resolution_algo"] = sr_val

                if self.denoise_checkbox.isChecked():
                    denoise_val = self.denoise_combo.currentText()
                    if denoise_val != language_config.UI_NO_CHANGE:
                        batch_params["checkbox_denoising"] = (denoise_val != "No Denoising")
                        batch_params["denoising_algo"] = denoise_val

                all_params[str(batch_id)] = batch_params

        save_json_state(self.json_path, all_params)
        QMessageBox.information(
            self,
            language_config.BATCH_SUCCESS_HEADER,
            language_config.ALGORITHM_SUCCESS_UPDATE.format(start_seq, end_seq),
        )
        self.algorithms_updated.emit()
        self.accept()


class ProcessingThread(QThread):
    progress_update = Signal(int, str, str, int, int, int)
    batch_finished = Signal(int, bool, str)
    processing_complete = Signal(list)

    def __init__(self, panels_to_process, batch_page_layout, target_folder):
        super().__init__()
        self.panels_to_process = panels_to_process
        self.batch_page_layout = batch_page_layout
        self.target_folder = target_folder
        self._is_running = True

    def run(self):
        failed_batches_summary = []
        total_batches_to_process = len(self.panels_to_process)

        for i, (panel, row) in enumerate(self.panels_to_process):
            if not self._is_running:
                break

            seq_num = getattr(panel, "sequential_batch_number", "?")
            batch_id = getattr(panel, "batch_id", "UNKNOWN")

            try:
                def sub_process_progress_callback(*args):
                    if not self._is_running:
                        return
                    percent = 0
                    message = ""
                    current_num_for_ui = i + 1

                    if len(args) == 3:
                        current, total, message = args
                        percent = int((current / total) * 100) if total > 0 else 0
                    elif len(args) == 2:
                        percent, message = args
                    else:
                        return

                    self.progress_update.emit(
                        row,
                        "Processing",
                        message,
                        percent,
                        current_num_for_ui,
                        total_batches_to_process,
                    )

                files_before = set(self.batch_page_layout.get_files_in_stack_folder())
                panel.process_all_batch(progress_callback=sub_process_progress_callback)
                files_after = set(self.batch_page_layout.get_files_in_stack_folder())
                new_files = list(files_after - files_before)

                if new_files:
                    output_file = new_files[0]
                    move_success = self.batch_page_layout._move_single_batch_result(
                        output_file, self.target_folder
                    )
                    if move_success:
                        self.batch_finished.emit(row, True, "Success: Saved")
                    else:
                        self.batch_finished.emit(
                            row, False, "Error: Failed to move result."
                        )
                else:
                    self.batch_finished.emit(
                        row, False, "Error: No output file generated."
                    )

            except Exception as e:
                error_detail = str(e)
                failed_summary = {"seq": seq_num, "id": batch_id, "error": error_detail}
                failed_batches_summary.append(failed_summary)
                self.batch_finished.emit(row, False, f"Failed: {error_detail[:100]}...")

        self.processing_complete.emit(failed_batches_summary)

    def stop(self):
        self._is_running = False


class BatchProcessDialog(QDialog):
    def __init__(self, panels_to_process, batch_page_layout, parent=None):
        super().__init__(parent)
        self.panels = panels_to_process
        self.batch_page_layout = batch_page_layout
        self.database_manager = self.batch_page_layout.database_manager

        self.COLOR_SUCCESS = QColor("#D4EDDA")
        self.COLOR_FAILED = QColor("#F8D7DA")
        self.COLOR_CANCELLED = QColor("#D9E44C")

        self._was_cancelled = False
        self.setWindowTitle(language_config.UI_BATCH_HEADER)
        self.setMinimumSize(650, 450)
        self.initUI()
        self.populate_table()
        self.setStyleSheet(stylesheet_global_page())

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        folder_layout = QHBoxLayout()
        folder_label = QLabel(language_config.ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER)
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setReadOnly(True)
        self.browse_button = QPushButton(
            language_config.SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER
        )
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(self.browse_button)
        layout.addLayout(folder_layout)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(
            ["", "Project Name", "Status", "Details"]
        )
        self.table_widget.verticalHeader().setVisible(True)
        layout.addWidget(self.table_widget)

        progress_layout = QHBoxLayout()
        progress_label = QLabel(language_config.OVERALL_PROGRESS)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(PROGRESS_BAR)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)

        button_layout = QHBoxLayout()
        self.edit_algo_button = QPushButton(language_config.UI_ALGORIHM_EDIT)
        button_layout.addWidget(self.edit_algo_button)
        button_layout.addStretch()
        self.start_button = QPushButton(
            language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT
        )
        self.close_button = QPushButton(language_config.CLOSE_BUTTON)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.close_button)
        self.start_button.setObjectName("startButton")
        layout.addLayout(button_layout)

        self.browse_button.clicked.connect(self.browse_output_folder)
        self.start_button.clicked.connect(self.start_processing)
        self.close_button.clicked.connect(self.close)
        self.edit_algo_button.clicked.connect(self.open_mass_edit_dialog)

    def _set_row_color(self, row, color):
        color_name = color.name() if color != Qt.transparent else "transparent"
        for col in range(self.table_widget.columnCount()):
            item = self.table_widget.item(row, col)
            if item:
                item.setBackground(color)
            widget = self.table_widget.cellWidget(row, col)
            if widget:
                widget.setStyleSheet(f"background-color: {color_name};")
                label = widget.findChild(QLabel)
                if label:
                    label.setStyleSheet(f"background-color: {color_name};")

    def _get_algorithm_summary(self, batch_id):
        json_path = os.path.join("database", "align", "batch_parameter.json")
        all_params = load_json_state(json_path)
        batch_params = all_params.get(str(batch_id), {})
        active_algos = []

        if batch_params.get("checkbox_align_images", False):
            algo = batch_params.get("alignment_algo", "None")
            if algo not in ["None", "No Alignment"]:
                active_algos.append(algo)
        if batch_params.get("checkbox_super_resolution", False):
            algo = batch_params.get("super_resolution_algo", "None")
            if algo not in ["None", "No Super Resolution"]:
                active_algos.append(algo)
        if batch_params.get("checkbox_denoising", False):
            algo = batch_params.get("denoising_algo", "None")
            if algo not in ["None", "No Denoising"]:
                active_algos.append(algo)

        return (
            ", ".join(active_algos)
            if active_algos
            else language_config.UI_ALGORITHM_NOT_SET
        )

    def populate_table(self):
        self.table_widget.setRowCount(len(self.panels))
        for i, panel in enumerate(self.panels):
            checkbox_widget = QWidget()
            chk_layout = QHBoxLayout(checkbox_widget)
            chk_box = QCheckBox()
            chk_box.setStyleSheet(CHECKBOX_SWITCH_STYLE)
            chk_box.setChecked(True)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table_widget.setCellWidget(i, 0, checkbox_widget)

            project_name_text = (
                f"Batch {panel.sequential_batch_number} ({str(panel.batch_id)[:8]}...)"
            )
            item_name = QTableWidgetItem(project_name_text)
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_widget.setItem(i, 1, item_name)

            item_status = QTableWidgetItem(language_config.BATCH_QUEUE)
            item_status.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(i, 2, item_status)

            algo_summary = self._get_algorithm_summary(panel.batch_id)
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

        self.table_widget.setVerticalHeaderLabels(
            [str(i + 1) for i in range(len(self.panels))]
        )
        self.adjust_column_widths()
        self.table_widget.resizeRowsToContents()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_column_widths()

    def on_batch_finished(self, row, success, result_message):
        status = "Success" if success else "Failed"
        color = self.COLOR_SUCCESS if success else self.COLOR_FAILED

        self.table_widget.item(row, 2).setText(status)
        self.table_widget.item(row, 2).setTextAlignment(Qt.AlignCenter)
        self._update_details_cell(row, result_message)
        self._set_row_color(row, color)
        self.table_widget.resizeRowsToContents()
        self.processed_count += 1

        num_total = len(self.panels_to_process_with_rows)
        overall_percent = (
            int((self.processed_count / num_total) * 100) if num_total > 0 else 0
        )
        self.progress_bar.setValue(overall_percent)
        self.progress_bar.setFormat(f"{overall_percent}%")

        if self.processed_count == num_total and not self._was_cancelled:
            self.on_processing_complete([])

    def refresh_details_column(self):
        for i in range(self.table_widget.rowCount()):
            panel = self.panels[i]
            algo_summary = self._get_algorithm_summary(panel.batch_id)
            self._update_details_cell(i, algo_summary)
        self.table_widget.resizeRowsToContents()

    def on_progress_update_from_thread(
        self, row, status, details, percent_in_batch, current_num, total_num
    ):
        self.table_widget.item(row, 2).setText(status)
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
        widget = self.table_widget.cellWidget(row, 3)
        if widget:
            label = widget.findChild(QLabel)
            if label:
                if text == language_config.UI_ALGORITHM_NOT_SET:
                     label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                     label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                label.setText(text)

    def start_processing(self):
        self._was_cancelled = False
        target_folder = self.folder_path_edit.text()
        if not target_folder:
            QMessageBox.warning(self, "Warning", language_config.UI_FOLDER_PATH_NOT_SET)
            return

        self.panels_to_process_with_rows = []
        for i in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(i, 0).findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                self.panels_to_process_with_rows.append((self.panels[i], i))

        if not self.panels_to_process_with_rows:
            QMessageBox.information(
                self, "Info", language_config.UI_LABEL_BATCH_NO_PROCESS
            )
            return

        for panel, row in self.panels_to_process_with_rows:
            self.table_widget.item(row, 2).setText(language_config.BATCH_QUEUE)
            algo_summary = self._get_algorithm_summary(panel.batch_id)
            self._update_details_cell(row, algo_summary)
            self._set_row_color(row, Qt.transparent)

        self.start_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.edit_algo_button.setEnabled(False)
        self.close_button.setText(language_config.BATCH_CANCELED_PROCESS)
        self.close_button.clicked.disconnect()
        self.close_button.clicked.connect(self.cancel_processing)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Starting...")
        self.processed_count = 0

        self.processing_thread = ProcessingThread(
            self.panels_to_process_with_rows, self.batch_page_layout, target_folder
        )
        self.processing_thread.progress_update.connect(
            self.on_progress_update_from_thread
        )
        self.processing_thread.batch_finished.connect(self.on_batch_finished)
        self.processing_thread.processing_complete.connect(self.on_processing_complete)
        self.processing_thread.start()

    def cancel_processing(self):
        if hasattr(self, "processing_thread") and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self,
                language_config.BATCH_CANCELED_PROCESS,
                language_config.BATCH_CANCELED_CONFIRMATION,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._was_cancelled = True
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
        self.close_button.clicked.disconnect()
        self.close_button.clicked.connect(self.close)

        for i in range(self.table_widget.rowCount()):
            status_item = self.table_widget.item(i, 2)
            if not status_item:
                continue

            if status_item.text() == "Processing":
                status_item.setText(language_config.BATCH_CANCELED_INFO)
                self._update_details_cell(i, "")
                self._set_row_color(i, self.COLOR_CANCELLED)

            elif status_item.text() == "Pending" and self._was_cancelled:
                status_item.setText(language_config.BATCH_CANCELED_INFO)
                self._update_details_cell(i, "")
                self._set_row_color(i, self.COLOR_CANCELLED)

    def adjust_column_widths(self):
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        available_width = (
            self.table_widget.viewport().width()
            - header.sectionSize(0)
            - header.sectionSize(2)
        )
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        self.table_widget.setColumnWidth(1, int(available_width * (1 / 4)))
        self.table_widget.setColumnWidth(3, int(available_width * (3 / 4)))

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, language_config.SELECT_OUTPUT_FOLDER_TITLE
        )
        if folder:
            self.folder_path_edit.setText(folder)

    def open_mass_edit_dialog(self):
        if not self.panels:
            QMessageBox.information(
                self, "Info", language_config.BATCH_CONFIGURATION_INFO
            )
            return

        edit_dialog = MassAlgorithmEditDialog(self.panels, self)
        result = edit_dialog.exec_()
        if result == QDialog.Accepted:
            self.refresh_details_column()

    def on_processing_complete(self, failed_batches_summary):
        if not self._was_cancelled:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat(language_config.BATCH_SUCCESS_HEADER)
            QMessageBox.information(
                self,
                language_config.BATCH_SUCCESS_HEADER,
                language_config.BATCH_SUCCESS,
            )
        print("Failed batches:", failed_batches_summary)
        self.reset_dialog_state()
