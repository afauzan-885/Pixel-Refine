"""
WorkspaceParameterPanel - General Parameter Panel
==================================================
Clone dari enhance_stack AlgorithmPanel UI shell.
Seluruh layout, widget, animasi di-clone tanpa logic spesifik.

UI yang di-clone:
- Parameter stack (QStackedWidget 4 halaman: left, right, both, empty)
- Horizontal slide animation antar halaman
- Progress bar (linear, minimalist)
- Process/Cancel button dengan state machine
- Debounce timer untuk settings changes
- Visibility state signal untuk collapse/expand integration
- Cancel delay timer (1s)
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal, QTimer

from resources.GenericUILibrary import (
    Button,
    ProgressBar as ModernProgressBar,
)
from resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from resources.animations.slide import slide


class WorkspaceParameterPanel(QWidget):
    """
    General parameter panel - UI clone dari enhance_stack AlgorithmPanel.

    Layout Structure:
    ┌──────────────────────────────────────────────┐
    │  Parameter Stack (QStackedWidget)            │
    │  Index 0: Left Column Only                   │
    │  Index 1: Right Column Only                  │
    │  Index 2: Both Columns (side-by-side)        │
    │  Index 3: Empty (initial)                    │
    ├──────────────────────────────────────────────┤
    │  Progress Bar (linear, minimalist)           │
    ├──────────────────────────────────────────────┤
    │  [▶ Start]  /  [✖ Cancel]                   │
    └──────────────────────────────────────────────┘
    """

    # Signals
    process_requested = Signal(dict)
    processing_completed = Signal(dict)
    visibility_state_changed = Signal(bool)

    def __init__(self, controller=None, store=None):
        super().__init__()
        self.controller = controller
        self.store = store
        self.current_batch_id = None
        self._last_target_idx = -1
        self._all_process_buttons = []
        self._is_processing = False

        # Track header labels for retranslate
        self.left_headers = []
        self.left_placeholders = []
        self.right_headers = []
        self.right_placeholders = []

        # Debounce timer
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._do_update_adaptive_ui)
        self._pending_settings = None

        # Cancel delay timer (1s)
        self._cancel_delay_timer = QTimer(self)
        self._cancel_delay_timer.setSingleShot(True)
        self._cancel_delay_timer.timeout.connect(self._enable_cancel_button)

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI dengan parameter stack dan progress bar."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 0, 0)

        # --- Parameter Stack ---
        self.param_stack = QStackedWidget()
        self.param_animator = StackedWidgetAnimator(self.param_stack)
        self.param_stack.setStyleSheet("background-color: transparent;")

        # Page 0: Left Column Only
        self.left_page = self._create_left_column()
        self.param_stack.addWidget(self.left_page)

        # Page 1: Right Column Only
        self.right_page = self._create_right_column()
        self.param_stack.addWidget(self.right_page)

        # Page 2: Both Columns
        self.both_page = QWidget()
        both_layout = QHBoxLayout(self.both_page)
        both_layout.setContentsMargins(0, 0, 0, 0)
        both_layout.setSpacing(20)

        self.left_column_both = self._create_left_column()
        self.right_column_both = self._create_right_column()
        both_layout.addWidget(self.left_column_both, stretch=1)
        both_layout.addWidget(self.right_column_both, stretch=1)
        self.param_stack.addWidget(self.both_page)

        # Page 3: Empty (initial)
        self.empty_page = QWidget()
        self.param_stack.addWidget(self.empty_page)

        self.param_stack.setCurrentIndex(3)  # Start empty

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

        # --- Process Button ---
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.process_btn = Button("▶ Start", variant="primary")
        self.process_btn.setFixedWidth(180)

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

        self.process_btn.clicked.connect(self._on_process_button_clicked)
        btn_layout.addWidget(self.process_btn)
        self._all_process_buttons.append(self.process_btn)
        main_layout.addWidget(btn_container)

    # =========================================================================
    # === COLUMN FACTORY (Subclass override untuk konten spesifik) ===
    # =========================================================================

    def _create_left_column(self) -> QWidget:
        """
        Buat widget kolom kiri parameter.
        Subclass HARUS override untuk isi konten spesifik.
        """
        widget = QWidget()
        widget.setObjectName("paramLeftWidget")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel("LEFT PARAMETERS")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)
        self.left_headers.append(header)

        placeholder = QLabel("Configure left column parameters...")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        self.left_placeholders.append(placeholder)

        layout.addStretch()
        return widget

    def _create_right_column(self) -> QWidget:
        """
        Buat widget kolom kanan parameter.
        Subclass HARUS override untuk isi konten spesifik.
        """
        widget = QWidget()
        widget.setObjectName("paramRightWidget")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel("RIGHT PARAMETERS")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)
        self.right_headers.append(header)

        placeholder = QLabel("Configure right column parameters...")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        self.right_placeholders.append(placeholder)

        layout.addStretch()
        return widget

    # =========================================================================
    # === SETTINGS & ADAPTIVE UI ===
    # =========================================================================

    def get_settings(self) -> dict:
        """Ambil pengaturan saat ini. Subclass HARUS override."""
        return {}

    def set_current_batch(self, batch_id):
        """Set batch/item yang aktif."""
        self.current_batch_id = batch_id
        self._update_timer.stop()
        self._pending_settings = None

    def update_settings(self, settings: dict):
        """Terima settings baru dan trigger adaptive UI dengan debounce."""
        self._pending_settings = settings
        self._update_timer.start(50)

    def update_settings_immediate(self, settings: dict):
        """Bypass debounce untuk immediate update."""
        self._pending_settings = settings
        self._do_update_adaptive_ui()

    def _do_update_adaptive_ui(self):
        """Eksekusi update UI dari debounce timer."""
        if self._pending_settings:
            self._update_adaptive_ui(self._pending_settings)
            self._pending_settings = None

    def _update_adaptive_ui(self, settings: dict):
        """
        Update parameter stack dengan animasi slide horizontal.
        Subclass BISA override untuk logic adaptive yang berbeda.

        Default: mapping berdasarkan _determine_target_index().
        """
        target_idx = self._determine_target_index(settings)
        current_idx = self.param_stack.currentIndex()

        if target_idx != current_idx:
            if self._last_target_idx == target_idx:
                return
            self._last_target_idx = target_idx

            direction = self._determine_slide_direction(current_idx, target_idx)

            slide(
                self.param_animator,
                self.param_stack,
                self.param_stack.widget(target_idx),
                direction,
                duration=400,
            )

        # Notify visibility
        self.visibility_state_changed.emit(target_idx != 3)

    def _determine_target_index(self, settings: dict) -> int:
        """
        Tentukan index target stack. Subclass HARUS override.
        Default return 3 (empty).
        """
        return 3  # Empty

    def _determine_slide_direction(self, current_idx: int, target_idx: int) -> SlideDirection:
        """Tentukan arah slide. BISA override."""
        if target_idx == 2:
            return SlideDirection.LEFT
        elif current_idx == 2:
            if target_idx == 1:
                return SlideDirection.LEFT
            elif target_idx == 0:
                return SlideDirection.RIGHT
        elif current_idx == 3:
            return SlideDirection.LEFT
        elif target_idx == 3:
            return SlideDirection.DOWN
        else:
            return SlideDirection.LEFT if target_idx > current_idx else SlideDirection.RIGHT

    # =========================================================================
    # === PROCESS BUTTON STATE MACHINE ===
    # =========================================================================

    def _on_process_button_clicked(self):
        """Handle process button click. Manage state lock dan cancel."""
        if not self.current_batch_id:
            return

        if self._is_processing:
            self._on_cancel_requested()
            return

        settings = self.get_settings()

        # State lock
        self._is_processing = True
        self._update_all_buttons(enabled=False, text="⏳ Waiting...")

        # Start
        self.show_progress(0)
        self._on_process_clicked(settings)

        # 1s delay sebelum cancel aktif
        self._cancel_delay_timer.start(1000)

    def _enable_cancel_button(self):
        """Dipanggil 1s setelah Start untuk ubah tombol ke Cancel."""
        if self._is_processing:
            self._update_all_buttons(enabled=True, text="✖ Cancel", variant="danger")

    def _on_cancel_requested(self):
        """Handle cancel. Subclass BISA override untuk custom cancel."""
        self._is_processing = False
        self._cancel_delay_timer.stop()
        self._update_all_buttons(enabled=True, text="▶ Start", variant="primary")
        self.hide_progress()

    def _on_process_clicked(self, settings: dict):
        """
        Logic proses. Subclass HARUS override.
        Setelah selesai, panggil self.on_processing_finished().
        """
        self.on_processing_finished()

    def on_processing_finished(self):
        """Dipanggil saat proses selesai. Reset state."""
        self._is_processing = False
        self._cancel_delay_timer.stop()
        self._update_all_buttons(enabled=True, text="▶ Start", variant="primary")
        self.hide_progress()
        completion_data = {
            "batch_id": self.current_batch_id,
            "settings": self.get_settings(),
        }
        self.processing_completed.emit(completion_data)

    def _update_all_buttons(self, enabled=None, text=None, variant=None):
        """Sync semua process button instances."""
        from resources.GenericUILibrary.theme import get_theme, create_button_style
        theme = get_theme()
        for btn in self._all_process_buttons:
            try:
                if enabled is not None:
                    btn.setEnabled(enabled)
                if text is not None:
                    btn.setText(text)
                if variant is not None:
                    btn.variant = variant
                    btn.setObjectName(
                        "deleteButton" if variant == "danger" else "processButton"
                    )
                    btn.setStyleSheet(
                        create_button_style(btn.variant, theme)
                        + """
                        QPushButton {
                            padding: 6px 12px;
                            font-size: 10pt;
                        }
                    """
                    )
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
            except RuntimeError:
                continue

    # =========================================================================
    # === PROGRESS BAR ===
    # =========================================================================

    def show_progress(self, value: int):
        """Tampilkan progress bar."""
        if 0 <= value <= 100:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(value)

    def hide_progress(self):
        """Sembunyikan progress bar."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def set_process_enabled(self, enabled: bool):
        """Enable/disable tombol proses."""
        if hasattr(self, "process_btn"):
            self.process_btn.setEnabled(enabled)

    # =========================================================================
    # === RETRANSLATE & THEME ===
    # =========================================================================

    def retranslate_ui(self):
        """Update semua teks saat language berubah. Subclass BISA override."""
        for btn in self._all_process_buttons:
            try:
                btn.setText("▶ Start")
            except RuntimeError:
                pass
        self.update_theme()

    def update_theme(self):
        """Update tema. Subclass BISA override."""
        pass
