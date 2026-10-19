import json
import os
import threading
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_names, get_spec, plan_stages
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_result_service import (
    batch_selections, copy_result, expected_output_names, find_existing_outputs,
    returned_output_paths, usable_output,
)
import config
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_eta import BatchEtaEstimator
from PySide6.QtWidgets import (
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
    QComboBox,
    QMenu,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal, QPoint, QEvent, QTimer
from PySide6.QtGui import QColor, QGuiApplication, QKeySequence, QShortcut
from resources.styles.stylesheet import (
    CHECKBOX_SWITCH_STYLE,
    PROGRESS_BAR,
    stylesheet_global_page,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.core.logic.batch_parameter_manager import (
    load_json_state,
)
from UILibrary import (
    ModalDialog,
    ProgressBar,
    Button,
    NumericStepper,
)
from UILibrary.forms import apply_numeric_spinbox_style


def save_json_state(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def _parse_bulk_progress(*args, **kwargs):
    """Normalize legacy positional and resident UI/console progress callbacks."""
    if len(args) >= 3:
        current, total, message = args[:3]
        percent = int((current / total) * 100) if total else 0
    elif len(args) >= 2:
        percent, message = args[:2]
    elif args:
        percent = args[0]
        message = kwargs.get("ui", kwargs.get("message", ""))
        if not message:
            message = kwargs.get("console", "")
    else:
        percent = kwargs.get("percent", 0)
        message = kwargs.get("ui", kwargs.get("message", kwargs.get("console", "")))

    try:
        percent = int(percent)
    except (TypeError, ValueError):
        percent = 0
    return percent, str(message or "")


class MassAlgorithmEditDialog(ModalDialog):
    algorithms_updated = Signal()

    def __init__(self, panels, parent=None):
        super().__init__(
            message="",
            parent=parent,
            title=getattr(
                language_config, "UI_ALGORITHM_EDIT_HEADER", "Bulk Edit Algorithm"
            ),
            close_on_click_outside=False,
            width=440,
            height=300,
        )
        self.panels = panels
        self.seq_to_batch_id = {
            getattr(p, "sequential_batch_number", i + 1): getattr(
                p, "batch_id", getattr(p, "id", i + 1)
            )
            for i, p in enumerate(self.panels)
        }
        self.algorithms = {
            category: [language_config.UI_NO_CHANGE, *get_names(category, context="bulk_edit")]
            for category in ("alignment", "super_resolution", "denoising")
        }
        self.json_path = os.path.join("database", "align", "batch_parameter.json")
        self.initUI()
        self.setStyleSheet(stylesheet_global_page())

    def initUI(self):
        container_layout = self.container.layout()

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        range_layout = QHBoxLayout()
        from_label = QLabel("From:")
        from_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 12px; font-weight: 600; color: #334155;"
        )
        self.from_spinbox = NumericStepper()
        self.from_spinbox.setAccelerated(True)
        self.from_spinbox.setFixedWidth(128)
        apply_numeric_spinbox_style(self.from_spinbox)
        to_label = QLabel("To:")
        to_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 12px; font-weight: 600; color: #334155;"
        )
        self.to_spinbox = NumericStepper()
        self.to_spinbox.setAccelerated(True)
        self.to_spinbox.setFixedWidth(128)
        apply_numeric_spinbox_style(self.to_spinbox)

        range_layout.addWidget(from_label)
        range_layout.addWidget(self.from_spinbox)
        range_layout.addSpacing(15)
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
        apply_btn = Button("Apply", variant="primary")
        cancel_btn = Button("Cancel", variant="secondary")
        btn_box.addStretch()
        btn_box.addWidget(apply_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

        container_layout.addWidget(content_widget, 1)

        apply_btn.clicked.connect(self.apply_changes)
        cancel_btn.clicked.connect(self.reject)

    def apply_changes(self):
        start_seq = self.from_spinbox.value()
        end_seq = self.to_spinbox.value()

        if start_seq > end_seq:
            QMessageBox.warning(
                self, "Warning", "Start batch number must be <= end batch number."
            )
            return

        all_params = load_json_state(self.json_path)

        for seq, batch_id in self.seq_to_batch_id.items():
            if start_seq <= seq <= end_seq:
                batch_params = all_params.get(str(batch_id), {})

                if self.align_checkbox.isChecked():
                    align_val = self.align_combo.currentText()
                    if align_val != language_config.UI_NO_CHANGE:
                        batch_params["checkbox_align_images"] = (
                            align_val != "No Alignment"
                        )
                        batch_params["alignment_algo"] = align_val

                if self.sr_checkbox.isChecked():
                    sr_val = self.sr_combo.currentText()
                    if sr_val != language_config.UI_NO_CHANGE:
                        batch_params["checkbox_super_resolution"] = (
                            sr_val != "No Super Resolution"
                        )
                        batch_params["super_resolution_algo"] = sr_val

                if self.denoise_checkbox.isChecked():
                    denoise_val = self.denoise_combo.currentText()
                    if denoise_val != language_config.UI_NO_CHANGE:
                        batch_params["checkbox_denoising"] = (
                            denoise_val != "No Denoising"
                        )
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


class MasterHeaderView(QHeaderView):
    master_checkbox_toggled = Signal()
    context_menu_requested = Signal(object)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.master_checkbox = QCheckBox(self)
        self.master_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
        self.master_checkbox.setToolTip("Check All / Uncheck All")
        self.master_checkbox.clicked.connect(self._on_master_clicked)

        # Connect custom context menu directly on the master checkbox button
        self.master_checkbox.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.master_checkbox.customContextMenuRequested.connect(
            self._on_chk_context_menu
        )

        self.setSectionsClickable(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _on_master_clicked(self):
        self.master_checkbox_toggled.emit()

    def _on_context_menu(self, pos):
        global_pos = self.mapToGlobal(pos)
        self.context_menu_requested.emit(global_pos)

    def _on_chk_context_menu(self, pos):
        global_pos = self.master_checkbox.mapToGlobal(pos)
        self.context_menu_requested.emit(global_pos)

    def update_checkbox_geometry(self):
        sec_size = self.sectionSize(0)
        chk_size = self.master_checkbox.sizeHint()
        x = self.sectionPosition(0) + (sec_size - chk_size.width()) // 2
        y = (self.height() - chk_size.height()) // 2
        self.master_checkbox.move(max(2, x), max(2, y))
        self.master_checkbox.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_checkbox_geometry()

    def paintEvent(self, event):
        super().paintEvent(event)
        self.update_checkbox_geometry()


class BatchProcessDialog(ModalDialog):
    def __init__(self, panels_to_process, batch_page_layout, parent=None):
        super().__init__(
            message="",
            parent=parent,
            title=getattr(
                language_config, "UI_BATCH_HEADER", "Batch Processing Manager"
            ),
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
        self._last_toggled_row = None
        self._eta = None
        self._close_after_processing = False
        self._eta_timer = QTimer(self)
        self._eta_timer.setInterval(1000)
        self._eta_timer.timeout.connect(self._refresh_eta)

        self.initUI()
        self.populate_table()
        QTimer.singleShot(0, self.adjust_column_widths)

    def initUI(self):
        container_layout = self.container.layout()

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 1. Folder Output Selection Row
        folder_layout = QHBoxLayout()
        folder_label = QLabel(language_config.ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER)
        folder_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 12px; color: #334155; font-weight: 600;"
        )

        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setReadOnly(True)
        self.folder_path_edit.setStyleSheet(
            """
            QLineEdit {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
                color: #1E293B;
            }
        """
        )

        self.browse_button = Button(
            language_config.SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER, variant="secondary"
        )
        self.browse_button.setFixedHeight(30)
        self.browse_button.setStyleSheet(
            """
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
        """
        )

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path_edit, 1)
        folder_layout.addWidget(self.browse_button)
        layout.addLayout(folder_layout)

        # 2. Table Widget with Master Header Checkbox
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setWordWrap(False)
        self.table_widget.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_widget.verticalHeader().setDefaultSectionSize(44)
        self.table_widget.setAutoFillBackground(True)
        self.table_widget.viewport().setAutoFillBackground(True)

        # Set custom header with Master Checkbox
        self.header_view = MasterHeaderView(
            Qt.Orientation.Horizontal, self.table_widget
        )
        self.table_widget.setHorizontalHeader(self.header_view)
        self.table_widget.setHorizontalHeaderLabels(
            ["", "Project Name", "Status", "Details", ""]
        )
        self.header_view.master_checkbox_toggled.connect(
            self._on_master_checkbox_clicked
        )
        self.header_view.context_menu_requested.connect(self._show_table_context_menu)

        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(
            self._show_table_context_menu
        )
        self.table_widget.setStyleSheet(
            """
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
        """
        )
        layout.addWidget(self.table_widget, 1)

        # Shortcut Ctrl+A
        self.shortcut_select_all = QShortcut(QKeySequence("Ctrl+A"), self.table_widget)
        self.shortcut_select_all.activated.connect(
            lambda: self._set_all_checkboxes(True)
        )

        # 3. Translucent Gray Card Container for Progress Bar & Real-time ETA
        self.progress_container = QWidget()
        self.progress_container.setObjectName("ProgressCardContainer")
        self.progress_container.setStyleSheet(
            """
            QWidget#ProgressCardContainer {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }
        """
        )
        prog_card_layout = QVBoxLayout(self.progress_container)
        prog_card_layout.setContentsMargins(12, 8, 12, 8)
        prog_card_layout.setSpacing(4)

        # Top row: Percentage & Status Tag (Left) + ETA (Right)
        prog_top_layout = QHBoxLayout()
        self.progress_percent_label = QLabel("Overall Progress: 0%")
        self.progress_percent_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 12px; font-weight: 700; color: #1E293B;"
        )
        self.progress_status_tag = QLabel("Ready to process")
        self.progress_status_tag.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 11.5px; font-weight: 600; color: #10B981; margin-left: 8px;"
        )
        self.eta_label = QLabel("ETA: --:--")
        self.eta_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 11.5px; font-weight: 600; color: #64748B;"
        )

        prog_top_layout.addWidget(self.progress_percent_label)
        prog_top_layout.addWidget(self.progress_status_tag)
        prog_top_layout.addStretch()
        prog_top_layout.addWidget(self.eta_label)
        prog_card_layout.addLayout(prog_top_layout)

        # Middle row: Animated Progress Bar
        self.progress_bar = ProgressBar(
            style="animated", variant="primary", show_label=False
        )
        prog_card_layout.addWidget(self.progress_bar)

        # Bottom row: Detail status text (Tight spacing right below progress bar, like a note info label)
        self.progress_detail_label = QLabel("")
        self.progress_detail_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 11px; color: #475569; font-weight: 500; margin-top: 1px;"
        )
        self.progress_detail_label.setWordWrap(False)
        self.progress_detail_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.progress_detail_label.setFixedHeight(
            self.progress_detail_label.fontMetrics().height()
        )
        prog_card_layout.addWidget(self.progress_detail_label)

        layout.addWidget(self.progress_container)

        # 4. Action Buttons Row
        button_layout = QHBoxLayout()
        self.edit_algo_button = Button(
            language_config.UI_ALGORIHM_EDIT, variant="secondary"
        )
        self.edit_algo_button.setStyleSheet(
            """
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
        """
        )
        button_layout.addWidget(self.edit_algo_button)
        button_layout.addStretch()

        self.action_button = Button(
            language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT, variant="primary"
        )
        self.action_button.setObjectName("actionButton")
        self._apply_start_button_style()
        self.action_button.setFixedWidth(max(
            self.action_button.fontMetrics().horizontalAdvance(text) for text in (
                language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT,
                language_config.BATCH_CANCELED_PROCESS,
            )
        ) + 48)

        self.close_button = Button(language_config.CLOSE_BUTTON, variant="secondary")
        self.close_button.setStyleSheet(
            """
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
        """
        )

        button_layout.addWidget(self.action_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        container_layout.addWidget(content_widget, 1)

        self.browse_button.clicked.connect(self.browse_output_folder)
        self.action_button.clicked.connect(self._on_action_button_clicked)
        self.close_button.clicked.connect(self.close)
        self.edit_algo_button.clicked.connect(self.open_mass_edit_dialog)

    def _on_master_checkbox_clicked(self):
        checked_count = self._get_checked_checkbox_count()
        # Rule:
        # If checked_count <= 1: Check ALL
        # If checked_count >= 2: Uncheck ALL
        target_state = checked_count <= 1
        self._set_all_checkboxes(target_state)

    def _get_checked_checkbox_count(self):
        count = 0
        for i in range(self.table_widget.rowCount()):
            chk = self._get_row_checkbox(i)
            if chk and chk.isChecked():
                count += 1
        return count

    def _get_row_checkbox(self, row):
        widget = self.table_widget.cellWidget(row, 0)
        if widget:
            return widget.findChild(QCheckBox)
        return None

    def _set_all_checkboxes(self, is_checked):
        for i in range(self.table_widget.rowCount()):
            chk = self._get_row_checkbox(i)
            if chk:
                chk.blockSignals(True)
                chk.setChecked(is_checked)
                chk.blockSignals(False)
        self._update_master_checkbox_visual()

    def _set_selected_checkboxes(self, row_indices, is_checked):
        for r in row_indices:
            chk = self._get_row_checkbox(r)
            if chk:
                chk.blockSignals(True)
                chk.setChecked(is_checked)
                chk.blockSignals(False)
        self._update_master_checkbox_visual()

    def _update_master_checkbox_visual(self):
        total = self.table_widget.rowCount()
        count = self._get_checked_checkbox_count()
        if hasattr(self, "header_view") and self.header_view:
            chk = self.header_view.master_checkbox
            chk.blockSignals(True)
            if count == total and total > 0:
                chk.setChecked(True)
            elif count == 0:
                chk.setChecked(False)
            else:
                chk.setChecked(True)
            chk.blockSignals(False)

    def _handle_checkbox_click(self, row, event=None):
        modifiers = QGuiApplication.keyboardModifiers()
        is_shift = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

        current_chk = self._get_row_checkbox(row)
        if not current_chk:
            return

        target_state = current_chk.isChecked()

        if is_shift and self._last_toggled_row is not None:
            start_r = min(self._last_toggled_row, row)
            end_r = max(self._last_toggled_row, row)
            for r in range(start_r, end_r + 1):
                chk = self._get_row_checkbox(r)
                if chk:
                    chk.blockSignals(True)
                    chk.setChecked(target_state)
                    chk.blockSignals(False)

        self._last_toggled_row = row
        self._update_master_checkbox_visual()

    def _show_table_context_menu(self, pos_or_global_pos):
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
                color: #1E293B;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #F1F5F9;
                color: #0284C7;
            }
        """
        )

        selected_rows = sorted(
            list(set(index.row() for index in self.table_widget.selectedIndexes()))
        )
        checked_in_selection = []
        unchecked_in_selection = []
        for r in selected_rows:
            chk = self._get_row_checkbox(r)
            if chk:
                if chk.isChecked():
                    checked_in_selection.append(r)
                else:
                    unchecked_in_selection.append(r)

        if selected_rows:
            if unchecked_in_selection:
                act_check_sel = menu.addAction(
                    f"Check Selected ({len(unchecked_in_selection)})"
                )
                act_check_sel.triggered.connect(
                    lambda: self._set_selected_checkboxes(unchecked_in_selection, True)
                )
            if checked_in_selection:
                act_uncheck_sel = menu.addAction(
                    f"Uncheck Selected ({len(checked_in_selection)})"
                )
                act_uncheck_sel.triggered.connect(
                    lambda: self._set_selected_checkboxes(checked_in_selection, False)
                )
            menu.addSeparator()

        action_check_all = menu.addAction("Check All (Ctrl+A)")
        action_uncheck_all = menu.addAction("Uncheck All")

        action_check_all.triggered.connect(lambda: self._set_all_checkboxes(True))
        action_uncheck_all.triggered.connect(lambda: self._set_all_checkboxes(False))

        if isinstance(pos_or_global_pos, QPoint):
            if pos_or_global_pos.y() > self.header_view.height():
                global_pos = self.table_widget.mapToGlobal(pos_or_global_pos)
            else:
                global_pos = self.header_view.mapToGlobal(pos_or_global_pos)
        else:
            global_pos = pos_or_global_pos

        menu.exec_(global_pos)

    def _apply_start_button_style(self):
        self.action_button.setText(language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT)
        self.action_button.setStyleSheet(
            """
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
        """
        )

    def _apply_cancel_button_style(self):
        self.action_button.setText(language_config.BATCH_CANCELED_PROCESS)
        self.action_button.setStyleSheet(
            """
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
        """
        )

    def _on_action_button_clicked(self):
        if not self._is_processing:
            self.start_processing()
        else:
            self.cancel_processing()

    def open_mass_edit_dialog(self):
        dialog = MassAlgorithmEditDialog(self.panels, self)
        dialog.algorithms_updated.connect(self.on_algorithms_updated)
        dialog.exec()

    def on_algorithms_updated(self):
        for i, panel in enumerate(self.panels):
            batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
            algo_summary = self._get_algorithm_summary(batch_id)
            self._update_details_cell(i, algo_summary)

    def _set_row_color(self, row, color):
        color_name = color.name() if color != Qt.transparent else "#FFFFFF"
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
            checkbox_widget.setStyleSheet("background-color: #FFFFFF;")
            chk_layout = QHBoxLayout(checkbox_widget)
            chk_box = QCheckBox()
            chk_box.setStyleSheet(CHECKBOX_SWITCH_STYLE)
            chk_box.setChecked(True)
            chk_box.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            chk_box.customContextMenuRequested.connect(
                lambda pos, chk=chk_box: self.table_widget.customContextMenuRequested.emit(
                    chk.mapToGlobal(pos)
                )
            )
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table_widget.setCellWidget(i, 0, checkbox_widget)

            chk_box.clicked.connect(
                lambda checked=False, r=i: self._handle_checkbox_click(r)
            )

            batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
            seq_num = getattr(
                panel, "sequential_batch_number", getattr(panel, "name", f"Batch {i+1}")
            )
            if isinstance(seq_num, str) and seq_num.startswith("Batch "):
                project_name_text = f"{seq_num} ({str(batch_id)[:8]}...)"
            else:
                project_name_text = f"Batch {seq_num} ({str(batch_id)[:8]}...)"

            item_name = QTableWidgetItem(project_name_text)
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_widget.setItem(i, 1, item_name)

            item_status = QTableWidgetItem(f"⏳ {language_config.BATCH_QUEUE}")
            item_status.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(i, 2, item_status)

            algo_summary = self._get_algorithm_summary(batch_id)
            item_details = QTableWidgetItem(algo_summary)
            item_details.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_details.setToolTip(algo_summary)
            self.table_widget.setItem(i, 3, item_details)

            cancel_button = QPushButton("×")
            cancel_button.setToolTip("Cancel this queued or running batch")
            cancel_button.setAccessibleName(f"Cancel {seq_num}")
            cancel_button.setFixedSize(26, 26)
            cancel_button.clicked.connect(
                lambda checked=False, row=i: self.cancel_batch(row)
            )
            self.table_widget.setCellWidget(i, 4, cancel_button)

        self.table_widget.setVerticalHeaderLabels(
            [str(i + 1) for i in range(len(self.panels))]
        )
        self.adjust_column_widths()
        self._update_master_checkbox_visual()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_column_widths()

    def on_batch_finished(self, row, success, result_message):
        was_cancelled = str(result_message).startswith("Cancelled")
        status = "Cancelled" if was_cancelled else ("Success" if success else "Failed")
        color = (
            self.COLOR_CANCELLED
            if was_cancelled
            else (self.COLOR_SUCCESS if success else self.COLOR_FAILED)
        )

        self.table_widget.item(row, 2).setText(status)
        self.table_widget.item(row, 2).setTextAlignment(Qt.AlignCenter)
        self._update_details_cell(row, result_message)
        self._set_row_color(row, color)
        cancel_button = self.table_widget.cellWidget(row, 4)
        if cancel_button:
            cancel_button.setEnabled(False)
        self.processed_count += 1
        self._eta.finish(success)

        num_total = len(self.panels_to_process_with_rows)
        overall_percent = (
            int((self.processed_count / num_total) * 100) if num_total > 0 else 0
        )
        self._update_progress_and_eta(
            overall_percent, f"{self.processed_count}/{num_total} batches processed..."
        )

    def on_processing_complete(self, failed_batches_summary):
        self.reset_dialog_state()
        total = len(self.panels_to_process_with_rows)
        if self._was_cancelled:
            percent = int(100 * self.processed_count / total) if total else 0
            self._update_progress_and_eta(percent, "Batch processing cancelled.")
            self.progress_status_tag.setText("Cancelled")
            self.eta_label.setText("ETA: Cancelled")
        else:
            message = f"Batch processing complete: {len(failed_batches_summary)} failed." if failed_batches_summary else "Batch processing complete!"
            self._update_progress_and_eta(100, message)
            self.progress_status_tag.setText("Completed with errors" if failed_batches_summary else "Completed")
            self.eta_label.setText("ETA: Completed")

        if failed_batches_summary:
            print(f"Failed batches: {failed_batches_summary}")
        elif not self._was_cancelled:
            print("Batch processing completed successfully!")

    def on_progress_update_from_thread(
        self, row, status, details, percent_in_batch, current_num, total_num
    ):
        if row < len(self.panels):
            batch_id = getattr(
                self.panels[row], "batch_id", getattr(self.panels[row], "id", "")
            )
            if getattr(self, "processing_thread", None) and self.processing_thread._batch_cancelled(batch_id):
                return
        self.table_widget.item(row, 2).setText(f"⚙ {status}")
        self._update_details_cell(row, details)

        num_total_batches = len(self.panels_to_process_with_rows)
        overall_percent = (
            int(
                (
                    (self.processed_count + (max(0, min(99, percent_in_batch)) / 100.0))
                    / num_total_batches
                )
                * 100
            )
            if num_total_batches > 0
            else 0
        )

        detail_msg = f"{self.processed_count}/{total_num} batches processed... ({details})"
        self._update_progress_and_eta(overall_percent, detail_msg)

    def _update_progress_and_eta(self, percent, detail_msg=""):
        self.progress_bar.setValue(percent)
        self.progress_percent_label.setText(f"Overall Progress: {percent}%")

        if detail_msg:
            self.progress_status_tag.setText("Processing...")
            self.progress_status_tag.setStyleSheet(
                "font-family: 'Segoe UI', Arial; font-size: 11.5px; font-weight: 600; color: #0284C7; margin-left: 8px;"
            )
            self.progress_detail_label.setText(detail_msg)
            self.progress_detail_label.setToolTip(detail_msg)
        else:
            self.progress_status_tag.setText("Ready to process")
            self.progress_status_tag.setStyleSheet(
                "font-family: 'Segoe UI', Arial; font-size: 11.5px; font-weight: 600; color: #10B981; margin-left: 8px;"
            )
            self.progress_detail_label.clear()
            self.progress_detail_label.setToolTip("")

        self._refresh_eta()

    def _on_batch_started(self, row, reused):
        self._eta.begin(reused)
        self._refresh_eta()

    def _refresh_eta(self):
        if not self._is_processing or self._eta is None:
            return
        remaining = self._eta.remaining()
        if remaining is not None:
            mins, secs = divmod(remaining, 60)
            self.eta_label.setText(f"ETA: {mins:02d}:{secs:02d}")
        else:
            self.eta_label.setText("ETA: Estimating...")

    def _update_details_cell(self, row, text):
        item = self.table_widget.item(row, 3)
        if item:
            item.setText(text)
            item.setToolTip(text)

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
            self.table_widget.item(row, 2).setText(f"⏳ {language_config.BATCH_QUEUE}")
            batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
            algo_summary = self._get_algorithm_summary(batch_id)
            self._update_details_cell(row, algo_summary)
            self._set_row_color(row, Qt.transparent)

        self._is_processing = True
        self.processed_count = 0
        self._eta = BatchEtaEstimator(len(self.panels_to_process_with_rows))
        self._eta_timer.start()

        self._apply_cancel_button_style()
        self.browse_button.setEnabled(False)
        self.edit_algo_button.setEnabled(False)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self._update_progress_and_eta(0, "Starting batch process...")
        self.processing_thread = ProcessingThread(
            self.panels_to_process_with_rows, self.batch_page_layout, target_folder
        )
        self.processing_thread.progress_update.connect(
            self.on_progress_update_from_thread
        )
        self.processing_thread.batch_started.connect(self._on_batch_started)
        self.processing_thread.batch_finished.connect(self.on_batch_finished)
        self.processing_thread.processing_complete.connect(self.on_processing_complete)
        self.processing_thread.finished.connect(self._on_worker_stopped)
        self.processing_thread.start()

    def cancel_processing(self):
        if hasattr(self, "processing_thread") and self.processing_thread.isRunning():
            from UILibrary import modal_confirm

            reply = modal_confirm.question(
                self,
                language_config.BATCH_CANCELED_CONFIRMATION,
            )
            if reply:
                self._was_cancelled = True
                self.processing_thread.stop()
                self.action_button.setEnabled(False)
                self.progress_status_tag.setText("Cancelling...")

    def cancel_batch(self, row):
        """Cancel one queued job or request cancellation of its active worker."""
        if not self._is_processing or row < 0 or row >= len(self.panels):
            return
        panel = self.panels[row]
        batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
        status_item = self.table_widget.item(row, 2)
        if status_item is None:
            return
        status = status_item.text()
        if status in ("Success", "Failed", "Cancelled"):
            return
        processing_thread = getattr(self, "processing_thread", None)
        if processing_thread is None:
            return
        processing_thread.cancel_batch(batch_id)
        if "Processing" in status:
            status_item.setText("Cancelling…")
        else:
            status_item.setText("Cancelled")
            self._set_row_color(row, self.COLOR_CANCELLED)
            button = self.table_widget.cellWidget(row, 4)
            if button:
                button.setEnabled(False)

    def cancel_batch_by_id(self, batch_id):
        """Resolve and cancel a job by stable batch identity, independent of row order."""
        for row, panel in enumerate(self.panels):
            panel_batch_id = getattr(panel, "batch_id", getattr(panel, "id", ""))
            if str(panel_batch_id) == str(batch_id):
                self.cancel_batch(row)
                return True
        return False

    def closeEvent(self, event):
        """Keep the dialog alive until cancellation completes without blocking Qt."""
        processing_thread = getattr(self, "processing_thread", None)
        if processing_thread is not None and processing_thread.isRunning():
            self._was_cancelled = True
            self._close_after_processing = True
            processing_thread.stop()
            self.action_button.setEnabled(False)
            self.progress_status_tag.setText("Cancelling...")
            event.ignore()
            return

        event.accept()
        super().closeEvent(event)

    def _on_worker_stopped(self):
        if self._close_after_processing:
            self._close_after_processing = False
            self.close()

    def reject(self):
        processing_thread = getattr(self, "processing_thread", None)
        if processing_thread is not None and processing_thread.isRunning():
            self.close()
        else:
            super().reject()

    def reset_dialog_state(self):
        self._is_processing = False
        self._eta_timer.stop()

        self._apply_start_button_style()
        self.action_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.edit_algo_button.setEnabled(True)

        for i in range(self.table_widget.rowCount()):
            status_item = self.table_widget.item(i, 2)
            if not status_item:
                continue

            if "Processing" in status_item.text() or status_item.text().startswith("Cancelling"):
                status_item.setText(language_config.BATCH_CANCELED_INFO)
                self._update_details_cell(i, "")
                self._set_row_color(i, self.COLOR_CANCELLED)

            elif self._was_cancelled and (
                "Waiting" in status_item.text()
                or "Menunggu" in status_item.text()
                or status_item.text() == "Pending"
            ):
                status_item.setText(language_config.BATCH_CANCELED_INFO)
                self._update_details_cell(i, "")
                self._set_row_color(i, self.COLOR_CANCELLED)

    def adjust_column_widths(self):
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_widget.setColumnWidth(0, 36)

        available_width = (
            self.table_widget.viewport().width()
            - header.sectionSize(0)
            - header.sectionSize(2)
            - 36
        )
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(4, 36)
        self.table_widget.setColumnWidth(1, int(available_width * (1 / 4)))

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, language_config.SELECT_OUTPUT_FOLDER_TITLE
        )
        if folder:
            self.folder_path_edit.setText(folder)


class ProcessingThread(QThread):
    batch_started = Signal(int, bool)
    progress_update = Signal(int, str, str, int, int, int)
    batch_finished = Signal(int, bool, str)
    processing_complete = Signal(list)

    def __init__(self, panels_to_process, batch_page_layout, target_folder):
        super().__init__()
        self.panels_to_process = panels_to_process
        self.batch_page_layout = batch_page_layout
        self.target_folder = target_folder
        self._is_running = True
        self._cancelled_batch_ids = set()
        self._active_batch_id = None
        self._cancel_lock = threading.Lock()

    def cancel_batch(self, batch_id):
        batch_key = str(batch_id)
        with self._cancel_lock:
            self._cancelled_batch_ids.add(batch_key)
            active = self._active_batch_id == batch_key
        if active:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
                    BackendWorkerManager,
                )

                BackendWorkerManager.instance().stop_current_task()
            except Exception:
                pass

    def _batch_cancelled(self, batch_id):
        with self._cancel_lock:
            return str(batch_id) in self._cancelled_batch_ids

    def _result_identity(self, panel, batch_id):
        database = getattr(self.batch_page_layout, "database_manager", None)
        if database is None:
            return None, [os.path.join("database", "stack")]
        image_paths = [path for path in database.get_images_by_batch(batch_id)
                       if os.path.isfile(path)]
        stages = plan_stages(self._batch_selections(panel, batch_id))
        settings = {}
        if os.path.isfile(config.GENERAL_SETTINGS_FILE):
            with open(config.GENERAL_SETTINGS_FILE, "r", encoding="utf-8") as stream:
                settings = json.load(stream)
        names = expected_output_names(stages, image_paths, settings)
        directories = [os.path.join("database", "stack")]
        db_path = getattr(database, "db_path", None)
        if db_path:
            directories.append(os.path.join(os.path.dirname(db_path), "stack"))
        return names, directories

    def _batch_selections(self, panel, batch_id):
        state_path = getattr(self.batch_page_layout, "json_path", None) or os.path.join(
            "database", "align", "batch_parameter.json"
        )
        state = load_json_state(state_path).get(str(batch_id), {}) if os.path.isfile(state_path) else {}
        return batch_selections(state, getattr(panel, "selected_algorithms", {}))

    def _process_batch(self, panel, batch_id, progress_callback):
        from pixel_refine_desktop.enhance_stack.core.logic.algorithm_processor import dispatch_worker_task
        from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import BackendWorkerManager

        selections = self._batch_selections(panel, batch_id)
        settings = dict(selections)
        for category, key in (
            ("alignment", config.KEY_CHECKBOX_ALIGN),
            ("denoising", config.KEY_CHECKBOX_DENOISING),
            ("super_resolution", config.KEY_CHECKBOX_SUPER_RES),
            ("hdr", config.KEY_CHECKBOX_HDR),
        ):
            settings[key] = not get_spec(category, selections[category]).disabled
        database = getattr(self.batch_page_layout, "database_manager", None)
        db_path = getattr(database, "db_path", None) or os.environ.get("PIXEL_REFINE_SESSION_DB")
        if not db_path:
            raise RuntimeError("A session database is required for batch processing")
        progress_callback(0, "Menyiapkan mesin proses...")
        result = dispatch_worker_task(
            BackendWorkerManager.instance(),
            {"batch_id": batch_id, "single_process": False, "db_path": db_path, "settings": settings},
            lambda percent, message="": progress_callback(percent, str(message).split("||", 1)[0]),
            lambda: not self._is_running or self._batch_cancelled(batch_id),
        )
        if result.get("type") == "cancelled":
            return []
        if not result.get("success"):
            raise RuntimeError(result.get("error", "Batch worker failed"))
        return result.get("output_paths", [])

    def run(self):
        failed_batches_summary = []
        total_batches_to_process = len(self.panels_to_process)

        for i, (panel, row) in enumerate(self.panels_to_process):
            if not self._is_running:
                break

            seq_num = getattr(
                panel, "sequential_batch_number", getattr(panel, "name", "?")
            )
            batch_id = getattr(panel, "batch_id", getattr(panel, "id", "UNKNOWN"))

            if self._batch_cancelled(batch_id):
                self.batch_finished.emit(row, False, "Cancelled before processing")
                continue
            with self._cancel_lock:
                self._active_batch_id = str(batch_id)

            try:

                def sub_process_progress_callback(*args, **kwargs):
                    if not self._is_running:
                        return
                    current_num_for_ui = i + 1
                    if not args and not kwargs:
                        return
                    percent, message = _parse_bulk_progress(*args, **kwargs)

                    self.progress_update.emit(
                        row,
                        "Processing",
                        message,
                        percent,
                        current_num_for_ui,
                        total_batches_to_process,
                    )

                target_panel = getattr(panel, "original_panel", panel)
                if not os.path.isdir(self.target_folder):
                    raise OSError(f"Target folder is not accessible: {self.target_folder}")
                names, stack_directories = self._result_identity(target_panel, batch_id)
                outputs = find_existing_outputs(names, [self.target_folder, *stack_directories])
                reused = bool(outputs)
                self.batch_started.emit(row, reused)
                if reused:
                    print(f"[Bulk Save] batch={batch_id} reusing exact outputs: {outputs}")
                    sub_process_progress_callback(100, "Existing result found; skipping stacking")
                else:
                    result = self._process_batch(target_panel, batch_id, sub_process_progress_callback)
                    if self._batch_cancelled(batch_id):
                        self.batch_finished.emit(row, False, "Cancelled during processing")
                        continue
                    if not self._is_running:
                        break
                    outputs = returned_output_paths(result)
                    if not outputs:
                        # Compatibility for entrypoints that still return None:
                        # use exact expected names, never folder set-differences.
                        outputs = find_existing_outputs(names, stack_directories)
                    if not outputs or any(not usable_output(path) for path in outputs):
                        raise OSError(f"No complete output generated for batch {batch_id}; expected={names}")
                    if names and not set(names).issubset({os.path.basename(path) for path in outputs}):
                        raise OSError(f"Incomplete output set for batch {batch_id}; expected={names}, returned={outputs}")

                details = []
                sub_process_progress_callback(99, "Menyimpan hasil ke folder tujuan...")
                for output_file in dict.fromkeys(outputs):
                    if not self._is_running or self._batch_cancelled(batch_id):
                        break
                    if reused:
                        destination = os.path.join(self.target_folder, os.path.basename(output_file))
                        success, detail = copy_result(output_file, destination)
                    else:
                        success = self.batch_page_layout._move_single_batch_result(
                            output_file, self.target_folder
                        )
                        detail = getattr(self.batch_page_layout, "_last_result_export_detail", "")
                    if not success:
                        raise OSError(f"Could not save {os.path.basename(output_file)}: {detail}")
                    details.append(detail)
                if self._batch_cancelled(batch_id):
                    self.batch_finished.emit(row, False, "Cancelled during export")
                    continue
                if not self._is_running:
                    break
                message = "Success: Reused existing result" if reused else "Success: Saved"
                warnings = [detail for detail in details if "original retained" in detail]
                if warnings:
                    message += "; output saved, locked original retained"
                self.batch_finished.emit(row, True, message)

            except Exception as e:
                error_detail = str(e)
                if self._batch_cancelled(batch_id):
                    self.batch_finished.emit(row, False, "Cancelled during processing")
                else:
                    failed_summary = {"seq": seq_num, "id": batch_id, "error": error_detail}
                    failed_batches_summary.append(failed_summary)
                    print(f"[Bulk Save] batch={batch_id} error: {error_detail}")
                    self.batch_finished.emit(row, False, f"Failed: {error_detail}")
            finally:
                with self._cancel_lock:
                    if self._active_batch_id == str(batch_id):
                        self._active_batch_id = None

        self.processing_complete.emit(failed_batches_summary)

    def stop(self):
        self._is_running = False
