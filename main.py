import math
import os
import sys
import time

# Impor semua modul PySide6 yang dibutuhkan
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget, 
                               QMessageBox, QSplashScreen, QLabel, 
                               QVBoxLayout, QWidget)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRectF

# Impor modul-modul dari proyek Anda
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.animation.animation_manager import StackedWidgetAnimator
from UI.resources.animation.fade import fade_in
from UI.sidebar import Sidebar
from UI.main_content import MainContent 
import config
from shutil import rmtree

class CircularProgress(QWidget):
    """
    Widget kustom untuk menampilkan progress bar berbentuk lingkaran.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.setMinimumSize(80, 80) # Ukuran minimum bisa lebih kecil

    def setValue(self, value: int):
        if 0 <= value <= 100:
            self._value = value
            self.update()

    def value(self) -> int:
        return self._value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        side = min(rect.width(), rect.height())
        draw_rect = QRectF(
            (rect.width() - side) / 2,
            (rect.height() - side) / 2,
            side,
            side
        )

        painter.setPen(Qt.PenStyle.NoPen)
        # Warna hitam dengan opasitas ~30% untuk menciptakan efek alas
        painter.setBrush(QColor(0, 0, 0, 0)) 
        painter.drawEllipse(draw_rect)
        
        num_dots = 12
        dot_radius = side * 0.04  
        circle_radius = side / 2 - dot_radius * 2

        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(num_dots):
            angle_rad = math.radians(i * (360 / num_dots) - 90) # -90 agar mulai dari atas
            center_x = draw_rect.center().x()
            center_y = draw_rect.center().y()
            x = center_x + circle_radius * math.cos(angle_rad)
            y = center_y + circle_radius * math.sin(angle_rad)
            painter.setBrush(QColor(255, 255, 255, 60)) # Warna abu-abu lebih redup
            painter.drawEllipse(x - dot_radius/2, y - dot_radius/2, dot_radius, dot_radius)

        # Gambar titik-titik progres
        num_active_dots = int(self._value / 100 * num_dots)
        painter.setBrush(QColor(255, 255, 255, 255))
        for i in range(num_active_dots):
            angle_rad = math.radians(i * (360 / num_dots) - 90) # -90 agar mulai dari atas
            center_x = draw_rect.center().x()
            center_y = draw_rect.center().y()
            x = center_x + circle_radius * math.cos(angle_rad)
            y = center_y + circle_radius * math.sin(angle_rad)
            painter.drawEllipse(x - dot_radius/2, y - dot_radius/2, dot_radius, dot_radius)

        # Gambar teks persentase
        font = QFont("Segoe UI", int(side * 0.18), QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        painter.drawText(draw_rect, Qt.AlignmentFlag.AlignCenter, f"{self._value}%")

class SplashScreen(QSplashScreen):
    """
    Splash screen kustom yang menampilkan gambar, indikator progres melingkar,
    dan label status.
    """
    # DIUBAH: Tambahkan parameter 'version_string' di konstruktor
    def __init__(self, pixmap: QPixmap, version_string: str, flags=Qt.WindowType.WindowStaysOnTopHint):
        super().__init__(pixmap, flags)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 15)
        
        main_layout.addStretch()

        # Widget progres melingkar kustom
        self.progress_indicator = CircularProgress(self)
        self.progress_indicator.setFixedSize(120, 120) 
        main_layout.addWidget(self.progress_indicator, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label untuk "LOADING..."
        self.status_label = QLabel("L O A D I N G . . .", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white; 
            font-size: 14px;
            font-weight: normal;
            letter-spacing: 4px;
            background-color: transparent;
            padding-top: 5px;
        """)
        main_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label untuk pesan detail
        self.detail_label = QLabel("", self)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet("color: #DDDDDD; font-size: 11px; background-color: transparent;")
        main_layout.addWidget(self.detail_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # BARU: Spacer kecil untuk memberi jarak ke nomor versi
        main_layout.addSpacing(10)

        # BARU: Label untuk nomor versi
        self.version_label = QLabel(version_string, self)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Dibuat lebih kecil dan redup agar elegan dan tidak mengganggu
        self.version_label.setStyleSheet("""
            color: #AAAAAA; 
            font-size: 9px; 
            background-color: transparent;
        """)
        main_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_status(self, message: str, value: int):
        self.progress_indicator.setValue(value)
        self.detail_label.setText(message) 
        QApplication.processEvents()
               
class PixelRefineMain(QMainWindow):
    def __init__(self):
        """
        Konstruktor __init__ dibuat sangat ringan.
        Hanya memanggil parent dan menginisialisasi atribut.
        """
        super().__init__()
        self.main_content = None
        self.sidebar = None
        self.database_manager = None
        self.main_content_animator = None

    def setup_ui_and_logic(self, splash: SplashScreen):
        """
        Metode ini berisi semua pekerjaan berat untuk membangun UI dan logika,
        yang sebelumnya ada di __init__.
        """
        # Setiap langkah "berat" diikuti oleh pembaruan splash screen.
        
        splash.update_status("Loading database...", 10)
        db_path = "pixel_refine_database.db" 
        self.database_manager = DatabaseManager(db_path)
        self.database_manager.create_database()
        # time.sleep(1.3) # HAPUS PADA VERSI PRODUKSI

        splash.update_status("Initializing animations...", 25)
        self.main_content_animator = StackedWidgetAnimator(self)
        # time.sleep(1.3) # HAPUS PADA VERSI PRODUKSI

        splash.update_status("Setting up main window...", 40)
        self.setWindowIcon(QIcon("UI/resources/image/Logo_Pixel_Refine.png"))
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION}")
        self.setMinimumSize(1200, 600)
        # time.sleep(1.2) # HAPUS PADA VERSI PRODUKSI

        splash.update_status("Preparing temporary folders...", 55)
        self.database_folder = "database" 
        self.align_folder = os.path.join(self.database_folder, "align")
        self.stack_folder = os.path.join(self.database_folder, "stack")
        self.create_folders_if_needed()
        # time.sleep(1.2) # HAPUS PADA VERSI PRODUKSI

        splash.update_status("Loading UI components...", 70)
        self.main_content = MainContent(self.database_manager) 
        self.sidebar = Sidebar(self.toggle_sidebar, self.switch_page)
        # time.sleep(0.5) # HAPUS PADA VERSI PRODUKSI

        splash.update_status("Assembling UI layout...", 90)
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.main_content)
        self.main_layout.setStretch(0, 1) 
        self.main_layout.setStretch(1, 4) 
        self.main_layout.setContentsMargins(0, 0, 0, 0) 
        self.main_layout.setSpacing(0)
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        # time.sleep(0.3) # HAPUS PADA VERSI PRODUKSI
       
        splash.update_status("Finalizing...", 100)
        self.switch_page(0)
        # time.sleep(0.3) # HAPUS PADA VERSI PRODUKSI

    def create_folders_if_needed(self):
        try:
            os.makedirs(self.database_folder, exist_ok=True) 
            os.makedirs(self.align_folder, exist_ok=True)
            os.makedirs(self.stack_folder, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "Error", f"An error occurred while creating folders: {e}. The application will now close.")
            sys.exit(1)

    def closeEvent(self, event):
        try:
            if os.path.exists(self.align_folder):
                for item in os.listdir(self.align_folder):
                    item_path = os.path.join(self.align_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path): os.unlink(item_path) 
                    elif os.path.isdir(item_path): rmtree(item_path) 
            if os.path.exists(self.stack_folder):
                for item in os.listdir(self.stack_folder):
                    item_path = os.path.join(self.stack_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path): os.unlink(item_path)
                    elif os.path.isdir(item_path): rmtree(item_path)  
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while deleting folder contents: {e}")
        finally:
            event.accept()

    def switch_page(self, index):
        if self.main_content is None: return
        if not (0 <= index < self.main_content.count()): return
        if index == self.main_content.currentIndex() and self.main_content.widget(index) is not None:
             if self.sidebar: 
                 for i, btn in enumerate(self.sidebar.side_buttons): btn.setChecked(i == index)
             return
        if self.sidebar:
            for i, btn in enumerate(self.sidebar.side_buttons): btn.setChecked(i == index)
        fade_in(self.main_content_animator, self.main_content, index, duration=250)

    def toggle_sidebar(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # LANGKAH 1: Siapkan dan tampilkan Custom Splash Screen
    screen_geometry = app.primaryScreen().geometry()
    original_pixmap = QPixmap("UI/resources/image/Logo_Pixel_Refine.png")
    
    splash_width = int(screen_geometry.width() * 0.25)
    scaled_pixmap = original_pixmap.scaledToWidth(splash_width, Qt.TransformationMode.SmoothTransformation)
    
    version_text = f"Version {config.APP_VERSION}"
    splash = SplashScreen(scaled_pixmap, version_text)
    
    splash.show()
    app.processEvents()
    
    window = PixelRefineMain()
    
    window.setup_ui_and_logic(splash)

    window.show()
    splash.finish(window)

    sys.exit(app.exec())