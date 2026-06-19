# Implementation Plan: Route Average Denoising Through MFDenoiser

## Overview

When the user selects "Average" in the denoising algorithm dropdown, instead of running the standalone `Average.py`, route it through `MFDenoiser` which will use its universal tiling infrastructure. The Average algorithm becomes a lightweight per-tile processor (`AverageDenoiseProcessor`) that simply sums frames and returns equal weights.

## Current State Analysis

### Algorithm Dispatch (3 locations)
All three currently map `"Average"` → `running_average` (standalone):

| File | Line | Context |
|------|------|---------|
| `algorithm_processor.py` | L19, L137 | Single process mode (AlgorithmProcessorThread) |
| `bulk_combined_panel.py` | L40-42, L986 | Batch mode (CombinedPanel.process_all_batch) |
| `image_processing_controller.py` | L284-285, L294 | Controller (ImageProcessingController._run_denoising_algorithm) |

### MFDenoiser Current Pipeline
```
running_mf_denoiser() → main() → MFDenoiserAlgorithm.run_pipeline()
  → stage_load_data()    — loads images from HDF5 or filesystem
  → stage_align()        — Taichi GPU alignment (skipped if HDF5 exists)
  → stage_merge()        — dispatches to TileProcessor based on merging_mode
  → stage_postprocess()  — normalize by weight + optional adaptive box denoise
  → stage_save()         — saves as _mf_denoiser.tif
```

`stage_merge()` currently dispatches:
- `"spatial"` → SpatialDenoiseProcessor (default)
- `"smart"` → SmartDenoiseProcessor
- `"super_resolution"` → SuperResolutionProcessor

### TileProcessor Interface
```python
class TileProcessor(ABC):
    setup(ctx, shared_data)          # one-time init before tile loop
    get_output_size(tile_h, tile_w)  # returns (out_h, out_w)
    process_tile(tile_ctx, shared_data) → (weighted_sum, weight_map)
    preprocess_batch(batch_float, shared_data)  # optional batch hook
    teardown()                       # cleanup
```

### Average Algorithm (Current)
Simple pixel-wise accumulation: `sum += image.astype(float32)` for all images, then `result = sum / count`. No tiling, no weights.

---

## Plan

### Task 1: Create `AverageDenoiseProcessor`

**File**: `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/average_denoise_processor.py` (NEW)

A minimal TileProcessor that implements simple averaging per tile:

```python
class AverageDenoiseProcessor(TileProcessor):
    def setup(self, ctx, shared_data):
        shared_data["total_frames"] = ctx.total_images

    def get_output_size(self, tile_h, tile_w):
        return (tile_h, tile_w)  # 1:1 ratio

    def process_tile(self, tile_ctx, shared_data):
        # tile_ctx.frame_tiles: (N, H, W, C) float32
        frame_sum = tile_ctx.frame_tiles.sum(axis=0)  # (H, W, C)
        num_frames = tile_ctx.frame_tiles.shape[0]    # scalar weight
        weight_map = np.full(
            (tile_ctx.tile_h, tile_ctx.tile_w),
            float(num_frames), dtype=np.float32
        )
        return frame_sum, weight_map
```

**Why this works with MFDenoiser's tiler:**
- MFDenoiser accumulates: `accumulator += tile_sum * hanning_win` and `weight_accumulator += tile_weight * hanning_win`
- For Average: `tile_sum` = sum of N frames (unweighted by Hanning yet), `tile_weight` = N
- After all tiles: `result = accumulator / weight_accumulator` = correct average
- Hanning stitching ensures smooth tile boundary blending
- Each pixel ends up weighted by the sum of Hanning windows from overlapping tiles (numerator and denominator cancel out correctly)

### Task 2: Add `"average"` Case to `MFDenoiser.stage_merge()`

**File**: `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/MFDenoiser.py`

Add a new branch in `stage_merge()`:

```python
def stage_merge(self, ctx):
    backend = ctx.params.get("merging_mode", "spatial")

    if backend == "average":
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.average_denoise_processor import (
            AverageDenoiseProcessor,
        )
        processor = AverageDenoiseProcessor()
    elif backend == "smart":
        ...
    elif backend == "super_resolution":
        ...
    else:
        ...  # spatial

    return self._run_tiled_merge(processor, ctx)
```

### Task 3: Add `merging_mode` Parameter to MFDenoiser Entry Points

**File**: `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/MFDenoiser.py`

Modify `main()` and `running_mf_denoiser()` to accept an optional `merging_mode` parameter:

```python
def main(db_path, update_progress=None, stop_requested=None,
         single_process=None, batch_id=None, progress_bar=None,
         merging_mode=None):
    ...
    processor = MFDenoiserAlgorithm(db_path)
    output_path = processor.run_pipeline(
        single_process=single_process,
        batch_id=batch_id,
        update_progress=update_progress,
        stop_requested=stop_requested,
        merging_mode=merging_mode,
    )
    ...

def running_mf_denoiser(parent=None, single_process=None, batch_id=None,
                        progress_callback=None, stop_callback=None,
                        merging_mode=None):
    ...
    # Pass merging_mode through to main()
```

Modify `run_pipeline()` to accept and inject `merging_mode` into `ctx.params`:

