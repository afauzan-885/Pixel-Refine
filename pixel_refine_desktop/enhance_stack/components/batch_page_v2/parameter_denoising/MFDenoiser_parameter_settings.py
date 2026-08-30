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
    QLabel,
    QSlider,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QScrollArea,
    QSizePolicy,
    QButtonGroup,
    QComboBox,
    QStackedWidget,
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt, QLocale

from resources.GenericUILibrary import FormGroup, live_update
from resources.styles.stylesheet import SLIDER_STYLE, APPLY_BUTTON, SCROLL_AREA
from pixel_refine_desktop.ui.views.settings.General.Language import language_config

# Backend value providers
from .similarity_parameter_settings import (
    PARAMETER_SCHEMA as SIMILARITY_PARAMETER_SCHEMA,
    load_similarity_config,
    save_similarity_config,
    save_similarity_config_for_active_batch,
    save_similarity_v1_config,
)
from ..parameter_alignment.akaze_parameter_settings import (
    PARAMETER_SCHEMA as AKAZE_PARAMETER_SCHEMA,
    load_akaze_config,
    save_akaze_config,
    save_akaze_config_for_active_batch,
)
from ..parameter_alignment.orb_parameter_settings import (
    PARAMETER_SCHEMA as ORB_PARAMETER_SCHEMA,
    load_orb_config,
    save_orb_config,
    save_orb_config_for_active_batch,
)
from ..parameter_alignment.light_glue_parameter_settings import (
    PARAMETER_SCHEMA as LIGHT_GLUE_PARAMETER_SCHEMA,
    load_light_glue_config,
    save_light_glue_config,
    save_light_glue_config_for_active_batch,
)
from ..parameter_alignment.farneback_parameter_settings import (
    PARAMETER_SCHEMA as FARNEBACK_PARAMETER_SCHEMA,
    load_farneback_config,
    save_farneback_config,
    save_farneback_config_for_active_batch,
)
from ..parameter_alignment.lucas_kanade_parameter_settings import (
    PARAMETER_SCHEMA as LUCAS_KANADE_PARAMETER_SCHEMA,
    GPU_PARAMETER_SCHEMA as LUCAS_KANADE_GPU_PARAMETER_SCHEMA,
    load_lucas_kanade_config,
    load_lucas_kanade_gpu_config,
    save_lucas_kanade_config,
    save_lucas_kanade_gpu_config,
    save_lucas_kanade_config_for_active_batch,
    save_lucas_kanade_gpu_config_for_active_batch,
)
from ..parameter_alignment.block_matching_parameter_settings import (
    GPU_PARAMETER_SCHEMA as BLOCK_MATCHING_GPU_PARAMETER_SCHEMA,
    load_block_matching_gpu_config,
    save_block_matching_gpu_config,
    save_block_matching_gpu_config_for_active_batch,
)
from ..parameter_alignment.raft_parameter_settings import (
    PARAMETER_SCHEMA as RAFT_PARAMETER_SCHEMA,
    load_raft_config,
    save_raft_config,
    save_raft_config_for_active_batch,
)
from ..parameter_alignment.alignment_config_provider import (
    save_alignment_config_for_active_batch,
)


def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)


class ResponsiveSliderRow(QWidget):
    """Slider row that reflows from horizontal to stacked on narrow panels."""

    def __init__(
        self, label_text, min_val, max_val, default, format_func=None, tooltip=""
    ):
        super().__init__()
        self.format_func = format_func
        self._is_compact = None

        self.label = QLabel(label_text)
        self.label.setFont(get_default_font(10, QFont.Weight.Bold))
        self.label.setToolTip(tooltip)
        self.label.setMinimumHeight(24)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setStyleSheet(SLIDER_STYLE)
        self.slider.setToolTip(tooltip)

        self.value_input = QLineEdit()
        self.value_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value_input.setLocale(
            QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)
        )
        self.value_input.setMinimumHeight(24)
        edit_hint = getattr(
            language_config,
            "PARAMETER_DIRECT_EDIT_TOOLTIP",
            "Edit value directly, then press Enter or leave the field.",
        )
        self.value_input.setToolTip(
            f"{tooltip}\n\n{edit_hint}" if tooltip else edit_hint
        )
        self.setToolTip(tooltip)

        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(8)
        self.header_layout.addWidget(self.label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.value_input)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self._update_value_text)
        self.slider.setValue(default)
        self._update_value_text(self.slider.value())
        self.apply_density(420)

    def _update_value_text(self, value):
        if self.label.text() == "Batch Size (AI)" and int(value) == 16:
            text = "Full Frame"
        else:
            text = self.format_func(value) if self.format_func else str(value)
        self.value_input.setText(text)
        if text in ("Full Frame", "16"):
            self.value_input.setEnabled(False)
        else:
            self.value_input.setEnabled(True)

    def set_slider_value_from_text(self, scale=1.0):
        try:
            value = float(self.value_input.text().strip())
        except ValueError:
            self._update_value_text(self.slider.value())
            return False

        slider_value = int(round(value / scale))
        slider_value = max(
            self.slider.minimum(), min(self.slider.maximum(), slider_value)
        )
        self.slider.setValue(slider_value)
        self._update_value_text(slider_value)
        return True

    def apply_density(self, available_width):
        compact = available_width < 390
        if compact == self._is_compact:
            return
        self._is_compact = compact

        self.label.setMinimumWidth(0 if compact else 135)
        self.value_input.setFixedWidth(66 if compact else 78)
        self.slider.setMinimumWidth(90 if compact else 120)
        self.main_layout.setSpacing(2 if compact else 3)
        self.setMinimumHeight(58 if compact else 38)
        self.setMaximumHeight(72 if compact else 44)
        self.label.setFont(get_default_font(9 if compact else 10, QFont.Weight.Bold))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_density(self.width())


