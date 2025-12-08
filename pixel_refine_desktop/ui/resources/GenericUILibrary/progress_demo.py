"""
GenericUILibrary - Progress Bar, Modal, and Toast Demo

Demonstrates all progress bar styles, enhanced modals, and toast notifications.
"""

import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import QTimer

# Import stylesheet
from pixel_refine_desktop.ui.resources.styles.stylesheet import stylesheet_global_page

# Import components
from containers import Container, Row, Stack
from cards import Card
from buttons import Button
from progress_bars import ProgressBar, IndeterminateProgress, ProgressGroup
from modals import Modal


class ProgressDemo(QMainWindow):
    """Demo application for progress bars, modals, and toasts"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Progress Bars, Modals & Toast Demo")
        self.resize(1000, 800)

        # Apply stylesheet
        self.setStyleSheet(stylesheet_global_page())

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = Stack(orientation="vertical")
        central_widget.setLayout(main_layout.layout)

        container = Container(padding=20)
        main_layout.add_item(container)

        # Demo sections
        self._create_progress_demos(container)
        self._create_modal_demo(container)
        self._create_indeterminate_demo(container)
        self._create_progress_group_demo(container)

    def _create_progress_demos(self, container):
        """Demo: Different progress bar styles"""
        # Initialize progress bars list FIRST
        self.progress_bars = []

        card = Card(title="Progress Bar Styles")

        # Linear progress
        card.add_body_widget(
            self._create_progress_section("Linear Progress", "linear", "primary", 75)
        )

        # Striped progress
        card.add_body_widget(
            self._create_progress_section("Striped Progress", "striped", "success", 60)
        )

        # Animated striped
        card.add_body_widget(
            self._create_progress_section("Animated Stripes", "animated", "info", 45)
        )

        # Gradient progress
        card.add_body_widget(
            self._create_progress_section(
                "Gradient Progress", "gradient", "warning", 80
            )
        )

        # Circular progress
        from PySide6.QtWidgets import QLabel
        from PySide6.QtCore import Qt

        label = QLabel("Circular Progress")
        label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        card.add_body_widget(label)

        circular = ProgressBar(style="circular", variant="primary", show_label=False)
        circular.set_value(65)
        card.add_body_widget(circular)

        # Animate button
        animate_btn = Button("Animate All Progress Bars", variant="primary")
        animate_btn.clicked.connect(self._animate_all_progress)
        card.add_footer_widget(animate_btn)

        container.add_widget(card)

    def _create_progress_section(self, title, style, variant, value):
        """Create a progress bar section"""
        from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(5)

        label = QLabel(title)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        progress = ProgressBar(style=style, variant=variant, show_label=True)
        progress.set_value(value)
        layout.addWidget(progress)

        self.progress_bars.append(progress)

        return widget

    def _create_modal_demo(self, container):
        """Demo: Modal dialogs"""
        card = Card(title="Modal Dialogs")

        from PySide6.QtWidgets import QLabel

        label = QLabel("Click buttons to show different modal types:")
        card.add_body_widget(label)

        row = Row(spacing=10)

        # Confirmation modal
        btn_confirm = Button("Confirmation Modal", variant="primary")
        btn_confirm.clicked.connect(self._show_confirmation_modal)
        row.add_column(btn_confirm)

        # Info modal
        btn_info = Button("Info Modal", variant="info")
        btn_info.clicked.connect(self._show_info_modal)
        row.add_column(btn_info)

        # Warning modal
        btn_warning = Button("Warning Modal", variant="warning")
        btn_warning.clicked.connect(self._show_warning_modal)
        row.add_column(btn_warning)

        row.add_stretch()
        card.add_body_widget(row)

        container.add_widget(card)

    def _create_indeterminate_demo(self, container):
        """Demo: Indeterminate progress (spinner)"""
        card = Card(title="Indeterminate Progress (Loading Spinner)")

        from PySide6.QtWidgets import QLabel

        label = QLabel("Loading spinner for indeterminate operations:")
        card.add_body_widget(label)

        # Spinner
        self.spinner = IndeterminateProgress(style="spinner", size=60)
        card.add_body_widget(self.spinner)

        # Control buttons
        row = Row(spacing=10)

        start_btn = Button("Start Loading", variant="success")
        start_btn.clicked.connect(self.spinner.start)
        row.add_column(start_btn)

        stop_btn = Button("Stop Loading", variant="danger")
        stop_btn.clicked.connect(self.spinner.stop)
        row.add_column(stop_btn)

        row.add_stretch()
        card.add_body_widget(row)

        container.add_widget(card)

    def _create_progress_group_demo(self, container):
        """Demo: Progress group (multiple progress bars)"""
        card = Card(title="Progress Group (Multiple Tasks)")

        from PySide6.QtWidgets import QLabel

        label = QLabel("Track multiple tasks with progress group:")
        card.add_body_widget(label)

        # Progress group
        self.progress_group = ProgressGroup()
        self.progress_group.add_progress(
            "Downloading files", 75, variant="info", style="linear"
        )
        self.progress_group.add_progress(
            "Processing data", 50, variant="primary", style="gradient"
        )
        self.progress_group.add_progress(
            "Uploading results", 25, variant="success", style="striped"
        )

        card.add_body_widget(self.progress_group)

        # Update button
        update_btn = Button("Simulate Progress", variant="primary")
        update_btn.clicked.connect(self._simulate_group_progress)
        card.add_footer_widget(update_btn)

        container.add_widget(card)

    def _animate_all_progress(self):
        """Animate all progress bars"""
        import random

        for progress in self.progress_bars:
            target = random.randint(20, 100)
            progress.animate_to(target, duration=1500)

    def _simulate_group_progress(self):
        """Simulate progress in group"""
        import random

        for i in range(3):
            value = random.randint(30, 100)
            self.progress_group.update_progress(i, value)

    def _show_confirmation_modal(self):
        """Show confirmation modal"""
        modal = Modal(title="Confirm Action", size="small", parent=self)
        modal.set_body("Are you sure you want to proceed with this action?")
        modal.add_footer_button("Cancel", variant="secondary")
        modal.add_footer_button(
            "Confirm", variant="primary", callback=lambda: print("Confirmed!")
        )
        modal.exec()

    def _show_info_modal(self):
        """Show info modal"""
        modal = Modal(title="Information", size="medium", parent=self)
        modal.set_body(
            "This is an informational modal.\n\n"
            "You can display important information to users here.\n"
            "Modals are great for focused interactions."
        )
        modal.add_footer_button("Got it!", variant="info")
        modal.exec()

    def _show_warning_modal(self):
        """Show warning modal"""
        modal = Modal(title="⚠️ Warning", size="small", parent=self)
        modal.set_body(
            "This action cannot be undone!\n\n"
            "Please make sure you have backed up your data."
        )
        modal.add_footer_button("Cancel", variant="secondary")
        modal.add_footer_button(
            "Proceed Anyway",
            variant="danger",
            callback=lambda: print("Warning accepted!"),
        )
        modal.exec()


def main():
    """Run the demo"""
    print("=" * 60)
    print("Progress Bars, Modals & Toast Demo")
    print("=" * 60)
    print("\nFeatures:")
    print("  ✓ 5 Progress bar styles (linear, striped, animated, gradient, circular)")
    print("  ✓ Indeterminate progress (spinner)")
    print("  ✓ Progress groups (multiple tasks)")
    print("  ✓ Modal dialogs (confirmation, info, warning)")
    print("\nInteract with the UI to test all features!")
    print("=" * 60)

    app = QApplication(sys.argv)
    window = ProgressDemo()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
