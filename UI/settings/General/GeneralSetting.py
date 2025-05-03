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
        # V1
        "similarity_tile_size": 16,
        "similarity_motion_threshold": 0.030,
        "similarity_overlap_percent": 40.0,
        # --- V2 Baru ---
        "similarity_v2_tile_size": 16,
        "similarity_v2_motion_threshold": 0.0025,
        "similarity_v2_overlap_percent": 40.0
        # -------------
    }
    if not os.path.exists(GENERAL_SETTINGS_FILE):
        try: os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
        except OSError: pass
        return defaults
    try:
        with open(GENERAL_SETTINGS_FILE, "r") as f:
            settings = json.load(f)
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
    similarity_group_title = getattr(language_config, 'SIMILARITY_V2_GROUP_TITLE', "Similarity V2 Parameters") # Judul V2
    similarity_group_box = QGroupBox(similarity_group_title)

    similarity_form_layout = QFormLayout()
    similarity_form_layout.setContentsMargins(10, 10, 10, 10)
    similarity_form_layout.setSpacing(10)
    similarity_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    similarity_form_layout.setHorizontalSpacing(15)

    similarity_widgets_v2 = {} 
    
    # a. Tile Size (V2)
    tile_size_label_text = getattr(language_config, 'TILE_SIZE_LABEL', "Tile Size:")
    tile_size_label = QLabel(tile_size_label_text)
    tile_size_label.setToolTip(getattr(language_config, 'TILE_SIZE_DESCRIPTION', ''))
    tile_size_combo = QComboBox()
    tile_options_int = [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256]
    tile_size_combo.addItems([str(size) for size in tile_options_int])
    # Gunakan kunci config V2
    initial_tile_size_int = current_settings.get("similarity_v2_tile_size", 16)
    tile_size_combo.setCurrentText(str(initial_tile_size_int))
    tile_size_combo.setStyleSheet(DROPDOWN_BOX)
    tile_size_combo.setMinimumWidth(100)
    similarity_form_layout.addRow(tile_size_label, tile_size_combo)
    similarity_widgets_v2['tile_combo'] = tile_size_combo

    # b. Motion Threshold (V2) - Slider 3 Desimal, Input 4 Desimal
    motion_thresh_label_text = getattr(language_config, 'MOTION_THRESHOLD_LABEL', "Motion Threshold:")
    motion_thresh_label = QLabel(motion_thresh_label_text)
    motion_thresh_label.setToolTip(getattr(language_config, 'MOTION_THRESHOLD_DESCRIPTION', ''))

    motion_thresh_slider = QSlider(Qt.Orientation.Horizontal)
    slider_min_v2 = 1
    slider_max_v2 = 100
    motion_thresh_multiplier_v2 = 1000.0
    motion_thresh_slider.setMinimum(slider_min_v2)
    motion_thresh_slider.setMaximum(slider_max_v2)
    # ----------------------------------------

    initial_motion_thresh = current_settings.get("similarity_v2_motion_threshold", 0.0025) 
    initial_motion_thresh_rounded3 = round(initial_motion_thresh, 3)
    motion_thresh_slider.setValue(int(round(initial_motion_thresh_rounded3 * motion_thresh_multiplier_v2)))
    motion_thresh_slider.setStyleSheet(TOGGLE_SWITCH_STYLE.replace("QCheckBox", "QSlider"))

    # --- Input field tetap menampilkan 4 desimal ---
    motion_thresh_input = QLineEdit(f"{initial_motion_thresh:.4f}")
    motion_thresh_input.setFixedWidth(70)
    motion_thresh_input.setAlignment(Qt.AlignmentFlag.AlignRight)
    c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)
    motion_thresh_input.setLocale(c_locale)
    motion_thresh_validator = QDoubleValidator(0.0001, 0.1000, 5, motion_thresh_input)
    motion_thresh_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    motion_thresh_input.setValidator(motion_thresh_validator)
    
    motion_thresh_layout = QHBoxLayout()
    motion_thresh_layout.addWidget(motion_thresh_slider)
    motion_thresh_layout.addWidget(motion_thresh_input)
    similarity_form_layout.addRow(motion_thresh_label, motion_thresh_layout)
    similarity_widgets_v2['motion_slider'] = motion_thresh_slider
    similarity_widgets_v2['motion_input'] = motion_thresh_input

    # --- Koneksi dua arah (DIMODIFIKASI) ---
    # 1. Slider -> Input (Slider hanya punya presisi 3 desimal)
    motion_thresh_slider.valueChanged.connect(
        lambda value, inp=motion_thresh_input, m=motion_thresh_multiplier_v2, loc=c_locale:
            # Tampilkan 3 desimal dari slider
            inp.setText(loc.toString(value / m, 'f', 3))
    )

    # 2. Input -> Slider (Input punya presisi 4 desimal)
    def update_motion_slider_v2():
        current_locale = motion_thresh_input.locale()
        try:
            value_float, ok = current_locale.toDouble(motion_thresh_input.text())
            if not ok: raise ValueError("Conversion failed")

            value_float = max(0.0001, min(value_float, 0.1000))

            # --- PERUBAHAN: Bulatkan float ke 3 desimal HANYA untuk slider ---
            value_float_for_slider = round(value_float, 3)
            # Hitung nilai slider int dari nilai yang dibulatkan
            slider_value = int(round(value_float_for_slider * motion_thresh_multiplier_v2))
            # Clamp nilai slider ke range slider
            slider_value = max(slider_min_v2, min(slider_value, slider_max_v2))
            # -----------------------------------------------------------------

            motion_thresh_slider.blockSignals(True)
            motion_thresh_slider.setValue(slider_value)
            motion_thresh_slider.blockSignals(False)

            # --- PERUBAHAN: Format ulang teks di input ke 4 desimal (nilai asli) ---
            motion_thresh_input.setText(current_locale.toString(value_float, 'f', 4))

        except ValueError:
            # Reset input ke nilai slider saat ini (format 3 desimal dari slider)
            current_slider_val = motion_thresh_slider.value()
            motion_thresh_input.setText(current_locale.toString(current_slider_val / motion_thresh_multiplier_v2, 'f', 3))

    motion_thresh_input.editingFinished.connect(update_motion_slider_v2)

    # c. Overlap (V2)
    overlap_label_text = getattr(language_config, 'OVERLAP_LABEL', "Overlap %:")
    overlap_label = QLabel(overlap_label_text)
    overlap_label.setToolTip(getattr(language_config, 'OVERLAP_DESCRIPTION', ''))
    overlap_slider = QSlider(Qt.Orientation.Horizontal)
    overlap_slider.setMinimum(0); overlap_slider.setMaximum(90)
    # Gunakan kunci config V2
    initial_overlap_percent = current_settings.get("similarity_v2_overlap_percent", 40.0) # KUNCI V2
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

    similarity_group_box.setLayout(similarity_form_layout)
    return similarity_group_box, similarity_widgets_v2 # Kembalikan dict V2
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
        QGroupBox { /* Stylesheet untuk GroupBox */
            font-weight: bold; border: 1px solid gray; border-radius: 5px;
            margin-top: 10px; padding-top: 15px; padding-left: 5px;
            padding-right: 5px; padding-bottom: 5px;
            max-width: 300px; 
            min-width: 100px;
        }
        QGroupBox::title {
            subcontrol-origin: margin; subcontrol-position: top left;
            padding: 0 3px; left: 10px;
        }
        """
    )

    # 1. Load Settings Awal
    current_settings = load_general_settings()
    initial_language = current_settings.get("language", "English")

    # 2. Buat Layout Utama dan Form Layout Atas
    main_layout = QVBoxLayout(general_tab)
    top_form_layout = QFormLayout()
    top_form_layout.setContentsMargins(15, 15, 15, 15)
    top_form_layout.setSpacing(12)
    top_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    top_form_layout.setHorizontalSpacing(20)
 
    # Bahasa
    language_dropdown = _create_language_settings(top_form_layout, current_settings)
    
    # Akselerasi
    accel_widgets = _create_acceleration_settings(top_form_layout, current_settings)
    gpu_checkbox = accel_widgets['gpu'] 
    cpu_checkbox = accel_widgets['cpu'] 

    # Tambahkan form layout atas ke layout utama
    main_layout.addLayout(top_form_layout) 

    similarity_groups_layout = QHBoxLayout() 
    
    similarity_group_box_v1, similarity_widgets_v1 = _create_similarity_v1_group(current_settings)
    tile_size_combo_v1 = similarity_widgets_v1['tile_combo']
    motion_thresh_slider_v1 = similarity_widgets_v1['motion_slider']
    overlap_slider_v1 = similarity_widgets_v1['overlap_slider']
    similarity_groups_layout.addWidget(similarity_group_box_v1) 
    
    # Similarity Grup V2
    similarity_group_box_v2, similarity_widgets_v2 = _create_similarity_v2_group(current_settings)
    tile_size_combo_v2 = similarity_widgets_v2['tile_combo']
    similarity_groups_layout.addWidget(similarity_group_box_v2)

    similarity_groups_layout.addStretch()
    main_layout.addLayout(similarity_groups_layout)

    main_layout.addStretch()

    apply_button_layout, apply_button = _create_apply_button()
    main_layout.addLayout(apply_button_layout)

    def save_settings():
        new_language = language_dropdown.currentText()
        new_gpu_setting = gpu_checkbox.isChecked()
        new_multicore_setting = cpu_checkbox.isChecked()
        try:
            new_tile_size_int_v1 = int(tile_size_combo_v1.currentText())
        except ValueError: 
            return

        motion_thresh_multiplier = 1000.0
        new_motion_threshold_v1 = motion_thresh_slider_v1.value() / motion_thresh_multiplier
        new_overlap_percent_v1 = float(overlap_slider_v1.value())

        try:
            new_tile_size_int_v2 = int(tile_size_combo_v2.currentText())
        except ValueError: return

        motion_thresh_input_v2 = similarity_widgets_v2['motion_input']
        overlap_input_v2 = similarity_widgets_v2['overlap_input'] 

        locale_v2 = motion_thresh_input_v2.locale() 
        v2_motion_text = motion_thresh_input_v2.text()
        new_motion_threshold_v2, ok = locale_v2.toDouble(v2_motion_text)
        if not ok:
            QMessageBox.warning(general_tab, "Invalid Input", f"Invalid Motion Threshold value for V2: '{v2_motion_text}'. Settings not saved.")
            return 
        new_motion_threshold_v2 = max(0.0001, min(new_motion_threshold_v2, 0.1000))

        try:
            v2_overlap_text = overlap_input_v2.text()
            new_overlap_percent_v2 = float(v2_overlap_text) # Baca dari input V2
            new_overlap_percent_v2 = max(0.0, min(new_overlap_percent_v2, 90.0)) # Clamp
        except ValueError:
            QMessageBox.warning(general_tab, "Invalid Input", f"Invalid Overlap value for V2: '{v2_overlap_text}'. Settings not saved.")
            return
      

        settings_to_save_general = {
            "language": new_language,
            "gpu_acceleration": new_gpu_setting,
            "multi_core_cpu": new_multicore_setting,
            # V1
            "similarity_tile_size": new_tile_size_int_v1,
            "similarity_motion_threshold": new_motion_threshold_v1,
            "similarity_overlap_percent": new_overlap_percent_v1,
            # V2 (simpan nilai presisi dari input)
            "similarity_v2_tile_size": new_tile_size_int_v2,
            "similarity_v2_motion_threshold": new_motion_threshold_v2, # <-- Nilai presisi dari input
            "similarity_v2_overlap_percent": new_overlap_percent_v2  # <-- Nilai presisi dari input
        }

        # --- Simpan ke GENERAL_SETTINGS_FILE ---
        # ... (kode save general seperti sebelumnya) ...
        general_save_successful = False
        try:
            os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
            with open(GENERAL_SETTINGS_FILE, "w") as f:
                json.dump(settings_to_save_general, f, indent=4)
            general_save_successful = True
        except Exception as e:
             QMessageBox.critical(general_tab, "Error Saving Settings", f"Could not save general settings... Error: {e}")
             return
         
        # --- Propagasi ke ALGORITHM_PARAMETER_SETTINGS_FILE ---
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
                    algo_keys_cpu = ["Farneback", "ORB", "AKAZE"] # Algoritma yg pakai multi_core
                    algo_keys_gpu = ["Farneback"] # Algoritma yg pakai GPU

                    for key in algo_keys_cpu:
                         if key not in all_specific_params: all_specific_params[key] = {}; specific_file_needs_writing = True
                         if isinstance(all_specific_params.get(key), dict):
                             if all_specific_params[key].get("use_multi_core") != new_multicore_setting:
                                 all_specific_params[key]["use_multi_core"] = new_multicore_setting; specific_file_needs_writing = True

                    for key in algo_keys_gpu:
                         # Asumsikan Farneback sudah dicek/dibuat di loop CPU
                         if isinstance(all_specific_params.get(key), dict):
                              if all_specific_params[key].get("use_gpu") != new_gpu_setting:
                                  all_specific_params[key]["use_gpu"] = new_gpu_setting; specific_file_needs_writing = True

                    # --- Update Similarity V1 ---
                    similarity_section_key_v1 = "Similarity" # Nama section V1
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

                    # --- Update Similarity V2 ---
                    similarity_section_key_v2 = "Similarity_V2" # Nama section V2 (atau sesuaikan)
                    tile_size_key_v2 = "tileGridSize"
                    motion_thresh_key_v2 = "motionThreshold"
                    overlap_key_v2 = "overlapRatio"

                    if similarity_section_key_v2 not in all_specific_params: all_specific_params[similarity_section_key_v2] = {}; specific_file_needs_writing = True
                    if isinstance(all_specific_params.get(similarity_section_key_v2), dict):
                        params_v2 = all_specific_params[similarity_section_key_v2]
                        list_v2 = [new_tile_size_int_v2, new_tile_size_int_v2]
                        if params_v2.get(tile_size_key_v2) != list_v2: params_v2[tile_size_key_v2] = list_v2; specific_file_needs_writing = True
                        if abs(params_v2.get(motion_thresh_key_v2, -1.0) - new_motion_threshold_v2) > 1e-6: params_v2[motion_thresh_key_v2] = new_motion_threshold_v2; specific_file_needs_writing = True
                        ratio_v2 = new_overlap_percent_v2 / 100.0
                        if abs(params_v2.get(overlap_key_v2, -1.0) - ratio_v2) > 1e-6: params_v2[overlap_key_v2] = ratio_v2; specific_file_needs_writing = True

                    # Tulis file spesifik jika perlu
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
                 QMessageBox.information(general_tab, "Setting", language_config.SETTINGS_SAVED)
            
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
