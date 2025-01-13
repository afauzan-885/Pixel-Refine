from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from UI.settings.General.Language import language_config
class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Preview Panel
        self.preview_panel_widget = QWidget()
        preview_panel_layout = QVBoxLayout(self.preview_panel_widget)
        preview_panel_label = QLabel("Preview Panel")
        preview_panel_layout.addWidget(preview_panel_label)
        self.preview_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        # Parameter Panel
        self.parameter_panel_widget = QWidget()
        parameter_panel_layout = QVBoxLayout(self.parameter_panel_widget)
        parameter_panel_layout.setContentsMargins(10, 10, 0, 0)

        # Fungsi untuk membuat bagian dropdown (untuk mengurangi duplikasi kode)
        def dropdown_section(label_text, items, tooltips):
            section_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")  # Membuat label lebih tebal
            dropdown = QComboBox()
            for item, tooltip in zip(items, tooltips):
                dropdown.addItem(item)
                dropdown.setItemData(dropdown.count() - 1, tooltip, Qt.ItemDataRole.ToolTipRole)
            dropdown.setStyleSheet(self.get_dropdown_style())
            section_layout.addWidget(label)
            section_layout.addWidget(dropdown)
            section_widget = QWidget()
            section_widget.setLayout(section_layout)
            return dropdown, section_widget
        
        # Alignment Dropdown
        alignment_options = [
            ("None", language_config.NONE_ALIGNMENT_DESCRIPTION),
            ("Farneback Optical Flow", language_config.FARNEBACK_DESCRIPTION),
            ("AKAZE", language_config.AKAZE_DESCRIPTION),
            ("ORB", language_config.ORB_DESCRIPTION),
            # ("EEC", language_config.ORB_DESCRIPTION)
        ]
        alignment_items, alignment_tooltips = zip(*alignment_options)
        self.alignment_dropdown, alignment_widget = dropdown_section(
            
            language_config.ALIGNMENT_NAME,
            
            alignment_items,
            alignment_tooltips
        )
        
        # Super Resolution Dropdown
        super_resolution_items_options = [
            ("None", language_config.NONE_SUPER_RESOLUTION_DESCRIPTION)
        ]
        super_resolution_items, super_resolution_tooltips = zip(*super_resolution_items_options)
        self.super_resolution_dropdown, super_resolution_widget = dropdown_section(
            
            language_config.SUPER_RESOLUTION_NAME,
            
            super_resolution_items,
            super_resolution_tooltips
        )
        
        # Denoising Dropdown
        denoising_items_options = [
            ("None", language_config.NONE_DENOISING_DESCRIPTION),
            ("Average", language_config.AVERAGE_DESCRIPTION),
            ("Median", language_config.MEDIAN_DESCRIPTION),
            ("Similarity", language_config.SIMILARITY_DESCRIPTION)
        ]
        denoising_items, denoising_tooltips = zip(*denoising_items_options)
        self.denoising_dropdown, denoising_widget = dropdown_section(
            
            language_config.DENOISING_NAME,
            denoising_items,
            denoising_tooltips
        )

        # Tambahkan dropdown ke layout parameter panel
        parameter_panel_layout.addWidget(alignment_widget)
        parameter_panel_layout.addWidget(super_resolution_widget)
        parameter_panel_layout.addWidget(denoising_widget)
        self.parameter_panel_widget.setLayout(parameter_panel_layout)
        self.parameter_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        # Hubungkan sinyal
        self.denoising_dropdown.currentIndexChanged.connect(self.handle_dropdown_change)
        self.super_resolution_dropdown.currentIndexChanged.connect(self.handle_dropdown_change)

        # Add panels to main layout
        layout.addWidget(self.preview_panel_widget)
        layout.addWidget(self.parameter_panel_widget)
        self.setLayout(layout)

    def get_dropdown_style(self):
        return """
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

    def handle_dropdown_change(self, index):
        sender = self.sender()
        if sender == self.denoising_dropdown:
            if index != 0:
                self.super_resolution_dropdown.setCurrentIndex(0)
        elif sender == self.super_resolution_dropdown:
            if index != 0:
                self.denoising_dropdown.setCurrentIndex(0)
