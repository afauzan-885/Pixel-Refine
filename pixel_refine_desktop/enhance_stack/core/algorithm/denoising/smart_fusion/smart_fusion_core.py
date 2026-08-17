import os
import gc
import cv2
import numpy as np
import onnxruntime as ort
import psutil
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    estimate_noise_in_python,
    normalize_image,
    to_gamma_proxy,
)


def get_ram_usage():
    """Returns the current RAM usage of the process in MiB."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024


class SmartFusionProcessor:
    """Handles the AI-based Smart Fusion merging logic using ONNX models."""

    def __init__(self, model_dir="database/Learning_Model/nanoburst"):
        self.model_dir = model_dir
        self.sess_a = None
        self.sess_f = None
        self.current_tile_size = None

    def _get_sessions(self, tile_size, preferred_device="gpu"):
        """Loads or returns cached ONNX inference sessions for the given tile size."""
        if self.sess_a is not None and self.current_tile_size == tile_size:
            return self.sess_a, self.sess_f

        # Priority mapping
        device_map = {
            "gpu": [
                "CUDAExecutionProvider",
                "DmlExecutionProvider",
                "CPUExecutionProvider",
            ],
            "dml": ["DmlExecutionProvider", "CPUExecutionProvider"],
            "cpu": ["CPUExecutionProvider"],
        }
        providers = device_map.get(preferred_device, device_map["gpu"])

        # Format model paths
        fmt = "fp16_gpu" if preferred_device in ["gpu", "dml"] else "fp32_cpu"
        a_path = os.path.join(self.model_dir, f"smart_analysis_{tile_size}_{fmt}.onnx")
        f_path = os.path.join(self.model_dir, f"smart_fusion_{tile_size}_{fmt}.onnx")

        # Fallback to float32 if float16 missing
        if not os.path.exists(a_path):
            a_path = os.path.join(
                self.model_dir, f"smart_analysis_{tile_size}_fp32_cpu.onnx"
            )
            f_path = os.path.join(
                self.model_dir, f"smart_fusion_{tile_size}_fp32_cpu.onnx"
            )
            providers = ["CPUExecutionProvider"]

        if not os.path.exists(a_path) or not os.path.exists(f_path):
            raise FileNotFoundError(
                f"Smart Merging models not found for tile {tile_size}"
            )

        self.sess_a = ort.InferenceSession(a_path, providers=providers)
        self.sess_f = ort.InferenceSession(f_path, providers=providers)
        self.current_tile_size = tile_size
        return self.sess_a, self.sess_f

    def release_sessions(self):
        """Releases the ONNX sessions and clears cache."""
        self.sess_a = None
        self.sess_f = None
        self.current_tile_size = None
        gc.collect()

    def process(
        self,
        images,
        reference_image_float,
        update_progress,
        stop_requested,
        tile_size,
        overlap,
        pass_merge_range=(0, 100),
        preferred_device="gpu",
        enable_alignment=True,
        work_res_h=None,
        work_res_w=None,
        ref_dtype=None,
        is_linear_mode=False,
        proxy_scale=1.0,
        num_workers=-1,
        noise_alpha=1.8,
        **unused_kwargs,
    ):
        """Executes the Smart Fusion algorithm on a batch of images."""
        print(f"[RAM] Startup SmartFusionProcessor: {get_ram_usage():.2f} MB")
        num_images = len(images)
        h_orig, w_orig, _ = reference_image_float.shape
        tile_h, tile_w = map(int, tile_size)

        # 1. ALIGNMENT
        if enable_alignment and num_images > 1:
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
                perform_image_alignment,
            )

            p_align_start = int(pass_merge_range[0])
            p_align_end = int(
                pass_merge_range[0] + (pass_merge_range[1] - pass_merge_range[0]) * 0.3
            )
            f_merge_range = (p_align_end, pass_merge_range[1])

            if update_progress:
                update_progress(p_align_start, "Smart Fusion: Aligning frames (CPU)...")

            align_ref_input = reference_image_float
            if is_linear_mode:
                align_ref_input = to_gamma_proxy(
                    reference_image_float, scale=proxy_scale
                )

            alignment_success = perform_image_alignment(
                images,
                align_ref_input,
                work_res_h if work_res_h else h_orig,
                work_res_w if work_res_w else w_orig,
                8,
                8,
                ref_dtype if ref_dtype else images[0].dtype,
                update_progress,
                stop_requested,
                num_alignment_workers=num_workers,
                progress_start=p_align_start,
                progress_end=p_align_end,
                is_linear_mode=is_linear_mode,
                proxy_scale=proxy_scale,
            )
            if not alignment_success and stop_requested and stop_requested():
                return None, None, 0

            pass_merge_range = f_merge_range

        # 2. Initialize Sessions
        try:
            sess_a, sess_f = self._get_sessions(tile_h, preferred_device)
        except Exception as e:
            print(f"[Smart Fusion] Error loading sessions: {e}")
            return None, None, 0

        # 3. Noise Estimation
        noise_aware_enable = unused_kwargs.get(
            "similarity_smart_noise_aware_enable", True
        )
        if noise_aware_enable:
            gray_image = cv2.cvtColor(
                (reference_image_float * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY
            )
            sigma_val = estimate_noise_in_python(gray_image.astype(np.float32) / 255.0)
        else:
            sigma_val = 0.0
            print("[Smart Fusion] Noise Awareness disabled: sigma forced to 0.0")

        sigma_input = np.array([[[[sigma_val]]]], dtype=np.float32)
        alpha_input = np.array([[[[noise_alpha]]]], dtype=np.float32)
        if noise_aware_enable:
            print(f"[Smart Fusion] Sigma: {sigma_val:.5f}")

        # 4. Tiling & Buffers
        overlap_factor = overlap if overlap is not None else 0.1
        stride_h = max(1, int(tile_h * (1 - overlap_factor)))
        stride_w = max(1, int(tile_w * (1 - overlap_factor)))

        def generate_coords(full_size, tile_size, stride):
            if full_size <= tile_size:
                return [0]
            coords = list(range(0, full_size - tile_size, stride))
            if coords[-1] + tile_size < full_size:
                coords.append(full_size - tile_size)
            return sorted(list(set(coords)))

        y_coords = generate_coords(h_orig, tile_h, stride_h)
        x_coords = generate_coords(w_orig, tile_w, stride_w)

        # Padding minimal jika gambar lebih kecil dari tile
        pad_h = max(0, tile_h - h_orig)
        pad_w = max(0, tile_w - w_orig)

        ref_padded = reference_image_float
        if pad_h > 0 or pad_w > 0:
            ref_padded = np.pad(
                reference_image_float, ((0, pad_h), (0, pad_w), (0, 0)), mode="reflect"
            )

        h_padded, w_padded = ref_padded.shape[:2]

        # 5. Row-Batching Optimized Processing
        num_rows = len(y_coords)
        num_cols = len(x_coords)
        batch_size = 25

        accum_final_img = np.zeros_like(ref_padded, dtype=np.float32)
        accum_final_weight = np.zeros((h_padded, w_padded), dtype=np.float32)

        win_y = np.hanning(tile_h + 2)[1:-1].astype(np.float32)
        win_x = np.hanning(tile_w + 2)[1:-1].astype(np.float32)
        win_2d = np.outer(win_y, win_x).astype(np.float32)

        input_names_f = [i.name for i in sess_f.get_inputs()]

        for iy, y_start in enumerate(y_coords):
            if stop_requested and stop_requested():
                return None, None, 0

            # Progress update per row for better UX
            if update_progress:
                prog = pass_merge_range[0] + (iy / num_rows) * (
                    pass_merge_range[1] - pass_merge_range[0]
                )
                update_progress(
                    int(prog), f"Smart Fusion: Processing Row {iy+1}/{num_rows}..."
                )

            for ix_idx in range(0, num_cols, batch_size):
                batch_x = x_coords[ix_idx : ix_idx + batch_size]
                actual_b_size = len(batch_x)

                # 1. Prepare Reference Batch for these 10 X-coords
                ref_patches = np.stack(
                    [
                        ref_padded[y_start : y_start + tile_h, x : x + tile_w]
                        for x in batch_x
                    ]
                )
                ref_nchw = ref_patches.transpose(0, 3, 1, 2).astype(np.float32)
                ref_feats = sess_a.run(None, {"x": ref_nchw})[0]

                # Local Accumulators for these 10 tiles (Correct Quality Logic)
                # sum(I*W) and sum(W)
                tile_sum = ref_patches.copy().astype(
                    np.float32
                )  # Init with Ref (Weight 1.0)
                tile_weight = np.ones((actual_b_size, tile_h, tile_w), dtype=np.float32)

                # 2. Iterate through other frames for this horizontal batch
                sigma_b = np.repeat(sigma_input, actual_b_size, axis=0)
                alpha_b = np.repeat(alpha_input, actual_b_size, axis=0)

                for f_idx in range(1, num_images):
                    curr_frame = images[f_idx]
                    if curr_frame is None:
                        continue

                    # Extract Frame Batch
                    curr_patches_list = []
                    for x in batch_x:
                        p = curr_frame[
                            y_start : min(y_start + tile_h, h_orig),
                            x : min(x + tile_w, w_orig),
                        ]
                        if p.shape[0] < tile_h or p.shape[1] < tile_w:
                            p = np.pad(
                                p,
                                (
                                    (0, tile_h - p.shape[0]),
                                    (0, tile_w - p.shape[1]),
                                    (0, 0),
                                ),
                                mode="reflect",
                            )
                        curr_patches_list.append(p)

                    curr_batch = np.stack(curr_patches_list)
                    curr_batch_norm = normalize_image(
                        curr_batch, curr_frame.dtype
                    ).astype(np.float32)
                    curr_nchw = curr_batch_norm.transpose(0, 3, 1, 2)

                    curr_feats = sess_a.run(None, {"x": curr_nchw})[0]

                    input_feed = {"ref_feat": ref_feats, "curr_feat": curr_feats}
                    if "sigma" in input_names_f:
                        input_feed["sigma"] = sigma_b
                    if "alpha" in input_names_f:
                        input_feed["alpha"] = alpha_b

                    w_batch = sess_f.run(None, input_feed)[0]
                    w_2d_batch = w_batch.reshape(actual_b_size, tile_h, tile_w)

                    # Accumulate Locally (Per-Tile Weighting)
                    tile_sum += curr_batch_norm * w_2d_batch[..., np.newaxis]
                    tile_weight += w_2d_batch

                # 3. Finalize these 10 tiles and Splat to Global Buffer
                # Blended = sum(I*W) / sum(W)
                # Then Result = Blended * HanningWindow
                for i, x in enumerate(batch_x):
                    blended = tile_sum[i] / (tile_weight[i][..., np.newaxis] + 1e-8)

                    accum_final_img[y_start : y_start + tile_h, x : x + tile_w] += (
                        blended * win_2d[..., np.newaxis]
                    )
                    accum_final_weight[
                        y_start : y_start + tile_h, x : x + tile_w
                    ] += win_2d

                del ref_patches, ref_nchw, ref_feats, tile_sum, tile_weight
                gc.collect()

        # 6. Final Outputs
        # Kita mengembalikan akumulasi mentah dan weight map agar pipeline similarity
        # dapat melakukan normalisasi akhir secara global. Ini mencegah normalisasi ganda.
        if h_orig != h_padded or w_orig != w_padded:
            accum_final_img = accum_final_img[:h_orig, :w_orig]
            accum_final_weight = accum_final_weight[:h_orig, :w_orig]

        return accum_final_img, accum_final_weight, num_images
