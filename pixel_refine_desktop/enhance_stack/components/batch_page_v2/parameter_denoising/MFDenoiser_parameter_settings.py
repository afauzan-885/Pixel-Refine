"""
MFDenoiser Parameter Settings - Generic UI Components
======================================================

Pure generic UI components and binding utilities for parameter management.

Generic component creators:
  slider()   → slider widget with label
  dropdown() → dropdown widget with label
  toggle()   → toggle button with label
  text()     → text input widget with label

Binding utilities:
  bind()     → load config values into widgets
  collect()  → gather widget values into dict
"""

import os
from PySide6.QtWidgets import (
    QLabel, QSlider, QLineEdit, QPushButton, QHBoxLayout,
    QWidget, QVBoxLayout, QTabWidget, QScrollArea, QSizePolicy
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt, QLocale

from resources.GenericUILibrary import FormGroup, live_update
from resources.styles.stylesheet import SLIDER_STYLE, APPLY_BUTTON, SCROLL_AREA

# Backend value providers
from .similarity_parameter_settings import (
    load_similarity_config,
    save_similarity_v1_config,
)
from ..parameter_alignment.akaze_parameter_settings import (
    load_akaze_config,
    save_akaze_config,
)
from ..parameter_alignment.orb_parameter_settings import (
    load_orb_config,
    save_orb_config,
)


def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)


class ResponsiveSliderRow(QWidget):
    """Slider row that reflows from horizontal to stacked on narrow panels."""

    def __init__(self, label_text, min_val, max_val, default, format_func=None, tooltip=""):
        super().__init__()
        self.format_func = format_func
        self._is_compact = None

        self.label = QLabel(label_text)
        self.label.setFont(get_default_font(10, QFont.Weight.Bold))
        self.label.setToolTip(tooltip)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setStyleSheet(SLIDER_STYLE)

        self.value_input = QLineEdit()
        self.value_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value_input.setLocale(QLocale(QLocale.Language.C, QLocale.Country.AnyCountry))

        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(8)
        self.header_layout.addWidget(self.label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.value_input)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self._update_value_text)
        self.slider.setValue(default)
        self.apply_density(420)

    def _update_value_text(self, value):
        self.value_input.setText(self.format_func(value) if self.format_func else str(value))

    def apply_density(self, available_width):
        compact = available_width < 390
        if compact == self._is_compact:
            return
        self._is_compact = compact

        self.label.setMinimumWidth(0 if compact else 135)
        self.value_input.setFixedWidth(46 if compact else 50)
        self.slider.setMinimumWidth(90 if compact else 120)
        self.main_layout.setSpacing(4 if compact else 5)
        self.setMinimumHeight(58 if compact else 38)
        self.setMaximumHeight(72 if compact else 44)
        self.label.setFont(get_default_font(9 if compact else 10, QFont.Weight.Bold))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_density(self.width())


# ═══════════════════════════════════════════════════════════════════════
# GENERIC UI COMPONENT CREATORS
# ═══════════════════════════════════════════════════════════════════════

def slider(label_text, min_val, max_val, default, format_func=None, tooltip=""):
    """Create [slider] widget with label.

    Returns: (row_widget, slider, line_edit)
    """
    row = ResponsiveSliderRow(label_text, min_val, max_val, default, format_func, tooltip)
    return row, row.slider, row.value_input


def dropdown(label_text, options, default, tooltip=""):
    """Create [dropdown] widget with label using FormGroup.

    Returns: FormGroup
    """
    form = FormGroup(label=label_text, input_type="select")
    form.add_options([str(o) for o in options])
    form.set_value(str(default))
    form.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    form.setMinimumHeight(58)
    form.setMaximumHeight(64)
    form.input.setMinimumWidth(120)
    form.input.setMaximumWidth(16777215)
    form.label.setToolTip(tooltip)
    return form


