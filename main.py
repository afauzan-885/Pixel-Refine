import os
import sys

# Impor semua modul PySide6 yang dibutuhkan
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget, 
                               QMessageBox, QSplashScreen, QLabel, 
                               QVBoxLayout, QWidget)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

# Impor modul-modul dari proyek Anda
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.animation.animation_manager import StackedWidgetAnimator
from UI.resources.animation.fade import fade_in
from UI.resources.animation.loading.circular_progress import CircularProgress
from UI.sidebar import Sidebar
from UI.main_content import MainContent 
import config
from shutil import rmtree

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

    def setup_ui_and_logic(self, splash: 'SplashScreen'):
        splash.update_status("Loading database...", 10)
        db_path = "pixel_refine_database.db" 
        self.database_manager = DatabaseManager(db_path)
        self.database_manager.create_database()

        splash.update_status("Initializing animations...", 25)
        self.main_content_animator = StackedWidgetAnimator(self)

        splash.update_status("Setting up main window...", 40)
        self.setWindowIcon(QIcon("UI/resources/image/Logo_Pixel_Refine.png"))
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION}")
        
        # <<< PERUBAHAN DI SINI >>>
        self._set_adaptive_window_size()

        splash.update_status("Preparing temporary folders...", 55)
        self.database_folder = "database" 
        self.align_folder = os.path.join(self.database_folder, "align")
        self.stack_folder = os.path.join(self.database_folder, "stack")
        self.align_stitch_cache_folder = os.path.join(self.database_folder, "cache", "align_stitch")
        
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
        
    def _set_adaptive_window_size(self):
        """
        Mengatur ukuran awal dan UKURAN MINIMUM jendela secara adaptif,
        sehingga tidak bisa di-resize lebih kecil dari persentase layar yang ditentukan.
        """
        # --- Parameter Konfigurasi ---
        # Aspek rasio yang diinginkan untuk aplikasi Anda (lebar / tinggi)
        APP_ASPECT_RATIO = 1200 / 600  # Hasilnya 2.0

        # Persentase layar yang akan menjadi UKURAN MINIMUM
        MIN_SCREEN_RATIO = 0.76

        # Ukuran minimum absolut (fallback untuk layar resolusi sangat rendah)
        ABS_MIN_WIDTH = 800
        ABS_MIN_HEIGHT = 400

        # 1. Dapatkan geometri layar yang tersedia
        screen_geom = QApplication.primaryScreen().availableGeometry()
        
        # 2. Tentukan area minimum di layar
        min_safe_width = int(screen_geom.width() * MIN_SCREEN_RATIO)
        min_safe_height = int(screen_geom.height() * MIN_SCREEN_RATIO)
        
        # 3. Hitung aspek rasio dari area minimum di layar
        screen_aspect_ratio = min_safe_width / min_safe_height

        # --- Logika "Fit Inside a Box" untuk Menentukan Ukuran Minimum Adaptif ---
        if screen_aspect_ratio > APP_ASPECT_RATIO:
            # Layar lebih LEBAR daripada aplikasi -> Tinggi menjadi pembatas
            adaptive_min_height = min_safe_height
            adaptive_min_width = int(adaptive_min_height * APP_ASPECT_RATIO)
        else:
            # Layar lebih TINGGI (atau sama) daripada aplikasi -> Lebar menjadi pembatas
            adaptive_min_width = min_safe_width
            adaptive_min_height = int(adaptive_min_width / APP_ASPECT_RATIO)

        # 4. Tentukan ukuran minimum final: ambil yang lebih besar antara
        #    hasil adaptif dan batas absolut.
        final_min_width = max(ABS_MIN_WIDTH, adaptive_min_width)
        final_min_height = max(ABS_MIN_HEIGHT, adaptive_min_height)

        # 5. Atur UKURAN MINIMUM jendela
        self.setMinimumSize(final_min_width, final_min_height)
        
        # 6. Atur UKURAN AWAL jendela sama dengan ukuran minimumnya
        self.resize(final_min_width, final_min_height)
        
        # 7. Pusatkan jendela di tengah area layar yang tersedia
        center_x = screen_geom.x() + (screen_geom.width() - final_min_width) / 2
        center_y = screen_geom.y() + (screen_geom.height() - final_min_height) / 2
        self.move(int(center_x), int(center_y))
        
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
            # Hapus isi align_folder
            if os.path.exists(self.align_folder):
                for item in os.listdir(self.align_folder):
                    item_path = os.path.join(self.align_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        rmtree(item_path)

            # Hapus isi stack_folder
            if os.path.exists(self.stack_folder):
                for item in os.listdir(self.stack_folder):
                    item_path = os.path.join(self.stack_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        rmtree(item_path)

            # Hapus align_stitch_cache_folder
            if os.path.exists(self.align_stitch_cache_folder):
                rmtree(self.align_stitch_cache_folder)

            # Hapus database\cache\render_tiles
            render_tiles_folder = os.path.join("database", "cache", "render_tiles")
            if os.path.exists(render_tiles_folder):
                rmtree(render_tiles_folder)

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