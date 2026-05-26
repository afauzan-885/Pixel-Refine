import os
import sys
import time
import numpy as np
import taichi as ti
import rawpy
import cv2

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
    QPushButton,
    QFileDialog,
    QGroupBox,
    QSplitter,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsPixmapItem,
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap

# Initialize Taichi on GPU
ti.init(arch=ti.vulkan, offline_cache=False)

# =========================================================================
# TAICHI JIT KERNELS
# =========================================================================


@ti.kernel
def _preprocess_bayer_kernel(
    bayer: ti.types.ndarray(),
    wb_bayer: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    black: ti.f32,
    white: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        val = ti.math.clamp(
            (bayer[r, c] - black) / ti.max(1.0, white - black), 0.0, 1.0
        )
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        gain = 1.0
        if color_idx == 0:
            gain = wb_r
        elif color_idx == 1:
            gain = wb_g1
        elif color_idx == 2:
            gain = wb_b
        else:
            gain = wb_g2

        wb_bayer[r, c] = val * gain


@ti.kernel
def _ha_green_interpolation_kernel_opt(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        is_green = (color_idx == 1) or (color_idx == 3)
        if is_green:
            green[r, c] = wb_bayer[r, c]
        else:
            if r > 1 and r < h - 2 and c > 1 and c < w - 2:
                g_left = wb_bayer[r, c - 1]
                g_right = wb_bayer[r, c + 1]
                g_up = wb_bayer[r - 1, c]
                g_down = wb_bayer[r + 1, c]
                c_center = wb_bayer[r, c]
                c_left2 = wb_bayer[r, c - 2]
                c_right2 = wb_bayer[r, c + 2]
                c_up2 = wb_bayer[r - 2, c]
                c_down2 = wb_bayer[r + 2, c]

                dh = ti.abs(g_left - g_right) + ti.abs(
                    2.0 * c_center - c_left2 - c_right2
                )
                dv = ti.abs(g_up - g_down) + ti.abs(2.0 * c_center - c_up2 - c_down2)

                if dh < dv:
                    green[r, c] = (g_left + g_right) * 0.5 + (
                        2.0 * c_center - c_left2 - c_right2
                    ) * 0.25
                elif dh > dv:
                    green[r, c] = (g_up + g_down) * 0.5 + (
                        2.0 * c_center - c_up2 - c_down2
                    ) * 0.25
                else:
                    green[r, c] = (g_left + g_right + g_up + g_down) * 0.25 + (
                        4.0 * c_center - c_left2 - c_right2 - c_up2 - c_down2
                    ) * 0.125
            else:
                g_val = 0.0
                g_count = 0.0
                for dr, dc in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < h and nc >= 0 and nc < w:
                        g_val += wb_bayer[nr, nc]
                        g_count += 1.0
                green[r, c] = g_val / g_count


@ti.kernel
def demosaic_camera_linear_kernel(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    dst_linear: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        R, G, B = 0.0, 0.0, 0.0
        G = green[r, c]

        if color_idx == 0:  # Red pixel
            R = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                b_diff = (
                    (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1])
                    + (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1])
                    + (wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                    + (wb_bayer[r + 1, c + 1] - green[r + 1, c + 1])
                ) * 0.25
                B = G + b_diff
            else:
                B = G

        elif color_idx == 2:  # Blue pixel
            B = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                r_diff = (
                    (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1])
                    + (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1])
                    + (wb_bayer[r + 1, c - 1] - green[r - 1, c - 1])
                    + (wb_bayer[r + 1, c + 1] - green[r + 1, c + 1])
                ) * 0.25
                R = G + r_diff
            else:
                R = G

        else:  # Green pixel
            is_red_horizontal = False
            if r_mod == 0:
                other_color = c00 if c_mod == 1 else c01
                is_red_horizontal = other_color == 0
            else:
                other_color = c10 if c_mod == 1 else c11
                is_red_horizontal = other_color == 0

            if is_red_horizontal:  # Red is Horizontal, Blue is Vertical
                if c > 0 and c < w - 1:
                    r_diff = (
                        (wb_bayer[r, c - 1] - green[r, c - 1])
                        + (wb_bayer[r, c + 1] - green[r, c + 1])
                    ) * 0.5
                    R = G + r_diff
                else:
                    R = G

                if r > 0 and r < h - 1:
                    b_diff = (
                        (wb_bayer[r - 1, c] - green[r - 1, c])
                        + (wb_bayer[r + 1, c] - green[r + 1, c])
                    ) * 0.5
                    B = G + b_diff
                else:
                    B = G

            else:  # Blue is Horizontal, Red is Vertical
                if r > 0 and r < h - 1:
                    r_diff = (
                        (wb_bayer[r - 1, c] - green[r - 1, c])
                        + (wb_bayer[r + 1, c] - green[r + 1, c])
                    ) * 0.5
                    R = G + r_diff
                else:
                    R = G

                if c > 0 and c < w - 1:
                    b_diff = (
                        (wb_bayer[r, c - 1] - green[r, c - 1])
                        + (wb_bayer[r, c + 1] - green[r, c + 1])
                    ) * 0.5
                    B = G + b_diff
                else:
                    B = G

        # Save camera space linear values
        dst_linear[r, c, 0] = R
        dst_linear[r, c, 1] = G
        dst_linear[r, c, 2] = B


