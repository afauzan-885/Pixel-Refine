import os
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform

# Import Controllers
from pixel_refine.controllers.main_controller import MainController


class PixelRefineApp(App):
    def build(self):
        self.title = "Pixel Refine"

        # Load KV styles
        self.load_kv_files()

        # Initialize Controller
        self.controller = MainController()

        # Determine platform and load appropriate view
        if platform == "android":
            from pixel_refine.views.android.main_layout import AndroidMainLayout

            return AndroidMainLayout(controller=self.controller)
        else:
            # Default to Windows/Desktop
            from pixel_refine.views.windows.main_window import MainWindow

            return MainWindow(controller=self.controller)

    def load_kv_files(self):
        # Load main style.kv
        kv_path = os.path.join(os.path.dirname(__file__), "resources", "style.kv")
        if os.path.exists(kv_path):
            Builder.load_file(kv_path)

        # We can load other component-specific KV files here if needed
