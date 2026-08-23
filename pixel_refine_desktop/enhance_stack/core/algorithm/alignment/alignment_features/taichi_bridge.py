import os
import numpy as np
from taichi_vision import taichi_aot
from taichi_vision.taichi_aot import get_engine


def _resolve_aot_asset(name, *, engine=None):
    """Resolve an optional canonical TCM root for isolated parity probes.

    The desktop UI still owns its historical flat asset directory by default.
    A test/build process can set ``PIXEL_REFINE_AOT_TCM_ROOT`` to force the
    bridge helpers to use the same backend-qualified artifacts as
    ``taichi_vision``.  This is deliberately opt-in so existing application
    packaging and public call sites remain unchanged.
    """

    engine = engine or get_engine()
    # Keep this bridge on the same target-qualified resolver as the public
    # ``aot_api`` facade.  Previously only the test override was considered;
    # normal application runs therefore loaded the old flat
    # ``ui/data/aot_assets/normalize_image_*.tcm`` archives even when the
    # active LLVM20 bundle already contained a rebuilt target artifact. Those
    # legacy archives can lack ``aot_metadata.tcb`` and fail during a later
    # spatial crop dispatch, which looks like a lifecycle failure.
    arch = str(getattr(engine, "arch", "cpu")).lower()
    try:
        from taichi_vision.taichi_aot.artifact_targets import (
            detect_target,
            resolve_artifact,
        )
        from taichi_vision.llvm20_runtime_paths import tcm_root as staged_tcm_root

        target = detect_target(
            backend=arch,
            device=getattr(engine, "gpu_name", ""),
        )
        stem, _ = os.path.splitext(name)
        roots = []
        override = os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip()
        if override:
            roots.append(os.path.abspath(override))
        else:
            staged = staged_tcm_root(target.target_id)
            if staged is not None:
                roots.append(os.path.abspath(str(staged)))
            roots.append(
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../../../../../../taichi_vision/taichi_algorithm/aot_tcm",
                    )
                )
            )
        seen_roots = set()
        for root in roots:
            root = os.path.normcase(os.path.realpath(root))
            if root in seen_roots or not os.path.isdir(root):
                continue
            seen_roots.add(root)
            resolved = resolve_artifact(
                root,
                stem,
                target,
                allow_legacy=False,
            )
            if resolved is not None:
                return os.path.abspath(str(resolved))
    except (ImportError, OSError, RuntimeError, ValueError):
        # Resolution is an additive hardening layer. If a package/frozen build
        # omits the registry, preserve the historical fallback below.
        pass

    file_dir = os.path.dirname(os.path.abspath(__file__))
    aot_assets_dir = os.path.abspath(
        os.path.join(file_dir, "../../../../../ui/data/aot_assets")
    )
    return os.path.join(aot_assets_dir, name)


def normalize_image_gpu(image_gpu, dtype, out_gpu=None):
    engine = get_engine()
    h, w = image_gpu.shape[0], image_gpu.shape[1]
    if out_gpu is None:
        out_gpu = engine.allocate(
            (h, w, 3), dtype=np.float32, is_vector=True, vector_dim=3
        )

    src_f32 = image_gpu.cast(np.float32)

    tcm_path = _resolve_aot_asset("normalize_image.tcm", engine=engine)

    inv_scale = 1.0
    buf_dtype = getattr(image_gpu, "dtype", dtype)
    if np.issubdtype(buf_dtype, np.integer):
        inv_scale = 1.0 / float(np.iinfo(buf_dtype).max)

    graph = (
        "normalize_vec3_f32_to_vec3_f32"
        if image_gpu.is_vector
        else "normalize_f32_to_vec3"
    )
    mod = engine.load(tcm_path)
    if graph == "normalize_f32_to_vec3":
        mod.run(graph, src=src_f32, dst=out_gpu, inv_scale=float(inv_scale))
    else:
        mod.run(graph, src_vec3=src_f32, dst=out_gpu, inv_scale=float(inv_scale))

    # Destroy intermediate cast buffer immediately
    if src_f32 is not image_gpu:
        src_f32.destroy()
    return out_gpu


