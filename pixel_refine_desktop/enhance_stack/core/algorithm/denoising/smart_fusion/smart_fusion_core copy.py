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
        """Release ONNX sessions and free memory."""
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
        print(f"[RAM] Startup SmartFusionProcessor: {get_ram_usage():.2f} MB", flush=True)
        num_images = len(images)
        h_orig, w_orig, _ = reference_image_float.shape
        tile_h, tile_w = map(int, tile_size)

        # 1. Initialize Sessions (Fusion & Alignment)
        try:
            print("[DEBUG] Memuat sesi AI Smart Fusion (sess_a, sess_f)...", flush=True)
            sess_a, sess_f = self._get_sessions(tile_h, preferred_device)
            print("[DEBUG] Sesi AI berhasil dimuat.", flush=True)
            
            # Persistent Alignment session
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.smart_flow import (
                SmartFlowProcessor,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
                perform_image_alignment,
            )
            align_processor = SmartFlowProcessor()
            print("[DEBUG] Sesi AI Smart Flow (Alignment) berhasil dimuat.", flush=True)
            
        except Exception as e:
            print(f"[Smart Fusion] Error loading sessions: {e}", flush=True)
            return None, None, 0

        # 2. [PROXY SYSTEM] Noise Estimation & Setup
        print("[DEBUG] Memulai estimasi noise...", flush=True)
        if is_linear_mode:
            ref_proxy_full = to_gamma_proxy(reference_image_float, scale=proxy_scale)
            gray_image = cv2.cvtColor((ref_proxy_full * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray_image = cv2.cvtColor((reference_image_float * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            
        sigma_val = estimate_noise_in_python(gray_image.astype(np.float32) / 255.0)
        sigma_input = np.array([[[[sigma_val]]]], dtype=np.float32)
        print(f"[DEBUG] Estimasi noise selesai. Sigma: {sigma_val}", flush=True)

        # 3. [OPTIMIZATION] 50% Analysis Resolution / Tiling Setup
        # AI works on 512x512 tiles, each representing a 1024x1024 area of the original image
        analysis_scale = 2.0
        work_tile_h = int(tile_h * analysis_scale)
        work_tile_w = int(tile_w * analysis_scale)

        pad_h = (work_tile_h - h_orig % work_tile_h) % work_tile_h
        pad_w = (work_tile_w - w_orig % work_tile_w) % work_tile_w

        ref_padded = reference_image_float
        if pad_h > 0 or pad_w > 0:
            ref_padded = np.pad(reference_image_float, ((0, pad_h), (0, pad_w), (0, 0)), mode="reflect")
        
        h_padded, w_padded = ref_padded.shape[:2]
        y_coords_full = list(range(0, h_padded, work_tile_h))
        x_coords_full = list(range(0, w_padded, work_tile_w))
        print(f"[DEBUG] Tiling Grid: {len(y_coords_full)} x {len(x_coords_full)} tiles.", flush=True)

        # 4. PRE-CALCULATE REFERENCE FEATURES (One-time)
        print("[DEBUG] Menyiapkan Low-Res Proxy & Fitur Referensi...", flush=True)
        h_low, w_low = h_orig // 2, w_orig // 2
        if is_linear_mode:
            ref_proxy_low = cv2.resize(ref_proxy_full, (w_low, h_low), interpolation=cv2.INTER_AREA)
            del ref_proxy_full
        else:
            ref_proxy_low = cv2.resize(reference_image_float, (w_low, h_low), interpolation=cv2.INTER_AREA)
        
        pad_h_low = (tile_h - h_low % tile_h) % tile_h
        pad_w_low = (tile_w - w_low % tile_w) % tile_w
        ref_proxy_p_low = np.pad(ref_proxy_low, ((0, pad_h_low), (0, pad_w_low), (0, 0)), mode="reflect")
        ref_low_nchw = ref_proxy_p_low.transpose(2, 0, 1)[np.newaxis, ...].astype(np.float32)
        del ref_proxy_low
        
        # Dictionary to store ref features per tile position (y_start_low, x_start_low)
        ref_features_cache = {}
        for y_start_full in y_coords_full:
            y_start_low = y_start_full // 2
            for x_start_full in x_coords_full:
                x_start_low = x_start_full // 2
                ref_patch_low = ref_low_nchw[:, :, y_start_low : y_start_low + tile_h, x_start_low : x_start_low + tile_w]
                feat = sess_a.run(None, {"x": ref_patch_low})[0]
                ref_features_cache[(y_start_low, x_start_low)] = feat
        
        del ref_low_nchw
        gc.collect()
        print("[DEBUG] Fitur Referensi berhasil disimpan.", flush=True)

        # 5. INITIALIZE ACCUMULATORS
        print("[DEBUG] Inisialisasi Accumulator Global...", flush=True)
        accum_final_img = np.zeros_like(ref_padded, dtype=np.float32)
        accum_final_weight = np.zeros((h_padded, w_padded), dtype=np.float32)
        
        # Start with reference image as first frame (Weight 1.0)
        accum_final_img += ref_padded
        accum_final_weight += 1.0
        print("[DEBUG] Gambar referensi berhasil ditambahkan ke accumulator.", flush=True)

        # 6. INCREMENTAL FRAME LOOP (O(1) Memory Architecture)
        p_start, p_end = pass_merge_range
        total_frames_to_blend = num_images - 1
        
        align_ref_input = reference_image_float
        if is_linear_mode:
            align_ref_input = to_gamma_proxy(reference_image_float, scale=proxy_scale)

        for f_idx in range(1, num_images):
            if stop_requested and stop_requested(): break
            
            f_prog_start = p_start + ((f_idx - 1) / total_frames_to_blend) * (p_end - p_start)
            f_prog_end = p_start + (f_idx / total_frames_to_blend) * (p_end - p_start)
            
            if update_progress:
                update_progress(int(f_prog_start), f"Fusing Frame {f_idx}/{total_frames_to_blend}...")
            
            print(f"\n[DEBUG] --- PROCESSING FRAME {f_idx}/{total_frames_to_blend} ---", flush=True)
            
            # a. Alignment (Incremental - Single Frame)
            # Create a shallow list with just [ref, current_frame]
            single_frame_list = [images[0], images[f_idx]]
            
            alignment_success = perform_image_alignment(
                single_frame_list,
                align_ref_input,
                work_res_h if work_res_h else h_orig,
                work_res_w if work_res_w else w_orig,
                320, 320,
                ref_dtype if ref_dtype else images[0].dtype,
                update_progress=None, # Silent for inner loop
                stop_requested=stop_requested,
                optical_flow_type="smart_flow",
                smart_flow_processor=align_processor, # PASS PERSISTENT PROCESSOR
                index_offset=f_idx - 1,
                is_linear_mode=is_linear_mode,
                proxy_scale=proxy_scale,
            )
            
            if not alignment_success:
                print(f"  [WARNING] Alignment frame {f_idx} gagal. Melewati frame.", flush=True)
                images[f_idx] = None
                continue
            
            # The warped frame is now in single_frame_list[1]
            warped_frame = single_frame_list[1]
            
            # b. Blend Frame Row-by-Row
            h_f = warped_frame.shape[0]
            for iy, y_start_full in enumerate(y_coords_full):
                y_end_full = y_start_full + work_tile_h
                y_s_f, y_e_f = min(y_start_full, h_f), min(y_start_full + work_tile_h, h_f)
                
                # Extract Strip
                strip_raw = warped_frame[y_s_f:y_e_f, :, :]
                if strip_raw.dtype == np.uint16:
                    strip_f32 = strip_raw.astype(np.float32) / 65535.0
                else:
                    strip_f32 = normalize_image(strip_raw, strip_raw.dtype)
                
                # Padding strip
                p_v = work_tile_h - strip_f32.shape[0]
                p_h = w_padded - strip_f32.shape[1]
                strip_p = np.pad(strip_f32, ((0, p_v), (0, p_h), (0, 0)), mode="reflect")
                
                # Proxy for AI Analysis (Low-Res)
                if is_linear_mode:
                    strip_proxy = to_gamma_proxy(strip_p, scale=proxy_scale)
                else:
                    strip_proxy = strip_p

                strip_low = cv2.resize(strip_proxy, (w_padded // 2, tile_h), interpolation=cv2.INTER_AREA)
                if is_linear_mode: del strip_proxy
                
                strip_low_nchw = strip_low.transpose(2, 0, 1)[np.newaxis, ...].astype(np.float32)
                del strip_low
                
                # Tiling Blend Loop
                y_start_low = y_start_full // 2
                for ix, x_start_full in enumerate(x_coords_full):
                    x_start_low = x_start_full // 2
                    
                    # AI Analysis
                    feat_curr = sess_a.run(
                        None, {"x": strip_low_nchw[:, :, :, x_start_low : x_start_low + tile_w]}
                    )[0]
                    w_patch = sess_f.run(
                        None,
                        {
                            "ref_feat": ref_features_cache[(y_start_low, x_start_low)],
                            "curr_feat": feat_curr,
                            "sigma": sigma_input,
                        },
                    )[0]
                    
                    # Decode weights
                    w_2d = np.squeeze(np.array(w_patch)).astype(np.float32)
                    if w_2d.ndim > 2: w_2d = w_2d[..., 0]
                    w_full = cv2.resize(w_2d, (work_tile_w, work_tile_h), interpolation=cv2.INTER_LINEAR)

                    # ACCUMULATE into global buffer
                    accum_final_img[y_start_full:y_end_full, x_start_full : x_start_full + work_tile_w] += (
                        strip_p[:, x_start_full : x_start_full + work_tile_w] * w_full[:, :, np.newaxis]
                    )
                    accum_final_weight[y_start_full:y_end_full, x_start_full : x_start_full + work_tile_w] += w_full
                
                del strip_p, strip_low_nchw
            
            # c. Explicit DEALLOCATION
            print(f"  [DEBUG] Frame {f_idx} selesai digabung. Membersihkan RAM...", flush=True)
            del warped_frame
            images[f_idx] = None # FREE the original frame in the list
            gc.collect()

        # 7. Cleanupsessions
        print("[DEBUG] Melepas sesi AI Alignment & Fusion...", flush=True)
        align_processor.release_sessions()
        
        # 8. FINAL NORMALIZATION
        valid_mask = accum_final_weight > 1e-8
        final_img = np.zeros_like(accum_final_img)
        np.divide(
            accum_final_img,
            accum_final_weight[:, :, np.newaxis],
            out=final_img,
            where=valid_mask[:, :, np.newaxis],
        )
        final_img[~valid_mask] = ref_padded[~valid_mask]

        if h_orig != h_padded or w_orig != w_padded:
            final_img = final_img[:h_orig, :w_orig]
            accum_final_weight = accum_final_weight[:h_orig, :w_orig]

        print(f"✅ Incremental Smart Fusion Selesai. Penggunaan RAM: {get_ram_usage():.2f} MB", flush=True)
        return final_img, accum_final_weight, num_images
