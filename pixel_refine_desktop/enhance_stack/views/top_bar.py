from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QButtonGroup,
    QGridLayout,
    QSizePolicy,
    QStackedWidget,
)
from PySide6.QtCore import Qt  # Import Qt untuk AlignmentFlag

from resources.styles import stylesheet
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


class TopBar(QWidget):
    """Top bar dengan QGridLayout untuk menjaga tombol switch tetap di tengah."""

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 5, 5, 0)  # Beri margin
        self.layout.setSpacing(10)

        # === Tombol-Tombol (Definisi tidak berubah) ===
        self.single_page_import_button = QPushButton(
            language_config.TOPBAR_SINGLE_IMPORT_BUTTON_TEXT
        )
        self.single_page_import_button.setStyleSheet(stylesheet.IMPORT_BUTTON)
        self.single_page_delete_button = QPushButton(
            language_config.TOPBAR_SINGLE_DELETE_BUTTON_TEXT
        )
        self.single_page_delete_button.setStyleSheet(stylesheet.DELETE_BUTTON)

        self.batch_page_import_button = QPushButton(
            language_config.TOPBAR_BATCH_IMPORT_BUTTON_TEXT
        )
        self.batch_page_import_button.setStyleSheet(stylesheet.IMPORT_BUTTON)
        self.batch_page_delete_button = QPushButton(
            language_config.TOPBAR_BATCH_DELETE_BUTTON_TEXT
        )
        self.batch_page_delete_button.setStyleSheet(stylesheet.DELETE_BUTTON)
        self.start_process_batch = QPushButton(
            language_config.TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT
        )
        self.start_process_batch.setStyleSheet(stylesheet.PROCESS_BUTTON)

        # === Tombol Switch (Tidak berubah) ===
        self.single_button = QPushButton("Single")
        self.single_button.setCheckable(True)
        self.single_button.setChecked(True)
        self.single_button.setStyleSheet(stylesheet.SWITCH_BUTTON)
        self.batch_button = QPushButton("Batch")
        self.batch_button.setCheckable(True)
        self.batch_button.setStyleSheet(stylesheet.SWITCH_BUTTON)

        self.switch_group = QButtonGroup(self)
        self.switch_group.setExclusive(True)
        self.switch_group.addButton(self.single_button)
        self.switch_group.addButton(self.batch_button)

        self.switch_inner_layout = QHBoxLayout()
        self.switch_inner_layout.setSpacing(0)
        self.switch_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.switch_inner_layout.addWidget(self.single_button)
        self.switch_inner_layout.addWidget(self.batch_button)
        self.switch_container = QWidget()
        self.switch_container.setLayout(self.switch_inner_layout)
        self.switch_container.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )

        # === Stack Kiri ===
        self.left_stack = QStackedWidget()
        self.left_stack.setStyleSheet(stylesheet.TRANSPARENT_BACKGROUND_STYLE)
        # Kontainer Single Kiri
        single_left_container = QWidget()
        single_left_layout = QHBoxLayout(single_left_container)
        single_left_layout.setContentsMargins(0, 0, 0, 0)
        single_left_layout.addWidget(self.single_page_import_button)
        single_left_layout.addStretch()
        self.left_stack.addWidget(single_left_container)  # Index 0
        # Kontainer Batch Kiri
        batch_left_container = QWidget()
        batch_left_layout_internal = QHBoxLayout(batch_left_container)
        batch_left_layout_internal.setContentsMargins(0, 0, 0, 0)
        batch_left_layout_internal.setSpacing(5)
        batch_left_layout_internal.addWidget(self.batch_page_import_button)
        batch_left_layout_internal.addWidget(self.batch_page_delete_button)
        batch_left_layout_internal.addStretch()
        self.left_stack.addWidget(batch_left_container)  # Index 1

        # === Stack Kanan ===
        self.right_stack = QStackedWidget()
        self.right_stack.setStyleSheet(stylesheet.TRANSPARENT_BACKGROUND_STYLE)
        # Kontainer Single Kanan
        single_right_container = QWidget()
        single_right_layout = QHBoxLayout(single_right_container)
        single_right_layout.setContentsMargins(0, 0, 0, 0)
        single_right_layout.addStretch()
        single_right_layout.addWidget(self.single_page_delete_button)
        self.right_stack.addWidget(single_right_container)  # Index 0
        # Kontainer Batch Kanan
        batch_right_container = QWidget()
        batch_right_layout_internal = QHBoxLayout(batch_right_container)
        batch_right_layout_internal.setContentsMargins(0, 0, 0, 0)
        batch_right_layout_internal.setSpacing(5)
        batch_right_layout_internal.addStretch()
        batch_right_layout_internal.addWidget(self.start_process_batch)
        self.right_stack.addWidget(batch_right_container)  # Index 1

        # === Susun Layout Utama (Gunakan QGridLayout) ===
        self.layout.addWidget(self.left_stack, 0, 0)  # Baris 0, Kolom 0
        self.layout.addWidget(
            self.switch_container, 0, 1, Qt.AlignmentFlag.AlignCenter
        )  # Baris 0, Kolom 1
        self.layout.addWidget(self.right_stack, 0, 2)  # Baris 0, Kolom 2
        # Atur Column Stretch Factor
        self.layout.setColumnStretch(0, 1)  # Kiri meregang
        self.layout.setColumnStretch(1, 0)  # Tengah tidak meregang
        self.layout.setColumnStretch(2, 1)  # Kanan meregang

        # Atur halaman awal stack
        self.left_stack.setCurrentIndex(0)
        self.right_stack.setCurrentIndex(0)

    # --- Tambahkan Metode untuk Mengontrol Stack (BARU) ---
    def switch_stacks_to_index(self, index):
        """Memberi tahu EnhanceStackPage untuk memulai transisi pada stack ini."""
        # EnhanceStackPage akan memanggil start_transition_for_stack
        pass  # Fungsi ini mungkin tidak perlu jika EnhanceStackPage langsung handle
