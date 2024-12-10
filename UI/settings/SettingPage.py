from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .General.GeneralPage import general_page
from .Perfomance.PerformancePage import performance_page
from .Advance.AdvancePage import advance_page

class SettingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # Add Tabs
        self.tab_widget.addTab(general_page(), "General")
        self.tab_widget.addTab(performance_page(), "Performance")
        self.tab_widget.addTab(advance_page(), "Advanced")

        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)
