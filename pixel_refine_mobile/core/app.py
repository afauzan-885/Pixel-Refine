"""
pixel_refine_mobile/core/app.py
--------------------------------
MobileApp — Wrapper transparan yang membuat pemanggilan komponen
Generic UI Library **100% identik** antara Desktop dan Mobile.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESKTOP                           MOBILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from ...cards import Card         from ...cards import Card     ✅
from ...buttons import Button     from ...buttons import Button ✅
...                               ...

card = Card(title="Denoise")      card = Card(title="Denoise") ✅
btn  = Button("Start","primary")  btn  = Button("Start","primary") ✅
card.add_body_widget(btn)         card.add_body_widget(btn)    ✅
layout.add_widget(card)           layout.add_widget(card)      ✅

window = QMainWindow()            window = MobileApp()         ← satu-satunya beda
window.setWindowTitle("App")      window.setWindowTitle("App") ✅
window.setCentralWidget(layout)   window.setCentralWidget(layout) ✅
window.show()                     window.show()                ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtQml     import QQmlApplicationEngine
from PySide6.QtCore    import QUrl, Qt

from resources.GenericUILibrary.theme import QmlThemeBridge
from pixel_refine_mobile.core.app_bridge import AppBridge


# ── Lokasi folder QML bawaan (untuk ApplicationWindow wrapper) ────────────────
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))


class MobileApp:
    """
    Wrapper Mobile yang API-nya identik dengan QMainWindow Desktop.

    Properti publik:
        theme  (QmlThemeBridge) — akses untuk mengganti tema
        bridge (AppBridge)      — connect signal tool_requested, dst.

    Method publik (identik dengan QMainWindow):
        setWindowTitle(title)
        setCentralWidget(widget)  ← kunci parity — menerima komponen Generic UI
        show()
        setWindowSize(w, h)       ← khusus mobile: atur ukuran layar
        exec_()                   ← jalankan event loop, return exit code
    """

    # ── Ukuran default (portrait phone) ──────────────────────────────────────
    DEFAULT_WIDTH  = 360
    DEFAULT_HEIGHT = 640

    def __init__(self, theme: str = "light"):
        """
        Args:
            theme: "light" atau "dark". Default "light" agar sesuai
                   dengan palette Desktop yang ada.
        """
        self._title    = "Pixel Refine Mobile"
        self._width    = self.DEFAULT_WIDTH
        self._height   = self.DEFAULT_HEIGHT
        self._widget   = None   # widget yang akan di-render
        self._is_shown = False

        # Context objects — tersedia untuk di-connect dari luar
        self.theme  = QmlThemeBridge()
        self.bridge = AppBridge()

        # Engine & App — dibuat sekali saat __init__
        os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
        if QApplication.instance() is None:
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

        # Pastikan QApplication sudah ada (bisa dibuat sebelumnya)
        self._app = QApplication.instance() or QApplication(sys.argv)

        self._engine = QQmlApplicationEngine()
        
        # Parent the theme and bridge to the engine to prevent garbage collection in PySide6 QML context
        self.theme.setParent(self._engine)
        self.bridge.setParent(self._engine)
        
        self._engine.rootContext().setContextProperty("genericTheme", self.theme)
        self._engine.rootContext().setContextProperty("appBridge",    self.bridge)

        # Error logger
        self._engine.warnings.connect(self._on_warnings)

    # ─────────────────────────────────────────────────────────────────────────
    # API PUBLIK — identik dengan QMainWindow
    # ─────────────────────────────────────────────────────────────────────────

    def setWindowTitle(self, title: str):
        """Atur judul window. Identik dengan QMainWindow.setWindowTitle()."""
        self._title = title

    def setWindowSize(self, width: int, height: int):
        """
        Atur ukuran window (khusus mobile).
        Desktop menggunakan resize() / WindowConfig; mobile menggunakan ini.
        """
        self._width  = width
        self._height = height

    def setCentralWidget(self, widget):
        """
        Terima komponen Generic UI (Container, Card, Button, dll.)
        dan persiapkan untuk di-render oleh QML engine.

        Identik dengan QMainWindow.setCentralWidget().
        Secara internal memanggil widget.to_qml() untuk menghasilkan
        kode QML, lalu membungkusnya dalam ApplicationWindow.
        """
        self._widget = widget

    def show(self):
        """
        Render dan tampilkan window.
        Identik dengan QMainWindow.show() / QWidget.show().

        Mengonversi komponen Generic UI ke QML secara otomatis.
        """
        if self._widget is None:
            raise RuntimeError(
                "MobileApp.show() dipanggil tanpa setCentralWidget().\n"
                "Panggil window.setCentralWidget(layout) terlebih dahulu."
            )

        # Konversi komponen Generic UI ke string QML
        body_qml = self._widget.to_qml(indent=2) \
            if hasattr(self._widget, "to_qml") \
            else ""

        # Bungkus dalam ApplicationWindow QML
        full_qml = self._build_application_window(body_qml)

        # Load ke engine
        self._engine.loadData(full_qml.encode("utf-8"))

        if not self._engine.rootObjects():
            raise RuntimeError(
                "MobileApp gagal memuat QML.\n"
                "Periksa output error di atas untuk detail."
            )

        self._is_shown = True

    def exec_(self) -> int:
        """
        Jalankan event loop aplikasi. Return exit code.
        Identik dengan QApplication.exec() yang dipanggil setelah show().

        Contoh:
            window.show()
            sys.exit(window.exec_())
        """
        if not self._is_shown:
            self.show()
        return self._app.exec()

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _build_application_window(self, body_qml: str) -> str:
        """
        Bungkus body QML ke dalam ApplicationWindow standar.
        Menggunakan genericTheme untuk warna background agar tema reaktif.
        """
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

{body_qml}
    }}
}}
"""

    def _on_warnings(self, warnings):
        """Log QML warnings ke stderr."""
        for w in warnings:
            print(f"[MobileApp QML Warning] {w.toString()}", file=sys.stderr)
