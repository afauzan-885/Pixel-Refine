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
    QSizePolicy,
)
from PySide6.QtCore import QThread, Qt, Signal, QTimer
import config

# Generic UI Library
from resources.GenericUILibrary import (
    FormGroup,
    Button,
    ProgressBar as ModernProgressBar,
)
from resources.GenericUILibrary.mixins import SyncMixin

# Algorithm logic
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic

# Animation support
from resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from resources.animations.slide import slide

# Import AlgorithmProcessorThread from core logic
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_processor import (
    AlgorithmProcessorThread,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


from resources.GenericUILibrary import live_update


@live_update
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
        self._all_process_buttons = []  # Track all instances for dual-mode sync
        self.align_headers = []
        self.align_placeholders = []
        self.algo_headers = []
        self.algo_placeholders = []

        # Debounce timer for rapid setting changes
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        # Keep adaptive controls responsive when the denoising selector
        # changes.  Persistence remains debounced separately in RightPanel.
        self._update_timer.setInterval(40)
        self._update_timer.timeout.connect(self._do_update_adaptive_ui)
        self._pending_settings = None
        self._is_processing = False

        # Timer for 1s delay before Cancel becomes active
        self._cancel_delay_timer = QTimer(self)
        self._cancel_delay_timer.setSingleShot(True)
        self._cancel_delay_timer.timeout.connect(self._enable_cancel_button)

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
        self.progress_container.setObjectName("progressContainer")
        self.progress_container.setFixedHeight(4)

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
        widget.setVisible(False)
        widget.setMaximumHeight(0)
        widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel(language_config.LBL_PARAMETER_ALIGNMENT)
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)
        self.align_headers.append(header)

        placeholder = QLabel(language_config.LBL_ALIGNMENT_PLACEHOLDER)
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        self.align_placeholders.append(placeholder)

        layout.addStretch()
        return widget

    def _create_parameter_algorithm(self):
        """Create column for algorithm parameters."""
        widget = QWidget()
        widget.setObjectName("paramAlgoWidget")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel(language_config.LBL_PARAMETER_ALGORITHM)
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)
        self.algo_headers.append(header)

        placeholder = QLabel(language_config.LBL_ALGORITHM_PLACEHOLDER)
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        self.algo_placeholders.append(placeholder)

        # Process Button (Optimized size)
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.process_btn = Button(
            f"▶ {language_config.BTN_START}",
            variant="primary",
        )
        self.process_btn.setFixedWidth(180)  # Make it smaller and elegant
        
        from resources.GenericUILibrary.theme import get_theme, create_button_style
        theme = get_theme()
        self.process_btn.setStyleSheet(
            create_button_style(self.process_btn.variant, theme)
            + """
            QPushButton {
                padding: 6px 12px;
                font-size: 10pt;
            }
        """
        )

        self.process_btn.clicked.connect(self._on_process_clicked)
        btn_layout.addWidget(self.process_btn)
        self._all_process_buttons.append(self.process_btn)  # Track instance
        layout.addWidget(btn_container)

        layout.addStretch()
        return widget

    def _on_process_clicked(self):
        if not self.current_batch_id:
            return

        # If already processing, this button is now "Cancel"
        if self._is_processing:
            self._on_cancel_requested()
            return

        settings = self.logic.get_settings()

        # 1. State lock
        self._is_processing = True
        self._update_all_buttons(enabled=False, text="⏳ Waiting...")

        # --- Show Loading Toast at Bottom Left ---
        active_algos = []
        if settings.get("alignment") and settings.get("alignment") != "No Alignment":
            active_algos.append(f"Penyelarasan ({settings['alignment']})")
        if settings.get("denoising") and settings.get("denoising") != "No Denoising":
            active_algos.append(f"Denoising ({settings['denoising']})")
        if settings.get("super_resolution") and settings.get("super_resolution") != "No Super Resolution":
            active_algos.append(f"Super Resolusi ({settings['super_resolution']})")

        msg = ", ".join(active_algos) if active_algos else "Memproses batch"
        
        if hasattr(self, "display_panel") and self.display_panel and hasattr(self.display_panel, "toast"):
            from resources.animations.toast.toast_manager import ToastPosition
            self.display_panel.toast.show_progress(
                message=msg + " (0%)",
                category="process_loading",
                position=ToastPosition.BOTTOM_LEFT,
                priority="HIGH"
            )

        # 2. Start Processing
        self.show_progress(0)
        self.processor_thread = AlgorithmProcessorThread(
            self.current_batch_id, settings, self
        )
        self.processor_thread.progress_update.connect(self._on_progress_update)
        self.processor_thread.finished_processing.connect(self._on_processing_finished)
        self.processor_thread.start()

        # 3. Start timer for Cancel button (1s delay)
        self._cancel_delay_timer.start(1000)

    def _enable_cancel_button(self):
        """Called 1s after Start to turn button into Cancel."""
        if self._is_processing:
            self._update_all_buttons(
                enabled=True,
                text="✖ Cancel",
                variant="danger",
            )

    def _on_cancel_requested(self):
        """Handle cancellation logic."""
        if self.processor_thread and self.processor_thread.isRunning():
            print(
                f"[AlgorithmPanel] Cancellation requested for batch {self.current_batch_id}"
            )
            self.processor_thread.stop()
            # Button feedback
            self._update_all_buttons(enabled=False, text="🛑 Stopping...")
            
            # Hide loading toast
            if hasattr(self, "display_panel") and self.display_panel and hasattr(self.display_panel, "toast"):
                self.display_panel.toast.hide_category("process_loading")
            # We don't reset state here, wait for finished_processing signal

    def _update_all_buttons(
        self, enabled=None, text=None, variant=None, bg=None, hover=None
    ):
        """Helper to sync all process button instances."""
        from resources.GenericUILibrary.theme import get_theme
        theme = get_theme()
        for btn in self._all_process_buttons:
            try:
                if enabled is not None:
                    btn.setEnabled(enabled)
                if text is not None:
                    btn.setText(text)
                if variant is not None:
                    btn.variant = variant
                    # Update objectName to match the correct QSS selector for dynamic styling
                    btn.setObjectName("deleteButton" if variant == "danger" else "processButton")
                    from resources.GenericUILibrary.theme import get_theme, create_button_style
                    theme = get_theme()
                    is_display_start = hasattr(self, "display_panel") and self.display_panel and btn == self.display_panel.start_btn_ref
                    padding_val = "5px" if is_display_start else "6px 12px"
                    btn.setStyleSheet(
                        create_button_style(btn.variant, theme)
                        + f"""
                        QPushButton {{
                            padding: {padding_val};
                            font-size: 10pt;
                        }}
                        """
                    )
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
                if bg or hover:
                    btn._apply_custom_colors(bg_color=bg, hover_color=hover)
            except RuntimeError:
                continue  # Widget might be deleted

    def _on_progress_update(self, percent, message):
        # Determine active category name based on settings
        settings = self.logic.get_settings()
        active_stages = []
        if settings.get("alignment") and settings.get("alignment") != "No Alignment":
            active_stages.append("alignment")
        if settings.get("denoising") and settings.get("denoising") != "No Denoising":
            active_stages.append("denoising")
        if settings.get("super_resolution") and settings.get("super_resolution") != "No Super Resolution":
            active_stages.append("super_resolution")
            
        total_stages = len(active_stages) if active_stages else 1

        # We can track the current stage index
        current_stage_idx = 0
        display_msg = "Memproses"
        stage_percent = percent

        if "||" in message:
            # Format: message||description
            parts = message.split("||")
            total_img_str = parts[0]
            desc_text = parts[1] if len(parts) > 1 else ""
            
            # Since this is alignment:
            current_stage_idx = active_stages.index("alignment") if "alignment" in active_stages else 0
            
            try:
                total_imgs = int(total_img_str)
                completed_imgs = percent
                stage_percent = int((completed_imgs / total_imgs) * 100)
                display_msg = f"Menyelaraskan gambar {completed_imgs}/{total_imgs}"
            except Exception:
                display_msg = desc_text if desc_text else "Menyelaraskan gambar"
        else:
            # Determine stage based on message text
            if "super-resolution" in message.lower() or "super" in message.lower():
                current_stage_idx = active_stages.index("super_resolution") if "super_resolution" in active_stages else 0
                display_msg = "Super resolusi"
            else:
                current_stage_idx = active_stages.index("denoising") if "denoising" in active_stages else 0
                display_msg = "Mengurangi noise gambar"

            # Parse processed tiles from tile message if possible to show e.g. "Denoising 3/4"
            # format: "Merging tile 73354/103788..." or "Processing super-resolution tile 5/10..."
            import re
            tile_match = re.search(r"(\d+)/(\d+)", message)
            if tile_match:
                # We show the progress of tiles
                display_msg = f"{display_msg} (tile {tile_match.group(1)}/{tile_match.group(2)})"
            else:
                # Fallback to image counts
                total_imgs = 0
                if hasattr(self, "display_panel") and self.display_panel and hasattr(self.display_panel, "logic") and self.display_panel.logic.current_images:
                    total_imgs = len(self.display_panel.logic.current_images)
                if total_imgs > 0:
                    display_msg = f"{display_msg} {total_imgs}/{total_imgs}"

        # Global percentage calculation
        stage_percent = max(0, min(100, stage_percent))
        actual_percent = int((current_stage_idx * 100 + stage_percent) / total_stages)
        actual_percent = max(0, min(100, actual_percent))

        self.show_progress(actual_percent)
        
        if hasattr(self, "display_panel") and self.display_panel and hasattr(self.display_panel, "toast"):
            from resources.animations.toast.toast_manager import ToastPosition
            self.display_panel.toast.show_progress(
                message=f"{display_msg} ({actual_percent}%)",
                category="process_loading",
                position=ToastPosition.BOTTOM_LEFT,
                priority="HIGH"
            )

    def _on_processing_finished(self):
        self._is_processing = False
        self._cancel_delay_timer.stop()

        self._update_all_buttons(enabled=True, text="▶ Start", variant="primary")

        self.hide_progress()
        
        # Hide loading toast and show process finished message
        if hasattr(self, "display_panel") and self.display_panel and hasattr(self.display_panel, "toast"):
            from resources.animations.toast.toast_manager import ToastPosition
            self.display_panel.toast.hide_category("process_loading")
            self.display_panel.toast.show_message(
                message="Proses selesai dengan sukses!",
                duration=3000,
                position=ToastPosition.BOTTOM_LEFT,
                priority="NORMAL"
            )

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
                config.KEY_ALIGNMENT: (
                    all_settings.get(config.KEY_ALIGNMENT_ALGO, "No Alignment")
                    if all_settings.get(config.KEY_CHECKBOX_ALIGN, False)
                    else "No Alignment"
                ),
                config.KEY_SUPER_RESOLUTION: (
                    all_settings.get(config.KEY_SUPER_RESOLUTION_ALGO, "No Super Resolution")
                    if all_settings.get(config.KEY_CHECKBOX_SUPER_RES, False)
                    else "No Super Resolution"
                ),
                config.KEY_DENOISING: (
                    all_settings.get(config.KEY_DENOISING_ALGO, "No Denoising")
                    if all_settings.get(config.KEY_CHECKBOX_DENOISING, False)
                    else "No Denoising"
                ),
                config.KEY_CHECKBOX_ALIGN: bool(
                    all_settings.get(config.KEY_CHECKBOX_ALIGN, False)
                ),
                config.KEY_CHECKBOX_SUPER_RES: bool(
                    all_settings.get(config.KEY_CHECKBOX_SUPER_RES, False)
                ),
                config.KEY_CHECKBOX_DENOISING: bool(
                    all_settings.get(config.KEY_CHECKBOX_DENOISING, False)
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

        # Relocate the Start button when the selected stage can be launched
        # directly.  Average/Median/Similarity have no parameter page, and
        # splattingSR follows the same contract: alignment is owned by its
        # internal block-matching stage and therefore does not require an
        # external parameter panel before starting.
        is_no_algo_panel = denoising in [
            "Average",
            "Median",
            "Similarity",
            "Similarity Fusion",
        ] or super_res not in ["", "None", "No Super Resolution"]
        for btn in self._all_process_buttons:
            if hasattr(self, "display_panel") and self.display_panel and btn == self.display_panel.start_btn_ref:
                continue
            btn.setVisible(not is_no_algo_panel)
            
        if hasattr(self, "display_panel") and self.display_panel:
            self.display_panel.set_start_button_mode(is_no_algo_panel)

        none_values = [
            "",
            "None",
            "No Alignment",
            "No Denoising",
            "No Super Resolution",
        ]
        is_align_active = alignment not in none_values
        is_algo_active = (
            denoising not in none_values
            and denoising
            not in ["Average", "Median", "Similarity", "Similarity Fusion"]
        ) or (
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
                duration=100,
            )

        # The visible parameter surface has moved to SwitchableParameterPanel.
        # Keep this legacy AlgorithmPanel collapsed so it never pushes the
        # DisplayPanel upward when settings are saved or refreshed.
        self.visibility_state_changed.emit(False)

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

    def retranslate_ui(self):
        """Update all text dynamically when language changes."""
        # 1. Update alignment headers and placeholders
        for header in self.align_headers:
            try:
                header.setText(language_config.LBL_PARAMETER_ALIGNMENT)
            except RuntimeError:
                pass
        for placeholder in self.align_placeholders:
            try:
                placeholder.setText(language_config.LBL_ALIGNMENT_PLACEHOLDER)
            except RuntimeError:
                pass

        # 2. Update algorithm headers and placeholders
        for header in self.algo_headers:
            try:
                header.setText(language_config.LBL_PARAMETER_ALGORITHM)
            except RuntimeError:
                pass
        for placeholder in self.algo_placeholders:
            try:
                placeholder.setText(language_config.LBL_ALGORITHM_PLACEHOLDER)
            except RuntimeError:
                pass

        # 3. Update process buttons
        for btn in self._all_process_buttons:
            try:
                btn.setText(f"▶ {language_config.BTN_START}")
            except RuntimeError:
                pass

        # 4. Update theme
        self.update_theme()

    def update_theme(self):
        """Update stylesheets of child widgets dynamically when theme changes."""
        from resources.styles.stylesheet import SLIDER_STYLE, SLIDER_VALUE_LABEL, VALUE_EDIT_LABEL
        from PySide6.QtWidgets import QSlider, QLabel, QLineEdit

        # Re-apply styles for QSliders and their value labels/edits
        for slider in self.findChildren(QSlider):
            try:
                slider.setStyleSheet(SLIDER_STYLE)
            except RuntimeError:
                pass

        for label in self.findChildren(QLabel):
            try:
                if label.styleSheet() and "min-width: 40px" in label.styleSheet():
                    label.setStyleSheet(SLIDER_VALUE_LABEL)
            except RuntimeError:
                pass

        for edit in self.findChildren(QLineEdit):
            try:
                if edit.styleSheet() and "min-width: 40px" in edit.styleSheet():
                    edit.setStyleSheet(VALUE_EDIT_LABEL)
            except RuntimeError:
                pass

