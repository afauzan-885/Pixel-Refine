import numpy as np

class AverageMerge:
    """Simple Average merging backend."""
    
    def merge_tiles(self, aligned_tiles):
        from taichi_library.taichi_aot.engine import TaichiGPUBuffer
        aligned_tiles_np = [
            t.to_numpy() if isinstance(t, TaichiGPUBuffer) else t
            for t in aligned_tiles
        ]
        sum_tile = np.sum(aligned_tiles_np, axis=0)
        weight_map = np.ones(sum_tile.shape[:2], dtype=np.float32) * len(aligned_tiles_np)
        return sum_tile / len(aligned_tiles_np), weight_map

def running_average(parent=None, single_process=None, batch_id=None, progress_callback=None, stop_callback=None):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import running_mf_denoiser
    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode="average",
        output_suffix="average"
    )

