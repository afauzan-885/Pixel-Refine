import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
from app.views.sidebar import Sidebar
from app.views.main_content import MainContent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi dengan Sidebar Responsif")
        self.setGeometry(100, 100, 1200, 600)

        # Sidebar
        self.sidebar = Sidebar(self.toggle_sidebar, self.switch_page)

        # Main Content
        self.main_content = MainContent()

        # Layout utama
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.main_content)
        self.main_layout.setStretch(0, 1)  # Sidebar width
        self.main_layout.setStretch(1, 4)  # Main content width

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Secara otomatis buka halaman pertama
        self.switch_page(0)

    def switch_page(self, index):
        """Switch pages in the main content."""
        self.main_content.setCurrentIndex(index)
        for i, btn in enumerate(self.sidebar.nav_buttons):
            btn.setChecked(i == index)

    def toggle_sidebar(self):
        """Handle additional actions when toggling the sidebar."""
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
