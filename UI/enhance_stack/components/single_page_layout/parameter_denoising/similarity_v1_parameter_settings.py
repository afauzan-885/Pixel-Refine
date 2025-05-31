import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout,
                             QScrollArea, QComboBox, QLineEdit, QPushButton,
                             QFormLayout, QSizePolicy, QToolButton) # QGroupBox tidak jadi dipakai, QWidget cukup
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt6.QtCore import Qt, QLocale

from UI.resources.stylesheet.stylesheet import (SCROLL_AREA, SLIDER_STYLE, DROPDOWN_BOX,
                                                APPLY_BUTTON, VALUE_EDIT_LABEL, TOGGLE_BUTTON)
from UI.settings.General.Language import language_config
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

# --- Fungsi Helper ---
def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)

def load_similarity_v1_config():
    # Default untuk struktur baru
    defaults = {
        "similarity_V1_merging_type": "spatial",
        "use_multi_core": True,
        "spatial_params": {
            "similarity_V1_tile_size": 16,
            "similarity_V1_motion_sensitivity": 110.0,
            "similarity_V1_noise_mad_offset_factor": 0.3,
            "similarity_V1_overlap_percent": 0.4,
        },
        "frequency_params": {
            "similarity_V1_freq_c_wiener_factor": 5.0,
            "similarity_V1_freq_tile_size": 32,
            "similarity_V1_freq_overlap_percent": 0.25,
        }
    }
    final_config = {
        "similarity_V1_merging_type": defaults["similarity_V1_merging_type"],
        "use_multi_core": defaults["use_multi_core"],
        **defaults["spatial_params"],
        **defaults["frequency_params"]
    }
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f:
                all_params_file = json.load(f)
            if "Similarity" in all_params_file and isinstance(all_params_file.get("Similarity"), dict):
                loaded_similarity_section = all_params_file["Similarity"]
                if "similarity_V1_merging_type" in loaded_similarity_section:
                    final_config["similarity_V1_merging_type"] = loaded_similarity_section["similarity_V1_merging_type"]
                if "use_multi_core" in loaded_similarity_section:
                    final_config["use_multi_core"] = loaded_similarity_section["use_multi_core"]
                if "spatial_params" in loaded_similarity_section and isinstance(loaded_similarity_section["spatial_params"], dict):
                    for key, value in defaults["spatial_params"].items():
                        final_config[key] = loaded_similarity_section["spatial_params"].get(key, value)
                else:
                    for key, value in defaults["spatial_params"].items():
                         final_config[key] = loaded_similarity_section.get(key, value)
                if "frequency_params" in loaded_similarity_section and isinstance(loaded_similarity_section["frequency_params"], dict):
                    for key, value in defaults["frequency_params"].items():
                        final_config[key] = loaded_similarity_section["frequency_params"].get(key, value)
                else:
                    for key, value in defaults["frequency_params"].items():
                         final_config[key] = loaded_similarity_section.get(key, value)
                return final_config
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading Similarity config: {e}. Using defaults.")
    return final_config

def save_similarity_v1_config(config_to_save):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE
    all_params_file = {}
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params_file = json.load(f)
    except Exception: pass
    if "Similarity" not in all_params_file or not isinstance(all_params_file.get("Similarity"), dict):
        all_params_file["Similarity"] = {}
    similarity_section_to_save = {
        "similarity_V1_merging_type": config_to_save.get("similarity_V1_merging_type", "spatial"),
        "use_multi_core": config_to_save.get("use_multi_core", True),
        "spatial_params": {},
        "frequency_params": {}
    }
    spatial_keys = ["similarity_V1_tile_size", "similarity_V1_motion_sensitivity",
                    "similarity_V1_noise_mad_offset_factor", "similarity_V1_overlap_percent"]
    for key in spatial_keys:
        if key in config_to_save:
            similarity_section_to_save["spatial_params"][key] = config_to_save[key]
    frequency_keys = ["similarity_V1_freq_c_wiener_factor", "similarity_V1_freq_tile_size",
                      "similarity_V1_freq_overlap_percent"]
    for key in frequency_keys:
        if key in config_to_save:
            similarity_section_to_save["frequency_params"][key] = config_to_save[key]
    all_params_file["Similarity"] = similarity_section_to_save
    try:
        with open(config_filename, "w") as f:
            json.dump(all_params_file, f, indent=4)
    except Exception as e:
      print(f"Error saving Similarity config: {e}")

