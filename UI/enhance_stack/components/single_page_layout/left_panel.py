# File: left_panel.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QStackedWidget,
)
from PyQt6.QtCore import Qt
from UI.enhance_stack.components.algorithm_list import get_algorithm_descriptions, get_algorithm_names, get_algorithm_options, get_category_display_name
from UI.enhance_stack.components.single_page_layout.parameter_pages import ParameterPages
from UI.resources.stylesheet.stylesheet import DROPDOWN_BOX
from UI.settings.General.Language import language_config

class LeftPanel(QWidget):
    """
    Kelas LeftPanel mengatur tampilan panel sebelah kiri, yang berisi dropdown untuk
    memilih parameter dan panel pengaturan dinamis yang berubah sesuai pilihan.
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Inisialisasi tampilan panel dengan Preview Panel (70%) dan Parameter Panel (30%).
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # Beri sedikit jarak antar elemen

        self.init_preview_panel(layout)
        self.init_parameter_panel(layout)
        
        self.setLayout(layout)

    def init_preview_panel(self, parent_layout):
        """
        Inisialisasi Preview Panel dan tambahkan ke parent layout.
        """
        self.preview_panel_widget = QWidget()
        preview_panel_layout = QVBoxLayout(self.preview_panel_widget)
        preview_panel_label = QLabel(language_config.PREVIEW_PANEL_LABEL)
        preview_panel_layout.addWidget(preview_panel_label)
        self.preview_panel_widget.setStyleSheet("QWidget { background-color: white; }")
        parent_layout.addWidget(self.preview_panel_widget)

    def init_parameter_panel(self, parent_layout):
        """
        Inisialisasi Parameter Panel yang berisi dropdown di sisi kiri dan QStackedWidget
        untuk pengaturan di sisi kanan.
        """
        self.parameter_panel_widget = QWidget()
        self.parameter_panel_widget.setMaximumHeight(270)
        parameter_panel_layout = QHBoxLayout(self.parameter_panel_widget)
        parameter_panel_layout.setContentsMargins(10, 5, 0, 0)
        parameter_panel_layout.setSpacing(0)

        left_panel_widget = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_widget)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)

        # --- Dropdown Alignment ---
        alignment_names = get_algorithm_names("alignment")
        alignment_descs = get_algorithm_descriptions("alignment")
        alignment_display_name = get_category_display_name("alignment")
        self.alignment_dropdown, alignment_widget = self.create_dropdown(
            alignment_display_name,
            alignment_names,
            alignment_descs
        )
        left_panel_layout.addWidget(alignment_widget)

        # --- Dropdown Super Resolution ---
        super_res_names = get_algorithm_names("super_resolution")
        super_res_descs = get_algorithm_descriptions("super_resolution")
        super_res_display_name = get_category_display_name("super_resolution")

        # Buat dropdown dengan semua opsi
        self.super_resolution_dropdown, super_resolution_widget = self.create_dropdown(
            super_res_display_name,
            super_res_names, # Gunakan list nama yang lengkap
            super_res_descs  # Gunakan list deskripsi yang lengkap
        )
        left_panel_layout.addWidget(super_resolution_widget)

        # --- Dropdown Denoising ---
        denoising_names = get_algorithm_names("denoising")
        denoising_descs = get_algorithm_descriptions("denoising")
        denoising_display_name = get_category_display_name("denoising")
        self.denoising_dropdown, denoising_widget = self.create_dropdown(
            denoising_display_name,
            denoising_names,
            denoising_descs
        )
        left_panel_layout.addWidget(denoising_widget)

        # --- Panel Kanan (Parameter Stack) ---
        self.parameter_stack = QStackedWidget()
        parameter_pages = ParameterPages(self.parameter_stack)
        self.setting_pages_map = parameter_pages.get_setting_pages_map()

        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(self.parameter_stack)
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel_layout)

        # --- Gabungkan Panel Kiri dan Kanan ---
        parameter_panel_layout.addWidget(left_panel_widget, 1)
        parameter_panel_layout.addWidget(right_panel_widget, 2)

        self.parameter_panel_widget.setLayout(parameter_panel_layout)
        self.parameter_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        parent_layout.addWidget(self.parameter_panel_widget)

        # --- Hubungkan Sinyal ---
        # Pastikan Anda memiliki metode self.update_parameter_panel dan self.handle_dropdown_change
        self.alignment_dropdown.currentIndexChanged.connect(
            lambda index: self.update_parameter_panel("alignment") # Pastikan key "alignment" cocok
        )
        # Koneksi untuk denoising dan super-resolution (asumsi handle_dropdown_change bisa menanganinya)
        self.denoising_dropdown.currentIndexChanged.connect(self.handle_dropdown_change)
        self.super_resolution_dropdown.currentIndexChanged.connect(self.handle_dropdown_change)


    def create_dropdown(self, label_text, items, tooltips):
        """
        Membuat komponen dropdown yang dilengkapi label dan tooltip.
        
        Args:
            label_text (str): Teks label untuk dropdown.
            items (list): List item yang akan dimasukkan ke dropdown.
            tooltips (list): List tooltip untuk masing-masing item.
            
        Returns:
            tuple: (QComboBox, QWidget) yang merupakan dropdown dan widget container-nya.
        """
        section_layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold;")
        dropdown = QComboBox()
        for item, tooltip in zip(items, tooltips):
            dropdown.addItem(item)
            dropdown.setItemData(dropdown.count() - 1, tooltip, Qt.ItemDataRole.ToolTipRole)
        dropdown.setStyleSheet(DROPDOWN_BOX)
        section_layout.addWidget(label)
        section_layout.addWidget(dropdown)
        section_widget = QWidget()
        section_widget.setLayout(section_layout)
        return dropdown, section_widget

    def handle_dropdown_change(self, index):
        """
        Tangani perubahan pada dropdown Denoising dan Super Resolution. 
        Jika salah satu diubah (selain 'None'), reset dropdown yang lain.
        """
        sender = self.sender()
        if sender == self.denoising_dropdown:
            if index != 0:
                self.super_resolution_dropdown.setCurrentIndex(0)
            self.update_parameter_panel("denoising")
        elif sender == self.super_resolution_dropdown:
            if index != 0:
                self.denoising_dropdown.setCurrentIndex(0)
            self.update_parameter_panel("super_resolution")

    def update_parameter_panel(self, source):
        """
        Perbarui tampilan halaman pengaturan sesuai dengan dropdown yang terakhir diubah.
        
        Args:
            source (str): Sumber perubahan, misalnya "alignment", "denoising", atau "super_resolution".
        """
        if source == "alignment":
            chosen = self.alignment_dropdown.currentText()
            if chosen in self.setting_pages_map and chosen != "None":
                self.parameter_stack.setCurrentIndex(self.setting_pages_map[chosen])
                return
        elif source == "denoising":
            chosen = self.denoising_dropdown.currentText()
            if chosen in self.setting_pages_map and chosen != "None":
                self.parameter_stack.setCurrentIndex(self.setting_pages_map[chosen])
                return
        elif source == "super_resolution":
            chosen = self.super_resolution_dropdown.currentText()
            if chosen in self.setting_pages_map and chosen != "None":
                self.parameter_stack.setCurrentIndex(self.setting_pages_map[chosen])
                return
        self.parameter_stack.setCurrentIndex(self.setting_pages_map["default"])
