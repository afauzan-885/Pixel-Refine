from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

# KV String for SelectorPanel
# Removed RecycleBoxLayout from KV to avoid "ScrollView accept only one widget" error
Builder.load_string(
    """
<SelectableLabel>:
    canvas.before:
        Color:
            rgba: (0.3, 0.3, 0.3, 1) if self.selected else (0.1, 0.1, 0.1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    text_size: self.size
    halign: 'left'
    valign: 'middle'
    padding_x: 10

<SelectorPanel>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    
    BoxLayout:
        size_hint_y: None
        height: 40
        spacing: 5
        PrimaryButton:
            id: btn_add
            text: "Add Pano"
            on_release: root.add_requested()
        DeleteButton:
            id: btn_del
            text: "Delete Pano"
            on_release: root.delete_requested()
            
    RecycleView:
        id: rv
        viewclass: 'SelectableLabel'
            
    BoxLayout:
        size_hint_y: None
        height: 50
        spacing: 5
        PrimaryButton:
            id: btn_import
            text: "Import Images"
        SuccessButton:
            id: btn_action
            text: "Process All"

"""
)


class SelectableRecycleBoxLayout(
    FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    """Adds selection and focus behaviour to the view."""

    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    """Add selection support to the Label"""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Add selection on touch down"""
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            if hasattr(self.parent, "select_with_touch"):
                return self.parent.select_with_touch(self.index, touch)
            elif hasattr(self.parent, "layout_manager") and hasattr(
                self.parent.layout_manager, "select_with_touch"
            ):
                return self.parent.layout_manager.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class SelectorPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Populate dummy data
        self.ids.rv.data = [{"text": str(x)} for x in range(10)]

        # Expose buttons for controller
        self.btn_action = self.ids.btn_action
        self.btn_import = self.ids.btn_import

        # Add layout manually if not present
        if not self.ids.rv.children:
            self.layout_manager = RecycleBoxLayout(
                default_size=(None, 40),
                default_size_hint=(1, None),
                size_hint_y=None,
                orientation="vertical",
            )
            self.layout_manager.bind(
                minimum_height=self.layout_manager.setter("height")
            )
            self.ids.rv.add_widget(self.layout_manager)

    def add_requested(self):
        print("Add requested")

    def delete_requested(self):
        print("Delete requested")
