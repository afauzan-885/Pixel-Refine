from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QFormLayout
def general_page():
    """Creates a general settings tab with QFormLayout."""
    general_tab = QWidget()

    # Tab background style
    general_tab.setStyleSheet(
        """
        background-color: #ffffff;
        border: none;
    """
    )

    form_layout = QFormLayout()
    form_layout.setContentsMargins(10, 10, 10, 10)
    form_layout.setSpacing(10)

    # Define the language dropdown and label first
    language_label = QLabel("Language")
    language_dropdown = QComboBox()
    language_dropdown.addItems(["English", "Indonesian", "French", "Melayu", "Spanish"])
    language_dropdown.setStyleSheet(
        """
        QComboBox {
            background-color: #f0f0f0;
            border: none;
            padding: 5px;
            border-radius: 5px;
            max-width: 200px;
        }
    """
    )

    # Add language label and dropdown to the layout
    form_layout.addRow(language_label, language_dropdown)

    # Define the resolution dropdown and label
    resolution_label = QLabel("Output Resolution")
    resolution_dropdown = QComboBox()
    resolution_dropdown.addItems(["Original", "1920x1080", "1280x720", "640x480"])
    resolution_dropdown.setStyleSheet(
        """
        QComboBox {
            background-color: #f0f0f0;
            border: none;
            padding: 5px;
            border-radius: 5px;
            max-width: 200px;
        }
    """
    )

    # Add resolution label and dropdown to the layout
    form_layout.addRow(resolution_label, resolution_dropdown)

    # Define the format dropdown and label
    format_label = QLabel("Output Format")
    format_dropdown = QComboBox()
    format_dropdown.addItems(["JPEG", "PNG", "TIFF", "BMP"])
    format_dropdown.setStyleSheet(
        """
        QComboBox {
            background-color: #f0f0f0;
            border: none;
            padding: 5px;
            border-radius: 5px;
            max-width: 200px;
        }
    """
    )

    # Add format label and dropdown to the layout
    form_layout.addRow(format_label, format_dropdown)
    # Set the layout to the tab
    general_tab.setLayout(form_layout)

    return general_tab