def to_gamma_proxy_gpu(
    image_gpu, scale=1.0, gamma_pow=2.22, slope=4.5, cutoff=0.018, dst_gpu=None
):
    engine = get_engine()
    tcm_path = _resolve_aot_asset("gamma_proxy.tcm", engine=engine)

    mod = engine.load(tcm_path)
    if dst_gpu is None:
        dst_gpu = engine.allocate(
            image_gpu.shape,
            dtype=np.float32,
            is_vector=image_gpu.is_vector,
            vector_dim=image_gpu.vector_dim,
        )

    graph_name = "gamma_proxy_rgb" if image_gpu.is_vector else "gamma_proxy_single"
    if graph_name == "gamma_proxy_rgb":
        # Retrieve active color matrix or fallback to identity
        cmatrix = getattr(engine, "active_cmatrix", None)
        if cmatrix is None:
            cmatrix = np.eye(3, dtype=np.float32)
        cmatrix_gpu = engine.upload(cmatrix)
        mod.run(
            graph_name,
            src=image_gpu,
            dst=dst_gpu,
            cmatrix=cmatrix_gpu,
            scale=float(scale),
            gamma_pow=float(gamma_pow),
            slope=float(slope),
            cutoff=float(cutoff),
        )
        cmatrix_gpu.destroy()
    else:
        mod.run(
            graph_name,
            src=image_gpu,
            dst=dst_gpu,
            scale=float(scale),
            gamma_pow=float(gamma_pow),
            slope=float(slope),
            cutoff=float(cutoff),
        )
    return dst_gpu


