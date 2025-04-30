import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, 
                             QPushButton, QScrollArea, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import FarnebackAlgorithm
from UI.resources.stylesheet.stylesheet import APPLY_BUTTON, DROPDOWN_BOX, SCROLL_AREA, SLIDER_STYLE
from UI.settings.General.Language import language_config

def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)

def load_farneback_config():
    return FarnebackAlgorithm.load_farneback_config()

def save_farneback_config(config):
    config_dir = os.path.join("database", "setting")
    os.makedirs(config_dir, exist_ok=True)
    config_filename = os.path.join(config_dir, "Parameter_Stack_Enhance.json")
    
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params = json.load(f)
        else:
            all_params = {}
    except Exception as e:
        print("Error reading existing config:", e)
        all_params = {}
    
    all_params["Farneback"] = config
    
    try:
        with open(config_filename, "w") as f:
            json.dump(all_params, f, indent=4)
        print("Settings applied and saved to", config_filename)
    except Exception as e:
        print("Error saving Farneback settings:", e)

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
    value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    layout = QHBoxLayout()
    layout.addWidget(slider)
    layout.addWidget(value_label)
    
    slider.valueChanged.connect(lambda v: value_label.setText(format_func(v)))
    
    return label, slider, layout

def get_farneback_optical_flow_page():
    fb_config = load_farneback_config()
    
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)
    
    title_label = QLabel(language_config.FARNEBACK_PARAMETER_SETTING_LABEL)
    title_label.setFont(get_default_font(10, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)
    
    params = [
        (language_config.FARNEBACK_PYRAMID_SCALE_LABEL, 10, 100, 5, int(fb_config["pyr_scale"] * 100), lambda v: f"{v/100:.2f}", language_config.FARNEBACK_PYRAMID_SCALE_DESCRIPTION),
        (language_config.FARNEBACK_LEVELS_LABEL, 1, 10, 1, fb_config["levels"], str, language_config.FARNEBACK_LEVELS_DESCRIPTION),
        (language_config.FARNEBACK_WIN_SIZE_LABEL, 5, 50, 1, fb_config["winsize"], str, language_config.FARNEBACK_WIN_SIZE_DESCRIPTION),
        (language_config.FARNEBACK_ITERATIONS_LABEL, 1, 10, 1, fb_config["iterations"], str, language_config.FARNEBACK_ITERATIONS_DESCRIPTION),
        (language_config.FARNEBACK_POLY_N_LABEL, 5, 7, 1, fb_config["poly_n"], str, language_config.FARNEBACK_POLY_N_DESCRIPTION),
        (language_config.FARNEBACK_POLY_SIGMA_LABEL, 10, 200, 1, int(fb_config["poly_sigma"] * 100), lambda v: f"{v/100:.2f}", language_config.FARNEBACK_POLY_SIGMA_DESCRIPTION),
        (language_config.FARNEBACK_FLAGS_LABEL, 0, 10, 1, fb_config["flags"], str, language_config.FARNEBACK_FLAGS_DESCRIPTION)
    ]
    
    sliders = {}
    for label, min_v, max_v, step, init_v, fmt, tip in params:
        lbl, sld, lay = create_slider(label, min_v, max_v, step, init_v, fmt, tip)
        layout.addWidget(lbl)
        layout.addLayout(lay)
        sliders[label] = sld
    
    apply_button = QPushButton(language_config.APPLY_PARAMETER_BUTTON_TEXT)
    apply_button.setStyleSheet(APPLY_BUTTON)
    layout.addWidget(apply_button)
    
    def apply_settings():
        fb_params = {
            "pyr_scale": sliders[language_config.FARNEBACK_PYRAMID_SCALE_LABEL].value() / 100.0,
            "levels": sliders[language_config.FARNEBACK_LEVELS_LABEL].value(),
            "winsize": sliders[language_config.FARNEBACK_WIN_SIZE_LABEL].value(),
            "iterations": sliders[language_config.FARNEBACK_ITERATIONS_LABEL].value(),
            "poly_n": sliders[language_config.FARNEBACK_POLY_N_LABEL].value(),
            "poly_sigma": sliders[language_config.FARNEBACK_POLY_SIGMA_LABEL].value() / 100.0,
            "flags": sliders[language_config.FARNEBACK_FLAGS_LABEL].value(),
            "use_gpu": True
        }
        save_farneback_config(fb_params)
    
    apply_button.clicked.connect(apply_settings)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll
