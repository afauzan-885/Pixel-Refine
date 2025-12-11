"""
Algorithm Panel Component - Handles workflow settings and algorithms.
Part of the refactored LeftPanel architecture.

UI Layer only - Logic separated to core/logic/algorithm_logic.py
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    FormGroup,
    Button,
)

# Algorithm logic
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic


class AlgorithmPanel(QWidget):
    """
    Algorithm Panel untuk workflow settings dan parameter konfigurasi.
    
    UI Layer - handles only presentation logic.
    Business logic delegated to AlgorithmLogic.
    
    Features:
    - Tabs untuk berbagai algoritma (Alignment, Denoising, dll)
    - Algorithm selection per category
    - Process button dan progress tracking
    """

    # Signals
    process_requested = Signal(dict)  # Emit settings dict

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.logic = AlgorithmLogic()  # Business logic
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI dengan tabs untuk berbagai algoritma."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- 1. Workflow Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setFixedHeight(250)

        # Tab 1: Alignment & Super Resolution
        self.tabs.addTab(self._create_alignment_tab(), "Alignment & Resolution")

        # Tab 2: Denoising
        self.tabs.addTab(self._create_denoising_tab(), "Denoising")

        main_layout.addWidget(self.tabs)

        # --- 2. Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # --- 3. Process Button ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.process_btn = Button("Start Processing", variant="primary")
        self.process_btn.clicked.connect(self._on_process_clicked)
        btn_layout.addWidget(self.process_btn)

        main_layout.addLayout(btn_layout)

    def _create_alignment_tab(self):
        """Create Alignment and Super Resolution settings tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(20)

        # Group 1: Alignment
        align_names = self.logic.get_algorithm_names('alignment')
        self.align_form = FormGroup("Alignment Method", input_type="select")
        self.align_form.add_options(align_names)
        if align_names:
            self.align_form.set_value(align_names[0])
        layout.addWidget(self.align_form)
        self.align_select = self.align_form.input

        # Group 2: Super Resolution
        sr_names = self.logic.get_algorithm_names('super_resolution')
        self.sr_form = FormGroup("Super Resolution", input_type="select")
        self.sr_form.add_options(sr_names)
        if sr_names:
            self.sr_form.set_value(sr_names[0])
        layout.addWidget(self.sr_form)
        self.sr_select = self.sr_form.input

        layout.addStretch()
        # Initialize logic with default selections
        self.logic.set_settings({
            'alignment': align_names[0] if align_names else None,
            'super_resolution': sr_names[0] if sr_names else None,
            'denoising': None,
        })
        return widget

    def _create_denoising_tab(self):
        """Create Denoising settings tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(20)

        # Denoising
        denoise_names = self.logic.get_algorithm_names('denoising')
        self.denoise_form = FormGroup("Denoising", input_type="select")
        self.denoise_form.add_options(denoise_names)
        if denoise_names:
            self.denoise_form.set_value(denoise_names[0])
        layout.addWidget(self.denoise_form)
        self.denoise_select = self.denoise_form.input

        layout.addStretch()
        return widget

    def _on_process_clicked(self):
        """
        Collect settings dari semua tabs dan emit signal untuk processing.
        """
        settings = {
            "alignment": self.align_select.currentText(),
            "super_resolution": self.sr_select.currentText(),
            "denoising": self.denoise_select.currentText(),
        }
        
        # Validate and emit
        if self.logic.set_settings(settings):
            self.process_requested.emit(settings)

    def get_settings(self):
        """
        Get current settings dari semua algorithm selections.
        
        Returns:
            dict: Settings dictionary dengan format:
                {
                    "alignment": str,
                    "super_resolution": str,
                    "denoising": str
                }
        """
        return self.logic.get_settings()

    def set_settings(self, settings):
        """
        Set settings untuk semua algorithm selections.
        
        Args:
            settings (dict): Settings dictionary dengan format:
                {
                    "alignment": str,
                    "super_resolution": str,
                    "denoising": str
                }
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
        
        Args:
            value (int): Progress value (0-100)
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
        
        Args:
            enabled (bool): True untuk enable, False untuk disable
        """
        self.process_btn.setEnabled(enabled)
