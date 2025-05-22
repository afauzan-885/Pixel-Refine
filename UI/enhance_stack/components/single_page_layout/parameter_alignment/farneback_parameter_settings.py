import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout,
                             QScrollArea)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import FarnebackAlgorithm
from UI.resources.stylesheet.stylesheet import  SCROLL_AREA, SLIDER_STYLE, SLIDER_VALUE_LABEL
from UI.settings.General.Language import language_config
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

# --- Fungsi Helper (Tetap Sama) ---
def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)

def load_farneback_config():
    return FarnebackAlgorithm.load_farneback_config()

def _load_general_setting():
    """Membaca semua setting relevan dari app_setting.json."""
    defaults = {
        "gpu_acceleration": False,
        "multi_core_cpu": True
    }
    if not os.path.exists(GENERAL_SETTINGS_FILE):
        return defaults
    try:
        with open(GENERAL_SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        for key, value in defaults.items():
            settings.setdefault(key, value)
        return settings
    except (json.JSONDecodeError, IOError, KeyError) as e:
        return defaults

def save_farneback_config(config):
    """Menyimpan konfigurasi Farneback ke Parameter_Stack_Enhance.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE

    all_params = {}
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params = json.load(f)
    except Exception as e:
        pass
    all_params["Farneback"] = config

    try:
        with open(config_filename, "w") as f:
            json.dump(all_params, f, indent=4)
    except Exception as e:
      pass

def create_slider(label_text, min_val, max_val, step, initial_value, format_func, tooltip):
    label = QLabel(label_text)
    label.setToolTip(tooltip)
    label.setFont(get_default_font(10, QFont.Weight.Bold))

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_val)
    slider.setMaximum(max_val)
    slider.setValue(initial_value)
    slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    slider.setTickInterval(step)
    slider.setStyleSheet(SLIDER_STYLE)

    value_label = QLabel(format_func(initial_value))
    value_label.setStyleSheet(SLIDER_VALUE_LABEL)
    value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout = QHBoxLayout()
    layout.addWidget(slider)
    layout.addWidget(value_label)
    return label, slider, layout, value_label


def get_farneback_optical_flow_page():
    try:
        all_params = {}
        farneback_section_exists = False
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f:
                all_params = json.load(f)
            if "Farneback" in all_params and isinstance(all_params.get("Farneback"), dict):
                farneback_section_exists = True

        if not farneback_section_exists:
           
            # 1. Dapatkan default Farneback
            fb_params = load_farneback_config()

            # 2. Dapatkan setting general saat ini
            general_settings = _load_general_setting()
            use_gpu_setting = general_settings.get("gpu_acceleration", False)
            use_multicore_setting = general_settings.get("multi_core_cpu", True)

            # 3. Update default dengan setting general
            fb_params["use_gpu"] = use_gpu_setting
            fb_params["use_multi_core"] = use_multicore_setting

            # 4. Panggil save_farneback_config untuk menyimpan default ini
            save_farneback_config(fb_params)        
            fb_config = fb_params
        else:
            fb_config = load_farneback_config() 
    except (IOError, json.JSONDecodeError) as e:
        fb_config = load_farneback_config() 
        
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)

    title_label = QLabel(language_config.FARNEBACK_PARAMETER_SETTING_LABEL)
    title_label.setFont(get_default_font(10, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)

    sliders = {}
    value_labels = {}
    param_formatters = {}

    def save_current_settings():
        general_settings = _load_general_setting()
        use_gpu_setting = general_settings.get("gpu_acceleration", False)
        use_multicore_setting = general_settings.get("multi_core_cpu", True)
      
        fb_params = {}
        for label_key, slider_widget in sliders.items():
            current_value = slider_widget.value()
            if label_key == language_config.FARNEBACK_PYRAMID_SCALE_LABEL:
                fb_params["pyr_scale"] = current_value / 100.0
            elif label_key == language_config.FARNEBACK_LEVELS_LABEL:
                fb_params["levels"] = current_value
            elif label_key == language_config.FARNEBACK_WIN_SIZE_LABEL:
                fb_params["winsize"] = current_value
            elif label_key == language_config.FARNEBACK_ITERATIONS_LABEL:
                fb_params["iterations"] = current_value
            elif label_key == language_config.FARNEBACK_POLY_N_LABEL:
                fb_params["poly_n"] = current_value
            elif label_key == language_config.FARNEBACK_POLY_SIGMA_LABEL:
                fb_params["poly_sigma"] = current_value / 100.0
            elif label_key == language_config.FARNEBACK_FLAGS_LABEL:
                fb_params["flags"] = current_value
            fb_params["cpu_num_blocks"] = fb_config.get("cpu_num_blocks", [2, 2]) # Ambil dari config yg dimuat
            fb_params["cpu_overlap_ratio"] = fb_config.get("cpu_overlap_ratio", 0.3) # Ambil dari config yg dimuat
            fb_params["interpolation"] = fb_config.get("interpolation", "INTER_CUBIC") # Ambil dari config yg dimuat
            if label_key in value_labels and label_key in param_formatters:
                 value_labels[label_key].setText(param_formatters[label_key](current_value))

        fb_params["use_gpu"] = use_gpu_setting
        fb_params["use_multi_core"] = use_multicore_setting # Tambahkan ini

        # Panggil fungsi save
        save_farneback_config(fb_params)


    params = [
        (language_config.FARNEBACK_PYRAMID_SCALE_LABEL, 10, 100, 5, "pyr_scale", 100, lambda v: f"{v/100:.2f}", language_config.FARNEBACK_PYRAMID_SCALE_DESCRIPTION),
        (language_config.FARNEBACK_LEVELS_LABEL, 1, 10, 1, "levels", 1, str, language_config.FARNEBACK_LEVELS_DESCRIPTION),
        (language_config.FARNEBACK_WIN_SIZE_LABEL, 5, 50, 1, "winsize", 1, str, language_config.FARNEBACK_WIN_SIZE_DESCRIPTION),
        (language_config.FARNEBACK_ITERATIONS_LABEL, 1, 10, 1, "iterations", 1, str, language_config.FARNEBACK_ITERATIONS_DESCRIPTION),
        (language_config.FARNEBACK_POLY_N_LABEL, 5, 7, 1, "poly_n", 1, str, language_config.FARNEBACK_POLY_N_DESCRIPTION),
        (language_config.FARNEBACK_POLY_SIGMA_LABEL, 10, 200, 1, "poly_sigma", 100, lambda v: f"{v/100:.2f}", language_config.FARNEBACK_POLY_SIGMA_DESCRIPTION),
        (language_config.FARNEBACK_FLAGS_LABEL, 0, 10, 1, "flags", 1, str, language_config.FARNEBACK_FLAGS_DESCRIPTION)
    ]

    for label_key, min_v, max_v, step, config_key, mult, fmt, tip in params:
        initial_float_value = fb_config.get(config_key, 0)

        # Berikan default yang lebih baik jika perlu
        if config_key == "pyr_scale" and initial_float_value == 0: initial_float_value = 0.5
        if config_key == "levels" and initial_float_value == 0: initial_float_value = 3
        if config_key == "winsize" and initial_float_value == 0: initial_float_value = 15
        if config_key == "iterations" and initial_float_value == 0: initial_float_value = 3
        if config_key == "poly_n" and initial_float_value == 0: initial_float_value = 5
        if config_key == "poly_sigma" and initial_float_value == 0: initial_float_value = 1.1

        initial_slider_value = int(initial_float_value * mult)
        lbl, sld, lay, val_lbl = create_slider(label_key, min_v, max_v, step, initial_slider_value, fmt, tip)

        layout.addWidget(lbl)
        layout.addLayout(lay)

        sliders[label_key] = sld
        value_labels[label_key] = val_lbl
        param_formatters[label_key] = fmt

        # Hubungkan valueChanged ke fungsi save
        sld.valueChanged.connect(save_current_settings)

    layout.addStretch(1) 

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll
 