def toggle(label_text, default=False, tooltip=""):
    """Create [toggle] widget with label.

    Returns: (layout, button)
    """
    btn = QPushButton()
    btn.setCheckable(True)
    btn.setFixedSize(40, 20)
    btn.setChecked(default)
    btn.setToolTip(tooltip)

    layout = QHBoxLayout()
    layout.addWidget(QLabel(label_text))
    layout.addStretch()
    layout.addWidget(btn)

    return layout, btn


def text(label_text, default="", tooltip=""):
    """Create [text] widget with label using FormGroup.

    Returns: FormGroup
    """
    form = FormGroup(label=label_text, input_type="text")
    form.input.setText(str(default))
    form.input.setFixedWidth(80)
    form.input.setValidator(QDoubleValidator())
    form.label.setToolTip(tooltip)
    form.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    form.setMinimumHeight(58)
    form.setMaximumHeight(64)
    return form


# ═══════════════════════════════════════════════════════════════════════
# GENERIC BINDING UTILITIES
# ═══════════════════════════════════════════════════════════════════════

def bind(config_dict, widget_map):
    """Bind backend config values to widgets.

    Args:
        config_dict: dict of {key: value} from load_xxx_config()
        widget_map: dict of {key: widget} where widget is a FormGroup
    """
    for key, form in widget_map.items():
        if key in config_dict:
            value = config_dict[key]
            if hasattr(form, 'set_value'):
                form.set_value(str(value))
            elif hasattr(form, 'input') and hasattr(form.input, 'currentText'):
                form.input.setCurrentText(str(value))
            elif hasattr(form, 'input') and hasattr(form.input, 'text'):
                form.input.setText(str(value))


def collect(widget_map):
    """Collect values from widgets.

    Args:
        widget_map: dict of {key: widget} where widget is a FormGroup

    Returns:
        dict of {key: value}
    """
    result = {}
    for key, form in widget_map.items():
        if hasattr(form, 'input'):
            widget = form.input
            if hasattr(widget, 'currentText'):
                result[key] = widget.currentText()
            elif hasattr(widget, 'text'):
                result[key] = widget.text()
            elif hasattr(widget, 'isChecked'):
                result[key] = widget.isChecked()
            elif hasattr(widget, 'value'):
                result[key] = widget.value()
    return result


# ═══════════════════════════════════════════════════════════════════════
# MFDenoiser PARAMETER PAGE
# ═══════════════════════════════════════════════════════════════════════

