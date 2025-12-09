import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ListGroup,
    ImageCard,
    EmptyState,
    Theme,
)


def test_components():
    app = QApplication(sys.argv)

    # Main window
    window = QWidget()
    window.setWindowTitle("GenericUILibrary - Component Demo")
    window.resize(800, 600)

    main_layout = QHBoxLayout(window)
    main_layout.setSpacing(20)
    main_layout.setContentsMargins(20, 20, 20, 20)

    # === Left Column: ListGroup ===
    left_column = QVBoxLayout()

    list_label = QLabel("ListGroup Component")
    list_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
    left_column.addWidget(list_label)

    lg = ListGroup()
    lg.add_item("Project Alpha", value=1)
    lg.add_item("Project Beta", value=2)
    lg.add_item("Project Gamma", value=3)
    lg.add_item("Project Delta", value=4)
    lg.selection_changed.connect(lambda values: print(f"Selected: {values}"))
    left_column.addWidget(lg)

    main_layout.addLayout(left_column, 1)

    # === Middle Column: ImageCard Grid ===
    middle_column = QVBoxLayout()

    card_label = QLabel("ImageCard Component")
    card_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
    middle_column.addWidget(card_label)

    # Create a grid of image cards
    card_container = QWidget()
    card_grid = QHBoxLayout(card_container)
    card_grid.setSpacing(10)

    # Card 1 - Loading state
    card1 = ImageCard("card1", size=120)
    card1.set_loading(True)
    card1.clicked.connect(lambda id, event: print(f"Clicked: {id}"))
    card_grid.addWidget(card1)

    # Card 2 - Selected with colored background
    card2 = ImageCard("card2", size=120)
    # Create a simple colored pixmap for demo
    pixmap2 = QPixmap(100, 100)
    pixmap2.fill(QColor("#2ECC71"))  # Green
    card2.set_image(pixmap2)
    card2.select()
    card_grid.addWidget(card2)

    # Card 3 - Normal with colored background
    card3 = ImageCard("card3", size=120)
    pixmap3 = QPixmap(100, 100)
    pixmap3.fill(QColor("#3498DB"))  # Blue
    card3.set_image(pixmap3)
    card_grid.addWidget(card3)

    middle_column.addWidget(card_container)
    middle_column.addStretch()

    main_layout.addLayout(middle_column, 1)

    # === Right Column: EmptyState ===
    right_column = QVBoxLayout()

    empty_label = QLabel("EmptyState Component")
    empty_label.setStyleSheet(
        "font-size: 14px; font-weight: bold; margin-bottom: 10px;"
    )
    right_column.addWidget(empty_label)

    empty = EmptyState(
        "No Data Available",
        "Click the button below to add new items.",
        "Add Item",
        on_click=lambda: print("Button clicked!"),
    )
    right_column.addWidget(empty)

    main_layout.addLayout(right_column, 1)

    # Show window
    window.show()
    print("✅ All components displayed successfully!")
    print("💡 Try clicking on ImageCards and ListGroup items")
    print("💡 Try clicking the 'Add Item' button")

    sys.exit(app.exec())


if __name__ == "__main__":
    test_components()
