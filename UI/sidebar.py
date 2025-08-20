from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QIcon
from UI.main_content import Pages
from UI.resources.animation.animation_manager import WidthAnimator
from UI.settings.General.Language import language_config
from PySide6.QtCore import Slot, QEasingCurve

class Sidebar(QWidget):
    
    EXPANDED_WIDTH = 180
    COLLAPSED_WIDTH = 70
    ANIMATION_DURATION = 250
    ANIMATION_CURVE = QEasingCurve.Type.InOutQuad
    
    def __init__(self, toggle_callback, switch_page_callback):
        super().__init__()
        self.expanded_width = 180
        self.collapsed_width = 70
        self.sidebar_expanded = True
        self.toggle_callback = toggle_callback
        self.switch_page_callback = switch_page_callback
        
        self.width_animator = WidthAnimator(self) 

        self.setStyleSheet(
            """
            QWidget {
                background-color: #e0e0e0;
                color: #333;
            }
        """
        )

        # Layout sidebar
        self.sidebar_layout = QVBoxLayout()
        self.setLayout(self.sidebar_layout)

        # Tombol toggle sidebar
        self.toggle_button = QPushButton("☰")
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                background-color: #c8d6e5;
                border: none;
                color: #333;
                font-size: 18px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #b2bec3;
            }
        """
        )
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addWidget(self.toggle_button)

        # --- MEMBUAT TOMBOL NAVIGASI SECARA DINAMIS DARI 'Pages' ---
        self.side_buttons = []
        current_index = 0 # Sangat penting untuk menjaga indeks yang benar

        # Buat tombol navigasi utama
        for text, icon_path, _ in Pages.MAIN_PAGES: # kelas widget tidak diperlukan di sini
            btn = self.create_nav_button(text, icon_path, current_index)
            self.sidebar_layout.addWidget(btn)
            self.side_buttons.append(btn)
            current_index += 1

        self.sidebar_layout.addStretch() # Pemisah visual

        # Buat tombol navigasi footer (contoh: Settings)
        for text, icon_path, _ in Pages.FOOTER_PAGES:
            btn = self.create_nav_button(text, icon_path, current_index)
            self.sidebar_layout.addWidget(btn)
            self.side_buttons.append(btn)
            current_index += 1
        
        # Atur ukuran awal sidebar
        self.setFixedWidth(self.expanded_width)

    def create_nav_button(self, text, icon_path, index):
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setIcon(QIcon(icon_path))
        btn.setCheckable(True)
        btn.setStyleSheet(
            """
            QPushButton {
                qproperty-iconSize: 24px;
                text-align: left;
                padding: 10px;
                border: none;
                color: #333;
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #dfe6e9;
            }
            QPushButton:checked {
                background-color: #74b9ff;
                color: white;
                font-weight: bold;
            }
        """
        )
         # Gunakan lambda yang benar untuk index
        btn.clicked.connect(lambda checked=False, idx=index: self._handle_nav_click(idx))
        btn.setProperty("default_text", text) # Simpan teks asli sebagai properti
        return btn
    
    @Slot(int)
    def _handle_nav_click(self, index):
        """Menangani klik tombol navigasi."""
        for i, btn in enumerate(self.side_buttons):
            btn.setChecked(i == index)
        self.switch_page_callback(index) # Panggil callback dengan index


    def toggle_sidebar(self):
        """Memulai animasi expand/collapse sidebar menggunakan WidthAnimator."""
        target_expanded = not self.sidebar_expanded
        end_width = self.expanded_width if target_expanded else self.collapsed_width

        # Update state internal & tampilan teks/ikon SEGERA
        self.sidebar_expanded = target_expanded
        self.toggle_button.setText("☰" if target_expanded else "➡")
        for btn in self.side_buttons:
             default_text = btn.property("default_text")
             btn.setText(default_text if target_expanded else "")

        # Panggil callback eksternal
        self.toggle_callback()

        # --- Gunakan WidthAnimator ---
        self.width_animator.animate_width(
            target_widget=self, # Target adalah sidebar itu sendiri
            end_width=end_width,
            duration=self.ANIMATION_DURATION, # Gunakan konstanta
            curve=self.ANIMATION_CURVE      # Gunakan konstanta
        )