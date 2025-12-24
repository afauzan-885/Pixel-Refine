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
    QStackedWidget,
)
from PySide6.QtCore import QThread, Qt, Signal, QTimer

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    FormGroup,
    Button,
    ProgressBar as ModernProgressBar,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.mixins import SyncMixin

# Algorithm logic
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic

# Animation support
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from pixel_refine_desktop.ui.resources.animations.slide import slide

# Import AlgorithmProcessorThread from core logic
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_processor import (
    AlgorithmProcessorThread,
)


class AlgorithmPanel(QWidget, SyncMixin):
    """
    Algorithm Panel untuk workflow settings dan parameter konfigurasi.

    Features:
    - Adaptive layout using QStackedWidget for parameter sections
    - Smooth horizontal animations (Slide)
    - Auto-collapse integration via visibility signals
    """

    # Signals
    process_requested = Signal(dict)  # Emit settings dict
    processing_completed = Signal(dict)  # Emit completion data
    visibility_state_changed = Signal(
        bool
    )  # Emit True if any parameter column is visible

    def __init__(self, controller=None, store=None):
        super().__init__()
        self.controller = controller
        self.logic = AlgorithmLogic()  # Business logic
        self.current_batch_id = None  # Track selected batch
        self.processor_thread = None
        self._last_target_idx = -1  # Guard for redundant animations

        # Debounce timer for rapid setting changes
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._do_update_adaptive_ui)
        self._pending_settings = None

        # Real-time state binding
        if store:
            self.bind_store(store)

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI dengan adaptive parameter stack."""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 0, 0)

        # --- CONTENT STACK for Parameters ---
        self.param_stack = QStackedWidget()
        self.param_animator = StackedWidgetAnimator(self.param_stack)
        self.param_stack.setStyleSheet("background-color: transparent;")

        # Page 0: Alignment Only (100% width)
        self.align_page = self._create_parameter_alignment()
        self.param_stack.addWidget(self.align_page)

        # Page 1: Algorithm Only (100% width)
        self.algo_page = self._create_parameter_algorithm()
        self.param_stack.addWidget(self.algo_page)

        # Page 2: Both
        self.both_page = QWidget()
        both_layout = QHBoxLayout(self.both_page)
        both_layout.setContentsMargins(0, 0, 0, 0)
        both_layout.setSpacing(20)

        # Create separate instances for the 'both' view
        self.left_column_both = self._create_parameter_alignment()
        self.right_column_both = self._create_parameter_algorithm()
        both_layout.addWidget(self.left_column_both, stretch=1)
        both_layout.addWidget(self.right_column_both, stretch=1)
        self.param_stack.addWidget(self.both_page)

        # Page 3: Empty (Initial/None)
        self.empty_page = QWidget()
        self.param_stack.addWidget(self.empty_page)

        # Start at empty
        self.param_stack.setCurrentIndex(3)

        main_layout.addWidget(self.param_stack)

        # --- Progress Bar ---
        self.progress_container = QWidget()
        self.progress_container.setFixedHeight(4)
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
        """Create column for alignment parameters."""
        widget = QWidget()
        widget.setObjectName("paramAlignWidget")
        widget.setStyleSheet("#paramAlignWidget { background-color: #FFFFFF; }")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel("Parameter Alignment")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)

        placeholder = QLabel("Alignment parameters will\nappear here")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()
        return widget

    def _create_parameter_algorithm(self):
        """Create column for algorithm parameters."""
        widget = QWidget()
        widget.setObjectName("paramAlgoWidget")
        widget.setStyleSheet("#paramAlgoWidget { background-color: #FFFFFF; }")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel("Parameter Algorithm")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)

        placeholder = QLabel("Parameters will appear here\nbased on selected algorithm")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        # Process Button (Optimized size)
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.process_btn = Button(
            "▶ Start",
            variant="primary",
            bg_color="#2ECC71",
            text_color="#FFFFFF",
            hover_color="#28B463",
        )
        self.process_btn.setFixedWidth(180)  # Make it smaller and elegant
        self.process_btn.setStyleSheet(
            self.process_btn.styleSheet()
            + """
            QPushButton {
                padding: 6px 12px;
                font-size: 10pt;
            }
        """
        )

        self.process_btn.clicked.connect(self._on_process_clicked)
        btn_layout.addWidget(self.process_btn)
        layout.addWidget(btn_container)

        layout.addStretch()
        return widget

    def _on_process_clicked(self):
        if not self.current_batch_id:
            return
        settings = self.logic.get_settings()
        self.set_process_enabled(False)
        self.show_progress(0)
        self.processor_thread = AlgorithmProcessorThread(
            self.current_batch_id, settings, self
        )
        self.processor_thread.progress_update.connect(self._on_progress_update)
        self.processor_thread.finished_processing.connect(self._on_processing_finished)
        self.processor_thread.start()

    def _on_progress_update(self, percent, message):
        self.show_progress(percent)

    def _on_processing_finished(self):
        self.set_process_enabled(True)
        self.hide_progress()
        completion_data = {
            "batch_id": self.current_batch_id,
            "settings": self.get_settings(),
        }
        self.processing_completed.emit(completion_data)

    def set_current_batch(self, batch_id):
        self.current_batch_id = batch_id
        self._update_timer.stop()
        self._pending_settings = None

        # Set scope for SyncMixin
        self.set_scope(str(batch_id))

        # Initial sync is handled automatically by SyncMixin when scope changes?
        # No, we need to trigger it manually after scope change if we want immediate effect
        self.on_store_changed(None, self.get_data())

    def get_settings(self):
        return self.logic.get_settings()

    def _setup_bindings(self):
        """Setup declarative bindings for the algorithm panel."""
        # Note: AlgorithmPanel doesn't have direct input widgets to bind TO,
        # but it has logic that needs to be triggered.
        # We'll use virtual properties or just keep the simplified on_store_changed.
        # Actually, for AlgorithmPanel, it's easier to just fix on_store_changed.
        pass

    def on_store_changed(self, key, value):
        """React to store changes with fallback support."""
        if not self.current_batch_id:
            return

        str_id = str(self.current_batch_id)

        # 1. Handle scope-specific updates
        if (
            key is None
            or key == str_id
            or (isinstance(key, str) and key.startswith(f"{str_id}."))
        ):
            # Get data with fallbacks manually if not using add_binding
            all_settings = self.get_data(str_id)
            if not all_settings or not isinstance(all_settings, dict):
                all_settings = {}

            ui_settings = {
                "alignment": (
                    all_settings.get("alignment_algo", "No Alignment")
                    if all_settings.get("checkbox_align_images", False)
                    else "No Alignment"
                ),
                "super_resolution": (
                    all_settings.get("super_resolution_algo", "No Super Resolution")
                    if all_settings.get("checkbox_super_resolution", False)
                    else "No Super Resolution"
                ),
                "denoising": (
                    all_settings.get("denoising_algo", "No Denoising")
                    if all_settings.get("checkbox_denoising", False)
                    else "No Denoising"
                ),
            }
            # Update the UI
            self.update_settings(ui_settings)

    def update_settings(self, settings):
        """Receive updated settings and trigger adaptive UI with debounce."""
        self.logic.set_settings(settings)
        self._pending_settings = settings
        self._update_timer.start(50)  # Small delay for state stability

    def _do_update_adaptive_ui(self):
        """Perform the actual UI update from debounced timer."""
        if self._pending_settings:
            self._update_adaptive_ui(self._pending_settings)
            self._pending_settings = None

    def update_settings_immediate(self, settings):
        """Bypass debounce for immediate initialization."""
        self.logic.set_settings(settings)
        self._update_adaptive_ui(settings)

    def _update_adaptive_ui(self, settings):
        """Update parameter stack with horizontal slide animation."""
        alignment = str(settings.get("alignment", "")).strip()
        denoising = str(settings.get("denoising", "")).strip()
        super_res = str(settings.get("super_resolution", "")).strip()

        none_values = [
            "",
            "None",
            "No Alignment",
            "No Denoising",
            "No Super Resolution",
        ]
        is_align_active = alignment not in none_values
        is_algo_active = (denoising not in none_values) or (
            super_res not in none_values
        )

        # Map to stack indices: 0: Align, 1: Algo, 2: Both, 3: Empty
        target_idx = 3
        if is_align_active and is_algo_active:
            target_idx = 2
        elif is_align_active:
            target_idx = 0
        elif is_algo_active:
            target_idx = 1

        current_idx = self.param_stack.currentIndex()
        if target_idx != current_idx:
            # Skip if we already started an animation for this target
            if self._last_target_idx == target_idx:
                return
            self._last_target_idx = target_idx

            # User Specific Rules for horizontal push/pull effect:
            # 1. Any -> Both (2): SLIDE_LEFT (expand to right)
            # 2. Both (2) -> Algo Only (1): SLIDE_LEFT (push alignment out to left)
            # 3. Both (2) -> Align Only (0): SLIDE_RIGHT (push algorithm out to right)
            # 4. None (3) -> Any: Direction based on position or SLIDE_LEFT default

            direction = SlideDirection.LEFT  # Default

            if target_idx == 2:  # Moving to Both
                direction = SlideDirection.LEFT
            elif current_idx == 2:  # Moving FROM Both
                if target_idx == 1:  # Moving to Algo Only
                    direction = SlideDirection.LEFT
                elif target_idx == 0:  # Moving to Align Only
                    direction = SlideDirection.RIGHT
            elif current_idx == 3:  # From Empty
                direction = SlideDirection.LEFT
            elif target_idx == 3:  # To Empty
                direction = SlideDirection.DOWN
            else:
                # Switching single views
                direction = (
                    SlideDirection.LEFT
                    if target_idx > current_idx
                    else SlideDirection.RIGHT
                )

            slide(
                self.param_animator,
                self.param_stack,
                self.param_stack.widget(target_idx),
                direction,
                duration=400,
            )

        # Notify LeftPanel about overall visibility (expanded/collapsed)
        self.visibility_state_changed.emit(target_idx != 3)

    def set_settings(self, settings):
        self.logic.set_settings(settings)
        self._update_adaptive_ui(settings)

    def show_progress(self, value):
        if 0 <= value <= 100:
            self.logic.set_progress(value)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(value)

    def hide_progress(self):
        self.logic.stop_processing()
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def set_process_enabled(self, enabled):
        if hasattr(self, "process_btn"):
            self.process_btn.setEnabled(enabled)

    @property
    def database_manager(self):
        if self.controller:
            return self.controller.database_manager
        return None
