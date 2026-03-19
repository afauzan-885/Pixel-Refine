from kivy.uix.screenmanager import Screen

class HomeScreen(Screen):
    """
    View logic for the Home Screen.
    Handles user interaction with the Denoising, HDR, and Panorama cards.
    """
    def open_tool_projects(self, tool_name):
        # Ambil referensi ke ProjectScreen dan atur context tool_type-nya
        project_screen = self.manager.get_screen('project')
        project_screen.tool_type = tool_name
        
        # Lakukan transisi usap ke kiri
        self.manager.transition.direction = 'left'
        self.manager.current = 'project'
