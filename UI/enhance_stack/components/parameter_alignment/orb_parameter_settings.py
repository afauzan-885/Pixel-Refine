import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider,
                             QHBoxLayout, QPushButton, QScrollArea, QToolButton, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.ORB import ORBAlgorithm
from UI.resources.stylesheet.stylesheet import APPLY_BUTTON, DROPDOWN_BOX, KEEP_EDGES_BUTTON, SCROLL_AREA, SLIDER_STYLE, SLIDER_VALUE_LABEL
from UI.settings.General.Language import language_config

def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)

def load_orb_config():
    return ORBAlgorithm.load_orb_config()

def save_orb_config(config):
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
    
    all_params["ORB"] = config
    
    try:
        with open(config_filename, "w") as f:
            json.dump(all_params, f, indent=4)
        print("Settings applied and saved to", config_filename)
    except Exception as e:
        print("Error saving ORB settings:", e)

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

def get_orb_page():
    orb_config = load_orb_config()
    
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)
    
    title_label = QLabel(language_config.ORB_PARAMETER_SETTING_LABEL)
    title_label.setFont(get_default_font(10, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)
    
    params = [
        (language_config.ORB_NFEATURES_LABEL, 100, 5000, 100, orb_config["nfeatures"], str, language_config.ORB_NFEATURES_DESCRIPTION),
        (language_config.ORB_SCALEFACTOR_LABEL, 10, 20, 1, int(orb_config["scaleFactor"] * 10), lambda v: f"{v/10:.1f}", language_config.ORB_SCALEFACTOR_DESCRIPTION),
        (language_config.ORB_NLEVELS_LABEL, 1, 8, 1, orb_config["nlevels"], str, language_config.ORB_NLEVELS_DESCRIPTION),
        (language_config.ORB_RANSAC_LABEL, 10, 100, 5, int(orb_config["ransacThreshold"] * 10), lambda v: f"{v/10:.1f}", language_config.ORB_RANSAC_DESCRIPTION)
    ]
    
    sliders = {}
    for label, min_v, max_v, step, init_v, fmt, tip in params:
        lbl, sld, lay = create_slider(label, min_v, max_v, step, init_v, fmt, tip)
        layout.addWidget(lbl)
        layout.addLayout(lay)
        sliders[label] = sld
    
    transformation_label = QLabel(language_config.ORB_TRANSFORMATION_LABEL)
    transformation_label.setToolTip(language_config.ORB_TRANSFORMATION_DESCRIPTION)
    transformation_label.setFont(get_default_font(10, QFont.Weight.Bold))
    layout.addWidget(transformation_label)
    
    transformation_combo = QComboBox()
    transformation_combo.addItems(["homography", "affine", "similarity", "euclidean"])
    transformation_combo.setCurrentText(orb_config["transformation"])
    transformation_combo.setStyleSheet(DROPDOWN_BOX)
    layout.addWidget(transformation_combo)
    
    keep_edges_button = QToolButton()
    keep_edges_button.setCheckable(True)
    keep_edges_button.setChecked(orb_config.get("keep_edges", True))
    keep_edges_button.setText("Keep Edges" if orb_config.get("keep_edges", True) else "Ignore Edges")
    keep_edges_button.setFont(get_default_font(10, QFont.Weight.Bold))
    keep_edges_button.setToolTip(language_config.KEEP_EDGES_DESCRIPTION)
    keep_edges_button.setStyleSheet(KEEP_EDGES_BUTTON)
    
    keep_edges_button.toggled.connect(lambda state: keep_edges_button.setText("Keep Edges" if state else "Ignore Edges"))
    layout.addWidget(keep_edges_button)
    
    apply_button = QPushButton(language_config.APPLY_PARAMETER_BUTTON_TEXT)
    apply_button.setStyleSheet(APPLY_BUTTON)
    layout.addWidget(apply_button)
    
    def apply_settings():
        orb_params = {
            "nfeatures": sliders[language_config.ORB_NFEATURES_LABEL].value(),
            "scaleFactor": sliders[language_config.ORB_SCALEFACTOR_LABEL].value() / 10.0,
            "nlevels": sliders[language_config.ORB_NLEVELS_LABEL].value(),
            "transformation": transformation_combo.currentText(),
            "ransacThreshold": sliders[language_config.ORB_RANSAC_LABEL].value() / 10.0,
            "keep_edges": keep_edges_button.isChecked()
        }
        save_orb_config(orb_params)
    
    apply_button.clicked.connect(apply_settings)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll
