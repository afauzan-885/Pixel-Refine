from kivy.uix.screenmanager import ScreenManager
from pixel_refine_mobile.ui.screens.welcome_screen import WelcomeScreen
from pixel_refine_mobile.ui.screens.home_screen import HomeScreen
from pixel_refine_mobile.ui.screens.project_screen import ProjectScreen
from pixel_refine_mobile.ui.screens.workspace_screen import WorkspaceScreen


class AppState:
    """
    Core state manager setara dengan 'app_manager' di Desktop.
    Mengelola ScreenManager dan transisi antar halaman.
    """

    def __init__(self):
        self.screen_manager = ScreenManager()
        self._init_screens()

    def _init_screens(self):
        # Register all application screens
        self.screen_manager.add_widget(WelcomeScreen(name="welcome"))
        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(ProjectScreen(name="project"))
        self.screen_manager.add_widget(WorkspaceScreen(name="workspace"))

    def get_root_widget(self):
        return self.screen_manager
