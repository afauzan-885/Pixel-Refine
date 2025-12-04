from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

from pixel_refine.views.windows.workspace_layout import WorkspaceLayout
from pixel_refine.views.windows.selector_panel import SelectorPanel
from pixel_refine.resources.theme import THEME_KV

class MainWindow(BoxLayout):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        Builder.load_string(THEME_KV)
        
        self.controller = controller
        self.controller.set_view(self)  # Link view to controller
        self.orientation = "horizontal"

        # Workspace (Left, larger)
        self.workspace = WorkspaceLayout(size_hint_x=0.75)
        self.add_widget(self.workspace)

        # Selector (Right, smaller)
        self.selector = SelectorPanel(size_hint_x=0.25)
        self.add_widget(self.selector)

        # Connect signals/logic (Simulation)
        # When "Process All" is clicked, toggle the config panel
        self.selector.btn_action.bind(
            on_release=lambda x: self.workspace.toggle_config_panel(
                not self.workspace.is_config_open
            )
        )

    def show_file_chooser(self, callback):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(path='.', filters=['*.jpg', '*.png', '*.dng', '*.tiff'])
        
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        btn_cancel = Button(text="Cancel", on_release=lambda x: popup.dismiss())
        btn_select = Button(text="Select", on_release=lambda x: self._select_files(file_chooser.selection, callback, popup))
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_select)
        
        content.add_widget(file_chooser)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Select Images", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def _select_files(self, selection, callback, popup):
        popup.dismiss()
        callback(selection)

    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height=40, on_release=lambda x: popup.dismiss())
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.4))
        popup.open()
