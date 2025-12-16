"""
Algorithm Panel Component - Handles workflow settings and algorithms.
Part of the refactored LeftPanel architecture.

UI Layer only - Logic separated to core/logic/algorithm_logic.py
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal, QThread

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    # Generic UI Library
    FormGroup,
    Button,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.progress_bars import (
    ProgressBar as ModernProgressBar,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.progress_bars import (
    ProgressBar as ModernProgressBar,
)

# Algorithm logic
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic

# Algorithms Imports
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.AKAZE import (
    running_akaze,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Farneback_optical_flow import (
    running_farneback_optical_flow,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Light_Glue import (
    running_light_glue,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.ORB import running_orb
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Average import (
    running_average,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
    running_median,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Similarity import (
    running_similarity,
)


class AlgorithmProcessorThread(QThread):
    """
    Background thread to execute selected algorithms for a batch.
    """

    progress_update = Signal(int, str)
    finished_processing = Signal()

    def __init__(self, batch_id, settings, parent=None):
        super().__init__(parent)
        self.batch_id = batch_id
        self.settings = settings
        self.parent_panel = parent  # Reference to panel for context if needed

    def run(self):
        # Progress callback to emit signal
        def progress_callback(percent, message=""):
            self.progress_update.emit(percent, message)

        # Define actions mapping (similar to CombinedPanel)
        actions = {
            "alignment": {
                "Farneback Optical Flow": lambda: running_farneback_optical_flow(
                    self.parent_panel,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "AKAZE": lambda: running_akaze(
                    self.parent_panel,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "ORB": lambda: running_orb(
                    self.parent_panel,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "Light Glue": lambda: running_light_glue(
                    self.parent_panel,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "No Alignment": lambda: None,
                "None": lambda: None,
            },
            "super_resolution": {
                "No Super Resolution": lambda: None,
                "None": lambda: None,
            },
            "denoising": {
                "Average": lambda: running_average(
                    self.parent_panel,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "Median": lambda: running_median(
                    self.parent_panel,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "Similarity": lambda: running_similarity(
                    self.parent_panel,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "No Denoising": lambda: None,
                "None": lambda: None,
            },
        }

        # Execute selected algorithms
        any_algorithm_executed = False
        for category, selected_algo_name in self.settings.items():
            if not selected_algo_name or selected_algo_name in [
                "None",
                "No Alignment",
                "No Super Resolution",
                "No Denoising",
            ]:
                continue

            if category in actions and selected_algo_name in actions[category]:
                print(
                    f"[INFO] Executing '{selected_algo_name}' for batch_id: {self.batch_id}"
                )
                try:
                    actions[category][selected_algo_name]()
                    any_algorithm_executed = True
                except Exception as e:
                    print(f"[ERROR] Failed to execute {selected_algo_name}: {e}")
            else:
                print(
                    f"[WARN] Algorithm '{selected_algo_name}' for category '{category}' not found in actions."
                )

        if not any_algorithm_executed:
            print(f"[INFO] No algorithms were executed for batch_id: {self.batch_id}")

        self.finished_processing.emit()


class AlgorithmPanel(QWidget):
    """
    Algorithm Panel untuk workflow settings dan parameter konfigurasi.

    UI Layer - handles only presentation logic.
    Business logic delegated to AlgorithmLogic.

    Features:
    - Two-column layout: ParameterAlignment (left) and ParameterAlgorithm (right)
    - Algorithm selection per category
    - Process button dan progress tracking
    """

    # Signals
    process_requested = Signal(dict)  # Emit settings dict

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.logic = AlgorithmLogic()  # Business logic
        self.current_batch_id = None  # Track selected batch
        self.processor_thread = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI dengan two-column layout."""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 0, 0)

        # Two-column layout
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(20)

        # --- LEFT COLUMN: Parameter Alignment ---
        left_column = self._create_parameter_alignment()
        columns_layout.addWidget(left_column, stretch=1)

        # --- RIGHT COLUMN: Parameter Algorithm (Other) ---
        right_column = self._create_parameter_algorithm()
        columns_layout.addWidget(right_column, stretch=1)

        main_layout.addLayout(columns_layout)

        # --- Progress Bar (Restored) ---
        self.progress_container = QWidget()
        self.progress_container.setFixedHeight(4)  # Match minimalist bar height
        self.progress_container.setStyleSheet("background-color: #FFFFFF;")

        container_layout = QVBoxLayout(self.progress_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.progress_bar = ModernProgressBar(
            style="linear", variant="primary", minimalist=True
        )
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        container_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_container)

    def _create_parameter_alignment(self):
        """Create left column for alignment parameters (formerly list algorithm)."""
        widget = QWidget()
        widget.setObjectName("paramAlignWidget")
        widget.setStyleSheet("#paramAlignWidget { background-color: #FFFFFF; }")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header = QLabel("Parameter Alignment")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)

        # Placeholder for future alignment parameters
        placeholder = QLabel("Alignment parameters will\nappear here")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()
        return widget

    def _create_parameter_algorithm(self):
        """Create right column for algorithm parameters."""
        widget = QWidget()
        widget.setObjectName("paramAlgoWidget")
        widget.setStyleSheet("#paramAlgoWidget { background-color: #FFFFFF; }")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header = QLabel("Parameter Algorithm")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)

        # Placeholder for future parameters
        placeholder = QLabel("Parameters will appear here\nbased on selected algorithm")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        # Process Button (moved here)
        self.process_btn = Button("▶ Start", variant="primary")
        self.process_btn.clicked.connect(self._on_process_clicked)
        layout.addWidget(self.process_btn)

        layout.addStretch()
        return widget

    def _on_process_clicked(self):
        """
        Process based on selected batch_id.
        Executes algorithms using AlgorithmProcessorThread.
        """
        if not self.current_batch_id:
            print("Warning: No batch selected for processing")
            return

        settings = self.logic.get_settings()

        # Disable button during processing
        self.set_process_enabled(False)
        self.show_progress(0)

        # Start processing thread
        self.processor_thread = AlgorithmProcessorThread(
            self.current_batch_id, settings, self
        )
        self.processor_thread.progress_update.connect(self._on_progress_update)
        self.processor_thread.finished_processing.connect(self._on_processing_finished)
        self.processor_thread.start()

    def _on_progress_update(self, percent, message):
        """Handle progress updates from thread."""
        self.show_progress(percent)  # Updates logic state and local bar

    def _on_processing_finished(self):
        """Handle processing completion."""
        self.set_process_enabled(True)
        self.hide_progress()
        print(f"Processing finished for batch {self.current_batch_id}")

    def set_current_batch(self, batch_id):
        """
        Set the current batch ID for processing.

        Args:
            batch_id: ID of the selected batch
        """
        self.current_batch_id = batch_id

    def get_settings(self):
        """
        Get current settings dari semua algorithm selections.
        """
        return self.logic.get_settings()

    def update_settings(self, settings):
        """
        Receive updated settings from RightPanel.
        """
        self.logic.set_settings(settings)
        # Here we could also update the parameter UI based on selected algorithms

    def set_settings(self, settings):
        """
        Set settings directly (legacy support).
        """
        self.logic.set_settings(settings)

    def show_progress(self, value):
        """
        Update local logic progress state and UI.
        """
        if 0 <= value <= 100:
            self.logic.set_progress(value)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(value)

    def hide_progress(self):
        """Update local logic state to stop and hide UI."""
        self.logic.stop_processing()
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def set_process_enabled(self, enabled):
        """
        Enable/disable process button.
        """
        self.process_btn.setEnabled(enabled)

    # Property to allow worker threads to access database_manager if needed
    @property
    def database_manager(self):
        if self.controller:
            return self.controller.database_manager
        return None
