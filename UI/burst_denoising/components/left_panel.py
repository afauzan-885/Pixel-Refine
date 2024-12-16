from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox

class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Preview Panel
        self.preview_panel_widget = QWidget()
        preview_panel_layout = QVBoxLayout(self.preview_panel_widget)
        preview_panel_label = QLabel(" Preview Panel")
        preview_panel_layout.addWidget(preview_panel_label)
        self.preview_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        # Parameter Panel
        self.parameter_panel_widget = QWidget()
        parameter_panel_layout = QVBoxLayout(self.parameter_panel_widget)
        parameter_panel_layout.setContentsMargins(10, 10, 0, 0)

        # Global Alignment Dropdown
        global_layout = QVBoxLayout()
        global_label = QLabel("Global Alignment Algorithm")
        global_layout.setContentsMargins(0, 10, 0, 20)
        self.global_dropdown = QComboBox()
        self.global_dropdown.addItems(["FFT Phase Correlation","EEC", "Stack Optical Flow"])
        self.global_dropdown.setStyleSheet(self.get_dropdown_style())
        global_layout.addWidget(global_label)
        global_layout.addWidget(self.global_dropdown)

        global_widget = QWidget()
        global_widget.setLayout(global_layout)
        parameter_panel_layout.addWidget(global_widget)

        # Local Alignment Dropdown
        local_layout = QVBoxLayout()
        local_label = QLabel("Local Alignment Algorithm")
        local_layout.setContentsMargins(0, 10, 0, 20)
        self.local_dropdown = QComboBox()
        self.local_dropdown.addItems(["Horn-Schunck", "Farneback"])
        self.local_dropdown.setStyleSheet(self.get_dropdown_style())
        local_layout.addWidget(local_label)
        local_layout.addWidget(self.local_dropdown)

        local_widget = QWidget()
        local_widget.setLayout(local_layout)
        parameter_panel_layout.addWidget(local_widget)

        # Stacking Dropdown
        stacking_layout = QVBoxLayout()
        stacking_label = QLabel("Stacking Method")
        stacking_layout.setContentsMargins(0, 10, 0, 20)
        self.stacking_dropdown = QComboBox()
        self.stacking_dropdown.addItems(["Weighted Averaging", "Average"])
        self.stacking_dropdown.setStyleSheet(self.get_dropdown_style())
        stacking_layout.addWidget(stacking_label)
        stacking_layout.addWidget(self.stacking_dropdown)

        stacking_widget = QWidget()
        stacking_widget.setLayout(stacking_layout)
        parameter_panel_layout.addWidget(stacking_widget)

        self.parameter_panel_widget.setStyleSheet("QWidget { background-color: white; }")

        # Add parameter_panel Left Panel to Main Layout
        layout.addWidget(self.preview_panel_widget)
        layout.addWidget(self.parameter_panel_widget)

    def get_dropdown_style(self):
        """Returns a consistent style for dropdown menus."""
        return """
            QComboBox {
                background-color: #f0f0f0;
                border: none;
                padding: 5px;
                border-radius: 5px;
                max-width: 200px;
            }
        """
