# GenericUILibrary - Bootstrap-like UI Components for PySide6

A comprehensive library of reusable UI components inspired by Bootstrap 5, designed specifically for PySide6 applications.

## Features

- **Bootstrap-inspired**: Familiar naming conventions and component structure
- **Highly Customizable**: Extensive parameters and styling options
- **Signal-based**: All components use Qt signals for clean event handling
- **Stylesheet Compatible**: Works seamlessly with existing QSS stylesheets
- **Comprehensive**: 40+ components covering all common UI needs

## Installation

The library is already included in your project at:
```
pixel_refine_desktop/ui/resources/GenericUILibrary/
```

## Quick Start

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from pixel_refine_desktop.ui.resources.GenericUILibrary import Button, Card, Container
from pixel_refine_desktop.ui.resources.styles.stylesheet import stylesheet_global_page

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Apply global stylesheet
        self.setStyleSheet(stylesheet_global_page())
        
        # Create container
        container = Container(padding=15)
        
        # Create card
        card = Card(title="Welcome")
        card.set_body_content("Hello, World!")
        
        # Add button
        btn = Button("Click Me", variant="primary")
        btn.clicked.connect(self.on_click)
        card.add_footer_widget(btn)
        
        container.add_widget(card)
        self.setCentralWidget(container)
    
    def on_click(self):
        print("Button clicked!")

app = QApplication([])
window = MyApp()
window.show()
app.exec()
```

## Component Categories

### 1. Buttons (`buttons.py`)
- `Button` - Standard button with variants (primary, secondary, success, danger, info)
- `IconButton` - Button with icon support
- `ButtonGroup` - Group of buttons
- `ToggleButton` - Toggle/switch button

### 2. Forms (`forms.py`)
- `FormGroup` - Label + input wrapper
- `Input` - Text input with validation states
- `Select` - Dropdown/combobox
- `Checkbox` - Checkbox with label
- `Radio` - Radio button with label
- `RadioGroup` - Group of radio buttons
- `FormRow` - Horizontal form layout

### 3. Containers (`containers.py`)
- `Container` - Main container with padding
- `Row` - Horizontal layout
- `Col` - Column layout
- `Stack` - Vertical/horizontal stack
- `ScrollContainer` - Scrollable container
- `GridLayout` - Grid layout
- `Spacer` - Spacing widget

### 4. Cards (`cards.py`)
- `Card` - Container with header, body, footer
- `CardHeader` - Card header component
- `CardBody` - Card body component
- `CardFooter` - Card footer component
- `CardGroup` - Group of cards

### 5. List Groups (`list_group.py`)
- `ListGroup` - Selectable list with actions
- `ListGroupItem` - Custom list item
- `SimpleList` - Simple list widget

### 6. Modals (`modals.py`)
- `Modal` - Dialog/popup window
- `ModalHeader` - Modal header
- `ModalBody` - Modal content
- `ModalFooter` - Modal footer
- `Overlay` - Loading overlay
- `Toast` - Notification toast
- `LoadingSpinner` - Loading indicator

### 7. Grids (`grids.py`)
- `GridContainer` - Scrollable grid
- `GridItem` - Individual grid item
- `Gallery` - Image gallery
- `ThumbnailGrid` - Thumbnail grid

### 8. Tabs (`tabs.py`)
- `TabContainer` - Tab widget
- `TabPane` - Tab content
- `SimpleTabs` - Simple tab implementation

### 9. Collapse (`collapse.py`)
- `Collapse` - Collapsible panel
- `Accordion` - Multiple collapsible panels
- `AccordionItem` - Individual accordion item

### 10. Navigation (`navbar.py`)
- `Navbar` - Top navigation bar
- `NavItem` - Navigation item
- `Sidebar` - Vertical sidebar
- `SidebarItem` - Sidebar item

## Usage Examples

### Button Variants
```python
from GenericUILibrary import Button

btn_primary = Button("Save", variant="primary")
btn_danger = Button("Delete", variant="danger")
btn_success = Button("Add", variant="success")
btn_info = Button("Import", variant="info")
```

### Form with Validation
```python
from GenericUILibrary import FormGroup, Button, Card

card = Card(title="User Registration")

