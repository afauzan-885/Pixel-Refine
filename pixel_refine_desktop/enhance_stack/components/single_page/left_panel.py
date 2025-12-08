# File: left_panel.py
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QPushButton,
    QButtonGroup,
)
from PySide6.QtCore import Qt

# Import GenericUILibrary
from pixel_refine_desktop.ui.resources.GenericUILibrary import FormGroup

from pixel_refine_desktop.enhance_stack.models.algorithm_list import (
    get_algorithm_descriptions,
    get_algorithm_names,
    get_algorithm_options,
    get_category_display_name,
)
from pixel_refine_desktop.enhance_stack.components.single_page.parameter_pages import (
    ParameterPages,
)
from pixel_refine_desktop.ui.resources.styles import stylesheet
from pixel_refine_desktop.ui.resources.styles.stylesheet import (
    SWITCH_BUTTON_ACTIVE_STYLE,
    SWITCH_BUTTON_DEFAULT_STYLE,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.init_preview_panel(layout)
        self.init_parameter_panel(layout)
        self.setLayout(layout)

    def init_preview_panel(self, parent_layout):
        self.preview_panel_widget = QWidget()
        preview_panel_layout = QVBoxLayout(self.preview_panel_widget)
        preview_panel_label = QLabel(language_config.PREVIEW_PANEL_LABEL)
        preview_panel_layout.addWidget(preview_panel_label)
        self.preview_panel_widget.setStyleSheet(stylesheet.PANEL_BACKGROUND_STYLE)
        parent_layout.addWidget(self.preview_panel_widget)

    def init_parameter_panel(self, parent_layout):
        self.parameter_panel_widget = QWidget()
        self.parameter_panel_widget.setMaximumHeight(300)
        parameter_panel_outer_layout = QVBoxLayout(self.parameter_panel_widget)
        parameter_panel_outer_layout.setContentsMargins(10, 10, 0, 0)
        parameter_panel_outer_layout.setSpacing(0)

        main_parameter_area_layout = QHBoxLayout()
        main_parameter_area_layout.setSpacing(0)

        left_dropdown_panel_widget = QWidget()
        left_dropdown_layout = QVBoxLayout(left_dropdown_panel_widget)
        left_dropdown_layout.setContentsMargins(0, 15, 0, 0)
        left_dropdown_layout.setSpacing(
            30
        )  # Match spacing from similarity_parameter_settings (line 185)

        alignment_names = get_algorithm_names("alignment")
        alignment_descs = get_algorithm_descriptions("alignment")
        alignment_display_name = get_category_display_name("alignment")
        self.alignment_dropdown, alignment_widget = self.create_dropdown(
            alignment_display_name, alignment_names, alignment_descs
        )
        left_dropdown_layout.addWidget(alignment_widget)

        super_res_names = get_algorithm_names("super_resolution")
        super_res_descs = get_algorithm_descriptions("super_resolution")
        super_res_display_name = get_category_display_name("super_resolution")
        self.super_resolution_dropdown, super_resolution_widget = self.create_dropdown(
            super_res_display_name, super_res_names, super_res_descs
        )
        left_dropdown_layout.addWidget(super_resolution_widget)

        denoising_names = get_algorithm_names("denoising")
        denoising_descs = get_algorithm_descriptions("denoising")
        denoising_display_name = get_category_display_name("denoising")
        self.denoising_dropdown, denoising_widget = self.create_dropdown(
            denoising_display_name, denoising_names, denoising_descs
        )
        left_dropdown_layout.addWidget(denoising_widget)

        # Add stretch to prevent widgets from spreading vertically
        left_dropdown_layout.addStretch()
        # left_dropdown_layout.addStretch()

        self.parameter_stack = QStackedWidget()
        parameter_pages = ParameterPages(self.parameter_stack)
        self.setting_pages_map = parameter_pages.get_setting_pages_map()
        if "default" not in self.setting_pages_map:
            default_page = QWidget()
            default_layout = QVBoxLayout(default_page)
            default_label = QLabel("Select an algorithm to see its parameters.")
            default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            default_layout.addWidget(default_label)
            default_page_index = self.parameter_stack.addWidget(default_page)
            self.setting_pages_map["default"] = default_page_index

        right_parameter_stack_widget = QWidget()
        right_parameter_stack_layout = QVBoxLayout(right_parameter_stack_widget)
        right_parameter_stack_layout.setContentsMargins(0, 0, 0, 0)
        right_parameter_stack_layout.addWidget(self.parameter_stack)

        main_parameter_area_layout.addWidget(left_dropdown_panel_widget, 1)
        main_parameter_area_layout.addWidget(right_parameter_stack_widget, 2)

        switch_button_panel_layout = QHBoxLayout()
        switch_button_panel_layout.setSpacing(5)

        self.btn_show_alignment_params = QPushButton("Alignment")
        self.btn_show_super_res_params = QPushButton("Super Resolution")
        self.btn_show_denoising_params = QPushButton("Denoising")

        self.parameter_switch_buttons_map = {
            self.btn_show_alignment_params: "alignment",
            # self.btn_show_super_res_params: "super_resolution",
            self.btn_show_denoising_params: "denoising",
        }

        self.switch_button_group = QButtonGroup(self)
        self.switch_button_group.setExclusive(True)

        for btn, source_key in self.parameter_switch_buttons_map.items():
            btn.setStyleSheet(
                SWITCH_BUTTON_DEFAULT_STYLE
            )  # Terapkan style default awal
            btn.setCheckable(True)
            btn.adjustSize()

            self.switch_button_group.addButton(btn)
            switch_button_panel_layout.addWidget(btn)

        # Hubungkan sinyal dari QButtonGroup
        self.switch_button_group.buttonClicked.connect(self.on_switch_button_clicked)

        switch_button_panel_layout.addWidget(self.btn_show_alignment_params)
        # switch_button_panel_layout.addWidget(self.btn_show_super_res_params)
        switch_button_panel_layout.addWidget(self.btn_show_denoising_params)
        switch_button_panel_layout.addStretch()

        parameter_panel_outer_layout.addLayout(switch_button_panel_layout)
        parameter_panel_outer_layout.addLayout(main_parameter_area_layout)

        self.parameter_panel_widget.setLayout(parameter_panel_outer_layout)
        self.parameter_panel_widget.setStyleSheet(stylesheet.PANEL_BACKGROUND_STYLE)
        parent_layout.addWidget(self.parameter_panel_widget)

        # --- Hubungkan Sinyal Dropdown ---
        self.alignment_dropdown.currentIndexChanged.connect(
            lambda: self.handle_dropdown_change_for_source("alignment")
        )
        self.super_resolution_dropdown.currentIndexChanged.connect(
            lambda: self.handle_dropdown_change_for_source("super_resolution")
        )
        self.denoising_dropdown.currentIndexChanged.connect(
            lambda: self.handle_dropdown_change_for_source("denoising")
        )

        # Inisialisasi tampilan awal
        self.btn_show_alignment_params.setChecked(True)
        self.on_switch_button_clicked(self.btn_show_alignment_params)

    def create_dropdown(self, label_text, items, tooltips):
        """Create dropdown using GenericUILibrary FormGroup"""
        # Create FormGroup with select input
        form_group = FormGroup(label=label_text, input_type="select")
        form_group.add_options(items)

        # Add tooltips to the internal QComboBox
        combo = form_group.input  # Access internal QComboBox
        for i, tooltip in enumerate(tooltips):
            combo.setItemData(i, tooltip, Qt.ItemDataRole.ToolTipRole)

        # Return the internal QComboBox and the FormGroup widget
        # This maintains compatibility with existing code
        return combo, form_group

    def handle_dropdown_change_for_source(self, source_category):
        """
        Dipanggil ketika salah satu dropdown utama berubah.
        Ini akan mencoba menampilkan panel parameter yang sesuai DAN mengupdate tombol switch.
        """
        target_button = None
        if source_category == "alignment":
            target_button = self.btn_show_alignment_params
        # elif source_category == "super_resolution":
        #     target_button = self.btn_show_super_res_params
        elif source_category == "denoising":
            target_button = self.btn_show_denoising_params

        block_sr_signals = False
        block_den_signals = False

        if (
            source_category == "denoising"
            and self.denoising_dropdown.currentIndex() != 0
        ):
            if self.super_resolution_dropdown.currentIndex() != 0:
                block_sr_signals = True
                self.super_resolution_dropdown.blockSignals(True)
                self.super_resolution_dropdown.setCurrentIndex(0)
                self.super_resolution_dropdown.blockSignals(False)
        elif (
            source_category == "super_resolution"
            and self.super_resolution_dropdown.currentIndex() != 0
        ):
            if self.denoising_dropdown.currentIndex() != 0:
                block_den_signals = True
                self.denoising_dropdown.blockSignals(True)
                self.denoising_dropdown.setCurrentIndex(0)
                self.denoising_dropdown.blockSignals(False)

        if target_button:
            if not target_button.isChecked():
                target_button.setChecked(
                    True
                )  # Ini akan memanggil on_switch_button_clicked
            else:
                self.on_switch_button_clicked(target_button)

    def on_switch_button_clicked(self, clicked_button):
        source_key = self.parameter_switch_buttons_map.get(clicked_button)
        if not source_key:
            return

        for btn, key in self.parameter_switch_buttons_map.items():
            is_active = btn == clicked_button
            if is_active:
                btn.setStyleSheet(SWITCH_BUTTON_ACTIVE_STYLE)
            else:
                btn.setStyleSheet(SWITCH_BUTTON_DEFAULT_STYLE)

        chosen_text = ""
        dropdown_to_check = None
        if source_key == "alignment":
            dropdown_to_check = self.alignment_dropdown
        elif source_key == "super_resolution":
            dropdown_to_check = self.super_resolution_dropdown
        elif source_key == "denoising":
            dropdown_to_check = self.denoising_dropdown

        if dropdown_to_check:
            chosen_text = dropdown_to_check.currentText()

        is_none_selection = False
        try:
            options_for_key = get_algorithm_options(source_key)
            if options_for_key:
                is_none_selection = chosen_text == options_for_key[0]
        except Exception:
            is_none_selection = True

        if chosen_text in self.setting_pages_map and not is_none_selection:
            self.parameter_stack.setCurrentIndex(self.setting_pages_map[chosen_text])
        else:
            self.parameter_stack.setCurrentIndex(
                self.setting_pages_map.get("default", 0)
            )
