# splat_sr_runtime.py - Production runtime for splattingSR
# Uses pre-compiled .tcm modules via the C++ AOT engine.
# NO Taichi dependency — safe to import in production without Taichi installed.

import os
import numpy as np


# Compiled graph K values (must match splat_sr.py compile output)
COMPILED_KS = [2, 3, 4, 5, 8]


class SplatSRAOTEngine:
    """
    Production runtime for GPU-accelerated splattingSR.

    AOT solver with the stable iterative solver API:
        solver = SplatSRAOTEngine(lr_shape, hr_shape, num_frames, scale=2)
        solver.set_lr_data(lr_np, weight_maps_np, shifts_np)
        solver.set_initial_hr(hr_np)
        for i in range(120):
            solver.step(lam=0.001)
        result = solver.get_hr_image()
    """

    def __init__(self, lr_shape, hr_shape, num_frames, scale=2,
                 alpha=0.7, beta=0.01, btv_window=2):
        from taichi_vision.taichi_aot import get_engine
        import ctypes

        self.scale = scale
        self.lr_h, self.lr_w = lr_shape
        self.hr_h, self.hr_w = hr_shape
        self.num_frames = num_frames
        self.alpha = alpha
        self.beta = beta
        self.btv_window = btv_window

        # Select graph K: smallest compiled K >= num_frames
        self._graph_k = next(
            (k for k in COMPILED_KS if k >= num_frames),
            COMPILED_KS[-1]
        )

        # Initialize engine and load TCM
        self._engine = get_engine()
        tcm_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../../../ui/data/aot_assets"
        )
        tcm_path = os.path.join(tcm_dir, "splat_sr_vulkan.tcm")
        self._mod = self._engine.load(tcm_path)

        # Allocate persistent GPU buffers
        self._hr_image = self._engine.allocate(
            (self.hr_h, self.hr_w), dtype=np.float32
        )
        self._hr_grad = self._engine.allocate(
            (self.hr_h, self.hr_w), dtype=np.float32
        )
        self._temp_hr = self._engine.allocate(
            (self.hr_h, self.hr_w), dtype=np.float32
        )
        # sim_lr and lr_error sized to graph_k (may be > num_frames)
        self._sim_lr = self._engine.allocate(
            (self._graph_k, self.lr_h, self.lr_w), dtype=np.float32
        )
        self._lr_error = self._engine.allocate(
            (self._graph_k, self.lr_h, self.lr_w), dtype=np.float32
        )

        # Upload buffers (set in set_lr_data / set_initial_hr)
        self._lr_frames = None
        self._weight_maps = None
        self._shifts = None

        # Prepare k-index arguments for the graph
        # Extra frames (if graph_k > num_frames) point to frame 0
        # Their contribution is zero because padded lr_frames/weight_maps are zero
        self._k_args = {}
        for i in range(self._graph_k):
            self._k_args[f"k_{i}"] = min(i, num_frames - 1)

        self._ctypes = ctypes

    def set_lr_data(self, lr_np, weight_maps_np, shifts_np):
        """Upload LR frames, weight maps, and shifts to GPU.
        Pads to graph_k frames if needed (zero padding)."""
        lr_np = np.ascontiguousarray(lr_np, dtype=np.float32)
        weight_maps_np = np.ascontiguousarray(weight_maps_np, dtype=np.float32)
        shifts_np = np.ascontiguousarray(shifts_np, dtype=np.float32)

        # Pad to graph_k if needed
        if self._graph_k > self.num_frames:
            pad_k = self._graph_k - self.num_frames
            lr_np = np.pad(lr_np, ((0, pad_k), (0, 0), (0, 0)),
                           mode='constant', constant_values=0)
            weight_maps_np = np.pad(weight_maps_np, ((0, pad_k), (0, 0), (0, 0)),
                                    mode='constant', constant_values=0)
            shifts_np = np.pad(shifts_np, ((0, pad_k), (0, 0)),
                               mode='constant', constant_values=0)

        # Destroy previous buffers if they exist
        for buf in (self._lr_frames, self._weight_maps, self._shifts):
            if buf is not None:
                try:
                    buf.destroy()
                except Exception:
                    pass

        self._lr_frames = self._engine.upload(lr_np)
        self._weight_maps = self._engine.upload(weight_maps_np)
        self._shifts = self._engine.upload(shifts_np)

    def set_initial_hr(self, hr_np):
        """Upload initial HR estimate to GPU."""
        hr_np = np.ascontiguousarray(hr_np, dtype=np.float32)

        # Destroy previous buffer if it was uploaded separately
        # (hr_image is pre-allocated, so we write into it via upload which
        # creates a new buffer — we need to replace the reference)
        old_hr = self._hr_image
        self._hr_image = self._engine.upload(hr_np)
        try:
            old_hr.destroy()
        except Exception:
            pass

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = float(value)

    def step(self, lam):
        """Execute one SR iteration (simulate → error → backproject → BTV → update).
        All kernels dispatched as a single GPU command buffer."""
        self._mod.run(
            f"sr_step_K{self._graph_k}",
            hr_image=self._hr_image,
            hr_grad=self._hr_grad,
            temp_hr=self._temp_hr,
            lr_frames=self._lr_frames,
            sim_lr=self._sim_lr,
            lr_error=self._lr_error,
            weight_maps=self._weight_maps,
            shifts=self._shifts,
            scale=int(self.scale),
            lam=float(lam),
            beta=float(self.beta),
            alpha=float(self.alpha),
            btv_window=int(self.btv_window),
            **self._k_args,
        )
        self._engine.sync()

    def get_hr_image(self):
        """Download the current HR image from GPU to numpy array."""
        return self._hr_image.to_numpy()

    def __del__(self):
        """Clean up GPU buffers."""
        bufs = [
            self._hr_image, self._hr_grad, self._temp_hr,
            self._sim_lr, self._lr_error,
            self._lr_frames, self._weight_maps, self._shifts,
        ]
        for buf in bufs:
            if buf is not None:
                try:
                    buf.destroy()
                except Exception:
                    pass
