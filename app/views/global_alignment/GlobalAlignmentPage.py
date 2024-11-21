from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QListWidget,
    QFrame,
)
from PyQt6.QtCore import Qt


class GlobalAlignmentPage(QWidget):
    def __init__(self):
        super().__init__()

        # Layout utama
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Tambahkan top bar dan panel konten ke layout utama
        main_layout.addWidget(self.create_top_bar())
        main_layout.addLayout(self.create_content_layout())

        self.setLayout(main_layout)

    def create_top_bar(self) -> QLabel:
        """Membuat top bar dengan teks Global Alignment."""
        top_bar = QLabel("Global Alignment")
        top_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_bar.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 10px;
            """
        )
        return top_bar

    def create_content_layout(self) -> QHBoxLayout:
        """Membuat layout untuk panel kiri dan kanan."""
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Tambahkan panel kiri dan kanan ke layout
        content_layout.addLayout(self.create_left_panel(), 2)
        content_layout.addLayout(self.create_right_panel(), 1)

        return content_layout

    def create_left_panel(self) -> QVBoxLayout:
        """Membuat panel kiri dengan elemen Preview Image, Parameter, dan Progress Bar."""
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        left_panel.addWidget(self.create_preview_frame())
        left_panel.addWidget(self.create_parameter_frame())
        left_panel.addWidget(self.create_progress_bar())

        return left_panel

    def create_preview_frame(self) -> QFrame:
        """Membuat frame untuk Preview Image."""
        frame = QFrame()
        frame.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        label = QLabel("Preview Image")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")

        layout.addWidget(label)
        frame.setLayout(layout)

        return frame

    def create_parameter_frame(self) -> QFrame:
        """Membuat frame untuk Parameter Alignment."""
        frame = QFrame()
        frame.setStyleSheet("background-color: #FFFDF7;")

        layout = QVBoxLayout()
        label = QLabel("Parameter Alignment")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800;")

        layout.addWidget(label)
        frame.setLayout(layout)

        return frame

    def create_progress_bar(self) -> QProgressBar:
        """Membuat Progress Bar."""
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                background: #eee;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
            """
        )
        progress_bar.setValue(50)

        return progress_bar

    def create_right_panel(self) -> QVBoxLayout:
        """Membuat panel kanan dengan List Image dan tombol."""
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        right_panel.addWidget(self.create_list_widget())
        right_panel.addLayout(self.create_button_layout())

        return right_panel

    def create_list_widget(self) -> QListWidget:
        """Membuat widget untuk List Image."""
        list_widget = QListWidget()
        list_widget.setStyleSheet("background-color: #E9EFF3; padding: 5px; border: 2px solid #D1D9DF;")
        return list_widget

    def create_button_layout(self) -> QHBoxLayout:
        """Membuat layout untuk tombol Align dan Next."""
        button_layout = QHBoxLayout()

        align_button = self.create_button("Align")
        next_button = self.create_button("Next")

        button_layout.addWidget(align_button)
        button_layout.addWidget(next_button)

        return button_layout

    def create_button(self, text: str) -> QPushButton:
        """Membuat tombol dengan gaya khusus."""
        button = QPushButton(text)
        button.setStyleSheet(
            """
            QPushButton {
                background-color: #3F51B5;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5C6BC0;
            }
            """
        )
        return button
