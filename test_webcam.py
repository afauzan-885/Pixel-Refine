"""
test_webcam.py - Camera Preview with Parallel Capture + Denoise
===============================================================
Runnable script untuk testing camera preview dengan parallel capture dan denoise.

Usage:
    python test_webcam.py
"""

import sys
import os
import numpy as np
from collections import deque

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QWidget, QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

from taichi_library.taichi_algorithm.camera_api2 import (
    OpenCVSource,
    SyntheticSource,
)
from taichi_library.taichi_algorithm.camera_api2.parallel_capture_denoise import (
    ParallelCaptureDenoise,
)


class SimplePreviewWidget(QLabel):
    """Simple preview widget that displays frames directly."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setText("Camera Preview")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #666666;
                font-size: 14px;
                border: 1px solid #333333;
            }
        """)

    def update_frame(self, frame_uint8):
        """Update display dengan frame baru."""
        if frame_uint8 is None:
            return

        h, w, ch = frame_uint8.shape
        bytes_per_line = ch * w

        q_image = QImage(
            frame_uint8.copy().data,
            w, h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(q_image)
        scaled = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(scaled)


def main():
    """Main entry point."""
    # Create app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Main window
    window = QWidget()
    window.setWindowTitle("Camera Preview - Parallel Capture + Denoise")
    window.setMinimumSize(720, 650)
    window.setStyleSheet("QWidget { background-color: #f5f5f5; }")

    layout = QVBoxLayout(window)
    layout.setSpacing(12)
    layout.setContentsMargins(16, 16, 16, 16)

    # Title
    title = QLabel("Camera Preview with Parallel Capture + Denoise")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    # Preview widget
    preview_widget = SimplePreviewWidget()
    layout.addWidget(preview_widget)

    # Controls row 1: Source
    controls1_layout = QHBoxLayout()

    source_combo = QComboBox()
    source_combo.addItems(["Synthetic (Gradient)", "Synthetic (Bars)", "Synthetic (Checkerboard)", "Webcam"])
    source_combo.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 4px;")
    controls1_layout.addWidget(QLabel("Source:"))
    controls1_layout.addWidget(source_combo)

    controls1_layout.addStretch()

    status_label = QLabel("Ready")
    status_label.setStyleSheet("color: #666; font-size: 12px;")
    controls1_layout.addWidget(status_label)

    layout.addLayout(controls1_layout)

    # Controls row 2: Denoising
    controls2_layout = QHBoxLayout()

    chk_denoise = QCheckBox("Parallel Denoise")
    chk_denoise.setChecked(True)
    chk_denoise.setStyleSheet("font-weight: bold;")
    controls2_layout.addWidget(chk_denoise)

    controls2_layout.addWidget(QLabel("Buffer:"))
    spin_buffer = QSpinBox()
    spin_buffer.setRange(2, 16)
    spin_buffer.setValue(4)
    spin_buffer.setStyleSheet("padding: 4px; border: 1px solid #ccc; border-radius: 4px;")
    controls2_layout.addWidget(spin_buffer)
    controls2_layout.addWidget(QLabel("frames"))

    controls2_layout.addStretch()

    info_label = QLabel("Denoise: 2.0x | Motion Detect: ON")
    info_label.setStyleSheet("color: #27AE60; font-size: 11px;")
    controls2_layout.addWidget(info_label)

    layout.addLayout(controls2_layout)

    # Buttons
    btn_layout = QHBoxLayout()

    btn_start = QPushButton("Start Preview")
    btn_start.setStyleSheet("""
        QPushButton {
            background-color: #2ECC71;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover { background-color: #27AE60; }
    """)
    btn_layout.addWidget(btn_start)

    layout.addLayout(btn_layout)

    # State
    current_source = SyntheticSource(width=640, height=480, pattern="gradient")
    is_running = False
    frame_count = 0

    # Parallel processor
    processor = ParallelCaptureDenoise(
        source=current_source,
        buffer_size=30,
        denoise_buffer=4,
        use_motion_detection=True
    )

    # Timer for polling
    timer = QTimer()
    timer.timeout.connect(lambda: update_frame())

    def update_frame():
        nonlocal frame_count
        if not is_running:
            return

        # Get denoised frame dari parallel processor
        frame = processor.get_denoised_frame()

        if frame is not None:
            preview_widget.update_frame(frame)
            frame_count += 1

            # Update status
            fps_text = f"FPS: {processor.fps:.0f} | Frames: {frame_count}"
            if chk_denoise.isChecked():
                stats = processor.get_stats()
                fps_text += f" | Denoised: {stats.get('denoise_count', 0)}"
            status_label.setText(fps_text)

    def on_source_changed(index):
        nonlocal current_source, is_running

        if is_running:
            timer.stop()
            processor.stop()
            is_running = False
            btn_start.setText("Start Preview")

        if index == 0:
            current_source = SyntheticSource(width=640, height=480, pattern="gradient")
        elif index == 1:
            current_source = SyntheticSource(width=640, height=480, pattern="bars")
        elif index == 2:
            current_source = SyntheticSource(width=640, height=480, pattern="checkerboard")
        elif index == 3:
            try:
                current_source = OpenCVSource(camera_id=0)
            except Exception as e:
                status_label.setText(f"Error: {e}")
                source_combo.setCurrentIndex(0)
                current_source = SyntheticSource(width=640, height=480, pattern="gradient")

        # Update processor source
        processor.source = current_source
        processor.clear()
        status_label.setText(f"Source: {source_combo.currentText()}")

    source_combo.currentIndexChanged.connect(on_source_changed)

    def on_buffer_changed(value):
        processor.set_denoise_buffer_size(value)
        noise_factor = np.sqrt(value)
        motion_text = "ON" if processor.denoiser.use_motion_detection else "OFF"
        info_label.setText(f"Denoise: {noise_factor:.1f}x | Motion Detect: {motion_text}")

    spin_buffer.valueChanged.connect(on_buffer_changed)

    def on_denoise_toggled(checked):
        processor.set_motion_detection(checked)
        if not checked:
            processor.denoiser.clear()
        motion_text = "ON" if checked else "OFF"
        noise_factor = np.sqrt(spin_buffer.value())
        info_label.setText(f"Denoise: {noise_factor:.1f}x | Motion Detect: {motion_text}")

    chk_denoise.toggled.connect(on_denoise_toggled)

    def toggle_preview():
        nonlocal is_running, frame_count

        if is_running:
            timer.stop()
            processor.stop()
            is_running = False
            btn_start.setText("Start Preview")
            status_label.setText("Stopped")
        else:
            is_running = True
            frame_count = 0
            processor.clear()
            processor.start()
            timer.start(33)  # ~30 FPS
            btn_start.setText("Stop Preview")
            status_label.setText(f"Running - {source_combo.currentText()}")

    btn_start.clicked.connect(toggle_preview)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
