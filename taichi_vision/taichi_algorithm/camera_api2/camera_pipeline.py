"""
Camera Pipeline - Taichi GPU Orchestrator
==========================================
Pipeline orchestrator untuk Camera2 real-time processing.
Meng-orchestrate seluruh stage processing dengan zero-copy GPU pipeline.

Pipeline Stages:
  1. YUV → RGB conversion (yuv_converter.py)
  2. Denoising (nlm, bm3d, guided_filter, bilateral)
  3. Color & Tone (white balance, CLAHE, color convert)
  4. Enhancement (sharpen, edge enhance)
  5. Output (resize, format convert)

Menggunakan:
  - frame_manager.py untuk buffer management
  - taichi_algorithm existing modules untuk processing
  - common.py untuk GPU buffer pool
  - taichi_worker.py untuk CUDA context serialization
"""

import numpy as np
import threading
import time
import os
import importlib

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
    from ..taichi_worker import ti_thread
    from .yuv_converter import yuv420_to_rgb, nv21_to_rgb
    from .frame_manager import (
        LatestFrameQueue,
        AdaptiveFrameController,
        FrameBufferPool,
        TripleBuffer,
    )
except ImportError:
    pass


# =========================================================================
# Pipeline Stage Interface
# =========================================================================


class PipelineStage:
    """
    Base class untuk setiap pipeline stage.
    Setiap stage: terima Taichi field input, return Taichi field output.
    Stay di GPU selama mungkin (zero-copy).
    """

    def __init__(self, name="unnamed", enabled=True):
        self.name = name
        self.enabled = enabled
        self._last_time_ms = 0.0

    @ti_thread
    def process(self, input_field, context=None):
        """
        Process input field dan return output field.
        Override di subclass.

        Args:
            input_field: Taichi ndarray (GPU buffer)
            context: dict dengan metadata Camera2 (ISO, exposure, dll)

        Returns:
            Taichi ndarray (GPU buffer, bisa sama atau beda dari input)
        """
        raise NotImplementedError

    @property
    def last_time_ms(self):
        return self._last_time_ms


# =========================================================================
# Concrete Pipeline Stages
# =========================================================================


class DenoiseStage(PipelineStage):
    """
    Adaptive denoising stage.
    Auto-select algorithm berdasarkan ISO dari Camera2 metadata.

    ISO < 400:   skip (noise rendah)
    ISO 400-1600: guided filter (cepat, edge-preserving)
    ISO 1600-3200: NLM search=5, patch=2 (balanced)
    ISO > 3200:   NLM search=7, patch=3 (heavy)
    """

    def __init__(self):
        super().__init__("denoise", enabled=True)

    @ti_thread
    def process(self, input_field, context=None):
        if not TAICHI_AVAILABLE:
            return input_field

        iso = 100
        if context and "iso" in context:
            iso = context["iso"]

        start = time.perf_counter_ns()

        if iso < 400:
            # Noise rendah, skip denoise
            result = input_field
        elif iso < 1600:
            # Light denoise: guided filter
            from ..smoothing.guided_filter import guided_filter

            result = guided_filter(input_field, radius=2, epsilon=0.01)
        elif iso < 3200:
            # Medium denoise: NLM
            from ..denoising.nlm import non_local_means

            result = non_local_means(
                input_field, h_param=8.0, search_window=5, patch_size=2
            )
        else:
            # Heavy denoise: NLM aggressive
            from ..denoising.nlm import non_local_means

            result = non_local_means(
                input_field, h_param=12.0, search_window=7, patch_size=3
            )

        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        self._last_time_ms = elapsed
        return result


class ColorEnhanceStage(PipelineStage):
    """
    Color enhancement stage.
    CLAHE untuk local contrast, white balance correction.
    """

    def __init__(self, clahe_clip=2.0, clahe_grid=8):
        super().__init__("color_enhance", enabled=True)
        self.clahe_clip = clahe_clip
        self.clahe_grid = clahe_grid

    @ti_thread
    def process(self, input_field, context=None):
        if not TAICHI_AVAILABLE:
            return input_field

        start = time.perf_counter_ns()

        # CLAHE untuk adaptive contrast
        from ..image_processing.clahe import clahe

        result = clahe(
            input_field, clip_limit=self.clahe_clip, grid_size=self.clahe_grid
        )

        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        self._last_time_ms = elapsed
        return result