def prepare_pyramid_aot(image_gpu, num_layers=3):
    """Creates a multi-layer pyramid (L0, L1, ...). L0=full res, L1=1/2, L2=1/4, etc."""
    layers = [image_gpu]
    for i in range(1, num_layers):
        prev = layers[-1]
        h_prev, w_prev = prev.shape[:2]
        next_layer = taichi_aot.resize(
            prev, (w_prev // 2, h_prev // 2), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True
        )
        layers.append(next_layer)
    return tuple(layers)


def prepare_reference_for_alignment(
    reference_image_float,
    is_linear_mode,
    proxy_scale,
    work_res_h,
    work_res_w,
    lut_gpu=None,
    blur_work_gpu=None,
    num_layers=3,
):
    """Prepare reference image pyramid on GPU. Returns (l0, l1, l2, ...) — caller must destroy all."""
    from taichi_vision.taichi_aot import (
        TaichiGPUBuffer,
    )

    input_is_gpu_buf = isinstance(reference_image_float, TaichiGPUBuffer)

    # Check if the reference image is a 1-channel RAW image that needs fast demosaicing directly to grayscale
    is_raw_sensor = (not input_is_gpu_buf and reference_image_float.ndim == 2) or (
        input_is_gpu_buf and len(reference_image_float.shape) == 2
    )

    if is_raw_sensor:
        # FUSED RAW OPTIMIZATION: Decode Bayer directly to Grayscale 1-channel (Green-only fast luma)
        # Avoids allocating massive RGB intermediate VRAM buffers!
        ref_gpu = taichi_aot.upload(reference_image_float, force_8bit=False)
        # Get active camera parameters from engine if available
        engine = get_engine()
        wb_r = getattr(engine, "active_wb_r", 1.0)
        wb_g1 = getattr(engine, "active_wb_g1", 1.0)
        wb_b = getattr(engine, "active_wb_b", 1.0)
        wb_g2 = getattr(engine, "active_wb_g2", 1.0)
        black_level = getattr(engine, "active_black_level", 0.0)
        white_level = getattr(engine, "active_white_level", 16383.0)
        c00 = getattr(engine, "active_c00", 0)
        c01 = getattr(engine, "active_c01", 1)
        c10 = getattr(engine, "active_c10", 1)
        c11 = getattr(engine, "active_c11", 2)

        ref_final = taichi_aot.demosaic(
            ref_gpu,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            None,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            method="hamilton-1channel",
            return_gpu=True,
        )
        if ref_gpu is not ref_final:
            ref_gpu.release()
    else:
        ref_gpu = taichi_aot.upload(reference_image_float, force_8bit=True)
        ref_final = ref_gpu

        if is_linear_mode:
            ref_final = to_gamma_proxy_gpu(ref_gpu, scale=proxy_scale)
            if ref_gpu is not ref_final:
                ref_gpu.release()

    # Convert ref_final to grayscale 1-channel if it is a 3-channel image
    if not is_raw_sensor:
        ref_gray = taichi_aot.rgb2gray(ref_final)
        if ref_final is not ref_gray:
            ref_final.release()
    else:
        # Already Grayscale 1-channel
        ref_gray = ref_final

    final_res_gray = ref_gray
    if ref_gray.shape[:2] != (work_res_h, work_res_w):
        final_res_gray = taichi_aot.resize(
            ref_gray,
            (work_res_w, work_res_h),
            interpolation=taichi_aot.INTER_LINEAR,
            return_gpu=True,
        )
        if ref_gray is not final_res_gray:
            ref_gray.release()

    return prepare_pyramid_aot(final_res_gray, num_layers=num_layers)


def prepare_comparison_for_alignment(
    comp_image,
    ref_dtype,
    is_linear_mode,
    proxy_scale,
    work_res_h,
    work_res_w,
    lut_gpu=None,
    blur_work_gpu=None,
    num_layers=3,
):
    """Prepare comparison image pyramid on GPU. Returns (l0, l1, l2, ...) — caller must destroy all."""
    from taichi_vision.taichi_aot import (
        TaichiGPUBuffer,
    )

    input_is_gpu_buf = isinstance(comp_image, TaichiGPUBuffer)

    # Check if the image is a 1-channel RAW image that needs fast demosaicing directly to grayscale
    is_raw_sensor = (not input_is_gpu_buf and comp_image.ndim == 2) or (
        input_is_gpu_buf and len(comp_image.shape) == 2
    )

    if is_raw_sensor:
        # FUSED RAW OPTIMIZATION: Decode Bayer directly to Grayscale 1-channel (Green-only fast luma)
        # Avoids allocating massive RGB intermediate VRAM buffers!
        comp_gpu = taichi_aot.upload(comp_image, force_8bit=False)
        # Get active camera parameters from engine if available
        engine = get_engine()
        wb_r = getattr(engine, "active_wb_r", 1.0)
        wb_g1 = getattr(engine, "active_wb_g1", 1.0)
        wb_b = getattr(engine, "active_wb_b", 1.0)
        wb_g2 = getattr(engine, "active_wb_g2", 1.0)
        black_level = getattr(engine, "active_black_level", 0.0)
        white_level = getattr(engine, "active_white_level", 16383.0)
        c00 = getattr(engine, "active_c00", 0)
        c01 = getattr(engine, "active_c01", 1)
        c10 = getattr(engine, "active_c10", 1)
        c11 = getattr(engine, "active_c11", 2)

        comp_final = taichi_aot.demosaic(
            comp_gpu,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            None,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            method="hamilton-1channel",
            return_gpu=True,
        )
        if comp_gpu is not comp_final:
            comp_gpu.release()
    else:
        comp_input = taichi_aot.upload(comp_image, force_8bit=True)
        comp_normalized = normalize_image_gpu(comp_input, dtype=ref_dtype)
        if comp_input is not comp_normalized:
            comp_input.release()

        comp_final = comp_normalized
        if is_linear_mode:
            comp_final = to_gamma_proxy_gpu(comp_normalized, scale=proxy_scale)
            if comp_normalized is not comp_final:
                comp_normalized.release()

    # Convert comp_final to grayscale 1-channel if it is a 3-channel image
    if not is_raw_sensor:
        comp_gray = taichi_aot.rgb2gray(comp_final)
        if comp_final is not comp_gray:
            comp_final.release()
    else:
        # Already Grayscale 1-channel
        comp_gray = comp_final

    final_res_gray = comp_gray
    if comp_gray.shape[:2] != (work_res_h, work_res_w):
        final_res_gray = taichi_aot.resize(
            comp_gray,
            (work_res_w, work_res_h),
            interpolation=taichi_aot.INTER_LINEAR,
            return_gpu=True,
        )
        if comp_gray is not final_res_gray:
            comp_gray.release()

    return prepare_pyramid_aot(final_res_gray, num_layers=num_layers)


def prepare_reference_aot(
    reference_image_float, is_linear_mode, proxy_scale, work_res_h, work_res_w
):
    """Prepare reference image on GPU for merging. Returns (ref_work_res_pass2_gpu, ref_noise_sigma)."""
    ref_gpu = taichi_aot.upload(reference_image_float)
    ref_final = ref_gpu

    if is_linear_mode:
        ref_final = to_gamma_proxy_gpu(ref_gpu, scale=proxy_scale)
        if ref_gpu is not ref_final:
            ref_gpu.destroy()

    ref_gray = taichi_aot.rgb2gray(ref_final)
    if ref_final is not ref_gray:
        ref_final.destroy()

    final_res_gray = ref_gray
    if ref_gray.shape[:2] != (work_res_h, work_res_w):
        final_res_gray = taichi_aot.resize(
            ref_gray,
            (work_res_w, work_res_h),
            interpolation=taichi_aot.INTER_LINEAR,
            return_gpu=True,
        )
        if ref_gray is not final_res_gray:
            ref_gray.destroy()

    # Estimate noise on CPU/NumPy
    ref_gray_np = final_res_gray.to_numpy()
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
        estimate_noise_in_python,
    )

    ref_noise_sigma = estimate_noise_in_python(ref_gray_np)

    return final_res_gray, ref_noise_sigma


