from kivymd.app import MDApp
from kivy.core.window import Window
import os

# Define mobile-like window size for testing on desktop
Window.size = (360, 640)

class PixelRefineApp(MDApp):
    def build(self):
        # Set Global Theme Settings
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.material_style = "M3"
        
        # Load all .kv design files dynamically
        from pixel_refine_mobile.core.theme_config import load_kv_files
        load_kv_files()
        
        # Initialize Core App State (ScreenManager & Navigation)
        from pixel_refine_mobile.core.app_state import AppState
        self.app_state = AppState()
        
        # Return the root widget manager
        return self.app_state.get_root_widget()

if __name__ == '__main__':
    PixelRefineApp().run()
