from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QProgressBar,
    QPushButton,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sqlite3


class GlobalAlignmentPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Global Alignment")
        self.setStyleSheet(
            """
            /* Desain untuk tombol */
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }

            /* Desain untuk QLabel preview image */
            QLabel {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                color: #555;
                padding: 8px;
            }

            /* Desain untuk QListWidget (panel daftar gambar) */
            QListWidget {
                background-color: #f3f3f3;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #e7e7e7;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }

            /* Desain untuk QGroupBox (panel parameter alignment) */
            QGroupBox {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-weight: bold;
            }

            /* Desain untuk QProgressBar */
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f3f3f3;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """
        )  # Stylesheet yang lengkap dan benar

        # Layout utama (Horizontal)
        main_layout = QHBoxLayout()

        # Panel kiri: untuk gambar dan parameter alignment
        left_panel = QVBoxLayout()

        # Panel untuk preview gambar
        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(700, 350)
        left_panel.addWidget(self.image_label, stretch=3)

        # Panel untuk parameter alignment
        self.param_group_box = QGroupBox("Parameter Alignment")
        param_layout = QVBoxLayout()
        self.param_group_box.setMinimumHeight(150)
        self.param_group_box.setLayout(param_layout)

        param_layout.addStretch(2)  # Menambahkan stretch agar panel alignment mengisi ruang vertikal
        left_panel.addWidget(
            self.param_group_box, stretch=4
        )  # Menambahkan stretch untuk membuatnya lebih besar

        left_panel.addStretch(1)
        main_layout.addLayout(
        left_panel, stretch=4
        )  # Mengubah stretch untuk panel kiri

        # Panel kanan: untuk daftar gambar + tombol + progress bar
        right_panel = QVBoxLayout()

        # Daftar gambar
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.display_image)
        right_panel.addWidget(
            self.image_list, stretch=1
        )

        # Progress bar dan tombol
        progress_layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        # Tombol Align dan Next
        button_layout = QHBoxLayout()
        self.align_button = QPushButton("Align")
        self.next_button = QPushButton("Next (Local Alignment)")

        # Menambahkan style untuk tombol
        self.align_button.setStyleSheet(
            """ 
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """
        )

        self.next_button.setStyleSheet(
            """ 
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #cc8400;
            }
            QPushButton:pressed {
                background-color: #995c00;
            }
        """
        )

        button_layout.addWidget(self.align_button)
        button_layout.addWidget(self.next_button)
        progress_layout.addLayout(button_layout)

        # Menambahkan progress bar dan tombol ke dalam panel kanan
        right_panel.addLayout(progress_layout)

        main_layout.addLayout(
            right_panel, stretch=1
        )  # Mengubah stretch untuk panel kanan

        # Memuat daftar gambar dari database
        self.load_images_from_db()

        self.setLayout(main_layout)

    def load_images_from_db(self):
        conn = sqlite3.connect("image_paths.db")
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM images")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            item = QListWidgetItem(row[0])
            self.image_list.addItem(item)

    def display_image(self, item):
        image_path = item.text()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.image_label.setText("Failed to load image")
