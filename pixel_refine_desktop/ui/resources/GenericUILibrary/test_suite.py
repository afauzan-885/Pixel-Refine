"""
GenericUILibrary - Comprehensive Test Suite

Interactive test application to verify all UI components work correctly.
Tests both default styling and color customization.
"""

import sys
import os

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QSpinBox
from PySide6.QtCore import Qt

# Import stylesheet
from pixel_refine_desktop.ui.resources.styles.stylesheet import stylesheet_global_page

# Import all components using relative imports
from buttons import Button, IconButton, ButtonGroup, ToggleButton
from cards import Card, CardHeader, CardBody, CardFooter
from forms import FormGroup, Input, Select, Checkbox, Radio, RadioGroup
from containers import Container, Row, Col, Stack, ScrollContainer
from list_group import ListGroup
from modals import Modal
from tabs import TabContainer, TabPane
from grids import Gallery
from collapse import Collapse, Accordion


class ComponentTestSuite(QMainWindow):
    """Comprehensive test suite for all GenericUILibrary components"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GenericUILibrary - Test Suite")
        self.resize(1400, 900)

        # Apply global stylesheet
        self.setStyleSheet(stylesheet_global_page())

        # Main container with scroll
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = Stack(orientation="vertical")
        central_widget.setLayout(main_layout.layout)

        scroll = ScrollContainer()
        main_layout.add_item(scroll)

        container = Container(padding=20)
        scroll.add_widget(container)

        # Add title
        title = QLabel("GenericUILibrary - Component Test Suite")
        title.setStyleSheet(
            "font-size: 24pt; font-weight: bold; color: #2C3E50; margin-bottom: 20px;"
        )
        container.add_widget(title)

        # Test sections
        self._test_buttons(container)
        self._test_cards(container)
        self._test_forms(container)
        self._test_lists(container)
        self._test_tabs(container)
        self._test_gallery(container)
        self._test_collapse(container)
        self._test_custom_colors(container)

    def _test_buttons(self, container):
        """Test all button components"""
        card = Card(title="1. Button Components")

        # Standard buttons
        section = QLabel("Standard Buttons (Default Styling):")
        section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        card.add_body_widget(section)

        row1 = Row(spacing=10)
        row1.add_column(Button("Primary", variant="primary"))
        row1.add_column(Button("Secondary", variant="secondary"))
        row1.add_column(Button("Success", variant="success"))
        row1.add_column(Button("Danger", variant="danger"))
        row1.add_column(Button("Info", variant="info"))
        row1.add_stretch()
        card.add_body_widget(row1)

        # Custom colored buttons
        section2 = QLabel("Custom Colored Buttons:")
        section2.setStyleSheet("font-weight: bold; margin-top: 15px;")
        card.add_body_widget(section2)

        row2 = Row(spacing=10)
        row2.add_column(
            Button(
                "Purple", variant="primary", bg_color="#9B59B6", hover_color="#8E44AD"
            )
        )
        row2.add_column(
            Button(
                "Orange", variant="primary", bg_color="#FF8C00", hover_color="#FF7F00"
            )
        )
        row2.add_column(
            Button("Teal", variant="primary", bg_color="#20B2AA", hover_color="#008B8B")
        )
        row2.add_column(
            Button("Pink", variant="primary", bg_color="#FF1493", hover_color="#C71585")
        )
        row2.add_stretch()
        card.add_body_widget(row2)

        # Button group
        section3 = QLabel("Button Group:")
        section3.setStyleSheet("font-weight: bold; margin-top: 15px;")
        card.add_body_widget(section3)

        btn_group = ButtonGroup(orientation="horizontal")
        btn_group.add_button("Option 1", checkable=True)
        btn_group.add_button("Option 2", checkable=True)
        btn_group.add_button("Option 3", checkable=True)
        btn_group.button_clicked.connect(
            lambda idx, text: print(f"Button {idx}: {text}")
        )
        card.add_body_widget(btn_group)

        # Toggle button
        section4 = QLabel("Toggle Button:")
        section4.setStyleSheet("font-weight: bold; margin-top: 15px;")
        card.add_body_widget(section4)

        toggle = ToggleButton("Enable Feature", checked=False)
        toggle.toggled.connect(lambda checked: print(f"Toggle: {checked}"))
        card.add_body_widget(toggle)

        container.add_widget(card)

    def _test_cards(self, container):
        """Test card components"""
        # Default card
        card1 = Card(title="2. Card Components - Default Styling")
        card1.set_body_content(
            "This card uses default styling from stylesheet_global_page()."
        )
        card1.add_footer_widget(Button("Action", variant="primary"))
        card1.add_footer_widget(Button("Cancel", variant="secondary"))
        container.add_widget(card1)

        # Custom colored card
        card2 = Card(
            title="Card with Custom Colors", bg_color="#FFF3CD", border_color="#FFC107"
        )
        card2.set_body_content(
            "This card has a custom yellow background and amber border."
        )
        card2.add_footer_widget(Button("OK", variant="success"))
        container.add_widget(card2)

    def _test_forms(self, container):
        """Test form components"""
        card = Card(title="3. Form Components")

        # Text input
        name_field = FormGroup(
            label="Name", input_type="text", placeholder="Enter your name"
        )
        card.add_body_widget(name_field)

        # Email input
        email_field = FormGroup(
            label="Email", input_type="text", placeholder="Enter your email"
        )
        card.add_body_widget(email_field)

        # Number input
        age_field = FormGroup(label="Age", input_type="number")
        card.add_body_widget(age_field)

        # Select/Dropdown
        role_field = FormGroup(label="Role", input_type="select")
        role_field.add_options(["Developer", "Designer", "Manager", "Tester", "Other"])
        card.add_body_widget(role_field)

        # Checkboxes
        section = QLabel("Preferences:")
        section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        card.add_body_widget(section)

        check1 = Checkbox("Receive newsletter", checked=True)
        check2 = Checkbox("Enable notifications", checked=False)
        card.add_body_widget(check1)
        card.add_body_widget(check2)

        # Radio buttons
        section2 = QLabel("Experience Level:")
        section2.setStyleSheet("font-weight: bold; margin-top: 10px;")
        card.add_body_widget(section2)

        radio_group = RadioGroup(
            options=["Beginner", "Intermediate", "Advanced", "Expert"]
        )
        radio_group.selection_changed.connect(
            lambda idx, text: print(f"Selected: {text}")
        )
        card.add_body_widget(radio_group)

        # Submit button
        submit_btn = Button("Submit Form", variant="primary")
        submit_btn.clicked.connect(
            lambda: self._on_form_submit(name_field, email_field, role_field)
        )
        card.add_footer_widget(submit_btn)

        container.add_widget(card)

    def _test_lists(self, container):
        """Test list components"""
        card = Card(title="4. List Group Component")

        list_group = ListGroup(
            title="Projects", selection_mode="single", show_actions=True
        )

        # Add sample items
        list_group.add_item("proj_1", "Project Alpha - Web Application")
        list_group.add_item("proj_2", "Project Beta - Mobile App")
        list_group.add_item("proj_3", "Project Gamma - Desktop Software")
        list_group.add_item("proj_4", "Project Delta - API Service")
        list_group.add_item("proj_5", "Project Epsilon - Data Pipeline")

        # Connect signals
        list_group.item_selected.connect(
            lambda item_id, label: print(f"Selected: {label} (ID: {item_id})")
        )

        if list_group.btn_add:
            list_group.btn_add.clicked.connect(
                lambda: list_group.add_item(
                    f"proj_{list_group.list_widget.count() + 1}",
                    f"New Project {list_group.list_widget.count() + 1}",
                )
            )

        if list_group.btn_delete:
            list_group.btn_delete.clicked.connect(
                lambda: self._delete_selected_items(list_group)
            )

        card.add_body_widget(list_group)
        container.add_widget(card)

    def _test_tabs(self, container):
        """Test tab components"""
        card = Card(title="5. Tab Component")

        tabs = TabContainer()

        # Tab 1 - General
        tab1 = TabPane()
        tab1.add_widget(QLabel("General Settings"))
        tab1.add_widget(
            FormGroup(label="App Name", input_type="text", placeholder="My Application")
        )
        tab1.add_widget(
            FormGroup(label="Version", input_type="text", placeholder="1.0.0")
        )
        tabs.add_tab("General", tab1)

        # Tab 2 - Advanced
        tab2 = TabPane()
        tab2.add_widget(QLabel("Advanced Settings"))
        tab2.add_widget(Checkbox("Enable debug mode"))
        tab2.add_widget(Checkbox("Auto-save"))
        tab2.add_widget(FormGroup(label="Max connections", input_type="number"))
        tabs.add_tab("Advanced", tab2)

        # Tab 3 - About
        tab3 = TabPane()
        tab3.add_widget(QLabel("About This Application"))
        about_text = QLabel(
            "GenericUILibrary Test Suite\nVersion 1.0.0\n\nTesting all UI components."
        )
        about_text.setWordWrap(True)
        tab3.add_widget(about_text)
        tabs.add_tab("About", tab3)

        tabs.tab_changed.connect(lambda idx, title: print(f"Tab changed to: {title}"))

        card.add_body_widget(tabs)
        container.add_widget(card)

    def _test_gallery(self, container):
        """Test gallery/grid components"""
        card = Card(title="6. Gallery Component")

        gallery = Gallery(title="Image Gallery", columns=6, show_header=False)

        # Add sample items
        for i in range(18):
            gallery.add_item(f"img_{i}", f"Image {i+1}")

        gallery.item_clicked.connect(lambda item_id, label: print(f"Clicked: {label}"))
        gallery.item_double_clicked.connect(
            lambda item_id, label: print(f"Double-clicked: {label}")
        )

        card.add_body_widget(gallery)
        container.add_widget(card)

    def _test_collapse(self, container):
        """Test collapse/accordion components"""
        card = Card(title="7. Collapse & Accordion Components")

        # Single collapse
        section = QLabel("Single Collapse:")
        section.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        card.add_body_widget(section)

        collapse = Collapse(title="Click to expand", expanded=False)
        collapse_content = QLabel(
            "This is the collapsible content.\nIt can contain any widgets."
        )
        collapse_content.setWordWrap(True)
        collapse.set_content(collapse_content)
        card.add_body_widget(collapse)

        # Accordion
        section2 = QLabel("Accordion (only one open at a time):")
        section2.setStyleSheet(
            "font-weight: bold; margin-top: 15px; margin-bottom: 5px;"
        )
        card.add_body_widget(section2)

        accordion = Accordion()

        # Accordion item 1
        item1_content = QLabel("Content for section 1.\nThis is a collapsible section.")
        item1_content.setWordWrap(True)
        accordion.add_item("Section 1", item1_content)

        # Accordion item 2
        item2_content = QLabel(
            "Content for section 2.\nOnly one section can be open at a time."
        )
        item2_content.setWordWrap(True)
        accordion.add_item("Section 2", item2_content)

        # Accordion item 3
        item3_content = QLabel(
            "Content for section 3.\nClick headers to expand/collapse."
        )
        item3_content.setWordWrap(True)
        accordion.add_item("Section 3", item3_content)

        accordion.item_expanded.connect(lambda idx, title: print(f"Expanded: {title}"))

        card.add_body_widget(accordion)
        container.add_widget(card)

    def _test_custom_colors(self, container):
        """Test custom color combinations"""
        card = Card(title="8. Custom Color Combinations")

        section = QLabel("Mix of default and custom styled components:")
        section.setWordWrap(True)
        card.add_body_widget(section)

        # Row 1: Default buttons
        row1 = Row(spacing=10)
        row1.add_column(QLabel("Default:"))
        row1.add_column(Button("Save", variant="success"))
        row1.add_column(Button("Delete", variant="danger"))
        row1.add_column(Button("Info", variant="info"))
        row1.add_stretch()
        card.add_body_widget(row1)

        # Row 2: Custom buttons
        row2 = Row(spacing=10)
        row2.add_column(QLabel("Custom:"))
        row2.add_column(
            Button(
                "Violet", variant="primary", bg_color="#8B00FF", hover_color="#7300CC"
            )
        )
        row2.add_column(
            Button(
                "Coral", variant="primary", bg_color="#FF7F50", hover_color="#FF6347"
            )
        )
        row2.add_column(
            Button("Lime", variant="primary", bg_color="#32CD32", hover_color="#228B22")
        )
        row2.add_stretch()
        card.add_body_widget(row2)

        # Custom card in a row
        section2 = QLabel("Custom colored cards:")
        section2.setStyleSheet("font-weight: bold; margin-top: 15px;")
        card.add_body_widget(section2)

        row3 = Row(spacing=10)

        mini_card1 = Card(title="Info", bg_color="#E3F2FD", border_color="#2196F3")
        mini_card1.set_body_content("Blue theme")
        row3.add_column(mini_card1, stretch=1)

        mini_card2 = Card(title="Success", bg_color="#E8F5E9", border_color="#4CAF50")
        mini_card2.set_body_content("Green theme")
        row3.add_column(mini_card2, stretch=1)

        mini_card3 = Card(title="Warning", bg_color="#FFF3E0", border_color="#FF9800")
        mini_card3.set_body_content("Orange theme")
        row3.add_column(mini_card3, stretch=1)

        card.add_body_widget(row3)

        container.add_widget(card)

    def _on_form_submit(self, name_field, email_field, role_field):
        """Handle form submission"""
        name = name_field.get_value()
        email = email_field.get_value()
        role = role_field.get_value()

        print(f"\n=== Form Submitted ===")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Role: {role}")
        print("=====================\n")

        # Show modal
        modal = Modal(title="Form Submitted", size="small", parent=self)
        modal.set_body(f"Name: {name}\nEmail: {email}\nRole: {role}")
        modal.add_footer_button("Close", variant="primary")
        modal.exec()

    def _delete_selected_items(self, list_group):
        """Delete selected items from list"""
        selected = list_group.get_selected_items()
        for item_id, label in selected:
            list_group.remove_item(item_id)
            print(f"Deleted: {label}")


def main():
    """Run the test suite"""
    print("=" * 60)
    print("GenericUILibrary - Component Test Suite")
    print("=" * 60)
    print("\nTesting all components with:")
    print("  ✓ Default stylesheet_global_page() styling")
    print("  ✓ Optional color customization")
    print("  ✓ All component variants")
    print("\nInteract with components to test functionality.")
    print("Check console for event outputs.\n")
    print("=" * 60)

    app = QApplication(sys.argv)
    window = ComponentTestSuite()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
