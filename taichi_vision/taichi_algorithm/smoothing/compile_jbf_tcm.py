import os
os.environ["AOT_MODE"] = "0"

"""
compile_jbf_tcm.py
Compiles Joint Bilateral Filter (JBF) + JBLU kernels to AOT (.tcm).

Graphs compiled:
  JBF:  jbf_1ch_r1/r2/r3, jbf_3ch_r1/r2/r3, jbf_flow_r1/r2/r3
  JBLU: jblu_1ch_r2, jblu_3ch_r2, jblu_flow_r2
"""
import taichi as ti
import os, sys, importlib

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

jbf = importlib.import_module(
    "taichi_vision.taichi_algorithm.smoothing.joint_bilateral_guidance"
)

def compile_jbf_aot(arch=ti.vulkan, save_path="jbf_vulkan.tcm"):
    print(f"\n>>> Compiling JBF+JBLU AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    F32 = ti.f32
    I32 = ti.i32
    VEC2 = ti.types.vector(2, ti.f32)
    VEC3 = ti.types.vector(3, ti.f32)

    # ---- Common arg helper ----
    def scalar_args():
        h   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h",       I32)
        w   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w",       I32)
        ss2 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_2ss2",F32)
        sr2 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_2sr2",F32)
        return h, w, ss2, sr2

    # ==============================================================
    # JBF Ã¢â‚¬â€ 1ch (scalar map, depth, mask, etc.)
    # ==============================================================
    def add_jbf_1ch(name, kernel):
        b = ti.graph.GraphBuilder()
        src   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src",   F32, ndim=2)
        guide = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide", F32, ndim=2)
        dst   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst",   F32, ndim=2)
        h, w, ss2, sr2 = scalar_args()
        b.dispatch(kernel, src, guide, dst, h, w, ss2, sr2)
        module.add_graph(name, b.compile())

    add_jbf_1ch("jbf_1ch_r1", jbf._jbf_1ch_r1)
    add_jbf_1ch("jbf_1ch_r2", jbf._jbf_1ch_r2)
    add_jbf_1ch("jbf_1ch_r3", jbf._jbf_1ch_r3)

    # ==============================================================
    # JBF Ã¢â‚¬â€ 3ch (RGB image)
    # ==============================================================
    def add_jbf_3ch(name, kernel):
        b = ti.graph.GraphBuilder()
        src   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src",   VEC3, ndim=2)
        guide = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide", F32,  ndim=2)
        dst   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst",   VEC3, ndim=2)
        h, w, ss2, sr2 = scalar_args()
        b.dispatch(kernel, src, guide, dst, h, w, ss2, sr2)
        module.add_graph(name, b.compile())

    add_jbf_3ch("jbf_3ch_r1", jbf._jbf_3ch_r1)
    add_jbf_3ch("jbf_3ch_r2", jbf._jbf_3ch_r2)
    add_jbf_3ch("jbf_3ch_r3", jbf._jbf_3ch_r3)

    # ==============================================================
    # JBF Ã¢â‚¬â€ flow (2ch U/V field)
    # ==============================================================
    def add_jbf_flow(name, kernel):
        b = ti.graph.GraphBuilder()
        src   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src",   VEC2, ndim=2)
        guide = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide", F32,  ndim=2)
        dst   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst",   VEC2, ndim=2)
        h, w, ss2, sr2 = scalar_args()
        b.dispatch(kernel, src, guide, dst, h, w, ss2, sr2)
        module.add_graph(name, b.compile())

    add_jbf_flow("jbf_flow_r1", jbf._jbf_flow_r1)
    add_jbf_flow("jbf_flow_r2", jbf._jbf_flow_r2)
    add_jbf_flow("jbf_flow_r3", jbf._jbf_flow_r3)

    # ==============================================================
    # JBLU Ã¢â‚¬â€ Scalar 1ch
    # ==============================================================
    def jblu_scalar_args():
        h_low = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_low", I32)
        w_low = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_low", I32)
        H     = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "H",     I32)
        W     = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "W",     I32)
        ss2   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_2ss2", F32)
        sr2   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_2sr2", F32)
        return h_low, w_low, H, W, ss2, sr2

    b = ti.graph.GraphBuilder()
    src_low  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src_low",  F32, ndim=2)
    guide_hi = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide_hi", F32, ndim=2)
    dst      = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst",      F32, ndim=2)
    h_low, w_low, H, W, ss2, sr2 = jblu_scalar_args()
    b.dispatch(jbf._jblu_1ch_r2, src_low, guide_hi, dst, h_low, w_low, H, W, ss2, sr2)
    module.add_graph("jblu_1ch_r2", b.compile())

    # ==============================================================
    # JBLU Ã¢â‚¬â€ Flow 2ch
    # ==============================================================
    b = ti.graph.GraphBuilder()
    src_low  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src_low",  VEC2, ndim=2)
    guide_hi = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide_hi", F32,  ndim=2)
    dst      = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst",      VEC2, ndim=2)
    h_low, w_low, H, W, ss2, sr2 = jblu_scalar_args()
    scale_y  = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_y", F32)
    scale_x  = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_x", F32)
    b.dispatch(jbf._jblu_flow_r2, src_low, guide_hi, dst,
               h_low, w_low, H, W, ss2, sr2, scale_y, scale_x)
    module.add_graph("jblu_flow_r2", b.compile())

    # ==============================================================
    # JBLU Ã¢â‚¬â€ 3ch Image
    # ==============================================================
    b = ti.graph.GraphBuilder()
    src_low  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src_low",  VEC3, ndim=2)
    guide_hi = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide_hi", F32,  ndim=2)
    dst      = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst",      VEC3, ndim=2)
    h_low, w_low, H, W, ss2, sr2 = jblu_scalar_args()
    b.dispatch(jbf._jblu_3ch_r2, src_low, guide_hi, dst, h_low, w_low, H, W, ss2, sr2)
    module.add_graph("jblu_3ch_r2", b.compile())

    module.archive(save_path)
    print(f"[OK] Archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    assets_dir = os.path.abspath(os.path.join(file_dir, "../aot_tcm"))
    os.makedirs(assets_dir, exist_ok=True)

    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        path = os.path.join(assets_dir, f"jbf_{suffix}.tcm")
        try:
            compile_jbf_aot(arch=arch, save_path=path)
        except Exception as e:
            print(f"[SKIP] {suffix}: {e}")
