from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QFormLayout

def general_page():
    """Creates a general settings tab with QFormLayout."""
    general_tab = QWidget()

    # Tab background style
    general_tab.setStyleSheet("""
        background-color: #ffffff;
        border: none;
    """)

    form_layout = QFormLayout()
    form_layout.setContentsMargins(10, 10, 10, 10)
    form_layout.setSpacing(10) 

    # Language and Dropdown Language
    language_label = QLabel("Language")
    language_dropdown = QComboBox()
    language_dropdown.addItems(["English", "Indonesian"])
    language_dropdown.setStyleSheet("""
        QComboBox {
            background-color: #f0f0f0;
            border: none;
            padding: 5px;
            border-radius: 5px;
            max-width: 200px;
        }
    """)

    # Add to layout
    form_layout.addRow(language_label, language_dropdown)

    # Set the layout to the tab
    general_tab.setLayout(form_layout)

    return general_tab
