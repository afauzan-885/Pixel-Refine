import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QSplitter
from PyQt6.QtCore import Qt

# Impor kelas Sidebar dan MainContent dari file spesifik
from app.views.sidebar import Sidebar
from app.views.main_content import MainContent


class PixelRefineApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Refine - Modular Layout")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()

    def initUI(self):
        # Main container
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Sidebar dan Main Content
        self.sidebar = Sidebar()  # Menggunakan kelas Sidebar
        self.main_content = MainContent()  # Menggunakan kelas MainContent

        # Splitter untuk Sidebar dan Main Content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.main_content)

        # Adjust initial sizes of sidebar and content
        splitter.setSizes([150, 750])
        main_layout.addWidget(splitter)

        self.setCentralWidget(main_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PixelRefineApp()
    window.show()
    sys.exit(app.exec())
