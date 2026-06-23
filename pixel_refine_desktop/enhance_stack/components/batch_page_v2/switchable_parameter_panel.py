import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
    QComboBox,
    QLabel,
    QScrollArea,
    QSizePolicy,
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from resources.GenericUILibrary import live_update

# Import parameter pages
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.light_glue_parameter_settings import (
    get_light_glue_page
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.farneback_parameter_settings import (
    get_farneback_optical_flow_page
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.akaze_parameter_settings import (
    get_akaze_page
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.orb_parameter_settings import (
    get_orb_page
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.MFDenoiser_parameter_settings import (
    get_mfdenoiser_settings_page
)

# Colors
COLOR_ALIGNMENT_RED = "#E74C3C"      # Premium calm red
COLOR_DENOISING_GREEN = "#2ECC71"    # Premium calm green
COLOR_INACTIVE_TAB = "#BDC3C7"       # Muted gray for inactive state
COLOR_BACKGROUND = "#FFFFFF"

@live_update("refresh_responsive_layout", on_resize=True)
class SwitchableParameterPanel(QWidget):
    """
    Custom Parameter Panel matching the approved implementation plan.
    Features:
    - Vertical tabs on the right side: Red (Alignment) and Green (Denoising).
    - Border matches the active tab's color.
    - Alignment: Dropdown to select algorithm + dynamic parameters below.
    - Denoising: Specifically displays Similarity parameters.
    - Visibility logic: Denoising tab hidden if average/median selected.
    """
    settings_changed = Signal()

    def __init__(self, parent=None, store=None):
        super().__init__(parent)
        self.setObjectName("SwitchableParameterPanel")
        self.store = store
        self.active_tab = None # None initially, neither tab active
        self.current_denoising_algo = "No Denoising"
        self._last_settings_snapshot = None
        self._resize_sync_pending = False
        self._setup_ui()
        self.set_expanded(False)
        self._update_styles("transparent")

    def set_expanded(self, expanded):
        if self.content_wrapper.isVisible() == expanded:
            return

        self.content_wrapper.setVisible(expanded)
        if expanded:
            width, height = self._expanded_size()
            self.setMinimumSize(width, height)
            self.setMaximumSize(width, height)
        else:
            # Keep the collapsed tab rail deterministic so OverlayContainer does
            # not reuse a stale expanded geometry during rapid setting changes.
            self.setMinimumSize(50, self._collapsed_height())
            self.setMaximumSize(50, self._collapsed_height())
        
        self.updateGeometry()
        self.adjustSize()

        # Trigger parent OverlayContainer size adjustment after Qt has applied
        # the new size constraints.
        overlay = self.get_overlay_container()
        if overlay:
            QTimer.singleShot(0, self._sync_overlay_geometry)

    def _collapsed_height(self):
        visible_buttons = sum(
            1
            for button in (self.btn_align_tab, self.btn_denoise_tab)
            if button.isVisible()
        )
        return max(60, (visible_buttons * 50) + 20)

    def _expanded_size(self):
        parent = self.get_overlay_container()
        if parent:
            parent_widget = parent.parent()
        else:
            parent_widget = self.parent()

        available_w = parent_widget.width() if parent_widget else 1200
        available_h = parent_widget.height() if parent_widget else 800

        width_cap = max(240, available_w - 20)
        height_cap = max(240, available_h - 70)
        width = max(240, min(520, int(available_w * 0.42), width_cap))
        height = max(240, min(640, height_cap))
        return width, height

    def _sync_overlay_geometry(self):
        overlay = self.get_overlay_container()
        if overlay:
            if self.content_wrapper.isVisible():
                width, height = self._expanded_size()
                self.setMinimumSize(width, height)
                self.setMaximumSize(width, height)
            self.adjustSize()
            overlay.content_wrapper.adjustSize()
            overlay.adjustSize()
            overlay._update_position()

    def _setup_ui(self):
        # Main layout is horizontal: Content area (left) + Tabs (right)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main widget background transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # 1. Content Wrapper (Left)
        self.content_wrapper = QWidget()
        self.content_wrapper.setObjectName("ParamContentWrapper")
        self.content_layout = QVBoxLayout(self.content_wrapper)
        self.content_layout.setContentsMargins(14, 14, 14, 14)
        self.content_layout.setSpacing(8)

        # Content stacked widget
        self.content_stack = QStackedWidget()
        
        # Build pages
        self._setup_alignment_page()
        self._setup_denoising_page()

        self.content_layout.addWidget(self.content_stack)
        self.main_layout.addWidget(self.content_wrapper, 1)

        # 2. Tabs Sidebar (Right)
        self.tabs_sidebar = QWidget()
        self.tabs_sidebar.setFixedWidth(50)
        # Transparent background for the sidebar
        self.tabs_sidebar.setStyleSheet("background: transparent; border: none;")
        self.tabs_layout = QVBoxLayout(self.tabs_sidebar)
        self.tabs_layout.setContentsMargins(0, 10, 0, 10)
        self.tabs_layout.setSpacing(10)
        self.tabs_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        # Alignment Tab Button (Red)
        self.btn_align_tab = QPushButton("A")
        self.btn_align_tab.setToolTip("Alignment Parameters")
        self.btn_align_tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_align_tab.setFixedSize(40, 40)
        self.btn_align_tab.clicked.connect(lambda: self.set_active_tab("alignment"))
        self.tabs_layout.addWidget(self.btn_align_tab)

        # Denoising Tab Button (Green)
        self.btn_denoise_tab = QPushButton("D")
        self.btn_denoise_tab.setToolTip("Denoising Parameters")
        self.btn_denoise_tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_denoise_tab.setFixedSize(40, 40)
        self.btn_denoise_tab.clicked.connect(lambda: self.set_active_tab("denoising"))
        self.tabs_layout.addWidget(self.btn_denoise_tab)

        self.main_layout.addWidget(self.tabs_sidebar)

        # Minimum Panel Size
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(50, 100)

    def refresh_responsive_layout(self):
        if not self.content_wrapper.isVisible():
            self._sync_overlay_geometry()
            return
        self._apply_adaptive_density()
        if not self._resize_sync_pending:
            self._resize_sync_pending = True
            QTimer.singleShot(0, self._flush_resize_sync)

    def _flush_resize_sync(self):
        self._resize_sync_pending = False
        self._sync_overlay_geometry()

    def _apply_adaptive_density(self):
        width = self.width()
        compact = width < 380
        margin = 10 if compact else 14
        spacing = 6 if compact else 8
        self.content_layout.setContentsMargins(margin, margin, margin, margin)
        self.content_layout.setSpacing(spacing)
        self.align_dropdown_label.setFont(
            QFont("Arial", 9 if compact else 10, QFont.Weight.Bold)
        )
        denoise_page = self.denoise_page_container.widget() if isinstance(self.denoise_page_container, QScrollArea) else None
        if denoise_page and hasattr(denoise_page, "refresh_responsive_layout"):
            denoise_page.refresh_responsive_layout()

    def _setup_alignment_page(self):
        self.align_page = QWidget()
        align_layout = QVBoxLayout(self.align_page)
        align_layout.setContentsMargins(0, 0, 0, 0)
        align_layout.setSpacing(10)

        # Dropdown selection for Alignment algorithm
        self.align_dropdown_label = QLabel("Alignment Algorithm:")
        self.align_dropdown_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.align_dropdown = QComboBox()
        self.align_dropdown.addItems([
            "No Alignment",
            "Farneback Optical Flow",
            "Light Glue",
            "AKAZE",
            "ORB"
        ])
        self.align_dropdown.currentIndexChanged.connect(self._on_alignment_algo_changed)

        align_layout.addWidget(self.align_dropdown_label)
        align_layout.addWidget(self.align_dropdown)

        # Stacked widget for alignment parameter settings pages
        self.align_param_stack = QStackedWidget()

        # Build individual parameter pages
        # Index 0: No Alignment (placeholder)
        self.none_align_page = QLabel("No alignment parameters to configure.")
        self.none_align_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.none_align_page.setStyleSheet("color: #7F8C8D; font-style: italic;")
        self.align_param_stack.addWidget(self.none_align_page)

        # Index 1: Farneback
        self.farneback_page = get_farneback_optical_flow_page()
        self.align_param_stack.addWidget(self.farneback_page)

        # Index 2: Light Glue
        self.light_glue_page = get_light_glue_page()
        self.align_param_stack.addWidget(self.light_glue_page)

        # Index 3: AKAZE
        self.akaze_page = get_akaze_page()
        self.align_param_stack.addWidget(self.akaze_page)

        # Index 4: ORB
        self.orb_page = get_orb_page()
        self.align_param_stack.addWidget(self.orb_page)

        align_layout.addWidget(self.align_param_stack, 1)
        self.content_stack.addWidget(self.align_page)

    def _setup_denoising_page(self):
        # We reuse the get_mfdenoiser_settings_page but hide the tab widget tab bar
        # so that it specifically displays only the Similarity parameters.
        self.denoise_page_container = get_mfdenoiser_settings_page()
        
        # Retrieve the inner page and hide tab bar
        inner_scroll = self.denoise_page_container
        if isinstance(inner_scroll, QScrollArea) and inner_scroll.widget():
            inner_page = inner_scroll.widget()
            if hasattr(inner_page, "tab_widget"):
                # Hide the tab widget tab bar! This keeps only the Similarity page active/visible
                inner_page.tab_widget.tabBar().setVisible(False)
                # Hide the title label "MFDenoiser Parameters" to look cleaner
                for child in inner_page.findChildren(QLabel):
                    if child.text() == "MFDenoiser Parameters":
                        child.setVisible(False)

        self.content_stack.addWidget(self.denoise_page_container)

    def set_active_tab(self, tab_name):
        if tab_name == "denoising" and self.current_denoising_algo in ["Average", "Median"]:
            self.set_expanded(False)
            self.active_tab = None
            self._update_styles("transparent")
            return

        # Toggle visibility if same tab clicked
        if self.active_tab == tab_name and self.content_wrapper.isVisible():
            self.set_expanded(False)
            self._update_styles("transparent")
            return

        # Show and switch
        self.set_expanded(True)
        self.active_tab = tab_name
        if tab_name == "alignment":
            self.content_stack.setCurrentWidget(self.align_page)
            border_color = COLOR_ALIGNMENT_RED
        else:
            self.content_stack.setCurrentWidget(self.denoise_page_container)
            border_color = COLOR_DENOISING_GREEN

        self._update_styles(border_color)

    def _update_styles(self, active_color):
        # Main container border styles matching active tab
        self.setStyleSheet(f"""
            #SwitchableParameterPanel {{
                background: transparent;
                background-color: transparent;
                border: none;
            }}
            QWidget#ParamContentWrapper {{
                background-color: {COLOR_BACKGROUND};
                border: 3px solid {active_color};
                border-radius: 8px;
            }}
            QComboBox {{
                padding: 4px 8px;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
            }}
        """)

        # Update tab buttons colors
        align_bg = COLOR_ALIGNMENT_RED if (self.active_tab == "alignment" and self.content_wrapper.isVisible()) else COLOR_INACTIVE_TAB
        denoise_bg = COLOR_DENOISING_GREEN if (self.active_tab == "denoising" and self.content_wrapper.isVisible()) else COLOR_INACTIVE_TAB

        self.btn_align_tab.setStyleSheet(f"""
            QPushButton {{
                background-color: {align_bg};
                color: white;
                border: none;
                outline: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """)
        self.btn_denoise_tab.setStyleSheet(f"""
            QPushButton {{
                background-color: {denoise_bg};
                color: white;
                border: none;
                outline: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """)

    def _on_alignment_algo_changed(self, index):
        # Map selected dropdown to align param stack
        # Combobox options: No Alignment, Farneback Optical Flow, Light Glue, AKAZE, ORB
        self.align_param_stack.setCurrentIndex(index)
        
        # Save choice to settings / store
        selected_text = self.align_dropdown.currentText()
        if hasattr(self.parent(), "right_panel") and self.parent().right_panel:
            if hasattr(self.parent().right_panel, "align_form"):
                self.parent().right_panel.align_form.set_value(selected_text)

    def get_overlay_container(self):
        p = self.parent()
        while p:
            if p.objectName() == "OverlayContainer":
                return p
            p = p.parent()
        return None

    def update_settings_state(self, settings):
        """Update active UI state when RightPanel settings change."""
        snapshot = (
            settings.get("alignment", "No Alignment"),
            settings.get("denoising", "No Denoising"),
        )
        if snapshot == self._last_settings_snapshot:
            return
        self._last_settings_snapshot = snapshot

        # 1. Update alignment selection dropdown
        alignment_algo = settings.get("alignment", "No Alignment")
        idx = self.align_dropdown.findText(alignment_algo)
        if idx >= 0:
            self.align_dropdown.blockSignals(True)
            self.align_dropdown.setCurrentIndex(idx)
            self.align_param_stack.setCurrentIndex(idx)
            self.align_dropdown.blockSignals(False)

        # 2. Handle visibility logic for denoising
        denoising_algo = settings.get("denoising", "No Denoising")
        
        # If denoising algo changed, collapse panel and reset active tab
        if denoising_algo != self.current_denoising_algo:
            if self.active_tab == "denoising" or denoising_algo in ["Average", "Median"]:
                self.active_tab = None
                self.set_expanded(False)
                self._update_styles("transparent")
            
        self.current_denoising_algo = denoising_algo

        overlay = self.get_overlay_container()

        if denoising_algo in ["No Denoising", "None", ""]:
            # Hide the entire overlay panel
            if overlay:
                overlay.hide()
        else:
            # Show the overlay panel
            if overlay:
                overlay.show()
                overlay.raise_()

            if denoising_algo in ["Average", "Median"]:
                self.btn_align_tab.setVisible(True)
                self.btn_denoise_tab.setVisible(False)
                self.btn_denoise_tab.setEnabled(False)
                if self.content_wrapper.isVisible() and self.active_tab != "alignment":
                    self.active_tab = None
                    self.set_expanded(False)
            elif denoising_algo == "Similarity":
                self.btn_align_tab.setVisible(True)
                self.btn_denoise_tab.setVisible(True)
                self.btn_denoise_tab.setEnabled(True)
                
            self._update_styles("transparent" if self.active_tab is None else (COLOR_ALIGNMENT_RED if self.active_tab == "alignment" else COLOR_DENOISING_GREEN))
            self._sync_overlay_geometry()
