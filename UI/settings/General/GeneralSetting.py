import json
import os
import sys
import time
from PyQt6.QtWidgets import (QWidget, QLabel, QComboBox, QFormLayout,
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QCheckBox, QSlider, QGroupBox,
                             QLineEdit)
from PyQt6.QtCore import QProcess, QCoreApplication, Qt, QLocale
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from UI.resources.stylesheet.stylesheet import APPLY_BUTTON, DROPDOWN_BOX, TOGGLE_SWITCH_STYLE
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

SETTINGS_DIR = "database/setting"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "app_setting.json")

# --- Fungsi Helper Load Settings (General) ---
def load_general_settings():
    """Memuat pengaturan dari app_setting.json."""
    defaults = {
        "language": "English",
        "gpu_acceleration": False,
        "multi_core_cpu": True,
        "enable_thumbnails": False,
        # Similarity V1
        "similarity_tile_size": 16,
        "similarity_motion_threshold": 0.030,
        "similarity_overlap_percent": 40.0,
        
        # --- Similarity V2 ---
        "similarity_v2_tile_size": 16,
        "similarity_v2_overlap_percent": 38.0,
        "similarity_v2_mbm_noise_mad_offset_factor": 0.65,
        "similarity_v2_mbm_mad_sensitivity": 18.8,
        "similarity_v2_mbm_confidence_skip_dft_threshold": 0.78,
        "similarity_v2_freq_merge_wiener_c_factor": 2.1,
        "similarity_v2_coarse_alignment_search_margin": 12
        # -------------
    }
    if not os.path.exists(GENERAL_SETTINGS_FILE):
        try: os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
        except OSError: pass
        return defaults
    try:
        with open(GENERAL_SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        # Pastikan semua keys dari defaults ada di settings
        for key, value in defaults.items():
            settings.setdefault(key, value)
        return settings
    except (json.JSONDecodeError, IOError):
        print(f"Warning: Could not read settings file '{GENERAL_SETTINGS_FILE}'. Using defaults.")
        return defaults

# --- Fungsi Pembuatan Komponen UI ---

def _create_language_settings(parent_layout, current_settings):
    """Membuat dan menambahkan pengaturan bahasa ke layout."""
    initial_language = current_settings.get("language", "English")
    language_label_text = getattr(language_config, 'LANGUAGE_LABEL', "Language:")
    language_label = QLabel(language_label_text)
    language_dropdown = QComboBox()
    languages = ["English", "Indonesian", "China Traditional", "Melayu"]
    # Logika pemilihan bahasa awal (sama seperti sebelumnya)
    current_lang_lower = initial_language.lower()
    selected_lang = next((lang for lang in languages if lang.lower() == current_lang_lower), None)
    if selected_lang:
        languages.remove(selected_lang)
        languages.insert(0, selected_lang)
    language_dropdown.addItems(languages)
    language_dropdown.setCurrentText(initial_language)
    language_dropdown.setStyleSheet(DROPDOWN_BOX)
    language_dropdown.setMinimumWidth(150)
    parent_layout.addRow(language_label, language_dropdown)
    return language_dropdown # Kembalikan widget agar bisa diakses save_settings

def _create_acceleration_settings(parent_layout, current_settings):
    """Membuat dan menambahkan pengaturan akselerasi GPU & CPU ke layout."""
    # GPU
    gpu_label_text = getattr(language_config, 'GPU_ACCELERATION_LABEL', "GPU Acceleration")
    gpu_checkbox = QCheckBox(gpu_label_text)
    gpu_checkbox.setChecked(current_settings.get("gpu_acceleration", False))
    gpu_checkbox.setToolTip(getattr(language_config, 'GPU_ACCELERATION_DESCRIPTION', ''))
    gpu_checkbox.setStyleSheet(TOGGLE_SWITCH_STYLE)
    parent_layout.addRow(gpu_checkbox)

    # CPU
    # Pastikan nama atribut benar (MULTI_CORE_CPU vs MULTI_CORE_CPU_LABEL)
    cpu_label_text = getattr(language_config, 'MULTI_CORE_CPU', "Multi-Core CPU") # Atau 'MULTI_CORE_CPU' ?
    cpu_checkbox = QCheckBox(cpu_label_text)
    cpu_checkbox.setToolTip(getattr(language_config, 'MULTI_CORE_CPU_DESCRIPTION', ''))
    cpu_checkbox.setChecked(current_settings.get("multi_core_cpu", True))
    cpu_checkbox.setStyleSheet(TOGGLE_SWITCH_STYLE)
    parent_layout.addRow(cpu_checkbox)

    # Kembalikan tuple/dict berisi widget
    return {"gpu": gpu_checkbox, "cpu": cpu_checkbox}

def _create_similarity_v1_group(current_settings):
    """Membuat QGroupBox yang berisi pengaturan Similarity V1."""
    similarity_group_title = getattr(language_config, 'SIMILARITY_V1_GROUP_TITLE', "Similarity V1 Parameters")
    similarity_group_box = QGroupBox(similarity_group_title)

    similarity_form_layout = QFormLayout()
    similarity_form_layout.setContentsMargins(10, 10, 10, 10)
    similarity_form_layout.setSpacing(10)
    similarity_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    similarity_form_layout.setHorizontalSpacing(15)

    similarity_widgets = {}

    # a. Tile Size (Tetap ComboBox)
    tile_size_label_text = getattr(language_config, 'TILE_SIZE_LABEL', "Tile Size:")
    tile_size_label = QLabel(tile_size_label_text)
    tile_size_label.setToolTip(getattr(language_config, 'TILE_SIZE_DESCRIPTION', ''))
    tile_size_combo = QComboBox()
    tile_options_int = [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256]
    tile_size_combo.addItems([str(size) for size in tile_options_int])
    initial_tile_size_int = current_settings.get("similarity_tile_size", 32)
    tile_size_combo.setCurrentText(str(initial_tile_size_int))
    tile_size_combo.setStyleSheet(DROPDOWN_BOX)
    tile_size_combo.setMinimumWidth(100)
    similarity_form_layout.addRow(tile_size_label, tile_size_combo)
    similarity_widgets['tile_combo'] = tile_size_combo

    # b. Motion Threshold (Slider + QLineEdit)
    motion_thresh_label_text = getattr(language_config, 'MOTION_THRESHOLD_LABEL', "Motion Threshold:")
    motion_thresh_label = QLabel(motion_thresh_label_text)
    motion_thresh_label.setToolTip(getattr(language_config, 'MOTION_THRESHOLD_DESCRIPTION', ''))
    motion_thresh_slider = QSlider(Qt.Orientation.Horizontal)
    motion_thresh_slider.setMinimum(1); motion_thresh_slider.setMaximum(100)
    motion_thresh_multiplier = 1000.0
    initial_motion_thresh = current_settings.get("similarity_motion_threshold", 0.030)
    motion_thresh_slider.setValue(int(initial_motion_thresh * motion_thresh_multiplier))
    motion_thresh_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    motion_thresh_input = QLineEdit(f"{initial_motion_thresh:.3f}")
    motion_thresh_input.setFixedWidth(60)
    motion_thresh_input.setAlignment(Qt.AlignmentFlag.AlignRight)

    c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry) 
    motion_thresh_input.setLocale(c_locale)
 
 
    motion_thresh_validator = QDoubleValidator(0.001, 0.1000, 5, motion_thresh_input)
    motion_thresh_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    motion_thresh_input.setValidator(motion_thresh_validator)

    motion_thresh_layout = QHBoxLayout()
    motion_thresh_layout.addWidget(motion_thresh_slider)
    motion_thresh_layout.addWidget(motion_thresh_input)
    similarity_form_layout.addRow(motion_thresh_label, motion_thresh_layout)
    similarity_widgets['motion_slider'] = motion_thresh_slider
    similarity_widgets['motion_input'] = motion_thresh_input

    motion_thresh_slider.valueChanged.connect(
        lambda value, inp=motion_thresh_input, m=motion_thresh_multiplier: inp.setText(f"{value / m:.3f}")
    )

    def update_motion_slider():
        current_locale = motion_thresh_input.locale()
        try:
            value_float, ok = current_locale.toDouble(motion_thresh_input.text()) # Gunakan locale
            if not ok: raise ValueError("Conversion failed")

            value_float = max(0.001, min(value_float, 0.1000))
            slider_value = int(round(value_float * motion_thresh_multiplier)) # Rounding bisa membantu

            motion_thresh_slider.blockSignals(True)
            motion_thresh_slider.setValue(slider_value)
            motion_thresh_slider.blockSignals(False)

            motion_thresh_input.setText(current_locale.toString(value_float, 'f', 4))

        except ValueError:
            current_slider_val = motion_thresh_slider.value()
            motion_thresh_input.setText(current_locale.toString(current_slider_val / motion_thresh_multiplier, 'f', 3))

    motion_thresh_input.editingFinished.connect(update_motion_slider)

    overlap_label_text = getattr(language_config, 'OVERLAP_LABEL', "Overlap %:")
    overlap_label = QLabel(overlap_label_text)
    overlap_label.setToolTip(getattr(language_config, 'OVERLAP_DESCRIPTION', ''))

    overlap_slider = QSlider(Qt.Orientation.Horizontal)
    overlap_slider.setMinimum(0); overlap_slider.setMaximum(90) # 0-90%
    initial_overlap_percent = current_settings.get("similarity_overlap_percent", 40.0)
    overlap_slider.setValue(int(initial_overlap_percent))
    overlap_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    # Ganti QLabel dengan QLineEdit untuk angka
    overlap_input = QLineEdit(f"{int(initial_overlap_percent)}")
    overlap_input.setFixedWidth(40) # Lebar lebih kecil untuk angka persen
    overlap_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    # Tambahkan Validator untuk integer 0-90
    overlap_validator = QIntValidator(0, 90, overlap_input)
    overlap_input.setValidator(overlap_validator)

    # Tambahkan QLabel statis untuk "%"
    percent_label = QLabel("%")

    # Layout untuk slider, input field, dan label %
    overlap_layout = QHBoxLayout()
    overlap_layout.addWidget(overlap_slider)
    overlap_layout.addWidget(overlap_input)
    overlap_layout.addWidget(percent_label) # Tambahkan label %
    similarity_form_layout.addRow(overlap_label, overlap_layout)
    similarity_widgets['overlap_slider'] = overlap_slider
    similarity_widgets['overlap_input'] = overlap_input # Simpan referensi input

    # --- Koneksi dua arah untuk Overlap ---
    # 1. Slider -> Input
    overlap_slider.valueChanged.connect(
        lambda value, inp=overlap_input: inp.setText(f"{value}")
    )

    # 2. Input -> Slider
    def update_overlap_slider():
        try:
            value_int = int(overlap_input.text())
            # Clamp nilai int ke range valid (0 - 90)
            value_int = max(0, min(value_int, 90))

            # Set slider (cegah sinyal balik)
            overlap_slider.blockSignals(True)
            overlap_slider.setValue(value_int)
            overlap_slider.blockSignals(False)

            # Set ulang teks input untuk konsistensi (hapus leading zero dll)
            overlap_input.setText(f"{value_int}")

        except ValueError:
            # Jika input tidak valid, reset input ke nilai slider saat ini
            current_slider_val = overlap_slider.value()
            overlap_input.setText(f"{current_slider_val}")

    overlap_input.editingFinished.connect(update_overlap_slider)
    # ----------------------------------------

    # Set layout untuk GroupBox
    similarity_group_box.setLayout(similarity_form_layout)

    # Kembalikan group box DAN dictionary widget inputnya
    return similarity_group_box, similarity_widgets

