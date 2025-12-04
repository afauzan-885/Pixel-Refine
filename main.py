import sys

# ============================================================================
# MVC ARCHITECTURE TOGGLE
# Set to True to use new MVC architecture, False to use legacy code
# ============================================================================
USE_MVC_ARCHITECTURE = False  # Toggle this to test new vs old code
# ============================================================================

# Import PySide6 modules
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget, 
                               QStackedWidget, QLabel, QVBoxLayout, QPushButton)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

# Import project modules
from core import ApplicationManager, WindowConfig
from UI.components import SplashScreen
from UI.resources.animation.fade import fade_in
import config

# Conditional imports based on architecture
if USE_MVC_ARCHITECTURE:
    # New MVC architecture
    from UI.enhance_stack.views import EnhanceStackView
else:
    # Legacy architecture
    from UI.sidebar import Sidebar
    from UI.main_content import MainContent


class PixelRefineMain(QMainWindow):
    def __init__(self):
        """
        Initialize main window.
        Lightweight constructor that only initializes attributes.
        """
        super().__init__()
        self.main_content = None
        self.sidebar = None
        self.app_manager = None
        self.window_config = None
        self.sidebar_buttons = []

    def setup_ui_and_logic(self, splash: SplashScreen):
        """Setup UI and application logic with progress updates."""
        # Initialize application manager
        splash.update_status("Initializing application...", 10)
        self.app_manager = ApplicationManager(self)
        
        # Setup database
        splash.update_status("Loading database...", 25)
        database_manager = self.app_manager.initialize_database()

        # Setup animator
        splash.update_status("Initializing animations...", 40)
        main_content_animator = self.app_manager.setup_animator()

        # Configure window
        splash.update_status("Setting up main window...", 55)
        self.setWindowIcon(QIcon("UI/resources/icon/enhance_stack.png"))
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION} {'(MVC)' if USE_MVC_ARCHITECTURE else '(Legacy)'}")
        
        self.window_config = WindowConfig(
            app_aspect_ratio=1200 / 600,
            min_screen_ratio=0.76,
            abs_min_width=800,
            abs_min_height=400
        )
        self.window_config.apply_to_window(self)

        # Prepare folders
        splash.update_status("Preparing temporary folders...", 70)
        self.app_manager.initialize_folders()

        # Load UI components based on architecture
        splash.update_status("Loading UI components...", 85)
        
        if USE_MVC_ARCHITECTURE:
            # New MVC architecture - simplified main content
            self.main_content = QStackedWidget()
            
            # Add MVC-based enhance stack view
            enhance_stack_view = EnhanceStackView(
                db_path=self.app_manager.database_manager.db_path,
                parent=self.main_content
            )
            self.main_content.addWidget(enhance_stack_view)
            
            # Add placeholders for other pages
            panorama_placeholder = QLabel("Panorama Page\n(Legacy - Not Yet Migrated)")
            panorama_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panorama_placeholder.setStyleSheet("font-size: 14px; padding: 20px;")
            self.main_content.addWidget(panorama_placeholder)
            
            settings_placeholder = QLabel("Settings Page\n(Legacy - Not Yet Migrated)")
            settings_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            settings_placeholder.setStyleSheet("font-size: 14px; padding: 20px;")
            self.main_content.addWidget(settings_placeholder)
            
            # Create simple MVC sidebar
            self.sidebar = self._create_mvc_sidebar()
            
            print("\n" + "="*60)
            print("✅ MVC ARCHITECTURE LOADED")
            print("="*60)
            print("📦 Models:")
            print("   - ImageModel, BatchModel, AlgorithmConfig")
            print("   - Repositories: Image, Batch, Panorama")
            print("\n🎮 Controllers:")
            print("   - SinglePageController")
            print("   - BatchPageController")
            print("   - ImageProcessingController")
            print("   - ImportExportController")
            print("\n🖼️  Views:")
            print("   - EnhanceStackView (MVC-based)")
            print("   - Panorama (Legacy - Not Migrated)")
            print("   - Settings (Legacy - Not Migrated)")
            print("="*60)
            print("💡 Toggle USE_MVC_ARCHITECTURE in main.py to switch\n")
        else:
            # Legacy architecture
            self.main_content = MainContent(database_manager)
            self.sidebar = Sidebar(self.toggle_sidebar, self.switch_page)
            print("\n" + "="*60)
            print("⚠️  LEGACY ARCHITECTURE LOADED")
            print("="*60)
            print("Using original UI/main_content.py")
            print("Set USE_MVC_ARCHITECTURE = True to use new MVC code")
            print("="*60 + "\n")

        # Assemble layout
        splash.update_status("Assembling UI layout...", 95)
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
       
        splash.update_status("Finalizing...", 100)
        self.switch_page(0)
    
    def _create_mvc_sidebar(self):
        """Create a simple sidebar for MVC mode."""
        sidebar = QWidget()
        sidebar.setStyleSheet("QWidget { background-color: #e0e0e0; color: #333; }")
        sidebar.setFixedWidth(180)
        
        layout = QVBoxLayout()
        sidebar.setLayout(layout)
        
        # Toggle button (placeholder)
        toggle_btn = QPushButton("☰")
        toggle_btn.setStyleSheet("""
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
        """)
        layout.addWidget(toggle_btn)
        
        # Navigation buttons
        pages = [
            ("Enhance Stack", "UI/resources/icon/enhance_stack.png"),
            ("Panorama", "UI/resources/icon/panorama.png"),
        ]
        
        for idx, (text, icon_path) in enumerate(pages):
            btn = QPushButton(text)
            btn.setIcon(QIcon(icon_path))
            btn.setCheckable(True)
            btn.setStyleSheet("""
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
            """)
            # Use default argument to capture idx
            btn.clicked.connect(lambda checked=False, i=idx: self.switch_page(i))
            layout.addWidget(btn)
            self.sidebar_buttons.append(btn)
        
        layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setIcon(QIcon("UI/resources/icon/setting.png"))
        settings_btn.setCheckable(True)
        settings_btn.setStyleSheet("""
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
        """)
        settings_btn.clicked.connect(lambda: self.switch_page(2))
        layout.addWidget(settings_btn)
        self.sidebar_buttons.append(settings_btn)
        
        # Store buttons for switch_page to use
        sidebar.side_buttons = self.sidebar_buttons
        
        return sidebar

    def closeEvent(self, event):
        """Handle application close event."""
        if self.app_manager:
            self.app_manager.cleanup_folders()
        event.accept()

    def switch_page(self, index):
        """Switch to a different page with fade animation."""
        if self.main_content is None: 
            return
        if not (0 <= index < self.main_content.count()): 
            return
        if index == self.main_content.currentIndex() and self.main_content.widget(index) is not None:
            if USE_MVC_ARCHITECTURE:
                for i, btn in enumerate(self.sidebar_buttons):
                    btn.setChecked(i == index)
            elif self.sidebar: 
                for i, btn in enumerate(self.sidebar.side_buttons): 
                    btn.setChecked(i == index)
            return
        
        if USE_MVC_ARCHITECTURE:
            for i, btn in enumerate(self.sidebar_buttons):
                btn.setChecked(i == index)
        elif self.sidebar:
            for i, btn in enumerate(self.sidebar.side_buttons): 
                btn.setChecked(i == index)
        
        fade_in(self.app_manager.animator, self.main_content, index, duration=250)

    def toggle_sidebar(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Setup and display custom splash screen
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
