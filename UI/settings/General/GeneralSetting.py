import json
import os
import sys
import time
from PyQt6.QtWidgets import (
    QWidget, QLabel, QComboBox, QFormLayout,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import QProcess

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
        
        # print(f"Settings saved to {SETTINGS_FILE}: {settings}")

        # Tampilkan QMessageBox untuk meminta restart
        msg_box = QMessageBox()
        msg_box.setWindowTitle(language_config.RESTART_APPLICATION_REQUIRED)
        msg_box.setText(language_config.RESTART_APPLICATION_DESCRIPTION)
        msg_box.setIcon(QMessageBox.Icon.Warning)

        # Tambahkan tombol "Restart" dan "Nanti saja"
        restart_button = msg_box.addButton(language_config.ACCEPT_RESTART_APPLICATION, QMessageBox.ButtonRole.AcceptRole)
        later_button = msg_box.addButton(language_config.REJECT_APPLICATION_DESCRIPTION, QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        # Jika user memilih "Restart"
        if msg_box.clickedButton() == restart_button:
            # print("User memilih restart.")
            restart_application()

    def restart_application():
        """Fungsi untuk merestart aplikasi menggunakan QProcess.
        
        Fungsi ini dirancang untuk bekerja baik saat menjalankan skrip .py
        maupun saat menjalankan aplikasi .exe yang sudah di-build.
        """
        try:
            print(language_config.TRY_RESTART_APPLICATION) # Pesan: Mencoba memulai ulang...

            executable = sys.executable
            arguments = [] # Akan diisi berdasarkan mode

            # Deteksi apakah berjalan sebagai skrip atau paket beku (.exe)
            # hasattr(sys, 'frozen') umumnya True jika dibuild oleh PyInstaller/cx_Freeze
            # getattr digunakan untuk default ke False jika atribut tidak ada
            is_frozen = getattr(sys, 'frozen', False)

            if is_frozen:
                # Mode .exe: Jalankan .exe itu sendiri dengan argumen asli
                executable = sys.executable 
                arguments = sys.argv[1:]
            else:
                # Mode .py: Jalankan python.exe dengan skrip dan argumen asli
                executable = sys.executable 
                arguments = sys.argv

            # Pastikan path executable absolut
            executable_abs = os.path.abspath(executable)

            # Mulai proses baru yang terpisah
            started = QProcess.startDetached(executable_abs, arguments)

            if started:
                time.sleep(0.1) 
                sys.exit(0) # Keluar dari aplikasi saat ini
            else:
                print(language_config.COMMAND_FAILED_IN_RESTART_APPLICATION) # Pesan: Gagal menjalankan perintah restart.
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setWindowTitle(language_config.RESTART_FAILED) # Judul: Restart Gagal
                error_msg.setText(language_config.COMMAND_TO_RESTART_MANUALLY) # Pesan: Tidak dapat memulai ulang otomatis...
                error_msg.exec()

        except Exception as e:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setWindowTitle(language_config.RESTART_FAILED) # Judul: Restart Gagal
            # Sesuaikan pesan error ini jika perlu
            error_msg.setText(f"An error occurred while trying to restart:\n{e}\n\Please restart the application manually.") 
            error_msg.exec()
    
    # Hubungkan tombol Apply dengan fungsi penyimpanan
    apply_button.clicked.connect(save_settings)
    
    # Set the main layout to the tab
    general_tab.setLayout(main_layout)
    
    return general_tab
