import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout,
                             QScrollArea, QToolButton, QComboBox, QFileDialog) # QPushButton tidak diperlukan lagi
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from UI.resources.stylesheet.stylesheet import (DROPDOWN_BOX, TOGGLE_BUTTON,
                                                SCROLL_AREA, SLIDER_STYLE, SLIDER_VALUE_LABEL)
from UI.settings.General.Language import language_config
# Impor path file yang konsisten
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

# --- Fungsi Helper (Sama seperti di Farneback) ---
def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)

def load_light_glue_config(config_filename=None):
    """
    Memuat konfigurasi LightGlue dari file JSON.
    Fungsi ini sekarang menjadi sumber utama untuk memuat konfigurasi.
    """
    # Nilai default yang relevan untuk LightGlue
    default_config = {
        "transformation": "homography",
        "ransacThreshold": 5.0,
        "keep_edges": False,
        "enable_cropping": False,
        "save_align": False,
        "command_save_to_hd5f": True,
        "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"),
        "use_multi_core": True # Diambil dari general settings nanti
    }

    if config_filename is None:
        config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE

    # Jika file tidak ada, langsung gunakan default
    if not os.path.exists(config_filename):
        return default_config

    config_data = default_config.copy()
    try:
        with open(config_filename, "r") as config_file:
            params = json.load(config_file)
        # Ambil dari kunci "Light_Glue"
        loaded_config = params.get("Light_Glue", {})
        config_data.update(loaded_config)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading LightGlue config from '{config_filename}': {e}. Using defaults.")
        # Jika error, pastikan kembali ke default yang bersih
        config_data = default_config.copy()

    return config_data

def _load_general_settings():
    """Membaca semua setting relevan dari app_setting.json."""
    defaults = {"gpu_acceleration": False, "multi_core_cpu": True}
    if not os.path.exists(GENERAL_SETTINGS_FILE):
        return defaults
    try:
        with open(GENERAL_SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        for key, value in defaults.items():
            settings.setdefault(key, value)
        return settings
    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"Warning: Could not read general settings: {e}. Using defaults.")
        return defaults