def create_slider_with_input(label_text, min_val, max_val, initial_value_slider, initial_value_text,
                             slider_multiplier, text_format_func, validator, tooltip, parent_layout, c_locale,
                             slider_min_val=None, slider_max_val=None):
    label = QLabel(label_text)
    label.setToolTip(tooltip)
    label.setFont(get_default_font(10, QFont.Weight.Bold))
    slider = QSlider(Qt.Orientation.Horizontal)
    actual_slider_min = slider_min_val if slider_min_val is not None else min_val
    actual_slider_max = slider_max_val if slider_max_val is not None else max_val
    slider.setMinimum(int(actual_slider_min))
    slider.setMaximum(int(actual_slider_max))
    slider.setValue(int(initial_value_slider))
    slider.setStyleSheet(SLIDER_STYLE)
    slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    line_edit = QLineEdit(initial_value_text)
    line_edit.setStyleSheet(VALUE_EDIT_LABEL)
    line_edit.setFixedWidth(50 if isinstance(validator, QDoubleValidator) else 40)
    line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
    if isinstance(validator, QDoubleValidator):
        line_edit.setLocale(c_locale)
    line_edit.setValidator(validator)
    layout = QHBoxLayout()
    layout.addWidget(slider, 1)
    layout.addSpacing(10)
    layout.addWidget(line_edit)
    if "Overlap" in label_text or "Overlap %" in label_text :
        percent_label = QLabel("%")
        percent_label.setFont(get_default_font(9))
        layout.addSpacing(3)
        layout.addWidget(percent_label)
    parent_layout.addRow(label, layout)
    return slider, line_edit