name = FormGroup(label="Name", input_type="text", placeholder="Enter name")
email = FormGroup(label="Email", input_type="text", placeholder="Enter email")
role = FormGroup(label="Role", input_type="select")
role.add_options(["Admin", "User", "Guest"])

card.add_body_widget(name)
card.add_body_widget(email)
card.add_body_widget(role)

submit = Button("Submit", variant="primary")
card.add_footer_widget(submit)
```

### List with Selection
```python
from GenericUILibrary import ListGroup

list_group = ListGroup(title="Projects", selection_mode="single", show_actions=True)
list_group.add_item("proj_1", "Project Alpha")
list_group.add_item("proj_2", "Project Beta")

list_group.item_selected.connect(lambda id, label: print(f"Selected: {label}"))
```

### Modal Dialog
```python
from GenericUILibrary import Modal, Button

def show_confirmation():
    modal = Modal(title="Confirm Delete", parent=self)
    modal.set_body("Are you sure you want to delete this item?")
    modal.add_footer_button("Cancel", variant="secondary")
    modal.add_footer_button("Delete", variant="danger", callback=on_delete)
    modal.exec()

btn = Button("Delete", variant="danger")
btn.clicked.connect(show_confirmation)
```

### Grid Gallery
```python
from GenericUILibrary import Gallery

gallery = Gallery(title="Images", columns=5)
gallery.add_item("img1", "Photo 1.jpg")
gallery.add_item("img2", "Photo 2.jpg")
gallery.add_item("img3", "Photo 3.jpg")

gallery.item_clicked.connect(lambda id, label: print(f"Clicked: {label}"))
```

### Tabs
```python
from GenericUILibrary import TabContainer, TabPane

tabs = TabContainer()

tab1 = TabPane()
tab1.add_widget(QLabel("General settings content"))
tabs.add_tab("General", tab1)

tab2 = TabPane()
tab2.add_widget(QLabel("Advanced settings content"))
tabs.add_tab("Advanced", tab2)

tabs.tab_changed.connect(lambda idx, title: print(f"Tab: {title}"))
```

## Styling

All components are designed to work with the existing stylesheet system. Components use `setObjectName()` to apply specific styles:

- `processButton` - Primary action buttons (green)
- `addButton` - Add/success buttons (green)
- `deleteButton` - Delete/danger buttons (red)
- `importButton` - Import/info buttons (blue)
- `sectionTitle` - Section titles (bold, larger font)
- `displayContainer` - Main display containers (white background, rounded)
- `projectPanel` - Panel containers (white background, rounded)
- `scrollArea` - Scroll areas (custom scrollbar)

## Component Signals

Most components emit signals for user interactions:

```python
# Button
button.clicked.connect(callback)

# ListGroup
list_group.item_selected.connect(lambda id, label: ...)
list_group.selection_cleared.connect(callback)

# TabContainer
tabs.tab_changed.connect(lambda index, title: ...)

# Modal
modal.accepted.connect(callback)
modal.rejected.connect(callback)

# GridItem
item.clicked.connect(lambda id: ...)
item.double_clicked.connect(lambda id: ...)
```

## Best Practices

1. **Use Variants**: Leverage button variants for consistent styling
2. **Signal-based Logic**: Connect signals instead of subclassing
3. **Compose Components**: Build complex UIs by combining simple components
4. **Apply Stylesheet**: Always apply `stylesheet_global_page()` to your main window
5. **Object Names**: Use object names for custom styling when needed

## Complete Example

See `examples.py` for a complete working example demonstrating all components.

Run the example:
```bash
python pixel_refine_desktop/ui/resources/GenericUILibrary/examples.py
```

## Migration from Old Components

Old components have been replaced:

| Old Component | New Component |
|--------------|---------------|
| `config_panel.py` | Use `Card` + `TabContainer` + `FormGroup` |
| `selector_panel.py` | Use `ListGroup` with `show_actions=True` |
| `viewer_panel.py` | Use `Gallery` or `GridContainer` |
| `workspace_layout.py` | Use `Container` + `Row` + `Col` |
| `ui_component.py` | Use `GridItem`, `LoadingSpinner` |

## License

Part of the Pixel Refine project.
