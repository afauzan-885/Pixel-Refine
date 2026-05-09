import os
import numpy as np

# NO TAICHI IMPORT HERE - Full AOT Runtime

def _get_engine():
    from ..taichi_aot.engine import AOTEngine
    return AOTEngine()

def warp_image_gpu(
    src,
    flow,
    dst=None,
    guidance=None,
    return_numpy=True,
    **kwargs
):
    """
    Pure AOT Runtime Warp Image.
    Compatible as a drop-in replacement for OpenCV warp.
    """
    engine = _get_engine()
    
    # 1. Load Warp Module
    aot_assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../ui/data/aot_assets"))
    tcm_path = os.path.join(aot_assets_dir, "warp_vulkan")
    mod = engine.load(tcm_path)
    
    # 2. Upload & Cast Inputs (AOT expects i32 for uint16/uint8)
    src_gpu = engine.upload(src)
    if src_gpu.dtype != np.int32 and np.issubdtype(src_gpu.dtype, np.integer):
        src_gpu = src_gpu.cast(np.int32)
        
    flow_gpu = engine.upload(flow)
    
    h, w = src_gpu.shape[:2]
    is_3d = len(src_gpu.shape) == 3
    is_guided = guidance is not None
    
    # 3. Allocate Output
    if dst is None:
        dst = engine.allocate(src_gpu.shape, dtype=src_gpu.dtype, is_vector=is_3d)
    
    # 4. View Mapping (AOT expects vector for RGB)
    src_v = src_gpu.view_as_vector(True) if is_3d else src_gpu
    dst_v = dst.view_as_vector(True) if is_3d else dst
    
    type_suffix = "f32" if src_gpu.dtype == np.float32 else "i32"
    ch_suffix = "3ch" if is_3d else "1ch"
    
    # 5. Execute
    if is_guided:
        guidance_gpu = engine.upload(guidance)
        if guidance_gpu.dtype != np.int32 and np.issubdtype(guidance_gpu.dtype, np.integer):
            guidance_gpu = guidance_gpu.cast(np.int32)
            
        guidance_v = guidance_gpu.view_as_vector(True) if is_3d else guidance_gpu
        graph = f"warp_guided_{type_suffix}_{ch_suffix}"
        mod.run(graph, src=src_v, flow=flow_gpu, dst=dst_v, ref=guidance_v)
    else:
        graph = f"warp_naked_{type_suffix}_{ch_suffix}"
        mod.run(graph, src=src_v, flow=flow_gpu, dst=dst_v)
        
    if return_numpy:
        return dst.to_numpy()
    return dst
