from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QScrollArea, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal

from UI.resources.GenericUILibrary.ui_component import GridItemWidget, LoadingOverlay

class ViewerPanel(QWidget):
    import_clicked = Signal()
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Frame Container Utama ---
        # Ini agar background/border area display sesuai style
        self.container_frame = QFrame()
        self.container_frame.setObjectName("displayContainer") # <--- ID PENTING
        
        container_layout = QVBoxLayout(self.container_frame)

        # --- Header ---
        header_layout = QHBoxLayout()
        
        self.lbl_title = QLabel("No Selection")
        self.lbl_title.setObjectName("sectionTitle") # <--- ID PENTING (Judul besar)
        
        self.btn_back = QPushButton("Back")
        self.btn_back.setVisible(False)
        
        self.btn_import = QPushButton("Import Images")
        self.btn_import.setObjectName("importButton") # <--- ID PENTING (Tombol Import)
        self.btn_import.setVisible(False)
        
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_back)
        header_layout.addWidget(self.btn_import)
        
        container_layout.addLayout(header_layout)

        # --- Stack Container ---
        self.stack = QStackedWidget()
        container_layout.addWidget(self.stack)

        # 1. Grid Page
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setObjectName("scrollArea") # <--- ID PENTING (Background scroll)
        self.grid_scroll.setWidgetResizable(True)
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_scroll.setWidget(self.grid_container)
        self.stack.addWidget(self.grid_scroll)

        # 2. Loading Page
        self.loading_view = LoadingOverlay()
        self.stack.addWidget(self.loading_view)

        main_layout.addWidget(self.container_frame)

        # Signals
        self.btn_import.clicked.connect(self.import_clicked.emit)
        self.btn_back.clicked.connect(self.back_clicked.emit)

    # ... (Method set_view_title, dll sama seperti sebelumnya) ...
    def set_view_title(self, title):
        self.lbl_title.setText(title)
        self.btn_import.setVisible(True)
        self.show_grid()

    def show_empty_state(self):
        self.lbl_title.setText("Select or Create Project")
        self.btn_import.setVisible(False)
        self._clear_grid()
        self.show_grid()

    def show_grid(self):
        self.stack.setCurrentWidget(self.grid_scroll)
        self.btn_back.setVisible(False)

    def show_loading(self, message="Processing..."):
        self.loading_view.set_status(message)
        self.stack.setCurrentWidget(self.loading_view)
        self.btn_back.setVisible(True)

    def add_grid_item(self, item_id, label):
        widget = GridItemWidget(item_id, label)
        count = self.grid_layout.count()
        row, col = divmod(count, 5) 
        self.grid_layout.addWidget(widget, row, col)

    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def to_qml(self, indent=0):
        tab = "    " * indent
        title = self.lbl_title.text().replace("'", "\\'")
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    Rectangle {{\n"
        qml += f"{tab}        width: parent.width\n"
        qml += f"{tab}        height: 400\n"
        qml += f"{tab}        color: genericTheme.bgPrimary\n"
        qml += f"{tab}        radius: genericTheme.radiusLg\n"
        qml += f"{tab}        border.color: genericTheme.borderColor\n"
        qml += f"{tab}        border.width: 1\n"
        qml += f"{tab}        Column {{\n"
        qml += f"{tab}            anchors.fill: parent\n"
        qml += f"{tab}            anchors.margins: 10\n"
        qml += f"{tab}            Row {{\n"
        qml += f"{tab}                width: parent.width\n"
        qml += f"{tab}                Text {{ text: '{title}'; font.bold: true; font.pixelSize: 16; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}                Item {{ Layout.fillWidth: true }}\n"
        qml += f"{tab}                Rectangle {{ width: 100; height: 30; radius: genericTheme.radiusSm; color: genericTheme.info; Text {{ text: 'Import Images'; color: 'white'; anchors.centerIn: parent; font.pixelSize: 10 }} MouseArea {{ anchors.fill: parent; onClicked: appBridge.openTool('Import Images') }} }}\n"
        qml += f"{tab}            }}\n"
        qml += f"{tab}            Grid {{ columns: 5; spacing: 10; width: parent.width }}\n"
        qml += f"{tab}        }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml