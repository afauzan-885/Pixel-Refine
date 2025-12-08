"""
GenericUILibrary - Bootstrap-like UI Components for PySide6

A comprehensive library of reusable UI components inspired by Bootstrap 5,
designed for PySide6 applications.

Auto-Styling:
    The library automatically applies stylesheet_global_page() to the QApplication
    when any component is imported, ensuring consistent styling without manual setup.

Usage:
    from GenericUILibrary import Button, Card, Container, ListGroup

    # Stylesheet is automatically applied!
    btn = Button("Click Me", variant="primary")
    card = Card(title="My Card")
    container = Container()

    # Use with signals
    btn.clicked.connect(on_click)
"""

__version__ = "1.0.0"
__author__ = "Pixel Refine Team"

# Auto-apply stylesheet system
import sys
from PySide6.QtWidgets import QApplication

_stylesheet_applied = False


def apply_stylesheet():
    """
    Apply stylesheet_global_page() to QApplication.
    Call this after creating QApplication for auto-styling.

    Usage:
        app = QApplication(sys.argv)
        from GenericUILibrary import apply_stylesheet
        apply_stylesheet()  # Auto-apply stylesheet
    """
    global _stylesheet_applied

    if _stylesheet_applied:
        return

    try:
        app = QApplication.instance()
        if app is not None:
            from pixel_refine_desktop.ui.resources.styles.stylesheet import (
                stylesheet_global_page,
            )

            app.setStyleSheet(stylesheet_global_page())
            _stylesheet_applied = True
            print("✅ GenericUILibrary: stylesheet_global_page() applied")
        else:
            print("⚠️ GenericUILibrary: QApplication not found")
    except Exception as e:
        print(f"⚠️ GenericUILibrary: Could not apply stylesheet - {e}")


# Import all components for easy access

# Buttons
from .buttons import Button, IconButton, ButtonGroup, ToggleButton

# Forms
from .forms import FormGroup, Input, Select, Checkbox, Radio, RadioGroup, FormRow

# Containers and Layouts
from .containers import Container, Row, Col, Stack, ScrollContainer, GridLayout, Spacer

# Cards
from .cards import Card, CardHeader, CardBody, CardFooter, CardGroup

# List Groups
# from .list_group import ListGroup, ListGroupItem, SimpleList  # TODO: Create list_group.py

# Modals and Overlays
from .modals import (
    Modal,
    ModalHeader,
    ModalBody,
    ModalFooter,
    Overlay,
    Toast,
    LoadingSpinner,
)

# Grids and Galleries
from .grids import GridContainer, GridItem, Gallery, ThumbnailGrid

# Tabs
from .tabs import TabContainer, TabPane, SimpleTabs

# Collapse and Accordion
from .collapse import Collapse, Accordion, AccordionItem

# Navigation
from .navbar import Navbar, NavItem, Sidebar, SidebarItem

# Progress Bars
from .progress_bars import (
    ProgressBar,
    CustomProgressBar,
    CircularProgressFallback,
    IndeterminateProgress,
    ProgressGroup,
)

# Define what's available when using "from GenericUILibrary import *"
__all__ = [
    # Utility
    "apply_stylesheet",
    # Buttons
    "Button",
    "IconButton",
    "ButtonGroup",
    "ToggleButton",
    # Forms
    "FormGroup",
    "Input",
    "Select",
    "Checkbox",
    "Radio",
    "RadioGroup",
    "FormRow",
    # Containers
    "Container",
    "Row",
    "Col",
    "Stack",
    "ScrollContainer",
    "GridLayout",
    "Spacer",
    # Cards
    "Card",
    "CardHeader",
    "CardBody",
    "CardFooter",
    "CardGroup",
    # List Groups
    # "ListGroup",  # TODO: Uncomment when list_group.py is created
    # "ListGroupItem",
    # "SimpleList",
    # Modals
    "Modal",
    "ModalHeader",
    "ModalBody",
    "ModalFooter",
    "Overlay",
    "Toast",
    "LoadingSpinner",
    # Grids
    "GridContainer",
    "GridItem",
    "Gallery",
    "ThumbnailGrid",
    # Tabs
    "TabContainer",
    "TabPane",
    "SimpleTabs",
    # Collapse
    "Collapse",
    "Accordion",
    "AccordionItem",
    # Navigation
    "Navbar",
    "NavItem",
    "Sidebar",
    "SidebarItem",
    # Progress Bars
    "ProgressBar",
    "CustomProgressBar",
    "CircularProgressFallback",
    "IndeterminateProgress",
    "ProgressGroup",
]
