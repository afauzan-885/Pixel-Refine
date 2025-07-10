from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.settings.General.Language import language_config
from .General.GeneralSetting import general_page
from .Perfomance.PerformancePage import performance_page
from .Advance.AdvancePage import advance_page

class SettingPage(QWidget):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # Add Tabs
        self.tab_widget.addTab(general_page(), language_config.SETTING_GENERAL_LABEL)
        # self.tab_widget.addTab(performance_page(), "Performance")
        # self.tab_widget.addTab(advance_page(), "Advanced")

        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)
