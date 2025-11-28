from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Slot, Signal

# Asumsi import UI komponen tetap ada
from UI.panorama.display_area.display_panel import DisplayPanel
from UI.panorama.workflow_area.workflow_panel import WorkflowPanel
from UI.resources.animation.animation_manager import HeightAnimator, SlideDirection, StackedWidgetAnimator
from UI.resources.animation.slide import slide

class WorkingLeftPanel(QWidget):
    """
    Panel Kiri: Pengontrol utama Layout (Display di atas, Workflow di bawah).
    Murni menangani transisi UI dan Layout.
    """
    rename_project_requested = Signal(str, str) # id, new_name

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Animator ---
        self.slide_animator = StackedWidgetAnimator()
        self.height_animator = HeightAnimator(self)

        # --- Setup Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # --- Komponen UI ---
        self.display_panel = DisplayPanel()
        
        # Setup Workflow Area (Bisa disembunyikan/slide)
        self.workflow_stack = QStackedWidget()
        self.workflow_panel = WorkflowPanel()
        self.workflow_placeholder = QWidget() # Kosong saat panel tertutup
        
        self.workflow_stack.addWidget(self.workflow_panel)
        self.workflow_stack.addWidget(self.workflow_placeholder)
        
        # Tambahkan ke layout
        main_layout.addWidget(self.display_panel, 1) # Expand
        main_layout.addWidget(self.workflow_stack, 0) # Fit size
        
        # Kondisi Awal: Workflow panel tertutup
        self.workflow_stack.setCurrentWidget(self.workflow_placeholder)
        self.workflow_stack.setFixedHeight(0)
        
        self._connect_signals()

    def _connect_signals(self):
        # Sinyal internal UI
        self.display_panel.back_to_grid_requested.connect(self._on_back_to_grid)
        self.workflow_panel.preview_requested.connect(self._on_preview_simulation)

    # --- View Management (Visual Only) ---

    @Slot(str, str)
    def update_display_for_project(self, project_id, project_name):
        """Dipanggil saat user memilih item di panel kanan."""
        self.display_panel.set_project_view(project_name)
        
        # Animasi Membuka Panel Workflow
        if self.workflow_stack.height() == 0:
            target_height = self.workflow_panel.sizeHint().height() or 200
            self.height_animator.animate_height(self.workflow_stack, target_height, 350)
            slide(self.slide_animator, self.workflow_stack, self.workflow_panel, SlideDirection.UP, 350)

    @Slot()
    def clear_display(self):
        """Dipanggil saat seleksi kosong."""
        self.display_panel.show_empty_state()
        
        # Animasi Menutup Panel Workflow
        if self.workflow_stack.height() > 0:
            self.height_animator.animate_height(self.workflow_stack, 0, 300)
            slide(self.slide_animator, self.workflow_stack, self.workflow_placeholder, SlideDirection.DOWN, 300)

    # --- UI Interactions ---

    @Slot()
    def _on_back_to_grid(self):
        self.display_panel.show_grid_view()

    @Slot(str)
    def _on_preview_simulation(self, stage_name):
        """Hanya simulasi visual saat tombol preview ditekan."""
        print(f"UI Simulation: Showing processing view for {stage_name}")
        self.display_panel.show_processing_view(f"Processing {stage_name}...")
        
        # Simulasi selesai setelah 1 detik (tanpa thread)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.display_panel.show_preview_result())