@ti.kernel
def postprocess_highlight_kernel(
    src_linear: ti.types.ndarray(),
    dst_srgb: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    h: ti.i32,
    w: ti.i32,
    hl_threshold: ti.f32,
    hl_range: ti.f32,
    hl_neutral_threshold: ti.f32,
    hl_neutral_range: ti.f32,
    hl_blend: ti.f32,
    exposure: ti.f32,
    anti_magenta: ti.f32,
):
    for r, c in ti.ndrange(h, w):
        # 1. Get original camera-space values (pre-exposure)
        R_orig = src_linear[r, c, 0]
        G_orig = src_linear[r, c, 1]
        B_orig = src_linear[r, c, 2]

        # 2. Estimate original RAW Bayer values (before exposure and white balance)
        R_raw = R_orig / ti.max(0.1, wb_r)
        G_raw = G_orig / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
        B_raw = B_orig / ti.max(0.1, wb_b)

        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        min_raw = ti.min(R_raw, ti.min(G_raw, B_raw))

        # 3. Calculate highlight desaturation factor (Smoothstep) on original RAW
        factor = ti.math.clamp(
            (max_raw - hl_threshold) / ti.max(1e-5, hl_range), 0.0, 1.0
        )
        factor = factor * factor * (3.0 - 2.0 * factor)

        # Forcibly and automatically balance all RAW channels in highlights first
        # G_raw is used as the reference luminance channel to balance red and blue channels
        R_raw_balanced = R_raw * (1.0 - factor) + G_raw * factor
        B_raw_balanced = B_raw * (1.0 - factor) + G_raw * factor
        G_raw_balanced = G_raw

        # Re-apply camera white balance to get perfectly balanced camera space linear values
        R_orig_balanced = R_raw_balanced * wb_r
        G_orig_balanced = G_raw_balanced * (wb_g1 + wb_g2) * 0.5
        B_orig_balanced = B_raw_balanced * wb_b

        # Calculate color neutrality weight
        ratio = min_raw / ti.max(1e-5, max_raw)
        neutrality = ti.math.clamp(
            (ratio - hl_neutral_threshold) / ti.max(1e-5, hl_neutral_range), 0.0, 1.0
        )
        neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)

        # Morphed blend factor: when anti_magenta=1.0, we ignore neutrality and force desaturation to white
        blend_to_white = factor * (1.0 - (1.0 - neutrality) * (1.0 - anti_magenta)) * hl_blend

        # 4. Apply exposure gain to get output values
        R_out = R_orig_balanced * exposure
        G_out = G_orig_balanced * exposure
        B_out = B_orig_balanced * exposure

        # 5. Reconstruct and blend
        L_out = ti.max(R_out, ti.max(G_out, B_out))
        R_new = R_out * (1.0 - blend_to_white) + L_out * blend_to_white
        G_new = G_out * (1.0 - blend_to_white) + L_out * blend_to_white
        B_new = B_out * (1.0 - blend_to_white) + L_out * blend_to_white

        # 6. Apply Camera-to-sRGB matrix transform
        sR = cmatrix[0, 0] * R_new + cmatrix[0, 1] * G_new + cmatrix[0, 2] * B_new
        sG = cmatrix[1, 0] * R_new + cmatrix[1, 1] * G_new + cmatrix[1, 2] * B_new
        sB = cmatrix[2, 0] * R_new + cmatrix[2, 1] * G_new + cmatrix[2, 2] * B_new

        # 7. Apply Dynamic Algebraic Sigmoid Highlight Roll-off
        sR = sR / ti.math.sqrt(1.0 + sR * sR)
        sG = sG / ti.math.sqrt(1.0 + sG * sG)
        sB = sB / ti.math.sqrt(1.0 + sB * sB)

        dst_srgb[r, c, 0] = ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22)
        dst_srgb[r, c, 1] = ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22)
        dst_srgb[r, c, 2] = ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)


