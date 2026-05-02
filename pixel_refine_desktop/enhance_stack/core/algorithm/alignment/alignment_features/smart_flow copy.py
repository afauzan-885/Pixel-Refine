import sys
import os
import subprocess
import gc
import cv2
import numpy as np
import onnxruntime as ort
from concurrent.futures import ThreadPoolExecutor

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    normalize_image,
)


class SmartFlowProcessor:
    """
    Handles memory-efficient optical flow alignment using NanoFlowNet.
    Uses tiling (320x320) and Overlap-Add (OLA) with warping per tile.
    """

    def __init__(self, model_dir="database/Learning_Model/nanoflow"):
        self.model_dir = model_dir
        self.session = None
        self.tile_size = 320
        self.batch_ready = False
        self.optimal_batch_size = 1
        self._cached_win = None
        self._cached_win_size = (0, 0)

    def _initialize_session(self, target_device="gpu"):
        """Loads the NanoFlowNet ONNX model for 320x320 tiles."""
        if self.session is not None:
            return True

        model_name = "nanoflow_fp32_256_cpu.onnx"
        if target_device in ["gpu", "dml"]:
            # Try to load fp16 version if requested and available
            model_name = "nanoflow_fp16_512_gpu.onnx"
            providers = [
                "CUDAExecutionProvider",
                "DmlExecutionProvider",
                "CPUExecutionProvider",
            ]
        else:
            providers = ["CPUExecutionProvider"]

        model_path = os.path.join(self.model_dir, model_name)
        if not os.path.exists(model_path):
            # Fallback to fp32 cpu if specific one not found
            model_path = os.path.join(self.model_dir, "nanoflow_fp32_320_cpu.onnx")
            providers = ["CPUExecutionProvider"]

        if not os.path.exists(model_path):
            print(f"[Smart Flow] Error: Model not found at {model_path}")
            return False

        try:
            self.session = ort.InferenceSession(model_path, providers=providers)

            # Auto-detect expected tile size and batch support from model inputs
            input_obj = self.session.get_inputs()[0]
            input_shape = input_obj.shape

            self.batch_ready = True  # Assume dynamic/batch support unless proven static

            if len(input_shape) == 4:
                batch_dim = input_shape[0]
                h, w = input_shape[2], input_shape[3]

                # Check for static batch = 1
                if isinstance(batch_dim, int) and batch_dim == 1:
                    self.batch_ready = False
                    print(
                        "[Smart Flow] Model has static batch=1. Batch processing disabled."
                    )

                if isinstance(h, int) and isinstance(w, int):
                    self.tile_size = h
                    print(
                        f"[Smart Flow] Model detected as static {h}x{w}. Adapting tile_size."
                    )
                else:
                    self.tile_size = 320  # Fallback for dynamic
                    print(
                        f"[Smart Flow] Model detected as dynamic. Using default tile_size: {self.tile_size}"
                    )

            # --- Auto VRAM Implementation ---
            if self.batch_ready:
                vram_mb = self._get_gpu_vram()
                self.optimal_batch_size = self._calculate_optimal_batch_size(vram_mb)
                print(
                    f"[Smart Flow] Detected VRAM: {vram_mb}MB | Optimized Batch: {self.optimal_batch_size}"
                )
            else:
                self.optimal_batch_size = 1

            return True
        except Exception as e:
            print(f"Error loading ONNX model: {e}")
            return False

    def _get_gpu_vram(self):
        """Returns dedicated VRAM in MB using PowerShell (Windows)."""
        try:
            # Menggunakan Get-CimInstance untuk akurasi tinggi di Windows
            cmd = 'powershell "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty AdapterRAM"'
            result = subprocess.check_output(cmd, shell=True).decode().strip().split()
            if not result:
                return 2048  # Fallback safe value

            # Ambil nilai RAM terbesar (biasanya Dedicated GPU)
            max_ram_bytes = max([int(r) for r in result if r.isdigit()])
            return max_ram_bytes // (1024 * 1024)
        except Exception:
            return 2048  # Fallback safe value (2GB)

    def _calculate_optimal_batch_size(self, vram_mb):
        """Calculates batch size based on VRAM capacity."""
        # Safety buffer (Sesuai permintaan user: 150MB)
        # Namun kita tambahkan deteksi jika kartu < 2GB agar tidak crash total
        SAFETY_BUFFER = 150 if vram_mb > 1024 else 100

        # Berdasarkan telemetry user, NanoFlowNet 512x512 butuh ~310MB-320MB per item
        MB_PER_512_TILE = 370

        available_vram = vram_mb - SAFETY_BUFFER
        if available_vram < MB_PER_512_TILE:
            return 1

        optimal = int(available_vram // MB_PER_512_TILE)
        return max(1, min(optimal, 32))  # Cap at 32 to avoid host-side overhead

    def release_sessions(self):
        """Releases the ONNX session to free memory."""
        if self.session is not None:
            self.session = None
            gc.collect()

    def process_image(self, ref_img, curr_img, overlap=0.10, stop_requested=None):
        """
        Aligns curr_img to ref_img using tiled NanoFlowNet.
        Warps per tile and blends using Hanning window (OLA).
        """
        if self.session is None:
            if not self._initialize_session():
                return curr_img

        h_orig, w_orig = ref_img.shape[:2]
        tile_h, tile_w = self.tile_size, self.tile_size

        # 1. Tiling setup (Stride with overlap)
        stride_h = max(1, int(tile_h * (1.0 - overlap)))
        stride_w = max(1, int(tile_w * (1.0 - overlap)))

        pad_h = (
            (stride_h - (h_orig - tile_h) % stride_h) % stride_h
            if h_orig > tile_h
            else tile_h - h_orig
        )
        pad_w = (
            (stride_w - (w_orig - tile_w) % stride_w) % stride_w
            if w_orig > tile_w
            else tile_w - w_orig
        )

        # Pad images
        ref_pad = np.pad(
            ref_img, ((0, pad_h), (0, pad_w), (0, 0)), mode="reflect"
        ).astype(np.float32)

        h_padded, w_padded = ref_pad.shape[:2]
        ch, cw = curr_img.shape[:2]

        # Ensure curr_img doesn't exceed padded dimensions
        if ch > h_padded or cw > w_padded:
            curr_img = curr_img[: min(ch, h_padded), : min(cw, w_padded)]
            ch, cw = curr_img.shape[:2]

        # Calculate specific padding for curr_img so it exactly matches ref_pad shape
        pad_h_curr = h_padded - ch
        pad_w_curr = w_padded - cw

        curr_pad = np.pad(
            curr_img, ((0, pad_h_curr), (0, pad_w_curr), (0, 0)), mode="reflect"
        ).astype(np.float32)

        # [MODIFIED] Smart Normalization: only divide by 255 if images look like uint8 (range > 1.0)
        # NanoFlowNet model ALWAYS expects [0, 1] normalized float32.
        if np.max(ref_pad) > 1.01:
            ref_pad /= 255.0
        if np.max(curr_pad) > 1.01:
            curr_pad /= 255.0

        h_padded, w_padded = ref_pad.shape[:2]
        y_coords = list(range(0, max(1, h_padded - tile_h + 1), stride_h))
        x_coords = list(range(0, max(1, w_padded - tile_w + 1), stride_w))

    def _estimate_global_shift(self, ref, curr):
        """Estimates global translation using Phase Correlation on downsampled gray images."""
        try:
            scale = 0.25

            # Ambil dimensi minimum untuk memastikan parity ukuran sebelum resize
            h1, w1 = ref.shape[:2]
            h2, w2 = curr.shape[:2]
            h_min, w_min = min(h1, h2), min(w1, w2)

            # Use only green channel for speed or convert to gray
            if ref.ndim == 3:
                r_small = cv2.resize(ref[:h_min, :w_min, 1], (0, 0), fx=scale, fy=scale)
                c_small = cv2.resize(
                    curr[:h_min, :w_min, 1], (0, 0), fx=scale, fy=scale
                )
            else:
                r_small = cv2.resize(ref[:h_min, :w_min], (0, 0), fx=scale, fy=scale)
                c_small = cv2.resize(curr[:h_min, :w_min], (0, 0), fx=scale, fy=scale)

            # Phase Correlation (Very fast sub-pixel translation estimator)
            shift, response = cv2.phaseCorrelate(
                r_small.astype(np.float32), c_small.astype(np.float32)
            )
            dx, dy = shift
            return dx / scale, dy / scale
        except Exception as e:
            print(f"[Smart Flow] Global shift failed: {e}")
            return 0.0, 0.0

    def process_image(
        self,
        ref_img,
        curr_img,
        overlap=0.15,
        batch_size=None,
        stop_requested=None,
        return_flow=False,
    ):
        """
        Aligns curr_img to ref_img using Hybrid Global-to-Local strategy.
        1. Coarse: Calculate global translation (dx, dy).
        2. Fine: Calculate local residual flow using Batch Inference on GPU.
        3. Warp: Single global remap for performance and quality.
        """
        if self.session is None:
            if not self._initialize_session():
                return curr_img if not return_flow else None

        # Use calculated optimal batch if none provided or auto (-1)
        if batch_size is None or batch_size <= 0:
            batch_size = self.optimal_batch_size

        h_orig, w_orig = ref_img.shape[:2]
        tile_h, tile_w = self.tile_size, self.tile_size

        # --- STEP 1: Global Pre-Alignment (Disabled for Debugging as requested) ---
        # dx_global, dy_global = self._estimate_global_shift(ref_img, curr_img)
        dx_global, dy_global = 0.0, 0.0
        # print(f"[Smart Flow] Coarse Alignment: dx={dx_global:.2f}, dy={dy_global:.2f}")

        # Tiling setup
        stride_h = max(1, int(tile_h * (1.0 - overlap)))
        stride_w = max(1, int(tile_w * (1.0 - overlap)))

        pad_h = (
            (stride_h - (h_orig - tile_h) % stride_h) % stride_h
            if h_orig > tile_h
            else tile_h - h_orig
        )
        pad_w = (
            (stride_w - (w_orig - tile_w) % stride_w) % stride_w
            if w_orig > tile_w
            else tile_w - w_orig
        )

        ref_pad = np.pad(
            ref_img, ((0, pad_h), (0, pad_w), (0, 0)), mode="reflect"
        ).astype(np.float32)

        h_padded, w_padded = ref_pad.shape[:2]
        pad_h_curr = h_padded - curr_img.shape[0]
        pad_w_curr = w_padded - curr_img.shape[1]

        curr_pad = np.pad(
            curr_img, ((0, pad_h_curr), (0, pad_w_curr), (0, 0)), mode="reflect"
        ).astype(np.float32)

        # Normalization
        if np.max(ref_pad) > 1.01:
            ref_pad /= 255.0
        if np.max(curr_pad) > 1.01:
            curr_pad /= 255.0

        y_coords = list(range(0, max(1, h_padded - tile_h + 1), stride_h))
        x_coords = list(range(0, max(1, w_padded - tile_w + 1), stride_w))

        # Buffers for Overlap-Add
        accum_resid_flow = np.zeros((h_padded, w_padded, 2), dtype=np.float32)
        accum_weight = np.zeros((h_padded, w_padded), dtype=np.float32)

        if self._cached_win_size != (tile_h, tile_w):
            self._cached_win = np.outer(np.hanning(tile_h), np.hanning(tile_w)).astype(
                np.float32
            )
            self._cached_win_size = (tile_h, tile_w)
        win = self._cached_win

        # --- STEP 2: Residual Local Flow (Batch Inference) ---
        tile_positions = []
        for y in y_coords:
            for x in x_coords:
                tile_positions.append((y, x))

        num_tiles = len(tile_positions)
        input_name_ref = self.session.get_inputs()[0].name
        input_name_curr = self.session.get_inputs()[1].name

        # Enforce batch_size=1 if model is static, else use ALL tiles if batch_size=-1
        if not self.batch_ready:
            actual_batch_size = 1
            print("[Smart Flow] Model static. Dipaksa pemrosesan batch=1.")
        elif batch_size <= 0:
            actual_batch_size = num_tiles
            print(
                f"[Smart Flow] GPU Max-Throughput aktif: Mengirim {num_tiles} tile sekaligus."
            )
        else:
            actual_batch_size = batch_size

        for i in range(0, num_tiles, actual_batch_size):
            if stop_requested and stop_requested():
                break

            batch_coords = tile_positions[i : i + actual_batch_size]
            curr_batch_len = len(batch_coords)

            # Prepare batch tensors (Ditingkatkan: pengisian lebih cepat)
            ref_batch = np.empty((curr_batch_len, tile_h, tile_w, 3), dtype=np.float32)
            curr_batch = np.empty((curr_batch_len, tile_h, tile_w, 3), dtype=np.float32)

            for b_idx, (y_s, x_s) in enumerate(batch_coords):
                ref_batch[b_idx] = ref_pad[y_s : y_s + tile_h, x_s : x_s + tile_w]
                curr_batch[b_idx] = curr_pad[y_s : y_s + tile_h, x_s : x_s + tile_w]

            # Transpose HWC -> CHW for the entire batch at once (jauh lebih cepat bagi CPU)
            ref_batch = ref_batch.transpose(0, 3, 1, 2)
            curr_batch = curr_batch.transpose(0, 3, 1, 2)

            # Inference (Pengiriman tunggal ke GPU)
            outputs = self.session.run(
                None, {input_name_ref: ref_batch, input_name_curr: curr_batch}
            )
            batch_flow = outputs[0]  # Shape [Batch, 2, H, W]

            # Accumulate flow (Transpose CHW -> HWC in batch mode)
            batch_flow = batch_flow.transpose(0, 2, 3, 1)  # [Batch, H, W, 2]

            for b_idx, (y_s, x_s) in enumerate(batch_coords):
                local_flow = batch_flow[b_idx]
                accum_resid_flow[y_s : y_s + tile_h, x_s : x_s + tile_w, 0] += (
                    local_flow[..., 0] * win
                )
                accum_resid_flow[y_s : y_s + tile_h, x_s : x_s + tile_w, 1] += (
                    local_flow[..., 1] * win
                )
                accum_weight[y_s : y_s + tile_h, x_s : x_s + tile_w] += win

        # Final Flow Normalization
        mask = accum_weight > 1e-8
        final_flow = np.zeros_like(accum_resid_flow)
        np.divide(
            accum_resid_flow,
            accum_weight[..., np.newaxis],
            out=final_flow,
            where=mask[..., np.newaxis],
        )

        # Add back global translation support
        final_flow[..., 0] += dx_global
        final_flow[..., 1] += dy_global

        if return_flow:
            return final_flow[:h_orig, :w_orig]

        # --- STEP 3: Single Global Warp ---
        y_mesh_global, x_mesh_global = np.mgrid[0:h_padded, 0:w_padded].astype(
            np.float32
        )
        map_x_global = x_mesh_global + final_flow[..., 0]
        map_y_global = y_mesh_global + final_flow[..., 1]

        final_img = cv2.remap(
            curr_pad,
            map_x_global,
            map_y_global,
            interpolation=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REFLECT_101,
        )

        final_img[~mask] = ref_pad[~mask]

        # Crop back to original resolution and rescale to 255 (if needed by caller)
        final_img = final_img[:h_orig, :w_orig]

        # Return as image of the same type as input
        if curr_img.dtype == np.uint8:
            return np.clip(final_img * 255.0, 0, 255).astype(np.uint8)
        else:
            return final_img
