import os
import numpy as np
from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import AOTEngine


def normalize_image_gpu(image_gpu, dtype, out_gpu=None):
    engine = AOTEngine()
    h, w = image_gpu.shape[0], image_gpu.shape[1]
    if out_gpu is None:
        out_gpu = engine.allocate((h, w, 3), dtype=np.float32, is_vector=True, vector_dim=3)

    src_f32 = image_gpu.cast(np.float32)

    file_dir = os.path.dirname(os.path.abspath(__file__))
    aot_assets_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data/aot_assets"))
    tcm_path = os.path.join(aot_assets_dir, "normalize_image.tcm")

    inv_scale = 1.0
    if np.issubdtype(dtype, np.integer):
        inv_scale = 1.0 / float(np.iinfo(dtype).max)

    graph = "normalize_vec3_f32_to_vec3_f32" if image_gpu.is_vector else "normalize_f32_to_vec3"
    mod = engine.load(tcm_path)
    if graph == "normalize_f32_to_vec3":
        mod.run(graph, src=src_f32, dst=out_gpu, inv_scale=float(inv_scale))
    else:
        mod.run(graph, src_vec3=src_f32, dst=out_gpu, inv_scale=float(inv_scale))

    # Destroy intermediate cast buffer immediately
    if src_f32 is not image_gpu:
        src_f32.destroy()
    return out_gpu


def to_gamma_proxy_gpu(image_gpu, scale=1.0, gamma_pow=2.22, slope=4.5, cutoff=0.018, dst_gpu=None):
    engine = AOTEngine()
    file_dir = os.path.dirname(os.path.abspath(__file__))
    aot_assets_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data/aot_assets"))
    tcm_path = os.path.join(aot_assets_dir, "gamma_proxy.tcm")

    mod = engine.load(tcm_path)
    if dst_gpu is None:
        dst_gpu = engine.allocate(image_gpu.shape, dtype=np.float32, is_vector=image_gpu.is_vector, vector_dim=image_gpu.vector_dim)

    graph_name = "gamma_proxy_rgb" if image_gpu.is_vector else "gamma_proxy_single"
    mod.run(graph_name, src=image_gpu, dst=dst_gpu, scale=float(scale), gamma_pow=float(gamma_pow), slope=float(slope), cutoff=float(cutoff))
    return dst_gpu


def prepare_pyramid_aot(image_gpu):
    """Creates a 3-layer pyramid (L0, L1, L2). L0=full res, L1=1/2, L2=1/4."""
    l0 = image_gpu
    h, w = l0.shape[0], l0.shape[1]
    l1 = taichi_aot.resize(l0, (w // 2, h // 2), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
    l2 = taichi_aot.resize(l1, (w // 4, h // 4), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
    return l0, l1, l2


def prepare_reference_for_alignment(reference_image_float, is_linear_mode, proxy_scale, work_res_h, work_res_w):
    """Prepare reference image pyramid on GPU. Returns (l0, l1, l2) — caller must destroy all."""
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
        final_res_gray = taichi_aot.resize(ref_gray, (work_res_w, work_res_h), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        if ref_gray is not final_res_gray:
            ref_gray.destroy()

    return prepare_pyramid_aot(final_res_gray)


def prepare_comparison_for_alignment(comp_image, ref_dtype, is_linear_mode, proxy_scale, work_res_h, work_res_w):
    """Prepare comparison image pyramid on GPU. Returns (l0, l1, l2) — caller must destroy all."""
    comp_input = taichi_aot.upload(comp_image)
    comp_normalized = normalize_image_gpu(comp_input, dtype=ref_dtype)
    if comp_input is not comp_normalized:
        comp_input.destroy()

    comp_final = comp_normalized
    if is_linear_mode:
        comp_final = to_gamma_proxy_gpu(comp_normalized, scale=proxy_scale)
        if comp_normalized is not comp_final:
            comp_normalized.destroy()

    comp_gray = taichi_aot.rgb2gray(comp_final)
    if comp_final is not comp_gray:
        comp_final.destroy()

    final_res_gray = comp_gray
    if comp_gray.shape[:2] != (work_res_h, work_res_w):
        final_res_gray = taichi_aot.resize(comp_gray, (work_res_w, work_res_h), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        if comp_gray is not final_res_gray:
            comp_gray.destroy()

    return prepare_pyramid_aot(final_res_gray)


def prepare_reference_aot(reference_image_float, is_linear_mode, proxy_scale, work_res_h, work_res_w):
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
        final_res_gray = taichi_aot.resize(ref_gray, (work_res_w, work_res_h), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        if ref_gray is not final_res_gray:
            ref_gray.destroy()

    # Estimate noise on CPU/NumPy
    ref_gray_np = final_res_gray.to_numpy()
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import estimate_noise_in_python
    ref_noise_sigma = estimate_noise_in_python(ref_gray_np)

    return final_res_gray, ref_noise_sigma


def prepare_frame_aot(img_orig, ref_dtype, is_linear_mode, proxy_scale, work_res_h, work_res_w, ref_image_h, ref_image_w):
    """Prepare comparison frame on GPU for merging. Returns (curr_full_gpu, curr_work_gray_gpu)."""
    uploaded = taichi_aot.upload(img_orig)
    curr_full_gpu = normalize_image_gpu(uploaded, dtype=ref_dtype)
    if uploaded is not curr_full_gpu:
        uploaded.destroy()
    if curr_full_gpu.shape[:2] != (ref_image_h, ref_image_w):
        new_full = taichi_aot.resize(curr_full_gpu, (ref_image_w, ref_image_h), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        curr_full_gpu.destroy()
        curr_full_gpu = new_full

    curr_final = curr_full_gpu
    if is_linear_mode:
        curr_final = to_gamma_proxy_gpu(curr_full_gpu, scale=proxy_scale)

    curr_gray = taichi_aot.rgb2gray(curr_final)
    if curr_final is not curr_full_gpu and curr_final is not curr_gray:
        curr_final.destroy()

    curr_work_gray_gpu = curr_gray
    if curr_gray.shape[:2] != (work_res_h, work_res_w):
        curr_work_gray_gpu = taichi_aot.resize(curr_gray, (work_res_w, work_res_h), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True)
        if curr_gray is not curr_work_gray_gpu:
            curr_gray.destroy()

    return curr_full_gpu, curr_work_gray_gpu
