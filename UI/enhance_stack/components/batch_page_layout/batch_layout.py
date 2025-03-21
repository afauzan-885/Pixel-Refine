import os
from PyQt6.QtWidgets import (QLabel, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
import weakref

from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, create_thumbnail_placeholder, update_thumbnail
from config import CACHE
from UI.settings.General.Language import language_config

def setup_main_panel(parent, scroll_area_style):
    """Membuat panel utama dengan layout vertikal agar UI tersusun dari atas."""
    main_panel = QWidget(parent)
    main_panel.setStyleSheet("background-color: white;")
    
    main_panel_layout = QVBoxLayout(main_panel)
    main_panel_layout.setContentsMargins(10, 10, 10, 10)
    main_panel_layout.setSpacing(30)  
    
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(main_panel)
    scroll_area.setStyleSheet(scroll_area_style)

    return scroll_area, main_panel_layout


def refresh_ui(database_manager, main_panel_layout, setup_combined_panel):
    """Memperbarui UI dengan daftar batch yang tersedia."""
    # Bersihkan layout yang ada
    while main_panel_layout.count():
        item = main_panel_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    batch_ids = database_manager.get_all_batch_ids()

    if not batch_ids:
        placeholder = QLabel("Tidak ada batch yang tersedia.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_panel_layout.addWidget(placeholder)
    else:
        for batch_id in batch_ids:
            combined_panel = setup_combined_panel(batch_id=batch_id)
            main_panel_layout.addWidget(combined_panel)

    spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    main_panel_layout.addSpacerItem(spacer)

def setup_combined_panel(database_manager, batch_id, thumbnail_threads, thumbnail_placeholders,
                         handle_add_image_to_batch, handle_delete_batch, SCROLL_AREA):
    """Membuat panel gabungan yang berisi tombol tambah, tombol delete, parameter_panel, dan list_panel."""

    create_thumbnail = CACHE.get("create_thumbnail", False)  # Ambil nilai dari CACHE

    combined_panel = QWidget()
    combined_panel.setMaximumHeight(120)  # Berikan tinggi maksimum agar UI tetap rapi
    combined_panel_layout = QHBoxLayout(combined_panel)
    combined_panel_layout.setContentsMargins(0, 0, 0, 0)

    button_layout = QVBoxLayout()
    button_layout.setContentsMargins(0, 0, 0, 0)

    # Add button
    add_button = QPushButton()
    add_button.setFixedSize(30, 30)
    add_button.setIcon(QIcon("UI/resources/icon/add-image.png"))
    add_button.setIconSize(QSize(25, 25))
    add_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50; 
            border-radius: 5px; 
            color: white; 
            font-weight: semi-bold;
        }
        QPushButton:hover {
            background-color: #347A36;
        }
    """)
    add_button.setToolTip(language_config.ADD_IMAGE_BUTTON)
    add_button.clicked.connect(lambda: handle_add_image_to_batch(database_manager, thumbnail_threads, batch_id, list_layout))

    # Preview button
    play_preview = QPushButton()
    play_preview.setFixedSize(30, 30)
    play_preview.setIcon(QIcon("UI/resources/icon/play-preview.png"))
    play_preview.setStyleSheet("""
        QPushButton {
            background-color: #31CBD1;
            border-radius: 5px;
            color: white;
            font-weight: semi-bold;
        }
        QPushButton:hover {
            background-color: #27A1A7;
        }
    """)
    play_preview.setToolTip(language_config.PREVIEW_IMAGE_BUTTON)

    # Delete button
    delete_button = QPushButton()
    delete_button.setFixedSize(30, 30)
    delete_button.setIcon(QIcon("UI/resources/icon/delete-image.png"))
    delete_button.setStyleSheet("""
        QPushButton {
            background-color: #F44336; 
            border-radius: 5px; 
            color: white; 
            font-weight: semi-bold;
        }
        QPushButton:hover {
            background-color: #B9332A;
        }
    """)
    delete_button.setToolTip(language_config.DELETE_IMAGE_BUTTON)
    delete_button.clicked.connect(lambda: handle_delete_batch(batch_id))

    button_layout.addWidget(add_button)
    button_layout.addWidget(play_preview)
    button_layout.addWidget(delete_button)

    button_widget = QWidget()
    button_widget.setLayout(button_layout)

    # Layout horizontal untuk tombol + parameter panel
    left_layout = QHBoxLayout()
    left_layout.setContentsMargins(0, 0, 0, 0)

    # Parameter Panel dengan dua bagian
    parameter_panel = QWidget()
    parameter_panel.setStyleSheet("background-color: #EBEAEA")
    parameter_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    parameter_layout = QHBoxLayout(parameter_panel)
    parameter_layout.setContentsMargins(10, 10, 10, 10)

    # Bagian Kiri - Combo Box
    algorithm_layout = QVBoxLayout()
    algorithm_layout.setContentsMargins(5, 5, 5, 5)
    algorithm_layout.setSpacing(5)

    combo_label = QLabel("Pilih Opsi:")
    combo_label.setStyleSheet("font-weight: bold;")

    combo_box = QComboBox()
    combo_box.addItems(["Opsi 1", "Opsi 2", "Opsi 3"])

    algorithm_layout.addWidget(combo_label)
    algorithm_layout.addWidget(combo_box)

    
    option_widged = QWidget()  # Widget untuk menampung layout checkbox
    option_layout = QVBoxLayout(option_widged)
    option_layout.setContentsMargins(5, 5, 5, 5)
    option_layout.setSpacing(5)

    checkbox_1 = QCheckBox("Aktifkan Fitur A")
    checkbox_2 = QCheckBox("Gunakan Mode B")
    checkbox_3 = QCheckBox("Tampilkan Detail")
    checkbox_4 = QCheckBox("Mode Hemat Daya")
    checkbox_5 = QCheckBox("Tampilkan Notifikasi")
    checkbox_6 = QCheckBox("Gunakan Tema Gelap")

    option_layout.addWidget(checkbox_1)
    option_layout.addWidget(checkbox_2)
    option_layout.addWidget(checkbox_3)
    option_layout.addWidget(checkbox_4)
    option_layout.addWidget(checkbox_5)
    option_layout.addWidget(checkbox_6)
    option_layout.addStretch()

    # Tambahkan Scroll Area
    scroll_option_layout = QScrollArea()
    scroll_option_layout.setWidgetResizable(True)
    scroll_option_layout.setWidget(option_widged)
    scroll_option_layout.setStyleSheet("border: none;")  # Opsional, menghilangkan border

    # Tambahkan ke parameter_layout
    parameter_layout.addLayout(algorithm_layout, 1)  # Bagian kiri (Combo Box)
    parameter_layout.addWidget(scroll_option_layout, 1)  # Bagian kanan (Checkbox dengan Scroll)



    left_layout.addWidget(button_widget)
    left_layout.addWidget(parameter_panel, 1)

    # Panel kanan (Thumbnail List Panel)
    list_panel = QWidget()
    list_panel.setStyleSheet("background-color: #DBDBDB")
    list_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    list_layout = QHBoxLayout(list_panel)
    list_layout.setContentsMargins(5, 5, 5, 5)
    list_layout.setSpacing(10)

    if batch_id is not None:
        image_paths = database_manager.get_images_by_batch(batch_id)
        for path in image_paths:
            if create_thumbnail:
                # Jika opsi create_thumbnail True, buat thumbnail seperti biasa
                placeholder = create_thumbnail_placeholder(list_layout, path, thumbnail_placeholders)
                loader = ThumbnailLoader(path)
                loader.thumbnail_ready.connect(lambda pixmap, p, ref_layout=weakref.ref(list_layout):
                                                 update_thumbnail(ref_layout, pixmap, p) if ref_layout() else None)
                loader.start()
                thumbnail_threads.append(loader)
            else:
                label = QLabel(os.path.basename(path))
                label.setFixedSize(80, 80)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setWordWrap(True)  # Mengaktifkan pemisahan kata jika teks terlalu panjang
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)  # Membuat teks bisa diseleksi
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Memungkinkan ekspansi jika perlu

                # Paksa pemisahan kata pada karakter `_`
                file_name = os.path.basename(path).replace("_", "\n")  # Ganti "_" dengan baris baru
                label.setText(file_name)

                label.setStyleSheet("""
                    background-color: lightgray; 
                    border: 1px solid gray; 
                    font-size: 11px; /* Ukuran font lebih kecil agar muat */
                    color: gray;
                    padding: 3px;
                """)
                list_layout.addWidget(label)



    # Scroll Area untuk list_panel
    scroll_list_panel = QScrollArea()
    scroll_list_panel.setWidgetResizable(True)
    scroll_list_panel.setWidget(list_panel)
    scroll_list_panel.setStyleSheet(SCROLL_AREA)

    left_widget = QWidget()
    left_widget.setLayout(left_layout)

    combined_panel_layout.addWidget(left_widget, 1)
    combined_panel_layout.addWidget(scroll_list_panel, 2)

    combined_panel.batch_id = batch_id

    return combined_panel
