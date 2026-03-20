from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock


class WorkspaceScreen(Screen):
    tool_type = StringProperty("Denoising")  # Bisa diganti jadi HDR/Panorama
    preview_source = StringProperty(
        "placeholder_image.jpg"
    )  # Ganti dengan path default Anda
    image_count = NumericProperty(20)

    def on_enter(self, *args):
        # Di sini nanti Anda bisa me-load thumbnail secara dinamis
        pass

    def run_algorithm(self, *args):
        print(
            f"[Workspace] Running {self.tool_type} algorithm on {self.image_count} images..."
        )
        # Logika algoritma Anda di sini

    def go_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "project"