class ToggleButtonRow(QWidget):
    """Reusable ON/OFF button row for boolean provider fields."""

    def __init__(self, label_text, default=False, tooltip=""):
        super().__init__()
        self.label = QLabel(label_text)
        self.label.setFont(get_default_font(10, QFont.Weight.Normal))
        self.label.setToolTip(tooltip)

        self.button = QPushButton()
        self.button.setCheckable(True)
        self.button.setFixedSize(64, 28)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setToolTip(tooltip)
        self.button.setChecked(bool(default))
        self.button.toggled.connect(self._apply_state)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.button)

        self.setMinimumHeight(34)
        self.setMaximumHeight(40)
        self._apply_state(self.button.isChecked())

    def _apply_state(self, checked):
        self.button.setText("ON" if checked else "OFF")
        if checked:
            self.button.setStyleSheet(
                """
                QPushButton {
                    background-color: #2ECC71;
                    color: white;
                    border: 1px solid #27AE60;
                    border-radius: 6px;
                    font-weight: 700;
                    padding: 4px 10px;
                }
                QPushButton:hover { background-color: #27AE60; }
                """
            )
        else:
            self.button.setStyleSheet(
                """
                QPushButton {
                    background-color: #F4F6F7;
                    color: #2C3E50;
                    border: 1px solid #D5DBDB;
                    border-radius: 6px;
                    font-weight: 700;
                    padding: 4px 10px;
                }
                QPushButton:hover { background-color: #EAECEE; }
                """
            )


# ═══════════════════════════════════════════════════════════════════════
# GENERIC UI COMPONENT CREATORS
# ═══════════════════════════════════════════════════════════════════════


def slider(label_text, min_val, max_val, default, format_func=None, tooltip=""):
    """Create [slider] widget with label.

    Returns: (row_widget, slider, line_edit)
    """
    row = ResponsiveSliderRow(
        label_text, min_val, max_val, default, format_func, tooltip
    )
    row.slider.value_input = row.value_input
    row.slider.row_widget = row
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
    form.input.setToolTip(tooltip)
    form.setToolTip(tooltip)
    return form


def toggle(label_text, default=False, tooltip=""):
    """Create [toggle] widget with label.

    Returns: (row_widget, button)
    """
    row = ToggleButtonRow(label_text, default=default, tooltip=tooltip)
    return row, row.button


def text(label_text, default="", tooltip=""):
    """Create [text] widget with label using FormGroup.

    Returns: FormGroup
    """
    form = FormGroup(label=label_text, input_type="text")
    form.input.setText(str(default))
    form.input.setFixedWidth(80)
    form.input.setValidator(QDoubleValidator())
    form.label.setToolTip(tooltip)
    form.input.setToolTip(tooltip)
    form.setToolTip(tooltip)
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
            if hasattr(form, "set_value"):
                form.set_value(str(value))
            elif hasattr(form, "input") and hasattr(form.input, "currentText"):
                form.input.setCurrentText(str(value))
            elif hasattr(form, "input") and hasattr(form.input, "text"):
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
        if hasattr(form, "input"):
            widget = form.input
            if hasattr(widget, "currentText"):
                result[key] = widget.currentText()
            elif hasattr(widget, "text"):
                result[key] = widget.text()
            elif hasattr(widget, "isChecked"):
                result[key] = widget.isChecked()
            elif hasattr(widget, "value"):
                result[key] = widget.value()
    return result


ALIGNMENT_PARAMETER_PROVIDERS = {
    "AKAZE": {
        "schema": AKAZE_PARAMETER_SCHEMA,
        "load": load_akaze_config,
        "save": save_akaze_config,
        "save_batch": save_akaze_config_for_active_batch,
    },
    "ORB": {
        "schema": ORB_PARAMETER_SCHEMA,
        "load": load_orb_config,
        "save": save_orb_config,
        "save_batch": save_orb_config_for_active_batch,
    },
    "Light Glue": {
        "schema": LIGHT_GLUE_PARAMETER_SCHEMA,
        "load": load_light_glue_config,
        "save": save_light_glue_config,
        "save_batch": save_light_glue_config_for_active_batch,
    },
    "Farneback": {
        "schema": FARNEBACK_PARAMETER_SCHEMA,
        "load": load_farneback_config,
        "save": save_farneback_config,
        "save_batch": save_farneback_config_for_active_batch,
    },
    "Block Matching GPU": {
        "schema": BLOCK_MATCHING_GPU_PARAMETER_SCHEMA,
        "load": load_block_matching_gpu_config,
        "save": save_block_matching_gpu_config,
        "save_batch": save_block_matching_gpu_config_for_active_batch,
    },
    "RAFT": {
        "schema": RAFT_PARAMETER_SCHEMA,
        "load": load_raft_config,
        "save": save_raft_config,
        "save_batch": save_raft_config_for_active_batch,
    },
}


DENOISING_PARAMETER_PROVIDERS = {
    "Similarity": {
        "schema": SIMILARITY_PARAMETER_SCHEMA,
        "load": load_similarity_config,
        "save": save_similarity_config,
        "save_batch": save_similarity_config_for_active_batch,
    },
}


