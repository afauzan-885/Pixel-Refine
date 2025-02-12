import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider,
                             QHBoxLayout, QPushButton, QScrollArea, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Pastikan Anda mengimpor modul ORB yang diperlukan
import UI.enhance_stack.algorithm.alignment.ORB

def get_orb_page():
    """
    Buat halaman pengaturan untuk ORB dengan widget untuk mengatur parameter algoritma.
    Jika file JSON ditemukan, gunakan nilai yang ada; jika tidak, gunakan nilai default.
    """
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)  # Atur jarak 10 pixel antar widget di layout utama

    # Ambil konfigurasi ORB, gunakan default jika file tidak ditemukan
    orb_config = UI.enhance_stack.algorithm.alignment.ORB.ORBAlgorithm.load_orb_config()

    # Siapkan font bold untuk semua label parameter
    bold_font = QFont()
    bold_font.setBold(True)

    # Judul halaman
    title_label = QLabel("Pengaturan ORB")
    title_label.setFont(bold_font)
    layout.addWidget(title_label)

    # === Parameter nfeatures ===
    nfeatures_label = QLabel("Jumlah Fitur (nfeatures)")
    nfeatures_label.setToolTip(
        "Deskripsi: Jumlah fitur menentukan berapa banyak fitur yang akan dideteksi dan disimpan.\n"
        "Efek: Lebih banyak fitur akan meningkatkan kualitas penyelarasan dan ketahanan terhadap variasi, "
        "tetapi juga akan meningkatkan waktu komputasi.\n"
        "Rekomendasi: Untuk kebanyakan aplikasi, nilai antara 500 hingga 2000 sudah cukup baik. "
        "Untuk aplikasi dengan kebutuhan tinggi, bisa mencapai 5000."
    )
    nfeatures_label.setFont(bold_font)
    layout.addWidget(nfeatures_label)
    nfeatures_slider = QSlider(Qt.Orientation.Horizontal)
    nfeatures_slider.setMinimum(100)
    nfeatures_slider.setMaximum(5000)
    nfeatures_slider.setValue(orb_config["nfeatures"])
    nfeatures_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    nfeatures_slider.setTickInterval(100)
    # Layout horizontal untuk slider dan label nilai
    nfeatures_layout = QHBoxLayout()
    nfeatures_layout.setSpacing(10)
    nfeatures_layout.addWidget(nfeatures_slider)
    nfeatures_value_label = QLabel(str(nfeatures_slider.value()))
    nfeatures_layout.addWidget(nfeatures_value_label)
    layout.addLayout(nfeatures_layout)
    nfeatures_slider.valueChanged.connect(lambda value: nfeatures_value_label.setText(str(value)))

    # === Parameter Scale Factor ===
    scale_factor_label = QLabel("Scale Factor")
    scale_factor_label.setToolTip(
        "Scale Factor (Faktor Skala)\n"
        "Deskripsi: Scale factor adalah rasio pengurangan piramida. "
        "Ini menentukan seberapa besar gambar akan diperkecil pada setiap level dalam piramida.\n"
        "Efek: Nilai yang lebih kecil (lebih dekat ke 1.0) berarti lebih banyak level dalam piramida, "
        "yang meningkatkan waktu komputasi tetapi juga memungkinkan deteksi fitur yang lebih halus. "
        "Nilai yang lebih besar mempercepat proses tetapi mungkin kehilangan fitur yang lebih kecil.\n"
        "Rekomendasi: Nilai umum yang digunakan adalah 1.2 hingga 1.5."
    )
    scale_factor_label.setFont(bold_font)
    layout.addWidget(scale_factor_label)
    scale_factor_slider = QSlider(Qt.Orientation.Horizontal)
    # Rentang 1.0 - 2.0: diwakili oleh nilai 10 - 20 (nilai sebenarnya = value/10)
    scale_factor_slider.setMinimum(10)
    scale_factor_slider.setMaximum(20)
    scale_factor_slider.setValue(int(orb_config["scaleFactor"] * 10))
    scale_factor_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    scale_factor_slider.setTickInterval(1)
    scale_factor_layout = QHBoxLayout()
    scale_factor_layout.setSpacing(10)
    scale_factor_layout.addWidget(scale_factor_slider)
    scale_factor_value_label = QLabel(f"{scale_factor_slider.value()/10:.1f}")
    scale_factor_layout.addWidget(scale_factor_value_label)
    layout.addLayout(scale_factor_layout)
    scale_factor_slider.valueChanged.connect(
        lambda value: scale_factor_value_label.setText(f"{value/10:.1f}")
    )

    # === Parameter nlevels ===
    nlevels_label = QLabel("Jumlah Level (nlevels)")
    nlevels_label.setToolTip(
        "Deskripsi: Jumlah level menentukan berapa banyak level piramida yang akan digunakan dalam deteksi fitur.\n"
        "Efek: Nilai yang lebih tinggi memungkinkan deteksi fitur pada berbagai skala, tetapi juga meningkatkan waktu komputasi.\n"
        "Rekomendasi: Nilai umum yang digunakan adalah antara 4 hingga 8."
    )
    nlevels_label.setFont(bold_font)
    layout.addWidget(nlevels_label)
    nlevels_slider = QSlider(Qt.Orientation.Horizontal)
    nlevels_slider.setMinimum(1)
    nlevels_slider.setMaximum(8)
    nlevels_slider.setValue(orb_config["nlevels"])
    nlevels_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    nlevels_slider.setTickInterval(1)
    nlevels_layout = QHBoxLayout()
    nlevels_layout.setSpacing(10)
    nlevels_layout.addWidget(nlevels_slider)
    nlevels_value_label = QLabel(str(nlevels_slider.value()))
    nlevels_layout.addWidget(nlevels_value_label)
    layout.addLayout(nlevels_layout)
    nlevels_slider.valueChanged.connect(lambda value: nlevels_value_label.setText(str(value)))

    # === Parameter Tipe Transformasi ===
    transformation_label = QLabel("Tipe Transformasi:")
    transformation_label.setToolTip(
        "Deskripsi: Jenis transformasi yang digunakan untuk menyelaraskan gambar, seperti homography, affine, similarity, atau euclidean.\n"
        "Efek:\n"
        "  - Homography: Mengizinkan transformasi perspektif. Baik untuk penyelarasan gambar dengan perbedaan sudut pandang.\n"
        "  - Affine: Mengizinkan rotasi, skala, dan translasi, tetapi tidak perspektif. Berguna untuk penyelarasan dengan perubahan bentuk sederhana.\n"
        "  - Similarity: Hanya mengizinkan rotasi, skala seragam, dan translasi.\n"
        "  - Euclidean: Hanya mengizinkan rotasi dan translasi.\n"
        "Rekomendasi: Pemilihan tergantung pada kebutuhan aplikasi spesifik. Homography sering digunakan untuk aplikasi penyelarasan umum."
    )
    transformation_label.setFont(bold_font)
    layout.addWidget(transformation_label)
    transformation_combo = QComboBox()
    transformation_combo.addItems(["homography", "affine", "similarity", "euclidean"])
    transformation_combo.setCurrentText(orb_config["transformation"])
    # Terapkan style sheet ke QComboBox
    combo_style = """
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
    transformation_combo.setStyleSheet(combo_style)
    layout.addWidget(transformation_combo)

    # === Parameter RANSAC Threshold ===
    ransac_label = QLabel("RANSAC Threshold:")
    ransac_label.setToolTip(
        "Deskripsi: Ambang batas untuk algoritma RANSAC yang digunakan untuk mengeliminasi outlier saat menyelaraskan gambar.\n"
        "Efek: Nilai yang lebih rendah lebih ketat dan lebih baik dalam mengeliminasi outlier tetapi bisa mengabaikan fitur penting."
        "Nilai yang lebih tinggi lebih toleran terhadap outlier tetapi bisa menyebabkan penyelarasan yang kurang tepat.\n"
        "Rekomendasi: Nilai umum yang digunakan adalah antara 1 hingga 5."
    )
    ransac_label.setFont(bold_font)
    layout.addWidget(ransac_label)
    ransac_slider = QSlider(Qt.Orientation.Horizontal)
    # Rentang 1.0 - 10.0: diwakili oleh nilai 10 - 100 (nilai sebenarnya = value/10)
    ransac_slider.setMinimum(10)
    ransac_slider.setMaximum(100)
    ransac_slider.setValue(int(orb_config["ransacThreshold"] * 10))
    ransac_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    ransac_slider.setTickInterval(5)
    ransac_layout = QHBoxLayout()
    ransac_layout.setSpacing(10)
    ransac_layout.addWidget(ransac_slider)
    ransac_value_label = QLabel(f"{ransac_slider.value()/10:.1f}")
    ransac_layout.addWidget(ransac_value_label)
    layout.addLayout(ransac_layout)
    ransac_slider.valueChanged.connect(
        lambda value: ransac_value_label.setText(f"{value/10:.1f}")
    )

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

    layout.addWidget(apply_button)

    def apply_settings():
        """
        Simpan nilai dari widget ke file konfigurasi JSON.
        Jika file konfigurasi global sudah ada, update bagian 'ORB'.
        Jika tidak, buat file baru.
        """
        orb_params = {
            "nfeatures": nfeatures_slider.value(),
            "scaleFactor": scale_factor_slider.value() / 10.0,
            "nlevels": nlevels_slider.value(),
            "transformation": transformation_combo.currentText(),
            "ransacThreshold": ransac_slider.value() / 10.0
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

        all_params["ORB"] = orb_params

        try:
            with open(config_filename, "w") as config_file:
                json.dump(all_params, config_file, indent=4)
            print("Settings applied and saved to", config_filename)
        except Exception as e:
            print("Error saving ORB settings:", e)

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
