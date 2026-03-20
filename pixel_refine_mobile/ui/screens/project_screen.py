from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty

class ProjectScreen(Screen):
    """
    Generic Project Screen that acts as an explorer for Recent and Other projects.
    It adapts to the tool chosen from the Home Screen (Denoising, HDR Stack, or Panorama).
    """
    tool_type = StringProperty("Denoising")
    has_projects = BooleanProperty(False)
    
    def on_enter(self, *args):
        # Memperbarui judul toolbar sesuai dengan alat yang dipilih
        self.ids.top_bar.title = f"{self.tool_type} Projects"
        self.refresh_project_list()
        
    def refresh_project_list(self):
        # TODO: Cek database SQLite berdasarkan self.tool_type
        # Jika kosong, biarkan hanya tombol "New" yang terlihat sesuai desain
        pass
        
    def go_back(self):
        # Kembali ke Home Screen dengan animasi usap ke kanan
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'
        
    def create_new_project(self):
        # Arahkan ke workspace editor spesifik (saat ini default ke Denoising)
        print(f"[UI] User tapped New Project for: {self.tool_type}")
        
        self.manager.transition.direction = 'left'
        self.manager.current = 'denoising'
