from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton

def performance_page():
    performance_tab = QWidget()
    layout = QVBoxLayout()

    # CPU/GPU Allocation
    cpu_checkbox = QCheckBox("Enable Multi-threading")
    gpu_checkbox = QCheckBox("Use GPU Acceleration")
    layout.addWidget(cpu_checkbox)
    layout.addWidget(gpu_checkbox)

    # Cache Clear
    clear_cache_button = QPushButton("Clear Cache")
    layout.addWidget(clear_cache_button)

    performance_tab.setLayout(layout)
    return performance_tab
