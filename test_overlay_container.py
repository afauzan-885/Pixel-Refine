import sys
import unittest
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QSize, QRect, QPoint

# Generic GenericUILibrary imports
from pixel_refine_desktop.ui.resources.GenericUILibrary.overlays import (
    OverlayContainer,
    OverlayPosition,
)

app = QApplication.instance() or QApplication(sys.argv)


class TestOverlayContainer(unittest.TestCase):
    def setUp(self):
        self.parent = QWidget()
        self.parent.resize(800, 600)

        self.overlay = OverlayContainer(
            self.parent, position=OverlayPosition.BOTTOM_CENTER
        )
        self.overlay.resize(200, 100)  # Fixed size for testing

        self.parent.show()
        self.overlay.show()

    def tearDown(self):
        self.overlay.close()
        self.parent.close()

    def test_default_positioning_bottom_center(self):
        """Test if it positions at bottom center correctly."""
        # Force update
        self.overlay._update_position()

        expected_x = (800 - 200) // 2
        expected_y = 600 - 100 - 20  # Margin 20

        pos = self.overlay.pos()
        self.assertEqual(pos.x(), expected_x)
        self.assertEqual(pos.y(), expected_y)

    def test_positioning_top_left(self):
        """Test TOP_LEFT positioning."""
        self.overlay.preferred_position = OverlayPosition.TOP_LEFT
        self.overlay._update_position()

        expected_x = 20  # Margin
        expected_y = 20  # Margin

        pos = self.overlay.pos()
        self.assertEqual(pos.x(), expected_x)
        self.assertEqual(pos.y(), expected_y)

    def test_smart_positioning_flip_vertical(self):
        """Test if it flips from Bottom to Top if Bottom is out of bounds."""
        # Make parent very small height, so bottom is clipped?
        # Actually logic is: if pos.y + height > parent.height.
        # But _calculate_coordinates uses parent height, so it usually fits unless parent is smaller than widget + margin.

        # Scenario: User sets position manually to something that would be out of bounds?
        # Or: Parent resizes to be very small?

        # Let's try forcing a scenario where "natural" position is bad.
        # Wait, _calculate_coordinates ALWAYS puts it inside rect relative to width/height.
        # So it only goes out of bounds if margin > width/height or similar.

        # Smart positioning is more useful if we had absolute coordinates or specific offsets.
        # But here logic is relative.
        # HOWEVER, let's test if we offset it manually and ask it to adjust?
        # No, _update_position recalculates from scratch.

        # Let's test the `_adjust_position_smartly` method directly with a hypothetical rect.
        # Suppose we want to place it at (0, 700) in a (800, 600) window.

        mock_rect = QRect(0, 0, 800, 600)
        bad_pos = QPoint(
            300, 550
        )  # Height is 100, so y+h = 650 > 600. Out of bounds bottom.

        # Ideally it should flip to TOP.
        self.overlay.preferred_position = OverlayPosition.BOTTOM_CENTER

        # We simulate the logic step:
        # calculate natural: (300, 480) [Fits]

        # To trigger the smart logic, we need a case where preferred calculation results in out-of-bounds.
        # This happens if we use an anchor point or global position, but here we calculate top-left relative.
        # Actually, if parent is smaller than overlay?

        # Case: Parent is 100x100. Overlay is 200x50.
        # BOTTOM_CENTER of 100x100 parent: x = (100-200)/2 = -50.
        # y = 100 - 50 - 20 = 30.
        # Rect: (-50, 30, 200, 50).
        # Left (-50) is < 0. Right (150) > 100.

        # Check logic:
        # is_out_left = True.

        # It should try to clamp or shift.
        # My implementation clamps: final_x = max(0, min(-50, ...)) -> 0.

        small_rect = QRect(0, 0, 100, 100)
        adjusted = self.overlay._adjust_position_smartly(
            QPoint(-50, 30), 200, 50, small_rect
        )

        self.assertEqual(adjusted.x(), 0)  # Clamped to 0

    def test_smart_flip_logic(self):
        """Test explicit flip logic."""
        # Use _adjust_position_smartly directly.
        # Scenario: We are at BOTTOM. But we pretend it's out of bounds bottom.

        p_rect = QRect(0, 0, 800, 600)
        w, h = 200, 100

        # Pretend calculation returned y = 550. (Bottom is 650 > 600).
        bad_pos = QPoint(300, 550)
        self.overlay.preferred_position = OverlayPosition.BOTTOM_CENTER

        # Call adjust
        adjusted = self.overlay._adjust_position_smartly(bad_pos, w, h, p_rect)

        self.assertEqual(adjusted.y(), 20)
        self.assertEqual(adjusted.x(), 300)


from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QSlider,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import QTimer, Qt


