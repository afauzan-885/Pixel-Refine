"""
Bootstrap-like Form Components for PySide6
Provides reusable form input components
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QRadioButton,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QButtonGroup,
)
from PySide6.QtCore import Signal, Qt, Slot
from .mixins import RealtimeMixin


class FormGroup(QWidget, RealtimeMixin):
    """
    Form group with label and input field.
    Supports real-time data binding via RealtimeMixin.

    Usage:
        form = FormGroup(label="Username", input_type="text")
        form.bind_store(store, "username")
    """

    value_changed = Signal(object)  # Emits the current value

    def __init__(
        self, label="", input_type="text", placeholder="", auto_sync=False, parent=None
    ):
        super().__init__(parent)
        self.input_type = input_type
        self.auto_sync = auto_sync  # If True, UI changes update store automatically

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove bottom margin
        layout.setSpacing(5)  # Match spacing from similarity_parameter_settings.py

        # Label
        if label:
            self.label = QLabel(label)
            self.label.setStyleSheet("font-weight: bold; margin-bottom: 0px;")
            layout.addWidget(self.label)
        else:
            self.label = None

        # Input field based on type
        if input_type == "text":
            self.input = QLineEdit()
            self.input.setPlaceholderText(placeholder)
            self.input.textChanged.connect(lambda v: self.value_changed.emit(v))
        elif input_type == "number":
            self.input = QSpinBox()
            self.input.setMinimum(0)
            self.input.setMaximum(999)
            # Apply modern styling to match other inputs
            self.input.setStyleSheet(
                """
                QSpinBox {
                    background-color: #FFFFFF;
                    border: 1px solid #E8EDF2;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 11pt;
                    color: #333333;
                }
                QSpinBox:hover {
                    border-color: #0078D4;
                }
                QSpinBox:focus {
                    border-color: #0078D4;
                    border-width: 2px;
                }
                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #E8EDF2;
                    border-bottom: 1px solid #E8EDF2;
                    border-top-right-radius: 4px;
                    background-color: #F5F8FA;
                }
                QSpinBox::up-button:hover {
                    background-color: #E8EDF2;
                }
                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 20px;
                    border-left: 1px solid #E8EDF2;
                    border-bottom-right-radius: 4px;
                    background-color: #F5F8FA;
                }
                QSpinBox::down-button:hover {
                    background-color: #E8EDF2;
                }
                QSpinBox::up-arrow {
                    image: none;
                    width: 0px;
                    height: 0px;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 5px solid #666666;
                }
                QSpinBox::down-arrow {
                    image: none;
                    width: 0px;
                    height: 0px;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #666666;
                }
            """
            )
            self.input.valueChanged.connect(lambda v: self.value_changed.emit(v))
        elif input_type == "decimal":
            self.input = QDoubleSpinBox()
            self.input.valueChanged.connect(lambda v: self.value_changed.emit(v))
        elif input_type == "select":
            self.input = QComboBox()
            self.input.currentTextChanged.connect(lambda v: self.value_changed.emit(v))
        elif input_type == "textarea":
            self.input = QTextEdit()
            self.input.setMaximumHeight(100)
            self.input.textChanged.connect(
                lambda: self.value_changed.emit(self.input.toPlainText())
            )
        else:
            self.input = QLineEdit()

        layout.addWidget(self.input)

        # Connect internal signal for auto-sync
        self.value_changed.connect(self._handle_internal_value_change)

        # Add stretch to keep label and input close together at the top
        # even if the widget is stretched vertically
        layout.addStretch()

    def get_value(self):
        """Get current value"""
        if isinstance(self.input, QLineEdit):
            return self.input.text()
        elif isinstance(self.input, (QSpinBox, QDoubleSpinBox)):
            return self.input.value()
        elif isinstance(self.input, QComboBox):
            return self.input.currentText()
        elif isinstance(self.input, QTextEdit):
            return self.input.toPlainText()
        return None

    def set_value(self, value):
        """Set value"""
        if isinstance(self.input, QLineEdit):
            self.input.setText(str(value))
        elif isinstance(self.input, (QSpinBox, QDoubleSpinBox)):
            self.input.setValue(value)
        elif isinstance(self.input, QComboBox):
            index = self.input.findText(str(value))
            if index >= 0:
                self.input.setCurrentIndex(index)
        elif isinstance(self.input, QTextEdit):
            self.input.setPlainText(str(value))

    def add_options(self, options):
        """Add options to select input"""
        if isinstance(self.input, QComboBox):
            self.input.addItems(options)

    # --- RealtimeMixin Implementation ---

    def on_store_changed(self, key, value):
        """Update UI value from Store."""
        if value is not None:
            # Block internal signal to prevent loop if auto_sync is on
            self.blockSignals(True)
            self.set_value(value)
            self.blockSignals(False)

    def _handle_internal_value_change(self, value):
        """Handle value change from UI side."""
        if self.auto_sync:
            self.set_data(value)


class Input(QLineEdit):
    """
    Enhanced text input with validation states

    Usage:
        input = Input(placeholder="Enter email")
        input.set_state("valid")  # or "invalid", "warning"
    """

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._state = "normal"

    def set_state(self, state):
        """Set validation state: 'valid', 'invalid', 'warning', 'normal'"""
        self._state = state

        if state == "valid":
            self.setStyleSheet("border-bottom: 2px solid #2ecc71;")
        elif state == "invalid":
            self.setStyleSheet("border-bottom: 2px solid #e74c3c;")
        elif state == "warning":
            self.setStyleSheet("border-bottom: 2px solid #f39c12;")
        else:
            self.setStyleSheet("")


class Select(QComboBox):
    """
    Enhanced dropdown/select component

    Usage:
        select = Select(options=["Option 1", "Option 2"])
        select.value_changed.connect(on_change)
    """

    value_changed = Signal(str, int)  # text, index

    def __init__(self, options=None, placeholder=None, parent=None):
        super().__init__(parent)

        if placeholder:
            self.addItem(placeholder)
            self.setCurrentIndex(0)

        if options:
            self.addItems(options)

        self.currentIndexChanged.connect(
            lambda idx: self.value_changed.emit(self.currentText(), idx)
        )

    def set_options(self, options):
        """Replace all options"""
        self.clear()
        self.addItems(options)


class Checkbox(QWidget, RealtimeMixin):
    """
    Checkbox with label. Supports DataStore binding.

    Usage:
        cb = Checkbox("Option 1")
        cb.bind_store(store, "option_1_enabled")
    """

    toggled = Signal(bool)

    def __init__(self, text="", checked=False, auto_sync=False, parent=None):
        super().__init__(parent)
        self.auto_sync = auto_sync

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox(text)
        self.checkbox.setChecked(checked)
        self.checkbox.toggled.connect(self._on_internal_toggle)

        layout.addWidget(self.checkbox)
        layout.addStretch()

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)

    # --- RealtimeMixin ---
    def on_store_changed(self, key, value):
        if isinstance(value, bool):
            self.checkbox.blockSignals(True)
            self.checkbox.setChecked(value)
            self.checkbox.blockSignals(False)

    def _on_internal_toggle(self, checked):
        self.toggled.emit(checked)
        if self.auto_sync:
            self.set_data(checked)


class Radio(QWidget):
    """
    Radio button with label

    Usage:
        radio = Radio("Option 1")
        radio.toggled.connect(on_toggle)
    """

    toggled = Signal(bool)

    def __init__(self, text="", checked=False, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.radio = QRadioButton(text)
        self.radio.setChecked(checked)
        self.radio.toggled.connect(self.toggled.emit)

        layout.addWidget(self.radio)
        layout.addStretch()

    def is_checked(self):
        return self.radio.isChecked()

    def set_checked(self, checked):
        self.radio.setChecked(checked)


class RadioGroup(QWidget, RealtimeMixin):
    """
    Group of radio buttons. Supports DataStore binding (index or text).

    Usage:
        group = RadioGroup(options=["A", "B"])
        group.bind_store(store, "selected_mode")
    """

    selection_changed = Signal(int, str)  # index, text

    def __init__(
        self, options=None, orientation="vertical", auto_sync=False, parent=None
    ):
        super().__init__(parent)
        self.auto_sync = auto_sync

        self.button_group = QButtonGroup(self)
        self.radios = []

        if orientation == "vertical":
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        # Connect internal signal
        self.selection_changed.connect(self._on_internal_selection_change)

        if options:
            for i, option in enumerate(options):
                self.add_option(option)

    def add_option(self, text, checked=False):
        """Add a radio option"""
        radio = QRadioButton(text)
        radio.setChecked(checked)

        index = len(self.radios)
        self.button_group.addButton(radio, index)
        self.radios.append(radio)

        radio.toggled.connect(
            lambda checked, idx=index, txt=text: (
                self.selection_changed.emit(idx, txt) if checked else None
            )
        )

        self.layout().addWidget(radio)

    def get_selected_index(self):
        """Get index of selected option"""
        return self.button_group.checkedId()

    def get_selected_text(self):
        """Get text of selected option"""
        checked = self.button_group.checkedButton()
        return checked.text() if checked else None

    def set_selected(self, index):
        """Set selected option by index"""
        if 0 <= index < len(self.radios):
            self.radios[index].setChecked(True)

    # --- RealtimeMixin ---
    def on_store_changed(self, key, value):
        if isinstance(value, int):
            self._block_radios(True)
            self.set_selected(value)
            self._block_radios(False)
        elif isinstance(value, str):
            # Try find by text
            for i, radio in enumerate(self.radios):
                if radio.text() == value:
                    self._block_radios(True)
                    radio.setChecked(True)
                    self._block_radios(False)
                    break

    def _block_radios(self, block):
        for r in self.radios:
            r.blockSignals(block)

    def _on_internal_selection_change(self, index, text):
        if self.auto_sync:
            # We can sync either index or text. Preferring index for robustness,
            # but usually it matches what's in the store.
            self.set_data(index)


class FormRow(QWidget):
    """
    Horizontal form layout with label and input side by side

    Usage:
        form = FormRow()
        form.add_field("Name:", QLineEdit())
        form.add_field("Age:", QSpinBox())
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.form_layout = QFormLayout(self)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(5)

    def add_field(self, label, widget):
        """Add a field to the form"""
        self.form_layout.addRow(label, widget)

    def add_row(self, widget):
        """Add a full-width row"""
        self.form_layout.addRow(widget)
