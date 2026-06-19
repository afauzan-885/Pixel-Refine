"""
app.py
------
MobileApp wrapper — identical API to QMainWindow Desktop.
Only difference: generates QML dynamically via to_qml().
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import Qt

from resources.GenericUILibrary.theme import QmlThemeBridge
from pixel_refine_mobile.core.app_bridge import AppBridge


class MobileApp:
    """
    Mobile wrapper with API identical to QMainWindow Desktop.

    Methods:
        setWindowTitle(title)
        setCentralWidget(widget)  # receives GenericUI component
        show()
        setWindowSize(w, h)
        exec_()
    """

    DEFAULT_WIDTH = 360
    DEFAULT_HEIGHT = 640

    def __init__(self):
        self._title = "Pixel Refine Mobile"
        self._width = self.DEFAULT_WIDTH
        self._height = self.DEFAULT_HEIGHT
        self._widget = None
        self._is_shown = False

        self.theme = QmlThemeBridge()
        self.bridge = AppBridge()

        os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
        if QApplication.instance() is None:
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

        self._app = QApplication.instance() or QApplication(sys.argv)
        self._engine = QQmlApplicationEngine()

        self.theme.setParent(self._engine)
        self.bridge.setParent(self._engine)

        self._engine.rootContext().setContextProperty("genericTheme", self.theme)
        self._engine.rootContext().setContextProperty("appBridge", self.bridge)
        self._engine.warnings.connect(self._on_warnings)

    def setWindowTitle(self, title: str):
        self._title = title

    def setWindowSize(self, width: int, height: int):
        self._width = width
        self._height = height

    def setCentralWidget(self, widget):
        self._widget = widget

    def show(self):
        if self._widget is None:
            raise RuntimeError("Call setCentralWidget() before show()")

        body_qml = self._widget.to_qml(indent=2) if hasattr(self._widget, "to_qml") else ""
        
        # Load the base window only once
        if not self._is_shown:
            base_qml = self._build_base_window()
            self._engine.loadData(base_qml.encode("utf-8"))
            if not self._engine.rootObjects():
                raise RuntimeError("Failed to load base QML")
            self._is_shown = True

        # Dynamically load the page QML using the contentContainer
        root_objects = self._engine.rootObjects()
        if root_objects:
            root_window = root_objects[0]
            from PySide6.QtCore import QObject
            content_container = root_window.findChild(QObject, "contentContainer")
            if content_container:
                content_container.loadPage(body_qml)

    def exec_(self) -> int:
        if not self._is_shown:
            self.show()
        return self._app.exec()

    def _build_base_window(self) -> str:
        return f"""
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {{
    id: window
    visible: true
    width: {self._width}
    height: {self._height}
    title: "{self._title}"
    color: genericTheme.bgSecondary

    ScrollView {{
        anchors.fill: parent
        clip: true
        contentWidth: parent.width
        contentHeight: contentContainer.childrenRect.height
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        Item {{
            id: contentContainer
            objectName: "contentContainer"
            width: parent.width
            
            property string pendingQml: ""
            
            function loadPage(qmlString) {{
                pendingQml = qmlString;
                // If it's the very first page load (opacity is 1 and no children), load instantly
                if (children.length === 0) {{
                    _applyNewPage();
                }} else {{
                    fadeOutAnim.start();
                }}
            }}
            
            function _applyNewPage() {{
                // 1. Destroy all current children
                for (var i = children.length - 1; i >= 0; i--) {{
                    var child = children[i];
                    child.parent = null;
                    child.destroy();
                }}
                // 2. Create the new dynamic page
                if (pendingQml !== "") {{
                    var newObj = Qt.createQmlObject("import QtQuick 2.15; import QtQuick.Controls 2.15; " + pendingQml, contentContainer, "dynamicPage");
                    fadeInAnim.start();
                }}
            }}
            
            NumberAnimation {{
                id: fadeOutAnim
                target: contentContainer
                property: "opacity"
                to: 0.0
                duration: 150
                onStopped: contentContainer._applyNewPage()
            }}
            
            NumberAnimation {{
                id: fadeInAnim
                target: contentContainer
                property: "opacity"
                to: 1.0
                duration: 200
            }}
        }}
    }}
}}
"""

    def _on_warnings(self, warnings):
        for w in warnings:
            print(f"[QML Warning] {w.toString()}", file=sys.stderr)
