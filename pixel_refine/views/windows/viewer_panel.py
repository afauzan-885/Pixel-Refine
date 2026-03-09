from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button


class ViewerPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Header
        header = BoxLayout(size_hint_y=None, height=40)
        self.lbl_title = Label(text="No Selection", size_hint_x=0.5, halign="left")
        self.lbl_title.bind(size=self.lbl_title.setter("text_size"))  # Align text left

        self.btn_back = Button(text="Back", size_hint_x=None, width=80)
        self.btn_import = Button(text="Import Images", size_hint_x=None, width=120)

        header.add_widget(self.lbl_title)
        header.add_widget(self.btn_back)
        header.add_widget(self.btn_import)
        self.add_widget(header)

        # Content Area (Stack)
        self.sm = ScreenManager()

        # Grid Screen
        self.grid_screen = Screen(name="grid")
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=5, size_hint_y=None, spacing=5, padding=5)
        self.grid.bind(minimum_height=self.grid.setter("height"))

        # Dummy Grid Items
        for i in range(20):
            self.grid.add_widget(Button(text=f"Img {i}", size_hint_y=None, height=100))

        self.scroll.add_widget(self.grid)
        self.grid_screen.add_widget(self.scroll)
        self.sm.add_widget(self.grid_screen)

        # Loading Screen
        self.loading_screen = Screen(name="loading")
        self.loading_screen.add_widget(Label(text="Processing..."))
        self.sm.add_widget(self.loading_screen)

        self.add_widget(self.sm)

    def show_grid(self):
        self.sm.current = "grid"
        self.btn_back.disabled = True  # Or hide

    def show_loading(self, message="Processing..."):
        self.sm.current = "loading"
        # Update label text if possible, need reference to label
        # For now just switch screen
        self.btn_back.disabled = False
