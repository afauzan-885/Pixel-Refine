# MFDenoiser Architecture

## Overview

`MFDenoiserAlgorithm` adalah orchestrator pipeline multi-frame denoising yang menggantikan `Similarity.py` sebagai entry point utama.

**Pipeline**: `Load → Align → Merge → PostProcess → Save`

## Single Truth Source

`_load_params()` membaca parameter dari `load_similarity_config()` — config yang sama digunakan oleh `Similarity.py`, memastikan kedua orchestrator share identical parameter behavior.

```python
def _load_params(self):
    """Reads from load_similarity_config() — same config as Similarity.py."""
    sim_config = load_similarity_config()
    
    params = {
        # Tiling
        "tile_size": (tile_val, tile_val),           # (h, w) tuple
        "overlap": 0.30,                              # 0.0-1.0
        
        # Ghost Rejection
        "motion_sensitivity": 150.0,                  # Higher = more aggressive
        "noise_offset_factor": 0.15,                  # Noise floor offset
        
        # Backend Selection
        "merging_mode": "spatial_fusion",             # Default backend
        "optical_flow_type": "alignment_tile",        # Farneback/Horn-Schunck/BMA
        "alignment_backend": "taichi_gpu",
        
        # Smart Fusion (AI)
        "similarity_smart_noise_alpha": 1.0,
        
        # Spatial Fusion specific
        "early_exit_threshold": 0.05,
        "equalize_brightness": False,
    }
    return params
```

## Backend Selection (Pluggable via `ctx.params`)

| Stage | Parameter | Options | Default |
|-------|-----------|---------|---------|
| **Align** | `alignment_backend` | `"taichi_gpu"`, `"none"`, callable | `"taichi_gpu"` |
| **Align** | `optical_flow_type` | `"alignment_tile"` (BMA), `"horn_schunck"`, `"farneback_aot"`, `"farneback_jit"`, `"block_align"` | `"alignment_tile"` |
| **Merge** | `merging_mode` | `"spatial_fusion"`, `"average"`, `"smart"`, `"super_resolution"`, `"spatial"` | `"spatial_fusion"` |
| **Post** | `postprocessor` | `"adaptive_box"`, `"none"`, callable | `"adaptive_box"` |

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│  UI Settings (similarity_parameter_settings.py)             │
│  └─ load_similarity_config() → JSON config                  │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  MFDenoiserAlgorithm._load_params()  ← SINGLE TRUTH        │
│  └─ Simpan ke ctx.params (dict)                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  run_pipeline() → ctx.params ke setiap stage                │
│                                                             │
│  stage_load_data(ctx):                                      │
│    └─ Load images, detect linear mode, calculate proxy      │
│                                                             │
│  stage_align(ctx):                                          │
│    ├─ alignment_backend → "taichi_gpu" / "none" / callable │
│    └─ optical_flow_type → "alignment_tile" / "horn_schunck" │
│         / "farneback_aot" / "farneback_jit" / "block_align" │
│                                                             │
│  stage_merge(ctx):                                          │
│    ├─ merging_mode="spatial_fusion" → SpatialFusionProcessor│
│    ├─ merging_mode="average" → AverageDenoiseProcessor     │
│    ├─ merging_mode="smart" → SmartDenoiseProcessor (AI)    │
│    ├─ merging_mode="super_resolution" → SRProcessor        │
│    └─ merging_mode="spatial" → SpatialDenoiseProcessor     │
│                                                             │
│  stage_postprocess(ctx):                                    │
│    ├─ postprocessor="adaptive_box" → HF Denoise            │
│    ├─ postprocessor="none" → Skip                          │
│    └─ postprocessor=callable → Custom function             │
│                                                             │
│  stage_save(ctx):                                           │
│    └─ Save to database/stack/                               │
└─────────────────────────────────────────────────────────────┘
```

## Spatial Fusion Processor

**Modul**: `spatial_core/spatial_fusion_processor.py`

`SpatialFusionProcessor` menggunakan kernel Taichi AOT dari `compute_spatial.py` untuk ghost rejection berbasis hybrid gradient MAD score dengan analisis coarse-to-fine.

### Pipeline per Frame

```
1. Precompute gradients (GPU AOT) → grad_x, grad_y
2. Coarse analysis (1/4 res) → guidance map
3. Fine analysis (4-pass sliding window MAD) → per-frame weight map
4. Bilinear upsample work-res weights → full-res
5. Accumulate: sum += frame * weight
6. Finalize: result = sum / weight_sum
```

### AOT Graphs (dari `spatial_vulkan.tcm`)

| Graph | Fungsi |
|-------|--------|
| `precompute_gradients` | Sobel DX/DY gradients |
| `equalize_brightness` | Brightness equalization (optional) |
| `phase1_coarse_analysis` | Coarse confidence map (1/4 res) |
| `phase2_fine_analysis` | Fine weight map (4-pass sliding window) |
| `generate_fine_weights_4passes` | Fused 4-pass fine analysis |
| `accumulate_spatial_merging` | Bilinear upsample + accumulate |
| `fine_analysis_and_accumulate` | Fused fine + accumulate |

### Error Handling

Jika GPU AOT engine tidak tersedia, raise `RuntimeError` dengan pesan jelas:
```python
raise RuntimeError(
    f"[SpatialFusion] GPU AOT engine not available: {e}. "
    "Spatial fusion requires a compatible GPU with Vulkan support."
)
```

## Cara Penggunaan

### Via UI Settings (JSON config)
```json
{
    "merging_mode": "spatial_fusion",
    "optical_flow_type": "alignment_tile",
    "similarity_spatial_tile_size": 16,
    "similarity_spatial_motion_sensitivity": 150.0,
    "similarity_spatial_noise_mad_offset_factor": 0.15,
    "similarity_spatial_overlap_percent": 0.30
}
```

### Via Code Override
```python
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import MFDenoiserAlgorithm

processor = MFDenoiserAlgorithm(db_path)
output_path = processor.run_pipeline(
    single_process=True,
    merging_mode="spatial_fusion",  # Override backend
)
```

### Spatial Fusion Processor API
```python
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion_processor import SpatialFusionProcessor

processor = SpatialFusionProcessor(
    motion_sensitivity=150.0,
    noise_offset_factor=0.15,
    early_exit_threshold=0.05,
    equalize_brightness=False,
)

frame_count, sum_img, sum_weight, ref_noise_sigma = processor.process(
    images=images_list,
    reference_image_float=ref_float,
    ref_h=h, ref_w=w,
    ref_dtype=np.uint16,
    work_res_h=work_h, work_res_w=work_w,
    update_progress=callback,
    stop_requested=stop_check,
)
```

## Key Files

| File | Deskripsi |
|------|-----------|
| `MFDenoiser.py` | Orchestrator utama (single truth source) |
| `Similarity.py` | Legacy orchestrator (backup) |
| `spatial_fusion_processor.py` | Spatial Fusion GPU AOT processor |
| `compute_spatial.py` | Taichi AOT kernels untuk ghost rejection |
| `similarity_parameter_settings.py` | UI settings & config loader |
