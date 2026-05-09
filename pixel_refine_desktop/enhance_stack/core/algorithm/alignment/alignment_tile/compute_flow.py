import os
import numpy as np

# NO TAICHI IMPORT HERE - Pure AOT Runtime

def _get_engine():
    from ...taichi_aot.engine import AOTEngine
    return AOTEngine()

def compute_alignment_flow(
    ref_img,
    comp_img,
    tile_h=16,
    tile_w=16,
    n_layers=3,
    search_dist=2.0,
    **kwargs
):
    """
    Pure AOT Runtime Compute Flow (Standalone Wrapper).
    Orchestrates the 'One Big Graph' for alignment.
    """
    from .alignment_tile_taichi import TaichiAlignment
    
    # Use the orchestrator for consistent behavior
    aligner = TaichiAlignment()
    
    # 1. Set Reference
    h, w = ref_img.shape[:2]
    aligner.set_reference(ref_img, work_h=h, work_w=w, **kwargs)
    
    # 2. Compute Flow
    # Note: alignment_tile_taichi currently returns a placeholder image
    # In a full pipeline, it would return the flow or the warped image.
    res = aligner.compute_alignment_and_warp(
        comp_img, tile_h=tile_h, tile_w=tile_w, n_layers=n_layers, search_dist=search_dist, **kwargs
    )
    
    return res
