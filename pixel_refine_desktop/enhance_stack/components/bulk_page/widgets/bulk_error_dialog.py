from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                             QDialogButtonBox, QLabel, QStyle, QHBoxLayout)

class BulkErrorDialog(QDialog):
    """
    Custom dialog for displaying long error messages in a scrollable text area.
    """
    def __init__(self, title, intro_text, detailed_text, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        
        icon_label = QLabel()
        warning_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        icon_label.setPixmap(warning_icon.pixmap(30, 30))
        top_layout.addWidget(icon_label)

        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        top_layout.addWidget(intro_label, 1)
        
        main_layout.addLayout(top_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(detailed_text)
        self.text_edit.setReadOnly(True)
        
        self.text_edit.setMinimumHeight(150)
        self.text_edit.setMinimumWidth(450)
        
        main_layout.addWidget(self.text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)
