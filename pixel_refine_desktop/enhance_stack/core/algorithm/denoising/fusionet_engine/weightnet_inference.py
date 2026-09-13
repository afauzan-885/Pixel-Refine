"""
WeightNet ONNX Inference Engine.
Handles loading images (Taichi AOT Hamilton demosaic for RAW/DNG, Taichi AOT imread for standard images),
converting burst to NumPy array [1, N, 3, H, W] float32 in [0.0, 1.0],
tiled ONNX inference (512x512 tiles, Hann overlap-add blending),
and full-resolution weighted average fusion.
Returns raw uncompressed float32 RGB array [H, W, 3] in range [0.0, 1.0].
"""

import os
import threading
from pathlib import Path
from typing import Callable, Optional, Sequence

import numpy as np
import cv2
from PIL import Image, ImageOps

DEFAULT_WEIGHTNET_ONNX = Path(
    "database/Learning_Model/weightNet/weightnet_master.bundle"
)

# DirectML feature outputs are device-resident OrtValues.  Keep only a small
# bounded working set on the DML device; uncached reference features remain
# ordinary CPU arrays and are uploaded by ONNX Runtime when needed.
MAX_DML_REFERENCE_CACHE_TILES = max(
    1, int(os.environ.get("PIXEL_REFINE_DML_CACHE_TILES", "2"))
)
RAW_EXTENSIONS = {
    ".dng",
    ".cr2",
    ".cr3",
    ".nef",
    ".arw",
    ".rw2",
    ".orf",
    ".raf",
    ".pef",
    ".srw",
}


def _read_image_orientation(image_path: Path) -> int:
    try:
        with Image.open(image_path) as image:
            exif = image.getexif()
            return int(exif.get(0x0112, 1))
    except Exception:
        return 1


def _apply_orientation(image: np.ndarray, orientation: int) -> np.ndarray:
    if orientation == 2:
        return np.fliplr(image)
    if orientation == 3:
        return np.rot90(image, 2)
    if orientation == 4:
        return np.flipud(image)
    if orientation == 5:
        return np.fliplr(np.rot90(image, -1))
    if orientation == 6:
        return np.rot90(image, -1)
    if orientation == 7:
        return np.fliplr(np.rot90(image, 1))
    if orientation == 8:
        return np.rot90(image, 1)
    return image


