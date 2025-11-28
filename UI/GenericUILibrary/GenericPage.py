from PySide6.QtWidgets import QWidget, QHBoxLayout
from UI.GenericUILibrary.selector_panel import SelectorPanel
from UI.GenericUILibrary.workspace_layout import WorkspaceLayout
from UI.enhance_stack.logic.database_manager import DatabaseManager

# Import Stylesheet
from UI.resources.stylesheet.stylesheet import stylesheet_global_page

class GenericPage(QWidget):
    def __init__(self, database_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        
        # 1. Terapkan Stylesheet Global di Root Page ini
        self.setStyleSheet(stylesheet_global_page())

        # Setup Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Nol-kan margin agar style full
        main_layout.setSpacing(0)

        # Kontainer Konten (Agar margin dalam bisa diatur terpisah seperti aslinya)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(10)

        # --- Instansiasi Komponen ---
        self.workspace = WorkspaceLayout()
        
        # Beri ID pada Selector agar mirip dengan panel kanan lama
        self.selector = SelectorPanel(title="Panorama Projects", action_btn_text="Process All Pano")
        
        content_layout.addWidget(self.workspace, 3)
        content_layout.addWidget(self.selector, 1)

        main_layout.addWidget(content_widget)

        # --- Logic Controller Mock ---
        self._setup_controller_logic()
        self._populate_dummy_data()

    def _setup_controller_logic(self):
        # ... (Logika sama seperti sebelumnya) ...
        self.selector.item_selected.connect(self._on_item_selected)
        self.selector.selection_cleared.connect(self._on_selection_cleared)
        self.selector.add_requested.connect(lambda name: self.selector.add_item("new", name))
        self.selector.delete_requested.connect(lambda ids: [self.selector.remove_item(i) for i in ids])
        self.workspace.config_panel.apply_clicked.connect(self._on_process)

    def _on_item_selected(self, item_id, label):
        self.workspace.viewer.set_view_title(label)
        self.workspace.toggle_config_panel(True)
        # Dummy Grid
        self.workspace.viewer._clear_grid()
        for i in range(5):
            self.workspace.viewer.add_grid_item(f"img{i}", f"Image {i}.jpg")

    def _on_selection_cleared(self):
        self.workspace.viewer.show_empty_state()
        self.workspace.toggle_config_panel(False)

    def _on_process(self, data):
        self.workspace.viewer.show_loading(f"Processing {data.get('name', 'Task')}...")

    def _populate_dummy_data(self):
        self.selector.add_item("1", "Project Bali")
        self.selector.add_item("2", "Project Jakarta")