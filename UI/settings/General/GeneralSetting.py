import json
import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QComboBox, QFormLayout,
    QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt

from UI.settings.General.Language import language_config

# Path untuk menyimpan setting
SETTINGS_DIR = "database/setting"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "app_setting.json")

def general_page():
    """Creates a general settings tab with QFormLayout and a styled apply button."""
    general_tab = QWidget()

    # Tab background style
    general_tab.setStyleSheet(
        """
        background-color: #ffffff;
        border: none;
        """
    )

    # Layout utama
    main_layout = QVBoxLayout()
    form_layout = QFormLayout()
    form_layout.setContentsMargins(10, 10, 10, 10)
    form_layout.setSpacing(10)

    # Define the language dropdown and label
    language_label = QLabel(language_config.LANGUAGE_LABEL)

    language_dropdown = QComboBox()
    
    # Daftar bahasa yang tersedia
    languages = ["English", "Indonesian", "China Traditional", "Melayu"]
    
    # Dapatkan bahasa yang tersimpan di file setting (sudah dalam lowercase)
    current_lang = language_config.LANGUAGE
    
    # Cari bahasa yang sesuai dan pindahkan ke posisi pertama
    selected_lang = next((lang for lang in languages if lang.lower() == current_lang), None)
    if selected_lang:
        languages.remove(selected_lang)
        languages.insert(0, selected_lang)
    
    language_dropdown.addItems(languages)
    
    language_dropdown.setStyleSheet(
        """
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
    )

    # Tambahkan label dan dropdown ke form layout
    form_layout.addRow(language_label, language_dropdown)
    
    # Tambahkan form_layout ke main_layout
    main_layout.addLayout(form_layout)
    
    # Layout horizontal untuk tombol Apply agar berada di pojok kanan bawah
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    apply_button = QPushButton(language_config.APPLY_PARAMETER_BUTTON_TEXT)
    button_layout.addWidget(apply_button)
    main_layout.addLayout(button_layout)
    
    # Mempercantik tombol Apply
    apply_button.setStyleSheet(
        """
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
        """
    )
    
    # Fungsi untuk menyimpan setting ke file JSON
    def save_settings():
        settings = {"language": language_dropdown.currentText()}
    
        # Pastikan direktori ada sebelum menyimpan
        os.makedirs(SETTINGS_DIR, exist_ok=True)
    
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    
        print(f"Settings saved to {SETTINGS_FILE}: {settings}")
    
    # Hubungkan tombol Apply dengan fungsi penyimpanan
    apply_button.clicked.connect(save_settings)
    
    # Set the main layout to the tab
    general_tab.setLayout(main_layout)
    
    return general_tab
