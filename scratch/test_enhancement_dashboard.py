import os
import sys

# Add project root to sys.path to resolve 'pixel_refine_desktop' imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QFileDialog,
    QGroupBox,
    QGridLayout,
    QSplitter,
    QFrame,
)
from PySide6.QtGui import (
    QPixmap,
    QImage,
    QColor,
    QPainter,
    QPen,
    QBrush,
    QFont,
    QLinearGradient,
)
from PySide6.QtCore import Qt, QSize

# Initialize Taichi
# =========================================================================
# === REAL-TIME HISTOGRAM WIDGET ===
# =========================================================================


class HistogramWidget(QWidget):
    """Draws a beautiful real-time overlay histogram of Original vs Enhanced images."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.orig_hist = None
        self.enh_hist = None
        self.setMinimumHeight(150)

    def update_histograms(self, orig_img, enh_img):
        """Update histogram data from 2D float32 images in range [0, 1]."""
        orig_u8 = (orig_img * 255.0).astype(np.uint8)
        enh_u8 = (enh_img * 255.0).astype(np.uint8)

        # Compute histograms
        self.orig_hist = cv2.calcHist([orig_u8], [0], None, [256], [0, 256])
        self.enh_hist = cv2.calcHist([enh_u8], [0], None, [256], [0, 256])

        # Normalize
        if self.orig_hist.max() > 0:
            self.orig_hist /= self.orig_hist.max()
        if self.enh_hist.max() > 0:
            self.enh_hist /= self.enh_hist.max()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QBrush(QColor("#1e1e24")))

        # Grid lines
        grid_pen = QPen(QColor("#2d2d38"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(1, 4):
            x = int(w * i / 4)
            painter.drawLine(x, 0, x, h)
            y = int(h * i / 4)
            painter.drawLine(0, y, w, y)

        if self.orig_hist is None or self.enh_hist is None:
            painter.setPen(QPen(QColor("#888888")))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Load an image to display histogram",
            )
            return

        # Draw Original Histogram (Translucent Grey Fill)
        orig_path = []
        for i in range(256):
            x = int(i * (w / 256.0))
            y = h - int(self.orig_hist[i][0] * (h - 10))
            orig_path.append((x, y))

        painter.setPen(QPen(QColor("rgba(150, 150, 150, 0.4)"), 1.5))
        painter.setBrush(QBrush(QColor("rgba(150, 150, 150, 0.1)")))

        # Simplified lines for performance
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#7f8c8d"), 1.5))
        for i in range(len(orig_path) - 1):
            painter.drawLine(
                orig_path[i][0],
                orig_path[i][1],
                orig_path[i + 1][0],
                orig_path[i + 1][1],
            )

        # Draw Enhanced Histogram (Vibrant Cyan Fill)
        enh_path = []
        for i in range(256):
            x = int(i * (w / 256.0))
            y = h - int(self.enh_hist[i][0] * (h - 10))
            enh_path.append((x, y))

        painter.setPen(QPen(QColor("#00ffd2"), 2))
        for i in range(len(enh_path) - 1):
            painter.drawLine(
                enh_path[i][0], enh_path[i][1], enh_path[i + 1][0], enh_path[i + 1][1]
            )

        # Labels
        painter.setPen(QPen(QColor("#7f8c8d")))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(5, h - 5, "0 (Shadows)")
        painter.drawText(w // 2 - 20, h - 5, "128 (Midtones)")
        painter.drawText(w - 75, h - 5, "255 (Highlights)")


# =========================================================================
# === MAIN INSTRUMENTATION & CALIBRATION DASHBOARD ===
# =========================================================================


class EnhancementDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Pixel Refine - Premium GPU Image Enhancement Calibration Dashboard"
        )
        self.resize(1400, 900)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #121216;
            }
            QWidget {
                color: #e2e2eb;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid #2d2d38;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                color: #00ffd2;
                background-color: #1a1a22;
            }
            QLabel {
                font-size: 11px;
                color: #b0b0bc;
            }
            QSlider::groove:horizontal {
                border: 1px solid #2d2d38;
                height: 4px;
                background: #252530;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #00ffd2;
                border: none;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QPushButton {
                background-color: #00ffd2;
                color: #121216;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00e0b8;
            }
            QPushButton#btn_load {
                background-color: #2b2b3a;
                color: #e2e2eb;
                border: 1px solid #3d3d4e;
            }
            QPushButton#btn_load:hover {
                background-color: #37374a;
            }
            QFrame#separator {
                background-color: #2d2d38;
            }
        """
        )

        # Core State Variables
        self.img_gray = None
        self.enhanced_gray = None
        self.h = 0
        self.w = 0

        self._init_ui()
        self._load_default_image()

    def _init_ui(self):
        # Master Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        master_layout = QHBoxLayout(main_widget)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Sidebar (Controls & Metrics Panel)
        sidebar = QWidget()
        sidebar.setFixedWidth(360)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(12)

        # Load / Save Actions
        btn_layout = QHBoxLayout()
        self.btn_load = QPushButton("Load Image")
        self.btn_load.setObjectName("btn_load")
        self.btn_load.clicked.connect(self.select_image)
        self.btn_save = QPushButton("Save Parameters")
        self.btn_save.clicked.connect(self.save_calibrated_results)
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_save)
        sidebar_layout.addLayout(btn_layout)

        # 1. Parameter Adjusters Group
        grp_controls = QGroupBox("Enhancement Calibration")
        ctrl_layout = QVBoxLayout(grp_controls)
        ctrl_layout.setSpacing(10)

        # Sliders list helper: (Key, Name, Min, Max, Default, Scale)
        self.sliders = {}
        slider_config = [
            ("micro_c", "Micro-Contrast (Details)", 0, 500, 150, 100.0),
            ("clarity", "Clarity (Midtone Local Contrast)", 0, 400, 120, 100.0),
            ("sigma", "Detail Scale (Sigma)", 5, 50, 15, 10.0),
            ("noise_coring", "Noise Coring (Suppress Noise)", 0, 100, 20, 1000.0),
            ("contrast", "Global Contrast Scale", 50, 300, 100, 100.0),
            ("brightness", "Brightness Offset", -50, 50, 0, 100.0),
            ("gamma", "Gamma Curve Adjust", 20, 300, 100, 100.0),
        ]

        for key, name, s_min, s_max, s_default, scale in slider_config:
            lbl_layout = QHBoxLayout()
            lbl = QLabel(name)
            val_lbl = QLabel(f"{s_default/scale:.2f}")
            lbl_layout.addWidget(lbl)
            lbl_layout.addStretch()
            lbl_layout.addWidget(val_lbl)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(s_min, s_max)
            slider.setValue(s_default)
            slider.valueChanged.connect(
                lambda v, kl=val_lbl, sc=scale, k=key: self.on_slider_changed(
                    k, v, kl, sc
                )
            )

            ctrl_layout.addLayout(lbl_layout)
            ctrl_layout.addWidget(slider)
            self.sliders[key] = (slider, val_lbl, scale)

        sidebar_layout.addWidget(grp_controls)

        # 2. Advanced Metrics Group
        grp_metrics = QGroupBox("Image Metrics & Instrumentation")
        metrics_layout = QGridLayout(grp_metrics)
        metrics_layout.setSpacing(12)

        # Metrics values labels
        self.lbl_orig_bright = QLabel("0.00%")
        self.lbl_enh_bright = QLabel("0.00%")
        self.lbl_orig_contrast = QLabel("0.00%")
        self.lbl_enh_contrast = QLabel("0.00%")
        self.lbl_orig_detail = QLabel("0.00%")
        self.lbl_enh_detail = QLabel("0.00%")

        # Style labels for metrics values
        for lbl in [
            self.lbl_orig_bright,
            self.lbl_enh_bright,
            self.lbl_orig_contrast,
            self.lbl_enh_contrast,
            self.lbl_orig_detail,
            self.lbl_enh_detail,
        ]:
            lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #ffffff;")

        self.lbl_enh_bright.setStyleSheet("color: #00ffd2;")
        self.lbl_enh_contrast.setStyleSheet("color: #00ffd2;")
        self.lbl_enh_detail.setStyleSheet("color: #00ffd2;")

        # Header Row
        metrics_layout.addWidget(QLabel("Metric"), 0, 0)
        metrics_layout.addWidget(QLabel("Original"), 0, 1)
        metrics_layout.addWidget(QLabel("Enhanced"), 0, 2)

        # Rows
        metrics_layout.addWidget(QLabel("Luminance / Brightness"), 1, 0)
        metrics_layout.addWidget(self.lbl_orig_bright, 1, 1)
        metrics_layout.addWidget(self.lbl_enh_bright, 1, 2)

        metrics_layout.addWidget(QLabel("Contrast (RMS)"), 2, 0)
        metrics_layout.addWidget(self.lbl_orig_contrast, 2, 1)
        metrics_layout.addWidget(self.lbl_enh_contrast, 2, 2)

        metrics_layout.addWidget(QLabel("Detail Density (Robust)"), 3, 0)
        metrics_layout.addWidget(self.lbl_orig_detail, 3, 1)
        metrics_layout.addWidget(self.lbl_enh_detail, 3, 2)

        sidebar_layout.addWidget(grp_metrics)
        sidebar_layout.addStretch()

        master_layout.addWidget(sidebar)

        # Right Panel (Visual Previews & Real-time Histogram)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # Interactive Previews Area (Split View)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            "QSplitter::handle { background-color: #2d2d38; width: 2px; }"
        )

        # Left preview pane (Original)
        left_pane = QWidget()
        lp_layout = QVBoxLayout(left_pane)
        lp_layout.setContentsMargins(0, 0, 0, 0)
        lp_layout.addWidget(QLabel("ORIGINAL INPUT IMAGE"))
        self.lbl_orig_preview = QLabel("Drag or click load image to display")
        self.lbl_orig_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_orig_preview.setStyleSheet(
            "background-color: #16161c; border: 1px solid #23232c; border-radius: 6px;"
        )
        lp_layout.addWidget(self.lbl_orig_preview, 1)

        # Right preview pane (Enhanced)
        right_pane = QWidget()
        rp_layout = QVBoxLayout(right_pane)
        rp_layout.setContentsMargins(0, 0, 0, 0)
        rp_layout.addWidget(QLabel("REAL-TIME ENHANCED OUTPUT (TAICHI GPU)"))
        self.lbl_enh_preview = QLabel("Waiting for image...")
        self.lbl_enh_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_enh_preview.setStyleSheet(
            "background-color: #16161c; border: 1px solid #23232c; border-radius: 6px;"
        )
        rp_layout.addWidget(self.lbl_enh_preview, 1)

        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        right_layout.addWidget(splitter, 1)

        # Histogram Panel
        grp_hist = QGroupBox("Real-time Histogram Representation")
        hist_layout = QVBoxLayout(grp_hist)
        hist_layout.setContentsMargins(10, 10, 10, 10)
        self.histogram_widget = HistogramWidget()
        hist_layout.addWidget(self.histogram_widget)

        right_layout.addWidget(grp_hist)
        master_layout.addWidget(right_panel, 1)

        # Enable Drag and Drop
        self.setAcceptDrops(True)

    # =========================================================================
    # === IMAGE HANDLING ===
    # =========================================================================

    def _load_default_image(self):
        """Attempts to load standard benchmark test image."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_path = os.path.join(root, "test_algorithm/IMG_20250401_182043_B003.png")
        if os.path.exists(default_path):
            self.load_image(default_path)
        else:
            # Generate dummy textured noise-free and noisy regions
            w, h = 800, 600
            grid_y, grid_x = np.mgrid[0:h, 0:w]
            img = (0.5 + 0.25 * np.sin(grid_x / 12.0) * np.cos(grid_y / 12.0)).astype(
                np.float32
            )
            img += 0.03 * np.random.randn(h, w).astype(np.float32)
            img = np.clip(img, 0.0, 1.0)
            self.set_image_data(img)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Input Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.dng *.raw)",
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, path):
        if not os.path.exists(path):
            return

        ext = os.path.splitext(path)[1].lower()
        if ext in (".dng", ".nef", ".cr2", ".arw", ".raw"):
            # Load DNG using Hamilton Demosaic with GPU acceleration
            try:
                from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot
                from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
                    taichi_lock,
                )

                with taichi_lock:
                    # Demosaic RAW directly via Hamilton
                    rgb_f32 = taichi_aot.demosaic(path, method="hamilton")

                if rgb_f32 is not None:
                    # Convert float32 RGB output of demosaic to uint8, then grayscale
                    rgb_u8 = np.clip(rgb_f32 * 255.0, 0, 255).astype(np.uint8)
                    img_gray = (
                        cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2GRAY).astype(np.float32)
                        / 255.0
                    )
                else:
                    raise RuntimeError("Hamilton demosaic returned None")
            except Exception as e:
                print(
                    f"Error loading RAW via Hamilton AOT: {e}. Falling back to rawpy."
                )
                import rawpy

                try:
                    with rawpy.imread(path) as raw:
                        img_bgr = raw.postprocess(half_size=True, use_camera_wb=True)
                        img_gray = (
                            cv2.cvtColor(img_bgr, cv2.COLOR_RGB2GRAY).astype(np.float32)
                            / 255.0
                        )
                except Exception as e_raw:
                    print(f"Error reading RAW via rawpy fallback: {e_raw}")
                    return
        else:
            img_bgr = cv2.imread(path)
            if img_bgr is None:
                return
            img_gray = (
                cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
            )

        h_orig, w_orig = img_gray.shape
        if w_orig > 1024:
            w_new = 1024
            h_new = int(h_orig * (w_new / w_orig))
            img_gray = cv2.resize(img_gray, (w_new, h_new))

        self.set_image_data(img_gray)

    def set_image_data(self, img_gray):
        self.img_gray = img_gray
        self.h, self.w = img_gray.shape

        self.display_on_label(self.img_gray, self.lbl_orig_preview)
        self.recompute_enhancement()

    def display_on_label(self, img_float, label):
        img_u8 = (img_float * 255.0).astype(np.uint8)
        height, width = img_u8.shape
        bytes_per_line = width
        q_img = QImage(
            img_u8.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8
        )

        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            label.width() - 4,
            label.height() - 4,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        label.setPixmap(scaled_pixmap)

    # =========================================================================
    # === INTERACTIVE UPDATE & GPU PIPELINE ===
    # =========================================================================

    def on_slider_changed(self, key, value, val_lbl, scale):
        val_lbl.setText(f"{value/scale:.2f}")
        self.recompute_enhancement()

    def get_current_params(self):
        params = {}
        for k, (slider, _, scale) in self.sliders.items():
            params[k] = slider.value() / scale
        return params

    def recompute_enhancement(self):
        if self.img_gray is None:
            return

        params = self.get_current_params()
        micro_c = params["micro_c"]
        clarity = params["clarity"]
        sigma = params["sigma"]
        noise_coring = params.get("noise_coring", 0.02)
        contrast = params["contrast"]
        brightness = params["brightness"]
        gamma = params["gamma"]

        # 1. Generate 1D LUT Curve on CPU
        lut_np = np.zeros(256, dtype=np.float32)
        for i in range(256):
            val = (i / 255.0) ** gamma * contrast + brightness
            lut_np[i] = np.clip(val, 0.0, 1.0)

        # 2. Run Gaussian blur using core taichi_algorithm module
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian import (
            gaussian_blur,
        )

        blurred_np = gaussian_blur(self.img_gray, sigma=sigma)

        # 3. Run Grayscale Image Enhancement using core taichi_algorithm module
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.enhance_image import (
            enhance_grayscale,
        )

        self.enhanced_gray = enhance_grayscale(
            self.img_gray,
            blurred_np,
            lut_np,
            micro_contrast=micro_c,
            clarity=clarity,
            noise_coring=noise_coring,
        )

        self.display_on_label(self.enhanced_gray, self.lbl_enh_preview)
        self.histogram_widget.update_histograms(self.img_gray, self.enhanced_gray)
        self.calculate_metrics()

    # =========================================================================
    # === ADVANCED METRICS ENGINE (NOISE-ROBUST DETAIL & CONTRAST) ===
    # =========================================================================

    def calculate_metrics(self):
        if self.img_gray is None or self.enhanced_gray is None:
            return

        orig_metrics = self._extract_image_features(self.img_gray)
        self.lbl_orig_bright.setText(f"{orig_metrics['brightness']:.2f}%")
        self.lbl_orig_contrast.setText(f"{orig_metrics['rms_contrast']:.2f}%")
        self.lbl_orig_detail.setText(f"{orig_metrics['detail_score']:.2f}%")

        enh_metrics = self._extract_image_features(self.enhanced_gray)
        self.lbl_enh_bright.setText(f"{enh_metrics['brightness']:.2f}%")
        self.lbl_enh_contrast.setText(f"{enh_metrics['rms_contrast']:.2f}%")
        self.lbl_enh_detail.setText(f"{enh_metrics['detail_score']:.2f}%")

    def _extract_image_features(self, img_float):
        img_u8 = (img_float * 255.0).astype(np.uint8)
        brightness = float(np.mean(img_float)) * 100.0
        rms_contrast = float(np.std(img_float)) * 100.0

        # Noise-robust detail evaluation using bilateral filter and Sobel gradient thresholding
        denoised = cv2.bilateralFilter(img_u8, d=5, sigmaColor=15, sigmaSpace=15)
        sobel_x = cv2.Sobel(denoised, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(denoised, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(sobel_x**2 + sobel_y**2)

        noise_threshold = 12.0
        significant_details = grad_mag[grad_mag > noise_threshold]

        if len(significant_details) > 0:
            detail_density = (len(significant_details) / grad_mag.size) * 100.0
            avg_magnitude = np.mean(significant_details)
            detail_score = (detail_density * 0.4) + (avg_magnitude * 0.6)
        else:
            detail_score = 0.0

        detail_score = min(100.0, max(0.0, detail_score))

        return {
            "brightness": brightness,
            "rms_contrast": rms_contrast,
            "detail_score": detail_score,
        }

    # =========================================================================
    # === UTILITIES ===
    # =========================================================================

    def save_calibrated_results(self):
        if self.img_gray is None or self.enhanced_gray is None:
            return

        file_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if not file_dir:
            return

        src_u8 = (self.img_gray * 255.0).astype(np.uint8)
        enh_u8 = (self.enhanced_gray * 255.0).astype(np.uint8)
        comparison = np.hstack((src_u8, enh_u8))

        comp_path = os.path.join(file_dir, "calibrated_comparison.png")
        cv2.imwrite(comp_path, comparison)

        params = self.get_current_params()
        orig_metrics = self._extract_image_features(self.img_gray)
        enh_metrics = self._extract_image_features(self.enhanced_gray)

        txt_path = os.path.join(file_dir, "calibration_metadata.txt")
        with open(txt_path, "w") as f:
            f.write("=== CALIBRATION METADATA FILE ===\n\n")
            f.write("--- Calibration Slider Parameters ---\n")
            for k, v in params.items():
                f.write(f"{k}: {v:.4f}\n")
            f.write("\n--- Image Analytics Metrics ---\n")
            f.write(f"Original Brightness: {orig_metrics['brightness']:.2f}%\n")
            f.write(f"Enhanced Brightness: {enh_metrics['brightness']:.2f}%\n")
            f.write(f"Original Contrast (RMS): {orig_metrics['rms_contrast']:.2f}%\n")
            f.write(f"Enhanced Contrast (RMS): {enh_metrics['rms_contrast']:.2f}%\n")
            f.write(f"Original Detail Index: {orig_metrics['detail_score']:.2f}%\n")
            f.write(f"Enhanced Detail Index: {enh_metrics['detail_score']:.2f}%\n")

        print(f"Calibration data saved to {file_dir}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.exists(file_path):
                self.load_image(file_path)
                break

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.img_gray is not None:
            self.display_on_label(self.img_gray, self.lbl_orig_preview)
        if self.enhanced_gray is not None:
            self.display_on_label(self.enhanced_gray, self.lbl_enh_preview)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = EnhancementDashboard()
    dashboard.show()
    sys.exit(app.exec())