def get_similarity_v1_settings_page():
    sim_v1_config = load_similarity_v1_config()
    
    original_v1_ui_defaults = {
        "similarity_V1_merging_type": "spatial", # Ini tidak direset oleh tombol spesifik
        "similarity_V1_tile_size": 16,
        "similarity_V1_motion_sensitivity": 120.5,
        "similarity_V1_noise_mad_offset_factor": 0.2,
        "similarity_V1_overlap_percent": 0.38,
        "similarity_V1_freq_c_wiener_factor": 5.0,
        "similarity_V1_freq_tile_size": 16,
        "similarity_V1_freq_overlap_percent": 0.25,
    }

    page_widget = QWidget()
    main_layout = QVBoxLayout(page_widget)
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(10,10,10,10)

    title_label = QLabel(getattr(language_config, 'SIMILARITY_V1_GROUP_TITLE', "Similarity V1 Parameters"))
    title_label.setFont(get_default_font(11, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("margin-bottom: 10px;")
    main_layout.addWidget(title_label)

    spatial_params_container = QWidget()
    spatial_params_layout = QFormLayout(spatial_params_container)
    spatial_params_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
    spatial_params_layout.setContentsMargins(0, 5, 0, 0)
    spatial_params_layout.setSpacing(6)
    spatial_params_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    spatial_params_layout.setHorizontalSpacing(20)

    frequency_params_container = QWidget()
    frequency_params_layout = QFormLayout(frequency_params_container)
    frequency_params_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
    frequency_params_layout.setContentsMargins(0, 5, 0, 0)
    frequency_params_layout.setSpacing(12)
    frequency_params_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    frequency_params_layout.setHorizontalSpacing(20)

    widgets = {}
    c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)

    merging_type_button = QToolButton()
    merging_type_button.setCheckable(True)
    
    initial_merging_type = sim_v1_config.get("similarity_V1_merging_type", "spatial")
    
    merging_type_button.setChecked(initial_merging_type == "spatial")
    merging_type_button.setFont(get_default_font(10, QFont.Weight.Bold))
    merging_type_button.setStyleSheet(TOGGLE_BUTTON + " QToolButton { min-width: 150px}")
    merging_type_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    merging_type_layout = QHBoxLayout()
    merging_type_layout.addWidget(merging_type_button, 0, Qt.AlignmentFlag.AlignCenter)
    main_layout.addLayout(merging_type_layout)
    main_layout.addSpacing(10)
    widgets['merging_type_button'] = merging_type_button

    # --- Parameter untuk Spatial Merging ---
    tile_size_label_text_sp = getattr(language_config, 'TILE_SIZE_LABEL_SPATIAL', "Tile Size (Spatial):")
    tile_size_label_sp = QLabel(tile_size_label_text_sp)
    tile_size_label_sp.setFont(get_default_font(9, QFont.Weight.DemiBold))
    tile_size_label_sp.setToolTip(getattr(language_config, 'TILE_SIZE_DESCRIPTION_SPATIAL', 'Size of tiles for spatial merging.'))
    tile_size_combo_sp = QComboBox()
    tile_options_int = [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256]
    tile_size_combo_sp.addItems([str(size) for size in tile_options_int])
    initial_tile_size_sp_int = sim_v1_config.get("similarity_V1_tile_size", 24)
    tile_size_combo_sp.setCurrentText(str(initial_tile_size_sp_int))
    tile_size_combo_sp.setStyleSheet(DROPDOWN_BOX + "QComboBox { padding: 4px 6px; min-height: 20px; }")
    tile_size_combo_sp.setMinimumWidth(100)
    spatial_params_layout.addRow(tile_size_label_sp, tile_size_combo_sp)
    widgets['tile_combo_spatial'] = tile_size_combo_sp

    overlap_label_text_sp = getattr(language_config, 'OVERLAP_LABEL_SPATIAL', "Overlap % (Spatial):")
    initial_overlap_ratio_sp = sim_v1_config.get("similarity_V1_overlap_percent", 0.35)
    initial_overlap_percent_sp = int(round(initial_overlap_ratio_sp * 100))
    overlap_validator_sp = QIntValidator(0, 90)
    slider_ov_sp, input_ov_sp = create_slider_with_input(
        overlap_label_text_sp, 0, 90, initial_overlap_percent_sp, str(initial_overlap_percent_sp),
        1.0, lambda v, m=1, loc=c_locale: str(int(v)), overlap_validator_sp,
        getattr(language_config, 'OVERLAP_DESCRIPTION_SPATIAL', 'Overlap for spatial merging.'),
        spatial_params_layout, c_locale
    )
    widgets['overlap_slider_spatial'] = slider_ov_sp
    widgets['overlap_input_spatial'] = input_ov_sp

    motion_sens_label_text = getattr(language_config, 'MOTION_THRESHOLD_LABEL', "Motion Sensitivity:")
    initial_motion_sens_v1 = sim_v1_config.get("similarity_V1_motion_sensitivity", 110.0)
    motion_sens_multiplier_v1 = 10.0
    motion_sens_slider_min_v1, motion_sens_slider_max_v1 = 10, 2000
    motion_sens_validator_v1 = QDoubleValidator(0.1, 200.0, 1)
    motion_sens_validator_v1.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_ms, input_ms = create_slider_with_input(
        motion_sens_label_text, 0, 0, int(round(initial_motion_sens_v1 * motion_sens_multiplier_v1)),
        c_locale.toString(initial_motion_sens_v1, 'f', 1), motion_sens_multiplier_v1,
        lambda v, m=motion_sens_multiplier_v1, loc=c_locale: loc.toString(v / m, 'f', 1),
        motion_sens_validator_v1, getattr(language_config, 'MOTION_THRESHOLD_DESCRIPTION', 'Controls sensitivity to motion.'),
        spatial_params_layout, c_locale,
        slider_min_val=motion_sens_slider_min_v1, slider_max_val=motion_sens_slider_max_v1
    )
    widgets['motion_sensitivity_slider'] = slider_ms
    widgets['motion_sensitivity_input'] = input_ms

    noise_mad_label_text = getattr(language_config, 'NOISE_MAD_OFFSET_LABEL_V1', "Noise Offset Factor:")
    initial_noise_mad_v1 = sim_v1_config.get("similarity_V1_noise_mad_offset_factor", 0.3)
    noise_mad_multiplier_v1 = 100.0
    noise_mad_slider_min_v1, noise_mad_slider_max_v1 = 0, 100
    noise_mad_validator_v1 = QDoubleValidator(0.0, 5.0, 2)
    noise_mad_validator_v1.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_nm, input_nm = create_slider_with_input(
        noise_mad_label_text, 0, 0, int(round(initial_noise_mad_v1 * noise_mad_multiplier_v1)),
        c_locale.toString(initial_noise_mad_v1, 'f', 2), noise_mad_multiplier_v1,
        lambda v, m=noise_mad_multiplier_v1, loc=c_locale: loc.toString(v / m, 'f', 2),
        noise_mad_validator_v1, getattr(language_config, 'NOISE_MAD_OFFSET_DESCRIPTION_V1', 'Factor for noise MAD adjustment.'),
        spatial_params_layout, c_locale,
        slider_min_val=noise_mad_slider_min_v1, slider_max_val=noise_mad_slider_max_v1
    )
    widgets['noise_mad_offset_slider'] = slider_nm
    widgets['noise_mad_offset_input'] = input_nm
    
    # Tombol Reset untuk Spatial
    reset_spatial_button = QPushButton(getattr(language_config, 'RESET_SPATIAL_DEFAULTS_BUTTON', "Reset Spatial Defaults"))
    reset_spatial_button.setStyleSheet(APPLY_BUTTON) # Tambahkan margin atas
    # reset_spatial_button.setMinimumHeight(28)
    spatial_params_layout.addRow(reset_spatial_button) # Tambahkan sebagai baris baru di form layout
    widgets['reset_spatial_button'] = reset_spatial_button


    tile_size_label_text_fq = getattr(language_config, 'TILE_SIZE_LABEL_FREQUENCY', "Tile Size (Frequency):")
    tile_size_label_fq = QLabel(tile_size_label_text_fq)
    tile_size_label_fq.setFont(get_default_font(9, QFont.Weight.DemiBold))
    tile_size_label_fq.setToolTip(getattr(language_config, 'TILE_SIZE_DESCRIPTION_FREQUENCY', 'Size of tiles for frequency merging.'))
    tile_size_combo_fq = QComboBox()
    tile_size_combo_fq.addItems([str(size) for size in tile_options_int])
    initial_tile_size_fq_int = sim_v1_config.get("similarity_V1_freq_tile_size", 16)
    tile_size_combo_fq.setCurrentText(str(initial_tile_size_fq_int))
    tile_size_combo_fq.setStyleSheet(DROPDOWN_BOX + "QComboBox { padding: 4px 6px; min-height: 20px; }")
    tile_size_combo_fq.setMinimumWidth(100)
    frequency_params_layout.addRow(tile_size_label_fq, tile_size_combo_fq)
    widgets['tile_combo_frequency'] = tile_size_combo_fq

    overlap_label_text_fq = getattr(language_config, 'OVERLAP_LABEL_FREQUENCY', "Overlap % (Frequency):")
    initial_overlap_ratio_fq = sim_v1_config.get("similarity_V1_freq_overlap_percent", 0.25)
    initial_overlap_percent_fq = int(round(initial_overlap_ratio_fq * 100))
    overlap_validator_fq = QIntValidator(0, 90)
    slider_ov_fq, input_ov_fq = create_slider_with_input(
        overlap_label_text_fq, 0, 90, initial_overlap_percent_fq, str(initial_overlap_percent_fq),
        1.0, lambda v, m=1, loc=c_locale: str(int(v)), overlap_validator_fq,
        getattr(language_config, 'OVERLAP_DESCRIPTION_FREQUENCY', 'Overlap for frequency merging.'),
        frequency_params_layout, c_locale
    )
    widgets['overlap_slider_frequency'] = slider_ov_fq
    widgets['overlap_input_frequency'] = input_ov_fq
    
    # --- Parameter untuk Frequency Merging ---
    c_wiener_label_text = getattr(language_config, 'C_WIENER_FACTOR_LABEL', "C Wiener Factor:")
    initial_c_wiener = sim_v1_config.get("similarity_V1_freq_c_wiener_factor", 5.0)
    c_wiener_multiplier = 10.0
    c_wiener_slider_min, c_wiener_slider_max = 1, 200
    c_wiener_validator = QDoubleValidator(0.1, 20.0, 1)
    c_wiener_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    slider_cw, input_cw = create_slider_with_input(
        c_wiener_label_text, 0,0, int(round(initial_c_wiener * c_wiener_multiplier)),
        c_locale.toString(initial_c_wiener, 'f', 1), c_wiener_multiplier,
        lambda v, m=c_wiener_multiplier, loc=c_locale: loc.toString(v / m, 'f', 1),
        c_wiener_validator, getattr(language_config, 'C_WIENER_FACTOR_DESCRIPTION', 'Constant for Wiener filter.'),
        frequency_params_layout, c_locale,
        slider_min_val=c_wiener_slider_min, slider_max_val=c_wiener_slider_max
    )
    widgets['c_wiener_factor_slider'] = slider_cw
    widgets['c_wiener_factor_input'] = input_cw

    # Tombol Reset untuk Frequency
    reset_frequency_button = QPushButton(getattr(language_config, 'RESET_FREQUENCY_DEFAULTS_BUTTON', "Reset Frequency Defaults"))
    reset_frequency_button.setStyleSheet(APPLY_BUTTON)
    # reset_frequency_button.setMinimumHeight(28)
    frequency_params_layout.addRow(reset_frequency_button) # Tambahkan sebagai baris baru
    widgets['reset_frequency_button'] = reset_frequency_button


    main_layout.addWidget(spatial_params_container)
    main_layout.addWidget(frequency_params_container)

    def save_current_settings_v1():
        # ... (fungsi save_current_settings_v1 seperti sebelumnya)
        settings_to_save_flat = {}
        try:
            settings_to_save_flat["similarity_V1_merging_type"] = "spatial" if widgets['merging_type_button'].isChecked() else "frequency"
            settings_to_save_flat["similarity_V1_tile_size"] = int(widgets['tile_combo_spatial'].currentText())
            ms_val, _ = c_locale.toDouble(widgets['motion_sensitivity_input'].text())
            settings_to_save_flat["similarity_V1_motion_sensitivity"] = ms_val
            nm_val, _ = c_locale.toDouble(widgets['noise_mad_offset_input'].text())
            settings_to_save_flat["similarity_V1_noise_mad_offset_factor"] = nm_val
            ov_sp_percent = int(widgets['overlap_input_spatial'].text())
            settings_to_save_flat["similarity_V1_overlap_percent"] = ov_sp_percent / 100.0
            cw_val, _ = c_locale.toDouble(widgets['c_wiener_factor_input'].text())
            settings_to_save_flat["similarity_V1_freq_c_wiener_factor"] = cw_val
            settings_to_save_flat["similarity_V1_freq_tile_size"] = int(widgets['tile_combo_frequency'].currentText())
            ov_fq_percent = int(widgets['overlap_input_frequency'].text())
            settings_to_save_flat["similarity_V1_freq_overlap_percent"] = ov_fq_percent / 100.0
        except ValueError as e: print(f"Error parsing settings for saving: {e}"); return
        except Exception as e: print(f"Unexpected error during settings parsing: {e}"); return
        general_settings_for_algo = {}
        try:
            if os.path.exists(GENERAL_SETTINGS_FILE):
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    general_settings_for_algo = json.load(f)
        except: pass
        settings_to_save_flat["use_multi_core"] = general_settings_for_algo.get("multi_core_cpu", True)
        save_similarity_v1_config(settings_to_save_flat)


    def update_merging_mode_ui(is_spatial):
        if is_spatial:
            merging_type_button.setText(getattr(language_config, 'SIMILARITY_MERGING_TYPE_SPATIAL_LABEL', "Mode: Spatial Merging"))
            merging_type_button.setToolTip(getattr(language_config, 'SIMILARITY_MERGING_TYPE_SPATIAL_DESC', "Spatial domain processing."))
            spatial_params_container.setVisible(True)
            frequency_params_container.setVisible(False)
        else:
            merging_type_button.setText(getattr(language_config, 'SIMILARITY_MERGING_TYPE_FREQUENCY_LABEL', "Mode: Frequency Merging"))
            merging_type_button.setToolTip(getattr(language_config, 'SIMILARITY_MERGING_TYPE_FREQUENCY_DESC', "Frequency domain processing."))
            spatial_params_container.setVisible(False)
            frequency_params_container.setVisible(True)
        save_current_settings_v1()

    merging_type_button.toggled.connect(update_merging_mode_ui)
    update_merging_mode_ui(initial_merging_type == "spatial")

    def setup_slider_input_connections(slider, line_edit, multiplier, min_actual, max_actual, locale_obj, format_digits, is_float=True, slider_min_val_raw=None, slider_max_val_raw=None):
        slider.valueChanged.connect(
            lambda value, inp=line_edit, m=multiplier, loc=locale_obj, d=format_digits, f=is_float:
                inp.setText(loc.toString(value / m, 'f', d) if f else str(int(round(value / m))))
        )
        def update_slider_from_input():
            current_locale = line_edit.locale() if is_float else None
            try:
                if is_float: value_actual, ok = current_locale.toDouble(line_edit.text()); assert ok
                else: value_actual = int(line_edit.text())
                value_actual_clamped = max(min_actual, min(value_actual, max_actual))
                slider_value_target = int(round(value_actual_clamped * multiplier))
                s_min_raw_actual = slider_min_val_raw if slider_min_val_raw is not None else int(round(min_actual * multiplier))
                s_max_raw_actual = slider_max_val_raw if slider_max_val_raw is not None else int(round(max_actual * multiplier))
                slider_value_clamped_for_slider = max(s_min_raw_actual, min(slider_value_target, s_max_raw_actual))
                slider.blockSignals(True); slider.setValue(slider_value_clamped_for_slider); slider.blockSignals(False)
                line_edit.setText(current_locale.toString(value_actual_clamped, 'f', format_digits) if is_float else str(int(value_actual_clamped)))
            except (ValueError, AssertionError):
                current_slider_val = slider.value()
                line_edit.setText(current_locale.toString(current_slider_val / multiplier, 'f', format_digits) if is_float else str(int(round(current_slider_val / multiplier))))
        line_edit.editingFinished.connect(update_slider_from_input)

    setup_slider_input_connections(slider_ms, input_ms, motion_sens_multiplier_v1, 0.1, 200.0, c_locale, 1, True, motion_sens_slider_min_v1, motion_sens_slider_max_v1)
    setup_slider_input_connections(slider_nm, input_nm, noise_mad_multiplier_v1, 0.0, 5.0, c_locale, 2, True, noise_mad_slider_min_v1, noise_mad_slider_max_v1)
    setup_slider_input_connections(slider_ov_sp, input_ov_sp, 1.0, 0, 90, c_locale, 0, False)
    setup_slider_input_connections(slider_cw, input_cw, c_wiener_multiplier, 0.1, 20.0, c_locale, 1, True, c_wiener_slider_min, c_wiener_slider_max)
    setup_slider_input_connections(slider_ov_fq, input_ov_fq, 1.0, 0, 90, c_locale, 0, False)

    # Fungsi Reset Spesifik
    def reset_spatial_defaults():
        defaults = original_v1_ui_defaults
        widgets['tile_combo_spatial'].setCurrentText(str(defaults.get("similarity_V1_tile_size", 16)))
        default_ms = defaults.get("similarity_V1_motion_sensitivity", 110.0)
        widgets['motion_sensitivity_slider'].setValue(int(round(default_ms * motion_sens_multiplier_v1)))
        default_nm = defaults.get("similarity_V1_noise_mad_offset_factor", 0.3)
        widgets['noise_mad_offset_slider'].setValue(int(round(default_nm * noise_mad_multiplier_v1)))
        default_ov_ratio_sp = defaults.get("similarity_V1_overlap_percent", 0.40)
        widgets['overlap_slider_spatial'].setValue(int(round(default_ov_ratio_sp * 100)))
        save_current_settings_v1()
    
    def reset_frequency_defaults():
        defaults = original_v1_ui_defaults
        default_cw = defaults.get("similarity_V1_freq_c_wiener_factor", 5.0)
        widgets['c_wiener_factor_slider'].setValue(int(round(default_cw * c_wiener_multiplier)))
        widgets['tile_combo_frequency'].setCurrentText(str(defaults.get("similarity_V1_freq_tile_size", 16)))
        default_ov_ratio_fq = defaults.get("similarity_V1_freq_overlap_percent", 0.25)
        widgets['overlap_slider_frequency'].setValue(int(round(default_ov_ratio_fq * 100)))
        save_current_settings_v1()

    widgets['reset_spatial_button'].clicked.connect(reset_spatial_defaults)
    widgets['reset_frequency_button'].clicked.connect(reset_frequency_defaults)
    
    widgets['tile_combo_spatial'].currentIndexChanged.connect(save_current_settings_v1)
    widgets['motion_sensitivity_slider'].sliderReleased.connect(save_current_settings_v1)
    widgets['motion_sensitivity_input'].editingFinished.connect(save_current_settings_v1)
    widgets['noise_mad_offset_slider'].sliderReleased.connect(save_current_settings_v1)
    widgets['noise_mad_offset_input'].editingFinished.connect(save_current_settings_v1)
    widgets['overlap_slider_spatial'].sliderReleased.connect(save_current_settings_v1)
    widgets['overlap_input_spatial'].editingFinished.connect(save_current_settings_v1)
    widgets['c_wiener_factor_slider'].sliderReleased.connect(save_current_settings_v1)
    widgets['c_wiener_factor_input'].editingFinished.connect(save_current_settings_v1)
    widgets['tile_combo_frequency'].currentIndexChanged.connect(save_current_settings_v1)
    widgets['overlap_slider_frequency'].sliderReleased.connect(save_current_settings_v1)
    widgets['overlap_input_frequency'].editingFinished.connect(save_current_settings_v1)

    main_layout.addStretch(1)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page_widget)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll