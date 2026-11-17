# GenericUILibrary - Bootstrap-like UI Components for PySide6

A comprehensive library of reusable UI components inspired by Bootstrap 5, designed specifically for PySide6 applications.

## Features

- **Bootstrap-inspired**: Familiar naming conventions and component structure
- **Highly Customizable**: Extensive parameters and styling options
- **Signal-based**: All components use Qt signals for clean event handling
- **Stylesheet Compatible**: Works seamlessly with existing QSS stylesheets
- **Comprehensive**: 40+ components covering all common UI needs
- **Store-bound**: `RealtimeMixin`/`SyncMixin` expose a 3-API data binding surface (`bind`, `sync`, `on_sync`)

## Installation

The library is already included in your project at:
```
resources/GenericUILibrary/
```

## Quick Start

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from resources.GenericUILibrary import Button, Card, Container
from resources.styles.stylesheet import stylesheet_global_page

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

### 11. Store & Bindings (`store.py`, `mixins.py`)
- `DataStore` - JSON-backed store (dotted keys, bulk update, transaction, file watcher)
- `RealtimeMixin` - Binding store untuk satu key / broadcast
- `SyncMixin` - Binding store untuk panel yang mengikuti satu scope
- `AdaptiveSizingMixin` - Helper ukuran/font adaptif

Lihat bagian **Store Binding API** di bawah untuk tiga API utamanya.

## Usage Examples

### Button Variants
```python
from resources.GenericUILibrary import Button

btn_primary = Button("Save", variant="primary")
btn_danger = Button("Delete", variant="danger")
btn_success = Button("Add", variant="success")
btn_info = Button("Import", variant="info")
```

### Form with Validation
```python
from resources.GenericUILibrary import FormGroup, Button, Card

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
from resources.GenericUILibrary import ListGroup

list_group = ListGroup(title="Projects", selection_mode="single", show_actions=True)
list_group.add_item("proj_1", "Project Alpha")
list_group.add_item("proj_2", "Project Beta")

list_group.item_selected.connect(lambda id, label: print(f"Selected: {label}"))
```

### Modal Dialog
```python
from resources.GenericUILibrary import Modal, Button

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
from resources.GenericUILibrary import Gallery

gallery = Gallery(title="Images", columns=5)
gallery.add_item("img1", "Photo 1.jpg")
gallery.add_item("img2", "Photo 2.jpg")
gallery.add_item("img3", "Photo 3.jpg")

gallery.item_clicked.connect(lambda id, label: print(f"Clicked: {label}"))
```

### Tabs
```python
from resources.GenericUILibrary import TabContainer, TabPane

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

## Store Binding API (`RealtimeMixin` / `SyncMixin`)

`mixins.py` menyediakan **tiga API utama** untuk menghubungkan widget/panel ke `DataStore`.
Kebutuhan khusus memakai keyword lanjutan, bukan method tambahan.

### 1. `bind(store, *, key=None, scope=None, bindings=None, fallback=None, apply=True, follow=True)`

- `key="language"` → mode **single-key** (widget form/settings).
- `scope="625"` → mode **panel berscope** (mis. id batch/project).
- `bindings={...}` → `{rel_key: widget | (widget, prop) | (widget, prop, fallback)}`.
  Boleh dipanggil ulang untuk menambah binding setelah widget lain dibangun.
- `fallback` → nilai default untuk binding yang tidak menyebut fallback sendiri.
- `apply=False` → tunda sinkronisasi awal; `follow=False` → tidak berlangganan `store.changed`.
- `key` dan `scope` saling eksklusif; `bindings` tidak boleh digabung dengan `key`.

### 2. `sync(*, scope=None, key=None, keys=None, values=None, notify=True, persist=False, peek=False)`

Satu method untuk tarik, pindah konteks, tulis, dan baca tanpa menerapkan:

- `sync()` → terapkan ulang konteks aktif.
- `sync(scope="625")` → pindah scope lalu terapkan.
- `sync(values={...})` → tulis relatif terhadap scope, lalu terapkan (nilai `None` dilewati).
- `sync(values={...}, notify=False)` → tulis tanpa memancarkan `changed`.
- `sync(values={...}, persist=True)` → tulis lalu `save_to_file()` sinkron.
- `sync(peek=True)` → kembalikan payload **tanpa** menyentuh widget.
- Return: mapping scope, skalar (mode single-key), atau `None`.
- Kombinasi ilegal (`values`+`peek`, `values`+`keys`, `scope`+`key`, `notify=False`/`persist=True`
  tanpa `values`) memunculkan `ValueError`.

### 3. `on_sync(payload, *, key=None, origin=None)`

Satu-satunya hook reaktif; dipanggil **setelah** binding diterapkan oleh `sync`.

- `payload` → snapshot mapping scope, `{bound_key: value}` (single-key), atau `None`
  (invalidasi global). Ini salinan, bukan referensi hidup `DataStore._data`.
- `key` → key relatif yang memicu, atau `None` untuk update scope-wide/bulk.
- `origin` → `"store"` atau `"self"` (komponen ini sendiri yang menulis).
  Pakai `origin="self"` untuk melewati pekerjaan yang tidak perlu saat menulis sendiri.

### Contoh: widget single-key

```python
from resources.GenericUILibrary import Checkbox

cb = Checkbox("Buat thumbnail", auto_sync=True)
cb.bind(store, key="create_thumbnail")   # nilai awal langsung diterapkan

# Widget sudah mengimplementasikan on_sync; tidak perlu override bila memakai Checkbox/FormGroup.
```

### Contoh: panel berscope

```python
from resources.GenericUILibrary.mixins import SyncMixin

class AlgorithmPanel(QWidget, SyncMixin):
    def _build(self):
        self._specs = {
            "alignment_algo": (self.align_form, "value", "No Alignment"),
            "denoising_algo": (self.denoise_card, "value", "No Denoising"),
        }

    def attach(self, store):
        self.bind(store, bindings=self._specs)
        self.sync(scope="625")                 # ikuti batch 625

    def on_sync(self, payload, *, key=None, origin=None):
        if origin == "self" or not payload:
            return
        self._refresh_derived_controls(payload)
```

### Migrasi dari API lama

| Lama | Baru |
|---|---|
| `bind_store(store)` | `bind(store)` |
| `bind_store(store, key)` | `bind(store, key=...)` |
| `add_binding(k, w, prop, fallback)` | `bind(bindings={k: (w, prop, fallback)})` |
| `set_scope(prefix)` | `sync(scope=...)` |
| `sync_from_store()` | `sync()` |
| `get_data(key)` | `sync(peek=True, key=...)` |
| `set_data(v, key, notify)` | `sync(values={key: v}, notify=...)` |
| `signal_blocker()` | `sync(values={...}, notify=False)` |
| `on_store_changed(k, v)` | `on_sync(payload, key=..., origin=...)` |

Nama lama **sudah dihapus**; tidak ada alias. Kontrak signature dijaga oleh
`tests/golden_signatures.json` + `tests/test_api_signature_parity.py`, dan perilaku
API ini diuji di `tests/test_sync_mixin.py`.

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
python resources/GenericUILibrary/examples.py
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