@live_update("refresh_responsive_layout", on_resize=True)
class MFDenoiserParameterPage(QWidget):
    """MFDenoiser parameter settings page.
    
    Uses generic UI components to display and manage parameters.
    Saves to JSON in realtime when widgets change.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)
        
        # Widget maps for each backend
        self.similarity_widgets = {}
        self.akaze_widgets = {}
        self.orb_widgets = {}
        self.tile_based_widgets = {}
        self._responsive_slider_rows = []
        self._tab_pages = []
        
        self._setup_ui()
        self._load_configs()
        self._connect_signals()
        self.refresh_responsive_layout()

    def refresh_responsive_layout(self):
        available_width = max(240, self.width() - 44)
        compact = available_width < 390
        margin = 8 if compact else 12
        spacing = 8 if compact else 12

        for page in self._tab_pages:
            page_layout = page.layout()
            if page_layout:
                page_layout.setContentsMargins(margin, margin, margin, margin)
                page_layout.setSpacing(spacing)

        for form_map in (
            self.similarity_widgets,
            self.tile_based_widgets,
            self.akaze_widgets,
            self.orb_widgets,
        ):
            for widget in form_map.values():
                if isinstance(widget, FormGroup):
                    widget.setMaximumHeight(58 if compact else 64)
                    widget.input.setMaximumWidth(16777215)

        for row in self._responsive_slider_rows:
            row.apply_density(available_width)

    def _setup_ui(self):
        """Setup main UI layout with tabs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("MFDenoiser Parameters")
        title.setFont(get_default_font(12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_similarity_tab()
        self._create_akaze_tab()
        self._create_orb_tab()
        self._create_tile_based_tab()

    def _create_similarity_tab(self):
        """Create Similarity settings tab."""
        page = QWidget()
        self._tab_pages.append(page)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Tile Size
        self.similarity_widgets["similarity_spatial_tile_size"] = dropdown(
            "Tile Size:", [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256],
            default=16, tooltip="Ukuran tile untuk pemrosesan spasial"
        )
        layout.addWidget(self.similarity_widgets["similarity_spatial_tile_size"])
        
        # Processing Cores
        max_cores = os.cpu_count() or 4
        self.similarity_widgets["similarity_spatial_num_workers"] = dropdown(
            "Processing Cores:", ["Auto"] + [str(i) for i in range(1, max_cores + 1)],
            default="Auto", tooltip="Jumlah inti CPU untuk pemrosesan paralel"
        )
        layout.addWidget(self.similarity_widgets["similarity_spatial_num_workers"])
        
        # Overlap
        overlap_layout, self._overlap_slider, _ = slider(
            "Overlap %:", 0, 90, 30,
            format_func=lambda v: str(v),
            tooltip="Persentase overlap antar tile"
        )
        self.similarity_widgets["similarity_spatial_overlap_percent"] = overlap_layout
        self._responsive_slider_rows.append(overlap_layout)
        layout.addWidget(overlap_layout)
        
        # Motion Sensitivity
        motion_layout, self._motion_slider, _ = slider(
            "Motion Sensitivity:", 10, 2000, 1500,
            format_func=lambda v: f"{v/10.0:.1f}",
            tooltip="Sensitivitas terhadap gerakan"
        )
        self.similarity_widgets["similarity_spatial_motion_sensitivity"] = motion_layout
        self._responsive_slider_rows.append(motion_layout)
        layout.addWidget(motion_layout)
        
        # Noise Offset Factor
        noise_layout, self._noise_slider, _ = slider(
            "Noise Offset Factor:", 0, 100, 15,
            format_func=lambda v: f"{v/100.0:.2f}",
            tooltip="Faktor offset noise untuk thresholding"
        )
        self.similarity_widgets["similarity_spatial_noise_mad_offset_factor"] = noise_layout
        self._responsive_slider_rows.append(noise_layout)
        layout.addWidget(noise_layout)
        
        # Reset Button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(APPLY_BUTTON)
        reset_btn.setMinimumHeight(30)
        reset_btn.clicked.connect(self._reset_similarity)
        
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(reset_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(page, "Similarity")

    def _create_akaze_tab(self):
        """Create AKAZE settings tab."""
        page = QWidget()
        self._tab_pages.append(page)
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.akaze_widgets["akaze_threshold"] = text(
            "Threshold:", default=0.008,
            tooltip="Threshold untuk deteksi keypoint AKAZE"
        )
        layout.addWidget(self.akaze_widgets["akaze_threshold"])
        
        self.akaze_widgets["akaze_nOctaves"] = dropdown(
            "Octaves:", [1, 2, 3, 4, 5, 6, 7, 8],
            default=4, tooltip="Jumlah octave untuk scale space"
        )
        layout.addWidget(self.akaze_widgets["akaze_nOctaves"])
        
        self.akaze_widgets["akaze_nOctaveLayers"] = dropdown(
            "Octave Layers:", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            default=4, tooltip="Jumlah layer per octave"
        )
        layout.addWidget(self.akaze_widgets["akaze_nOctaveLayers"])
        
        self.akaze_widgets["ratio_threshold"] = text(
            "Ratio Threshold:", default=0.75,
            tooltip="Ratio threshold untuk Lowe's ratio test"
        )
        layout.addWidget(self.akaze_widgets["ratio_threshold"])
        
        self.akaze_widgets["transformation"] = dropdown(
            "Transformation:", ["homography", "affine"],
            default="homography", tooltip="Tipe transformasi geometris"
        )
        layout.addWidget(self.akaze_widgets["transformation"])
        
        # Reset Button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(APPLY_BUTTON)
        reset_btn.setMinimumHeight(28)
        reset_btn.clicked.connect(self._reset_akaze)
        
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(reset_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(page, "AKAZE")

    def _create_orb_tab(self):
        """Create ORB settings tab."""
        page = QWidget()
        self._tab_pages.append(page)
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.orb_widgets["nfeatures"] = text(
            "Max Features:", default=1500,
            tooltip="Jumlah maksimum keypoint yang dideteksi"
        )
        layout.addWidget(self.orb_widgets["nfeatures"])
        
        self.orb_widgets["scaleFactor"] = text(
            "Scale Factor:", default=1.1,
            tooltip="Faktor skala untuk image pyramid"
        )
        layout.addWidget(self.orb_widgets["scaleFactor"])
        
        self.orb_widgets["nlevels"] = dropdown(
            "Levels:", [1, 2, 3, 4, 5, 6, 7, 8],
            default=5, tooltip="Jumlah level untuk image pyramid"
        )
        layout.addWidget(self.orb_widgets["nlevels"])
        
        self.orb_widgets["ransacThreshold"] = text(
            "RANSAC Threshold:", default=5.0,
            tooltip="Threshold untuk RANSAC inlier detection"
        )
        layout.addWidget(self.orb_widgets["ransacThreshold"])
        
        self.orb_widgets["transformation"] = dropdown(
            "Transformation:", ["homography", "affine"],
            default="homography", tooltip="Tipe transformasi geometris"
        )
        layout.addWidget(self.orb_widgets["transformation"])
        
        # Reset Button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(APPLY_BUTTON)
        reset_btn.setMinimumHeight(28)
        reset_btn.clicked.connect(self._reset_orb)
        
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(reset_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(page, "ORB")

    def _create_tile_based_tab(self):
        """Create Tile-Based Spatial Fusion settings tab."""
        page = QWidget()
        self._tab_pages.append(page)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Tile Size
        self.tile_based_widgets["tile_based_tile_size"] = dropdown(
            "Tile Size:", [128, 192, 256, 320, 384, 512, 640, 768, 896, 1024],
            default=256, tooltip="Ukuran tile untuk pemrosesan tile-based (pixels)"
        )
        layout.addWidget(self.tile_based_widgets["tile_based_tile_size"])
        
        # Alignment Backend
        self.tile_based_widgets["tile_based_alignment_backend"] = dropdown(
            "Alignment Backend:", ["farneback", "horn_schunck"],
            default="farneback", tooltip="Algoritma optical flow untuk alignment"
        )
        layout.addWidget(self.tile_based_widgets["tile_based_alignment_backend"])
        
        # Overlap
        overlap_layout, self._tb_overlap_slider, _ = slider(
            "Overlap %:", 0, 50, 20,
            format_func=lambda v: str(v),
            tooltip="Persentase overlap antar tile"
        )
        self.tile_based_widgets["tile_based_overlap_percent"] = overlap_layout
        self._responsive_slider_rows.append(overlap_layout)
        layout.addWidget(overlap_layout)
        
        # Motion Sensitivity
        motion_layout, self._tb_motion_slider, _ = slider(
            "Motion Sensitivity:", 10, 2000, 1500,
            format_func=lambda v: f"{v/10.0:.1f}",
            tooltip="Sensitivitas terhadap gerakan (ghost rejection)"
        )
        self.tile_based_widgets["tile_based_motion_sensitivity"] = motion_layout
        self._responsive_slider_rows.append(motion_layout)
        layout.addWidget(motion_layout)
        
        # Noise Offset Factor
        noise_layout, self._tb_noise_slider, _ = slider(
            "Noise Offset Factor:", 0, 100, 15,
            format_func=lambda v: f"{v/100.0:.2f}",
            tooltip="Faktor offset noise untuk thresholding"
        )
        self.tile_based_widgets["tile_based_noise_offset_factor"] = noise_layout
        self._responsive_slider_rows.append(noise_layout)
        layout.addWidget(noise_layout)
        
        # Reset Button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(APPLY_BUTTON)
        reset_btn.setMinimumHeight(28)
        reset_btn.clicked.connect(self._reset_tile_based)
        
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(reset_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(page, "Tile-Based")

    # ──────────────────────────────────────────────────────────────
    # LOAD: Read from backend → Set to widgets
    # ──────────────────────────────────────────────────────────────
    def _load_configs(self):
        """Load all configs from backends."""
        self._load_similarity()
        self._load_akaze()
        self._load_orb()
        self._load_tile_based()

    def _load_similarity(self):
        """Load Similarity config from backend."""
        config = load_similarity_config()
        bind(config, self.similarity_widgets)
        
        # Set slider values
        overlap_val = int(config.get("similarity_spatial_overlap_percent", 0.30) * 100)
        self._overlap_slider.setValue(overlap_val)
        
        motion_val = int(config.get("similarity_spatial_motion_sensitivity", 150.0) * 10)
        self._motion_slider.setValue(motion_val)
        
        noise_val = int(config.get("similarity_spatial_noise_mad_offset_factor", 0.15) * 100)
        self._noise_slider.setValue(noise_val)

    def _load_akaze(self):
        """Load AKAZE config from backend."""
        config = load_akaze_config()
        bind(config, self.akaze_widgets)

    def _load_orb(self):
        """Load ORB config from backend."""
        config = load_orb_config()
        bind(config, self.orb_widgets)

    def _load_tile_based(self):
        """Load Tile-Based config from backend."""
        config = load_similarity_config()  # Reuse similarity config for tile-based settings
        # Set dropdowns
        tile_size = config.get("tile_based_tile_size", 256)
        self.tile_based_widgets["tile_based_tile_size"].set_value(str(tile_size))
        
        alignment_backend = config.get("tile_based_alignment_backend", "farneback")
        self.tile_based_widgets["tile_based_alignment_backend"].set_value(alignment_backend)
        
        # Set slider values
        overlap_val = int(config.get("tile_based_overlap_percent", 0.2) * 100)
        self._tb_overlap_slider.setValue(overlap_val)
        
        motion_val = int(config.get("tile_based_motion_sensitivity", 150.0) * 10)
        self._tb_motion_slider.setValue(motion_val)
        
        noise_val = int(config.get("tile_based_noise_offset_factor", 0.15) * 100)
        self._tb_noise_slider.setValue(noise_val)

    # ──────────────────────────────────────────────────────────────
    # CONNECT: Widget signals → Save functions
    # ──────────────────────────────────────────────────────────────
    def _connect_signals(self):
        """Connect widget signals to save functions."""
        # Similarity
        self.similarity_widgets["similarity_spatial_tile_size"].input.currentIndexChanged.connect(self._save_similarity)
        self.similarity_widgets["similarity_spatial_num_workers"].input.currentIndexChanged.connect(self._save_similarity)
        self._overlap_slider.sliderReleased.connect(self._save_similarity)
        self._motion_slider.sliderReleased.connect(self._save_similarity)
        self._noise_slider.sliderReleased.connect(self._save_similarity)
        
        # AKAZE
        self.akaze_widgets["akaze_threshold"].input.editingFinished.connect(self._save_akaze)
        self.akaze_widgets["akaze_nOctaves"].input.currentIndexChanged.connect(self._save_akaze)
        self.akaze_widgets["akaze_nOctaveLayers"].input.currentIndexChanged.connect(self._save_akaze)
        self.akaze_widgets["ratio_threshold"].input.editingFinished.connect(self._save_akaze)
        self.akaze_widgets["transformation"].input.currentIndexChanged.connect(self._save_akaze)
        
        # ORB
        self.orb_widgets["nfeatures"].input.editingFinished.connect(self._save_orb)
        self.orb_widgets["scaleFactor"].input.editingFinished.connect(self._save_orb)
        self.orb_widgets["nlevels"].input.currentIndexChanged.connect(self._save_orb)
        self.orb_widgets["ransacThreshold"].input.editingFinished.connect(self._save_orb)
        self.orb_widgets["transformation"].input.currentIndexChanged.connect(self._save_orb)
        
        # Tile-Based
        self.tile_based_widgets["tile_based_tile_size"].input.currentIndexChanged.connect(self._save_tile_based)
        self.tile_based_widgets["tile_based_alignment_backend"].input.currentIndexChanged.connect(self._save_tile_based)
        self._tb_overlap_slider.sliderReleased.connect(self._save_tile_based)
        self._tb_motion_slider.sliderReleased.connect(self._save_tile_based)
        self._tb_noise_slider.sliderReleased.connect(self._save_tile_based)

    # ──────────────────────────────────────────────────────────────
    # SAVE: Collect from widgets → Save to backend (REALTIME)
    # ──────────────────────────────────────────────────────────────
    def _save_similarity(self):
        """Save Similarity config to backend (realtime)."""
        values = collect(self.similarity_widgets)
        config = {
            "similarity_spatial_tile_size": int(values.get("similarity_spatial_tile_size", 16)),
            "similarity_spatial_num_workers": -1 if values.get("similarity_spatial_num_workers") == "Auto" else int(values.get("similarity_spatial_num_workers", 1)),
            "similarity_spatial_overlap_percent": self._overlap_slider.value() / 100.0,
            "similarity_spatial_motion_sensitivity": self._motion_slider.value() / 10.0,
            "similarity_spatial_noise_mad_offset_factor": self._noise_slider.value() / 100.0,
        }
        save_similarity_v1_config(config)

    def _save_akaze(self):
        """Save AKAZE config to backend (realtime)."""
        values = collect(self.akaze_widgets)
        config = {
            "akaze_threshold": float(values.get("akaze_threshold", 0.008)),
            "akaze_nOctaves": int(values.get("akaze_nOctaves", 4)),
            "akaze_nOctaveLayers": int(values.get("akaze_nOctaveLayers", 4)),
            "ratio_threshold": float(values.get("ratio_threshold", 0.75)),
            "ransacThreshold": 5.0,
            "transformation": values.get("transformation", "homography"),
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,
            "command_save_to_hd5f": True,
            "align_folder": "",
        }
        save_akaze_config(config)

    def _save_orb(self):
        """Save ORB config to backend (realtime)."""
        values = collect(self.orb_widgets)
        config = {
            "nfeatures": int(values.get("nfeatures", 1500)),
            "scaleFactor": float(values.get("scaleFactor", 1.1)),
            "nlevels": int(values.get("nlevels", 5)),
            "ransacThreshold": float(values.get("ransacThreshold", 5.0)),
            "transformation": values.get("transformation", "homography"),
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,
            "command_save_to_hd5f": True,
            "align_folder": "",
        }
        save_orb_config(config)

    def _save_tile_based(self):
        """Save Tile-Based config to backend (realtime)."""
        values = collect(self.tile_based_widgets)
        config = {
            "tile_based_tile_size": int(values.get("tile_based_tile_size", 256)),
            "tile_based_alignment_backend": values.get("tile_based_alignment_backend", "farneback"),
            "tile_based_overlap_percent": self._tb_overlap_slider.value() / 100.0,
            "tile_based_motion_sensitivity": self._tb_motion_slider.value() / 10.0,
            "tile_based_noise_offset_factor": self._tb_noise_slider.value() / 100.0,
        }
        # Save to similarity config (reuse same file for tile-based settings)
        current_config = load_similarity_config()
        current_config.update(config)
        save_similarity_v1_config(current_config)

    # ──────────────────────────────────────────────────────────────
    # RESET: Reload defaults from backend
    # ──────────────────────────────────────────────────────────────
    def _reset_similarity(self):
        """Reset Similarity to backend defaults."""
        self._load_similarity()
        self._save_similarity()

    def _reset_akaze(self):
        """Reset AKAZE to backend defaults."""
        self._load_akaze()
        self._save_akaze()

    def _reset_orb(self):
        """Reset ORB to backend defaults."""
        self._load_orb()
        self._save_orb()

    def _reset_tile_based(self):
        """Reset Tile-Based to backend defaults."""
        self._load_tile_based()
        self._save_tile_based()


def get_mfdenoiser_settings_page():
    """Return MFDenoiser settings page wrapped in QScrollArea."""
    page = MFDenoiserParameterPage()
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll
