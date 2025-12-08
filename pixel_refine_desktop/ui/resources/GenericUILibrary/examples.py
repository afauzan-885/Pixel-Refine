"""
GenericUILibrary - Usage Examples

This file demonstrates how to use the Bootstrap-like UI components.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt

# Import stylesheet
from pixel_refine_desktop.ui.resources.styles.stylesheet import stylesheet_global_page

# Import components
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    # Layouts
    Container,
    Row,
    Col,
    Stack,
    # Components
    Button,
    Card,
    ListGroup,
    FormGroup,
    Select,
    TabContainer,
    TabPane,
    Gallery,
    Modal,
)


class ExampleApp(QMainWindow):
    """Example application demonstrating GenericUILibrary components"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GenericUILibrary - Examples")
        self.resize(1200, 800)

        # Apply global stylesheet
        self.setStyleSheet(stylesheet_global_page())

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_container = Container(padding=15)
        central_widget_layout = Stack(orientation="vertical")
        central_widget.setLayout(central_widget_layout.layout)
        central_widget_layout.add_item(main_container)

        # Example 1: Buttons
        self._create_button_example(main_container)

        # Example 2: Cards
        self._create_card_example(main_container)

        # Example 3: Forms
        self._create_form_example(main_container)

        # Example 4: List Group
        self._create_list_example(main_container)

        # Example 5: Tabs
        self._create_tab_example(main_container)

    def _create_button_example(self, container):
        """Example: Different button variants"""
        card = Card(title="Buttons Example")

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

    def _create_card_example(self, container):
        """Example: Card with header and footer"""
        card = Card(title="User Profile")

        # Body content
        from PySide6.QtWidgets import QLabel

        content = QLabel(
            "This is a card body with some content.\nCards can contain any widgets."
        )
        content.setWordWrap(True)
        card.add_body_widget(content)

        # Footer buttons
        save_btn = Button("Save", variant="primary")
        cancel_btn = Button("Cancel", variant="secondary")

        card.add_footer_widget(cancel_btn)
        card.add_footer_widget(save_btn)

        container.add_widget(card)

    def _create_form_example(self, container):
        """Example: Form with inputs"""
        card = Card(title="Form Example")

        # Form fields
        name_field = FormGroup(
            label="Name", input_type="text", placeholder="Enter your name"
        )
        email_field = FormGroup(
            label="Email", input_type="text", placeholder="Enter your email"
        )

        role_field = FormGroup(label="Role", input_type="select")
        role_field.add_options(["Developer", "Designer", "Manager", "Tester"])

        card.add_body_widget(name_field)
        card.add_body_widget(email_field)
        card.add_body_widget(role_field)

        # Submit button
        submit_btn = Button("Submit", variant="primary")
        submit_btn.clicked.connect(
            lambda: self._on_form_submit(name_field, email_field, role_field)
        )
        card.add_footer_widget(submit_btn)

        container.add_widget(card)

    def _create_list_example(self, container):
        """Example: List group with selection"""
        list_group = ListGroup(
            title="Projects", selection_mode="single", show_actions=True
        )

        # Add items
        list_group.add_item("proj_1", "Project Alpha")
        list_group.add_item("proj_2", "Project Beta")
        list_group.add_item("proj_3", "Project Gamma")
        list_group.add_item("proj_4", "Project Delta")

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

        container.add_widget(list_group)

    def _create_tab_example(self, container):
        """Example: Tabs"""
        card = Card(title="Tabs Example")

        tabs = TabContainer()

        # Tab 1
        tab1 = TabPane()
        from PySide6.QtWidgets import QLabel

        tab1.add_widget(QLabel("This is the content of Tab 1"))
        tabs.add_tab("General", tab1)

        # Tab 2
        tab2 = TabPane()
        tab2.add_widget(QLabel("This is the content of Tab 2"))
        tabs.add_tab("Advanced", tab2)

        # Tab 3
        tab3 = TabPane()
        tab3.add_widget(QLabel("This is the content of Tab 3"))
        tabs.add_tab("Settings", tab3)

        tabs.tab_changed.connect(lambda index, title: print(f"Tab changed to: {title}"))

        card.add_body_widget(tabs)
        container.add_widget(card)

    def _on_form_submit(self, name_field, email_field, role_field):
        """Handle form submission"""
        name = name_field.get_value()
        email = email_field.get_value()
        role = role_field.get_value()

        print(f"Form submitted:")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Role: {role}")

        # Show modal confirmation
        modal = Modal(title="Form Submitted", parent=self)
        modal.set_body(f"Name: {name}\nEmail: {email}\nRole: {role}")
        modal.add_footer_button("OK", variant="primary")
        modal.exec()

    def _delete_selected_items(self, list_group):
        """Delete selected items from list"""
        selected = list_group.get_selected_items()
        for item_id, label in selected:
            list_group.remove_item(item_id)
            print(f"Deleted: {label}")


def main():
    """Run the example application"""
    app = QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
