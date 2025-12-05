"""
Settings View (MVC).
Inherits from legacy SettingPage to maintain all functionality.
"""

from UI.settings.SettingPage import SettingPage


class SettingsView(SettingPage):
    """
    Settings view with MVC architecture.
    Inherits from legacy SettingPage - simple wrapper for consistency.
    """

    def __init__(self, db_path: str, parent=None):
        # Create database manager
        from UI.enhance_stack.logic.database_manager import DatabaseManager

        database_manager = DatabaseManager(db_path)

        # Initialize parent (legacy SettingPage)
        super().__init__(database_manager)

        # Store db_path for future use
        self.db_path = db_path

        # Future: Add settings controllers here if needed
        # For now, settings are mostly UI-only (language, theme, etc.)
