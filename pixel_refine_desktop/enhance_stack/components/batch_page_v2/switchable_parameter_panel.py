import os
from PySide6.QtWidgets import (
    QApplication,
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
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QEvent
from resources.GenericUILibrary import live_update

# Import parameter pages
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.light_glue_parameter_settings import (
    load_light_glue_config,
    save_light_glue_config_for_active_batch,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.farneback_parameter_settings import (
    load_farneback_config,
    save_farneback_config_for_active_batch,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.lucas_kanade_parameter_settings import (
    load_lucas_kanade_config,
    load_lucas_kanade_gpu_config,
    save_lucas_kanade_config_for_active_batch,
    save_lucas_kanade_gpu_config_for_active_batch,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.block_matching_parameter_settings import (
    load_block_matching_gpu_config,
    save_block_matching_gpu_config_for_active_batch,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.raft_parameter_settings import (
    load_raft_config,
    save_raft_config_for_active_batch,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.akaze_parameter_settings import (
    load_akaze_config,
    save_akaze_config_for_active_batch,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.orb_parameter_settings import (
    load_orb_config,
    save_orb_config_for_active_batch,
)
from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.MFDenoiser_parameter_settings import (
    get_alignment_settings_page,
    get_denoising_settings_page,
    get_mfdenoiser_settings_page,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    get_algorithm_names as get_mfdenoiser_algorithm_names,
)

# Colors
COLOR_ALIGNMENT_RED = "#E74C3C"      # Premium calm red
COLOR_DENOISING_GREEN = "#2ECC71"    # Premium calm green
COLOR_INACTIVE_TAB = "#BDC3C7"       # Muted gray for inactive state
COLOR_BACKGROUND = "#FFFFFF"
COLOR_ALIGNMENT_BG = "#FEF2F2"
COLOR_ALIGNMENT_BORDER_SOFT = "#F3B4AD"
COLOR_DENOISING_BG = "#F0FDF4"
COLOR_DENOISING_BORDER_SOFT = "#A8E6BF"

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
        # React when device backend changes (e.g., user switches GPU↔CPU in Settings)
        try:
            from pixel_refine_desktop.ui.views.settings.General.general_store import get_general_store
            get_general_store().changed.connect(self._on_general_settings_changed)
        except Exception:
            pass

    def _on_general_settings_changed(self, key=None, *args):
        """React to device backend arch changes to show/hide Block Matching GPU."""
        if key is None or key in ("device_backend_arch", "device_backend_id"):
            self._filter_alignment_for_backend()

    # RAFT still requires its external model/runtime. Lucas-Kanade, Block
    # Matching, and Farneback use the validated native AOT paths on OpenGL.
    _VULKAN_ONLY_ALIGNMENT = {"RAFT"}
    _CPU_HIDDEN_ALIGNMENT = {"RAFT"}

    def _repopulate_alignment_combo(self):
        """Rebuild the alignment combo items based on current backend arch.

        Completely removes hidden items (e.g. Block Matching GPU on CPU mode)
        so they never appear in the dropdown. The page stack is untouched so
        we can re-add items if the user switches to GPU mode later.
        """
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import get_backend_arch
        if not hasattr(self, "align_dropdown"):
            return

        backend_arch = get_backend_arch()
        combo = self.align_dropdown

        # Remember current selection
        current_text = combo.currentText()

        # Rebuild item list
        combo.blockSignals(True)
        combo.clear()
        for name in self.alignment_algorithm_names:
            if backend_arch == "opengl" and name in self._VULKAN_ONLY_ALIGNMENT:
                continue
            if backend_arch == "cpu" and name in self._CPU_HIDDEN_ALIGNMENT:
                continue
            combo.addItem(name)

        # Restore selection if still available, else fall back to No Alignment
        idx = combo.findText(current_text)
        if idx < 0:
            idx = combo.findText("No Alignment")
        combo.setCurrentIndex(max(0, idx))
        combo.blockSignals(False)

        # Sync the page stack to the new selection
        selected = combo.currentText()
        if hasattr(self, "alignment_pages") and selected in self.alignment_pages:
            self.align_param_stack.setCurrentWidget(self.alignment_pages[selected])

    def _filter_alignment_for_backend(self):
        """Wrapper kept for backward compatibility (called by general_store listener)."""
        self._repopulate_alignment_combo()

    def _persist_alignment_selection(self):
        selected_text = self.align_dropdown.currentText()
        right_panel = getattr(self.parent(), "right_panel", None)
        if right_panel and hasattr(right_panel, "align_form"):
            right_panel.align_form.set_value(selected_text)
            if hasattr(right_panel, "_on_settings_changed"):
                right_panel._on_settings_changed(save_to_store=True)

        if selected_text == "Farneback":
            save_farneback_config_for_active_batch(load_farneback_config())
        elif selected_text == "ORB":
            save_orb_config_for_active_batch(load_orb_config())
        elif selected_text == "AKAZE":
            save_akaze_config_for_active_batch(load_akaze_config())
        elif selected_text == "Light Glue":
            save_light_glue_config_for_active_batch(load_light_glue_config())
        elif selected_text == "Lucas Kanade":
            save_lucas_kanade_config_for_active_batch(load_lucas_kanade_config())
            save_lucas_kanade_gpu_config_for_active_batch(load_lucas_kanade_gpu_config())
        elif selected_text == "Block Matching GPU":
            save_block_matching_gpu_config_for_active_batch(load_block_matching_gpu_config())
        elif selected_text == "RAFT":
            save_raft_config_for_active_batch(load_raft_config())

        print(
            f"[SwitchableParameterPanel] persisted alignment='{selected_text}' "
            f"batch_id={getattr(right_panel, 'current_batch_id', None)}"
        )

    def _save_alignment_params_for_active_batch(self, algorithm_name, params_key, params):
        right_panel = getattr(self.parent(), "right_panel", None)
        if not right_panel or not getattr(right_panel, "current_batch_id", None):
            return

        batch_id = right_panel.current_batch_id
        str_id = str(batch_id)
        denoising_algo = (
            right_panel.denoise_card.get_value()
            if hasattr(right_panel, "denoise_card")
            else "Average"
        )
        super_resolution_algo = (
            right_panel.sr_card.get_value()
            if hasattr(right_panel, "sr_card")
            else "No Super Resolution"
        )
        bulk_data = {
            f"{str_id}.alignment_algo": algorithm_name,
            f"{str_id}.super_resolution_algo": super_resolution_algo or "No Super Resolution",
            f"{str_id}.denoising_algo": denoising_algo or "No Denoising",
            f"{str_id}.checkbox_align_images": algorithm_name not in ("", "None", "No Alignment"),
            f"{str_id}.checkbox_super_resolution": bool(getattr(right_panel.sr_card, "is_checked", False))
            if hasattr(right_panel, "sr_card")
            else False,
            f"{str_id}.checkbox_denoising": bool(getattr(right_panel.denoise_card, "is_checked", False))
            if hasattr(right_panel, "denoise_card")
            else denoising_algo not in ("", "None", "No Denoising"),
            f"{str_id}.{params_key}": params,
        }
        if hasattr(right_panel, "_store") and right_panel._store:
            right_panel._store.update_bulk(bulk_data, save=True)
        else:
            data = batch_parameter_manager.load_json_state()
            entry = data.setdefault(str_id, {})
            for key, value in bulk_data.items():
                entry[key.split(".", 1)[1]] = value
            batch_parameter_manager.save_json_state(data=data)

        if hasattr(right_panel, "logic"):
            right_panel.logic.set_settings(
                {
                    "alignment": algorithm_name,
                    "super_resolution": super_resolution_algo,
                    "denoising": denoising_algo,
                }
            )
        print(f"[{algorithm_name}Settings] Saved params for batch_id={batch_id}")

    def set_expanded(self, expanded):
        if self.content_wrapper.isVisible() == expanded:
            return

        self.content_wrapper.setVisible(expanded)
        if expanded:
            width, height = self._expanded_size()
            self.setMinimumSize(width, height)
            self.setMaximumSize(width, height)
            window = self.window()
            if window:
                window.installEventFilter(self)
        else:
            # Keep the collapsed tab rail deterministic so OverlayContainer does
            # not reuse a stale expanded geometry during rapid setting changes.
            self.setMinimumSize(50, self._collapsed_height())
            self.setMaximumSize(50, self._collapsed_height())
            window = self.window()
            if window:
                window.removeEventFilter(self)
        
        self.updateGeometry()
        self.adjustSize()

        # Trigger parent OverlayContainer size adjustment after Qt has applied
        # the new size constraints.
        overlay = self.get_overlay_container()
        if overlay:
            QTimer.singleShot(0, self._sync_overlay_geometry)

    def collapse_panel(self):
        self.active_tab = None
        self.set_expanded(False)
        self._update_styles("transparent")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and self.content_wrapper.isVisible():
            global_pos = (
                event.globalPosition().toPoint()
                if hasattr(event, "globalPosition")
                else event.globalPos()
            )
            clicked_widget = QApplication.widgetAt(global_pos)
            if clicked_widget and clicked_widget != self and not self.isAncestorOf(clicked_widget):
                self.collapse_panel()
        return super().eventFilter(obj, event)

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
        
        if self.active_tab == "alignment":
            preferred_width = max(260 + 58, int(available_w * 0.35))
            width = max(290, min(750, preferred_width, width_cap))
        else:
            preferred_width = max(260 + 58, int(available_w * 0.24))
            width = max(290, min(520, preferred_width, width_cap))

        # Tinggi maksimal ditambah 30%: dari 0.52 menjadi 0.67 area layar
        height = max(240, min(562, int(available_h * 0.67), height_cap))
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
        
        if self.active_tab == "alignment":
            preferred_width = max(260 + 58, int(available_w * 0.35))
            width = max(290, min(750, preferred_width, width_cap))
        else:
            preferred_width = max(260 + 58, int(available_w * 0.24))
            width = max(290, min(520, preferred_width, width_cap))

        # Tinggi maksimal ditambah 30%: dari 0.52 menjadi 0.67 area layar
        height = max(240, min(562, int(available_h * 0.67), height_cap))
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

        # Keep ALL algorithm names so pages are always built (needed if user switches to GPU later)
        self.alignment_algorithm_names = get_mfdenoiser_algorithm_names("alignment")

        # Build ALL parameter pages into the stack keyed by name (name-based lookup in _on_alignment_algo_changed)
        self.alignment_pages = {}
        self.align_param_stack = QStackedWidget()
        for name in self.alignment_algorithm_names:
            page = get_alignment_settings_page(name)
            self.alignment_pages[name] = page
            self.align_param_stack.addWidget(page)

        # Populate combo filtered by backend (apply now before connecting signal)
        self._repopulate_alignment_combo()
        self.align_dropdown.currentIndexChanged.connect(self._on_alignment_algo_changed)

        align_layout.addWidget(self.align_dropdown_label)
        align_layout.addWidget(self.align_dropdown)
        align_layout.addWidget(self.align_param_stack, 1)
        self.content_stack.addWidget(self.align_page)

    def _setup_denoising_page(self):
        self.denoise_page_container = get_denoising_settings_page("Similarity")
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
            self.active_tab = None
            self._update_styles("transparent")
            return

        # Show and switch
        self.active_tab = tab_name
        self.set_expanded(True)
        if tab_name == "alignment":
            self.content_stack.setCurrentWidget(self.align_page)
            border_color = COLOR_ALIGNMENT_RED
            self._persist_alignment_selection()
        else:
            self.content_stack.setCurrentWidget(self.denoise_page_container)
            border_color = COLOR_DENOISING_GREEN

        self._update_styles(border_color)

    def _update_styles(self, active_color):
        is_expanded = self.content_wrapper.isVisible()
        compact = self.width() < 380
        panel_bg = COLOR_BACKGROUND
        soft_border = "#DDE5EC"
        selection_bg = "#EAF2F8"
        selection_text = "#2C3E50"
        if is_expanded and self.active_tab == "alignment":
            panel_bg = COLOR_ALIGNMENT_BG
            soft_border = COLOR_ALIGNMENT_BORDER_SOFT
            selection_bg = "#FDE2E2"
            selection_text = "#7A1F17"
        elif is_expanded and self.active_tab == "denoising":
            panel_bg = COLOR_DENOISING_BG
            soft_border = COLOR_DENOISING_BORDER_SOFT
            selection_bg = "#DCFCE7"
            selection_text = "#166534"

        combo_padding_y = 3 if compact else 4
        combo_padding_x = 7 if compact else 8
        combo_font_size = 9 if compact else 10
        tooltip_font_size = 9 if compact else 10

        # Main container border styles matching active tab
        self.setStyleSheet(f"""
            #SwitchableParameterPanel {{
                background: transparent;
                background-color: transparent;
                border: none;
            }}
            QWidget#ParamContentWrapper {{
                background-color: {panel_bg};
                border: 3px solid {active_color};
                border-radius: 8px;
            }}
            QWidget#ParamContentWrapper QWidget {{
                background-color: {panel_bg};
            }}
            QWidget#ParamContentWrapper QComboBox,
            QWidget#ParamContentWrapper QComboBox QAbstractItemView,
            QWidget#ParamContentWrapper QLineEdit {{
                background-color: #FFFFFF;
                color: #2C3E50;
            }}
            QComboBox {{
                background-color: #FFFFFF;
                color: #2C3E50;
                padding: {combo_padding_y}px {combo_padding_x}px;
                border: 1px solid {active_color};
                border-radius: 6px;
                font-size: {combo_font_size}pt;
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: transparent;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #2C3E50;
                width: 0;
                height: 0;
                margin-right: 8px;
            }}
            QComboBox:focus {{
                border: 1px solid {active_color};
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid {active_color};
                selection-background-color: {selection_bg};
                selection-color: {selection_text};
                outline: none;
            }}
            QToolTip {{
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #DDE5EC;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: {tooltip_font_size}pt;
            }}
        """)

        self.content_wrapper.setStyleSheet(f"""
            #ParamContentWrapper {{
                background-color: {panel_bg};
                border: 3px solid {active_color};
                border-radius: 8px;
            }}
            QWidget#ParamContentWrapper QWidget {{
                background-color: {panel_bg};
            }}
            QWidget#ParamContentWrapper QComboBox,
            QWidget#ParamContentWrapper QComboBox QAbstractItemView,
            QWidget#ParamContentWrapper QLineEdit {{
                background-color: #FFFFFF;
                color: #2C3E50;
            }}
            QToolTip {{
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #DDE5EC;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: {tooltip_font_size}pt;
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
            QToolTip {{
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #DDE5EC;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 10pt;
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
            QToolTip {{
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #DDE5EC;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 10pt;
            }}
        """)

    def _on_alignment_algo_changed(self, index):
        # Use name-based lookup so the page stack index is independent of combo order
        selected = self.align_dropdown.currentText()
        if selected in self.alignment_pages:
            self.align_param_stack.setCurrentWidget(self.alignment_pages[selected])

        # Save choice to settings / store
        self._persist_alignment_selection()

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
        alignment_algo = self._normalize_alignment_name(settings.get("alignment", "No Alignment"))
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
            if self.active_tab == "denoising" or denoising_algo in [
                "Average",
                "Median",
            ]:
                self.active_tab = None
                self.set_expanded(False)
                self._update_styles("transparent")
            
        self.current_denoising_algo = denoising_algo

        overlay = self.get_overlay_container()

        if denoising_algo in ["No Denoising", "None", ""]:
            # Hide the entire overlay panel
            self.collapse_panel()
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
            elif denoising_algo in ["Similarity", "Similarity Fusion"]:
                self.btn_align_tab.setVisible(True)
                self.btn_denoise_tab.setVisible(True)
                self.btn_denoise_tab.setEnabled(True)

            self._update_styles("transparent" if self.active_tab is None else (COLOR_ALIGNMENT_RED if self.active_tab == "alignment" else COLOR_DENOISING_GREEN))
            if not self.content_wrapper.isVisible():
                self.setMinimumSize(50, self._collapsed_height())
                self.setMaximumSize(50, self._collapsed_height())
            self._sync_overlay_geometry()

    def _normalize_alignment_name(self, value):
        mapping = {
            "Farneback Optical Flow": "Farneback",
            "Lucas Kanade Optical Flow": "Lucas Kanade",
            "Lucas Kanade GPU Optical Flow": "Lucas Kanade",
            "Block Matching GPU Optical Flow": "Block Matching GPU",
            "RAFT Optical Flow": "RAFT",
        }
        return mapping.get(str(value or "").strip(), str(value or "No Alignment"))
