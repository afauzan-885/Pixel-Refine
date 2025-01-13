from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class BatchPageLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Tampilkan pesan sementara
        self.label = QLabel("Halo, ini adalah halaman batch")
        self.layout.addWidget(self.label)
