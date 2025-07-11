from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QTextEdit, 
                             QDialogButtonBox, QLabel, QStyle, QHBoxLayout)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class ScrollableErrorDialog(QDialog):
    """
    Sebuah dialog kustom untuk menampilkan pesan error yang panjang
    dengan area teks yang bisa di-scroll.
    """
    def __init__(self, title, intro_text, detailed_text, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        
        # --- Atur tata letak utama ---
        main_layout = QVBoxLayout(self)

        # --- Bagian Atas: Ikon dan Teks Pengantar ---
        top_layout = QHBoxLayout()
        
        # Tambahkan ikon warning standar
        icon_label = QLabel()
        warning_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        icon_label.setPixmap(warning_icon.pixmap(30, 30)) # Ukuran ikon
        top_layout.addWidget(icon_label)

        # Tambahkan teks pengantar
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True) # Agar teks tidak melebar jika panjang
        top_layout.addWidget(intro_label, 1) # Stretch factor 1
        
        main_layout.addLayout(top_layout)

        # --- Area Teks yang Bisa Di-scroll ---
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(detailed_text)
        self.text_edit.setReadOnly(True)  # Pengguna tidak bisa mengedit laporan
        
        # Set ukuran minimum agar tidak terlalu kecil saat pertama muncul
        self.text_edit.setMinimumHeight(150)
        self.text_edit.setMinimumWidth(450)
        
        main_layout.addWidget(self.text_edit)

        # --- Tombol OK ---
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept) # Menutup dialog saat OK ditekan
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)