def prepare_frame_aot(
    img_orig,
    ref_dtype,
    is_linear_mode,
    proxy_scale,
    work_res_h,
    work_res_w,
    ref_image_h,
    ref_image_w,
):
    """Prepare comparison frame on GPU for merging. Returns (curr_full_gpu, curr_work_gray_gpu)."""
    from taichi_vision.taichi_aot.engine import (
        TaichiGPUBuffer,
    )

    input_is_gpu_buf = isinstance(img_orig, TaichiGPUBuffer)

    uploaded = taichi_aot.upload(img_orig)
    we_own_uploaded = not input_is_gpu_buf

    # FUSED OPTIMIZATION: Combine normalization scale and gamma proxy scale together.
    # We directly apply scale (combined with normalizer inverse scale) inside gamma curve kernel if linear mode.
    if is_linear_mode:
        inv_scale = 1.0
        buf_dtype = getattr(uploaded, "dtype", ref_dtype)
        if np.issubdtype(buf_dtype, np.integer):
            inv_scale = 1.0 / float(np.iinfo(buf_dtype).max)

        # We pass combined scale (proxy_scale * inv_scale) directly to gamma_proxy
        # to process raw uint16 -> gamma scale in one step!
        curr_final = to_gamma_proxy_gpu(uploaded, scale=proxy_scale * inv_scale)
        curr_full_gpu = curr_final  # For linear merging we use gamma proxy space
    else:
        # Non-linear: directly normalize image
        curr_full_gpu = normalize_image_gpu(uploaded, dtype=ref_dtype)
        curr_final = curr_full_gpu

    if (
        we_own_uploaded
        and (uploaded is not curr_final)
        and (uploaded is not curr_full_gpu)
    ):
        uploaded.release()

    if curr_full_gpu.shape[:2] != (ref_image_h, ref_image_w):
        new_full = taichi_aot.resize(
            curr_full_gpu,
            (ref_image_w, ref_image_h),
            interpolation=taichi_aot.INTER_LINEAR,
            return_gpu=True,
        )
        if curr_full_gpu is not curr_final:
            curr_full_gpu.release()
        curr_full_gpu = new_full

    curr_gray = taichi_aot.rgb2gray(curr_final)

    # Eagerly release curr_final if it is an intermediate and not full result
    if curr_final is not curr_full_gpu and curr_final is not curr_gray:
        curr_final.release()

    curr_work_gray_gpu = curr_gray
    if curr_gray.shape[:2] != (work_res_h, work_res_w):
        curr_work_gray_gpu = taichi_aot.resize(
            curr_gray,
            (work_res_w, work_res_h),
            interpolation=taichi_aot.INTER_LINEAR,
            return_gpu=True,
        )
        if curr_gray is not curr_work_gray_gpu:
            curr_gray.release()

    return curr_full_gpu, curr_work_gray_gpu
