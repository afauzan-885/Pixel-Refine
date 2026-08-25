import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys
import importlib.util

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)


import taichi_vision.taichi_algorithm.pyramid.fft
fft_module = sys.modules["taichi_vision.taichi_algorithm.pyramid.fft"]

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module

def compile_fft_aot(arch=ti.vulkan, save_path="fft_vulkan.tcm"):
    print(f"\n>>> Compiling FFT AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    bits_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "bits", ti.i32)
    is_col_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "is_col", ti.i32)
    n_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32)
    stage_len_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stage_len", ti.i32)
    is_inverse_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "is_inverse", ti.i32)
    scale_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    conj_b_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "conj_b", ti.i32)

    # 1. Bit Reverse
    g_br = ti.graph.GraphBuilder()
    src_vec = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.math.vec2, ndim=2)
    dst_vec = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.math.vec2, ndim=2)
    g_br.dispatch(fft_module._bit_reverse_kernel, src_vec, dst_vec, bits_arg, is_col_arg)
    module.add_graph("fft_bit_reverse_f32", g_br.compile())

    # 2. FFT Stage
    g_fs = ti.graph.GraphBuilder()
    data_vec = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "data", ti.math.vec2, ndim=2)
    g_fs.dispatch(fft_module._fft_stage_kernel, data_vec, n_arg, stage_len_arg, is_inverse_arg, is_col_arg)
    module.add_graph("fft_stage_f32", g_fs.compile())

    # 3. Normalize
    g_norm = ti.graph.GraphBuilder()
    g_norm.dispatch(fft_module._normalize_kernel, data_vec, scale_arg)
    module.add_graph("fft_normalize_f32", g_norm.compile())

    # 4. Real to Complex
    g_r2c = ti.graph.GraphBuilder()
    src_real = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    g_r2c.dispatch(fft_module._real_to_complex_kernel, src_real, dst_vec, h_arg, w_arg)
    module.add_graph("fft_real_to_complex_f32", g_r2c.compile())

    # 5. Complex to Real
    g_c2r = ti.graph.GraphBuilder()
    dst_real = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_c2r.dispatch(fft_module._complex_to_real_kernel, src_vec, dst_real, h_arg, w_arg)
    module.add_graph("fft_complex_to_real_f32", g_c2r.compile())

    # 6. Complex Mul
    g_cmul = ti.graph.GraphBuilder()
    b_vec = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b", ti.math.vec2, ndim=2)
    g_cmul.dispatch(fft_module._complex_mul_kernel, src_vec, b_vec, dst_vec, conj_b_arg)
    module.add_graph("fft_complex_mul_f32", g_cmul.compile())

    # 7. Complex Mag
    g_cmag = ti.graph.GraphBuilder()
    g_cmag.dispatch(fft_module._complex_to_mag_kernel, src_vec, dst_real)
    module.add_graph("fft_complex_to_mag_f32", g_cmag.compile())
    
    # 8. Phase Normalize
    g_pnorm = ti.graph.GraphBuilder()
    g_pnorm.dispatch(fft_module._phase_normalize_kernel, data_vec)
    module.add_graph("fft_phase_normalize_f32", g_pnorm.compile())

    # 9. Hanning Window
    g_hwin = ti.graph.GraphBuilder()
    g_hwin.dispatch(fft_module._hanning_window_kernel, dst_real, h_arg, w_arg)
    module.add_graph("fft_hanning_window_f32", g_hwin.compile())

    # 10. Complex Hanning Window
    g_chwin = ti.graph.GraphBuilder()
    g_chwin.dispatch(fft_module._complex_hanning_kernel, data_vec, h_arg, w_arg)
    module.add_graph("fft_complex_hanning_f32", g_chwin.compile())

    archive_module(module, save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = file_dir
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.cpu, "cpu")
    ]
    
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"fft_{suffix}.tcm"))
        try:
            compile_fft_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
