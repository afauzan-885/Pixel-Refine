import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout,
                             QScrollArea, QComboBox, QLineEdit, QPushButton,
                             QFormLayout, QSizePolicy)
from PySide6.QtGui import QFont, QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt, QLocale

from resources.styles.stylesheet import (SCROLL_AREA, SLIDER_STYLE, DROPDOWN_BOX,
                                                APPLY_BUTTON, VALUE_EDIT_LABEL)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)

def load_similarity_v2_config():
    """Memuat konfigurasi Similarity V2 dari Parameter_Stack_Enhance.json."""
    defaults = {
        "similarity_v2_tile_size": 32,
        "similarity_v2_overlap_percent": 38.0,
        "similarity_v2_mbm_noise_mad_offset_factor": 0.65,
        "similarity_v2_mbm_mad_sensitivity": 18.8,
        "similarity_v2_mbm_confidence_skip_dft_threshold": 0.30,
        "similarity_v2_freq_merge_wiener_c_factor": 4.0,
        "use_gpu": False, 
    }
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f:
                all_params = json.load(f)
            if "Similarity_V2" in all_params and isinstance(all_params.get("Similarity_V2"), dict):
                loaded_config = all_params["Similarity_V2"]
                config_to_use = defaults.copy()
                
                if "overlapRatio" in loaded_config:
                    loaded_config["similarity_v2_overlap_percent"] = round(loaded_config["overlapRatio"] * 100)
                   
                for key in defaults.keys():
                    if key in loaded_config:
                        config_to_use[key] = loaded_config[key]
                return config_to_use
    except (IOError, json.JSONDecodeError):
        pass
    return defaults.copy()

