from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner


class ConfigPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Tabbed Panel
        self.tabs = TabbedPanel(do_default_tab=False)

        # Tab 1: Alignment
        tab1 = TabbedPanelItem(text="Alignment")
        content1 = BoxLayout(orientation="vertical", padding=10)

        row1 = BoxLayout(size_hint_y=None, height=40)
        row1.add_widget(Label(text="Feature Matching:"))
        self.spinner_method = Spinner(text="AKAZE", values=("AKAZE", "SIFT", "ORB"))
        row1.add_widget(self.spinner_method)

        content1.add_widget(row1)
        content1.add_widget(Label())  # Spacer
        tab1.content = content1
        self.tabs.add_widget(tab1)

        # Tab 2: Projection
        tab2 = TabbedPanelItem(text="Projection")
        content2 = BoxLayout(orientation="vertical", padding=10)
        content2.add_widget(Label(text="Projection Settings Placeholder"))
        tab2.content = content2
        self.tabs.add_widget(tab2)

        self.add_widget(self.tabs)

        # Apply Button
        self.btn_apply = Button(text="Run Process", size_hint_y=None, height=50)
        self.btn_apply.bind(on_release=self.on_apply)
        self.add_widget(self.btn_apply)

    def on_apply(self, instance):
        # Get settings
        method = self.spinner_method.text
        settings = {"method": method}

        # We need access to the controller.
        # In a strict MVC, the view shouldn't know about the controller directly if possible,
        # or it should fire an event.
        # But for simplicity here, we can traverse up or use the App instance.
        from kivy.app import App

        app = App.get_running_app()
        if app and hasattr(app, "controller"):
            app.controller.run_process(settings)
