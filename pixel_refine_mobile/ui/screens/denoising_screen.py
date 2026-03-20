from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock

class DenoisingScreen(Screen):
    """
    Denoising Workspace Screen.
    Handles the 60-15-25 layout for main editing.
    """
    has_images = BooleanProperty(False)
    preview_source = StringProperty("")
    mode = StringProperty("Denoising")
    progress = NumericProperty(0)

    def import_images(self, *args):
        # TODO: Implement native file picker
        print("[UI] Importing burst images...")
        self.has_images = True
        # Placeholder image logic
        self.preview_source = "pixel_refine_mobile/ui/kv/logo_placeholder.png" 
        
    def run_algorithm(self, *args):
        print(f"[UI] Running {self.mode} algorithm...")
        self.progress = 0
        Clock.schedule_interval(self._simulate_progress, 0.05)
        
    def _simulate_progress(self, dt):
        self.progress += 2
        if self.progress >= 100:
            self.progress = 100
            print(f"[UI] {self.mode} Finished!")
            return False # Terminate interval
            
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'project'
