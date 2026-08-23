"""
Frame Manager - Taichi GPU
==========================
Buffer pool dan frame queue untuk Camera2 real-time pipeline.
Mengelola lifecycle buffer GPU (Taichi ndarray) untuk zero-allocation hot path.

Menggunakan BufferCache dari common.py sebagai backend pool.
Menambah frame queue logic: latest-frame-only, triple buffering, adaptive drop.
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
except ImportError:
    pass


class FrameSlot:
    """Single frame buffer slot - pre-allocated GPU buffer."""
    
    __slots__ = ['field', 'timestamp_ns', 'frame_number', 'state', 'metadata']
    
    def __init__(self, field, timestamp_ns=0, frame_number=0):
        self.field = field
        self.timestamp_ns = timestamp_ns
        self.frame_number = frame_number
        self.state = 'empty'  # empty, writing, ready, reading, displaying
        self.metadata = {}


class LatestFrameQueue:
    """
    Non-blocking frame queue: hanya simpan frame terbaru.
    
    Strategi: Producer (Camera2 callback) selalu replace frame.
    Consumer (processing thread) ambil latest, skip intermediate.
    Menghasilkan: zero queue buildup, zero lag accumulation.
    """
    
    def __init__(self):
        self._slot = None
        self._lock = threading.Lock()
        self._total_offered = 0
        self._total_consumed = 0
    
    def offer(self, field, timestamp_ns=0, frame_number=0, metadata=None):
        """
        Offer frame ke queue. Jika ada frame lama yang belum di-consume,
        frame lama di-replace (di-drop).
        Non-blocking, aman dari Camera2 callback thread.
        """
        with self._lock:
            old = self._slot
            self._slot = FrameSlot(field, timestamp_ns, frame_number)
            if metadata:
                self._slot.metadata = metadata
            self._slot.state = 'ready'
            self._total_offered += 1
        return old  # Return old slot untuk cleanup
    
    def poll_latest(self):
        """
        Ambil frame terbaru. Return None jika kosong.
        Non-blocking, aman dari processing thread.
        """
        with self._lock:
            if self._slot is None or self._slot.state != 'ready':
                return None
            slot = self._slot
            self._slot = None
            slot.state = 'reading'
            self._total_consumed += 1
            return slot
    
    @property
    def dropped_frames(self):
        """Total frame yang di-drop (offered tapi tidak consumed)."""
        return self._total_offered - self._total_consumed
    
    @property
    def size(self):
        return 1 if self._slot is not None else 0


class TripleBuffer:
    """
    Triple buffer pipeline: overlap capture, processing, dan display.
    
    3 slot:
    - write_slot: sedang diisi oleh producer
    - process_slot: sedang diproses oleh consumer
    - display_slot: siap untuk display
    
    Setiap stage bisa berjalan paralel tanpa blocking.
    """
    
    def __init__(self):
        self.slots = [None, None, None]
        self.write_idx = 0
        self.read_idx = 1
        self.display_idx = 2
        self._lock = threading.Lock()
    
    def acquire_write(self):
        """Ambil slot kosong untuk write. Return slot index."""
        with self._lock:
            return self.write_idx
    
    def commit_write(self, field, timestamp_ns=0, frame_number=0, metadata=None):
        """Commit frame ke write slot, advance pointer."""
        with self._lock:
            slot = FrameSlot(field, timestamp_ns, frame_number)
            if metadata:
                slot.metadata = metadata
            slot.state = 'ready'
            self.slots[self.write_idx] = slot
            # Rotate: write → display, display → read, read → write
            old_write = self.write_idx
            self.write_idx = self.read_idx
            self.read_idx = self.display_idx
            self.display_idx = old_write
    
    def get_display(self):
        """Ambil frame terbaru untuk display."""
        with self._lock:
            slot = self.slots[self.display_idx]
            if slot and slot.state == 'ready':
                slot.state = 'displaying'
                return slot
            return None
    
    def get_processing(self):
        """Ambil frame untuk processing."""
        with self._lock:
            slot = self.slots[self.read_idx]
            if slot and slot.state == 'ready':
                slot.state = 'reading'
                return slot
            return None
    
    def release(self, slot_idx):
        """Release slot kembali ke pool."""
        with self._lock:
            if self.slots[slot_idx]:
                self.slots[slot_idx].state = 'empty'


class AdaptiveFrameController:
    """
    Adaptive frame rate controller.
    
    Dynamically adjust capture rate berdasarkan processing capacity.
    Jika processing lambat → skip frame, bukan queue buildup (lag).
    """
    
    def __init__(self, target_fps=30.0, window_size=30):
        self.target_fps = target_fps
        self.window_size = window_size
        self._processing_times = []
        self._frame_counter = 0
        self._skip_ratio = 0
    
    def should_process(self):
        """Decision: should we process this frame or skip?"""
        self._frame_counter += 1
        
        # Always process first N frames (bootstrap)
        if self._frame_counter < 10:
            return True
        
        if not self._processing_times:
            return True
        
        target_ms = 1000.0 / self.target_fps
        avg_ms = sum(self._processing_times) / len(self._processing_times)
        
        if avg_ms < target_ms * 0.7:
            self._skip_ratio = 0
            return True
        elif avg_ms < target_ms * 0.95:
            self._skip_ratio = 0
            return True
        elif avg_ms < target_ms * 1.5:
            self._skip_ratio = 1
            return self._frame_counter % 2 == 0
        else:
            self._skip_ratio = max(1, int(avg_ms / target_ms))
            return self._frame_counter % (self._skip_ratio + 1) == 0
    
    def record_processing(self, start_time_ns, end_time_ns):
        """Record processing time untuk adaptive decisions."""
        elapsed_ms = (end_time_ns - start_time_ns) / 1_000_000
        self._processing_times.append(elapsed_ms)
        if len(self._processing_times) > self.window_size:
            self._processing_times.pop(0)
    
    @property
    def avg_processing_ms(self):
        if not self._processing_times:
            return 0.0
        return sum(self._processing_times) / len(self._processing_times)
    
    @property
    def measured_fps(self):
        if not self._processing_times or self.avg_processing_ms < 0.001:
            return 0.0
        return 1000.0 / self.avg_processing_ms


class FrameBufferPool:
    """
    Pre-allocated GPU buffer pool untuk Camera2 pipeline.
    Menggunakan common.BufferCache sebagai backend.
    
    Pre-allocate buffers untuk resolusi yang sering digunakan.
    Eliminasi allocation overhead di hot path.
    """
    
    def __init__(self, default_h=1080, default_w=1920, channels=3):
        self.default_h = default_h
        self.default_w = default_w
        self.channels = channels
        self._preallocated = False
    
    @ti_thread
    def preallocate(self, count=4):
        """Pre-allocate GPU buffers untuk pipeline stages."""
        if not TAICHI_AVAILABLE or self._preallocated:
            return
        
        h, w, c = self.default_h, self.default_w, self.channels
        
        # Pre-allocate common shapes
        shapes = [
            (h, w, c),       # RGB buffer
            (h, w),           # Grayscale buffer
            (h, w, 2),        # Flow buffer (dx, dy)
        ]
        
        for shape in shapes:
            for _ in range(count):
                buf = common.get_temp_buffer(shape, ti.f32, buffer_provider="pool")
                common.release_temp_buffer(buf)
        
        self._preallocated = True
    
    @ti_thread
    def get_rgb_buffer(self, h=None, w=None):
        """Ambil RGB buffer dari pool."""
        if not TAICHI_AVAILABLE:
            return None
        h = h or self.default_h
        w = w or self.default_w
        return common.get_temp_buffer((h, w, 3), ti.f32, buffer_provider="pool")
    
    @ti_thread
    def get_gray_buffer(self, h=None, w=None):
        """Ambil grayscale buffer dari pool."""
        if not TAICHI_AVAILABLE:
            return None
        h = h or self.default_h
        w = w or self.default_w
        return common.get_temp_buffer((h, w), ti.f32, buffer_provider="pool")
    
    @ti_thread
    def get_flow_buffer(self, h=None, w=None):
        """Ambil flow buffer dari pool."""
        if not TAICHI_AVAILABLE:
            return None
        h = h or self.default_h
        w = w or self.default_w
        return common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")
    
    @ti_thread
    def release_buffer(self, buf):
        """Return buffer ke pool."""
        if buf is not None and TAICHI_AVAILABLE:
            common.release_temp_buffer(buf)
    
    def clear(self):
        """Clear semua pre-allocated buffers."""
        if TAICHI_AVAILABLE:
            common.cleanup_cache()
        self._preallocated = False


class AOTFrameBufferPool:
    """Small explicit pool for buffers owned by the native AOT engine.

    ``FrameBufferPool`` above is intentionally kept as the JIT/common pool
    used by the legacy :class:`CameraPipeline`.  AOT buffers have a different
    owner and lifecycle, so they are not mixed with ``common.BufferCache``.
    This class is useful to callers building a zero-copy AOT display path;
    the NumPy-returning ``AOTCameraPipeline`` does not require it.
    """

    def __init__(self, default_h=1080, default_w=1920, channels=3):
        self.default_h = int(default_h)
        self.default_w = int(default_w)
        self.channels = int(channels)
        self._free = {}
        self._lock = threading.Lock()

    @staticmethod
    def _key(shape):
        return tuple(int(value) for value in shape)

    @staticmethod
    def _allocate(shape):
        from ...taichi_aot.engine import OutputArray

        return OutputArray(tuple(shape), dtype=np.float32, is_vector=False)

    def preallocate(self, count=4):
        count = max(0, int(count))
        shapes = [
            (self.default_h, self.default_w, self.channels),
            (self.default_h, self.default_w),
            (self.default_h, self.default_w, 2),
        ]
        with self._lock:
            for shape in shapes:
                bucket = self._free.setdefault(self._key(shape), [])
                for _ in range(count):
                    bucket.append(self._allocate(shape))

    def _get(self, shape):
        key = self._key(shape)
        with self._lock:
            bucket = self._free.setdefault(key, [])
            if bucket:
                return bucket.pop()
        return self._allocate(key)

    def get_rgb_buffer(self, h=None, w=None):
        return self._get((h or self.default_h, w or self.default_w, self.channels))

    def get_gray_buffer(self, h=None, w=None):
        return self._get((h or self.default_h, w or self.default_w))

    def get_flow_buffer(self, h=None, w=None):
        return self._get((h or self.default_h, w or self.default_w, 2))

    def release_buffer(self, buffer):
        if buffer is None:
            return
        with self._lock:
            self._free.setdefault(self._key(buffer.shape), []).append(buffer)

    def clear(self):
        with self._lock:
            buffers = [buffer for bucket in self._free.values() for buffer in bucket]
            self._free.clear()
        for buffer in buffers:
            buffer.destroy()
