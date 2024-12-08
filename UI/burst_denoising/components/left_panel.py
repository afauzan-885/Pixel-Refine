from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PIL import Image
import io

class LeftPanel(QWidget):
    """Left panel with top and parameter_panel sections."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Preview Panel
        self.preview_panel_widget = QWidget()
        preview_panel_layout = QVBoxLayout(self.preview_panel_widget)
        preview_panel_label = QLabel("Panel Preview")
        preview_panel_layout.addWidget(preview_panel_label)
        self.preview_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        # parameter_panel Panel
        self.parameter_panel_widget = QWidget()
        parameter_panel_layout = QVBoxLayout(self.parameter_panel_widget)
        parameter_panel_layout.setContentsMargins(10, 10, 0, 0)

        # Dropdown 1: Global Alignment
        global_layout = QVBoxLayout()
        global_label = QLabel("Algoritma Global Alignment")
        global_layout.setContentsMargins(0, 10, 0, 20)
        global_dropdown = QComboBox()
        global_dropdown.addItems(["Option 1", "Option 2", "Option 3"])  # Add options
        global_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: none;
                padding: 5px;
                border-radius: 5px;
                max-width: 200px;
            }
        """)  
        global_layout.addWidget(global_label)
        global_layout.addWidget(global_dropdown)

        # Widget Global Alignment
        global_widget = QWidget()
        global_widget.setLayout(global_layout)
        parameter_panel_layout.addWidget(global_widget)

        # Dropdown 2: Local Alignment
        local_layout = QVBoxLayout()
        local_label = QLabel("Algoritma Local Alignment")
        local_layout.setContentsMargins(0, 10, 0, 20)
        local_dropdown = QComboBox()
        local_dropdown.addItems(["Option A", "Option B", "Option C"])
        local_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: none;
                padding: 5px;
                border-radius: 5px;
                max-width: 200px;
            }
        """)  
        local_layout.addWidget(local_label)
        local_layout.addWidget(local_dropdown)

        # Widget Local Alignment
        local_widget = QWidget()
        local_widget.setLayout(local_layout)
        parameter_panel_layout.addWidget(local_widget)

        # Dropdown 3: Stacking
        stacking_layout = QVBoxLayout()
        stacking_label = QLabel("Algoritma Stacking")
        stacking_layout.setContentsMargins(0, 10, 0, 20)
        stacking_dropdown = QComboBox()
        stacking_dropdown.addItems(["Method X", "Method Y", "Method Z"])  # Add options
        stacking_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: none;
                padding: 5px;
                border-radius: 5px;
                max-width: 200px;
            }
        """)  
        stacking_layout.addWidget(stacking_label)
        stacking_layout.addWidget(stacking_dropdown)

        # Widget Stacking
        stacking_widget = QWidget()
        stacking_widget.setLayout(stacking_layout)
        parameter_panel_layout.addWidget(stacking_widget)

        self.parameter_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        # Add parameter_panel Left Panel to Main Layout
        layout.addWidget(self.preview_panel_widget)
        layout.addWidget(self.parameter_panel_widget)
