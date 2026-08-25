import taichi as ti
import importlib.util
import os
import sys

# Path setup
file_dir = os.path.dirname(os.path.abspath(__file__))
# 6 levels up to reach pixel_refine_desktop
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["AOT_MODE"] = "0"

# Relative import from the same aot folder
import normalize_image_kernels as kernels

def compile_normalize_image_aot(arch=ti.vulkan, save_path="normalize_image_vulkan.tcm"):
    print(f"\n>>> Compiling NORMALIZE IMAGE AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # Arguments
    inv_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_scale", ti.f32)
    src_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    src_vec3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src_vec3", ti.types.vector(3, ti.f32), ndim=2)
    dst_vec3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)

    # 1. normalize_f32_to_vec3
    builder1 = ti.graph.GraphBuilder()
    builder1.dispatch(kernels.normalize_f32_to_vec3_kernel, src_f32, dst_vec3, inv_scale)
    module.add_graph("normalize_f32_to_vec3", builder1.compile())

    # 2. normalize_vec3_f32_to_vec3_f32
    builder2 = ti.graph.GraphBuilder()
    builder2.dispatch(kernels.normalize_vec3_f32_to_vec3_f32_kernel, src_vec3, dst_vec3, inv_scale)
    module.add_graph("normalize_vec3_f32_to_vec3_f32", builder2.compile())

    # The archiver itself is stdlib-only, but importing it through the package
    # initializes the application AOT runtime as a parent-module side effect.
    # That creates a second OpenGL context in the compiler process.  Load the
    # file directly after ``ti.init`` so the requested Taichi architecture is
    # the only compiler context in this process.
    artifact_path = os.path.abspath(
        os.path.join(
            file_dir,
            "../../../../../../../taichi_vision/taichi_algorithm/aot_py/aot_artifact.py",
        )
    )
    spec = importlib.util.spec_from_file_location(
        "pixel_refine_normalize_image_archiver", artifact_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load AOT archiver: {artifact_path}")
    artifact_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(artifact_module)
    archive_module = artifact_module.archive_module

    # Use the canonical archiver so LLVM/GFX metadata (including
    # ``aot_metadata.tcb``) is retained.  The legacy ``Module.archive`` path
    # emitted artifacts that the current runtime correctly quarantines.
    archive_module(module, save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 6 levels up to reach pixel_refine_desktop then into ui/data/aot_assets
    assets_dir = os.path.abspath(os.path.join(script_dir, "../../../../../../ui/data/aot_assets"))
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.opengl, "opengl"),
        (ti.cpu, "cpu"),
    ]
    for arch, suffix in archs:
        save_path = os.path.join(assets_dir, f"normalize_image_{suffix}.tcm")
        try:
            compile_normalize_image_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
