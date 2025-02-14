import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider,
                             QHBoxLayout, QPushButton, QScrollArea, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.EEC import EECAlgorithm
from UI.settings.General.Language import language_config

def get_eec_page():
    """Buat halaman pengaturan untuk EEC dengan widget untuk mengatur parameter."""
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)

    # Muat konfigurasi EEC dari file konfigurasi
    eec_config = EECAlgorithm.load_eec_config()

    # Siapkan font bold untuk label
    bold_font = QFont()
    bold_font.setBold(True)

    # Judul halaman
    title_label = QLabel(language_config.EEC_PARAMETER_SETTING_LABEL)
    title_label.setFont(bold_font)
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)

    # === Parameter number_of_iterations ===
    iterations_label = QLabel(language_config.EEC_ITERATIONS_LABEL)
    iterations_label.setToolTip(language_config.EEC_ITERATIONS_DESCRIPTION)
    iterations_label.setFont(bold_font)
    layout.addWidget(iterations_label)

    iterations_slider = QSlider(Qt.Orientation.Horizontal)
    # Misal rentang iterasi dari 1000 hingga 10000
    iterations_slider.setMinimum(100)
    iterations_slider.setMaximum(10000)
    iterations_slider.setValue(eec_config["number_of_iterations"])
    iterations_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    iterations_slider.setTickInterval(100)
    iterations_layout = QHBoxLayout()
    iterations_layout.setSpacing(10)
    iterations_layout.addWidget(iterations_slider)
    iterations_value_label = QLabel(str(iterations_slider.value()))
    iterations_layout.addWidget(iterations_value_label)
    layout.addLayout(iterations_layout)
    iterations_slider.valueChanged.connect(lambda value: iterations_value_label.setText(str(value)))

    # === Parameter termination_eps ===
    eps_label = QLabel(language_config.EEC_EPS_LABEL)
    eps_label.setToolTip(language_config.EEC_EPS_DESCRIPTION)
    eps_label.setFont(bold_font)
    layout.addWidget(eps_label)

    eps_slider = QSlider(Qt.Orientation.Horizontal)
    # Representasi: slider dari 1 hingga 10000, di mana nilai slider * 1e-8 menghasilkan nilai antara 1e-8 dan 1e-4.
    eps_slider.setMinimum(100)
    eps_slider.setMaximum(10000)
    eps_slider_value = int(eec_config["termination_eps"] / 1e-8)
    eps_slider.setValue(eps_slider_value)
    eps_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    eps_slider.setTickInterval(100)
    eps_layout = QHBoxLayout()
    eps_layout.setSpacing(10)
    eps_layout.addWidget(eps_slider)
    eps_value_label = QLabel(f"{eps_slider.value() * 1e-8:.1e}")
    eps_layout.addWidget(eps_value_label)
    layout.addLayout(eps_layout)
    eps_slider.valueChanged.connect(lambda value: eps_value_label.setText(f"{value * 1e-8:.1e}"))

    # === Parameter motion_type ===
    motion_label = QLabel(language_config.EEC_MOTION_LABEL)
    motion_label.setToolTip(language_config.EEC_MOTION_DESCRIPTION)
    motion_label.setFont(bold_font)
    layout.addWidget(motion_label)

    motion_combo = QComboBox()
    motion_options = ["affine", "homography", "translation"]
    motion_combo.addItems(motion_options)
    current_motion = eec_config.get("motion_type", "affine")
    if current_motion in motion_options:
        motion_combo.setCurrentIndex(motion_options.index(current_motion))
    motion_style = """
        QComboBox {
            background-color: #F0EEEE;
            padding: 5px;
            border-radius: 5px;
            max-width: 200px;
        }
        QComboBox::drop-down {
            background-color: #ffffff;
            border-radius: 5px;
            border: 1px solid #d1d1d1;
        }
        QComboBox::down-arrow {
            image: url('UI/resources/icon/menu-options.png');
            width: 24px;
            height: 24px;
        }
        QComboBox:hover {
            background-color: #9EFFE2;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #d1d1d1;
            selection-background-color: #7B9AC8;
            selection-color: white;
            padding: 5px;
        }
        QComboBox QAbstractItemView::item {
            margin-bottom: 5px;
        }
    """    
    motion_combo.setStyleSheet(motion_style)
    layout.addWidget(motion_combo)

    # Tombol untuk menerapkan pengaturan
    apply_button = QPushButton(language_config.APPLY_PARAMETER_BUTTON_TEXT)
    apply_button.setStyleSheet("""
        QPushButton {
            background-color: #5cb85c;    
            color: white;                 
            border: none;
            border-radius: 5px;           
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4cae4c;    
        }
        QPushButton:pressed {
            background-color: #449d44;
        }
    """)
    layout.addWidget(apply_button)

    def apply_settings():
        """
        Simpan nilai dari widget ke file konfigurasi JSON pada bagian EEC.
        """
        eec_params = {
            "number_of_iterations": iterations_slider.value(),
            "termination_eps": eps_slider.value() * 1e-8,
            "motion_type": motion_combo.currentText()
        }

        config_dir = os.path.join("database", "setting")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_filename = os.path.join(config_dir, "Parameter_Stack_Enhance.json")

        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    all_params = json.load(config_file)
            else:
                all_params = {}
        except Exception as e:
            print("Error reading existing config:", e)
            all_params = {}

        all_params["EEC"] = eec_params

        try:
            with open(config_filename, "w") as config_file:
                json.dump(all_params, config_file, indent=4)
            print("Settings applied and saved to", config_filename)
        except Exception as e:
            print("Error saving EEC settings:", e)

    apply_button.clicked.connect(apply_settings)

    # Bungkus halaman dalam QScrollArea untuk tampilan yang konsisten
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page)
    scroll.setStyleSheet("""
        QScrollArea {
            border: none;
        }
        QScrollBar:vertical {
            border: none;
            background: #F0F0F0;
            width: 10px;
            margin: 2px 0 2px 0;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #A0A0A0;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #808080;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            border: none;
        }
    """)
    return scroll
