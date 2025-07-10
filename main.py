import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QMessageBox
from PySide6.QtGui import QIcon

from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.animation.animation_manager import StackedWidgetAnimator
from UI.resources.animation.fade import fade_in
from UI.sidebar import Sidebar
from UI.main_content import MainContent
import config
from shutil import rmtree

class PixelRefineMain(QMainWindow):
    def __init__(self):
        super().__init__()
        
        db_path = "pixel_refine_database.db" 
        self.database_manager = DatabaseManager(db_path)
        self.database_manager.create_database()
        self.main_content = MainContent(self.database_manager)
        self.main_content_animator = StackedWidgetAnimator(self)
    
        # Ikon dan Judul Jendela
        self.setWindowIcon(QIcon("UI/resources/image/Logo_Pixel_Refine.png")) # Pastikan path ini benar
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION}")
        self.setMinimumSize(1200, 600)

        # Path Folder dan Pembuatan Folder
        self.database_folder = "database" 
        self.align_folder = os.path.join(self.database_folder, "align")
        self.stack_folder = os.path.join(self.database_folder, "stack")
        self.create_folders_if_needed()

        # Sidebar dan Konten Utama
        self.sidebar = Sidebar(self.toggle_sidebar, self.switch_page)
        self.main_content = MainContent(self.database_manager)

        # Layout Utama
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

       
        self.switch_page(0)

    def create_folders_if_needed(self):
        """Memeriksa dan membuat folder jika belum ada."""
        try:
            os.makedirs(self.database_folder, exist_ok=True) 
            os.makedirs(self.align_folder, exist_ok=True)
            os.makedirs(self.stack_folder, exist_ok=True)
        except OSError as e:
            print(f"Error creating folders: {e}")
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat membuat folder: {e}. Aplikasi akan ditutup.")
            sys.exit(1)  

    def closeEvent(self, event):
        """Dijalankan saat aplikasi ditutup."""
        try:
           
            if os.path.exists(self.align_folder):
                for item in os.listdir(self.align_folder):
                    item_path = os.path.join(self.align_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path) 
                    elif os.path.isdir(item_path):
                        rmtree(item_path) 

            if os.path.exists(self.stack_folder):
                for item in os.listdir(self.stack_folder):
                    item_path = os.path.join(self.stack_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        rmtree(item_path)  
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Terjadi kesalahan saat menghapus konten folder: {e}")
        finally:
            event.accept()
            
    def switch_page(self, index):
        """
        Mengganti halaman di konten utama (MainContent) dengan animasi fade
        yang dikelola oleh self.main_content_animator.
        """
        if not (0 <= index < self.main_content.count()):
            print(f"PixelRefineMain Error: Invalid page index requested: {index}")
            return

        if index == self.main_content.currentIndex():
            for i, btn in enumerate(self.sidebar.nav_buttons): btn.setChecked(i == index)
            return

        for i, btn in enumerate(self.sidebar.nav_buttons):
            btn.setChecked(i == index)
        fade_in(self.main_content_animator, self.main_content, index, duration=250)
        
    def toggle_sidebar(self):
        """Menangani aksi tambahan saat sidebar di-toggle."""
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PixelRefineMain()
    window.show()
    sys.exit(app.exec()) 