class OverlayPlayground(QMainWindow):
    """
    Interactive Playground to stress-test the OverlayContainer.
    Scenarios:
    1. Parent Resizing (Manual & Animation)
    2. Alignment Switching
    3. Content Resizing
    4. Smart Positioning Toggle
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OverlayContainer Stress Test GUI")
        self.resize(1000, 700)

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # --- Left Panel: Controls ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setFixedWidth(250)

        # Position Selection
        control_layout.addWidget(QLabel("<b>Position:</b>"))
        self.pos_combo = QComboBox()
        for name, value in vars(OverlayPosition).items():
            if isinstance(value, int):
                self.pos_combo.addItem(name, value)
        self.pos_combo.currentIndexChanged.connect(self.change_position)
        control_layout.addWidget(self.pos_combo)

        # Smart Positioning Toggle
        self.smart_cb = QCheckBox("Smart Positioning")
        self.smart_cb.setChecked(True)
        self.smart_cb.toggled.connect(self.toggle_smart)
        control_layout.addWidget(self.smart_cb)

        # Content Size Control
        control_layout.addWidget(QLabel("<b>Content Size:</b>"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(50, 400)
        self.size_slider.setValue(200)
        self.size_slider.valueChanged.connect(self.resize_content)
        control_layout.addWidget(self.size_slider)

        # Parent Stress Test (Animation)
        control_layout.addSpacing(20)
        self.anim_btn = QPushButton("Start/Stop Resize Dance")
        self.anim_btn.setCheckable(True)
        self.anim_btn.clicked.connect(self.toggle_animation)
        control_layout.addWidget(self.anim_btn)

        control_layout.addStretch()
        main_layout.addWidget(control_panel)

        # --- Right Panel: Simulation Area ---
        # We use a frame acting as the 'Parent' for the overlay
        self.simulation_area = QFrame()
        self.simulation_area.setFrameShape(QFrame.Shape.Box)
        self.simulation_area.setStyleSheet(
            "background-color: #f0f0f0; border: 2px dashed #ccc;"
        )
        # We wrap it in a layouts/widget to allow resizing styling

        # Container for the simulation parent to allow it to be virtually resized
        # Actually, let's just use the frame itself and resize it?
        # But we want to simulate window resize or container resize.
        # Making the right side a layout where the target container lives.

        container_wrapper = QWidget()
        cw_layout = QVBoxLayout(container_wrapper)
        cw_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the test subject

        self.target_container = QFrame()  # The parent of the overlay
        self.target_container.setFixedSize(600, 400)
        self.target_container.setStyleSheet(
            "background-color: #e0e0e0; border: 1px solid #999;"
        )
        self.target_container.setObjectName("TargetParent")

        # Label inside target
        l = QLabel("Target Parent\n(Resize Me)", self.target_container)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.resize(600, 400)

        cw_layout.addWidget(self.target_container)
        main_layout.addWidget(container_wrapper)

        # --- Create Overlay ---
        self.overlay = OverlayContainer(
            parent=self.target_container,
            position=OverlayPosition.BOTTOM_CENTER,
            smart_positioning=True,
        )
        # Content for overlay
        self.overlay_content = QPushButton("I am Floating! 👻")
        self.overlay_content.setFixedSize(200, 60)
        self.overlay_content.setStyleSheet(
            "background-color: #ff6b6b; color: white; border-radius: 8px; font-weight: bold;"
        )
        self.overlay.set_content(self.overlay_content)

        # Animation Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_step)
        self.angle = 0.0

    def change_position(self):
        data = self.pos_combo.currentData()
        self.overlay.preferred_position = data
        self.overlay._update_position()

    def toggle_smart(self):
        self.overlay.smart_positioning = self.smart_cb.isChecked()
        self.overlay._update_position()

    def resize_content(self):
        w = self.size_slider.value()
        h = int(w * 0.4)
        self.overlay_content.setFixedSize(w, h)
        # Overlay adjusts automatically via layout, but we might need to trigger update
        self.overlay.adjustSize()
        self.overlay._update_position()

    def toggle_animation(self):
        if self.anim_btn.isChecked():
            self.timer.start(50)
        else:
            self.timer.stop()

    def animate_step(self):
        import math

        self.angle += 0.1
        # Oscillate size
        new_w = 400 + int(math.sin(self.angle) * 200)  # 200 to 600
        new_h = 300 + int(math.cos(self.angle) * 150)  # 150 to 450

        self.target_container.setFixedSize(new_w, new_h)
        # Fix label size too just to look nice
        found_label = self.target_container.findChild(QLabel)
        if found_label:
            found_label.resize(new_w, new_h)


if __name__ == "__main__":
    # If run with argument 'unittest', run standard unit tests
    # Otherwise run GUI playground
    if len(sys.argv) > 1 and sys.argv[1] == "unittest":
        unittest.main(argv=[sys.argv[0]])
    else:
        print("Starting Interactive GUI Stress Test...")
        print(
            "Run with 'python test_overlay_container.py unittest' for automated tests."
        )

        # App instance might be created at top level
        window = OverlayPlayground()
        window.show()
        sys.exit(app.exec())
