import os, json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, QPushButton, QScrollArea, QComboBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import FarnebackAlgorithm 
def get_farneback_optical_flow_page():
    """Buat halaman pengaturan untuk Farneback Optical Flow."""
    # Muat konfigurasi Farneback Optical Flow dari file konfigurasi
    fb_config = FarnebackAlgorithm.load_farneback_config()

    # Buat halaman utama
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)

    # Siapkan font bold untuk label
    bold_font = QFont()
    bold_font.setBold(True)

    # Judul halaman
    title_label = QLabel("Pengaturan Farneback Optical Flow")
    title_label.setFont(bold_font)
    layout.addWidget(title_label)

    # === Parameter pyr_scale ===
    pyr_scale_label = QLabel("Pyr Scale")
    pyr_scale_label.setToolTip(
        "Deskripsi: Rasio pengurangan ukuran pyramid. Nilai tipikal adalah 0.5."
    )
    pyr_scale_label.setFont(bold_font)
    layout.addWidget(pyr_scale_label)

    pyr_scale_slider = QSlider(Qt.Orientation.Horizontal)
    pyr_scale_slider.setMinimum(10)    # Mewakili 0.10
    pyr_scale_slider.setMaximum(100)   # Mewakili 1.00
    pyr_scale_slider.setValue(int(fb_config["pyr_scale"] * 100))
    pyr_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    pyr_scale_slider.setTickInterval(5)
    pyr_scale_layout = QHBoxLayout()
    pyr_scale_layout.setSpacing(10)
    pyr_scale_layout.addWidget(pyr_scale_slider)
    pyr_scale_value_label = QLabel(f"{pyr_scale_slider.value()/100:.2f}")
    pyr_scale_layout.addWidget(pyr_scale_value_label)
    layout.addLayout(pyr_scale_layout)
    pyr_scale_slider.valueChanged.connect(
        lambda value: pyr_scale_value_label.setText(f"{value/100:.2f}")
    )

    # === Parameter levels ===
    levels_label = QLabel("Levels")
    levels_label.setToolTip(
        "Deskripsi: Jumlah level pyramid. Nilai tipikal adalah 3."
    )
    levels_label.setFont(bold_font)
    layout.addWidget(levels_label)

    levels_slider = QSlider(Qt.Orientation.Horizontal)
    levels_slider.setMinimum(1)
    levels_slider.setMaximum(10)
    levels_slider.setValue(fb_config["levels"])
    levels_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    levels_slider.setTickInterval(1)
    levels_layout = QHBoxLayout()
    levels_layout.setSpacing(10)
    levels_layout.addWidget(levels_slider)
    levels_value_label = QLabel(str(levels_slider.value()))
    levels_layout.addWidget(levels_value_label)
    layout.addLayout(levels_layout)
    levels_slider.valueChanged.connect(lambda value: levels_value_label.setText(str(value)))

    # === Parameter winsize ===
    winsize_label = QLabel("Win Size")
    winsize_label.setToolTip(
        "Deskripsi: Ukuran jendela pencarian optical flow. Nilai tipikal adalah 15."
    )
    winsize_label.setFont(bold_font)
    layout.addWidget(winsize_label)

    winsize_slider = QSlider(Qt.Orientation.Horizontal)
    winsize_slider.setMinimum(5)
    winsize_slider.setMaximum(50)
    winsize_slider.setValue(fb_config["winsize"])
    winsize_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    winsize_slider.setTickInterval(1)
    winsize_layout = QHBoxLayout()
    winsize_layout.setSpacing(10)
    winsize_layout.addWidget(winsize_slider)
    winsize_value_label = QLabel(str(winsize_slider.value()))
    winsize_layout.addWidget(winsize_value_label)
    layout.addLayout(winsize_layout)
    winsize_slider.valueChanged.connect(lambda value: winsize_value_label.setText(str(value)))

    # === Parameter iterations ===
    iterations_label = QLabel("Iterations")
    iterations_label.setToolTip(
        "Deskripsi: Jumlah iterasi pencarian optical flow. Nilai tipikal adalah 3."
    )
    iterations_label.setFont(bold_font)
    layout.addWidget(iterations_label)

    iterations_slider = QSlider(Qt.Orientation.Horizontal)
    iterations_slider.setMinimum(1)
    iterations_slider.setMaximum(10)
    iterations_slider.setValue(fb_config["iterations"])
    iterations_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    iterations_slider.setTickInterval(1)
    iterations_layout = QHBoxLayout()
    iterations_layout.setSpacing(10)
    iterations_layout.addWidget(iterations_slider)
    iterations_value_label = QLabel(str(iterations_slider.value()))
    iterations_layout.addWidget(iterations_value_label)
    layout.addLayout(iterations_layout)
    iterations_slider.valueChanged.connect(lambda value: iterations_value_label.setText(str(value)))

    # === Parameter poly_n ===
    poly_n_label = QLabel("Poly N")
    poly_n_label.setToolTip(
        "Deskripsi: Ukuran tetangga pixel untuk estimasi polinomial. Nilai tipikal adalah 5 atau 7."
    )
    poly_n_label.setFont(bold_font)
    layout.addWidget(poly_n_label)

    poly_n_slider = QSlider(Qt.Orientation.Horizontal)
    poly_n_slider.setMinimum(5)
    poly_n_slider.setMaximum(7)
    poly_n_slider.setValue(fb_config["poly_n"])
    poly_n_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    poly_n_slider.setTickInterval(1)
    poly_n_layout = QHBoxLayout()
    poly_n_layout.setSpacing(10)
    poly_n_layout.addWidget(poly_n_slider)
    poly_n_value_label = QLabel(str(poly_n_slider.value()))
    poly_n_layout.addWidget(poly_n_value_label)
    layout.addLayout(poly_n_layout)
    poly_n_slider.valueChanged.connect(lambda value: poly_n_value_label.setText(str(value)))

    # === Parameter poly_sigma ===
    poly_sigma_label = QLabel("Poly Sigma")
    poly_sigma_label.setToolTip(
        "Deskripsi: Standar deviasi untuk Gaussian smoothing. Nilai tipikal adalah 1.2."
    )
    poly_sigma_label.setFont(bold_font)
    layout.addWidget(poly_sigma_label)

    poly_sigma_slider = QSlider(Qt.Orientation.Horizontal)
    poly_sigma_slider.setMinimum(10)   # Misalnya, mewakili 0.10
    poly_sigma_slider.setMaximum(200)  # Mewakili 2.00
    poly_sigma_slider.setValue(int(fb_config["poly_sigma"] * 100))
    poly_sigma_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    poly_sigma_slider.setTickInterval(1)
    poly_sigma_layout = QHBoxLayout()
    poly_sigma_layout.setSpacing(10)
    poly_sigma_layout.addWidget(poly_sigma_slider)
    poly_sigma_value_label = QLabel(f"{poly_sigma_slider.value()/100:.2f}")
    poly_sigma_layout.addWidget(poly_sigma_value_label)
    layout.addLayout(poly_sigma_layout)
    poly_sigma_slider.valueChanged.connect(lambda value: poly_sigma_value_label.setText(f"{value/100:.2f}"))

    # === Parameter flags ===
    flags_label = QLabel("Flags")
    flags_label.setToolTip(
        "Deskripsi: Flags untuk optical flow Farneback. Nilai tipikal adalah 0."
    )
    flags_label.setFont(bold_font)
    layout.addWidget(flags_label)

    flags_slider = QSlider(Qt.Orientation.Horizontal)
    flags_slider.setMinimum(0)
    flags_slider.setMaximum(10)
    flags_slider.setValue(fb_config["flags"])
    flags_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    flags_slider.setTickInterval(1)
    flags_layout = QHBoxLayout()
    flags_layout.setSpacing(10)
    flags_layout.addWidget(flags_slider)
    flags_value_label = QLabel(str(flags_slider.value()))
    flags_layout.addWidget(flags_value_label)
    layout.addLayout(flags_layout)
    flags_slider.valueChanged.connect(lambda value: flags_value_label.setText(str(value)))

    # === Parameter Interpolation (ComboBox) ===
    interpolation_label = QLabel("Interpolation")
    interpolation_label.setToolTip(
        "Deskripsi: Metode interpolasi untuk remap. Contoh: INTER_AREA, INTER_LINEAR, INTER_CUBIC, INTER_NEAREST."
    )
    interpolation_label.setFont(bold_font)
    layout.addWidget(interpolation_label)

    interpolation_combo = QComboBox()
    interpolation_combo.addItems(["INTER_AREA", "INTER_LINEAR", "INTER_CUBIC", "INTER_NEAREST"])
    interpolation_combo.setCurrentText(fb_config.get("interpolation", "INTER_AREA"))
    interpolation_combo.setStyleSheet("""
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
    """)
    layout.addWidget(interpolation_combo)

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
        Simpan nilai dari widget ke file konfigurasi JSON pada bagian Farneback Optical Flow.
        """
        fb_params = {
            "pyr_scale": pyr_scale_slider.value() / 100.0,
            "levels": levels_slider.value(),
            "winsize": winsize_slider.value(),
            "iterations": iterations_slider.value(),
            "poly_n": poly_n_slider.value(),
            "poly_sigma": poly_sigma_slider.value() / 100.0,
            "flags": flags_slider.value(),
            "interpolation": interpolation_combo.currentText()
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

        all_params["Farneback"] = fb_params

        try:
            with open(config_filename, "w") as config_file:
                json.dump(all_params, config_file, indent=4)
            print("Settings applied and saved to", config_filename)
        except Exception as e:
            print("Error saving Farneback settings:", e)

    apply_button.clicked.connect(apply_settings)

    # Bungkus halaman dalam QScrollArea agar tampilan konsisten
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