def _create_similarity_v2_group(current_settings):
    """Membuat QGroupBox yang berisi pengaturan Similarity V2."""
    similarity_group_title = getattr(language_config, 'SIMILARITY_V2_GROUP_TITLE', "Similarity V2 Parameters")
    similarity_group_box = QGroupBox(similarity_group_title)

    similarity_form_layout = QFormLayout()
    similarity_form_layout.setContentsMargins(10, 10, 10, 10)
    similarity_form_layout.setSpacing(10)
    similarity_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    similarity_form_layout.setHorizontalSpacing(15)

    similarity_widgets_v2 = {}
    c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)

    # a. Tile Size (V2)
    tile_size_label_text = getattr(language_config, 'TILE_SIZE_LABEL', "Tile Size:")
    tile_size_label = QLabel(tile_size_label_text)
    tile_size_label.setToolTip(getattr(language_config, 'TILE_SIZE_DESCRIPTION', ''))
    tile_size_combo = QComboBox()
    tile_options_int = [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256]
    tile_options = [str(size) for size in tile_options_int]
    tile_size_combo.addItems(tile_options)
    initial_tile_size_int = current_settings.get("similarity_v2_tile_size", 16)
    tile_size_combo.setCurrentText(str(initial_tile_size_int))
    tile_size_combo.setStyleSheet(DROPDOWN_BOX)
    tile_size_combo.setMinimumWidth(100)
    similarity_form_layout.addRow(tile_size_label, tile_size_combo)
    similarity_widgets_v2['tile_combo'] = tile_size_combo

    # c. Overlap (V2)
    overlap_label_text = getattr(language_config, 'OVERLAP_LABEL', "Overlap %:")
    overlap_label = QLabel(overlap_label_text)
    overlap_label.setToolTip(getattr(language_config, 'OVERLAP_DESCRIPTION', ''))
    overlap_slider = QSlider(Qt.Orientation.Horizontal)
    overlap_slider.setMinimum(0); overlap_slider.setMaximum(90)
    initial_overlap_percent = current_settings.get("similarity_v2_overlap_percent", 38.0)
    overlap_slider.setValue(int(initial_overlap_percent))
    overlap_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))
    overlap_input = QLineEdit(f"{int(initial_overlap_percent)}")
    overlap_input.setFixedWidth(40)
    overlap_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    overlap_validator = QIntValidator(0, 90, overlap_input)
    overlap_input.setValidator(overlap_validator)
    percent_label = QLabel("%")
    overlap_layout = QHBoxLayout()
    overlap_layout.addWidget(overlap_slider)
    overlap_layout.addWidget(overlap_input)
    overlap_layout.addWidget(percent_label)
    similarity_form_layout.addRow(overlap_label, overlap_layout)
    similarity_widgets_v2['overlap_slider'] = overlap_slider
    similarity_widgets_v2['overlap_input'] = overlap_input
    overlap_slider.valueChanged.connect(
        lambda value, inp=overlap_input: inp.setText(f"{value}")
    )
    def update_overlap_slider_v2():
        try:
            value_int = int(overlap_input.text())
            value_int = max(0, min(value_int, 90))
            overlap_slider.blockSignals(True)
            overlap_slider.setValue(value_int)
            overlap_slider.blockSignals(False)
            overlap_input.setText(f"{value_int}")
        except ValueError:
            current_slider_val = overlap_slider.value()
            overlap_input.setText(f"{current_slider_val}")
    overlap_input.editingFinished.connect(update_overlap_slider_v2)

    # NEW: Tambahan Parameter untuk Similarity V2
    # d. MBM Noise MAD Offset Factor
    noise_mad_label_text = getattr(language_config, 'NOISE_MAD_OFFSET_LABEL', "Noise MAD Offset Factor:")
    noise_mad_label = QLabel(noise_mad_label_text)
    noise_mad_label.setToolTip(getattr(language_config, 'NOISE_MAD_OFFSET_DESCRIPTION', 'Factor for noise MAD offset.'))

    noise_mad_slider = QSlider(Qt.Orientation.Horizontal)
    noise_mad_slider_min, noise_mad_slider_max = 0, 200 # 0.00 to 2.00
    noise_mad_multiplier = 100.0
    noise_mad_slider.setMinimum(noise_mad_slider_min); noise_mad_slider.setMaximum(noise_mad_slider_max)
    initial_noise_mad = current_settings.get("similarity_v2_mbm_noise_mad_offset_factor", 0.65)
    noise_mad_slider.setValue(int(round(initial_noise_mad * noise_mad_multiplier)))
    noise_mad_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    noise_mad_input = QLineEdit(f"{initial_noise_mad:.2f}") # 2 desimal
    noise_mad_input.setFixedWidth(50)
    noise_mad_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    noise_mad_input.setLocale(c_locale)
    noise_mad_validator = QDoubleValidator(0.0, 5.0, 2, noise_mad_input)
    noise_mad_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    noise_mad_input.setValidator(noise_mad_validator)

    noise_mad_layout = QHBoxLayout()
    noise_mad_layout.addWidget(noise_mad_slider)
    noise_mad_layout.addWidget(noise_mad_input)
    similarity_form_layout.addRow(noise_mad_label, noise_mad_layout)
    similarity_widgets_v2['noise_mad_slider'] = noise_mad_slider
    similarity_widgets_v2['noise_mad_input'] = noise_mad_input

    noise_mad_slider.valueChanged.connect(
        lambda value, inp=noise_mad_input, m=noise_mad_multiplier, loc=c_locale:
            inp.setText(loc.toString(value / m, 'f', 2))
    )
    def update_noise_mad_slider_v2():
        current_locale = noise_mad_input.locale()
        try:
            value_float, ok = current_locale.toDouble(noise_mad_input.text())
            if not ok: raise ValueError("Conversion failed")
            value_float = max(0.0, min(value_float, 5.0))
            slider_value = int(round(value_float * noise_mad_multiplier))
            slider_value = max(noise_mad_slider_min, min(slider_value, noise_mad_slider_max))

            noise_mad_slider.blockSignals(True)
            noise_mad_slider.setValue(slider_value)
            noise_mad_slider.blockSignals(False)
            noise_mad_input.setText(current_locale.toString(value_float, 'f', 2))
        except ValueError:
            current_slider_val = noise_mad_slider.value()
            noise_mad_input.setText(current_locale.toString(current_slider_val / noise_mad_multiplier, 'f', 2))
    noise_mad_input.editingFinished.connect(update_noise_mad_slider_v2)

    # e. MBM MAD Sensitivity
    mad_sens_label_text = getattr(language_config, 'MAD_SENSITIVITY_LABEL', "MAD Sensitivity")
    mad_sens_label = QLabel(mad_sens_label_text)
    mad_sens_label.setToolTip(getattr(language_config, 'MAD_SENSITIVITY_DESCRIPTION', 'Sensitivity for MAD calculation.'))

    mad_sens_slider = QSlider(Qt.Orientation.Horizontal)
    mad_sens_slider_min, mad_sens_slider_max = 10, 500
    mad_sens_multiplier = 10.0
    mad_sens_slider.setMinimum(mad_sens_slider_min); mad_sens_slider.setMaximum(mad_sens_slider_max)
    initial_mad_sens = current_settings.get("similarity_v2_mbm_mad_sensitivity", 18.8)
    mad_sens_slider.setValue(int(round(initial_mad_sens * mad_sens_multiplier)))
    mad_sens_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    mad_sens_input = QLineEdit(f"{initial_mad_sens:.1f}")
    mad_sens_input.setFixedWidth(50)
    mad_sens_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    mad_sens_input.setLocale(c_locale)
    mad_sens_validator = QDoubleValidator(0.1, 100.0, 1, mad_sens_input)
    mad_sens_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    mad_sens_input.setValidator(mad_sens_validator)

    mad_sens_layout = QHBoxLayout()
    mad_sens_layout.addWidget(mad_sens_slider)
    mad_sens_layout.addWidget(mad_sens_input)
    similarity_form_layout.addRow(mad_sens_label, mad_sens_layout)
    similarity_widgets_v2['mad_sens_slider'] = mad_sens_slider
    similarity_widgets_v2['mad_sens_input'] = mad_sens_input

    mad_sens_slider.valueChanged.connect(
        lambda value, inp=mad_sens_input, m=mad_sens_multiplier, loc=c_locale:
            inp.setText(loc.toString(value / m, 'f', 1))
    )
    def update_mad_sens_slider_v2():
        current_locale = mad_sens_input.locale()
        try:
            value_float, ok = current_locale.toDouble(mad_sens_input.text())
            if not ok: raise ValueError("Conversion failed")
            value_float = max(0.1, min(value_float, 100.0))
            slider_value = int(round(value_float * mad_sens_multiplier))
            slider_value = max(mad_sens_slider_min, min(slider_value, mad_sens_slider_max))

            mad_sens_slider.blockSignals(True)
            mad_sens_slider.setValue(slider_value)
            mad_sens_slider.blockSignals(False)
            mad_sens_input.setText(current_locale.toString(value_float, 'f', 1))
        except ValueError:
            current_slider_val = mad_sens_slider.value()
            mad_sens_input.setText(current_locale.toString(current_slider_val / mad_sens_multiplier, 'f', 1))
    mad_sens_input.editingFinished.connect(update_mad_sens_slider_v2)

    # f. MBM Confidence Skip DFT Threshold
    conf_skip_label_text = getattr(language_config, 'CONF_SKIP_DFT_LABEL', "Confidence Skip DFT Thresh:")
    conf_skip_label = QLabel(conf_skip_label_text)
    conf_skip_label.setToolTip(getattr(language_config, 'CONF_SKIP_DFT_DESCRIPTION', 'Threshold to skip DFT based on confidence.'))

    conf_skip_slider = QSlider(Qt.Orientation.Horizontal)
    
    conf_skip_slider_min, conf_skip_slider_max = 1, 300
    conf_skip_multiplier = 10.0 
    conf_skip_slider.setMinimum(conf_skip_slider_min)
    conf_skip_slider.setMaximum(conf_skip_slider_max)

    initial_conf_skip = current_settings.get("similarity_v2_mbm_confidence_skip_dft_threshold", 0.78) # Sesuaikan default jika perlu
    initial_conf_skip_clamped = max(0.1, min(initial_conf_skip, 30.0))

    conf_skip_slider.setValue(int(round(initial_conf_skip_clamped * conf_skip_multiplier)))
    conf_skip_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    conf_skip_input = QLineEdit(f"{initial_conf_skip_clamped:.1f}") # 1 desimal
    conf_skip_input.setFixedWidth(60) # Mungkin perlu sedikit lebih lebar jika angka lebih besar
    conf_skip_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    conf_skip_input.setLocale(c_locale)
    # Validator: Range 0.1 - 30.0, misal 2 desimal untuk input presisi (slider hanya 1 desimal)
    conf_skip_validator = QDoubleValidator(0.1, 30.0, 2, conf_skip_input)
    conf_skip_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    conf_skip_input.setValidator(conf_skip_validator)

    conf_skip_layout = QHBoxLayout()
    conf_skip_layout.addWidget(conf_skip_slider)
    conf_skip_layout.addWidget(conf_skip_input)
    similarity_form_layout.addRow(conf_skip_label, conf_skip_layout)
    similarity_widgets_v2['conf_skip_slider'] = conf_skip_slider
    similarity_widgets_v2['conf_skip_input'] = conf_skip_input

    # Koneksi Slider -> Input (tampilkan 1 desimal dari slider)
    conf_skip_slider.valueChanged.connect(
        lambda value, inp=conf_skip_input, m=conf_skip_multiplier, loc=c_locale:
            inp.setText(loc.toString(value / m, 'f', 1))
    )
    def update_conf_skip_slider_v2():
        current_locale = conf_skip_input.locale()
        try:
            value_float_str = conf_skip_input.text()
            value_float, ok = current_locale.toDouble(value_float_str)
            if not ok: raise ValueError(f"Conversion failed for: {value_float_str}")

            # Clamp nilai input ke rentang valid (0.1 - 30.0)
            value_float_clamped = max(0.1, min(value_float, 30.0))

            # Hitung nilai slider (integer) dari float yang sudah di-clamp
            slider_value = int(round(value_float_clamped * conf_skip_multiplier))
            # Clamp nilai slider ke rentang min/max slider
            slider_value = max(conf_skip_slider_min, min(slider_value, conf_skip_slider_max))

            conf_skip_slider.blockSignals(True)
            conf_skip_slider.setValue(slider_value)
            conf_skip_slider.blockSignals(False)

            # Set ulang teks input ke nilai yang sudah di-clamp dan diformat (misal 2 desimal untuk konsistensi)
            # atau 1 desimal jika ingin sama dengan tampilan dari slider
            conf_skip_input.setText(current_locale.toString(value_float_clamped, 'f', 1)) # Tampilkan 1 desimal

        except ValueError:
            # Jika input tidak valid, reset input ke nilai slider saat ini (format 1 desimal dari slider)
            current_slider_val = conf_skip_slider.value()
            conf_skip_input.setText(current_locale.toString(current_slider_val / conf_skip_multiplier, 'f', 1))
    conf_skip_input.editingFinished.connect(update_conf_skip_slider_v2)

    # g. Freq Merge Wiener C Factor
    wiener_c_label_text = getattr(language_config, 'WIENER_C_FACTOR_LABEL', "Wiener C Factor:")
    wiener_c_label = QLabel(wiener_c_label_text)
    wiener_c_label.setToolTip(getattr(language_config, 'WIENER_C_FACTOR_DESCRIPTION', 'C factor for Wiener filter in frequency merging.'))

    wiener_c_slider = QSlider(Qt.Orientation.Horizontal)
    wiener_c_slider_min, wiener_c_slider_max = 10, 100 # 1.0 to 10.0
    wiener_c_multiplier = 10.0
    wiener_c_slider.setMinimum(wiener_c_slider_min); wiener_c_slider.setMaximum(wiener_c_slider_max)
    initial_wiener_c = current_settings.get("similarity_v2_freq_merge_wiener_c_factor", 2.1)
    wiener_c_slider.setValue(int(round(initial_wiener_c * wiener_c_multiplier)))
    wiener_c_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    wiener_c_input = QLineEdit(f"{initial_wiener_c:.1f}") # 1 desimal
    wiener_c_input.setFixedWidth(50)
    wiener_c_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    wiener_c_input.setLocale(c_locale)
    wiener_c_validator = QDoubleValidator(0.1, 20.0, 2, wiener_c_input) # Range 0.1 - 20.0, 2 desimal
    wiener_c_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    wiener_c_input.setValidator(wiener_c_validator)

    wiener_c_layout = QHBoxLayout()
    wiener_c_layout.addWidget(wiener_c_slider)
    wiener_c_layout.addWidget(wiener_c_input)
    similarity_form_layout.addRow(wiener_c_label, wiener_c_layout)
    similarity_widgets_v2['wiener_c_slider'] = wiener_c_slider
    similarity_widgets_v2['wiener_c_input'] = wiener_c_input

    wiener_c_slider.valueChanged.connect(
        lambda value, inp=wiener_c_input, m=wiener_c_multiplier, loc=c_locale:
            inp.setText(loc.toString(value / m, 'f', 1))
    )
    def update_wiener_c_slider_v2():
        current_locale = wiener_c_input.locale()
        try:
            value_float, ok = current_locale.toDouble(wiener_c_input.text())
            if not ok: raise ValueError("Conversion failed")
            value_float = max(0.1, min(value_float, 20.0))
            slider_value = int(round(value_float * wiener_c_multiplier))
            slider_value = max(wiener_c_slider_min, min(slider_value, wiener_c_slider_max))

            wiener_c_slider.blockSignals(True)
            wiener_c_slider.setValue(slider_value)
            wiener_c_slider.blockSignals(False)
            wiener_c_input.setText(current_locale.toString(value_float, 'f', 1)) # Tampilkan 1 desimal, simpan bisa lebih
        except ValueError:
            current_slider_val = wiener_c_slider.value()
            wiener_c_input.setText(current_locale.toString(current_slider_val / wiener_c_multiplier, 'f', 1))
    wiener_c_input.editingFinished.connect(update_wiener_c_slider_v2)

    # h. Coarse Alignment Search Margin
    coarse_margin_label_text = getattr(language_config, 'COARSE_MARGIN_LABEL', "Coarse Align Margin:")
    coarse_margin_label = QLabel(coarse_margin_label_text)
    coarse_margin_label.setToolTip(getattr(language_config, 'COARSE_MARGIN_DESCRIPTION', 'Search margin for coarse alignment (pixels).'))

    coarse_margin_slider = QSlider(Qt.Orientation.Horizontal)
    coarse_margin_slider_min, coarse_margin_slider_max = 0, 64
    coarse_margin_slider.setMinimum(coarse_margin_slider_min); coarse_margin_slider.setMaximum(coarse_margin_slider_max)
    initial_coarse_margin = current_settings.get("similarity_v2_coarse_alignment_search_margin", 12)
    coarse_margin_slider.setValue(int(initial_coarse_margin))
    coarse_margin_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    coarse_margin_input = QLineEdit(f"{int(initial_coarse_margin)}")
    coarse_margin_input.setFixedWidth(40)
    coarse_margin_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    coarse_margin_validator = QIntValidator(0, 128, coarse_margin_input) # Range 0 - 128
    coarse_margin_input.setValidator(coarse_margin_validator)

    coarse_margin_layout = QHBoxLayout()
    coarse_margin_layout.addWidget(coarse_margin_slider)
    coarse_margin_layout.addWidget(coarse_margin_input)
    similarity_form_layout.addRow(coarse_margin_label, coarse_margin_layout)
    similarity_widgets_v2['coarse_margin_slider'] = coarse_margin_slider
    similarity_widgets_v2['coarse_margin_input'] = coarse_margin_input
    
    coarse_margin_slider.valueChanged.connect(
        lambda value, inp=coarse_margin_input: inp.setText(f"{value}")
    )
    def update_coarse_margin_slider_v2():
        try:
            value_int = int(coarse_margin_input.text())
            value_int = max(0, min(value_int, 128)) # Clamp ke validator range
            value_int = max(coarse_margin_slider_min, min(value_int, coarse_margin_slider_max)) # Clamp ke slider range

            coarse_margin_slider.blockSignals(True)
            coarse_margin_slider.setValue(value_int)
            coarse_margin_slider.blockSignals(False)
            coarse_margin_input.setText(f"{value_int}")
        except ValueError:
            current_slider_val = coarse_margin_slider.value()
            coarse_margin_input.setText(f"{current_slider_val}")
    coarse_margin_input.editingFinished.connect(update_coarse_margin_slider_v2)
    # END NEW PARAMETERS

    # Tombol Reset
    reset_button = QPushButton("Reset to Defaults")
    reset_button.setStyleSheet(APPLY_BUTTON)
    reset_button.setMinimumHeight(30)
    similarity_form_layout.addRow(reset_button) 
    similarity_widgets_v2['reset_button'] = reset_button

    def reset_defaults_v2():
        """Mengembalikan widget ke nilai default."""
        tile_size_combo.setCurrentText(str(16))
        overlap_slider.setValue(40)
        overlap_input.setText("40")

        noise_mad_slider.setValue(int(round(0.5 * noise_mad_multiplier)))
        noise_mad_input.setText(c_locale.toString(0.5, 'f', 2))

        mad_sens_slider.setValue(int(round(20.0 * mad_sens_multiplier)))
        mad_sens_input.setText(c_locale.toString(20.0, 'f', 1))

        conf_skip_slider.setValue(int(round(0.9 * conf_skip_multiplier)))
        conf_skip_input.setText(c_locale.toString(0.9, 'f', 1))

        wiener_c_slider.setValue(int(round(2.0 * wiener_c_multiplier)))
        wiener_c_input.setText(c_locale.toString(2.0, 'f', 1))

        coarse_margin_slider.setValue(12)
        coarse_margin_input.setText("12")

    reset_button.clicked.connect(reset_defaults_v2)

    similarity_group_box.setLayout(similarity_form_layout)
    return similarity_group_box, similarity_widgets_v2

