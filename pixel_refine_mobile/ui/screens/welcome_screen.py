from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import os

class WelcomeScreen(Screen):
    """
    View logic for the Welcome Screen.
    Handles the initial loading animation and transition to the Home Screen.
    """
    def on_enter(self, *args):
        # Allow the view to render completely before starting the progress animation
        Clock.schedule_once(self.start_loading, 0.5)

    def start_loading(self, dt):
        if 'progress' in self.ids:
            self.ids.progress.value = 0
            # Schedule the update_progress function to run every 0.03 seconds
            self.loading_event = Clock.schedule_interval(self.update_progress, 0.03)
        else:
            # Fallback if the progress widget is not found
            self.manager.current = 'home'

    def update_progress(self, dt):
        if self.ids.progress.value < 100:
            self.ids.progress.value += 2
        else:
            # When loading is complete, stop the animation and go to the home screen
            self.loading_event.cancel()
            self.manager.current = 'home'