def save_similarity_v2_config(config):
    """Menyimpan konfigurasi Similarity V2 ke Parameter_Stack_Enhance.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE
    all_params = {}
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params = json.load(f)
    except Exception:
        pass

    if "Similarity_V2" not in all_params or not isinstance(all_params.get("Similarity_V2"), dict):
        all_params["Similarity_V2"] = {}

    config_to_save = config.copy()

    if "similarity_v2_overlap_percent" in config_to_save:
        config_to_save["overlapRatio"] = config_to_save["similarity_v2_overlap_percent"] / 100.0
        del config_to_save["similarity_v2_overlap_percent"] 

    if "similarity_v2_tile_size" in config_to_save: 
        config_to_save["tile_size"] = config_to_save["similarity_v2_tile_size"] # Key untuk JSON
        del config_to_save["similarity_v2_tile_size"]
    if "tileGridSize" in config_to_save:
        del config_to_save["tileGridSize"]


    all_params["Similarity_V2"].update(config_to_save)
    
    try:
        with open(config_filename, "w") as f:
            json.dump(all_params, f, indent=4)
    except Exception:
      pass

# Fungsi create_slider_with_input tetap sama seperti di similarity_v1_settings_ui.py
def create_slider_with_input(label_text, min_val, max_val, initial_value_slider, initial_value_text,
                             slider_multiplier, text_format_func, validator, tooltip, parent_layout, c_locale,
                             slider_min_val=None, slider_max_val=None):
    label = QLabel(label_text)
    label.setToolTip(tooltip)
    label.setFont(get_default_font(10, QFont.Weight.Bold))
    slider = QSlider(Qt.Orientation.Horizontal)
    actual_slider_min = slider_min_val if slider_min_val is not None else min_val
    actual_slider_max = slider_max_val if slider_max_val is not None else max_val
    slider.setMinimum(actual_slider_min); slider.setMaximum(actual_slider_max)
    slider.setValue(initial_value_slider); slider.setStyleSheet(SLIDER_STYLE)
    slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    line_edit = QLineEdit(initial_value_text)
    line_edit.setStyleSheet(VALUE_EDIT_LABEL) # Ganti LINE_EDIT_STYLE dengan VALUE_EDIT_LABEL jika itu yang benar
    line_edit.setFixedWidth(55 if isinstance(validator, QDoubleValidator) else 45)
    line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
    if isinstance(validator, QDoubleValidator): line_edit.setLocale(c_locale)
    line_edit.setValidator(validator)
    layout = QHBoxLayout(); layout.addWidget(slider, 1); layout.addSpacing(10); layout.addWidget(line_edit)
    if "Overlap" in label_text:
        percent_label = QLabel("%"); percent_label.setFont(get_default_font(9)); layout.addSpacing(3); layout.addWidget(percent_label)
    parent_layout.addRow(label, layout)
    return slider, line_edit


def get_similarity_v2_settings_page():
    sim_v2_config = load_similarity_v2_config()
    original_v2_defaults = { 
        "similarity_v2_tile_size": 32,
        "similarity_v2_overlap_percent": 38.0,
        "similarity_v2_mbm_noise_mad_offset_factor": 0.65,
        "similarity_v2_mbm_mad_sensitivity": 18.8,
        "similarity_v2_mbm_confidence_skip_dft_threshold": 0.30,
        "similarity_v2_freq_merge_wiener_c_factor": 4.0,
    }

    page_widget = QWidget()
    main_layout = QVBoxLayout(page_widget)
    main_layout.setSpacing(0)
    main_layout.setContentsMargins(10,10,10,10)

    title_label = QLabel(getattr(language_config, 'SIMILARITY_V2_GROUP_TITLE', "Similarity V2 Parameters"))
    title_label.setFont(get_default_font(10, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("margin-bottom: 10px;")
    main_layout.addWidget(title_label)

    form_layout = QFormLayout()
    form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
    form_layout.setContentsMargins(0, 0, 0, 0); form_layout.setSpacing(12)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft); form_layout.setHorizontalSpacing(20)

    widgets = {}
    c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)

    # 1. Tile Size V2
    tile_size_label_text = getattr(language_config, 'TILE_SIZE_LABEL', "Tile Size (tile):")
    tile_size_label = QLabel(tile_size_label_text)
    tile_size_label.setFont(get_default_font(9, QFont.Weight.DemiBold))
    tile_size_label.setToolTip(getattr(language_config, 'TILE_SIZE_DESCRIPTION', 'Size of the processing tiles.'))
    tile_size_combo = QComboBox()
    tile_options_int = [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256]
    tile_size_combo.addItems([str(size) for size in tile_options_int])
    initial_tile_size_int = sim_v2_config.get("similarity_v2_tile_size", 32)
    tile_size_combo.setCurrentText(str(initial_tile_size_int))
    tile_size_combo.setStyleSheet(DROPDOWN_BOX)
    tile_size_combo.setMinimumWidth(100)
    form_layout.addRow(tile_size_label, tile_size_combo)
    widgets['tile_combo'] = tile_size_combo

    # 2. Overlap Percent V2
    overlap_label_text = getattr(language_config, 'OVERLAP_LABEL', "Overlap %:")
    initial_overlap_percent_v2 = sim_v2_config.get("similarity_v2_overlap_percent", 35.0)
    overlap_validator_v2 = QIntValidator(0, 90)
    slider_ov, input_ov = create_slider_with_input(
        overlap_label_text, 0, 90, int(round(initial_overlap_percent_v2)),
        str(int(round(initial_overlap_percent_v2))), 1.0,
        lambda v, m=1, loc=c_locale: str(int(v)), overlap_validator_v2,
        getattr(language_config, 'OVERLAP_DESCRIPTION', 'Percentage of overlap between tiles.'),
        form_layout, c_locale
    )
    widgets['overlap_slider'] = slider_ov
    widgets['overlap_input'] = input_ov

    # 3. MBM Noise MAD Offset Factor V2
    noise_mad_label_text = getattr(language_config, 'NOISE_MAD_OFFSET_LABEL', "Noise MAD Offset Factor:")
    initial_val = sim_v2_config.get("similarity_v2_mbm_noise_mad_offset_factor", 0.65)
    multiplier = 100.0; slider_min, slider_max = 0, 200; validator = QDoubleValidator(0.0, 5.0, 2)
    validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_nm, input_nm = create_slider_with_input(
        noise_mad_label_text, 0,0, int(round(initial_val * multiplier)), c_locale.toString(initial_val, 'f', 2),
        multiplier, lambda v, m=multiplier, loc=c_locale: loc.toString(v/m, 'f', 2), validator,
        getattr(language_config, 'NOISE_MAD_OFFSET_DESCRIPTION', 'Factor for noise MAD offset.'),
        form_layout, c_locale, slider_min_val=slider_min, slider_max_val=slider_max
    )
    widgets['noise_mad_offset_slider'] = slider_nm
    widgets['noise_mad_offset_input'] = input_nm

    # 4. MBM MAD Sensitivity V2
    mad_sens_label_text = getattr(language_config, 'MAD_SENSITIVITY_LABEL', "MAD Sensitivity:")
    initial_val = sim_v2_config.get("similarity_v2_mbm_mad_sensitivity", 18.8)
    multiplier = 10.0; slider_min, slider_max = 10, 500; validator = QDoubleValidator(0.1, 100.0, 1)
    validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_ms, input_ms = create_slider_with_input(
        mad_sens_label_text, 0,0, int(round(initial_val * multiplier)), c_locale.toString(initial_val, 'f', 1),
        multiplier, lambda v, m=multiplier, loc=c_locale: loc.toString(v/m, 'f', 1), validator,
        getattr(language_config, 'MAD_SENSITIVITY_DESCRIPTION', 'Sensitivity for MBM MAD calculation.'),
        form_layout, c_locale, slider_min_val=slider_min, slider_max_val=slider_max
    )
    widgets['mad_sensitivity_slider'] = slider_ms
    widgets['mad_sensitivity_input'] = input_ms

    # 5. MBM Confidence Skip DFT Threshold V2
    conf_skip_label_text = getattr(language_config, 'CONF_SKIP_DFT_LABEL', "Conf. Skip DFT Thresh:")
    initial_val = sim_v2_config.get("similarity_v2_mbm_confidence_skip_dft_threshold", 0.78)
    multiplier = 100.0; slider_min, slider_max = 1, 200; validator = QDoubleValidator(0.01, 2.0, 2) # Range 0.01 - 1.00
    validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_cs, input_cs = create_slider_with_input(
        conf_skip_label_text, 0,0, int(round(initial_val * multiplier)), c_locale.toString(initial_val, 'f', 2),
        multiplier, lambda v, m=multiplier, loc=c_locale: loc.toString(v/m, 'f', 2), validator,
        getattr(language_config, 'CONF_SKIP_DFT_DESCRIPTION', 'MBM confidence threshold to skip DFT merging.'),
        form_layout, c_locale, slider_min_val=slider_min, slider_max_val=slider_max
    )
    widgets['conf_skip_slider'] = slider_cs
    widgets['conf_skip_input'] = input_cs

    # 6. Freq Merge Wiener C Factor V2
    wiener_c_label_text = getattr(language_config, 'WIENER_C_FACTOR_LABEL', "Wiener C Factor:")
    initial_val = sim_v2_config.get("similarity_v2_freq_merge_wiener_c_factor", 2.1)
    multiplier = 10.0; slider_min, slider_max = 1, 1000; validator = QDoubleValidator(0.1, 100.0, 1)
    validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_wc, input_wc = create_slider_with_input(
        wiener_c_label_text, 0,0, int(round(initial_val * multiplier)), c_locale.toString(initial_val, 'f', 1),
        multiplier, lambda v, m=multiplier, loc=c_locale: loc.toString(v/m, 'f', 1), validator,
        getattr(language_config, 'WIENER_C_FACTOR_DESCRIPTION', 'C factor for Wiener filter in frequency merging.'),
        form_layout, c_locale, slider_min_val=slider_min, slider_max_val=slider_max
    )
    widgets['wiener_c_slider'] = slider_wc
    widgets['wiener_c_input'] = input_wc

    # --- Koneksi dua arah untuk semua slider & input V2 ---
    def setup_slider_input_connections_v2(slider, line_edit, multiplier, min_actual, max_actual, locale_obj, format_digits, is_float=True, slider_min_val_raw=None, slider_max_val_raw=None):
        slider.valueChanged.connect(
            lambda value, inp=line_edit, m=multiplier, loc=locale_obj, d=format_digits, f=is_float:
                inp.setText(loc.toString(value / m, 'f', d) if f else str(int(round(value / m))))
        )
        def update_slider_from_input_v2(): # Nama unik
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
        line_edit.editingFinished.connect(update_slider_from_input_v2)

    setup_slider_input_connections_v2(widgets['overlap_slider'], widgets['overlap_input'], 1.0, 0, 90, c_locale, 0, False)
    setup_slider_input_connections_v2(widgets['noise_mad_offset_slider'], widgets['noise_mad_offset_input'], 100.0, 0.0, 5.0, c_locale, 2, True, 0, 200)
    setup_slider_input_connections_v2(widgets['mad_sensitivity_slider'], widgets['mad_sensitivity_input'], 10.0, 0.1, 100.0, c_locale, 1, True, 10, 500)
    setup_slider_input_connections_v2(widgets['conf_skip_slider'], widgets['conf_skip_input'], 100.0, 0.01, 1.0, c_locale, 2, True, 1, 100)
    setup_slider_input_connections_v2(widgets['wiener_c_slider'], widgets['wiener_c_input'], 10.0, 0.1, 100.0, c_locale, 1, True, 1, 1000)


    main_layout.addLayout(form_layout)

    reset_button = QPushButton(getattr(language_config, 'RESET_TO_DEFAULTS_BUTTON_TEXT', "Reset to Default"))
    reset_button.setStyleSheet(APPLY_BUTTON)
    reset_button.setMinimumHeight(30)

    def reset_similarity_v2_defaults():
        defaults = original_v2_defaults
        widgets['tile_combo'].setCurrentText(str(defaults.get("similarity_v2_tile_size")))
        widgets['overlap_slider'].setValue(int(round(defaults.get("similarity_v2_overlap_percent"))))
        widgets['noise_mad_offset_slider'].setValue(int(round(defaults.get("similarity_v2_mbm_noise_mad_offset_factor") * 100.0)))
        widgets['mad_sensitivity_slider'].setValue(int(round(defaults.get("similarity_v2_mbm_mad_sensitivity") * 10.0)))
        widgets['conf_skip_slider'].setValue(int(round(defaults.get("similarity_v2_mbm_confidence_skip_dft_threshold") * 100.0)))
        widgets['wiener_c_slider'].setValue(int(round(defaults.get("similarity_v2_freq_merge_wiener_c_factor") * 10.0)))
        save_current_settings_v2() # Simpan setelah reset

    reset_button.clicked.connect(reset_similarity_v2_defaults)
    reset_button_layout = QHBoxLayout()
    reset_button_layout.addStretch()
    reset_button_layout.setContentsMargins(0, 10, 0, 0)
    reset_button_layout.addWidget(reset_button)
    main_layout.addLayout(reset_button_layout)

    def save_current_settings_v2():
        try:
            tile_size = int(widgets['tile_combo'].currentText())
            overlap_percent, _ = c_locale.toDouble(widgets['overlap_input'].text()) # Seharusnya int
            noise_mad_offset, _ = c_locale.toDouble(widgets['noise_mad_offset_input'].text())
            mad_sensitivity, _ = c_locale.toDouble(widgets['mad_sensitivity_input'].text())
            conf_skip_dft, _ = c_locale.toDouble(widgets['conf_skip_input'].text())
            wiener_c_factor, _ = c_locale.toDouble(widgets['wiener_c_input'].text())
        except ValueError as e:
            print(f"Error parsing Similarity V2 settings for save: {e}")
            return

        general_settings_for_algo = {}
        try:
            if os.path.exists(GENERAL_SETTINGS_FILE):
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    general_settings_for_algo = json.load(f)
        except: pass

        sim_v2_params_to_save = {
            "similarity_v2_tile_size": tile_size, # Disimpan sebagai int
            "similarity_v2_overlap_percent": float(widgets['overlap_input'].text()), # Disimpan sebagai float persen
            "similarity_v2_mbm_noise_mad_offset_factor": noise_mad_offset,
            "similarity_v2_mbm_mad_sensitivity": mad_sensitivity,
            "similarity_v2_mbm_confidence_skip_dft_threshold": conf_skip_dft,
            "similarity_v2_freq_merge_wiener_c_factor": wiener_c_factor,
            "use_multi_core": general_settings_for_algo.get("multi_core_cpu", True),
            "use_gpu": general_settings_for_algo.get("gpu_acceleration", False),
        }
        save_similarity_v2_config(sim_v2_params_to_save)

    widgets['tile_combo'].currentIndexChanged.connect(save_current_settings_v2)
    widgets['overlap_slider'].sliderReleased.connect(save_current_settings_v2)
    widgets['overlap_input'].editingFinished.connect(save_current_settings_v2)
    widgets['noise_mad_offset_slider'].sliderReleased.connect(save_current_settings_v2)
    widgets['noise_mad_offset_input'].editingFinished.connect(save_current_settings_v2)
    widgets['mad_sensitivity_slider'].sliderReleased.connect(save_current_settings_v2)
    widgets['mad_sensitivity_input'].editingFinished.connect(save_current_settings_v2)
    widgets['conf_skip_slider'].sliderReleased.connect(save_current_settings_v2)
    widgets['conf_skip_input'].editingFinished.connect(save_current_settings_v2)
    widgets['wiener_c_slider'].sliderReleased.connect(save_current_settings_v2)
    widgets['wiener_c_input'].editingFinished.connect(save_current_settings_v2)

    main_layout.addStretch(1)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page_widget)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll