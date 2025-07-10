from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QScrollArea)
from PySide6.QtCore import Qt

from UI.enhance_stack.components.single_page_layout.parameter_alignment.akaze_parameter_settings import get_akaze_page

from UI.enhance_stack.components.single_page_layout.parameter_alignment.farneback_parameter_settings import get_farneback_optical_flow_page
from UI.enhance_stack.components.single_page_layout.parameter_alignment.orb_parameter_settings import get_orb_page
from UI.enhance_stack.components.single_page_layout.parameter_denoising.similarity_parameter_settings import get_similarity_settings_page
from UI.enhance_stack.components.single_page_layout.parameter_denoising.similarity_v2_parameter_settings import get_similarity_v2_settings_page
from UI.settings.General.Language import language_config


class ParameterPages:
    def __init__(self, stacked_widget):
        """
        Inisialisasi dengan QStackedWidget yang akan menampung halaman-halaman parameter.
        Kemudian, panggil metode untuk membuat dan menambahkan halaman.
        """
        self.stacked_widget = stacked_widget
        self.setting_pages_map = {}
        self.create_pages()

    def create_pages(self):
        """Buat dan tambahkan semua halaman parameter ke QStackedWidget."""
        # Halaman Default
        default_page = self.get_default_page()
        default_index = self.stacked_widget.addWidget(default_page)
        self.setting_pages_map["default"] = default_index

        akaze_page = get_akaze_page()
        index_akaze = self.stacked_widget.addWidget(akaze_page)
        self.setting_pages_map["AKAZE"] = index_akaze

        orb_page = get_orb_page()
        index_orb = self.stacked_widget.addWidget(orb_page)
        self.setting_pages_map["ORB"] = index_orb
        
        farneback_page = get_farneback_optical_flow_page()  
        index_farneback = self.stacked_widget.addWidget(farneback_page)
        self.setting_pages_map["Farneback Optical Flow"] = index_farneback

        # # Halaman untuk Average (dari Denoising Dropdown)
        similarity_v1_page = get_similarity_settings_page()
        index_similarity_v1 = self.stacked_widget.addWidget(similarity_v1_page)
        self.setting_pages_map["Similarity"] = index_similarity_v1
        
        similarity_v2_page = get_similarity_v2_settings_page()
        index_similarity_v2 = self.stacked_widget.addWidget(similarity_v2_page)
        self.setting_pages_map["Similarity V2"] = index_similarity_v2

    def wrap_in_scroll_area(self, widget):
        """
        Bungkus widget ke dalam QScrollArea dengan tampilan yang lebih modern dan tanpa outline.
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 10px;
                margin: 2px 0 2px 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #A0A0A0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
        """)
        return scroll

    def get_default_page(self):
        """Buat halaman default yang ditampilkan bila tidak ada pilihan parameter khusus."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel(language_config.DEFAULT_PARAMETER_SETTING_LABEL))
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return self.wrap_in_scroll_area(page)

    def get_setting_pages_map(self):
        """Kembalikan dictionary mapping nama halaman ke indeks QStackedWidget."""
        return self.setting_pages_map
