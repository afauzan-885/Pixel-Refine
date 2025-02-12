import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider,
                             QHBoxLayout, QPushButton, QScrollArea, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.AKAZE import AKAZEAlgorithm

def get_akaze_page():
    """Buat halaman pengaturan untuk AKAZE dengan widget untuk mengatur parameter."""
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)

    # Muat konfigurasi AKAZE dari file konfigurasi
    akaze_config = AKAZEAlgorithm.load_akaze_config()

    # Siapkan font bold untuk label
    bold_font = QFont()
    bold_font.setBold(True)

    # Judul halaman
    title_label = QLabel("Pengaturan AKAZE")
    title_label.setFont(bold_font)
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)

    # === Parameter akaze_threshold ===
    # Kita gunakan slider dengan representasi integer, misalnya:
    # Rentang slider: 1 - 100, di mana nilai slider / 10000 menghasilkan nilai antara 0.0001 dan 0.01.
    threshold_label = QLabel("Threshold")
    threshold_label.setToolTip(
        "Deskripsi: Nilai threshold untuk mendeteksi fitur AKAZE.\n"
        "Efek: Nilai yang lebih rendah mendeteksi lebih banyak fitur, tetapi bisa menghasilkan noise."
    )
    threshold_label.setFont(bold_font)
    layout.addWidget(threshold_label)

    threshold_slider = QSlider(Qt.Orientation.Horizontal)
    threshold_slider.setMinimum(1)
    threshold_slider.setMaximum(100)
    # Konversi nilai float ke integer untuk slider
    threshold_slider.setValue(int(akaze_config["akaze_threshold"] * 10000))
    threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    threshold_slider.setTickInterval(1)
    threshold_layout = QHBoxLayout()
    threshold_layout.setSpacing(10)
    threshold_layout.addWidget(threshold_slider)
    threshold_value_label = QLabel(f"{threshold_slider.value()/10000:.4f}")
    threshold_layout.addWidget(threshold_value_label)
    layout.addLayout(threshold_layout)
    threshold_slider.valueChanged.connect(
        lambda value: threshold_value_label.setText(f"{value/10000:.4f}")
    )

    # === Parameter akaze_nOctaves ===
    octaves_label = QLabel("Jumlah Octaves (nOctaves)")
    octaves_label.setToolTip(
        "Deskripsi: Jumlah octave untuk mendeteksi fitur. "
        "Nilai lebih tinggi memungkinkan deteksi pada skala yang lebih bervariasi, tetapi memperlambat proses."
    )
    octaves_label.setFont(bold_font)
    layout.addWidget(octaves_label)

    octaves_slider = QSlider(Qt.Orientation.Horizontal)
    octaves_slider.setMinimum(1)
    octaves_slider.setMaximum(8)
    octaves_slider.setValue(akaze_config["akaze_nOctaves"])
    octaves_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    octaves_slider.setTickInterval(1)
    octaves_layout = QHBoxLayout()
    octaves_layout.setSpacing(10)
    octaves_layout.addWidget(octaves_slider)
    octaves_value_label = QLabel(str(octaves_slider.value()))
    octaves_layout.addWidget(octaves_value_label)
    layout.addLayout(octaves_layout)
    octaves_slider.valueChanged.connect(lambda value: octaves_value_label.setText(str(value)))

    # === Parameter akaze_nOctaveLayers ===
    layers_label = QLabel("Jumlah Layers per Octave (nOctaveLayers)")
    layers_label.setToolTip(
        "Deskripsi: Jumlah layers per octave. "
        "Nilai lebih tinggi dapat meningkatkan resolusi deteksi fitur tetapi menambah beban komputasi."
    )
    layers_label.setFont(bold_font)
    layout.addWidget(layers_label)

    layers_slider = QSlider(Qt.Orientation.Horizontal)
    layers_slider.setMinimum(1)
    layers_slider.setMaximum(10)
    layers_slider.setValue(akaze_config["akaze_nOctaveLayers"])
    layers_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    layers_slider.setTickInterval(1)
    layers_layout = QHBoxLayout()
    layers_layout.setSpacing(10)
    layers_layout.addWidget(layers_slider)
    layers_value_label = QLabel(str(layers_slider.value()))
    layers_layout.addWidget(layers_value_label)
    layout.addLayout(layers_layout)
    layers_slider.valueChanged.connect(lambda value: layers_value_label.setText(str(value)))

    # === Parameter ratio_threshold ===
    ratio_label = QLabel("Ratio Threshold")
    ratio_label.setToolTip(
        "Deskripsi: Rasio threshold untuk uji rasio pada pencocokan fitur. "
        "Nilai yang lebih rendah lebih selektif dalam memilih pasangan fitur yang baik."
    )
    ratio_label.setFont(bold_font)
    layout.addWidget(ratio_label)

    ratio_slider = QSlider(Qt.Orientation.Horizontal)
    # Representasi: slider dari 50 hingga 100, di mana nilai slider/100 menghasilkan nilai antara 0.50 dan 1.00.
    ratio_slider.setMinimum(50)
    ratio_slider.setMaximum(100)
    ratio_slider.setValue(int(akaze_config["ratio_threshold"] * 100))
    ratio_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    ratio_slider.setTickInterval(1)
    ratio_layout = QHBoxLayout()
    ratio_layout.setSpacing(10)
    ratio_layout.addWidget(ratio_slider)
    ratio_value_label = QLabel(f"{ratio_slider.value()/100:.2f}")
    ratio_layout.addWidget(ratio_value_label)
    layout.addLayout(ratio_layout)
    ratio_slider.valueChanged.connect(lambda value: ratio_value_label.setText(f"{value/100:.2f}"))

    # Tombol untuk menerapkan pengaturan
    apply_button = QPushButton("Apply Settings")
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
        Simpan nilai dari widget ke file konfigurasi JSON pada bagian AKAZE.
        """
        akaze_params = {
            "akaze_threshold": threshold_slider.value() / 10000.0,
            "akaze_nOctaves": octaves_slider.value(),
            "akaze_nOctaveLayers": layers_slider.value(),
            "ratio_threshold": ratio_slider.value() / 100.0
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

        all_params["AKAZE"] = akaze_params

        try:
            with open(config_filename, "w") as config_file:
                json.dump(all_params, config_file, indent=4)
            print("Settings applied and saved to", config_filename)
        except Exception as e:
            print("Error saving AKAZE settings:", e)

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