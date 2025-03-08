import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider,
                             QHBoxLayout, QPushButton, QScrollArea,
                             QToolButton, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.AKAZE import AKAZEAlgorithm
from UI.resources.stylesheet.stylesheet import APPLY_BUTTON, DROPDOWN_BOX, TOGGLE_BUTTON, SCROLL_AREA, SLIDER_STYLE, SLIDER_VALUE_LABEL
from UI.settings.General.Language import language_config

def get_default_font(size=10, weight=QFont.Weight.Normal):
    """Mengembalikan objek QFont dengan ukuran dan berat tertentu."""
    return QFont("Arial", size, weight)

def load_akaze_config():
    """Muat konfigurasi AKAZE dari file JSON."""
    return AKAZEAlgorithm.load_akaze_config()

def save_akaze_config(config):
    """Simpan konfigurasi AKAZE ke file JSON."""
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
    
    all_params["AKAZE"] = config
    
    try:
        with open(config_filename, "w") as f:
            json.dump(all_params, f, indent=4)
        print("Settings applied and saved to", config_filename)
    except Exception as e:
        print("Error saving AKAZE settings:", e)

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
    
    slider.valueChanged.connect(lambda v: value_label.setText(format_func(v)))
    
    return label, slider, layout

def get_akaze_page():
    akaze_config = load_akaze_config()
    
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)
    
    title_label = QLabel(language_config.AKAZE_PARAMETER_SETTING_LABEL)
    title_label.setFont(get_default_font(10, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)
    
    params = [
        (language_config.AKAZE_THRESHOLD_LABEL, 1, 100, 1, int(akaze_config["akaze_threshold"] * 10000), lambda v: f"{v/10000:.4f}", language_config.AKAZE_THRESHOLD_DESCRIPTION),
        (language_config.AKAZE_OCTAVE_LABEL, 1, 8, 1, akaze_config["akaze_nOctaves"], str, language_config.AKAZE_OCTAVE_DESCRIPTION),
        (language_config.AKAZE_LAYER_LABEL, 1, 10, 1, akaze_config["akaze_nOctaveLayers"], str, language_config.AKAZE_LAYER_DESCRIPTION),
        (language_config.AKAZE_RATIO_LABEL, 50, 100, 1, int(akaze_config["ratio_threshold"] * 100), lambda v: f"{v/100:.2f}", language_config.AKAZE_RATIO_DESCRIPTION),
        (language_config.ORB_RANSAC_LABEL, 10, 100, 5, int(akaze_config["ransacThreshold"] * 10), lambda v: f"{v/10:.1f}", language_config.ORB_RANSAC_DESCRIPTION)
    ]
    
    sliders = {}
    for label, min_v, max_v, step, init_v, fmt, tip in params:
        lbl, sld, lay = create_slider(label, min_v, max_v, step, init_v, fmt, tip)
        layout.addWidget(lbl)
        layout.addLayout(lay)
        sliders[label] = sld
    
    # Tambahkan dua tombol toggle: keep_edges dan enable_cropping
    toggles_layout = QHBoxLayout()
    
    transformation_label = QLabel(language_config.ORB_TRANSFORMATION_LABEL)
    transformation_label.setToolTip(language_config.ORB_TRANSFORMATION_DESCRIPTION)
    transformation_label.setFont(get_default_font(10, QFont.Weight.Bold))
    layout.addWidget(transformation_label)
    
    transformation_combo = QComboBox()
    transformation_combo.addItems(["homography", "affine", "similarity", "euclidean"])
    transformation_combo.setCurrentText(akaze_config["transformation"])
    transformation_combo.setStyleSheet(DROPDOWN_BOX)
    layout.addWidget(transformation_combo)
    
    
    # Tombol toggle untuk keep_edges
    keep_edges_button = QToolButton()
    keep_edges_button.setCheckable(True)
    keep_edges_button.setChecked(akaze_config.get("keep_edges", True))
    keep_edges_button.setText(language_config.KEEP_EDGES_LABEL if akaze_config.get("keep_edges", True) else language_config.IGNORE_EDGE_LABEL)
    keep_edges_button.setFont(get_default_font(10, QFont.Weight.Bold))
    keep_edges_button.setToolTip(language_config.KEEP_EDGES_DESCRIPTION)
    keep_edges_button.setStyleSheet(TOGGLE_BUTTON)
    keep_edges_button.toggled.connect(lambda state: keep_edges_button.setText(language_config.KEEP_EDGES_LABEL if state else language_config.IGNORE_EDGE_LABEL))
    
    toggles_layout.addWidget(keep_edges_button)
    
    # Tombol toggle untuk enable_cropping
    enable_cropping_button = QToolButton()
    enable_cropping_button.setCheckable(True)
    enable_cropping_button.setChecked(akaze_config.get("enable_cropping", False))
    enable_cropping_button.setText(language_config.ENABLE_CROP_LABEL if akaze_config.get("enable_cropping", False) else language_config.DISABLE_CROP_LABEL)
    enable_cropping_button.setFont(get_default_font(10, QFont.Weight.Bold))
    enable_cropping_button.setToolTip(language_config.CROP_DESCRIPTION)
    enable_cropping_button.setStyleSheet(TOGGLE_BUTTON)
    
    # Logika: jika enable_cropping aktif, maka keep_edges otomatis disetel ke false dan dinonaktifkan
    def on_enable_cropping_toggled(state):
        enable_cropping_button.setText(language_config.ENABLE_CROP_LABEL if state else language_config.DISABLE_CROP_LABEL)
        if state:
            keep_edges_button.setChecked(False)
            keep_edges_button.setEnabled(False)
        else:
            keep_edges_button.setEnabled(True)
    enable_cropping_button.toggled.connect(on_enable_cropping_toggled)
    
    toggles_layout.addWidget(enable_cropping_button)
    layout.addLayout(toggles_layout)
    
    apply_button = QPushButton(language_config.APPLY_PARAMETER_BUTTON_TEXT)
    apply_button.setStyleSheet(APPLY_BUTTON)
    layout.addWidget(apply_button)
    
    def apply_settings():
        akaze_params = {
            "akaze_threshold": sliders[language_config.AKAZE_THRESHOLD_LABEL].value() / 10000.0,
            "akaze_nOctaves": sliders[language_config.AKAZE_OCTAVE_LABEL].value(),
            "akaze_nOctaveLayers": sliders[language_config.AKAZE_LAYER_LABEL].value(),
            "ransacThreshold": sliders[language_config.ORB_RANSAC_LABEL].value() / 10.0,
            "ratio_threshold": sliders[language_config.AKAZE_RATIO_LABEL].value() / 100.0,
            "transformation": transformation_combo.currentText(),
            "keep_edges": keep_edges_button.isChecked(),
            "enable_cropping": enable_cropping_button.isChecked()  # Simpan nilai enable_cropping
        }
        save_akaze_config(akaze_params)
    
    apply_button.clicked.connect(apply_settings)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    
    return scroll
