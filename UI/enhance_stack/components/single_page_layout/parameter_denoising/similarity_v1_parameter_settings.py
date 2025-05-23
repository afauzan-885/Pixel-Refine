import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout,
                             QScrollArea, QComboBox, QLineEdit, QPushButton,
                             QFormLayout, QSizePolicy) # Tambahkan QSizePolicy
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt6.QtCore import Qt, QLocale

from UI.resources.stylesheet.stylesheet import (SCROLL_AREA, SLIDER_STYLE, DROPDOWN_BOX,
                                                APPLY_BUTTON, VALUE_EDIT_LABEL) # Tambahkan LINE_EDIT_STYLE
from UI.settings.General.Language import language_config
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

# --- Fungsi Helper ---
def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)

def load_similarity_v1_config():
    defaults = {
        "similarity_V1_tile_size": 24,
        "similarity_V1_motion_sensitivity": 110.0,
        "similarity_V1_noise_mad_offset_factor": 0.3,
        "similarity_V1_overlap_percent": 0.35,
        "use_multi_core": True,
    }
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f:
                all_params = json.load(f)
            if "Similarity" in all_params and isinstance(all_params.get("Similarity"), dict):
                loaded_config = all_params["Similarity"]
                config_to_use = defaults.copy()
                config_to_use.update(loaded_config)
                return config_to_use
    except (IOError, json.JSONDecodeError):
        pass
    return defaults.copy()

