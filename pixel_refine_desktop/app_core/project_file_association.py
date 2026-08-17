"""Windows registration for Pixel Refine project files (.prf)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_PROG_ID = "PixelRefine"
_LEGACY_PROG_IDS = ("PixelRefine.Project",)


def _launch_command() -> str:
    """Build the command Windows uses when a .prf file is double-clicked."""
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable).resolve()}" "%1"'
    entrypoint = Path(__file__).resolve().parents[2] / "main_desktop.py"
    return f'"{Path(sys.executable).resolve()}" "{entrypoint}" "%1"'


def register_project_file_association() -> bool:
    """Register .prf for the current user without requiring administrator rights."""
    if os.name != "nt":
        return False
    try:
        import winreg

        icon = Path(__file__).resolve().parents[2] / "resources" / "assets" / "images" / "Logo_Pixel_Refine.ico"
        root = winreg.HKEY_CURRENT_USER
        classes = r"Software\Classes"

        def delete_tree(path: str) -> None:
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                    while True:
                        try:
                            child = winreg.EnumKey(key, 0)
                        except OSError:
                            break
                        delete_tree(path + "\\" + child)
                winreg.DeleteKey(root, path)
            except OSError:
                pass

        for legacy_id in _LEGACY_PROG_IDS:
            delete_tree(classes + "\\" + legacy_id)

        with winreg.CreateKey(root, classes + r"\.prf") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PROJECT_PROG_ID)
            winreg.SetValueEx(key, "FriendlyTypeName", 0, winreg.REG_SZ, "Pixel Refine")
        with winreg.CreateKey(root, classes + "\\" + PROJECT_PROG_ID) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Pixel Refine")
            winreg.SetValueEx(key, "FriendlyTypeName", 0, winreg.REG_SZ, "Pixel Refine")
        with winreg.CreateKey(root, classes + "\\" + PROJECT_PROG_ID + r"\DefaultIcon") as key:
            icon_value = str(icon) if icon.is_file() else _launch_command().split('"')[1]
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, icon_value)
        with winreg.CreateKey(root, classes + "\\" + PROJECT_PROG_ID + r"\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, _launch_command())
        try:
            import ctypes

            # Ask Explorer to refresh file icons/associations immediately.
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        except (AttributeError, OSError):
            pass
        return True
    except (OSError, ImportError):
        # Association is optional; a restricted corporate policy must not stop
        # the application from launching.
        return False
