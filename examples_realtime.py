import sys
import os
import random
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSplitter,
    QGroupBox,
)
from PySide6.QtCore import Qt, QTimer

# Import components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ListGroup,
    GridContainer,
    GridItem,
    Button,
    FormGroup,
    Checkbox,
    RadioGroup,
    ProgressBar,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.store import get_store


def create_demo_app():
    app = QApplication(sys.argv)

    # Store
    store = get_store()

    # Main Window
    window = QWidget()
    window.setWindowTitle("GenericUILibrary - Real-time Full Demo (Phase 2)")
    window.resize(1200, 700)

    main_layout = QVBoxLayout(window)
    main_layout.addWidget(
        QLabel("<h2>GenericUILibrary Phase 2: Reactive Forms & Progress</h2>")
    )

    content_layout = QHBoxLayout()

    # --- Column 1: Collections (Phase 1) ---
    col1 = QVBoxLayout()

    # List
    list_box = QGroupBox("Reactive List")
    list_layout = QVBoxLayout(list_box)
    lg = ListGroup()
    lg.bind_store(store, "projects")
    list_layout.addWidget(lg)
    col1.addWidget(list_box)

    # Grid
    grid_box = QGroupBox("Reactive Grid")
    grid_layout = QVBoxLayout(grid_box)
    grid = GridContainer(columns=2, spacing=10)
    grid.bind_store(store, "images")
    grid_layout.addWidget(grid)
    col1.addWidget(grid_box)

    content_layout.addLayout(col1, 1)

    # --- Column 2: Forms (Phase 2) ---
    col2 = QVBoxLayout()
    form_box = QGroupBox("Reactive Forms (Auto-Sync)")
    form_layout = QVBoxLayout(form_box)

    # Text Input
    input_name = FormGroup("Project Name", auto_sync=True)
    input_name.bind_store(store, "current_project_name")
    form_layout.addWidget(input_name)

    # Checkbox
    cb_enabled = Checkbox("System Enabled", auto_sync=True)
    cb_enabled.bind_store(store, "system_enabled")
    form_layout.addWidget(cb_enabled)

    # Radio Group
    radio_mode = RadioGroup(
        options=["High Speed", "Balanced", "High Quality"], auto_sync=True
    )
    radio_mode.bind_store(store, "processing_mode")
    form_layout.addWidget(QLabel("<b>Processing Mode:</b>"))
    form_layout.addWidget(radio_mode)

    col2.addWidget(form_box)

    # Status Display
    status_box = QGroupBox("Current Store Values")
    status_layout = QVBoxLayout(status_box)
    status_label = QLabel("Waiting for data...")
    status_label.setWordWrap(True)
    status_layout.addWidget(status_label)
    col2.addWidget(status_box)

    def update_status_label():
        data = {
            "name": store.get("current_project_name"),
            "enabled": store.get("system_enabled"),
            "mode": store.get("processing_mode"),
        }
        status_label.setText(
            f"Name: {data['name']}\nEnabled: {data['enabled']}\nMode Index: {data['mode']}"
        )

    store.changed.connect(update_status_label)

    content_layout.addLayout(col2, 1)

    # --- Column 3: Progress & Controls ---
    col3 = QVBoxLayout()

    progress_box = QGroupBox("Reactive Progress")
    p_layout = QVBoxLayout(progress_box)

    pb = ProgressBar(style="animated", variant="info")
    pb.bind_store(store, "global_progress")
    p_layout.addWidget(QLabel("Background Task:"))
    p_layout.addWidget(pb)

    col3.addWidget(progress_box)

    # Controls
    ctrl_box = QGroupBox("External Controllers")
    ctrl_layout = QVBoxLayout(ctrl_box)

    btn_random_data = Button("Randomize All", variant="primary")

    def randomize():
        store.set("current_project_name", f"Pro-{random.randint(10,99)}")
        store.set("system_enabled", random.choice([True, False]))
        store.set("processing_mode", random.randint(0, 2))
        store.set("projects", [{"text": f"P-{i}", "value": i} for i in range(3)])
        store.set("images", [{"id": i, "label": f"Img {i}"} for i in range(2)])

    btn_random_data.clicked.connect(randomize)
    ctrl_layout.addWidget(btn_random_data)

    # Simulate background task
    prog_val = 0

    def simulate_progress():
        nonlocal prog_val
        prog_val = (prog_val + 5) % 105
        store.set("global_progress", prog_val)

    timer = QTimer(window)
    timer.timeout.connect(simulate_progress)

    btn_task = Button("Start/Stop Simulation", variant="success")
    btn_task.clicked.connect(
        lambda: timer.stop() if timer.isActive() else timer.start(500)
    )
    ctrl_layout.addWidget(btn_task)

    col3.addWidget(ctrl_box)
    col3.addStretch()

    content_layout.addLayout(col3, 1)

    main_layout.addLayout(content_layout)

    # Initial Data
    store.update_bulk(
        {
            "current_project_name": "New Pixel Project",
            "system_enabled": True,
            "processing_mode": 1,
            "global_progress": 0,
            "projects": [{"text": "Sample A", "value": 1}],
            "images": [{"id": "1", "label": "Initial Image"}],
        }
    )

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    create_demo_app()
