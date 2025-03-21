import os
from PyQt6.QtWidgets import (QLabel, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox, QLineEdit)
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

def create_button_widget(database_manager, batch_id, thumbnail_threads, list_layout, 
                         handle_add_image_to_batch, handle_delete_batch):
    """Buat widget tombol yang berisi tombol add, preview, dan delete."""
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
    # Hubungkan callback setelah list_layout tersedia
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
    return button_widget

def create_parameter_panel():
    """Buat panel parameter yang berisi combo box dan checkbox dengan scroll area."""
    parameter_panel = QWidget()
    parameter_panel.setStyleSheet("background-color: #EBEAEA")
    parameter_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    parameter_layout = QHBoxLayout(parameter_panel)
    parameter_layout.setContentsMargins(10, 10, 10, 10)

    # Bagian Kiri - Layout untuk Algoritma dan Folder Icon
    algorithm_layout = QVBoxLayout()
    algorithm_layout.setContentsMargins(5, 5, 5, 5)
    algorithm_layout.setSpacing(5)

    # Dropdown algoritma penyelarasan
    algorithm_combox = QComboBox()
    algorithm_combox.addItems(["Algoritma Penyelarasan 1", "Algoritma Penyelarasan 2", "Algoritma Penyelarasan 3"])
    algorithm_combox.setVisible(False)  # Awalnya disembunyikan

    # Dropdown algoritma denoising/super resolusi
    denoising_combox = QComboBox()
    denoising_combox.addItems(["Denoising Algoritma 1", "Denoising Algoritma 2", "Denoising Algoritma 3"])
    denoising_combox.setVisible(False)  # Awalnya disembunyikan

    # Tombol folder output
    folder_button = QPushButton()
    folder_button.setIcon(QIcon("UI/resources/icon/folder-output.png"))  # Ganti dengan path icon yang sesuai
    folder_button.setVisible(False)  # Awalnya disembunyikan

    # Tambahkan ke layout vertikal
    algorithm_layout.addWidget(algorithm_combox)
    algorithm_layout.addWidget(denoising_combox)
    algorithm_layout.addWidget(folder_button)

    # Bagian Kanan - Checkbox dalam Scroll Area
    option_widget = QWidget()
    option_layout = QVBoxLayout(option_widget)
    option_layout.setContentsMargins(5, 5, 5, 5)
    option_layout.setSpacing(5)

    checkboxes = {}
    checkbox_texts = [
        language_config.PARAMETER_BATCH_ALIGNMENT,
        language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS,
        language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER,
        language_config.PARAMETER_BATCH_DENOISING,
        language_config.PARAMETER_BATCH_SUPER_RESOLUTION,
        language_config.PARAMETER_BATCH_CROP_EDGE,
        language_config.PARAMETER_BATCH_KEEP_EDGE
    ]

    for text in checkbox_texts:
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setSpacing(5)

        option_checkbox = QCheckBox()
        option_label = QLabel(text)
        option_label.setWordWrap(True)
        option_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        checkbox_layout.addWidget(option_checkbox)
        checkbox_layout.addWidget(option_label, 1)
        option_layout.addWidget(checkbox_widget)

        checkboxes[text] = option_checkbox  # Simpan checkbox dalam dictionary

    option_layout.addStretch()

    scroll_option_layout = QScrollArea()
    scroll_option_layout.setWidgetResizable(True)
    scroll_option_layout.setWidget(option_widget)
    scroll_option_layout.setStyleSheet("border: none;")

    parameter_layout.addLayout(algorithm_layout, 1)
    parameter_layout.addWidget(scroll_option_layout, 1)

    # EVENT HANDLER
    def update_visibility():
        """Perbarui tampilan dropdown dan ikon folder sesuai dengan checkbox yang aktif."""
        is_alignment_checked = checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT].isChecked()
        is_folder_checked = checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].isChecked()
        is_denoising_checked = checkboxes[language_config.PARAMETER_BATCH_DENOISING].isChecked()
        is_superres_checked = checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].isChecked()

        # Tampilkan dropdown penyelarasan jika "Selaraskan Gambar" dicentang
        algorithm_combox.setVisible(is_alignment_checked)

        # Tampilkan dropdown denoising jika "Denoising" atau "Super Resolusi" dicentang
        denoising_combox.setVisible(is_denoising_checked or is_superres_checked)

        # Tampilkan ikon folder jika "Simpan Hasil Penyelarasan ke dalam Folder" dicentang
        folder_button.setVisible(is_folder_checked)

    def toggle_exclusive_checkboxes(state, other_checkbox):
        """
        Jika checkbox diaktifkan, matikan checkbox lainnya.
        Jika checkbox dimatikan, aktifkan kembali pilihan pada checkbox lainnya.
        """
        if state == 2:  # 2 = Qt.Checked
            other_checkbox.setChecked(False)
            other_checkbox.setEnabled(False)
        else:
            other_checkbox.setEnabled(True)

    # Hubungkan semua checkbox ke fungsi update_visibility
    for checkbox in checkboxes.values():
        checkbox.stateChanged.connect(update_visibility)

    # Buat checkbox eksklusif untuk Denoising & Super Resolusi
    checkboxes[language_config.PARAMETER_BATCH_DENOISING].stateChanged.connect(
        lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION])
    )
    checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].stateChanged.connect(
        lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_DENOISING])
    )

    # Buat checkbox eksklusif untuk Potong Tepi & Pertahankan Tepi
    checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].stateChanged.connect(
        lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE])
    )
    checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].stateChanged.connect(
        lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE])
    )

    return parameter_panel

