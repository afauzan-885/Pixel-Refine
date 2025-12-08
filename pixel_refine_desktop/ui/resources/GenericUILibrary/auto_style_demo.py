"""
Demo: Auto-Stylesheet Application

Demonstrates that stylesheet is automatically applied when importing GenericUILibrary.
No need to manually call stylesheet_global_page()!
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
sys.path.insert(0, project_root)

# Just import GenericUILibrary components
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    Card,
    Button,
    FormGroup,
    Container,
    Stack,
    Row,
    apply_stylesheet,  # Import the stylesheet helper
)


class AutoStyleDemo(QMainWindow):
    """Demo showing auto-stylesheet application"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auto-Stylesheet Demo")
        self.resize(600, 400)

        # NO NEED TO CALL: self.setStyleSheet(stylesheet_global_page())
        # It's already applied automatically!

        # Create UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_stack = Stack(orientation="vertical", spacing=15)
        central_widget.setLayout(main_stack.layout)

        container = Container(padding=20)
        main_stack.add_item(container)

        # Title
        title_card = Card(title="✨ Auto-Stylesheet Demo")
        title_label = QLabel(
            "Stylesheet applied with apply_stylesheet()!\n\n"
            "Call apply_stylesheet() after creating QApplication.\n"
            "Simple and explicit - no magic imports!"
        )
        title_label.setWordWrap(True)
        title_card.add_body_widget(title_label)
        container.add_widget(title_card)

        # Components demo
        demo_card = Card(title="Sample Components")

        # Form
        name_field = FormGroup(
            label="Name", input_type="text", placeholder="Enter your name"
        )
        demo_card.add_body_widget(name_field)

        email_field = FormGroup(
            label="Email", input_type="text", placeholder="Enter your email"
        )
        demo_card.add_body_widget(email_field)

        # Buttons
        from pixel_refine_desktop.ui.resources.GenericUILibrary import Row

        button_row = Row(spacing=10)
        button_row.add_column(Button("Primary", variant="primary"))
        button_row.add_column(Button("Success", variant="success"))
        button_row.add_column(Button("Danger", variant="danger"))
        button_row.add_stretch()
        demo_card.add_body_widget(button_row)

        container.add_widget(demo_card)


def main():
    print("=" * 60)
    print("Auto-Stylesheet Demo")
    print("=" * 60)
    print("\n✅ Call apply_stylesheet() after QApplication creation!")
    print("\nUsage:\n")
    print("  app = QApplication(sys.argv)")
    print("  from GenericUILibrary import apply_stylesheet")
    print("  apply_stylesheet()  # Apply stylesheet")
    print("\n" + "=" * 60)

    app = QApplication(sys.argv)

    # Apply stylesheet after QApplication is created
    apply_stylesheet()

    window = AutoStyleDemo()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
