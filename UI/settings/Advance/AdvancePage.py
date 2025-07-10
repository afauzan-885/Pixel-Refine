from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton

def advance_page():
    advanced_tab = QWidget()
    layout = QVBoxLayout()

    # Logging Level
    logging_label = QLabel("Logging Level:")
    logging_combo = QComboBox()
    logging_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
    layout.addWidget(logging_label)
    layout.addWidget(logging_combo)

    # Reset Settings
    reset_button = QPushButton("Reset to Default")
    layout.addWidget(reset_button)

    advanced_tab.setLayout(layout)
    return advanced_tab
