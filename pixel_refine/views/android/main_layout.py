from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton


class AndroidMainLayout(BoxLayout):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.orientation = "vertical"

        # Action Bar (Top)
        self.action_bar = ActionBar()
        av = ActionView()
        av.add_widget(ActionPrevious(title="Pixel Refine", with_previous=False))
        av.add_widget(ActionButton(text="Settings", on_release=self.go_to_settings))
        self.action_bar.add_widget(av)
        self.add_widget(self.action_bar)

        # Screen Manager (Content)
        self.sm = ScreenManager()

        # Home Screen
        self.home_screen = Screen(name="home")
        home_layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        home_layout.add_widget(Label(text="Mobile Home Screen", font_size="24sp"))
        home_layout.add_widget(
            Button(text="Start New Project", size_hint_y=None, height=60)
        )
        home_layout.add_widget(Button(text="View Gallery", size_hint_y=None, height=60))
        self.home_screen.add_widget(home_layout)
        self.sm.add_widget(self.home_screen)

        # Settings Screen
        self.settings_screen = Screen(name="settings")
        settings_layout = BoxLayout(orientation="vertical", padding=20)
        settings_layout.add_widget(Label(text="Settings"))
        settings_layout.add_widget(
            Button(text="Back to Home", on_release=self.go_to_home)
        )
        self.settings_screen.add_widget(settings_layout)
        self.sm.add_widget(self.settings_screen)

        self.add_widget(self.sm)

    def go_to_settings(self, instance):
        self.sm.transition.direction = "left"
        self.sm.current = "settings"

    def go_to_home(self, instance):
        self.sm.transition.direction = "right"
        self.sm.current = "home"
