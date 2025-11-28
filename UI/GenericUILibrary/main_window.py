import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

# Import Generic Components
from .workspace_layout import WorkspaceLayout
from .selector_panel import SelectorPanel

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generic Application UI")
        self.resize(1000, 700)

        # --- Setup UI Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Kiri: Workspace (Viewer + Config)
        self.workspace = WorkspaceLayout()
        
        # Kanan: Selector (List)
        self.selector = SelectorPanel(title="My Projects", action_btn_text="Process All")
        
        main_layout.addWidget(self.workspace, 3) # Ratio 3
        main_layout.addWidget(self.selector, 1)  # Ratio 1

        # --- Connect Signals (Controller Logic Simulation) ---
        self._connect_logic()
        
        # --- Dummy Data ---
        self.selector.add_item("id_1", "Project Alpha")
        self.selector.add_item("id_2", "Project Beta")

    def _connect_logic(self):
        """
        Menghubungkan signal UI ke logika (Di sini logika simpel saja).
        """
        # Saat item dipilih di kanan -> Update Viewer kiri & Buka panel config
        self.selector.item_selected.connect(self._on_item_selected)
        
        # Saat seleksi hilang -> Bersihkan Viewer & Tutup panel config
        self.selector.selection_cleared.connect(self._on_selection_cleared)
        
        # Saat tombol Add ditekan
        self.selector.add_requested.connect(
            lambda name: self.selector.add_item("new_id", name)
        )
        
        # Saat tombol delete
        self.selector.delete_requested.connect(
            lambda ids: [self.selector.remove_item(i) for i in ids]
        )

        # Saat tombol 'Apply' di config panel ditekan
        self.workspace.config_panel.apply_clicked.connect(self._on_process_run)

    # --- Logic Handlers ---

    def _on_item_selected(self, item_id, label):
        self.workspace.viewer.set_view_title(label)
        self.workspace.toggle_config_panel(True) # Buka panel bawah
        
        # Simulasi isi konten grid
        for i in range(4):
            self.workspace.viewer.add_grid_item(f"img_{i}", f"Data {i}")

    def _on_selection_cleared(self):
        self.workspace.viewer.show_empty_state()
        self.workspace.toggle_config_panel(False) # Tutup panel bawah

    def _on_process_run(self, data):
        print(f"Processing with data: {data}")
        self.workspace.viewer.show_loading(f"Processing {data['name']}...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainAppWindow()
    window.show()
    sys.exit(app.exec())