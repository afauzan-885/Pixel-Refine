import numpy as np

class MedianMerge:
    """Median merging backend."""
    
    def merge_tiles(self, aligned_tiles):
        from taichi_library.taichi_aot.engine import TaichiGPUBuffer
        aligned_tiles_np = [
            t.to_numpy() if isinstance(t, TaichiGPUBuffer) else t
            for t in aligned_tiles
        ]
        merged_tile = np.median(aligned_tiles_np, axis=0)
        weight_map = np.ones(merged_tile.shape[:2], dtype=np.float32)
        return merged_tile, weight_map

def running_median(parent=None, single_process=None, batch_id=None, progress_callback=None, stop_callback=None):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import running_mf_denoiser
    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode="median",
        output_suffix="median"
    )

