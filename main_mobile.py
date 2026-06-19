"""
main_mobile.py
--------------
Entry point for Pixel Refine Mobile.

Usage:
    python main_mobile.py

Architecture mirrors desktop — same GenericUI components, same API.
Only difference: MobileApp() instead of QMainWindow().
"""

import sys
from PySide6.QtWidgets import QApplication

from pixel_refine_mobile.core import MobileApp, AppState
from pixel_refine_mobile.ui.screens.home_page import build_home_page
from pixel_refine_mobile.ui.screens.workspace_page import build_workspace_page
from pixel_refine_mobile.ui.screens.settings_page import build_settings_page


def on_tool_selected(tool_name):
    """Handle tool selection from bridge signal."""
    print(f"[Mobile] Tool selected: {tool_name}")


def main():
    app = QApplication(sys.argv)

    window = MobileApp()
    window.setWindowTitle("Pixel Refine Mobile")

    # Setup page router
    state = AppState(window.bridge)
    state.register_page("Home", build_home_page)
    state.register_page("MFDenoiser", build_workspace_page)
    state.register_page("MFResolution", build_workspace_page)
    state.register_page("HDR", build_workspace_page)
    state.register_page("Panorama", build_workspace_page)
    state.register_page("Settings", build_settings_page)

    def navigate(tool_name):
        print(f"[Navigation] Navigating to: {tool_name}")
        state.navigate_to(tool_name)
        if tool_name == "Home":
            page = build_home_page(window.bridge)
        elif tool_name == "Settings":
            page = build_settings_page(window.bridge)
        else:
            page = build_workspace_page(window.bridge)
        window.setCentralWidget(page)
        window.show()

    # Connect navigation
    window.bridge.tool_requested.connect(navigate)
    window.bridge.tool_requested.connect(on_tool_selected)

    # Show home page
    window.setCentralWidget(build_home_page(window.bridge))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
