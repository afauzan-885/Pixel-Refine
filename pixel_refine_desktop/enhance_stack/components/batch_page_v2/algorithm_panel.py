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
    - Two-column layout: ListAlgorithm (left) and ParameterAlgorithm (right)
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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Two-column layout
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(20)

        # --- LEFT COLUMN: ListAlgorithm ---
        left_column = self._create_list_algorithm()
        columns_layout.addWidget(left_column, stretch=1)

        # --- RIGHT COLUMN: ParameterAlgorithm ---
        right_column = self._create_parameter_algorithm()
        columns_layout.addWidget(right_column, stretch=1)

        main_layout.addLayout(columns_layout)

        # --- Progress Bar (Modern Minimalist) ---
        self.progress_bar = ModernProgressBar(
            style="linear", variant="primary", minimalist=True
        )
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        # self.progress_bar.setTextVisible(True) # Not needed for ModernProgressBar
        self.progress_bar.setVisible(False)
        # self.progress_bar.setFixedHeight(20) # Handle internally by minimalist=True
        main_layout.addWidget(self.progress_bar)

        # Removed fixed height to prevent squashing UI elements
        # self.setFixedHeight(187)

    def _create_list_algorithm(self):
        """Create left column with algorithm selection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header = QLabel("List Algorithm")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)

        # Alignment FormGroup
        align_names = self.logic.get_algorithm_names("alignment")
        self.align_form = FormGroup("Alignment", input_type="select")
        self.align_form.add_options(align_names)
        if align_names:
            self.align_form.set_value(align_names[0])
        layout.addWidget(self.align_form)
        self.align_select = self.align_form.input

        # Super Resolution FormGroup
        sr_names = self.logic.get_algorithm_names("super_resolution")
        self.sr_form = FormGroup("Super Resolution", input_type="select")
        self.sr_form.add_options(sr_names)
        if sr_names:
            self.sr_form.set_value(sr_names[0])
        layout.addWidget(self.sr_form)
        self.sr_select = self.sr_form.input

        # Denoising FormGroup
        denoise_names = self.logic.get_algorithm_names("denoising")
        self.denoise_form = FormGroup("Denoising", input_type="select")
        self.denoise_form.add_options(denoise_names)
        if denoise_names:
            self.denoise_form.set_value(denoise_names[0])
        layout.addWidget(self.denoise_form)
        self.denoise_select = self.denoise_form.input

        # Initialize logic with default selections
        self.logic.set_settings(
            {
                "alignment": align_names[0] if align_names else None,
                "super_resolution": sr_names[0] if sr_names else None,
                "denoising": denoise_names[0] if denoise_names else None,
            }
        )

        # Process Button (placed at the bottom of left column)
        self.process_btn = Button("▶ Start", variant="primary")
        self.process_btn.clicked.connect(self._on_process_clicked)
        layout.addWidget(self.process_btn)

        layout.addStretch()
        return widget

    def _create_parameter_algorithm(self):
        """Create right column for algorithm parameters."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
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

        settings = {
            "alignment": self.align_select.currentText(),
            "super_resolution": self.sr_select.currentText(),
            "denoising": self.denoise_select.currentText(),
        }

        # Save settings first (optional but good practice)
        self.logic.set_settings(settings)

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

        # Emit signal for other components that might need it
        # DISABLED to prevent double processing (signal triggers legacy logic)
        # self.process_requested.emit(settings)

    def _on_progress_update(self, percent, message):
        """Handle progress updates from thread."""
        self.show_progress(percent)
        # Could also update a status label with 'message' if available

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
        # print(f"AlgorithmPanel: Current batch set to {batch_id}")

    def get_settings(self):
        """
        Get current settings dari semua algorithm selections.
        """
        return self.logic.get_settings()

    def set_settings(self, settings):
        """
        Set settings untuk semua algorithm selections.
        """
        if self.logic.set_settings(settings):
            # Update UI controls to reflect new settings
            if "alignment" in settings and settings["alignment"]:
                self.align_select.setCurrentText(settings["alignment"])
            if "super_resolution" in settings and settings["super_resolution"]:
                self.sr_select.setCurrentText(settings["super_resolution"])
            if "denoising" in settings and settings["denoising"]:
                self.denoise_select.setCurrentText(settings["denoising"])

    def show_progress(self, value):
        """
        Show progress bar dengan value tertentu.
        """
        if 0 <= value <= 100:
            self.logic.set_progress(value)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(value)

    def hide_progress(self):
        """Hide progress bar."""
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