def save_similarity_v1_config(config): # config di sini sudah berisi "similarity_V1_tile_size" sebagai int
    """Menyimpan konfigurasi Similarity V1 ke Parameter_Stack_Enhance.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE
    all_params = {}
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params = json.load(f)
    except Exception:
        pass

    if "Similarity" not in all_params or not isinstance(all_params.get("Similarity"), dict):
        all_params["Similarity"] = {}

    all_params["Similarity"].update(config)

    if "tileGridSize" in all_params["Similarity"]:
        del all_params["Similarity"]["tileGridSize"]

    try:
        with open(config_filename, "w") as f:
            json.dump(all_params, f, indent=4)
    except Exception:
      pass
  
def create_slider_with_input(label_text, min_val, max_val, initial_value_slider, initial_value_text,
                             slider_multiplier, text_format_func, validator, tooltip, parent_layout, c_locale,
                             slider_min_val=None, slider_max_val=None):
    label = QLabel(label_text)
    label.setToolTip(tooltip)
    label.setFont(get_default_font(10, QFont.Weight.Bold)) # Sedikit lebih kecil & bold

    slider = QSlider(Qt.Orientation.Horizontal)
    actual_slider_min = slider_min_val if slider_min_val is not None else min_val
    actual_slider_max = slider_max_val if slider_max_val is not None else max_val
    slider.setMinimum(actual_slider_min)
    slider.setMaximum(actual_slider_max)
    slider.setValue(initial_value_slider)
    slider.setStyleSheet(SLIDER_STYLE)
    slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


    line_edit = QLineEdit(initial_value_text)
    line_edit.setStyleSheet(VALUE_EDIT_LABEL)
    line_edit.setFixedWidth(50 if isinstance(validator, QDoubleValidator) else 40) # Lebar disesuaikan
    line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
    if isinstance(validator, QDoubleValidator):
        line_edit.setLocale(c_locale)
    line_edit.setValidator(validator)

    layout = QHBoxLayout()
    layout.addWidget(slider, 1)
    layout.addSpacing(10)       
    layout.addWidget(line_edit)

    if "Overlap" in label_text:
        percent_label = QLabel("%")
        percent_label.setFont(get_default_font(9))
        layout.addSpacing(3) 
        layout.addWidget(percent_label)

    parent_layout.addRow(label, layout)
    return slider, line_edit

def get_similarity_v1_settings_page():
    sim_v1_config = load_similarity_v1_config() 
    original_v1_defaults = {
        "similarity_V1_tile_size": 24, 
        "similarity_V1_motion_sensitivity": 110.0,
        "similarity_V1_noise_mad_offset_factor": 0.3,
        "similarity_V1_overlap_percent": 0.35,
    }

    page_widget = QWidget()
    main_layout = QVBoxLayout(page_widget)
    main_layout.setSpacing(0) # Sedikit lebih banyak spasi antar grup
    main_layout.setContentsMargins(10,10,10,10)


    title_label = QLabel(getattr(language_config, 'SIMILARITY_V1_GROUP_TITLE', "Similarity V1 Parameters"))
    title_label.setFont(get_default_font(10, QFont.Weight.Bold)) # Font judul lebih besar
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("margin-bottom: 10px;") # Beri jarak bawah
    main_layout.addWidget(title_label)

    form_layout = QFormLayout()
    form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
    form_layout.setContentsMargins(0, 0, 0, 0) 
    form_layout.setSpacing(12)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form_layout.setHorizontalSpacing(20)

    widgets = {}
    c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)

    # 1. Tile Size
    tile_size_label_text = getattr(language_config, 'TILE_SIZE_LABEL', "Tile Size (tile):")
    tile_size_label = QLabel(tile_size_label_text)
    tile_size_label.setFont(get_default_font(9, QFont.Weight.DemiBold))
    tile_size_label.setToolTip(getattr(language_config, 'TILE_SIZE_DESCRIPTION', 'Size of the processing tiles.'))
    tile_size_combo = QComboBox()
    tile_options_int = [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256]
    tile_size_combo.addItems([str(size) for size in tile_options_int])
    
    # Ambil nilai tile dari config (sekarang integer)
    initial_tile_size_int = sim_v1_config.get("similarity_V1_tile_size", 24) # <--- PERUBAHAN: Gunakan key "similarity_V1_tile_size"
    
    tile_size_combo.setCurrentText(str(initial_tile_size_int))
    tile_size_combo.setStyleSheet(DROPDOWN_BOX + "QComboBox { padding: 4px 6px; min-height: 20px; }")
    tile_size_combo.setMinimumWidth(100)
    form_layout.addRow(tile_size_label, tile_size_combo)
    widgets['tile_combo'] = tile_size_combo
    
    # Overlap Percent
    overlap_label_text = getattr(language_config, 'OVERLAP_LABEL', "Overlap %:")
    initial_overlap_ratio_v1 = sim_v1_config.get("similarity_V1_overlap_percent", 0.35)
    initial_overlap_percent_v1 = int(round(initial_overlap_ratio_v1 * 100))
    overlap_validator_v1 = QIntValidator(0, 90)
    slider_ov, input_ov = create_slider_with_input(
        overlap_label_text, 0, 90,
        initial_overlap_percent_v1,
        str(initial_overlap_percent_v1),
        1.0,
        lambda v, m=1, loc=c_locale: str(int(v)),
        overlap_validator_v1,
        getattr(language_config, 'OVERLAP_DESCRIPTION', 'Percentage of overlap between tiles.'),
        form_layout, c_locale
    )
    widgets['overlap_slider'] = slider_ov
    widgets['overlap_input'] = input_ov

    # 2. Motion Sensitivity
    motion_sens_label_text = getattr(language_config, 'MOTION_THRESHOLD_LABEL', "Motion Sensitivity:")
    initial_motion_sens_v1 = sim_v1_config.get("similarity_V1_motion_sensitivity", 110.0)
    motion_sens_multiplier_v1 = 10.0
    motion_sens_slider_min_v1, motion_sens_slider_max_v1 = 10, 2000
    motion_sens_validator_v1 = QDoubleValidator(0.1, 200.0, 1)
    motion_sens_validator_v1.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_ms, input_ms = create_slider_with_input(
        motion_sens_label_text, 0, 0, # min/max slider akan di-set di create_slider_with_input
        int(round(initial_motion_sens_v1 * motion_sens_multiplier_v1)),
        c_locale.toString(initial_motion_sens_v1, 'f', 1),
        motion_sens_multiplier_v1,
        lambda v, m=motion_sens_multiplier_v1, loc=c_locale: loc.toString(v / m, 'f', 1),
        motion_sens_validator_v1,
        getattr(language_config, 'MOTION_THRESHOLD_DESCRIPTION', 'Controls sensitivity to motion. Higher values are more sensitive.'),
        form_layout, c_locale,
        slider_min_val=motion_sens_slider_min_v1, slider_max_val=motion_sens_slider_max_v1
    )
    widgets['motion_sensitivity_slider'] = slider_ms
    widgets['motion_sensitivity_input'] = input_ms

    # 3. Noise MAD Offset Factor
    noise_mad_label_text = getattr(language_config, 'NOISE_MAD_OFFSET_LABEL_V1', "Noise Offset Factor:")
    initial_noise_mad_v1 = sim_v1_config.get("similarity_V1_noise_mad_offset_factor", 0.3)
    noise_mad_multiplier_v1 = 100.0
    noise_mad_slider_min_v1, noise_mad_slider_max_v1 = 0, 100
    noise_mad_validator_v1 = QDoubleValidator(0.0, 5.0, 2)
    noise_mad_validator_v1.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_nm, input_nm = create_slider_with_input(
        noise_mad_label_text, 0, 0,
        int(round(initial_noise_mad_v1 * noise_mad_multiplier_v1)),
        c_locale.toString(initial_noise_mad_v1, 'f', 2),
        noise_mad_multiplier_v1,
        lambda v, m=noise_mad_multiplier_v1, loc=c_locale: loc.toString(v / m, 'f', 2),
        noise_mad_validator_v1,
        getattr(language_config, 'NOISE_MAD_OFFSET_DESCRIPTION_V1', 'Factor for noise MAD offset adjustment.'),
        form_layout, c_locale,
        slider_min_val=noise_mad_slider_min_v1, slider_max_val=noise_mad_slider_max_v1
    )
    widgets['noise_mad_offset_slider'] = slider_nm
    widgets['noise_mad_offset_input'] = input_nm

    def setup_slider_input_connections(slider, line_edit, multiplier, min_actual, max_actual, locale_obj, format_digits, is_float=True, slider_min_val_raw=None, slider_max_val_raw=None):
        slider.valueChanged.connect(
            lambda value, inp=line_edit, m=multiplier, loc=locale_obj, d=format_digits, f=is_float:
                inp.setText(loc.toString(value / m, 'f', d) if f else str(int(round(value / m)))) # round untuk int
        )
        def update_slider_from_input():
            current_locale = line_edit.locale() if is_float else None
            try:
                if is_float: value_actual, ok = current_locale.toDouble(line_edit.text()); assert ok
                else: value_actual = int(line_edit.text())
                value_actual = max(min_actual, min(value_actual, max_actual))
                slider_value_target = int(round(value_actual * multiplier))
                s_min = slider_min_val_raw if slider_min_val_raw is not None else int(round(min_actual * multiplier))
                s_max = slider_max_val_raw if slider_max_val_raw is not None else int(round(max_actual * multiplier))
                slider_value_clamped = max(s_min, min(slider_value_target, s_max))
                slider.blockSignals(True); slider.setValue(slider_value_clamped); slider.blockSignals(False)
                line_edit.setText(current_locale.toString(value_actual, 'f', format_digits) if is_float else str(int(value_actual)))
            except (ValueError, AssertionError):
                current_slider_val = slider.value()
                line_edit.setText(current_locale.toString(current_slider_val / multiplier, 'f', format_digits) if is_float else str(int(round(current_slider_val / multiplier))))
        line_edit.editingFinished.connect(update_slider_from_input)

    setup_slider_input_connections(slider_ms, input_ms, motion_sens_multiplier_v1, 0.1, 200.0, c_locale, 1, True, motion_sens_slider_min_v1, motion_sens_slider_max_v1)
    setup_slider_input_connections(slider_nm, input_nm, noise_mad_multiplier_v1, 0.0, 5.0, c_locale, 2, True, noise_mad_slider_min_v1, noise_mad_slider_max_v1)
    setup_slider_input_connections(slider_ov, input_ov, 1.0, 0, 90, c_locale, 0, False)

    main_layout.addLayout(form_layout)

    reset_button = QPushButton("Reset to Defaults")
    reset_button.setStyleSheet(APPLY_BUTTON)
    reset_button.setMinimumHeight(30)
    # reset_button.setFixedWidth(150) # Beri lebar tetap agar tidak terlalu lebar

    def reset_similarity_v1_defaults():
        defaults = original_v1_defaults
        default_tile = defaults.get("tileGridSize", [24,24])[0]
        
        widgets['tile_combo'].setCurrentText(str(default_tile))
        default_ms = defaults.get("similarity_V1_motion_sensitivity", 110.0)
        widgets['motion_sensitivity_slider'].setValue(int(round(default_ms * motion_sens_multiplier_v1)))
        
        default_nm = defaults.get("similarity_V1_noise_mad_offset_factor", 0.3)
        widgets['noise_mad_offset_slider'].setValue(int(round(default_nm * noise_mad_multiplier_v1)))
        
        default_ov_ratio = defaults.get("similarity_V1_overlap_percent", 0.35)
        default_ov_percent = int(round(default_ov_ratio * 100))
        widgets['overlap_slider'].setValue(default_ov_percent)
        
        save_current_settings_v1()

    reset_button.clicked.connect(reset_similarity_v1_defaults)
    
    reset_button_layout = QHBoxLayout()
    reset_button_layout.addStretch()
    reset_button_layout.setContentsMargins(0, 10, 0, 0)
    reset_button_layout.addWidget(reset_button)
    main_layout.addLayout(reset_button_layout)


    def save_current_settings_v1():
        try:
            similarity_V1_tile_size = int(widgets['tile_combo'].currentText())
            motion_sensitivity, _ = c_locale.toDouble(widgets['motion_sensitivity_input'].text())
            noise_mad_offset, _ = c_locale.toDouble(widgets['noise_mad_offset_input'].text())
            overlap_percent = int(widgets['overlap_input'].text())
            overlap_ratio = overlap_percent / 100.0
        except ValueError as e:
            return

        general_settings_for_algo = {}
        try:
            if os.path.exists(GENERAL_SETTINGS_FILE):
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    general_settings_for_algo = json.load(f)
        except: pass

        sim_v1_params_to_save = {
            "tileGridSize": [similarity_V1_tile_size, similarity_V1_tile_size],
            "similarity_V1_motion_sensitivity": motion_sensitivity,
            "similarity_V1_noise_mad_offset_factor": noise_mad_offset,
            "similarity_V1_overlap_percent": overlap_ratio,
            "use_multi_core": general_settings_for_algo.get("multi_core_cpu", True),
        }
        save_similarity_v1_config(sim_v1_params_to_save)

    widgets['tile_combo'].currentIndexChanged.connect(save_current_settings_v1)
    widgets['motion_sensitivity_slider'].sliderReleased.connect(save_current_settings_v1)
    widgets['motion_sensitivity_input'].editingFinished.connect(save_current_settings_v1)
    widgets['noise_mad_offset_slider'].sliderReleased.connect(save_current_settings_v1)
    widgets['noise_mad_offset_input'].editingFinished.connect(save_current_settings_v1)
    widgets['overlap_slider'].sliderReleased.connect(save_current_settings_v1)
    widgets['overlap_input'].editingFinished.connect(save_current_settings_v1)

    main_layout.addStretch(1)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page_widget)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll