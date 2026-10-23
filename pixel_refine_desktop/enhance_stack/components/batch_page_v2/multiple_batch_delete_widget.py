from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Signal, Qt
from UILibrary import Button, ModalDialog


class MultipleBatchDeleteWidget(QWidget):
    """
    Widget to confirm deletion of multiple batches.
    Emits signals for yes/no actions.
    """

    yes_clicked = Signal()
    no_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_batch_names = []
        
        # Enable stylesheet background styling on custom QWidget
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setObjectName("MultipleBatchDeleteWidget")
        self.setStyleSheet(
            "QWidget#MultipleBatchDeleteWidget { background-color: #FFF3CD; }"
        )
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(25)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setTextFormat(Qt.TextFormat.RichText)
        # Connect linkActivated to show the popup
        self.message_label.linkActivated.connect(self._show_all_batches_popup)
        main_layout.addWidget(self.message_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        # Explicitly calling _apply_custom_colors resolves variant background color issues
        # Added 30% transparency (0.7 alpha) as requested
        self.yes_button = Button(language_config.DELETE_IMAGE_BUTTON, variant="danger")
        self.yes_button._apply_custom_colors(bg_color="rgba(231, 76, 60, 0.7)")
        self.yes_button.clicked.connect(self.yes_clicked)
        button_layout.addWidget(self.yes_button)

        self.no_button = Button(language_config.BTN_NO_CANCEL, variant="secondary")
        self.no_button._apply_custom_colors(bg_color="rgba(149, 165, 166, 0.7)")
        self.no_button.clicked.connect(self.no_clicked)
        button_layout.addWidget(self.no_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def set_batch_info(self, batch_names: list):
        """
        Sets the information about the batches to be deleted.

        Args:
            batch_names: A list of names of the batches selected for deletion.
        """
        self.all_batch_names = batch_names
        count = len(batch_names)
        
        # Display first 10 in two columns
        display_limit = 10
        display_names = batch_names[:display_limit]
        
        # Build HTML table for 2 columns
        rows = []
        num_items = len(display_names)
        half = (num_items + 1) // 2
        
        for i in range(half):
            col1 = f"- {display_names[i]}"
            col2 = f"- {display_names[i + half]}" if (i + half) < num_items else ""
            rows.append(f"<tr><td style='padding-right: 40px; font-size: 13px; color: #475569;'>{col1}</td><td style='font-size: 13px; color: #475569;'>{col2}</td></tr>")
            
        table_html = f"<table style='margin: 0 auto; border-collapse: collapse;'>{''.join(rows)}</table>"
        
        if count > display_limit:
            table_html += "<br><a href='show_all' style='color: #2563eb; text-decoration: none; font-size: 13px;'><b>(.....)</b></a>"

        # Title/header for selected batches
        header_text = f"{language_config.UI_BATCH_HEADER} [{count}]"
        # Question for delete
        question_text = language_config.MSG_CONFIRM_DELETE_BATCH_COUNT.format(count)
        
        message = (
            f"<div style='text-align: center; font-family: \"Segoe UI\", Arial, sans-serif;'>"
            f"  <h3 style='font-size: 18px; font-weight: 600; color: #1e293b; margin: 0 0 15px 0;'>{header_text}</h3>"
            f"  {table_html}"
            f"  <p style='font-size: 13.5px; color: #64748b; margin: 20px 0 0 0;'>{question_text}</p>"
            f"</div>"
        )
        self.message_label.setText(message)

    def _show_all_batches_popup(self, link):
        if link == "show_all" and self.all_batch_names:
            modal = ModalDialog(
                message="",
                parent=self,
                title=language_config.MSG_CONFIRM_TITLE,
                close_on_click_outside=False,
                width=520,
                height=400,
            )
            container_layout = modal.container.layout()

            scroll_area = QScrollArea(modal.container)
            scroll_area.setObjectName("BatchNamesScrollArea")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setStyleSheet(
                "QScrollArea#BatchNamesScrollArea { background: #F1F5F9; "
                "border: 1px solid #E2E8F0; border-radius: 4px; }"
            )
            scroll_area.viewport().setStyleSheet("background-color: #F1F5F9;")

            names_content = QWidget()
            names_content.setObjectName("BatchNamesContent")
            names_content.setStyleSheet(
                "QWidget#BatchNamesContent { background-color: #F1F5F9; }"
            )
            names_layout = QVBoxLayout(names_content)
            names_layout.setContentsMargins(12, 8, 12, 8)
            names_layout.setSpacing(4)
            for name in self.all_batch_names:
                name_label = QLabel(f"- {name}", names_content)
                name_label.setWordWrap(True)
                name_label.setStyleSheet("color: #334155; background: transparent;")
                names_layout.addWidget(name_label)
            names_layout.addStretch(1)
            scroll_area.setWidget(names_content)

            container_layout.addWidget(scroll_area, 1)
            footer = QFrame(modal.container)
            footer_layout = QHBoxLayout(footer)
            footer_layout.setContentsMargins(14, 8, 14, 0)
            footer_layout.addStretch(1)
            close_button = Button("OK", variant="primary")
            close_button.clicked.connect(modal.accept)
            footer_layout.addWidget(close_button)
            container_layout.addWidget(footer)
            modal.exec()
