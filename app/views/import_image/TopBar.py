from PyQt6.QtWidgets import QHBoxLayout, QPushButton

class TopBar(QHBoxLayout):
    def __init__(self, import_callback, delete_callback):
        super().__init__()

        # Tombol Import Image
        import_button = QPushButton("Import Image")
        import_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        import_button.clicked.connect(import_callback)
        self.addWidget(import_button)

        # Tombol Delete
        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_button.clicked.connect(delete_callback)
        self.addStretch()  # Push delete button to the right
        self.addWidget(delete_button)
