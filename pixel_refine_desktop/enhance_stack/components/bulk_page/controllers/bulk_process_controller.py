import json
import os
import time
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
            getattr(p, "sequential_batch_number", i + 1): getattr(p, "batch_id", getattr(p, "id", i + 1))
            for i, p in enumerate(self.panels)
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


from resources.GenericUILibrary import (
    ModalDialog,
    ProgressBar,
    Button,
)


class BatchProcessDialog(ModalDialog):
    def __init__(self, panels_to_process, batch_page_layout, parent=None):
        super().__init__(
            message="",
            parent=parent,
            title=getattr(language_config, "UI_BATCH_HEADER", "Batch Processing Manager"),
            close_on_click_outside=False,
            width=780,
            height=560,
        )
        self.panels = panels_to_process
        self.batch_page_layout = batch_page_layout
        self.database_manager = self.batch_page_layout.database_manager

        self.COLOR_SUCCESS = QColor("#D1FAE5")
        self.COLOR_FAILED = QColor("#FEE2E2")
        self.COLOR_CANCELLED = QColor("#FEF3C7")

        self._was_cancelled = False
        self._is_processing = False
        self._start_time = None

        self.initUI()
        self.populate_table()

    def initUI(self):
        container_layout = self.container.layout()

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 1. Folder Output Selection Row
        folder_layout = QHBoxLayout()
        folder_label = QLabel(language_config.ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER)
        folder_label.setStyleSheet("font-family: 'Segoe UI', Arial; font-size: 12px; color: #334155; font-weight: 600;")

        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setReadOnly(True)
        self.folder_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
                color: #1E293B;
            }
        """)

        self.browse_button = Button(
            language_config.SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER, variant="secondary"
        )
        self.browse_button.setFixedHeight(30)
        self.browse_button.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                border: 1px solid #CBD5E1;
                background-color: #F8FAFC;
                color: #334155;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path_edit, 1)
        folder_layout.addWidget(self.browse_button)
        layout.addLayout(folder_layout)

        # 2. Table Widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(
            ["", "Project Name", "Status", "Details"]
        )
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                gridline-color: #F1F5F9;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #475569;
                font-weight: 600;
                font-size: 12px;
                border: none;
                border-bottom: 1px solid #CBD5E1;
                padding: 6px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #E0F2FE;
                color: #0369A1;
            }
        """)
        layout.addWidget(self.table_widget, 1)

        # 3. Translucent Gray Card Container for Progress Bar & Real-time ETA
        self.progress_container = QWidget()
        self.progress_container.setObjectName("ProgressCardContainer")
        self.progress_container.setStyleSheet("""
            QWidget#ProgressCardContainer {
                background-color: rgba(241, 245, 249, 0.85);
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }
        """)
        prog_card_layout = QVBoxLayout(self.progress_container)
        prog_card_layout.setContentsMargins(12, 10, 12, 10)
        prog_card_layout.setSpacing(6)

        # Top row: Percentage (Top Left) & ETA (Top Right)
        prog_top_layout = QHBoxLayout()
        self.progress_percent_label = QLabel("Overall Progress: 0%")
        self.progress_percent_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 12px; font-weight: 700; color: #1E293B;"
        )
        self.eta_label = QLabel("ETA: --:--")
        self.eta_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 11.5px; font-weight: 600; color: #64748B;"
        )

        prog_top_layout.addWidget(self.progress_percent_label)
        prog_top_layout.addStretch()
        prog_top_layout.addWidget(self.eta_label)
        prog_card_layout.addLayout(prog_top_layout)

        # Middle row: Animated Progress Bar
        self.progress_bar = ProgressBar(style="animated", variant="primary", show_label=False)
        prog_card_layout.addWidget(self.progress_bar)

        # Bottom row: Detail status text (e.g. 2/9 batches processed...)
        self.progress_detail_label = QLabel("Ready to process")
        self.progress_detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_detail_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 11px; color: #475569; font-weight: 500;"
        )
        prog_card_layout.addWidget(self.progress_detail_label)

        layout.addWidget(self.progress_container)

        # 4. Action Buttons Row (Single Switch Action Button: Start <-> Cancel)
        button_layout = QHBoxLayout()
        self.edit_algo_button = Button(language_config.UI_ALGORIHM_EDIT, variant="secondary")
        self.edit_algo_button.setStyleSheet("""
            QPushButton {
                font-size: 11.5px;
                padding: 5px 14px;
                border: 1px solid #CBD5E1;
                background-color: #F1F5F9;
                color: #334155;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        button_layout.addWidget(self.edit_algo_button)
        button_layout.addStretch()

        # Single Switch Action Button (Start Process <-> Cancel Process)
        self.action_button = Button(
            language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT, variant="primary"
        )
        self.action_button.setObjectName("actionButton")
        self._apply_start_button_style()

        self.close_button = Button(language_config.CLOSE_BUTTON, variant="secondary")
        self.close_button.setStyleSheet("""
            QPushButton {
                font-size: 11.5px;
                padding: 6px 16px;
                border: 1px solid #CBD5E1;
                background-color: #FFFFFF;
                color: #475569;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)

        button_layout.addWidget(self.action_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        container_layout.addWidget(content_widget, 1)

        self.browse_button.clicked.connect(self.browse_output_folder)
        self.action_button.clicked.connect(self._on_action_button_clicked)
        self.close_button.clicked.connect(self.close)
        self.edit_algo_button.clicked.connect(self.open_mass_edit_dialog)

    def _apply_start_button_style(self):
        """Applies Emerald Green style to single action button."""
        self.action_button.setText(language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT)
        self.action_button.setStyleSheet("""
            QPushButton#actionButton {
                background-color: #10B981;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 12px;
                padding: 7px 22px;
                border-radius: 6px;
                border: none;
            }
            QPushButton#actionButton:hover {
                background-color: #059669;
            }
            QPushButton#actionButton:pressed {
                background-color: #047857;
            }
        """)

    def _apply_cancel_button_style(self):
        """Applies Crimson Red style to single action button when running."""
        self.action_button.setText(language_config.BATCH_CANCELED_PROCESS)
        self.action_button.setStyleSheet("""
            QPushButton#actionButton {
                background-color: #EF4444;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 12px;
                padding: 7px 22px;
                border-radius: 6px;
                border: none;
            }
            QPushButton#actionButton:hover {
                background-color: #DC2626;
            }
            QPushButton#actionButton:pressed {
                background-color: #B91C1C;
            }
        """)

    def _on_action_button_clicked(self):
        """Toggle behavior for single switch action button."""
        if not self._is_processing:
            self.start_processing()
        else:
            self.cancel_processing()

    def open_mass_edit_dialog(self):
        dialog = MassAlgorithmEditDialog(self.panels, self)
        dialog.algorithms_updated.connect(self.on_algorithms_updated)
        dialog.exec_()

    def on_algorithms_updated(self):
        for i, panel in enumerate(self.panels):
            batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
            algo_summary = self._get_algorithm_summary(batch_id)
            self._update_details_cell(i, algo_summary)
        self.table_widget.resizeRowsToContents()

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

            batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
            seq_num = getattr(panel, "sequential_batch_number", getattr(panel, "name", f"Batch {i+1}"))
            if isinstance(seq_num, str) and seq_num.startswith("Batch "):
                project_name_text = f"{seq_num} ({str(batch_id)[:8]}...)"
            else:
                project_name_text = f"Batch {seq_num} ({str(batch_id)[:8]}...)"

            item_name = QTableWidgetItem(project_name_text)
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_widget.setItem(i, 1, item_name)

            item_status = QTableWidgetItem(language_config.BATCH_QUEUE)
            item_status.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(i, 2, item_status)

            algo_summary = self._get_algorithm_summary(batch_id)
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
        self._update_progress_and_eta(overall_percent, f"{self.processed_count}/{num_total} batches processed...")

    def on_processing_complete(self, failed_batches_summary):
        self.reset_dialog_state()
        self._update_progress_and_eta(100, "Batch processing complete!")
        self.eta_label.setText("ETA: Completed")

        if failed_batches_summary:
            print(f"Failed batches: {failed_batches_summary}")
        else:
            print("Batch processing completed successfully!")

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

        detail_msg = f"{current_num}/{total_num} batches processed... ({details})"
        self._update_progress_and_eta(overall_percent, detail_msg)
        self.table_widget.resizeRowToContents(row)

    def _update_progress_and_eta(self, percent, detail_msg=""):
        """Calculates real-time ETA and updates UI progress labels."""
        self.progress_bar.setValue(percent)
        self.progress_percent_label.setText(f"Overall Progress: {percent}%")
        if detail_msg:
            self.progress_detail_label.setText(detail_msg)

        # Calculate Real-Time ETA
        if self._start_time and percent > 0 and percent < 100:
            elapsed = time.time() - self._start_time
            est_total = (elapsed / percent) * 100
            remaining = max(0, int(est_total - elapsed))
            mins, secs = divmod(remaining, 60)
            self.eta_label.setText(f"ETA: {mins:02d}:{secs:02d}")
        elif percent >= 100:
            self.eta_label.setText("ETA: 00:00")
        else:
            self.eta_label.setText("ETA: Estimating...")

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
            batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
            algo_summary = self._get_algorithm_summary(batch_id)
            self._update_details_cell(row, algo_summary)
            self._set_row_color(row, Qt.transparent)

        self._is_processing = True
        self._start_time = time.time()

        # Switch action button to Crimson Red Cancel Process
        self._apply_cancel_button_style()
        self.browse_button.setEnabled(False)
        self.edit_algo_button.setEnabled(False)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self._update_progress_and_eta(0, "Starting batch process...")
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
            from resources.GenericUILibrary import modal_confirm
            reply = modal_confirm.question(
                self,
                language_config.BATCH_CANCELED_CONFIRMATION,
            )
            if reply:
                self._was_cancelled = True
                self.processing_thread.stop()
                self.processing_thread.wait()
                self.reset_dialog_state()

    def reset_dialog_state(self):
        self._is_processing = False
        self._start_time = None

        # Switch action button back to Emerald Green Start Process
        self._apply_start_button_style()
        self.browse_button.setEnabled(True)
        self.edit_algo_button.setEnabled(True)

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

            seq_num = getattr(panel, "sequential_batch_number", getattr(panel, "name", "?"))
            batch_id = getattr(panel, "batch_id", getattr(panel, "id", "UNKNOWN"))

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
                target_panel = getattr(panel, "original_panel", panel)
                target_panel.process_all_batch(progress_callback=sub_process_progress_callback)
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
