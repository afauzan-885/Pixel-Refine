"""
GenericUILibrary - Color Customization Example

Demonstrates how to use components with:
1. Default stylesheet_global_page() styling
2. Optional color customization per component
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PySide6.QtCore import Qt

# Import stylesheet
from resources.styles.stylesheet import stylesheet_global_page

# Import components
from resources.GenericUILibrary import (
    Container,
    Row,
    Button,
    Card,
)


class ColorCustomizationExample(QMainWindow):
    """Example showing default and customized component styling"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GenericUILibrary - Color Customization")
        self.resize(1000, 700)

        # IMPORTANT: Apply global stylesheet for default styling
        self.setStyleSheet(stylesheet_global_page())

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_container = Container(padding=15)
        from resources.GenericUILibrary.containers import Stack

        layout = Stack(orientation="vertical")
        central_widget.setLayout(layout.layout)
        layout.add_item(main_container)

        # Example 1: Default Styling (uses stylesheet_global_page)
        self._create_default_example(main_container)

        # Example 2: Custom Colors
        self._create_custom_example(main_container)

        # Example 3: Mixed Approach
        self._create_mixed_example(main_container)

    def _create_default_example(self, container):
        """Example 1: Components using default stylesheet"""
        card = Card(title="Default Styling (stylesheet_global_page)")

        label = QLabel(
            "These components use the default stylesheet_global_page() styling.\n"
            "No custom colors specified - they use objectName-based styling."
        )
        label.setWordWrap(True)
        card.add_body_widget(label)

        # Buttons with default styling
        row = Row(spacing=10)

        btn_primary = Button("Primary", variant="primary")
        btn_success = Button("Success", variant="success")
        btn_danger = Button("Danger", variant="danger")
        btn_info = Button("Info", variant="info")

        btn_primary.clicked.connect(lambda: print("Primary clicked"))
        btn_success.clicked.connect(lambda: print("Success clicked"))
        btn_danger.clicked.connect(lambda: print("Danger clicked"))
        btn_info.clicked.connect(lambda: print("Info clicked"))

        row.add_column(btn_primary)
        row.add_column(btn_success)
        row.add_column(btn_danger)
        row.add_column(btn_info)
        row.add_stretch()

        card.add_body_widget(row)
        container.add_widget(card)

    def _create_custom_example(self, container):
        """Example 2: Components with custom colors"""
        # Custom card colors
        card = Card(
            title="Custom Colors",
            bg_color="#F0F8FF",  # Light blue background
            border_color="#4682B4",  # Steel blue border
        )

        label = QLabel(
            "These components override the default colors with custom values.\n"
            "Notice the card has a custom background and border color."
        )
        label.setWordWrap(True)
        card.add_body_widget(label)

        # Buttons with custom colors
        row = Row(spacing=10)

        btn_purple = Button(
            "Custom Purple",
            variant="primary",
            bg_color="#9B59B6",  # Purple
            hover_color="#8E44AD",  # Darker purple
        )

        btn_orange = Button(
            "Custom Orange",
            variant="primary",
            bg_color="#FF8C00",  # Dark orange
            hover_color="#FF7F00",  # Darker orange
        )

        btn_teal = Button(
            "Custom Teal",
            variant="primary",
            bg_color="#20B2AA",  # Light sea green
            hover_color="#008B8B",  # Dark cyan
        )

        btn_purple.clicked.connect(lambda: print("Purple clicked"))
        btn_orange.clicked.connect(lambda: print("Orange clicked"))
        btn_teal.clicked.connect(lambda: print("Teal clicked"))

        row.add_column(btn_purple)
        row.add_column(btn_orange)
        row.add_column(btn_teal)
        row.add_stretch()

        card.add_body_widget(row)
        container.add_widget(card)

    def _create_mixed_example(self, container):
        """Example 3: Mix of default and custom styling"""
        card = Card(title="Mixed Approach")

        label = QLabel(
            "You can mix default and custom styling in the same interface.\n"
            "Most buttons use default colors, one uses custom."
        )
        label.setWordWrap(True)
        card.add_body_widget(label)

        row = Row(spacing=10)

        # Default buttons
        btn1 = Button("Cancel", variant="secondary")  # Default gray
        btn2 = Button("Delete", variant="danger")  # Default red

        # Custom button
        btn3 = Button(
            "Special Action",
            variant="primary",
            bg_color="#FF1493",  # Deep pink
            text_color="#FFFFFF",
            hover_color="#C71585",  # Medium violet red
        )

        # Default button
        btn4 = Button("Save", variant="success")  # Default green

        btn1.clicked.connect(lambda: print("Cancel"))
        btn2.clicked.connect(lambda: print("Delete"))
        btn3.clicked.connect(lambda: print("Special Action"))
        btn4.clicked.connect(lambda: print("Save"))

        row.add_column(btn1)
        row.add_column(btn2)
        row.add_column(btn3)
        row.add_column(btn4)
        row.add_stretch()

        card.add_body_widget(row)

        # Footer with default buttons
        save_btn = Button("Apply Changes", variant="primary")
        cancel_btn = Button("Close", variant="secondary")

        card.add_footer_widget(cancel_btn)
        card.add_footer_widget(save_btn)

        container.add_widget(card)


def main():
    """Run the color customization example"""
    app = QApplication(sys.argv)
    window = ColorCustomizationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