# =========================================================================
# INTERACTIVE ZOOM & PAN GRAPHICS VIEW
# =========================================================================


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setStyleSheet("background: #0f172a; border: none;")

    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def set_image(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(pixmap.rect())


# =========================================================================
# MAIN GUI WINDOW
# =========================================================================


class InteractiveHighlightApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Refine - Realtime Highlight Reconstruction Analyzer")
        self.resize(1300, 800)

        # Style layout
        self.setStyleSheet(
            """
            QMainWindow { background-color: #0f172a; }
            QWidget { color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }
            QGroupBox {
                border: 1px solid #334155;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #1e293b;
                font-weight: bold;
                color: #38bdf8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel { color: #cbd5e1; }
            QSlider::groove:horizontal {
                border: 1px solid #475569;
                height: 6px;
                background: #334155;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #38bdf8;
                border: 1px solid #0284c7;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton:pressed { background-color: #1d4ed8; }
        """
        )

        # Core state
        self.dng_path = None
        self.bayer_gpu = None
        self.wb_bayer_gpu = None
        self.green_gpu = None
        self.dst_linear_gpu = None
        self.dst_srgb_gpu = None
        self.cmatrix_gpu = None
        self.metadata = {}

        # Default DNG path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_dng = os.path.join(
            project_root, "test_algorithm/IMG_20250423_160105_B001.dng"
        )
        if os.path.exists(default_dng):
            self.dng_path = default_dng

        self.setup_ui()

        if self.dng_path:
            self.load_and_demosaic()

    def setup_ui(self):
        # Master splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # Left panel: Controls
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)

        # File IO
        io_group = QGroupBox("RAW Input File")
        io_layout = QVBoxLayout(io_group)
        self.lbl_file = QLabel(
            "No file loaded"
            if not self.dng_path
            else f"Loaded: {os.path.basename(self.dng_path)}"
        )
        self.lbl_file.setWordWrap(True)
        btn_open = QPushButton("Open DNG File")
        btn_open.clicked.connect(self.on_open_file)
        io_layout.addWidget(self.lbl_file)
        io_layout.addWidget(btn_open)
        control_layout.addWidget(io_group)

        # Exposure Group
        exp_group = QGroupBox("Exposure Control")
        exp_layout = QVBoxLayout(exp_group)
        self.slider_exp = self.create_slider(
            exp_layout, "Gain Multiplier", 0.1, 4.0, 1.0, decimals=2
        )
        control_layout.addWidget(exp_group)

        # Highlight Desaturation Parameters
        hl_group = QGroupBox("Highlight Recovery Thresholds")
        hl_layout = QVBoxLayout(hl_group)
        self.slider_hl_thresh = self.create_slider(
            hl_layout, "Desat Start Threshold", 0.0, 1.0, 0.55, decimals=2
        )
        self.slider_hl_range = self.create_slider(
            hl_layout, "Desat Transition Range", 0.01, 1.0, 0.43, decimals=2
        )
        control_layout.addWidget(hl_group)

        # Neutrality constraints
        neut_group = QGroupBox("Color Neutrality (Magenta Blending)")
        neut_layout = QVBoxLayout(neut_group)
        self.slider_neut_thresh = self.create_slider(
            neut_layout, "Neutrality Start Threshold", 0.0, 1.0, 0.40, decimals=2
        )
        self.slider_neut_range = self.create_slider(
            neut_layout, "Neutrality Soft Range", 0.01, 1.0, 0.45, decimals=2
        )
        self.slider_hl_blend = self.create_slider(
            neut_layout, "Highlight Blending Strength", 0.0, 1.0, 1.0, decimals=2
        )
        self.slider_anti_magenta = self.create_slider(
            neut_layout, "Anti-Magenta Protection", 0.0, 1.0, 1.0, decimals=2
        )
        control_layout.addWidget(neut_group)

        # Status and Save
        status_group = QGroupBox("Diagnostics & Actions")
        status_layout = QVBoxLayout(status_group)
        self.lbl_perf = QLabel("Performance: - ms")
        btn_save = QPushButton("Save Output TIFF")
        btn_save.clicked.connect(self.on_save_tiff)
        status_layout.addWidget(self.lbl_perf)
        status_layout.addWidget(btn_save)
        control_layout.addWidget(status_group)

        control_layout.addStretch()
        splitter.addWidget(control_panel)

        # Right panel: Viewport
        self.view = ZoomableGraphicsView()
        splitter.addWidget(self.view)

        # Set splitter sizes
        splitter.setSizes([350, 950])

    def create_slider(self, layout, name, min_val, max_val, default, decimals=2):
        lbl_text = QLabel(f"{name}: {default:.2f}")
        slider = QSlider(Qt.Orientation.Horizontal)

        # Scale to integer for QSlider
        scale = 10**decimals
        slider.setRange(int(min_val * scale), int(max_val * scale))
        slider.setValue(int(default * scale))

        def on_value_changed(val):
            actual_val = val / scale
            lbl_text.setText(f"{name}: {actual_val:.2f}")
            self.update_render()

        slider.valueChanged.connect(on_value_changed)
        layout.addWidget(lbl_text)
        layout.addWidget(slider)
        return slider

    def get_slider_val(self, slider, decimals=2):
        return slider.value() / (10**decimals)

    def load_and_demosaic(self):
        if not self.dng_path or not os.path.exists(self.dng_path):
            return

        self.lbl_file.setText(
            f"Loading & Interpolating: {os.path.basename(self.dng_path)}"
        )
        QApplication.processEvents()

        # Load RAW and metadata
        with rawpy.imread(self.dng_path) as raw:
            bayer_np = raw.raw_image.astype(np.float32)
            self.metadata["black_level"] = float(raw.black_level_per_channel[0])
            self.metadata["white_level"] = float(raw.white_level)

            wb_np = np.array(raw.camera_whitebalance, dtype=np.float32)
            if len(wb_np) == 4:
                if wb_np[3] <= 0.01:
                    wb_np[3] = wb_np[1]
                g_gain = (wb_np[1] + wb_np[3]) / 2.0
                wb_np /= g_gain
            else:
                wb_np = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)

            self.metadata["wb"] = wb_np
            self.metadata["c00"] = int(raw.raw_colors[0, 0])
            self.metadata["c01"] = int(raw.raw_colors[0, 1])
            self.metadata["c10"] = int(raw.raw_colors[1, 0])
            self.metadata["c11"] = int(raw.raw_colors[1, 1])
            self.metadata["cmatrix"] = raw.color_matrix[:, :3].astype(np.float32)

        h, w = bayer_np.shape

        # Allocate GPU buffers
        self.bayer_gpu = ti.ndarray(dtype=ti.f32, shape=(h, w))
        self.wb_bayer_gpu = ti.ndarray(dtype=ti.f32, shape=(h, w))
        self.green_gpu = ti.ndarray(dtype=ti.f32, shape=(h, w))
        self.dst_linear_gpu = ti.ndarray(dtype=ti.f32, shape=(h, w, 3))
        self.dst_srgb_gpu = ti.ndarray(dtype=ti.f32, shape=(h, w, 3))
        self.cmatrix_gpu = ti.ndarray(dtype=ti.f32, shape=(3, 3))

        # Copy static data
        self.bayer_gpu.from_numpy(bayer_np)
        self.cmatrix_gpu.from_numpy(self.metadata["cmatrix"])

        # Run Linear Demosaicing (Once!)
        t0 = time.perf_counter()
        _preprocess_bayer_kernel(
            self.bayer_gpu,
            self.wb_bayer_gpu,
            self.metadata["wb"][0],
            self.metadata["wb"][1],
            self.metadata["wb"][2],
            self.metadata["wb"][3],
            self.metadata["black_level"],
            self.metadata["white_level"],
            h,
            w,
            self.metadata["c00"],
            self.metadata["c01"],
            self.metadata["c10"],
            self.metadata["c11"],
        )
        _ha_green_interpolation_kernel_opt(
            self.wb_bayer_gpu,
            self.green_gpu,
            h,
            w,
            self.metadata["c00"],
            self.metadata["c01"],
            self.metadata["c10"],
            self.metadata["c11"],
        )
        demosaic_camera_linear_kernel(
            self.wb_bayer_gpu,
            self.green_gpu,
            self.dst_linear_gpu,
            h,
            w,
            self.metadata["c00"],
            self.metadata["c01"],
            self.metadata["c10"],
            self.metadata["c11"],
        )
        ti.sync()
        t1 = time.perf_counter()

        self.lbl_file.setText(
            f"Loaded: {os.path.basename(self.dng_path)}\nDemosaicing JIT Time: {(t1-t0)*1000:.1f} ms"
        )
        self.update_render()

    @Slot()
    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open DNG RAW Image", "", "RAW Images (*.dng *.raw)"
        )
        if file_path:
            self.dng_path = file_path
            self.load_and_demosaic()

    def update_render(self):
        if self.dst_linear_gpu is None:
            return

        # Get values from sliders
        exposure = self.get_slider_val(self.slider_exp)
        hl_threshold = self.get_slider_val(self.slider_hl_thresh)
        hl_range = self.get_slider_val(self.slider_hl_range)
        hl_neutral_threshold = self.get_slider_val(self.slider_neut_thresh)
        hl_neutral_range = self.get_slider_val(self.slider_neut_range)
        hl_blend = self.get_slider_val(self.slider_hl_blend)
        anti_magenta = self.get_slider_val(self.slider_anti_magenta)

        h, w = self.dst_linear_gpu.shape[:2]

        # Time the postprocess kernel
        t0 = time.perf_counter()
        postprocess_highlight_kernel(
            self.dst_linear_gpu,
            self.dst_srgb_gpu,
            self.cmatrix_gpu,
            self.metadata["wb"][0],
            self.metadata["wb"][1],
            self.metadata["wb"][2],
            self.metadata["wb"][3],
            h,
            w,
            hl_threshold,
            hl_range,
            hl_neutral_threshold,
            hl_neutral_range,
            hl_blend,
            exposure,
            anti_magenta,
        )
        ti.sync()
        t1 = time.perf_counter()
        perf_ms = (t1 - t0) * 1000
        self.lbl_perf.setText(f"Postprocess GPU Time: {perf_ms:.2f} ms")

        # Download result to display
        res_np = self.dst_srgb_gpu.to_numpy()
        res_8u = (res_np * 255.0).astype(np.uint8)

        # Convert to QImage
        h_im, w_im, _ = res_8u.shape
        qimg = QImage(res_8u.data, w_im, h_im, w_im * 3, QImage.Format.Format_RGB888)

        # We need to keep a reference to the image data so it doesn't get GC'd
        self._curr_image_data = res_8u
        self.view.set_image(qimg)

    @Slot()
    def on_save_tiff(self):
        if self.dst_srgb_gpu is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output Image",
            "calibrated_highlight_render.tif",
            "TIFF Image (*.tif);;PNG Image (*.png)",
        )
        if file_path:
            res_np = self.dst_srgb_gpu.to_numpy()

            if file_path.endswith(".tif"):
                # Save high-fidelity 16-bit BGR image
                res_bgr_16 = (res_np[:, :, ::-1] * 65535.0).astype(np.uint16)
                cv2.imwrite(file_path, res_bgr_16)
            else:
                # Save standard 8-bit BGR image
                res_bgr_8 = (res_np[:, :, ::-1] * 255.0).astype(np.uint8)
                cv2.imwrite(file_path, res_bgr_8)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InteractiveHighlightApp()
    window.show()
    sys.exit(app.exec())
