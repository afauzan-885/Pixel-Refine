"""Performance settings, including target backend selection and validation."""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from resources.GenericUILibrary import (
    Button,
    Checkbox,
    Container,
    FormGroup,
    FormRow,
    Modal,
    Stack,
)
from pixel_refine_desktop.ui.views.settings.General.GeneralSetting import (
    GeneralSettingsPage,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from resources.GenericUILibrary.modals import modal_confirm
from pixel_refine_desktop.ui.views.settings.General.helpers import restart_application


class PerformanceSettingsPage(GeneralSettingsPage):
    """Backend controls sharing the General page's discovery/test pipeline.

    The implementation deliberately inherits the established backend resolver
    and hardware test worker. Only the presentation and apply surface move to
    the Performance tab, so persisted keys and runtime selection stay stable.
    """

    def _setup_ui(self):
        self.performance_container = Container(padding=0, fluid=True)
        self.performance_container.setObjectName("performance_container")
        self.performance_container.setStyleSheet(
            "#performance_container { background-color: transparent; border: none; }"
        )
        self.performance_container.main_layout.setContentsMargins(0, 0, 0, 0)
        split_layout = QHBoxLayout()
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(0)
        self.performance_container.main_layout.addLayout(split_layout)

        self.performance_left = Container(padding=0)
        self.performance_left.setObjectName("performance_left")
        self.performance_left.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.performance_left.main_layout.setContentsMargins(0, 0, 3, 0)
        self.performance_left.main_layout.setSpacing(6)

        self.performance_right = Container(padding=0)
        self.performance_right.setObjectName("performance_right")
        self.performance_right.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.performance_right.main_layout.setContentsMargins(3, 0, 0, 0)
        self.performance_right.main_layout.setSpacing(6)

        split_layout.addWidget(self.performance_left, 1)
        split_layout.addWidget(self.performance_right, 1)

        hardware_backends = self._scan_hardware_backend_options()
        self._migrate_saved_backend_option(hardware_backends)

        left_form = FormRow()
        right_form = FormRow()

        device_label = getattr(
            language_config,
            "DEVICE_ACCELERATION_LABEL",
            "GPU Acceleration",
        )
        self.device_group = FormGroup(
            label=device_label, input_type="select", auto_sync=False
        )
        if isinstance(self.device_group.input, QComboBox):
            for option in hardware_backends:
                self.device_group.input.addItem(option["text"], option)
            self.device_group.input.currentTextChanged.connect(
                self.update_device_dropdown_style
            )
        self.device_group.bind_store(self.store, "device_backend")
        self._restore_saved_backend_selection(hardware_backends)
        self._add_backend_info_action()
        left_form.add_row(self.device_group)
        self._apply_selected_backend_to_process()

        self.test_btn = Button(
            language_config.BTN_TEST_BACKEND_HARDWARE, variant="secondary"
        )
        self.test_btn.setMinimumHeight(35)
        self.test_btn.setStyleSheet(
            self.test_btn.styleSheet()
            + "\nQPushButton { font-size: 10.4pt; }"
        )
        self.test_btn.set_content_width_limit(
            reference=self.device_group.input,
            minimum_width=120,
        )
        self.test_btn.clicked.connect(self._on_test_backends_clicked)
        left_form.add_row(self.test_btn)
        left_form.form_layout.setAlignment(
            self.test_btn, Qt.AlignmentFlag.AlignHCenter
        )

        auto_fb_label = getattr(language_config, "LBL_AUTO_FALLBACK", "Auto Fallback")
        auto_fb_tip = getattr(
            language_config,
            "LBL_AUTO_FALLBACK_TIP",
            "When enabled, automatically fall back through CUDA, Vulkan, OpenGL, "
            "then CPU if the selected backend is unavailable.",
        )
        self.auto_fallback_cb = Checkbox(auto_fb_label, auto_sync=True)
        self.auto_fallback_cb.checkbox.setToolTip(auto_fb_tip)
        self.auto_fallback_cb.bind_store(self.store, "auto_fallback")
        left_form.add_row(self.auto_fallback_cb)

        # FormGroup's decimal editor is the GenericUILibrary component as
        # well; auto_sync makes threshold edits immediately available to the
        # runtime without restarting the application.
        self.compute_block_threshold_group = FormGroup(
            label="Megapixel Threshold", input_type="decimal", auto_sync=True
        )
        self.compute_block_threshold_group.input.setRange(0.1, 1000.0)
        self.compute_block_threshold_group.input.setSingleStep(0.5)
        self.compute_block_threshold_group.input.setDecimals(1)
        self.compute_block_threshold_group.bind_store(
            self.store, "compute_block_threshold_mp"
        )
        self.compute_block_mode_group = FormGroup(
            label="Block Processing", input_type="select", auto_sync=False
        )
        self.compute_block_mode_group.input.addItems(
            ["Automatic (by megapixels)", "Enabled", "Disabled"]
        )
        # Persist a compact canonical value while displaying friendly labels.
        mode_text = self._block_mode_text(self.store.get("compute_block_mode", "auto"))
        self.compute_block_mode_group.input.setCurrentText(mode_text)
        self.compute_block_mode_group.input.currentTextChanged.connect(
            self._on_block_processing_changed
        )
        self.store.changed.connect(self._on_performance_store_changed)
        right_form.add_row(self.compute_block_mode_group)
        right_form.add_row(self.compute_block_threshold_group)

        self.compute_block_size_group = FormGroup(
            label="Block Size", input_type="select", auto_sync=True
        )
        self.compute_block_size_group.input.addItems(["512", "768", "1024", "2048"])
        self.compute_block_size_group.bind_store(self.store, "compute_block_size")
        right_form.add_row(self.compute_block_size_group)

        self.performance_left.add_widget(left_form)
        self.performance_left.add_stretch()
        self.performance_right.add_widget(right_form)
        self.performance_right.add_stretch()
        self._update_block_processing_controls()
        self.update_device_dropdown_style()

        self.add_widget(self.performance_container, stretch=1)
        QTimer.singleShot(0, self._compact_performance_inputs)

        actions = Stack(orientation="horizontal")
        actions.add_stretch()
        self.apply_btn = Button(
            getattr(language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings"),
            variant="success",
        )
        self.apply_btn.setObjectName("ApplyPerformanceSettingsBtn")
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.clicked.connect(self._on_apply_clicked)
        actions.add_item(self.apply_btn)
        self.add_widget(actions)

    def _add_backend_info_action(self):
        """Add a compact help action beside the GPU acceleration label."""
        label = getattr(self.device_group, "label", None)
        group_layout = self.device_group.layout()
        if label is None or group_layout is None:
            return

        group_layout.removeWidget(label)
        label_row = QWidget(self.device_group)
        label_row.setObjectName("GPUAccelerationLabelRow")
        label_layout = QHBoxLayout(label_row)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(5)
        label.setParent(label_row)
        label_layout.addWidget(label)

        self.backend_info_btn = Button(
            "?",
            variant="ghost",
            object_name="GPUAccelerationInfoButton",
        )
        self.backend_info_btn.setFixedSize(18, 18)
        self.backend_info_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.backend_info_btn.setToolTip(
            "Lihat hardware yang terdeteksi, status backend, dan estimasi performa."
        )
        self.backend_info_btn.setStyleSheet(
            """
            QPushButton#GPUAccelerationInfoButton {
                background-color: #E8F3F9;
                color: #0078D4;
                border: 1px solid #B8D8EA;
                border-radius: 9px;
                padding: 0px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#GPUAccelerationInfoButton:hover {
                background-color: #D5ECF8;
                border-color: #0078D4;
            }
            QPushButton#GPUAccelerationInfoButton:pressed {
                background-color: #B8D8EA;
            }
            """
        )
        self.backend_info_btn.clicked.connect(self._show_backend_statistics)
        label_layout.addWidget(self.backend_info_btn)
        label_layout.addStretch()
        group_layout.insertWidget(0, label_row)

    def _show_backend_statistics(self):
        """Show detected backend support and small-test performance estimates."""
        options = self._get_backend_test_options()
        test_results = self.store.get("backend_test_results", {})
        target_megapixels = 24.0
        target_label = "24 MP (6000 x 4000)"

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(10)

        tested = sum(
            1
            for result in test_results.values()
            if isinstance(result, dict) and result.get("total", 0)
        )
        supported = sum(
            1
            for result in test_results.values()
            if isinstance(result, dict) and result.get("status") == "support"
        )
        skipped = sum(
            int(result.get("benchmark_skipped", 0) or 0)
            for result in test_results.values()
            if isinstance(result, dict)
        )
        summary = QLabel(
            f"Terdeteksi: {len(options)} backend · Lulus: {supported}/{tested} diuji\n"
            f"Benchmark kecil: 256 x 256 (0,066 MP) · Estimasi target: {target_label}"
        )
        summary.setWordWrap(True)
        summary.setText(
            f"Terdeteksi: {len(options)} backend | Lulus: {supported}/{tested} diuji"
            f" | Opsional dilewati: {skipped}\n"
            f"Benchmark GPU: 1024 x 1024 (1,049 MP) | 4x per algoritma "
            f"(1 warm-up + 3 pengukuran) | Estimasi target: {target_label}"
        )
        summary.setStyleSheet(
            "color: #475569; font-size: 11px; padding: 2px 0 4px 0;"
        )
        body_layout.addWidget(summary)

        grouped = {}
        for option in options:
            hardware = str(option.get("raw_name") or option.get("text", "Unknown hardware"))
            group_key = hardware.strip().lower()
            grouped.setdefault((group_key, hardware), []).append(option)
        grouped_options = []
        backend_order = {"vulkan": 0, "opengl": 1, "cuda": 2, "cpu": 3}
        for (_, hardware), group_options in grouped.items():
            grouped_options.append(("group", hardware, None))
            grouped_options.extend(
                ("backend", hardware, option)
                for option in sorted(
                    group_options,
                    key=lambda item: backend_order.get(
                        str(item.get("backend", "")).lower(), 99
                    ),
                )
            )

        table = QTableWidget(len(grouped_options), 5)
        table.setHorizontalHeaderLabels(
            ["Backend", "Hardware", "Status", "GPU 1024²", "Estimasi 24 MP"]
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setWordWrap(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.setStyleSheet(
            """
            QTableWidget {
                background: #FFFFFF;
                alternate-background-color: #F8FAFC;
                border: 1px solid #D9E2EA;
                gridline-color: #E7EDF2;
                color: #25313C;
                font-size: 10px;
            }
            QHeaderView::section {
                background: #EEF5F8;
                color: #334155;
                border: none;
                border-bottom: 1px solid #D9E2EA;
                padding: 6px;
                font-weight: bold;
            }
            """
        )

        for row, row_type, option in (
            (index, kind, item) for index, (kind, _hardware, item) in enumerate(grouped_options)
        ):
            if row_type == "group":
                table.setSpan(row, 0, 1, 5)
                group_item = QTableWidgetItem(str(grouped_options[row][1]))
                group_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                group_item.setBackground(Qt.GlobalColor.lightGray)
                table.setItem(row, 0, group_item)
                continue
            key = option.get("key", option.get("text", ""))
            result = test_results.get(key, {})
            if not isinstance(result, dict):
                result = {"status": result}
            status = str(result.get("status", "not_tested"))
            status_text = {
                "support": "Didukung",
                "disable": "Gagal",
                "not_tested": "Belum diuji",
            }.get(status, status)
            benchmark_ms = result.get("benchmark_elapsed_ms")
            benchmark_width = int(result.get("benchmark_width", 1024) or 1024)
            benchmark_height = int(result.get("benchmark_height", 1024) or 1024)
            benchmark_mp = max(
                0.000001, benchmark_width * benchmark_height / 1_000_000.0
            )
            if benchmark_ms is not None:
                try:
                    benchmark_ms = float(benchmark_ms)
                    projected_ms = benchmark_ms * target_megapixels / benchmark_mp
                    small_text = f"{benchmark_ms:.0f} ms\n{benchmark_width}x{benchmark_height}"
                    large_text = (
                        f"~{projected_ms / 1000.0:.1f} s\n"
                        f"~{1000.0 / max(projected_ms, 1.0):.2f} FPS"
                    )
                except (TypeError, ValueError):
                    small_text = "Tidak valid"
                    large_text = "-"
            else:
                small_text = "Belum diuji"
                large_text = "-"

            values = (
                str(option.get("backend", "")).upper(),
                str(option.get("raw_name") or option.get("text", "")),
                status_text,
                small_text,
                large_text,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                table.setItem(row, column, item)
            table.item(row, 2).setForeground(
                Qt.GlobalColor.darkGreen
                if status == "support"
                else Qt.GlobalColor.darkRed
                if status == "disable"
                else Qt.GlobalColor.darkGray
            )

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table_width = sum(table.columnWidth(column) for column in range(table.columnCount()))
        table_width += table.verticalScrollBar().sizeHint().width() + 4
        table_height = table.horizontalHeader().height()
        table_height += sum(table.rowHeight(row) for row in range(table.rowCount()))
        table_height += 4
        table.setFixedSize(
            min(max(table_width, 420), 620),
            min(max(table_height, 120), 420),
        )
        body_layout.addWidget(table, 1)
        note = QLabel(
            "Estimasi menggunakan pendekatan linear dari uji cepat resolusi kecil; "
            "hasil aktual pada resolusi besar dapat berbeda karena bandwidth, cache, "
            "tiling, dan penggunaan VRAM."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #64748B; font-size: 10px;")
        body_layout.addWidget(note)

        dialog = Modal(title="Hardware Backend Statistics", size="medium", parent=self.window())
        dialog.set_body(body)
        dialog.add_footer_button("Tutup", variant="secondary")
        dialog.fit_to_content(max_width=660, max_height=700)
        dialog.exec()

    @staticmethod
    def _block_mode_text(mode):
        mode = str(mode or "auto").strip().lower()
        return {
            "block": "Enabled",
            "always": "Enabled",
            "enabled": "Enabled",
            "auto": "Automatic (by megapixels)",
            "automatic": "Automatic (by megapixels)",
            "full": "Disabled",
            "disabled": "Disabled",
        }.get(mode, "Automatic (by megapixels)")

    def _block_mode_value(self):
        text = self.compute_block_mode_group.input.currentText()
        return {
            "Enabled": "block",
            "Automatic (by megapixels)": "auto",
            "Disabled": "full",
        }.get(text, "auto")

    def _on_block_processing_changed(self, _text):
        self.store.set("compute_block_mode", self._block_mode_value())
        self._update_block_processing_controls()

    def _on_performance_store_changed(self, key, _value):
        if key is None or key == "compute_block_mode":
            mode_text = self._block_mode_text(
                self.store.get("compute_block_mode", "auto")
            )
            combo = self.compute_block_mode_group.input
            combo.blockSignals(True)
            combo.setCurrentText(mode_text)
            combo.blockSignals(False)
            self._update_block_processing_controls()

    def _update_block_processing_controls(self):
        """Apply the mode-dependent visibility/enabled contract."""
        mode = self._block_mode_value()
        is_disabled = mode == "full"
        is_automatic = mode == "auto"

        self.compute_block_threshold_group.setVisible(not is_disabled)
        self.compute_block_threshold_group.input.setEnabled(is_automatic)
        self.compute_block_size_group.input.setEnabled(not is_disabled)

    def _compact_performance_inputs(self):
        """Keep settings editors compact while allowing long options to fit."""
        inputs = (
            getattr(getattr(self, "device_group", None), "input", None),
            getattr(getattr(self, "compute_block_size_group", None), "input", None),
            getattr(getattr(self, "compute_block_threshold_group", None), "input", None),
            getattr(getattr(self, "compute_block_mode_group", None), "input", None),
        )
        compact_width = max(180, int(max(1, self.width()) * 0.5) - 30)
        block_inputs = (
            getattr(getattr(self, "compute_block_size_group", None), "input", None),
            getattr(getattr(self, "compute_block_mode_group", None), "input", None),
        )
        block_required_width = max(
            (
                editor.sizeHint().width() + 24
                for editor in block_inputs
                if editor is not None
            ),
            default=180,
        )
        block_width = min(compact_width, block_required_width)
        for editor in inputs:
            if editor is None:
                continue
            required_width = editor.sizeHint().width() + 24
            width = (
                block_width
                if editor in block_inputs
                else min(compact_width, max(180, required_width))
            )
            editor.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            editor.setMinimumWidth(width)
            editor.setFixedWidth(width)
            if isinstance(editor, QComboBox):
                editor.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        if hasattr(self, "test_btn"):
            self.test_btn.refresh_content_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._compact_performance_inputs()

    def _restore_saved_backend_selection(self, options):
        """Select the persisted backend by key, identity, or architecture.

        The display text can be stale after a device rename or migration. The
        canonical architecture/device selector is therefore preferred so the
        combo box reflects the backend actually loaded at startup.
        """
        if not isinstance(getattr(self.device_group, "input", None), QComboBox):
            return
        saved_key = str(self.store.get("device_backend_key", "") or "")
        saved_arch = str(self.store.get("device_backend_arch", "cpu") or "cpu").lower()
        saved_id = self.store.get("device_backend_id", None)
        try:
            saved_id = int(saved_id)
        except (TypeError, ValueError):
            saved_id = None
        selector = self.store.get("device_selector", {})
        saved_name = str(selector.get("name", "") if isinstance(selector, dict) else "").lower()
        saved_text = str(self.store.get("device_backend", "") or "")

        def matches(option):
            if saved_key and option.get("key") == saved_key:
                return True
            if option.get("backend") != saved_arch:
                return False
            if saved_id is not None and option.get("device_id") == saved_id:
                return True
            if saved_name and saved_name in str(option.get("raw_name", "")).lower():
                return True
            return option.get("text") == saved_text

        selected = next((option for option in options if matches(option)), None)
        if selected is None:
            return
        index = self.device_group.input.findData(selected)
        if index < 0:
            index = self.device_group.input.findText(selected.get("text", ""))
        if index >= 0:
            self.device_group.input.setCurrentIndex(index)

    def retranslate_ui(self):
        language_config.reload_language()
        parent_tab = self.parentWidget()
        if parent_tab and hasattr(parent_tab, "parentWidget"):
            from PySide6.QtWidgets import QTabWidget

            tabs = parent_tab.parentWidget()
            if isinstance(tabs, QTabWidget):
                index = tabs.indexOf(parent_tab)
                if index >= 0:
                    tabs.setTabText(
                        index,
                        getattr(language_config, "SETTING_PERFORMANCE_LABEL", "Performance"),
                    )
        self.device_group.label.setText(
            getattr(language_config, "DEVICE_ACCELERATION_LABEL", "GPU Acceleration")
        )
        if hasattr(self, "compute_block_mode_group"):
            self.compute_block_mode_group.label.setText("Block Processing")
        if hasattr(self, "compute_block_threshold_group"):
            self.compute_block_threshold_group.label.setText("Megapixel Threshold")
        if hasattr(self, "compute_block_size_group"):
            self.compute_block_size_group.label.setText("Block Size")
        self.auto_fallback_cb.checkbox.setText(
            getattr(language_config, "LBL_AUTO_FALLBACK", "Auto Fallback")
        )
        self.auto_fallback_cb.checkbox.setToolTip(
            getattr(language_config, "LBL_AUTO_FALLBACK_TIP", "")
        )
        self.test_btn.setText(language_config.BTN_TEST_BACKEND_HARDWARE)
        self.apply_btn.setText(
            getattr(language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings")
        )
        self.update_theme()
        self.update_device_dropdown_style()

    def _on_apply_clicked(self):
        selected_backend_text = self.device_group.input.currentText()
        backend_changed = selected_backend_text != self._initial_device_backend
        self._apply_selected_backend_to_process()
        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()

        from resources.GenericUILibrary import Toast, trigger_live_update

        trigger_live_update()
        self._initial_device_backend = selected_backend_text
        Toast(
            getattr(language_config, "SETTINGS_SAVED", "Settings saved successfully!"),
            variant="success",
            parent=self.window(),
        ).show_toast(duration=3000)

        if backend_changed:
            dialog = modal_confirm(
                language_config.MSG_BACKEND_EXIT_REQUIRED, self.window()
            )
            dialog.title_text.setText(language_config.EXIT_APPLICATION_APPLY_BACKEND_TITLE)
            dialog.yes_button.setText(language_config.EXIT_APPLICATION_YES)
            dialog.no_button.setText(language_config.EXIT_APPLICATION_NO)
            if dialog.exec() == dialog.DialogCode.Accepted:
                restart_application()


def performance_page():
    return PerformanceSettingsPage()