class AlignmentParameterPage(QWidget):
    """Render an alignment algorithm's provider schema with generic controls."""

    def __init__(self, algorithm_name, parent=None):
        super().__init__(parent)
        self.algorithm_name = algorithm_name
        self.provider = ALIGNMENT_PARAMETER_PROVIDERS.get(algorithm_name)
        self.controls = {}
        self._loading = False
        self._responsive_slider_rows = []
        self._setup_ui()

    def refresh_responsive_layout(self):
        available_width = max(240, self.width() - 24)
        for row in self._responsive_slider_rows:
            row.apply_density(available_width)
        for field, control in self.controls.values():
            if field["type"] in ("dropdown", "text") and isinstance(control, FormGroup):
                control.input.setMaximumWidth(16777215)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        if not self.provider:
            label = QLabel(f"{self.algorithm_name} parameters are not available.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #7F8C8D; font-style: italic;")
            layout.addWidget(label)
            return

        title = QLabel(self.algorithm_name)
        title.setFont(get_default_font(10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        title.setMinimumHeight(32)
        title.setContentsMargins(0, 4, 0, 6)
        layout.addWidget(title)

        config = self.provider["load"]()
        self._loading = True
        for field in self.provider["schema"]:
            key = field["key"]
            value = config.get(key, field.get("default"))
            widget = self._create_field(field, value)
            if widget is not None:
                (
                    layout.addWidget(widget)
                    if isinstance(widget, QWidget)
                    else layout.addLayout(widget)
                )
        self._loading = False

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(APPLY_BUTTON)
        reset_btn.setMinimumHeight(28)
        reset_btn.clicked.connect(self._reset_to_defaults)
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(reset_layout)
        layout.addStretch()


@live_update("refresh_responsive_layout", on_resize=True)
class LucasKanadeParameterPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading = False
        self.cpu_controls = {}
        self.gpu_controls = {}
        self._cpu_rows = []
        self._gpu_rows = []
        self._setup_ui()
        self._load_configs()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        title = QLabel("Lucas Kanade")
        title.setFont(get_default_font(10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setMinimumHeight(32)
        layout.addWidget(title)

        mode_label = QLabel("Backend")
        mode_label.setFont(get_default_font(9, QFont.Weight.Bold))
        mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mode_label)

        toggle_row = QHBoxLayout()
        toggle_row.addStretch()
        self.backend_buttons = QButtonGroup(self)
        self.cpu_btn = QPushButton("CPU")
        self.gpu_btn = QPushButton("GPU")
        for btn in (self.cpu_btn, self.gpu_btn):
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setMinimumWidth(78)
            self.backend_buttons.addButton(btn)
            toggle_row.addWidget(btn)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)

        self.backend_stack = QStackedWidget()
        self.cpu_page = self._build_page(
            LUCAS_KANADE_PARAMETER_SCHEMA,
            self.cpu_controls,
            self._cpu_rows,
        )
        self.gpu_page = self._build_page(
            LUCAS_KANADE_GPU_PARAMETER_SCHEMA,
            self.gpu_controls,
            self._gpu_rows,
        )
        self.backend_stack.addWidget(self.cpu_page)
        self.backend_stack.addWidget(self.gpu_page)
        layout.addWidget(self.backend_stack, 1)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(APPLY_BUTTON)
        reset_btn.setMinimumHeight(28)
        reset_btn.clicked.connect(self._reset_to_defaults)
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(reset_layout)
        layout.addStretch()

        self.cpu_btn.clicked.connect(lambda: self._set_backend("cpu"))
        self.gpu_btn.clicked.connect(lambda: self._set_backend("gpu"))
        self.refresh_responsive_layout()

        # Lock to CPU if app backend is CPU (Taichi C-API does not support cpu arch)
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import (
            is_cpu_backend,
        )

        if is_cpu_backend():
            self.gpu_btn.setVisible(False)
            self._set_backend("cpu", save=False)

    def _build_page(self, schema, target_controls, target_rows):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(10)

        for field in schema:
            widget = self._create_field(field, target_controls, target_rows)
            if widget is not None:
                page_layout.addWidget(widget)

        page_layout.addStretch()
        return page

    def _create_field(self, field, target_controls, target_rows):
        field_type = field["type"]
        key = field["key"]
        label = field.get("label", key)
        tooltip = self._resolve_tooltip(field)
        default = field.get("default")

        if field_type == "dropdown":
            form = dropdown(label, field.get("options", []), default, tooltip=tooltip)
            form.input.currentIndexChanged.connect(self._save_current_config)
            target_controls[key] = (field, form)
            return form

        if field_type == "toggle":
            row_layout, button = toggle(label, bool(default), tooltip=tooltip)
            button.toggled.connect(
                lambda checked, btn=button: btn.setText("ON" if checked else "OFF")
            )
            button.toggled.connect(self._save_current_config)
            target_controls[key] = (field, button)
            return row_layout

        if field_type == "slider":
            scale = float(field.get("scale", 1.0))
            slider_value = int(round(float(default) / scale))
            row, slider_widget, _ = slider(
                label,
                int(field.get("min", 0)),
                int(field.get("max", 100)),
                slider_value,
                format_func=lambda v, s=scale, f=field: self._format_slider_value(
                    v * s, f
                ),
                tooltip=tooltip,
            )
            slider_widget.sliderReleased.connect(
                lambda sw=slider_widget, f=field: self._commit_slider_position(sw, f)
            )
            slider_widget.value_input.editingFinished.connect(
                lambda sw=slider_widget, f=field: self._commit_slider_text(sw, f)
            )
            target_controls[key] = (field, slider_widget)
            target_rows.append(row)
            return row

        return None

    def _resolve_tooltip(self, field):
        tooltip_key = field.get("tooltip_key")
        if tooltip_key:
            return getattr(language_config, tooltip_key, field.get("tooltip", ""))
        return field.get("tooltip", "")

    def _read_value(self, field, control):
        if field["type"] == "dropdown":
            return control.input.currentText()
        if field["type"] == "toggle":
            return control.isChecked()
        if field["type"] == "slider":
            return control.value() * float(field.get("scale", 1.0))
        return field.get("default")

    def _coerce_value(self, field, value):
        value_type = field.get("value_type", "str")
        if value_type == "int":
            return int(round(float(value)))
        if value_type == "float":
            return float(value)
        if value_type == "bool":
            return bool(value)
        return value

    def _format_slider_value(self, value, field):
        if field.get("key") == "ai_batch_size" and int(round(value)) == 16:
            return "Full Frame"
        value_type = field.get("value_type", "float")
        decimals = int(field.get("decimals", 2 if value_type == "float" else 0))
        if value_type == "int" or decimals <= 0:
            return str(int(round(value)))
        return f"{float(value):.{decimals}f}"

    def _commit_slider_position(self, slider_widget, field):
        self._save_current_config()

    def _commit_slider_text(self, slider_widget, field):
        scale = float(field.get("scale", 1.0))
        row = getattr(slider_widget, "row_widget", None)
        if row:
            row.set_slider_value_from_text(scale)
        self._save_current_config()

    def _collect_controls(self, controls, loader):
        config = loader()
        for key, (field, control) in controls.items():
            config[key] = self._coerce_value(field, self._read_value(field, control))
        return config

    def _apply_toggle_styles(self):
        active_style = """
            QPushButton {
                background-color: #E6F4EA;
                color: #137333;
                border: 1px solid #A3E2B8;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D2EBD9;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: #F4F6F7;
                color: #52606D;
                border: 1px solid #D9E2EC;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #EAECEE;
            }
        """
        self.cpu_btn.setStyleSheet(
            active_style if self.cpu_btn.isChecked() else inactive_style
        )
        self.gpu_btn.setStyleSheet(
            active_style if self.gpu_btn.isChecked() else inactive_style
        )

    def _set_backend(self, backend, save=True):
        if backend == "gpu":
            self.gpu_btn.setChecked(True)
            self.cpu_btn.setChecked(False)
            self.backend_stack.setCurrentWidget(self.gpu_page)
        else:
            self.cpu_btn.setChecked(True)
            self.gpu_btn.setChecked(False)
            self.backend_stack.setCurrentWidget(self.cpu_page)
        self._apply_toggle_styles()
        if save and not self._loading:
            self._save_current_config()

    def _load_configs(self):
        self._loading = True
        cpu_config = load_lucas_kanade_config()
        gpu_config = load_lucas_kanade_gpu_config()

        for key, (field, control) in self.cpu_controls.items():
            value = cpu_config.get(key, field.get("default"))
            if field["type"] == "dropdown":
                control.set_value(str(value))
            elif field["type"] == "toggle":
                control.setChecked(bool(value))
                control.setText("ON" if control.isChecked() else "OFF")
            elif field["type"] == "slider":
                scale = float(field.get("scale", 1.0))
                control.setValue(int(round(float(value) / scale)))
                row = getattr(control, "row_widget", None)
                if row:
                    row._update_value_text(control.value())

        for key, (field, control) in self.gpu_controls.items():
            value = gpu_config.get(key, field.get("default"))
            if field["type"] == "dropdown":
                control.set_value(str(value))

        self._set_backend(
            str(cpu_config.get("backend", "cpu")).strip().lower(), save=False
        )
        self._loading = False

    def _save_current_config(self):
        if self._loading:
            return
        backend = "gpu" if self.gpu_btn.isChecked() else "cpu"
        cpu_config = self._collect_controls(self.cpu_controls, load_lucas_kanade_config)
        cpu_config["backend"] = backend
        gpu_config = self._collect_controls(
            self.gpu_controls, load_lucas_kanade_gpu_config
        )

        save_lucas_kanade_config(cpu_config)
        save_lucas_kanade_gpu_config(gpu_config)
        save_alignment_config_for_active_batch(
            "Lucas Kanade", "lucas_kanade_params", cpu_config
        )
        save_alignment_config_for_active_batch(
            "Lucas Kanade", "lucas_kanade_gpu_params", gpu_config
        )

    def _reset_to_defaults(self):
        self._loading = True
        cpu_defaults = {}
        gpu_defaults = {}
        for field in LUCAS_KANADE_PARAMETER_SCHEMA:
            cpu_defaults[field["key"]] = field.get("default")
        for field in LUCAS_KANADE_GPU_PARAMETER_SCHEMA:
            gpu_defaults[field["key"]] = field.get("default")
        cpu_defaults["backend"] = "cpu"
        save_lucas_kanade_config(cpu_defaults)
        save_lucas_kanade_gpu_config(gpu_defaults)
        self._loading = False
        self._load_configs()
        self._save_current_config()

    def refresh_responsive_layout(self):
        available_width = max(240, self.width() - 24)
        for row in self._cpu_rows:
            row.apply_density(available_width)
        for row in self._gpu_rows:
            row.apply_density(available_width)


class DenoisingParameterPage(AlignmentParameterPage):
    """Render a denoising algorithm's provider schema with generic controls."""

    def __init__(self, algorithm_name, parent=None):
        QWidget.__init__(self, parent)
        self.algorithm_name = algorithm_name
        self.provider = DENOISING_PARAMETER_PROVIDERS.get(algorithm_name)
        self.controls = {}
        self._loading = False
        self._responsive_slider_rows = []
        self._setup_ui()

    def _create_field(self, field, value):
        field_type = field["type"]
        key = field["key"]
        label = field.get("label", key)
        tooltip = self._resolve_tooltip(field)

        if field_type == "dropdown":
            form = dropdown(label, field.get("options", []), value, tooltip=tooltip)
            form.input.currentIndexChanged.connect(
                lambda *_: self._save_current_config()
            )
            self.controls[key] = (field, form)
            return form

        if field_type == "text":
            form = text(label, value, tooltip=tooltip)
            form.input.editingFinished.connect(self._save_current_config)
            self.controls[key] = (field, form)
            return form

        if field_type == "toggle":
            row_layout, button = toggle(label, bool(value), tooltip=tooltip)
            button.setText("ON" if button.isChecked() else "OFF")
            button.toggled.connect(
                lambda checked, btn=button: btn.setText("ON" if checked else "OFF")
            )
            button.toggled.connect(lambda *_: self._save_current_config())
            self.controls[key] = (field, button)
            return row_layout

        if field_type == "slider":
            scale = float(field.get("scale", 1.0))
            slider_value = int(round(float(value) / scale))
            row, slider_widget, _ = slider(
                label,
                int(field.get("min", 0)),
                int(field.get("max", 100)),
                slider_value,
                format_func=lambda v, s=scale, f=field: self._format_slider_value(
                    v * s, f
                ),
                tooltip=tooltip,
            )
            slider_widget.sliderReleased.connect(
                lambda sw=slider_widget, f=field: self._commit_slider_position(sw, f)
            )
            slider_widget.value_input.editingFinished.connect(
                lambda sw=slider_widget, f=field: self._commit_slider_text(sw, f)
            )
            self.controls[key] = (field, slider_widget)
            self._responsive_slider_rows.append(row)
            return row

        return None

    def _resolve_tooltip(self, field):
        tooltip_key = field.get("tooltip_key")
        if tooltip_key:
            return getattr(language_config, tooltip_key, field.get("tooltip", ""))
        return field.get("tooltip", "")

    def _collect_current_config(self):
        config = self.provider["load"]()
        for key, (field, control) in self.controls.items():
            config[key] = self._coerce_value(field, self._read_value(field, control))
        return config

    def _read_value(self, field, control):
        field_type = field["type"]
        if field_type == "dropdown":
            return control.input.currentText()
        if field_type == "text":
            return control.input.text()
        if field_type == "toggle":
            return control.isChecked()
        if field_type == "slider":
            return control.value() * float(field.get("scale", 1.0))
        return field.get("default")

    def _format_slider_value(self, value, field):
        value_type = field.get("value_type", "float")
        decimals = int(field.get("decimals", 2 if value_type == "float" else 0))
        if value_type == "int" or decimals <= 0:
            return str(int(round(value)))
        return f"{float(value):.{decimals}f}"

    def _snap_slider_value(self, slider_value, field):
        step = int(field.get("step", 1))
        if step <= 1:
            return slider_value
        min_value = int(field.get("min", slider_value))
        return min_value + round((slider_value - min_value) / step) * step

    def _commit_slider_position(self, slider_widget, field):
        snapped = self._snap_slider_value(slider_widget.value(), field)
        if snapped != slider_widget.value():
            slider_widget.setValue(snapped)
        self._save_current_config()

    def _commit_slider_text(self, slider_widget, field):
        scale = float(field.get("scale", 1.0))
        row = getattr(slider_widget, "row_widget", None)
        if row and row.set_slider_value_from_text(scale):
            snapped = self._snap_slider_value(slider_widget.value(), field)
            if snapped != slider_widget.value():
                slider_widget.setValue(snapped)
            self._save_current_config()

    def _coerce_value(self, field, value):
        value_type = field.get("value_type", "str")
        try:
            if value_type == "int":
                coerced = int(float(value))
                step = int(field.get("step", 1))
                if step > 1:
                    min_value = int(field.get("min", coerced))
                    coerced = min_value + round((coerced - min_value) / step) * step
                return coerced
            if value_type == "float":
                coerced = float(value)
                step = float(field.get("step", 0))
                if step > 0:
                    min_value = float(field.get("min", coerced))
                    scale = float(field.get("scale", 1.0))
                    min_value *= scale
                    step *= scale
                    coerced = min_value + round((coerced - min_value) / step) * step
                return coerced
            if value_type == "bool":
                return bool(value)
        except (TypeError, ValueError):
            return field.get("default")
        return str(value)

    def _save_current_config(self):
        if self._loading or not self.provider:
            return
        config = self._collect_current_config()
        self.provider["save"](config)
        self.provider["save_batch"](config)

    def _reset_to_defaults(self):
        if not self.provider:
            return
        config = {}
        for field in self.provider["schema"]:
            config[field["key"]] = field.get("default")
        self.provider["save"](config)
        self.provider["save_batch"](config)
        self._reload_values(config)

    def _reload_values(self, config):
        self._loading = True
        for key, (field, control) in self.controls.items():
            value = config.get(key, field.get("default"))
            if field["type"] == "dropdown":
                control.set_value(str(value))
            elif field["type"] == "text":
                control.input.setText(str(value))
            elif field["type"] == "toggle":
                control.setChecked(bool(value))
                control.setText("ON" if control.isChecked() else "OFF")
            elif field["type"] == "slider":
                scale = float(field.get("scale", 1.0))
                slider_value = int(round(float(value) / scale))
                slider_value = max(
                    control.minimum(), min(control.maximum(), slider_value)
                )
                control.setValue(slider_value)
                row = getattr(control, "row_widget", None)
                if row:
                    row._update_value_text(control.value())
        self._loading = False


for _method_name in (
    "_create_field",
    "_resolve_tooltip",
    "_collect_current_config",
    "_read_value",
    "_format_slider_value",
    "_snap_slider_value",
    "_commit_slider_position",
    "_commit_slider_text",
    "_coerce_value",
    "_save_current_config",
    "_reset_to_defaults",
    "_reload_values",
):
    setattr(
        AlignmentParameterPage,
        _method_name,
        getattr(DenoisingParameterPage, _method_name),
    )


# ═══════════════════════════════════════════════════════════════════════
# SIMILARITY PARAMETER PAGE (CPU/GPU toggle)
# ═══════════════════════════════════════════════════════════════════════


@live_update("refresh_responsive_layout", on_resize=True)
class SimilarityParameterPage(QWidget):
    """Similarity denoising parameter page with CPU/GPU backend toggle.

    Both backends use the same SIMILARITY_PARAMETER_SCHEMA sliders.
    The toggle only changes `similarity_backend` in the saved config.
    When device_backend_arch=cpu, the GPU button is hidden/locked.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading = False
        self.controls = {}
        self._rows = []
        self.widgets_by_key = {}
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import (
            is_cpu_backend,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        title = QLabel("Similarity")
        title.setFont(get_default_font(10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setMinimumHeight(32)
        layout.addWidget(title)

        mode_label = QLabel("Backend")
        mode_label.setFont(get_default_font(9, QFont.Weight.Bold))
        mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mode_label)

        toggle_row = QHBoxLayout()
        toggle_row.addStretch()
        self.backend_buttons = QButtonGroup(self)
        self.cpu_btn = QPushButton("CPU")
        self.gpu_btn = QPushButton("GPU")
        self.ai_btn = QPushButton("AI")
        # AI WeightNet is temporarily quarantined from the production UI.  The
        # control remains instantiated so the old settings schema can be
        # restored later without a migration, but it is not user-selectable.
        self.ai_btn.setVisible(False)
        self.ai_btn.setEnabled(False)
        for btn in (self.cpu_btn, self.gpu_btn, self.ai_btn):
            btn.setCheckable(True)
            btn.setFixedHeight(26)
            btn.setMinimumWidth(60)
            self.backend_buttons.addButton(btn)
            toggle_row.addWidget(btn)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)

        # Build parameter controls (same schema for CPU and GPU)
        for field in SIMILARITY_PARAMETER_SCHEMA:
            key = field["key"]
            label_text = field.get("label", key)
            tooltip_key = field.get("tooltip_key")
            tooltip = (
                getattr(language_config, tooltip_key, field.get("tooltip", ""))
                if tooltip_key
                else field.get("tooltip", "")
            )
            field_type = field["type"]
            default = field.get("default")

            if field_type == "dropdown":
                form = dropdown(
                    label_text, field.get("options", []), default, tooltip=tooltip
                )
                form.input.currentIndexChanged.connect(self._save_config)
                self.controls[key] = (field, form)
                self.widgets_by_key[key] = form
                layout.addWidget(form)

            elif field_type == "toggle":
                row_widget, button = toggle(label_text, bool(default), tooltip=tooltip)
                button.setText("ON" if button.isChecked() else "OFF")
                button.toggled.connect(
                    lambda checked, btn=button: btn.setText("ON" if checked else "OFF")
                )
                button.toggled.connect(self._save_config)
                self.controls[key] = (field, button)
                self.widgets_by_key[key] = row_widget
                layout.addWidget(row_widget)

            elif field_type == "slider":
                scale = float(field.get("scale", 1.0))
                slider_value = int(round(float(default) / scale))
                row, slider_widget, _ = slider(
                    label_text,
                    int(field.get("min", 0)),
                    int(field.get("max", 100)),
                    slider_value,
                    format_func=lambda v, s=scale, f=field: self._fmt(v * s, f),
                    tooltip=tooltip,
                )
                slider_widget.sliderReleased.connect(self._save_config)
                slider_widget.value_input.editingFinished.connect(
                    lambda sw=slider_widget, f=field: self._commit_text(sw, f)
                )
                self.controls[key] = (field, slider_widget)
                self.widgets_by_key[key] = row
                self._rows.append(row)
                layout.addWidget(row)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(APPLY_BUTTON)
        reset_btn.setMinimumHeight(28)
        reset_btn.clicked.connect(self._reset_to_defaults)
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(reset_layout)
        layout.addStretch()

        self.cpu_btn.clicked.connect(lambda: self._set_backend("cpu"))
        self.gpu_btn.clicked.connect(lambda: self._set_backend("gpu"))
        # Lock to CPU if app backend arch is cpu.
        self._cpu_only = is_cpu_backend()
        if self._cpu_only:
            self.gpu_btn.setVisible(False)
            mode_label.setText("Backend")

        self.refresh_responsive_layout()

    def _fmt(self, value, field):
        value_type = field.get("value_type", "float")
        decimals = int(field.get("decimals", 2 if value_type == "float" else 0))
        if value_type == "int" or decimals <= 0:
            return str(int(round(value)))
        return f"{float(value):.{decimals}f}"

    def _commit_text(self, slider_widget, field):
        scale = float(field.get("scale", 1.0))
        row = getattr(slider_widget, "row_widget", None)
        if row:
            row.set_slider_value_from_text(scale)
        self._save_config()

    def _apply_toggle_styles(self):
        active_style = """
            QPushButton {
                background-color: #E6F4EA;
                color: #137333;
                border: 1px solid #A3E2B8;
                border-radius: 13px;
                padding: 2px 8px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #D2EBD9; }
        """
        inactive_style = """
            QPushButton {
                background-color: #F4F6F7;
                color: #52606D;
                border: 1px solid #D9E2EC;
                border-radius: 13px;
                padding: 2px 8px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #EAECEE; }
        """
        self.cpu_btn.setStyleSheet(
            active_style if self.cpu_btn.isChecked() else inactive_style
        )
        self.gpu_btn.setStyleSheet(
            active_style if self.gpu_btn.isChecked() else inactive_style
        )
        self.ai_btn.setStyleSheet(
            active_style if self.ai_btn.isChecked() else inactive_style
        )

    def _set_backend(self, backend, save=True):
        if backend == "ai":
            # Normalize stale persisted AI settings to the maintained spatial
            # backend while the AI route is quarantined.
            backend = "cpu" if getattr(self, "_cpu_only", False) else "gpu"
            self.ai_btn.setChecked(False)
            self.gpu_btn.setChecked(backend == "gpu")
            self.cpu_btn.setChecked(backend == "cpu")
        elif backend == "gpu" and not getattr(self, "_cpu_only", False):
            self.gpu_btn.setChecked(True)
            self.cpu_btn.setChecked(False)
            self.ai_btn.setChecked(False)
        else:
            self.cpu_btn.setChecked(True)
            self.gpu_btn.setChecked(False)
            self.ai_btn.setChecked(False)
        self._apply_toggle_styles()

        ai_keys = {"work_resolution_scale", "ai_tile_size", "ai_overlap_percent", "ai_batch_size", "ai_model_type"}
        for key, widget in self.widgets_by_key.items():
            widget.setVisible(key not in ai_keys)

        if save and not self._loading:
            self._save_config()

    def _load_config(self):
        self._loading = True
        config = load_similarity_config()
        for key, (field, control) in self.controls.items():
            value = config.get(key, field.get("default"))
            if field["type"] == "dropdown":
                control.set_value(str(value))
            elif field["type"] == "toggle":
                control.setChecked(bool(value))
                control.setText("ON" if control.isChecked() else "OFF")
            elif field["type"] == "slider":
                scale = float(field.get("scale", 1.0))
                control.setValue(int(round(float(value) / scale)))
                row = getattr(control, "row_widget", None)
                if row:
                    row._update_value_text(control.value())

        backend = str(config.get("similarity_backend", "gpu")).strip().lower()
        if backend == "ai":
            backend = "cpu" if getattr(self, "_cpu_only", False) else "gpu"
        if getattr(self, "_cpu_only", False):
            backend = "cpu"
        self._set_backend(backend, save=False)
        self._loading = False

    def _collect_config(self):
        config = load_similarity_config()
        for key, (field, control) in self.controls.items():
            ft = field["type"]
            if ft == "dropdown":
                config[key] = control.input.currentText()
                try:
                    vt = field.get("value_type", "str")
                    if vt == "int":
                        config[key] = int(float(config[key]))
                    elif vt == "float":
                        config[key] = float(config[key])
                except (ValueError, TypeError):
                    pass
            elif ft == "toggle":
                config[key] = control.isChecked()
            elif ft == "slider":
                config[key] = control.value() * float(field.get("scale", 1.0))
        if self.gpu_btn.isChecked():
            config["similarity_backend"] = "gpu"
        else:
            config["similarity_backend"] = "cpu"
        return config

    def _save_config(self):
        if self._loading:
            return
        config = self._collect_config()
        save_similarity_config(config)
        save_similarity_config_for_active_batch(config)

    def _reset_to_defaults(self):
        self._loading = True
        config = {k: v for k, v in SIMILARITY_PARAMETER_SCHEMA[0].items()}
        defaults = {}
        for field in SIMILARITY_PARAMETER_SCHEMA:
            defaults[field["key"]] = field.get("default")
        defaults["similarity_backend"] = (
            "cpu" if getattr(self, "_cpu_only", False) else "gpu"
        )
        save_similarity_config(defaults)
        self._loading = False
        self._load_config()
        self._save_config()

    def refresh_responsive_layout(self):
        available_width = max(240, self.width() - 24)
        for row in self._rows:
            row.apply_density(available_width)


def get_alignment_settings_page(algorithm_name):
    if algorithm_name == "Lucas Kanade":
        page = LucasKanadeParameterPage()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(page)
        scroll.setStyleSheet(SCROLL_AREA)
        return scroll

    page = AlignmentParameterPage(algorithm_name)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll


def get_denoising_settings_page(algorithm_name):
    if algorithm_name == "Similarity":
        page = SimilarityParameterPage()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(page)
        scroll.setStyleSheet(SCROLL_AREA)
        return scroll

    page = DenoisingParameterPage(algorithm_name)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(page)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll


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
        margin_lr = margin // 2

        for page in self._tab_pages:
            page_layout = page.layout()
            if page_layout:
                page_layout.setContentsMargins(margin_lr, margin, margin_lr, margin)
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
            "Tile Size:",
            [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256],
            default=16,
            tooltip="Ukuran tile untuk pemrosesan spasial",
        )
        layout.addWidget(self.similarity_widgets["similarity_spatial_tile_size"])

        # Processing Cores
        max_cores = os.cpu_count() or 4
        self.similarity_widgets["similarity_spatial_num_workers"] = dropdown(
            "Processing Cores:",
            ["Auto"] + [str(i) for i in range(1, max_cores + 1)],
            default="Auto",
            tooltip="Jumlah inti CPU untuk pemrosesan paralel",
        )
        layout.addWidget(self.similarity_widgets["similarity_spatial_num_workers"])

        # Overlap
        overlap_layout, self._overlap_slider, _ = slider(
            "Overlap %:",
            0,
            90,
            30,
            format_func=lambda v: str(v),
            tooltip="Persentase overlap antar tile",
        )
        self.similarity_widgets["similarity_spatial_overlap_percent"] = overlap_layout
        self._responsive_slider_rows.append(overlap_layout)
        layout.addWidget(overlap_layout)

        # Motion Sensitivity
        motion_layout, self._motion_slider, _ = slider(
            "Motion Sensitivity:",
            10,
            2000,
            1500,
            format_func=lambda v: f"{v/10.0:.1f}",
            tooltip="Sensitivitas terhadap gerakan",
        )
        self.similarity_widgets["similarity_spatial_motion_sensitivity"] = motion_layout
        self._responsive_slider_rows.append(motion_layout)
        layout.addWidget(motion_layout)

        # Noise Offset Factor
        noise_layout, self._noise_slider, _ = slider(
            "Noise Offset Factor:",
            0,
            100,
            15,
            format_func=lambda v: f"{v/100.0:.2f}",
            tooltip="Faktor offset noise untuk thresholding",
        )
        self.similarity_widgets["similarity_spatial_noise_mad_offset_factor"] = (
            noise_layout
        )
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
            "Threshold:",
            default=0.008,
            tooltip="Threshold untuk deteksi keypoint AKAZE",
        )
        layout.addWidget(self.akaze_widgets["akaze_threshold"])

        self.akaze_widgets["akaze_nOctaves"] = dropdown(
            "Octaves:",
            [1, 2, 3, 4, 5, 6, 7, 8],
            default=4,
            tooltip="Jumlah octave untuk scale space",
        )
        layout.addWidget(self.akaze_widgets["akaze_nOctaves"])

        self.akaze_widgets["akaze_nOctaveLayers"] = dropdown(
            "Octave Layers:",
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            default=4,
            tooltip="Jumlah layer per octave",
        )
        layout.addWidget(self.akaze_widgets["akaze_nOctaveLayers"])

        self.akaze_widgets["ratio_threshold"] = text(
            "Ratio Threshold:",
            default=0.75,
            tooltip="Ratio threshold untuk Lowe's ratio test",
        )
        layout.addWidget(self.akaze_widgets["ratio_threshold"])

        self.akaze_widgets["transformation"] = dropdown(
            "Transformation:",
            ["homography", "affine"],
            default="homography",
            tooltip="Tipe transformasi geometris",
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
            "Max Features:",
            default=1500,
            tooltip="Jumlah maksimum keypoint yang dideteksi",
        )
        layout.addWidget(self.orb_widgets["nfeatures"])

        self.orb_widgets["scaleFactor"] = text(
            "Scale Factor:", default=1.1, tooltip="Faktor skala untuk image pyramid"
        )
        layout.addWidget(self.orb_widgets["scaleFactor"])

        self.orb_widgets["nlevels"] = dropdown(
            "Levels:",
            [1, 2, 3, 4, 5, 6, 7, 8],
            default=5,
            tooltip="Jumlah level untuk image pyramid",
        )
        layout.addWidget(self.orb_widgets["nlevels"])

        self.orb_widgets["ransacThreshold"] = text(
            "RANSAC Threshold:",
            default=5.0,
            tooltip="Threshold untuk RANSAC inlier detection",
        )
        layout.addWidget(self.orb_widgets["ransacThreshold"])

        self.orb_widgets["transformation"] = dropdown(
            "Transformation:",
            ["homography", "affine"],
            default="homography",
            tooltip="Tipe transformasi geometris",
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
            "Tile Size:",
            [128, 192, 256, 320, 384, 512, 640, 768, 896, 1024],
            default=256,
            tooltip="Ukuran tile untuk pemrosesan tile-based (pixels)",
        )
        layout.addWidget(self.tile_based_widgets["tile_based_tile_size"])

        # Alignment Backend
        self.tile_based_widgets["tile_based_alignment_backend"] = dropdown(
            "Alignment Backend:",
            ["farneback", "lucas_kanade", "none"],
            default="farneback",
            tooltip="Algoritma optical flow untuk alignment",
        )
        layout.addWidget(self.tile_based_widgets["tile_based_alignment_backend"])

        # Overlap
        overlap_layout, self._tb_overlap_slider, _ = slider(
            "Overlap %:",
            0,
            50,
            20,
            format_func=lambda v: str(v),
            tooltip="Persentase overlap antar tile",
        )
        self.tile_based_widgets["tile_based_overlap_percent"] = overlap_layout
        self._responsive_slider_rows.append(overlap_layout)
        layout.addWidget(overlap_layout)

        # Motion Sensitivity
        motion_layout, self._tb_motion_slider, _ = slider(
            "Motion Sensitivity:",
            10,
            2000,
            1500,
            format_func=lambda v: f"{v/10.0:.1f}",
            tooltip="Sensitivitas terhadap gerakan (ghost rejection)",
        )
        self.tile_based_widgets["tile_based_motion_sensitivity"] = motion_layout
        self._responsive_slider_rows.append(motion_layout)
        layout.addWidget(motion_layout)

        # Noise Offset Factor
        noise_layout, self._tb_noise_slider, _ = slider(
            "Noise Offset Factor:",
            0,
            100,
            15,
            format_func=lambda v: f"{v/100.0:.2f}",
            tooltip="Faktor offset noise untuk thresholding",
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

        motion_val = int(
            config.get("similarity_spatial_motion_sensitivity", 150.0) * 10
        )
        self._motion_slider.setValue(motion_val)

        noise_val = int(
            config.get("similarity_spatial_noise_mad_offset_factor", 0.15) * 100
        )
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
        config = (
            load_similarity_config()
        )  # Reuse similarity config for tile-based settings
        # Set dropdowns
        tile_size = config.get("tile_based_tile_size", 256)
        self.tile_based_widgets["tile_based_tile_size"].set_value(str(tile_size))

        alignment_backend = config.get("tile_based_alignment_backend", "farneback")
        self.tile_based_widgets["tile_based_alignment_backend"].set_value(
            alignment_backend
        )

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
        self.similarity_widgets[
            "similarity_spatial_tile_size"
        ].input.currentIndexChanged.connect(self._save_similarity)
        self.similarity_widgets[
            "similarity_spatial_num_workers"
        ].input.currentIndexChanged.connect(self._save_similarity)
        self._overlap_slider.sliderReleased.connect(self._save_similarity)
        self._motion_slider.sliderReleased.connect(self._save_similarity)
        self._noise_slider.sliderReleased.connect(self._save_similarity)

        # AKAZE
        self.akaze_widgets["akaze_threshold"].input.editingFinished.connect(
            self._save_akaze
        )
        self.akaze_widgets["akaze_nOctaves"].input.currentIndexChanged.connect(
            self._save_akaze
        )
        self.akaze_widgets["akaze_nOctaveLayers"].input.currentIndexChanged.connect(
            self._save_akaze
        )
        self.akaze_widgets["ratio_threshold"].input.editingFinished.connect(
            self._save_akaze
        )
        self.akaze_widgets["transformation"].input.currentIndexChanged.connect(
            self._save_akaze
        )

        # ORB
        self.orb_widgets["nfeatures"].input.editingFinished.connect(self._save_orb)
        self.orb_widgets["scaleFactor"].input.editingFinished.connect(self._save_orb)
        self.orb_widgets["nlevels"].input.currentIndexChanged.connect(self._save_orb)
        self.orb_widgets["ransacThreshold"].input.editingFinished.connect(
            self._save_orb
        )
        self.orb_widgets["transformation"].input.currentIndexChanged.connect(
            self._save_orb
        )

        # Tile-Based
        self.tile_based_widgets[
            "tile_based_tile_size"
        ].input.currentIndexChanged.connect(self._save_tile_based)
        self.tile_based_widgets[
            "tile_based_alignment_backend"
        ].input.currentIndexChanged.connect(self._save_tile_based)
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
            "similarity_spatial_tile_size": int(
                values.get("similarity_spatial_tile_size", 16)
            ),
            "similarity_spatial_num_workers": (
                -1
                if values.get("similarity_spatial_num_workers") == "Auto"
                else int(values.get("similarity_spatial_num_workers", 1))
            ),
            "similarity_spatial_overlap_percent": self._overlap_slider.value() / 100.0,
            "similarity_spatial_motion_sensitivity": self._motion_slider.value() / 10.0,
            "similarity_spatial_noise_mad_offset_factor": self._noise_slider.value()
            / 100.0,
        }
        save_similarity_v1_config(config)
        save_similarity_config_for_active_batch(config)

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
        alignment_backend = values.get("tile_based_alignment_backend", "farneback")
        config = {
            "tile_based_tile_size": int(values.get("tile_based_tile_size", 256)),
            "tile_based_alignment_backend": alignment_backend,
            "alignment_backend": alignment_backend,
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
