from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLayout
from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout
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
            
class FlowLayout(QLayout):
    """
    Layout kustom Qt yang membungkus (wraps) item dari atas ke bawah,
    lalu memulai kolom baru jika ruang vertikal habis.
    """
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        """Inti dari layout: mengatur posisi semua item."""
        x = rect.x()
        y = rect.y()
        line_height = 0
        space_x = self.spacing()
        space_y = self.spacing()

        # Dapatkan lebar kolom saat ini (maksimum dari semua item)
        current_col_width = 0
        for item in self.itemList:
            current_col_width = max(current_col_width, item.sizeHint().width())

        for item in self.itemList:
            wid = item.widget()
            next_x = x + current_col_width + space_x

            # Jika item berikutnya akan keluar dari batas bawah
            if y + item.sizeHint().height() > rect.bottom() and line_height > 0:
                # Pindah ke kolom berikutnya
                y = rect.y()
                x = next_x
                next_x = x + current_col_width + space_x
                line_height = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            y += item.sizeHint().height() + space_y
            line_height = max(line_height, item.sizeHint().height())

        return y