def create_left_widget(database_manager, batch_id, thumbnail_threads, list_layout, 
                       handle_add_image_to_batch, handle_delete_batch):
    """Buat widget bagian kiri yang menggabungkan tombol dan panel parameter."""
    button_widget = create_button_widget(database_manager, batch_id, thumbnail_threads, 
                                         list_layout, handle_add_image_to_batch, handle_delete_batch)
    parameter_panel = create_parameter_panel()

    left_layout = QHBoxLayout()
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.addWidget(button_widget)
    left_layout.addWidget(parameter_panel, 1)

    left_widget = QWidget()
    left_widget.setLayout(left_layout)
    return left_widget


def setup_combined_panel(database_manager, batch_id, thumbnail_threads, thumbnail_placeholders,
                         handle_add_image_to_batch, handle_delete_batch, SCROLL_AREA):
    """Membuat panel gabungan yang berisi tombol tambah, tombol delete, parameter_panel, dan list_panel."""
    create_thumbnail = CACHE.get("create_thumbnail", False)

    combined_panel = QWidget()
    combined_panel.setMaximumHeight(120)
    combined_panel_layout = QHBoxLayout(combined_panel)
    combined_panel_layout.setContentsMargins(0, 0, 0, 0)

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
                label.setWordWrap(True)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                file_name = os.path.basename(path).replace("_", "\n")
                label.setText(file_name)
                label.setStyleSheet("""
                    background-color: lightgray; 
                    border: 1px solid gray; 
                    font-size: 11px;
                    color: gray;
                    padding: 3px;
                """)
                list_layout.addWidget(label)

    scroll_list_panel = QScrollArea()
    scroll_list_panel.setWidgetResizable(True)
    scroll_list_panel.setWidget(list_panel)
    scroll_list_panel.setStyleSheet(SCROLL_AREA)

    # Buat left widget dari fungsi modular
    left_widget = create_left_widget(database_manager, batch_id, thumbnail_threads, list_layout, 
                                     handle_add_image_to_batch, handle_delete_batch)

    left_widget.setMinimumWidth(420)
    combined_panel_layout.addWidget(left_widget, 1)
    combined_panel_layout.addWidget(scroll_list_panel, 2)

    combined_panel.batch_id = batch_id
    return combined_panel
