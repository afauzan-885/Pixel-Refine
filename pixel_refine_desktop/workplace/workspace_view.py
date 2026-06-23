"""
WorkspaceView - Base Workspace Container View
===============================================
Container utama untuk workspace pattern. Mengelola QStackedWidget untuk
switching antar halaman dengan animasi dan toast notification.

Digunakan oleh modul-modul seperti enhance_stack dan 3d_reconstruction
sebagai base container yang sama.

Layout Structure:
┌─────────────────────────────────┐
│  (opsional TopBar)              │
├─────────────────────────────────┤
│                                 │
│  QStackedWidget                 │
│  ┌───────────────────────────┐  │
│  │  Page 0: Single/PageView  │  │
│  │  Page 1: Batch/BulkView   │  │
│  └───────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Signal

from resources.animations.animation_manager import (
    SlideDirection,
    StackedWidgetAnimator,
)
from resources.animations.slide import slide
from resources.animations.fade import fade_in
from resources.animations.toast.toast_manager import ToastManager


class WorkspaceView(QWidget):
    """
    Base workspace view container.
    Menyediakan QStackedWidget dengan animation dan toast support.

    Subclass harus mengimplementasikan:
    - _create_pages(): Membuat halaman-halaman dan menambahkan ke stacked_widget
    - _connect_page_signals(): Menghubungkan sinyal antar halaman
    """

    page_changed = Signal(int)  # Forward global navigation

    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Animation and toast managers
        self.animator = StackedWidgetAnimator(self)
        self.toast_manager = ToastManager(self)

        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget, 1)

        # Subclass creates pages
        self._create_pages()

        # Set initial page
        self._set_initial_page()

    def connect_signals(self):
        """Connect signals between pages. Subclass can override."""
        self._connect_page_signals()

    def _create_pages(self):
        """
        Membuat halaman-halaman dan menambahkan ke stacked_widget.
        HARUS diimplementasikan oleh subclass.

        Contoh implementasi:
            self.page_a = PageAView(self.db_path, self)
            self.stacked_widget.addWidget(self.page_a)

            self.page_b = PageBView(self.db_path, self)
            self.stacked_widget.addWidget(self.page_b)
        """
        raise NotImplementedError("Subclass harus mengimplementasikan _create_pages()")

    def _connect_page_signals(self):
        """
        Menghubungkan sinyal antar halaman.
        Subclass bisa override untuk kustomisasi.
        """
        pass

    def _set_initial_page(self):
        """Set halaman awal. Subclass bisa override."""
        if self.stacked_widget.count() > 0:
            self.stacked_widget.setCurrentIndex(0)

    def switch_page(self, target_widget, direction=SlideDirection.LEFT, duration=400):
        """
        Switch ke halaman tertentu dengan animasi slide.

        Args:
            target_widget: Widget tujuan di stacked_widget
            direction: Arah slide (LEFT, RIGHT, UP, DOWN)
            duration: Durasi animasi dalam ms
        """
        slide(
            self.animator,
            self.stacked_widget,
            target_widget,
            direction,
            duration=duration,
        )

    def fade_to_page(self, target_widget, duration=300):
        """
        Switch ke halaman dengan animasi fade.

        Args:
            target_widget: Widget tujuan
            duration: Durasi animasi dalam ms
        """
        fade_in(self.animator, target_widget, self.stacked_widget, duration=duration)

    def show_toast(self, message, duration=3000):
        """Show toast notification."""
        self.toast_manager.show_message(message, duration=duration)

    def show_progress_toast(self, message, category="default"):
        """Show progress toast notification."""
        self.toast_manager.show_progress(message, category=category)
