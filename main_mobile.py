"""
main_mobile.py
--------------
Entry point aplikasi Pixel Refine Mobile.

Cara menjalankan:
    python main_mobile.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pola pemanggilan komponen IDENTIK dengan Desktop (main_desktop.py):

  Desktop                          Mobile
  ─────────────────────────────────────────────────────────────
  Card(title="...")            ↔   Card(title="...")
  Button("text", variant=...)  ↔   Button("text", variant=...)
  Container(padding=16)        ↔   Container(padding=16)
  card.add_body_widget(btn)    ↔   card.add_body_widget(btn)
  layout.add_widget(card)      ↔   layout.add_widget(card)
  window = QMainWindow()       ↔   window = MobileApp()      ← satu-satunya beda
  window.setCentralWidget(l)   ↔   window.setCentralWidget(l)
  window.show()                ↔   window.show()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
from PySide6.QtWidgets import QApplication

# ── MobileApp wrapper (satu-satunya perbedaan dengan Desktop) ─────────────────
from pixel_refine_mobile.core import MobileApp

# ── Komponen Generic UI — import IDENTIK dengan Desktop ──────────────────────
from resources.GenericUILibrary.containers import Container
from resources.GenericUILibrary.cards      import Card
from resources.GenericUILibrary.buttons    import Button


def main():
    app = QApplication(sys.argv)

    # ── 1. Compose UI — IDENTIK dengan cara Desktop ───────────────────────────

    layout = Container(padding=16)

    # Card: Denoising Process
    card_denoise = Card(title="Denoising Process")
    btn_denoise  = Button("Start Denoising", variant="primary")
    card_denoise.add_body_widget(btn_denoise)

    # Card: HDR Stack Process
    card_hdr = Card(title="HDR Stack Process")
    btn_hdr  = Button("Start HDR Stack", variant="success")
    card_hdr.add_body_widget(btn_hdr)

    # Susun layout
    layout.add_widget(card_denoise)
    layout.add_widget(card_hdr)

    # ── 2. Launch window — satu-satunya perbedaan: MobileApp vs QMainWindow ───

    window = MobileApp()
    window.setWindowTitle("Pixel Refine Mobile (Dynamic UI)")
    window.setCentralWidget(layout)       # identik dengan Desktop!

    # (Opsional) Connect signal tool_requested — identik dengan Desktop clicked.connect()
    window.bridge.tool_requested.connect(lambda name: print(f"[Mobile] Tool dipilih: {name}"))

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