def save_light_glue_config(config):
    """Menyimpan konfigurasi LightGlue ke ALGORITHM_PARAMETER_SETTINGS_FILE."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE

    all_params = {}
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params = json.load(f)
    except Exception as e:
        print(f"Warning: Could not read existing config file '{config_filename}': {e}")

    # Timpa atau tambahkan bagian "Light_Glue"
    all_params["Light_Glue"] = config

    try:
        with open(config_filename, "w") as f:
            json.dump(all_params, f, indent=4)
    except Exception as e:
        print(f"Error saving LightGlue config to '{config_filename}': {e}")

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

def get_light_glue_page():
    """
    Fungsi utama untuk membuat halaman UI pengaturan LightGlue.
    """
    try:
        # Panggil loader yang sudah disentralisasi
        light_glue_config = load_light_glue_config()
    except Exception as e:
        print(f"Error during initial load: {e}. Using default values for LightGlue UI.")
        light_glue_config = load_light_glue_config() # Fallback

    # --- Mulai Setup UI ---
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setSpacing(10)

    title_label = QLabel("LightGlue Parameter Setting") # Ganti dengan language_config jika perlu
    title_label.setFont(get_default_font(12, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title_label)

    # --- Dictionaries untuk menyimpan referensi UI ---
    sliders = {}
    value_labels = {}
    combos = {}
    toggles = {}
    folder_data = {'selected_path': light_glue_config.get("align_folder", "")}

    # --- Fungsi Auto-Save ---
    def save_current_settings():
        general_settings = _load_general_settings()
        use_gpu_setting = general_settings.get("gpu_acceleration", False)
        use_multicore_setting = general_settings.get("multi_core_cpu", True)

        current_config = load_light_glue_config() # Ambil basis terbaru

        # Update dari Slider (hanya ransacThreshold)
        if "ransacThreshold" in sliders:
            slider_widget = sliders["ransacThreshold"]
            current_value = slider_widget.value()
            current_config["ransacThreshold"] = current_value / 10.0
            # Update label
            if "ransacThreshold_label" in value_labels:
                 value_labels["ransacThreshold_label"].setText(f"{current_value / 10.0:.1f}")

        # Update dari Combo Box
        if 'transformation' in combos:
            current_config["transformation"] = combos['transformation'].currentText()

        # Update dari Toggle Buttons
        if 'keep_edges' in toggles:
            current_config["keep_edges"] = toggles['keep_edges'].isChecked()
        if 'enable_cropping' in toggles:
            current_config["enable_cropping"] = toggles['enable_cropping'].isChecked()
        if 'save_align' in toggles:
            current_config["save_align"] = toggles['save_align'].isChecked()
        if 'command_save_to_hd5f' in toggles:
            current_config["command_save_to_hd5f"] = toggles['command_save_to_hd5f'].isChecked()

        try:
            normalized_path = os.path.normpath(folder_data['selected_path']).replace("\\", "/")
            current_config["align_folder"] = normalized_path
        except TypeError:
            current_config["align_folder"] = ""
            
        current_config["use_gpu"] = use_gpu_setting
        current_config["use_multi_core"] = use_multicore_setting

        save_light_glue_config(current_config)
    
    # --- Pembuatan UI Slider (Hanya RANSAC) ---
    ransac_label_text = "RANSAC Threshold" # Ganti language_config
    ransac_tooltip = "Maximum pixel distance for a point to be considered an inlier."
    initial_float = light_glue_config.get("ransacThreshold", 5.0)
    initial_slider_val = int(initial_float * 10)

    lbl, sld, lay, val_lbl = create_slider(
        ransac_label_text, 10, 100, 5, initial_slider_val, lambda v: f"{v/10.0:.1f}", ransac_tooltip
    )
    layout.addWidget(lbl); layout.addLayout(lay)
    sliders["ransacThreshold"] = sld
    value_labels["ransacThreshold_label"] = val_lbl
    sld.valueChanged.connect(save_current_settings)

    # --- Pembuatan UI Toggle Buttons (Keep Edges, Enable Cropping) ---
    toggles_layout_1 = QHBoxLayout()
    toggles_layout_1.setAlignment(Qt.AlignmentFlag.AlignLeft)

    keep_edges_button = QToolButton()
    keep_edges_button.setCheckable(True)
    # Ambil nilai awal dari config UI
    keep_edges_initial = light_glue_config.get("keep_edges", False) # Default False untuk ORB?
    keep_edges_button.setChecked(keep_edges_initial)
    keep_edges_button.setText(language_config.KEEP_EDGES_LABEL if keep_edges_initial else language_config.IGNORE_EDGE_LABEL)
    keep_edges_button.setFont(get_default_font(10, QFont.Weight.Bold))
    keep_edges_button.setToolTip(language_config.KEEP_EDGES_DESCRIPTION)
    keep_edges_button.setStyleSheet(TOGGLE_BUTTON)
    keep_edges_button.toggled.connect(lambda state: keep_edges_button.setText(language_config.KEEP_EDGES_LABEL if state else language_config.IGNORE_EDGE_LABEL))
    toggles_layout_1.addWidget(keep_edges_button)
    toggles['keep_edges'] = keep_edges_button # Simpan referensi
    # Hubungkan ke auto-save
    keep_edges_button.toggled.connect(save_current_settings)

    enable_cropping_button = QToolButton()
    enable_cropping_button.setCheckable(True)
    enable_cropping_initial = light_glue_config.get("enable_cropping", False)
    enable_cropping_button.setChecked(enable_cropping_initial)
    enable_cropping_button.setText(language_config.ENABLE_CROP_LABEL if enable_cropping_initial else language_config.DISABLE_CROP_LABEL)
    enable_cropping_button.setFont(get_default_font(10, QFont.Weight.Bold))
    enable_cropping_button.setToolTip(language_config.CROP_DESCRIPTION)
    enable_cropping_button.setStyleSheet(TOGGLE_BUTTON)
    toggles_layout_1.addWidget(enable_cropping_button)
    toggles['enable_cropping'] = enable_cropping_button # Simpan referensi
    # Hubungkan ke auto-save (selain logika internal)
    enable_cropping_button.toggled.connect(save_current_settings)

    # Logika internal: jika enable_cropping aktif, maka keep_edges disetel ke False dan dinonaktifkan
    def on_enable_cropping_toggled(state):
        enable_cropping_button.setText(language_config.ENABLE_CROP_LABEL if state else language_config.DISABLE_CROP_LABEL)
        if state:
            # Block signals keep_edges agar tidak memicu save ganda
            keep_edges_button.blockSignals(True)
            keep_edges_button.setChecked(False)
            keep_edges_button.setEnabled(False)
            keep_edges_button.blockSignals(False)
        else:
            keep_edges_button.setEnabled(True)
        # Panggil save SETELAH logika internal selesai
        save_current_settings() # Pastikan perubahan state tersimpan

    # Hubungkan logika internal (setelah save_current_settings juga terhubung)
    enable_cropping_button.toggled.connect(on_enable_cropping_toggled)
    # Panggil sekali saat init untuk set state enable keep_edges
    on_enable_cropping_toggled(enable_cropping_initial)

    layout.addLayout(toggles_layout_1)

    # --- Pembuatan UI Toggle Buttons & Folder (Save Align, Command HD5F) ---
    extra_params_layout_main = QVBoxLayout() # Gunakan VBox untuk menumpuk tombol dan folder

    toggle_buttons_layout_2 = QHBoxLayout()
    toggle_buttons_layout_2.setAlignment(Qt.AlignmentFlag.AlignLeft)

    save_align_button = QToolButton()
    save_align_button.setCheckable(True)
    save_align_initial = light_glue_config.get("save_align", False) # Default False?
    save_align_button.setChecked(save_align_initial)
    save_align_button.setText(language_config.ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER if save_align_initial else language_config.DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER)
    save_align_button.setToolTip(language_config.SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION)
    save_align_button.setFont(get_default_font(10, QFont.Weight.Bold))
    save_align_button.setStyleSheet(TOGGLE_BUTTON)
    toggle_buttons_layout_2.addWidget(save_align_button)
    toggles['save_align'] = save_align_button
    save_align_button.toggled.connect(save_current_settings)

    command_save_to_hd5f_button = QToolButton()
    command_save_to_hd5f_button.setCheckable(True)
    command_save_hd5f_initial = light_glue_config.get("command_save_to_hd5f", True) # Default True?
    command_save_to_hd5f_button.setChecked(command_save_hd5f_initial)
    command_save_to_hd5f_button.setText(language_config.ACTIVATE_SAVE_ALIGN_TO_PROCESS if command_save_hd5f_initial else language_config.DEACTIVATE_SAVE_ALIGN_TO_PROCESS)
    command_save_to_hd5f_button.setToolTip(language_config.SAVE_ALIGN_TO_PROCESS_DESCRIPTION)
    command_save_to_hd5f_button.setFont(get_default_font(10, QFont.Weight.Bold))
    command_save_to_hd5f_button.setStyleSheet(TOGGLE_BUTTON)
    command_save_to_hd5f_button.toggled.connect(lambda state: command_save_to_hd5f_button.setText(language_config.ACTIVATE_SAVE_ALIGN_TO_PROCESS if state else language_config.DEACTIVATE_SAVE_ALIGN_TO_PROCESS))
    toggle_buttons_layout_2.addWidget(command_save_to_hd5f_button)
    toggles['command_save_to_hd5f'] = command_save_to_hd5f_button
    # Hubungkan ke auto-save
    command_save_to_hd5f_button.toggled.connect(save_current_settings)

    extra_params_layout_main.addLayout(toggle_buttons_layout_2)

    # --- Folder Selection ---
    folder_selection_layout = QHBoxLayout()
    folder_selection_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    saved_align_folder = folder_data['selected_path']
    def truncate_path(path, length=35):
        return (path[:length] + "...") if len(path) > length+3 else path

    truncated_folder = truncate_path(saved_align_folder)

    align_folder_dropdown = QComboBox()
    align_folder_dropdown.setStyleSheet(DROPDOWN_BOX)
    align_folder_dropdown.setMinimumWidth(250)

    current_items = []
    if saved_align_folder:
        current_items.append(truncated_folder)
    current_items.append(language_config.SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER)
    align_folder_dropdown.addItems(current_items)

    if saved_align_folder:
        align_folder_dropdown.setCurrentText(truncated_folder)
    else:
        align_folder_dropdown.setCurrentIndex(0)

    align_folder_dropdown.setVisible(save_align_initial)

    # Fungsi untuk menangani perubahan dropdown folder
    def on_align_folder_changed(index):
        selected_text = align_folder_dropdown.itemText(index) # Dapatkan teks dari index yg dipilih

        if selected_text == language_config.SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER:
            start_dir = folder_data['selected_path'] if os.path.isdir(folder_data['selected_path']) else ""
            folder_path = QFileDialog.getExistingDirectory(None, language_config.SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER, start_dir)

            if folder_path:
                folder_data['selected_path'] = os.path.normpath(folder_path) # Simpan path asli

                # Update dropdown UI
                truncated_new_path = truncate_path(folder_data['selected_path'])
                align_folder_dropdown.blockSignals(True)
                if align_folder_dropdown.count() > 1 and align_folder_dropdown.itemText(0) != language_config.SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER:
                     if align_folder_dropdown.itemText(0) != truncated_new_path:
                         align_folder_dropdown.removeItem(0)

                if align_folder_dropdown.findText(truncated_new_path) == -1:
                    align_folder_dropdown.insertItem(0, truncated_new_path)

                align_folder_dropdown.setCurrentIndex(0)
                align_folder_dropdown.blockSignals(False)

                save_current_settings()
                
            else:
                align_folder_dropdown.blockSignals(True)
                if align_folder_dropdown.count() > 1 and align_folder_dropdown.itemText(0) != language_config.SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER:
                    align_folder_dropdown.setCurrentIndex(0)
                else:
                    folder_data['selected_path'] = ""
                    align_folder_dropdown.setCurrentIndex(0)
                    save_current_settings()
                align_folder_dropdown.blockSignals(False)
        else:
             save_current_settings()
    
    align_folder_dropdown.currentIndexChanged.connect(on_align_folder_changed)

    folder_selection_layout.addWidget(align_folder_dropdown)
    extra_params_layout_main.addLayout(folder_selection_layout) # Tambahkan layout folder ke VBox

    # Logika internal: Tampilkan/sembunyikan dropdown & atur enable/disable command_save_to_hd5f
    def on_save_align_toggled(state):
        save_align_button.setText(language_config.ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER if state else language_config.DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER)
        align_folder_dropdown.setVisible(state)

        # Logika disable tombol HD5F jika save_align OFF (agar setidaknya satu aktif)
        if not state:
            
            command_save_to_hd5f_button.blockSignals(True)
            if not command_save_to_hd5f_button.isChecked():
                command_save_to_hd5f_button.setChecked(True)
            command_save_to_hd5f_button.setEnabled(False) 
            command_save_to_hd5f_button.blockSignals(False)
        else: 
            command_save_to_hd5f_button.setEnabled(True)
        save_current_settings() 
    
    save_align_button.toggled.connect(on_save_align_toggled)
    on_save_align_toggled(save_align_initial)


    layout.addLayout(extra_params_layout_main) 
    layout.addStretch(1)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll