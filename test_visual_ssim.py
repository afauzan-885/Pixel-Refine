"""
test_visual_ssim.py
-------------------
Automated visual parity test script.
For each UI component, it renders the PySide6 version (left) and the QML version (right)
side-by-side, captures screenshots of both, computes the SSIM (Structural Similarity Index),
and flags components that have a low similarity score.
"""

import sys
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

import time
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim

from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QFrame
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtGui import QScreen

# Import Generic UI Components
from resources.GenericUILibrary.theme import QmlThemeBridge, get_theme
from resources.GenericUILibrary.buttons import Button, ToggleButton, ToggleSwitch
from resources.GenericUILibrary.cards import Card, FeatureCard
from resources.GenericUILibrary.forms import Input, Select, Checkbox, RadioGroup
from resources.GenericUILibrary.progress_bars import ProgressBar, IndeterminateProgress
from resources.GenericUILibrary.list_group import ListGroup
from resources.GenericUILibrary.tables import DataTable
from resources.GenericUILibrary.containers import Container

# Directory to save diff results
DIFF_DIR = "visual_parity_reports"
os.makedirs(DIFF_DIR, exist_ok=True)

def get_screenshot(widget):
    """Grab widget screenshot and convert to grayscale numpy array."""
    pixmap = widget.grab()
    qimage = pixmap.toImage()
    width = qimage.width()
    height = qimage.height()
    
    # Extract bytes
    ptr = qimage.bits()
    arr = np.array(ptr).reshape(height, width, 4)  # RGBA
    gray = cv2.cvtColor(arr, cv2.COLOR_RGBA2GRAY)
    return gray

def compare_images(img1, img2, component_name):
    """Compare two grayscale images using SSIM and save diff if different."""
    # Resize img2 to match img1 size for comparison
    h, w = img1.shape
    img2_resized = cv2.resize(img2, (w, h))
    
    # Compute SSIM
    score, diff = ssim(img1, img2_resized, full=True)
    
    # Normalize diff to 0-255
    diff = (diff * 255).astype("uint8")
    
    # If score is below threshold, save visual comparison
    if score < 0.95:
        # Create side-by-side visualization
        combined = np.hstack([img1, img2_resized, diff])
        cv2.putText(combined, f"SSIM: {score:.4f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 2, cv2.LINE_AA)
        
        filepath = os.path.join(DIFF_DIR, f"{component_name.lower()}_diff.png")
        cv2.imwrite(filepath, combined)
        print(f"  [DISPARITY DETECTED] Saved comparison image: {filepath}")
        
    return score

def run_single_component_test(widget_creator, component_name):
    """Creates a temporary side-by-side view, renders it, and computes SSIM."""
    # Instantiate PySide6 widget
    pyside_widget = widget_creator()
    
    # Wrap in a Container to get QML
    container = Container(padding=10)
    container.add_widget(pyside_widget)
    body_qml = container.to_qml(indent=2)
    
    # Setup Main Window
    win = QWidget()
    win.setWindowTitle(f"Comparing {component_name}")
    win.resize(800, 400)
    layout = QHBoxLayout(win)
    layout.setContentsMargins(10, 10, 10, 10)
    
    # Left container for PySide6
    left_frame = QFrame()
    theme = get_theme()
    left_frame.setStyleSheet(f"background-color: {theme.bg_secondary}; border: none;")
    left_layout = QVBoxLayout(left_frame)
    left_layout.setContentsMargins(10, 10, 10, 10)
    left_layout.addWidget(pyside_widget)
    left_layout.addStretch()
    layout.addWidget(left_frame, 1)
    
    # Right QQuickWidget for QML
    theme_bridge = QmlThemeBridge()
    from pixel_refine_mobile.core.app_bridge import AppBridge
    app_bridge = AppBridge()
    
    full_qml = f"""
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {{
    anchors.fill: parent
    color: genericTheme.bgSecondary
    Column {{
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0
{body_qml}
    }}
}}
"""
    quick_widget = QQuickWidget()
    quick_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
    theme_bridge.setParent(quick_widget)
    app_bridge.setParent(quick_widget)
    quick_widget.rootContext().setContextProperty("genericTheme", theme_bridge)
    quick_widget.rootContext().setContextProperty("appBridge", app_bridge)
    
    qml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_ssim_test.qml")
    with open(qml_path, "w", encoding="utf-8") as f:
        f.write(full_qml)
        
    quick_widget.setSource(QUrl.fromLocalFile(qml_path))
    layout.addWidget(quick_widget, 1)
    
    win.show()
    
    # Process events to allow full layout and rendering
    for _ in range(10):
        QApplication.processEvents()
        time.sleep(0.02)
        
    # Capture screenshots of left and right frames
    img_pyside = get_screenshot(left_frame)
    img_qml = get_screenshot(quick_widget)
    
    # Perform SSIM comparison
    score = compare_images(img_pyside, img_qml, component_name)
    
    # Clean up window and temp file
    win.close()
    if os.path.exists(qml_path):
        try:
            os.remove(qml_path)
        except:
            pass
            
    return score

def main():
    app = QApplication(sys.argv)
    from resources.styles.stylesheet import stylesheet_global_page
    app.setStyleSheet(stylesheet_global_page())
    
    tests = [
        ("Button_Primary", lambda: Button("Start Process", variant="primary")),
        ("Button_Success", lambda: Button("Completed", variant="success")),
        ("ToggleButton", lambda: ToggleButton("Toggle Active", checked=True)),
        ("ToggleSwitch", lambda: ToggleSwitch()),
        ("Input", lambda: Input(placeholder="Type name...")),
        ("Select", lambda: Select(options=["High", "Medium", "Low"])),
        ("Checkbox", lambda: Checkbox("Autosave updates", checked=True)),
        ("RadioGroup", lambda: RadioGroup(options=["Fast", "Quality"], orientation="vertical")),
        ("ProgressBar", lambda: ProgressBar(style="linear", variant="info")),
        ("ListGroup", lambda: ListGroup()),
        ("DataTable", lambda: DataTable(columns=["File", "Size"])),
        ("FeatureCard", lambda: FeatureCard(
            title="HDR Demosaicing",
            description="Reconstruct color pixels using neighborhood values.",
            options=["Linear", "Bilinear", "Adaptive"],
            fallback_val="None"
        )),
    ]
    
    print("\n" + "=" * 50)
    print("STARTING VISUAL PARITY TESTING (SSIM)")
    print("=" * 50)
    
    results = {}
    for name, creator in tests:
        print(f"Testing component: {name}...")
        try:
            score = run_single_component_test(creator, name)
            results[name] = score
            print(f"  -> SSIM Score: {score:.4f}")
        except Exception as e:
            print(f"  -> [ERROR] Failed to test component {name}: {e}")
            results[name] = 0.0
            
    print("\n" + "=" * 50)
    print("VISUAL PARITY SUMMARY:")
    print("=" * 50)
    
    passed_count = 0
    for name, score in results.items():
        status = "PASSED" if score >= 0.95 else "DISPARITY (SSIM < 0.95)"
        if score >= 0.95:
            passed_count += 1
        print(f"  - {name:20s}: {score:.4f} | {status}")
        
    print("-" * 50)
    print(f"Passed: {passed_count} / {len(tests)} components.")
    print(f"Detailed diff reports saved in: {os.path.abspath(DIFF_DIR)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