def load_rgb_linear_image(path: str | Path, is_raw: bool = False) -> np.ndarray:
    """
    Loads an image in pure linear [0.0, 1.0] RGB float32.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    from taichi_vision import taichi_aot

    if is_raw or path.suffix.lower() in RAW_EXTENSIONS:
        try:
            demosaiced = taichi_aot.demosaic(
                str(path),
                method="hamilton",
                return_gpu=False,
            )
            img_np = np.asarray(demosaiced, dtype=np.float32)
        except Exception as exc:
            import rawpy

            with rawpy.imread(str(path)) as raw:
                rgb = raw.postprocess(
                    gamma=(1, 1),
                    no_auto_bright=True,
                    output_bps=16,
                    use_camera_wb=True,
                    highlight_mode=rawpy.HighlightMode.Blend,
                )
            img_np = rgb.astype(np.float32) / 65535.0
        if img_np.ndim != 3 or img_np.shape[2] != 3:
            raise ValueError(
                f"Raw decoding failed for {path}, got shape {img_np.shape}"
            )
        max_v = float(np.max(img_np)) if img_np.size > 0 else 1.0
        if max_v > 1.5:
            scale = 65535.0 if max_v > 255.0 else 255.0
            img_np /= scale
        return np.ascontiguousarray(np.clip(img_np, 0.0, 1.0), dtype=np.float32)

    image_bgr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image_bgr is None:
        raise ValueError(f"Failed to read image: {path}")

    orientation = _read_image_orientation(path)
    if orientation != 1:
        image_bgr = _apply_orientation(image_bgr, orientation)

    if image_bgr.ndim == 2:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    del image_bgr

    if np.issubdtype(image_rgb.dtype, np.integer):
        scale = 65535.0 if image_rgb.dtype == np.uint16 else 255.0
        return np.ascontiguousarray(
            image_rgb.astype(np.float32) / scale, dtype=np.float32
        )
    return np.ascontiguousarray(image_rgb.astype(np.float32), dtype=np.float32)


def load_burst_images(paths: Sequence[str | Path]) -> list[np.ndarray]:
    """
    Loads burst images and applies AutoEnhance:
    - Analyzes histogram metrics ONCE on reference frame (paths[0]).
    - Applies AutoEnhance with the derived parameters to reference and all support frames.
    """
    if not paths:
        raise ValueError("Burst is empty.")

    from taichi_vision import taichi_aot

    # 1. Load Reference Frame
    ref_linear = load_rgb_linear_image(paths[0])
    target_h, target_w = ref_linear.shape[:2]

    # 2. Analyze Reference Frame ONCE
    params = taichi_aot.analyze_auto_enhance_params(ref_linear)
    print(
        f"[AutoEnhance Burst] Analyzed ref={Path(paths[0]).name} -> "
        f"gain={params['gain']:.4f}, white={params['white_level']:.4f}, "
        f"shadow={params['shadow_lift']:.4f}, contrast={params['global_contrast']:.2f}"
    )

    # 3. Apply AutoEnhance to Reference Frame
    ref_enhanced = taichi_aot.AutoEnhance(ref_linear, params=params)
    normalized = [np.ascontiguousarray(ref_enhanced, dtype=np.float32)]

    # 4. Apply AutoEnhance to Support Frames
    for source_path in paths[1:]:
        supp_linear = load_rgb_linear_image(source_path)
        supp_enhanced = taichi_aot.AutoEnhance(supp_linear, params=params)

        if supp_enhanced.shape[:2] != (target_h, target_w):
            supp_enhanced = taichi_aot.resize(
                supp_enhanced,
                (target_w, target_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )

        normalized.append(np.ascontiguousarray(supp_enhanced, dtype=np.float32))

    return normalized


def normalize_burst_frames(
    frames: Sequence[np.ndarray],
    is_raw: bool = False,
) -> list[np.ndarray]:
    """
    Normalizes a list of in-memory image frames (e.g. from FlowNet alignment):
    - Scales integer types (uint8, uint16) to float32 in [0.0, 1.0].
    """
    if not frames:
        raise ValueError("Frames list is empty.")

    target_h, target_w = frames[0].shape[:2]

    def _to_f32(img):
        img_arr = np.asarray(img)
        if np.issubdtype(img_arr.dtype, np.integer):
            scale = 65535.0 if img_arr.dtype.itemsize > 1 else 255.0
            return np.ascontiguousarray(
                img_arr.astype(np.float32) / scale, dtype=np.float32
            )
        elif np.issubdtype(img_arr.dtype, np.floating):
            max_v = float(np.max(img_arr)) if img_arr.size > 0 else 1.0
            if max_v > 1.5:
                scale = 65535.0 if max_v > 255.0 else 255.0
                return np.ascontiguousarray(
                    img_arr.astype(np.float32) / scale, dtype=np.float32
                )
            return np.ascontiguousarray(
                img_arr.astype(np.float32, copy=False), dtype=np.float32
            )
        return np.ascontiguousarray(img_arr.astype(np.float32), dtype=np.float32)

    normalized = []
    for f in frames:
        f32 = _to_f32(f)
        if f32.shape[:2] != (target_h, target_w):
            from taichi_vision import taichi_aot

            f32 = taichi_aot.resize(
                f32,
                (target_w, target_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )
        normalized.append(np.ascontiguousarray(f32, dtype=np.float32))

    return normalized


def burst_images_to_array(images: Sequence[np.ndarray]) -> np.ndarray:
    if not images:
        raise ValueError("Cannot convert an empty burst to an array.")
    stacked = np.stack(images, axis=0)  # [N, H, W, 3]
    array = np.transpose(stacked, (0, 3, 1, 2))[np.newaxis, ...]  # [1, N, 3, H, W]
    return np.ascontiguousarray(array, dtype=np.float32)


class DecoupledWeightNetSession:
    """Encapsulates paired Encoder and Attention ONNX sessions with native resident VRAM/RAM cached reference features."""

    def __init__(
        self,
        encoder_session,
        attention_session,
        patch_size: int,
        runtime: str = "cpu",
    ):
        self.encoder_session = encoder_session
        self.attention_session = attention_session
        self.patch_size = patch_size
        self.runtime = str(runtime).lower().strip()
        self._cached_ref_hash = None
        self._cached_tiles = None
        self._is_vram_cached = False

    def get_providers(self):
        return self.attention_session.get_providers()

    def clear_cache(self):
        """Release cached reference features from VRAM and RAM cleanly."""
        self._cached_ref_hash = None
        self._cached_tiles = None
        self._is_vram_cached = False


def load_weightnet_onnx(
    model_path: str | Path,
    runtime: str = "auto",
    patch_size: int = 512,
):
    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError("ONNX inference requires the onnxruntime package.") from exc

    model_path = Path(model_path)
    runtime = str(runtime).strip().lower()
    available = set(ort.get_available_providers())
    if runtime == "auto":
        runtime = "dml" if "DmlExecutionProvider" in available else "cpu"
    if runtime == "dml":
        if "DmlExecutionProvider" not in available:
            raise RuntimeError(
                "DML runtime requested but DmlExecutionProvider is unavailable; "
                f"available={sorted(available)}"
            )
        providers = ["DmlExecutionProvider", "CPUExecutionProvider"]
    elif runtime == "cpu":
        providers = ["CPUExecutionProvider"]
    else:
        raise ValueError(
            f"Unsupported ONNX runtime {runtime!r}; choose auto, dml, or cpu."
        )

    options = ort.SessionOptions()
    # Disable node fusion completely on DML to eliminate DmlFusedNode crashes across long bursts
    options.graph_optimization_level = (
        ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        if runtime == "dml"
        else ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    )
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.enable_mem_pattern = runtime == "cpu"
    options.add_session_config_entry(
        "session.use_device_allocator_for_initializers", "1"
    )

    dev_suffix = "gpu" if runtime == "dml" else "cpu"
    dev_upper = dev_suffix.upper()

    search_dirs = [
        model_path.parent if model_path.is_file() else model_path,
        Path("database/Learning_Model/nanoFlow"),
        Path("database/Learning_Model/weightNet"),
        Path("pixel_refine_desktop/ui/data/models"),
        Path(f"database/Learning_Model/weightNet/{dev_upper}"),
        Path(f"database/Learning_Model/nanoFlow/{dev_upper}"),
    ]

    # 0. Check for Unified Model Archive Bundle (Zero-Disk In-Memory Streaming)
    bundle_names = [
        "weightnet_master.bundle",
        "weightnet_v3_master.bundle",
    ]
    bundle_file = None
    if model_path.is_file() and model_path.suffix.lower() == ".bundle":
        bundle_file = model_path
    else:
        for d in search_dirs:
            for bn in bundle_names:
                bp = d / bn
                if bp.is_file():
                    bundle_file = bp
                    break
            if bundle_file:
                break

    if bundle_file:
        try:
            import zipfile
            with zipfile.ZipFile(bundle_file, "r") as zf:
                candidate_names = [
                    f"weightnet_{patch_size}_{dev_suffix}_3c_fp32.onnx",
                    f"weightnet_{patch_size}_{dev_suffix}_1c_fp32.onnx",
                    f"weightnet_{patch_size}_{dev_suffix}_fp32.onnx",
                ]
                namelist = set(zf.namelist())
                target_model = None
                for cname in candidate_names:
                    if cname in namelist:
                        target_model = cname
                        break
                if target_model:
                    model_bytes = zf.read(target_model)
                    session = ort.InferenceSession(
                        model_bytes, sess_options=options, providers=providers
                    )
                    print(
                        f"[WeightNet ONNX Bundle] runtime={runtime} bundle={bundle_file.name} "
                        f"model={target_model} providers={session.get_providers()} patch={patch_size}"
                    )
                    return session
        except Exception as e:
            print(f"[WeightNet ONNX Bundle Warning] Failed loading from {bundle_file}: {e}")

    # 1. Try to find Decoupled Model Pair first (Encoder + Attention)
    enc_names = [
        f"weightnet_encoder_{patch_size}_{dev_suffix}_fp32.onnx",
        f"encoder_{patch_size}_{dev_suffix}.onnx",
        f"nano_burst_encoder_{patch_size}_ort_opt.onnx",
        f"nano_burst_encoder_{patch_size}.onnx",
    ]
    att_names = [
        f"weightnet_attention_{patch_size}_{dev_suffix}_fp32.onnx",
        f"attention_{patch_size}_{dev_suffix}.onnx",
        f"nano_burst_attention_{patch_size}_b1_ort_opt.onnx",
        f"nano_burst_attention_{patch_size}_b1.onnx",
    ]

    enc_file, att_file = None, None
    for d in search_dirs:
        for en in enc_names:
            p = d / en
            if p.is_file():
                enc_file = p
                break
        for an in att_names:
            p = d / an
            if p.is_file():
                att_file = p
                break
        if enc_file and att_file:
            break

    if enc_file and att_file:
        enc_sess = ort.InferenceSession(
            str(enc_file), sess_options=options, providers=providers
        )
        att_sess = ort.InferenceSession(
            str(att_file), sess_options=options, providers=providers
        )
        print(
            f"[WeightNet ONNX Decoupled] runtime={runtime} patch={patch_size} "
            f"encoder={enc_file.name} attention={att_file.name}"
        )
        return DecoupledWeightNetSession(
            enc_sess, att_sess, patch_size, runtime=runtime
        )

    # 2. Fallback to Coupled Model if decoupled pair is not found
    coupled_names = [
        f"weightnet_{patch_size}_{dev_suffix}_fp32.onnx",
        f"weightnet_{patch_size}_{dev_suffix}.onnx",
        model_path.name,
    ]
    found_coupled = None
    for d in search_dirs:
        for cn in coupled_names:
            p = d / cn
            if p.is_file():
                found_coupled = p
                break
        if found_coupled:
            break

    if not found_coupled:
        raise FileNotFoundError(
            f"WeightNet ONNX not found for patch {patch_size} in {search_dirs}"
        )

    session = ort.InferenceSession(
        str(found_coupled), sess_options=options, providers=providers
    )

    print(
        f"[WeightNet ONNX Coupled] runtime={runtime} model={found_coupled.name} "
        f"providers={session.get_providers()} patch={patch_size}"
    )
    return session


def infer_single_support_weight_map(
    session,
    ref_work: np.ndarray,
    supp_work: np.ndarray,
    *,
    tile_size: int = 512,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    stop_event: Optional[threading.Event] = None,
    progress: Optional[Callable[[int, str], None]] = None,
) -> tuple[np.ndarray, float]:
    """
    Computes 3-channel fusion weight map for a single (ref, support) pair at work resolution
    using Hybrid Luma-Anchor AI Inference + Vectorized Chroma Modulation for maximum speed and color fidelity.
    Inputs: ref_work [3, work_h, work_w], supp_work [3, work_h, work_w]
    Output: weight_map_work [3, work_h, work_w], mean_alpha
    """
    channels, work_h, work_w = ref_work.shape
    is_decoupled = isinstance(session, DecoupledWeightNetSession)

    if is_decoupled:
        tile_size = session.patch_size
    else:
        try:
            model_in_shape = session.get_inputs()[0].shape
            if (
                len(model_in_shape) >= 4
                and isinstance(model_in_shape[2], int)
                and model_in_shape[2] > 0
            ):
                tile_size = int(model_in_shape[2])
        except Exception:
            pass

    # Check if model accepts native 3-channel RGB input [1, 3, H, W]
    is_rgb_model = False
    try:
        active_sess = session.encoder_session if is_decoupled else session
        in_shape = active_sess.get_inputs()[0].shape
        if len(in_shape) >= 2 and in_shape[1] == 3:
            is_rgb_model = True
    except Exception:
        is_rgb_model = False

    # 1. Compute Luma (Y) for fallback 1-channel models
    ref_luma = (0.299 * ref_work[0] + 0.587 * ref_work[1] + 0.114 * ref_work[2]).astype(
        np.float32
    )
    supp_luma = (
        0.299 * supp_work[0] + 0.587 * supp_work[1] + 0.114 * supp_work[2]
    ).astype(np.float32)

    overlap_size = int(tile_size * float(overlap))
    stride = max(1, tile_size - overlap_size)
    hann_1d = np.hanning(tile_size).astype(np.float32)
    window_2d = np.outer(hann_1d, hann_1d).reshape(1, 1, tile_size, tile_size)

    # 1. Collect all tile coordinates
    tile_coords = []
    for y in range(0, work_h, stride):
        for x in range(0, work_w, stride):
            y_end, x_end = min(y + tile_size, work_h), min(x + tile_size, work_w)
            y_start, x_start = max(0, y_end - tile_size), max(0, x_end - tile_size)
            tile_coords.append((y_start, y_end, x_start, x_end))

    total_tiles = len(tile_coords)
    if total_tiles == 0:
        return np.ones((3, work_h, work_w), dtype=np.float32), 1.0

    # 2. Extract and cache reference features once per burst (Native VRAM on DirectML, RAM on CPU)
    if is_decoupled:
        ref_id = id(ref_work)
        if session._cached_ref_hash != ref_id:
            cached_tiles = []
            is_dml = getattr(session, "runtime", "") == "dml"
            use_vram = is_dml
            for y_start, y_end, x_start, x_end in tile_coords:
                cur_h, cur_w = y_end - y_start, x_end - x_start
                if is_rgb_model:
                    r_in = np.zeros((1, 3, tile_size, tile_size), dtype=np.float32)
                    r_in[0, :, :cur_h, :cur_w] = ref_work[
                        :, y_start:y_end, x_start:x_end
                    ]
                else:
                    r_in = np.zeros((1, 1, tile_size, tile_size), dtype=np.float32)
                    r_in[0, 0, :cur_h, :cur_w] = ref_luma[y_start:y_end, x_start:x_end]
                feat_obj = None
                att_io = None
                # Limit persistent DirectML feature/output bindings to three
                # tiles.  Keeping every tile resident can consume most of the
                # MX150's 2 GB heap before the Taichi alignment buffers run.
                tile_use_vram = use_vram and (
                    len(cached_tiles) < MAX_DML_REFERENCE_CACHE_TILES
                )
                if tile_use_vram:
                    try:
                        enc_io = session.encoder_session.io_binding()
                        enc_io.bind_cpu_input("ref_img", r_in)
                        enc_io.bind_output("ref_feat", device_type="dml", device_id=0)
                        session.encoder_session.run_with_iobinding(enc_io)
                        feat_obj = enc_io.get_outputs()[0]

                        # Pre-create and bind persistent reference features and outputs once per burst
                        att_io = session.attention_session.io_binding()
                        att_io.bind_ortvalue_input("ref_feat", feat_obj)
                        att_io.bind_cpu_input("ref_img", r_in)
                        att_io.bind_output("weight_map")
                        att_io.bind_output("alpha")
                    except Exception:
                        use_vram = False
                        feat_obj = None
                        att_io = None
                if feat_obj is None:
                    try:
                        feat_np = session.encoder_session.run(
                            ["ref_feat"],
                            {"ref_img": r_in},
                        )[0]
                    except Exception:
                        out_shape = session.encoder_session.get_outputs()[0].shape
                        fb = (
                            out_shape[0]
                            if len(out_shape) > 0 and isinstance(out_shape[0], int)
                            else (3 if is_rgb_model else 1)
                        )
                        fc = (
                            out_shape[1]
                            if len(out_shape) > 1 and isinstance(out_shape[1], int)
                            else 16
                        )
                        fh = (
                            out_shape[2]
                            if len(out_shape) > 2 and isinstance(out_shape[2], int)
                            else tile_size
                        )
                        fw = (
                            out_shape[3]
                            if len(out_shape) > 3 and isinstance(out_shape[3], int)
                            else tile_size
                        )
                        feat_np = np.zeros((fb, fc, fh, fw), dtype=np.float32)
                    feat_obj = feat_np
                cached_tiles.append((r_in, feat_obj, att_io))
            session._cached_ref_hash = ref_id
            session._cached_tiles = cached_tiles
            session._is_vram_cached = any(
                item[2] is not None for item in cached_tiles
            )

    # 3. High-throughput single-tile ONNX inference matching model
    # Color-Neutral Design: Always accumulate a unified 1-channel weight map (mean of R, G, B)
    # to eliminate chromatic fringing (bercak merah/biru) on moving objects, then broadcast to [3, H, W].
    weight_map_accum = np.zeros((1, work_h, work_w), dtype=np.float32)
    weight_stitch_work = np.zeros((1, 1, work_h, work_w), dtype=np.float32)
    alpha_total = 0.0

    ref_in = np.zeros(
        (1, 3 if is_rgb_model else 1, tile_size, tile_size), dtype=np.float32
    )
    supp_in = np.zeros(
        (1, 3 if is_rgb_model else 1, tile_size, tile_size), dtype=np.float32
    )

    for i, (y_start, y_end, x_start, x_end) in enumerate(tile_coords):
        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Inference cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Inference cancelled.")
        cur_h, cur_w = y_end - y_start, x_end - x_start
        cur_win = window_2d[:, :, :cur_h, :cur_w]

        if is_rgb_model:
            supp_in[0, :, :cur_h, :cur_w] = supp_work[:, y_start:y_end, x_start:x_end]
        else:
            supp_in[0, 0, :cur_h, :cur_w] = supp_luma[y_start:y_end, x_start:x_end]

        if is_decoupled:
            cached_item = session._cached_tiles[i]
            ref_in_tile = cached_item[0]
            ref_feat_obj = cached_item[1]
            tile_att_io = cached_item[2] if len(cached_item) > 2 else None

            weight_np, alpha_np = None, None

            if tile_att_io is not None:
                try:
                    tile_att_io.bind_cpu_input("support_img", supp_in)
                    session.attention_session.run_with_iobinding(tile_att_io)
                    outs = tile_att_io.get_outputs()
                    weight_np = outs[0].numpy()
                    alpha_np = outs[1].numpy()
                except Exception:
                    weight_np, alpha_np = None, None

            if weight_np is None:
                try:
                    feat_np = (
                        ref_feat_obj.numpy()
                        if hasattr(ref_feat_obj, "numpy")
                        else ref_feat_obj
                    )
                    weight_np, alpha_np = session.attention_session.run(
                        ["weight_map", "alpha"],
                        {
                            "ref_feat": feat_np,
                            "ref_img": ref_in_tile,
                            "support_img": supp_in,
                        },
                    )
                except Exception:
                    pass

            if weight_np is not None:
                raw_w = np.asarray(weight_np, dtype=np.float32)
                if raw_w.shape[1] == 3:
                    weight_tile = np.mean(raw_w[0, :, :cur_h, :cur_w], axis=0, keepdims=True)
                else:
                    weight_tile = raw_w[0, 0:1, :cur_h, :cur_w]
                alpha_values = np.asarray(alpha_np, dtype=np.float32)
                if np.isfinite(alpha_values).all():
                    alpha_total += float(alpha_values.mean())
            else:
                if is_rgb_model:
                    diff = np.mean(
                        np.abs(
                            ref_in_tile[0, :, :cur_h, :cur_w]
                            - supp_in[0, :, :cur_h, :cur_w]
                        ),
                        axis=0,
                        keepdims=True,
                    )
                else:
                    diff = np.abs(
                        ref_in_tile[0, 0:1, :cur_h, :cur_w]
                        - supp_in[0, 0:1, :cur_h, :cur_w]
                    )
                weight_tile = np.clip(1.0 - diff * 3.0, 0.0, 1.0)
                alpha_total += 0.5
        else:
            if is_rgb_model:
                ref_in[0, :, :cur_h, :cur_w] = ref_work[:, y_start:y_end, x_start:x_end]
            else:
                ref_in[0, 0, :cur_h, :cur_w] = ref_luma[y_start:y_end, x_start:x_end]
            try:
                weight_np, alpha_np = session.run(
                    ["weight_map", "alpha"],
                    {"ref_img": ref_in, "support_img": supp_in},
                )
                raw_w = np.asarray(weight_np, dtype=np.float32)
                if raw_w.shape[1] == 3:
                    # Color-neutral merge: average across 3 channels to eliminate chromatic fringing
                    weight_tile = np.mean(raw_w[0, :, :cur_h, :cur_w], axis=0, keepdims=True)
                else:
                    weight_tile = raw_w[0, 0:1, :cur_h, :cur_w]
                alpha_values = np.asarray(alpha_np, dtype=np.float32)
                if np.isfinite(alpha_values).all():
                    alpha_total += float(alpha_values.mean())
            except Exception:
                if is_rgb_model:
                    diff = np.mean(
                        np.abs(
                            ref_in[0, :, :cur_h, :cur_w] - supp_in[0, :, :cur_h, :cur_w]
                        ),
                        axis=0,
                        keepdims=True,
                    )
                else:
                    diff = np.abs(
                        ref_in[0, 0:1, :cur_h, :cur_w] - supp_in[0, 0:1, :cur_h, :cur_w]
                    )
                weight_tile = np.clip(1.0 - diff * 3.0, 0.0, 1.0)
                alpha_total += 0.5

        weight_map_accum[:, y_start:y_end, x_start:x_end] += weight_tile * cur_win[0]
        weight_stitch_work[:, :, y_start:y_end, x_start:x_end] += cur_win

    alpha_total = alpha_total / max(1, total_tiles)

    weight_map_norm = np.clip(
        weight_map_accum / (weight_stitch_work[0] + 1e-8), 0.0, 1.0
    )

    # Apply ghost penalty & cutoff
    if ghost_penalty != 1.0:
        weight_map_norm = np.power(weight_map_norm, float(ghost_penalty))

    if ghost_cutoff > 0.0:
        weight_map_norm = np.clip(
            (weight_map_norm - float(ghost_cutoff)) / (1.0 - float(ghost_cutoff)),
            0.0,
            1.0,
        )

    # Pure AI Weight Map: Direct broadcast of color-neutral unified weight map to 3 channels [3, H, W]
    weight_map_work = np.repeat(weight_map_norm, 3, axis=0).astype(np.float32)

    mean_alpha = alpha_total / max(1, total_tiles)
    return weight_map_work, mean_alpha


def fuse_support_frame_inplace(
    sum_img: np.ndarray,
    weight_sum: np.ndarray,
    supp_full_chw: np.ndarray,
    weight_map_work: np.ndarray,
    full_h: int,
    full_w: int,
):
    """
    Upsamples single-support weight map to full resolution and blends in-place into sum_img and weight_sum.
    All inputs and outputs are [3, full_h, full_w] float32 arrays.
    """
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
        taichi_bridge,
    )

    channels, work_h, work_w = weight_map_work.shape
    if (work_h, work_w) != (full_h, full_w):
        for c in range(channels):
            w_full_c = taichi_aot.resize(
                weight_map_work[c],
                (full_w, full_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )
            sum_img[c] += supp_full_chw[c] * w_full_c
            weight_sum[c] += w_full_c
            del w_full_c
    else:
        sum_img += supp_full_chw * weight_map_work
        weight_sum += weight_map_work


def run_collab_onnx_inference(
    session,
    burst_full: np.ndarray,
    *,
    tile_size: int = 512,
    work_scale: float = 0.50,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.05,
    stop_event: Optional[threading.Event] = None,
    progress: Optional[Callable[[int, str], None]] = None,
) -> tuple[np.ndarray, float]:
    """
    Run core ONNX inference on burst array [1, N, 3, H, W] and return
    uncompressed fused float32 RGB array [H, W, 3] in range [0.0, 1.0].
    """
    from taichi_vision import taichi_aot

    burst_full = np.ascontiguousarray(burst_full, dtype=np.float32)
    _, frame_count, channels, full_h, full_w = burst_full.shape
    if channels != 3 or frame_count < 1:
        raise ValueError("Burst must contain RGB frames and at least one image.")

    work_scale = float(work_scale)
    work_h = max(1, int(full_h * work_scale))
    work_w = max(1, int(full_w * work_scale))

    # Reference work frame
    if (work_h, work_w) != (full_h, full_w):
        ref_hwc = np.transpose(burst_full[0, 0], (1, 2, 0))
        ref_work = np.transpose(
            taichi_aot.resize(
                ref_hwc, (work_w, work_h), interpolation=taichi_aot.INTER_AREA
            ),
            (2, 0, 1),
        )
    else:
        ref_work = burst_full[0, 0]

    sum_img = burst_full[0, 0].copy()
    weight_sum = np.ones((channels, full_h, full_w), dtype=np.float32)
    alpha_total = 0.0

    for idx in range(1, frame_count):
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("Inference cancelled.")

        if (work_h, work_w) != (full_h, full_w):
            supp_hwc = np.transpose(burst_full[0, idx], (1, 2, 0))
            supp_work = np.transpose(
                taichi_aot.resize(
                    supp_hwc, (work_w, work_h), interpolation=taichi_aot.INTER_AREA
                ),
                (2, 0, 1),
            )
        else:
            supp_work = burst_full[0, idx]

        def pair_prog(p_val, p_msg):
            if progress:
                mapped = int(((idx - 1) + p_val / 100.0) / (frame_count - 1) * 100)
                progress(mapped, f"Frame {idx}/{frame_count - 1}: {p_msg}")

        weight_work, alpha_mean = infer_single_support_weight_map(
            session,
            ref_work,
            supp_work,
            tile_size=tile_size,
            overlap=overlap,
            ghost_penalty=ghost_penalty,
            ghost_cutoff=ghost_cutoff,
            stop_event=stop_event,
            progress=pair_prog,
        )
        alpha_total += alpha_mean

        fuse_support_frame_inplace(
            sum_img,
            weight_sum,
            burst_full[0, idx],
            weight_work,
            full_h,
            full_w,
        )
        del weight_work
        if (work_h, work_w) != (full_h, full_w):
            del supp_work

    result = np.clip(sum_img / (weight_sum + 1e-8), 0.0, 1.0)
    del sum_img, weight_sum
    mean_alpha = alpha_total / max(1, frame_count - 1)
    result_hwc = np.transpose(result, (1, 2, 0))
    if progress:
        progress(100, f"Finished ONNX; alpha={mean_alpha:.4f}")
    return result_hwc, mean_alpha


def run_weightnet_inference(
    image_paths: Optional[Sequence[str | Path]] = None,
    frames: Optional[Sequence[np.ndarray]] = None,
    is_raw: Optional[bool] = None,
    model_path: str | Path = DEFAULT_WEIGHTNET_ONNX,
    work_scale: float = 0.50,
    tile_size: int = 512,
    overlap: float = 0.30,
    ghost_penalty: Optional[float] = None,
    ghost_cutoff: Optional[float] = None,
    stop_event: Optional[threading.Event] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> tuple[np.ndarray, float]:
    """
    Self-contained inference engine:
    Accepts list of image paths OR list of in-memory NumPy frames ->
    executes tiled ONNX inference -> returns raw uncompressed float32 RGB array [H, W, 3] and mean alpha.
    """
    if frames is None and image_paths is None:
        raise ValueError("Either image_paths or frames must be provided.")

    if progress_callback:
        progress_callback(5, "Loading FusionNet ONNX model...")
    session = load_weightnet_onnx(model_path, runtime="auto", patch_size=tile_size)

    if is_raw is None:
        if image_paths:
            is_raw = any(Path(p).suffix.lower() in RAW_EXTENSIONS for p in image_paths)
        else:
            is_raw = False

    if ghost_penalty is None:
        ghost_penalty = 1.30 if is_raw else 1.0
    if ghost_cutoff is None:
        ghost_cutoff = 0.05 if is_raw else 0.0

    print(
        f"[WeightNet Pipeline] RAW mode={is_raw} -> "
        f"ghost_penalty={ghost_penalty:.2f}, ghost_cutoff={ghost_cutoff:.2f}"
    )

    if progress_callback:
        progress_callback(10, "Loading and preparing burst frames...")

    if frames is not None and len(frames) > 0:
        norm_images = normalize_burst_frames(frames, is_raw=is_raw)
    else:
        norm_images = load_burst_images(image_paths)

    burst = burst_images_to_array(norm_images)
    del norm_images

    def internal_progress(val, msg):
        if progress_callback:
            mapped_val = 15 + int(val * 0.80)
            progress_callback(mapped_val, msg)

    result_fp32, alpha = run_collab_onnx_inference(
        session,
        burst,
        tile_size=tile_size,
        work_scale=work_scale,
        overlap=overlap,
        ghost_penalty=ghost_penalty,
        ghost_cutoff=ghost_cutoff,
        stop_event=stop_event,
        progress=internal_progress,
    )
    return result_fp32, alpha
