from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class WelcomeScreen(Screen):
    def on_enter(self, *args):
        Clock.schedule_once(self.start_loading, 0.5)

    def start_loading(self, dt):
        if "progress" in self.ids:
            self.ids.progress.value = 0
            self.loading_event = Clock.schedule_interval(self.update_progress, 0.03)
        else:
            # Ubah dari 'home' ke 'project'
            self.manager.current = "project"

    def update_progress(self, dt):
        if self.ids.progress.value < 100:
            self.ids.progress.value += 2
        else:
            self.loading_event.cancel()
            # Ubah dari 'home' ke 'project'
            self.manager.current = "project"
