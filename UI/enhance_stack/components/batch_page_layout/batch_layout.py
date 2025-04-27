from PyQt6.QtWidgets import (QLabel, QSpacerItem, QSizePolicy, QWidget,  QScrollArea)
from PyQt6.QtCore import Qt

from UI.settings.General.Language import language_config
from config import SUPPORTED_FORMATS


def setup_main_panel(layout_instance, scroll_area_style):
    """Membuat panel utama dengan layout yang diberikan."""
    main_panel = QWidget()
    main_panel.setStyleSheet("background-color: white;")

    # Menggunakan layout yang diberikan daripada membuat baru
    layout_instance.setContentsMargins(10, 10, 10, 10)
    layout_instance.setSpacing(30)

    main_panel.setLayout(layout_instance)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(main_panel)
    scroll_area.setStyleSheet(scroll_area_style)

    return scroll_area


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
        try:
            format_keys = SUPPORTED_FORMATS.keys()
            supported_formats_text = ", ".join(sorted(list(format_keys)))
        except NameError:
            supported_formats_text = "jpg, png, tiff" 
        except Exception as e:
            print(f"Error processing SUPPORTED_FORMATS keys: {e}") # Pesan error lebih spesifik
            supported_formats_text = "(Gagal memuat format)"


        # Buat string HTML (tidak perlu diubah, hanya nilai variabel yang berbeda)
        html_text = f"""
        <p align="center">
            {language_config.PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES}<br><br>
            <span style="color:#666;">{language_config.SUPPORTED_IMAGE_EXTENSION}:</span><br>
            {supported_formats_text}
        </p>
        """

        # 4. Buat QLabel dan konfigurasikan
        placeholder_label = QLabel()
        placeholder_label.setTextFormat(Qt.TextFormat.RichText) # Penting untuk HTML
        placeholder_label.setText(html_text)
        placeholder_label.setWordWrap(True) # Agar teks format panjang tidak terpotong
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #777777; /* Sedikit lebih gelap mungkin */
                font-size: 21px; /* Sesuaikan ukuran font utama */
                border: none;
                background-color: transparent;
                padding: 20px;
                qproperty-alignment: 'AlignCenter'; /* Coba tambahkan ini juga */
            }
        """)
        # Atur agar label tidak mengambil ruang lebih dari yang dibutuhkan
        placeholder_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)


        # === PUSATKAN SECARA VERTIKAL ===
        main_panel_layout.addStretch(1)
        main_panel_layout.addWidget(placeholder_label, 0, Qt.AlignmentFlag.AlignCenter) # Coba tambahkan alignment di sini juga
        main_panel_layout.addStretch(1)

    else:
        for batch_id in batch_ids:
            combined_panel = setup_combined_panel(batch_id=batch_id)
            main_panel_layout.addWidget(combined_panel)

        # === Tambahkan spacer HANYA jika ada batch ===
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_panel_layout.addSpacerItem(spacer)