class SharpenStage(PipelineStage):
    """
    Sharpening via unsharp mask.
    sharpened = original + amount * (original - blurred)
    """

    def __init__(self, amount=0.5, sigma=1.0):
        super().__init__("sharpen", enabled=True)
        self.amount = amount
        self.sigma = sigma

    @ti_thread
    def process(self, input_field, context=None):
        if not TAICHI_AVAILABLE:
            return input_field

        start = time.perf_counter_ns()

        # Gaussian blur
        from ..smoothing.gaussian import gaussian_blur

        blurred = gaussian_blur(input_field, sigma=self.sigma, kernel_size=3)

        # Unsharp mask: result = input + amount * (input - blurred)
        result = common.get_temp_buffer(
            input_field.shape, ti.f32, buffer_provider="pool"
        )
        _unsharp_mask_kernel(
            input_field,
            blurred,
            result,
            self.amount,
            input_field.shape[0],
            input_field.shape[1],
        )

        # Cleanup
        common.release_temp_buffer(blurred)

        elapsed = (time.perf_counter_ns() - start) / 1_000_000
        self._last_time_ms = elapsed
        return result


if TAICHI_AVAILABLE:

    @ti.kernel
    def _unsharp_mask_kernel(
        src: ti.types.ndarray(),
        blurred: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        amount: float,
        h: int,
        w: int,
    ):
        """Unsharp mask: dst = src + amount * (src - blurred)"""
        for y, x in ti.ndrange(h, w):
            for c in ti.static(range(3)):
                diff = src[y, x, c] - blurred[y, x, c]
                dst[y, x, c] = tm.clamp(src[y, x, c] + amount * diff, 0.0, 1.0)


# =========================================================================
# Camera Pipeline Orchestrator
# =========================================================================


