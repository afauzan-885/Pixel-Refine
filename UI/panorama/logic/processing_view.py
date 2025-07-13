# processing_view.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QApplication, QFrame

from UI.resources.animation.loading.modern_progress_bar import ModernProgressBar

class ProcessingView(QFrame):
    """
    Widget kontainer adaptif yang menskalakan kontennya (judul, progress bar)
    berdasarkan ukurannya sendiri.
    """
    # --- Parameter Konfigurasi untuk Skala Adaptif ---
    BASE_WIDTH = 600.0  # Lebar ideal sebagai acuan (gunakan float untuk presisi)
    BASE_FONT_SIZE = 20
    BASE_PROGRESS_BAR_HEIGHT = 15
    BASE_MARGIN_X = 40
    BASE_MARGIN_Y = 30
    
    MIN_FONT_SIZE = 12
    MIN_PROGRESS_BAR_HEIGHT = 8
    MIN_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("processingView")
        self.setStyleSheet("#processingView { background-color: transparent; border: none; }")

        # Simpan layout sebagai anggota kelas agar bisa diakses nanti
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addStretch()

        self.title_label = QLabel("Loading...", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Hapus font-size dari stylesheet, kita akan mengaturnya secara dinamis
        self.title_label.setStyleSheet("""
            color: "#4C4E54"; 
            font-family: "Segoe UI Light", "Helvetica Neue", "Arial", sans-serif;
            background-color: transparent;
        """)
        self.main_layout.addWidget(self.title_label)
        
        self.main_layout.addSpacing(5) # Spasi ini bisa dibuat adaptif juga jika perlu

        self.progress_bar = ModernProgressBar(self)
        self.main_layout.addWidget(self.progress_bar)
        
        self.main_layout.addStretch()
        
        # Atur gaya awal
        self._update_adaptive_styles()

    def update_progress(self, title: str, value: int):
        """Memperbarui judul, persentase, dan bar progress."""
        # Tampilkan persentase hanya jika lebih besar dari 0 untuk tampilan awal yang lebih bersih
        if value > 0:
            self.title_label.setText(f"{title} {value}%")
        else:
            self.title_label.setText(title)
            
        self.progress_bar.setValue(value)
        # QApplication.processEvents() # Hati-hati dengan ini, bisa menyebabkan masalah re-entrancy

    def _update_adaptive_styles(self):
        """
        Menghitung ulang dan menerapkan semua ukuran adaptif (font, tinggi bar, margin).
        """
        current_width = self.width()
        if current_width <= 0: return

        # Hitung faktor skala, batasi agar tidak terlalu besar (misal max 1.2x)
        scale_factor = min(1.2, current_width / self.BASE_WIDTH)

        # Hitung ukuran font baru dan batasi
        new_font_size = int(self.BASE_FONT_SIZE * scale_factor)
        final_font_size = max(self.MIN_FONT_SIZE, new_font_size)
        
        # Hitung tinggi progress bar baru dan batasi
        new_bar_height = int(self.BASE_PROGRESS_BAR_HEIGHT * scale_factor)
        final_bar_height = max(self.MIN_PROGRESS_BAR_HEIGHT, new_bar_height)
        
        # Hitung margin baru dan batasi
        new_margin_x = int(self.BASE_MARGIN_X * scale_factor)
        final_margin_x = max(self.MIN_MARGIN, new_margin_x)
        new_margin_y = int(self.BASE_MARGIN_Y * scale_factor)
        final_margin_y = max(self.MIN_MARGIN, new_margin_y)

        # Terapkan perubahan
        font = self.title_label.font()
        font.setPixelSize(final_font_size)
        self.title_label.setFont(font)
        
        self.progress_bar.setFixedHeight(final_bar_height)
        
        self.main_layout.setContentsMargins(
            final_margin_x, final_margin_y, final_margin_x, final_margin_y
        )
        
    def showEvent(self, event):
        """Panggil pembaruan gaya saat widget pertama kali ditampilkan."""
        super().showEvent(event)
        self._update_adaptive_styles()

    def resizeEvent(self, event):
        """Panggil pembaruan gaya setiap kali ukuran widget berubah."""
        super().resizeEvent(event)
        self._update_adaptive_styles()