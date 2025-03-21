# File: left_panel.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QStackedWidget,
)
from PyQt6.QtCore import Qt
from UI.enhance_stack.components.single_page_layout.parameter_pages import ParameterPages
from UI.resources.stylesheet.stylesheet import DROPDOWN_BOX
from UI.settings.General.Language import language_config

class LeftPanel(QWidget):
    """
    Kelas LeftPanel mengatur tampilan panel sebelah kiri, yang berisi dropdown untuk
    memilih parameter dan panel pengaturan dinamis yang berubah sesuai pilihan.
    """

    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """
        Inisialisasi tampilan panel dengan Preview Panel (70%) dan Parameter Panel (30%).
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # Beri sedikit jarak antar elemen

        self.init_preview_panel(layout)
        self.init_parameter_panel(layout)
        
        self.setLayout(layout)

    def init_preview_panel(self, parent_layout: QVBoxLayout) -> None:
        """
        Inisialisasi Preview Panel dan tambahkan ke parent layout.
        """
        self.preview_panel_widget = QWidget()
        preview_panel_layout = QVBoxLayout(self.preview_panel_widget)
        preview_panel_label = QLabel(language_config.PREVIEW_PANEL_LABEL)
        preview_panel_layout.addWidget(preview_panel_label)
        self.preview_panel_widget.setStyleSheet("QWidget { background-color: white; }")
        parent_layout.addWidget(self.preview_panel_widget)

    def init_parameter_panel(self, parent_layout: QVBoxLayout) -> None:
        """
        Inisialisasi Parameter Panel yang berisi dropdown di sisi kiri dan QStackedWidget
        untuk pengaturan di sisi kanan.
        """
        self.parameter_panel_widget = QWidget()
        self.parameter_panel_widget.setMaximumHeight(270)
        parameter_panel_layout = QHBoxLayout(self.parameter_panel_widget)
        parameter_panel_layout.setContentsMargins(10, 5, 0, 0)
        parameter_panel_layout.setSpacing(0)

        # Buat widget pembungkus untuk left_panel
        left_panel_widget = QWidget()
        # left_panel_widget.setMinimumWidth(250)
        left_panel_layout = QVBoxLayout(left_panel_widget) 
        left_panel_layout.setContentsMargins(0, 0, 0, 0) 

        # Dropdown untuk pengaturan parameter
        self.alignment_dropdown, alignment_widget = self.create_dropdown(
            language_config.ALIGNMENT_NAME,
            [opt[0] for opt in [
                ("None", language_config.NONE_ALIGNMENT_DESCRIPTION),
                ("Farneback Optical Flow", language_config.FARNEBACK_DESCRIPTION),
                ("AKAZE", language_config.AKAZE_DESCRIPTION),
                ("ORB", language_config.ORB_DESCRIPTION)
            ]],
            [opt[1] for opt in [
                ("None", language_config.NONE_ALIGNMENT_DESCRIPTION),
                ("Farneback Optical Flow", language_config.FARNEBACK_DESCRIPTION),
                ("AKAZE", language_config.AKAZE_DESCRIPTION),
                ("ORB", language_config.ORB_DESCRIPTION)
            ]]
        )
        left_panel_layout.addWidget(alignment_widget)

        self.super_resolution_dropdown, super_resolution_widget = self.create_dropdown(
            language_config.SUPER_RESOLUTION_NAME,
            [opt[0] for opt in [
                ("None", language_config.NONE_SUPER_RESOLUTION_DESCRIPTION),
                ("Interpolation", language_config.INTERPOLATION_DESCRIPTION)
            ]],
            [opt[1] for opt in [
                ("None", language_config.NONE_SUPER_RESOLUTION_DESCRIPTION),
                ("Interpolation", language_config.INTERPOLATION_DESCRIPTION)
            ]]
        )
        left_panel_layout.addWidget(super_resolution_widget)

        self.denoising_dropdown, denoising_widget = self.create_dropdown(
            language_config.DENOISING_NAME,
            [opt[0] for opt in [
                ("None", language_config.NONE_DENOISING_DESCRIPTION),
                ("Average", language_config.AVERAGE_DESCRIPTION),
                ("Weighted Average", language_config.WEIGHTED_AVERAGE_DESCRIPTION),
                ("Median", language_config.MEDIAN_DESCRIPTION),
                ("Similarity", language_config.SIMILARITY_DESCRIPTION)
            ]],
            [opt[1] for opt in [
                ("None", language_config.NONE_DENOISING_DESCRIPTION),
                ("Average", language_config.AVERAGE_DESCRIPTION),
                ("Weighted Average", language_config.WEIGHTED_AVERAGE_DESCRIPTION),
                ("Median", language_config.MEDIAN_DESCRIPTION),
                ("Similarity", language_config.SIMILARITY_DESCRIPTION)
            ]]
        )
        left_panel_layout.addWidget(denoising_widget)

        # Inisialisasi QStackedWidget untuk panel pengaturan
        self.parameter_stack = QStackedWidget()
        parameter_pages = ParameterPages(self.parameter_stack)
        self.setting_pages_map = parameter_pages.get_setting_pages_map()

        # Tambahkan parameter_stack langsung ke panel kanan tanpa ScrollArea
        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(self.parameter_stack)

        # Widget pembungkus untuk right_panel
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel_layout)

        # Tambahkan left_panel_widget dan right_panel_widget ke dalam layout utama
        parameter_panel_layout.addWidget(left_panel_widget, 1)
        parameter_panel_layout.addWidget(right_panel_widget, 2) 

        self.parameter_panel_widget.setLayout(parameter_panel_layout)
        self.parameter_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        parent_layout.addWidget(self.parameter_panel_widget)

        # Hubungkan sinyal dropdown ke fungsi update panel
        self.alignment_dropdown.currentIndexChanged.connect(
            lambda index: self.update_parameter_panel("alignment")
        )
        self.denoising_dropdown.currentIndexChanged.connect(self.handle_dropdown_change)
        self.super_resolution_dropdown.currentIndexChanged.connect(self.handle_dropdown_change)


    def create_dropdown(self, label_text: str, items: list, tooltips: list) -> tuple:
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

    def handle_dropdown_change(self, index: int) -> None:
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

    def update_parameter_panel(self, source: str) -> None:
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
