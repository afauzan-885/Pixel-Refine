from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLayout
from PySide6.QtCore import Qt

class DynamicFlowPanel(QWidget):
    """
    Sebuah panel yang secara dinamis mengubah layout anaknya dari
    horizontal menjadi vertikal jika tidak ada cukup ruang.
    """
    def __init__(self, horizontal_threshold: int = 250, parent=None):
        super().__init__(parent)
        self.horizontal_threshold = horizontal_threshold
        
        # Buat kedua layout, tetapi jangan terapkan dulu
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self._widgets = []

    def addWidget(self, widget: QWidget):
        """Menambahkan widget ke dalam manajemen panel ini."""
        self._widgets.append(widget)

    def _reapply_layout(self, new_layout: QLayout):
        """Menghapus layout lama dan menerapkan yang baru."""
        # Hapus layout yang ada saat ini
        if self.layout() is not None:
            # Pindahkan semua item dari layout lama agar tidak terhapus
            while item := self.layout().takeAt(0):
                if item.widget():
                    item.widget().setParent(None)
            
            # Hapus layout lama itu sendiri
            # Ini penting untuk mencegah Qt bingung
            QWidget().setLayout(self.layout())

        # Tambahkan kembali semua widget ke layout baru
        for widget in self._widgets:
            new_layout.addWidget(widget)
        
        self.setLayout(new_layout)

    def resizeEvent(self, event):
        """Dipanggil setiap kali ukuran widget berubah."""
        super().resizeEvent(event)

        current_layout = self.layout()
        width = self.width()

        # Tentukan layout mana yang seharusnya aktif
        if width < self.horizontal_threshold and current_layout != self.v_layout:
            # Ruang sempit, butuh layout vertikal
            self._reapply_layout(self.v_layout)
        elif width >= self.horizontal_threshold and current_layout != self.h_layout:
            # Ruang lebar, bisa pakai layout horizontal
            self._reapply_layout(self.h_layout)