def _create_apply_button():
    """Membuat layout dan tombol Apply."""
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    apply_button_text = getattr(language_config, 'APPLY_PARAMETER_BUTTON_TEXT', "Apply Settings")
    apply_button = QPushButton(apply_button_text)
    button_layout.addWidget(apply_button)
    apply_button.setStyleSheet(APPLY_BUTTON)
    apply_button.setMinimumHeight(30)
    return button_layout, apply_button

# --- Fungsi Utama (Orchestrator) ---
def general_page():
    """Creates the general settings tab by composing smaller functions."""
    general_tab = QWidget()
    general_tab.setStyleSheet(
        """
        QWidget { background-color: #ffffff; border: none; }
        QGroupBox {
            font-weight: bold; border: 1px solid gray; border-radius: 5px;
            margin-top: 10px; padding-top: 15px; padding-left: 5px;
            padding-right: 5px; padding-bottom: 5px;
            max-width: 350px; /* MODIFIED: increased max-width for more params */
            min-width: 100px;
        }
        QGroupBox::title {
            subcontrol-origin: margin; subcontrol-position: top left;
            padding: 0 3px; left: 10px;
        }
        """
    )

    current_settings = load_general_settings()
    initial_language = current_settings.get("language", "English")

    main_layout = QVBoxLayout(general_tab)
    top_form_layout = QFormLayout()
    top_form_layout.setContentsMargins(15, 15, 15, 15)
    top_form_layout.setSpacing(12)
    top_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    top_form_layout.setHorizontalSpacing(20)

    language_dropdown = _create_language_settings(top_form_layout, current_settings)
    accel_widgets = _create_acceleration_settings(top_form_layout, current_settings)
    gpu_checkbox = accel_widgets['gpu']
    cpu_checkbox = accel_widgets['cpu']
    main_layout.addLayout(top_form_layout)

    similarity_groups_layout = QHBoxLayout()
    similarity_group_box_v1, similarity_widgets_v1 = _create_similarity_v1_group(current_settings)
    tile_size_combo_v1 = similarity_widgets_v1['tile_combo']
    motion_thresh_slider_v1 = similarity_widgets_v1['motion_slider'] # V1 slider used for saving
    # motion_thresh_input_v1 = similarity_widgets_v1['motion_input'] # V1 input
    overlap_slider_v1 = similarity_widgets_v1['overlap_slider'] # V1 slider used for saving
    # overlap_input_v1 = similarity_widgets_v1['overlap_input']   # V1 input
    similarity_groups_layout.addWidget(similarity_group_box_v1)

    similarity_group_box_v2, similarity_widgets_v2 = _create_similarity_v2_group(current_settings)
    tile_size_combo_v2 = similarity_widgets_v2['tile_combo']
    # motion_thresh_slider_v2 = similarity_widgets_v2['motion_slider'] # V2 slider
    # overlap_slider_v2 = similarity_widgets_v2['overlap_slider']     # V2 slider
    similarity_groups_layout.addWidget(similarity_group_box_v2)

    similarity_groups_layout.addStretch()
    main_layout.addLayout(similarity_groups_layout)
    main_layout.addStretch()

    apply_button_layout, apply_button = _create_apply_button()
    main_layout.addLayout(apply_button_layout)

    # MODIFIED: save_settings
    def save_settings():
        new_language = language_dropdown.currentText()
        new_gpu_setting = gpu_checkbox.isChecked()
        new_multicore_setting = cpu_checkbox.isChecked()
        try:
            new_tile_size_int_v1 = int(tile_size_combo_v1.currentText())
        except ValueError:
            QMessageBox.warning(general_tab, "Invalid Input", "Invalid Tile Size for V1.")
            return

        motion_thresh_multiplier_v1 = 1000.0 # Sesuai V1
        new_motion_threshold_v1 = motion_thresh_slider_v1.value() / motion_thresh_multiplier_v1
        new_overlap_percent_v1 = float(overlap_slider_v1.value())

        try:
            new_tile_size_int_v2 = int(tile_size_combo_v2.currentText())
        except ValueError:
            QMessageBox.warning(general_tab, "Invalid Input", "Invalid Tile Size for V2.")
            return

        # Ambil nilai dari QLineEdit untuk presisi
        c_locale_save = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)

        # Overlap V2 (dari input)
        overlap_input_v2 = similarity_widgets_v2['overlap_input']
        try:
            v2_overlap_text = overlap_input_v2.text()
            new_overlap_percent_v2 = float(v2_overlap_text)
            new_overlap_percent_v2 = max(0.0, min(new_overlap_percent_v2, 90.0)) # Clamp
        except ValueError:
            QMessageBox.warning(general_tab, "Invalid Input", f"Invalid Overlap V2: '{v2_overlap_text}'.")
            return

        # NEW: Ambil nilai parameter V2 tambahan dari QLineEdit
        try:
            # Noise MAD Offset Factor
            noise_mad_input_v2 = similarity_widgets_v2['noise_mad_input']
            v2_noise_mad_text = noise_mad_input_v2.text()
            new_noise_mad_v2, ok_nm = c_locale_save.toDouble(v2_noise_mad_text)
            if not ok_nm: raise ValueError(f"Invalid Noise MAD Offset: {v2_noise_mad_text}")
            new_noise_mad_v2 = max(0.0, min(new_noise_mad_v2, 5.0)) # Sesuai validator

            # MAD Sensitivity
            mad_sens_input_v2 = similarity_widgets_v2['mad_sens_input']
            v2_mad_sens_text = mad_sens_input_v2.text()
            new_mad_sens_v2, ok_ms = c_locale_save.toDouble(v2_mad_sens_text)
            if not ok_ms: raise ValueError(f"Invalid MAD Sensitivity: {v2_mad_sens_text}")
            new_mad_sens_v2 = max(0.1, min(new_mad_sens_v2, 100.0)) # Sesuai validator

            # Confidence Skip DFT Threshold
            conf_skip_input_v2 = similarity_widgets_v2['conf_skip_input']
            v2_conf_skip_text = conf_skip_input_v2.text()
            new_conf_skip_v2, ok_cs = c_locale_save.toDouble(v2_conf_skip_text)
            if not ok_cs: raise ValueError(f"Invalid Confidence Skip DFT: {v2_conf_skip_text}")
            new_conf_skip_v2 = max(0.1, min(new_conf_skip_v2, 30.0)) # Sesuai validator

            # Wiener C Factor
            wiener_c_input_v2 = similarity_widgets_v2['wiener_c_input']
            v2_wiener_c_text = wiener_c_input_v2.text()
            new_wiener_c_v2, ok_wc = c_locale_save.toDouble(v2_wiener_c_text)
            if not ok_wc: raise ValueError(f"Invalid Wiener C Factor: {v2_wiener_c_text}")
            new_wiener_c_v2 = max(0.1, min(new_wiener_c_v2, 20.0)) # Sesuai validator

            # Coarse Alignment Search Margin
            coarse_margin_input_v2 = similarity_widgets_v2['coarse_margin_input']
            v2_coarse_margin_text = coarse_margin_input_v2.text()
            new_coarse_margin_v2 = int(v2_coarse_margin_text)
            new_coarse_margin_v2 = max(0, min(new_coarse_margin_v2, 128)) # Sesuai validator

        except ValueError as e_val:
            QMessageBox.warning(general_tab, "Invalid Input", f"Error in V2 parameter: {e_val}. Settings not saved.")
            return

        settings_to_save_general = {
            "language": new_language,
            "gpu_acceleration": new_gpu_setting,
            "multi_core_cpu": new_multicore_setting,
            # V1
            "similarity_tile_size": new_tile_size_int_v1,
            "similarity_motion_threshold": new_motion_threshold_v1,
            "similarity_overlap_percent": new_overlap_percent_v1,
            # V2
            "similarity_v2_tile_size": new_tile_size_int_v2,
            "similarity_v2_overlap_percent": new_overlap_percent_v2,
            "similarity_v2_mbm_noise_mad_offset_factor": new_noise_mad_v2,
            "similarity_v2_mbm_mad_sensitivity": new_mad_sens_v2,
            "similarity_v2_mbm_confidence_skip_dft_threshold": new_conf_skip_v2,
            "similarity_v2_freq_merge_wiener_c_factor": new_wiener_c_v2,
            "similarity_v2_coarse_alignment_search_margin": new_coarse_margin_v2
        }

        general_save_successful = False
        try:
            os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
            with open(GENERAL_SETTINGS_FILE, "w") as f:
                json.dump(settings_to_save_general, f, indent=4)
            general_save_successful = True
        except Exception as e:
             QMessageBox.critical(general_tab, "Error Saving Settings", f"Could not save general settings... Error: {e}")
             return

        if general_save_successful:
            specific_file_needs_writing = False
            try:
                all_specific_params = {}
                if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
                    try:
                        with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f_specific:
                            all_specific_params = json.load(f_specific)
                    except Exception as e_read:
                         QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but failed to read algorithm settings... Error: {e_read}")
                         all_specific_params = None 
                else:
                    all_specific_params = {}

                if all_specific_params is not None:
                    algo_keys_cpu = ["Farneback", "ORB", "AKAZE"]
                    algo_keys_gpu = ["Farneback"]

                    for key in algo_keys_cpu:
                         if key not in all_specific_params: all_specific_params[key] = {}; specific_file_needs_writing = True
                         if isinstance(all_specific_params.get(key), dict):
                             if all_specific_params[key].get("use_multi_core") != new_multicore_setting:
                                 all_specific_params[key]["use_multi_core"] = new_multicore_setting; specific_file_needs_writing = True

                    for key in algo_keys_gpu:
                         if isinstance(all_specific_params.get(key), dict): # Farneback sudah ada dari loop CPU
                              if all_specific_params[key].get("use_gpu") != new_gpu_setting:
                                  all_specific_params[key]["use_gpu"] = new_gpu_setting; specific_file_needs_writing = True
                    
                    # --- Update Similarity V1 ---
                    similarity_section_key_v1 = "Similarity"
                    tile_size_key_v1 = "tileGridSize"
                    motion_thresh_key_v1 = "motionThreshold"
                    overlap_key_v1 = "overlapRatio"

                    if similarity_section_key_v1 not in all_specific_params: all_specific_params[similarity_section_key_v1] = {}; specific_file_needs_writing = True
                    if isinstance(all_specific_params.get(similarity_section_key_v1), dict):
                        params_v1 = all_specific_params[similarity_section_key_v1]
                        list_v1 = [new_tile_size_int_v1, new_tile_size_int_v1]
                        if params_v1.get(tile_size_key_v1) != list_v1: params_v1[tile_size_key_v1] = list_v1; specific_file_needs_writing = True
                        if abs(params_v1.get(motion_thresh_key_v1, -1.0) - new_motion_threshold_v1) > 1e-6: params_v1[motion_thresh_key_v1] = new_motion_threshold_v1; specific_file_needs_writing = True
                        ratio_v1 = new_overlap_percent_v1 / 100.0
                        if abs(params_v1.get(overlap_key_v1, -1.0) - ratio_v1) > 1e-6: params_v1[overlap_key_v1] = ratio_v1; specific_file_needs_writing = True


                    # --- Similarity V2 ---
                    similarity_section_key_v2 = "Similarity_V2"
                    tile_size_key_v2 = "tileGridSize"
                    overlap_key_v2 = "overlapRatio"
                    noise_mad_key_v2 = "mbm_noise_mad_offset_factor"
                    mad_sens_key_v2 = "mbm_mad_sensitivity"
                    conf_skip_key_v2 = "mbm_confidence_skip_dft_threshold"
                    wiener_c_key_v2 = "freq_merge_wiener_c_factor"
                    coarse_margin_key_v2 = "coarse_alignment_search_margin"

                    if similarity_section_key_v2 not in all_specific_params: all_specific_params[similarity_section_key_v2] = {}; specific_file_needs_writing = True
                    if isinstance(all_specific_params.get(similarity_section_key_v2), dict):
                        params_v2 = all_specific_params[similarity_section_key_v2]
                        list_v2 = [new_tile_size_int_v2, new_tile_size_int_v2]
                        if params_v2.get(tile_size_key_v2) != list_v2: params_v2[tile_size_key_v2] = list_v2; specific_file_needs_writing = True
                        ratio_v2 = new_overlap_percent_v2 / 100.0
                        if abs(params_v2.get(overlap_key_v2, -1.0) - ratio_v2) > 1e-7: params_v2[overlap_key_v2] = ratio_v2; specific_file_needs_writing = True

                        # NEW: Propagasi parameter tambahan V2
                        if abs(params_v2.get(noise_mad_key_v2, -1.0) - new_noise_mad_v2) > 1e-7: params_v2[noise_mad_key_v2] = new_noise_mad_v2; specific_file_needs_writing = True
                        if abs(params_v2.get(mad_sens_key_v2, -1.0) - new_mad_sens_v2) > 1e-7: params_v2[mad_sens_key_v2] = new_mad_sens_v2; specific_file_needs_writing = True
                        if abs(params_v2.get(conf_skip_key_v2, -1.0) - new_conf_skip_v2) > 1e-7: params_v2[conf_skip_key_v2] = new_conf_skip_v2; specific_file_needs_writing = True
                        if abs(params_v2.get(wiener_c_key_v2, -1.0) - new_wiener_c_v2) > 1e-7: params_v2[wiener_c_key_v2] = new_wiener_c_v2; specific_file_needs_writing = True
                        if params_v2.get(coarse_margin_key_v2, -1) != new_coarse_margin_v2: params_v2[coarse_margin_key_v2] = new_coarse_margin_v2; specific_file_needs_writing = True

                    if specific_file_needs_writing:
                        try:
                            os.makedirs(os.path.dirname(ALGORITHM_PARAMETER_SETTINGS_FILE), exist_ok=True)
                            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "w") as f_specific_write:
                                json.dump(all_specific_params, f_specific_write, indent=4)
                        except Exception as e_write: QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but failed to write algorithm settings... Error: {e_write}")

            except Exception as e_update:
                 QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but an error occurred during algorithm settings update... Error: {e_update}")

        language_changed = (new_language.lower() != initial_language.lower())
        if language_changed:
            msg_box = QMessageBox(); restart_title = getattr(language_config, 'RESTART_APPLICATION_REQUIRED', "Restart Required")
            restart_desc = getattr(language_config, 'RESTART_APPLICATION_DESCRIPTION', "Language change requires restart.")
            accept_text = getattr(language_config, 'ACCEPT_RESTART_APPLICATION', "Restart Now"); reject_text = getattr(language_config, 'REJECT_APPLICATION_DESCRIPTION', "Later")
            msg_box.setWindowTitle(restart_title); msg_box.setText(restart_desc); msg_box.setIcon(QMessageBox.Icon.Warning)
            restart_button = msg_box.addButton(accept_text, QMessageBox.ButtonRole.AcceptRole); later_button = msg_box.addButton(reject_text, QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()
            if msg_box.clickedButton() == restart_button: restart_application()
        else:
            if general_save_successful:
                 QMessageBox.information(general_tab, "Setting", getattr(language_config, 'SETTINGS_SAVED', "Settings saved successfully!")) # Pakai getattr
            
    def restart_application():
        """Fungsi untuk merestart aplikasi menggunakan QProcess."""
        try:
            print(language_config.TRY_RESTART_APPLICATION)

            sys_executable_abs = os.path.abspath(sys.executable)
            try:
                initial_launch_path = os.path.abspath(sys.argv[0])
            except Exception:
                initial_launch_path = sys_executable_abs # Fallback
            
            working_dir = os.path.dirname(initial_launch_path)

            is_frozen = getattr(sys, 'frozen', False)
            
            arguments = []
            program_to_run = "" 

            if is_frozen:
                program_to_run = initial_launch_path 
                arguments = sys.argv[1:]
            else:
                program_to_run = sys_executable_abs # Path ke python.exe
                arguments = [initial_launch_path] + sys.argv[1:] # initial_launch_path adalah main.py
            
            if not os.path.exists(program_to_run):
                raise FileNotFoundError(f"Program to run not found: {program_to_run}")
            if not is_frozen and not os.path.exists(arguments[0]): # Cek script path di mode dev
                raise FileNotFoundError(f"Script to run not found: {arguments[0]}")
            if not os.path.isdir(working_dir):
                raise NotADirectoryError(f"Working directory is not a valid directory: {working_dir}")

            started = QProcess.startDetached(program_to_run, arguments, working_dir)

            if started:
                time.sleep(0.2) 
                QCoreApplication.instance().quit() 
                QCoreApplication.instance().quit()
            else:
                print(language_config.COMMAND_FAILED_IN_RESTART_APPLICATION)
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setWindowTitle(language_config.RESTART_FAILED)
                error_msg.setText(f"{language_config.COMMAND_TO_RESTART_MANUALLY}\n\nFailed command:\nProgram: {program_to_run}\nArgs: {arguments}\nWD: {working_dir}")
                error_msg.exec()

        except Exception as e:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setWindowTitle(language_config.RESTART_FAILED)
            error_msg.setText(f"An error occurred while trying to restart:\n{e}\n\nPlease restart the application manually.")
            error_msg.exec()
    apply_button.clicked.connect(save_settings)
    general_tab.setLayout(main_layout)
    
    return general_tab
