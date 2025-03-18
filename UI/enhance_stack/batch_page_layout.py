from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from UI.enhance_stack.logic.database_manager import DatabaseManager

class BatchPageLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)

        # Membuat panel utama
        self.main_panel = self.setup_main_panel()

        # Membuat dua panel gabungan
        self.combined_panel_1 = self.setup_combined_panel()
        self.combined_panel_2 = self.setup_combined_panel()

        # Menambahkan combined_panel ke dalam main_panel_layout
        self.main_panel_layout.addWidget(self.combined_panel_1)
        self.main_panel_layout.addWidget(self.combined_panel_2)

        # Menambahkan Spacer agar combined_panel tetap berada di atas
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_panel_layout.addSpacerItem(spacer)

        # Menambahkan panel utama ke layout induk
        self.layout.addWidget(self.main_panel)

    def setup_main_panel(self):
        """Membuat panel utama dengan layout vertikal agar UI tersusun dari atas."""
        main_panel = QWidget(self)
        main_panel.setStyleSheet("background-color: white;")
        main_panel_layout = QVBoxLayout(main_panel)
        main_panel_layout.setContentsMargins(10, 10, 10, 10)
        main_panel_layout.setSpacing(30) 
        self.main_panel_layout = main_panel_layout
        return main_panel

    def setup_combined_panel(self):
        """Membuat panel gabungan yang berisi tombol tambah, tombol delete, parameter_panel, dan list_panel."""
        combined_panel = QWidget()
        combined_panel.setMaximumHeight(120)  # Berikan tinggi maksimum agar UI tetap rapi
        combined_panel_layout = QHBoxLayout(combined_panel)
        combined_panel_layout.setContentsMargins(0, 0, 0, 0)

        # Layout vertikal untuk tombol Add & Delete
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tombol "Tambah" (dengan ikon)
        add_button = QPushButton()
        add_button.setFixedSize(30, 30)
        add_button.setIcon(QIcon("UI/resources/icon/add-image.png"))
        add_button.setIconSize(QSize(25, 25))
        add_button.setStyleSheet("background-color: #4CAF50; border-radius: 5px;")

        # Tombol "Delete" (dengan ikon)
        delete_button = QPushButton()
        delete_button.setFixedSize(30, 30)
        delete_button.setIcon(QIcon("UI/resources/icon/delete-image.png"))
        delete_button.setStyleSheet("background-color: #F44336; border-radius: 5px;")
        
        # Tombol "Delete" (dengan ikon)
        play_preview = QPushButton()
        play_preview.setFixedSize(30, 30)
        play_preview.setIcon(QIcon("UI/resources/icon/play-preview.png"))
        play_preview.setStyleSheet("background-color: #31CBD1; border-radius: 5px;")

        # Spacer agar tombol tetap di atas
        # spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Tambahkan tombol ke dalam layout vertikal
        button_layout.addWidget(add_button)
        button_layout.addWidget(play_preview)
        button_layout.addWidget(delete_button)
        # button_layout.addSpacerItem(spacer)  # Spacer agar tombol tetap di atas

        # Bungkus button_layout dalam QWidget
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Layout horizontal untuk button_widget + parameter_panel
        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Panel Parameter
        parameter_panel = QWidget()
        parameter_panel.setStyleSheet("background-color: #EBEAEA")
        parameter_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Tambahkan button_widget ke kiri dan parameter_panel ke kanan
        left_layout.addWidget(button_widget)
        left_layout.addWidget(parameter_panel, 1)

        # Panel kanan (Panel List gambar)
        list_panel = QWidget()
        list_panel.setStyleSheet("background-color: #DBDBDB")
        list_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Bungkus left_layout dalam QWidget
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Tambahkan ke combined panel layout
        combined_panel_layout.addWidget(left_widget, 1)  # Button + Parameter Panel
        combined_panel_layout.addWidget(list_panel, 2)  # List Panel

        return combined_panel