class CameraPipeline:
    """
    Main orchestrator untuk Camera2 real-time processing.

    Mengelola:
    - Stage chain: YUV→RGB → Denoise → Color → Sharpen → Output
    - Buffer management: reuse GPU buffers, zero-allocation hot path
    - Adaptive frame control: skip frame jika processing lambat
    - Performance monitoring: FPS, latency per stage

    Usage:
        pipeline = CameraPipeline(width=1920, height=1080)
        pipeline.start()

        # Dari Camera2 callback:
        pipeline.submit_yuv(y_data, u_data, v_data, timestamp_ns)

        # Untuk display:
        result = pipeline.get_latest_output()

        pipeline.stop()
    """

    def __init__(
        self,
        width=1920,
        height=1080,
        target_fps=30.0,
        enable_denoise=True,
        enable_color_enhance=True,
        enable_sharpen=True,
        clahe_clip=2.0,
        clahe_grid=8,
        sharpen_amount=0.5,
    ):
        self.width = width
        self.height = height
        self.running = False

        # Frame management
        self.input_queue = LatestFrameQueue()
        self.output_queue = LatestFrameQueue()
        self.frame_ctrl = AdaptiveFrameController(target_fps=target_fps)
        self.buffer_pool = FrameBufferPool(height, width, 3)

        # Pipeline stages
        self.stages = []

        # Stage 1: YUV→RGB (selalu aktif)
        # (handled di _process_frame langsung, bukan PipelineStage)

        # Stage 2: Denoise
        if enable_denoise:
            self.denoise_stage = DenoiseStage()
            self.stages.append(self.denoise_stage)

        # Stage 3: Color enhance
        if enable_color_enhance:
            self.color_stage = ColorEnhanceStage(
                clahe_clip=clahe_clip, clahe_grid=clahe_grid
            )
            self.stages.append(self.color_stage)

        # Stage 4: Sharpen
        if enable_sharpen:
            self.sharpen_stage = SharpenStage(amount=sharpen_amount)
            self.stages.append(self.sharpen_stage)

        # Processing thread
        self._thread = None
        self._lock = threading.Lock()

        # Performance stats
        self._total_frames = 0
        self._total_dropped = 0
        self._last_total_ms = 0.0
        self._fps_history = []

    def start(self):
        """Start pipeline processing thread."""
        if self.running:
            return

        self.running = True
        self.buffer_pool.preallocate(count=4)

        self._thread = threading.Thread(
            target=self._processing_loop, name="CameraPipeline", daemon=True
        )
        self._thread.start()

    def stop(self):
        """Stop pipeline processing thread."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def submit_yuv(
        self,
        y_data,
        u_data,
        v_data,
        timestamp_ns=0,
        frame_number=0,
        y_row_stride=None,
        y_pixel_stride=1,
        u_row_stride=None,
        u_pixel_stride=1,
        v_row_stride=None,
        v_pixel_stride=1,
        metadata=None,
    ):
        """
        Submit YUV frame dari Camera2 ImageReader.
        Non-blocking: jika processing belum selesai, frame lama di-drop.

        Args:
            y_data: Y plane numpy array (H, W) uint8
            u_data: U plane numpy array (H/2, W/2) uint8
            v_data: V plane numpy array (H/2, W/2) uint8
            timestamp_ns: Camera2 timestamp
            frame_number: Frame counter
            *_row_stride, *_pixel_stride: Stride info dari Image.Plane
            metadata: dict dengan 'iso', 'exposure_time', 'awb_gains', dll
        """
        if not self.running:
            return

        # Package YUV data untuk queue
        yuv_package = {
            "y": y_data,
            "u": u_data,
            "v": v_data,
            "y_row_stride": y_row_stride or self.width,
            "y_pixel_stride": y_pixel_stride,
            "u_row_stride": u_row_stride or (self.width // 2),
            "u_pixel_stride": u_pixel_stride,
            "v_row_stride": v_row_stride or (self.width // 2),
            "v_pixel_stride": v_pixel_stride,
        }

        self.input_queue.offer(yuv_package, timestamp_ns, frame_number, metadata)

    def submit_raw(
        self,
        raw_data,
        timestamp_ns=0,
        frame_number=0,
        bayer_pattern="rggb",
        metadata=None,
    ):
        """
        Submit RAW Bayer frame dari Camera2.

        Args:
            raw_data: RAW sensor data numpy array (H, W) uint16
            bayer_pattern: 'rggb', 'bggr', 'grbg', 'gbrg'
            metadata: dict dengan Camera2 metadata
        """
        if not self.running:
            return

        raw_package = {
            "raw": raw_data,
            "bayer_pattern": bayer_pattern,
        }

        self.input_queue.offer(raw_package, timestamp_ns, frame_number, metadata)

    def get_latest_output(self):
        """
        Ambil frame terbaru yang sudah di-process.
        Non-blocking, return None jika tidak ada.

        Returns:
            numpy array (H, W, 3) float32 [0, 1] atau None
        """
        slot = self.output_queue.poll_latest()
        if slot is None:
            return None
        return slot.field

    def get_latest_output_uint8(self):
        """Ambil frame terbaru sebagai uint8 [0, 255]."""
        output = self.get_latest_output()
        if output is None:
            return None
        if isinstance(output, np.ndarray):
            return np.clip(output * 255.0, 0, 255).astype(np.uint8)
        # GPU field
        np_out = output.to_numpy()
        return np.clip(np_out * 255.0, 0, 255).astype(np.uint8)

    @property
    def fps(self):
        """Measured FPS dari processing."""
        if not self._fps_history:
            return 0.0
        return sum(self._fps_history) / len(self._fps_history)

    @property
    def total_frames(self):
        return self._total_frames

    @property
    def dropped_frames(self):
        return self.input_queue.dropped_frames

    @property
    def stage_times(self):
        """Latency per stage dalam ms."""
        times = {}
        for stage in self.stages:
            times[stage.name] = stage.last_time_ms
        return times

    def _processing_loop(self):
        """Main processing loop - runs di dedicated thread."""
        while self.running:
            # Poll input queue
            slot = self.input_queue.poll_latest()

            if slot is None:
                # Tidak ada frame, sleep sebentar
                time.sleep(0.001)
                continue

            # Adaptive frame control
            if not self.frame_ctrl.should_process():
                self._total_dropped += 1
                continue

            start_ns = time.perf_counter_ns()
            metadata = slot.metadata or {}

            try:
                result = self._process_frame(slot.field, metadata)
            except Exception as e:
                print(f"[CameraPipeline] Processing error: {e}")
                continue

            end_ns = time.perf_counter_ns()
            elapsed_ms = (end_ns - start_ns) / 1_000_000
            self._last_total_ms = elapsed_ms
            self._total_frames += 1

            # Record untuk adaptive control
            self.frame_ctrl.record_processing(start_ns, end_ns)

            # Calculate FPS
            if elapsed_ms > 0:
                instant_fps = 1000.0 / elapsed_ms
                self._fps_history.append(instant_fps)
                if len(self._fps_history) > 30:
                    self._fps_history.pop(0)

            # Output
            self.output_queue.offer(
                result, slot.timestamp_ns, slot.frame_number, metadata
            )

    @ti_thread
    def _process_frame(self, frame_data, metadata):
        """
        Process single frame melalui seluruh pipeline.
        Stay di GPU sebisa mungkin (zero-copy).
        """
        context = {
            "iso": metadata.get("iso", 100),
            "exposure_time": metadata.get("exposure_time", 0),
            "awb_gains": metadata.get("awb_gains", (1.0, 1.0, 1.0)),
        }

        # Stage 1: YUV → RGB (atau RAW → RGB)
        if "raw" in frame_data:
            from ..demosaicing.Hamilton_demosaice import hamilton_demosaic

            rgb_field = hamilton_demosaic(frame_data["raw"])
        else:
            rgb_field = yuv420_to_rgb(
                frame_data["y"],
                frame_data["u"],
                frame_data["v"],
                self.height,
                self.width,
                frame_data["y_row_stride"],
                frame_data["y_pixel_stride"],
                frame_data["u_row_stride"],
                frame_data["u_pixel_stride"],
                frame_data["v_row_stride"],
                frame_data["v_pixel_stride"],
            )

        # Chain stages di GPU (zero-copy)
        current = rgb_field
        for stage in self.stages:
            if stage.enabled:
                current = stage.process(current, context)

        # Download dari GPU ke NumPy (single download di akhir)
        if hasattr(current, "to_numpy"):
            result = current.to_numpy()
        else:
            result = current

        # Cleanup intermediate GPU buffers
        if rgb_field is not current and hasattr(rgb_field, "to_numpy"):
            common.release_temp_buffer(rgb_field)

        return result


# =========================================================================
# Native AOT Camera2 Orchestrator
# =========================================================================


class AOTCameraPipeline:
    """Camera2 pipeline backed by the portable native AOT camera graphs.

    Queueing, adaptive frame dropping, timestamps, and worker lifecycle are
    shared with the legacy pipeline.  The frame conversion and optional
    unsharp stage use ``taichi_vision.taichi_aot`` and return NumPy frames at
    the display boundary.  This keeps the ownership rule explicit: the
    legacy ``FrameBufferPool`` is never used for native AOT buffers.
    """

    def __init__(
        self,
        width=1920,
        height=1080,
        target_fps=30.0,
        enable_sharpen=False,
        sharpen_amount=0.5,
        bilinear_chroma=True,
    ):
        self.width = int(width)
        self.height = int(height)
        self.running = False
        self.enable_sharpen = bool(enable_sharpen)
        self.sharpen_amount = float(sharpen_amount)
        self.bilinear_chroma = bool(bilinear_chroma)
        self.input_queue = LatestFrameQueue()
        self.output_queue = LatestFrameQueue()
        self.frame_ctrl = AdaptiveFrameController(target_fps=float(target_fps))
        self._thread = None
        self._total_frames = 0
        self._total_dropped = 0
        self._last_total_ms = 0.0
        self._fps_history = []
        self._last_error = None
        # CUDA/OpenGL contexts are thread-affine in the native bridge.  Keep
        # those dispatches on the caller thread by default; CPU can safely
        # use the background worker.  Vulkan is kept synchronous as well so
        # one pipeline has the same ownership rule on every desktop GPU.
        selected_arch = os.environ.get("AOT_ARCH", "auto").lower()
        if selected_arch == "auto":
            try:
                from ...taichi_aot.engine import get_backend_name

                selected_arch = str(get_backend_name()).lower()
            except Exception:
                selected_arch = "cpu"
        self._synchronous_dispatch = selected_arch in {
            "cuda",
            "vulkan",
            "opengl",
            "gles",
        }

    def start(self):
        if self.running:
            return
        self.running = True
        if self._synchronous_dispatch:
            return
        self._thread = threading.Thread(
            target=self._processing_loop,
            name="AOTCameraPipeline",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def submit_yuv(
        self,
        y_data,
        u_data,
        v_data,
        timestamp_ns=0,
        frame_number=0,
        y_row_stride=None,
        y_pixel_stride=1,
        u_row_stride=None,
        u_pixel_stride=1,
        v_row_stride=None,
        v_pixel_stride=1,
        metadata=None,
    ):
        if not self.running:
            return
        package = {
            "y": y_data,
            "u": u_data,
            "v": v_data,
            "y_row_stride": self.width if y_row_stride is None else int(y_row_stride),
            "y_pixel_stride": int(y_pixel_stride),
            "u_row_stride": (
                self.width // 2 if u_row_stride is None else int(u_row_stride)
            ),
            "u_pixel_stride": int(u_pixel_stride),
            "v_row_stride": (
                self.width // 2 if v_row_stride is None else int(v_row_stride)
            ),
            "v_pixel_stride": int(v_pixel_stride),
        }
        self.input_queue.offer(package, timestamp_ns, frame_number, metadata)
        if self._synchronous_dispatch:
            slot = self.input_queue.poll_latest()
            if slot is not None:
                self._process_slot(slot)

    def get_latest_output(self):
        slot = self.output_queue.poll_latest()
        return None if slot is None else slot.field

    def get_latest_output_uint8(self):
        output = self.get_latest_output()
        if output is None:
            return None
        return np.clip(np.asarray(output) * 255.0, 0.0, 255.0).astype(np.uint8)

    @property
    def fps(self):
        return 0.0 if not self._fps_history else float(np.mean(self._fps_history))

    @property
    def total_frames(self):
        return self._total_frames

    @property
    def dropped_frames(self):
        return self.input_queue.dropped_frames + self._total_dropped

    @property
    def last_error(self):
        return self._last_error

    @property
    def last_time_ms(self):
        return self._last_total_ms

    def _processing_loop(self):
        while self.running:
            slot = self.input_queue.poll_latest()
            if slot is None:
                time.sleep(0.001)
                continue
            self._process_slot(slot)

    def _process_slot(self, slot):
        if not self.frame_ctrl.should_process():
            self._total_dropped += 1
            return
        start_ns = time.perf_counter_ns()
        try:
            result = self._process_frame(slot.field)
            self._last_error = None
        except Exception as exc:
            self._last_error = repr(exc)
            return
        end_ns = time.perf_counter_ns()
        elapsed_ms = (end_ns - start_ns) / 1_000_000.0
        self._last_total_ms = elapsed_ms
        self._total_frames += 1
        self.frame_ctrl.record_processing(start_ns, end_ns)
        if elapsed_ms > 0:
            self._fps_history.append(1000.0 / elapsed_ms)
            del self._fps_history[:-30]
        self.output_queue.offer(
            result, slot.timestamp_ns, slot.frame_number, slot.metadata
        )

    def _process_frame(self, frame_data):
        from ... import taichi_aot as aot

        rgb = aot.camera_yuv420_aot(
            frame_data["y"],
            frame_data["u"],
            frame_data["v"],
            self.height,
            self.width,
            y_row_stride=frame_data["y_row_stride"],
            y_pixel_stride=frame_data["y_pixel_stride"],
            u_row_stride=frame_data["u_row_stride"],
            u_pixel_stride=frame_data["u_pixel_stride"],
            v_row_stride=frame_data["v_row_stride"],
            v_pixel_stride=frame_data["v_pixel_stride"],
            bilinear_chroma=self.bilinear_chroma,
        )
        if self.enable_sharpen:
            blurred = aot.gaussian_blur(rgb, sigma=1.0, kernel_size=3)
            rgb = aot.camera_unsharp_aot(rgb, blurred, amount=self.sharpen_amount)
        return np.ascontiguousarray(np.clip(rgb, 0.0, 1.0), dtype=np.float32)


# =========================================================================
# Convenience Functions
# =========================================================================


def create_preview_pipeline(width=1280, height=720, target_fps=30):
    """
    Pipeline ringan untuk camera preview.
    Denoise ringan, tanpa sharpen, untuk FPS maksimal.
    """
    return CameraPipeline(
        width=width,
        height=height,
        target_fps=target_fps,
        enable_denoise=True,
        enable_color_enhance=True,
        enable_sharpen=False,
        clahe_clip=1.5,
        clahe_grid=8,
    )


def create_capture_pipeline(width=4000, height=3000):
    """
    Pipeline berat untuk photo capture.
    Denoise kuat, CLAHE, sharpen, untuk kualitas maksimal.
    """
    return CameraPipeline(
        width=width,
        height=height,
        target_fps=10,
        enable_denoise=True,
        enable_color_enhance=True,
        enable_sharpen=True,
        clahe_clip=3.0,
        clahe_grid=16,
        sharpen_amount=0.8,
    )


def create_low_light_pipeline(width=1920, height=1080):
    """
    Pipeline untuk kondisi low-light.
    Denoise agresif, tanpa sharpen (noise amplification).
    """
    return CameraPipeline(
        width=width,
        height=height,
        target_fps=24,
        enable_denoise=True,
        enable_color_enhance=True,
        enable_sharpen=False,
        clahe_clip=2.5,
        clahe_grid=8,
    )
