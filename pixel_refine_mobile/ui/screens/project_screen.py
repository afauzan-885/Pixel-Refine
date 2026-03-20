from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.lang import Builder

# Desain UI untuk Bottom Sheet Penamaan Proyek
naming_sheet_kv = """
<NamingSheet>:
    size_hint: 0.85, None
    height: "260dp"  # Disedikitkan karena garis handle dihapus
    background_color: 0, 0, 0, 0
    # Mengubah posisi agar benar-benar di tengah layar
    pos_hint: {"center_x": 0.5, "center_y": 0.5}
    
    MDCard:
        orientation: "vertical"
        radius: [25, 25, 25, 25]
        md_bg_color: 0.95, 0.95, 0.95, 1
        padding: "20dp"
        spacing: "16dp"
        
        # --- DRAG HANDLE DIHAPUS ---
            
        MDLabel:
            text: "Project Naming"
            font_style: "H6"
            bold: True
            halign: "center"
            adaptive_height: True
            
        MDTextField:
            id: project_name
            text: "Batch 05/25/2026"
            mode: "fill"
            fill_color_normal: 0.9, 0.9, 0.9, 1
            radius: [10, 10, 10, 10]
            icon_right: "close-circle"
            
        MDLabel:
            text: "Algorithm Tags"
            font_style: "Caption"
            theme_text_color: "Secondary"
            adaptive_height: True
            
        MDScrollView:
            do_scroll_y: False
            do_scroll_x: True
            size_hint_y: None
            height: "40dp"
            
            MDBoxLayout:
                orientation: "horizontal"
                adaptive_width: True
                spacing: "8dp"
                
                MDChip:
                    text: "Denoising"
                    color: 0.1, 0.65, 0.4, 1
                    md_bg_color: 0.8, 0.95, 0.85, 1
                MDChip:
                    text: "HDR Stack"
                    color: 0.1, 0.65, 0.4, 1
                    md_bg_color: 0.8, 0.95, 0.85, 1
                MDChip:
                    text: "Panorama"
                    color: 0.1, 0.65, 0.4, 1
                    md_bg_color: 0.8, 0.95, 0.85, 1
                    
        MDWidget:
            size_hint_y: 1
            
        MDFillRoundFlatButton:
            text: "Create & Open Workspace"
            size_hint_x: 1
            height: "50dp"
            md_bg_color: 0.1, 0.65, 0.4, 1
            font_style: "Button"
            on_release: root.create_project()
"""
Builder.load_string(naming_sheet_kv)


class NamingSheet(ModalView):
    def __init__(self, project_screen, **kwargs):
        super().__init__(**kwargs)
        self.project_screen = project_screen

    def create_project(self):
        self.dismiss()
        # Pindah ke Workspace Screen
        self.project_screen.manager.transition.direction = "left"
        self.project_screen.manager.current = "workspace"


class ProjectScreen(Screen):
    # tool_type sementara dibiarkan jika masih dipakai di Workspace
    tool_type = StringProperty("Denoising")
    has_projects = BooleanProperty(False)

    def open_naming_sheet(self):
        # Membuka Bottom Sheet untuk penamaan proyek
        sheet = NamingSheet(project_screen=self)
        sheet.open()
