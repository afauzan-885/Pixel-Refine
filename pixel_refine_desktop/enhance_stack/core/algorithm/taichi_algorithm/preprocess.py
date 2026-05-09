import os
import numpy as np

# NO TAICHI IMPORT HERE - Pure AOT Runtime

def _get_engine():
    from ..taichi_aot.engine import AOTEngine
    return AOTEngine()

def preprocess_pipeline_gpu(
    image, 
    target_size=None,
    apply_gamma=True,
    scale=1.0,
    gamma_pow=2.22,
    slope=4.5,
    cutoff=0.018,
    use_sharpen=False,
    **kwargs
):
    """
    Pure AOT Preprocess Pipeline.
    Uint16/Uint8 -> Normalize -> Resize -> Gamma -> Float32
    """
    engine = _get_engine()
    
    # 1. Load Preprocess Module
    # Path relative to: pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/preprocess.py
    # Goal: pixel_refine_desktop/ui/data/aot_assets
    aot_assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../ui/data/aot_assets"))
    tcm_path = os.path.join(aot_assets_dir, "preprocess.tcm")
    mod = engine.load(tcm_path)
    
    # 2. Upload & Cast (AOT expects i32 for src)
    src_gpu = engine.upload(image)
    if src_gpu.dtype != np.int32:
        src_gpu = src_gpu.cast(np.int32)

    # 3. Determine Target Size
    if target_size is None:
        target_size = image.shape[:2]
        
    # 4. Allocate Output (Always Float32 for subsequent processing)
    dst_gpu = engine.allocate(target_size, dtype=np.float32)
    
    # 5. Prepare Scalars
    dtype = getattr(image, "dtype", np.float32)
    scale_norm = float(np.iinfo(dtype).max) if np.issubdtype(dtype, np.integer) else 1.0
    scale_gamma = float(scale if apply_gamma else 1.0)
    
    # 6. Dispatch to TCM Graph
    is_rgb = len(src_gpu.shape) == 3
    graph_name = "preprocess_rgb" if is_rgb else "preprocess_gray"
    
    src_v = src_gpu.view_as_vector(True) if is_rgb else src_gpu
    
    mod.run(
        graph_name,
        src=src_v,
        dst=dst_gpu,
        scale_norm=scale_norm,
        apply_gamma=int(apply_gamma),
        scale_gamma=scale_gamma,
        gamma_pow=float(gamma_pow),
        slope=float(slope),
        cutoff=float(cutoff),
        use_sharpen=int(use_sharpen)
    )
    
    return dst_gpu
