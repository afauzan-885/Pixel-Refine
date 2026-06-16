"""
test_side_by_side.py
--------------------
Script to test and visually compare PySide6 Desktop widgets and QML Mobile representations
side-by-side in a single window.
"""

import sys
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QScrollArea,
)
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import QUrl, Qt

# Import Generic UI Components
from resources.GenericUILibrary.theme import QmlThemeBridge, get_theme
from resources.GenericUILibrary.buttons import Button, ToggleButton, ToggleSwitch
from resources.GenericUILibrary.cards import Card, FeatureCard
from resources.GenericUILibrary.forms import Input, Select, Checkbox, RadioGroup
from resources.GenericUILibrary.progress_bars import ProgressBar, IndeterminateProgress
from resources.GenericUILibrary.list_group import ListGroup
from resources.GenericUILibrary.tables import DataTable
from resources.GenericUILibrary.containers import Container, Row, Col

def create_test_components():
    """Create a list of widgets to display."""
    widgets = []

    # 1. Buttons
    widgets.append(QLabel("=== BUTTONS & TOGGLES ==="))
    widgets.append(Button("Primary Button", variant="primary"))
    widgets.append(Button("Success Button", variant="success"))
    widgets.append(ToggleButton("Toggle Me", checked=True))
    widgets.append(ToggleSwitch())

    # 2. Forms
    widgets.append(QLabel("=== FORM CONTROLS ==="))
    widgets.append(Input(placeholder="Type something..."))
    widgets.append(Select(options=["Option A", "Option B", "Option C"]))
    
    cb = Checkbox("Agree to terms", checked=True)
    widgets.append(cb)
    
    rg = RadioGroup(options=["Vertical Mode", "Horizontal Mode"], orientation="vertical")
    widgets.append(rg)

    # 3. Progress
    widgets.append(QLabel("=== PROGRESS & INDICATORS ==="))
    pb = ProgressBar(style="linear", variant="info")
    pb.set_value(75)
    widgets.append(pb)
    
    spinner = IndeterminateProgress(size=40)
    spinner.start()
    widgets.append(spinner)

    # 4. List Group
    widgets.append(QLabel("=== LIST GROUP ==="))
    lg = ListGroup()
    lg.add_item("Item 1 - Active")
    lg.add_item("Item 2 - Secondary")
    lg.select_first()
    widgets.append(lg)

    # 5. Tables
    widgets.append(QLabel("=== DATA TABLE ==="))
    table = DataTable(columns=["Name", "Status"])
    table.add_row_items(["User 1", "Active"])
    table.add_row_items(["User 2", "Offline"])
    table.setFixedHeight(120)
    widgets.append(table)

    # 6. Feature Card
    widgets.append(QLabel("=== PREMIUM CARDS ==="))
    fc = FeatureCard(
        title="Denoising Filter",
        description="Reduce noise using advanced bilateral filter algorithm.",
        options=["Weak", "Medium", "Strong"],
        fallback_val="Off"
    )
    widgets.append(fc)

    return widgets

class SideBySideWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generic UI Side-by-Side: PySide6 (Left) vs QML (Right)")
        self.resize(1000, 800)

        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # ── LEFT PANEL: PySide6 Desktop Widgets ──
        left_area = QScrollArea()
        left_area.setWidgetResizable(True)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)

        pyside_widgets = create_test_components()
        for w in pyside_widgets:
            # Set stylesheet for QLabels to look like headers
            if isinstance(w, QLabel) and "===" in w.text():
                w.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C3E50; margin-top: 15px;")
            left_layout.addWidget(w)
        
        left_layout.addStretch()
        left_area.setWidget(left_widget)
        
        # Wrap left panel in a vertical layout with header
        left_wrapper = QWidget()
        left_vbox = QVBoxLayout(left_wrapper)
        left_vbox.setContentsMargins(0, 0, 0, 0)
        left_title = QLabel("DESKTOP (PySide6 Widget API)")
        left_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #34495E; padding: 5px;")
        left_vbox.addWidget(left_title)
        left_vbox.addWidget(left_area)
        layout.addWidget(left_wrapper, 1)

        # ── RIGHT PANEL: Mobile QML Representation ──
        # Build Container layout containing the exact same structures to get combined QML
        container = Container(padding=15)
        for w in pyside_widgets:
            if not isinstance(w, QLabel):
                container.add_widget(w)

        # Get generated QML
        body_qml = container.to_qml(indent=2)

        # Setup Theme & Bridge for QML Context
        theme_bridge = QmlThemeBridge()
        from pixel_refine_mobile.core.app_bridge import AppBridge
        app_bridge = AppBridge()
        
        # Build full QML script
        full_qml = f"""
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {{
    anchors.fill: parent
    color: genericTheme.bgSecondary

    ScrollView {{
        anchors.fill: parent
        contentWidth: parent.width
        clip: true

        Column {{
            width: parent.width
            spacing: 15
            leftPadding: 15
            rightPadding: 15
            topPadding: 15

            Text {{
                text: "MOBILE (QML Engine Rendering)"
                font.bold: true
                font.pixelSize: 16
                color: "#34495E"
            }}

{body_qml}
        }}
    }}
}}
"""

        # Setup QQuickWidget
        quick_widget = QQuickWidget()
        quick_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        
        # Parent objects to the QQuickWidget to prevent Python garbage collection
        self.theme_bridge = theme_bridge
        self.app_bridge = app_bridge
        self.theme_bridge.setParent(quick_widget)
        self.app_bridge.setParent(quick_widget)
        
        quick_widget.rootContext().setContextProperty("genericTheme", self.theme_bridge)
        quick_widget.rootContext().setContextProperty("appBridge", self.app_bridge)

        # Write to temp file and load
        qml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_test.qml")
        with open(qml_path, "w", encoding="utf-8") as f:
            f.write(full_qml)

        quick_widget.setSource(QUrl.fromLocalFile(qml_path))

        layout.addWidget(quick_widget, 1)

if __name__ == "__main__":
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QApplication(sys.argv)
    window = SideBySideWindow()
    window.show()
    sys.exit(app.exec())
