from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import pyqtSignal, QObject

class LanguageManager(QObject):
    language_changed = pyqtSignal()  # Signal yang akan diberitahukan jika bahasa berubah

    def __init__(self):
        super().__init__()  # Memanggil konstruktor QObject
        self.translations = {
            "en": {
                "under_development": "{page_name} menu under development",
            },
            "id": {
                "under_development": "Menu {page_name} sedang dalam pengembangan",
            }
        }
        self.current_language = "id"  # Default to Indonesian

    def change_language(self, language_code):
        """Fungsi untuk mengubah bahasa aplikasi"""
        if language_code in self.translations:
            self.current_language = language_code
            self.language_changed.emit()  # Emit signal jika bahasa berubah

    def update_translations(self, widget):
        """Memperbarui terjemahan untuk semua elemen teks"""
        if isinstance(widget, QWidget):
            labels = widget.findChildren(QLabel)
            for label in labels:
                # Update label berdasarkan teks yang sesuai dalam bahasa yang dipilih
                label.setText(self.translations[self.current_language].get(label.text(), label.text()))