```python
def run_pipeline(self, single_process=True, batch_id=None,
                 update_progress=None, stop_requested=None,
                 merging_mode=None):
    ctx = PipelineContext(...)
    ctx.params = self._load_params()
    if merging_mode:
        ctx.params["merging_mode"] = merging_mode
    ...
```

### Task 4: Handle Output File Naming

**File**: `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/MFDenoiser.py`

Currently `stage_save()` always outputs `{name}_mf_denoiser.tif`. For Average, it should be `{name}_average.tif`.

Add an `output_suffix` param:

```python
def stage_save(self, ctx, result_image):
    output_suffix = ctx.params.get("output_suffix", "mf_denoiser")
    output_path = os.path.join(output_folder, f"{safe_name}_{output_suffix}.tif")
```

When calling with `merging_mode="average"`, also set `output_suffix="average"`.

### Task 5: Update Dispatch Points (3 files)

#### 5a. `algorithm_processor.py` (Single Process Mode)

```python
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    running_mf_denoiser as running_similarity,
    running_mf_denoiser,  # reuse with merging_mode
)

actions = {
    "denoising": {
        "Average": lambda: running_mf_denoiser(
            self.parent_panel,
            single_process=self.single_process,
            batch_id=self.batch_id,
            progress_callback=progress_callback,
            stop_callback=get_stop_cb,
            merging_mode="average",
        ),
        # ... Median and Similarity unchanged for now
    },
}
```

#### 5b. `bulk_combined_panel.py` (Batch Mode)

```python
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    running_mf_denoiser as running_similarity,
    running_mf_denoiser,  # reuse with merging_mode
)

actions = {
    "denoising": {
        "Average": lambda: running_mf_denoiser(
            self,
            single_process=False,
            batch_id=self.batch_id,
            progress_callback=progress_callback,
            merging_mode="average",
        ),
        # ... Median and Similarity unchanged
    },
}
```

Note: The `running_average` import can be removed from both files since it's no longer called.

#### 5c. `image_processing_controller.py`

```python
def _run_denoising_algorithm(self, algorithm_name, parameters, single_process):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
        running_mf_denoiser as running_similarity,
        running_mf_denoiser,
    )

    if algorithm_name == "Average":
        return running_mf_denoiser(
            merging_mode="average", single_process=single_process
        )
    # ... rest unchanged
```

### Task 6: Handle Average Params (Tile Size, Overlap)

MFDenoiser's `_load_params()` currently loads `similarity_config` which includes tile_size and overlap. These are suitable for Average too — no separate config needed. The default tile_size (32) and overlap (0.40) work fine for Average.

However, the Average algorithm doesn't need the spatial/smart-specific parameters (motion_sensitivity, noise_mad_offset, etc.). This is fine — they'll just be ignored by `AverageDenoiseProcessor`.

### Task 7: Handle MFDenoiser's `merging_mode` for Post-Processing

`stage_postprocess()` currently applies adaptive box denoise for spatial/smart modes. For Average, this should be optional (default ON is fine — it's a lightweight cleanup).

No change needed here — the adaptive box denoise is a generic post-processing step that works well with any algorithm.

---

## Files Modified Summary

| File | Change |
|------|--------|
| `average_denoise_processor.py` | **NEW** — AverageDenoiseProcessor(TileProcessor) |
| `MFDenoiser.py` | Add `merging_mode` param to main/running_mf_denoiser/run_pipeline, add "average" case to stage_merge, add output_suffix to stage_save |
| `algorithm_processor.py` | Route "Average" → running_mf_denoiser(merging_mode="average") |
| `bulk_combined_panel.py` | Route "Average" → running_mf_denoiser(merging_mode="average") |
| `image_processing_controller.py` | Route "Average" → running_mf_denoiser(merging_mode="average") |

---

## Execution Order

1. Create `average_denoise_processor.py` (Task 1)
2. Modify `MFDenoiser.py` — add merging_mode param + "average" branch + output_suffix (Tasks 2, 3, 4)
3. Modify `algorithm_processor.py` (Task 5a)
4. Modify `bulk_combined_panel.py` (Task 5b)
5. Modify `image_processing_controller.py` (Task 5c)
6. Verify all files compile (Task 7)

---

## Behavioral Notes

- **Tiling behavior**: Average will now be processed with the same tiling infrastructure (tile_size from similarity params, Hanning window stitching). This means large images are processed tile-by-tile with smooth blending, reducing memory usage and enabling better progress reporting.

- **Output quality**: The result should be mathematically equivalent to the old Average (simple pixel-wise average), but with Hanning window stitching at tile boundaries. For well-aligned images, the difference is negligible. For images with slight misalignment at tile boundaries, the Hanning blending may actually produce slightly better results.

- **Output file naming**: The output will be saved as `{name}_average.tif` instead of `{name}_average.tif` (same name, different path through MFDenoiser's save stage).

- **Post-processing**: MFDenoiser's adaptive box denoise will be applied as a post-processing step. If this changes the result too much compared to the old Average, it can be disabled by setting `ctx.params["postprocessor"] = "none"` for the average mode.

- **Alignment**: MFDenoiser's alignment stage will run if no HDF5 cache exists. The old Average.py had no alignment — it relied on pre-aligned images. This is actually an improvement since Average now benefits from alignment too.
