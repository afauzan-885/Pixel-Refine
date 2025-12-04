from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import NumericProperty

# Import child components (to be implemented)
from pixel_refine.views.windows.viewer_panel import ViewerPanel
from pixel_refine.views.windows.config_panel import ConfigPanel


class WorkspaceLayout(BoxLayout):
    config_height = NumericProperty(250)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 10

        # Viewer Panel (Top)
        self.viewer = ViewerPanel()
        self.add_widget(self.viewer)

        # Config Panel (Bottom)
        self.config_panel = ConfigPanel(size_hint_y=None, height=0, opacity=0)
        self.add_widget(self.config_panel)

        self.is_config_open = False

    def toggle_config_panel(self, show):
        if self.is_config_open == show:
            return

        self.is_config_open = show

        if show:
            anim = Animation(
                height=self.config_height, opacity=1, duration=0.35, t="in_out_quad"
            )
        else:
            anim = Animation(height=0, opacity=0, duration=0.35, t="in_out_quad")

        anim.start(self.config_panel)
